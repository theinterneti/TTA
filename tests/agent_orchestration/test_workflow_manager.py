
from src.agent_orchestration import (
    AgentStep,
    AgentType,
    OrchestrationRequest,
    WorkflowDefinition,
    WorkflowManager,
    WorkflowType,
)


def _simple_definition():
    return WorkflowDefinition(
        workflow_type=WorkflowType.COLLABORATIVE,
        agent_sequence=[
            AgentStep(agent=AgentType.IPA, name="ipa"),
            AgentStep(agent=AgentType.WBA, name="wba"),
            AgentStep(agent=AgentType.NGA, name="nga"),
        ],
    )


def test_register_and_list_workflows():
    wm = WorkflowManager()
    ok, err = wm.register_workflow("basic", _simple_definition())
    assert ok is True and err is None
    assert "basic" in wm.list_workflows()
    assert wm.get_workflow("basic") is not None


def test_register_invalid_definition():
    wm = WorkflowManager()
    # Empty definition: no steps
    empty_def = WorkflowDefinition(workflow_type=WorkflowType.INPUT_PROCESSING)
    ok, err = wm.register_workflow("invalid", empty_def)
    assert ok is False
    assert isinstance(err, str)


def test_execute_workflow_success():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    req = OrchestrationRequest(entrypoint=AgentType.IPA, input={"text": "go"})
    response, run_id, err = wm.execute_workflow("basic", req)
    assert err is None
    assert run_id is not None
    assert response is not None
    assert response.workflow_metadata["steps_executed"] == 3
    # Graph metadata included (stub or langgraph)
    assert "graph" in response.workflow_metadata


def test_execute_workflow_entrypoint_mismatch():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    # Entrypoint does not match first step
    req = OrchestrationRequest(entrypoint=AgentType.WBA)
    response, run_id, err = wm.execute_workflow("basic", req)
    assert response is None and run_id is None
    assert isinstance(err, str)


def test_run_state_tracking():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    req = OrchestrationRequest(entrypoint=AgentType.IPA)
    response, run_id, err = wm.execute_workflow("basic", req)
    assert err is None and run_id is not None
    run_state = wm.get_run_state(run_id)
    assert run_state is not None
    assert run_state.status.value == "completed"
    assert len(run_state.history) == 3


def test_update_run_metadata():
    wm = WorkflowManager()
    wm.register_workflow("basic", _simple_definition())
    req = OrchestrationRequest(entrypoint=AgentType.IPA)
    response, run_id, err = wm.execute_workflow("basic", req)
    assert err is None and run_id is not None
    assert wm.update_run_metadata(run_id, {"key": "value"}) is True
    run_state = wm.get_run_state(run_id)
    assert run_state.metadata.get("key") == "value"
