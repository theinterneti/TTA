import os

import pytest

from tta_ai.orchestration.workflow_transaction import WorkflowTransaction
from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_workflow_transaction_savepoint_and_rollback(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8626,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.error_handling.enabled": True,
            "agent_orchestration.tools": {"redis_key_prefix": "ao"},
        }
    )
    assert comp._start_impl() is True

    tx = WorkflowTransaction(redis_client, key_prefix="ao")
    run_id = "runrb1"

    await tx.create_savepoint(run_id, "start", 0.0)
    await tx.add_cleanup(run_id, "start", kind="redis_key", value="ao:test:wf:tmp1")
    # create a key to cleanup
    await redis_client.set("ao:test:wf:tmp1", "x")

    await tx.create_savepoint(run_id, "before_agent", 1.0)
    await tx.add_cleanup(
        run_id, "before_agent", kind="tmp_file", value="/tmp/ao-tmp-does-not-exist"
    )

    res = await tx.rollback_to(run_id, "before_agent")
    assert res["ok"] is True
    # Redis key should be deleted
    assert await redis_client.exists("ao:test:wf:tmp1") == 0
