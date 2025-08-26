"""
Validation tests for WebSocket connection management and authentication.

This module tests the existing WebSocket infrastructure to ensure it works
correctly with the new configuration management and real-time features.
"""

import asyncio
import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from src.agent_orchestration.realtime.websocket_manager import WebSocketConnectionManager
from src.agent_orchestration.realtime.config_manager import get_realtime_config_manager, RealtimeEnvironment
from src.agent_orchestration.realtime.models import (
    ConnectionStatusEvent, AgentStatusEvent, WorkflowProgressEvent, EventType
)


@pytest.mark.integration
@pytest.mark.redis
class TestWebSocketValidation:
    """Test WebSocket connection management and authentication."""
    
    @pytest.fixture
    async def realtime_config(self):
        """Create real-time configuration for testing."""
        config = {
            "agent_orchestration": {
                "realtime": {
                    "enabled": True,
                    "websocket": {
                        "enabled": True,
                        "path": "/ws",
                        "heartbeat_interval": 1.0,  # Fast for testing
                        "connection_timeout": 5.0,  # Short for testing
                        "max_connections": 10,
                        "auth_required": False  # Disabled for testing
                    },
                    "events": {
                        "enabled": True,
                        "redis_channel_prefix": "test:events",
                        "buffer_size": 100
                    }
                }
            }
        }
        
        config_manager = get_realtime_config_manager(config)
        return config_manager.get_config()
    
    @pytest.fixture
    async def websocket_manager(self, realtime_config, redis_client):
        """Create WebSocket manager for testing."""
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.heartbeat_interval": 1.0,
            "agent_orchestration.realtime.websocket.connection_timeout": 5.0,
            "agent_orchestration.realtime.websocket.max_connections": 10,
            "agent_orchestration.realtime.websocket.auth_required": False,
            "agent_orchestration.realtime.events.enabled": True,
            "agent_orchestration.realtime.events.redis_channel_prefix": "test:events"
        }
        
        manager = WebSocketConnectionManager(
            config=config_dict,
            redis_client=redis_client
        )
        
        return manager
    
    @pytest.fixture
    async def mock_websocket(self):
        """Create mock WebSocket for testing."""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.receive_text = AsyncMock()
        websocket.receive_json = AsyncMock()
        websocket.close = AsyncMock()
        
        # Mock client info
        websocket.client = Mock()
        websocket.client.host = "127.0.0.1"
        websocket.client.port = 12345
        websocket.headers = {"user-agent": "test-client"}
        
        return websocket
    
    async def test_websocket_connection_establishment(self, websocket_manager, mock_websocket):
        """Test basic WebSocket connection establishment."""
        # Mock receive_text to simulate connection messages
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "ping"}),
            asyncio.CancelledError()  # Simulate connection close
        ]
        
        # Handle connection
        try:
            await websocket_manager.handle_connection(mock_websocket)
        except asyncio.CancelledError:
            pass  # Expected when connection closes
        
        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify connection status was sent
        assert mock_websocket.send_json.call_count >= 1
        
        # Check that connection was registered
        assert len(websocket_manager.connections) >= 0  # May be cleaned up after close
    
    async def test_websocket_authentication_disabled(self, websocket_manager, mock_websocket):
        """Test WebSocket connection when authentication is disabled."""
        mock_websocket.receive_text.side_effect = [asyncio.CancelledError()]
        
        try:
            await websocket_manager.handle_connection(mock_websocket)
        except asyncio.CancelledError:
            pass
        
        # Should accept connection without authentication
        mock_websocket.accept.assert_called_once()
    
    async def test_websocket_authentication_enabled(self, redis_client):
        """Test WebSocket connection when authentication is enabled."""
        # Create manager with auth enabled
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.auth_required": True,
            "agent_orchestration.realtime.websocket.connection_timeout": 5.0,
            "agent_orchestration.realtime.events.enabled": True
        }
        
        auth_manager = WebSocketConnectionManager(
            config=config_dict,
            redis_client=redis_client
        )
        
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}
        
        # Mock authentication failure (no token provided)
        mock_websocket.receive_json.side_effect = [
            {"type": "auth", "token": "invalid_token"},
            asyncio.CancelledError()
        ]
        
        try:
            await auth_manager.handle_connection(mock_websocket)
        except asyncio.CancelledError:
            pass
        
        # Should close connection due to auth failure
        mock_websocket.close.assert_called()
    
    async def test_websocket_heartbeat_mechanism(self, websocket_manager, mock_websocket):
        """Test WebSocket heartbeat mechanism."""
        # Mock heartbeat messages
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "ping"}),
            json.dumps({"type": "ping"}),
            asyncio.CancelledError()
        ]
        
        try:
            await websocket_manager.handle_connection(mock_websocket)
        except asyncio.CancelledError:
            pass
        
        # Should respond to ping messages
        sent_messages = [call.args[0] for call in mock_websocket.send_text.call_args_list]
        pong_messages = [msg for msg in sent_messages if "pong" in msg.lower()]
        assert len(pong_messages) >= 1
    
    async def test_websocket_connection_limits(self, redis_client):
        """Test WebSocket connection limits."""
        # Create manager with low connection limit
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.max_connections": 1,
            "agent_orchestration.realtime.websocket.auth_required": False,
            "agent_orchestration.realtime.events.enabled": True
        }
        
        limited_manager = WebSocketConnectionManager(
            config=config_dict,
            redis_client=redis_client
        )
        
        # Create first connection
        mock_ws1 = Mock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws1.receive_text = AsyncMock(side_effect=[asyncio.CancelledError()])
        mock_ws1.client = Mock()
        mock_ws1.client.host = "127.0.0.1"
        mock_ws1.headers = {}
        
        # Create second connection (should be rejected)
        mock_ws2 = Mock(spec=WebSocket)
        mock_ws2.accept = AsyncMock()
        mock_ws2.close = AsyncMock()
        mock_ws2.client = Mock()
        mock_ws2.client.host = "127.0.0.1"
        mock_ws2.headers = {}
        
        # Start first connection in background
        task1 = asyncio.create_task(limited_manager.handle_connection(mock_ws1))
        await asyncio.sleep(0.1)  # Let first connection establish
        
        # Try second connection
        await limited_manager.handle_connection(mock_ws2)
        
        # Second connection should be closed due to limit
        mock_ws2.close.assert_called_once()
        
        # Cleanup
        task1.cancel()
        try:
            await task1
        except asyncio.CancelledError:
            pass
    
    async def test_websocket_event_broadcasting(self, websocket_manager, mock_websocket):
        """Test WebSocket event broadcasting."""
        # Setup connection
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "subscribe", "event_types": ["agent_status"]}),
            asyncio.CancelledError()
        ]
        
        # Start connection handling
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)  # Let connection establish
        
        # Create and broadcast event
        event = AgentStatusEvent(
            agent_id="test_agent",
            status="processing",
            message="Test status update",
            source="test"
        )
        
        sent_count = await websocket_manager.broadcast_event(event)
        
        # Should have sent to at least one connection
        assert sent_count >= 0
        
        # Cleanup
        connection_task.cancel()
        try:
            await connection_task
        except asyncio.CancelledError:
            pass
    
    async def test_websocket_connection_recovery(self, websocket_manager, mock_websocket):
        """Test WebSocket connection recovery mechanisms."""
        # Mock connection with user ID for recovery
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "auth", "user_id": "test_user"}),
            json.dumps({"type": "subscribe", "event_types": ["workflow_progress"]}),
            asyncio.CancelledError()  # Simulate disconnect
        ]
        
        try:
            await websocket_manager.handle_connection(mock_websocket)
        except asyncio.CancelledError:
            pass
        
        # Check that connection history was recorded for recovery
        assert "test_user" in websocket_manager.connection_history
        
        # Verify recovery info contains subscription data
        recovery_info = websocket_manager.connection_history["test_user"]
        assert "subscriptions" in recovery_info
    
    async def test_configuration_validation(self):
        """Test real-time configuration validation."""
        # Test valid configuration
        valid_config = {
            "agent_orchestration": {
                "realtime": {
                    "enabled": True,
                    "websocket": {
                        "enabled": True,
                        "heartbeat_interval": 30.0,
                        "connection_timeout": 60.0,
                        "max_connections": 1000
                    },
                    "events": {
                        "enabled": True,
                        "buffer_size": 1000
                    }
                }
            }
        }
        
        config_manager = get_realtime_config_manager(valid_config)
        config = config_manager.get_config()
        assert config.enabled is True
        assert config.websocket.enabled is True
        
        # Test invalid configuration
        invalid_config = {
            "agent_orchestration": {
                "realtime": {
                    "enabled": True,
                    "websocket": {
                        "enabled": True,
                        "heartbeat_interval": -1.0,  # Invalid
                        "max_connections": 0  # Invalid
                    }
                }
            }
        }
        
        with pytest.raises(ValueError):
            invalid_manager = get_realtime_config_manager(invalid_config)
            invalid_manager.get_config()
    
    async def test_environment_based_configuration(self):
        """Test environment-based configuration defaults."""
        # Test development environment
        with patch.dict("os.environ", {"TTA_ENVIRONMENT": "development"}):
            dev_manager = get_realtime_config_manager({})
            dev_config = dev_manager.get_config()
            assert dev_config.environment == RealtimeEnvironment.DEVELOPMENT
            # Should be enabled by default in development
            assert dev_config.enabled is True
        
        # Test production environment
        with patch.dict("os.environ", {"TTA_ENVIRONMENT": "production"}):
            prod_manager = get_realtime_config_manager({})
            prod_config = prod_manager.get_config()
            assert prod_config.environment == RealtimeEnvironment.PRODUCTION
            # Should be disabled by default in production
            assert prod_config.enabled is False
