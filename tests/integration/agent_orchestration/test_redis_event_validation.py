"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_redis_event_validation]]
Validation tests for Redis-based event publishing and subscription.

This module tests the Redis pub/sub event system to ensure it works correctly
with the WebSocket infrastructure and real-time configuration.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from tta_ai.orchestration.realtime.event_publisher import EventPublisher
from tta_ai.orchestration.realtime.event_subscriber import EventSubscriber
from tta_ai.orchestration.realtime.models import (
    AgentStatus,
    AgentStatusEvent,
    EventType,
    SystemMetricsEvent,
    WorkflowProgressEvent,
    WorkflowStatus,
)


@pytest.mark.integration
@pytest.mark.redis
class TestRedisEventValidation:
    """Test Redis-based event publishing and subscription."""

    @pytest_asyncio.fixture
    async def event_publisher(self, redis_client):
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
    async def event_subscriber(self, redis_client):
        """Create event subscriber for testing."""
        subscriber = EventSubscriber(
            redis_client=redis_client,
            channel_prefix="test:events",
            subscriber_id="test_subscriber",
        )
        await subscriber.start()
        yield subscriber
        await subscriber.stop()

    async def test_event_publishing_basic(self, event_publisher):
        """Test basic event publishing functionality."""
        # Create test event
        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.PROCESSING,
            message="Test agent status",
            source="test",
        )

        # Publish event
        success = await event_publisher.publish_event(event)
        assert success is True

        # Check statistics
        assert event_publisher.events_published == 1
        assert event_publisher.events_failed == 0

    async def test_event_subscription_basic(self, event_publisher, event_subscriber):
        """Test basic event subscription functionality."""
        received_events = []

        def event_handler(event):
            received_events.append(event)

        # Subscribe to agent status events
        await event_subscriber.subscribe_to_event_type(
            EventType.AGENT_STATUS, event_handler
        )

        # Give subscription time to establish
        await asyncio.sleep(0.1)

        # Publish event
        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.PROCESSING,
            message="Test subscription",
            source="test",
        )

        await event_publisher.publish_event(event)

        # Wait for event to be received
        await asyncio.sleep(0.2)

        # Verify event was received
        assert len(received_events) == 1
        received_event = received_events[0]
        assert received_event.agent_id == "test_agent"
        assert received_event.status == AgentStatus.PROCESSING

    async def test_multiple_event_types(self, event_publisher, event_subscriber):
        """Test publishing and subscribing to multiple event types."""
        received_events = []

        def event_handler(event):
            received_events.append(event)

        # Subscribe to multiple event types
        await event_subscriber.subscribe_to_event_type(
            EventType.AGENT_STATUS, event_handler
        )
        await event_subscriber.subscribe_to_event_type(
            EventType.WORKFLOW_PROGRESS, event_handler
        )

        await asyncio.sleep(0.1)

        # Publish different event types
        agent_event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.IDLE,
            message="Agent idle",
            source="test",
        )

        workflow_event = WorkflowProgressEvent(
            workflow_id="test_workflow",
            status=WorkflowStatus.IN_PROGRESS,
            progress=0.5,
            message="Workflow progress",
            source="test",
        )

        await event_publisher.publish_event(agent_event)
        await event_publisher.publish_event(workflow_event)

        # Wait for events
        await asyncio.sleep(0.2)

        # Verify both events were received
        assert len(received_events) == 2

        # Check event types
        event_types = [event.event_type for event in received_events]
        assert EventType.AGENT_STATUS in event_types
        assert EventType.WORKFLOW_PROGRESS in event_types

    async def test_event_filtering(self, event_publisher, event_subscriber):
        """Test event filtering by agent ID and user ID."""
        received_events = []

        def event_handler(event):
            received_events.append(event)

        # Subscribe to specific agent events
        await event_subscriber.subscribe_to_agent_events("target_agent", event_handler)

        await asyncio.sleep(0.1)

        # Publish events for different agents
        target_event = AgentStatusEvent(
            agent_id="target_agent",
            status=AgentStatus.PROCESSING,
            message="Target agent event",
            source="test",
        )

        other_event = AgentStatusEvent(
            agent_id="other_agent",
            status=AgentStatus.PROCESSING,
            message="Other agent event",
            source="test",
        )

        await event_publisher.publish_event(target_event)
        await event_publisher.publish_event(other_event)

        await asyncio.sleep(0.2)

        # Should only receive the target agent event
        assert len(received_events) == 1
        assert received_events[0].agent_id == "target_agent"

    async def test_event_buffering(self, redis_client):
        """Test event buffering functionality."""
        # Create publisher with small buffer
        publisher = EventPublisher(
            redis_client=redis_client,
            channel_prefix="test:events",
            enabled=True,
            buffer_size=3,  # Small buffer for testing
        )

        # Publish multiple events quickly
        events = []
        for i in range(5):
            event = AgentStatusEvent(
                agent_id=f"agent_{i}",
                status=AgentStatus.PROCESSING,
                message=f"Event {i}",
                source="test",
            )
            events.append(event)
            await publisher.publish_event(event)

        # Check that events were buffered
        assert len(publisher.event_buffer) <= 3  # Should not exceed buffer size
        assert publisher.events_published == 5

    async def test_websocket_manager_integration(self, event_publisher, redis_client):
        """Test integration between event publisher and WebSocket manager."""
        # Create mock WebSocket manager
        mock_ws_manager = Mock()
        mock_ws_manager.broadcast_event = AsyncMock(return_value=1)

        # Add WebSocket manager to publisher
        event_publisher.add_websocket_manager(mock_ws_manager)

        # Publish event
        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.PROCESSING,
            message="WebSocket integration test",
            source="test",
        )

        await event_publisher.publish_event(event)

        # Verify WebSocket manager was called
        mock_ws_manager.broadcast_event.assert_called_once()

        # Verify correct event was passed
        call_args = mock_ws_manager.broadcast_event.call_args[0]
        assert call_args[0].agent_id == "test_agent"

    async def test_event_publisher_reliability(self, redis_client):
        """Test event publisher reliability features."""
        publisher = EventPublisher(
            redis_client=redis_client,
            channel_prefix="test:events",
            enabled=True,
            buffer_size=100,
        )

        # Test with Redis temporarily unavailable
        original_redis = publisher.redis_client
        publisher.redis_client = None

        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.ERROR,
            message="Reliability test",
            source="test",
        )

        # Should handle Redis unavailability gracefully
        success = await publisher.publish_event(event)
        assert success is False
        assert publisher.events_failed == 1

        # Restore Redis and verify recovery
        publisher.redis_client = original_redis
        success = await publisher.publish_event(event)
        assert success is True

    async def test_event_subscriber_error_handling(self, event_subscriber):
        """Test event subscriber error handling."""
        error_count = 0

        def failing_handler(event):
            nonlocal error_count
            error_count += 1
            raise Exception("Handler error")

        def working_handler(event):
            pass  # Does nothing but doesn't fail

        # Subscribe with both handlers
        await event_subscriber.subscribe_to_event_type(
            EventType.AGENT_STATUS, failing_handler
        )
        await event_subscriber.subscribe_to_event_type(
            EventType.AGENT_STATUS, working_handler
        )

        await asyncio.sleep(0.1)

        # Publish event that will cause handler to fail
        event = AgentStatusEvent(
            agent_id="test_agent",
            status=AgentStatus.PROCESSING,
            message="Error handling test",
            source="test",
        )

        # Publish through Redis directly to test subscriber
        await event_subscriber.redis_client.publish(
            f"{event_subscriber.channel_prefix}:{EventType.AGENT_STATUS.value}",
            event.model_dump_json(),
        )

        await asyncio.sleep(0.2)

        # Verify error was handled gracefully
        assert error_count == 1
        assert event_subscriber.events_failed >= 1
        assert (
            event_subscriber.events_processed >= 1
        )  # Working handler should have processed

    async def test_system_metrics_events(self, event_publisher, event_subscriber):
        """Test system metrics event publishing and subscription."""
        received_events = []

        def metrics_handler(event):
            received_events.append(event)

        await event_subscriber.subscribe_to_event_type(
            EventType.SYSTEM_METRICS, metrics_handler
        )
        await asyncio.sleep(0.1)

        # Create system metrics event
        metrics_event = SystemMetricsEvent(
            cpu_usage=45.2,
            memory_usage=1024.5,
            active_connections=15,
            queue_depth=3,
            source="test",
        )

        await event_publisher.publish_event(metrics_event)
        await asyncio.sleep(0.2)

        # Verify metrics event was received
        assert len(received_events) == 1
        received_event = received_events[0]
        assert received_event.cpu_usage == 45.2
        assert received_event.memory_usage == 1024.5
        assert received_event.active_connections == 15

    async def test_concurrent_publishing(self, event_publisher):
        """Test concurrent event publishing."""
        # Create multiple events to publish concurrently
        events = []
        for i in range(10):
            event = AgentStatusEvent(
                agent_id=f"agent_{i}",
                status=AgentStatus.PROCESSING,
                message=f"Concurrent event {i}",
                source="test",
            )
            events.append(event)

        # Publish all events concurrently
        tasks = [event_publisher.publish_event(event) for event in events]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)
        assert event_publisher.events_published == 10
        assert event_publisher.events_failed == 0

    async def test_event_statistics(self, event_publisher, event_subscriber):
        """Test event statistics collection."""
        # Initial statistics
        initial_published = event_publisher.events_published
        initial_subscriber_received = event_subscriber.events_received

        # Publish several events
        for i in range(5):
            event = AgentStatusEvent(
                agent_id=f"stats_agent_{i}",
                status=AgentStatus.PROCESSING,
                message=f"Statistics test {i}",
                source="test",
            )
            await event_publisher.publish_event(event)

        # Check publisher statistics
        assert event_publisher.events_published == initial_published + 5
        assert event_publisher.last_publish_time > 0

        # Subscribe and check subscriber statistics
        received_events = []

        def stats_handler(event):
            received_events.append(event)

        await event_subscriber.subscribe_to_event_type(
            EventType.AGENT_STATUS, stats_handler
        )
        await asyncio.sleep(0.1)

        # Publish one more event
        final_event = AgentStatusEvent(
            agent_id="final_stats_agent",
            status=AgentStatus.COMPLETED,
            message="Final statistics test",
            source="test",
        )
        await event_publisher.publish_event(final_event)
        await asyncio.sleep(0.2)

        # Check that subscriber received the event
        assert len(received_events) == 1
        assert event_subscriber.events_received > initial_subscriber_received
