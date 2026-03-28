"""Unit tests for NGA world-context wiring (#278).

Verifies that NGAAdapter.generate_narrative() calls WorldContextBuilder.build()
when a builder and location context are provided, injects the assembled context
into nga_input, and degrades gracefully when builder or Neo4j is unavailable.
Also verifies AgentAdapterFactory propagates world_context_builder to all three
adapter create methods.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agent_orchestration.adapters import (
    AgentAdapterFactory,
    NGAAdapter,
    RetryConfig,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_builder(
    total_tokens: int = 1234,
    neo4j_available: bool = True,
    truncated_tiers: list[str] | None = None,
    text: str = "ASSEMBLED WORLD CONTEXT",
) -> MagicMock:
    assembled = MagicMock()
    assembled.text = text
    assembled.total_tokens = total_tokens
    assembled.neo4j_available = neo4j_available
    assembled.truncated_tiers = truncated_tiers or []
    builder = MagicMock()
    builder.build = AsyncMock(return_value=assembled)
    return builder


# ---------------------------------------------------------------------------
# NGAAdapter construction
# ---------------------------------------------------------------------------


class TestNGAAdapterConstruction:
    def test_default_no_builder(self) -> None:
        adapter = NGAAdapter()
        assert adapter._builder is None

    def test_builder_stored(self) -> None:
        builder = _make_mock_builder()
        adapter = NGAAdapter(world_context_builder=builder)
        assert adapter._builder is builder

    def test_retry_config_defaults(self) -> None:
        adapter = NGAAdapter()
        assert adapter.retry_config is not None


# ---------------------------------------------------------------------------
# NGAAdapter mock fallback path (unavailable NGA)
# ---------------------------------------------------------------------------


class TestNGAAdapterMockPath:
    @pytest.mark.asyncio
    async def test_unavailable_returns_mock_story(self) -> None:
        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative("hello world")
        assert result["source"] == "mock_fallback"
        assert "story" in result

    @pytest.mark.asyncio
    async def test_unavailable_no_fallback_raises(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError

        adapter = NGAAdapter(fallback_to_mock=False)
        with pytest.raises(AgentCommunicationError, match="not available"):
            await adapter.generate_narrative("hello")

    @pytest.mark.asyncio
    async def test_world_context_meta_included_in_mock_result(self) -> None:
        """When builder returns context, meta should survive even in mock fallback."""
        builder = _make_mock_builder(total_tokens=500, neo4j_available=False)
        adapter = NGAAdapter(fallback_to_mock=True, world_context_builder=builder)
        result = await adapter.generate_narrative(
            "tell me a story",
            session_id="sess-1",
            location_id="loc-abc",
            player_id="player-1",
        )
        assert result["source"] == "mock_fallback"
        assert "world_context_meta" in result
        meta = result["world_context_meta"]
        assert meta["total_tokens"] == 500
        assert meta["neo4j_available"] is False

    @pytest.mark.asyncio
    async def test_no_builder_mock_result_has_no_meta(self) -> None:
        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative("story prompt")
        assert "world_context_meta" not in result


# ---------------------------------------------------------------------------
# Builder invocation behaviour
# ---------------------------------------------------------------------------


class TestNGAAdapterBuilderInvocation:
    @pytest.mark.asyncio
    async def test_builder_called_with_correct_params(self) -> None:
        builder = _make_mock_builder()
        adapter = NGAAdapter(fallback_to_mock=True, world_context_builder=builder)
        await adapter.generate_narrative(
            "enter the cave",
            session_id="sess-42",
            location_id="loc-cave",
            player_id="p-99",
            player_character={"name": "Aria"},
        )
        builder.build.assert_awaited_once_with(
            session_id="sess-42",
            location_id="loc-cave",
            player_id="p-99",
            player_character={"name": "Aria"},
        )

    @pytest.mark.asyncio
    async def test_no_location_id_skips_builder(self) -> None:
        builder = _make_mock_builder()
        adapter = NGAAdapter(fallback_to_mock=True, world_context_builder=builder)
        await adapter.generate_narrative("story", session_id="sess-1")
        builder.build.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_session_id_skips_builder(self) -> None:
        builder = _make_mock_builder()
        adapter = NGAAdapter(fallback_to_mock=True, world_context_builder=builder)
        await adapter.generate_narrative("story", location_id="loc-1")
        builder.build.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_builder_skips_assembly(self) -> None:
        """No builder → no error, result is still returned."""
        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative(
            "story",
            session_id="sess-1",
            location_id="loc-1",
        )
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_builder_exception_is_swallowed(self) -> None:
        """Builder failure degrades gracefully; NGA still runs (mock path here)."""
        builder = MagicMock()
        builder.build = AsyncMock(side_effect=RuntimeError("neo4j down"))
        adapter = NGAAdapter(fallback_to_mock=True, world_context_builder=builder)
        result = await adapter.generate_narrative(
            "story",
            session_id="sess-1",
            location_id="loc-1",
        )
        assert result["source"] == "mock_fallback"
        assert "story" in result


# ---------------------------------------------------------------------------
# AgentAdapterFactory propagation
# ---------------------------------------------------------------------------


class TestAgentAdapterFactoryBuilderPropagation:
    def test_factory_stores_builder(self) -> None:
        builder = _make_mock_builder()
        factory = AgentAdapterFactory(world_context_builder=builder)
        assert factory.world_context_builder is builder

    def test_factory_default_no_builder(self) -> None:
        factory = AgentAdapterFactory()
        assert factory.world_context_builder is None

    def test_create_ipa_adapter_receives_builder(self) -> None:
        builder = _make_mock_builder()
        factory = AgentAdapterFactory(world_context_builder=builder)
        ipa = factory.create_ipa_adapter()
        assert ipa._builder is builder

    def test_create_wba_adapter_receives_builder(self) -> None:
        builder = _make_mock_builder()
        factory = AgentAdapterFactory(world_context_builder=builder)
        wba = factory.create_wba_adapter()
        assert wba._builder is builder

    def test_create_nga_adapter_receives_builder(self) -> None:
        builder = _make_mock_builder()
        factory = AgentAdapterFactory(world_context_builder=builder)
        nga = factory.create_nga_adapter()
        assert nga._builder is builder

    def test_create_adapters_no_builder_all_none(self) -> None:
        factory = AgentAdapterFactory()
        assert factory.create_ipa_adapter()._builder is None
        assert factory.create_wba_adapter()._builder is None
        assert factory.create_nga_adapter()._builder is None

    def test_retry_config_propagated_to_nga(self) -> None:
        config = RetryConfig(max_retries=5)
        factory = AgentAdapterFactory(retry_config=config)
        nga = factory.create_nga_adapter()
        assert nga.retry_config.max_retries == 5
