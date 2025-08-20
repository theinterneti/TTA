# Administrative Recovery Command

## Overview

A CLI utility is provided to manually trigger message recovery and display per-agent recovery statistics.

## Usage

```bash
uv run python -m src.agent_orchestration.admin.recover REDIS_URL --key-prefix ao
```

- Connects to Redis
- Executes `recover_pending(None)` logic per agent instance
- Prints recovered counts per agent type:instance and total

## Notes

- Uses the same key prefix as the orchestration system (default: `ao`)
- Safe to run multiple times; only expired reservations are reclaimed

