import pytest

from tta_ai.orchestration.models import AgentType, OrchestrationRequest
from tta_ai.orchestration.workflow import AgentStep, WorkflowDefinition, WorkflowType
from tta_ai.orchestration.workflow_manager import WorkflowManager


@pytest.mark.asyncio
async def test_workflow_manager_aggregates_safety_findings(monkeypatch):
    # Create a simple workflow with two steps (IPA, NGA). The Step execution is stubbed
    # in WorkflowManager and returns a dict; we simulate therapeutic_validation presence.
    wm = WorkflowManager()
    wf = WorkflowDefinition(
        workflow_type=WorkflowType.COLLABORATIVE,
        agent_sequence=[AgentStep(agent=AgentType.IPA), AgentStep(agent=AgentType.NGA)],
    )
    ok, err = wm.register_workflow("t", wf)
    assert ok and not err

    # Monkeypatch internal _execute_step to attach therapeutic_validation
    def fake_exec(step, run_state):
        from tta_ai.orchestration.workflow_manager import StepResult

        res = StepResult(step=step)
        if step.agent == AgentType.IPA:
            res.result = {
                "therapeutic_validation": {
                    "level": "warning",
                    "findings": [{"rule_id": "e1"}],
                }
            }
        else:
            res.result = {
                "therapeutic_validation": {
                    "level": "blocked",
                    "findings": [{"rule_id": "c1"}],
                }
            }
        return res

    monkeypatch.setattr(wm, "_execute_step", fake_exec)

    req = OrchestrationRequest(entrypoint=AgentType.IPA, input={})
    resp, run_id, error = wm.execute_workflow("t", req)
    assert error is None and resp is not None
    agg = resp.therapeutic_validation
    assert agg is not None
    assert agg.get("level") == "blocked"
    assert any(f.get("rule_id") == "c1" for f in agg.get("findings", []))
