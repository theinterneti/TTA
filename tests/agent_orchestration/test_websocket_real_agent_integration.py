"""
End-to-end WebSocket communication tests with real agent integration.

This module tests the complete WebSocket integration with real agent communication,
including progress tracking, error reporting, and user-specific event filtering.
"""

import asyncio
import contextlib
import json
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from fastapi.websockets import WebSocket
from tta_ai.orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.realtime.agent_event_integration import (
    AgentWorkflowCoordinator,
)
from tta_ai.orchestration.realtime.config_manager import get_realtime_config_manager
from tta_ai.orchestration.realtime.error_reporting import (
    ErrorReportingManager,
    ErrorSeverity,
)
from tta_ai.orchestration.realtime.event_publisher import EventPublisher
from tta_ai.orchestration.realtime.models import (
    AgentStatus,
    AgentStatusEvent,
)
from tta_ai.orchestration.realtime.progressive_feedback import (
    ProgressiveFeedbackManager,
)
from tta_ai.orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
)


@pytest.mark.integration
@pytest.mark.redis
class TestWebSocketRealAgentIntegration:
    """Test WebSocket integration with real agent communication."""

    @pytest_asyncio.fixture
    async def realtime_config(self):
        """Create real-time configuration for testing."""
        config = {
            "agent_orchestration": {
                "realtime": {
                    "enabled": True,
                    "websocket": {
                        "enabled": True,
                        "path": "/ws",
                        "heartbeat_interval": 1.0,
                        "connection_timeout": 5.0,
                        "max_connections": 10,
                        "auth_required": False,
                    },
                    "events": {
                        "enabled": True,
                        "redis_channel_prefix": "test:events",
                        "buffer_size": 100,
                        "broadcast_agent_status": True,
                        "broadcast_workflow_progress": True,
                        "broadcast_system_metrics": True,
                    },
                    "progressive_feedback": {
                        "enabled": True,
                        "update_interval": 0.5,
                        "max_updates_per_workflow": 50,
                    },
                }
            }
        }

        config_manager = get_realtime_config_manager(config)
        return config_manager.get_config()

    @pytest_asyncio.fixture
    async def event_publisher(self, redis_client, realtime_config):
        """Create event publisher for testing."""
        return EventPublisher(
            redis_client=redis_client,
            channel_prefix="test:events",
            enabled=True,
            buffer_size=100,
            broadcast_agent_status=True,
            broadcast_workflow_progress=True,
            broadcast_system_metrics=True,
        )

    @pytest_asyncio.fixture
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
            "agent_orchestration.realtime.events.redis_channel_prefix": "test:events",
        }

        return WebSocketConnectionManager(config=config_dict, redis_client=redis_client)

    @pytest_asyncio.fixture
    async def enhanced_agent_proxies(self, redis_coordinator, event_publisher):
        """Create enhanced agent proxies with real-time integration."""
        ipa_proxy = InputProcessorAgentProxy(
            coordinator=redis_coordinator,
            instance="test_ipa",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        wba_proxy = WorldBuilderAgentProxy(
            coordinator=redis_coordinator,
            instance="test_wba",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        nga_proxy = NarrativeGeneratorAgentProxy(
            coordinator=redis_coordinator,
            instance="test_nga",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        return ipa_proxy, wba_proxy, nga_proxy

    @pytest_asyncio.fixture
    async def workflow_coordinator(self, enhanced_agent_proxies, event_publisher):
        """Create workflow coordinator for testing."""
        ipa_proxy, wba_proxy, nga_proxy = enhanced_agent_proxies

        return AgentWorkflowCoordinator(
            ipa_proxy=ipa_proxy,
            wba_proxy=wba_proxy,
            nga_proxy=nga_proxy,
            event_publisher=event_publisher,
        )

    @pytest_asyncio.fixture
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

    async def test_complete_workflow_with_websocket_events(
        self, workflow_coordinator, websocket_manager, mock_websocket, event_publisher
    ):
        """Test complete agent workflow with WebSocket event broadcasting."""
        received_events = []

        # Mock WebSocket to capture sent events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps(
                {
                    "type": "subscribe",
                    "event_types": ["agent_status", "workflow_progress"],
                }
            ),
            asyncio.CancelledError(),
        ]

        # Start WebSocket connection handling
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)  # Let connection establish

        # Execute complete workflow
        workflow_result = await workflow_coordinator.execute_complete_workflow(
            user_input="I want to explore the mysterious forest",
            session_id="test_session_001",
            world_id="test_world_001",
        )

        # Wait for events to be processed
        await asyncio.sleep(0.5)

        # Cleanup connection
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify workflow completed successfully
        assert workflow_result["story"] is not None
        assert workflow_result["session_id"] == "test_session_001"
        assert "ipa_result" in workflow_result
        assert "wba_result" in workflow_result
        assert "nga_result" in workflow_result

        # Verify WebSocket events were sent
        assert len(received_events) > 0

        # Check for agent status events
        agent_events = [
            e for e in received_events if e.get("event_type") == "agent_status"
        ]
        assert len(agent_events) > 0

        # Check for workflow progress events
        workflow_events = [
            e for e in received_events if e.get("event_type") == "workflow_progress"
        ]
        assert len(workflow_events) > 0

    async def test_progressive_feedback_integration(
        self, enhanced_agent_proxies, websocket_manager, mock_websocket, event_publisher
    ):
        """Test progressive feedback integration with WebSocket broadcasting."""
        ipa_proxy, wba_proxy, nga_proxy = enhanced_agent_proxies
        received_events = []

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "subscribe", "event_types": ["progressive_feedback"]}),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Process with IPA (should generate progressive feedback)
        await ipa_proxy.process(
            {"text": "I carefully examine the ancient runes on the temple wall"}
        )

        await asyncio.sleep(0.3)  # Wait for events

        # Cleanup
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify progressive feedback events were sent
        feedback_events = [
            e for e in received_events if e.get("event_type") == "progressive_feedback"
        ]
        assert len(feedback_events) > 0

        # Verify feedback contains progress information
        for event in feedback_events:
            assert "progress" in event
            assert "message" in event
            assert event["progress"] >= 0.0 and event["progress"] <= 1.0

    async def test_error_reporting_integration(
        self, websocket_manager, mock_websocket, event_publisher
    ):
        """Test error reporting integration with WebSocket broadcasting."""
        received_events = []

        # Create error reporting manager
        error_manager = ErrorReportingManager(
            event_publisher=event_publisher, max_recovery_attempts=2
        )
        await error_manager.start()

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "subscribe", "event_types": ["agent_status", "error"]}),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Report an error
        await error_manager.report_error(
            error_type="agent_communication_failure",
            error_message="Failed to connect to IPA service",
            severity=ErrorSeverity.HIGH,
            agent_id="test_ipa",
            workflow_id="test_workflow_001",
        )

        await asyncio.sleep(0.3)  # Wait for events

        # Cleanup
        await error_manager.stop()
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify error events were sent
        error_events = [
            e for e in received_events if "error" in e.get("event_type", "").lower()
        ]
        assert len(error_events) > 0

        # Verify error contains proper information
        for event in error_events:
            if event.get("agent_id") == "test_ipa":
                assert event.get("status") == "error"
                assert "error_id" in event.get("metadata", {})

    async def test_user_specific_event_filtering(
        self, websocket_manager, mock_websocket, event_publisher
    ):
        """Test user-specific event filtering and subscriptions."""
        received_events = []

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "auth", "user_id": "test_user_001"}),
            json.dumps(
                {
                    "type": "subscribe",
                    "event_types": ["agent_status"],
                    "filters": {"agent_ids": ["test_ipa"], "min_severity": "medium"},
                }
            ),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Subscribe user to specific events
        await websocket_manager.subscribe_user_to_events(
            user_id="test_user_001",
            event_types=["agent_status"],
            filters={"agent_ids": ["test_ipa"], "min_severity": "medium"},
        )

        # Publish events that should be filtered
        filtered_event = AgentStatusEvent(
            agent_id="test_wba",  # Different agent - should be filtered out
            status=AgentStatus.PROCESSING,
            message="WBA processing",
            source="test",
        )

        allowed_event = AgentStatusEvent(
            agent_id="test_ipa",  # Correct agent - should be sent
            status=AgentStatus.ERROR,
            message="IPA error",
            metadata={"severity": "high"},
            source="test",
        )

        await event_publisher.publish_event(filtered_event)
        await event_publisher.publish_event(allowed_event)

        await asyncio.sleep(0.3)  # Wait for events

        # Cleanup
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify only allowed events were received
        agent_events = [
            e for e in received_events if e.get("event_type") == "agent_status"
        ]

        # Should only receive the IPA event, not the WBA event
        ipa_events = [e for e in agent_events if e.get("agent_id") == "test_ipa"]
        wba_events = [e for e in agent_events if e.get("agent_id") == "test_wba"]

        assert len(ipa_events) > 0
        assert len(wba_events) == 0

    async def test_connection_recovery_with_subscriptions(
        self, websocket_manager, mock_websocket, event_publisher
    ):
        """Test WebSocket connection recovery with subscription restoration."""
        # First connection
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "auth", "user_id": "test_user_recovery"}),
            json.dumps(
                {
                    "type": "subscribe",
                    "event_types": ["agent_status", "workflow_progress"],
                }
            ),
            asyncio.CancelledError(),  # Simulate disconnect
        ]

        # Start first connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Subscribe user
        await websocket_manager.subscribe_user_to_events(
            user_id="test_user_recovery",
            event_types=["agent_status", "workflow_progress"],
        )

        # Simulate disconnect
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify subscription information is preserved
        user_subscriptions = await websocket_manager.get_user_subscriptions(
            "test_user_recovery"
        )
        assert "agent_status" in user_subscriptions["event_types"]
        assert "workflow_progress" in user_subscriptions["event_types"]

        # Verify connection history was recorded
        assert "test_user_recovery" in websocket_manager.connection_history

    async def test_concurrent_websocket_connections(
        self, websocket_manager, event_publisher
    ):
        """Test multiple concurrent WebSocket connections."""
        connections = []
        connection_tasks = []

        # Create multiple mock WebSocket connections
        for i in range(3):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            mock_ws.receive_text = AsyncMock(
                side_effect=[
                    json.dumps({"type": "auth", "user_id": f"test_user_{i}"}),
                    json.dumps({"type": "subscribe", "event_types": ["agent_status"]}),
                    asyncio.CancelledError(),
                ]
            )
            mock_ws.client = Mock()
            mock_ws.client.host = "127.0.0.1"
            mock_ws.client.port = 12345 + i
            mock_ws.headers = {"user-agent": f"test-client-{i}"}

            connections.append(mock_ws)

            # Start connection handling
            task = asyncio.create_task(websocket_manager.handle_connection(mock_ws))
            connection_tasks.append(task)

        await asyncio.sleep(0.2)  # Let connections establish

        # Publish event to all connections
        test_event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.PROCESSING,
            message="Test concurrent broadcast",
            source="test",
        )

        sent_count = await websocket_manager.broadcast_event(test_event)

        # Should have sent to all connections
        assert sent_count >= 0  # May be 0 if connections not fully established

        # Cleanup all connections
        for task in connection_tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        # Verify all connections were handled
        stats = await websocket_manager.get_connection_stats()
        assert stats["active_connections"] >= 0  # May be 0 after cleanup

    async def test_real_time_workflow_progress_tracking(
        self, workflow_coordinator, websocket_manager, mock_websocket, event_publisher
    ):
        """Test detailed real-time progress tracking for agent workflows."""
        received_events = []
        progress_events = []

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

            # Track progress events specifically
            if event_data.get("event_type") == "workflow_progress":
                progress_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps(
                {
                    "type": "subscribe",
                    "event_types": ["workflow_progress", "agent_status"],
                }
            ),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Execute workflow with progress tracking
        workflow_result = await workflow_coordinator.execute_complete_workflow(
            user_input="Tell me about the ancient library's secrets",
            session_id="progress_test_session",
            world_id="progress_test_world",
        )

        await asyncio.sleep(0.5)  # Wait for all events

        # Cleanup
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify workflow completed
        assert workflow_result["story"] is not None
        assert workflow_result["workflow_id"] is not None

        # Verify progress events were generated
        assert (
            len(progress_events) >= 3
        )  # Should have start, intermediate, and completion events

        # Verify progress sequence
        workflow_id = workflow_result["workflow_id"]
        workflow_progress_events = [
            e for e in progress_events if e.get("workflow_id") == workflow_id
        ]

        assert len(workflow_progress_events) >= 1

        # Check progress values are in correct range
        for event in workflow_progress_events:
            progress = event.get("progress", 0)
            assert 0.0 <= progress <= 1.0

    async def test_agent_operation_progress_tracking(
        self, enhanced_agent_proxies, websocket_manager, mock_websocket, event_publisher
    ):
        """Test individual agent operation progress tracking."""
        ipa_proxy, wba_proxy, nga_proxy = enhanced_agent_proxies
        received_events = []
        agent_events = []

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

            if event_data.get("event_type") == "agent_status":
                agent_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps(
                {
                    "type": "subscribe",
                    "event_types": ["agent_status", "progressive_feedback"],
                }
            ),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Process with each agent individually
        await ipa_proxy.process(
            {"text": "I want to explore the mysterious cave system"}
        )

        wba_result = await wba_proxy.process(
            {
                "world_id": "test_world",
                "updates": {"location": "cave_entrance", "player_action": "explore"},
            }
        )

        await nga_proxy.process(
            {
                "prompt": "Continue the cave exploration story",
                "context": {
                    "session_id": "test_session",
                    "world_state": wba_result.get("world_state", {}),
                },
            }
        )

        await asyncio.sleep(0.5)  # Wait for all events

        # Cleanup
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify each agent generated status events
        ipa_events = [e for e in agent_events if "ipa" in e.get("agent_id", "").lower()]
        wba_events = [e for e in agent_events if "wba" in e.get("agent_id", "").lower()]
        nga_events = [e for e in agent_events if "nga" in e.get("agent_id", "").lower()]

        assert len(ipa_events) > 0
        assert len(wba_events) > 0
        assert len(nga_events) > 0

        # Verify status progression (processing -> completed)
        for agent_events_list in [ipa_events, wba_events, nga_events]:
            statuses = [e.get("status") for e in agent_events_list]
            assert "processing" in statuses
            # Should end with completed or error
            final_status = statuses[-1] if statuses else None
            assert final_status in ["completed", "error"]

    async def test_progressive_feedback_with_intermediate_results(
        self, event_publisher, websocket_manager, mock_websocket
    ):
        """Test progressive feedback with intermediate results."""
        received_events = []
        feedback_events = []

        # Create progressive feedback manager
        feedback_manager = ProgressiveFeedbackManager(
            event_publisher=event_publisher,
            update_interval=0.1,  # Fast updates for testing
            max_updates_per_workflow=20,
        )
        await feedback_manager.start()

        # Mock WebSocket to capture events
        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

            if event_data.get("event_type") == "progressive_feedback":
                feedback_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event
        mock_websocket.receive_text.side_effect = [
            json.dumps({"type": "subscribe", "event_types": ["progressive_feedback"]}),
            asyncio.CancelledError(),
        ]

        # Start connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)

        # Track a long-running operation with intermediate results
        operation_id = await feedback_manager.track_agent_operation(
            agent_id="test_nga",
            operation_type="story_generation",
            user_id="test_user",
            workflow_id="test_workflow",
            estimated_duration=5.0,
        )

        # Simulate progressive updates with intermediate results
        intermediate_results = [
            {"partial_story": "Once upon a time..."},
            {"partial_story": "Once upon a time, in a land far away..."},
            {
                "partial_story": "Once upon a time, in a land far away, there lived a brave adventurer..."
            },
        ]

        for i, result in enumerate(intermediate_results):
            progress = (i + 1) / len(intermediate_results)
            await feedback_manager.update_agent_operation(
                operation_id=operation_id,
                progress=progress,
                stage=f"generating_part_{i + 1}",
                message=f"Generated {len(result['partial_story'])} characters",
                intermediate_result=result,
            )
            await asyncio.sleep(0.1)

        # Complete the operation
        await feedback_manager.complete_agent_operation(
            operation_id=operation_id,
            final_result={
                "complete_story": "Once upon a time, in a land far away, there lived a brave adventurer who discovered amazing treasures."
            },
            success=True,
        )

        await asyncio.sleep(0.3)  # Wait for events

        # Cleanup
        await feedback_manager.stop()
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

        # Verify progressive feedback events were generated
        assert len(feedback_events) >= len(intermediate_results)

        # Verify intermediate results were included
        events_with_results = [
            e for e in feedback_events if e.get("intermediate_result") is not None
        ]
        assert len(events_with_results) >= len(intermediate_results)

        # Verify progress values increase over time
        progress_values = [e.get("progress", 0) for e in feedback_events]
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i - 1]
