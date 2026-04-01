"""Unit tests for IPA (Input Processing Agent).

All LLM calls are mocked via AsyncMock so tests run offline and fast.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.components.ipa.agent import IPAAgent, _IPAFallback, _IPALLMCall
from src.components.ipa.models import (
    EmotionalTone,
    ExtractedEntity,
    Intent,
    ProcessedInput,
)

pytestmark = pytest.mark.unit

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    pytest.skip("ttadev.primitives not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_llm(response: str) -> Any:
    """Return a mock LLM that always responds with `response`."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=response))
    return llm


def _ipa_json(
    intent: str = "explore",
    confidence: float = 0.9,
    entities: list | None = None,
    primary: str = "neutral",
    intensity: float = 0.0,
    safety_signal: bool = False,
    normalized: str = "go north",
) -> str:
    return json.dumps(
        {
            "intent": intent,
            "intent_confidence": confidence,
            "entities": entities or [],
            "emotional_tone": {
                "primary": primary,
                "intensity": intensity,
                "safety_signal": safety_signal,
            },
            "normalized_text": normalized,
        }
    )


# ---------------------------------------------------------------------------
# ProcessedInput model
# ---------------------------------------------------------------------------


class TestProcessedInput:
    def test_npc_names_property(self) -> None:
        """Processed Input: npc names property."""
        pi = ProcessedInput(
            raw_text="talk to the guard",
            normalized_text="talk to the guard",
            entities=[
                ExtractedEntity(name="guard", entity_type="npc", confidence=0.9),
                ExtractedEntity(name="gate", entity_type="location", confidence=0.8),
            ],
        )
        assert pi.npc_names == ["guard"]

    def test_location_references_property(self) -> None:
        """Processed Input: location references property."""
        pi = ProcessedInput(
            raw_text="go to the forest",
            normalized_text="go to the forest",
            entities=[
                ExtractedEntity(name="forest", entity_type="location", confidence=0.9),
            ],
        )
        assert pi.location_references == ["forest"]

    def test_needs_safety_check_false_by_default(self) -> None:
        """Processed Input: needs safety check false by default."""
        pi = ProcessedInput(raw_text="hello", normalized_text="hello")
        assert not pi.needs_safety_check

    def test_needs_safety_check_true_on_signal(self) -> None:
        """Processed Input: needs safety check true on signal."""
        pi = ProcessedInput(
            raw_text="I feel hopeless",
            normalized_text="i feel hopeless",
            emotional_tone=EmotionalTone(
                primary="sad", intensity=0.9, safety_signal=True
            ),
        )
        assert pi.needs_safety_check

    def test_default_intent_is_unknown(self) -> None:
        """Processed Input: default intent is unknown."""
        pi = ProcessedInput(raw_text="...", normalized_text="...")
        assert pi.intent == Intent.UNKNOWN


# ---------------------------------------------------------------------------
# _IPALLMCall primitive
# ---------------------------------------------------------------------------


class TestIPALLMCall:
    @pytest.mark.asyncio
    async def test_parses_clean_json(self) -> None:
        """I P A L L M Call: parses clean json."""
        payload = _ipa_json(intent="interact", confidence=0.85)
        llm = _make_llm(payload)
        call = _IPALLMCall(llm)
        ctx = WorkflowContext(workflow_id="test")
        result = await call.execute({"raw_text": "talk to the guard"}, ctx)
        assert result["intent"] == "interact"
        assert result["intent_confidence"] == pytest.approx(0.85)

    @pytest.mark.asyncio
    async def test_strips_markdown_fences(self) -> None:
        """I P A L L M Call: strips markdown fences."""
        payload = f"```json\n{_ipa_json()}\n```"
        llm = _make_llm(payload)
        call = _IPALLMCall(llm)
        ctx = WorkflowContext(workflow_id="test")
        result = await call.execute({"raw_text": "go north"}, ctx)
        assert "intent" in result

    @pytest.mark.asyncio
    async def test_raises_on_invalid_json(self) -> None:
        """I P A L L M Call: raises on invalid json."""
        llm = _make_llm("not valid json at all")
        call = _IPALLMCall(llm)
        ctx = WorkflowContext(workflow_id="test")
        with pytest.raises(Exception):
            await call.execute({"raw_text": "hello"}, ctx)


# ---------------------------------------------------------------------------
# _IPAFallback primitive
# ---------------------------------------------------------------------------


class TestIPAFallback:
    @pytest.mark.asyncio
    async def test_returns_unknown_intent(self) -> None:
        """I P A Fallback: returns unknown intent."""
        fallback = _IPAFallback()
        ctx = WorkflowContext(workflow_id="test")
        result = await fallback.execute({"raw_text": "something"}, ctx)
        assert result["intent"] == "unknown"
        assert result["intent_confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_normalizes_raw_text(self) -> None:
        """I P A Fallback: normalizes raw text."""
        fallback = _IPAFallback()
        ctx = WorkflowContext(workflow_id="test")
        result = await fallback.execute({"raw_text": "  HELLO WORLD  "}, ctx)
        assert result["normalized_text"] == "hello world"


# ---------------------------------------------------------------------------
# IPAAgent integration (mocked LLM)
# ---------------------------------------------------------------------------


class TestIPAAgent:
    @pytest.mark.asyncio
    async def test_explore_intent(self) -> None:
        """I P A Agent: explore intent."""
        agent = IPAAgent(llm=_make_llm(_ipa_json(intent="explore", confidence=0.9)))
        result = await agent.process("I go north into the forest", session_id="s1")
        assert result.intent == Intent.EXPLORE
        assert result.intent_confidence == pytest.approx(0.9)

    @pytest.mark.asyncio
    async def test_interact_intent_with_npc(self) -> None:
        """I P A Agent: interact intent with npc."""
        payload = _ipa_json(
            intent="interact",
            entities=[{"name": "blacksmith", "entity_type": "npc", "confidence": 0.95}],
        )
        agent = IPAAgent(llm=_make_llm(payload))
        result = await agent.process(
            "I want to talk to the blacksmith", session_id="s1"
        )
        assert result.intent == Intent.INTERACT
        assert result.npc_names == ["blacksmith"]

    @pytest.mark.asyncio
    async def test_safety_signal_propagated(self) -> None:
        """I P A Agent: safety signal propagated."""
        payload = _ipa_json(
            intent="journal",
            primary="sad",
            intensity=0.9,
            safety_signal=True,
        )
        agent = IPAAgent(llm=_make_llm(payload))
        result = await agent.process("I feel like giving up", session_id="s1")
        assert result.needs_safety_check
        assert result.emotional_tone.primary == "sad"

    @pytest.mark.asyncio
    async def test_unknown_intent_on_bad_value(self) -> None:
        """I P A Agent: unknown intent on bad value."""
        payload = _ipa_json(intent="fly_to_mars")  # not a valid Intent
        agent = IPAAgent(llm=_make_llm(payload))
        result = await agent.process("weird input", session_id="s1")
        assert result.intent == Intent.UNKNOWN

    @pytest.mark.asyncio
    async def test_fallback_on_llm_failure(self) -> None:
        """When LLM fails entirely, the FallbackPrimitive kicks in."""
        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=Exception("LLM unavailable"))
        agent = IPAAgent(llm=llm)
        # Should NOT raise
        result = await agent.process("anything", session_id="s1")
        assert isinstance(result, ProcessedInput)
        assert result.intent == Intent.UNKNOWN

    @pytest.mark.asyncio
    async def test_session_and_player_ids_attached(self) -> None:
        """I P A Agent: session and player ids attached."""
        agent = IPAAgent(llm=_make_llm(_ipa_json()))
        result = await agent.process(
            "go north",
            session_id="sess-99",
            player_id="player-42",
            location_id="loc-7",
        )
        assert result.session_id == "sess-99"
        assert result.player_id == "player-42"
        assert result.location_id == "loc-7"

    @pytest.mark.asyncio
    async def test_malformed_entity_skipped(self) -> None:
        # entity missing 'entity_type' key — should be skipped
        """I P A Agent: malformed entity skipped."""
        payload = json.dumps(
            {
                "intent": "explore",
                "intent_confidence": 0.8,
                "entities": [{"name": "place"}],  # no entity_type
                "emotional_tone": {
                    "primary": "neutral",
                    "intensity": 0.0,
                    "safety_signal": False,
                },
                "normalized_text": "explore",
            }
        )
        agent = IPAAgent(llm=_make_llm(payload))
        result = await agent.process("go somewhere")
        # Should still succeed, possibly with no entities or default entity_type
        assert isinstance(result, ProcessedInput)
