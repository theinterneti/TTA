"""
Tests for Clinical Dashboard WebSocket Router

This module tests the real-time WebSocket functionality for clinical dashboard
including practitioner authentication, alert broadcasting, metrics streaming,
and real-time communication features.
"""

import asyncio
import json
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.clinical_dashboard_manager import (
    AccessLevel,
    AlertSeverity,
    ClinicalAlert,
    ClinicalDashboardManager,
    ClinicalRole,
    TherapeuticMetrics,
)
from src.components.clinical_dashboard.websocket_router import (
    ClinicalDashboardWebSocketRouter,
)


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.messages_sent = []
        self.messages_received = []
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.client_state = MagicMock()
        self.client_state.name = "CONNECTED"

    async def accept(self):
        """Mock accept method."""
        pass

    async def send_text(self, message: str):
        """Mock send_text method."""
        if self.closed:
            raise Exception("WebSocket is closed")
        self.messages_sent.append(message)

    async def receive_text(self) -> str:
        """Mock receive_text method."""
        if self.closed:
            from fastapi import WebSocketDisconnect

            raise WebSocketDisconnect()

        # Wait for messages with timeout
        for _ in range(50):  # Wait up to 5 seconds
            if self.messages_received:
                return self.messages_received.pop(0)
            await asyncio.sleep(0.1)

        # If no messages after timeout, simulate disconnect
        from fastapi import WebSocketDisconnect

        raise WebSocketDisconnect()

    async def close(self, code: int = 1000, reason: str = ""):
        """Mock close method."""
        self.closed = True
        self.close_code = code
        self.close_reason = reason
        self.client_state.name = "DISCONNECTED"

    def add_message(self, message: str):
        """Add a message to be received."""
        self.messages_received.append(message)


class TestClinicalDashboardWebSocketRouter:
    """Test Clinical Dashboard WebSocket Router functionality."""

    @pytest_asyncio.fixture
    async def dashboard_manager(self):
        """Create dashboard manager instance."""
        manager = ClinicalDashboardManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest_asyncio.fixture
    async def websocket_router(self, dashboard_manager):
        """Create WebSocket router instance."""
        router = ClinicalDashboardWebSocketRouter(dashboard_manager)
        yield router
        await router.shutdown()

    @pytest_asyncio.fixture
    async def authenticated_practitioner(self, dashboard_manager):
        """Create and authenticate a test practitioner."""
        # Register practitioner
        practitioner_id = await dashboard_manager.register_practitioner(
            username="test_practitioner",
            full_name="Test Practitioner",
            role=ClinicalRole.THERAPIST,
            access_level=AccessLevel.STANDARD,
            email="test@clinic.com",
        )

        # Authenticate practitioner
        session_token, _ = await dashboard_manager.authenticate_practitioner(
            username="test_practitioner", password_hash="test_hash"
        )

        return {
            "practitioner_id": practitioner_id,
            "session_token": session_token,
        }

    @pytest.mark.asyncio
    async def test_websocket_connection_authentication(
        self, websocket_router, authenticated_practitioner
    ):
        """Test WebSocket connection with valid authentication."""
        mock_websocket = MockWebSocket()
        session_token = authenticated_practitioner["session_token"]

        # Start connection handling in background
        connection_task = asyncio.create_task(
            websocket_router._handle_clinical_connection(mock_websocket, session_token)
        )

        # Wait a bit for connection to be established
        await asyncio.sleep(0.1)

        # Verify connection was accepted
        assert not mock_websocket.closed
        assert len(websocket_router.active_connections) == 1

        # Verify initial state message was sent
        assert len(mock_websocket.messages_sent) > 0
        initial_message = json.loads(mock_websocket.messages_sent[0])
        assert initial_message["type"] == "initial_state"
        assert "dashboard_overview" in initial_message["data"]
        assert "practitioner_info" in initial_message["data"]

        # Close connection
        await mock_websocket.close()

        # Wait for connection task to complete
        try:
            await asyncio.wait_for(connection_task, timeout=1.0)
        except asyncio.TimeoutError:
            connection_task.cancel()

    @pytest.mark.asyncio
    async def test_websocket_connection_invalid_token(self, websocket_router):
        """Test WebSocket connection with invalid authentication token."""
        mock_websocket = MockWebSocket()
        invalid_token = "invalid_token_123"

        # Start connection handling
        await websocket_router._handle_clinical_connection(
            mock_websocket, invalid_token
        )

        # Verify connection was rejected
        assert mock_websocket.closed
        assert mock_websocket.close_code == 1008
        assert mock_websocket.close_reason == "Invalid session token"

    @pytest.mark.asyncio
    async def test_alert_broadcasting(
        self, websocket_router, dashboard_manager, authenticated_practitioner
    ):
        """Test real-time alert broadcasting to connected practitioners."""
        mock_websocket = MockWebSocket()
        session_token = authenticated_practitioner["session_token"]

        # Establish connection
        connection_task = asyncio.create_task(
            websocket_router._handle_clinical_connection(mock_websocket, session_token)
        )
        await asyncio.sleep(0.1)

        # Clear initial messages
        mock_websocket.messages_sent.clear()

        # Create and add a clinical alert
        alert = ClinicalAlert(
            user_id="patient_123",
            session_id="session_456",
            alert_type="crisis_detected",
            severity=AlertSeverity.CRITICAL,
            message="Patient expressing distress",
            priority_score=8.5,
            intervention_required=True,
        )

        await dashboard_manager.add_clinical_alert(alert)

        # Broadcast alert
        await websocket_router.broadcast_alert(alert.alert_id)

        # Verify alert was broadcasted
        assert len(mock_websocket.messages_sent) > 0
        alert_message = json.loads(mock_websocket.messages_sent[-1])
        assert alert_message["type"] == "new_alert"
        assert alert_message["data"]["alert_id"] == alert.alert_id
        assert alert_message["data"]["severity"] == "critical"
        assert alert_message["data"]["priority_score"] == 8.5

        # Close connection
        await mock_websocket.close()
        try:
            await asyncio.wait_for(connection_task, timeout=1.0)
        except asyncio.TimeoutError:
            connection_task.cancel()

    @pytest.mark.asyncio
    async def test_metrics_streaming(
        self, websocket_router, dashboard_manager, authenticated_practitioner
    ):
        """Test real-time metrics streaming to subscribed practitioners."""
        mock_websocket = MockWebSocket()
        session_token = authenticated_practitioner["session_token"]

        # Establish connection
        connection_task = asyncio.create_task(
            websocket_router._handle_clinical_connection(mock_websocket, session_token)
        )
        await asyncio.sleep(0.1)

        # Subscribe to a session
        subscription_message = {
            "type": "subscribe_session",
            "session_id": "test_session_123",
        }
        mock_websocket.add_message(json.dumps(subscription_message))
        await asyncio.sleep(0.1)

        # Clear messages
        mock_websocket.messages_sent.clear()

        # Create therapeutic metrics
        metrics = TherapeuticMetrics(
            user_id="patient_123",
            session_id="test_session_123",
            therapeutic_value_accumulated=0.75,
            engagement_level=0.85,
            safety_score=0.95,
            session_duration_minutes=30.0,
            therapeutic_alliance_strength=0.8,
        )

        # Broadcast metrics update
        await websocket_router.broadcast_metrics_update("test_session_123", metrics)

        # Verify metrics were streamed
        assert len(mock_websocket.messages_sent) > 0
        metrics_message = json.loads(mock_websocket.messages_sent[-1])
        assert metrics_message["type"] == "metrics_update"
        assert metrics_message["data"]["session_id"] == "test_session_123"
        assert metrics_message["data"]["therapeutic_value_accumulated"] == 0.75
        assert metrics_message["data"]["engagement_level"] == 0.85

        # Close connection
        await mock_websocket.close()
        try:
            await asyncio.wait_for(connection_task, timeout=1.0)
        except asyncio.TimeoutError:
            connection_task.cancel()

    @pytest.mark.asyncio
    async def test_alert_acknowledgment(
        self, websocket_router, dashboard_manager, authenticated_practitioner
    ):
        """Test alert acknowledgment through WebSocket."""
        mock_websocket = MockWebSocket()
        session_token = authenticated_practitioner["session_token"]

        # Establish connection
        connection_task = asyncio.create_task(
            websocket_router._handle_clinical_connection(mock_websocket, session_token)
        )
        await asyncio.sleep(0.1)

        # Create and add alert
        alert = ClinicalAlert(
            user_id="patient_123",
            session_id="session_456",
            alert_type="medication_reminder",
            severity=AlertSeverity.MEDIUM,
            message="Patient missed medication dose",
        )
        await dashboard_manager.add_clinical_alert(alert)

        # Send acknowledgment message
        ack_message = {"type": "acknowledge_alert", "alert_id": alert.alert_id}
        mock_websocket.add_message(json.dumps(ack_message))
        await asyncio.sleep(0.2)

        # Verify alert was acknowledged
        stored_alert = dashboard_manager.active_alerts[alert.alert_id]
        assert stored_alert.acknowledged is True
        assert (
            stored_alert.acknowledged_by
            == authenticated_practitioner["practitioner_id"]
        )

        # Verify acknowledgment response was sent
        response_found = False
        for message_text in mock_websocket.messages_sent:
            message = json.loads(message_text)
            if message.get("type") == "alert_acknowledged":
                assert message["alert_id"] == alert.alert_id
                response_found = True
                break
        assert response_found

        # Close connection
        await mock_websocket.close()
        try:
            await asyncio.wait_for(connection_task, timeout=1.0)
        except asyncio.TimeoutError:
            connection_task.cancel()

    @pytest.mark.asyncio
    async def test_websocket_performance_benchmarks(
        self, websocket_router, authenticated_practitioner
    ):
        """Test WebSocket performance meets production benchmarks."""
        import time

        mock_websocket = MockWebSocket()
        session_token = authenticated_practitioner["session_token"]

        # Test connection establishment performance
        start_time = time.perf_counter()
        connection_task = asyncio.create_task(
            websocket_router._handle_clinical_connection(mock_websocket, session_token)
        )
        await asyncio.sleep(0.1)  # Wait for connection to be established
        connection_time = (time.perf_counter() - start_time) * 1000

        assert (
            connection_time < 150.0
        )  # Connection should be under 150ms (adjusted for CI environment)

        # Test message broadcasting performance
        alert = ClinicalAlert(
            user_id="patient_perf",
            session_id="session_perf",
            alert_type="performance_test",
            severity=AlertSeverity.LOW,
            message="Performance test alert",
        )

        start_time = time.perf_counter()
        await websocket_router.broadcast_alert(alert.alert_id)
        broadcast_time = (time.perf_counter() - start_time) * 1000

        assert broadcast_time < 50.0  # Broadcasting should be under 50ms

        # Verify metrics
        metrics = websocket_router.get_metrics()
        assert metrics["active_connections"] >= 1
        assert metrics["messages_sent"] > 0

        # Close connection
        await mock_websocket.close()
        try:
            await asyncio.wait_for(connection_task, timeout=1.0)
        except asyncio.TimeoutError:
            connection_task.cancel()

    @pytest.mark.asyncio
    async def test_multiple_practitioner_connections(
        self, websocket_router, dashboard_manager
    ):
        """Test multiple practitioners connected simultaneously."""
        # Register multiple practitioners
        practitioners = []
        for i in range(3):
            practitioner_id = await dashboard_manager.register_practitioner(
                username=f"practitioner_{i}",
                full_name=f"Practitioner {i}",
                role=ClinicalRole.THERAPIST,
                access_level=AccessLevel.STANDARD,
                email=f"practitioner{i}@clinic.com",
            )

            session_token, _ = await dashboard_manager.authenticate_practitioner(
                username=f"practitioner_{i}", password_hash=f"hash_{i}"
            )

            practitioners.append(
                {
                    "id": practitioner_id,
                    "token": session_token,
                    "websocket": MockWebSocket(),
                }
            )

        # Establish connections
        connection_tasks = []
        for practitioner in practitioners:
            task = asyncio.create_task(
                websocket_router._handle_clinical_connection(
                    practitioner["websocket"], practitioner["token"]
                )
            )
            connection_tasks.append(task)

        await asyncio.sleep(0.2)

        # Verify all connections are active
        assert len(websocket_router.active_connections) == 3
        assert len(websocket_router.practitioner_connections) == 3

        # Broadcast alert to all
        alert = ClinicalAlert(
            user_id="patient_multi",
            session_id="session_multi",
            alert_type="multi_test",
            severity=AlertSeverity.HIGH,
            message="Multi-practitioner test alert",
        )

        await websocket_router.broadcast_alert(alert.alert_id)

        # Verify all practitioners received the alert
        for practitioner in practitioners:
            messages_received = len(practitioner["websocket"].messages_sent)
            assert messages_received > 0

        # Close all connections
        for practitioner in practitioners:
            await practitioner["websocket"].close()

        for task in connection_tasks:
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
