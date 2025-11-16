#!/usr/bin/env python3
"""
Tool Audit Script - Catalog all existing MCP tools in Redis.

This script connects to Redis, retrieves all registered tools, and exports
a comprehensive inventory to JSON for analysis.

Usage:
    python scripts/tools/audit_tools.py --env dev
    python scripts/tools/audit_tools.py --env staging --output custom_path.json
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from redis.asyncio import Redis
from tta_ai.orchestration.tools.redis_tool_registry import RedisToolRegistry


async def get_redis_connection(env: str) -> Redis:
    """Get Redis connection for specified environment."""
    # Environment-specific Redis configurations
    redis_configs = {
        "dev": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "decode_responses": False,
        },
        "staging": {
            "host": os.getenv("REDIS_STAGING_HOST", "localhost"),
            "port": int(os.getenv("REDIS_STAGING_PORT", "6379")),
            "db": int(os.getenv("REDIS_STAGING_DB", "1")),
            "decode_responses": False,
        },
        "production": {
            "host": os.getenv("REDIS_PROD_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PROD_PORT", "6379")),
            "db": int(os.getenv("REDIS_PROD_DB", "2")),
            "decode_responses": False,
        },
    }

    if env not in redis_configs:
        raise ValueError(
            f"Invalid environment: {env}. Must be dev, staging, or production"
        )

    config = redis_configs[env]
    return Redis(**config)


async def audit_tools(env: str) -> dict[str, Any]:
    """
    Audit all tools in specified environment.

    Args:
        env: Environment name (dev, staging, production)

    Returns:
        Dictionary containing audit results
    """

    # Connect to Redis
    redis = await get_redis_connection(env)
    registry = RedisToolRegistry(redis, key_prefix=f"ao_{env}")

    try:
        # Get all tools (using existing list_tools method)
        all_tools = await registry.list_tools()

        # Convert ToolSpec objects to dictionaries
        tools_data = []
        for tool in all_tools:
            tool_dict = tool.model_dump()
            tools_data.append(tool_dict)

        # Analyze tools
        analysis = {
            "total_count": len(tools_data),
            "by_status": {},
            "by_capability": {},
            "missing_descriptions": [],
            "missing_parameters": [],
            "missing_returns_schema": [],
        }

        for tool in tools_data:
            # Count by status
            status = tool.get("status", "unknown")
            analysis["by_status"][status] = analysis["by_status"].get(status, 0) + 1

            # Count by capability
            for cap in tool.get("capabilities", []):
                analysis["by_capability"][cap] = (
                    analysis["by_capability"].get(cap, 0) + 1
                )

            # Identify missing/incomplete data
            if not tool.get("description") or len(tool.get("description", "")) < 50:
                analysis["missing_descriptions"].append(tool["name"])

            if not tool.get("parameters"):
                analysis["missing_parameters"].append(tool["name"])

            if not tool.get("returns_schema"):
                analysis["missing_returns_schema"].append(tool["name"])

        # Build result
        return {
            "environment": env,
            "tools": tools_data,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    finally:
        await redis.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Audit MCP tools in Redis")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "production"],
        default="dev",
        help="Environment to audit (default: dev)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: docs/tools/tool_inventory_{env}.json)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Audit all environments",
    )

    args = parser.parse_args()

    # Determine which environments to audit
    environments = ["dev", "staging", "production"] if args.all else [args.env]

    # Audit each environment
    for env in environments:
        try:
            result = await audit_tools(env)

            # Determine output path
            if args.output:
                output_path = Path(args.output)
            else:
                output_dir = Path("docs/tools")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"tool_inventory_{env}.json"

            # Write results
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)

        except Exception:
            if not args.all:
                sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
