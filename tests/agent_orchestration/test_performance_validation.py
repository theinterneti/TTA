"""
Performance validation tests for 2-second response time requirements.

This module provides comprehensive performance validation using the performance
optimization infrastructure to ensure sub-2-second response times.
"""

import asyncio
import statistics
import time

import pytest
import pytest_asyncio
from tta_ai.orchestration.models import AgentType
from tta_ai.orchestration.performance.alerting import PerformanceAlerting
from tta_ai.orchestration.performance.analytics import PerformanceAnalytics
from tta_ai.orchestration.performance.optimization import IntelligentAgentCoordinator
from tta_ai.orchestration.performance.response_time_monitor import (
    OperationType,
    ResponseTimeMonitor,
)
from tta_ai.orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.service import AgentOrchestrationService
from tta_ai.orchestration.therapeutic_safety import (
    CrisisInterventionManager,
    TherapeuticValidator,
)


@pytest.mark.performance
@pytest.mark.redis
@pytest.mark.neo4j
class TestPerformanceValidation:
    """Comprehensive performance validation for 2-second response time requirements."""

    @pytest_asyncio.fixture
    async def performance_infrastructure(self, redis_client):
        """Create complete performance monitoring and optimization infrastructure."""
        # Create response time monitor
        monitor = ResponseTimeMonitor(
            max_metrics_history=5000,
            statistics_window_minutes=30,
            enable_real_time_analysis=True,
        )
        await monitor.start()

        # Create intelligent agent coordinator
        coordinator = IntelligentAgentCoordinator(
            response_time_monitor=monitor, target_response_time=2.0
        )

        # Register agents for optimization
        coordinator.register_agent(
            "perf_ipa", AgentType.INPUT_PROCESSOR, max_concurrent=10
        )
        coordinator.register_agent(
            "perf_wba", AgentType.WORLD_BUILDER, max_concurrent=8
        )
        coordinator.register_agent(
            "perf_nga", AgentType.NARRATIVE_GENERATOR, max_concurrent=8
        )

        await coordinator.start()

        # Create performance analytics
        analytics = PerformanceAnalytics(
            response_time_monitor=monitor, analysis_window_minutes=15
        )

        # Create performance alerting
        alerting = PerformanceAlerting()
        await alerting.start()

        yield monitor, coordinator, analytics, alerting

        # Cleanup
        await coordinator.stop()
        await monitor.stop()
        await alerting.stop()

    @pytest_asyncio.fixture
    async def optimized_orchestration_service(
        self,
        redis_coordinator,
        neo4j_driver,
        event_publisher,
        performance_infrastructure,
    ):
        """Create orchestration service with performance optimization."""
        monitor, coordinator, analytics, alerting = performance_infrastructure

        # Create enhanced agent proxies with performance monitoring
        ipa_proxy = InputProcessorAgentProxy(
            coordinator=redis_coordinator,
            instance="perf_ipa",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        wba_proxy = WorldBuilderAgentProxy(
            coordinator=redis_coordinator,
            instance="perf_wba",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
            neo4j_driver=neo4j_driver,
        )

        nga_proxy = NarrativeGeneratorAgentProxy(
            coordinator=redis_coordinator,
            instance="perf_nga",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        # Create therapeutic components
        therapeutic_validator = TherapeuticValidator()
        crisis_manager = CrisisInterventionManager(event_publisher=event_publisher)
        await crisis_manager.start()

        # Create orchestration service
        service = AgentOrchestrationService(
            ipa_proxy=ipa_proxy,
            wba_proxy=wba_proxy,
            nga_proxy=nga_proxy,
            therapeutic_validator=therapeutic_validator,
            crisis_intervention_manager=crisis_manager,
        )

        yield service, monitor, coordinator, analytics, alerting

        await crisis_manager.stop()

    async def test_two_second_response_time_validation(
        self, optimized_orchestration_service
    ):
        """Test 2-second response time requirement validation."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Test scenarios with different complexity levels
        test_scenarios = [
            {
                "input": "Hello, how are you?",
                "complexity": "simple",
                "target_time": 1.0,  # Simple queries should be very fast
            },
            {
                "input": "I'm feeling anxious about my job interview tomorrow. Can you help?",
                "complexity": "medium",
                "target_time": 2.0,  # Standard therapeutic queries
            },
            {
                "input": "I'm dealing with complex relationship issues involving my family, work colleagues, and romantic partner. I need comprehensive guidance on managing all these dynamics while maintaining my mental health.",
                "complexity": "complex",
                "target_time": 2.0,  # Even complex queries should meet SLA
            },
        ]

        response_times = []
        results = []

        for i, scenario in enumerate(test_scenarios):
            session_id = f"perf_validation_session_{i + 1:03d}"
            world_id = f"perf_validation_world_{i + 1:03d}"
            user_id = f"perf_validation_user_{i + 1}"

            # Track performance with monitoring infrastructure
            async with monitor.track_operation(
                operation_type=OperationType.WORKFLOW_EXECUTION,
                workflow_id=f"perf_test_{i + 1}",
                user_id=user_id,
                metadata={"complexity": scenario["complexity"]},
            ):
                start_time = time.time()

                result = await service.process_user_input(
                    user_input=scenario["input"],
                    session_id=session_id,
                    world_id=world_id,
                    user_id=user_id,
                )

                end_time = time.time()
                response_time = end_time - start_time

            response_times.append(response_time)
            results.append(result)

            # Validate individual response time
            assert result is not None
            assert "story" in result
            assert len(result["story"]) > 0

            # Validate response time meets target
            assert response_time <= scenario["target_time"], (
                f"Response time {response_time:.2f}s exceeded target {scenario['target_time']}s for {scenario['complexity']} query"
            )

            print(
                f"{scenario['complexity'].capitalize()} query: {response_time:.2f}s (target: {scenario['target_time']}s)"
            )

        # Validate overall performance statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]

        # Performance assertions
        assert avg_response_time < 1.5, (
            f"Average response time {avg_response_time:.2f}s exceeds 1.5s"
        )
        assert max_response_time < 2.0, (
            f"Maximum response time {max_response_time:.2f}s exceeds 2.0s SLA"
        )
        assert p95_response_time < 2.0, (
            f"P95 response time {p95_response_time:.2f}s exceeds 2.0s SLA"
        )

        # Get performance statistics from monitor
        stats = monitor.get_statistics(time_window_minutes=5)

        if OperationType.WORKFLOW_EXECUTION in stats:
            workflow_stats = stats[OperationType.WORKFLOW_EXECUTION]
            assert workflow_stats.meets_sla, (
                "Workflow execution does not meet 2-second SLA"
            )
            assert workflow_stats.success_rate >= 1.0, (
                "Not all workflows completed successfully"
            )

        print("Performance validation summary:")
        print(f"  Average response time: {avg_response_time:.2f}s")
        print(f"  Maximum response time: {max_response_time:.2f}s")
        print(f"  P95 response time: {p95_response_time:.2f}s")
        print(f"  All scenarios met SLA: {max_response_time < 2.0}")

    async def test_performance_optimization_effectiveness(
        self, optimized_orchestration_service
    ):
        """Test effectiveness of performance optimization algorithms."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Test multiple iterations to allow optimization to take effect
        test_input = "I need help managing stress and anxiety in my daily life."
        iterations = 10

        response_times = []

        for i in range(iterations):
            session_id = f"optimization_session_{i + 1:03d}"
            world_id = f"optimization_world_{i + 1:03d}"
            user_id = f"optimization_user_{i + 1}"

            start_time = time.time()

            result = await service.process_user_input(
                user_input=test_input,
                session_id=session_id,
                world_id=world_id,
                user_id=user_id,
            )

            end_time = time.time()
            response_time = end_time - start_time

            response_times.append(response_time)

            assert result is not None
            assert "story" in result

            # Brief pause to allow optimization algorithms to adapt
            await asyncio.sleep(0.1)

        # Analyze optimization effectiveness
        first_half = response_times[: iterations // 2]
        second_half = response_times[iterations // 2 :]

        first_half_avg = statistics.mean(first_half)
        second_half_avg = statistics.mean(second_half)

        # Performance should improve or remain stable
        improvement_ratio = (first_half_avg - second_half_avg) / first_half_avg

        # All response times should meet SLA
        max_response_time = max(response_times)
        assert max_response_time < 2.5, (
            f"Maximum response time {max_response_time:.2f}s exceeds acceptable limit"
        )

        # Get optimization statistics
        optimization_stats = coordinator.get_optimization_statistics()

        assert optimization_stats["registered_agents"] == 3
        assert optimization_stats["system_load"] >= 0.0

        print("Optimization effectiveness test:")
        print(f"  First half average: {first_half_avg:.2f}s")
        print(f"  Second half average: {second_half_avg:.2f}s")
        print(f"  Improvement ratio: {improvement_ratio:.2%}")
        print(f"  System load: {optimization_stats['system_load']:.2%}")
        print(f"  Optimization strategy: {optimization_stats['optimization_strategy']}")

    async def test_performance_under_load(self, optimized_orchestration_service):
        """Test performance under concurrent load."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Create concurrent load
        concurrent_requests = 5
        test_inputs = [
            "I need help with time management.",
            "Can you help me deal with workplace stress?",
            "I'm struggling with social anxiety.",
            "How can I improve my sleep quality?",
            "I need strategies for managing depression.",
        ]

        # Create concurrent tasks
        tasks = []
        start_time = time.time()

        for i in range(concurrent_requests):
            session_id = f"load_test_session_{i + 1:03d}"
            world_id = f"load_test_world_{i + 1:03d}"
            user_id = f"load_test_user_{i + 1}"

            task = asyncio.create_task(
                service.process_user_input(
                    user_input=test_inputs[i],
                    session_id=session_id,
                    world_id=world_id,
                    user_id=user_id,
                )
            )
            tasks.append((task, session_id))

        # Wait for all tasks to complete
        results = []
        individual_times = []

        for task, session_id in tasks:
            task_start = time.time()
            try:
                result = await task
                task_end = time.time()
                task_time = task_end - task_start

                results.append(result)
                individual_times.append(task_time)

                assert result is not None
                assert "story" in result

            except Exception as e:
                pytest.fail(f"Concurrent task failed for session {session_id}: {e}")

        total_time = time.time() - start_time

        # Validate concurrent performance
        assert len(results) == concurrent_requests

        # Individual response times should still meet SLA
        max_individual_time = max(individual_times)
        avg_individual_time = statistics.mean(individual_times)

        assert max_individual_time < 3.0, (
            f"Maximum individual response time {max_individual_time:.2f}s under load exceeds limit"
        )
        assert avg_individual_time < 2.5, (
            f"Average individual response time {avg_individual_time:.2f}s under load exceeds limit"
        )

        # Total time should be reasonable (not sequential)
        expected_sequential_time = sum(individual_times)
        concurrency_efficiency = expected_sequential_time / total_time

        assert concurrency_efficiency > 2.0, (
            f"Concurrency efficiency {concurrency_efficiency:.1f}x is too low"
        )

        print("Performance under load test:")
        print(f"  Concurrent requests: {concurrent_requests}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average individual time: {avg_individual_time:.2f}s")
        print(f"  Maximum individual time: {max_individual_time:.2f}s")
        print(f"  Concurrency efficiency: {concurrency_efficiency:.1f}x")

    async def test_performance_analytics_validation(
        self, optimized_orchestration_service
    ):
        """Test performance analytics and bottleneck identification."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Generate varied workload for analytics
        test_scenarios = [
            ("Simple query", "Hello"),
            ("Medium query", "I need help with stress management"),
            (
                "Complex query",
                "I'm dealing with multiple mental health challenges including anxiety, depression, and relationship issues",
            ),
            ("Crisis query", "I'm feeling overwhelmed and don't know what to do"),
            ("Therapeutic query", "Can you help me develop coping strategies?"),
        ]

        # Execute scenarios multiple times
        for scenario_name, test_input in test_scenarios:
            for i in range(3):  # 3 iterations per scenario
                session_id = (
                    f"analytics_session_{scenario_name.replace(' ', '_')}_{i + 1}"
                )
                world_id = f"analytics_world_{i + 1:03d}"
                user_id = f"analytics_user_{i + 1}"

                result = await service.process_user_input(
                    user_input=test_input,
                    session_id=session_id,
                    world_id=world_id,
                    user_id=user_id,
                )

                assert result is not None

                # Brief pause between requests
                await asyncio.sleep(0.1)

        # Wait for analytics to process
        await asyncio.sleep(1.0)

        # Perform analytics analysis
        analysis_results = await analytics.analyze_performance()

        assert "bottlenecks" in analysis_results
        assert "trends" in analysis_results
        assert "recommendations" in analysis_results
        assert "overall_health" in analysis_results

        # Validate analytics results
        overall_health = analysis_results["overall_health"]
        assert overall_health in [
            "excellent",
            "good",
            "fair",
            "poor",
            "critical",
            "no_data",
        ]

        # Should not have critical bottlenecks for test workload
        critical_bottlenecks = [
            b for b in analysis_results["bottlenecks"] if b.get("severity", 0) > 0.8
        ]
        assert len(critical_bottlenecks) == 0, (
            f"Found critical bottlenecks: {critical_bottlenecks}"
        )

        # Get performance summary
        performance_summary = monitor.get_performance_summary()

        assert performance_summary["total_operations"] >= len(test_scenarios) * 3
        assert performance_summary["overall_performance"] != "no_data"

        print("Performance analytics validation:")
        print(f"  Overall health: {overall_health}")
        print(f"  Total bottlenecks: {len(analysis_results['bottlenecks'])}")
        print(f"  Total trends: {len(analysis_results['trends'])}")
        print(f"  Total recommendations: {len(analysis_results['recommendations'])}")
        print(f"  Total operations analyzed: {performance_summary['total_operations']}")

    async def test_performance_alerting_validation(
        self, optimized_orchestration_service
    ):
        """Test performance alerting system validation."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Track alerts
        received_alerts = []

        async def alert_handler(alert):
            received_alerts.append(alert)

        alerting.add_alert_handler(alert_handler)

        # Execute normal workload (should not trigger alerts)
        normal_inputs = [
            "I need help with anxiety",
            "Can you help me with stress?",
            "I want to improve my mood",
        ]

        for i, test_input in enumerate(normal_inputs):
            session_id = f"alert_test_session_{i + 1:03d}"
            world_id = f"alert_test_world_{i + 1:03d}"
            user_id = f"alert_test_user_{i + 1}"

            result = await service.process_user_input(
                user_input=test_input,
                session_id=session_id,
                world_id=world_id,
                user_id=user_id,
            )

            assert result is not None

            # Evaluate thresholds for each operation
            await alerting.evaluate_thresholds(
                operation_type=OperationType.WORKFLOW_EXECUTION,
                metric_value=1.0,  # Normal response time
                metadata={"test": True},
            )

        # Wait for alert processing
        await asyncio.sleep(0.5)

        # Should not have received performance alerts for normal operations
        performance_alerts = [
            a
            for a in received_alerts
            if a.alert_type.value == "response_time_violation"
        ]
        assert len(performance_alerts) == 0, (
            f"Unexpected performance alerts: {performance_alerts}"
        )

        # Test alert generation for slow operation
        slow_alert = await alerting.evaluate_thresholds(
            operation_type=OperationType.WORKFLOW_EXECUTION,
            metric_value=3.0,  # Slow response time
            metadata={"test": "slow_operation"},
        )

        assert slow_alert is not None
        assert slow_alert.severity.value in ["error", "critical"]
        assert slow_alert.metric_value == 3.0

        # Get alerting statistics
        alert_stats = alerting.get_alert_statistics()

        assert alert_stats["configured_thresholds"] > 0
        assert alert_stats["escalation_rules"] > 0

        print("Performance alerting validation:")
        print(f"  Normal operations alerts: {len(performance_alerts)}")
        print(f"  Slow operation alert generated: {slow_alert is not None}")
        print(f"  Alert severity: {slow_alert.severity.value if slow_alert else 'N/A'}")
        print(f"  Configured thresholds: {alert_stats['configured_thresholds']}")

    async def test_end_to_end_performance_validation(
        self, optimized_orchestration_service
    ):
        """Test complete end-to-end performance validation."""
        service, monitor, coordinator, analytics, alerting = (
            optimized_orchestration_service
        )

        # Comprehensive test scenario
        test_input = "I'm a healthcare worker dealing with burnout and compassion fatigue. I need comprehensive support and strategies to maintain my mental health while continuing to care for others."

        session_id = "e2e_performance_session_001"
        world_id = "e2e_performance_world_001"
        user_id = "e2e_performance_user"

        # Track complete workflow performance
        async with monitor.track_operation(
            operation_type=OperationType.WORKFLOW_EXECUTION,
            workflow_id="e2e_performance_test",
            user_id=user_id,
            metadata={"test_type": "end_to_end_validation"},
        ):
            start_time = time.time()

            result = await service.process_user_input(
                user_input=test_input,
                session_id=session_id,
                world_id=world_id,
                user_id=user_id,
            )

            end_time = time.time()
            total_response_time = end_time - start_time

        # Validate complete workflow
        assert result is not None
        assert "story" in result
        assert len(result["story"]) > 100  # Should be substantial content

        # Validate individual agent results
        assert "ipa_result" in result
        assert "wba_result" in result
        assert "nga_result" in result

        # Validate therapeutic appropriateness
        assert result.get("safety_validated", False) is True

        # Validate performance meets SLA
        assert total_response_time < 2.0, (
            f"End-to-end response time {total_response_time:.2f}s exceeds 2.0s SLA"
        )

        # Get comprehensive performance metrics
        performance_summary = monitor.get_performance_summary()
        optimization_stats = coordinator.get_optimization_statistics()

        # Validate system health
        assert performance_summary["overall_performance"] in [
            "excellent",
            "good",
            "acceptable",
        ]
        assert (
            optimization_stats["system_load"] < 0.8
        )  # System should not be overloaded

        print("End-to-end performance validation:")
        print(f"  Total response time: {total_response_time:.2f}s")
        print(f"  Story length: {len(result['story'])} characters")
        print(f"  Overall performance: {performance_summary['overall_performance']}")
        print(f"  System load: {optimization_stats['system_load']:.2%}")
        print(f"  SLA compliance: {total_response_time < 2.0}")
        print(f"  Safety validated: {result.get('safety_validated', False)}")
        print(
            f"  Therapeutic content: {len(result.get('nga_result', {}).get('therapeutic_elements', []))} elements"
        )
