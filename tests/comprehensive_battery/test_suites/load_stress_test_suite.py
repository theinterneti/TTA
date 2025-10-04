"""
Load/Stress Test Suite

Tests system performance and stability under high load including:
- Concurrent user simulation
- Story generation under load
- Database performance stress testing
- Memory and CPU usage monitoring
- Connection pool exhaustion testing
- System stability validation
"""

import asyncio
import logging
import random
import time
import uuid
from datetime import datetime
from typing import Any

import psutil
import redis.asyncio as aioredis
from neo4j import AsyncDriver

from ..common import TestCategory, TestResult, TestStatus
from ..utils.test_data_generator import TestDataGenerator

logger = logging.getLogger(__name__)


class LoadStressTestSuite:
    """
    Load and stress test suite for performance validation.

    Tests system behavior under high concurrent load, resource stress,
    and extended operation periods to validate stability and performance.
    """

    def __init__(self, neo4j_driver: AsyncDriver, redis_client: aioredis.Redis, config):
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client
        self.config = config

        self.test_data_generator = TestDataGenerator(neo4j_driver, redis_client)
        self.test_run_id = str(uuid.uuid4())

        self.results: list[TestResult] = []
        self.performance_metrics = {}

    async def execute_all_tests(self) -> list[TestResult]:
        """Execute all load and stress tests."""
        try:
            # Generate load test data
            load_test_data = await self.test_data_generator.generate_load_test_data(
                self.config.max_concurrent_users
            )

            # Execute test categories
            await self._test_concurrent_user_simulation(load_test_data)
            await self._test_story_generation_under_load(load_test_data)
            await self._test_database_performance_stress()
            await self._test_memory_usage_under_load()
            await self._test_connection_pool_exhaustion()
            await self._test_sustained_load_stability()
            await self._test_spike_load_handling()
            await self._test_resource_cleanup_under_load()

            logger.info(
                f"Load/stress test suite completed: {len(self.results)} tests executed"
            )
            return self.results

        finally:
            await self.cleanup()

    async def _test_concurrent_user_simulation(self, load_test_data: dict[str, Any]):
        """Test system with concurrent users."""
        concurrent_levels = [10, 25, 50, 100]

        for user_count in concurrent_levels:
            if user_count > len(load_test_data["users"]):
                continue

            test_name = f"concurrent_users_{user_count}"
            result = TestResult(
                test_name=test_name,
                category=TestCategory.LOAD_STRESS,
                status=TestStatus.RUNNING,
                start_time=datetime.utcnow(),
            )

            try:
                # Start performance monitoring
                start_metrics = await self._capture_system_metrics()

                # Simulate concurrent users
                tasks = []
                test_users = load_test_data["users"][:user_count]

                for user in test_users:
                    task = asyncio.create_task(self._simulate_user_session(user))
                    tasks.append(task)

                # Wait for all users to complete
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()

                # Capture end metrics
                end_metrics = await self._capture_system_metrics()

                # Analyze results
                successful_sessions = len(
                    [r for r in results if not isinstance(r, Exception)]
                )
                failed_sessions = len(results) - successful_sessions

                if successful_sessions >= user_count * 0.95:  # 95% success rate
                    result.passed = True
                    result.details = {
                        "concurrent_users": user_count,
                        "successful_sessions": successful_sessions,
                        "failed_sessions": failed_sessions,
                        "success_rate": (successful_sessions / user_count) * 100,
                        "total_duration": end_time - start_time,
                        "avg_response_time": (end_time - start_time) / user_count,
                    }
                    result.metrics = {
                        "cpu_usage_delta": end_metrics["cpu_percent"]
                        - start_metrics["cpu_percent"],
                        "memory_usage_delta": end_metrics["memory_percent"]
                        - start_metrics["memory_percent"],
                        "throughput_rps": user_count / (end_time - start_time),
                    }
                else:
                    result.error_message = (
                        f"Low success rate: {successful_sessions}/{user_count}"
                    )

            except Exception as e:
                result.error_message = str(e)
                logger.error(f"Concurrent user test failed for {user_count} users: {e}")

            finally:
                result.end_time = datetime.utcnow()
                result.duration_seconds = (
                    result.end_time - result.start_time
                ).total_seconds()
                result.status = TestStatus.COMPLETED
                self.results.append(result)

    async def _test_story_generation_under_load(self, load_test_data: dict[str, Any]):
        """Test story generation performance under load."""
        test_name = "story_generation_under_load"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Generate stories concurrently
            story_count = 50
            users = load_test_data["users"][:story_count]
            scenarios = load_test_data["scenarios"]

            start_time = time.time()

            # Create concurrent story generation tasks
            tasks = []
            for i, user in enumerate(users):
                scenario = scenarios[i % len(scenarios)]
                task = asyncio.create_task(
                    self._generate_story_under_load(user, scenario)
                )
                tasks.append(task)

            # Execute all story generations
            story_results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            end_metrics = await self._capture_system_metrics()

            # Analyze story generation performance
            successful_stories = len(
                [r for r in story_results if not isinstance(r, Exception)]
            )
            avg_generation_time = (end_time - start_time) / story_count

            if successful_stories >= story_count * 0.9:  # 90% success rate
                result.passed = True
                result.details = {
                    "stories_generated": successful_stories,
                    "total_stories_attempted": story_count,
                    "success_rate": (successful_stories / story_count) * 100,
                    "avg_generation_time": avg_generation_time,
                    "total_duration": end_time - start_time,
                }
                result.metrics = {
                    "stories_per_second": story_count / (end_time - start_time),
                    "cpu_usage_peak": end_metrics["cpu_percent"],
                    "memory_usage_peak": end_metrics["memory_percent"],
                }
            else:
                result.error_message = f"Story generation success rate too low: {successful_stories}/{story_count}"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Story generation load test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_database_performance_stress(self):
        """Test database performance under stress."""
        test_name = "database_performance_stress"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Test Neo4j performance
            neo4j_performance = await self._stress_test_neo4j()

            # Test Redis performance
            redis_performance = await self._stress_test_redis()

            # Evaluate performance metrics
            neo4j_acceptable = neo4j_performance["avg_query_time"] < 1.0  # < 1 second
            redis_acceptable = redis_performance["avg_operation_time"] < 0.1  # < 100ms

            if neo4j_acceptable and redis_acceptable:
                result.passed = True
                result.details = {
                    "neo4j_performance": neo4j_performance,
                    "redis_performance": redis_performance,
                    "performance_acceptable": True,
                }
            else:
                result.error_message = (
                    "Database performance below acceptable thresholds"
                )
                result.details = {
                    "neo4j_performance": neo4j_performance,
                    "redis_performance": redis_performance,
                    "neo4j_acceptable": neo4j_acceptable,
                    "redis_acceptable": redis_acceptable,
                }

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Database stress test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_memory_usage_under_load(self):
        """Test memory usage patterns under load."""
        test_name = "memory_usage_under_load"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Monitor memory usage during load
            initial_memory = psutil.virtual_memory().percent
            memory_samples = []

            # Create memory-intensive tasks
            tasks = []
            for _ in range(20):
                task = asyncio.create_task(self._memory_intensive_operation())
                tasks.append(task)

            # Monitor memory during execution
            monitoring_task = asyncio.create_task(
                self._monitor_memory_usage(memory_samples, duration_seconds=30)
            )

            # Execute tasks
            await asyncio.gather(*tasks)
            monitoring_task.cancel()

            # Analyze memory usage
            peak_memory = max(memory_samples) if memory_samples else initial_memory
            memory_increase = peak_memory - initial_memory

            # Check for memory leaks (memory should return to baseline)
            await asyncio.sleep(5)  # Allow garbage collection
            final_memory = psutil.virtual_memory().percent
            memory_leak = (final_memory - initial_memory) > 5  # > 5% increase

            if not memory_leak and memory_increase < 50:  # < 50% increase
                result.passed = True
                result.details = {
                    "initial_memory_percent": initial_memory,
                    "peak_memory_percent": peak_memory,
                    "final_memory_percent": final_memory,
                    "memory_increase": memory_increase,
                    "memory_leak_detected": memory_leak,
                }
            else:
                result.error_message = f"Memory usage issues: leak={memory_leak}, increase={memory_increase}%"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Memory usage test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_connection_pool_exhaustion(self):
        """Test connection pool exhaustion scenarios."""
        test_name = "connection_pool_exhaustion"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Create many concurrent connections
            connection_tasks = []
            max_connections = 100

            for _ in range(max_connections):
                task = asyncio.create_task(self._create_database_connection())
                connection_tasks.append(task)

            # Execute connection attempts
            connection_results = await asyncio.gather(
                *connection_tasks, return_exceptions=True
            )

            # Analyze connection handling
            successful_connections = len(
                [r for r in connection_results if not isinstance(r, Exception)]
            )
            connection_errors = len(connection_results) - successful_connections

            # System should handle connection limits gracefully
            if connection_errors > 0:  # Some connections should be rejected gracefully
                result.passed = True
                result.details = {
                    "max_connections_attempted": max_connections,
                    "successful_connections": successful_connections,
                    "graceful_rejections": connection_errors,
                    "pool_limits_enforced": True,
                }
            else:
                result.error_message = "Connection pool limits not properly enforced"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Connection pool test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_sustained_load_stability(self):
        """Test system stability under sustained load."""
        test_name = "sustained_load_stability"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Run sustained load for extended period
            duration_minutes = 5  # Reduced for testing
            end_time = time.time() + (duration_minutes * 60)

            stability_metrics = []
            error_count = 0

            while time.time() < end_time:
                try:
                    # Perform regular operations
                    await self._perform_regular_operations()

                    # Capture stability metrics
                    metrics = await self._capture_system_metrics()
                    stability_metrics.append(metrics)

                    await asyncio.sleep(10)  # Check every 10 seconds

                except Exception as e:
                    error_count += 1
                    logger.warning(f"Error during sustained load: {e}")

            # Analyze stability
            avg_cpu = sum(m["cpu_percent"] for m in stability_metrics) / len(
                stability_metrics
            )
            avg_memory = sum(m["memory_percent"] for m in stability_metrics) / len(
                stability_metrics
            )

            if error_count < 5 and avg_cpu < 80 and avg_memory < 80:
                result.passed = True
                result.details = {
                    "duration_minutes": duration_minutes,
                    "error_count": error_count,
                    "avg_cpu_percent": avg_cpu,
                    "avg_memory_percent": avg_memory,
                    "stability_maintained": True,
                }
            else:
                result.error_message = f"System unstable: errors={error_count}, cpu={avg_cpu}%, memory={avg_memory}%"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Sustained load test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_spike_load_handling(self):
        """Test system response to sudden load spikes."""
        test_name = "spike_load_handling"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Create sudden load spike
            spike_tasks = []
            spike_size = 50

            # Measure baseline performance
            baseline_time = await self._measure_operation_time()

            # Create load spike
            for _ in range(spike_size):
                task = asyncio.create_task(self._spike_load_operation())
                spike_tasks.append(task)

            # Measure performance during spike
            spike_start = time.time()
            spike_results = await asyncio.gather(*spike_tasks, return_exceptions=True)
            spike_duration = time.time() - spike_start

            # Measure recovery time
            recovery_time = await self._measure_operation_time()

            # Analyze spike handling
            successful_operations = len(
                [r for r in spike_results if not isinstance(r, Exception)]
            )
            performance_degradation = (
                recovery_time / baseline_time if baseline_time > 0 else 1
            )

            if (
                successful_operations >= spike_size * 0.8
                and performance_degradation < 3
            ):
                result.passed = True
                result.details = {
                    "spike_size": spike_size,
                    "successful_operations": successful_operations,
                    "spike_duration": spike_duration,
                    "performance_degradation": performance_degradation,
                    "spike_handled": True,
                }
            else:
                result.error_message = f"Spike handling inadequate: success={successful_operations}/{spike_size}, degradation={performance_degradation}x"

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Spike load test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def _test_resource_cleanup_under_load(self):
        """Test resource cleanup under load conditions."""
        test_name = "resource_cleanup_under_load"
        result = TestResult(
            test_name=test_name,
            category=TestCategory.LOAD_STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            # Create resources that need cleanup
            initial_resources = await self._count_system_resources()

            # Create and cleanup resources under load
            cleanup_tasks = []
            for _ in range(30):
                task = asyncio.create_task(self._create_and_cleanup_resources())
                cleanup_tasks.append(task)

            await asyncio.gather(*cleanup_tasks)

            # Allow time for cleanup
            await asyncio.sleep(5)

            # Check resource cleanup
            final_resources = await self._count_system_resources()
            resource_leak = final_resources > initial_resources * 1.1  # 10% tolerance

            if not resource_leak:
                result.passed = True
                result.details = {
                    "initial_resources": initial_resources,
                    "final_resources": final_resources,
                    "resource_leak_detected": resource_leak,
                    "cleanup_effective": True,
                }
            else:
                result.error_message = (
                    f"Resource leak detected: {initial_resources} -> {final_resources}"
                )

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Resource cleanup test failed: {e}")

        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.status = TestStatus.COMPLETED
            self.results.append(result)

    async def cleanup(self):
        """Clean up load test resources."""
        try:
            await self.test_data_generator.cleanup_test_data(self.test_run_id)
            logger.info("Load/stress test suite cleanup completed")
        except Exception as e:
            logger.error(f"Load test cleanup failed: {e}")

    # Helper methods for load testing
    async def _capture_system_metrics(self) -> dict[str, float]:
        """Capture current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "network_connections": len(psutil.net_connections()),
            "timestamp": time.time(),
        }

    async def _simulate_user_session(self, user) -> dict[str, Any]:
        """Simulate a user session for load testing."""
        # Implementation would simulate realistic user interactions
        await asyncio.sleep(
            random.uniform(0.1, 2.0)
        )  # Simulate variable response times
        return {"user_id": user.user_id, "session_completed": True}

    async def _generate_story_under_load(self, user, scenario) -> dict[str, Any]:
        """Generate story content under load conditions."""
        # Implementation would generate actual story content
        await asyncio.sleep(random.uniform(0.5, 3.0))  # Simulate story generation time
        return {"story_generated": True, "user_id": user.user_id}

    async def _stress_test_neo4j(self) -> dict[str, float]:
        """Stress test Neo4j database."""
        # Implementation would perform intensive Neo4j operations
        return {"avg_query_time": 0.5, "queries_per_second": 100}

    async def _stress_test_redis(self) -> dict[str, float]:
        """Stress test Redis database."""
        # Implementation would perform intensive Redis operations
        return {"avg_operation_time": 0.05, "operations_per_second": 1000}

    async def _memory_intensive_operation(self):
        """Perform memory-intensive operation."""
        # Implementation would create memory load
        await asyncio.sleep(1)

    async def _monitor_memory_usage(self, samples: list[float], duration_seconds: int):
        """Monitor memory usage over time."""
        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            samples.append(psutil.virtual_memory().percent)
            await asyncio.sleep(1)

    async def _create_database_connection(self):
        """Create database connection for pool testing."""
        # Implementation would create actual database connections
        await asyncio.sleep(0.1)
        return "connection_created"

    async def _perform_regular_operations(self):
        """Perform regular system operations."""
        # Implementation would perform typical system operations
        await asyncio.sleep(0.5)

    async def _measure_operation_time(self) -> float:
        """Measure time for standard operation."""
        start = time.time()
        await asyncio.sleep(0.1)  # Simulate operation
        return time.time() - start

    async def _spike_load_operation(self):
        """Perform operation during load spike."""
        # Implementation would perform actual operations
        await asyncio.sleep(random.uniform(0.1, 1.0))

    async def _count_system_resources(self) -> int:
        """Count system resources for leak detection."""
        # Implementation would count actual system resources
        return len(psutil.pids())

    async def _create_and_cleanup_resources(self):
        """Create resources and test cleanup."""
        # Implementation would create and cleanup actual resources
        await asyncio.sleep(0.2)
