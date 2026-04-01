"""Unit tests for WBA retry/fallback migration (#302).

Verifies that WBAAdapter.process_world_request() uses
FallbackPrimitive(RetryPrimitive(...)) with WorkflowContext.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    pytest.skip("ttadev.primitives not available", allow_module_level=True)

from src.agent_orchestration.adapters import (
    RetryConfig,
    _WBACall,
    _WBAFallback,
    _transform_wba_result,
)
from src.components.ipa.models import ProcessedInput
from src.components.world_context.models import LocationFact, WorldContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_world_context(location_id: str = "loc-1", name: str = "Forest") -> WorldContext:
    return WorldContext(
        location_id=location_id,
        location=LocationFact(id=location_id, name=name),
    )


def _make_processed_input() -> ProcessedInput:
    return ProcessedInput(raw_text="explore", normalized_text="explore")


# ---------------------------------------------------------------------------
# _transform_wba_result
# ---------------------------------------------------------------------------


class TestTransformWBAResult:
    def test_populates_all_fields(self) -> None:
        wc = _make_world_context("w1")
        result = _transform_wba_result("w1", None, wc)
        assert result["source"] == "native_wba"
        assert result["world_id"] == "w1"
        assert result["updated"] is False
        assert result["cached"] is False
        assert "world_state" in result

    def test_updated_true_when_updates_provided(self) -> None:
        wc = _make_world_context("w1")
        result = _transform_wba_result("w1", {"fog": True}, wc)
        assert result["updated"] is True

    def test_world_state_contains_location(self) -> None:
        wc = _make_world_context("w1", name="Dark Cave")
        result = _transform_wba_result("w1", None, wc)
        assert result["world_state"]["location"]["name"] == "Dark Cave"

    def test_world_context_preserved(self) -> None:
        wc = _make_world_context("w1")
        result = _transform_wba_result("w1", None, wc)
        assert result["world_context"] is wc


# ---------------------------------------------------------------------------
# _WBACall primitive
# ---------------------------------------------------------------------------


class TestWBACall:
    @pytest.mark.asyncio
    async def test_execute_calls_agent_build(self) -> None:
        wc = _make_world_context("w1")
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(return_value=wc)
        ctx = WorkflowContext(workflow_id="ses-1")
        input_data = {
            "world_id": "w1",
            "updates": None,
            "processed_input": _make_processed_input(),
        }

        result = await _WBACall(mock_agent).execute(input_data, ctx)

        mock_agent.build.assert_awaited_once()
        assert result["source"] == "native_wba"
        assert result["world_id"] == "w1"

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("WBA down"))
        ctx = WorkflowContext(workflow_id="s")
        input_data = {
            "world_id": "w1",
            "updates": None,
            "processed_input": _make_processed_input(),
        }
        with pytest.raises(RuntimeError, match="WBA down"):
            await _WBACall(mock_agent).execute(input_data, ctx)


# ---------------------------------------------------------------------------
# _WBAFallback primitive
# ---------------------------------------------------------------------------


class TestWBAFallback:
    @pytest.mark.asyncio
    async def test_returns_mock_structure_no_updates(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _WBAFallback().execute({"world_id": "w42", "updates": None}, ctx)
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
# WBAAdapter.process_world_request — native agent path
# ---------------------------------------------------------------------------


class TestWBAAdapterNativePath:
    """WBAAdapter with injected mock native WBA agent."""

    @pytest.mark.asyncio
    async def test_process_world_request_with_session_id(self) -> None:
        wc = _make_world_context("w1")
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(return_value=wc)

        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w1", session_id="ses-99")
        assert result["source"] == "native_wba"
        assert result["world_id"] == "w1"

    @pytest.mark.asyncio
    async def test_process_world_request_without_session_id(self) -> None:
        wc = _make_world_context("w2")
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(return_value=wc)

        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w2")
        assert result["source"] == "native_wba"

    @pytest.mark.asyncio
    async def test_process_world_request_with_updates(self) -> None:
        wc = _make_world_context("w1")
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(return_value=wc)

        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w1", updates={"weather": "stormy"})
        assert result["updated"] is True
        assert result["source"] == "native_wba"

    @pytest.mark.asyncio
    async def test_fallback_on_wba_failure(self) -> None:
        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("timeout"))

        from src.agent_orchestration.adapters import WBAAdapter

        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w1")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, WBAAdapter

        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("crash"))
        adapter = WBAAdapter(fallback_to_mock=False, wba_agent=mock_agent)
        with pytest.raises(AgentCommunicationError):
            await adapter.process_world_request("w1")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        call_count = 0
        wc = _make_world_context("w1")

        async def flaky_build(pi: ProcessedInput) -> WorldContext:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            return wc

        mock_agent = MagicMock()
        mock_agent.build = flaky_build
        adapter = WBAAdapter(
            fallback_to_mock=True,
            wba_agent=mock_agent,
            retry_config=RetryConfig(max_retries=3, base_delay=0.0, jitter=False),
        )
        result = await adapter.process_world_request("w1")
        assert result["source"] == "native_wba"
        assert call_count == 3


# ---------------------------------------------------------------------------
# WBAAdapter — fallback path (agent fails at call time)
# ---------------------------------------------------------------------------


class TestWBAAdapterFallbackPath:
    @pytest.mark.asyncio
    async def test_fallback_returns_mock_on_agent_failure(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w1")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_communication_error(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, WBAAdapter

        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = WBAAdapter(fallback_to_mock=False, wba_agent=mock_agent)
        with pytest.raises(AgentCommunicationError, match="WBA communication failed"):
            await adapter.process_world_request("w1")

    @pytest.mark.asyncio
    async def test_mock_applies_updates_to_world_state(self) -> None:
        from src.agent_orchestration.adapters import WBAAdapter

        mock_agent = MagicMock()
        mock_agent.build = AsyncMock(side_effect=RuntimeError("down"))
        adapter = WBAAdapter(fallback_to_mock=True, wba_agent=mock_agent)
        result = await adapter.process_world_request("w1", updates={"danger": 5})
        assert result["world_state"]["danger"] == 5
        assert result["updated"] is True
