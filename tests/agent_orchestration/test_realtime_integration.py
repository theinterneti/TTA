"""
Integration tests for real-time interaction management components.

This module tests the integration between WebSocket management, event publishing,
progressive feedback, and workflow progress tracking.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.agent_orchestration.realtime.event_publisher import EventPublisher
from src.agent_orchestration.realtime.models import (
    AgentStatus,
    WorkflowStatus,
    create_agent_status_event,
)
from src.agent_orchestration.realtime.progressive_feedback import (
    ProgressiveFeedbackManager,
)
from src.agent_orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
)
from src.agent_orchestration.realtime.workflow_progress import (
    WorkflowProgressTracker,
    WorkflowStage,
)


@pytest.mark.asyncio
async def test_event_publisher_integration():
    """Test event publisher with mock Redis and WebSocket manager."""
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_redis.publish = AsyncMock(return_value=1)

    # Create event publisher
    publisher = EventPublisher(
        redis_client=mock_redis,
        enabled=True,
        broadcast_agent_status=True,
    )

    # Mock WebSocket manager
    mock_ws_manager = Mock()
    mock_ws_manager.broadcast_event = AsyncMock(return_value=2)
    publisher.add_websocket_manager(mock_ws_manager)

    # Publish an agent status event
    success = await publisher.publish_agent_status_event(
        agent_id="test-agent",
        agent_type="ipa",
        status=AgentStatus.ONLINE,
        heartbeat_age=0.0,
    )

    assert success
    assert publisher.events_published == 1
    assert publisher.events_failed == 0

    # Verify Redis publish was called
    assert mock_redis.publish.call_count >= 2  # General and specific channels

    # Verify WebSocket broadcast was called
    mock_ws_manager.broadcast_event.assert_called_once()


@pytest.mark.asyncio
async def test_progressive_feedback_integration():
    """Test progressive feedback manager with event publisher."""
    # Mock event publisher
    mock_publisher = Mock()
    mock_publisher.publish_progressive_feedback_event = AsyncMock(return_value=True)

    # Create feedback manager
    feedback_manager = ProgressiveFeedbackManager(
        event_publisher=mock_publisher,
        update_interval=0.1,  # Fast for testing
        max_updates_per_operation=10,
    )

    await feedback_manager.start()

    try:
        # Start an operation
        operation_id = await feedback_manager.start_operation(
            operation_type="test_operation",
            user_id="test-user",
            total_steps=3,
        )

        assert operation_id is not None
        assert len(feedback_manager.active_operations) == 1

        # Update progress
        success = await feedback_manager.update_operation_progress(
            operation_id,
            stage="processing",
            message="Processing data",
            progress_percentage=50.0,
            intermediate_result={"processed": 100},
        )

        assert success
        assert feedback_manager.operation_update_counts[operation_id] == 1

        # Complete operation
        success = await feedback_manager.complete_operation(
            operation_id,
            "Operation completed successfully",
            {"final_result": "success"},
        )

        assert success
        assert operation_id not in feedback_manager.active_operations

        # Verify event publisher was called
        assert mock_publisher.publish_progressive_feedback_event.call_count >= 2

    finally:
        await feedback_manager.stop()


@pytest.mark.asyncio
async def test_workflow_progress_integration():
    """Test workflow progress tracker with event publisher."""
    # Mock event publisher
    mock_publisher = Mock()
    mock_publisher.publish_workflow_progress_event = AsyncMock(return_value=True)

    # Create workflow tracker
    workflow_tracker = WorkflowProgressTracker(
        event_publisher=mock_publisher,
        update_interval=0.1,  # Fast for testing
        auto_publish_updates=True,
    )

    await workflow_tracker.start()

    try:
        # Start a workflow
        workflow_id = await workflow_tracker.start_workflow(
            workflow_type="test_workflow",
            user_id="test-user",
            total_steps=5,
            milestones=[
                {
                    "name": "Initialize",
                    "description": "Initialize workflow",
                    "stage": WorkflowStage.INITIALIZING.value,
                    "weight": 0.2,
                },
                {
                    "name": "Process",
                    "description": "Process data",
                    "stage": WorkflowStage.EXECUTING.value,
                    "weight": 0.6,
                },
                {
                    "name": "Finalize",
                    "description": "Finalize workflow",
                    "stage": WorkflowStage.FINALIZING.value,
                    "weight": 0.2,
                },
            ],
        )

        assert workflow_id is not None
        assert len(workflow_tracker.active_workflows) == 1

        # Update workflow progress
        success = await workflow_tracker.update_workflow_progress(
            workflow_id,
            stage=WorkflowStage.EXECUTING,
            status=WorkflowStatus.RUNNING,
            current_step="Processing step 1",
            completed_steps=1,
        )

        assert success

        # Complete a milestone
        workflow = workflow_tracker.active_workflows[workflow_id]
        milestone_id = workflow.milestones[0].milestone_id
        success = await workflow_tracker.complete_milestone(workflow_id, milestone_id)

        assert success
        assert workflow.milestones[0].completed

        # Complete workflow
        success = await workflow_tracker.complete_workflow(
            workflow_id, "Workflow completed successfully", {"final_output": "success"}
        )

        assert success
        assert workflow_id not in workflow_tracker.active_workflows

        # Verify event publisher was called
        assert mock_publisher.publish_workflow_progress_event.call_count >= 3

    finally:
        await workflow_tracker.stop()


@pytest.mark.asyncio
async def test_websocket_manager_with_event_subscription():
    """Test WebSocket manager with event subscription."""
    # Mock configuration
    config = {
        "agent_orchestration.realtime.websocket.enabled": True,
        "agent_orchestration.realtime.websocket.heartbeat_interval": 1.0,
        "agent_orchestration.realtime.websocket.connection_timeout": 5.0,
        "agent_orchestration.realtime.websocket.auth_required": False,
        "agent_orchestration.realtime.events.enabled": True,
        "agent_orchestration.realtime.events.redis_channel_prefix": "test:events",
    }

    # Mock Redis client
    mock_redis = AsyncMock()

    # Create WebSocket manager
    ws_manager = WebSocketConnectionManager(
        config=config,
        redis_client=mock_redis,
    )

    # Test status
    status = ws_manager.get_status()
    assert status["total_connections"] == 0
    assert status["configuration"]["heartbeat_interval"] == 1.0

    # Test event broadcasting (no connections)
    test_event = create_agent_status_event(
        agent_id="test-agent", agent_type="ipa", status=AgentStatus.ONLINE
    )

    sent_count = await ws_manager.broadcast_event(test_event)
    assert sent_count == 0  # No connections to broadcast to


@pytest.mark.asyncio
async def test_full_integration_flow():
    """Test full integration flow with all components."""
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_redis.publish = AsyncMock(return_value=1)

    # Create event publisher
    event_publisher = EventPublisher(
        redis_client=mock_redis,
        enabled=True,
        broadcast_agent_status=True,
        broadcast_workflow_progress=True,
    )

    # Create progressive feedback manager
    feedback_manager = ProgressiveFeedbackManager(
        event_publisher=event_publisher,
        update_interval=0.1,
        max_updates_per_operation=5,
    )

    # Create workflow tracker
    workflow_tracker = WorkflowProgressTracker(
        event_publisher=event_publisher,
        update_interval=0.1,
        auto_publish_updates=True,
    )

    # Create WebSocket manager
    ws_config = {
        "agent_orchestration.realtime.websocket.enabled": True,
        "agent_orchestration.realtime.websocket.heartbeat_interval": 1.0,
        "agent_orchestration.realtime.events.enabled": True,
    }

    ws_manager = WebSocketConnectionManager(
        config=ws_config,
        redis_client=mock_redis,
    )

    # Connect event publisher with WebSocket manager
    event_publisher.add_websocket_manager(ws_manager)

    # Start services
    await feedback_manager.start()
    await workflow_tracker.start()

    try:
        # Start a workflow with progressive feedback
        workflow_id = await workflow_tracker.start_workflow(
            workflow_type="integrated_test",
            user_id="test-user",
            total_steps=3,
        )

        operation_id = await feedback_manager.start_operation(
            operation_type="workflow_operation",
            user_id="test-user",
        )

        # Simulate workflow progress with feedback
        await workflow_tracker.update_workflow_progress(
            workflow_id,
            stage=WorkflowStage.EXECUTING,
            current_step="Step 1",
            completed_steps=1,
        )

        await feedback_manager.update_operation_progress(
            operation_id,
            stage="step_1",
            message="Executing step 1",
            progress_percentage=33.0,
        )

        # Publish agent status event
        await event_publisher.publish_agent_status_event(
            agent_id="test-agent",
            agent_type="ipa",
            status=AgentStatus.BUSY,
        )

        # Complete workflow and operation
        await workflow_tracker.complete_workflow(workflow_id)
        await feedback_manager.complete_operation(operation_id)

        # Verify statistics
        pub_stats = event_publisher.get_statistics()
        feedback_stats = feedback_manager.get_statistics()
        workflow_stats = workflow_tracker.get_statistics()
        ws_stats = ws_manager.get_status()

        assert pub_stats["events_published"] > 0
        assert feedback_stats["is_running"]
        assert workflow_stats["is_running"]
        assert ws_stats["total_connections"] == 0

        # Verify Redis publish was called multiple times
        assert mock_redis.publish.call_count > 0

    finally:
        await feedback_manager.stop()
        await workflow_tracker.stop()
        await ws_manager.shutdown()


def test_component_statistics():
    """Test statistics collection from all components."""
    # Test event publisher statistics
    publisher = EventPublisher(enabled=True)
    stats = publisher.get_statistics()

    assert "enabled" in stats
    assert "events_published" in stats
    assert "configuration" in stats

    # Test feedback manager statistics
    feedback_manager = ProgressiveFeedbackManager()
    stats = feedback_manager.get_statistics()

    assert "is_running" in stats
    assert "active_operations" in stats
    assert "configuration" in stats

    # Test workflow tracker statistics
    workflow_tracker = WorkflowProgressTracker()
    stats = workflow_tracker.get_statistics()

    assert "is_running" in stats
    assert "active_workflows" in stats
    assert "workflows_by_type" in stats

    # Test WebSocket manager statistics
    config = {"agent_orchestration.realtime.websocket.enabled": True}
    ws_manager = WebSocketConnectionManager(config=config)
    stats = ws_manager.get_status()

    assert "total_connections" in stats
    assert "configuration" in stats
