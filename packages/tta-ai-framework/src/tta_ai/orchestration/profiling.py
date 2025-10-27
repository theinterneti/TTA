"""
Performance profiling utilities for agent coordination.

This module provides profiling and monitoring capabilities to analyze
agent coordination overhead under various load conditions.
"""

from __future__ import annotations

import asyncio
import cProfile
import io
import logging
import pstats
import threading
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ProfileResult:
    """Result of a profiling session."""

    duration: float
    function_calls: int
    primitive_calls: int
    total_time: float
    cumulative_time: float
    top_functions: list[dict[str, Any]] = field(default_factory=list)
    memory_usage: dict[str, float] | None = None


@dataclass
class ConcurrencyMetrics:
    """Metrics for concurrent agent coordination."""

    concurrent_requests: int
    total_duration: float
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    coordination_overhead: float
    memory_peak_mb: float


class AgentCoordinationProfiler:
    """Profiler for agent coordination performance."""

    def __init__(self):
        self._active_profiles: dict[str, cProfile.Profile] = {}
        self._profile_lock = threading.Lock()
        self._memory_tracker = MemoryTracker()

    @asynccontextmanager
    async def profile_async(self, profile_name: str):
        """Context manager for profiling async operations."""
        profiler = cProfile.Profile()

        with self._profile_lock:
            self._active_profiles[profile_name] = profiler

        # Start memory tracking
        self._memory_tracker.start_tracking(profile_name)

        start_time = time.time()
        profiler.enable()

        try:
            yield profiler
        finally:
            profiler.disable()
            end_time = time.time()

            # Stop memory tracking
            memory_usage = self._memory_tracker.stop_tracking(profile_name)

            # Generate profile result
            result = self._generate_profile_result(
                profiler, end_time - start_time, memory_usage
            )

            with self._profile_lock:
                self._active_profiles.pop(profile_name, None)

            logger.info(
                f"Profile '{profile_name}' completed: {result.duration:.3f}s, {result.function_calls} calls"
            )

    def _generate_profile_result(
        self,
        profiler: cProfile.Profile,
        duration: float,
        memory_usage: dict[str, float] | None,
    ) -> ProfileResult:
        """Generate profile result from profiler data."""
        # Capture profiler stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats("cumulative")

        # Extract top functions
        top_functions = []
        for func_info, (cc, _nc, tt, ct, _callers) in stats.stats.items():
            filename, line_num, func_name = func_info
            top_functions.append(
                {
                    "function": f"{filename}:{line_num}({func_name})",
                    "calls": cc,
                    "total_time": tt,
                    "cumulative_time": ct,
                    "per_call": ct / cc if cc > 0 else 0,
                }
            )

        # Sort by cumulative time and take top 20
        top_functions.sort(key=lambda x: x["cumulative_time"], reverse=True)
        top_functions = top_functions[:20]

        return ProfileResult(
            duration=duration,
            function_calls=stats.total_calls,
            primitive_calls=stats.prim_calls,
            total_time=stats.total_tt,
            cumulative_time=sum(
                ct for (cc, nc, tt, ct, callers) in stats.stats.values()
            ),
            top_functions=top_functions,
            memory_usage=memory_usage,
        )

    async def profile_concurrent_coordination(
        self,
        coordination_func: Callable,
        concurrency_levels: list[int],
        requests_per_level: int = 50,
    ) -> dict[int, ConcurrencyMetrics]:
        """Profile agent coordination under different concurrency levels."""
        results = {}

        for concurrency in concurrency_levels:
            logger.info(f"Profiling coordination at concurrency level: {concurrency}")

            async with self.profile_async(f"concurrency_{concurrency}"):
                metrics = await self._measure_concurrent_coordination(
                    coordination_func, concurrency, requests_per_level
                )
                results[concurrency] = metrics

        return results

    async def _measure_concurrent_coordination(
        self, coordination_func: Callable, concurrency: int, requests_per_level: int
    ) -> ConcurrencyMetrics:
        """Measure coordination performance at specific concurrency level."""
        import statistics

        response_times = []
        successful = 0
        failed = 0

        # Track memory usage
        memory_start = self._memory_tracker.get_current_memory_mb()

        async def single_request(request_id: int):
            """Execute a single coordination request."""
            nonlocal successful, failed

            start_time = time.time()
            try:
                await coordination_func(request_id)
                end_time = time.time()
                response_times.append(end_time - start_time)
                successful += 1
            except Exception as e:
                end_time = time.time()
                response_times.append(end_time - start_time)
                failed += 1
                logger.warning(f"Request {request_id} failed: {e}")

        # Execute concurrent requests
        start_time = time.time()

        # Create batches to manage concurrency
        batch_size = concurrency
        total_requests = requests_per_level

        for batch_start in range(0, total_requests, batch_size):
            batch_end = min(batch_start + batch_size, total_requests)
            batch_tasks = [single_request(i) for i in range(batch_start, batch_end)]
            await asyncio.gather(*batch_tasks, return_exceptions=True)

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate memory peak
        memory_end = self._memory_tracker.get_current_memory_mb()
        memory_peak = max(memory_start, memory_end)

        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) >= 20
                else max(response_times)
            )
            p99_response_time = (
                statistics.quantiles(response_times, n=100)[98]
                if len(response_times) >= 100
                else max(response_times)
            )
        else:
            avg_response_time = p95_response_time = p99_response_time = 0

        throughput = total_requests / total_duration if total_duration > 0 else 0

        # Estimate coordination overhead (time spent not in actual processing)
        total_processing_time = sum(response_times)
        coordination_overhead = max(0, total_duration - total_processing_time)

        return ConcurrencyMetrics(
            concurrent_requests=concurrency,
            total_duration=total_duration,
            successful_requests=successful,
            failed_requests=failed,
            average_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput_rps=throughput,
            coordination_overhead=coordination_overhead,
            memory_peak_mb=memory_peak,
        )


class MemoryTracker:
    """Track memory usage during profiling."""

    def __init__(self):
        self._tracking_sessions: dict[str, dict[str, float]] = {}
        self._lock = threading.Lock()

    def start_tracking(self, session_name: str):
        """Start tracking memory for a session."""
        with self._lock:
            self._tracking_sessions[session_name] = {
                "start_memory": self.get_current_memory_mb(),
                "peak_memory": self.get_current_memory_mb(),
            }

    def stop_tracking(self, session_name: str) -> dict[str, float] | None:
        """Stop tracking memory and return usage stats."""
        with self._lock:
            if session_name not in self._tracking_sessions:
                return None

            session_data = self._tracking_sessions.pop(session_name)
            end_memory = self.get_current_memory_mb()

            return {
                "start_memory_mb": session_data["start_memory"],
                "end_memory_mb": end_memory,
                "peak_memory_mb": session_data["peak_memory"],
                "memory_increase_mb": end_memory - session_data["start_memory"],
            }

    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback if psutil not available
            import resource

            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class CoordinationBenchmark:
    """Benchmark suite for agent coordination performance."""

    def __init__(self, profiler: AgentCoordinationProfiler | None = None):
        self.profiler = profiler or AgentCoordinationProfiler()
        self.benchmark_results: dict[str, Any] = {}

    async def run_coordination_benchmark(
        self, agent_proxies: dict[str, Any], test_scenarios: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Run comprehensive coordination benchmark."""
        results = {}

        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20, 50]

        for scenario in test_scenarios:
            scenario_name = scenario["name"]
            logger.info(f"Running benchmark scenario: {scenario_name}")

            async def coordination_func(
                request_id: int, scenario=scenario
            ):  # Bind scenario to avoid loop variable issue
                """Coordination function for this scenario."""
                return await self._execute_scenario(agent_proxies, scenario, request_id)

            # Profile coordination at different concurrency levels
            concurrency_results = await self.profiler.profile_concurrent_coordination(
                coordination_func, concurrency_levels, requests_per_level=20
            )

            results[scenario_name] = {
                "scenario": scenario,
                "concurrency_results": concurrency_results,
                "scalability_analysis": self._analyze_scalability(concurrency_results),
            }

        return results

    async def _execute_scenario(
        self, agent_proxies: dict[str, Any], scenario: dict[str, Any], request_id: int
    ):
        """Execute a single benchmark scenario."""
        scenario_type = scenario.get("type", "sequential")

        if scenario_type == "sequential":
            # Sequential IPA -> WBA -> NGA
            ipa_result = await agent_proxies["ipa"].process(
                {"text": f"{scenario['input']} (request {request_id})"}
            )

            wba_result = await agent_proxies["wba"].process(
                {
                    "world_id": f"benchmark_{request_id}",
                    "updates": scenario.get("world_updates", {}),
                }
            )

            nga_result = await agent_proxies["nga"].process(
                {
                    "prompt": f"{scenario['prompt']} (request {request_id})",
                    "context": {
                        "session_id": f"benchmark_{request_id}",
                        "world_state": wba_result.get("world_state", {}),
                    },
                }
            )

            return {
                "ipa_result": ipa_result,
                "wba_result": wba_result,
                "nga_result": nga_result,
            }

        if scenario_type == "parallel":
            # Parallel execution
            tasks = []

            if "ipa" in agent_proxies:
                tasks.append(
                    agent_proxies["ipa"].process(
                        {"text": f"{scenario['input']} (request {request_id})"}
                    )
                )

            if "wba" in agent_proxies:
                tasks.append(
                    agent_proxies["wba"].process(
                        {
                            "world_id": f"benchmark_{request_id}",
                            "updates": scenario.get("world_updates", {}),
                        }
                    )
                )

            if "nga" in agent_proxies:
                tasks.append(
                    agent_proxies["nga"].process(
                        {
                            "prompt": f"{scenario['prompt']} (request {request_id})",
                            "context": {"session_id": f"benchmark_{request_id}"},
                        }
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return {"parallel_results": results}

        raise ValueError(f"Unknown scenario type: {scenario_type}")

    def _analyze_scalability(
        self, concurrency_results: dict[int, ConcurrencyMetrics]
    ) -> dict[str, Any]:
        """Analyze scalability characteristics from concurrency results."""
        concurrency_levels = sorted(concurrency_results.keys())

        # Calculate scalability metrics
        throughput_scaling = []
        latency_degradation = []

        baseline_throughput = concurrency_results[concurrency_levels[0]].throughput_rps
        baseline_latency = concurrency_results[
            concurrency_levels[0]
        ].average_response_time

        for concurrency in concurrency_levels:
            metrics = concurrency_results[concurrency]

            # Throughput scaling (ideal would be linear)
            expected_throughput = baseline_throughput * concurrency
            actual_throughput = metrics.throughput_rps
            scaling_efficiency = (
                actual_throughput / expected_throughput
                if expected_throughput > 0
                else 0
            )
            throughput_scaling.append(scaling_efficiency)

            # Latency degradation
            latency_increase = (
                metrics.average_response_time / baseline_latency
                if baseline_latency > 0
                else 1
            )
            latency_degradation.append(latency_increase)

        return {
            "concurrency_levels": concurrency_levels,
            "throughput_scaling_efficiency": throughput_scaling,
            "latency_degradation_factor": latency_degradation,
            "optimal_concurrency": self._find_optimal_concurrency(concurrency_results),
            "scalability_score": min(throughput_scaling) if throughput_scaling else 0,
        }

    def _find_optimal_concurrency(
        self, concurrency_results: dict[int, ConcurrencyMetrics]
    ) -> int:
        """Find optimal concurrency level based on throughput and latency trade-off."""
        best_score = 0
        optimal_concurrency = 1

        for concurrency, metrics in concurrency_results.items():
            # Score based on throughput vs latency trade-off
            # Higher throughput is good, lower latency is good
            if metrics.average_response_time > 0:
                score = metrics.throughput_rps / metrics.average_response_time
                if score > best_score:
                    best_score = score
                    optimal_concurrency = concurrency

        return optimal_concurrency
