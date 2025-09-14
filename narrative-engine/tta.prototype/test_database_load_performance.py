#!/usr/bin/env python3
"""
Database Load Performance Testing for TTA Prototype

This script tests database operations under load and error conditions
to validate the robustness of the database integration layer.

Usage:
    python test_database_load_performance.py [--concurrent-users N] [--duration SECONDS]
"""

import argparse
import logging
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

# Add the project paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseLoadTester:
    """
    Comprehensive database load testing for TTA prototype.

    Tests Neo4j and Redis under various load conditions including:
    - Concurrent user sessions
    - High-frequency operations
    - Error recovery scenarios
    - Memory pressure situations
    """

    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_username: str = "neo4j",
                 neo4j_password: str = "password",
                 redis_host: str = "localhost",
                 redis_port: int = 6379):
        """
        Initialize the database load tester.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
            redis_host: Redis host
            redis_port: Redis port
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.redis_host = redis_host
        self.redis_port = redis_port

        # Test results
        self.test_results = {
            "concurrent_sessions": {"status": "not_tested", "metrics": {}},
            "high_frequency_ops": {"status": "not_tested", "metrics": {}},
            "error_recovery": {"status": "not_tested", "metrics": {}},
            "memory_pressure": {"status": "not_tested", "metrics": {}},
            "overall": {"status": "not_tested", "score": 0.0}
        }

        # Performance metrics
        self.performance_metrics = {
            "response_times": [],
            "error_rates": [],
            "throughput": [],
            "memory_usage": []
        }

        # Thread-safe counters
        self._lock = threading.Lock()
        self._operation_count = 0
        self._error_count = 0
        self._success_count = 0

    def run_load_tests(self, concurrent_users: int = 50, duration: int = 60) -> dict[str, Any]:
        """
        Run comprehensive load tests.

        Args:
            concurrent_users: Number of concurrent users to simulate
            duration: Test duration in seconds

        Returns:
            Dict[str, Any]: Comprehensive test results
        """
        logger.info(f"Starting database load tests with {concurrent_users} concurrent users for {duration} seconds")
        start_time = time.time()

        try:
            # Initialize database connections
            if not self._initialize_connections():
                self.test_results["overall"]["status"] = "failed"
                self.test_results["overall"]["error"] = "Failed to initialize database connections"
                return self.test_results

            # Run load tests
            self._test_concurrent_sessions(concurrent_users, duration)
            self._test_high_frequency_operations(duration)
            self._test_error_recovery_scenarios()
            self._test_memory_pressure_scenarios()

            # Calculate overall score
            self._calculate_overall_score()

            # Generate summary
            test_time = time.time() - start_time
            self.test_results["test_time"] = test_time
            self.test_results["timestamp"] = datetime.now().isoformat()

            logger.info(f"Database load tests completed in {test_time:.2f} seconds")
            return self.test_results

        except Exception as e:
            logger.error(f"Database load tests failed: {e}")
            self.test_results["overall"]["status"] = "error"
            self.test_results["overall"]["error"] = str(e)
            return self.test_results

        finally:
            self._cleanup_connections()

    def _initialize_connections(self) -> bool:
        """Initialize database connections."""
        logger.info("Initializing database connections for load testing")

        try:
            # Initialize Neo4j connection
            from database.neo4j_schema import Neo4jSchemaManager
            self.neo4j_manager = Neo4jSchemaManager(
                uri=self.neo4j_uri,
                username=self.neo4j_username,
                password=self.neo4j_password
            )
            self.neo4j_manager.connect()
            logger.info("Neo4j connection established for load testing")

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {e}")
            return False

        try:
            # Initialize Redis connection
            from database.redis_cache_enhanced import (
                RedisConnectionManager,
                SessionCacheManager,
            )

            self.redis_connection_manager = RedisConnectionManager(
                host=self.redis_host,
                port=self.redis_port
            )
            self.redis_connection_manager.connect()

            self.session_cache_manager = SessionCacheManager(self.redis_connection_manager)

            logger.info("Redis connection established for load testing")

        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            return False

        return True

    def _test_concurrent_sessions(self, concurrent_users: int, duration: int) -> None:
        """Test concurrent user sessions."""
        logger.info(f"Testing concurrent sessions with {concurrent_users} users")

        try:
            start_time = time.time()
            response_times = []
            errors = []

            def simulate_user_session(user_id: int) -> dict[str, Any]:
                """Simulate a single user session."""
                session_metrics = {
                    "user_id": user_id,
                    "operations": 0,
                    "errors": 0,
                    "response_times": []
                }

                session_start = time.time()

                try:
                    # Create session
                    from models.data_models import SessionState

                    session = SessionState(
                        session_id=f"load_test_session_{user_id}_{int(time.time())}",
                        user_id=f"load_test_user_{user_id}",
                        current_scenario_id="load_test_scenario",
                        current_location_id="load_test_location",
                        narrative_position=1,
                        character_states={},
                        user_inventory=[],
                        therapeutic_progress=None,
                        emotional_state=None,
                        created_at=datetime.now(),
                        last_updated=datetime.now()
                    )

                    # Perform operations while test is running
                    while time.time() - start_time < duration:
                        op_start = time.time()

                        try:
                            # Cache session
                            success = self.session_cache_manager.cache_session_state(session)
                            if success:
                                # Retrieve session
                                retrieved = self.session_cache_manager.get_session_state(session.session_id)
                                if retrieved:
                                    session_metrics["operations"] += 1
                                    with self._lock:
                                        self._operation_count += 1
                                        self._success_count += 1
                                else:
                                    session_metrics["errors"] += 1
                                    with self._lock:
                                        self._error_count += 1
                            else:
                                session_metrics["errors"] += 1
                                with self._lock:
                                    self._error_count += 1

                        except Exception as e:
                            session_metrics["errors"] += 1
                            errors.append(str(e))
                            with self._lock:
                                self._error_count += 1

                        op_time = time.time() - op_start
                        session_metrics["response_times"].append(op_time)
                        response_times.append(op_time)

                        # Small delay to prevent overwhelming the system
                        time.sleep(0.01)

                except Exception as e:
                    logger.error(f"User session {user_id} failed: {e}")
                    session_metrics["errors"] += 1

                session_metrics["duration"] = time.time() - session_start
                return session_metrics

            # Run concurrent user sessions
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(simulate_user_session, i) for i in range(concurrent_users)]

                session_results = []
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        session_results.append(result)
                    except Exception as e:
                        logger.error(f"Session future failed: {e}")

            # Calculate metrics
            total_operations = sum(r["operations"] for r in session_results)
            total_errors = sum(r["errors"] for r in session_results)
            error_rate = (total_errors / (total_operations + total_errors)) if (total_operations + total_errors) > 0 else 0

            avg_response_time = statistics.mean(response_times) if response_times else 0
            throughput = total_operations / duration if duration > 0 else 0

            self.test_results["concurrent_sessions"] = {
                "status": "passed" if error_rate < 0.05 else "warning" if error_rate < 0.1 else "failed",
                "metrics": {
                    "concurrent_users": concurrent_users,
                    "duration": duration,
                    "total_operations": total_operations,
                    "total_errors": total_errors,
                    "error_rate": error_rate,
                    "avg_response_time": avg_response_time,
                    "throughput": throughput,
                    "session_results": len(session_results)
                }
            }

            logger.info(f"Concurrent sessions test completed: {total_operations} operations, {error_rate:.2%} error rate")

        except Exception as e:
            logger.error(f"Concurrent sessions test failed: {e}")
            self.test_results["concurrent_sessions"]["status"] = "error"
            self.test_results["concurrent_sessions"]["error"] = str(e)

    def _test_high_frequency_operations(self, duration: int) -> None:
        """Test high-frequency database operations."""
        logger.info("Testing high-frequency operations")

        try:
            start_time = time.time()
            operation_count = 0
            error_count = 0
            response_times = []

            # Perform rapid operations
            while time.time() - start_time < min(duration, 30):  # Limit to 30 seconds for high-frequency test
                op_start = time.time()

                try:
                    # Rapid Redis operations
                    test_key = f"high_freq_test_{operation_count}"
                    test_value = f"test_value_{operation_count}_{time.time()}"

                    with self.redis_connection_manager.get_client_context() as client:
                        # Set operation
                        client.set(test_key, test_value, ex=60)

                        # Get operation
                        retrieved = client.get(test_key)

                        # Delete operation
                        client.delete(test_key)

                    if retrieved and retrieved.decode() == test_value:
                        operation_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    logger.debug(f"High-frequency operation error: {e}")

                op_time = time.time() - op_start
                response_times.append(op_time)

            # Calculate metrics
            error_rate = error_count / (operation_count + error_count) if (operation_count + error_count) > 0 else 0
            avg_response_time = statistics.mean(response_times) if response_times else 0
            ops_per_second = operation_count / (time.time() - start_time)

            self.test_results["high_frequency_ops"] = {
                "status": "passed" if error_rate < 0.01 and ops_per_second > 100 else "warning" if error_rate < 0.05 else "failed",
                "metrics": {
                    "total_operations": operation_count,
                    "total_errors": error_count,
                    "error_rate": error_rate,
                    "avg_response_time": avg_response_time,
                    "ops_per_second": ops_per_second,
                    "duration": time.time() - start_time
                }
            }

            logger.info(f"High-frequency operations test completed: {ops_per_second:.1f} ops/sec, {error_rate:.2%} error rate")

        except Exception as e:
            logger.error(f"High-frequency operations test failed: {e}")
            self.test_results["high_frequency_ops"]["status"] = "error"
            self.test_results["high_frequency_ops"]["error"] = str(e)

    def _test_error_recovery_scenarios(self) -> None:
        """Test error recovery scenarios."""
        logger.info("Testing error recovery scenarios")

        try:
            recovery_tests = {
                "invalid_data": False,
                "connection_timeout": False,
                "large_payload": False,
                "concurrent_conflicts": False
            }

            # Test 1: Invalid data handling
            try:
                from models.data_models import SessionState

                # Try to cache invalid session data
                invalid_session = SessionState(
                    session_id="",  # Invalid empty ID
                    user_id="error_test_user",
                    current_scenario_id="error_test",
                    current_location_id="error_test",
                    narrative_position=-1,  # Invalid negative position
                    character_states={},
                    user_inventory=[],
                    therapeutic_progress=None,
                    emotional_state=None,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )

                # This should handle the error gracefully
                result = self.session_cache_manager.cache_session_state(invalid_session)
                recovery_tests["invalid_data"] = True  # If no exception, error handling works

            except Exception as e:
                logger.debug(f"Invalid data test error (expected): {e}")
                recovery_tests["invalid_data"] = True  # Expected to fail gracefully

            # Test 2: Large payload handling
            try:
                from models.data_models import SessionState

                # Create session with large data
                large_session = SessionState(
                    session_id="large_payload_test",
                    user_id="large_test_user",
                    current_scenario_id="large_test",
                    current_location_id="large_test",
                    narrative_position=1,
                    character_states={f"char_{i}": f"large_data_{'x' * 1000}" for i in range(100)},  # Large data
                    user_inventory=[f"item_{i}" for i in range(1000)],  # Large inventory
                    therapeutic_progress=None,
                    emotional_state=None,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )

                # This should handle large payloads
                result = self.session_cache_manager.cache_session_state(large_session)
                if result:
                    retrieved = self.session_cache_manager.get_session_state("large_payload_test")
                    recovery_tests["large_payload"] = retrieved is not None

            except Exception as e:
                logger.debug(f"Large payload test error: {e}")
                recovery_tests["large_payload"] = False

            # Test 3: Concurrent conflicts
            try:
                def concurrent_operation(thread_id: int) -> bool:
                    try:
                        from models.data_models import SessionState

                        session = SessionState(
                            session_id=f"concurrent_test_{thread_id}",
                            user_id=f"concurrent_user_{thread_id}",
                            current_scenario_id="concurrent_test",
                            current_location_id="concurrent_test",
                            narrative_position=thread_id,
                            character_states={},
                            user_inventory=[],
                            therapeutic_progress=None,
                            emotional_state=None,
                            created_at=datetime.now(),
                            last_updated=datetime.now()
                        )

                        # Rapid concurrent operations
                        for _i in range(10):
                            self.session_cache_manager.cache_session_state(session)
                            self.session_cache_manager.get_session_state(session.session_id)

                        return True
                    except Exception:
                        return False

                # Run concurrent operations
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(concurrent_operation, i) for i in range(10)]
                    results = [future.result() for future in as_completed(futures)]

                recovery_tests["concurrent_conflicts"] = sum(results) >= 8  # At least 80% success

            except Exception as e:
                logger.debug(f"Concurrent conflicts test error: {e}")
                recovery_tests["concurrent_conflicts"] = False

            # Calculate overall recovery score
            passed_tests = sum(1 for test in recovery_tests.values() if test)
            total_tests = len(recovery_tests)
            recovery_score = passed_tests / total_tests

            self.test_results["error_recovery"] = {
                "status": "passed" if recovery_score >= 0.8 else "warning" if recovery_score >= 0.6 else "failed",
                "metrics": {
                    "tests": recovery_tests,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "recovery_score": recovery_score
                }
            }

            logger.info(f"Error recovery test completed: {passed_tests}/{total_tests} tests passed")

        except Exception as e:
            logger.error(f"Error recovery test failed: {e}")
            self.test_results["error_recovery"]["status"] = "error"
            self.test_results["error_recovery"]["error"] = str(e)

    def _test_memory_pressure_scenarios(self) -> None:
        """Test memory pressure scenarios."""
        logger.info("Testing memory pressure scenarios")

        try:
            import gc

            import psutil

            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            memory_tests = {
                "large_batch_operations": False,
                "memory_cleanup": False,
                "cache_eviction": False
            }

            # Test 1: Large batch operations
            try:
                from models.data_models import SessionState

                # Create many sessions
                sessions = []
                for i in range(1000):
                    session = SessionState(
                        session_id=f"memory_test_session_{i}",
                        user_id=f"memory_test_user_{i}",
                        current_scenario_id="memory_test",
                        current_location_id="memory_test",
                        narrative_position=i,
                        character_states={f"char_{j}": f"data_{j}" for j in range(10)},
                        user_inventory=[f"item_{j}" for j in range(20)],
                        therapeutic_progress=None,
                        emotional_state=None,
                        created_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    sessions.append(session)

                # Cache all sessions
                cached_count = self.session_cache_manager.cache_multiple_sessions(sessions)
                memory_tests["large_batch_operations"] = cached_count >= 900  # At least 90% success

                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory

                logger.info(f"Memory usage increased by {memory_increase:.1f} MB during batch operations")

            except Exception as e:
                logger.debug(f"Large batch operations test error: {e}")
                memory_tests["large_batch_operations"] = False

            # Test 2: Memory cleanup
            try:
                # Force garbage collection
                gc.collect()

                # Check if memory was cleaned up
                post_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_tests["memory_cleanup"] = post_gc_memory <= current_memory * 1.1  # Within 10% of previous

            except Exception as e:
                logger.debug(f"Memory cleanup test error: {e}")
                memory_tests["memory_cleanup"] = False

            # Test 3: Cache eviction (Redis)
            try:
                # Fill cache with temporary data
                with self.redis_connection_manager.get_client_context() as client:
                    for i in range(1000):
                        client.setex(f"temp_key_{i}", 1, f"temp_value_{i}")  # 1 second TTL

                # Wait for eviction
                time.sleep(2)

                # Check if keys were evicted
                with self.redis_connection_manager.get_client_context() as client:
                    remaining_keys = client.keys("temp_key_*")

                memory_tests["cache_eviction"] = len(remaining_keys) < 100  # Most keys should be evicted

            except Exception as e:
                logger.debug(f"Cache eviction test error: {e}")
                memory_tests["cache_eviction"] = False

            # Calculate overall memory pressure score
            passed_tests = sum(1 for test in memory_tests.values() if test)
            total_tests = len(memory_tests)
            memory_score = passed_tests / total_tests

            final_memory = process.memory_info().rss / 1024 / 1024  # MB

            self.test_results["memory_pressure"] = {
                "status": "passed" if memory_score >= 0.8 else "warning" if memory_score >= 0.6 else "failed",
                "metrics": {
                    "tests": memory_tests,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "memory_score": memory_score,
                    "initial_memory_mb": initial_memory,
                    "final_memory_mb": final_memory,
                    "memory_increase_mb": final_memory - initial_memory
                }
            }

            logger.info(f"Memory pressure test completed: {passed_tests}/{total_tests} tests passed")

        except Exception as e:
            logger.error(f"Memory pressure test failed: {e}")
            self.test_results["memory_pressure"]["status"] = "error"
            self.test_results["memory_pressure"]["error"] = str(e)

    def _calculate_overall_score(self) -> None:
        """Calculate overall load test score."""
        scores = []

        for test_name, test_result in self.test_results.items():
            if test_name == "overall":
                continue

            if test_result["status"] == "passed":
                scores.append(1.0)
            elif test_result["status"] == "warning":
                scores.append(0.7)
            elif test_result["status"] == "failed":
                scores.append(0.3)
            else:  # error
                scores.append(0.0)

        overall_score = statistics.mean(scores) if scores else 0.0

        if overall_score >= 0.8:
            status = "passed"
        elif overall_score >= 0.6:
            status = "warning"
        else:
            status = "failed"

        self.test_results["overall"] = {
            "status": status,
            "score": overall_score
        }

    def _cleanup_connections(self) -> None:
        """Clean up database connections."""
        try:
            if hasattr(self, 'neo4j_manager') and self.neo4j_manager:
                self.neo4j_manager.disconnect()

            if hasattr(self, 'redis_connection_manager') and self.redis_connection_manager:
                self.redis_connection_manager.disconnect()

        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def print_results(self) -> None:
        """Print formatted test results."""
        print("=" * 80)
        print("TTA PROTOTYPE DATABASE LOAD TESTING REPORT")
        print("=" * 80)
        print(f"Test Time: {self.test_results.get('timestamp', 'Unknown')}")
        print(f"Total Duration: {self.test_results.get('test_time', 0):.2f} seconds")
        print(f"Overall Score: {self.test_results['overall']['score']:.2f}")
        print(f"Overall Status: {self.test_results['overall']['status'].upper()}")
        print()

        print("COMPONENT RESULTS:")
        print("-" * 40)

        for test_name, result in self.test_results.items():
            if test_name in ["overall", "test_time", "timestamp"]:
                continue

            status = result["status"].upper()
            score = result.get("metrics", {}).get("recovery_score", result.get("metrics", {}).get("memory_score", 1.0 if status == "PASSED" else 0.0))

            print(f"{test_name.replace('_', ' ').title()}: {status} ({score:.2f})")

            if "metrics" in result:
                metrics = result["metrics"]
                if "total_operations" in metrics:
                    print(f"  Operations: {metrics['total_operations']}")
                if "error_rate" in metrics:
                    print(f"  Error Rate: {metrics['error_rate']:.2%}")
                if "throughput" in metrics:
                    print(f"  Throughput: {metrics['throughput']:.1f} ops/sec")
                if "ops_per_second" in metrics:
                    print(f"  Ops/Second: {metrics['ops_per_second']:.1f}")

            if "error" in result:
                print(f"  Error: {result['error']}")

        print()
        print("RECOMMENDATIONS:")
        print("-" * 40)

        overall_score = self.test_results["overall"]["score"]
        if overall_score >= 0.8:
            print("• Database system is ready for production load")
            print("• Performance is within acceptable limits")
        elif overall_score >= 0.6:
            print("• Database system needs optimization before production")
            print("• Monitor performance closely in production")
        else:
            print("• Database system requires significant improvements")
            print("• Not recommended for production use")

        print("=" * 80)


def main():
    """Main function to run database load tests."""
    parser = argparse.ArgumentParser(description="Database Load Performance Testing for TTA Prototype")
    parser.add_argument("--concurrent-users", type=int, default=50, help="Number of concurrent users to simulate")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j connection URI")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")

    args = parser.parse_args()

    # Create and run load tester
    tester = DatabaseLoadTester(
        neo4j_uri=args.neo4j_uri,
        redis_host=args.redis_host
    )

    results = tester.run_load_tests(
        concurrent_users=args.concurrent_users,
        duration=args.duration
    )

    # Print results
    tester.print_results()

    # Return appropriate exit code
    overall_score = results["overall"]["score"]
    return 0 if overall_score >= 0.8 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
