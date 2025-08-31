"""
Tests for the API Gateway WebSocket proxy.

This module contains unit tests for WebSocket proxying functionality,
message routing, and backend service integration.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import WebSocket

from src.api_gateway.core.service_router import ServiceRouter
from src.api_gateway.models import (
    AuthContext,
    ServiceEndpoint,
    ServiceInfo,
    ServiceType,
    UserPermissions,
    UserRole,
)
from src.api_gateway.services import ServiceDiscoveryManager
from src.api_gateway.websocket.connection_manager import (
    ConnectionType,
    WebSocketConnectionManager,
)
from src.api_gateway.websocket.proxy import WebSocketProxy


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket."""
    websocket = MagicMock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
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


@pytest.fixture
def mock_service_router():
    """Create a mock service router."""
    router = AsyncMock(spec=ServiceRouter)
    return router


@pytest.fixture
def mock_discovery_manager():
    """Create a mock service discovery manager."""
    manager = AsyncMock(spec=ServiceDiscoveryManager)
    return manager


@pytest.fixture
def websocket_proxy(connection_manager, mock_service_router, mock_discovery_manager):
    """Create a WebSocket proxy."""
    return WebSocketProxy(
        connection_manager, mock_service_router, mock_discovery_manager
    )


class TestWebSocketProxy:
    """Test cases for WebSocketProxy."""

    @pytest.mark.asyncio
    async def test_select_backend_service_success(
        self, websocket_proxy, mock_service_info, mock_auth_context
    ):
        """Test successful backend service selection."""
        websocket_proxy.service_router.select_service.return_value = mock_service_info

        service = await websocket_proxy._select_backend_service(
            "test-service", mock_auth_context
        )

        assert service == mock_service_info
        websocket_proxy.service_router.select_service.assert_called_once()

        # Check that gateway request was created with correct context
        call_args = websocket_proxy.service_router.select_service.call_args
        gateway_request = call_args[0][1]  # Second argument is gateway_request

        assert gateway_request.is_therapeutic is True
        assert gateway_request.crisis_mode is False
        assert gateway_request.auth_context["user_id"] == str(mock_auth_context.user_id)
        assert gateway_request.auth_context["username"] == mock_auth_context.username

    @pytest.mark.asyncio
    async def test_select_backend_service_crisis_mode(
        self, websocket_proxy, mock_service_info, mock_auth_context
    ):
        """Test backend service selection in crisis mode."""
        mock_auth_context.crisis_mode = True
        websocket_proxy.service_router.select_service.return_value = mock_service_info

        service = await websocket_proxy._select_backend_service(
            "test-service", mock_auth_context
        )

        call_args = websocket_proxy.service_router.select_service.call_args
        gateway_request = call_args[0][1]

        assert gateway_request.crisis_mode is True

    @pytest.mark.asyncio
    async def test_select_backend_service_no_auth(
        self, websocket_proxy, mock_service_info
    ):
        """Test backend service selection without authentication."""
        websocket_proxy.service_router.select_service.return_value = mock_service_info

        service = await websocket_proxy._select_backend_service("test-service", None)

        call_args = websocket_proxy.service_router.select_service.call_args
        gateway_request = call_args[0][1]

        assert gateway_request.is_therapeutic is False
        assert gateway_request.crisis_mode is False
        assert gateway_request.auth_context is None

    @pytest.mark.asyncio
    async def test_select_backend_service_error(
        self, websocket_proxy, mock_auth_context
    ):
        """Test backend service selection error handling."""
        websocket_proxy.service_router.select_service.side_effect = Exception(
            "Service error"
        )

        service = await websocket_proxy._select_backend_service(
            "test-service", mock_auth_context
        )

        assert service is None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_connect_to_backend_success(
        self, mock_session_class, websocket_proxy, mock_service_info, mock_auth_context
    ):
        """Test successful backend connection."""
        # Mock aiohttp session and WebSocket
        mock_session = MagicMock()
        mock_backend_ws = AsyncMock()
        mock_session.ws_connect.return_value = mock_backend_ws
        mock_session_class.return_value = mock_session

        backend_key = await websocket_proxy._connect_to_backend(
            mock_service_info, "connection-123", mock_auth_context
        )

        assert backend_key is not None
        assert backend_key in websocket_proxy.backend_connections
        assert websocket_proxy.backend_connections[backend_key] == mock_backend_ws

        # Verify connection parameters
        mock_session.ws_connect.assert_called_once()
        call_args = mock_session.ws_connect.call_args

        # Check URL
        assert (
            call_args[0][0]
            == f"ws://{mock_service_info.endpoint.host}:{mock_service_info.endpoint.port}/ws"
        )

        # Check headers
        headers = call_args[1]["headers"]
        assert headers["X-User-ID"] == str(mock_auth_context.user_id)
        assert headers["X-Username"] == mock_auth_context.username
        assert headers["X-User-Role"] == mock_auth_context.permissions.role.value
        assert headers["X-Therapeutic-Context"] == "True"
        assert headers["X-Crisis-Mode"] == "False"
        assert headers["X-Gateway-Connection-ID"] == "connection-123"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_connect_to_backend_error(
        self, mock_session_class, websocket_proxy, mock_service_info, mock_auth_context
    ):
        """Test backend connection error handling."""
        # Mock connection error
        mock_session = MagicMock()
        mock_session.ws_connect.side_effect = Exception("Connection failed")
        mock_session_class.return_value = mock_session

        backend_key = await websocket_proxy._connect_to_backend(
            mock_service_info, "connection-123", mock_auth_context
        )

        assert backend_key is None

    @pytest.mark.asyncio
    async def test_disconnect_from_backend(self, websocket_proxy):
        """Test backend disconnection."""
        # Setup mock backend connection
        mock_backend_ws = AsyncMock()
        mock_backend_ws.closed = False
        mock_backend_ws.close = AsyncMock()

        backend_key = "test-service:localhost:8080:connection-123"
        connection_id = "connection-123"

        websocket_proxy.backend_connections[backend_key] = mock_backend_ws
        websocket_proxy.connection_to_backend[connection_id] = backend_key
        websocket_proxy.backend_to_connections[backend_key] = [connection_id]

        await websocket_proxy._disconnect_from_backend(backend_key, connection_id)

        # Verify cleanup
        assert backend_key not in websocket_proxy.backend_connections
        assert connection_id not in websocket_proxy.connection_to_backend
        assert backend_key not in websocket_proxy.backend_to_connections

        mock_backend_ws.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_gateway_message_ping(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling ping message."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )
        connection = connection_manager.get_connection(connection_id)

        message = {"type": "ping"}
        handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True
        mock_websocket.send_text.assert_called_once()

        # Verify pong response
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "pong"
        assert "timestamp" in parsed_message
        assert parsed_message["connection_id"] == connection_id

    @pytest.mark.asyncio
    async def test_handle_gateway_message_join_session(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling join session message."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )
        connection = connection_manager.get_connection(connection_id)

        session_id = "session-123"
        message = {"type": "join_session", "session_id": session_id}
        handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True
        assert connection.therapeutic_session_id == session_id

        # Verify session indexing
        session_connections = connection_manager.get_session_connections(session_id)
        assert len(session_connections) == 1
        assert session_connections[0].connection_id == connection_id

        # Verify response
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "session_joined"
        assert parsed_message["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_handle_gateway_message_leave_session(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling leave session message."""
        # Create connection with session
        session_id = "session-123"
        connection_id = await connection_manager.connect(
            mock_websocket,
            ConnectionType.THERAPEUTIC_SESSION,
            therapeutic_session_id=session_id,
        )
        connection = connection_manager.get_connection(connection_id)

        message = {"type": "leave_session"}
        handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True
        assert connection.therapeutic_session_id is None

        # Verify session cleanup
        session_connections = connection_manager.get_session_connections(session_id)
        assert len(session_connections) == 0

    @pytest.mark.asyncio
    async def test_handle_gateway_message_therapeutic_event(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling therapeutic event message."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.THERAPEUTIC_SESSION
        )
        connection = connection_manager.get_connection(connection_id)

        message = {
            "type": "therapeutic_event",
            "event_type": "mood_update",
            "data": {"mood": "happy", "intensity": 7},
        }

        with patch("src.api_gateway.websocket.proxy.logger") as mock_logger:
            handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True

        # Verify logging
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args
        assert "Therapeutic event: mood_update" in log_call[0][0]

        # Verify response
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "therapeutic_event_ack"
        assert parsed_message["event_type"] == "mood_update"

    @pytest.mark.asyncio
    async def test_handle_gateway_message_crisis_alert(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling crisis alert message."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )
        connection = connection_manager.get_connection(connection_id)

        message = {
            "type": "crisis_alert",
            "data": {"severity": "high", "description": "feeling overwhelmed"},
        }

        with patch("src.api_gateway.websocket.proxy.logger") as mock_logger:
            handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True
        assert connection.crisis_mode is True

        # Verify critical logging
        mock_logger.critical.assert_called_once()
        log_call = mock_logger.critical.call_args
        assert "Crisis alert received" in log_call[0][0]

        # Verify response
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "crisis_alert_ack"
        assert parsed_message["support_available"] is True

    @pytest.mark.asyncio
    async def test_handle_gateway_message_unknown_type(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling unknown message type."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )
        connection = connection_manager.get_connection(connection_id)

        message = {"type": "unknown_type", "data": "test"}
        handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is False

    @pytest.mark.asyncio
    async def test_handle_gateway_message_error(
        self, websocket_proxy, connection_manager, mock_websocket
    ):
        """Test handling message with error."""
        # Create connection
        connection_id = await connection_manager.connect(
            mock_websocket, ConnectionType.CHAT
        )
        connection = connection_manager.get_connection(connection_id)

        # Mock handler to raise exception
        async def failing_handler(conn, msg):
            raise Exception("Handler error")

        websocket_proxy.message_handlers["test_type"] = failing_handler

        message = {"type": "test_type"}
        handled = await websocket_proxy._handle_gateway_message(connection, message)

        assert handled is True

        # Verify error response sent
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "error"
        assert parsed_message["original_type"] == "test_type"
        assert "Handler error" in parsed_message["error"]

    def test_get_proxy_stats(self, websocket_proxy):
        """Test getting proxy statistics."""
        # Add some mock data
        websocket_proxy.backend_connections["service1:host1:8080:conn1"] = MagicMock()
        websocket_proxy.backend_connections["service2:host2:8081:conn2"] = MagicMock()
        websocket_proxy.connection_to_backend["conn1"] = "service1:host1:8080:conn1"
        websocket_proxy.connection_to_backend["conn2"] = "service2:host2:8081:conn2"

        stats = websocket_proxy.get_proxy_stats()

        assert stats["backend_connections"] == 2
        assert stats["active_proxies"] == 2
        assert stats["backend_services"] == 2  # service1 and service2


class TestWebSocketProxyIntegration:
    """Integration tests for WebSocket proxy functionality."""

    @pytest.mark.asyncio
    async def test_full_proxy_flow_mock(
        self,
        websocket_proxy,
        connection_manager,
        mock_websocket,
        mock_service_info,
        mock_auth_context,
    ):
        """Test full proxy flow with mocked backend."""
        # Mock service selection
        websocket_proxy.service_router.select_service.return_value = mock_service_info

        # Mock backend connection
        mock_backend_ws = AsyncMock()
        mock_backend_ws.closed = False

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.ws_connect.return_value = mock_backend_ws
            mock_session_class.return_value = mock_session

            # Mock WebSocket disconnect to end the connection quickly
            mock_websocket.receive_text.side_effect = Exception(
                "WebSocket disconnected"
            )

            # This would normally run the full proxy flow
            # For testing, we'll just verify the setup
            backend_key = await websocket_proxy._connect_to_backend(
                mock_service_info, "test-connection", mock_auth_context
            )

            assert backend_key is not None
            assert backend_key in websocket_proxy.backend_connections
