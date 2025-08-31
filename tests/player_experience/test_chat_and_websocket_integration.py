"""
Tests for Chat and WebSocket Integration

This test suite covers the WebSocket communication layer and chat management
for real-time gameplay interactions.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.player_experience.models.gameplay_messages import (
    ChoiceRequestMessage,
    GameplayMessageType,
    NarrativeResponseMessage,
)
from src.player_experience.routers.gameplay_websocket_router import (
    GameplayWebSocketRouter,
)
from src.player_experience.services.gameplay_chat_manager import GameplayChatManager


@pytest.fixture
async def chat_manager():
    """Create chat manager for testing."""
    manager = GameplayChatManager()
    await manager.start()
    yield manager
    await manager.stop()


@pytest.fixture
def mock_websocket():
    """Create mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def sample_gameplay_messages():
    """Sample gameplay messages for testing."""
    return {
        "narrative_response": {
            "type": GameplayMessageType.NARRATIVE_RESPONSE.value,
            "session_id": "test_session_001",
            "content": {
                "text": "You find yourself in a peaceful garden...",
                "scene_updates": {"location": "garden_entrance"},
                "therapeutic_elements": {
                    "mindfulness_cue": "Notice the sounds around you"
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
        "choice_request": {
            "type": GameplayMessageType.CHOICE_REQUEST.value,
            "session_id": "test_session_001",
            "content": {
                "prompt": "What would you like to do?",
                "choices": [
                    {"id": "choice_1", "text": "Sit by the fountain"},
                    {"id": "choice_2", "text": "Walk through the flowers"},
                ],
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
        "player_input": {
            "type": GameplayMessageType.PLAYER_INPUT.value,
            "session_id": "test_session_001",
            "content": {
                "text": "I want to explore the garden and find peace",
                "input_type": "narrative_action",
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


class TestGameplayChatManager:
    """Test the gameplay chat manager functionality."""

    @pytest.mark.asyncio
    async def test_connection_management(self, chat_manager, mock_websocket):
        """Test WebSocket connection management."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Test adding connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        assert connection_id is not None
        assert len(chat_manager.active_connections) == 1

        # Test getting connection
        connection = chat_manager.get_connection(connection_id)
        assert connection is not None
        assert connection.player_id == player_id
        assert connection.session_id == session_id

        # Test removing connection
        await chat_manager.remove_connection(connection_id)
        assert len(chat_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_message_broadcasting(
        self, chat_manager, mock_websocket, sample_gameplay_messages
    ):
        """Test message broadcasting to sessions."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Test broadcasting to session
        message = sample_gameplay_messages["narrative_response"]
        sent_count = await chat_manager.broadcast_to_session(session_id, message)

        assert sent_count == 1
        mock_websocket.send_text.assert_called_once()

        # Verify message content
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == GameplayMessageType.NARRATIVE_RESPONSE.value
        assert sent_message["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_player_message_processing(
        self, chat_manager, mock_websocket, sample_gameplay_messages
    ):
        """Test processing of player messages."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Mock message processing
        with patch.object(
            chat_manager, "_process_player_message", return_value=True
        ) as mock_process:
            message = sample_gameplay_messages["player_input"]

            result = await chat_manager.handle_player_message(connection_id, message)

            assert result is True
            mock_process.assert_called_once_with(connection_id, message)

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self, chat_manager, mock_websocket):
        """Test connection cleanup when WebSocket disconnects."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Simulate disconnect
        await chat_manager.handle_disconnect(connection_id)

        # Verify cleanup
        assert len(chat_manager.active_connections) == 0
        assert connection_id not in chat_manager.session_connections.get(session_id, [])

    @pytest.mark.asyncio
    async def test_multiple_connections_per_session(self, chat_manager):
        """Test handling multiple connections for the same session."""
        session_id = "test_session_001"

        # Add multiple connections for same session
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()

        connection_id1 = await chat_manager.add_connection(
            websocket1, "player_001", session_id
        )
        connection_id2 = await chat_manager.add_connection(
            websocket2, "player_002", session_id
        )

        assert len(chat_manager.active_connections) == 2
        assert len(chat_manager.session_connections[session_id]) == 2

        # Test broadcasting to all connections in session
        message = {"type": "test", "content": "test message"}
        sent_count = await chat_manager.broadcast_to_session(session_id, message)

        assert sent_count == 2
        websocket1.send_text.assert_called_once()
        websocket2.send_text.assert_called_once()


class TestGameplayWebSocketRouter:
    """Test the gameplay WebSocket router."""

    @pytest.mark.asyncio
    async def test_websocket_connection_flow(self):
        """Test WebSocket connection establishment and flow."""
        router = GameplayWebSocketRouter()

        # Mock dependencies
        mock_websocket = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps({"type": "connection_init", "player_id": "test_player"}),
                json.dumps({"type": "player_input", "content": {"text": "Hello"}}),
                asyncio.CancelledError(),  # Simulate disconnect
            ]
        )

        with patch.object(router, "chat_manager") as mock_chat_manager:
            mock_chat_manager.add_connection = AsyncMock(return_value="conn_001")
            mock_chat_manager.handle_player_message = AsyncMock(return_value=True)
            mock_chat_manager.remove_connection = AsyncMock()

            # Test connection handling
            with pytest.raises(asyncio.CancelledError):
                await router.websocket_endpoint(
                    mock_websocket, "test_player", "test_session"
                )

            # Verify connection lifecycle
            mock_chat_manager.add_connection.assert_called_once()
            mock_chat_manager.handle_player_message.assert_called_once()
            mock_chat_manager.remove_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_validation(self):
        """Test message validation in WebSocket router."""
        router = GameplayWebSocketRouter()

        # Test valid message
        valid_message = {
            "type": GameplayMessageType.PLAYER_INPUT.value,
            "content": {"text": "I want to explore"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        is_valid = router._validate_message(valid_message)
        assert is_valid

        # Test invalid message
        invalid_message = {"type": "invalid_type", "content": {}}

        is_valid = router._validate_message(invalid_message)
        assert not is_valid

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in WebSocket communication."""
        router = GameplayWebSocketRouter()

        mock_websocket = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=Exception("Connection error")
        )

        with patch.object(router, "chat_manager") as mock_chat_manager:
            mock_chat_manager.add_connection = AsyncMock(return_value="conn_001")
            mock_chat_manager.remove_connection = AsyncMock()

            # Should handle exception gracefully
            await router.websocket_endpoint(
                mock_websocket, "test_player", "test_session"
            )

            # Verify cleanup occurred
            mock_chat_manager.remove_connection.assert_called_once()


class TestGameplayMessageModels:
    """Test gameplay message models and validation."""

    def test_narrative_response_message_creation(self):
        """Test creating narrative response messages."""
        message = NarrativeResponseMessage(
            session_id="test_session",
            content={
                "text": "You enter a peaceful garden...",
                "scene_updates": {"location": "garden"},
                "therapeutic_elements": {"mindfulness": True},
            },
        )

        assert message.type == GameplayMessageType.NARRATIVE_RESPONSE
        assert message.session_id == "test_session"
        assert "text" in message.content
        assert message.content["text"] == "You enter a peaceful garden..."

    def test_choice_request_message_creation(self):
        """Test creating choice request messages."""
        choices = [
            {"id": "choice_1", "text": "Sit by the fountain"},
            {"id": "choice_2", "text": "Walk among the flowers"},
        ]

        message = ChoiceRequestMessage(
            session_id="test_session",
            content={"prompt": "What would you like to do?", "choices": choices},
        )

        assert message.type == GameplayMessageType.CHOICE_REQUEST
        assert message.content["prompt"] == "What would you like to do?"
        assert len(message.content["choices"]) == 2

    def test_message_serialization(self):
        """Test message serialization to JSON."""
        message = NarrativeResponseMessage(
            session_id="test_session", content={"text": "Test narrative"}
        )

        # Test dict conversion
        message_dict = message.dict()
        assert message_dict["type"] == GameplayMessageType.NARRATIVE_RESPONSE.value
        assert message_dict["session_id"] == "test_session"

        # Test JSON serialization
        json_str = message.json()
        parsed = json.loads(json_str)
        assert parsed["type"] == GameplayMessageType.NARRATIVE_RESPONSE.value


class TestRealTimePerformance:
    """Test real-time performance characteristics."""

    @pytest.mark.asyncio
    async def test_concurrent_message_handling(self, chat_manager):
        """Test handling multiple concurrent messages."""
        session_id = "test_session_001"

        # Create multiple connections
        connections = []
        for i in range(5):
            websocket = AsyncMock()
            connection_id = await chat_manager.add_connection(
                websocket, f"player_{i}", session_id
            )
            connections.append((connection_id, websocket))

        # Send messages concurrently
        messages = [{"type": "test", "content": f"Message {i}"} for i in range(10)]

        start_time = datetime.utcnow()

        tasks = [
            chat_manager.broadcast_to_session(session_id, message)
            for message in messages
        ]

        results = await asyncio.gather(*tasks)

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Verify performance (should handle 10 messages in under 5 seconds)
        assert processing_time < 5

        # Verify all messages were sent
        assert all(result == 5 for result in results)  # 5 connections per message

    @pytest.mark.asyncio
    async def test_message_throughput(self, chat_manager, mock_websocket):
        """Test message throughput under load."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Send many messages rapidly
        message_count = 100
        messages = [
            {"type": "test", "content": f"Message {i}"} for i in range(message_count)
        ]

        start_time = datetime.utcnow()

        for message in messages:
            await chat_manager.broadcast_to_session(session_id, message)

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Calculate throughput
        throughput = message_count / processing_time

        # Should handle at least 20 messages per second
        assert throughput >= 20

        # Verify all messages were sent
        assert mock_websocket.send_text.call_count == message_count


@pytest.mark.integration
class TestWebSocketIntegrationWithServices:
    """Test WebSocket integration with other services."""

    @pytest.mark.asyncio
    async def test_story_service_integration(self, chat_manager, mock_websocket):
        """Test integration with story generation services."""
        from src.player_experience.services.dynamic_story_generation_service import (
            DynamicStoryGenerationService,
        )

        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Mock story service
        story_service = AsyncMock(spec=DynamicStoryGenerationService)
        story_service.process_player_message = AsyncMock(
            return_value=MagicMock(
                narrative_text="You explore the garden...",
                response_type="narrative_response",
            )
        )

        # Integrate story service with chat manager
        chat_manager.story_service = story_service

        # Test player message processing
        player_message = {
            "type": GameplayMessageType.PLAYER_INPUT.value,
            "content": {"text": "I want to explore the garden"},
        }

        with patch.object(chat_manager, "_process_player_message") as mock_process:
            mock_process.return_value = True

            result = await chat_manager.handle_player_message(
                connection_id, player_message
            )

            assert result is True
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_safety_integration(self, chat_manager, mock_websocket):
        """Test integration with therapeutic safety monitoring."""
        from src.player_experience.services.therapeutic_safety_integration import (
            TherapeuticSafetyIntegration,
        )

        player_id = "test_player_001"
        session_id = "test_session_001"

        # Add connection
        connection_id = await chat_manager.add_connection(
            mock_websocket, player_id, session_id
        )

        # Mock safety service
        safety_service = AsyncMock(spec=TherapeuticSafetyIntegration)
        safety_service.monitor_player_message = AsyncMock(
            return_value=None
        )  # No safety alert

        # Integrate safety service
        chat_manager.safety_service = safety_service

        # Test message monitoring
        player_message = {
            "type": GameplayMessageType.PLAYER_INPUT.value,
            "content": {"text": "I'm feeling anxious about this situation"},
        }

        with patch.object(chat_manager, "_process_player_message") as mock_process:
            mock_process.return_value = True

            result = await chat_manager.handle_player_message(
                connection_id, player_message
            )

            assert result is True
            # Verify safety monitoring was called
            safety_service.monitor_player_message.assert_called_once_with(
                player_id, session_id, "I'm feeling anxious about this situation", None
            )
