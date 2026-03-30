"""Unit tests for WBA retry/fallback migration (#302).

Verifies that WBAAdapter.process_world_request() uses
FallbackPrimitive(RetryPrimitive(...)) with WorkflowContext.
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
    _WBACall,
    _WBAFallback,
    _transform_wba_result,
)


# ---------------------------------------------------------------------------
# _transform_wba_result
# ---------------------------------------------------------------------------

class TestTransformWBAResult:
    def test_populates_all_fields(self) -> None:
        raw = {"world_state": {"id": "w1", "regions": ["north"]}}
        result = _transform_wba_result("w1", None, raw)
        assert result["source"] == "real_wba"
        assert result["world_id"] == "w1"
        assert result["world_state"] == raw["world_state"]
        assert result["updated"] is False
        assert result["cached"] is False

    def test_updated_true_when_updates_provided(self) -> None:
        result = _transform_wba_result("w1", {"fog": True}, {"world_state": {}})
        assert result["updated"] is True

    def test_missing_world_state_defaults_to_empty(self) -> None:
        result = _transform_wba_result("w1", None, {})
        assert result["world_state"] == {}

    def test_raw_result_preserved(self) -> None:
        raw = {"world_state": {}, "extra_field": "value"}
        result = _transform_wba_result("w1", None, raw)
        assert result["raw_result"] is raw


# ---------------------------------------------------------------------------
# _WBACall primitive
# ---------------------------------------------------------------------------

class TestWBACall:
    @pytest.mark.asyncio
    async def test_execute_calls_wba_process(self) -> None:
        wba_instance = MagicMock()
        wba_instance.process = MagicMock(
            return_value={"world_state": {"id": "w1"}}
        )
        ctx = WorkflowContext(workflow_id="ses-1")
        input_data: dict[str, Any] = {
            "wba_instance": wba_instance,
            "wba_input": {"world_id": "w1", "action": "fetch", "updates": {}},
            "world_id": "w1",
            "updates": None,
        }

        result = await _WBACall().execute(input_data, ctx)

        wba_instance.process.assert_called_once()
        assert result["source"] == "real_wba"
        assert result["world_id"] == "w1"

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        wba_instance = MagicMock()
        wba_instance.process = MagicMock(side_effect=RuntimeError("WBA down"))
        ctx = WorkflowContext(workflow_id="s")
        input_data: dict[str, Any] = {
            "wba_instance": wba_instance,
            "wba_input": {},
            "world_id": "w1",
            "updates": None,
        }
        with pytest.raises(RuntimeError, match="WBA down"):
            await _WBACall().execute(input_data, ctx)


# ---------------------------------------------------------------------------
# _WBAFallback primitive
# ---------------------------------------------------------------------------

class TestWBAFallback:
    @pytest.mark.asyncio
    async def test_returns_mock_structure_no_updates(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _WBAFallback().execute(
            {"world_id": "w42", "updates": None}, ctx
        )
        assert result["source"] == "mock_fallback"
        assert result["world_id"] == "w42"
        assert result["updated"] is False
        assert result["world_state"]["id"] == "w42"
        assert result["world_state"]["regions"] == []

    @pytest.mark.asyncio
    async def test_updates_merged_into_world_state(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        updates = {"fog": True, "danger_level": 3}
        result = await _WBAFallback().execute(
            {"world_id": "w1", "updates": updates}, ctx
        )
        assert result["updated"] is True
        assert result["world_state"]["fog"] is True
        assert result["world_state"]["danger_level"] == 3


# ---------------------------------------------------------------------------
# WBAAdapter.process_world_request — primitive path
# ---------------------------------------------------------------------------

class TestWBAAdapterPrimitivePath:
    def _make_adapter_available(self) -> Any:
        from src.agent_orchestration.adapters import WBAAdapter

        mock_wba = MagicMock()
        mock_wba.process = MagicMock(
            return_value={"world_state": {"id": "w1"}}
        )
        adapter = WBAAdapter(fallback_to_mock=True)
        adapter._available = True  # type: ignore[attr-defined]
        adapter._wba_instance = mock_wba  # type: ignore[attr-defined]
        return adapter

    @pytest.mark.asyncio
    async def test_process_world_request_with_session_id(self) -> None:
        adapter = self._make_adapter_available()
        result = await adapter.process_world_request("w1", session_id="ses-99")
        assert result["source"] == "real_wba"
        assert result["world_id"] == "w1"

    @pytest.mark.asyncio
    async def test_process_world_request_without_session_id(self) -> None:
        adapter = self._make_adapter_available()
        result = await adapter.process_world_request("w2")
        assert result["source"] == "real_wba"

    @pytest.mark.asyncio
    async def test_process_world_request_with_updates(self) -> None:
        adapter = self._make_adapter_available()
        result = await adapter.process_world_request(
            "w1", updates={"weather": "stormy"}
        )
        assert result["updated"] is True
        assert result["source"] == "real_wba"

    @pytest.mark.asyncio
    async def test_fallback_on_wba_failure(self) -> None:
        adapter = self._make_adapter_available()
        adapter._wba_instance.process = MagicMock(  # type: ignore[union-attr]
            side_effect=RuntimeError("timeout")
        )
        result = await adapter.process_world_request("w1")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, WBAAdapter

        mock_wba = MagicMock()
        mock_wba.process = MagicMock(side_effect=RuntimeError("crash"))
        adapter = WBAAdapter(fallback_to_mock=False)
        adapter._available = True  # type: ignore[attr-defined]
        adapter._wba_instance = mock_wba  # type: ignore[attr-defined]

        with pytest.raises(AgentCommunicationError):
            await adapter.process_world_request("w1")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        call_count = 0

        def flaky_process(wba_input: dict) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            return {"world_state": {"id": "w1"}}

        mock_wba = MagicMock()
        mock_wba.process = flaky_process
        adapter = WBAAdapter(
            fallback_to_mock=True,
            retry_config=RetryConfig(max_retries=3, base_delay=0.0, jitter=False),
        )
        adapter._available = True  # type: ignore[attr-defined]
        adapter._wba_instance = mock_wba  # type: ignore[attr-defined]

        result = await adapter.process_world_request("w1")
        assert result["source"] == "real_wba"
        assert call_count == 3


# ---------------------------------------------------------------------------
# WBAAdapter — unavailable path (unchanged behaviour)
# ---------------------------------------------------------------------------

class TestWBAAdapterUnavailablePath:
    @pytest.mark.asyncio
    async def test_unavailable_with_fallback_returns_mock(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True)
        result = await adapter.process_world_request("w1")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_unavailable_no_fallback_raises(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=False)
        with pytest.raises(AgentCommunicationError, match="not available"):
            await adapter.process_world_request("w1")

    @pytest.mark.asyncio
    async def test_mock_applies_updates_to_world_state(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True)
        result = await adapter.process_world_request(
            "w1", updates={"danger": 5}
        )
        assert result["world_state"]["danger"] == 5
        assert result["updated"] is True
