"""
Performance benchmarks for real agent communication.

This module tests performance characteristics of real agent communication,
including latency, throughput, and resource usage under various load conditions.
"""

import asyncio
import statistics
import time
from dataclasses import dataclass
from typing import Any

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.enhanced_coordinator import EnhancedRedisMessageCoordinator


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent communication."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    average_latency: float
    median_latency: float
    p95_latency: float
    p99_latency: float
    throughput_rps: float
    error_rate: float


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.performance
class TestRealAgentPerformance:
    """Performance benchmarks for real agent communication."""

    @pytest_asyncio.fixture
    async def performance_coordinator(self, redis_client):
        """Create coordinator optimized for performance testing."""
        return EnhancedRedisMessageCoordinator(
            redis=redis_client,
            key_prefix="perf_test",
            enable_real_agents=True,
            fallback_to_mock=True,
            retry_attempts=3,
            backoff_base=0.5,
        )

    @pytest_asyncio.fixture
    async def performance_proxies(self, performance_coordinator):
        """Create proxies for performance testing."""
        return {
            "ipa": InputProcessorAgentProxy(
                coordinator=performance_coordinator,
                instance="perf_ipa",
                enable_real_agent=True,
                fallback_to_mock=True,
                default_timeout_s=10.0,
            ),
            "wba": WorldBuilderAgentProxy(
                coordinator=performance_coordinator,
                instance="perf_wba",
                enable_real_agent=True,
                fallback_to_mock=True,
                default_timeout_s=15.0,
            ),
            "nga": NarrativeGeneratorAgentProxy(
                coordinator=performance_coordinator,
                instance="perf_nga",
                enable_real_agent=True,
                fallback_to_mock=True,
                default_timeout_s=20.0,
            ),
        }

    async def measure_single_agent_latency(
        self, proxy, test_input: dict[str, Any], num_requests: int = 100
    ) -> PerformanceMetrics:
        """Measure latency for a single agent type."""
        latencies = []
        successful = 0
        failed = 0

        start_time = time.time()

        for _ in range(num_requests):
            request_start = time.time()

            try:
                _result = await proxy.process(test_input)
                request_end = time.time()

                latency = (
                    request_end - request_start
                ) * 1000  # Convert to milliseconds
                latencies.append(latency)
                successful += 1

            except Exception:
                request_end = time.time()
                latency = (request_end - request_start) * 1000
                latencies.append(latency)
                failed += 1

        end_time = time.time()
        total_time = end_time - start_time

        return PerformanceMetrics(
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            average_latency=statistics.mean(latencies) if latencies else 0,
            median_latency=statistics.median(latencies) if latencies else 0,
            p95_latency=(
                statistics.quantiles(latencies, n=20)[18]
                if len(latencies) >= 20
                else max(latencies)
                if latencies
                else 0
            ),
            p99_latency=(
                statistics.quantiles(latencies, n=100)[98]
                if len(latencies) >= 100
                else max(latencies)
                if latencies
                else 0
            ),
            throughput_rps=num_requests / total_time if total_time > 0 else 0,
            error_rate=failed / num_requests if num_requests > 0 else 0,
        )

    async def test_ipa_latency_benchmark(self, performance_proxies):
        """Benchmark IPA latency performance."""
        ipa_proxy = performance_proxies["ipa"]
        test_input = {"text": "explore the mysterious ancient temple"}

        metrics = await self.measure_single_agent_latency(
            ipa_proxy, test_input, num_requests=50
        )

        # Performance assertions
        assert metrics.error_rate < 0.1, f"Error rate too high: {metrics.error_rate}"
        assert metrics.average_latency < 5000, (
            f"Average latency too high: {metrics.average_latency}ms"
        )
        assert metrics.throughput_rps > 1, (
            f"Throughput too low: {metrics.throughput_rps} RPS"
        )

        return metrics

    async def test_wba_latency_benchmark(self, performance_proxies):
        """Benchmark WBA latency performance."""
        wba_proxy = performance_proxies["wba"]
        test_input = {"world_id": "perf_test_world", "updates": {"location": "temple"}}

        metrics = await self.measure_single_agent_latency(
            wba_proxy, test_input, num_requests=50
        )

        # Performance assertions
        assert metrics.error_rate < 0.1, f"Error rate too high: {metrics.error_rate}"
        assert metrics.average_latency < 8000, (
            f"Average latency too high: {metrics.average_latency}ms"
        )
        assert metrics.throughput_rps > 0.5, (
            f"Throughput too low: {metrics.throughput_rps} RPS"
        )

        return metrics

    async def test_nga_latency_benchmark(self, performance_proxies):
        """Benchmark NGA latency performance."""
        nga_proxy = performance_proxies["nga"]
        test_input = {
            "prompt": "Generate a story about exploring an ancient temple",
            "context": {
                "session_id": "perf_test",
                "world_state": {"location": "temple"},
            },
        }

        metrics = await self.measure_single_agent_latency(
            nga_proxy, test_input, num_requests=30
        )

        # Performance assertions (NGA typically slower due to content generation)
        assert metrics.error_rate < 0.15, f"Error rate too high: {metrics.error_rate}"
        assert metrics.average_latency < 15000, (
            f"Average latency too high: {metrics.average_latency}ms"
        )
        assert metrics.throughput_rps > 0.2, (
            f"Throughput too low: {metrics.throughput_rps} RPS"
        )

        return metrics

    async def test_concurrent_throughput_benchmark(self, performance_proxies):
        """Benchmark concurrent throughput across all agent types."""
        concurrency_levels = [1, 5, 10, 20]
        throughput_results = {}

        for concurrency in concurrency_levels:

            async def concurrent_workflow(worker_id: int):
                """Execute a complete workflow concurrently."""
                session_id = f"throughput_test_{worker_id}"

                # IPA processing
                ipa_start = time.time()
                _ipa_result = await performance_proxies["ipa"].process(
                    {"text": f"worker {worker_id} explores the dungeon"}
                )
                ipa_time = time.time() - ipa_start

                # WBA processing
                wba_start = time.time()
                wba_result = await performance_proxies["wba"].process(
                    {
                        "world_id": session_id,
                        "updates": {"worker_id": worker_id, "location": "dungeon"},
                    }
                )
                wba_time = time.time() - wba_start

                # NGA processing
                nga_start = time.time()
                _nga_result = await performance_proxies["nga"].process(
                    {
                        "prompt": f"Worker {worker_id} story in dungeon",
                        "context": {
                            "session_id": session_id,
                            "world_state": wba_result["world_state"],
                        },
                    }
                )
                nga_time = time.time() - nga_start

                return {
                    "worker_id": worker_id,
                    "ipa_time": ipa_time,
                    "wba_time": wba_time,
                    "nga_time": nga_time,
                    "total_time": ipa_time + wba_time + nga_time,
                    "success": True,
                }

            # Run concurrent workflows
            start_time = time.time()
            tasks = [concurrent_workflow(i) for i in range(concurrency)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            # Analyze results
            successful_results = [
                r for r in results if isinstance(r, dict) and r.get("success")
            ]
            total_time = end_time - start_time

            throughput_results[concurrency] = {
                "concurrency": concurrency,
                "successful_workflows": len(successful_results),
                "total_time": total_time,
                "workflows_per_second": (
                    len(successful_results) / total_time if total_time > 0 else 0
                ),
                "average_workflow_time": (
                    statistics.mean([r["total_time"] for r in successful_results])
                    if successful_results
                    else 0
                ),
                "average_ipa_time": (
                    statistics.mean([r["ipa_time"] for r in successful_results])
                    if successful_results
                    else 0
                ),
                "average_wba_time": (
                    statistics.mean([r["wba_time"] for r in successful_results])
                    if successful_results
                    else 0
                ),
                "average_nga_time": (
                    statistics.mean([r["nga_time"] for r in successful_results])
                    if successful_results
                    else 0
                ),
            }

        # Verify throughput scaling
        for concurrency, result in throughput_results.items():
            assert result["workflows_per_second"] > 0, (
                f"No throughput at concurrency {concurrency}"
            )
            assert result["successful_workflows"] == concurrency, (
                f"Not all workflows succeeded at concurrency {concurrency}"
            )

        return throughput_results

    async def test_sustained_load_benchmark(self, performance_proxies):
        """Test performance under sustained load."""
        duration_seconds = 30  # 30-second sustained load test
        target_rps = 2  # Target 2 requests per second

        ipa_proxy = performance_proxies["ipa"]
        request_count = 0
        successful_count = 0
        latencies = []

        start_time = time.time()
        end_time = start_time + duration_seconds

        async def sustained_requester():
            """Generate sustained requests."""
            nonlocal request_count, successful_count

            while time.time() < end_time:
                request_start = time.time()

                try:
                    _result = await ipa_proxy.process(
                        {"text": f"sustained load test request {request_count}"}
                    )
                    request_end = time.time()

                    latency = (request_end - request_start) * 1000
                    latencies.append(latency)
                    successful_count += 1

                except Exception:
                    pass  # Count as failed request

                request_count += 1

                # Rate limiting to achieve target RPS
                await asyncio.sleep(1.0 / target_rps)

        # Run sustained load
        await sustained_requester()

        actual_duration = time.time() - start_time
        actual_rps = request_count / actual_duration
        success_rate = successful_count / request_count if request_count > 0 else 0

        # Performance assertions for sustained load
        assert success_rate > 0.8, (
            f"Success rate too low under sustained load: {success_rate}"
        )
        assert actual_rps >= target_rps * 0.8, (
            f"Actual RPS too low: {actual_rps} (target: {target_rps})"
        )

        if latencies:
            avg_latency = statistics.mean(latencies)
            assert avg_latency < 10000, (
                f"Average latency too high under sustained load: {avg_latency}ms"
            )

        return {
            "duration": actual_duration,
            "total_requests": request_count,
            "successful_requests": successful_count,
            "success_rate": success_rate,
            "actual_rps": actual_rps,
            "target_rps": target_rps,
            "average_latency": statistics.mean(latencies) if latencies else 0,
            "p95_latency": (
                statistics.quantiles(latencies, n=20)[18]
                if len(latencies) >= 20
                else max(latencies)
                if latencies
                else 0
            ),
        }

    async def test_memory_usage_benchmark(self, performance_proxies):
        """Test memory usage during agent operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Baseline memory usage
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform intensive operations
        num_operations = 100
        for i in range(num_operations):
            # Create multiple concurrent operations
            tasks = [
                performance_proxies["ipa"].process({"text": f"memory test {i}"}),
                performance_proxies["wba"].process({"world_id": f"mem_test_{i}"}),
                performance_proxies["nga"].process(
                    {
                        "prompt": f"memory test story {i}",
                        "context": {"session_id": f"mem_test_{i}"},
                    }
                ),
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory every 10 operations
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - baseline_memory

                # Memory should not grow excessively
                assert memory_increase < 500, (
                    f"Memory usage increased too much: {memory_increase}MB"
                )

        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_increase = final_memory - baseline_memory

        return {
            "baseline_memory_mb": baseline_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": total_memory_increase,
            "operations_performed": num_operations,
            "memory_per_operation_kb": (
                (total_memory_increase * 1024) / num_operations
                if num_operations > 0
                else 0
            ),
        }
