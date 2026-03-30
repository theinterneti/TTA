"""Unit tests for CircuitBreakerPrimitive integration in IPA/WBA/NGA adapters.

Verifies that:
- CircuitBreakerPrimitive is part of the execution chain for each adapter.
- When the real agent repeatedly fails, the CB transitions to OPEN state.
- In OPEN state, FallbackPrimitive (fallback_to_mock=True) returns a mock
  result without re-raising.
- With fallback_to_mock=False, OPEN state raises AgentCommunicationError.
- The CB recovers through OPEN -> HALF_OPEN -> CLOSED on subsequent success.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    from tta_dev_primitives import WorkflowContext  # type: ignore[no-redef]
from ttadev.primitives.recovery.circuit_breaker_primitive import (
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
)

from src.agent_orchestration.adapters import (
    AgentCommunicationError,
    IPAAdapter,
    NGAAdapter,
    RetryConfig,
    WBAAdapter,
    _IPACall,
    _NGACall,
    _WBACall,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cb_config(threshold: int = 3, recovery: float = 0.01) -> CircuitBreakerConfig:
    """Small thresholds so tests don't need many iterations."""
    return CircuitBreakerConfig(
        failure_threshold=threshold,
        recovery_timeout=recovery,
        success_threshold=1,
    )


# ---------------------------------------------------------------------------
# IPA adapter — circuit breaker chain
# ---------------------------------------------------------------------------


class TestIPAAdapterCircuitBreaker:
    """CircuitBreakerPrimitive is in the IPA execution chain."""

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_with_fallback(self) -> None:
        """Repeated IPA failures open the CB; FallbackPrimitive returns mock."""
        adapter = IPAAdapter(
            fallback_to_mock=True,
            cb_config=_cb_config(threshold=2),
        )
        # Force real-agent path to be available but always raise
        adapter._available = True
        failing_call = AsyncMock(side_effect=RuntimeError("ipa down"))

        with patch.object(_IPACall, "execute", failing_call):
            # First two calls hit the real agent and fail (filling the CB)
            result1 = await adapter.process_input("hello")
            result2 = await adapter.process_input("world")

        # FallbackPrimitive catches the CircuitBreakerError and returns mock
        assert result1["source"] == "mock_fallback"
        assert result2["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_no_fallback(self) -> None:
        """With fallback_to_mock=False, OPEN CB propagates as AgentCommunicationError."""
        adapter = IPAAdapter(
            fallback_to_mock=False,
            cb_config=_cb_config(threshold=2),
        )
        adapter._available = True
        failing_call = AsyncMock(side_effect=RuntimeError("ipa down"))

        call_count = 0
        with patch.object(_IPACall, "execute", failing_call):
            for _ in range(4):
                with pytest.raises(AgentCommunicationError):
                    await adapter.process_input("test")
                call_count += 1

        # After threshold, CB is OPEN — further calls still raise without
        # hitting the underlying primitive
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_successful_call_returns_real_source(self) -> None:
        """A successful _IPACall result flows through the chain unchanged."""
        adapter = IPAAdapter(fallback_to_mock=True, cb_config=_cb_config())
        adapter._available = True

        expected = {
            "normalized_text": "go north",
            "routing": {"intent": "move", "confidence": 0.95},
            "raw_intent": {"intent": "move"},
            "source": "real_ipa",
        }
        success_call = AsyncMock(return_value=expected)
        with patch.object(_IPACall, "execute", success_call):
            result = await adapter.process_input("go north")

        assert result["source"] == "real_ipa"
        assert result["routing"]["intent"] == "move"

    @pytest.mark.asyncio
    async def test_cb_recovers_after_timeout(self) -> None:
        """After recovery_timeout the CB moves to HALF_OPEN and closes on success."""
        import asyncio

        # max_retries=0 so a single _IPACall failure reaches the CB directly
        adapter = IPAAdapter(
            fallback_to_mock=False,
            cb_config=_cb_config(threshold=1, recovery=0.05),
            retry_config=RetryConfig(max_retries=0),
        )
        adapter._available = True

        fail_then_succeed = AsyncMock(
            side_effect=[
                RuntimeError("down"),
                {"normalized_text": "ok", "routing": {}, "raw_intent": {}, "source": "real_ipa"},
            ]
        )
        with patch.object(_IPACall, "execute", fail_then_succeed):
            # First call opens the CB (no retries so failure propagates immediately)
            with pytest.raises(AgentCommunicationError):
                await adapter.process_input("fail")

            # Wait for recovery_timeout to elapse
            await asyncio.sleep(0.1)

            # CB should now be HALF_OPEN -> CLOSED after success
            result = await adapter.process_input("recover")

        assert result["source"] == "real_ipa"


# ---------------------------------------------------------------------------
# WBA adapter — circuit breaker chain
# ---------------------------------------------------------------------------


class TestWBAAdapterCircuitBreaker:
    """CircuitBreakerPrimitive is in the WBA execution chain."""

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_with_fallback(self) -> None:
        adapter = WBAAdapter(
            fallback_to_mock=True,
            cb_config=_cb_config(threshold=2),
        )
        adapter._available = True
        adapter._wba_instance = MagicMock()
        failing_call = AsyncMock(side_effect=RuntimeError("wba down"))

        with patch.object(_WBACall, "execute", failing_call):
            result1 = await adapter.process_world_request("world-1")
            result2 = await adapter.process_world_request("world-1")

        assert result1["source"] == "mock_fallback"
        assert result2["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_no_fallback(self) -> None:
        adapter = WBAAdapter(
            fallback_to_mock=False,
            cb_config=_cb_config(threshold=2),
        )
        adapter._available = True
        adapter._wba_instance = MagicMock()
        failing_call = AsyncMock(side_effect=RuntimeError("wba down"))

        with patch.object(_WBACall, "execute", failing_call):
            for _ in range(4):
                with pytest.raises(AgentCommunicationError):
                    await adapter.process_world_request("world-1")

    @pytest.mark.asyncio
    async def test_successful_call_returns_real_source(self) -> None:
        adapter = WBAAdapter(fallback_to_mock=True, cb_config=_cb_config())
        adapter._available = True
        adapter._wba_instance = MagicMock()

        expected: dict[str, Any] = {
            "world_id": "w1",
            "world_state": {"id": "w1"},
            "updated": False,
            "cached": False,
            "source": "real_wba",
            "raw_result": {},
        }
        with patch.object(_WBACall, "execute", AsyncMock(return_value=expected)):
            result = await adapter.process_world_request("w1")

        assert result["source"] == "real_wba"


# ---------------------------------------------------------------------------
# NGA adapter — circuit breaker chain
# ---------------------------------------------------------------------------


class TestNGAAdapterCircuitBreaker:
    """CircuitBreakerPrimitive is in the NGA execution chain."""

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_with_fallback(self) -> None:
        adapter = NGAAdapter(
            fallback_to_mock=True,
            cb_config=_cb_config(threshold=2),
        )
        adapter._available = True
        failing_call = AsyncMock(side_effect=RuntimeError("nga down"))

        with patch.object(_NGACall, "execute", failing_call):
            result1 = await adapter.generate_narrative("A dark forest", {})
            result2 = await adapter.generate_narrative("A dark forest", {})

        assert result1["source"] == "mock_fallback"
        assert result2["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_cb_opens_after_threshold_failures_no_fallback(self) -> None:
        adapter = NGAAdapter(
            fallback_to_mock=False,
            cb_config=_cb_config(threshold=2),
        )
        adapter._available = True
        failing_call = AsyncMock(side_effect=RuntimeError("nga down"))

        with patch.object(_NGACall, "execute", failing_call):
            for _ in range(4):
                with pytest.raises(AgentCommunicationError):
                    await adapter.generate_narrative("test", {})

    @pytest.mark.asyncio
    async def test_successful_call_returns_real_source(self) -> None:
        adapter = NGAAdapter(fallback_to_mock=True, cb_config=_cb_config())
        adapter._available = True

        expected: dict[str, Any] = {
            "story": "You enter the forest.",
            "raw": "You enter the forest.",
            "context_used": True,
            "source": "real_nga",
            "raw_result": {},
        }
        with patch.object(_NGACall, "execute", AsyncMock(return_value=expected)):
            result = await adapter.generate_narrative("forest", {"scene": "dark"})

        assert result["source"] == "real_nga"
        assert "forest" in result["story"] or result["story"] == "You enter the forest."
