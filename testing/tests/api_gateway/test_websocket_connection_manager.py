"""
Tests for the API Gateway WebSocket connection manager.

This module contains unit tests for WebSocket connection management,
authentication integration, and therapeutic session handling.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from src.api_gateway.models import (
    AuthContext,
    ServiceEndpoint,
    ServiceInfo,
    ServiceType,
    UserPermissions,
    UserRole,
)
from src.api_gateway.websocket.connection_manager import (
    ConnectionStatus,
    ConnectionType,
    WebSocketConnection,
    WebSocketConnectionManager,
)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket."""
    websocket = MagicMock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.client_state = WebSocketState.CONNECTED
    websocket.client.host = "127.0.0.1"
    websocket.headers = {"user-agent": "test-client"}
    return websocket


@pytest.fixture
def mock_auth_context():
    """Create a mock authentication context."""
    auth_context = MagicMock(spec=AuthContext)
    auth_context.user_id = uuid4()
    auth_context.username = "test_user"
    auth_context.permissions = UserPermissions(role=UserRole.PATIENT)
    auth_context.crisis_mode = False
    auth_context.is_therapeutic_context.return_value = True
    return auth_context


@pytest.fixture
def mock_service_info():
    """Create a mock service info."""
    return ServiceInfo(
        id=uuid4(),
        name="test-service",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8080),
    )


@pytest.fixture
async def connection_manager():
    """Create a WebSocket connection manager."""
    manager = WebSocketConnectionManager()
    yield manager
    await manager.shutdown()


class TestWebSocketConnectionManager:
    """Test cases for WebSocketConnectionManager."""

    @pytest.mark.asyncio
    async def test_connect_success(
        self, connection_manager, mock_websocket, mock_auth_context
    ):
        """Test successful WebSocket connection."""
        connection_id = await connection_manager.connect(
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
            auth_context=mock_auth_context,
        )

        assert connection_id is not None
        assert connection_id in connection_manager.connections

        connection = connection_manager.get_connection(connection_id)
        assert connection is not None
        assert connection.connection_type == ConnectionType.CHAT
        assert connection.user_id == str(mock_auth_context.user_id)
        assert connection.username == mock_auth_context.username
        assert connection.status == ConnectionStatus.CONNECTED

        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_without_auth(self, connection_manager, mock_websocket):
        """Test WebSocket connection without authentication."""
        connection_id = await connection_manager.connect(
            websocket=mock_websocket, connection_type=ConnectionType.CHAT
        )

        assert connection_id is not None
        connection = connection_manager.get_connection(connection_id)
        assert connection.user_id is None
        assert connection.username is None
        assert connection.auth_context is None

    @pytest.mark.asyncio
    async def test_connect_therapeutic_session(
        self, connection_manager, mock_websocket, mock_auth_context
    ):
        """Test therapeutic session connection."""
        session_id = "therapeutic-session-123"

        connection_id = await connection_manager.connect(
            websocket=mock_websocket,
            connection_type=ConnectionType.THERAPEUTIC_SESSION,
            auth_context=mock_auth_context,
            therapeutic_session_id=session_id,
        )

        connection = connection_manager.get_connection(connection_id)
        assert connection.therapeutic_session_id == session_id
        assert connection.is_therapeutic() is True

        # Check session indexing
        session_connections = connection_manager.get_session_connections(session_id)
        assert len(session_connections) == 1
        assert session_connections[0].connection_id == connection_id

    @pytest.mark.asyncio
    async def test_connect_crisis_mode(
        self, connection_manager, mock_websocket, mock_auth_context
    ):
        """Test crisis mode connection."""
        mock_auth_context.crisis_mode = True

        connection_id = await connection_manager.connect(
            websocket=mock_websocket,
            connection_type=ConnectionType.CRISIS_SUPPORT,
            auth_context=mock_auth_context,
        )

        connection = connection_manager.get_connection(connection_id)
        assert connection.crisis_mode is True
        assert connection.is_crisis() is True

    @pytest.mark.asyncio
    async def test_connect_max_connections_exceeded(
        self, connection_manager, mock_websocket
    ):
        """Test connection rejection when max connections exceeded."""
        # Set low limit for testing
        connection_manager.max_total_connections = 1

        # First connection should succeed
        await connection_manager.connect(mock_websocket, ConnectionType.CHAT)

        # Second connection should fail
        mock_websocket2 = MagicMock(spec=WebSocket)
        mock_websocket2.accept = AsyncMock()
        mock_websocket2.close = AsyncMock()

        with pytest.raises(Exception, match="Maximum connections exceeded"):
            await connection_manager.connect(mock_websocket2, ConnectionType.CHAT)

        mock_websocket2.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_max_per_user_exceeded(
        self, connection_manager, mock_websocket, mock_auth_context
    ):
        """Test connection rejection when max per user exceeded."""
        # Set low limit for testing
        connection_manager.max_connections_per_user = 1

        # First connection should succeed
        await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT, mock_auth_context
        )

        # Second connection for same user should fail
        mock_websocket2 = MagicMock(spec=WebSocket)
        mock_websocket2.accept = AsyncMock()
        mock_websocket2.close = AsyncMock()

        with pytest.raises(Exception, match="Maximum connections per user exceeded"):
            await connection_manager.connect(
                mock_websocket2, ConnectionType.CHAT, mock_auth_context
            )

        mock_websocket2.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(
        self, connection_manager, mock_websocket, mock_auth_context
    ):
        """Test WebSocket disconnection."""
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT, mock_auth_context
        )

        # Verify connection exists
        assert connection_id in connection_manager.connections

        # Disconnect
        await connection_manager.disconnect(connection_id, "test_disconnect")

        # Verify connection removed
        assert connection_id not in connection_manager.connections
        mock_websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self, connection_manager):
        """Test disconnecting non-existent connection."""
        # Should not raise exception
        await connection_manager.disconnect("nonexistent-id", "test")

    @pytest.mark.asyncio
    async def test_get_user_connections(self, connection_manager, mock_auth_context):
        """Test getting connections for a user."""
        # Create multiple connections for same user
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.client.host = "127.0.0.1"
        mock_ws1.headers = {}

        mock_ws2 = MagicMock(spec=WebSocket)
        mock_ws2.accept = AsyncMock()
        mock_ws2.client.host = "127.0.0.1"
        mock_ws2.headers = {}

        conn_id1 = await connection_manager.connect(
            mock_ws1, ConnectionType.CHAT, mock_auth_context
        )
        conn_id2 = await connection_manager.connect(
            mock_ws2, ConnectionType.NARRATIVE, mock_auth_context
        )

        user_connections = connection_manager.get_user_connections(
            str(mock_auth_context.user_id)
        )

        assert len(user_connections) == 2
        connection_ids = [conn.connection_id for conn in user_connections]
        assert conn_id1 in connection_ids
        assert conn_id2 in connection_ids

    @pytest.mark.asyncio
    async def test_send_message_success(self, connection_manager, mock_websocket):
        """Test successful message sending."""
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )

        message = {"type": "test", "data": "hello"}
        result = await connection_manager.send_message(connection_id, message)

        assert result is True
        mock_websocket.send_text.assert_called_once()

        # Verify message content
        sent_message = mock_websocket.send_text.call_args[0][0]
        import json

        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "test"
        assert parsed_message["data"] == "hello"

    @pytest.mark.asyncio
    async def test_send_message_connection_error(
        self, connection_manager, mock_websocket
    ):
        """Test message sending with connection error."""
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )

        # Mock send error
        mock_websocket.send_text.side_effect = Exception("Connection broken")

        message = {"type": "test", "data": "hello"}
        result = await connection_manager.send_message(connection_id, message)

        assert result is False
        # Connection should be removed after error
        assert connection_id not in connection_manager.connections

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, connection_manager, mock_auth_context):
        """Test broadcasting message to all user connections."""
        # Create multiple connections for user
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws1.client.host = "127.0.0.1"
        mock_ws1.headers = {}

        mock_ws2 = MagicMock(spec=WebSocket)
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_text = AsyncMock()
        mock_ws2.client.host = "127.0.0.1"
        mock_ws2.headers = {}

        await connection_manager.connect(
            mock_ws1, ConnectionType.CHAT, mock_auth_context
        )
        await connection_manager.connect(
            mock_ws2, ConnectionType.NARRATIVE, mock_auth_context
        )

        message = {"type": "broadcast", "data": "hello all"}
        sent_count = await connection_manager.broadcast_to_user(
            str(mock_auth_context.user_id), message
        )

        assert sent_count == 2
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_session(self, connection_manager, mock_auth_context):
        """Test broadcasting message to therapeutic session."""
        session_id = "session-123"

        # Create connections in same session
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws1.client.host = "127.0.0.1"
        mock_ws1.headers = {}

        mock_ws2 = MagicMock(spec=WebSocket)
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_text = AsyncMock()
        mock_ws2.client.host = "127.0.0.1"
        mock_ws2.headers = {}

        await connection_manager.connect(
            mock_ws1,
            ConnectionType.THERAPEUTIC_SESSION,
            mock_auth_context,
            therapeutic_session_id=session_id,
        )
        await connection_manager.connect(
            mock_ws2,
            ConnectionType.THERAPEUTIC_SESSION,
            mock_auth_context,
            therapeutic_session_id=session_id,
        )

        message = {"type": "session_broadcast", "data": "session message"}
        sent_count = await connection_manager.broadcast_to_session(session_id, message)

        assert sent_count == 2
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

    def test_get_connection_stats(self, connection_manager):
        """Test getting connection statistics."""
        stats = connection_manager.get_connection_stats()

        assert "total_connections" in stats
        assert "therapeutic_connections" in stats
        assert "crisis_connections" in stats
        assert "unique_users" in stats
        assert "active_sessions" in stats
        assert "connection_types" in stats
        assert "connection_status" in stats
        assert "max_connections" in stats
        assert "max_per_user" in stats

        assert stats["total_connections"] == 0
        assert stats["max_connections"] == connection_manager.max_total_connections

    @pytest.mark.asyncio
    async def test_idle_connection_cleanup(self, connection_manager, mock_websocket):
        """Test cleanup of idle connections."""
        # Set short idle timeout for testing
        connection_manager.idle_timeout = 0.1

        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )

        # Wait for idle timeout
        await asyncio.sleep(0.2)

        # Trigger cleanup
        await connection_manager._remove_idle_connections()

        # Connection should be removed
        assert connection_id not in connection_manager.connections
        mock_websocket.close.assert_called()


class TestWebSocketConnection:
    """Test cases for WebSocketConnection."""

    def test_is_therapeutic(self, mock_websocket, mock_auth_context):
        """Test therapeutic connection detection."""
        # Therapeutic session type
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.THERAPEUTIC_SESSION,
        )
        assert connection.is_therapeutic() is True

        # Crisis support type
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CRISIS_SUPPORT,
        )
        assert connection.is_therapeutic() is True

        # With therapeutic session ID
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
            therapeutic_session_id="session-123",
        )
        assert connection.is_therapeutic() is True

        # Regular chat
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
        )
        assert connection.is_therapeutic() is False

    def test_is_crisis(self, mock_websocket):
        """Test crisis connection detection."""
        # Crisis support type
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CRISIS_SUPPORT,
        )
        assert connection.is_crisis() is True

        # Crisis mode flag
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
            crisis_mode=True,
        )
        assert connection.is_crisis() is True

        # Regular connection
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
        )
        assert connection.is_crisis() is False

    def test_activity_tracking(self, mock_websocket):
        """Test activity tracking."""
        connection = WebSocketConnection(
            connection_id="test",
            websocket=mock_websocket,
            connection_type=ConnectionType.CHAT,
        )

        initial_activity = connection.last_activity

        # Update activity
        connection.update_activity()

        assert connection.last_activity > initial_activity
        assert connection.get_idle_time() >= 0
        assert connection.get_connection_duration() >= 0
