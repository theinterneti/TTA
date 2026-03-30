"""Unit tests for NGA (Narrative Generation Agent).

All LLM calls are mocked via AsyncMock so tests run offline and fast.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.components.ipa.models import EmotionalTone, Intent, ProcessedInput
from src.components.nga.agent import (
    NGAAgent,
    _NGAFallback,
    _NGALLMCall,
    _build_user_message,
)
from src.components.world_context.models import (
    ConnectedLocation,
    LocationFact,
    NPCState,
    WorldContext,
    WorldEventSummary,
    ZoneSummary,
)

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    from tta_dev_primitives import WorkflowContext  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_llm(response: str = "The world trembles softly.") -> Any:
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=response))
    return llm


def _simple_world_context(location_id: str = "loc-1") -> WorldContext:
    return WorldContext(
        location_id=location_id,
        location=LocationFact(
            id=location_id,
            name="Village Square",
            description="Cobblestones gleam after the rain.",
        ),
    )


def _rich_world_context() -> WorldContext:
    return WorldContext(
        location_id="loc-2",
        location=LocationFact(
            id="loc-2",
            name="Market",
            description="Stalls overflow with wares.",
        ),
        npcs=[
            NPCState(
                id="npc-1",
                name="Merchant",
                role="shopkeeper",
                emotional_state="cheerful",
                is_active=True,
            ),
        ],
        active_events=[
            WorldEventSummary(
                id="ev-1",
                name="Festival",
                description="Music fills the air.",
                is_active=True,
            )
        ],
        connected_locations=[
            ConnectedLocation(id="loc-3", name="North Gate", direction="north")
        ],
        zone=ZoneSummary(id="z-1", name="Trade District"),
    )


def _simple_processed_input(
    intent: Intent = Intent.EXPLORE,
    session_id: str = "sess-1",
) -> ProcessedInput:
    return ProcessedInput(
        raw_text="I look around",
        normalized_text="i look around",
        intent=intent,
        intent_confidence=0.9,
        session_id=session_id,
        player_id="player-1",
        location_id="loc-1",
    )


# ---------------------------------------------------------------------------
# _build_user_message
# ---------------------------------------------------------------------------


class TestBuildUserMessage:
    def test_includes_location_name(self) -> None:
        pi = _simple_processed_input()
        wc = _simple_world_context()
        msg = _build_user_message(pi, wc, history=None)
        assert "Village Square" in msg

    def test_includes_npc_names(self) -> None:
        pi = _simple_processed_input()
        wc = _rich_world_context()
        msg = _build_user_message(pi, wc, history=None)
        assert "Merchant" in msg

    def test_includes_events(self) -> None:
        pi = _simple_processed_input()
        wc = _rich_world_context()
        msg = _build_user_message(pi, wc, history=None)
        assert "Festival" in msg

    def test_includes_exits(self) -> None:
        pi = _simple_processed_input()
        wc = _rich_world_context()
        msg = _build_user_message(pi, wc, history=None)
        assert "North Gate" in msg

    def test_safety_signal_warning_included(self) -> None:
        pi = ProcessedInput(
            raw_text="I feel hopeless",
            normalized_text="i feel hopeless",
            emotional_tone=EmotionalTone(
                primary="sad", intensity=0.9, safety_signal=True
            ),
        )
        wc = _simple_world_context()
        msg = _build_user_message(pi, wc, history=None)
        assert "⚠" in msg or "Safety signal" in msg

    def test_history_appended(self) -> None:
        pi = _simple_processed_input()
        wc = _simple_world_context()
        history = ["Turn 1: walked north.", "Turn 2: met the guard."]
        msg = _build_user_message(pi, wc, history=history)
        assert "walked north" in msg

    def test_only_last_three_history_turns_used(self) -> None:
        pi = _simple_processed_input()
        wc = _simple_world_context()
        history = [f"Turn {i}" for i in range(10)]
        msg = _build_user_message(pi, wc, history=history)
        # First 7 should NOT be present; last 3 should be
        assert "Turn 0" not in msg
        assert "Turn 9" in msg


# ---------------------------------------------------------------------------
# _NGALLMCall primitive
# ---------------------------------------------------------------------------


class TestNGALLMCall:
    @pytest.mark.asyncio
    async def test_returns_stripped_content(self) -> None:
        llm = _make_llm("  The forest breathes.  ")
        call = _NGALLMCall(llm)
        ctx = WorkflowContext(workflow_id="test")
        result = await call.execute(
            {"system_prompt": "You are a narrator.", "user_message": "hello"},
            ctx,
        )
        assert result == "The forest breathes."

    @pytest.mark.asyncio
    async def test_raises_on_llm_failure(self) -> None:
        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=RuntimeError("timeout"))
        call = _NGALLMCall(llm)
        ctx = WorkflowContext(workflow_id="test")
        with pytest.raises(RuntimeError):
            await call.execute({"system_prompt": "s", "user_message": "u"}, ctx)


# ---------------------------------------------------------------------------
# _NGAFallback primitive
# ---------------------------------------------------------------------------


class TestNGAFallback:
    @pytest.mark.asyncio
    async def test_returns_safe_fallback_string(self) -> None:
        fallback = _NGAFallback()
        ctx = WorkflowContext(workflow_id="test")
        result = await fallback.execute({}, ctx)
        assert isinstance(result, str)
        assert len(result) > 10


# ---------------------------------------------------------------------------
# NGAAgent integration
# ---------------------------------------------------------------------------


class TestNGAAgent:
    @pytest.mark.asyncio
    async def test_generate_returns_narrative_string(self) -> None:
        agent = NGAAgent(llm=_make_llm("The sun sets over the valley."))
        pi = _simple_processed_input()
        wc = _simple_world_context()
        result = await agent.generate(pi, wc)
        assert result == "The sun sets over the valley."

    @pytest.mark.asyncio
    async def test_generate_with_rich_context(self) -> None:
        narrative = "The merchant waves at you warmly."
        agent = NGAAgent(llm=_make_llm(narrative))
        pi = _simple_processed_input(intent=Intent.INTERACT)
        wc = _rich_world_context()
        result = await agent.generate(pi, wc)
        assert result == narrative

    @pytest.mark.asyncio
    async def test_fallback_on_llm_failure(self) -> None:
        """When LLM fails entirely, FallbackPrimitive returns safe string."""
        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=Exception("LLM down"))
        agent = NGAAgent(llm=llm)
        pi = _simple_processed_input()
        wc = _simple_world_context()
        result = await agent.generate(pi, wc)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_history_passed_through(self) -> None:
        captured: list[Any] = []

        async def capture(messages: list) -> AIMessage:
            captured.append(messages)
            return AIMessage(content="story text")

        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=capture)

        agent = NGAAgent(llm=llm)
        pi = _simple_processed_input()
        wc = _simple_world_context()
        history = ["Earlier, you walked south."]
        await agent.generate(pi, wc, history=history)

        # The user message (HumanMessage) should contain history text
        messages = captured[0]
        user_content = messages[-1].content
        assert "walked south" in user_content
