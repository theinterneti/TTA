"""Unit tests for IPA retry/fallback migration (#301).

Verifies that IPAAdapter.process_input() uses FallbackPrimitive(RetryPrimitive(...))
with WorkflowContext when the native IPA is available, and delegates to mock
correctly when unavailable.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from ttadev.primitives import WorkflowContext

from src.agent_orchestration.adapters import (
    RetryConfig,
    _IPACall,
    _IPAFallback,
    _transform_ipa_result,
)
from src.components.ipa.models import ExtractedEntity, Intent, ProcessedInput

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_processed_input(**kwargs) -> ProcessedInput:  # type: ignore[no-untyped-def]
    defaults: dict = {
        "raw_text": "go north",
        "normalized_text": "go north",
        "intent": Intent.EXPLORE,
        "intent_confidence": 0.9,
    }
    defaults.update(kwargs)
    return ProcessedInput(**defaults)


# ---------------------------------------------------------------------------
# _transform_ipa_result
# ---------------------------------------------------------------------------


class TestTransformIPAResult:
    def test_populates_all_fields(self) -> None:
        pi = _make_processed_input()
        result = _transform_ipa_result("go north", pi)
        assert result["source"] == "native_ipa"
        assert result["routing"]["intent"] == "explore"
        assert result["routing"]["confidence"] == 0.9
        assert result["normalized_text"] == "go north"
        assert "processed_input" in result

    def test_entities_in_routing(self) -> None:
        entity = ExtractedEntity(name="forest", entity_type="location", confidence=0.9)
        pi = _make_processed_input(entities=[entity])
        result = _transform_ipa_result("go to forest", pi)
        assert result["routing"]["entities"] == {"forest": "location"}

    def test_entities_defaults_to_empty_dict(self) -> None:
        pi = _make_processed_input(entities=[])
        result = _transform_ipa_result("x", pi)
        assert result["routing"]["entities"] == {}

    def test_npc_name_in_routing(self) -> None:
        entity = ExtractedEntity(name="merchant", entity_type="npc", confidence=0.8)
        pi = _make_processed_input(entities=[entity])
        result = _transform_ipa_result("talk to merchant", pi)
        assert result["routing"]["npc"] == "merchant"

    def test_npc_none_when_no_npcs(self) -> None:
        pi = _make_processed_input(entities=[])
        result = _transform_ipa_result("go north", pi)
        assert result["routing"]["npc"] is None

    def test_raw_intent_is_model_dump(self) -> None:
        pi = _make_processed_input()
        result = _transform_ipa_result("go north", pi)
        assert isinstance(result["raw_intent"], dict)


# ---------------------------------------------------------------------------
# _IPACall primitive
# ---------------------------------------------------------------------------


class TestIPACall:
    @pytest.mark.asyncio
    async def test_execute_calls_agent_process(self) -> None:
        mock_pi = _make_processed_input(intent=Intent.ACTION, intent_confidence=0.95)
        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(return_value=mock_pi)
        ctx = WorkflowContext(workflow_id="session-001")

        result = await _IPACall(mock_agent).execute(
            {"text": "go south", "session_id": "s1", "player_id": "p1", "location_id": None},
            ctx,
        )

        mock_agent.process.assert_awaited_once()
        assert result["source"] == "native_ipa"
        assert result["routing"]["intent"] == "action"

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(side_effect=RuntimeError("IPA failure"))
        ctx = WorkflowContext(workflow_id="s")
        with pytest.raises(RuntimeError, match="IPA failure"):
            await _IPACall(mock_agent).execute(
                {"text": "hi", "session_id": "", "player_id": "", "location_id": None},
                ctx,
            )


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
# IPAAdapter.process_input integration (native agent path)
# ---------------------------------------------------------------------------


class TestIPAAdapterNativePath:
    """IPAAdapter with injected mock native IPA agent."""

    @pytest.mark.asyncio
    async def test_process_input_with_session_id(self) -> None:
        """session_id flows through to WorkflowContext.workflow_id."""
        mock_pi = _make_processed_input(intent=Intent.EXPLORE)
        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(return_value=mock_pi)

        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=True, ipa_agent=mock_agent)
        result = await adapter.process_input("go north", session_id="ses-42")

        assert result["source"] == "native_ipa"
        assert result["routing"]["intent"] == "explore"

    @pytest.mark.asyncio
    async def test_process_input_without_session_id(self) -> None:
        """session_id=None auto-generates a workflow_id."""
        mock_pi = _make_processed_input(intent=Intent.QUERY)
        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(return_value=mock_pi)

        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=True, ipa_agent=mock_agent)
        result = await adapter.process_input("say hello")

        assert result["source"] == "native_ipa"

    @pytest.mark.asyncio
    async def test_fallback_on_native_ipa_failure(self) -> None:
        """When native IPA raises, FallbackPrimitive returns mock response."""
        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(side_effect=RuntimeError("timeout"))

        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(fallback_to_mock=True, ipa_agent=mock_agent)
        result = await adapter.process_input("help")

        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_on_failure(self) -> None:
        """fallback_to_mock=False + native IPA failure → AgentCommunicationError."""
        from src.agent_orchestration.adapters import AgentCommunicationError, IPAAdapter

        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(side_effect=RuntimeError("crash"))
        adapter = IPAAdapter(fallback_to_mock=False, ipa_agent=mock_agent)
        with pytest.raises(AgentCommunicationError):
            await adapter.process_input("test")

    @pytest.mark.asyncio
    async def test_retry_config_respected(self) -> None:
        """RetryConfig.max_retries is forwarded to RetryStrategy."""
        call_count = 0
        mock_pi = _make_processed_input(intent=Intent.ACTION)

        async def flaky_process(**kwargs):  # type: ignore[no-untyped-def]
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("flaky")
            return mock_pi

        mock_agent = MagicMock()
        mock_agent.process = flaky_process

        from src.agent_orchestration.adapters import IPAAdapter

        adapter = IPAAdapter(
            fallback_to_mock=True,
            ipa_agent=mock_agent,
            retry_config=RetryConfig(max_retries=3, base_delay=0.0, jitter=False),
        )
        result = await adapter.process_input("retry me")

        assert result["source"] == "native_ipa"
        assert call_count == 3


# ---------------------------------------------------------------------------
# IPAAdapter.process_input — fallback path (agent fails at call time)
# ---------------------------------------------------------------------------


class TestIPAAdapterFallbackPath:
    @pytest.mark.asyncio
    async def test_fallback_returns_mock_on_agent_failure(self) -> None:
        from src.agent_orchestration.adapters import IPAAdapter

        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = IPAAdapter(fallback_to_mock=True, ipa_agent=mock_agent)
        result = await adapter.process_input("test")
        assert result["source"] == "mock_fallback"

    @pytest.mark.asyncio
    async def test_no_fallback_raises_communication_error(self) -> None:
        from src.agent_orchestration.adapters import AgentCommunicationError, IPAAdapter

        mock_agent = MagicMock()
        mock_agent.process = AsyncMock(side_effect=RuntimeError("ollama down"))
        adapter = IPAAdapter(fallback_to_mock=False, ipa_agent=mock_agent)
        with pytest.raises(AgentCommunicationError, match="IPA communication failed"):
            await adapter.process_input("test")
