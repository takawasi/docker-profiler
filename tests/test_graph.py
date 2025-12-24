"""Tests for ASCII graph generator."""

from docker_profiler.graph import render_ascii_graph, render_summary


def test_render_graph():
    """Render basic graph."""
    values = [10, 20, 30, 40, 50, 40, 30, 20, 10]
    result = render_ascii_graph(values, title="Test Graph")

    assert "Test Graph" in result
    assert "50.0" in result  # Max value
    assert "10.0" in result  # Min value


def test_render_empty():
    """Handle empty values."""
    result = render_ascii_graph([])
    assert "No data" in result


def test_render_single_value():
    """Handle single value."""
    values = [50.0]
    result = render_ascii_graph(values)
    # Should not crash
    assert "50.0" in result


def test_render_summary():
    """Render summary statistics."""
    cpu = [10, 20, 30]
    memory = [100, 200, 300]

    result = render_summary(cpu, memory)

    assert "Peak CPU: 30.0%" in result
    assert "Avg CPU: 20.0%" in result
    assert "Peak Memory: 300.0MB" in result
