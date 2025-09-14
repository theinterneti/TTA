"""
Neo4j Schema Management for TTA Prototype

This module provides schema setup, migration, and query helper methods
for the therapeutic text adventure Neo4j database.

Classes:
    Neo4jSchemaManager: Manages Neo4j schema constraints, indexes, and migrations
    Neo4jQueryHelper: Provides common query operations for therapeutic data
"""

import logging
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

logger = logging.getLogger(__name__)


class Neo4jConnectionError(Exception):
    """Raised when Neo4j connection fails."""

    pass


class Neo4jSchemaError(Exception):
    """Raised when Neo4j schema operations fail."""

    pass


class Neo4jSchemaManager:
    """
    Manages Neo4j schema constraints, indexes, and migrations for therapeutic text adventure.

    This class handles the creation and management of the Neo4j database schema
    including constraints, indexes, and data migrations for characters, locations,
    therapeutic data, and user sessions.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7688",
        username: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize Neo4j schema manager.

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        if GraphDatabase is None:
            raise ImportError(
                "neo4j package is required. Install with: pip install neo4j"
            )

        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Driver | None = None

        # Schema version for migration tracking
        self.current_schema_version = "1.0.0"

    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}") from e
        except Exception as e:
            raise Neo4jConnectionError(
                f"Unexpected error connecting to Neo4j: {e}"
            ) from e

    def disconnect(self) -> None:
        """Close connection to Neo4j database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Disconnected from Neo4j")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def create_constraints(self) -> bool:
        """
        Create all necessary constraints for the therapeutic text adventure schema.

        Returns:
            bool: True if all constraints were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        constraints = [
            # Core entity constraints
            "CREATE CONSTRAINT character_id IF NOT EXISTS FOR (c:Character) REQUIRE c.character_id IS UNIQUE",
            "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
            "CREATE CONSTRAINT scenario_id IF NOT EXISTS FOR (sc:Scenario) REQUIRE sc.scenario_id IS UNIQUE",
            # Therapeutic entity constraints
            "CREATE CONSTRAINT goal_id IF NOT EXISTS FOR (g:TherapeuticGoal) REQUIRE g.goal_id IS UNIQUE",
            "CREATE CONSTRAINT intervention_id IF NOT EXISTS FOR (i:Intervention) REQUIRE i.intervention_id IS UNIQUE",
            "CREATE CONSTRAINT strategy_id IF NOT EXISTS FOR (cs:CopingStrategy) REQUIRE cs.strategy_id IS UNIQUE",
            "CREATE CONSTRAINT opportunity_id IF NOT EXISTS FOR (o:TherapeuticOpportunity) REQUIRE o.opportunity_id IS UNIQUE",
            # Memory and dialogue constraints
            "CREATE CONSTRAINT memory_id IF NOT EXISTS FOR (m:Memory) REQUIRE m.memory_id IS UNIQUE",
            "CREATE CONSTRAINT dialogue_id IF NOT EXISTS FOR (d:Dialogue) REQUIRE d.dialogue_id IS UNIQUE",
            # Choice and narrative constraints
            "CREATE CONSTRAINT choice_id IF NOT EXISTS FOR (ch:Choice) REQUIRE ch.choice_id IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:NarrativeEvent) REQUIRE e.event_id IS UNIQUE",
        ]

        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                        logger.debug(f"Created constraint: {constraint}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(f"Constraint already exists: {constraint}")
                        else:
                            logger.error(
                                f"Failed to create constraint: {constraint}, Error: {e}"
                            )
                            return False

            logger.info("All constraints created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating constraints: {e}")
            return False

    def create_indexes(self) -> bool:
        """
        Create all necessary indexes for optimal query performance.

        Returns:
            bool: True if all indexes were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        indexes = [
            # Character indexes
            "CREATE INDEX character_name IF NOT EXISTS FOR (c:Character) ON (c.name)",
            "CREATE INDEX character_role IF NOT EXISTS FOR (c:Character) ON (c.therapeutic_role)",
            # Location indexes
            "CREATE INDEX location_name IF NOT EXISTS FOR (l:Location) ON (l.name)",
            "CREATE INDEX location_type IF NOT EXISTS FOR (l:Location) ON (l.location_type)",
            # User and session indexes
            "CREATE INDEX user_created_at IF NOT EXISTS FOR (u:User) ON (u.created_at)",
            "CREATE INDEX session_created_at IF NOT EXISTS FOR (s:Session) ON (s.created_at)",
            "CREATE INDEX session_status IF NOT EXISTS FOR (s:Session) ON (s.status)",
            # Therapeutic indexes
            "CREATE INDEX goal_status IF NOT EXISTS FOR (g:TherapeuticGoal) ON (g.status)",
            "CREATE INDEX goal_created_at IF NOT EXISTS FOR (g:TherapeuticGoal) ON (g.created_at)",
            "CREATE INDEX intervention_type IF NOT EXISTS FOR (i:Intervention) ON (i.intervention_type)",
            "CREATE INDEX intervention_completed_at IF NOT EXISTS FOR (i:Intervention) ON (i.completed_at)",
            # Memory and emotional indexes
            "CREATE INDEX memory_timestamp IF NOT EXISTS FOR (m:Memory) ON (m.timestamp)",
            "CREATE INDEX memory_emotional_weight IF NOT EXISTS FOR (m:Memory) ON (m.emotional_weight)",
            # Choice and narrative indexes
            "CREATE INDEX choice_timestamp IF NOT EXISTS FOR (ch:Choice) ON (ch.timestamp)",
            "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:NarrativeEvent) ON (e.timestamp)",
            # Composite indexes for common queries
            "CREATE INDEX user_session_composite IF NOT EXISTS FOR (s:Session) ON (s.user_id, s.created_at)",
            "CREATE INDEX character_location_composite IF NOT EXISTS FOR (c:Character) ON (c.current_location_id, c.last_interaction)",
        ]

        try:
            with self.driver.session() as session:
                for index in indexes:
                    try:
                        session.run(index)
                        logger.debug(f"Created index: {index}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(f"Index already exists: {index}")
                        else:
                            logger.error(f"Failed to create index: {index}, Error: {e}")
                            return False

            logger.info("All indexes created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False

    def setup_schema(self) -> bool:
        """
        Set up the complete Neo4j schema including constraints and indexes.

        Returns:
            bool: True if schema setup was successful
        """
        logger.info("Setting up Neo4j schema for therapeutic text adventure")

        try:
            # Create constraints first
            if not self.create_constraints():
                logger.error("Failed to create constraints")
                return False

            # Create indexes
            if not self.create_indexes():
                logger.error("Failed to create indexes")
                return False

            # Record schema version
            self._record_schema_version()

            logger.info("Neo4j schema setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting up schema: {e}")
            return False

    def _record_schema_version(self) -> None:
        """Record the current schema version in the database."""
        if not self.driver:
            return

        query = """
        MERGE (sv:SchemaVersion {id: 'current'})
        SET sv.version = $version,
            sv.updated_at = datetime()
        """

        try:
            with self.driver.session() as session:
                session.run(query, version=self.current_schema_version)
            logger.info(f"Recorded schema version: {self.current_schema_version}")
        except Exception as e:
            logger.error(f"Failed to record schema version: {e}")

    def get_schema_version(self) -> str | None:
        """
        Get the current schema version from the database.

        Returns:
            Optional[str]: Current schema version or None if not found
        """
        if not self.driver:
            return None

        query = "MATCH (sv:SchemaVersion {id: 'current'}) RETURN sv.version as version"

        try:
            with self.driver.session() as session:
                result = session.run(query)
                record = result.single()
                return record["version"] if record else None
        except Exception as e:
            logger.error(f"Failed to get schema version: {e}")
            return None

    def migrate_data(self, from_version: str = None, to_version: str = None) -> bool:
        """
        Perform data migration between schema versions.

        Args:
            from_version: Source schema version
            to_version: Target schema version

        Returns:
            bool: True if migration was successful
        """
        current_version = self.get_schema_version()
        target_version = to_version or self.current_schema_version

        logger.info(
            f"Migrating data from version {current_version} to {target_version}"
        )

        # For now, we only have one version, so no migration is needed
        if current_version == target_version:
            logger.info("No migration needed - already at target version")
            return True

        # Future migrations would be implemented here
        logger.info("No migration scripts available for this version change")
        return True

    def validate_schema(self) -> bool:
        """
        Validate that the schema is properly set up.

        Returns:
            bool: True if schema is valid
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        try:
            with self.driver.session() as session:
                # Check if constraints exist
                constraints_result = session.run("SHOW CONSTRAINTS")
                constraints = [record["name"] for record in constraints_result]

                expected_constraints = [
                    "character_id",
                    "location_id",
                    "user_id",
                    "session_id",
                    "goal_id",
                    "intervention_id",
                    "strategy_id",
                ]

                missing_constraints = []
                for expected in expected_constraints:
                    if not any(expected in constraint for constraint in constraints):
                        missing_constraints.append(expected)

                if missing_constraints:
                    logger.error(f"Missing constraints: {missing_constraints}")
                    return False

                # Check if indexes exist
                indexes_result = session.run("SHOW INDEXES")
                indexes = [record["name"] for record in indexes_result]

                expected_indexes = [
                    "character_name",
                    "location_name",
                    "user_created_at",
                ]

                missing_indexes = []
                for expected in expected_indexes:
                    if not any(expected in index for index in indexes):
                        missing_indexes.append(expected)

                if missing_indexes:
                    logger.warning(f"Missing indexes (non-critical): {missing_indexes}")

                logger.info("Schema validation completed successfully")
                return True

        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return False

    def drop_schema(self) -> bool:
        """
        Drop all schema elements (constraints and indexes).
        WARNING: This is destructive and should only be used for testing.

        Returns:
            bool: True if schema was dropped successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        logger.warning("Dropping all schema elements - this is destructive!")

        try:
            with self.driver.session() as session:
                # Drop all constraints
                constraints_result = session.run("SHOW CONSTRAINTS")
                for record in constraints_result:
                    constraint_name = record["name"]
                    session.run(f"DROP CONSTRAINT {constraint_name}")
                    logger.debug(f"Dropped constraint: {constraint_name}")

                # Drop all indexes
                indexes_result = session.run("SHOW INDEXES")
                for record in indexes_result:
                    index_name = record["name"]
                    if index_name not in [
                        "token_names",
                        "token_lookup",
                    ]:  # Skip system indexes
                        session.run(f"DROP INDEX {index_name}")
                        logger.debug(f"Dropped index: {index_name}")

                logger.info("Schema dropped successfully")
                return True

        except Exception as e:
            logger.error(f"Error dropping schema: {e}")
            return False


class Neo4jQueryHelper:
    """
    Provides common query operations for therapeutic text adventure data.

    This class contains helper methods for frequently used Neo4j queries
    related to characters, locations, therapeutic progress, and narrative state.
    """

    def __init__(self, driver: Driver):
        """
        Initialize query helper with Neo4j driver.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def create_user(self, user_id: str, **properties) -> bool:
        """
        Create a new user node.

        Args:
            user_id: Unique user identifier
            **properties: Additional user properties

        Returns:
            bool: True if user was created successfully
        """
        query = """
        CREATE (u:User {user_id: $user_id, created_at: datetime()})
        SET u += $properties
        RETURN u
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id, properties=properties)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def create_character(self, character_id: str, name: str, **properties) -> bool:
        """
        Create a new character node.

        Args:
            character_id: Unique character identifier
            name: Character name
            **properties: Additional character properties

        Returns:
            bool: True if character was created successfully
        """
        query = """
        CREATE (c:Character {
            character_id: $character_id,
            name: $name,
            created_at: datetime()
        })
        SET c += $properties
        RETURN c
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, character_id=character_id, name=name, properties=properties
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            return False

    def create_location(self, location_id: str, name: str, **properties) -> bool:
        """
        Create a new location node.

        Args:
            location_id: Unique location identifier
            name: Location name
            **properties: Additional location properties

        Returns:
            bool: True if location was created successfully
        """
        query = """
        CREATE (l:Location {
            location_id: $location_id,
            name: $name,
            created_at: datetime()
        })
        SET l += $properties
        RETURN l
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, location_id=location_id, name=name, properties=properties
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating location: {e}")
            return False

    def create_session(self, session_id: str, user_id: str, **properties) -> bool:
        """
        Create a new session node and link it to a user.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
            **properties: Additional session properties

        Returns:
            bool: True if session was created successfully
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (s:Session {
            session_id: $session_id,
            user_id: $user_id,
            created_at: datetime(),
            status: 'active'
        })
        SET s += $properties
        CREATE (u)-[:HAS_SESSION]->(s)
        RETURN s
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, session_id=session_id, user_id=user_id, properties=properties
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False

    def create_therapeutic_goal(
        self, goal_id: str, user_id: str, title: str, description: str, **properties
    ) -> bool:
        """
        Create a therapeutic goal and link it to a user.

        Args:
            goal_id: Unique goal identifier
            user_id: User identifier
            title: Goal title
            description: Goal description
            **properties: Additional goal properties

        Returns:
            bool: True if goal was created successfully
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (g:TherapeuticGoal {
            goal_id: $goal_id,
            title: $title,
            description: $description,
            created_at: datetime(),
            status: 'active',
            progress_percentage: 0.0
        })
        SET g += $properties
        CREATE (g)-[:BELONGS_TO]->(u)
        RETURN g
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    goal_id=goal_id,
                    user_id=user_id,
                    title=title,
                    description=description,
                    properties=properties,
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating therapeutic goal: {e}")
            return False

    def create_character_relationship(
        self,
        char1_id: str,
        char2_id: str,
        relationship_type: str,
        strength: float = 0.0,
    ) -> bool:
        """
        Create a relationship between two characters.

        Args:
            char1_id: First character ID
            char2_id: Second character ID
            relationship_type: Type of relationship
            strength: Relationship strength (-1.0 to 1.0)

        Returns:
            bool: True if relationship was created successfully
        """
        query = """
        MATCH (c1:Character {character_id: $char1_id})
        MATCH (c2:Character {character_id: $char2_id})
        CREATE (c1)-[:HAS_RELATIONSHIP {
            type: $relationship_type,
            strength: $strength,
            created_at: datetime()
        }]->(c2)
        RETURN c1, c2
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    char1_id=char1_id,
                    char2_id=char2_id,
                    relationship_type=relationship_type,
                    strength=strength,
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating character relationship: {e}")
            return False

    def get_user_sessions(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent sessions for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return

        Returns:
            List[Dict[str, Any]]: List of session data
        """
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)
        RETURN s
        ORDER BY s.created_at DESC
        LIMIT $limit
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id, limit=limit)
                return [dict(record["s"]) for record in result]
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    def get_character_memories(
        self, character_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Get memories for a character.

        Args:
            character_id: Character identifier
            limit: Maximum number of memories to return

        Returns:
            List[Dict[str, Any]]: List of memory data
        """
        query = """
        MATCH (c:Character {character_id: $character_id})-[:HAS_MEMORY]->(m:Memory)
        RETURN m
        ORDER BY m.timestamp DESC
        LIMIT $limit
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, character_id=character_id, limit=limit)
                return [dict(record["m"]) for record in result]
        except Exception as e:
            logger.error(f"Error getting character memories: {e}")
            return []

    def get_therapeutic_progress(self, user_id: str) -> dict[str, Any]:
        """
        Get therapeutic progress summary for a user.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Therapeutic progress data
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (g:TherapeuticGoal)-[:BELONGS_TO]->(u)
        OPTIONAL MATCH (i:Intervention)-[:APPLIED_TO]->(u)
        OPTIONAL MATCH (cs:CopingStrategy)-[:LEARNED_BY]->(u)
        RETURN u,
               collect(DISTINCT g) as goals,
               collect(DISTINCT i) as interventions,
               collect(DISTINCT cs) as strategies
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id)
                record = result.single()
                if record:
                    return {
                        "user": dict(record["u"]),
                        "goals": [dict(goal) for goal in record["goals"] if goal],
                        "interventions": [
                            dict(intervention)
                            for intervention in record["interventions"]
                            if intervention
                        ],
                        "strategies": [
                            dict(strategy)
                            for strategy in record["strategies"]
                            if strategy
                        ],
                    }
                return {}
        except Exception as e:
            logger.error(f"Error getting therapeutic progress: {e}")
            return {}

    def update_character_location(self, character_id: str, location_id: str) -> bool:
        """
        Update character's current location.

        Args:
            character_id: Character identifier
            location_id: New location identifier

        Returns:
            bool: True if location was updated successfully
        """
        query = """
        MATCH (c:Character {character_id: $character_id})
        OPTIONAL MATCH (c)-[r:LOCATED_AT]->()
        DELETE r
        WITH c
        MATCH (l:Location {location_id: $location_id})
        CREATE (c)-[:LOCATED_AT]->(l)
        SET c.current_location_id = $location_id,
            c.last_interaction = datetime()
        RETURN c
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, character_id=character_id, location_id=location_id
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error updating character location: {e}")
            return False


# Utility functions for schema management
def setup_neo4j_schema(
    uri: str = "bolt://localhost:7688",
    username: str = "neo4j",
    password: str = "password",
) -> bool:
    """
    Utility function to set up Neo4j schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if schema setup was successful
    """
    try:
        with Neo4jSchemaManager(uri, username, password) as schema_manager:
            return schema_manager.setup_schema()
    except Exception as e:
        logger.error(f"Failed to setup Neo4j schema: {e}")
        return False


def validate_neo4j_schema(
    uri: str = "bolt://localhost:7688",
    username: str = "neo4j",
    password: str = "password",
) -> bool:
    """
    Utility function to validate Neo4j schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if schema is valid
    """
    try:
        with Neo4jSchemaManager(uri, username, password) as schema_manager:
            return schema_manager.validate_schema()
    except Exception as e:
        logger.error(f"Failed to validate Neo4j schema: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Setup schema
    if setup_neo4j_schema():
        print("✅ Neo4j schema setup completed successfully")

        # Validate schema
        if validate_neo4j_schema():
            print("✅ Neo4j schema validation passed")
        else:
            print("❌ Neo4j schema validation failed")
    else:
        print("❌ Neo4j schema setup failed")
