"""
Nexus Codex Database Schema Extensions for Neo4j.

This module extends the existing TTA database schema with Nexus Codex-specific
nodes and relationships for therapeutic world creation and management.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NexusSchemaManager:
    """Manages Nexus Codex schema extensions in Neo4j."""

    def __init__(self, driver):
        """Initialize with Neo4j driver."""
        self.driver = driver

    async def create_nexus_schema(self) -> bool:
        """Create all Nexus Codex schema extensions."""
        try:
            async with self.driver.session() as session:
                # Create Nexus Codex central hub
                await self._create_nexus_codex_hub(session)

                # Create indexes for performance
                await self._create_indexes(session)

                # Create constraints for data integrity
                await self._create_constraints(session)

                logger.info("Nexus Codex schema created successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to create Nexus schema: {e}")
            return False

    async def _create_nexus_codex_hub(self, session):
        """Create the central Nexus Codex hub node."""
        query = """
        MERGE (nexus:NexusCodex {codex_id: 'central_nexus'})
        SET nexus.name = 'The Nexus Codex',
            nexus.total_worlds = 0,
            nexus.active_story_weavers = 0,
            nexus.silence_threat_level = 0.1,
            nexus.narrative_strength = 1.0,
            nexus.created_at = datetime(),
            nexus.last_updated = datetime()
        RETURN nexus
        """
        await session.run(query)

    async def _create_indexes(self, session):
        """Create indexes for Nexus Codex nodes."""
        indexes = [
            "CREATE INDEX nexus_codex_id_index IF NOT EXISTS FOR (n:NexusCodex) ON (n.codex_id)",
            "CREATE INDEX story_world_id_index IF NOT EXISTS FOR (n:StoryWorld) ON (n.world_id)",
            "CREATE INDEX story_world_genre_index IF NOT EXISTS FOR (n:StoryWorld) ON (n.genre)",
            "CREATE INDEX story_world_therapeutic_focus IF NOT EXISTS FOR (n:StoryWorld) ON (n.therapeutic_focus)",
            "CREATE INDEX story_weaver_player_index IF NOT EXISTS FOR (n:StoryWeaver) ON (n.player_id)",
            "CREATE INDEX story_weaver_level_index IF NOT EXISTS FOR (n:StoryWeaver) ON (n.nexus_level)",
            "CREATE INDEX story_sphere_world_index IF NOT EXISTS FOR (n:StorySphere) ON (n.world_id)",
            "CREATE INDEX world_template_genre_index IF NOT EXISTS FOR (n:WorldTemplate) ON (n.genre)",
            "CREATE INDEX world_template_goals_index IF NOT EXISTS FOR (n:WorldTemplate) ON (n.therapeutic_goals)",
        ]

        for index_query in indexes:
            try:
                await session.run(index_query)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")

    async def _create_constraints(self, session):
        """Create constraints for data integrity."""
        constraints = [
            "CREATE CONSTRAINT nexus_codex_unique IF NOT EXISTS FOR (n:NexusCodex) REQUIRE n.codex_id IS UNIQUE",
            "CREATE CONSTRAINT story_world_unique IF NOT EXISTS FOR (n:StoryWorld) REQUIRE n.world_id IS UNIQUE",
            "CREATE CONSTRAINT story_weaver_unique IF NOT EXISTS FOR (n:StoryWeaver) REQUIRE n.weaver_id IS UNIQUE",
            "CREATE CONSTRAINT story_sphere_unique IF NOT EXISTS FOR (n:StorySphere) REQUIRE n.sphere_id IS UNIQUE",
            "CREATE CONSTRAINT world_template_unique IF NOT EXISTS FOR (n:WorldTemplate) REQUIRE n.template_id IS UNIQUE",
        ]

        for constraint_query in constraints:
            try:
                await session.run(constraint_query)
            except Exception as e:
                logger.warning(f"Constraint creation warning: {e}")

    async def create_story_world(self, world_data: dict[str, Any]) -> str | None:
        """Create a new StoryWorld node."""
        query = """
        CREATE (world:StoryWorld {
            world_id: $world_id,
            title: $title,
            description: $description,
            genre: $genre,
            therapeutic_focus: $therapeutic_focus,
            narrative_state: $narrative_state,
            creator_id: $creator_id,
            strength_level: $strength_level,
            silence_threat: $silence_threat,
            completion_rate: $completion_rate,
            therapeutic_efficacy: $therapeutic_efficacy,
            difficulty_level: $difficulty_level,
            estimated_duration: $estimated_duration,
            player_count: $player_count,
            rating: $rating,
            tags: $tags,
            is_public: $is_public,
            is_featured: $is_featured,
            created_at: datetime(),
            last_updated: datetime()
        })

        // Connect to Nexus Codex
        WITH world
        MATCH (nexus:NexusCodex {codex_id: 'central_nexus'})
        CREATE (nexus)-[:CONTAINS {
            connection_strength: $strength_level,
            created_at: datetime()
        }]->(world)

        // Create corresponding StorySphere
        CREATE (sphere:StorySphere {
            sphere_id: $world_id + '_sphere',
            world_id: $world_id,
            visual_state: CASE
                WHEN $strength_level > 0.8 THEN 'bright_glow'
                WHEN $strength_level > 0.5 THEN 'gentle_pulse'
                WHEN $strength_level > 0.2 THEN 'dim_flicker'
                ELSE 'dark_void'
            END,
            pulse_frequency: $strength_level,
            connection_strength: $strength_level,
            position_x: rand() * 100,
            position_y: rand() * 100,
            position_z: rand() * 100,
            color_primary: CASE $genre
                WHEN 'fantasy' THEN '#A23B72'
                WHEN 'sci-fi' THEN '#2E86AB'
                WHEN 'contemporary' THEN '#F18F01'
                ELSE '#10B981'
            END,
            color_secondary: '#FFFFFF',
            size_scale: $strength_level
        })

        CREATE (world)-[:VISUALIZED_BY {
            sync_status: 'synchronized',
            last_sync: datetime()
        }]->(sphere)

        RETURN world.world_id as world_id
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, world_data)
                record = await result.single()
                return record["world_id"] if record else None
        except Exception as e:
            logger.error(f"Failed to create story world: {e}")
            return None

    async def create_story_weaver(self, player_id: str) -> str | None:
        """Create a StoryWeaver profile for a player."""
        weaver_id = f"{player_id}_weaver"

        query = """
        MATCH (player:Player {player_id: $player_id})
        CREATE (weaver:StoryWeaver {
            weaver_id: $weaver_id,
            player_id: $player_id,
            nexus_level: 1,
            worlds_created: 0,
            worlds_completed: 0,
            stories_strengthened: 0,
            therapeutic_impact_score: 0.0,
            preferred_genres: [],
            creation_specialties: [],
            community_reputation: 0.0,
            mentor_status: false,
            total_play_time: 0,
            achievements: [],
            created_at: datetime(),
            last_active: datetime()
        })

        CREATE (player)-[:STORY_WEAVER]->(weaver)

        RETURN weaver.weaver_id as weaver_id
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query, {"player_id": player_id, "weaver_id": weaver_id}
                )
                record = await result.single()
                return record["weaver_id"] if record else None
        except Exception as e:
            logger.error(f"Failed to create story weaver: {e}")
            return None

    async def strengthen_world(
        self, world_id: str, weaver_id: str, contribution: float
    ) -> bool:
        """Record a story weaver's contribution to strengthening a world."""
        query = """
        MATCH (world:StoryWorld {world_id: $world_id})
        MATCH (weaver:StoryWeaver {weaver_id: $weaver_id})

        // Create or update strengthening relationship
        MERGE (weaver)-[r:STRENGTHENED_BY]->(world)
        SET r.strength_contribution = COALESCE(r.strength_contribution, 0) + $contribution,
            r.interaction_date = datetime(),
            r.interaction_type = 'completion'

        // Update world strength
        SET world.strength_level = CASE
            WHEN world.strength_level + ($contribution * 0.1) > 1.0 THEN 1.0
            ELSE world.strength_level + ($contribution * 0.1)
        END,
        world.last_updated = datetime()

        // Update weaver stats
        SET weaver.stories_strengthened = weaver.stories_strengthened + 1,
            weaver.therapeutic_impact_score = weaver.therapeutic_impact_score + $contribution,
            weaver.last_active = datetime()

        // Update corresponding sphere visual state
        WITH world
        MATCH (world)-[:VISUALIZED_BY]->(sphere:StorySphere)
        SET sphere.visual_state = CASE
            WHEN world.strength_level > 0.8 THEN 'bright_glow'
            WHEN world.strength_level > 0.5 THEN 'gentle_pulse'
            WHEN world.strength_level > 0.2 THEN 'dim_flicker'
            ELSE 'dark_void'
        END,
        sphere.pulse_frequency = world.strength_level,
        sphere.connection_strength = world.strength_level,
        sphere.size_scale = world.strength_level

        RETURN world.strength_level as new_strength
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    {
                        "world_id": world_id,
                        "weaver_id": weaver_id,
                        "contribution": contribution,
                    },
                )
                record = await result.single()
                return record is not None
        except Exception as e:
            logger.error(f"Failed to strengthen world: {e}")
            return False

    async def get_nexus_state(self) -> dict[str, Any] | None:
        """Get current state of the Nexus Codex."""
        query = """
        MATCH (nexus:NexusCodex {codex_id: 'central_nexus'})
        OPTIONAL MATCH (nexus)-[:CONTAINS]->(worlds:StoryWorld)
        OPTIONAL MATCH (:StoryWeaver)

        WITH nexus,
             count(DISTINCT worlds) as total_worlds,
             count(DISTINCT CASE WHEN worlds.is_featured THEN worlds END) as featured_worlds,
             avg(worlds.strength_level) as avg_strength,
             count(DISTINCT CASE WHEN exists((:StoryWeaver)-[:STRENGTHENED_BY]->(worlds)) THEN worlds END) as active_worlds

        RETURN {
            codex_id: nexus.codex_id,
            name: nexus.name,
            total_worlds: total_worlds,
            featured_worlds: featured_worlds,
            average_strength: avg_strength,
            active_worlds: active_worlds,
            silence_threat_level: nexus.silence_threat_level,
            narrative_strength: nexus.narrative_strength,
            last_updated: nexus.last_updated
        } as nexus_state
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query)
                record = await result.single()
                return record["nexus_state"] if record else None
        except Exception as e:
            logger.error(f"Failed to get nexus state: {e}")
            return None


# Schema validation and migration utilities
async def validate_nexus_schema(driver) -> bool:
    """Validate that Nexus Codex schema is properly installed."""
    try:
        async with driver.session() as session:
            # Check for central nexus node
            result = await session.run(
                "MATCH (n:NexusCodex {codex_id: 'central_nexus'}) RETURN count(n) as count"
            )
            record = await result.single()

            if not record or record["count"] == 0:
                logger.warning("Central Nexus Codex node not found")
                return False

            # Check for required indexes
            result = await session.run("SHOW INDEXES")
            indexes = [record["name"] async for record in result]

            required_indexes = [
                "story_world_id_index",
                "story_weaver_player_index",
                "nexus_codex_id_index",
            ]

            missing_indexes = [idx for idx in required_indexes if idx not in indexes]
            if missing_indexes:
                logger.warning(f"Missing indexes: {missing_indexes}")
                return False

            logger.info("Nexus Codex schema validation passed")
            return True

    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        return False


async def migrate_existing_worlds_to_nexus(driver) -> bool:
    """Migrate existing worlds to Nexus Codex structure."""
    try:
        async with driver.session() as session:
            # Find existing worlds that aren't connected to Nexus
            query = """
            MATCH (world:World)
            WHERE NOT exists((world)<-[:CONTAINS]-(:NexusCodex))

            // Convert to StoryWorld if not already
            SET world:StoryWorld
            SET world.world_id = COALESCE(world.world_id, world.id),
                world.title = COALESCE(world.title, world.name),
                world.genre = COALESCE(world.genre, 'contemporary'),
                world.therapeutic_focus = COALESCE(world.therapeutic_focus, []),
                world.narrative_state = 'active',
                world.strength_level = 0.5,
                world.silence_threat = 0.1,
                world.completion_rate = 0.0,
                world.therapeutic_efficacy = 0.0,
                world.player_count = 0,
                world.rating = 0.0,
                world.is_public = true,
                world.is_featured = false

            // Connect to Nexus
            WITH world
            MATCH (nexus:NexusCodex {codex_id: 'central_nexus'})
            CREATE (nexus)-[:CONTAINS {
                connection_strength: world.strength_level,
                created_at: datetime()
            }]->(world)

            RETURN count(world) as migrated_count
            """

            result = await session.run(query)
            record = await result.single()
            migrated_count = record["migrated_count"] if record else 0

            logger.info(f"Migrated {migrated_count} existing worlds to Nexus Codex")
            return True

    except Exception as e:
        logger.error(f"World migration failed: {e}")
        return False
