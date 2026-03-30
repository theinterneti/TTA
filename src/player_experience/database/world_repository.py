"""

# Logseq: [[TTA.dev/Player_experience/Database/World_repository]]
World Repository for Neo4j persistence.

This module provides database operations for therapeutic worlds,
following the same pattern as CharacterRepository.
"""

import json
import logging
from datetime import datetime, timedelta

from neo4j import Driver, GraphDatabase

from ..models.enums import DifficultyLevel, TherapeuticApproach
from ..models.world import WorldDetails

logger = logging.getLogger(__name__)


class WorldRepository:
    """Repository for managing therapeutic worlds in Neo4j with in-memory fallback."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "tta_dev_password_2024",
    ):
        """Initialize the World Repository with Neo4j connection."""
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Driver | None = None
        self._connected = False

        # Fallback in-memory storage for when Neo4j is not available
        self._worlds: dict[str, WorldDetails] = {}

        # Try to connect to Neo4j
        try:
            self._connect()
            logger.info("WorldRepository initialized with Neo4j persistence")
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j, using in-memory storage: {e}")
            logger.info("WorldRepository initialized with in-memory fallback")

    def _connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self._connected = True
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            raise

    def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def create_world(self, world: WorldDetails) -> WorldDetails:
        """
        Create a new world in the database.

        Args:
            world: The world to create

        Returns:
            The created world
        """
        if self._connected and self.driver:
            try:
                self._create_world_neo4j(world)
                logger.debug(f"Created world {world.world_id} in Neo4j")
            except Exception as e:
                logger.error(f"Failed to create world in Neo4j: {e}")
                # Fall back to in-memory storage
                self._create_world_memory(world)
        else:
            # Use in-memory storage
            self._create_world_memory(world)

        return world

    def _create_world_neo4j(self, world: WorldDetails) -> None:
        """Create world in Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            # Convert therapeutic approaches to strings
            therapeutic_approaches = [
                approach.value
                if isinstance(approach, TherapeuticApproach)
                else str(approach)
                for approach in world.therapeutic_approaches
            ]

            # Convert difficulty level to string
            difficulty_level = (
                world.difficulty_level.value
                if isinstance(world.difficulty_level, DifficultyLevel)
                else str(world.difficulty_level)
            )

            query = """
            CREATE (w:World {
                world_id: $world_id,
                name: $name,
                description: $description,
                long_description: $long_description,
                therapeutic_themes: $therapeutic_themes,
                therapeutic_approaches: $therapeutic_approaches,
                difficulty_level: $difficulty_level,
                estimated_duration_minutes: $estimated_duration_minutes,
                setting_description: $setting_description,
                key_characters: $key_characters,
                main_storylines: $main_storylines,
                therapeutic_techniques_used: $therapeutic_techniques_used,
                recommended_therapeutic_readiness: $recommended_therapeutic_readiness,
                content_warnings: $content_warnings,
                player_count: $player_count,
                average_rating: $average_rating,
                completion_rate: $completion_rate,
                therapeutic_effectiveness_score: $therapeutic_effectiveness_score,
                created_at: $created_at
            })
            RETURN w.world_id as world_id
            """

            result = session.run(
                query,
                world_id=world.world_id,
                name=world.name,
                description=world.description,
                long_description=world.long_description,
                therapeutic_themes=world.therapeutic_themes,
                therapeutic_approaches=therapeutic_approaches,
                difficulty_level=difficulty_level,
                estimated_duration_minutes=int(
                    world.estimated_duration.total_seconds() / 60
                ),
                setting_description=world.setting_description,
                key_characters=json.dumps(world.key_characters),
                main_storylines=world.main_storylines,
                therapeutic_techniques_used=world.therapeutic_techniques_used,
                recommended_therapeutic_readiness=world.recommended_therapeutic_readiness,
                content_warnings=world.content_warnings,
                player_count=world.player_count,
                average_rating=world.average_rating,
                completion_rate=world.completion_rate,
                therapeutic_effectiveness_score=world.therapeutic_effectiveness_score,
                created_at=world.created_at.isoformat(),
            )

            record = result.single()
            if record:
                created_id = record["world_id"]
                logger.debug(f"World {created_id} created in Neo4j")

    def _create_world_memory(self, world: WorldDetails) -> None:
        """Create world in in-memory storage."""
        self._worlds[world.world_id] = world
        logger.debug(f"World {world.world_id} created in memory")

    def get_world(self, world_id: str) -> WorldDetails | None:
        """
        Get a world by ID.

        Args:
            world_id: The world ID

        Returns:
            The world if found, None otherwise
        """
        if self._connected and self.driver:
            try:
                return self._get_world_neo4j(world_id)
            except Exception as e:
                logger.error(f"Failed to get world from Neo4j: {e}")
                # Fall back to in-memory storage
                return self._worlds.get(world_id)
        else:
            return self._worlds.get(world_id)

    def _get_world_neo4j(self, world_id: str) -> WorldDetails | None:
        """Get world from Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            query = """
            MATCH (w:World {world_id: $world_id})
            RETURN w
            """

            result = session.run(query, world_id=world_id)
            record = result.single()

            if not record:
                return None

            return self._deserialize_world(record["w"])

    def _deserialize_world(self, world_node: dict) -> WorldDetails:
        """Convert Neo4j node to WorldDetails object."""
        # Parse key_characters JSON
        key_characters = []
        if world_node.get("key_characters"):
            try:
                key_characters = json.loads(world_node["key_characters"])
            except json.JSONDecodeError:
                logger.warning(
                    f"Failed to parse key_characters for world {world_node.get('world_id')}"
                )

        # Convert therapeutic approaches from strings to enums
        therapeutic_approaches = []
        for approach_str in world_node.get("therapeutic_approaches", []):
            try:
                therapeutic_approaches.append(TherapeuticApproach(approach_str))
            except ValueError:
                logger.warning(f"Unknown therapeutic approach: {approach_str}")

        # Convert difficulty level from string to enum
        difficulty_level = DifficultyLevel.INTERMEDIATE
        if world_node.get("difficulty_level"):
            try:
                difficulty_level = DifficultyLevel(world_node["difficulty_level"])
            except ValueError:
                logger.warning(
                    f"Unknown difficulty level: {world_node.get('difficulty_level')}"
                )

        return WorldDetails(
            world_id=world_node["world_id"],
            name=world_node["name"],
            description=world_node["description"],
            long_description=world_node.get("long_description", ""),
            therapeutic_themes=world_node.get("therapeutic_themes", []),
            therapeutic_approaches=therapeutic_approaches,
            difficulty_level=difficulty_level,
            estimated_duration=timedelta(
                minutes=world_node.get("estimated_duration_minutes", 120)
            ),
            setting_description=world_node.get("setting_description", ""),
            key_characters=key_characters,
            main_storylines=world_node.get("main_storylines", []),
            therapeutic_techniques_used=world_node.get(
                "therapeutic_techniques_used", []
            ),
            recommended_therapeutic_readiness=world_node.get(
                "recommended_therapeutic_readiness", 0.5
            ),
            content_warnings=world_node.get("content_warnings", []),
            player_count=world_node.get("player_count", 0),
            average_rating=world_node.get("average_rating", 0.0),
            completion_rate=world_node.get("completion_rate", 0.0),
            therapeutic_effectiveness_score=world_node.get(
                "therapeutic_effectiveness_score", 0.0
            ),
            created_at=datetime.fromisoformat(
                world_node.get("created_at", datetime.now().isoformat())
            ),
        )

    def get_all_worlds(self) -> list[WorldDetails]:
        """
        Get all worlds from the database.

        Returns:
            List of all worlds
        """
        if self._connected and self.driver:
            try:
                return self._get_all_worlds_neo4j()
            except Exception as e:
                logger.error(f"Failed to get worlds from Neo4j: {e}")
                # Fall back to in-memory storage
                return list(self._worlds.values())
        else:
            return list(self._worlds.values())

    def _get_all_worlds_neo4j(self) -> list[WorldDetails]:
        """Get all worlds from Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            query = """
            MATCH (w:World)
            RETURN w
            ORDER BY w.created_at DESC
            """

            result = session.run(query)
            worlds = []
            for record in result:
                try:
                    world = self._deserialize_world(record["w"])
                    worlds.append(world)
                except Exception as e:
                    logger.error(f"Failed to deserialize world: {e}")

            return worlds
