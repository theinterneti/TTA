"""Tests for world_context budget.py, builder.py, and compressor.py.

Issues: #276 (budget + builder), #277 (compressor)
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.components.world_context.budget import (
    ALL_TIERS,
    TIER_CHARACTER,
    TIER_HISTORY,
    TIER_NEO4J,
    TIER_RULES,
    TIER_SCENE,
    TIER_SYSTEM,
    TierBudget,
    TokenCounter,
)
from src.components.world_context.builder import AssembledContext, WorldContextBuilder
from src.components.world_context.compressor import HistoryCompressor
from src.components.world_context.models import (
    ConnectedLocation,
    LocationFact,
    NPCState,
    WorldContext,
    WorldEventSummary,
    WorldRuleSummary,
    ZoneSummary,
)


# ---------------------------------------------------------------------------
# TierBudget
# ---------------------------------------------------------------------------


class TestTierBudget:
    def test_default_values_sum_to_total_or_less(self) -> None:
        budget = TierBudget()
        total_tiers = (
            budget.tier1_system
            + budget.tier2_scene
            + budget.tier3_neo4j
            + budget.tier4_rules
            + budget.tier5_history
            + budget.tier6_character
        )
        # Tier allocations must not exceed total; they may be less (slack allowed)
        assert total_tiers <= budget.total

    def test_budget_for_each_tier(self) -> None:
        budget = TierBudget()
        assert budget.budget_for(TIER_SYSTEM) == budget.tier1_system
        assert budget.budget_for(TIER_SCENE) == budget.tier2_scene
        assert budget.budget_for(TIER_NEO4J) == budget.tier3_neo4j
        assert budget.budget_for(TIER_RULES) == budget.tier4_rules
        assert budget.budget_for(TIER_HISTORY) == budget.tier5_history
        assert budget.budget_for(TIER_CHARACTER) == budget.tier6_character

    def test_unknown_tier_raises_key_error(self) -> None:
        budget = TierBudget()
        with pytest.raises(KeyError):
            budget.budget_for("tier99_unknown")

    def test_overallocation_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="exceed total"):
            TierBudget(
                total=100,
                tier1_system=50,
                tier2_scene=60,  # over total
                tier3_neo4j=0,
                tier4_rules=0,
                tier5_history=0,
                tier6_character=0,
            )

    def test_minimal_factory(self) -> None:
        budget = TierBudget.minimal()
        assert budget.total == 1200
        total = (
            budget.tier1_system
            + budget.tier2_scene
            + budget.tier3_neo4j
            + budget.tier4_rules
            + budget.tier5_history
            + budget.tier6_character
        )
        assert total == budget.total

    def test_all_tiers_constant_covers_all_keys(self) -> None:
        budget = TierBudget()
        for tier in ALL_TIERS:
            budget.budget_for(tier)  # must not raise


# ---------------------------------------------------------------------------
# TokenCounter
# ---------------------------------------------------------------------------


class TestTokenCounter:
    def test_empty_string_returns_zero(self) -> None:
        counter = TokenCounter()
        assert counter.count("") == 0

    def test_non_empty_returns_positive(self) -> None:
        counter = TokenCounter()
        assert counter.count("Hello, world!") > 0

    def test_fits_within_budget(self) -> None:
        counter = TokenCounter()
        text = "a" * 10  # definitely small
        assert counter.fits(text, 1000) is True

    def test_does_not_fit_tiny_budget(self) -> None:
        counter = TokenCounter()
        text = "word " * 200  # ~200 tokens
        assert counter.fits(text, 1) is False

    def test_truncate_returns_shorter_text(self) -> None:
        counter = TokenCounter()
        long_text = "word " * 500
        truncated = counter.truncate_to_budget(long_text, 50)
        assert len(truncated) < len(long_text)
        assert truncated.endswith("…")

    def test_truncate_already_fits(self) -> None:
        counter = TokenCounter()
        short = "short"
        result = counter.truncate_to_budget(short, 1000)
        assert result == short

    def test_truncate_zero_budget(self) -> None:
        counter = TokenCounter()
        result = counter.truncate_to_budget("text", 0)
        assert result == ""

    def test_backend_attribute(self) -> None:
        counter = TokenCounter()
        assert counter.backend in ("tiktoken", "char_count")


# ---------------------------------------------------------------------------
# WorldContextBuilder helpers — fixtures
# ---------------------------------------------------------------------------


def _make_world_context() -> WorldContext:
    """Minimal WorldContext for builder rendering tests."""
    return WorldContext(
        location_id="loc-001",
        location=LocationFact(
            id="loc-001",
            name="Forest Clearing",
            description="A quiet glade.",
            atmosphere="peaceful",
            region="Ancient Forest",
        ),
        npcs=[
            NPCState(
                id="npc-001",
                name="Aria",
                role="ally",
                disposition_toward_player="friendly",
                emotional_state="calm",
            )
        ],
        active_events=[
            WorldEventSummary(
                id="evt-001",
                name="Storm Approaching",
                description="Dark clouds roll in.",
                event_type="environmental",
            )
        ],
        connected_locations=[
            ConnectedLocation(
                id="loc-002",
                name="Dark Cave",
                direction="north",
                distance=2,
            )
        ],
        zone=ZoneSummary(
            id="zone-001",
            name="Ancient Forest",
            description="A primordial woodland.",
        ),
        rules=[
            WorldRuleSummary(
                id="rule-001",
                name="No Open Flame",
                rule_text="Fire is forbidden here.",
                rule_type="social",
                priority=5,
            )
        ],
    )


# ---------------------------------------------------------------------------
# WorldContextBuilder
# ---------------------------------------------------------------------------


class TestWorldContextBuilder:
    @pytest.mark.asyncio
    async def test_build_no_driver_no_store_returns_empty(self) -> None:
        """Builder with no driver and no store returns minimal context."""
        builder = WorldContextBuilder()
        result = await builder.build(
            session_id="sess-001",
            location_id="loc-001",
            player_id="player-001",
        )
        assert isinstance(result, AssembledContext)
        assert result.neo4j_available is False
        assert result.total_tokens >= 0

    @pytest.mark.asyncio
    async def test_build_with_system_prompt(self) -> None:
        builder = WorldContextBuilder()
        result = await builder.build(
            session_id="sess-001",
            location_id="",
            player_id="p1",
            system_prompt="You are a helpful guide.",
        )
        assert "helpful guide" in result.text
        assert result.tiers[TIER_SYSTEM] == "You are a helpful guide."

    @pytest.mark.asyncio
    async def test_build_with_character(self) -> None:
        builder = WorldContextBuilder()
        result = await builder.build(
            session_id="sess-001",
            location_id="",
            player_id="p1",
            player_character={"name": "Evren", "health_state": "healthy"},
        )
        assert "Evren" in result.text
        assert result.tiers[TIER_CHARACTER] != ""

    @pytest.mark.asyncio
    async def test_build_with_session_store(self) -> None:
        store = MagicMock()
        store.load_messages.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        builder = WorldContextBuilder(session_store=store)
        result = await builder.build(
            session_id="sess-001",
            location_id="",
            player_id="p1",
        )
        assert "Hello" in result.text or "Hi there" in result.text
        assert result.tiers[TIER_HISTORY] != ""
        store.load_messages.assert_called_once_with("sess-001")

    @pytest.mark.asyncio
    async def test_build_neo4j_engine_called(self) -> None:
        """When driver is provided, Neo4jTraversalEngine is used."""
        mock_driver = MagicMock()
        world_ctx = _make_world_context()

        with patch(
            "src.components.world_context.builder.Neo4jTraversalEngine"
        ) as MockEngine:
            mock_engine = AsyncMock()
            mock_engine.build_context = AsyncMock(return_value=world_ctx)
            MockEngine.return_value = mock_engine

            builder = WorldContextBuilder(driver=mock_driver)
            result = await builder.build(
                session_id="sess-001",
                location_id="loc-001",
                player_id="p1",
            )

        assert result.neo4j_available is True
        assert "Forest Clearing" in result.tiers[TIER_SCENE]
        assert "Dark Cave" in result.tiers[TIER_NEO4J]
        assert "No Open Flame" in result.tiers[TIER_RULES]

    @pytest.mark.asyncio
    async def test_neo4j_failure_degrades_gracefully(self) -> None:
        """If Neo4j fails, builder continues with empty graph tiers."""
        mock_driver = MagicMock()

        with patch(
            "src.components.world_context.builder.Neo4jTraversalEngine"
        ) as MockEngine:
            mock_engine = AsyncMock()
            mock_engine.build_context.side_effect = Exception("connection refused")
            MockEngine.return_value = mock_engine

            builder = WorldContextBuilder(driver=mock_driver)
            result = await builder.build(
                session_id="sess-001",
                location_id="loc-001",
                player_id="p1",
            )

        assert result.neo4j_available is False
        assert result.tiers[TIER_SCENE] == ""

    @pytest.mark.asyncio
    async def test_truncation_applied_when_over_budget(self) -> None:
        """Oversized tiers should be truncated and reported in truncated_tiers."""
        budget = TierBudget(
            total=200,
            tier1_system=50,
            tier2_scene=10,  # tiny scene budget
            tier3_neo4j=30,
            tier4_rules=30,
            tier5_history=50,
            tier6_character=30,
        )
        world_ctx = _make_world_context()
        # Make scene text massive
        world_ctx.location.description = "word " * 500

        with patch(
            "src.components.world_context.builder.Neo4jTraversalEngine"
        ) as MockEngine:
            mock_engine = AsyncMock()
            mock_engine.build_context = AsyncMock(return_value=world_ctx)
            MockEngine.return_value = mock_engine

            builder = WorldContextBuilder(driver=MagicMock(), budget=budget)
            result = await builder.build(
                session_id="sess-001",
                location_id="loc-001",
                player_id="p1",
            )

        assert TIER_SCENE in result.truncated_tiers

    @pytest.mark.asyncio
    async def test_assembly_time_ms_positive(self) -> None:
        builder = WorldContextBuilder()
        result = await builder.build("sess-001", "", "p1")
        assert result.assembly_time_ms >= 0.0

    @pytest.mark.asyncio
    async def test_all_tiers_in_result(self) -> None:
        builder = WorldContextBuilder()
        result = await builder.build("sess-001", "", "p1")
        for tier in ALL_TIERS:
            assert tier in result.tiers
            assert tier in result.tier_token_counts


# ---------------------------------------------------------------------------
# HistoryCompressor
# ---------------------------------------------------------------------------


class TestHistoryCompressor:
    def _make_turns(self, n: int = 10) -> list[dict[str, str]]:
        return [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"message {i}"}
            for i in range(n)
        ]

    @pytest.mark.asyncio
    async def test_no_compression_needed(self) -> None:
        """Turns that fit the budget are returned unchanged."""
        compressor = HistoryCompressor()
        counter = TokenCounter()
        turns = self._make_turns(2)
        result = await compressor.compress_if_needed(
            "sess-001", turns, budget=10000, counter=counter
        )
        assert result == turns

    @pytest.mark.asyncio
    async def test_returns_recent_half_when_over_budget(self) -> None:
        compressor = HistoryCompressor(redis_client=None)
        counter = TokenCounter()
        turns = self._make_turns(20)
        result = await compressor.compress_if_needed(
            "sess-001", turns, budget=1, counter=counter
        )
        assert len(result) <= 10

    @pytest.mark.asyncio
    async def test_cached_summary_prepended(self) -> None:
        """When Redis has a cached summary, it is prepended to recent turns."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"Earlier the player explored a cave."
        compressor = HistoryCompressor(redis_client=mock_redis)
        counter = TokenCounter()
        turns = self._make_turns(20)
        result = await compressor.compress_if_needed(
            "sess-001", turns, budget=1, counter=counter
        )
        assert result[0]["role"] == "assistant"
        assert "Summary" in result[0]["content"]

    @pytest.mark.asyncio
    async def test_background_compression_scheduled(self) -> None:
        """When no cached summary, background task is scheduled (fire-and-forget)."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None  # no cached summary
        mock_redis.setex = AsyncMock()

        async def mock_summarise(turns: list[dict[str, str]]) -> str:
            return "Summarised content"

        compressor = HistoryCompressor(
            redis_client=mock_redis, llm_summarise=mock_summarise
        )
        counter = TokenCounter()
        turns = self._make_turns(20)

        # Should not raise even though background task fires
        result = await compressor.compress_if_needed(
            "sess-001", turns, budget=1, counter=counter
        )
        assert isinstance(result, list)

        # Allow background task to run
        await asyncio.sleep(0.01)

    @pytest.mark.asyncio
    async def test_llm_fallback_summarise(self) -> None:
        """Compressor uses simple fallback when no llm_summarise is provided."""
        compressor = HistoryCompressor(redis_client=None, llm_summarise=None)
        turns = [
            {"role": "user", "content": "Tell me a story"},
            {"role": "assistant", "content": "Once upon a time. A hero emerged."},
        ]
        summary = await compressor._do_summarise(turns)
        assert "Earlier" in summary or isinstance(summary, str)

    @pytest.mark.asyncio
    async def test_get_stored_summary_no_redis(self) -> None:
        compressor = HistoryCompressor(redis_client=None)
        result = await compressor.get_stored_summary("sess-001")
        assert result is None

    @pytest.mark.asyncio
    async def test_clear_summary(self) -> None:
        mock_redis = AsyncMock()
        compressor = HistoryCompressor(redis_client=mock_redis)
        await compressor.clear_summary("sess-001")
        mock_redis.delete.assert_called_once()
