"""
Test Data Generator

Generates realistic test data for comprehensive testing including:
- User profiles and sessions
- Story content and interactions
- Malformed and edge case data
- Load testing scenarios
"""

import random
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from neo4j import AsyncDriver

from src.player_experience.models.session import SessionContext, TherapeuticSettings


@dataclass
class TestUserProfile:
    """Test user profile for comprehensive testing."""

    user_id: str
    username: str
    email: str
    age_range: str
    gaming_experience: str
    therapeutic_profile: dict[str, Any]
    preferences: dict[str, Any]
    demographics: dict[str, Any]


@dataclass
class TestScenario:
    """Test scenario configuration."""

    scenario_id: str
    name: str
    description: str
    duration_minutes: int
    steps: list[str]
    expected_outcomes: list[str]
    test_data: dict[str, Any]


class TestDataGenerator:
    """
    Generates comprehensive test data for all testing scenarios.

    Provides realistic user profiles, story content, edge cases,
    and malformed data for thorough system testing.
    """

    def __init__(self, neo4j_driver: AsyncDriver, redis_client: aioredis.Redis):
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client

        # Test data templates
        self.user_profile_templates = self._load_user_profile_templates()
        self.story_templates = self._load_story_templates()
        self.malformed_data_patterns = self._load_malformed_patterns()

    async def generate_test_users(self, count: int = 10) -> list[TestUserProfile]:
        """Generate realistic test user profiles."""
        users = []

        for i in range(count):
            user_id = str(uuid.uuid4())
            template = random.choice(self.user_profile_templates)

            user = TestUserProfile(
                user_id=user_id,
                username=f"test_user_{i}_{random.randint(1000, 9999)}",
                email=f"test{i}@example.com",
                age_range=template["demographics"]["age_range"],
                gaming_experience=template["demographics"]["gaming_experience"],
                therapeutic_profile=template["therapeutic_profile"],
                preferences=template["preferences"],
                demographics=template["demographics"],
            )
            users.append(user)

        return users

    async def generate_story_scenarios(self, count: int = 5) -> list[TestScenario]:
        """Generate story testing scenarios."""
        scenarios = []

        for i in range(count):
            template = random.choice(self.story_templates)
            scenario_id = str(uuid.uuid4())

            scenario = TestScenario(
                scenario_id=scenario_id,
                name=f"{template['name']} - Test {i+1}",
                description=template["description"],
                duration_minutes=template["duration_minutes"],
                steps=template["steps"],
                expected_outcomes=template["expected_outcomes"],
                test_data=template["test_data"],
            )
            scenarios.append(scenario)

        return scenarios

    async def generate_malformed_inputs(self) -> list[dict[str, Any]]:
        """Generate malformed and edge case inputs for adversarial testing."""
        malformed_inputs = []

        for pattern in self.malformed_data_patterns:
            malformed_inputs.extend(self._generate_from_pattern(pattern))

        return malformed_inputs

    async def generate_load_test_data(self, concurrent_users: int) -> dict[str, Any]:
        """Generate data for load testing scenarios."""
        users = await self.generate_test_users(concurrent_users)
        scenarios = await self.generate_story_scenarios(min(concurrent_users // 2, 10))

        return {
            "users": users,
            "scenarios": scenarios,
            "concurrent_sessions": concurrent_users,
            "test_duration_minutes": 10,
            "ramp_up_time_seconds": 60,
            "actions_per_user": random.randint(5, 15),
        }

    async def create_test_session(
        self, user: TestUserProfile, scenario: TestScenario
    ) -> SessionContext:
        """Create a test session context."""
        session_id = str(uuid.uuid4())

        # Create therapeutic settings based on user profile
        therapeutic_settings = TherapeuticSettings(
            intensity_level=user.therapeutic_profile.get(
                "preferred_intensity", "medium"
            ),
            preferred_approaches=user.therapeutic_profile.get(
                "preferred_approaches", ["cbt"]
            ),
            focus_areas=user.therapeutic_profile.get("challenge_areas", []),
            safety_monitoring=True,
        )

        session_context = SessionContext(
            session_id=session_id,
            player_id=user.user_id,
            character_id=str(uuid.uuid4()),
            world_id=str(uuid.uuid4()),
            therapeutic_settings=therapeutic_settings,
            start_time=datetime.utcnow(),
            is_active=True,
            metadata={
                "test_scenario": scenario.scenario_id,
                "test_type": "comprehensive_battery",
                "user_profile": user.therapeutic_profile,
            },
        )

        return session_context

    async def cleanup_test_data(self, test_run_id: str):
        """Clean up test data after test execution."""
        # Clean up Redis test data
        pattern = f"test:{test_run_id}:*"
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)

        # Clean up Neo4j test data
        async with self.neo4j_driver.session() as session:
            await session.run(
                "MATCH (n) WHERE n.test_run_id = $test_run_id DETACH DELETE n",
                test_run_id=test_run_id,
            )

    def _load_user_profile_templates(self) -> list[dict[str, Any]]:
        """Load user profile templates for test data generation."""
        return [
            {
                "name": "Creative Writer + Depression Support",
                "demographics": {
                    "age_range": "25-35",
                    "gaming_experience": "medium",
                    "creative_background": "high",
                },
                "therapeutic_profile": {
                    "primary_concerns": ["depression", "creative_blocks"],
                    "challenge_areas": ["self_worth", "motivation"],
                    "comfort_zones": ["storytelling", "character_development"],
                    "preferred_intensity": "medium",
                },
                "preferences": {
                    "narrative_style": "character_driven",
                    "pacing": "slow",
                    "interaction_frequency": "medium",
                },
            },
            {
                "name": "Gaming Enthusiast + Anxiety Management",
                "demographics": {
                    "age_range": "22-28",
                    "gaming_experience": "high",
                    "tech_comfort": "high",
                },
                "therapeutic_profile": {
                    "primary_concerns": ["anxiety", "stress_management"],
                    "challenge_areas": ["social_interaction", "uncertainty"],
                    "comfort_zones": ["fantasy_settings", "problem_solving"],
                    "preferred_intensity": "medium",
                },
                "preferences": {
                    "narrative_style": "complex",
                    "pacing": "moderate",
                    "interaction_frequency": "high",
                },
            },
            {
                "name": "Professional + Stress Management",
                "demographics": {
                    "age_range": "30-45",
                    "gaming_experience": "low",
                    "time_availability": "limited",
                },
                "therapeutic_profile": {
                    "primary_concerns": ["work_stress", "burnout"],
                    "challenge_areas": ["work_life_balance", "perfectionism"],
                    "comfort_zones": ["structured_progress", "clear_goals"],
                    "preferred_intensity": "low",
                },
                "preferences": {
                    "narrative_style": "goal_oriented",
                    "pacing": "fast",
                    "interaction_frequency": "low",
                },
            },
        ]

    def _load_story_templates(self) -> list[dict[str, Any]]:
        """Load story scenario templates."""
        return [
            {
                "name": "Character Development Journey",
                "description": "Test character progression and therapeutic integration",
                "duration_minutes": 90,
                "steps": [
                    "initial_character_state",
                    "growth_opportunities",
                    "skill_development",
                    "milestone_achievement",
                ],
                "expected_outcomes": [
                    "character_progression_tracked",
                    "therapeutic_goals_integrated",
                    "achievement_satisfaction_measured",
                ],
                "test_data": {
                    "character_attributes": ["courage", "empathy", "resilience"],
                    "growth_scenarios": [
                        "facing_fear",
                        "helping_others",
                        "overcoming_setback",
                    ],
                },
            },
            {
                "name": "Multi-Session Story Continuity",
                "description": "Test narrative coherence across multiple sessions",
                "duration_minutes": 120,
                "steps": [
                    "session_1_setup",
                    "session_2_continuation",
                    "session_3_progression",
                ],
                "expected_outcomes": [
                    "narrative_coherence_maintained",
                    "character_consistency_verified",
                    "world_persistence_confirmed",
                ],
                "test_data": {
                    "session_count": 3,
                    "continuity_elements": [
                        "character_memory",
                        "world_state",
                        "story_arc",
                    ],
                },
            },
        ]

    def _load_malformed_patterns(self) -> list[dict[str, Any]]:
        """Load malformed data patterns for adversarial testing."""
        return [
            {
                "type": "sql_injection",
                "patterns": [
                    "'; DROP TABLE users; --",
                    "' OR '1'='1",
                    "'; INSERT INTO users VALUES ('hacker', 'password'); --",
                ],
            },
            {
                "type": "xss_injection",
                "patterns": [
                    "<script>alert('XSS')</script>",
                    "javascript:alert('XSS')",
                    "<img src=x onerror=alert('XSS')>",
                ],
            },
            {
                "type": "boundary_conditions",
                "patterns": [
                    "",  # Empty string
                    "a" * 10000,  # Very long string
                    "\x00\x01\x02",  # Binary data
                    "🚀🌟💫",  # Unicode emojis
                ],
            },
            {
                "type": "json_malformed",
                "patterns": [
                    '{"incomplete": ',
                    '{"duplicate": "key", "duplicate": "value"}',
                    '{"nested": {"very": {"deeply": {"nested": "value"}}}}' * 100,
                ],
            },
        ]

    def _generate_from_pattern(self, pattern: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate test cases from a malformed data pattern."""
        test_cases = []

        for malformed_value in pattern["patterns"]:
            test_cases.append(
                {
                    "type": pattern["type"],
                    "input": malformed_value,
                    "expected_behavior": "graceful_error_handling",
                    "security_risk": pattern["type"]
                    in ["sql_injection", "xss_injection"],
                }
            )

        return test_cases
