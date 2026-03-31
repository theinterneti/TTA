# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_state_validator_repairs]]
import os

import pytest
from tta_ai.orchestration.coordinators import RedisMessageCoordinator
from tta_ai.orchestration.models import AgentId, AgentMessage, AgentType, MessageType

from src.components.agent_orchestration_component import AgentOrchestrationComponent


@pytest.mark.redis
@pytest.mark.asyncio
async def test_state_validator_repairs_stale_reservations(redis_client):
    url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
    comp = AgentOrchestrationComponent(
        {
            "player_experience.api.redis_url": url,
            "agent_orchestration.port": 8627,
            "agent_orchestration.diagnostics.enabled": True,
            "agent_orchestration.error_handling.enabled": True,
            "agent_orchestration.workflow": {"state_validation_interval_s": 0.05},
            "agent_orchestration.tools": {"redis_key_prefix": "ao"},
        }
    )
    assert comp._start_impl() is True

    coord = RedisMessageCoordinator(redis_client, key_prefix="ao")
    sender = AgentId(type=AgentType.IPA)
    recipient = AgentId(type=AgentType.WBA, instance="v1")
    m = AgentMessage(
        message_id="msg-000001",
        sender=sender,
        recipient=recipient,
        message_type=MessageType.EVENT,
    )
    await coord.send_message(sender, recipient, m)

    # Reserve explicitly and force timeout by manipulating deadlines
    rm = await coord.receive(recipient, visibility_timeout=1)
    assert rm is not None
    # Set deadline in the past to mark as expired
    await redis_client.zadd(
        f"ao:reserved_deadlines:{recipient.type.value}:{recipient.instance}",
        {rm.token: 1},
    )

    # Trigger validator repair once
    from tta_ai.orchestration.state_validator import StateValidator

    sv = getattr(comp, "_state_validator", None)
    assert isinstance(sv, StateValidator)

    rep = await sv.validate_and_repair()
    assert rep["repaired"] >= 1

    # Message should be back in sched zset
    ready_count = await redis_client.zcard(
        f"ao:sched:{recipient.type.value}:{recipient.instance}:prio:5"
    )
    assert ready_count >= 1
