"""
Database Migration Scripts for Gameplay Loop

This module provides database migration and setup procedures for the therapeutic
gameplay loop Neo4j schema, including rollback capabilities and version management.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.components.gameplay_loop.database.neo4j_manager import Neo4jConnectionManager
from src.components.gameplay_loop.database.schema import GraphIndexes, GraphSchema

logger = logging.getLogger(__name__)


@dataclass
class MigrationStep:
    """Individual migration step with rollback capability."""

    version: str
    description: str
    up_statements: list[str]
    down_statements: list[str]
    dependencies: list[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class MigrationManager:
    """Manages database migrations for the gameplay loop system."""

    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager
        self.migrations = self._define_migrations()

    def _define_migrations(self) -> list[MigrationStep]:
        """Define all migration steps in order."""
        return [
            MigrationStep(
                version="001_initial_schema",
                description="Create initial gameplay loop schema with constraints and indexes",
                up_statements=GraphSchema.get_all_schema_statements(),
                down_statements=[
                    "DROP CONSTRAINT session_session_id_unique IF EXISTS",
                    "DROP CONSTRAINT scene_scene_id_unique IF EXISTS",
                    "DROP CONSTRAINT choice_choice_id_unique IF EXISTS",
                    "DROP CONSTRAINT user_user_id_unique IF EXISTS",
                    "DROP CONSTRAINT therapeutic_goal_goal_id_unique IF EXISTS",
                    "DROP CONSTRAINT skill_skill_id_unique IF EXISTS",
                    "DROP CONSTRAINT progress_metric_metric_id_unique IF EXISTS",
                    "DROP CONSTRAINT milestone_milestone_id_unique IF EXISTS",
                    "DROP CONSTRAINT safety_check_check_id_unique IF EXISTS",
                    "DROP INDEX session_user_state_index IF EXISTS",
                    "DROP INDEX scene_session_type_index IF EXISTS",
                    "DROP INDEX metric_type_updated_index IF EXISTS",
                ],
            ),
            MigrationStep(
                version="002_performance_indexes",
                description="Add performance optimization indexes",
                up_statements=GraphIndexes.get_performance_indexes(),
                down_statements=[
                    "DROP INDEX scene_content_fulltext IF EXISTS",
                    "DROP INDEX choice_content_fulltext IF EXISTS",
                    "DROP INDEX skill_content_fulltext IF EXISTS",
                    "DROP INDEX therapeutic_relevance_range IF EXISTS",
                    "DROP INDEX safety_score_range IF EXISTS",
                    "DROP INDEX progress_value_range IF EXISTS",
                ],
                dependencies=["001_initial_schema"],
            ),
            MigrationStep(
                version="003_user_nodes",
                description="Create initial user nodes and relationships",
                up_statements=[
                    """
                    // Create User nodes if they don't exist
                    MERGE (u:User {user_id: 'system'})
                    SET u.created_at = datetime().epochSeconds,
                        u.user_type = 'system',
                        u.description = 'System user for automated processes'
                    """,
                    """
                    // Create basic therapeutic goals
                    MERGE (tg1:TherapeuticGoal {goal_id: 'anxiety_management'})
                    SET tg1.goal_name = 'Anxiety Management',
                        tg1.goal_type = 'emotional_regulation',
                        tg1.description = 'Develop skills to manage anxiety effectively'

                    MERGE (tg2:TherapeuticGoal {goal_id: 'social_skills'})
                    SET tg2.goal_name = 'Social Skills Development',
                        tg2.goal_type = 'interpersonal',
                        tg2.description = 'Improve social interaction and communication skills'

                    MERGE (tg3:TherapeuticGoal {goal_id: 'emotional_awareness'})
                    SET tg3.goal_name = 'Emotional Awareness',
                        tg3.goal_type = 'self_awareness',
                        tg3.description = 'Increase awareness and understanding of emotions'
                    """,
                ],
                down_statements=[
                    "MATCH (u:User {user_id: 'system'}) DELETE u",
                    "MATCH (tg:TherapeuticGoal) WHERE tg.goal_id IN ['anxiety_management', 'social_skills', 'emotional_awareness'] DELETE tg",
                ],
                dependencies=["001_initial_schema"],
            ),
            MigrationStep(
                version="004_skill_nodes",
                description="Create basic skill nodes for therapeutic development",
                up_statements=[
                    """
                    // Create basic therapeutic skills
                    MERGE (s1:Skill {skill_id: 'deep_breathing'})
                    SET s1.skill_name = 'Deep Breathing',
                        s1.skill_category = 'anxiety_management',
                        s1.description = 'Controlled breathing technique for anxiety reduction',
                        s1.learning_objectives = ['Learn proper breathing technique', 'Practice in stressful situations', 'Achieve automatic response']

                    MERGE (s2:Skill {skill_id: 'grounding_techniques'})
                    SET s2.skill_name = 'Grounding Techniques',
                        s2.skill_category = 'anxiety_management',
                        s2.description = '5-4-3-2-1 and other grounding methods',
                        s2.learning_objectives = ['Learn 5-4-3-2-1 technique', 'Practice sensory awareness', 'Apply in crisis situations']

                    MERGE (s3:Skill {skill_id: 'active_listening'})
                    SET s3.skill_name = 'Active Listening',
                        s3.skill_category = 'social_skills',
                        s3.description = 'Focused listening and response techniques',
                        s3.learning_objectives = ['Understand active listening principles', 'Practice reflection techniques', 'Demonstrate empathy']

                    MERGE (s4:Skill {skill_id: 'emotion_identification'})
                    SET s4.skill_name = 'Emotion Identification',
                        s4.skill_category = 'emotional_awareness',
                        s4.description = 'Recognizing and naming emotions accurately',
                        s4.learning_objectives = ['Learn emotion vocabulary', 'Practice self-monitoring', 'Identify triggers']
                    """
                ],
                down_statements=[
                    "MATCH (s:Skill) WHERE s.skill_id IN ['deep_breathing', 'grounding_techniques', 'active_listening', 'emotion_identification'] DELETE s"
                ],
                dependencies=["003_user_nodes"],
            ),
            MigrationStep(
                version="005_skill_goal_relationships",
                description="Create relationships between skills and therapeutic goals",
                up_statements=[
                    """
                    // Link skills to therapeutic goals
                    MATCH (s:Skill {skill_id: 'deep_breathing'}), (tg:TherapeuticGoal {goal_id: 'anxiety_management'})
                    MERGE (s)-[:SUPPORTS_GOAL {effectiveness: 0.8, evidence_level: 'high'}]->(tg)

                    MATCH (s:Skill {skill_id: 'grounding_techniques'}), (tg:TherapeuticGoal {goal_id: 'anxiety_management'})
                    MERGE (s)-[:SUPPORTS_GOAL {effectiveness: 0.9, evidence_level: 'high'}]->(tg)

                    MATCH (s:Skill {skill_id: 'active_listening'}), (tg:TherapeuticGoal {goal_id: 'social_skills'})
                    MERGE (s)-[:SUPPORTS_GOAL {effectiveness: 0.85, evidence_level: 'high'}]->(tg)

                    MATCH (s:Skill {skill_id: 'emotion_identification'}), (tg:TherapeuticGoal {goal_id: 'emotional_awareness'})
                    MERGE (s)-[:SUPPORTS_GOAL {effectiveness: 0.9, evidence_level: 'high'}]->(tg)

                    // Cross-skill relationships
                    MATCH (s1:Skill {skill_id: 'emotion_identification'}), (s2:Skill {skill_id: 'deep_breathing'})
                    MERGE (s1)-[:ENHANCES {synergy_level: 0.7}]->(s2)
                    """
                ],
                down_statements=[
                    "MATCH ()-[r:SUPPORTS_GOAL]->() DELETE r",
                    "MATCH ()-[r:ENHANCES]->() DELETE r",
                ],
                dependencies=["004_skill_nodes"],
            ),
        ]

    async def get_applied_migrations(self) -> list[str]:
        """Get list of applied migration versions."""
        try:
            query = """
            MATCH (m:Migration)
            RETURN m.version as version
            ORDER BY m.applied_at ASC
            """

            async with self.connection_manager.session() as session:
                result = await session.run(query)
                records = await result.data()
                return [record["version"] for record in records]

        except Exception as e:
            logger.warning(f"Could not retrieve migration history: {e}")
            return []

    async def record_migration(
        self, version: str, description: str, success: bool
    ) -> None:
        """Record migration application in the database."""
        try:
            query = """
            MERGE (m:Migration {version: $version})
            SET m.description = $description,
                m.applied_at = $applied_at,
                m.success = $success
            RETURN m
            """

            parameters = {
                "version": version,
                "description": description,
                "applied_at": datetime.utcnow().isoformat(),
                "success": success,
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

        except Exception as e:
            logger.error(f"Failed to record migration: {e}")

    async def apply_migration(self, migration: MigrationStep) -> bool:
        """Apply a single migration step."""
        try:
            logger.info(
                f"Applying migration {migration.version}: {migration.description}"
            )

            async with self.connection_manager.session() as session:
                for statement in migration.up_statements:
                    if statement.strip() and not statement.strip().startswith("//"):
                        logger.debug(f"Executing: {statement[:100]}...")
                        await session.run(statement)

            await self.record_migration(migration.version, migration.description, True)
            logger.info(f"Successfully applied migration {migration.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            await self.record_migration(migration.version, migration.description, False)
            return False

    async def rollback_migration(self, migration: MigrationStep) -> bool:
        """Rollback a single migration step."""
        try:
            logger.info(
                f"Rolling back migration {migration.version}: {migration.description}"
            )

            async with self.connection_manager.session() as session:
                for statement in migration.down_statements:
                    if statement.strip() and not statement.strip().startswith("//"):
                        logger.debug(f"Executing rollback: {statement[:100]}...")
                        await session.run(statement)

            # Remove migration record
            query = "MATCH (m:Migration {version: $version}) DELETE m"
            async with self.connection_manager.session() as session:
                await session.run(query, {"version": migration.version})

            logger.info(f"Successfully rolled back migration {migration.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False

    async def migrate_up(self, target_version: str | None = None) -> bool:
        """Apply migrations up to target version (or all if None)."""
        try:
            applied_migrations = await self.get_applied_migrations()

            for migration in self.migrations:
                if migration.version in applied_migrations:
                    logger.debug(
                        f"Migration {migration.version} already applied, skipping"
                    )
                    continue

                # Check dependencies
                for dep in migration.dependencies:
                    if dep not in applied_migrations:
                        logger.error(
                            f"Migration {migration.version} depends on {dep} which is not applied"
                        )
                        return False

                # Apply migration
                success = await self.apply_migration(migration)
                if not success:
                    logger.error(f"Migration failed at {migration.version}")
                    return False

                applied_migrations.append(migration.version)

                # Stop if we've reached target version
                if target_version and migration.version == target_version:
                    break

            logger.info("All migrations applied successfully")
            return True

        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False

    async def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations down to target version."""
        try:
            applied_migrations = await self.get_applied_migrations()

            # Find migrations to rollback (in reverse order)
            migrations_to_rollback = []
            for migration in reversed(self.migrations):
                if migration.version in applied_migrations:
                    migrations_to_rollback.append(migration)
                    if migration.version == target_version:
                        break

            # Remove target version from rollback list (we want to keep it)
            if (
                migrations_to_rollback
                and migrations_to_rollback[-1].version == target_version
            ):
                migrations_to_rollback.pop()

            # Rollback migrations
            for migration in migrations_to_rollback:
                success = await self.rollback_migration(migration)
                if not success:
                    logger.error(f"Rollback failed at {migration.version}")
                    return False

            logger.info(f"Successfully rolled back to version {target_version}")
            return True

        except Exception as e:
            logger.error(f"Rollback process failed: {e}")
            return False

    async def get_migration_status(self) -> dict[str, Any]:
        """Get current migration status."""
        applied_migrations = await self.get_applied_migrations()

        status = {
            "total_migrations": len(self.migrations),
            "applied_migrations": len(applied_migrations),
            "pending_migrations": len(self.migrations) - len(applied_migrations),
            "current_version": applied_migrations[-1] if applied_migrations else None,
            "latest_version": self.migrations[-1].version if self.migrations else None,
            "is_up_to_date": len(applied_migrations) == len(self.migrations),
            "applied_versions": applied_migrations,
            "pending_versions": [
                m.version
                for m in self.migrations
                if m.version not in applied_migrations
            ],
        }

        return status


async def setup_database(connection_manager: Neo4jConnectionManager) -> bool:
    """Setup the database with all migrations."""
    migration_manager = MigrationManager(connection_manager)

    logger.info("Starting database setup...")
    success = await migration_manager.migrate_up()

    if success:
        status = await migration_manager.get_migration_status()
        logger.info(
            f"Database setup complete. Applied {status['applied_migrations']} migrations."
        )
    else:
        logger.error("Database setup failed")

    return success
