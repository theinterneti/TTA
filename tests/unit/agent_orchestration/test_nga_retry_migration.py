"""Unit tests for NGA retry/fallback migration (#303).

Verifies that NGAAdapter.generate_narrative() uses FallbackPrimitive(RetryPrimitive(...))
with WorkflowContext when the native NGA is available, and delegates to mock
correctly when unavailable.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    pytest.skip("ttadev.primitives not available", allow_module_level=True)

from src.agent_orchestration.adapters import (
    RetryConfig,
    _NGACall,
    _NGAFallback,
    _transform_nga_result,
)
from src.components.ipa.models import ProcessedInput
from src.components.world_context.models import LocationFact, WorldContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_world_context(location_id: str = "loc-1") -> WorldContext:
    return WorldContext(
        location_id=location_id,
        location=LocationFact(id=location_id, name="Forest"),
    )


def _make_processed_input() -> ProcessedInput:
    return ProcessedInput(raw_text="explore", normalized_text="explore")


# ---------------------------------------------------------------------------
# _transform_nga_result
# ---------------------------------------------------------------------------


class TestTransformNGAResult:
    def test_populates_all_fields(self) -> None:
        result = _transform_nga_result("explore", {"ctx": 1}, "The hero ventures forth.")
        assert result["source"] == "native_nga"
        assert result["story"] == "The hero ventures forth."
        assert result["raw"] == "The hero ventures forth."
        assert result["context_used"] is True

    def test_context_used_false_when_no_context(self) -> None:
        result = _transform_nga_result("prompt", None, "A story.")
        assert result["context_used"] is False

    def test_context_used_true_when_context_provided(self) -> None:
        result = _transform_nga_result("prompt", {"key": "val"}, "A story.")
        assert result["context_used"] is True

    def test_story_is_the_narrative_string(self) -> None:
        result = _transform_nga_result("p", None, "Once upon a time...")
        assert result["story"] == "Once upon a time..."

    def test_raw_matches_story(self) -> None:
        result = _transform_nga_result("p", None, "narrative text")
        assert result["raw"] == result["story"]


# ---------------------------------------------------------------------------
# _NGACall primitive
# ---------------------------------------------------------------------------


class TestNGACall:
    @pytest.mark.asyncio
    async def test_execute_calls_agent_generate(self) -> None:
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value="A dark forest awaits.")
        ctx = WorkflowContext(workflow_id="session-001")

        result = await _NGACall(mock_agent).execute(
            {
                "prompt": "explore",
                "context": {"world": "dark"},
                "processed_input": _make_processed_input(),
                "world_context": _make_world_context(),
            },
            ctx,
        )

        mock_agent.generate.assert_awaited_once()
        assert result["source"] == "native_nga"
        assert result["story"] == "A dark forest awaits."
        assert result["context_used"] is True

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(side_effect=RuntimeError("NGA failure"))
        ctx = WorkflowContext(workflow_id="s")
        with pytest.raises(RuntimeError, match="NGA failure"):
            await _NGACall(mock_agent).execute(
                {
                    "prompt": "hi",
                    "context": None,
                    "processed_input": _make_processed_input(),
                    "world_context": _make_world_context(),
                },
                ctx,
            )

    @pytest.mark.asyncio
    async def test_execute_no_context_gives_false_context_used(self) -> None:
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value="text")
        ctx = WorkflowContext(workflow_id="s")
        result = await _NGACall(mock_agent).execute(
            {
                "prompt": "p",
                "context": None,
                "processed_input": _make_processed_input(),
                "world_context": _make_world_context(),
            },
            ctx,
        )
        assert result["context_used"] is False


# ---------------------------------------------------------------------------
# _NGAFallback primitive
# ---------------------------------------------------------------------------


class TestNGAFallback:
    @pytest.mark.asyncio
    async def test_returns_mock_structure(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        primitive = _NGAFallback()
        result = await primitive.execute(
            {"prompt": "tell me a story", "context": None, "world_context_meta": {}},
            ctx,
        )
        assert result["source"] == "mock_fallback"
        assert "story" in result
        assert "tell me a story" in result["story"]

    @pytest.mark.asyncio
    async def test_context_used_false_when_no_context(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _NGAFallback().execute(
            {"prompt": "p", "context": None, "world_context_meta": {}}, ctx
        )
        assert result["context_used"] is False

    @pytest.mark.asyncio
    async def test_context_used_true_when_context_provided(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _NGAFallback().execute(
            {"prompt": "p", "context": {"key": "val"}, "world_context_meta": {}}, ctx
        )
        assert result["context_used"] is True

    @pytest.mark.asyncio
    async def test_world_context_meta_included_when_present(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        meta = {"total_tokens": 500, "neo4j_available": False, "truncated_tiers": []}
        result = await _NGAFallback().execute(
            {"prompt": "p", "context": None, "world_context_meta": meta}, ctx
        )
        assert result["world_context_meta"] == meta

    @pytest.mark.asyncio
    async def test_empty_meta_not_included(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _NGAFallback().execute(
            {"prompt": "p", "context": None, "world_context_meta": {}}, ctx
        )
        assert "world_context_meta" not in result

    @pytest.mark.asyncio
    async def test_prompt_truncated_in_story(self) -> None:
        long_prompt = "x" * 100
        ctx = WorkflowContext(workflow_id="s")
        result = await _NGAFallback().execute(
            {"prompt": long_prompt, "context": None, "world_context_meta": {}}, ctx
        )
        # story uses prompt[:64]
        assert len(result["story"]) < len(long_prompt) + 30


# ---------------------------------------------------------------------------
# NGAAdapter.generate_narrative — native agent path
# ---------------------------------------------------------------------------


class TestNGAAdapterNativePath:
    """NGAAdapter with injected mock native NGA agent."""

    @pytest.mark.asyncio
    async def test_generate_narrative_with_session_id(self) -> None:
        """session_id flows through to WorkflowContext.workflow_id."""
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value="The adventure begins.")

        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True, nga_agent=mock_agent)
        result = await adapter.generate_narrative("start", session_id="ses-99")

        assert result["source"] == "native_nga"
        assert result["story"] == "The adventure begins."

    @pytest.mark.asyncio
    async def test_generate_narrative_without_session_id(self) -> None:
        """session_id=None auto-generates a workflow_id."""
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value="Story text.")

        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True, nga_agent=mock_agent)
        result = await adapter.generate_narrative("continue")

        assert result["source"] == "native_nga"

    @pytest.mark.asyncio
    async def test_fallback_on_native_nga_failure(self) -> None:
        """When native NGA raises, FallbackPrimitive returns mock response."""
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(side_effect=RuntimeError("timeout"))

        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True, nga_agent=mock_agent)
        result = await adapter.generate_narrative("help")

        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        """fallback_to_mock=False + native NGA failure → AgentCommunicationError."""
        from src.agent_orchestration.adapters import AgentCommunicationError, NGAAdapter

        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(side_effect=RuntimeError("crash"))
        adapter = NGAAdapter(fallback_to_mock=False, nga_agent=mock_agent)
        with pytest.raises(AgentCommunicationError):
            await adapter.generate_narrative("test")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        """RetryConfig.max_retries is forwarded to RetryStrategy."""
        call_count = 0

        async def flaky_generate(pi: Any, wc: Any) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            return "done"

        mock_agent = MagicMock()
        mock_agent.generate = flaky_generate

        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(
            fallback_to_mock=True,
            nga_agent=mock_agent,
            retry_config=RetryConfig(max_retries=3, base_delay=0.0, jitter=False),
        )
        result = await adapter.generate_narrative("retry me")

        assert result["source"] == "native_nga"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_context_used_in_result(self) -> None:
        """context dict is reflected in context_used field."""
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value="Narrative.")

        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True, nga_agent=mock_agent)
        result = await adapter.generate_narrative(
            "continue", context={"scene": "forest"}
        )

        assert result["context_used"] is True


# ---------------------------------------------------------------------------
# NGAAdapter.generate_narrative — fallback path (agent fails at call time)
# ---------------------------------------------------------------------------


class TestNGAAdapterFallbackPath:
    @pytest.mark.asyncio
    async def test_fallback_returns_mock_on_agent_failure(self) -> None:
        from src.agent_orchestration.adapters import NGAAdapter

        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = NGAAdapter(fallback_to_mock=True, nga_agent=mock_agent)
        result = await adapter.generate_narrative("test")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_communication_error(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, NGAAdapter

        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = NGAAdapter(fallback_to_mock=False, nga_agent=mock_agent)
        with pytest.raises(AgentCommunicationError, match="NGA communication failed"):
            await adapter.generate_narrative("test")
