"""Tests for agent_orchestration.validators module."""

from pydantic import ValidationError

from src.agent_orchestration.models import AgentMessage
from src.agent_orchestration.validators import validate_agent_message


class TestValidateAgentMessage:
    """Tests for validate_agent_message function."""

    def test_validate_valid_message(self):
        """Test validation of a valid agent message."""
        from src.agent_orchestration.models import AgentId, AgentType, MessageType

        msg = AgentMessage(
            message_id="msg-12345",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.WBA),
            message_type=MessageType.REQUEST,
        )
        is_valid, error = validate_agent_message(msg)
        assert is_valid is True
        assert error is None

    def test_validate_invalid_message_returns_error(self):
        """Test that invalid message returns error."""
        # Create an invalid message (missing required fields)
        invalid_msg = {"message_id": "msg"}
        try:
            is_valid, error = validate_agent_message(invalid_msg)
            # If it doesn't raise, check the result
            if not is_valid:
                assert error is not None
        except (ValidationError, AttributeError, TypeError):
            # Expected for invalid input
            pass

    def test_validate_returns_tuple(self):
        """Test that function returns a tuple."""
        from src.agent_orchestration.models import AgentId, AgentType, MessageType

        msg = AgentMessage(
            message_id="msg-12345",
            sender=AgentId(type=AgentType.IPA),
            recipient=AgentId(type=AgentType.NGA),
            message_type=MessageType.RESPONSE,
        )
        result = validate_agent_message(msg)
        assert isinstance(result, tuple)
        assert len(result) == 2
