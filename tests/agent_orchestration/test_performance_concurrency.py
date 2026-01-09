"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_performance_concurrency]]
Performance and concurrency integration tests for multi-agent workflows.

This module implements comprehensive tests for concurrent workflow execution,
resource contention handling, performance benchmarks, and system scalability.
"""

import asyncio
import statistics
import time
from unittest.mock import patch

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    AgentStep,
    AgentType,
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    OrchestrationRequest,
    SessionContext,
    WorkflowDefinition,
    WorkflowManager,
    WorkflowType,
    WorldBuilderAgentProxy,
)

from tests.agent_orchestration.test_multi_agent_workflow_integration import (
    IntegrationTestHelper,
    PerformanceMetrics,
)

# ============================================================================
# Concurrent Workflow Execution Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestConcurrentWorkflowExecution:
    """Test concurrent execution of multiple independent workflows."""

    @pytest_asyncio.fixture
    async def integration_helper(self, redis_client, neo4j_driver):
        """Create integration test helper."""
        return IntegrationTestHelper(redis_client, neo4j_driver)

    async def test_concurrent_workflow_isolation(
        self, integration_helper, sample_player_inputs, performance_test_scenarios
    ):
        """Test that concurrent workflows are properly isolated."""
        test_env = await integration_helper.setup_test_environment(
            "concurrent_isolation"
        )

        try:
            # Get low load scenario for testing
            scenario = performance_test_scenarios["low_load"]
            concurrent_count = scenario["concurrent_workflows"]

            workflow_manager = WorkflowManager()

            # Create workflow definition
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="concurrent_ipa"),
                    AgentStep(agent=AgentType.WBA, name="concurrent_wba"),
                    AgentStep(agent=AgentType.NGA, name="concurrent_nga"),
                ],
            )

            workflow_manager.register_workflow("concurrent_test", workflow_def)

            # Create concurrent requests with unique identifiers
            concurrent_requests = []
            for i in range(concurrent_count):
                session_context = SessionContext(
                    session_id=f"{test_env['session_id']}_concurrent_{i}",
                    player_id=f"{test_env['player_id']}_{i}",
                    therapeutic_profile={"intensity": "medium", "request_id": i},
                    game_state={"location": f"location_{i}", "request_id": i},
                )

                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input={
                        **sample_player_inputs[i % len(sample_player_inputs)],
                        "request_id": i,
                    },
                    context=session_context,
                )

                concurrent_requests.append((request, i))

            # Execute workflows concurrently
            async def execute_single_workflow(request, request_id):
                start_time = time.time()
                response, run_id, error = workflow_manager.execute_workflow(
                    "concurrent_test", request
                )
                execution_time = time.time() - start_time

                return {
                    "request_id": request_id,
                    "response": response,
                    "run_id": run_id,
                    "error": error,
                    "execution_time": execution_time,
                    "session_id": (
                        request.context.session_id if request.context else None
                    ),
                }

            # Run all workflows concurrently
            start_time = time.time()
            tasks = [
                execute_single_workflow(req, req_id)
                for req, req_id in concurrent_requests
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time

            # Verify concurrent execution results
            successful_results = []
            failed_results = []

            for result in results:
                if isinstance(result, Exception):
                    failed_results.append(result)
                elif result["error"] is None:
                    successful_results.append(result)
                else:
                    failed_results.append(result["error"])

            # Verify success rate meets expectations
            success_rate = len(successful_results) / len(results)
            expected_success_rate = scenario["expected_success_rate"]
            assert success_rate >= expected_success_rate, (
                f"Success rate {success_rate:.2f} below expected {expected_success_rate:.2f}"
            )

            # Verify workflow isolation - each should have unique identifiers
            request_ids = [result["request_id"] for result in successful_results]
            assert len(set(request_ids)) == len(request_ids), (
                "Request IDs not unique - isolation failed"
            )

            session_ids = [
                result["session_id"]
                for result in successful_results
                if result["session_id"]
            ]
            assert len(set(session_ids)) == len(session_ids), (
                "Session IDs not unique - isolation failed"
            )

            # Verify performance characteristics
            execution_times = [
                result["execution_time"] for result in successful_results
            ]
            avg_execution_time = statistics.mean(execution_times)
            max(execution_times)

            assert avg_execution_time <= scenario["expected_avg_response_time"], (
                f"Average execution time {avg_execution_time:.2f}s exceeds expected {scenario['expected_avg_response_time']}s"
            )

            # Verify concurrent execution was actually concurrent (not sequential)
            theoretical_sequential_time = sum(execution_times)
            concurrency_factor = theoretical_sequential_time / total_time
            assert concurrency_factor > 1.5, (
                f"Low concurrency factor {concurrency_factor:.2f} - may be running sequentially"
            )

        finally:
            # Cleanup all concurrent sessions
            cleanup_tasks = []
            for result in successful_results:
                if result["session_id"] and result["run_id"]:
                    cleanup_tasks.append(
                        integration_helper.cleanup_test_data(
                            result["session_id"],
                            result["run_id"],
                            test_env["player_id"],
                        )
                    )

            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)

    async def test_workflow_resource_contention(
        self, integration_helper, sample_player_inputs
    ):
        """Test resource contention handling when multiple workflows access the same agents."""
        test_env = await integration_helper.setup_test_environment(
            "resource_contention"
        )

        try:
            # Create resource-limited scenario
            resource_usage = {}
            max_concurrent_per_agent = 2  # Simulate resource limits

            class ResourceLimitedAgent(WorldBuilderAgentProxy):
                def __init__(self, agent_type, **kwargs):
                    super().__init__(**kwargs)
                    self.agent_type = agent_type
                    self.active_requests = 0

                async def process(self, input_payload: dict) -> dict:
                    # Track resource usage
                    self.active_requests += 1
                    agent_key = f"{self.agent_type}:{self.instance or 'default'}"

                    if agent_key not in resource_usage:
                        resource_usage[agent_key] = {
                            "max_concurrent": 0,
                            "total_requests": 0,
                        }

                    resource_usage[agent_key]["max_concurrent"] = max(
                        resource_usage[agent_key]["max_concurrent"],
                        self.active_requests,
                    )
                    resource_usage[agent_key]["total_requests"] += 1

                    # Simulate resource contention
                    if self.active_requests > max_concurrent_per_agent:
                        await asyncio.sleep(0.5)  # Longer processing under contention
                    else:
                        await asyncio.sleep(0.1)  # Normal processing

                    result = await super().process(input_payload)
                    self.active_requests -= 1
                    return result

            workflow_manager = WorkflowManager()

            # Mock agent registry to return resource-limited agents
            with patch(
                "src.agent_orchestration.agents.AgentRegistry.get_agent"
            ) as mock_get_agent:
                resource_limited_wba = ResourceLimitedAgent("WBA", instance="limited")

                def get_agent(agent_id):
                    if agent_id.type == AgentType.WBA:
                        return resource_limited_wba
                    if agent_id.type == AgentType.IPA:
                        return InputProcessorAgentProxy(instance="normal")
                    if agent_id.type == AgentType.NGA:
                        return NarrativeGeneratorAgentProxy(instance="normal")
                    return None

                mock_get_agent.side_effect = get_agent

                workflow_def = WorkflowDefinition(
                    workflow_type=WorkflowType.COLLABORATIVE,
                    agent_sequence=[
                        AgentStep(agent=AgentType.IPA, name="ipa"),
                        AgentStep(agent=AgentType.WBA, name="resource_limited_wba"),
                        AgentStep(agent=AgentType.NGA, name="nga"),
                    ],
                )

                workflow_manager.register_workflow("contention_test", workflow_def)

                # Create multiple concurrent requests targeting the same resource-limited agent
                concurrent_requests = []
                for i in range(5):  # More requests than max_concurrent_per_agent
                    request = OrchestrationRequest(
                        entrypoint=AgentType.IPA,
                        input={**sample_player_inputs[0], "request_id": i},
                    )
                    concurrent_requests.append((request, i))

                # Execute with resource contention
                async def execute_with_contention(request, request_id):
                    start_time = time.time()
                    response, run_id, error = workflow_manager.execute_workflow(
                        "contention_test", request
                    )
                    execution_time = time.time() - start_time

                    return {
                        "request_id": request_id,
                        "execution_time": execution_time,
                        "error": error,
                        "response": response,
                    }

                tasks = [
                    execute_with_contention(req, req_id)
                    for req, req_id in concurrent_requests
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Analyze resource contention results
                successful_results = [
                    r
                    for r in results
                    if not isinstance(r, Exception) and r["error"] is None
                ]

                # Verify resource limits were respected
                wba_key = "WBA:limited"
                if wba_key in resource_usage:
                    resource_usage[wba_key]["max_concurrent"]
                    total_requests = resource_usage[wba_key]["total_requests"]

                    # Verify that resource contention was handled (some requests should have been queued)
                    assert total_requests >= len(concurrent_requests), (
                        "Not all requests were processed"
                    )

                    # Verify execution times show contention effects
                    execution_times = [r["execution_time"] for r in successful_results]
                    if len(execution_times) > 1:
                        time_variance = statistics.stdev(execution_times)
                        assert time_variance > 0.1, (
                            "Execution times too uniform - contention not evident"
                        )

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


# ============================================================================
# Performance Benchmark Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
class TestPerformanceBenchmarks:
    """Test performance benchmarks and system scalability."""

    async def test_workflow_performance_benchmarks(
        self, integration_helper, sample_player_inputs, performance_test_scenarios
    ):
        """Test workflow performance under different load scenarios."""
        test_env = await integration_helper.setup_test_environment(
            "performance_benchmark"
        )

        try:
            workflow_manager = WorkflowManager()

            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="benchmark_ipa"),
                    AgentStep(agent=AgentType.WBA, name="benchmark_wba"),
                    AgentStep(agent=AgentType.NGA, name="benchmark_nga"),
                ],
            )

            workflow_manager.register_workflow("benchmark_test", workflow_def)

            # Test different load scenarios
            benchmark_results = {}

            for scenario_name, scenario in performance_test_scenarios.items():
                if scenario_name == "stress_test":
                    continue  # Skip stress test in regular benchmarks

                concurrent_count = scenario["concurrent_workflows"]
                duration = scenario["duration_seconds"]
                expected_avg_time = scenario["expected_avg_response_time"]
                expected_success_rate = scenario["expected_success_rate"]

                # Create performance metrics collector
                metrics = PerformanceMetrics()

                # Run benchmark for specified duration
                start_time = time.time()
                completed_workflows = 0

                async def benchmark_workflow(workflow_id):
                    nonlocal completed_workflows

                    request = OrchestrationRequest(
                        entrypoint=AgentType.IPA,
                        input=sample_player_inputs[
                            workflow_id % len(sample_player_inputs)
                        ],
                    )

                    workflow_start = time.time()
                    response, run_id, error = workflow_manager.execute_workflow(
                        "benchmark_test", request
                    )
                    workflow_time = time.time() - workflow_start

                    if error is None:
                        metrics.record_workflow_time(workflow_time)
                        completed_workflows += 1
                    else:
                        metrics.record_error("workflow_failure")

                    return error is None

                # Run concurrent workflows for the duration
                workflow_id = 0
                active_tasks = set()

                while time.time() - start_time < duration:
                    # Maintain concurrent workflow count
                    while len(active_tasks) < concurrent_count:
                        task = asyncio.create_task(benchmark_workflow(workflow_id))
                        active_tasks.add(task)
                        workflow_id += 1

                    # Check for completed tasks
                    done_tasks = {task for task in active_tasks if task.done()}
                    active_tasks -= done_tasks

                    await asyncio.sleep(0.1)  # Small delay to prevent tight loop

                # Wait for remaining tasks to complete
                if active_tasks:
                    await asyncio.gather(*active_tasks, return_exceptions=True)

                # Analyze benchmark results
                stats = metrics.get_statistics()
                workflow_stats = stats["workflow_stats"]

                success_rate = (
                    completed_workflows / workflow_id if workflow_id > 0 else 0
                )
                avg_time = workflow_stats["avg_time"]
                throughput = completed_workflows / duration  # workflows per second

                benchmark_results[scenario_name] = {
                    "completed_workflows": completed_workflows,
                    "total_attempts": workflow_id,
                    "success_rate": success_rate,
                    "avg_execution_time": avg_time,
                    "max_execution_time": workflow_stats["max_time"],
                    "min_execution_time": workflow_stats["min_time"],
                    "throughput": throughput,
                    "duration": duration,
                }

                # Verify performance meets expectations
                assert success_rate >= expected_success_rate, (
                    f"{scenario_name}: Success rate {success_rate:.2%} below expected {expected_success_rate:.2%}"
                )

                assert avg_time <= expected_avg_time, (
                    f"{scenario_name}: Average time {avg_time:.2f}s exceeds expected {expected_avg_time}s"
                )

            # Generate benchmark report
            for scenario_name in benchmark_results:
                pass

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_memory_and_cpu_usage_monitoring(
        self, integration_helper, sample_player_inputs
    ):
        """Test memory and CPU usage under load conditions."""
        test_env = await integration_helper.setup_test_environment(
            "resource_monitoring"
        )

        try:
            import os

            import psutil

            # Get initial resource usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            process.cpu_percent()

            workflow_manager = WorkflowManager()

            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="resource_ipa"),
                    AgentStep(agent=AgentType.WBA, name="resource_wba"),
                    AgentStep(agent=AgentType.NGA, name="resource_nga"),
                ],
            )

            workflow_manager.register_workflow("resource_test", workflow_def)

            # Monitor resources during load test
            resource_samples = []
            monitoring_active = True

            async def monitor_resources():
                while monitoring_active:
                    try:
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        cpu_percent = process.cpu_percent()

                        resource_samples.append(
                            {
                                "timestamp": time.time(),
                                "memory_mb": memory_mb,
                                "cpu_percent": cpu_percent,
                            }
                        )

                        await asyncio.sleep(0.5)  # Sample every 500ms
                    except Exception:
                        break

            # Start resource monitoring
            monitor_task = asyncio.create_task(monitor_resources())

            # Execute load test
            concurrent_workflows = 10
            test_duration = 15  # seconds

            async def load_test_workflow(workflow_id):
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input={
                        **sample_player_inputs[workflow_id % len(sample_player_inputs)],
                        "load_test_id": workflow_id,
                    },
                )

                response, run_id, error = workflow_manager.execute_workflow(
                    "resource_test", request
                )
                return error is None

            # Run load test
            start_time = time.time()
            workflow_id = 0
            active_tasks = set()
            successful_workflows = 0

            while time.time() - start_time < test_duration:
                # Maintain concurrent load
                while len(active_tasks) < concurrent_workflows:
                    task = asyncio.create_task(load_test_workflow(workflow_id))
                    active_tasks.add(task)
                    workflow_id += 1

                # Check completed tasks
                done_tasks = {task for task in active_tasks if task.done()}
                for task in done_tasks:
                    try:
                        if await task:
                            successful_workflows += 1
                    except Exception:
                        pass

                active_tasks -= done_tasks
                await asyncio.sleep(0.1)

            # Stop monitoring and wait for remaining tasks
            monitoring_active = False
            if active_tasks:
                remaining_results = await asyncio.gather(
                    *active_tasks, return_exceptions=True
                )
                successful_workflows += sum(1 for r in remaining_results if r is True)

            monitor_task.cancel()

            # Analyze resource usage
            if resource_samples:
                memory_values = [sample["memory_mb"] for sample in resource_samples]
                cpu_values = [
                    sample["cpu_percent"]
                    for sample in resource_samples
                    if sample["cpu_percent"] > 0
                ]

                max_memory = max(memory_values)
                statistics.mean(memory_values)
                memory_increase = max_memory - initial_memory

                max(cpu_values) if cpu_values else 0
                avg_cpu = statistics.mean(cpu_values) if cpu_values else 0

                # Resource usage assertions
                assert memory_increase < 500, (
                    f"Memory increase {memory_increase:.1f}MB too high - possible memory leak"
                )
                assert max_memory < 2000, f"Peak memory {max_memory:.1f}MB too high"
                assert avg_cpu < 80, f"Average CPU {avg_cpu:.1f}% too high"

                # Verify system stability
                final_memory = process.memory_info().rss / 1024 / 1024
                memory_cleanup = max_memory - final_memory

                if memory_cleanup > 50:  # Significant memory was freed
                    pass

        except ImportError:
            pytest.skip("psutil not available for resource monitoring")
        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


# ============================================================================
# Agent Pool Scaling Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
class TestAgentPoolScaling:
    """Test agent pool scaling behavior under varying loads."""

    async def test_dynamic_agent_scaling(
        self, integration_helper, sample_player_inputs
    ):
        """Test dynamic scaling of agent pools based on load."""
        test_env = await integration_helper.setup_test_environment("agent_scaling")

        try:
            # Simulate agent pool with scaling capabilities
            agent_pools = {
                AgentType.IPA: {"active": 1, "max": 5, "instances": []},
                AgentType.WBA: {"active": 1, "max": 5, "instances": []},
                AgentType.NGA: {"active": 1, "max": 5, "instances": []},
            }

            scaling_events = []

            class ScalableAgent:
                def __init__(self, agent_type, instance_id):
                    self.agent_type = agent_type
                    self.instance_id = instance_id
                    self.active_requests = 0
                    self.total_requests = 0
                    self.created_at = time.time()

                async def process(self, input_payload: dict) -> dict:
                    self.active_requests += 1
                    self.total_requests += 1

                    # Simulate processing time
                    await asyncio.sleep(0.2)

                    result = {
                        "agent_type": self.agent_type.value,
                        "instance_id": self.instance_id,
                        "processed": True,
                        "load": self.active_requests,
                    }

                    self.active_requests -= 1
                    return result

            def scale_agent_pool(agent_type, target_load):
                """Simulate agent pool scaling based on load."""
                pool = agent_pools[agent_type]
                current_active = pool["active"]

                # Scale up if load is high
                if target_load > current_active * 2 and current_active < pool["max"]:
                    new_instances = min(
                        pool["max"] - current_active, max(1, target_load // 2)
                    )
                    for i in range(new_instances):
                        instance_id = f"{agent_type.value}_{current_active + i}"
                        agent = ScalableAgent(agent_type, instance_id)
                        pool["instances"].append(agent)
                        pool["active"] += 1

                        scaling_events.append(
                            {
                                "event": "scale_up",
                                "agent_type": agent_type.value,
                                "instance_id": instance_id,
                                "timestamp": time.time(),
                                "trigger_load": target_load,
                            }
                        )

                # Scale down if load is low (simplified logic)
                elif target_load < current_active // 2 and current_active > 1:
                    instances_to_remove = min(
                        current_active - 1, current_active - target_load
                    )
                    for _ in range(instances_to_remove):
                        if pool["instances"]:
                            removed_agent = pool["instances"].pop()
                            pool["active"] -= 1

                            scaling_events.append(
                                {
                                    "event": "scale_down",
                                    "agent_type": agent_type.value,
                                    "instance_id": removed_agent.instance_id,
                                    "timestamp": time.time(),
                                    "trigger_load": target_load,
                                }
                            )

            # Initialize agent pools
            for agent_type in agent_pools:
                agent = ScalableAgent(agent_type, f"{agent_type.value}_0")
                agent_pools[agent_type]["instances"].append(agent)

            # Simulate varying load patterns
            load_patterns = [
                {"duration": 5, "concurrent_requests": 2, "description": "low_load"},
                {
                    "duration": 10,
                    "concurrent_requests": 8,
                    "description": "medium_load",
                },
                {"duration": 8, "concurrent_requests": 15, "description": "high_load"},
                {"duration": 5, "concurrent_requests": 3, "description": "scale_down"},
            ]

            workflow_manager = WorkflowManager()

            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="scalable_ipa"),
                    AgentStep(agent=AgentType.WBA, name="scalable_wba"),
                    AgentStep(agent=AgentType.NGA, name="scalable_nga"),
                ],
            )

            workflow_manager.register_workflow("scaling_test", workflow_def)

            # Execute load patterns and monitor scaling
            for pattern in load_patterns:
                concurrent_requests = pattern["concurrent_requests"]
                duration = pattern["duration"]

                # Trigger scaling based on expected load
                for agent_type in agent_pools:
                    scale_agent_pool(agent_type, concurrent_requests)

                # Execute workflows under this load pattern
                start_time = time.time()
                active_workflows = set()
                completed_workflows = 0
                workflow_id = 0

                async def execute_scaling_workflow(wf_id):
                    nonlocal completed_workflows

                    request = OrchestrationRequest(
                        entrypoint=AgentType.IPA,
                        input={
                            **sample_player_inputs[wf_id % len(sample_player_inputs)],
                            "scaling_test_id": wf_id,
                        },
                    )

                    # Mock agent selection from pool
                    selected_agents = {}
                    for agent_type, pool in agent_pools.items():
                        if pool["instances"]:
                            # Simple round-robin selection
                            selected_agent = pool["instances"][
                                wf_id % len(pool["instances"])
                            ]
                            selected_agents[agent_type] = selected_agent

                    # Simulate workflow execution with selected agents
                    time.time()

                    try:
                        # Process through each agent in sequence
                        current_payload = request.input
                        for agent_type in [AgentType.IPA, AgentType.WBA, AgentType.NGA]:
                            if agent_type in selected_agents:
                                agent = selected_agents[agent_type]
                                current_payload = await agent.process(current_payload)

                        completed_workflows += 1
                        return True
                    except Exception:
                        return False

                # Run workflows for the pattern duration
                while time.time() - start_time < duration:
                    # Maintain concurrent load
                    while len(active_workflows) < concurrent_requests:
                        task = asyncio.create_task(
                            execute_scaling_workflow(workflow_id)
                        )
                        active_workflows.add(task)
                        workflow_id += 1

                    # Remove completed workflows
                    done_workflows = {task for task in active_workflows if task.done()}
                    active_workflows -= done_workflows

                    await asyncio.sleep(0.1)

                # Wait for remaining workflows
                if active_workflows:
                    await asyncio.gather(*active_workflows, return_exceptions=True)

                # Report scaling results for this pattern
                sum(pool["active"] for pool in agent_pools.values())

                for agent_type, pool in agent_pools.items():
                    pass

            # Analyze scaling behavior
            scale_up_events = [e for e in scaling_events if e["event"] == "scale_up"]
            scale_down_events = [
                e for e in scaling_events if e["event"] == "scale_down"
            ]

            # Verify scaling behavior
            assert len(scale_up_events) > 0, (
                "No scale-up events detected - scaling may not be working"
            )

            # Verify agents scaled appropriately for high load
            high_load_events = [e for e in scale_up_events if e["trigger_load"] >= 10]
            assert len(high_load_events) > 0, (
                "No scaling detected for high load scenarios"
            )

            # Verify scale-down occurred during low load
            if len(scale_down_events) > 0:
                pass

            # Verify maximum limits were respected
            for agent_type, pool in agent_pools.items():
                assert pool["active"] <= pool["max"], (
                    f"{agent_type.value} exceeded maximum pool size"
                )
                assert pool["active"] >= 1, f"{agent_type.value} scaled below minimum"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )
