"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Database/Migrations]]

# Logseq: [[TTA/Components/Gameplay_loop/Database/Migrations]]
Database Migrations for Gameplay Loop

This module provides database migration functionality for the therapeutic text adventure
gameplay loop system, including schema updates and data migrations.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Migration:
    """Base class for database migrations."""

    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at: datetime | None = None

    async def up(self, neo4j_driver) -> bool:
        """Apply the migration."""
        raise NotImplementedError("Subclasses must implement up()")

    async def down(self, neo4j_driver) -> bool:
        """Rollback the migration."""
        raise NotImplementedError("Subclasses must implement down()")


class InitialSchemaMigration(Migration):
    """Initial schema creation migration."""

    def __init__(self):
        super().__init__("001", "Create initial gameplay loop schema")

    async def up(self, neo4j_driver) -> bool:
        """Create initial schema."""
        try:
            from .schema import GameplayLoopSchema

            schema = GameplayLoopSchema()

            async with neo4j_driver.session() as session:
                # Create constraints
                for constraint in schema.get_node_constraints():
                    try:
                        await session.run(constraint)
                        logger.info(f"Applied constraint: {constraint[:50]}...")
                    except Exception as e:
                        logger.warning(f"Constraint may already exist: {e}")

                # Create indexes
                for index in schema.get_indexes():
                    try:
                        await session.run(index)
                        logger.info(f"Applied index: {index[:50]}...")
                    except Exception as e:
                        logger.warning(f"Index may already exist: {e}")

                logger.info("Initial schema migration completed")
                return True

        except Exception as e:
            logger.error(f"Initial schema migration failed: {e}")
            return False

    async def down(self, neo4j_driver) -> bool:
        """Remove initial schema."""
        try:
            from .schema import GameplayLoopSchema

            schema = GameplayLoopSchema()

            async with neo4j_driver.session() as session:
                # Drop constraints (in reverse order)
                constraints = schema.get_node_constraints()
                for constraint in reversed(constraints):
                    drop_constraint = constraint.replace(
                        "CREATE CONSTRAINT", "DROP CONSTRAINT"
                    ).replace(" IF NOT EXISTS", " IF EXISTS")
                    try:
                        await session.run(drop_constraint)
                    except Exception as e:
                        logger.warning(f"Could not drop constraint: {e}")

                # Drop indexes (in reverse order)
                indexes = schema.get_indexes()
                for index in reversed(indexes):
                    drop_index = index.replace("CREATE INDEX", "DROP INDEX").replace(
                        " IF NOT EXISTS", " IF EXISTS"
                    )
                    try:
                        await session.run(drop_index)
                    except Exception as e:
                        logger.warning(f"Could not drop index: {e}")

                logger.info("Initial schema rollback completed")
                return True

        except Exception as e:
            logger.error(f"Initial schema rollback failed: {e}")
            return False


class SampleDataMigration(Migration):
    """Sample data creation migration for testing."""

    def __init__(self):
        super().__init__("002", "Create sample therapeutic content")

    async def up(self, neo4j_driver) -> bool:
        """Create sample data."""
        try:
            from .schema import GameplayLoopSchema

            schema = GameplayLoopSchema()

            async with neo4j_driver.session() as session:
                for query in schema.get_sample_data_queries():
                    await session.run(query)

                logger.info("Sample data migration completed")
                return True

        except Exception as e:
            logger.error(f"Sample data migration failed: {e}")
            return False

    async def down(self, neo4j_driver) -> bool:
        """Remove sample data."""
        try:
            async with neo4j_driver.session() as session:
                # Remove sample data by specific IDs
                cleanup_queries = [
                    "MATCH (sc:NarrativeScene {scene_id: 'sample_intro_scene'}) DETACH DELETE sc",
                    "MATCH (c:PlayerChoice {choice_id: 'garden_explore_mindfully'}) DETACH DELETE c",
                    "MATCH (c:PlayerChoice {choice_id: 'garden_explore_curious'}) DETACH DELETE c",
                ]

                for query in cleanup_queries:
                    await session.run(query)

                logger.info("Sample data rollback completed")
                return True

        except Exception as e:
            logger.error(f"Sample data rollback failed: {e}")
            return False


class TherapeuticValidationMigration(Migration):
    """Add therapeutic validation enhancements."""

    def __init__(self):
        super().__init__("003", "Add therapeutic validation enhancements")

    async def up(self, neo4j_driver) -> bool:
        """Add validation enhancements."""
        try:
            async with neo4j_driver.session() as session:
                # Add new properties to existing nodes
                enhancement_queries = [
                    """
                    MATCH (s:GameplaySession)
                    WHERE NOT EXISTS(s.therapeutic_effectiveness_score)
                    SET s.therapeutic_effectiveness_score = 0.0,
                        s.safety_validation_required = false,
                        s.last_validation_check = null
                    """,
                    """
                    MATCH (c:PlayerChoice)
                    WHERE NOT EXISTS(c.validation_status)
                    SET c.validation_status = 'pending',
                        c.safety_rating = 'safe',
                        c.therapeutic_appropriateness = 0.0
                    """,
                    """
                    MATCH (sc:NarrativeScene)
                    WHERE NOT EXISTS(sc.content_validated)
                    SET sc.content_validated = false,
                        sc.validation_timestamp = null,
                        sc.therapeutic_quality_score = 0.0
                    """,
                ]

                for query in enhancement_queries:
                    await session.run(query)

                logger.info("Therapeutic validation migration completed")
                return True

        except Exception as e:
            logger.error(f"Therapeutic validation migration failed: {e}")
            return False

    async def down(self, neo4j_driver) -> bool:
        """Remove validation enhancements."""
        try:
            async with neo4j_driver.session() as session:
                # Remove added properties
                rollback_queries = [
                    """
                    MATCH (s:GameplaySession)
                    REMOVE s.therapeutic_effectiveness_score,
                           s.safety_validation_required,
                           s.last_validation_check
                    """,
                    """
                    MATCH (c:PlayerChoice)
                    REMOVE c.validation_status,
                           c.safety_rating,
                           c.therapeutic_appropriateness
                    """,
                    """
                    MATCH (sc:NarrativeScene)
                    REMOVE sc.content_validated,
                           sc.validation_timestamp,
                           sc.therapeutic_quality_score
                    """,
                ]

                for query in rollback_queries:
                    await session.run(query)

                logger.info("Therapeutic validation rollback completed")
                return True

        except Exception as e:
            logger.error(f"Therapeutic validation rollback failed: {e}")
            return False


class MigrationManager:
    """Manages database migrations for the gameplay loop system."""

    def __init__(self, neo4j_driver):
        self.neo4j_driver = neo4j_driver
        self.migrations = [
            InitialSchemaMigration(),
            SampleDataMigration(),
            TherapeuticValidationMigration(),
        ]

    async def initialize_migration_tracking(self) -> bool:
        """Initialize migration tracking in the database."""
        try:
            async with self.neo4j_driver.session() as session:
                # Create migration tracking node
                query = """
                MERGE (mt:MigrationTracker {id: 'gameplay_loop'})
                ON CREATE SET mt.created_at = datetime(),
                             mt.applied_migrations = []
                RETURN mt
                """
                await session.run(query)
                logger.info("Migration tracking initialized")
                return True

        except Exception as e:
            logger.error(f"Failed to initialize migration tracking: {e}")
            return False

    async def get_applied_migrations(self) -> list[str]:
        """Get list of applied migration versions."""
        try:
            async with self.neo4j_driver.session() as session:
                query = """
                MATCH (mt:MigrationTracker {id: 'gameplay_loop'})
                RETURN mt.applied_migrations as applied
                """
                result = await session.run(query)
                record = await result.single()

                if record and record["applied"]:
                    return record["applied"]
                return []

        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []

    async def mark_migration_applied(self, version: str) -> bool:
        """Mark a migration as applied."""
        try:
            async with self.neo4j_driver.session() as session:
                query = """
                MATCH (mt:MigrationTracker {id: 'gameplay_loop'})
                SET mt.applied_migrations = mt.applied_migrations + [$version],
                    mt.last_migration_at = datetime()
                RETURN mt
                """
                await session.run(query, {"version": version})
                return True

        except Exception as e:
            logger.error(f"Failed to mark migration applied: {e}")
            return False

    async def run_pending_migrations(self) -> bool:
        """Run all pending migrations."""
        try:
            await self.initialize_migration_tracking()
            applied_migrations = await self.get_applied_migrations()

            for migration in self.migrations:
                if migration.version not in applied_migrations:
                    logger.info(
                        f"Applying migration {migration.version}: {migration.description}"
                    )

                    if await migration.up(self.neo4j_driver):
                        await self.mark_migration_applied(migration.version)
                        migration.applied_at = datetime.utcnow()
                        logger.info(
                            f"Migration {migration.version} applied successfully"
                        )
                    else:
                        logger.error(f"Migration {migration.version} failed")
                        return False
                else:
                    logger.info(f"Migration {migration.version} already applied")

            logger.info("All migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False


async def run_migrations(neo4j_driver) -> bool:
    """Run all pending migrations."""
    migration_manager = MigrationManager(neo4j_driver)
    return await migration_manager.run_pending_migrations()
