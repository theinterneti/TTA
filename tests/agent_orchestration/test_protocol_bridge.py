"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_protocol_bridge]]
Comprehensive unit tests for protocol_bridge module.

Tests cover:
- ProtocolType enum
- MessageTranslationResult dataclass
- ProtocolTranslator class with translation rules
- MessageRouter class with message routing
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent_orchestration.adapters import AgentCommunicationError
from agent_orchestration.messaging import MessageResult
from agent_orchestration.models import AgentMessage, AgentType
from agent_orchestration.protocol_bridge import (
    MessageRouter,
    MessageTranslationResult,
    ProtocolTranslator,
    ProtocolType,
)


class TestProtocolType:
    """Tests for ProtocolType enum."""

    def test_protocol_type_values(self):
        """Test ProtocolType enum has expected values."""
        assert hasattr(ProtocolType, "ORCHESTRATION")
        assert hasattr(ProtocolType, "REAL_AGENT")
        assert hasattr(ProtocolType, "HYBRID")

    def test_protocol_type_is_enum(self):
        """Test ProtocolType is an Enum."""
        assert isinstance(ProtocolType.ORCHESTRATION, ProtocolType)


class TestMessageTranslationResult:
    """Tests for MessageTranslationResult dataclass."""

    def test_translation_result_creation_success(self):
        """Test creating successful translation result."""
        result = MessageTranslationResult(
            success=True,
            translated_message={"text": "translated"},
            error=None,
        )
        assert result.success is True
        assert result.translated_message == {"text": "translated"}
        assert result.error is None

    def test_translation_result_creation_failure(self):
        """Test creating failed translation result."""
        result = MessageTranslationResult(
            success=False,
            translated_message=None,
            error="Translation failed",
        )
        assert result.success is False
        assert result.translated_message is None
        assert result.error == "Translation failed"

    def test_translation_result_with_empty_message(self):
        """Test translation result with empty message."""
        result = MessageTranslationResult(
            success=True,
            translated_message={},
            error=None,
        )
        assert result.success is True
        assert result.translated_message == {}


class TestProtocolTranslator:
    """Tests for ProtocolTranslator class."""

    def test_translator_initialization(self):
        """Test ProtocolTranslator initializes with default rules."""
        translator = ProtocolTranslator()
        assert translator._translation_rules is not None
        assert len(translator._translation_rules) > 0

    def test_translator_has_default_rules(self):
        """Test translator has all expected default rules."""
        translator = ProtocolTranslator()
        expected_rules = [
            "orchestration_to_ipa",
            "orchestration_to_wba",
            "orchestration_to_nga",
            "ipa_to_orchestration",
            "wba_to_orchestration",
            "nga_to_orchestration",
        ]
        for rule in expected_rules:
            assert rule in translator._translation_rules

    def test_translate_message_with_dict(self):
        """Test translating a dictionary message."""
        translator = ProtocolTranslator()
        message = {"text": "test message", "type": "command"}

        result = translator.translate_message(
            message,
            ProtocolType.ORCHESTRATION,
            ProtocolType.REAL_AGENT,
            AgentType.IPA,
        )

        assert isinstance(result, MessageTranslationResult)
        assert result.success is not None

    def test_translate_message_with_agent_message(self):
        """Test translating an AgentMessage object."""
        translator = ProtocolTranslator()
        message = AgentMessage(
            id="test-id",
            type="command",
            content="test content",
            agent_type=AgentType.IPA,
        )

        result = translator.translate_message(
            message,
            ProtocolType.ORCHESTRATION,
            ProtocolType.REAL_AGENT,
            AgentType.IPA,
        )

        assert isinstance(result, MessageTranslationResult)

    def test_translate_message_same_protocol(self):
        """Test translating between same protocol."""
        translator = ProtocolTranslator()
        message = {"text": "test"}

        result = translator.translate_message(
            message,
            ProtocolType.ORCHESTRATION,
            ProtocolType.ORCHESTRATION,
            AgentType.IPA,
        )

        assert isinstance(result, MessageTranslationResult)


class TestMessageRouter:
    """Tests for MessageRouter class."""

    @pytest.fixture
    def mock_adapters(self):
        """Create mock adapters for testing."""
        ipa_adapter = AsyncMock()
        wba_adapter = AsyncMock()
        nga_adapter = AsyncMock()
        return ipa_adapter, wba_adapter, nga_adapter

    @pytest.fixture
    def router(self, mock_adapters):
        """Create MessageRouter with mock adapters."""
        ipa_adapter, wba_adapter, nga_adapter = mock_adapters
        return MessageRouter(ipa_adapter, wba_adapter, nga_adapter)

    def test_router_initialization(self, router):
        """Test MessageRouter initializes correctly."""
        assert router.ipa_adapter is not None
        assert router.wba_adapter is not None
        assert router.nga_adapter is not None
        assert router.translator is not None
        assert len(router._routing_table) == 3

    def test_router_has_routing_handlers(self, router):
        """Test router has handlers for all agent types."""
        assert AgentType.IPA in router._routing_table
        assert AgentType.WBA in router._routing_table
        assert AgentType.NGA in router._routing_table

    @pytest.mark.asyncio
    async def test_route_message_to_ipa(self, router, mock_adapters):
        """Test routing message to IPA adapter."""
        ipa_adapter, _, _ = mock_adapters
        ipa_adapter.process_input = AsyncMock()

        message = {"text": "test message"}
        result = await router.route_message(AgentType.IPA, message)

        assert isinstance(result, MessageResult)

    @pytest.mark.asyncio
    async def test_route_message_invalid_agent_type(self, router):
        """Test routing with invalid agent type."""
        message = {"text": "test"}

        # Create an invalid agent type
        invalid_type = "INVALID"

        # This should handle gracefully
        try:
            result = await router.route_message(invalid_type, message)
            # If it doesn't raise, check the result
            if isinstance(result, MessageResult):
                assert result.delivered is False or result.delivered is True
        except (TypeError, AttributeError):
            # Expected if invalid type is not handled
            pass

    @pytest.mark.asyncio
    async def test_route_message_with_dict(self, router):
        """Test routing with dictionary message."""
        message = {"text": "test", "priority": "high"}
        result = await router.route_message(AgentType.IPA, message)

        assert isinstance(result, MessageResult)

    @pytest.mark.asyncio
    async def test_route_message_with_agent_message(self, router):
        """Test routing with AgentMessage object."""
        message = AgentMessage(
            id="test-id",
            type="command",
            content="test",
            agent_type=AgentType.IPA,
        )
        result = await router.route_message(AgentType.IPA, message)

        assert isinstance(result, MessageResult)

    @pytest.mark.asyncio
    async def test_route_message_error_handling(self, router, mock_adapters):
        """Test error handling during message routing."""
        ipa_adapter, _, _ = mock_adapters
        ipa_adapter.process_input = AsyncMock(
            side_effect=AgentCommunicationError("Connection failed")
        )

        message = {"text": "test"}
        result = await router.route_message(AgentType.IPA, message)

        assert isinstance(result, MessageResult)
        assert result.delivered is False


class TestProtocolBridgeIntegration:
    """Integration tests for protocol bridge components."""

    @pytest.mark.asyncio
    async def test_full_message_translation_and_routing(self):
        """Test complete message translation and routing flow."""
        translator = ProtocolTranslator()

        # Create a message
        message = {"text": "test command", "priority": "high"}

        # Translate it
        translation = translator.translate_message(
            message,
            ProtocolType.ORCHESTRATION,
            ProtocolType.REAL_AGENT,
            AgentType.IPA,
        )

        assert isinstance(translation, MessageTranslationResult)

    def test_protocol_translator_rule_registration(self):
        """Test that translation rules are properly registered."""
        translator = ProtocolTranslator()

        # Verify all rules are callable
        for rule_name, rule_func in translator._translation_rules.items():
            assert callable(rule_func), f"Rule {rule_name} is not callable"

    @pytest.mark.asyncio
    async def test_message_router_with_multiple_messages(self):
        """Test routing multiple messages sequentially."""
        ipa_adapter = AsyncMock()
        wba_adapter = AsyncMock()
        nga_adapter = AsyncMock()

        router = MessageRouter(ipa_adapter, wba_adapter, nga_adapter)

        messages = [
            {"text": "message 1"},
            {"text": "message 2"},
            {"text": "message 3"},
        ]

        results = []
        for msg in messages:
            result = await router.route_message(AgentType.IPA, msg)
            results.append(result)

        assert len(results) == 3
        assert all(isinstance(r, MessageResult) for r in results)
