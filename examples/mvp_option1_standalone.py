"""
MVP Option 1: Complete Standalone Example

This demonstrates the full enhanced workflow without dependencies on tta_ai package.
All code is self-contained and ready to run!
"""

import asyncio
import hashlib
import logging
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "packages" / "tta-workflow-primitives" / "src"),
)

from tta_workflow_primitives import (
    CachePrimitive,
    LambdaPrimitive,
    RouterPrimitive,
    TimeoutPrimitive,
    WorkflowContext,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== LLM HANDLERS ====================


async def openai_handler(data: dict) -> dict:
    """Simulate OpenAI API (expensive, high quality)."""
    await asyncio.sleep(0.3)
    prompt = data.get("prompt", "")
    return {
        "narrative": f"[OpenAI] Masterful story: {prompt[:40]}...",
        "provider": "openai",
        "quality": 0.95,
        "cost": 0.10,
    }


async def local_handler(data: dict) -> dict:
    """Simulate local LLM (cheap, good quality)."""
    await asyncio.sleep(0.1)
    prompt = data.get("prompt", "")
    return {
        "narrative": f"[Local] Good story: {prompt[:40]}...",
        "provider": "local",
        "quality": 0.80,
        "cost": 0.01,
    }


async def fallback_handler(data: dict) -> dict:
    """Fallback for timeouts."""
    return {
        "narrative": "Experiencing high load. Brief response...",
        "provider": "fallback",
        "quality": 0.60,
        "cost": 0.0,
    }


# ==================== WORKFLOW BUILDER ====================


def create_workflow():
    """Build the complete enhanced workflow."""

    # Wrap handlers
    openai_prim = LambdaPrimitive(openai_handler)
    local_prim = LambdaPrimitive(local_handler)
    fallback_prim = LambdaPrimitive(fallback_handler)

    # Routing logic
    def route(data: dict, ctx: WorkflowContext) -> str:
        tier = ctx.metadata.get("tier", "free")
        if tier == "premium":
            return "openai"

        prompt = data.get("prompt", "")
        if len(prompt) > 200:
            return "openai"  # Complex
        return "local"  # Simple

    # Build: Cache → Timeout → Router
    router = RouterPrimitive(
        routes={"openai": openai_prim, "local": local_prim},
        router_fn=route,
        default="local",
    )

    timeout = TimeoutPrimitive(router, timeout_seconds=30.0, fallback=fallback_prim)

    return CachePrimitive(
        timeout,
        cache_key_fn=lambda d, c: (
            f"{hashlib.md5(d.get('prompt', '').encode()).hexdigest()[:16]}:"
            f"{c.metadata.get('tier', 'free')}"
        ),
        ttl_seconds=3600.0,
    )


# ==================== TEST SCENARIOS ====================


async def test1_simple_with_cache():
    workflow = create_workflow()
    ctx = WorkflowContext(metadata={"tier": "free"})

    await workflow.execute({"prompt": "Story about dragons"}, ctx)

    ctx2 = WorkflowContext(metadata={"tier": "free"})
    await workflow.execute({"prompt": "Story about dragons"}, ctx2)

    workflow.get_stats()


async def test2_complex_routing():
    workflow = create_workflow()

    complex = "x" * 250  # Long prompt
    ctx = WorkflowContext(metadata={"tier": "free"})

    await workflow.execute({"prompt": complex}, ctx)


async def test3_premium_tier():
    workflow = create_workflow()
    ctx = WorkflowContext(metadata={"tier": "premium"})

    await workflow.execute({"prompt": "Short story"}, ctx)


async def test4_cost_analysis():
    workflow = create_workflow()

    prompts = [
        "Dragons",
        "Wizards",
        "Knights",
        "Dragons",  # Hit
        "Wizards",  # Hit
        "Elves",
        "Dragons",  # Hit
        "Knights",  # Hit
        "Dwarves",
        "Orcs",
    ]

    total_cost = 0.0

    for _i, p in enumerate(prompts, 1):
        ctx = WorkflowContext(metadata={"tier": "free"})
        r = await workflow.execute({"prompt": p}, ctx)
        ctx.state.get("cache_hits", 0) > 0
        total_cost += r["cost"]

    workflow.get_stats()
    len(prompts) * 0.01


async def main():
    await test1_simple_with_cache()
    await test2_complex_routing()
    await test3_premium_tier()
    await test4_cost_analysis()


if __name__ == "__main__":
    asyncio.run(main())
