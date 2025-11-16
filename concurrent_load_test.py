#!/usr/bin/env python3
"""
TTA Concurrent Load Testing
Test system performance under concurrent user load
"""

import asyncio
import json
import logging
import time
from datetime import datetime

import aiohttp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConcurrentLoadTester:
    def __init__(
        self, base_url: str = "http://localhost:3004", concurrent_users: int = 10
    ):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []

    async def simulate_user_session(self, user_id: int, session: aiohttp.ClientSession):
        """Simulate a complete user session"""
        user_results = {
            "user_id": user_id,
            "start_time": time.time(),
            "operations": [],
            "errors": [],
        }

        try:
            # 1. Health check
            start = time.time()
            async with session.get(f"{self.base_url}/health") as response:
                duration = time.time() - start
                user_results["operations"].append(
                    {
                        "operation": "health_check",
                        "status_code": response.status,
                        "duration_ms": duration * 1000,
                        "success": response.status == 200,
                    }
                )

            # 2. User registration
            test_user = {
                "username": f"load_test_user_{user_id}_{int(time.time())}",
                "email": f"loadtest{user_id}_{int(time.time())}@example.com",
                "password": "LoadTest123!",
                "role": "player",
            }

            start = time.time()
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"},
            ) as response:
                duration = time.time() - start
                success = response.status == 200
                user_results["operations"].append(
                    {
                        "operation": "user_registration",
                        "status_code": response.status,
                        "duration_ms": duration * 1000,
                        "success": success,
                    }
                )

                if not success:
                    error_data = await response.json()
                    user_results["errors"].append(
                        {"operation": "user_registration", "error": error_data}
                    )

            # 3. Login attempt (expected to fail due to DB issues, but test performance)
            start = time.time()
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": test_user["username"],
                    "password": test_user["password"],
                },
                headers={"Content-Type": "application/json"},
            ) as response:
                duration = time.time() - start
                user_results["operations"].append(
                    {
                        "operation": "user_login",
                        "status_code": response.status,
                        "duration_ms": duration * 1000,
                        "success": response.status == 200,
                    }
                )

            # 4. Metrics endpoint check
            start = time.time()
            async with session.get(f"{self.base_url}/metrics") as response:
                duration = time.time() - start
                user_results["operations"].append(
                    {
                        "operation": "metrics_check",
                        "status_code": response.status,
                        "duration_ms": duration * 1000,
                        "success": response.status == 200,
                    }
                )

        except Exception as e:
            user_results["errors"].append(
                {"operation": "session_error", "error": str(e)}
            )

        user_results["end_time"] = time.time()
        user_results["total_duration"] = (
            user_results["end_time"] - user_results["start_time"]
        )

        return user_results

    async def run_concurrent_test(self):
        """Run concurrent load test"""
        logger.info(f"Starting concurrent load test with {self.concurrent_users} users")
        start_time = time.time()

        # Create session with connection limits
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Create tasks for concurrent users
            tasks = [
                self.simulate_user_session(user_id, session)
                for user_id in range(self.concurrent_users)
            ]

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_sessions = 0
            failed_sessions = 0
            total_operations = 0
            successful_operations = 0

            for result in results:
                if isinstance(result, Exception):
                    failed_sessions += 1
                    logger.error(f"Session failed with exception: {result}")
                else:
                    successful_sessions += 1
                    self.results.append(result)

                    # Count operations
                    for op in result["operations"]:
                        total_operations += 1
                        if op["success"]:
                            successful_operations += 1

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate statistics
        response_times = []
        operation_stats = {}

        for result in self.results:
            for op in result["operations"]:
                response_times.append(op["duration_ms"])

                op_name = op["operation"]
                if op_name not in operation_stats:
                    operation_stats[op_name] = {
                        "count": 0,
                        "success_count": 0,
                        "total_time": 0,
                        "min_time": float("inf"),
                        "max_time": 0,
                    }

                stats = operation_stats[op_name]
                stats["count"] += 1
                stats["total_time"] += op["duration_ms"]
                stats["min_time"] = min(stats["min_time"], op["duration_ms"])
                stats["max_time"] = max(stats["max_time"], op["duration_ms"])

                if op["success"]:
                    stats["success_count"] += 1

        # Calculate averages
        for op_name, stats in operation_stats.items():
            if stats["count"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["count"]
                stats["success_rate"] = (stats["success_count"] / stats["count"]) * 100

        summary = {
            "test_config": {
                "concurrent_users": self.concurrent_users,
                "base_url": self.base_url,
            },
            "timing": {
                "total_duration_seconds": total_duration,
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
            },
            "session_results": {
                "successful_sessions": successful_sessions,
                "failed_sessions": failed_sessions,
                "session_success_rate": (successful_sessions / self.concurrent_users)
                * 100,
            },
            "operation_results": {
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "operation_success_rate": (successful_operations / total_operations)
                * 100
                if total_operations > 0
                else 0,
            },
            "performance_metrics": {
                "avg_response_time_ms": sum(response_times) / len(response_times)
                if response_times
                else 0,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "operations_per_second": total_operations / total_duration
                if total_duration > 0
                else 0,
            },
            "operation_breakdown": operation_stats,
        }

        return {"summary": summary, "detailed_results": self.results}


async def main():
    """Main test execution"""
    # Test with 5 concurrent users (conservative for testing)
    tester = ConcurrentLoadTester(concurrent_users=5)

    logger.info("Starting concurrent load test...")
    results = await tester.run_concurrent_test()

    # Save results
    with open("concurrent_load_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    summary = results["summary"]
    logger.info("=== CONCURRENT LOAD TEST SUMMARY ===")
    logger.info(f"Concurrent Users: {summary['test_config']['concurrent_users']}")
    logger.info(
        f"Total Duration: {summary['timing']['total_duration_seconds']:.2f} seconds"
    )
    logger.info(
        f"Session Success Rate: {summary['session_results']['session_success_rate']:.1f}%"
    )
    logger.info(
        f"Operation Success Rate: {summary['operation_results']['operation_success_rate']:.1f}%"
    )
    logger.info(
        f"Average Response Time: {summary['performance_metrics']['avg_response_time_ms']:.2f} ms"
    )
    logger.info(
        f"Operations per Second: {summary['performance_metrics']['operations_per_second']:.2f}"
    )

    logger.info("\n=== OPERATION BREAKDOWN ===")
    for op_name, stats in summary["operation_breakdown"].items():
        logger.info(
            f"{op_name}: {stats['success_rate']:.1f}% success, {stats['avg_time']:.2f}ms avg"
        )

    logger.info("Detailed results saved to concurrent_load_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
