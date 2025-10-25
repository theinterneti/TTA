"""Comprehensive unit tests for agent_orchestration.messaging module."""

import pytest

from src.agent_orchestration.messaging import (
    FailureType,
    MessageResult,
    MessageSubscription,
    QueueMessage,
    ReceivedMessage,
)
from src.agent_orchestration.models import (
    AgentId,
    AgentMessage,
    AgentType,
    MessagePriority,
    MessageType,
)

# ============================================================================
# MessageResult Tests
# ============================================================================


class TestMessageResult:
    """Tests for MessageResult model."""

    def test_message_result_delivered_success(self):
        """Test MessageResult with successful delivery."""
        result = MessageResult(message_id="msg_001", delivered=True)
        assert result.message_id == "msg_001"
        assert result.delivered is True
        assert result.error is None

    def test_message_result_delivered_with_error(self):
        """Test MessageResult with delivery error."""
        result = MessageResult(
            message_id="msg_002",
            delivered=False,
            error="Connection timeout",
        )
        assert result.message_id == "msg_002"
        assert result.delivered is False
        assert result.error == "Connection timeout"

    def test_message_result_serialization(self):
        """Test MessageResult serialization."""
        result = MessageResult(message_id="msg_003", delivered=True)
        data = result.model_dump()
        assert data["message_id"] == "msg_003"
        assert data["delivered"] is True

    def test_message_result_deserialization(self):
        """Test MessageResult deserialization."""
        data = {"message_id": "msg_004", "delivered": False, "error": "Failed"}
        result = MessageResult(**data)
        assert result.message_id == "msg_004"
        assert result.delivered is False
        assert result.error == "Failed"


# ============================================================================
# MessageSubscription Tests
# ============================================================================


class TestMessageSubscription:
    """Tests for MessageSubscription model."""

    def test_message_subscription_single_type(self):
        """Test MessageSubscription with single message type."""
        sub = MessageSubscription(
            subscription_id="sub_001",
            agent_id=AgentId(type=AgentType.IPA),
            message_types=[MessageType.REQUEST],
        )
        assert sub.subscription_id == "sub_001"
        assert sub.agent_id.type == AgentType.IPA
        assert len(sub.message_types) == 1
        assert MessageType.REQUEST in sub.message_types

    def test_message_subscription_multiple_types(self):
        """Test MessageSubscription with multiple message types."""
        sub = MessageSubscription(
            subscription_id="sub_002",
            agent_id=AgentId(type=AgentType.WBA),
            message_types=[MessageType.REQUEST, MessageType.RESPONSE, MessageType.EVENT],
        )
        assert len(sub.message_types) == 3
        assert MessageType.REQUEST in sub.message_types
        assert MessageType.RESPONSE in sub.message_types
        assert MessageType.EVENT in sub.message_types

    def test_message_subscription_with_instance(self):
        """Test MessageSubscription with agent instance."""
        sub = MessageSubscription(
            subscription_id="sub_003",
            agent_id=AgentId(type=AgentType.NGA, instance="nga_v2"),
            message_types=[MessageType.RESPONSE],
        )
        assert sub.agent_id.instance == "nga_v2"

    def test_message_subscription_serialization(self):
        """Test MessageSubscription serialization."""
        sub = MessageSubscription(
            subscription_id="sub_004",
            agent_id=AgentId(type=AgentType.IPA),
            message_types=[MessageType.REQUEST],
        )
        data = sub.model_dump()
        assert data["subscription_id"] == "sub_004"
        assert len(data["message_types"]) == 1


# ============================================================================
# FailureType Tests
# ============================================================================


class TestFailureType:
    """Tests for FailureType enum."""

    def test_failure_type_values(self):
        """Test FailureType enum values."""
        assert FailureType.TRANSIENT.value == "transient"
        assert FailureType.PERMANENT.value == "permanent"
        assert FailureType.TIMEOUT.value == "timeout"

    def test_failure_type_from_string(self):
        """Test creating FailureType from string."""
        assert FailureType("transient") == FailureType.TRANSIENT
        assert FailureType("permanent") == FailureType.PERMANENT
        assert FailureType("timeout") == FailureType.TIMEOUT


# ============================================================================
# QueueMessage Tests
# ============================================================================


class TestQueueMessage:
    """Tests for QueueMessage model."""

    def test_queue_message_minimal(self):
        """Test QueueMessage with minimal fields."""
        msg = AgentMessage(
            message_id="msg_001",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        qm = QueueMessage(message=msg)
        assert qm.message == msg
        assert qm.delivery_attempts == 0
        assert qm.enqueued_at is None

    def test_queue_message_with_attempts(self):
        """Test QueueMessage with delivery attempts."""
        msg = AgentMessage(
            message_id="msg_002",
            sender=AgentId(type=AgentType.WBA),
            recipient=AgentId(type=AgentType.NGA),
            message_type=MessageType.RESPONSE,
        )
        qm = QueueMessage(message=msg, delivery_attempts=3)
        assert qm.delivery_attempts == 3

    def test_queue_message_with_timestamp(self):
        """Test QueueMessage with enqueued_at timestamp."""
        msg = AgentMessage(
            message_id="msg_003",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.EVENT,
        )
        timestamp = "2025-10-25T10:30:00Z"
        qm = QueueMessage(message=msg, enqueued_at=timestamp)
        assert qm.enqueued_at == timestamp

    def test_queue_message_serialization(self):
        """Test QueueMessage serialization."""
        msg = AgentMessage(
            message_id="msg_004",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        qm = QueueMessage(message=msg, delivery_attempts=2)
        data = qm.model_dump()
        assert data["delivery_attempts"] == 2
        assert data["message"]["message_id"] == "msg_004"


# ============================================================================
# ReceivedMessage Tests
# ============================================================================


class TestReceivedMessage:
    """Tests for ReceivedMessage model."""

    def test_received_message_success(self):
        """Test ReceivedMessage with successful receipt."""
        msg = AgentMessage(
            message_id="msg_001",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        rm = ReceivedMessage(message=msg, success=True)
        assert rm.message == msg
        assert rm.success is True
        assert rm.failure_type is None

    def test_received_message_failure(self):
        """Test ReceivedMessage with failure."""
        msg = AgentMessage(
            message_id="msg_002",
            sender=AgentId(type=AgentType.WBA),
            recipient=AgentId(type=AgentType.NGA),
            message_type=MessageType.RESPONSE,
        )
        rm = ReceivedMessage(
            message=msg,
            success=False,
            failure_type=FailureType.TIMEOUT,
        )
        assert rm.message == msg
        assert rm.success is False
        assert rm.failure_type == FailureType.TIMEOUT

    def test_received_message_with_error_details(self):
        """Test ReceivedMessage with error details."""
        msg = AgentMessage(
            message_id="msg_003",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.EVENT,
        )
        rm = ReceivedMessage(
            message=msg,
            success=False,
            failure_type=FailureType.VALIDATION_ERROR,
            error_details="Invalid payload format",
        )
        assert rm.failure_type == FailureType.VALIDATION_ERROR
        assert rm.error_details == "Invalid payload format"

    def test_received_message_serialization(self):
        """Test ReceivedMessage serialization."""
        msg = AgentMessage(
            message_id="msg_004",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        rm = ReceivedMessage(message=msg, success=True)
        data = rm.model_dump()
        assert data["success"] is True
        assert data["message"]["message_id"] == "msg_004"
