"""Unit tests targeting src/agent_orchestration/service.py directly.

The existing test_agent_orchestration_service.py imports from tta_ai (the installed
package), leaving src/agent_orchestration/service.py at ~10% coverage.
This file imports from src. directly to fill that gap.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_orchestration.models import AgentId, AgentType
from src.agent_orchestration.service import (
    AgentOrchestrationService,
    ServiceError,
    TherapeuticSafetyError,
    WorkflowExecutionError,
)
from src.agent_orchestration.state import AgentContext, SessionContext
from src.agent_orchestration.workflow import WorkflowType
from src.agent_orchestration.workflow_manager import WorkflowManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _session(session_id: str = "s-1", user_id: str = "u-1") -> SessionContext:
    return SessionContext(session_id=session_id, user_id=user_id)


def _mock_agent_registry() -> MagicMock:
    registry = MagicMock()
    registry.get = MagicMock(return_value=None)
    return registry


def _mock_message_coordinator() -> MagicMock:
    return MagicMock()


def _service(initialized: bool = False) -> AgentOrchestrationService:
    svc = AgentOrchestrationService(
        workflow_manager=WorkflowManager(),
        message_coordinator=_mock_message_coordinator(),
        agent_registry=_mock_agent_registry(),
    )
    if initialized:
        svc._initialized = True
        # Pre-register workflows so coordinate_agents can find them
        svc.workflow_manager._workflows["collaborative"] = MagicMock()
        svc.workflow_manager._workflows["input_processing"] = MagicMock()
        svc.workflow_manager._workflows["world_building"] = MagicMock()
        svc.workflow_manager._workflows["narrative_generation"] = MagicMock()
    return svc


# ---------------------------------------------------------------------------
# initialize
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_initialize_registers_default_workflows():
    svc = AgentOrchestrationService(
        workflow_manager=WorkflowManager(),
        message_coordinator=_mock_message_coordinator(),
        agent_registry=_mock_agent_registry(),
    )
    result = await svc.initialize()
    assert result is True
    assert svc._initialized is True
    assert "collaborative" in svc.workflow_manager.list_workflows()
    assert "input_processing" in svc.workflow_manager.list_workflows()


@pytest.mark.asyncio
async def test_initialize_returns_false_on_exception():
    svc = AgentOrchestrationService(
        workflow_manager=None,  # will cause validation to fail
        message_coordinator=_mock_message_coordinator(),
        agent_registry=_mock_agent_registry(),
    )
    result = await svc.initialize()
    assert result is False


# ---------------------------------------------------------------------------
# process_user_input – before init
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_user_input_raises_when_not_initialized():
    svc = _service(initialized=False)
    with pytest.raises(ServiceError, match="not initialized"):
        await svc.process_user_input("hello", _session())


# ---------------------------------------------------------------------------
# get_service_status
# ---------------------------------------------------------------------------


def test_get_service_status_structure():
    svc = _service()
    status = svc.get_service_status()
    assert "initialized" in status
    assert "active_sessions" in status
    assert "active_workflows" in status
    assert "metrics" in status
    assert "components" in status


def test_get_service_status_metrics_before_requests():
    svc = _service()
    metrics = svc.get_service_status()["metrics"]
    assert metrics["request_count"] == 0
    assert metrics["error_count"] == 0
    assert metrics["error_rate"] == 0.0


def test_get_service_status_components_reflect_none_optional():
    svc = _service()
    components = svc.get_service_status()["components"]
    assert components["therapeutic_validator"] is False
    assert components["resource_manager"] is False
    assert components["neo4j_manager"] is False


# ---------------------------------------------------------------------------
# shutdown
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_clears_state():
    svc = _service(initialized=True)
    svc._session_contexts["s-1"] = _session()
    svc._active_workflows["s-1"] = "run-1"
    result = await svc.shutdown()
    assert result is True
    assert svc._initialized is False
    assert len(svc._session_contexts) == 0
    assert len(svc._active_workflows) == 0


# ---------------------------------------------------------------------------
# get_therapeutic_safety_metrics
# ---------------------------------------------------------------------------


def test_get_therapeutic_safety_metrics_no_validator():
    svc = _service()
    result = svc.get_therapeutic_safety_metrics()
    assert "validator_available" in result
    assert result["validator_available"] is False


def test_get_therapeutic_safety_metrics_with_validator():
    svc = _service()
    mock_validator = MagicMock()
    mock_validator.get_monitoring_metrics = MagicMock(return_value={"status": "ok"})
    svc.therapeutic_validator = mock_validator
    result = svc.get_therapeutic_safety_metrics()
    assert result == {"status": "ok"}


def test_get_therapeutic_safety_metrics_validator_exception():
    svc = _service()
    mock_validator = MagicMock()
    mock_validator.get_monitoring_metrics = MagicMock(side_effect=RuntimeError("crash"))
    svc.therapeutic_validator = mock_validator
    result = svc.get_therapeutic_safety_metrics()
    assert "error" in result


# ---------------------------------------------------------------------------
# get_crisis_intervention_metrics
# ---------------------------------------------------------------------------


def test_get_crisis_intervention_metrics_no_components():
    svc = _service()
    result = svc.get_crisis_intervention_metrics()
    assert result["crisis_manager"] == {}
    assert result["emergency_protocols"] == {}


def test_get_crisis_intervention_metrics_with_crisis_manager():
    svc = _service()
    svc.crisis_intervention_manager = MagicMock()
    svc.crisis_intervention_manager.get_crisis_metrics = MagicMock(
        return_value={"events": 0}
    )
    result = svc.get_crisis_intervention_metrics()
    assert result["crisis_manager"] == {"events": 0}


def test_get_crisis_intervention_metrics_exception():
    svc = _service()
    svc.crisis_intervention_manager = MagicMock()
    svc.crisis_intervention_manager.get_crisis_metrics = MagicMock(
        side_effect=RuntimeError("crash")
    )
    result = svc.get_crisis_intervention_metrics()
    assert "error" in result


# ---------------------------------------------------------------------------
# get_crisis_dashboard / get_safety_report
# ---------------------------------------------------------------------------


def test_get_crisis_dashboard_no_dashboard():
    svc = _service()
    result = svc.get_crisis_dashboard()
    assert "error" in result


def test_get_crisis_dashboard_with_dashboard():
    svc = _service()
    svc.safety_monitoring_dashboard = MagicMock()
    svc.safety_monitoring_dashboard.get_crisis_dashboard = MagicMock(
        return_value={"alerts": []}
    )
    result = svc.get_crisis_dashboard()
    assert result == {"alerts": []}


def test_get_safety_report_no_dashboard():
    svc = _service()
    result = svc.get_safety_report()
    assert "error" in result


def test_get_safety_report_with_dashboard():
    svc = _service()
    svc.safety_monitoring_dashboard = MagicMock()
    svc.safety_monitoring_dashboard.get_safety_report = MagicMock(
        return_value={"summary": "ok"}
    )
    result = svc.get_safety_report(time_range_hours=12)
    svc.safety_monitoring_dashboard.get_safety_report.assert_called_with(12)
    assert result == {"summary": "ok"}


# ---------------------------------------------------------------------------
# _get_workflow_name
# ---------------------------------------------------------------------------


def test_get_workflow_name_collaborative():
    svc = _service()
    assert svc._get_workflow_name(WorkflowType.COLLABORATIVE) == "collaborative"


def test_get_workflow_name_input_processing():
    svc = _service()
    assert svc._get_workflow_name(WorkflowType.INPUT_PROCESSING) == "input_processing"


def test_get_workflow_name_world_building():
    svc = _service()
    assert svc._get_workflow_name(WorkflowType.WORLD_BUILDING) == "world_building"


def test_get_workflow_name_narrative_generation():
    svc = _service()
    assert (
        svc._get_workflow_name(WorkflowType.NARRATIVE_GENERATION)
        == "narrative_generation"
    )


# ---------------------------------------------------------------------------
# _determine_workflow_type
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_determine_workflow_type_simple_command():
    svc = _service()
    wt = await svc._determine_workflow_type("help", _session())
    assert wt == WorkflowType.INPUT_PROCESSING


@pytest.mark.asyncio
async def test_determine_workflow_type_world_keyword():
    svc = _service()
    wt = await svc._determine_workflow_type("look around", _session())
    assert wt == WorkflowType.WORLD_BUILDING


@pytest.mark.asyncio
async def test_determine_workflow_type_narrative_keyword():
    svc = _service()
    wt = await svc._determine_workflow_type("tell me a story", _session())
    assert wt == WorkflowType.NARRATIVE_GENERATION


@pytest.mark.asyncio
async def test_determine_workflow_type_default_collaborative():
    svc = _service()
    wt = await svc._determine_workflow_type("go north", _session())
    assert wt == WorkflowType.COLLABORATIVE


# ---------------------------------------------------------------------------
# _basic_safety_checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_basic_safety_checks_safe_content():
    svc = _service()
    await svc._basic_safety_checks("I want to explore the cave")  # must not raise


@pytest.mark.asyncio
async def test_basic_safety_checks_high_risk_keyword_raises():
    svc = _service()
    with pytest.raises(TherapeuticSafetyError):
        await svc._basic_safety_checks("I want to hurt myself")


@pytest.mark.asyncio
async def test_basic_safety_checks_suicide_keyword_raises():
    svc = _service()
    with pytest.raises(TherapeuticSafetyError):
        await svc._basic_safety_checks("I want to commit suicide")


# ---------------------------------------------------------------------------
# coordinate_agents – before init
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coordinate_agents_raises_when_not_initialized():
    svc = _service(initialized=False)
    context = AgentContext(session_id="s-1", user_id="u-1")
    with pytest.raises(ServiceError, match="not initialized"):
        await svc.coordinate_agents(WorkflowType.COLLABORATIVE, context)


# ---------------------------------------------------------------------------
# Full process_user_input – mocked workflow execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_user_input_happy_path():
    from src.agent_orchestration.workflow import OrchestrationResponse

    svc = _service()
    mock_response = OrchestrationResponse(
        response_text="Narrative response",
        updated_context={},
        workflow_metadata={},
        performance_metrics={},
    )

    with patch.object(
        svc, "_execute_workflow_with_context", return_value=mock_response
    ) as mock_exec:
        svc._initialized = True
        result = await svc.process_user_input("go north", _session())

    assert result.response_text == "Narrative response"
    mock_exec.assert_called_once()


@pytest.mark.asyncio
async def test_process_user_input_increments_request_count():
    from src.agent_orchestration.workflow import OrchestrationResponse

    svc = _service()
    mock_response = OrchestrationResponse(
        response_text="x",
        updated_context={},
        workflow_metadata={},
        performance_metrics={},
    )
    svc._initialized = True

    with patch.object(
        svc, "_execute_workflow_with_context", return_value=mock_response
    ):
        await svc.process_user_input("go north", _session())

    assert svc._request_count == 1


@pytest.mark.asyncio
async def test_process_user_input_re_raises_therapeutic_safety_error():
    svc = _service()
    svc._initialized = True

    with patch.object(
        svc,
        "_validate_therapeutic_safety",
        side_effect=TherapeuticSafetyError("blocked"),
    ):
        with pytest.raises(TherapeuticSafetyError):
            await svc.process_user_input("bad content", _session())

    assert svc._error_count == 1


@pytest.mark.asyncio
async def test_process_user_input_wraps_unexpected_exception():
    svc = _service()
    svc._initialized = True

    with patch.object(
        svc,
        "_validate_therapeutic_safety",
        side_effect=RuntimeError("unexpected"),
    ):
        with pytest.raises(ServiceError, match="Unexpected error"):
            await svc.process_user_input("go north", _session())
