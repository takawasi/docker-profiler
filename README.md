# docker-profiler

> **Documentation**: https://takawasi-social.com/tools/docker-profiler/

Visualize Docker container resources with ASCII graphs.

docker stats, but visual.

## Quick Start

```bash
# 1. Install
pip install docker-profiler

# 2. Profile
docker-profiler -c myapp
```

## Features

- **ASCII graphs**: See trends in your terminal
- **Live mode**: Real-time updating display
- **No dependencies**: Just Docker SDK
- **Simple**: One container, one command

## Output Example

```
Profiling: myapp for 1m
Interval: 1s

CPU Usage (%)
 85.0 ┤                    ╭─╮
 50.0 ┤          ╭─────────╯ ╰───────╮
 15.0 ┤    ╭─────╯                   ╰────
      └────────────────────────────────────────
      0                                     now

Memory Usage (MB)
512.0 ┤                         ╭──────────
256.0 ┤          ╭──────────────╯
128.0 ┤    ╭─────╯
      └────────────────────────────────────────

╭─────────────────── Summary ───────────────────╮
│ Peak CPU: 85.2%, Avg CPU: 45.3%               │
│ Peak Memory: 487.2MB, Avg Memory: 312.1MB     │
╰───────────────────────────────────────────────╯
```

## Usage

```bash
# Basic profiling (1 minute default)
docker-profiler -c myapp

# Custom duration
docker-profiler -c myapp -d 5m
docker-profiler -c myapp -d 1h

# Custom interval
docker-profiler -c myapp -i 5  # 5 second intervals

# Live updating display
docker-profiler -c myapp --live
```

## Requirements

- Docker running locally
- Python 3.10+
- `docker` Python SDK

## More Tools

See all dev tools: https://takawasi-social.com/en/

## License

MIT
