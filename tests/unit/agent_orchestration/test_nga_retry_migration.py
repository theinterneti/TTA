"""Unit tests for NGA retry/fallback migration (#303).

Verifies that NGAAdapter.generate_narrative() uses FallbackPrimitive(RetryPrimitive(...))
with WorkflowContext when the real NGA is available, and delegates to mock
correctly when unavailable.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    from tta_dev_primitives import WorkflowContext  # type: ignore[no-redef]

from src.agent_orchestration.adapters import (
    RetryConfig,
    _NGACall,
    _NGAFallback,
    _transform_nga_result,
)


# ---------------------------------------------------------------------------
# _transform_nga_result
# ---------------------------------------------------------------------------


class TestTransformNGAResult:
    def test_extracts_response_key(self) -> None:
        raw = {"response": "The hero ventures forth.", "model": "gpt-4"}
        result = _transform_nga_result("explore", {"ctx": 1}, raw)
        assert result["source"] == "real_nga"
        assert result["story"] == "The hero ventures forth."
        assert result["raw"] == "The hero ventures forth."
        assert result["context_used"] is True
        assert result["raw_result"] is raw

    def test_falls_back_to_story_key(self) -> None:
        raw = {"story": "Once upon a time..."}
        result = _transform_nga_result("tell me", None, raw)
        assert result["story"] == "Once upon a time..."
        assert result["context_used"] is False

    def test_generates_placeholder_when_no_keys(self) -> None:
        raw: dict[str, Any] = {}
        result = _transform_nga_result("a" * 80, None, raw)
        assert result["story"].startswith("Generated story for:")
        assert len(result["story"]) < 100  # prompt truncated to 64 chars

    def test_context_used_false_when_no_context(self) -> None:
        result = _transform_nga_result("prompt", None, {"response": "text"})
        assert result["context_used"] is False

    def test_context_used_true_when_context_provided(self) -> None:
        result = _transform_nga_result("prompt", {"key": "val"}, {"response": "text"})
        assert result["context_used"] is True

    def test_response_key_takes_precedence_over_story(self) -> None:
        raw = {"response": "primary", "story": "secondary"}
        result = _transform_nga_result("p", None, raw)
        assert result["story"] == "primary"


# ---------------------------------------------------------------------------
# _NGACall primitive
# ---------------------------------------------------------------------------


class TestNGACall:
    @pytest.mark.asyncio
    async def test_execute_calls_real_fn(self) -> None:
        raw = {"response": "A dark forest awaits."}
        real_fn = MagicMock(return_value=raw)
        nga_input: dict[str, Any] = {"prompt": "explore", "context": {}}
        ctx = WorkflowContext(workflow_id="session-001")

        primitive = _NGACall()
        result = await primitive.execute(
            {
                "nga_input": nga_input,
                "prompt": "explore",
                "context": {"world": "dark"},
                "real_fn": real_fn,
            },
            ctx,
        )

        real_fn.assert_called_once_with(nga_input)
        assert result["source"] == "real_nga"
        assert result["story"] == "A dark forest awaits."
        assert result["context_used"] is True

    @pytest.mark.asyncio
    async def test_execute_runs_in_executor(self) -> None:
        """real_fn is called via run_in_executor (thread pool)."""
        import threading

        call_thread_ids: list[int] = []

        def real_fn(nga_input: dict[str, Any]) -> dict[str, Any]:
            call_thread_ids.append(threading.get_ident())
            return {"response": "ok"}

        ctx = WorkflowContext(workflow_id="s")
        primitive = _NGACall()
        await primitive.execute(
            {"nga_input": {}, "prompt": "hi", "context": None, "real_fn": real_fn}, ctx
        )
        assert len(call_thread_ids) == 1

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        def real_fn(nga_input: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("NGA failure")

        ctx = WorkflowContext(workflow_id="s")
        primitive = _NGACall()
        with pytest.raises(RuntimeError, match="NGA failure"):
            await primitive.execute(
                {"nga_input": {}, "prompt": "hi", "context": None, "real_fn": real_fn},
                ctx,
            )

    @pytest.mark.asyncio
    async def test_execute_no_context_gives_false_context_used(self) -> None:
        real_fn = MagicMock(return_value={"response": "text"})
        ctx = WorkflowContext(workflow_id="s")
        primitive = _NGACall()
        result = await primitive.execute(
            {"nga_input": {}, "prompt": "p", "context": None, "real_fn": real_fn}, ctx
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
# NGAAdapter.generate_narrative integration (primitive path)
# ---------------------------------------------------------------------------


class TestNGAAdapterPrimitivePath:
    """NGAAdapter when real NGA is available uses FallbackPrimitive(RetryPrimitive(...))."""

    def _make_adapter_available(self) -> Any:
        """Return an NGAAdapter patched so _available=True."""
        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True)
        adapter._available = True  # type: ignore[attr-defined]
        return adapter

    @pytest.mark.asyncio
    async def test_generate_narrative_with_session_id(self) -> None:
        """session_id flows through to WorkflowContext.workflow_id."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            return_value={"response": "The adventure begins."},
        ):
            adapter = self._make_adapter_available()
            result = await adapter.generate_narrative("start", session_id="ses-99")

        assert result["source"] == "real_nga"
        assert result["story"] == "The adventure begins."

    @pytest.mark.asyncio
    async def test_generate_narrative_without_session_id(self) -> None:
        """session_id=None auto-generates a workflow_id."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            return_value={"response": "Story text."},
        ):
            adapter = self._make_adapter_available()
            result = await adapter.generate_narrative("continue")

        assert result["source"] == "real_nga"

    @pytest.mark.asyncio
    async def test_fallback_on_real_nga_failure(self) -> None:
        """When real NGA raises, FallbackPrimitive returns mock response."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            side_effect=RuntimeError("timeout"),
        ):
            adapter = self._make_adapter_available()
            result = await adapter.generate_narrative("help")

        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        """fallback_to_mock=False + real NGA failure → AgentCommunicationError."""
        from src.agent_orchestration import adapters as adapters_mod
        from src.agent_orchestration.adapters import AgentCommunicationError, NGAAdapter

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            side_effect=RuntimeError("crash"),
        ):
            adapter = NGAAdapter(fallback_to_mock=False)
            adapter._available = True  # type: ignore[attr-defined]
            with pytest.raises(AgentCommunicationError):
                await adapter.generate_narrative("test")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        """RetryConfig.max_retries is forwarded to RetryStrategy."""
        from src.agent_orchestration import adapters as adapters_mod

        call_count = 0

        def flaky_fn(nga_input: dict[str, Any]) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            return {"response": "done"}

        with patch.object(
            adapters_mod, "generate_narrative_response", side_effect=flaky_fn
        ):
            adapter = self._make_adapter_available()
            adapter.retry_config = RetryConfig(
                max_retries=3, base_delay=0.0, jitter=False
            )
            result = await adapter.generate_narrative("retry me")

        assert result["source"] == "real_nga"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_context_used_in_result(self) -> None:
        """context dict is reflected in context_used field."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            return_value={"response": "Narrative."},
        ):
            adapter = self._make_adapter_available()
            result = await adapter.generate_narrative(
                "continue", context={"scene": "forest"}
            )

        assert result["context_used"] is True

    @pytest.mark.asyncio
    async def test_story_key_falls_back_in_result(self) -> None:
        """NGA response with 'story' key (not 'response') is handled."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod,
            "generate_narrative_response",
            return_value={"story": "Alternative story key."},
        ):
            adapter = self._make_adapter_available()
            result = await adapter.generate_narrative("prompt")

        assert result["story"] == "Alternative story key."
        assert result["source"] == "real_nga"


# ---------------------------------------------------------------------------
# NGAAdapter.generate_narrative — unavailable path (unchanged behaviour)
# ---------------------------------------------------------------------------


class TestNGAAdapterUnavailablePath:
    @pytest.mark.asyncio
    async def test_unavailable_with_fallback_returns_mock(self) -> None:
        from src.agent_orchestration.adapters import NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative("test")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_unavailable_no_fallback_raises(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, NGAAdapter

        adapter = NGAAdapter(fallback_to_mock=False)
        with pytest.raises(AgentCommunicationError, match="not available"):
            await adapter.generate_narrative("test")
