"""
Performance benchmarking and load testing utilities.

This module provides comprehensive benchmarking tools for performance
testing, load testing, and system capacity planning.
"""

import asyncio
import csv
import json
import statistics
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
import psutil

from .logging_config import LogCategory, get_logger
from .metrics_collector import get_metrics_collector

logger = get_logger(__name__)


class BenchmarkType(str, Enum):
    """Types of benchmarks."""

    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SPIKE_TEST = "spike_test"
    VOLUME_TEST = "volume_test"
    ENDURANCE_TEST = "endurance_test"
    BASELINE_TEST = "baseline_test"


class LoadPattern(str, Enum):
    """Load patterns for testing."""

    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    RAMP_DOWN = "ramp_down"
    SPIKE = "spike"
    STEP = "step"
    WAVE = "wave"


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark tests."""

    name: str
    benchmark_type: BenchmarkType
    duration_seconds: int = 60
    concurrent_users: int = 10
    requests_per_second: int | None = None
    load_pattern: LoadPattern = LoadPattern.CONSTANT
    ramp_up_time: int = 10
    ramp_down_time: int = 10
    target_endpoints: list[str] = field(default_factory=list)
    test_data: dict[str, Any] = field(default_factory=dict)
    success_criteria: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Set default success criteria if not provided."""
        if not self.success_criteria:
            self.success_criteria = {
                "max_response_time": 2.0,  # seconds
                "max_error_rate": 5.0,  # percentage
                "min_throughput": 10.0,  # requests per second
                "max_cpu_usage": 80.0,  # percentage
                "max_memory_usage": 80.0,  # percentage
            }


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""

    config: BenchmarkConfig
    start_time: datetime
    end_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = field(default_factory=list)
    error_details: list[dict[str, Any]] = field(default_factory=list)
    system_metrics: dict[str, list[float]] = field(default_factory=dict)
    throughput: float = 0.0
    success_rate: float = 0.0

    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        return statistics.mean(self.response_times) if self.response_times else 0.0

    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time."""
        if not self.response_times:
            return 0.0
        return (
            statistics.quantiles(self.response_times, n=20)[18]
            if len(self.response_times) >= 20
            else max(self.response_times)
        )

    @property
    def p99_response_time(self) -> float:
        """Calculate 99th percentile response time."""
        if not self.response_times:
            return 0.0
        return (
            statistics.quantiles(self.response_times, n=100)[98]
            if len(self.response_times) >= 100
            else max(self.response_times)
        )

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

    def meets_success_criteria(self) -> tuple[bool, list[str]]:
        """Check if results meet success criteria."""
        failures = []
        criteria = self.config.success_criteria

        if self.average_response_time > criteria.get("max_response_time", float("inf")):
            failures.append(
                f"Average response time {self.average_response_time:.2f}s exceeds limit {criteria['max_response_time']}s"
            )

        if self.error_rate > criteria.get("max_error_rate", float("inf")):
            failures.append(
                f"Error rate {self.error_rate:.2f}% exceeds limit {criteria['max_error_rate']}%"
            )

        if self.throughput < criteria.get("min_throughput", 0):
            failures.append(
                f"Throughput {self.throughput:.2f} RPS below minimum {criteria['min_throughput']} RPS"
            )

        # Check system metrics
        if "cpu_usage" in self.system_metrics:
            max_cpu = (
                max(self.system_metrics["cpu_usage"])
                if self.system_metrics["cpu_usage"]
                else 0
            )
            if max_cpu > criteria.get("max_cpu_usage", float("inf")):
                failures.append(
                    f"CPU usage {max_cpu:.2f}% exceeds limit {criteria['max_cpu_usage']}%"
                )

        if "memory_usage" in self.system_metrics:
            max_memory = (
                max(self.system_metrics["memory_usage"])
                if self.system_metrics["memory_usage"]
                else 0
            )
            if max_memory > criteria.get("max_memory_usage", float("inf")):
                failures.append(
                    f"Memory usage {max_memory:.2f}% exceeds limit {criteria['max_memory_usage']}%"
                )

        return len(failures) == 0, failures

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        success, failures = self.meets_success_criteria()

        return {
            "config": {
                "name": self.config.name,
                "type": self.config.benchmark_type.value,
                "duration": self.config.duration_seconds,
                "concurrent_users": self.config.concurrent_users,
                "load_pattern": self.config.load_pattern.value,
            },
            "execution": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration": (self.end_time - self.start_time).total_seconds(),
            },
            "requests": {
                "total": self.total_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "success_rate": self.success_rate,
                "error_rate": self.error_rate,
            },
            "performance": {
                "throughput": self.throughput,
                "avg_response_time": self.average_response_time,
                "p95_response_time": self.p95_response_time,
                "p99_response_time": self.p99_response_time,
                "min_response_time": (
                    min(self.response_times) if self.response_times else 0
                ),
                "max_response_time": (
                    max(self.response_times) if self.response_times else 0
                ),
            },
            "system_metrics": self.system_metrics,
            "success_criteria": {
                "passed": success,
                "failures": failures,
            },
            "errors": self.error_details[:10],  # Include first 10 errors
        }


class LoadGenerator(ABC):
    """Abstract base class for load generators."""

    @abstractmethod
    async def generate_load(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Generate load according to configuration."""
        pass


class HTTPLoadGenerator(LoadGenerator):
    """HTTP load generator for API testing."""

    def __init__(self, base_url: str, headers: dict[str, str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.session = None

    async def generate_load(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Generate HTTP load."""
        result = BenchmarkResult(
            config=config,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),  # Will be updated
        )

        # Initialize system metrics collection
        system_metrics_task = asyncio.create_task(
            self._collect_system_metrics(config.duration_seconds, result)
        )

        try:
            # Create HTTP session
            connector = aiohttp.TCPConnector(limit=config.concurrent_users * 2)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30),
            )

            # Generate load based on pattern
            if config.load_pattern == LoadPattern.CONSTANT:
                await self._constant_load(config, result)
            elif config.load_pattern == LoadPattern.RAMP_UP:
                await self._ramp_up_load(config, result)
            elif config.load_pattern == LoadPattern.SPIKE:
                await self._spike_load(config, result)
            else:
                await self._constant_load(config, result)  # Default

        finally:
            if self.session:
                await self.session.close()

            # Wait for system metrics collection to complete
            system_metrics_task.cancel()
            try:
                await system_metrics_task
            except asyncio.CancelledError:
                pass

            result.end_time = datetime.utcnow()

            # Calculate final metrics
            duration = (result.end_time - result.start_time).total_seconds()
            result.throughput = result.total_requests / duration if duration > 0 else 0
            result.success_rate = (
                (result.successful_requests / result.total_requests * 100)
                if result.total_requests > 0
                else 0
            )

        return result

    async def _constant_load(self, config: BenchmarkConfig, result: BenchmarkResult):
        """Generate constant load."""
        semaphore = asyncio.Semaphore(config.concurrent_users)
        tasks = []

        start_time = time.time()
        end_time = start_time + config.duration_seconds

        # Calculate request interval if RPS is specified
        request_interval = (
            1.0 / config.requests_per_second if config.requests_per_second else 0
        )

        while time.time() < end_time:
            if len(tasks) < config.concurrent_users:
                task = asyncio.create_task(
                    self._make_request(semaphore, config, result)
                )
                tasks.append(task)

            # Remove completed tasks
            tasks = [task for task in tasks if not task.done()]

            # Rate limiting
            if request_interval > 0:
                await asyncio.sleep(request_interval)
            else:
                await asyncio.sleep(0.01)  # Small delay to prevent tight loop

        # Wait for remaining tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _ramp_up_load(self, config: BenchmarkConfig, result: BenchmarkResult):
        """Generate ramping up load."""
        ramp_up_duration = config.ramp_up_time
        steady_duration = (
            config.duration_seconds - config.ramp_up_time - config.ramp_down_time
        )
        ramp_down_duration = config.ramp_down_time

        # Ramp up phase
        await self._ramp_phase(
            config, result, 0, config.concurrent_users, ramp_up_duration
        )

        # Steady phase
        if steady_duration > 0:
            await self._constant_load_phase(config, result, steady_duration)

        # Ramp down phase
        await self._ramp_phase(
            config, result, config.concurrent_users, 0, ramp_down_duration
        )

    async def _spike_load(self, config: BenchmarkConfig, result: BenchmarkResult):
        """Generate spike load pattern."""
        normal_users = config.concurrent_users // 2
        spike_users = config.concurrent_users
        spike_duration = config.duration_seconds // 4

        # Normal load
        await self._constant_load_phase(config, result, spike_duration, normal_users)

        # Spike
        await self._constant_load_phase(config, result, spike_duration, spike_users)

        # Back to normal
        await self._constant_load_phase(
            config, result, config.duration_seconds - 2 * spike_duration, normal_users
        )

    async def _ramp_phase(
        self,
        config: BenchmarkConfig,
        result: BenchmarkResult,
        start_users: int,
        end_users: int,
        duration: int,
    ):
        """Execute a ramping phase."""
        if duration <= 0:
            return

        steps = min(duration, abs(end_users - start_users))
        step_duration = duration / steps if steps > 0 else duration

        for step in range(steps):
            progress = step / steps if steps > 0 else 1
            current_users = int(start_users + (end_users - start_users) * progress)

            await self._constant_load_phase(
                config, result, step_duration, current_users
            )

    async def _constant_load_phase(
        self,
        config: BenchmarkConfig,
        result: BenchmarkResult,
        duration: float,
        concurrent_users: int = None,
    ):
        """Execute constant load for a specific duration."""
        if concurrent_users is None:
            concurrent_users = config.concurrent_users

        semaphore = asyncio.Semaphore(concurrent_users)
        tasks = []

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            if len(tasks) < concurrent_users:
                task = asyncio.create_task(
                    self._make_request(semaphore, config, result)
                )
                tasks.append(task)

            # Remove completed tasks
            tasks = [task for task in tasks if not task.done()]

            await asyncio.sleep(0.01)

        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _make_request(
        self,
        semaphore: asyncio.Semaphore,
        config: BenchmarkConfig,
        result: BenchmarkResult,
    ):
        """Make a single HTTP request."""
        async with semaphore:
            endpoint = self._select_endpoint(config.target_endpoints)
            url = f"{self.base_url}{endpoint}"

            start_time = time.time()

            try:
                async with self.session.get(url) as response:
                    await response.text()  # Read response body

                    response_time = time.time() - start_time
                    result.response_times.append(response_time)
                    result.total_requests += 1

                    if response.status < 400:
                        result.successful_requests += 1
                    else:
                        result.failed_requests += 1
                        result.error_details.append(
                            {
                                "url": url,
                                "status": response.status,
                                "timestamp": datetime.utcnow().isoformat(),
                                "response_time": response_time,
                            }
                        )

            except Exception as e:
                response_time = time.time() - start_time
                result.response_times.append(response_time)
                result.total_requests += 1
                result.failed_requests += 1

                result.error_details.append(
                    {
                        "url": url,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                        "response_time": response_time,
                    }
                )

    def _select_endpoint(self, endpoints: list[str]) -> str:
        """Select an endpoint for testing."""
        if not endpoints:
            return "/health"  # Default endpoint

        import random

        return random.choice(endpoints)

    async def _collect_system_metrics(self, duration: int, result: BenchmarkResult):
        """Collect system metrics during the test."""
        result.system_metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_usage": [],
            "network_io": [],
        }

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                result.system_metrics["cpu_usage"].append(cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                result.system_metrics["memory_usage"].append(memory.percent)

                # Disk usage
                disk = psutil.disk_usage("/")
                result.system_metrics["disk_usage"].append(disk.percent)

                # Network I/O
                network = psutil.net_io_counters()
                result.system_metrics["network_io"].append(
                    {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                    }
                )

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass


class BenchmarkSuite:
    """Suite of benchmark tests."""

    def __init__(self, base_url: str, output_dir: str = "./benchmark_results"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: list[BenchmarkResult] = []

    def add_benchmark(self, config: BenchmarkConfig) -> "BenchmarkSuite":
        """Add a benchmark configuration to the suite."""
        # Store config for later execution
        if not hasattr(self, "_configs"):
            self._configs = []
        self._configs.append(config)
        return self

    async def run_all(self) -> list[BenchmarkResult]:
        """Run all benchmark tests."""
        if not hasattr(self, "_configs"):
            logger.warning("No benchmark configurations added")
            return []

        results = []

        for config in self._configs:
            logger.info(f"Running benchmark: {config.name}")

            try:
                load_generator = HTTPLoadGenerator(self.base_url)
                result = await load_generator.generate_load(config)
                results.append(result)

                # Save individual result
                await self._save_result(result)

                # Log summary
                success, failures = result.meets_success_criteria()
                logger.info(
                    f"Benchmark {config.name} completed: "
                    f"Success={success}, "
                    f"Requests={result.total_requests}, "
                    f"Avg Response Time={result.average_response_time:.2f}s, "
                    f"Error Rate={result.error_rate:.2f}%",
                    category=LogCategory.PERFORMANCE,
                )

                if not success:
                    logger.warning(
                        f"Benchmark {config.name} failed criteria: {failures}"
                    )

            except Exception as e:
                logger.error(f"Benchmark {config.name} failed: {e}", exc_info=True)

        self.results = results

        # Generate summary report
        await self._generate_summary_report()

        return results

    async def _save_result(self, result: BenchmarkResult):
        """Save benchmark result to file."""
        timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{result.config.name}_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

        # Also save as CSV for easy analysis
        csv_filename = f"{result.config.name}_{timestamp}_response_times.csv"
        csv_filepath = self.output_dir / csv_filename

        with open(csv_filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "response_time"])

            for i, response_time in enumerate(result.response_times):
                timestamp = result.start_time.timestamp() + i * 0.1  # Approximate
                writer.writerow([timestamp, response_time])

    async def _generate_summary_report(self):
        """Generate a summary report of all benchmark results."""
        if not self.results:
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"benchmark_summary_{timestamp}.json"

        summary = {
            "execution_time": datetime.utcnow().isoformat(),
            "total_benchmarks": len(self.results),
            "passed_benchmarks": 0,
            "failed_benchmarks": 0,
            "benchmarks": [],
        }

        for result in self.results:
            success, failures = result.meets_success_criteria()

            if success:
                summary["passed_benchmarks"] += 1
            else:
                summary["failed_benchmarks"] += 1

            summary["benchmarks"].append(
                {
                    "name": result.config.name,
                    "type": result.config.benchmark_type.value,
                    "passed": success,
                    "failures": failures,
                    "metrics": {
                        "total_requests": result.total_requests,
                        "success_rate": result.success_rate,
                        "avg_response_time": result.average_response_time,
                        "p95_response_time": result.p95_response_time,
                        "throughput": result.throughput,
                    },
                }
            )

        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Benchmark summary saved to {report_path}")


class LoadTester:
    """High-level load testing interface."""

    @staticmethod
    def create_baseline_test(base_url: str, duration: int = 60) -> BenchmarkConfig:
        """Create a baseline performance test."""
        return BenchmarkConfig(
            name="baseline_performance",
            benchmark_type=BenchmarkType.BASELINE_TEST,
            duration_seconds=duration,
            concurrent_users=1,
            load_pattern=LoadPattern.CONSTANT,
            target_endpoints=["/health", "/api/v1/players/", "/api/v1/characters/"],
            success_criteria={
                "max_response_time": 1.0,
                "max_error_rate": 1.0,
                "min_throughput": 5.0,
            },
        )

    @staticmethod
    def create_load_test(
        base_url: str, concurrent_users: int = 10, duration: int = 300
    ) -> BenchmarkConfig:
        """Create a standard load test."""
        return BenchmarkConfig(
            name="standard_load_test",
            benchmark_type=BenchmarkType.LOAD_TEST,
            duration_seconds=duration,
            concurrent_users=concurrent_users,
            load_pattern=LoadPattern.RAMP_UP,
            ramp_up_time=30,
            ramp_down_time=30,
            target_endpoints=[
                "/api/v1/players/",
                "/api/v1/characters/",
                "/api/v1/worlds/",
                "/api/v1/sessions/",
            ],
            success_criteria={
                "max_response_time": 2.0,
                "max_error_rate": 5.0,
                "min_throughput": concurrent_users * 0.5,
                "max_cpu_usage": 80.0,
                "max_memory_usage": 80.0,
            },
        )

    @staticmethod
    def create_stress_test(
        base_url: str, max_users: int = 100, duration: int = 600
    ) -> BenchmarkConfig:
        """Create a stress test."""
        return BenchmarkConfig(
            name="stress_test",
            benchmark_type=BenchmarkType.STRESS_TEST,
            duration_seconds=duration,
            concurrent_users=max_users,
            load_pattern=LoadPattern.RAMP_UP,
            ramp_up_time=120,
            ramp_down_time=60,
            target_endpoints=[
                "/api/v1/players/",
                "/api/v1/characters/",
                "/api/v1/worlds/",
                "/api/v1/sessions/",
                "/api/v1/chat/",
            ],
            success_criteria={
                "max_response_time": 5.0,
                "max_error_rate": 10.0,
                "min_throughput": max_users * 0.2,
                "max_cpu_usage": 95.0,
                "max_memory_usage": 90.0,
            },
        )

    @staticmethod
    def create_spike_test(
        base_url: str, spike_users: int = 50, duration: int = 180
    ) -> BenchmarkConfig:
        """Create a spike test."""
        return BenchmarkConfig(
            name="spike_test",
            benchmark_type=BenchmarkType.SPIKE_TEST,
            duration_seconds=duration,
            concurrent_users=spike_users,
            load_pattern=LoadPattern.SPIKE,
            target_endpoints=[
                "/api/v1/players/",
                "/api/v1/characters/",
                "/api/v1/worlds/",
            ],
            success_criteria={
                "max_response_time": 3.0,
                "max_error_rate": 15.0,
                "min_throughput": spike_users * 0.3,
            },
        )


class PerformanceBenchmark:
    """Comprehensive performance benchmarking system."""

    def __init__(self, base_url: str, output_dir: str = "./benchmark_results"):
        self.base_url = base_url
        self.suite = BenchmarkSuite(base_url, output_dir)
        self.metrics_collector = get_metrics_collector()

    async def run_comprehensive_benchmark(self) -> dict[str, Any]:
        """Run a comprehensive benchmark suite."""
        logger.info("Starting comprehensive performance benchmark")

        # Add all benchmark types
        self.suite.add_benchmark(LoadTester.create_baseline_test(self.base_url))
        self.suite.add_benchmark(LoadTester.create_load_test(self.base_url, 10, 300))
        self.suite.add_benchmark(LoadTester.create_stress_test(self.base_url, 50, 600))
        self.suite.add_benchmark(LoadTester.create_spike_test(self.base_url, 25, 180))

        # Run all benchmarks
        results = await self.suite.run_all()

        # Analyze results
        analysis = self._analyze_results(results)

        logger.info("Comprehensive benchmark completed")

        return analysis

    def _analyze_results(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Analyze benchmark results and provide recommendations."""
        analysis = {
            "summary": {
                "total_tests": len(results),
                "passed_tests": 0,
                "failed_tests": 0,
                "overall_health": "unknown",
            },
            "performance_metrics": {},
            "bottlenecks": [],
            "recommendations": [],
            "detailed_results": [],
        }

        for result in results:
            success, failures = result.meets_success_criteria()

            if success:
                analysis["summary"]["passed_tests"] += 1
            else:
                analysis["summary"]["failed_tests"] += 1

            # Collect performance metrics
            test_name = result.config.name
            analysis["performance_metrics"][test_name] = {
                "avg_response_time": result.average_response_time,
                "p95_response_time": result.p95_response_time,
                "throughput": result.throughput,
                "error_rate": result.error_rate,
                "max_cpu": max(result.system_metrics.get("cpu_usage", [0])),
                "max_memory": max(result.system_metrics.get("memory_usage", [0])),
            }

            # Identify bottlenecks
            if result.average_response_time > 2.0:
                analysis["bottlenecks"].append(
                    f"High response time in {test_name}: {result.average_response_time:.2f}s"
                )

            if result.error_rate > 5.0:
                analysis["bottlenecks"].append(
                    f"High error rate in {test_name}: {result.error_rate:.2f}%"
                )

            max_cpu = max(result.system_metrics.get("cpu_usage", [0]))
            if max_cpu > 80.0:
                analysis["bottlenecks"].append(
                    f"High CPU usage in {test_name}: {max_cpu:.2f}%"
                )

            analysis["detailed_results"].append(result.to_dict())

        # Determine overall health
        if analysis["summary"]["failed_tests"] == 0:
            analysis["summary"]["overall_health"] = "excellent"
        elif (
            analysis["summary"]["failed_tests"]
            <= analysis["summary"]["total_tests"] * 0.2
        ):
            analysis["summary"]["overall_health"] = "good"
        elif (
            analysis["summary"]["failed_tests"]
            <= analysis["summary"]["total_tests"] * 0.5
        ):
            analysis["summary"]["overall_health"] = "fair"
        else:
            analysis["summary"]["overall_health"] = "poor"

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _generate_recommendations(self, analysis: dict[str, Any]) -> list[str]:
        """Generate performance recommendations based on analysis."""
        recommendations = []

        # Check response times
        high_response_times = [
            test
            for test, metrics in analysis["performance_metrics"].items()
            if metrics["avg_response_time"] > 1.0
        ]

        if high_response_times:
            recommendations.append(
                f"Consider optimizing response times for: {', '.join(high_response_times)}. "
                "Check database queries, caching, and algorithm efficiency."
            )

        # Check error rates
        high_error_rates = [
            test
            for test, metrics in analysis["performance_metrics"].items()
            if metrics["error_rate"] > 2.0
        ]

        if high_error_rates:
            recommendations.append(
                f"Investigate error causes in: {', '.join(high_error_rates)}. "
                "Check logs for specific error patterns and implement proper error handling."
            )

        # Check resource usage
        high_cpu_tests = [
            test
            for test, metrics in analysis["performance_metrics"].items()
            if metrics["max_cpu"] > 70.0
        ]

        if high_cpu_tests:
            recommendations.append(
                "High CPU usage detected. Consider implementing caching, "
                "optimizing algorithms, or scaling horizontally."
            )

        high_memory_tests = [
            test
            for test, metrics in analysis["performance_metrics"].items()
            if metrics["max_memory"] > 70.0
        ]

        if high_memory_tests:
            recommendations.append(
                "High memory usage detected. Check for memory leaks, "
                "optimize data structures, or increase available memory."
            )

        # Check throughput
        low_throughput_tests = [
            test
            for test, metrics in analysis["performance_metrics"].items()
            if metrics["throughput"] < 10.0
        ]

        if low_throughput_tests:
            recommendations.append(
                f"Low throughput in: {', '.join(low_throughput_tests)}. "
                "Consider connection pooling, async processing, or load balancing."
            )

        if not recommendations:
            recommendations.append(
                "System performance looks good! Continue monitoring and consider capacity planning for growth."
            )

        return recommendations
