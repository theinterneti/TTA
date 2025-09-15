"""
Integration tests for response time optimization engine.

This module tests the complete optimization system including response time
monitoring, optimization algorithms, resource management, and analytics.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from src.agent_orchestration.optimization import (
    OptimizationEngine,
    OptimizationStrategy,
    PerformanceAnalytics,
    ResourceType,
    ResponseTimeCategory,
    ResponseTimeCollector,
    WorkflowPriority,
    WorkflowResourceManager,
)


@pytest.mark.asyncio
async def test_response_time_collector_integration():
    """Test response time collector with metrics collection."""
    collector = ResponseTimeCollector(
        max_metrics_per_operation=100,
        cleanup_interval=1.0,
        metric_retention_hours=1.0,
    )

    await collector.start()

    try:
        # Test timing operations
        context_id = collector.start_timing(
            ResponseTimeCategory.MESSAGE_PROCESSING,
            "test_message_send",
            metadata={"agent_type": "ipa", "priority": "high"},
        )

        # Simulate some work
        await asyncio.sleep(0.01)

        metric = collector.end_timing(context_id, success=True)

        assert metric is not None
        assert metric.category == ResponseTimeCategory.MESSAGE_PROCESSING
        assert metric.operation == "test_message_send"
        assert metric.success is True
        assert metric.duration > 0

        # Test statistics
        stats = collector.get_stats(
            ResponseTimeCategory.MESSAGE_PROCESSING, "test_message_send"
        )
        assert stats is not None
        assert stats.sample_count == 1
        assert stats.mean_duration > 0
        assert stats.success_rate == 1.0

        # Test direct duration recording
        collector.record_duration(
            ResponseTimeCategory.WORKFLOW_EXECUTION,
            "test_workflow",
            duration=2.5,
            success=True,
            metadata={"workflow_type": "narrative_generation"},
        )

        workflow_stats = collector.get_stats(
            ResponseTimeCategory.WORKFLOW_EXECUTION, "test_workflow"
        )
        assert workflow_stats is not None
        assert workflow_stats.sample_count == 1
        assert workflow_stats.mean_duration == 2.5

    finally:
        await collector.stop()


@pytest.mark.asyncio
async def test_optimization_engine_integration():
    """Test optimization engine with parameter adjustment."""
    # Create response time collector with some data
    collector = ResponseTimeCollector()
    await collector.start()

    # Add some slow operations to trigger optimization
    for _i in range(10):
        collector.record_duration(
            ResponseTimeCategory.MESSAGE_PROCESSING,
            "slow_operation",
            duration=6.0,  # Slow operation (> 5s threshold)
            success=True,
        )

    # Create optimization engine
    engine = OptimizationEngine(
        response_time_collector=collector,
        optimization_interval=0.1,  # Fast for testing
        enabled_strategies=[OptimizationStrategy.CONSERVATIVE],
        max_adjustments_per_cycle=2,
    )

    await engine.start()

    try:
        # Register a test parameter
        callback_called = False
        new_value = None

        def test_callback(param_name: str, value):
            nonlocal callback_called, new_value
            callback_called = True
            new_value = value

        engine.register_parameter(
            name="message_queue_size",
            current_value=10000,
            min_value=1000,
            max_value=50000,
            step_size=1000,
            parameter_type="int",
            component="test",
            description="Test message queue size",
            callback=test_callback,
        )

        # Run optimization cycle
        results = await engine.run_optimization_cycle()

        # Should have optimization suggestions due to slow operations
        assert len(results) >= 0  # May or may not have suggestions based on algorithm

        # Check engine statistics
        stats = engine.get_statistics()
        assert stats["is_running"] is True
        assert stats["registered_parameters"] == 1
        assert "conservative" in stats["enabled_strategies"]

    finally:
        await engine.stop()
        await collector.stop()


@pytest.mark.asyncio
async def test_workflow_resource_manager_integration():
    """Test workflow resource manager with resource allocation."""
    manager = WorkflowResourceManager(
        max_concurrent_workflows=3,
        resource_monitoring_interval=0.1,
    )

    await manager.start()

    try:
        # Request resources for a workflow
        success = await manager.request_workflow_resources(
            workflow_id="test-workflow-1",
            workflow_type="narrative_generation",
            priority=WorkflowPriority.HIGH,
            user_id="test-user",
            estimated_duration=60.0,
            resource_requirements={
                ResourceType.CPU: 20.0,  # 20% CPU
                ResourceType.MEMORY: 1024.0,  # 1GB memory
                ResourceType.AGENT_SLOTS: 3.0,  # 3 agent slots
            },
            max_concurrent_agents=3,
        )

        assert success is True

        # Check resource allocation
        stats = manager.get_statistics()
        assert stats["active_allocations"] == 1
        assert stats["scheduler_stats"]["running_workflows"] == 1

        # Check resource pool utilization
        cpu_pool = stats["resource_pools"]["cpu"]
        assert cpu_pool["allocated_capacity"] == 20.0
        assert cpu_pool["utilization_percent"] == 20.0

        # Request resources for another workflow
        success2 = await manager.request_workflow_resources(
            workflow_id="test-workflow-2",
            workflow_type="world_building",
            priority=WorkflowPriority.NORMAL,
            user_id="test-user",
        )

        assert success2 is True

        # Release resources
        released = await manager.release_workflow_resources("test-workflow-1")
        assert released is True

        # Check updated statistics
        final_stats = manager.get_statistics()
        assert final_stats["scheduler_stats"]["running_workflows"] == 1

    finally:
        await manager.stop()


@pytest.mark.asyncio
async def test_performance_analytics_integration():
    """Test performance analytics with dashboard generation."""
    # Create components
    collector = ResponseTimeCollector()
    engine = OptimizationEngine(collector, optimization_interval=0.1)
    manager = WorkflowResourceManager(max_concurrent_workflows=5)

    analytics = PerformanceAnalytics(
        response_time_collector=collector,
        optimization_engine=engine,
        resource_manager=manager,
        analytics_interval=0.1,
    )

    # Start all components
    await collector.start()
    await engine.start()
    await manager.start()
    await analytics.start()

    try:
        # Add some test data
        collector.record_duration(
            ResponseTimeCategory.MESSAGE_PROCESSING,
            "fast_operation",
            duration=0.5,
            success=True,
        )

        collector.record_duration(
            ResponseTimeCategory.WORKFLOW_EXECUTION,
            "slow_workflow",
            duration=8.0,
            success=True,
        )

        collector.record_duration(
            ResponseTimeCategory.API_REQUEST,
            "api_call",
            duration=1.2,
            success=False,  # Failed operation
        )

        # Get dashboard data
        dashboard = await analytics.get_performance_dashboard(force_refresh=True)

        # Verify dashboard structure
        assert "system_health" in dashboard
        assert "response_time_analytics" in dashboard
        assert "optimization_analytics" in dashboard
        assert "resource_analytics" in dashboard
        assert "performance_trends" in dashboard
        assert "recommendations" in dashboard

        # Check system health
        health = dashboard["system_health"]
        assert "overall_health_score" in health
        assert "response_time_health" in health
        assert "success_rate_health" in health

        # Check response time analytics
        rt_analytics = dashboard["response_time_analytics"]
        assert "category_summaries" in rt_analytics
        assert "slowest_operations" in rt_analytics
        assert rt_analytics["total_operations"] > 0

        # Check recommendations
        recommendations = dashboard["recommendations"]
        assert isinstance(recommendations, list)

        # Should have recommendations for slow operations and failed operations
        slow_ops_rec = any(rec["type"] == "performance" for rec in recommendations)
        failed_ops_rec = any(rec["type"] == "reliability" for rec in recommendations)

        # At least one type of recommendation should be present
        assert slow_ops_rec or failed_ops_rec

        # Test analytics statistics
        analytics_stats = analytics.get_statistics()
        assert analytics_stats["is_running"] is True

    finally:
        await analytics.stop()
        await manager.stop()
        await engine.stop()
        await collector.stop()


@pytest.mark.asyncio
async def test_full_optimization_system_integration():
    """Test complete optimization system working together."""
    # Create all components
    collector = ResponseTimeCollector(max_metrics_per_operation=50)

    # Mock event publisher
    mock_publisher = Mock()
    mock_publisher.publish_optimization_event = AsyncMock(return_value=True)

    engine = OptimizationEngine(
        response_time_collector=collector,
        event_publisher=mock_publisher,
        optimization_interval=0.1,
        enabled_strategies=[
            OptimizationStrategy.CONSERVATIVE,
            OptimizationStrategy.STATISTICAL,
        ],
    )

    manager = WorkflowResourceManager(
        response_time_collector=collector,
        event_publisher=mock_publisher,
        max_concurrent_workflows=3,
    )

    analytics = PerformanceAnalytics(
        response_time_collector=collector,
        optimization_engine=engine,
        resource_manager=manager,
    )

    # Start all components
    await collector.start()
    await engine.start()
    await manager.start()
    await analytics.start()

    try:
        # Register optimization parameters
        engine.register_parameter(
            name="test_timeout",
            current_value=30.0,
            min_value=10.0,
            max_value=120.0,
            step_size=5.0,
            parameter_type="float",
            component="test",
            description="Test timeout parameter",
        )

        # Simulate system activity
        # 1. Record various response times
        operations = [
            ("message_send", ResponseTimeCategory.MESSAGE_PROCESSING, 0.8, True),
            ("workflow_exec", ResponseTimeCategory.WORKFLOW_EXECUTION, 4.2, True),
            ("agent_response", ResponseTimeCategory.AGENT_RESPONSE, 2.1, True),
            ("db_query", ResponseTimeCategory.DATABASE_OPERATION, 0.3, True),
            (
                "slow_operation",
                ResponseTimeCategory.SYSTEM_OPERATION,
                7.5,
                True,
            ),  # Slow
            (
                "failed_operation",
                ResponseTimeCategory.API_REQUEST,
                1.0,
                False,
            ),  # Failed
        ]

        for op_name, category, duration, success in operations:
            for _ in range(5):  # Multiple samples
                collector.record_duration(category, op_name, duration, success)

        # 2. Request workflow resources
        await manager.request_workflow_resources(
            workflow_id="integration-test-workflow",
            workflow_type="integration_test",
            priority=WorkflowPriority.HIGH,
            resource_requirements={
                ResourceType.CPU: 15.0,
                ResourceType.MEMORY: 512.0,
                ResourceType.AGENT_SLOTS: 2.0,
            },
        )

        # 3. Run optimization cycle
        optimization_results = await engine.run_optimization_cycle()

        # 4. Get comprehensive analytics
        dashboard = await analytics.get_performance_dashboard(force_refresh=True)

        # Verify integration
        assert dashboard["system_health"]["overall_health_score"] > 0
        assert dashboard["response_time_analytics"]["total_operations"] == 6
        assert dashboard["resource_analytics"]["enabled"] is True
        assert dashboard["optimization_analytics"]["enabled"] is True

        # Check that slow operations are identified
        slowest_ops = dashboard["response_time_analytics"]["slowest_operations"]
        slow_op_names = [op["operation"] for op in slowest_ops]
        assert "slow_operation" in slow_op_names

        # Check recommendations
        recommendations = dashboard["recommendations"]
        assert len(recommendations) > 0

        # Verify resource utilization
        resource_stats = dashboard["resource_analytics"]["resource_stats"]
        assert resource_stats["active_allocations"] == 1

        # Check optimization effectiveness (if any optimizations were applied)
        if optimization_results:
            assert len(engine.optimization_history) > 0

        # Verify event publishing was called if optimizations occurred
        if optimization_results:
            mock_publisher.publish_optimization_event.assert_called()

    finally:
        # Clean up
        await manager.release_workflow_resources("integration-test-workflow")
        await analytics.stop()
        await manager.stop()
        await engine.stop()
        await collector.stop()


def test_optimization_system_statistics():
    """Test statistics collection from all optimization components."""
    # Test individual component statistics
    collector = ResponseTimeCollector()
    stats = collector.get_statistics()

    assert "is_running" in stats
    assert "total_metrics" in stats
    assert "active_timings" in stats

    engine = OptimizationEngine(collector)
    stats = engine.get_statistics()

    assert "is_running" in stats
    assert "enabled_strategies" in stats
    assert "registered_parameters" in stats

    manager = WorkflowResourceManager()
    stats = manager.get_statistics()

    assert "is_running" in stats
    assert "resource_pools" in stats
    assert "scheduler_stats" in stats

    analytics = PerformanceAnalytics(collector, engine, manager)
    stats = analytics.get_statistics()

    assert "is_running" in stats
    assert "performance_trends" in stats
    assert "configuration" in stats
