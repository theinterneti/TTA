"""
WebSocket connection recovery and error handling tests.

This module tests WebSocket connection recovery, error handling scenarios,
and resilience under various failure conditions.
"""

import asyncio
import contextlib
import json
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from tta_ai.orchestration.realtime.error_reporting import (
    ErrorReportingManager,
    ErrorSeverity,
)
from tta_ai.orchestration.realtime.event_publisher import EventPublisher
from tta_ai.orchestration.realtime.models import AgentStatus, AgentStatusEvent
from tta_ai.orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
)


@pytest.mark.integration
@pytest.mark.redis
class TestWebSocketErrorRecovery:
    """Test WebSocket error handling and recovery scenarios."""

    @pytest_asyncio.fixture
    async def websocket_manager(self, redis_client):
        """Create WebSocket manager for testing."""
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.heartbeat_interval": 1.0,
            "agent_orchestration.realtime.websocket.connection_timeout": 3.0,
            "agent_orchestration.realtime.websocket.max_connections": 5,
            "agent_orchestration.realtime.websocket.auth_required": False,
            "agent_orchestration.realtime.events.enabled": True,
            "agent_orchestration.realtime.recovery.enabled": True,
            "agent_orchestration.realtime.recovery.timeout": 10.0,
        }

        manager = WebSocketConnectionManager(
            config=config_dict, redis_client=redis_client
        )

        return manager

    @pytest_asyncio.fixture
    async def event_publisher(self, redis_client):
        """Create event publisher for testing."""
        publisher = EventPublisher(
            redis_client=redis_client, channel_prefix="test:events", enabled=True
        )
        return publisher

    @pytest_asyncio.fixture
    async def error_manager(self, event_publisher):
        """Create error reporting manager for testing."""
        manager = ErrorReportingManager(
            event_publisher=event_publisher,
            max_recovery_attempts=3,
            escalation_timeout=5.0,
        )
        await manager.start()
        yield manager
        await manager.stop()

    async def test_websocket_connection_timeout_handling(self, websocket_manager):
        """Test WebSocket connection timeout handling."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}

        # Mock receive_text to simulate timeout
        mock_websocket.receive_text = AsyncMock(side_effect=TimeoutError())

        # Handle connection (should timeout and close)
        await websocket_manager.handle_connection(mock_websocket)

        # Should have closed the connection due to timeout
        mock_websocket.close.assert_called()

    async def test_websocket_connection_limit_enforcement(self, websocket_manager):
        """Test WebSocket connection limit enforcement."""
        connections = []
        tasks = []

        # Create connections up to the limit
        for i in range(6):  # Limit is 5, so 6th should be rejected
            mock_ws = Mock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            mock_ws.close = AsyncMock()
            mock_ws.receive_text = AsyncMock(side_effect=[asyncio.CancelledError()])
            mock_ws.client = Mock()
            mock_ws.client.host = "127.0.0.1"
            mock_ws.client.port = 12345 + i
            mock_ws.headers = {}

            connections.append(mock_ws)

            # Start connection handling
            task = asyncio.create_task(websocket_manager.handle_connection(mock_ws))
            tasks.append(task)

            if i < 5:  # First 5 connections
                await asyncio.sleep(0.05)  # Let connection establish

        await asyncio.sleep(0.2)  # Let all connections process

        # The 6th connection should be closed due to limit
        assert connections[5].close.called

        # Cleanup
        for task in tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def test_redis_connection_failure_handling(self, websocket_manager):
        """Test handling of Redis connection failures."""
        # Simulate Redis failure by setting client to None
        original_redis = websocket_manager.redis_client
        websocket_manager.redis_client = None

        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps({"type": "subscribe", "event_types": ["agent_status"]}),
                asyncio.CancelledError(),
            ]
        )
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}

        # Should handle connection gracefully even without Redis
        with contextlib.suppress(asyncio.CancelledError):
            await websocket_manager.handle_connection(mock_websocket)

        # Connection should still be accepted
        mock_websocket.accept.assert_called_once()

        # Restore Redis client
        websocket_manager.redis_client = original_redis

    async def test_malformed_message_handling(self, websocket_manager):
        """Test handling of malformed WebSocket messages."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                "invalid json",  # Malformed JSON
                json.dumps({"invalid": "message"}),  # Missing required fields
                json.dumps({"type": "unknown_type"}),  # Unknown message type
                asyncio.CancelledError(),
            ]
        )
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}

        # Should handle malformed messages gracefully
        with contextlib.suppress(asyncio.CancelledError):
            await websocket_manager.handle_connection(mock_websocket)

        # Connection should remain open despite malformed messages
        mock_websocket.accept.assert_called_once()
        # Should not close connection for malformed messages
        assert not mock_websocket.close.called

    async def test_event_publishing_failure_recovery(self, event_publisher):
        """Test recovery from event publishing failures."""
        # Simulate Redis failure
        original_redis = event_publisher.redis_client
        event_publisher.redis_client = None

        # Try to publish event (should fail gracefully)
        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.ERROR,
            message="Test error event",
            source="test",
        )

        success = await event_publisher.publish_event(event)
        assert success is False
        assert event_publisher.events_failed > 0

        # Restore Redis and verify recovery
        event_publisher.redis_client = original_redis
        success = await event_publisher.publish_event(event)
        assert success is True

    async def test_error_escalation_mechanism(self, error_manager):
        """Test error escalation for unresolved errors."""
        escalated_errors = []

        # Add escalation handler
        async def escalation_handler(error_report, escalated=False):
            if escalated:
                escalated_errors.append(error_report)

        error_manager.add_notification_handler(escalation_handler)

        # Report a critical error
        error_id = await error_manager.report_error(
            error_type="critical_system_failure",
            error_message="System is down",
            severity=ErrorSeverity.CRITICAL,
            agent_id="system",
        )

        # Wait for escalation timeout (5 seconds in fixture)
        await asyncio.sleep(6.0)

        # Verify error was escalated
        assert len(escalated_errors) > 0
        assert escalated_errors[0].error_id == error_id
        assert escalated_errors[0].escalation_level > 0

    async def test_automatic_error_recovery(self, error_manager):
        """Test automatic error recovery mechanisms."""
        recovery_attempts = []

        # Add recovery handler
        async def recovery_handler(error_report):
            recovery_attempts.append(error_report)
            # Simulate successful recovery
            return True

        error_manager.add_recovery_handler("connection_failure", recovery_handler)

        # Report recoverable error
        error_id = await error_manager.report_error(
            error_type="connection_failure",
            error_message="Connection lost",
            severity=ErrorSeverity.MEDIUM,
            agent_id="test_agent",
        )

        await asyncio.sleep(0.5)  # Wait for recovery attempt

        # Verify recovery was attempted
        assert len(recovery_attempts) > 0
        assert recovery_attempts[0].error_id == error_id

        # Verify error was resolved
        assert error_id not in error_manager.active_errors

    async def test_connection_recovery_with_state_restoration(self, websocket_manager):
        """Test connection recovery with state restoration."""
        user_id = "test_user_recovery"

        # First connection with subscriptions
        mock_websocket1 = Mock()
        mock_websocket1.accept = AsyncMock()
        mock_websocket1.send_json = AsyncMock()
        mock_websocket1.receive_text = AsyncMock(
            side_effect=[
                json.dumps({"type": "auth", "user_id": user_id}),
                json.dumps(
                    {
                        "type": "subscribe",
                        "event_types": ["agent_status", "workflow_progress"],
                    }
                ),
                asyncio.CancelledError(),  # Simulate disconnect
            ]
        )
        mock_websocket1.client = Mock()
        mock_websocket1.client.host = "127.0.0.1"
        mock_websocket1.headers = {}

        # Handle first connection
        task1 = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket1)
        )
        await asyncio.sleep(0.1)

        # Subscribe user
        await websocket_manager.subscribe_user_to_events(
            user_id=user_id,
            event_types=["agent_status", "workflow_progress"],
            filters={"agent_ids": ["test_agent"]},
        )

        # Simulate disconnect
        task1.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task1

        # Verify connection history was saved
        assert user_id in websocket_manager.connection_history

        # Second connection (recovery)
        mock_websocket2 = Mock()
        mock_websocket2.accept = AsyncMock()
        mock_websocket2.send_json = AsyncMock()
        mock_websocket2.receive_text = AsyncMock(
            side_effect=[
                json.dumps({"type": "auth", "user_id": user_id}),
                json.dumps({"type": "recover_connection"}),
                asyncio.CancelledError(),
            ]
        )
        mock_websocket2.client = Mock()
        mock_websocket2.client.host = "127.0.0.1"
        mock_websocket2.headers = {}

        # Handle recovery connection
        task2 = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket2)
        )
        await asyncio.sleep(0.1)

        # Verify subscriptions were restored
        user_subscriptions = await websocket_manager.get_user_subscriptions(user_id)
        assert "agent_status" in user_subscriptions["event_types"]
        assert "workflow_progress" in user_subscriptions["event_types"]
        assert user_subscriptions["filters"].get("agent_ids") == ["test_agent"]

        # Cleanup
        task2.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task2

    async def test_concurrent_error_handling(self, error_manager):
        """Test handling of multiple concurrent errors."""
        error_ids = []

        # Report multiple errors concurrently
        error_tasks = []
        for i in range(5):
            task = asyncio.create_task(
                error_manager.report_error(
                    error_type=f"concurrent_error_{i}",
                    error_message=f"Concurrent error {i}",
                    severity=ErrorSeverity.MEDIUM,
                    agent_id=f"agent_{i}",
                )
            )
            error_tasks.append(task)

        # Wait for all errors to be reported
        error_ids = await asyncio.gather(*error_tasks)

        # Verify all errors were reported
        assert len(error_ids) == 5
        assert len(error_manager.active_errors) == 5

        # Verify each error has unique ID
        assert len(set(error_ids)) == 5

    async def test_websocket_heartbeat_failure_detection(self, websocket_manager):
        """Test detection of failed WebSocket connections via heartbeat."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock(side_effect=Exception("Connection lost"))
        mock_websocket.close = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[json.dumps({"type": "ping"}), asyncio.CancelledError()]
        )
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}

        # Handle connection (should detect failure and close)
        with contextlib.suppress(asyncio.CancelledError):
            await websocket_manager.handle_connection(mock_websocket)

        # Should have attempted to send heartbeat response and detected failure
        mock_websocket.send_text.assert_called()
        mock_websocket.close.assert_called()
