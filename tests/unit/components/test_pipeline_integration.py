"""Integration test: IPA → WBA → NGA pipeline with mocked LLM.

Tests the full pipeline with:
- IPAAgent: mocked LLM returning a structured JSON response
- WBAAgent: mocked WorldContextBuilder returning a WorldContext
- NGAAgent: mocked LLM returning a narrative string

All external dependencies (real LLM, Neo4j) are mocked.
This validates the data flow and type contracts across all three agents.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.components.ipa.agent import IPAAgent
from src.components.ipa.models import Intent, ProcessedInput
from src.components.nga.agent import NGAAgent
from src.components.wba.agent import WBAAgent
from src.components.world_context.models import LocationFact, NPCState, WorldContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ipa_llm(intent: str = "interact") -> Any:
    payload = json.dumps(
        {
            "intent": intent,
            "intent_confidence": 0.92,
            "entities": [
                {"name": "blacksmith", "entity_type": "npc", "confidence": 0.95}
            ],
            "emotional_tone": {
                "primary": "curious",
                "intensity": 0.4,
                "safety_signal": False,
            },
            "normalized_text": "i want to talk to the blacksmith",
        }
    )
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=payload))
    return llm


def _make_world_builder(location_id: str = "loc-forge") -> Any:
    wc = WorldContext(
        location_id=location_id,
        location=LocationFact(
            id=location_id,
            name="The Forge District",
            description="The air smells of iron and smoke.",
        ),
        npcs=[
            NPCState(
                id="npc-bs",
                name="blacksmith",
                role="craftsman",
                emotional_state="focused",
                is_active=True,
            )
        ],
    )
    assembled = MagicMock()
    assembled.total_tokens = 420
    assembled.neo4j_available = True
    assembled.truncated_tiers = []
    assembled.neo4j_context = wc

    builder = MagicMock()
    builder.build = AsyncMock(return_value=assembled)
    return builder


def _make_nga_llm(narrative: str) -> Any:
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=narrative))
    return llm


# ---------------------------------------------------------------------------
# Pipeline test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_ipa_wba_nga_pipeline() -> None:
    """Full pipeline: raw text → ProcessedInput → WorldContext → narrative."""
    # Arrange
    session_id = "integration-test-session"
    player_id = "player-1"
    location_id = "loc-forge"
    raw_text = "I want to talk to the blacksmith"
    expected_narrative = "The blacksmith looks up from the anvil, eyeing you carefully."

    ipa = IPAAgent(llm=_make_ipa_llm("interact"))
    wba = WBAAgent(builder=_make_world_builder(location_id))
    nga = NGAAgent(llm=_make_nga_llm(expected_narrative))

    # Act — IPA stage
    processed = await ipa.process(
        raw_text,
        session_id=session_id,
        player_id=player_id,
        location_id=location_id,
    )

    # Assert IPA output shape
    assert isinstance(processed, ProcessedInput)
    assert processed.intent == Intent.INTERACT
    assert processed.session_id == session_id
    assert processed.player_id == player_id
    assert processed.location_id == location_id
    assert processed.npc_names == ["blacksmith"]

    # Act — WBA stage
    world_ctx = await wba.build(processed)

    # Assert WBA output shape
    assert isinstance(world_ctx, WorldContext)
    assert world_ctx.location.name == "The Forge District"
    assert any(n.name == "blacksmith" for n in world_ctx.npcs)

    # Act — NGA stage
    narrative = await nga.generate(processed, world_ctx)

    # Assert NGA output
    assert isinstance(narrative, str)
    assert narrative == expected_narrative


@pytest.mark.asyncio
async def test_pipeline_handles_missing_location() -> None:
    """Pipeline should not crash when no location_id is available."""
    ipa = IPAAgent(llm=_make_ipa_llm("explore"))
    wba = WBAAgent(builder=None)  # no builder
    nga = NGAAgent(llm=_make_nga_llm("The world is quiet."))

    processed = await ipa.process("go somewhere", session_id="s1")
    processed = processed.model_copy(update={"location_id": None})

    world_ctx = await wba.build(processed)
    assert world_ctx.location_id == "unknown"

    narrative = await nga.generate(processed, world_ctx)
    assert isinstance(narrative, str)


@pytest.mark.asyncio
async def test_pipeline_propagates_safety_signal() -> None:
    """Safety signals from IPA should be visible to NGA via ProcessedInput."""
    ipa_payload = json.dumps(
        {
            "intent": "journal",
            "intent_confidence": 0.7,
            "entities": [],
            "emotional_tone": {
                "primary": "sad",
                "intensity": 0.85,
                "safety_signal": True,
            },
            "normalized_text": "i feel like giving up",
        }
    )
    ipa_llm = MagicMock()
    ipa_llm.ainvoke = AsyncMock(return_value=AIMessage(content=ipa_payload))

    ipa = IPAAgent(llm=ipa_llm)
    wba = WBAAgent(builder=None)
    nga = NGAAgent(llm=_make_nga_llm("You are not alone."))

    processed = await ipa.process(
        "I feel like giving up",
        session_id="crisis-session",
        location_id="loc-home",
    )

    assert processed.needs_safety_check

    world_ctx = await wba.build(processed)
    narrative = await nga.generate(processed, world_ctx)
    assert isinstance(narrative, str)
