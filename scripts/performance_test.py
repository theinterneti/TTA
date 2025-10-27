# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Performance Testing Script for TTA Core Gameplay Loop

This script performs load testing and performance validation
for the integrated gameplay loop system.
"""

import asyncio
import logging
import statistics
import time
from typing import Any

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameplayPerformanceTester:
    """Performance tester for gameplay loop system."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = "test-token"  # Would be real JWT in production

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_health_endpoint(self) -> dict[str, Any]:
        """Test health endpoint performance."""
        logger.info("Testing health endpoint performance...")

        response_times = []
        for _i in range(100):
            start_time = time.time()
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/health"
            ) as response:
                await response.text()
                response_times.append(time.time() - start_time)

        return {
            "endpoint": "health",
            "requests": 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[
                18
            ],  # 95th percentile
            "target_met": statistics.mean(response_times) < 0.1,  # 100ms target
        }

    async def test_session_creation_performance(self) -> dict[str, Any]:
        """Test session creation performance."""
        logger.info("Testing session creation performance...")

        response_times = []
        success_count = 0

        for _i in range(50):  # Fewer requests for session creation
            start_time = time.time()
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/gameplay/sessions",
                    json={"therapeutic_context": {"goals": ["test"]}},
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                ) as response:
                    if response.status == 200:
                        success_count += 1
                    response_times.append(time.time() - start_time)
            except Exception as e:
                logger.warning(f"Request failed: {e}")
                response_times.append(time.time() - start_time)

        return {
            "endpoint": "session_creation",
            "requests": 50,
            "success_rate": success_count / 50,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18]
            if len(response_times) >= 20
            else max(response_times),
            "target_met": statistics.mean(response_times) < 1.0,  # 1 second target
        }

    async def test_concurrent_sessions(self) -> dict[str, Any]:
        """Test concurrent session handling."""
        logger.info("Testing concurrent session handling...")

        async def create_session():
            start_time = time.time()
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/gameplay/sessions",
                    json={"therapeutic_context": {"goals": ["concurrent_test"]}},
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                ) as response:
                    success = response.status == 200
                    return time.time() - start_time, success
            except Exception:
                return time.time() - start_time, False

        # Create 20 concurrent sessions
        tasks = [create_session() for _ in range(20)]
        results = await asyncio.gather(*tasks)

        response_times = [r[0] for r in results]
        success_count = sum(1 for r in results if r[1])

        return {
            "endpoint": "concurrent_sessions",
            "concurrent_requests": 20,
            "success_rate": success_count / 20,
            "avg_response_time": statistics.mean(response_times),
            "max_response_time": max(response_times),
            "all_completed_under_5s": max(response_times) < 5.0,
        }

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all performance tests."""
        logger.info("Starting comprehensive performance testing...")

        results = {}

        # Test 1: Health endpoint
        results["health"] = await self.test_health_endpoint()

        # Test 2: Session creation
        results["session_creation"] = await self.test_session_creation_performance()

        # Test 3: Concurrent sessions
        results["concurrent_sessions"] = await self.test_concurrent_sessions()

        # Overall assessment
        results["overall"] = {
            "health_target_met": results["health"]["target_met"],
            "session_creation_target_met": results["session_creation"]["target_met"],
            "concurrent_handling_ok": results["concurrent_sessions"][
                "all_completed_under_5s"
            ],
            "overall_performance": "PASS"
            if all(
                [
                    results["health"]["target_met"],
                    results["session_creation"]["target_met"],
                    results["concurrent_sessions"]["all_completed_under_5s"],
                ]
            )
            else "NEEDS_OPTIMIZATION",
        }

        return results


async def main():
    """Main performance testing function."""
    logger.info("=" * 60)
    logger.info("TTA GAMEPLAY LOOP - PERFORMANCE TESTING")
    logger.info("=" * 60)

    async with GameplayPerformanceTester() as tester:
        results = await tester.run_all_tests()

        # Display results
        logger.info("\n" + "=" * 60)
        logger.info("PERFORMANCE TEST RESULTS")
        logger.info("=" * 60)

        for test_name, test_results in results.items():
            if test_name == "overall":
                continue

            logger.info(f"\n{test_name.upper()} TEST:")
            for key, value in test_results.items():
                if isinstance(value, float):
                    logger.info(f"  {key}: {value:.3f}s")
                else:
                    logger.info(f"  {key}: {value}")

        # Overall results
        overall = results["overall"]
        logger.info(f"\nOVERALL PERFORMANCE: {overall['overall_performance']}")

        if overall["overall_performance"] == "PASS":
            logger.info("✅ All performance targets met!")
        else:
            logger.warning("⚠️  Some performance targets not met - optimization needed")

        return overall["overall_performance"] == "PASS"


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
