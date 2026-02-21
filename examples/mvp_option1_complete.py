"""

# Logseq: [[TTA.dev/Examples/Mvp_option1_complete]]
Complete MVP Example - Production-Ready Narrative Workflow

This example demonstrates a complete narrative generation workflow using:
- RouterPrimitive for cost optimization
- TimeoutPrimitive for reliability
- CachePrimitive for performance

Run this to see the enhanced workflow in action!
"""

import asyncio
import logging

from tta_ai.orchestration.primitives import create_enhanced_narrative_workflow
from tta_workflow_primitives import WorkflowContext

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


# ==================== MOCK LLM HANDLERS ====================
# Replace these with real API calls to OpenAI, Anthropic, local models, etc.


async def openai_narrative_handler(data: dict) -> dict:
    """Simulate OpenAI API call (expensive, high quality)."""
    await asyncio.sleep(0.3)  # Simulate API latency

    prompt = data.get("prompt", "")
    return {
        "narrative": f"[OpenAI GPT-4] A masterfully crafted story: {prompt[:50]}...",
        "provider": "openai",
        "quality_score": 0.95,
        "tokens_used": 150,
        "cost": 0.10,  # $0.10 per request
    }


async def local_llm_handler(data: dict) -> dict:
    """Simulate local LLM (cheap, good quality)."""
    await asyncio.sleep(0.1)  # Faster than API

    prompt = data.get("prompt", "")
    return {
        "narrative": f"[Local LLama] A well-crafted story: {prompt[:50]}...",
        "provider": "local",
        "quality_score": 0.80,
        "tokens_used": 150,
        "cost": 0.01,  # $0.01 per request (local inference)
    }


async def fallback_handler(data: dict) -> dict:
    """Fallback for timeouts/errors."""
    return {
        "narrative": "I'm experiencing high load. Here's a brief response...",
        "provider": "fallback",
        "quality_score": 0.60,
        "tokens_used": 50,
        "cost": 0.0,
    }


# ==================== TEST SCENARIOS ====================


async def test_scenario_1_simple_query():
    """Test 1: Simple query (routes to local, should cache)."""

    workflow = create_enhanced_narrative_workflow(
        openai_handler=openai_narrative_handler,
        local_handler=local_llm_handler,
        fallback_handler=fallback_handler,
    )

    context = WorkflowContext(
        session_id="test-session-1", player_id="player-123", metadata={"tier": "free"}
    )

    # First call
    await workflow.execute({"prompt": "Tell me a quick story about dragons"}, context)

    # Second call (should hit cache)
    context2 = WorkflowContext(
        session_id="test-session-1", player_id="player-123", metadata={"tier": "free"}
    )
    await workflow.execute({"prompt": "Tell me a quick story about dragons"}, context2)

    # Show stats
    return workflow.get_stats()


async def test_scenario_2_complex_query():
    """Test 2: Complex query (routes to OpenAI)."""

    workflow = create_enhanced_narrative_workflow(
        openai_handler=openai_narrative_handler,
        local_handler=local_llm_handler,
        fallback_handler=fallback_handler,
    )

    context = WorkflowContext(
        session_id="test-session-2", player_id="player-456", metadata={"tier": "free"}
    )

    complex_prompt = """
    Create a detailed epic fantasy narrative involving multiple characters,
    intricate plot twists, and a complex world with its own history, culture,
    and magical system. The story should span multiple generations and include
    political intrigue, moral dilemmas, and character development.
    """

    await workflow.execute({"prompt": complex_prompt}, context)


async def test_scenario_3_premium_user():
    """Test 3: Premium user (always routes to OpenAI)."""

    workflow = create_enhanced_narrative_workflow(
        openai_handler=openai_narrative_handler,
        local_handler=local_llm_handler,
        fallback_handler=fallback_handler,
    )

    context = WorkflowContext(
        session_id="test-session-3",
        player_id="premium-user-789",
        metadata={"tier": "premium"},
    )

    await workflow.execute({"prompt": "Short story about a cat"}, context)


async def test_scenario_4_cost_comparison():
    """Test 4: Show cost savings over multiple requests."""

    workflow = create_enhanced_narrative_workflow(
        openai_handler=openai_narrative_handler,
        local_handler=local_llm_handler,
        fallback_handler=fallback_handler,
    )

    # Simulate 10 requests with 60% repetition (realistic cache hit rate)
    prompts = [
        "Story about dragons",  # Used 3 times
        "Story about wizards",  # Used 2 times
        "Story about knights",  # Used 2 times
        "Story about dragons",  # Cache hit
        "Story about wizards",  # Cache hit
        "Story about elves",  # New
        "Story about dragons",  # Cache hit
        "Story about knights",  # Cache hit
        "Story about dwarves",  # New
        "Story about orcs",  # New
    ]

    total_cost = 0.0

    for i, prompt in enumerate(prompts, 1):
        context = WorkflowContext(
            session_id=f"test-session-{i}",
            player_id="player-test",
            metadata={"tier": "free"},
        )

        result = await workflow.execute({"prompt": prompt}, context)
        total_cost += result["cost"]

        context.state.get("cache_hits", 0) > 0

    # Calculate savings
    workflow.get_stats()
    len(prompts) * 0.01  # All local


async def main():
    """Run all test scenarios."""

    # Run all tests
    await test_scenario_1_simple_query()
    await test_scenario_2_complex_query()
    await test_scenario_3_premium_user()
    await test_scenario_4_cost_comparison()

    # Final summary


if __name__ == "__main__":
    asyncio.run(main())
