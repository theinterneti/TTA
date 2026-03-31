"""Unit tests targeting src/agent_orchestration/unified_orchestrator.py directly.

The existing test_unified_orchestrator.py imports from tta_ai (the installed package),
which means src/agent_orchestration/unified_orchestrator.py gets 0% coverage.
This file imports from src. to fill that gap.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_orchestration.safety_validation.enums import SafetyLevel
from src.agent_orchestration.unified_orchestrator import (
    OrchestrationPhase,
    OrchestrationState,
    UnifiedAgentOrchestrator,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _state(**kwargs) -> OrchestrationState:
    defaults: dict = {
        "workflow_id": "wf-1",
        "session_id": "s-1",
        "player_id": "p-1",
        "phase": OrchestrationPhase.INPUT_PROCESSING,
        "user_input": "hello",
    }
    defaults.update(kwargs)
    return OrchestrationState(**defaults)


def _mock_safety(level: SafetyLevel = SafetyLevel.SAFE):
    r = MagicMock()
    r.level = level
    return r


def _patched_orchestrator() -> UnifiedAgentOrchestrator:
    orch = UnifiedAgentOrchestrator(
        redis_url="redis://localhost:6379", enable_real_agents=False
    )
    orch.initialized = True
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)
    orch.redis = mock_redis
    mock_safety = AsyncMock()
    mock_safety.validate_text = AsyncMock(return_value=_mock_safety(SafetyLevel.SAFE))
    orch.safety_service = mock_safety
    orch.ipa_adapter = AsyncMock()
    orch.ipa_adapter.process_input = AsyncMock(
        return_value={"routing": {"intent": "explore", "entities": {}}}
    )
    orch.wba_adapter = AsyncMock()
    orch.wba_adapter.process_world_request = AsyncMock(
        return_value={"description": "Forest path.", "world_state": {"loc": "forest"}}
    )
    orch.nga_adapter = AsyncMock()
    orch.nga_adapter.generate_narrative = AsyncMock(
        return_value={"story": "You walk deeper into the forest."}
    )
    return orch


# ---------------------------------------------------------------------------
# OrchestrationPhase
# ---------------------------------------------------------------------------


def test_phase_enum_values():
    assert OrchestrationPhase.INPUT_PROCESSING.value == "input_processing"
    assert OrchestrationPhase.COMPLETE.value == "complete"
    assert OrchestrationPhase.ERROR.value == "error"


# ---------------------------------------------------------------------------
# OrchestrationState serialisation
# ---------------------------------------------------------------------------


def test_to_dict_and_from_dict_round_trip():
    original = _state(
        phase=OrchestrationPhase.COMPLETE,
        ipa_result={"routing": {"intent": "move"}},
        nga_result={"story": "You proceed."},
        safety_level=SafetyLevel.SAFE,
    )
    restored = OrchestrationState.from_dict(original.to_dict())
    assert restored.workflow_id == original.workflow_id
    assert restored.phase == OrchestrationPhase.COMPLETE
    assert restored.ipa_result == original.ipa_result
    assert restored.safety_level == SafetyLevel.SAFE


def test_to_dict_includes_required_keys():
    d = _state().to_dict()
    for key in (
        "workflow_id",
        "session_id",
        "player_id",
        "phase",
        "user_input",
        "safety_level",
    ):
        assert key in d


def test_from_dict_with_error_field():
    state = _state(error="something broke")
    restored = OrchestrationState.from_dict(state.to_dict())
    assert restored.error == "something broke"


def test_timestamps_are_timezone_aware():
    state = _state()
    assert state.created_at.tzinfo is not None


# ---------------------------------------------------------------------------
# _build_narrative_prompt
# ---------------------------------------------------------------------------


def test_build_narrative_prompt_includes_input_and_intent():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(
        user_input="climb the wall",
        ipa_result={"routing": {"intent": "climb"}},
        wba_result={"description": "The wall crumbles."},
    )
    prompt = orch._build_narrative_prompt(state)
    assert "climb the wall" in prompt
    assert "climb" in prompt
    assert "The wall crumbles." in prompt


def test_build_narrative_prompt_omits_world_changes_when_absent():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(ipa_result=None, wba_result=None)
    prompt = orch._build_narrative_prompt(state)
    assert "World changes:" not in prompt


# ---------------------------------------------------------------------------
# _handle_safety_concern
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_blocked_returns_intervention_flag():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(safety_level=SafetyLevel.BLOCKED)
    result = await orch._handle_safety_concern(state)
    assert result["success"] is True
    assert result["safety_intervention"] is True
    assert result["safety_level"] == "blocked"


@pytest.mark.asyncio
async def test_handle_warning_returns_checkin_narrative():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(safety_level=SafetyLevel.WARNING)
    result = await orch._handle_safety_concern(state)
    assert result["safety_intervention"] is True
    assert result["safety_level"] == "warning"
    assert result["workflow_id"] == "wf-1"


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_with_no_redis_does_not_raise():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    await orch.close()


@pytest.mark.asyncio
async def test_close_calls_redis_close():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    orch.redis = AsyncMock()
    await orch.close()
    orch.redis.close.assert_called_once()


@pytest.mark.asyncio
async def test_process_user_input_raises_when_not_initialised():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    with pytest.raises(RuntimeError, match="not initialized"):
        await orch.process_user_input("hi", "s", "p")


# ---------------------------------------------------------------------------
# No-redis state access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_workflow_state_returns_none_without_redis():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    assert await orch.get_workflow_state("wf-x") is None


@pytest.mark.asyncio
async def test_get_session_latest_workflow_returns_none_without_redis():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    assert await orch.get_session_latest_workflow("s-x") is None


@pytest.mark.asyncio
async def test_save_state_skips_without_redis():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    orch.redis = None
    await orch._save_state(_state())  # should not raise


# ---------------------------------------------------------------------------
# Full happy-path workflow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_user_input_happy_path():
    orch = _patched_orchestrator()
    result = await orch.process_user_input("go north", "s-1", "p-1")
    assert result["success"] is True
    assert result["narrative"] == "You walk deeper into the forest."
    assert result["safety_level"] == "safe"
    assert result["intent"] == "explore"


@pytest.mark.asyncio
async def test_process_user_input_complete_state_phase():
    orch = _patched_orchestrator()
    result = await orch.process_user_input("look", "s-1", "p-1")
    assert result["complete_state"]["phase"] == "complete"


@pytest.mark.asyncio
async def test_process_user_input_safety_blocked_skips_wba_nga():
    orch = _patched_orchestrator()
    orch.safety_service.validate_text = AsyncMock(
        return_value=_mock_safety(SafetyLevel.BLOCKED)
    )
    result = await orch.process_user_input("bad input", "s-1", "p-1")
    assert result.get("safety_intervention") is True
    orch.wba_adapter.process_world_request.assert_not_called()
    orch.nga_adapter.generate_narrative.assert_not_called()


@pytest.mark.asyncio
async def test_process_user_input_safety_warning_skips_wba_nga():
    orch = _patched_orchestrator()
    orch.safety_service.validate_text = AsyncMock(
        return_value=_mock_safety(SafetyLevel.WARNING)
    )
    result = await orch.process_user_input("sad input", "s-1", "p-1")
    assert result.get("safety_intervention") is True


@pytest.mark.asyncio
async def test_process_user_input_adapter_error_returns_failure_response():
    orch = _patched_orchestrator()
    orch.ipa_adapter.process_input = AsyncMock(side_effect=RuntimeError("IPA down"))
    result = await orch.process_user_input("hi", "s-1", "p-1")
    assert result["success"] is False
    assert "IPA down" in result["error"]
    assert result["narrative"]  # fallback message present


@pytest.mark.asyncio
async def test_process_user_input_passes_world_context_to_wba():
    orch = _patched_orchestrator()
    await orch.process_user_input(
        "look", "s-1", "p-1", world_context={"world_id": "w-99"}
    )
    kwargs = orch.wba_adapter.process_world_request.call_args.kwargs
    assert kwargs["world_id"] == "w-99"


# ---------------------------------------------------------------------------
# Redis state retrieval
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_workflow_state_returns_none_on_redis_miss():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    orch.redis = AsyncMock()
    orch.redis.get = AsyncMock(return_value=None)
    assert await orch.get_workflow_state("wf-missing") is None


@pytest.mark.asyncio
async def test_get_workflow_state_deserialises_state():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(phase=OrchestrationPhase.COMPLETE)
    orch.redis = AsyncMock()
    orch.redis.get = AsyncMock(return_value=json.dumps(state.to_dict()))
    result = await orch.get_workflow_state("wf-1")
    assert result is not None
    assert result.phase == OrchestrationPhase.COMPLETE


@pytest.mark.asyncio
async def test_get_session_latest_workflow_no_session():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    orch.redis = AsyncMock()
    orch.redis.get = AsyncMock(return_value=None)
    assert await orch.get_session_latest_workflow("s-none") is None


@pytest.mark.asyncio
async def test_get_session_latest_workflow_follows_workflow_id():
    orch = UnifiedAgentOrchestrator(enable_real_agents=False)
    state = _state(phase=OrchestrationPhase.COMPLETE)
    state_json = json.dumps(state.to_dict())
    orch.redis = AsyncMock()
    orch.redis.get = AsyncMock(side_effect=["wf-1", state_json])
    result = await orch.get_session_latest_workflow("s-1")
    assert result is not None
    assert result.workflow_id == "wf-1"
