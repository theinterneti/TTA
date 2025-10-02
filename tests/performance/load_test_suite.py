"""
Comprehensive Load Testing Suite for TTA Storytelling Platform
Tests performance under realistic healthcare usage scenarios
"""

import asyncio
import csv
import json
import logging
import random
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result data"""

    test_name: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: str
    session_id: str | None = None
    error_message: str | None = None


@dataclass
class LoadTestConfig:
    """Load test configuration"""

    base_url: str = "https://api-staging.tta-platform.com"
    concurrent_users: int = 50
    test_duration_minutes: int = 10
    ramp_up_time_seconds: int = 60
    think_time_seconds: int = 2
    max_response_time_ms: int = 2000
    success_rate_threshold: float = 0.99


class TTALoadTester:
    """Comprehensive load testing for TTA platform"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: list[TestResult] = []
        self.session_pool: list[aiohttp.ClientSession] = []
        self.test_users: list[dict[str, Any]] = []

    async def initialize(self):
        """Initialize test environment and user pool"""
        logger.info("Initializing load test environment...")

        # Create test users
        await self._create_test_users()

        # Initialize session pool
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        for _ in range(self.config.concurrent_users):
            session = aiohttp.ClientSession(
                connector=connector, timeout=aiohttp.ClientTimeout(total=30)
            )
            self.session_pool.append(session)

        logger.info(
            f"Initialized {len(self.test_users)} test users and {len(self.session_pool)} sessions"
        )

    async def _create_test_users(self):
        """Create test user accounts for load testing"""
        for i in range(self.config.concurrent_users):
            user = {
                "user_id": f"load_test_user_{i:04d}",
                "email": f"loadtest{i:04d}@tta-testing.com",
                "role": "patient" if i % 4 != 0 else "clinician",
                "therapeutic_framework": random.choice(
                    ["CBT", "DBT", "Narrative", "Mindfulness"]
                ),
                "session_count": 0,
                "auth_token": f"test_token_{i:04d}",
            }
            self.test_users.append(user)

    async def run_load_test(self) -> dict[str, Any]:
        """Execute comprehensive load test"""
        logger.info(
            f"Starting load test with {self.config.concurrent_users} concurrent users"
        )

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=self.config.test_duration_minutes)

        # Create user simulation tasks
        tasks = []
        for i, user in enumerate(self.test_users):
            # Stagger user start times for ramp-up
            delay = (i / len(self.test_users)) * self.config.ramp_up_time_seconds
            task = asyncio.create_task(
                self._simulate_user_journey(user, delay, end_time)
            )
            tasks.append(task)

        # Wait for all user simulations to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Generate test report
        report = await self._generate_test_report()

        # Cleanup
        await self._cleanup()

        return report

    async def _simulate_user_journey(
        self, user: dict[str, Any], delay: float, end_time: datetime
    ):
        """Simulate realistic user journey through the platform"""
        await asyncio.sleep(delay)

        session = self.session_pool[self.test_users.index(user)]

        try:
            if user["role"] == "patient":
                await self._simulate_patient_journey(user, session, end_time)
            else:
                await self._simulate_clinician_journey(user, session, end_time)
        except Exception as e:
            logger.error(f"Error in user journey for {user['user_id']}: {str(e)}")

    async def _simulate_patient_journey(
        self, user: dict[str, Any], session: aiohttp.ClientSession, end_time: datetime
    ):
        """Simulate patient user journey"""
        while datetime.utcnow() < end_time:
            try:
                # 1. Login/Authentication
                await self._test_endpoint(
                    session,
                    "POST",
                    "/api/auth/login",
                    data={"email": user["email"], "password": "test_password"},
                    test_name="patient_login",
                    user_id=user["user_id"],
                )

                # 2. Create therapeutic session
                session_response = await self._test_endpoint(
                    session,
                    "POST",
                    "/api/patient/sessions",
                    data={
                        "patient_id": user["user_id"],
                        "therapeutic_framework": user["therapeutic_framework"],
                        "initial_difficulty": random.randint(1, 5),
                    },
                    test_name="create_session",
                    user_id=user["user_id"],
                )

                if session_response and session_response.get("id"):
                    session_id = session_response["id"]
                    user["session_count"] += 1

                    # 3. Simulate therapeutic gaming session
                    await self._simulate_gaming_session(
                        user, session, session_id, end_time
                    )

                # Think time between major actions
                await asyncio.sleep(
                    random.uniform(1, self.config.think_time_seconds * 2)
                )

            except Exception as e:
                logger.error(f"Error in patient journey: {str(e)}")
                await asyncio.sleep(5)  # Error recovery delay

    async def _simulate_gaming_session(
        self,
        user: dict[str, Any],
        session: aiohttp.ClientSession,
        session_id: str,
        end_time: datetime,
    ):
        """Simulate therapeutic gaming session interactions"""
        gaming_actions = [
            "make_choice",
            "view_progress",
            "interact_character",
            "update_emotional_state",
            "request_intervention",
        ]

        session_duration = random.randint(300, 1800)  # 5-30 minutes
        session_end = min(
            datetime.utcnow() + timedelta(seconds=session_duration), end_time
        )

        while datetime.utcnow() < session_end:
            action = random.choice(gaming_actions)

            if action == "make_choice":
                await self._test_endpoint(
                    session,
                    "POST",
                    f"/api/patient/sessions/{session_id}/choices",
                    data={
                        "choice_id": f"choice_{random.randint(1, 100)}",
                        "choice_text": "I want to explore this path",
                        "emotional_impact": random.uniform(-1, 1),
                    },
                    test_name="make_choice",
                    user_id=user["user_id"],
                    session_id=session_id,
                )

            elif action == "view_progress":
                await self._test_endpoint(
                    session,
                    "GET",
                    f"/api/patient/sessions/{session_id}/progress",
                    test_name="view_progress",
                    user_id=user["user_id"],
                    session_id=session_id,
                )

            elif action == "interact_character":
                await self._test_endpoint(
                    session,
                    "POST",
                    f"/api/patient/sessions/{session_id}/interactions",
                    data={
                        "character_id": f"char_{random.randint(1, 10)}",
                        "interaction_type": "conversation",
                        "message": "How are you feeling today?",
                    },
                    test_name="interact_character",
                    user_id=user["user_id"],
                    session_id=session_id,
                )

            elif action == "update_emotional_state":
                await self._test_endpoint(
                    session,
                    "PATCH",
                    f"/api/patient/sessions/{session_id}/emotional-state",
                    data={
                        "valence": random.uniform(-1, 1),
                        "arousal": random.uniform(0, 1),
                        "dominance": random.uniform(0, 1),
                    },
                    test_name="update_emotional_state",
                    user_id=user["user_id"],
                    session_id=session_id,
                )

            elif action == "request_intervention":
                # Simulate occasional intervention requests
                if random.random() < 0.1:  # 10% chance
                    await self._test_endpoint(
                        session,
                        "POST",
                        f"/api/patient/sessions/{session_id}/interventions",
                        data={
                            "intervention_type": random.choice(
                                [
                                    "emotional_support",
                                    "skill_building",
                                    "crisis_support",
                                ]
                            ),
                            "urgency": random.choice(["low", "medium", "high"]),
                        },
                        test_name="request_intervention",
                        user_id=user["user_id"],
                        session_id=session_id,
                    )

            # Short think time between gaming actions
            await asyncio.sleep(random.uniform(0.5, 2.0))

    async def _simulate_clinician_journey(
        self, user: dict[str, Any], session: aiohttp.ClientSession, end_time: datetime
    ):
        """Simulate clinician user journey"""
        while datetime.utcnow() < end_time:
            try:
                # 1. Login/Authentication
                await self._test_endpoint(
                    session,
                    "POST",
                    "/api/auth/login",
                    data={"email": user["email"], "password": "test_password"},
                    test_name="clinician_login",
                    user_id=user["user_id"],
                )

                # 2. View clinical dashboard
                await self._test_endpoint(
                    session,
                    "GET",
                    f"/api/clinical/dashboard/{user['user_id']}",
                    test_name="view_dashboard",
                    user_id=user["user_id"],
                )

                # 3. Monitor patient alerts
                await self._test_endpoint(
                    session,
                    "GET",
                    "/api/clinical/alerts",
                    params={"clinician_id": user["user_id"], "status": "active"},
                    test_name="monitor_alerts",
                    user_id=user["user_id"],
                )

                # 4. Review patient progress
                patient_ids = [
                    f"load_test_user_{i:04d}" for i in range(0, len(self.test_users), 4)
                ]
                for patient_id in random.sample(patient_ids, min(5, len(patient_ids))):
                    await self._test_endpoint(
                        session,
                        "GET",
                        f"/api/clinical/patients/{patient_id}/progress",
                        test_name="review_patient_progress",
                        user_id=user["user_id"],
                    )

                # 5. Acknowledge alerts (occasionally)
                if random.random() < 0.3:  # 30% chance
                    await self._test_endpoint(
                        session,
                        "PATCH",
                        f"/api/clinical/alerts/{random.randint(1, 100)}/acknowledge",
                        test_name="acknowledge_alert",
                        user_id=user["user_id"],
                    )

                # Think time between major actions
                await asyncio.sleep(
                    random.uniform(5, self.config.think_time_seconds * 3)
                )

            except Exception as e:
                logger.error(f"Error in clinician journey: {str(e)}")
                await asyncio.sleep(5)

    async def _test_endpoint(
        self,
        session: aiohttp.ClientSession,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
        test_name: str = "",
        user_id: str = "",
        session_id: str | None = None,
    ) -> dict | None:
        """Test individual API endpoint and record results"""
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
        }

        start_time = time.time()
        success = False
        status_code = 0
        error_message = None
        response_data = None

        try:
            async with session.request(
                method=method, url=url, json=data, params=params, headers=headers
            ) as response:
                status_code = response.status
                response_time = (
                    time.time() - start_time
                ) * 1000  # Convert to milliseconds
                success = 200 <= status_code < 400

                if success:
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = await response.text()
                else:
                    error_message = await response.text()

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_message = str(e)
            success = False

        # Record test result
        result = TestResult(
            test_name=test_name,
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            success=success,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            error_message=error_message,
        )

        self.results.append(result)

        # Log slow responses
        if response_time > self.config.max_response_time_ms:
            logger.warning(f"Slow response: {test_name} took {response_time:.2f}ms")

        return response_data

    async def _generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.results:
            return {"error": "No test results available"}

        # Calculate basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0

        response_times = [r.response_time for r in self.results]
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) > 20
            else max(response_times)
        )
        p99_response_time = (
            statistics.quantiles(response_times, n=100)[98]
            if len(response_times) > 100
            else max(response_times)
        )

        # Group results by test type
        test_stats = {}
        for result in self.results:
            if result.test_name not in test_stats:
                test_stats[result.test_name] = {
                    "total": 0,
                    "successful": 0,
                    "response_times": [],
                }

            test_stats[result.test_name]["total"] += 1
            if result.success:
                test_stats[result.test_name]["successful"] += 1
            test_stats[result.test_name]["response_times"].append(result.response_time)

        # Calculate per-test statistics
        for _, stats in test_stats.items():
            stats["success_rate"] = (
                stats["successful"] / stats["total"] if stats["total"] > 0 else 0
            )
            stats["avg_response_time"] = (
                statistics.mean(stats["response_times"])
                if stats["response_times"]
                else 0
            )
            stats["median_response_time"] = (
                statistics.median(stats["response_times"])
                if stats["response_times"]
                else 0
            )

        # Identify errors
        errors = [r for r in self.results if not r.success]
        error_summary = {}
        for error in errors:
            key = f"{error.status_code}: {error.error_message[:100] if error.error_message else 'Unknown error'}"
            error_summary[key] = error_summary.get(key, 0) + 1

        report = {
            "test_summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "test_passed": success_rate >= self.config.success_rate_threshold,
            },
            "performance_metrics": {
                "avg_response_time_ms": avg_response_time,
                "median_response_time_ms": median_response_time,
                "p95_response_time_ms": p95_response_time,
                "p99_response_time_ms": p99_response_time,
                "performance_passed": p95_response_time
                <= self.config.max_response_time_ms,
            },
            "test_breakdown": test_stats,
            "error_summary": error_summary,
            "configuration": asdict(self.config),
        }

        # Save detailed results to CSV
        await self._save_results_to_csv()

        # Generate performance charts
        await self._generate_performance_charts()

        logger.info(
            f"Load test completed: {success_rate:.2%} success rate, {avg_response_time:.2f}ms avg response time"
        )

        return report

    async def _save_results_to_csv(self):
        """Save detailed test results to CSV file"""
        filename = (
            f"load_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "test_name",
                "endpoint",
                "method",
                "response_time",
                "status_code",
                "success",
                "timestamp",
                "user_id",
                "session_id",
                "error_message",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                writer.writerow(asdict(result))

        logger.info(f"Detailed results saved to {filename}")

    async def _generate_performance_charts(self):
        """Generate performance visualization charts"""
        if not self.results:
            return

        # Response time distribution
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 2, 1)
        response_times = [r.response_time for r in self.results]
        plt.hist(response_times, bins=50, alpha=0.7)
        plt.title("Response Time Distribution")
        plt.xlabel("Response Time (ms)")
        plt.ylabel("Frequency")

        # Response time over time
        plt.subplot(2, 2, 2)
        timestamps = [r.timestamp for r in self.results]
        plt.plot(timestamps, response_times, alpha=0.6)
        plt.title("Response Time Over Time")
        plt.xlabel("Time")
        plt.ylabel("Response Time (ms)")
        plt.xticks(rotation=45)

        # Success rate by test type
        plt.subplot(2, 2, 3)
        test_names = list(set(r.test_name for r in self.results))
        success_rates = []
        for test_name in test_names:
            test_results = [r for r in self.results if r.test_name == test_name]
            success_rate = sum(1 for r in test_results if r.success) / len(test_results)
            success_rates.append(success_rate)

        plt.bar(test_names, success_rates)
        plt.title("Success Rate by Test Type")
        plt.xlabel("Test Type")
        plt.ylabel("Success Rate")
        plt.xticks(rotation=45)

        # Status code distribution
        plt.subplot(2, 2, 4)
        status_codes = [r.status_code for r in self.results]
        unique_codes = list(set(status_codes))
        code_counts = [status_codes.count(code) for code in unique_codes]

        plt.bar([str(code) for code in unique_codes], code_counts)
        plt.title("HTTP Status Code Distribution")
        plt.xlabel("Status Code")
        plt.ylabel("Count")

        plt.tight_layout()

        chart_filename = (
            f"load_test_charts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        )
        plt.savefig(chart_filename, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Performance charts saved to {chart_filename}")

    async def _cleanup(self):
        """Cleanup resources"""
        for session in self.session_pool:
            await session.close()

        logger.info("Load test cleanup completed")


# Test execution functions
async def run_standard_load_test():
    """Run standard load test configuration"""
    config = LoadTestConfig(
        concurrent_users=50, test_duration_minutes=10, ramp_up_time_seconds=60
    )

    tester = TTALoadTester(config)
    await tester.initialize()

    report = await tester.run_load_test()

    print("\n" + "=" * 80)
    print("LOAD TEST REPORT")
    print("=" * 80)
    print(json.dumps(report, indent=2, default=str))

    return report


async def run_stress_test():
    """Run stress test with high load"""
    config = LoadTestConfig(
        concurrent_users=200,
        test_duration_minutes=15,
        ramp_up_time_seconds=120,
        max_response_time_ms=5000,
    )

    tester = TTALoadTester(config)
    await tester.initialize()

    report = await tester.run_load_test()

    print("\n" + "=" * 80)
    print("STRESS TEST REPORT")
    print("=" * 80)
    print(json.dumps(report, indent=2, default=str))

    return report


if __name__ == "__main__":
    # Run standard load test
    asyncio.run(run_standard_load_test())
