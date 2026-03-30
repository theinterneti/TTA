"""Unit tests for WBA (World Building Agent).

All external dependencies (WorldContextBuilder, Neo4j) are mocked.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.components.ipa.models import ProcessedInput
from src.components.wba.agent import WBAAgent, _minimal_world_context
from src.components.world_context.models import (
    LocationFact,
    NPCState,
    WorldContext,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_processed_input(
    session_id: str = "sess-1",
    player_id: str = "player-1",
    location_id: str | None = "loc-forest",
) -> ProcessedInput:
    return ProcessedInput(
        raw_text="go north",
        normalized_text="go north",
        session_id=session_id,
        player_id=player_id,
        location_id=location_id,
    )


def _make_world_context(location_id: str = "loc-forest") -> WorldContext:
    return WorldContext(
        location_id=location_id,
        location=LocationFact(
            id=location_id,
            name="Forest Clearing",
            description="Tall pines surround you.",
        ),
        npcs=[
            NPCState(id="npc-1", name="Old Hermit", role="guide", is_active=True)
        ],
    )


def _make_builder(world_context: WorldContext | None = None) -> Any:
    """Return a mock WorldContextBuilder."""
    builder = MagicMock()
    assembled = MagicMock()
    assembled.total_tokens = 500
    assembled.neo4j_available = True
    assembled.truncated_tiers = []
    assembled.neo4j_context = world_context
    builder.build = AsyncMock(return_value=assembled)
    return builder


# ---------------------------------------------------------------------------
# _minimal_world_context
# ---------------------------------------------------------------------------


class TestMinimalWorldContext:
    def test_returns_valid_world_context(self) -> None:
        ctx = _minimal_world_context("loc-unknown")
        assert ctx.location_id == "loc-unknown"
        assert ctx.location.id == "loc-unknown"
        assert len(ctx.npcs) == 0

    def test_location_name_is_sensible(self) -> None:
        ctx = _minimal_world_context("xyz")
        assert ctx.location.name == "Unknown Location"


# ---------------------------------------------------------------------------
# WBAAgent — no builder configured
# ---------------------------------------------------------------------------


class TestWBAAgentNoBuilder:
    @pytest.mark.asyncio
    async def test_returns_stub_when_no_builder(self) -> None:
        agent = WBAAgent(builder=None)
        pi = _make_processed_input(location_id="loc-x")
        result = await agent.build(pi)
        assert result.location_id == "loc-x"
        assert result.location.name == "Unknown Location"

    @pytest.mark.asyncio
    async def test_returns_stub_when_no_location_id(self) -> None:
        agent = WBAAgent(builder=MagicMock())
        pi = _make_processed_input(location_id=None)
        result = await agent.build(pi)
        assert result.location_id == "unknown"


# ---------------------------------------------------------------------------
# WBAAgent — with mocked builder
# ---------------------------------------------------------------------------


class TestWBAAgentWithBuilder:
    @pytest.mark.asyncio
    async def test_returns_world_context_from_builder(self) -> None:
        wc = _make_world_context("loc-forest")
        builder = _make_builder(world_context=wc)
        agent = WBAAgent(builder=builder)
        pi = _make_processed_input(location_id="loc-forest")
        result = await agent.build(pi)
        assert result.location_id == "loc-forest"
        assert result.location.name == "Forest Clearing"
        assert len(result.npcs) == 1

    @pytest.mark.asyncio
    async def test_builder_called_with_correct_args(self) -> None:
        wc = _make_world_context()
        builder = _make_builder(world_context=wc)
        agent = WBAAgent(builder=builder)
        pi = _make_processed_input(
            session_id="sess-99", player_id="player-7", location_id="loc-77"
        )
        await agent.build(pi)
        builder.build.assert_called_once_with(
            session_id="sess-99",
            location_id="loc-77",
            player_id="player-7",
            player_character=None,
        )

    @pytest.mark.asyncio
    async def test_falls_back_to_stub_when_no_neo4j_context(self) -> None:
        """When builder succeeds but neo4j_context is None → return stub."""
        builder = _make_builder(world_context=None)
        agent = WBAAgent(builder=builder)
        pi = _make_processed_input(location_id="loc-x")
        result = await agent.build(pi)
        assert result.location.name == "Unknown Location"

    @pytest.mark.asyncio
    async def test_falls_back_when_builder_raises(self) -> None:
        builder = MagicMock()
        builder.build = AsyncMock(side_effect=Exception("Neo4j unavailable"))
        agent = WBAAgent(builder=builder)
        pi = _make_processed_input(location_id="loc-x")
        result = await agent.build(pi)
        assert result.location.name == "Unknown Location"

    @pytest.mark.asyncio
    async def test_player_character_forwarded(self) -> None:
        wc = _make_world_context()
        builder = _make_builder(world_context=wc)
        agent = WBAAgent(builder=builder)
        pi = _make_processed_input(location_id="loc-x")
        char = {"name": "Ada", "class": "ranger"}
        await agent.build(pi, player_character=char)
        builder.build.assert_called_once_with(
            session_id="sess-1",
            location_id="loc-x",
            player_id="player-1",
            player_character=char,
        )
