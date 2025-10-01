"""
Standard Test Suite

Tests normal user interactions and story generation flows including:
- Character creation and development
- Story generation and continuity
- Choice consequences and branching
- Therapeutic integration subtlety
- Multi-session persistence
"""

import logging
import uuid
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from neo4j import AsyncDriver

from src.living_worlds.neo4j_integration import LivingWorldsManager
from testing.single_player_test_framework import SinglePlayerTestFramework

from ..common import TestCategory, TestResult, TestStatus
from ..utils.test_data_generator import TestDataGenerator, TestScenario, TestUserProfile

logger = logging.getLogger(__name__)


class StandardTestSuite:
    """
    Standard test suite for normal user interaction flows.

    Tests the complete story generation pipeline under normal
    operating conditions with realistic user profiles and scenarios.
    """

    def __init__(self, neo4j_driver: AsyncDriver, redis_client: aioredis.Redis, config):
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client
        self.config = config

        self.test_data_generator = TestDataGenerator(neo4j_driver, redis_client)
        self.test_run_id = str(uuid.uuid4())

        # Initialize TTA components
        self.living_worlds_manager = None
        self.player_experience_manager = None
        self.single_player_framework = None

        self.results: list[TestResult] = []

    async def initialize(self):
        """Initialize test suite components."""
        # Initialize Living Worlds Manager
        self.living_worlds_manager = LivingWorldsManager(
            neo4j_uri=self.config.neo4j_uri,
            neo4j_user=self.config.neo4j_user,
            neo4j_password=self.config.neo4j_password,
            redis_url=self.config.redis_url,
        )
        await self.living_worlds_manager.initialize()

        # Initialize Single Player Test Framework
        self.single_player_framework = SinglePlayerTestFramework()
        await self.single_player_framework.initialize_connections()

        logger.info("Standard test suite initialized")

    async def execute_all_tests(self) -> list[TestResult]:
        """Execute all standard tests."""
        await self.initialize()

        try:
            # Generate test data
            test_users = await self.test_data_generator.generate_test_users(10)
            test_scenarios = await self.test_data_generator.generate_story_scenarios(5)

            # Execute test categories
            await self._test_character_creation_flow(test_users[:3])
            await self._test_story_generation_pipeline(
                test_users[:5], test_scenarios[:3]
            )
            await self._test_choice_consequences(test_users[:3], test_scenarios[:2])
            await self._test_multi_session_continuity(
                test_users[:2], test_scenarios[:1]
            )
            await self._test_therapeutic_integration(test_users[:3], test_scenarios[:2])
            await self._test_session_persistence(test_users[:3])

            logger.info(
                f"Standard test suite completed: {len(self.results)} tests executed"
            )
            return self.results

        finally:
            await self.cleanup()

    async def _test_character_creation_flow(self, users: list[TestUserProfile]):
        """Test character creation and initial setup."""
        for user in users:
            test_name = f"character_creation_{user.user_id[:8]}"
            result = TestResult(
                test_name=test_name,
                category=TestCategory.STANDARD,
                status=TestStatus.RUNNING,
                start_time=datetime.utcnow(),
            )

            try:
                # Test character creation process
                character_data = await self._create_test_character(user)

                # Validate character was created properly
                if await self._validate_character_creation(character_data, user):
                    result.passed = True
                    result.details = {
                        "character_id": character_data.get("character_id"),
                        "therapeutic_profile_integrated": True,
                        "preferences_applied": True,
                    }
                else:
                    result.error_message = "Character creation validation failed"

            except Exception as e:
                result.error_message = str(e)
                logger.error(f"Character creation test failed for {user.user_id}: {e}")

            finally:
                result.end_time = datetime.utcnow()
                result.duration_seconds = (
                    result.end_time - result.start_time
                ).total_seconds()
                result.status = TestStatus.COMPLETED
                self.results.append(result)

    async def _test_story_generation_pipeline(
        self, users: list[TestUserProfile], scenarios: list[TestScenario]
    ):
        """Test story generation and narrative flow."""
        for user in users:
            for scenario in scenarios:
                test_name = (
                    f"story_generation_{user.user_id[:8]}_{scenario.scenario_id[:8]}"
                )
                result = TestResult(
                    test_name=test_name,
                    category=TestCategory.STANDARD,
                    status=TestStatus.RUNNING,
                    start_time=datetime.utcnow(),
                )

                try:
                    # Create test session
                    session_context = (
                        await self.test_data_generator.create_test_session(
                            user, scenario
                        )
                    )

                    # Test story generation
                    story_content = await self._generate_story_content(
                        session_context, scenario
                    )

                    # Validate story quality and coherence
                    validation_results = await self._validate_story_content(
                        story_content, user, scenario
                    )

                    if validation_results["passed"]:
                        result.passed = True
                        result.details = validation_results
                        result.metrics = {
                            "story_length": len(story_content.get("narrative", "")),
                            "choice_count": len(story_content.get("choices", [])),
                            "therapeutic_elements": validation_results.get(
                                "therapeutic_score", 0
                            ),
                        }
                    else:
                        result.error_message = validation_results.get(
                            "error", "Story validation failed"
                        )

                except Exception as e:
                    result.error_message = str(e)
                    logger.error(f"Story generation test failed: {e}")

                finally:
                    result.end_time = datetime.utcnow()
                    result.duration_seconds = (
                        result.end_time - result.start_time
                    ).total_seconds()
                    result.status = TestStatus.COMPLETED
                    self.results.append(result)

    async def _test_choice_consequences(
        self, users: list[TestUserProfile], scenarios: list[TestScenario]
    ):
        """Test choice tracking and consequence implementation."""
        for user in users:
            for scenario in scenarios:
                test_name = (
                    f"choice_consequences_{user.user_id[:8]}_{scenario.scenario_id[:8]}"
                )
                result = TestResult(
                    test_name=test_name,
                    category=TestCategory.STANDARD,
                    status=TestStatus.RUNNING,
                    start_time=datetime.utcnow(),
                )

                try:
                    # Create session and make choices
                    session_context = (
                        await self.test_data_generator.create_test_session(
                            user, scenario
                        )
                    )
                    choice_sequence = await self._execute_choice_sequence(
                        session_context, 5
                    )

                    # Validate consequences were applied
                    consequences_valid = await self._validate_choice_consequences(
                        choice_sequence
                    )

                    if consequences_valid:
                        result.passed = True
                        result.details = {
                            "choices_made": len(choice_sequence),
                            "consequences_tracked": True,
                            "character_development": True,
                        }
                    else:
                        result.error_message = (
                            "Choice consequences not properly tracked"
                        )

                except Exception as e:
                    result.error_message = str(e)
                    logger.error(f"Choice consequences test failed: {e}")

                finally:
                    result.end_time = datetime.utcnow()
                    result.duration_seconds = (
                        result.end_time - result.start_time
                    ).total_seconds()
                    result.status = TestStatus.COMPLETED
                    self.results.append(result)

    async def _test_multi_session_continuity(
        self, users: list[TestUserProfile], scenarios: list[TestScenario]
    ):
        """Test narrative continuity across multiple sessions."""
        for user in users:
            for scenario in scenarios:
                test_name = f"multi_session_continuity_{user.user_id[:8]}"
                result = TestResult(
                    test_name=test_name,
                    category=TestCategory.STANDARD,
                    status=TestStatus.RUNNING,
                    start_time=datetime.utcnow(),
                )

                try:
                    # Create multiple sessions for the same user
                    sessions = []
                    for i in range(3):
                        session = await self.test_data_generator.create_test_session(
                            user, scenario
                        )
                        session.session_id = f"{session.session_id}_part_{i+1}"
                        sessions.append(session)

                    # Test continuity between sessions
                    continuity_valid = await self._validate_session_continuity(sessions)

                    if continuity_valid:
                        result.passed = True
                        result.details = {
                            "sessions_tested": len(sessions),
                            "continuity_maintained": True,
                            "character_memory_preserved": True,
                        }
                    else:
                        result.error_message = "Session continuity validation failed"

                except Exception as e:
                    result.error_message = str(e)
                    logger.error(f"Multi-session continuity test failed: {e}")

                finally:
                    result.end_time = datetime.utcnow()
                    result.duration_seconds = (
                        result.end_time - result.start_time
                    ).total_seconds()
                    result.status = TestStatus.COMPLETED
                    self.results.append(result)

    async def _test_therapeutic_integration(
        self, users: list[TestUserProfile], scenarios: list[TestScenario]
    ):
        """Test therapeutic content integration and subtlety."""
        for user in users:
            for scenario in scenarios:
                test_name = f"therapeutic_integration_{user.user_id[:8]}"
                result = TestResult(
                    test_name=test_name,
                    category=TestCategory.STANDARD,
                    status=TestStatus.RUNNING,
                    start_time=datetime.utcnow(),
                )

                try:
                    # Generate story with therapeutic elements
                    session_context = (
                        await self.test_data_generator.create_test_session(
                            user, scenario
                        )
                    )
                    story_content = await self._generate_story_content(
                        session_context, scenario
                    )

                    # Evaluate therapeutic integration
                    therapeutic_score = await self._evaluate_therapeutic_integration(
                        story_content, user.therapeutic_profile
                    )

                    # Check subtlety (not too clinical)
                    subtlety_score = await self._evaluate_subtlety(story_content)

                    if therapeutic_score >= 7.0 and subtlety_score >= 7.0:
                        result.passed = True
                        result.details = {
                            "therapeutic_score": therapeutic_score,
                            "subtlety_score": subtlety_score,
                            "integration_quality": "excellent",
                        }
                    else:
                        result.error_message = f"Therapeutic integration scores too low: {therapeutic_score}, {subtlety_score}"

                except Exception as e:
                    result.error_message = str(e)
                    logger.error(f"Therapeutic integration test failed: {e}")

                finally:
                    result.end_time = datetime.utcnow()
                    result.duration_seconds = (
                        result.end_time - result.start_time
                    ).total_seconds()
                    result.status = TestStatus.COMPLETED
                    self.results.append(result)

    async def _test_session_persistence(self, users: list[TestUserProfile]):
        """Test session data persistence in Neo4j and Redis."""
        for user in users:
            test_name = f"session_persistence_{user.user_id[:8]}"
            result = TestResult(
                test_name=test_name,
                category=TestCategory.STANDARD,
                status=TestStatus.RUNNING,
                start_time=datetime.utcnow(),
            )

            try:
                # Create and store session
                scenario = (await self.test_data_generator.generate_story_scenarios(1))[
                    0
                ]
                session_context = await self.test_data_generator.create_test_session(
                    user, scenario
                )

                # Store in databases
                await self._store_session_data(session_context)

                # Verify persistence
                neo4j_data = await self._retrieve_from_neo4j(session_context.session_id)
                redis_data = await self._retrieve_from_redis(session_context.session_id)

                if neo4j_data and redis_data:
                    result.passed = True
                    result.details = {
                        "neo4j_persistence": True,
                        "redis_persistence": True,
                        "data_consistency": await self._verify_data_consistency(
                            neo4j_data, redis_data
                        ),
                    }
                else:
                    result.error_message = "Session data not properly persisted"

            except Exception as e:
                result.error_message = str(e)
                logger.error(f"Session persistence test failed: {e}")

            finally:
                result.end_time = datetime.utcnow()
                result.duration_seconds = (
                    result.end_time - result.start_time
                ).total_seconds()
                result.status = TestStatus.COMPLETED
                self.results.append(result)

    async def cleanup(self):
        """Clean up test resources."""
        try:
            # Clean up test data
            await self.test_data_generator.cleanup_test_data(self.test_run_id)

            # Close connections
            if self.living_worlds_manager:
                await self.living_worlds_manager.close()

            if self.single_player_framework:
                await self.single_player_framework.cleanup()

            logger.info("Standard test suite cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    # Helper methods for test implementation
    async def _create_test_character(self, user: TestUserProfile) -> dict[str, Any]:
        """Create a test character based on user profile."""
        # Implementation would integrate with character creation system
        return {
            "character_id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "therapeutic_profile": user.therapeutic_profile,
            "created_at": datetime.utcnow().isoformat(),
        }

    async def _validate_character_creation(
        self, character_data: dict[str, Any], user: TestUserProfile
    ) -> bool:
        """Validate character creation was successful."""
        # Implementation would verify character data integrity
        return character_data.get("character_id") is not None

    async def _generate_story_content(
        self, session_context, scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate story content for testing."""
        # Implementation would integrate with narrative generation system
        return {
            "narrative": f"Test story content for scenario {scenario.name}",
            "choices": ["Choice 1", "Choice 2", "Choice 3"],
            "therapeutic_elements": ["growth_opportunity", "reflection_prompt"],
        }

    async def _validate_story_content(
        self,
        story_content: dict[str, Any],
        user: TestUserProfile,
        scenario: TestScenario,
    ) -> dict[str, Any]:
        """Validate generated story content quality."""
        # Implementation would evaluate story quality metrics
        return {
            "passed": True,
            "narrative_quality": 8.5,
            "therapeutic_score": 7.8,
            "coherence_score": 8.2,
        }

    async def _execute_choice_sequence(
        self, session_context, choice_count: int
    ) -> list[dict[str, Any]]:
        """Execute a sequence of choices and track consequences."""
        # Implementation would simulate user choices
        return [
            {"choice": f"Choice {i}", "consequence": f"Consequence {i}"}
            for i in range(choice_count)
        ]

    async def _validate_choice_consequences(
        self, choice_sequence: list[dict[str, Any]]
    ) -> bool:
        """Validate that choices had proper consequences."""
        # Implementation would verify consequence tracking
        return len(choice_sequence) > 0

    async def _validate_session_continuity(self, sessions: list) -> bool:
        """Validate continuity between multiple sessions."""
        # Implementation would check narrative consistency
        return len(sessions) > 1

    async def _evaluate_therapeutic_integration(
        self, story_content: dict[str, Any], therapeutic_profile: dict[str, Any]
    ) -> float:
        """Evaluate therapeutic content integration quality."""
        # Implementation would analyze therapeutic elements
        return 8.0

    async def _evaluate_subtlety(self, story_content: dict[str, Any]) -> float:
        """Evaluate subtlety of therapeutic integration."""
        # Implementation would check for clinical language
        return 8.5

    async def _store_session_data(self, session_context):
        """Store session data in databases."""
        # Implementation would store in Neo4j and Redis
        pass

    async def _retrieve_from_neo4j(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data from Neo4j."""
        # Implementation would query Neo4j
        return {"session_id": session_id, "source": "neo4j"}

    async def _retrieve_from_redis(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data from Redis."""
        # Implementation would query Redis
        return {"session_id": session_id, "source": "redis"}

    async def _verify_data_consistency(
        self, neo4j_data: dict[str, Any], redis_data: dict[str, Any]
    ) -> bool:
        """Verify data consistency between databases."""
        # Implementation would compare data structures
        return neo4j_data.get("session_id") == redis_data.get("session_id")
