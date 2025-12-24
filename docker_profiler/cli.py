"""CLI interface for docker-profiler."""

import sys
import time
import click
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from .collector import collect_stats, get_single_stats, DOCKER_AVAILABLE
from .graph import render_ascii_graph, render_summary

console = Console()


@click.command()
@click.option('--container', '-c', required=True, help='Container name or ID')
@click.option('--duration', '-d', default='1m', help='Duration (e.g., 30s, 5m, 1h)')
@click.option('--interval', '-i', default=1, type=int, help='Sample interval in seconds')
@click.option('--live', is_flag=True, help='Live updating display')
@click.version_option()
def main(container: str, duration: str, interval: int, live: bool):
    """Visualize Docker container resources with ASCII graphs.

    Examples:

        docker-profiler -c myapp
        docker-profiler -c myapp -d 5m
        docker-profiler -c myapp --live
    """
    if not DOCKER_AVAILABLE:
        console.print("[red]Error:[/red] Docker SDK not installed.")
        console.print("Run: pip install docker")
        sys.exit(1)

    # Parse duration
    duration_seconds = _parse_duration(duration)

    console.print(f"[bold blue]Profiling:[/] {container} for {duration}")
    console.print(f"[dim]Interval: {interval}s[/dim]")
    console.print()

    cpu_values = []
    memory_values = []

    try:
        if live:
            _live_mode(container, duration_seconds, interval, cpu_values, memory_values)
        else:
            _batch_mode(container, duration_seconds, interval, cpu_values, memory_values)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Final output
    if cpu_values:
        console.print()
        console.print(render_ascii_graph(cpu_values, title="CPU Usage (%)", unit=duration))
        console.print()
        console.print(render_ascii_graph(memory_values, title="Memory Usage (MB)", unit=duration))
        console.print()
        console.print(Panel(render_summary(cpu_values, memory_values), title="Summary"))


def _batch_mode(container, duration_seconds, interval, cpu_values, memory_values):
    """Collect all data then display."""
    with console.status(f"Collecting data..."):
        for point in collect_stats(container, duration_seconds, interval):
            cpu_values.append(point.cpu_percent)
            memory_values.append(point.memory_mb)


def _live_mode(container, duration_seconds, interval, cpu_values, memory_values):
    """Live updating display."""
    start = time.time()

    with Live(console=console, refresh_per_second=1) as live:
        for point in collect_stats(container, duration_seconds, interval):
            cpu_values.append(point.cpu_percent)
            memory_values.append(point.memory_mb)

            elapsed = int(time.time() - start)
            output = f"[dim]Elapsed: {elapsed}s[/dim]\n\n"
            output += render_ascii_graph(cpu_values[-60:], title="CPU Usage (%)", width=50, height=6)
            output += "\n\n"
            output += render_ascii_graph(memory_values[-60:], title="Memory (MB)", width=50, height=6)

            live.update(Panel(output, title=f"Profiling: {container}"))


def _parse_duration(duration: str) -> int:
    """Parse duration string to seconds."""
    duration = duration.lower().strip()

    if duration.endswith('s'):
        return int(duration[:-1])
    elif duration.endswith('m'):
        return int(duration[:-1]) * 60
    elif duration.endswith('h'):
        return int(duration[:-1]) * 3600

    return int(duration)


if __name__ == '__main__':
    main()
