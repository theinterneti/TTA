from tta_ai.orchestration import (
    AgentId,
    AgentMessage,
    AgentType,
    MessageResult,
    MessageSubscription,
    MessageType,
    QueueMessage,
)


def test_message_result_defaults():
    res = MessageResult(message_id="abc", delivered=True)
    assert res.error is None


def test_message_subscription_roundtrip():
    sub = MessageSubscription(
        subscription_id="sub1",
        agent_id=AgentId(type=AgentType.IPA),
        message_types=[MessageType.REQUEST, MessageType.EVENT],
    )
    assert sub.subscription_id == "sub1"
    assert len(sub.message_types) == 2


def test_queue_message_defaults():
    qm = QueueMessage(
        message=AgentMessage(
            message_id="abcdef",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
    )
    assert isinstance(qm.delivery_attempts, int)
    assert qm.enqueued_at is None
