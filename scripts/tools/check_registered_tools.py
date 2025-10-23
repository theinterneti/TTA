#!/usr/bin/env python3
"""Check what tools are currently registered in Redis."""

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

        print(f"\n{'='*80}")
        print(f"REGISTERED TOOLS IN REDIS (DB 1, prefix: ao-dev)")
        print(f"{'='*80}\n")

        if not tools:
            print("❌ NO TOOLS REGISTERED")
            print("\nThis is expected - the tool infrastructure exists but no concrete")
            print("tools have been implemented yet. This is what Phase 3 will address.")
        else:
            print(f"✅ Found {len(tools)} registered tool(s):\n")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name} (v{tool.version})")
                print(f"   Description: {tool.description}")
                print(f"   Parameters: {len(tool.parameters)}")
                print(f"   Supports Pagination: {tool.supports_pagination}")
                print(f"   Status: {tool.status}")
                print()

        print(f"{'='*80}\n")

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())

