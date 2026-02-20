"""Comprehensive unit tests for agent_orchestration.models module."""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_models]]

import pytest

from src.agent_orchestration.models import (
    AgentId,
    AgentMessage,
    AgentType,
    CapabilityScope,
    CapabilityStatus,
    CapabilityType,
    MessagePriority,
    MessageType,
    OrchestrationRequest,
    OrchestrationResponse,
    RoutingKey,
)

# ============================================================================
# AgentType Tests
# ============================================================================


class TestAgentType:
    """Tests for AgentType enum."""

    def test_agent_type_ipa(self):
        """Test IPA agent type."""
        assert AgentType.IPA.value == "input_processor"

    def test_agent_type_wba(self):
        """Test WBA agent type."""
        assert AgentType.WBA.value == "world_builder"

    def test_agent_type_nga(self):
        """Test NGA agent type."""
        assert AgentType.NGA.value == "narrative_generator"

    def test_agent_type_openhands(self):
        """Test OpenHands agent type."""
        assert AgentType.OPENHANDS.value == "openhands"

    def test_agent_type_from_string(self):
        """Test creating AgentType from string."""
        assert AgentType("input_processor") == AgentType.IPA
        assert AgentType("world_builder") == AgentType.WBA
        assert AgentType("narrative_generator") == AgentType.NGA

    def test_agent_type_invalid(self):
        """Test invalid agent type."""
        with pytest.raises(ValueError):
            AgentType("invalid_type")


# ============================================================================
# MessageType Tests
# ============================================================================


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_type_request(self):
        """Test REQUEST message type."""
        assert MessageType.REQUEST.value == "request"

    def test_message_type_response(self):
        """Test RESPONSE message type."""
        assert MessageType.RESPONSE.value == "response"

    def test_message_type_event(self):
        """Test EVENT message type."""
        assert MessageType.EVENT.value == "event"

    def test_message_type_from_string(self):
        """Test creating MessageType from string."""
        assert MessageType("request") == MessageType.REQUEST
        assert MessageType("response") == MessageType.RESPONSE


# ============================================================================
# MessagePriority Tests
# ============================================================================


class TestMessagePriority:
    """Tests for MessagePriority enum."""

    def test_priority_low(self):
        """Test LOW priority."""
        assert MessagePriority.LOW.value == 1

    def test_priority_normal(self):
        """Test NORMAL priority."""
        assert MessagePriority.NORMAL.value == 5

    def test_priority_high(self):
        """Test HIGH priority."""
        assert MessagePriority.HIGH.value == 9

    def test_priority_comparison(self):
        """Test priority comparison."""
        assert MessagePriority.LOW < MessagePriority.NORMAL
        assert MessagePriority.NORMAL < MessagePriority.HIGH
        assert MessagePriority.LOW < MessagePriority.HIGH


# ============================================================================
# RoutingKey Tests
# ============================================================================


class TestRoutingKey:
    """Tests for RoutingKey model."""

    def test_routing_key_defaults(self):
        """Test RoutingKey with default values."""
        key = RoutingKey()
        assert key.topic is None
        assert key.tags == []

    def test_routing_key_with_topic(self):
        """Test RoutingKey with topic."""
        key = RoutingKey(topic="user_input")
        assert key.topic == "user_input"
        assert key.tags == []

    def test_routing_key_with_tags(self):
        """Test RoutingKey with tags."""
        key = RoutingKey(tags=["priority", "urgent"])
        assert key.topic is None
        assert key.tags == ["priority", "urgent"]

    def test_routing_key_full(self):
        """Test RoutingKey with all fields."""
        key = RoutingKey(topic="workflow", tags=["tag1", "tag2", "tag3"])
        assert key.topic == "workflow"
        assert len(key.tags) == 3

    def test_routing_key_serialization(self):
        """Test RoutingKey serialization."""
        key = RoutingKey(topic="test", tags=["tag1"])
        data = key.dict()
        assert data["topic"] == "test"
        assert data["tags"] == ["tag1"]

    def test_routing_key_deserialization(self):
        """Test RoutingKey deserialization."""
        data = {"topic": "test_topic", "tags": ["a", "b"]}
        key = RoutingKey(**data)
        assert key.topic == "test_topic"
        assert key.tags == ["a", "b"]


# ============================================================================
# AgentId Tests
# ============================================================================


class TestAgentId:
    """Tests for AgentId model."""

    def test_agent_id_with_type_only(self):
        """Test AgentId with only type."""
        agent_id = AgentId(type=AgentType.IPA)
        assert agent_id.type == AgentType.IPA
        assert agent_id.instance is None

    def test_agent_id_with_instance(self):
        """Test AgentId with instance."""
        agent_id = AgentId(type=AgentType.WBA, instance="wba_001")
        assert agent_id.type == AgentType.WBA
        assert agent_id.instance == "wba_001"

    def test_agent_id_serialization(self):
        """Test AgentId serialization."""
        agent_id = AgentId(type=AgentType.NGA, instance="nga_v2")
        data = agent_id.model_dump()
        assert data["type"] == "narrative_generator"
        assert data["instance"] == "nga_v2"

    def test_agent_id_deserialization(self):
        """Test AgentId deserialization."""
        data = {"type": AgentType.IPA, "instance": "ipa_prod"}
        agent_id = AgentId(**data)
        assert agent_id.type == AgentType.IPA
        assert agent_id.instance == "ipa_prod"

    def test_agent_id_equality(self):
        """Test AgentId equality."""
        id1 = AgentId(type=AgentType.IPA, instance="ipa_1")
        id2 = AgentId(type=AgentType.IPA, instance="ipa_1")
        id3 = AgentId(type=AgentType.IPA, instance="ipa_2")
        assert id1 == id2
        assert id1 != id3


# ============================================================================
# AgentMessage Tests
# ============================================================================


class TestAgentMessage:
    """Tests for AgentMessage model."""

    def test_agent_message_minimal(self):
        """Test AgentMessage with minimal required fields."""
        msg = AgentMessage(
            message_id="msg_001",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        assert msg.message_id == "msg_001"
        assert msg.sender.type == AgentType.IPA
        assert msg.recipient.type == AgentType.WBA
        assert msg.message_type == MessageType.REQUEST
        assert msg.priority == MessagePriority.NORMAL  # Default

    def test_agent_message_with_payload(self):
        """Test AgentMessage with payload."""
        payload = {"action": "process", "data": [1, 2, 3]}
        msg = AgentMessage(
            message_id="msg_002",
            sender=AgentId(type=AgentType.WBA),
            recipient=AgentId(type=AgentType.NGA),
            message_type=MessageType.RESPONSE,
            payload=payload,
        )
        assert msg.payload == payload

    def test_agent_message_with_priority(self):
        """Test AgentMessage with different priorities."""
        for priority in [
            MessagePriority.LOW,
            MessagePriority.NORMAL,
            MessagePriority.HIGH,
        ]:
            msg = AgentMessage(
                message_id=f"msg_{priority.name.lower()}",
                sender=AgentId(type=AgentType.IPA),
                recipient=AgentId(type=AgentType.WBA),
                message_type=MessageType.EVENT,
                priority=priority,
            )
            assert msg.priority == priority

    def test_agent_message_routing_defaults(self):
        """Test AgentMessage routing defaults."""
        msg = AgentMessage(
            message_id="msg_003",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        assert msg.routing is not None
        assert msg.routing.topic is None
        assert msg.routing.tags == []

    def test_agent_message_with_routing(self):
        """Test AgentMessage with custom routing."""
        routing = RoutingKey(topic="workflow", tags=["priority", "urgent"])
        msg = AgentMessage(
            message_id="msg_004",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
            routing=routing,
        )
        assert msg.routing.topic == "workflow"
        assert msg.routing.tags == ["priority", "urgent"]

    def test_agent_message_serialization(self):
        """Test AgentMessage serialization."""
        msg = AgentMessage(
            message_id="msg_005",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
            priority=MessagePriority.HIGH,
        )
        data = msg.model_dump()
        assert data["message_id"] == "msg_005"
        assert data["priority"] == 9  # HIGH priority value

    def test_agent_message_deserialization(self):
        """Test AgentMessage deserialization."""
        data = {
            "message_id": "msg_006",
            "sender": {"type": AgentType.IPA},
            "recipient": {"type": AgentType.WBA},
            "message_type": MessageType.REQUEST,
            "priority": 5,
        }
        msg = AgentMessage(**data)
        assert msg.message_id == "msg_006"
        assert msg.sender.type == AgentType.IPA
        assert msg.priority == MessagePriority.NORMAL


# ============================================================================
# OrchestrationRequest/Response Tests
# ============================================================================


class TestOrchestrationRequest:
    """Tests for OrchestrationRequest model."""

    def test_orchestration_request_defaults(self):
        """Test OrchestrationRequest with defaults."""
        req = OrchestrationRequest()
        assert req.session_id is None
        assert req.entrypoint == AgentType.IPA
        assert req.input == {}

    def test_orchestration_request_with_session(self):
        """Test OrchestrationRequest with session_id."""
        req = OrchestrationRequest(
            session_id="session_001",
            entrypoint=AgentType.WBA,
        )
        assert req.session_id == "session_001"
        assert req.entrypoint == AgentType.WBA

    def test_orchestration_request_with_input(self):
        """Test OrchestrationRequest with input."""
        input_data = {"query": "test", "mode": "async"}
        req = OrchestrationRequest(
            session_id="session_002",
            entrypoint=AgentType.NGA,
            input=input_data,
        )
        assert req.input == input_data

    def test_orchestration_request_serialization(self):
        """Test OrchestrationRequest serialization."""
        req = OrchestrationRequest(
            session_id="session_003",
            entrypoint=AgentType.IPA,
            input={"data": "test"},
        )
        data = req.model_dump()
        assert data["session_id"] == "session_003"
        assert data["entrypoint"] == "input_processor"
        assert data["input"] == {"data": "test"}


class TestOrchestrationResponse:
    """Tests for OrchestrationResponse model."""

    def test_orchestration_response_minimal(self):
        """Test OrchestrationResponse with minimal fields."""
        resp = OrchestrationResponse(
            response_text="Success",
        )
        assert resp.response_text == "Success"
        assert resp.updated_context == {}
        assert resp.workflow_metadata == {}

    def test_orchestration_response_with_context(self):
        """Test OrchestrationResponse with context."""
        context = {"state": "processed", "version": 1}
        resp = OrchestrationResponse(
            response_text="Completed",
            updated_context=context,
        )
        assert resp.updated_context == context

    def test_orchestration_response_with_metadata(self):
        """Test OrchestrationResponse with metadata."""
        metadata = {"duration_ms": 1500, "agent": "wba_001"}
        resp = OrchestrationResponse(
            response_text="Done",
            workflow_metadata=metadata,
        )
        assert resp.workflow_metadata == metadata

    def test_orchestration_response_serialization(self):
        """Test OrchestrationResponse serialization."""
        resp = OrchestrationResponse(
            response_text="Result",
            updated_context={"key": "value"},
            workflow_metadata={"id": "wf_001"},
        )
        data = resp.model_dump()
        assert data["response_text"] == "Result"
        assert data["updated_context"] == {"key": "value"}
        assert data["workflow_metadata"] == {"id": "wf_001"}


# ============================================================================
# Capability Tests
# ============================================================================


class TestCapabilityType:
    """Tests for CapabilityType enum."""

    def test_capability_type_values(self):
        """Test CapabilityType enum values."""
        assert CapabilityType.PROCESSING.value == "processing"
        assert CapabilityType.GENERATION.value == "generation"
        assert CapabilityType.ANALYSIS.value == "analysis"
        assert CapabilityType.COORDINATION.value == "coordination"
        assert CapabilityType.STORAGE.value == "storage"
        assert CapabilityType.COMMUNICATION.value == "communication"

    def test_capability_type_from_string(self):
        """Test creating CapabilityType from string."""
        assert CapabilityType("processing") == CapabilityType.PROCESSING
        assert CapabilityType("generation") == CapabilityType.GENERATION


class TestCapabilityScope:
    """Tests for CapabilityScope enum."""

    def test_capability_scope_values(self):
        """Test CapabilityScope enum values."""
        assert CapabilityScope.SESSION.value == "session"
        assert CapabilityScope.GLOBAL.value == "global"
        assert CapabilityScope.INSTANCE.value == "instance"

    def test_capability_scope_from_string(self):
        """Test creating CapabilityScope from string."""
        assert CapabilityScope("session") == CapabilityScope.SESSION
        assert CapabilityScope("global") == CapabilityScope.GLOBAL


class TestCapabilityStatus:
    """Tests for CapabilityStatus enum."""

    def test_capability_status_values(self):
        """Test CapabilityStatus enum values."""
        assert CapabilityStatus.ACTIVE.value == "active"
        assert CapabilityStatus.DEPRECATED.value == "deprecated"
        assert CapabilityStatus.DISABLED.value == "disabled"
        assert CapabilityStatus.EXPERIMENTAL.value == "experimental"

    def test_capability_status_from_string(self):
        """Test creating CapabilityStatus from string."""
        assert CapabilityStatus("active") == CapabilityStatus.ACTIVE
        assert CapabilityStatus("experimental") == CapabilityStatus.EXPERIMENTAL
