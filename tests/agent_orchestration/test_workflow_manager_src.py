"""Unit tests targeting src/agent_orchestration/workflow_manager.py directly.

The existing test_workflow_manager.py imports from tta_ai (the installed package),
leaving src/agent_orchestration/workflow_manager.py at 0% coverage.
This file imports from src. to fill that gap.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_orchestration.models import OrchestrationRequest
from src.agent_orchestration.workflow import (
    AgentStep,
    AgentType,
    WorkflowDefinition,
    WorkflowType,
)
from src.agent_orchestration.workflow_manager import (
    WorkflowManager,
    WorkflowRunStatus,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _simple_definition() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_type=WorkflowType.COLLABORATIVE,
        agent_sequence=[
            AgentStep(agent=AgentType.IPA, name="ipa"),
            AgentStep(agent=AgentType.WBA, name="wba"),
            AgentStep(agent=AgentType.NGA, name="nga"),
        ],
    )


def _request(entrypoint: AgentType = AgentType.IPA) -> OrchestrationRequest:
    return OrchestrationRequest(
        player_input="hello",
        session_id="s-1",
        player_id="p-1",
        entrypoint=entrypoint,
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_workflow_success():
    wm = WorkflowManager()
    ok, err = wm.register_workflow("basic", _simple_definition())
    assert ok is True
    assert err is None
    assert "basic" in wm.list_workflows()


def test_register_workflow_empty_sequence_fails():
    wm = WorkflowManager()
    defn = WorkflowDefinition(
        workflow_type=WorkflowType.COLLABORATIVE,
        agent_sequence=[],
    )
    ok, err = wm.register_workflow("empty", defn)
    assert ok is False
    assert err is not None


def test_get_workflow_returns_none_for_unknown():
    wm = WorkflowManager()
    assert wm.get_workflow("nonexistent") is None


def test_list_workflows_sorted():
    wm = WorkflowManager()
    wm.register_workflow("zebra", _simple_definition())
    wm.register_workflow("alpha", _simple_definition())
    assert wm.list_workflows() == ["alpha", "zebra"]


# ---------------------------------------------------------------------------
# execute_workflow – sync path
# ---------------------------------------------------------------------------


def test_execute_workflow_unknown_name():
    wm = WorkflowManager()
    resp, run_id, err = wm.execute_workflow("missing", _request())
    assert resp is None
    assert run_id is None
    assert err is not None
    assert "missing" in err


def test_execute_workflow_entrypoint_mismatch():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    # entrypoint is WBA but first step is IPA
    resp, run_id, err = wm.execute_workflow("basic", _request(AgentType.WBA))
    assert resp is None
    assert err is not None
    assert "Entrypoint" in err or "entrypoint" in err.lower()


def test_execute_workflow_happy_path():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    resp, run_id, err = wm.execute_workflow("basic", _request())
    assert err is None
    assert run_id is not None
    assert resp is not None
    assert resp.response_text == "Workflow executed"


def test_execute_workflow_sets_completed_status():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    _, run_id, _ = wm.execute_workflow("basic", _request())
    run = wm.get_run_state(run_id)
    assert run is not None
    assert run.status == WorkflowRunStatus.COMPLETED


def test_execute_workflow_records_history():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    _, run_id, _ = wm.execute_workflow("basic", _request())
    run = wm.get_run_state(run_id)
    assert len(run.history) == 3  # ipa, wba, nga


def test_execute_workflow_passes_metadata():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    _, run_id, _ = wm.execute_workflow("basic", _request(), metadata={"tag": "test"})
    run = wm.get_run_state(run_id)
    assert run.metadata["tag"] == "test"


# ---------------------------------------------------------------------------
# State introspection
# ---------------------------------------------------------------------------


def test_get_run_state_unknown_returns_none():
    wm = WorkflowManager()
    assert wm.get_run_state("nope") is None


def test_update_run_metadata_success():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    _, run_id, _ = wm.execute_workflow("basic", _request())
    updated = wm.update_run_metadata(run_id, {"key": "value"})
    assert updated is True
    run = wm.get_run_state(run_id)
    assert run.metadata["key"] == "value"


def test_update_run_metadata_unknown_run():
    wm = WorkflowManager()
    assert wm.update_run_metadata("ghost", {"x": 1}) is False


# ---------------------------------------------------------------------------
# build_graph / execute_graph
# ---------------------------------------------------------------------------


def test_build_graph_returns_dict():
    wm = WorkflowManager()
    defn = _simple_definition()
    graph = wm.build_graph(defn)
    assert isinstance(graph, dict)


def test_execute_graph_returns_orchestration_response():
    from src.agent_orchestration.workflow import OrchestrationResponse

    wm = WorkflowManager()
    graph = wm.build_graph(_simple_definition())
    resp = wm.execute_graph(graph, {"history": []})
    assert isinstance(resp, OrchestrationResponse)


# ---------------------------------------------------------------------------
# execute_workflow_async – without circuit breaker
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_workflow_async_happy_path():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    resp, run_id, err = await wm.execute_workflow_async("basic", _request())
    assert err is None
    assert resp is not None
    assert run_id is not None


@pytest.mark.asyncio
async def test_execute_workflow_async_unknown_workflow():
    wm = WorkflowManager()
    resp, run_id, err = await wm.execute_workflow_async("nope", _request())
    assert resp is None
    assert run_id is None
    assert err is not None


@pytest.mark.asyncio
async def test_execute_workflow_async_entrypoint_mismatch():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    resp, run_id, err = await wm.execute_workflow_async("basic", _request(AgentType.WBA))
    assert resp is None
    assert err is not None


# ---------------------------------------------------------------------------
# Circuit breaker management – no registry path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_circuit_breaker_status_no_registry():
    wm = WorkflowManager()
    assert await wm.get_circuit_breaker_status("any") is None


@pytest.mark.asyncio
async def test_reset_circuit_breaker_no_registry():
    wm = WorkflowManager()
    assert await wm.reset_circuit_breaker("any") is False


@pytest.mark.asyncio
async def test_get_all_circuit_breaker_status_no_registry():
    wm = WorkflowManager()
    assert await wm.get_all_circuit_breaker_status() == {}


# ---------------------------------------------------------------------------
# execute_workflow_async – with mocked circuit breaker registry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_workflow_async_with_open_circuit_breaker():
    """When circuit breaker reports open, degraded execution is returned."""
    from src.agent_orchestration.circuit_breaker_registry import CircuitBreakerRegistry

    mock_registry = AsyncMock(spec=CircuitBreakerRegistry)
    mock_cb = AsyncMock()
    mock_cb.is_call_permitted = AsyncMock(return_value=False)
    mock_registry.get_or_create = AsyncMock(return_value=mock_cb)

    wm = WorkflowManager(circuit_breaker_registry=mock_registry)
    wm.register_workflow("basic", _simple_definition())
    resp, run_id, err = await wm.execute_workflow_async("basic", _request())
    assert err is None
    assert resp is not None
    assert resp.workflow_metadata.get("degraded_mode") is True
