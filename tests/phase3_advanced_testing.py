#!/usr/bin/env python3
"""
Phase 3: Advanced Character Integration Testing Suite

This module provides comprehensive testing for advanced character creation scenarios,
load testing, concurrent operations, and system performance validation.
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestMetrics:
    """Metrics collection for test results."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = None
    errors: list[str] = None
    start_time: datetime | None = None
    end_time: datetime | None = None

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        if self.errors is None:
            self.errors = []

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)

    @property
    def p95_response_time(self) -> float:
        if len(self.response_times) < 20:
            return max(self.response_times) if self.response_times else 0.0
        return statistics.quantiles(self.response_times, n=20)[18]

    @property
    def duration_seconds(self) -> float:
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    @property
    def requests_per_second(self) -> float:
        if self.duration_seconds == 0:
            return 0.0
        return self.total_requests / self.duration_seconds


class AdvancedCharacterTester:
    """Advanced character creation testing framework."""

    def __init__(self, base_url: str = "http://localhost:8080", auth_token: str = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        connector = aiohttp.TCPConnector(limit=100)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def create_test_character(
        self, character_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a single test character."""
        start_time = time.time()

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/characters/", json=character_data
            ) as response:
                response_time = time.time() - start_time

                if response.status == 201:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_time": response_time,
                        "character_id": result.get("character_id"),
                        "data": result,
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "response_time": response_time,
                        "status": response.status,
                        "error": error_text,
                    }
        except Exception as e:
            response_time = time.time() - start_time
            return {"success": False, "response_time": response_time, "error": str(e)}

    def generate_test_character_data(self, character_id: int) -> dict[str, Any]:
        """Generate test character data with variations."""
        character_variations = [
            {
                "name": f"TestChar_Anxiety_{character_id}",
                "therapeutic_profile": {
                    "primary_concerns": ["anxiety", "stress"],
                    "preferred_intensity": "medium",
                    "therapeutic_approaches": [
                        "cognitive_behavioral_therapy",
                        "mindfulness",
                    ],
                },
            },
            {
                "name": f"TestChar_Depression_{character_id}",
                "therapeutic_profile": {
                    "primary_concerns": ["depression", "mood"],
                    "preferred_intensity": "high",
                    "therapeutic_approaches": [
                        "cognitive_behavioral_therapy",
                        "interpersonal_therapy",
                    ],
                },
            },
            {
                "name": f"TestChar_Social_{character_id}",
                "therapeutic_profile": {
                    "primary_concerns": ["social_anxiety", "relationships"],
                    "preferred_intensity": "low",
                    "therapeutic_approaches": [
                        "exposure_therapy",
                        "social_skills_training",
                    ],
                },
            },
        ]

        base_variation = character_variations[character_id % len(character_variations)]

        return {
            "name": base_variation["name"],
            "appearance": {
                "age_range": "adult",
                "gender_identity": ["male", "female", "non-binary"][character_id % 3],
                "physical_description": f"Test character {character_id} with unique traits",
                "clothing_style": ["casual", "professional", "artistic"][
                    character_id % 3
                ],
                "distinctive_features": [f"feature_{character_id}", "expressive_eyes"],
            },
            "background": {
                "name": base_variation["name"],
                "backstory": f"A test character {character_id} with specific therapeutic needs",
                "personality_traits": ["resilient", "curious", "empathetic"],
                "life_goals": ["improve_wellbeing", "build_confidence"],
            },
            "therapeutic_profile": {
                **base_variation["therapeutic_profile"],
                "therapeutic_goals": [
                    {
                        "goal_id": f"goal_{character_id}",
                        "description": f"Primary therapeutic goal for character {character_id}",
                        "target_date": "2024-12-31",
                        "progress_percentage": 0,
                        "is_active": True,
                        "therapeutic_approaches": base_variation["therapeutic_profile"][
                            "therapeutic_approaches"
                        ],
                    }
                ],
                "comfort_zones": ["journaling", "meditation"],
                "readiness_level": 0.7 + (character_id % 3) * 0.1,
            },
        }

    async def concurrent_character_creation_test(
        self,
        concurrent_users: int = 10,
        characters_per_user: int = 3,
        duration_seconds: int = 60,
    ) -> TestMetrics:
        """Test concurrent character creation scenarios."""
        logger.info(
            f"Starting concurrent character creation test: {concurrent_users} users, {characters_per_user} chars each"
        )

        metrics = TestMetrics()
        metrics.start_time = datetime.utcnow()

        async def user_workflow(user_id: int):
            """Simulate a single user creating multiple characters."""
            user_metrics = TestMetrics()

            for char_num in range(characters_per_user):
                character_data = self.generate_test_character_data(
                    user_id * 100 + char_num
                )
                result = await self.create_test_character(character_data)

                user_metrics.total_requests += 1
                user_metrics.response_times.append(result["response_time"])

                if result["success"]:
                    user_metrics.successful_requests += 1
                else:
                    user_metrics.failed_requests += 1
                    user_metrics.errors.append(result.get("error", "Unknown error"))

                # Small delay between character creations
                await asyncio.sleep(0.1)

            return user_metrics

        # Run concurrent user workflows
        tasks = [user_workflow(user_id) for user_id in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate metrics
        for result in user_results:
            if isinstance(result, TestMetrics):
                metrics.total_requests += result.total_requests
                metrics.successful_requests += result.successful_requests
                metrics.failed_requests += result.failed_requests
                metrics.response_times.extend(result.response_times)
                metrics.errors.extend(result.errors)

        metrics.end_time = datetime.utcnow()

        logger.info(
            f"Concurrent test completed: {metrics.success_rate:.2%} success rate, "
            f"{metrics.average_response_time:.2f}s avg response time"
        )

        return metrics


# Test authentication token (fresh token for Phase 3)
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlODBiMGIyNS04ZTNiLTQ0ZjAtYjQ0MS1hN2I5NmY3MTkyNzUiLCJ1c2VybmFtZSI6InRlc3R1c2VyMiIsImVtYWlsIjoidGVzdDJAZXhhbXBsZS5jb20iLCJyb2xlIjoicGxheWVyIiwicGVybWlzc2lvbnMiOlsiY3JlYXRlX2NoYXJhY3RlciIsIm1hbmFnZV9vd25fY2hhcmFjdGVycyIsImFjY2Vzc190aGVyYXBldXRpY19jb250ZW50IiwibWFuYWdlX293bl9wcm9maWxlIiwiZXhwb3J0X293bl9kYXRhIiwiZGVsZXRlX293bl9kYXRhIl0sInNlc3Npb25faWQiOiJkYzQ5ZTQ5YS1jYjM3LTQ0M2ItYWVkNy0xY2RiZWZlNmQyMmYiLCJtZmFfdmVyaWZpZWQiOmZhbHNlLCJleHAiOjE3NTY0ODcwNTh9.zAOsrpjX1cTBWw8Cj9LiWCrmkUuA6oQc_ss7QVCJibE"


class EdgeCaseTester:
    """Edge case testing functionality."""

    def __init__(self, tester: AdvancedCharacterTester):
        self.tester = tester

    async def edge_case_testing(self) -> TestMetrics:
        """Test edge cases and boundary conditions."""
        logger.info("Starting edge case and boundary testing")

        metrics = TestMetrics()
        metrics.start_time = datetime.utcnow()

        # Test cases with edge conditions
        edge_cases = [
            # Minimum length names
            {"name": "A", "expected_success": False},
            # Maximum length names
            {"name": "A" * 100, "expected_success": False},
            # Special characters in names
            {"name": "Test@Character#1", "expected_success": True},
            # Unicode characters
            {"name": "测试角色", "expected_success": True},
            # Empty therapeutic goals
            {"therapeutic_goals": [], "expected_success": True},
            # Maximum therapeutic goals
            {
                "therapeutic_goals": [f"goal_{i}" for i in range(10)],
                "expected_success": True,
            },
            # Invalid intensity levels
            {"preferred_intensity": "extreme", "expected_success": False},
            # Boundary readiness levels
            {"readiness_level": 0.0, "expected_success": True},
            {"readiness_level": 1.0, "expected_success": True},
            {"readiness_level": 1.5, "expected_success": False},
        ]

        for i, case in enumerate(edge_cases):
            character_data = self.tester.generate_test_character_data(i)

            # Apply edge case modifications
            if "name" in case:
                character_data["name"] = case["name"]
                character_data["background"]["name"] = case["name"]

            if "therapeutic_goals" in case:
                if case["therapeutic_goals"]:
                    character_data["therapeutic_profile"]["therapeutic_goals"] = [
                        {
                            "goal_id": f"edge_goal_{j}",
                            "description": goal,
                            "target_date": "2024-12-31",
                            "progress_percentage": 0,
                            "is_active": True,
                            "therapeutic_approaches": ["cognitive_behavioral_therapy"],
                        }
                        for j, goal in enumerate(case["therapeutic_goals"])
                    ]
                else:
                    character_data["therapeutic_profile"]["therapeutic_goals"] = []

            if "preferred_intensity" in case:
                character_data["therapeutic_profile"]["preferred_intensity"] = case[
                    "preferred_intensity"
                ]

            if "readiness_level" in case:
                character_data["therapeutic_profile"]["readiness_level"] = case[
                    "readiness_level"
                ]

            result = await self.tester.create_test_character(character_data)

            metrics.total_requests += 1
            metrics.response_times.append(result["response_time"])

            expected_success = case.get("expected_success", True)
            actual_success = result["success"]

            if actual_success == expected_success:
                metrics.successful_requests += 1
                logger.info(
                    f"Edge case {i}: Expected {expected_success}, got {actual_success} ✓"
                )
            else:
                metrics.failed_requests += 1
                metrics.errors.append(
                    f"Edge case {i}: Expected {expected_success}, got {actual_success}"
                )
                logger.warning(
                    f"Edge case {i}: Expected {expected_success}, got {actual_success} ✗"
                )

        metrics.end_time = datetime.utcnow()
        return metrics


async def main():
    """Main testing function."""
    async with AdvancedCharacterTester(auth_token=AUTH_TOKEN) as tester:
        print("=== Phase 3: Advanced Character Integration Testing ===\n")

        # Test 1: Edge Case Testing
        print("1. Running Edge Case and Boundary Testing...")
        edge_tester = EdgeCaseTester(tester)
        edge_metrics = await edge_tester.edge_case_testing()
        print(
            f"   Edge Cases: {edge_metrics.success_rate:.1%} success rate, "
            f"{edge_metrics.average_response_time:.3f}s avg response time"
        )

        # Test 2: Concurrent Load Testing (reduced to avoid character limit)
        print("\n2. Running Concurrent Character Creation Test...")
        concurrent_metrics = await tester.concurrent_character_creation_test(
            concurrent_users=2, characters_per_user=1, duration_seconds=15
        )
        print(
            f"   Concurrent: {concurrent_metrics.success_rate:.1%} success rate, "
            f"{concurrent_metrics.average_response_time:.3f}s avg response time"
        )

        # Summary
        print("\n=== Phase 3 Testing Summary ===")
        total_requests = edge_metrics.total_requests + concurrent_metrics.total_requests
        total_successful = (
            edge_metrics.successful_requests + concurrent_metrics.successful_requests
        )
        overall_success_rate = (
            total_successful / total_requests if total_requests > 0 else 0
        )

        print(f"Total Requests: {total_requests}")
        print(f"Overall Success Rate: {overall_success_rate:.1%}")
        print(f"Edge Case Success Rate: {edge_metrics.success_rate:.1%}")
        print(f"Concurrent Test Success Rate: {concurrent_metrics.success_rate:.1%}")

        # Show errors if any
        all_errors = edge_metrics.errors + concurrent_metrics.errors
        if all_errors:
            print(f"\nErrors ({len(all_errors)}):")
            for error in all_errors[:10]:  # Show first 10 errors
                print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(main())
