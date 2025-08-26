"""
Tests for WebSocket integration in agent orchestration.

This module tests the WebSocket endpoints, connection management,
and real-time event broadcasting functionality.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, AsyncMock

from src.agent_orchestration.realtime.models import (
    WebSocketEvent,
    AgentStatusEvent,
    EventType,
    AgentStatus,
)
from src.agent_orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
    WebSocketConnection,
)


@pytest.mark.asyncio
async def test_websocket_event_creation():
    """Test creating WebSocket events."""
    # Test basic WebSocket event
    event = WebSocketEvent(
        event_type=EventType.CONNECTION_STATUS,
        source="test",
        data={"status": "connected"}
    )
    
    assert event.event_type == EventType.CONNECTION_STATUS
    assert event.source == "test"
    assert event.data["status"] == "connected"
    assert event.event_id is not None
    assert event.timestamp > 0


@pytest.mark.asyncio
async def test_agent_status_event_creation():
    """Test creating agent status events."""
    event = AgentStatusEvent(
        agent_id="test-agent",
        agent_type="ipa",
        status=AgentStatus.ONLINE,
        source="test"
    )
    
    assert event.event_type == EventType.AGENT_STATUS
    assert event.agent_id == "test-agent"
    assert event.agent_type == "ipa"
    assert event.status == AgentStatus.ONLINE


@pytest.mark.asyncio
async def test_websocket_connection_creation():
    """Test creating WebSocket connections."""
    mock_websocket = Mock()
    mock_websocket.client = Mock()
    mock_websocket.client.host = "127.0.0.1"
    mock_websocket.client.port = 12345
    mock_websocket.headers = {"user-agent": "test"}
    
    connection = WebSocketConnection(
        websocket=mock_websocket,
        connection_id="test-conn-123",
        user_id="test-user",
        client_info={"test": "info"}
    )
    
    assert connection.connection_id == "test-conn-123"
    assert connection.user_id == "test-user"
    assert connection.client_info["test"] == "info"
    assert not connection.is_authenticated
    assert len(connection.subscriptions) == 0


@pytest.mark.asyncio
async def test_websocket_connection_manager_creation():
    """Test creating WebSocket connection manager."""
    config = {
        "agent_orchestration.realtime.websocket.heartbeat_interval": 30.0,
        "agent_orchestration.realtime.websocket.connection_timeout": 60.0,
        "agent_orchestration.realtime.websocket.max_connections": 100,
        "agent_orchestration.realtime.websocket.auth_required": True,
    }
    
    manager = WebSocketConnectionManager(
        config=config,
        agent_registry=None,
        redis_client=None
    )
    
    assert manager.heartbeat_interval == 30.0
    assert manager.connection_timeout == 60.0
    assert manager.max_connections == 100
    assert manager.auth_required is True
    assert len(manager.connections) == 0


@pytest.mark.asyncio
async def test_websocket_connection_health_status():
    """Test WebSocket connection health status."""
    mock_websocket = Mock()
    connection = WebSocketConnection(
        websocket=mock_websocket,
        connection_id="test-conn",
        user_id="test-user"
    )
    
    # Test healthy status
    assert connection._get_health_status() == "healthy"
    
    # Test with missed pongs
    connection.missed_pongs = 2
    assert connection._get_health_status() == "degraded"
    
    connection.missed_pongs = 4
    assert connection._get_health_status() == "unhealthy"


@pytest.mark.asyncio
async def test_event_authorization():
    """Test event type authorization."""
    config = {"agent_orchestration.realtime.websocket.auth_required": True}
    manager = WebSocketConnectionManager(config=config)
    
    mock_websocket = Mock()
    connection = WebSocketConnection(
        websocket=mock_websocket,
        connection_id="test-conn",
        user_id="test-user"
    )
    
    # Test unauthenticated connection
    connection.is_authenticated = False
    assert not manager._is_authorized_for_event_type(connection, EventType.AGENT_STATUS)
    
    # Test authenticated connection
    connection.is_authenticated = True
    assert manager._is_authorized_for_event_type(connection, EventType.AGENT_STATUS)
    assert manager._is_authorized_for_event_type(connection, EventType.CONNECTION_STATUS)
    assert manager._is_authorized_for_event_type(connection, EventType.HEARTBEAT)


@pytest.mark.asyncio
async def test_websocket_manager_status():
    """Test WebSocket manager status reporting."""
    config = {
        "agent_orchestration.realtime.websocket.heartbeat_interval": 30.0,
        "agent_orchestration.realtime.recovery.enabled": True,
        "agent_orchestration.realtime.recovery.timeout": 300.0,
    }
    
    manager = WebSocketConnectionManager(config=config)
    status = manager.get_status()
    
    assert "total_connections" in status
    assert "authenticated_connections" in status
    assert "unique_users" in status
    assert "configuration" in status
    assert "recovery" in status
    
    assert status["total_connections"] == 0
    assert status["recovery"]["enabled"] is True
    assert status["recovery"]["timeout"] == 300.0


@pytest.mark.asyncio
async def test_connection_recovery_tracking():
    """Test connection recovery tracking."""
    config = {"agent_orchestration.realtime.recovery.enabled": True}
    manager = WebSocketConnectionManager(config=config)
    
    mock_websocket = Mock()
    connection = WebSocketConnection(
        websocket=mock_websocket,
        connection_id="test-conn",
        user_id="test-user"
    )
    connection.is_authenticated = True
    connection.subscriptions.add(EventType.AGENT_STATUS)
    
    # Store connection info
    manager._store_connection_info(connection)
    assert "test-user" in manager.connection_history
    
    # Mark as disconnected
    manager._mark_connection_disconnected(connection)
    assert manager.connection_history["test-user"]["disconnected_at"] is not None
    
    # Check if can recover
    assert manager._can_recover_connection("test-user")


def test_websocket_event_serialization():
    """Test WebSocket event JSON serialization."""
    event = AgentStatusEvent(
        agent_id="test-agent",
        agent_type="ipa",
        status=AgentStatus.ONLINE,
        source="test"
    )
    
    # Test model_dump_json
    json_str = event.model_dump_json()
    assert isinstance(json_str, str)
    
    # Test parsing back
    data = json.loads(json_str)
    assert data["event_type"] == "agent_status"
    assert data["agent_id"] == "test-agent"
    assert data["status"] == "online"


@pytest.mark.asyncio
async def test_websocket_manager_shutdown():
    """Test WebSocket manager shutdown."""
    config = {}
    manager = WebSocketConnectionManager(config=config)
    
    # Add a mock connection
    mock_websocket = AsyncMock()
    connection = WebSocketConnection(
        websocket=mock_websocket,
        connection_id="test-conn",
        user_id="test-user"
    )
    manager.connections["test-conn"] = connection
    
    # Test shutdown
    await manager.shutdown()
    
    # Verify connection was closed
    mock_websocket.close.assert_called_once()
    assert len(manager.connections) == 0
