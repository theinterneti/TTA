"""
Neo4j Integration for Living Worlds System
Manages dynamic narrative environments and character relationships
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from neo4j import AsyncDriver, AsyncGraphDatabase

logger = logging.getLogger(__name__)


@dataclass
class WorldNode:
    """Represents a node in the living world graph"""

    id: str
    type: str  # 'character', 'location', 'event', 'narrative_thread'
    properties: dict[str, Any]
    relationships: list[dict[str, Any]]
    last_updated: datetime


@dataclass
class NarrativeRelationship:
    """Represents a relationship between narrative elements"""

    source_id: str
    target_id: str
    relationship_type: str
    strength: float  # 0.0 to 1.0
    properties: dict[str, Any]
    created_at: datetime


class LivingWorldsManager:
    """Manages the Neo4j-based living worlds system"""

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        redis_url: str = "redis://localhost:6379",
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.redis_url = redis_url

        self.driver: AsyncDriver | None = None
        self.redis: aioredis.Redis | None = None
        self.initialized = False

    async def initialize(self):
        """Initialize Neo4j and Redis connections"""
        try:
            # Initialize Neo4j driver
            self.driver = AsyncGraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )

            # Test Neo4j connection
            await self.driver.verify_connectivity()

            # Initialize Redis connection
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()

            # Create Neo4j constraints and indexes
            await self._create_schema()

            self.initialized = True
            logger.info("Living Worlds Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Living Worlds Manager: {str(e)}")
            raise

    async def close(self):
        """Close database connections"""
        if self.driver:
            await self.driver.close()
        if self.redis:
            await self.redis.close()

    async def _create_schema(self):
        """Create Neo4j schema constraints and indexes"""
        async with self.driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT character_id IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
                "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT narrative_id IF NOT EXISTS FOR (n:NarrativeThread) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT patient_id IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    logger.debug(f"Constraint already exists or failed: {str(e)}")

            # Create indexes for performance
            indexes = [
                "CREATE INDEX character_name IF NOT EXISTS FOR (c:Character) ON (c.name)",
                "CREATE INDEX location_name IF NOT EXISTS FOR (l:Location) ON (l.name)",
                "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:Event) ON (e.timestamp)",
                "CREATE INDEX narrative_active IF NOT EXISTS FOR (n:NarrativeThread) ON (n.active)",
            ]

            for index in indexes:
                try:
                    await session.run(index)
                except Exception as e:
                    logger.debug(f"Index already exists or failed: {str(e)}")

    async def create_character(
        self,
        character_id: str,
        name: str,
        personality_traits: list[str],  # Changed from Dict[str, float] to List[str]
        background: str,
        therapeutic_role: str,
        patient_id: str,
    ) -> WorldNode:
        """
        Create a new character in the living world.

        Note: personality_traits must be a list of strings (e.g., ['brave', 'curious'])
        to avoid Neo4j Browser crashes. Neo4j Browser cannot handle nested objects/maps.
        """
        if not self.initialized:
            await self.initialize()

        async with self.driver.session() as session:
            # Use primitive types only - Neo4j Browser compatible
            query = """
            MERGE (c:Character {id: $character_id})
            SET c.name = $name,
                c.personality_traits = $personality_traits,
                c.background = $background,
                c.therapeutic_role = $therapeutic_role,
                c.created_at = datetime(),
                c.last_updated = datetime(),
                c.active = true

            MERGE (p:Patient {id: $patient_id})
            MERGE (c)-[:BELONGS_TO]->(p)

            RETURN c
            """

            result = await session.run(
                query,
                character_id=character_id,
                name=name,
                personality_traits=personality_traits,  # Now a list of strings
                background=background,
                therapeutic_role=therapeutic_role,
                patient_id=patient_id,
            )

            record = await result.single()
            if record:
                character_node = record["c"]

                # Cache in Redis for quick access
                await self.redis.setex(
                    f"character:{character_id}",
                    3600,  # 1 hour TTL
                    json.dumps(
                        {
                            "id": character_id,
                            "name": name,
                            "personality_traits": personality_traits,
                            "therapeutic_role": therapeutic_role,
                        }
                    ),
                )

                logger.info(
                    f"Created character {name} ({character_id}) for patient {patient_id}"
                )

                return WorldNode(
                    id=character_id,
                    type="character",
                    properties=dict(character_node),
                    relationships=[],
                    last_updated=datetime.utcnow(),
                )

            raise Exception("Failed to create character")

    async def create_narrative_thread(
        self,
        thread_id: str,
        title: str,
        description: str,
        therapeutic_goals: list[str],
        patient_id: str,
        difficulty_level: int = 3,
    ) -> WorldNode:
        """Create a new narrative thread"""
        async with self.driver.session() as session:
            query = """
            MERGE (n:NarrativeThread {id: $thread_id})
            SET n.title = $title,
                n.description = $description,
                n.therapeutic_goals = $therapeutic_goals,
                n.difficulty_level = $difficulty_level,
                n.created_at = datetime(),
                n.last_updated = datetime(),
                n.active = true,
                n.progress = 0.0
            
            MERGE (p:Patient {id: $patient_id})
            MERGE (n)-[:ASSIGNED_TO]->(p)
            
            RETURN n
            """

            result = await session.run(
                query,
                thread_id=thread_id,
                title=title,
                description=description,
                therapeutic_goals=therapeutic_goals,
                difficulty_level=difficulty_level,
                patient_id=patient_id,
            )

            record = await result.single()
            if record:
                thread_node = record["n"]

                logger.info(
                    f"Created narrative thread {title} ({thread_id}) for patient {patient_id}"
                )

                return WorldNode(
                    id=thread_id,
                    type="narrative_thread",
                    properties=dict(thread_node),
                    relationships=[],
                    last_updated=datetime.utcnow(),
                )

            raise Exception("Failed to create narrative thread")

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        strength: float = 1.0,
        properties: dict[str, Any] | None = None,
    ) -> NarrativeRelationship:
        """Create a relationship between two nodes"""
        if properties is None:
            properties = {}

        async with self.driver.session() as session:
            query = """
            MATCH (source {id: $source_id})
            MATCH (target {id: $target_id})
            MERGE (source)-[r:RELATES_TO {type: $relationship_type}]->(target)
            SET r.strength = $strength,
                r.properties = $properties,
                r.created_at = datetime(),
                r.last_updated = datetime()
            RETURN r
            """

            result = await session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                properties=properties,
            )

            record = await result.single()
            if record:
                logger.info(
                    f"Created {relationship_type} relationship between {source_id} and {target_id}"
                )

                return NarrativeRelationship(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=relationship_type,
                    strength=strength,
                    properties=properties,
                    created_at=datetime.utcnow(),
                )

            raise Exception("Failed to create relationship")

    async def get_patient_world(self, patient_id: str) -> dict[str, Any]:
        """Get the complete living world for a patient"""
        async with self.driver.session() as session:
            query = """
            MATCH (p:Patient {id: $patient_id})
            OPTIONAL MATCH (p)<-[:BELONGS_TO]-(c:Character)
            OPTIONAL MATCH (p)<-[:ASSIGNED_TO]-(n:NarrativeThread)
            OPTIONAL MATCH (p)<-[:OCCURS_IN]-(e:Event)
            OPTIONAL MATCH (p)<-[:LOCATED_IN]-(l:Location)
            
            RETURN p,
                   collect(DISTINCT c) as characters,
                   collect(DISTINCT n) as narrative_threads,
                   collect(DISTINCT e) as events,
                   collect(DISTINCT l) as locations
            """

            result = await session.run(query, patient_id=patient_id)
            record = await result.single()

            if record:
                return {
                    "patient": dict(record["p"]) if record["p"] else {},
                    "characters": [dict(c) for c in record["characters"] if c],
                    "narrative_threads": [
                        dict(n) for n in record["narrative_threads"] if n
                    ],
                    "events": [dict(e) for e in record["events"] if e],
                    "locations": [dict(l) for l in record["locations"] if l],
                }

            return {
                "patient": {},
                "characters": [],
                "narrative_threads": [],
                "events": [],
                "locations": [],
            }

    async def update_narrative_progress(
        self,
        thread_id: str,
        progress: float,
        player_choices: list[dict[str, Any]],
        emotional_impact: dict[str, float],
    ):
        """Update progress on a narrative thread"""
        async with self.driver.session() as session:
            query = """
            MATCH (n:NarrativeThread {id: $thread_id})
            SET n.progress = $progress,
                n.last_updated = datetime(),
                n.player_choices = n.player_choices + $player_choices,
                n.emotional_impact = $emotional_impact
            
            CREATE (e:Event {
                id: randomUUID(),
                type: 'progress_update',
                thread_id: $thread_id,
                progress: $progress,
                choices: $player_choices,
                emotional_impact: $emotional_impact,
                timestamp: datetime()
            })
            
            MERGE (n)-[:HAS_EVENT]->(e)
            
            RETURN n, e
            """

            result = await session.run(
                query,
                thread_id=thread_id,
                progress=progress,
                player_choices=player_choices,
                emotional_impact=emotional_impact,
            )

            record = await result.single()
            if record:
                logger.info(
                    f"Updated narrative thread {thread_id} progress to {progress}"
                )

                # Update Redis cache
                await self.redis.setex(
                    f"narrative_progress:{thread_id}",
                    1800,  # 30 minutes TTL
                    json.dumps(
                        {
                            "progress": progress,
                            "last_updated": datetime.utcnow().isoformat(),
                            "emotional_impact": emotional_impact,
                        }
                    ),
                )

    async def get_character_relationships(
        self, character_id: str
    ) -> list[dict[str, Any]]:
        """Get all relationships for a character"""
        async with self.driver.session() as session:
            query = """
            MATCH (c:Character {id: $character_id})
            MATCH (c)-[r:RELATES_TO]-(other)
            RETURN other, r, type(r) as relationship_type
            ORDER BY r.strength DESC
            """

            result = await session.run(query, character_id=character_id)
            relationships = []

            async for record in result:
                relationships.append(
                    {
                        "character": dict(record["other"]),
                        "relationship": dict(record["r"]),
                        "type": record["relationship_type"],
                    }
                )

            return relationships

    async def evolve_world(self, patient_id: str, session_data: dict[str, Any]):
        """Evolve the living world based on patient interactions"""
        try:
            # Get current world state
            world_state = await self.get_patient_world(patient_id)

            # Analyze session data for world evolution triggers
            emotional_changes = session_data.get("emotional_changes", {})
            player_choices = session_data.get("player_choices", [])
            therapeutic_progress = session_data.get("therapeutic_progress", {})

            # Update character relationships based on interactions
            for choice in player_choices:
                if "character_interaction" in choice:
                    character_id = choice["character_interaction"]["character_id"]
                    interaction_type = choice["character_interaction"]["type"]
                    emotional_impact = choice.get("emotional_impact", 0.0)

                    # Strengthen or weaken relationships based on choices
                    await self._update_character_relationship(
                        character_id, patient_id, interaction_type, emotional_impact
                    )

            # Create new narrative events based on progress
            if therapeutic_progress.get("milestone_reached"):
                await self._create_milestone_event(
                    patient_id, therapeutic_progress["milestone_reached"]
                )

            logger.info(f"Evolved living world for patient {patient_id}")

        except Exception as e:
            logger.error(f"Failed to evolve world for patient {patient_id}: {str(e)}")

    async def _update_character_relationship(
        self,
        character_id: str,
        patient_id: str,
        interaction_type: str,
        emotional_impact: float,
    ):
        """Update character relationship strength based on interaction"""
        async with self.driver.session() as session:
            query = """
            MATCH (c:Character {id: $character_id})-[r:RELATES_TO]-(p:Patient {id: $patient_id})
            SET r.strength = CASE 
                WHEN $emotional_impact > 0 THEN r.strength + 0.1
                WHEN $emotional_impact < 0 THEN r.strength - 0.05
                ELSE r.strength
            END,
            r.last_interaction = datetime(),
            r.interaction_count = coalesce(r.interaction_count, 0) + 1
            
            RETURN r.strength as new_strength
            """

            result = await session.run(
                query,
                character_id=character_id,
                patient_id=patient_id,
                emotional_impact=emotional_impact,
            )

            record = await result.single()
            if record:
                logger.debug(
                    f"Updated relationship strength to {record['new_strength']}"
                )

    async def _create_milestone_event(self, patient_id: str, milestone: dict[str, Any]):
        """Create a milestone event in the narrative"""
        async with self.driver.session() as session:
            query = """
            MATCH (p:Patient {id: $patient_id})
            CREATE (e:Event {
                id: randomUUID(),
                type: 'milestone',
                milestone_type: $milestone_type,
                description: $description,
                therapeutic_value: $therapeutic_value,
                timestamp: datetime()
            })
            MERGE (e)-[:OCCURS_IN]->(p)
            RETURN e
            """

            await session.run(
                query,
                patient_id=patient_id,
                milestone_type=milestone.get("type", "progress"),
                description=milestone.get(
                    "description", "Therapeutic milestone reached"
                ),
                therapeutic_value=milestone.get("value", 1.0),
            )

            logger.info(f"Created milestone event for patient {patient_id}")


# Global instance
living_worlds_manager = LivingWorldsManager()
