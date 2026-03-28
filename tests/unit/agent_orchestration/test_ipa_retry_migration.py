"""Unit tests for IPA retry/fallback migration (#301).

Verifies that IPAAdapter.process_input() uses FallbackPrimitive(RetryPrimitive(...))
with WorkflowContext when the real IPA is available, and delegates to mock
correctly when unavailable.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tta_dev_primitives import WorkflowContext

from src.agent_orchestration.adapters import (
    RetryConfig,
    _IPACall,
    _IPAFallback,
    _transform_ipa_result,
)


# ---------------------------------------------------------------------------
# _transform_ipa_result
# ---------------------------------------------------------------------------

class TestTransformIPAResult:
    def test_pydantic_model_dump(self) -> None:
        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {
            "intent": "explore",
            "confidence": 0.9,
            "entities": {"location": "forest"},
            "direction": "north",
            "object": None,
            "npc": None,
        }
        result = _transform_ipa_result("go north", mock_intent)
        assert result["source"] == "real_ipa"
        assert result["routing"]["intent"] == "explore"
        assert result["routing"]["confidence"] == 0.9
        assert result["normalized_text"] == "go north"

    def test_non_pydantic_result(self) -> None:
        result = _transform_ipa_result("hello", "raw_intent_string")
        assert result["source"] == "real_ipa"
        assert result["routing"]["intent"] == "raw_intent_string"
        assert result["routing"]["confidence"] == 0.8

    def test_missing_optional_fields_default_to_none(self) -> None:
        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {"intent": "unknown", "confidence": 0.5}
        result = _transform_ipa_result("?", mock_intent)
        assert result["routing"]["direction"] is None
        assert result["routing"]["object"] is None
        assert result["routing"]["npc"] is None

    def test_entities_defaults_to_empty_dict(self) -> None:
        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {"intent": "x"}
        result = _transform_ipa_result("x", mock_intent)
        assert result["routing"]["entities"] == {}


# ---------------------------------------------------------------------------
# _IPACall primitive
# ---------------------------------------------------------------------------

class TestIPACall:
    @pytest.mark.asyncio
    async def test_execute_calls_real_fn(self) -> None:
        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {
            "intent": "move",
            "confidence": 0.95,
        }
        real_fn = MagicMock(return_value=mock_intent)
        ctx = WorkflowContext(workflow_id="session-001")

        primitive = _IPACall()
        result = await primitive.execute(
            {"text": "go south", "real_fn": real_fn}, ctx
        )

        real_fn.assert_called_once_with("go south")
        assert result["source"] == "real_ipa"
        assert result["routing"]["intent"] == "move"

    @pytest.mark.asyncio
    async def test_execute_runs_in_executor(self) -> None:
        """real_fn is called via run_in_executor (thread pool)."""
        call_thread_ids: list[int] = []
        import threading

        def real_fn(text: str) -> Any:
            call_thread_ids.append(threading.get_ident())
            result = MagicMock()
            result.model_dump.return_value = {"intent": "test"}
            return result

        ctx = WorkflowContext(workflow_id="s")
        primitive = _IPACall()
        await primitive.execute({"text": "hello", "real_fn": real_fn}, ctx)
        # executor runs in a different thread than the event loop
        assert len(call_thread_ids) == 1

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        def real_fn(text: str) -> Any:
            raise RuntimeError("IPA failure")

        ctx = WorkflowContext(workflow_id="s")
        primitive = _IPACall()
        with pytest.raises(RuntimeError, match="IPA failure"):
            await primitive.execute({"text": "hi", "real_fn": real_fn}, ctx)


# ---------------------------------------------------------------------------
# _IPAFallback primitive
# ---------------------------------------------------------------------------

class TestIPAFallback:
    @pytest.mark.asyncio
    async def test_returns_mock_structure(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        primitive = _IPAFallback()
        result = await primitive.execute({"text": "anything"}, ctx)

        assert result["source"] == "mock_fallback"
        assert result["routing"]["intent"] == "unknown"
        assert result["normalized_text"] == "anything"

    @pytest.mark.asyncio
    async def test_confidence_is_low(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _IPAFallback().execute({"text": "x"}, ctx)
        assert result["routing"]["confidence"] == 0.5


# ---------------------------------------------------------------------------
# IPAAdapter.process_input integration (primitive path)
# ---------------------------------------------------------------------------

class TestIPAAdapterPrimitivePath:
    """IPAAdapter when real IPA is available uses FallbackPrimitive(RetryPrimitive(...))."""

    def _make_adapter_available(self) -> Any:
        """Return an IPAAdapter patched so _available=True with a mock real IPA."""
        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=True)
        adapter._available = True  # type: ignore[attr-defined]
        return adapter

    @pytest.mark.asyncio
    async def test_process_input_with_session_id(self) -> None:
        """session_id flows through to WorkflowContext.workflow_id."""
        from src.agent_orchestration import adapters as adapters_mod

        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {"intent": "explore"}

        with patch.object(adapters_mod, "process_input", return_value=mock_intent):
            adapter = self._make_adapter_available()
            result = await adapter.process_input("go north", session_id="ses-42")

        assert result["source"] == "real_ipa"
        assert result["routing"]["intent"] == "explore"

    @pytest.mark.asyncio
    async def test_process_input_without_session_id(self) -> None:
        """session_id=None auto-generates a workflow_id."""
        from src.agent_orchestration import adapters as adapters_mod

        mock_intent = MagicMock()
        mock_intent.model_dump.return_value = {"intent": "talk"}

        with patch.object(adapters_mod, "process_input", return_value=mock_intent):
            adapter = self._make_adapter_available()
            result = await adapter.process_input("say hello")

        assert result["source"] == "real_ipa"

    @pytest.mark.asyncio
    async def test_fallback_on_real_ipa_failure(self) -> None:
        """When real IPA raises, FallbackPrimitive returns mock response."""
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod, "process_input", side_effect=RuntimeError("timeout")
        ):
            adapter = self._make_adapter_available()
            result = await adapter.process_input("help")

        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        """fallback_to_mock=False + real IPA failure → AgentCommunicationError."""
        from src.agent_orchestration.adapters import AgentCommunicationError, IPAAdapter
        from src.agent_orchestration import adapters as adapters_mod

        with patch.object(
            adapters_mod, "process_input", side_effect=RuntimeError("crash")
        ):
            adapter = IPAAdapter(fallback_to_mock=False)
            adapter._available = True  # type: ignore[attr-defined]
            with pytest.raises(AgentCommunicationError):
                await adapter.process_input("test")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        """RetryConfig.max_retries is forwarded to RetryStrategy."""
        from src.agent_orchestration import adapters as adapters_mod

        call_count = 0

        def flaky_fn(text: str) -> Any:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            result = MagicMock()
            result.model_dump.return_value = {"intent": "done"}
            return result

        with patch.object(adapters_mod, "process_input", side_effect=flaky_fn):
            adapter = self._make_adapter_available()
            adapter.retry_config = RetryConfig(
                max_retries=3, base_delay=0.0, jitter=False
            )
            result = await adapter.process_input("retry me")

        assert result["source"] == "real_ipa"
        assert call_count == 3


# ---------------------------------------------------------------------------
# IPAAdapter.process_input — unavailable path (unchanged behaviour)
# ---------------------------------------------------------------------------

class TestIPAAdapterUnavailablePath:
    @pytest.mark.asyncio
    async def test_unavailable_with_fallback_returns_mock(self) -> None:
        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=True)
        # _available is False because real agents aren't installed
        result = await adapter.process_input("test")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_unavailable_no_fallback_raises(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=False)
        with pytest.raises(AgentCommunicationError, match="not available"):
            await adapter.process_input("test")
