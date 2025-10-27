import pytest
from tta_ai.orchestration import (
    AgentId,
    AgentMessage,
    AgentType,
    MessagePriority,
    MessageType,
)
from tta_ai.orchestration.validators import validate_agent_message


def test_agent_message_valid():
    msg = AgentMessage(
        message_id="abcdef",
        sender=AgentId(type=AgentType.IPA),
        recipient=AgentId(type=AgentType.WBA),
        message_type=MessageType.REQUEST,
        payload={"text": "hello"},
        priority=MessagePriority.HIGH,
    )
    ok, err = validate_agent_message(msg)
    assert ok is True
    assert err is None


from pydantic import ValidationError


def test_agent_message_min_length_invalid():
    # Construction itself should raise due to min_length constraint
    with pytest.raises(ValidationError):
        AgentMessage(
            message_id="abc",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.NGA),
            message_type=MessageType.EVENT,
        )


def test_routing_defaults():
    msg = AgentMessage(
        message_id="abcdef",
        sender=AgentId(type=AgentType.IPA),
        recipient=AgentId(type=AgentType.NGA),
        message_type=MessageType.RESPONSE,
    )
    assert msg.routing is not None
    assert msg.routing.topic is None
    assert isinstance(msg.routing.tags, list)
