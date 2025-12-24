"""Docker stats collector."""

import time
from typing import Dict, List, Generator
from dataclasses import dataclass
from datetime import datetime

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class StatsPoint:
    """Single stats measurement."""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    net_rx_mb: float
    net_tx_mb: float


def collect_stats(
    container_name: str,
    duration_seconds: int = 60,
    interval_seconds: int = 1,
) -> Generator[StatsPoint, None, None]:
    """Collect stats from a Docker container.

    Yields StatsPoint every interval_seconds until duration_seconds elapsed.
    """
    if not DOCKER_AVAILABLE:
        raise RuntimeError("Docker SDK not installed. Run: pip install docker")

    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        raise ValueError(f"Container not found: {container_name}")

    start_time = time.time()
    end_time = start_time + duration_seconds

    for stats in container.stats(stream=True, decode=True):
        now = time.time()
        if now >= end_time:
            break

        point = _parse_stats(stats)
        yield point

        # Wait for next interval
        elapsed = time.time() - now
        if elapsed < interval_seconds:
            time.sleep(interval_seconds - elapsed)


def _parse_stats(stats: Dict) -> StatsPoint:
    """Parse Docker stats response into StatsPoint."""
    # CPU percent
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                   stats['precpu_stats'].get('system_cpu_usage', 0)

    if system_delta > 0:
        cpu_count = stats['cpu_stats'].get('online_cpus', 1)
        cpu_percent = (cpu_delta / system_delta) * cpu_count * 100
    else:
        cpu_percent = 0

    # Memory
    memory_usage = stats['memory_stats'].get('usage', 0)
    memory_limit = stats['memory_stats'].get('limit', 1)
    memory_mb = memory_usage / (1024 * 1024)
    memory_percent = (memory_usage / memory_limit) * 100 if memory_limit else 0

    # Network
    networks = stats.get('networks', {})
    net_rx = sum(n.get('rx_bytes', 0) for n in networks.values())
    net_tx = sum(n.get('tx_bytes', 0) for n in networks.values())
    net_rx_mb = net_rx / (1024 * 1024)
    net_tx_mb = net_tx / (1024 * 1024)

    return StatsPoint(
        timestamp=datetime.now(),
        cpu_percent=round(cpu_percent, 1),
        memory_mb=round(memory_mb, 1),
        memory_percent=round(memory_percent, 1),
        net_rx_mb=round(net_rx_mb, 2),
        net_tx_mb=round(net_tx_mb, 2),
    )


def get_single_stats(container_name: str) -> StatsPoint:
    """Get single stats snapshot."""
    for point in collect_stats(container_name, duration_seconds=2, interval_seconds=1):
        return point
    raise RuntimeError("Failed to collect stats")
