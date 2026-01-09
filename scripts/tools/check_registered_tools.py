#!/usr/bin/env python3
"""Check what tools are currently registered in Redis."""

# Logseq: [[TTA.dev/Scripts/Tools/Check_registered_tools]]

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from redis.asyncio import Redis

from agent_orchestration.tools.redis_tool_registry import RedisToolRegistry


async def main():
    """Check registered tools in Redis."""
    # Connect to Redis (DB 1 for tests/dev)
    redis_client = Redis(host="localhost", port=6379, db=1, decode_responses=False)

    try:
        # Create registry
        registry = RedisToolRegistry(redis_client, key_prefix="ao-dev")

        # List all tools
        tools, next_cursor = await registry.list_tools()

        if not tools:
            pass
        else:
            for _i, _tool in enumerate(tools, 1):
                pass

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
