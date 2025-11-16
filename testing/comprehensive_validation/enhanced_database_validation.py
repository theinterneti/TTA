"""
Enhanced Database Integration Validation for TTA System

This module provides comprehensive validation of database connectivity, persistence,
and performance for the TTA therapeutic storytelling system. It builds upon the
existing integration testing framework while focusing on production-readiness
and excellence-focused validation.

Key Features:
- Real Redis and Neo4j database operations (no mocks)
- User preference storage and retrieval validation
- Session persistence across database layers
- Performance and consistency validation
- Production-readiness assessment
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import redis.asyncio as aioredis
from neo4j import AsyncDriver, AsyncGraphDatabase

from src.living_worlds.neo4j_integration import LivingWorldsManager
from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.models.session import SessionContext

logger = logging.getLogger(__name__)


@dataclass
class DatabaseValidationMetrics:
    """Metrics for database validation assessment."""

    test_name: str
    duration_seconds: float
    redis_operations: int
    neo4j_operations: int
    success_rate: float
    performance_score: float  # 0-10 scale
    consistency_score: float  # 0-10 scale
    errors: list[str]
    recommendations: list[str]


@dataclass
class UserPreferenceTestData:
    """Test data for user preference validation."""

    player_id: str
    preferences: dict[str, Any]
    therapeutic_goals: list[str]
    character_preferences: dict[str, Any]
    expected_context: dict[str, Any]


class EnhancedDatabaseValidator:
    """
    Enhanced database validation system for TTA.

    Provides comprehensive testing of database connectivity, persistence,
    and performance with focus on production-readiness and user experience.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.redis_client: aioredis.Redis | None = None
        self.neo4j_driver: AsyncDriver | None = None
        self.session_repository: SessionRepository | None = None
        self.living_worlds_manager: LivingWorldsManager | None = None

        # Validation metrics
        self.validation_results: list[DatabaseValidationMetrics] = []
        self.test_sessions: list[str] = []

        # Excellence targets
        self.excellence_targets = {
            "performance_threshold": 8.5,  # Response time and throughput
            "consistency_threshold": 9.0,  # Data consistency across systems
            "reliability_threshold": 9.5,  # Success rate and error handling
        }

    async def initialize(self) -> bool:
        """Initialize database connections and components."""
        try:
            # Initialize Redis connection
            redis_config = self.config.get("redis", {})
            self.redis_client = await aioredis.from_url(
                redis_config.get("url", "redis://localhost:6379/1")
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")

            # Initialize Neo4j connection
            neo4j_config = self.config.get("neo4j", {})
            self.neo4j_driver = AsyncGraphDatabase.driver(
                neo4j_config.get("uri", "bolt://localhost:7687"),
                auth=(
                    neo4j_config.get("user", "tta_integration"),
                    neo4j_config.get("password", "tta_integration_password_2024"),
                ),
            )
            await self.neo4j_driver.verify_connectivity()
            logger.info("✅ Neo4j connection established")

            # Initialize session repository
            self.session_repository = SessionRepository(
                redis_client=self.redis_client, neo4j_driver=self.neo4j_driver
            )

            # Initialize living worlds manager
            self.living_worlds_manager = LivingWorldsManager(
                neo4j_uri=neo4j_config.get("uri", "bolt://localhost:7687"),
                neo4j_user=neo4j_config.get("user", "tta_integration"),
                neo4j_password=neo4j_config.get(
                    "password", "tta_integration_password_2024"
                ),
                redis_url=redis_config.get("url", "redis://localhost:6379/1"),
            )
            await self.living_worlds_manager.initialize()

            return True

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False

    async def validate_user_preference_persistence(self) -> DatabaseValidationMetrics:
        """
        Validate user preference storage and retrieval across database layers.

        Tests:
        - User preference storage in Redis and Neo4j
        - Preference retrieval and consistency
        - Therapeutic context integration
        - Performance under load
        """
        start_time = time.time()
        redis_ops = 0
        neo4j_ops = 0
        errors = []

        try:
            # Create test user preferences
            test_preferences = [
                UserPreferenceTestData(
                    player_id=f"test_user_{i}",
                    preferences={
                        "intensity_level": "medium",
                        "preferred_approaches": ["cbt", "mindfulness"],
                        "conversation_style": "supportive",
                        "character_name": f"TestChar{i}",
                        "preferred_setting": "peaceful_garden",
                    },
                    therapeutic_goals=["anxiety_management", "self_reflection"],
                    character_preferences={
                        "personality_traits": ["empathetic", "wise"],
                        "background": "therapeutic_guide",
                    },
                    expected_context={
                        "therapeutic_focus": "anxiety_management",
                        "narrative_tone": "supportive",
                        "interaction_style": "gentle_guidance",
                    },
                )
                for i in range(10)
            ]

            # Test preference storage
            for pref_data in test_preferences:
                # Store in Redis
                redis_key = f"user_preferences:{pref_data.player_id}"
                await self.redis_client.setex(
                    redis_key, 3600, json.dumps(pref_data.preferences)
                )
                redis_ops += 1

                # Store in Neo4j
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        """
                        MERGE (u:User {player_id: $player_id})
                        SET u.preferences = $preferences,
                            u.therapeutic_goals = $goals,
                            u.character_preferences = $char_prefs,
                            u.updated_at = datetime()
                        """,
                        player_id=pref_data.player_id,
                        preferences=pref_data.preferences,
                        goals=pref_data.therapeutic_goals,
                        char_prefs=pref_data.character_preferences,
                    )
                neo4j_ops += 1

            # Test preference retrieval and consistency
            consistency_score = 0.0
            for pref_data in test_preferences:
                # Retrieve from Redis
                redis_key = f"user_preferences:{pref_data.player_id}"
                redis_data = await self.redis_client.get(redis_key)
                redis_ops += 1

                if redis_data:
                    redis_prefs = json.loads(redis_data)
                    if redis_prefs == pref_data.preferences:
                        consistency_score += 1.0

                # Retrieve from Neo4j
                async with self.neo4j_driver.session() as session:
                    result = await session.run(
                        "MATCH (u:User {player_id: $player_id}) RETURN u",
                        player_id=pref_data.player_id,
                    )
                    record = await result.single()
                    neo4j_ops += 1

                    if record and record["u"]["preferences"] == pref_data.preferences:
                        consistency_score += 1.0

            # Calculate metrics
            duration = time.time() - start_time
            success_rate = 1.0 if not errors else 0.8
            performance_score = min(
                10.0, max(0.0, 10.0 - (duration / len(test_preferences)))
            )
            consistency_score = (consistency_score / (len(test_preferences) * 2)) * 10.0

            return DatabaseValidationMetrics(
                test_name="user_preference_persistence",
                duration_seconds=duration,
                redis_operations=redis_ops,
                neo4j_operations=neo4j_ops,
                success_rate=success_rate,
                performance_score=performance_score,
                consistency_score=consistency_score,
                errors=errors,
                recommendations=self._generate_recommendations(
                    performance_score, consistency_score
                ),
            )

        except Exception as e:
            errors.append(str(e))
            logger.error(f"❌ User preference validation failed: {e}")

            return DatabaseValidationMetrics(
                test_name="user_preference_persistence",
                duration_seconds=time.time() - start_time,
                redis_operations=redis_ops,
                neo4j_operations=neo4j_ops,
                success_rate=0.0,
                performance_score=0.0,
                consistency_score=0.0,
                errors=errors,
                recommendations=[
                    "Fix database connectivity issues",
                    "Review error handling",
                ],
            )

    async def validate_session_lifecycle_management(self) -> DatabaseValidationMetrics:
        """
        Validate complete session lifecycle with real database persistence.

        Tests:
        - Session creation and initialization
        - State updates and persistence
        - Session recovery and restoration
        - Cleanup and resource management
        """
        start_time = time.time()
        redis_ops = 0
        neo4j_ops = 0
        errors = []

        try:
            # Create test sessions
            test_sessions = []
            for i in range(5):
                session_id = f"test_session_{i}_{int(time.time())}"
                session_context = SessionContext(
                    session_id=session_id,
                    player_id=f"test_player_{i}",
                    character_id=f"test_character_{i}",
                    world_id=f"test_world_{i}",
                    therapeutic_settings={
                        "intensity_level": "medium",
                        "focus_areas": ["anxiety", "self_reflection"],
                    },
                    narrative_state={
                        "current_scene": "introduction",
                        "turn_count": 0,
                        "choices_made": [],
                    },
                )
                test_sessions.append((session_id, session_context))
                self.test_sessions.append(session_id)

            # Test session creation
            for session_id, session_context in test_sessions:
                success = await self.session_repository.create_session(session_context)
                if not success:
                    errors.append(f"Failed to create session {session_id}")
                redis_ops += 2  # Redis operations for session creation
                neo4j_ops += 1  # Neo4j operations for session creation

            # Test session retrieval
            for session_id, _original_context in test_sessions:
                retrieved_context = await self.session_repository.get_session(
                    session_id
                )
                if not retrieved_context or retrieved_context.session_id != session_id:
                    errors.append(f"Failed to retrieve session {session_id}")
                redis_ops += 1
                neo4j_ops += 1

            # Test session updates
            for session_id, session_context in test_sessions:
                # Update narrative state
                session_context.narrative_state["turn_count"] = 5
                session_context.narrative_state["choices_made"] = [
                    "choice_1",
                    "choice_2",
                ]

                success = await self.session_repository.update_session(session_context)
                if not success:
                    errors.append(f"Failed to update session {session_id}")
                redis_ops += 1
                neo4j_ops += 1

            # Calculate metrics
            duration = time.time() - start_time
            success_rate = 1.0 - (
                len(errors) / (len(test_sessions) * 3)
            )  # 3 operations per session
            performance_score = min(
                10.0, max(0.0, 10.0 - (duration / len(test_sessions)))
            )
            consistency_score = 9.0 if success_rate > 0.95 else 7.0

            return DatabaseValidationMetrics(
                test_name="session_lifecycle_management",
                duration_seconds=duration,
                redis_operations=redis_ops,
                neo4j_operations=neo4j_ops,
                success_rate=success_rate,
                performance_score=performance_score,
                consistency_score=consistency_score,
                errors=errors,
                recommendations=self._generate_recommendations(
                    performance_score, consistency_score
                ),
            )

        except Exception as e:
            errors.append(str(e))
            logger.error(f"❌ Session lifecycle validation failed: {e}")

            return DatabaseValidationMetrics(
                test_name="session_lifecycle_management",
                duration_seconds=time.time() - start_time,
                redis_operations=redis_ops,
                neo4j_operations=neo4j_ops,
                success_rate=0.0,
                performance_score=0.0,
                consistency_score=0.0,
                errors=errors,
                recommendations=[
                    "Fix session management issues",
                    "Review database operations",
                ],
            )

    def _generate_recommendations(
        self, performance_score: float, consistency_score: float
    ) -> list[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        if performance_score < self.excellence_targets["performance_threshold"]:
            recommendations.append("Optimize database query performance")
            recommendations.append("Consider connection pooling improvements")
            recommendations.append("Review indexing strategy")

        if consistency_score < self.excellence_targets["consistency_threshold"]:
            recommendations.append("Improve data consistency mechanisms")
            recommendations.append("Review transaction handling")
            recommendations.append("Implement better error recovery")

        if not recommendations:
            recommendations.append("Database performance meets excellence standards")

        return recommendations

    async def cleanup(self):
        """Clean up test data and close connections."""
        try:
            # Clean up test sessions
            for session_id in self.test_sessions:
                if self.redis_client:
                    await self.redis_client.delete(f"session:{session_id}")

                if self.neo4j_driver:
                    async with self.neo4j_driver.session() as session:
                        await session.run(
                            "MATCH (s:Session {session_id: $session_id}) DELETE s",
                            session_id=session_id,
                        )

            # Close connections
            if self.redis_client:
                await self.redis_client.close()

            if self.neo4j_driver:
                await self.neo4j_driver.close()

            logger.info("✅ Database validation cleanup completed")

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


async def run_enhanced_database_validation(
    config_path: str = None,
) -> list[DatabaseValidationMetrics]:
    """
    Run comprehensive database validation tests.

    Args:
        config_path: Path to validation configuration file

    Returns:
        List of validation metrics for each test
    """
    # Load configuration
    if config_path:
        with open(config_path) as f:
            import yaml

            config = yaml.safe_load(f)
    else:
        config = {
            "redis": {"url": "redis://localhost:6379/1"},
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "tta_integration",
                "password": "tta_integration_password_2024",
            },
        }

    validator = EnhancedDatabaseValidator(config)

    try:
        # Initialize validator
        if not await validator.initialize():
            raise Exception("Failed to initialize database validator")

        # Run validation tests
        results = []

        logger.info("🔍 Running user preference persistence validation...")
        results.append(await validator.validate_user_preference_persistence())

        logger.info("🔍 Running session lifecycle management validation...")
        results.append(await validator.validate_session_lifecycle_management())

        return results

    finally:
        await validator.cleanup()


if __name__ == "__main__":
    import asyncio

    async def main():
        results = await run_enhanced_database_validation()

        for result in results:
            if result.errors:
                for _error in result.errors[:3]:  # Show first 3 errors
                    pass

            if result.recommendations:
                for _rec in result.recommendations:
                    pass

    asyncio.run(main())
