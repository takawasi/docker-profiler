"""ASCII graph generator."""

from typing import List
from dataclasses import dataclass


@dataclass
class GraphConfig:
    """Graph configuration."""
    width: int = 60
    height: int = 10
    title: str = ""


def render_ascii_graph(
    values: List[float],
    title: str = "",
    width: int = 60,
    height: int = 8,
    unit: str = "",
) -> str:
    """Render values as ASCII line graph.

    Returns multi-line string.
    """
    if not values:
        return "No data"

    # Normalize values to height
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val != min_val else 1

    lines = []

    # Title
    if title:
        lines.append(title)

    # Y-axis labels
    y_labels = [
        f"{max_val:6.1f}",
        f"{(max_val + min_val) / 2:6.1f}",
        f"{min_val:6.1f}",
    ]

    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot values
    step = len(values) / width if len(values) > width else 1
    prev_y = None

    for x in range(width):
        idx = min(int(x * step), len(values) - 1)
        val = values[idx]
        normalized = (val - min_val) / val_range
        y = height - 1 - int(normalized * (height - 1))
        y = max(0, min(height - 1, y))

        # Draw point
        grid[y][x] = '─'

        # Connect to previous point
        if prev_y is not None:
            if y < prev_y:
                for fill_y in range(y + 1, prev_y):
                    grid[fill_y][x] = '│'
                grid[y][x] = '╭' if x > 0 else '─'
                grid[prev_y][x - 1] = '╯' if x > 0 and grid[prev_y][x - 1] == '─' else grid[prev_y][x - 1]
            elif y > prev_y:
                for fill_y in range(prev_y + 1, y):
                    grid[fill_y][x] = '│'
                grid[y][x] = '╰' if x > 0 else '─'
                grid[prev_y][x - 1] = '╮' if x > 0 and grid[prev_y][x - 1] == '─' else grid[prev_y][x - 1]

        prev_y = y

    # Render grid with Y-axis
    for i, row in enumerate(grid):
        if i == 0:
            label = y_labels[0]
        elif i == height - 1:
            label = y_labels[2]
        elif i == height // 2:
            label = y_labels[1]
        else:
            label = "      "

        lines.append(f"{label} ┤{''.join(row)}")

    # X-axis
    lines.append("       └" + "─" * width)

    # X-axis labels
    x_labels = f"       0{' ' * (width // 2 - 1)}{''.join(unit)}{' ' * (width // 2 - len(unit))}now"
    lines.append(x_labels)

    return '\n'.join(lines)


def render_summary(
    cpu_values: List[float],
    memory_values: List[float],
) -> str:
    """Render summary statistics."""
    lines = []

    if cpu_values:
        lines.append(f"Peak CPU: {max(cpu_values):.1f}%, Avg CPU: {sum(cpu_values) / len(cpu_values):.1f}%")

    if memory_values:
        lines.append(f"Peak Memory: {max(memory_values):.1f}MB, Avg Memory: {sum(memory_values) / len(memory_values):.1f}MB")

    return '\n'.join(lines)
