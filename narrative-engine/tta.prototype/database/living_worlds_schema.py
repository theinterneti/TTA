"""
Living Worlds Neo4j Schema Extensions

This module extends the existing Neo4j schema to support Living Worlds features
including timelines, events, family relationships, and world state persistence.
It builds upon the base schema in neo4j_schema.py.

Classes:
    LivingWorldsSchemaManager: Manages Living Worlds specific schema elements
    LivingWorldsQueryHelper: Provides query operations for Living Worlds data
"""

import logging
from datetime import datetime
from typing import Any

try:
    from neo4j import Driver, GraphDatabase, Result, Session
    from neo4j.exceptions import ClientError, ServiceUnavailable
except ImportError:
    print("Warning: neo4j package not installed. Install with: pip install neo4j")
    GraphDatabase = None
    Driver = None
    Session = None
    Result = None
    ServiceUnavailable = Exception
    ClientError = Exception

try:
    from .neo4j_schema import Neo4jConnectionError, Neo4jSchemaError, Neo4jSchemaManager
except ImportError:
    from neo4j_schema import Neo4jConnectionError, Neo4jSchemaManager

logger = logging.getLogger(__name__)


class LivingWorldsSchemaManager(Neo4jSchemaManager):
    """
    Extends Neo4jSchemaManager to support Living Worlds specific schema elements.

    This class adds constraints, indexes, and schema elements for timelines,
    events, family relationships, and world state management.
    """

    def __init__(self, uri: str = "bolt://localhost:7688", username: str = "neo4j", password: str = "password"):
        """Initialize Living Worlds schema manager."""
        super().__init__(uri, username, password)
        self.current_schema_version = "1.1.0"  # Living Worlds version

    def create_living_worlds_constraints(self) -> bool:
        """
        Create constraints specific to Living Worlds features.

        Returns:
            bool: True if all constraints were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        living_worlds_constraints = [
            # Timeline and event constraints
            "CREATE CONSTRAINT timeline_id IF NOT EXISTS FOR (t:Timeline) REQUIRE t.timeline_id IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:TimelineEvent) REQUIRE e.event_id IS UNIQUE",

            # World state constraints
            "CREATE CONSTRAINT world_id IF NOT EXISTS FOR (w:World) REQUIRE w.world_id IS UNIQUE",
            "CREATE CONSTRAINT world_state_id IF NOT EXISTS FOR (ws:WorldState) REQUIRE ws.world_state_id IS UNIQUE",

            # Family relationship constraints
            "CREATE CONSTRAINT family_tree_id IF NOT EXISTS FOR (ft:FamilyTree) REQUIRE ft.tree_id IS UNIQUE",
            "CREATE CONSTRAINT relationship_id IF NOT EXISTS FOR (r:FamilyRelationship) REQUIRE r.relationship_id IS UNIQUE",

            # Object and location history constraints
            "CREATE CONSTRAINT object_id IF NOT EXISTS FOR (o:Object) REQUIRE o.object_id IS UNIQUE",
            "CREATE CONSTRAINT location_history_id IF NOT EXISTS FOR (lh:LocationHistory) REQUIRE lh.history_id IS UNIQUE",
            "CREATE CONSTRAINT object_history_id IF NOT EXISTS FOR (oh:ObjectHistory) REQUIRE oh.history_id IS UNIQUE",

            # Evolution and task constraints
            "CREATE CONSTRAINT evolution_task_id IF NOT EXISTS FOR (et:EvolutionTask) REQUIRE et.task_id IS UNIQUE"
        ]

        try:
            with self.driver.session() as session:
                for constraint in living_worlds_constraints:
                    try:
                        session.run(constraint)
                        logger.debug(f"Created Living Worlds constraint: {constraint}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(f"Living Worlds constraint already exists: {constraint}")
                        else:
                            logger.error(f"Failed to create Living Worlds constraint: {constraint}, Error: {e}")
                            return False

            logger.info("All Living Worlds constraints created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating Living Worlds constraints: {e}")
            return False

    def create_living_worlds_indexes(self) -> bool:
        """
        Create indexes specific to Living Worlds features for optimal query performance.

        Returns:
            bool: True if all indexes were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        living_worlds_indexes = [
            # Timeline indexes
            "CREATE INDEX timeline_entity_id IF NOT EXISTS FOR (t:Timeline) ON (t.entity_id)",
            "CREATE INDEX timeline_entity_type IF NOT EXISTS FOR (t:Timeline) ON (t.entity_type)",
            "CREATE INDEX timeline_last_updated IF NOT EXISTS FOR (t:Timeline) ON (t.last_updated)",

            # Event indexes
            "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:TimelineEvent) ON (e.timestamp)",
            "CREATE INDEX event_type IF NOT EXISTS FOR (e:TimelineEvent) ON (e.event_type)",
            "CREATE INDEX event_significance IF NOT EXISTS FOR (e:TimelineEvent) ON (e.significance_level)",
            "CREATE INDEX event_emotional_impact IF NOT EXISTS FOR (e:TimelineEvent) ON (e.emotional_impact)",
            "CREATE INDEX event_participants IF NOT EXISTS FOR (e:TimelineEvent) ON (e.participants)",

            # World state indexes
            "CREATE INDEX world_name IF NOT EXISTS FOR (w:World) ON (w.world_name)",
            "CREATE INDEX world_status IF NOT EXISTS FOR (w:World) ON (w.world_status)",
            "CREATE INDEX world_current_time IF NOT EXISTS FOR (w:World) ON (w.current_time)",
            "CREATE INDEX world_last_evolution IF NOT EXISTS FOR (w:World) ON (w.last_evolution)",
            "CREATE INDEX world_player_last_visit IF NOT EXISTS FOR (w:World) ON (w.player_last_visit)",

            # Family relationship indexes
            "CREATE INDEX family_tree_root_character IF NOT EXISTS FOR (ft:FamilyTree) ON (ft.root_character_id)",
            "CREATE INDEX relationship_from_character IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.from_character_id)",
            "CREATE INDEX relationship_to_character IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.to_character_id)",
            "CREATE INDEX relationship_type IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.relationship_type)",
            "CREATE INDEX relationship_strength IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.strength)",
            "CREATE INDEX relationship_active IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.is_active)",

            # Object indexes
            "CREATE INDEX object_name IF NOT EXISTS FOR (o:Object) ON (o.name)",
            "CREATE INDEX object_type IF NOT EXISTS FOR (o:Object) ON (o.object_type)",
            "CREATE INDEX object_location IF NOT EXISTS FOR (o:Object) ON (o.current_location_id)",
            "CREATE INDEX object_owner IF NOT EXISTS FOR (o:Object) ON (o.current_owner_id)",

            # Evolution task indexes
            "CREATE INDEX evolution_task_type IF NOT EXISTS FOR (et:EvolutionTask) ON (et.task_type)",
            "CREATE INDEX evolution_task_scheduled_time IF NOT EXISTS FOR (et:EvolutionTask) ON (et.scheduled_time)",
            "CREATE INDEX evolution_task_status IF NOT EXISTS FOR (et:EvolutionTask) ON (et.status)",

            # Composite indexes for common queries
            "CREATE INDEX timeline_entity_composite IF NOT EXISTS FOR (t:Timeline) ON (t.entity_id, t.entity_type)",
            "CREATE INDEX event_timeline_timestamp IF NOT EXISTS FOR (e:TimelineEvent) ON (e.timeline_id, e.timestamp)",
            "CREATE INDEX relationship_characters_composite IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.from_character_id, r.to_character_id, r.relationship_type)"
        ]

        try:
            with self.driver.session() as session:
                for index in living_worlds_indexes:
                    try:
                        session.run(index)
                        logger.debug(f"Created Living Worlds index: {index}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(f"Living Worlds index already exists: {index}")
                        else:
                            logger.error(f"Failed to create Living Worlds index: {index}, Error: {e}")
                            return False

            logger.info("All Living Worlds indexes created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating Living Worlds indexes: {e}")
            return False

    def setup_living_worlds_schema(self) -> bool:
        """
        Set up the complete Living Worlds Neo4j schema including base schema.

        Returns:
            bool: True if schema setup was successful
        """
        logger.info("Setting up Living Worlds Neo4j schema")

        try:
            # First set up the base schema
            if not self.setup_schema():
                logger.error("Failed to set up base schema")
                return False

            # Create Living Worlds specific constraints
            if not self.create_living_worlds_constraints():
                logger.error("Failed to create Living Worlds constraints")
                return False

            # Create Living Worlds specific indexes
            if not self.create_living_worlds_indexes():
                logger.error("Failed to create Living Worlds indexes")
                return False

            # Record schema version
            self._record_schema_version()

            logger.info("Living Worlds Neo4j schema setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting up Living Worlds schema: {e}")
            return False


class LivingWorldsQueryHelper:
    """
    Provides query operations specific to Living Worlds data.

    This class contains helper methods for timeline, event, family relationship,
    and world state operations in Neo4j.
    """

    def __init__(self, driver: Driver):
        """
        Initialize Living Worlds query helper with Neo4j driver.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def create_timeline(self, timeline_id: str, entity_id: str, entity_type: str, **properties) -> bool:
        """
        Create a new timeline node.

        Args:
            timeline_id: Unique timeline identifier
            entity_id: Entity this timeline belongs to
            entity_type: Type of entity (character, location, object, world)
            **properties: Additional timeline properties

        Returns:
            bool: True if timeline was created successfully
        """
        query = """
        CREATE (t:Timeline {
            timeline_id: $timeline_id,
            entity_id: $entity_id,
            entity_type: $entity_type,
            created_at: datetime(),
            last_updated: datetime()
        })
        SET t += $properties
        RETURN t
        """

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   timeline_id=timeline_id,
                                   entity_id=entity_id,
                                   entity_type=entity_type,
                                   properties=properties)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating timeline: {e}")
            return False

    def create_timeline_event(self, event_id: str, timeline_id: str, event_type: str,
                            title: str, description: str, **properties) -> bool:
        """
        Create a new timeline event and link it to a timeline.

        Args:
            event_id: Unique event identifier
            timeline_id: Timeline this event belongs to
            event_type: Type of event
            title: Event title
            description: Event description
            **properties: Additional event properties

        Returns:
            bool: True if event was created successfully
        """
        query = """
        MATCH (t:Timeline {timeline_id: $timeline_id})
        CREATE (e:TimelineEvent {
            event_id: $event_id,
            event_type: $event_type,
            title: $title,
            description: $description,
            timestamp: datetime($timestamp),
            significance_level: $significance_level,
            emotional_impact: $emotional_impact,
            participants: $participants,
            consequences: $consequences,
            tags: $tags,
            created_at: datetime()
        })
        SET e += $properties
        CREATE (t)-[:CONTAINS_EVENT]->(e)
        RETURN e
        """

        # Set default values for required properties
        timestamp = properties.get('timestamp', datetime.now().isoformat())
        significance_level = properties.get('significance_level', 5)
        emotional_impact = properties.get('emotional_impact', 0.0)
        participants = properties.get('participants', [])
        consequences = properties.get('consequences', [])
        tags = properties.get('tags', [])
        location_id = properties.get('location_id')

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   event_id=event_id,
                                   timeline_id=timeline_id,
                                   event_type=event_type,
                                   title=title,
                                   description=description,
                                   timestamp=timestamp,
                                   significance_level=significance_level,
                                   emotional_impact=emotional_impact,
                                   participants=participants,
                                   consequences=consequences,
                                   tags=tags,
                                   properties=properties)

                # If location_id is provided, create relationship to location
                if location_id and result.single():
                    self._link_event_to_location(event_id, location_id)

                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating timeline event: {e}")
            return False

    def create_world_state(self, world_id: str, world_name: str, **properties) -> bool:
        """
        Create a new world state node.

        Args:
            world_id: Unique world identifier
            world_name: Name of the world
            **properties: Additional world properties

        Returns:
            bool: True if world state was created successfully
        """
        query = """
        CREATE (w:World {
            world_id: $world_id,
            world_name: $world_name,
            current_time: datetime(),
            world_status: $world_status,
            last_evolution: datetime(),
            created_at: datetime(),
            last_updated: datetime()
        })
        SET w += $properties
        RETURN w
        """

        world_status = properties.get('world_status', 'active')

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   world_id=world_id,
                                   world_name=world_name,
                                   world_status=world_status,
                                   properties=properties)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating world state: {e}")
            return False

    def create_family_tree(self, tree_id: str, root_character_id: str, **properties) -> bool:
        """
        Create a new family tree node.

        Args:
            tree_id: Unique family tree identifier
            root_character_id: Character this tree is centered on
            **properties: Additional tree properties

        Returns:
            bool: True if family tree was created successfully
        """
        query = """
        MATCH (c:Character {character_id: $root_character_id})
        CREATE (ft:FamilyTree {
            tree_id: $tree_id,
            root_character_id: $root_character_id,
            generations_tracked: $generations_tracked,
            created_at: datetime(),
            last_updated: datetime()
        })
        SET ft += $properties
        CREATE (ft)-[:CENTERED_ON]->(c)
        RETURN ft
        """

        generations_tracked = properties.get('generations_tracked', 3)

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   tree_id=tree_id,
                                   root_character_id=root_character_id,
                                   generations_tracked=generations_tracked,
                                   properties=properties)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating family tree: {e}")
            return False

    def create_family_relationship(self, relationship_id: str, from_character_id: str,
                                 to_character_id: str, relationship_type: str,
                                 strength: float = 1.0, **properties) -> bool:
        """
        Create a family relationship between two characters.

        Args:
            relationship_id: Unique relationship identifier
            from_character_id: Source character ID
            to_character_id: Target character ID
            relationship_type: Type of relationship (parent, child, sibling, etc.)
            strength: Relationship strength (0.0 to 1.0)
            **properties: Additional relationship properties

        Returns:
            bool: True if relationship was created successfully
        """
        query = """
        MATCH (c1:Character {character_id: $from_character_id})
        MATCH (c2:Character {character_id: $to_character_id})
        CREATE (r:FamilyRelationship {
            relationship_id: $relationship_id,
            from_character_id: $from_character_id,
            to_character_id: $to_character_id,
            relationship_type: $relationship_type,
            strength: $strength,
            established_date: datetime(),
            is_active: true
        })
        SET r += $properties
        CREATE (c1)-[:HAS_FAMILY_RELATIONSHIP]->(r)-[:WITH_CHARACTER]->(c2)
        RETURN r
        """

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   relationship_id=relationship_id,
                                   from_character_id=from_character_id,
                                   to_character_id=to_character_id,
                                   relationship_type=relationship_type,
                                   strength=strength,
                                   properties=properties)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating family relationship: {e}")
            return False

    def get_timeline_events(self, timeline_id: str, limit: int = 50,
                          min_significance: int = 1) -> list[dict[str, Any]]:
        """
        Get events from a timeline.

        Args:
            timeline_id: Timeline identifier
            limit: Maximum number of events to return
            min_significance: Minimum significance level

        Returns:
            List[Dict[str, Any]]: List of timeline events
        """
        query = """
        MATCH (t:Timeline {timeline_id: $timeline_id})-[:CONTAINS_EVENT]->(e:TimelineEvent)
        WHERE e.significance_level >= $min_significance
        RETURN e
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        try:
            with self.driver.session() as session:
                result = session.run(query,
                                   timeline_id=timeline_id,
                                   limit=limit,
                                   min_significance=min_significance)
                return [dict(record["e"]) for record in result]
        except Exception as e:
            logger.error(f"Error getting timeline events: {e}")
            return []

    def get_character_family_relationships(self, character_id: str) -> list[dict[str, Any]]:
        """
        Get all family relationships for a character.

        Args:
            character_id: Character identifier

        Returns:
            List[Dict[str, Any]]: List of family relationships
        """
        query = """
        MATCH (c:Character {character_id: $character_id})-[:HAS_FAMILY_RELATIONSHIP]->(r:FamilyRelationship)
        WHERE r.is_active = true
        RETURN r,
               [(r)-[:WITH_CHARACTER]->(other:Character) | other][0] as related_character
        ORDER BY r.relationship_type, r.strength DESC
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, character_id=character_id)
                relationships = []
                for record in result:
                    rel_data = dict(record["r"])
                    rel_data["related_character"] = dict(record["related_character"]) if record["related_character"] else None
                    relationships.append(rel_data)
                return relationships
        except Exception as e:
            logger.error(f"Error getting character family relationships: {e}")
            return []

    def get_world_state(self, world_id: str) -> dict[str, Any] | None:
        """
        Get world state information.

        Args:
            world_id: World identifier

        Returns:
            Optional[Dict[str, Any]]: World state data or None if not found
        """
        query = """
        MATCH (w:World {world_id: $world_id})
        OPTIONAL MATCH (w)-[:CONTAINS_CHARACTER]->(c:Character)
        OPTIONAL MATCH (w)-[:CONTAINS_LOCATION]->(l:Location)
        OPTIONAL MATCH (w)-[:CONTAINS_OBJECT]->(o:Object)
        RETURN w,
               collect(DISTINCT c) as characters,
               collect(DISTINCT l) as locations,
               collect(DISTINCT o) as objects
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, world_id=world_id)
                record = result.single()
                if record:
                    world_data = dict(record["w"])
                    world_data["characters"] = [dict(char) for char in record["characters"] if char]
                    world_data["locations"] = [dict(loc) for loc in record["locations"] if loc]
                    world_data["objects"] = [dict(obj) for obj in record["objects"] if obj]
                    return world_data
                return None
        except Exception as e:
            logger.error(f"Error getting world state: {e}")
            return None

    def update_world_state(self, world_id: str, updates: dict[str, Any]) -> bool:
        """
        Update world state properties.

        Args:
            world_id: World identifier
            updates: Dictionary of properties to update

        Returns:
            bool: True if update was successful
        """
        query = """
        MATCH (w:World {world_id: $world_id})
        SET w += $updates,
            w.last_updated = datetime()
        RETURN w
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, world_id=world_id, updates=updates)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error updating world state: {e}")
            return False

    def _link_event_to_location(self, event_id: str, location_id: str) -> bool:
        """Link an event to a location."""
        query = """
        MATCH (e:TimelineEvent {event_id: $event_id})
        MATCH (l:Location {location_id: $location_id})
        CREATE (e)-[:OCCURRED_AT]->(l)
        SET e.location_id = $location_id
        RETURN e, l
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, event_id=event_id, location_id=location_id)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error linking event to location: {e}")
            return False


# Utility functions for Living Worlds schema management
def setup_living_worlds_schema(uri: str = "bolt://localhost:7688",
                              username: str = "neo4j",
                              password: str = "password") -> bool:
    """
    Utility function to set up Living Worlds Neo4j schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if schema setup was successful
    """
    try:
        with LivingWorldsSchemaManager(uri, username, password) as schema_manager:
            return schema_manager.setup_living_worlds_schema()
    except Exception as e:
        logger.error(f"Failed to setup Living Worlds Neo4j schema: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Setup Living Worlds schema
    if setup_living_worlds_schema():
        print("Living Worlds schema setup completed successfully")
    else:
        print("Living Worlds schema setup failed")
