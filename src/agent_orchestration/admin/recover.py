from __future__ import annotations

import asyncio

from redis.asyncio import Redis
from tta_ai.orchestration.coordinators import RedisMessageCoordinator
from tta_ai.orchestration.models import AgentId, AgentType


async def run_recovery(redis_url: str, key_prefix: str = "ao") -> dict[str, int]:
    """Run global recovery and return per-agent recovered counts.

    Uses coordinator.recover_pending() per agent to compute exact recovered counts.
    """
    redis = Redis.from_url(redis_url)
    coord = RedisMessageCoordinator(redis, key_prefix=key_prefix)

    per_agent: dict[str, int] = {}
    for at in (AgentType.IPA, AgentType.WBA, AgentType.NGA):
        pattern = f"{key_prefix}:reserved_deadlines:{at.value}:*"
        async for key in redis.scan_iter(match=pattern):
            k = key.decode() if isinstance(key, (bytes, bytearray)) else key
            inst = k.split(":")[-1]
            # Targeted recovery for this agent
            aid = AgentId(type=at, instance=inst)
            recovered = await coord.recover_pending(aid)
            if recovered:
                per_agent[f"{at.name.lower()}:{inst}"] = recovered

    await redis.aclose()
    return per_agent


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Agent Orchestration Admin - Recovery")
    parser.add_argument(
        "redis_url", nargs="?", default="redis://localhost:6379/0", help="Redis URL"
    )
    parser.add_argument("--key-prefix", default="ao", help="Redis key prefix")
    args = parser.parse_args()

    per_agent = asyncio.run(run_recovery(args.redis_url, key_prefix=args.key_prefix))
    sum(per_agent.values())
    if not per_agent:
        pass
    for _agent, _count in per_agent.items():
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
