"""
Neo4j schema management for Player Profile data.

This module extends the existing TTA Neo4j schema to include
player profile management with proper constraints and indexes.
"""

import logging

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


class PlayerProfileSchemaError(Exception):
    """Raised when player profile schema operations fail."""

    pass


class PlayerProfileSchemaManager:
    """
    Manages Neo4j schema for player profiles and related data.

    This class extends the existing TTA Neo4j schema to include
    player profile management with proper constraints, indexes,
    and data validation for therapeutic text adventure players.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize Player Profile Schema Manager.

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

        # Schema version for player profile extensions
        self.player_schema_version = "1.0.0"

    def connect(self) -> None:
        """Establish connection to Neo4j database with retry/backoff for readiness races."""
        # Import here to access specific exception types without changing module import surface
        try:
            from neo4j.exceptions import (
                AuthError,
            )
            from neo4j.exceptions import ClientError as _ClientError
            from neo4j.exceptions import ServiceUnavailable as _ServiceUnavailable
        except Exception:  # pragma: no cover - neo4j not installed path
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = ServiceUnavailable  # type: ignore
            _ClientError = Exception  # type: ignore
        last_exc: Exception | None = None
        base_delay = 0.5
        # Option B: increase attempts to 6 (0.5,1,2,4,8,8)
        attempts = 6
        for attempt in range(attempts):
            try:
                self.driver = GraphDatabase.driver(
                    self.uri, auth=(self.username, self.password)
                )
                # Verify readiness
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"Connected to Neo4j at {self.uri}")
                return
            except (AuthError, _ServiceUnavailable) as e:
                last_exc = e
                delay = min(base_delay * (2**attempt), 8.0)
                logger.debug(
                    f"Neo4j connect attempt {attempt+1}/{attempts} failed ({e!s}); retrying in {delay:.1f}s"
                )
                # Close any partially created driver before sleeping
                try:
                    if self.driver:
                        self.driver.close()
                except Exception:
                    pass
                self.driver = None
                import time as _t

                if attempt < (attempts - 1):
                    _t.sleep(delay)
                else:
                    # Exhausted attempts: re-raise with original exception type
                    if isinstance(e, AuthError):
                        raise PlayerProfileSchemaError(
                            f"Failed to connect to Neo4j after retries: {e}"
                        )
                    elif isinstance(e, _ServiceUnavailable):
                        raise PlayerProfileSchemaError(
                            f"Failed to connect to Neo4j after retries: {e}"
                        )
            except _ClientError as e:
                # Retry only on AuthenticationRateLimit variant
                emsg = str(e)
                if ("AuthenticationRateLimit" in emsg) or (
                    "authentication details too many times" in emsg
                ):
                    last_exc = e
                    delay = min(base_delay * (2**attempt), 8.0)
                    logger.debug(
                        f"Neo4j connect attempt {attempt+1}/5 hit AuthenticationRateLimit; retrying in {delay:.1f}s"
                    )
                    try:
                        if self.driver:
                            self.driver.close()
                    except Exception:
                        pass
                    self.driver = None
                    import time as _t

                    if attempt < (attempts - 1):
                        _t.sleep(delay)
                    else:
                        raise PlayerProfileSchemaError(
                            f"Failed to connect to Neo4j after retries: {e}"
                        )
                else:
                    # Other ClientErrors fail fast
                    raise PlayerProfileSchemaError(
                        f"Unexpected error connecting to Neo4j: {e}"
                    )
            except Exception as e:
                # Unexpected errors should fail fast per requirement
                raise PlayerProfileSchemaError(
                    f"Unexpected error connecting to Neo4j: {e}"
                )
        # Should not reach here; safety net
        if last_exc is not None:
            raise PlayerProfileSchemaError(
                f"Failed to connect to Neo4j after retries: {last_exc}"
            )

    def disconnect(self) -> None:
        """Close connection to Neo4j database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Disconnected from Neo4j")

    def is_connected(self) -> bool:
        """
        Check if connected to Neo4j database.

        Returns:
            bool: True if connected and responsive
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.warning(f"Neo4j connection check failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def create_player_profile_constraints(self) -> bool:
        """
        Create constraints for player profile data.

        Returns:
            bool: True if all constraints were created successfully
        """
        if not self.driver:
            raise PlayerProfileSchemaError("Not connected to Neo4j")

        constraints = [
            # Player profile constraints
            "CREATE CONSTRAINT player_profile_id IF NOT EXISTS FOR (p:PlayerProfile) REQUIRE p.player_id IS UNIQUE",
            "CREATE CONSTRAINT player_username IF NOT EXISTS FOR (p:PlayerProfile) REQUIRE p.username IS UNIQUE",
            "CREATE CONSTRAINT player_email IF NOT EXISTS FOR (p:PlayerProfile) REQUIRE p.email IS UNIQUE",
            # Therapeutic preferences constraints
            "CREATE CONSTRAINT therapeutic_prefs_id IF NOT EXISTS FOR (tp:TherapeuticPreferences) REQUIRE tp.preferences_id IS UNIQUE",
            # Privacy settings constraints
            "CREATE CONSTRAINT privacy_settings_id IF NOT EXISTS FOR (ps:PrivacySettings) REQUIRE ps.settings_id IS UNIQUE",
            # Crisis contact info constraints
            "CREATE CONSTRAINT crisis_contact_id IF NOT EXISTS FOR (cc:CrisisContactInfo) REQUIRE cc.contact_id IS UNIQUE",
            # Progress summary constraints
            "CREATE CONSTRAINT progress_summary_id IF NOT EXISTS FOR (pr:ProgressSummary) REQUIRE pr.summary_id IS UNIQUE",
        ]

        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                        logger.debug(f"Created player profile constraint: {constraint}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(
                                f"Player profile constraint already exists: {constraint}"
                            )
                        else:
                            logger.error(
                                f"Failed to create player profile constraint: {constraint}, Error: {e}"
                            )
                            return False

            logger.info("All player profile constraints created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating player profile constraints: {e}")
            return False

    def create_player_profile_indexes(self) -> bool:
        """
        Create indexes for optimal player profile query performance.

        Returns:
            bool: True if all indexes were created successfully
        """
        if not self.driver:
            raise PlayerProfileSchemaError("Not connected to Neo4j")

        indexes = [
            # Player profile indexes
            "CREATE INDEX player_username_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.username)",
            "CREATE INDEX player_email_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.email)",
            "CREATE INDEX player_created_at_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.created_at)",
            "CREATE INDEX player_last_login_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.last_login)",
            "CREATE INDEX player_is_active_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.is_active)",
            # Therapeutic preferences indexes
            "CREATE INDEX therapeutic_intensity_idx IF NOT EXISTS FOR (tp:TherapeuticPreferences) ON (tp.intensity_level)",
            "CREATE INDEX therapeutic_approaches_idx IF NOT EXISTS FOR (tp:TherapeuticPreferences) ON (tp.preferred_approaches)",
            # Privacy settings indexes
            "CREATE INDEX privacy_consent_idx IF NOT EXISTS FOR (ps:PrivacySettings) ON (ps.data_collection_consent)",
            "CREATE INDEX privacy_research_idx IF NOT EXISTS FOR (ps:PrivacySettings) ON (ps.research_participation_consent)",
            "CREATE INDEX privacy_retention_idx IF NOT EXISTS FOR (ps:PrivacySettings) ON (ps.data_retention_period_days)",
            # Progress summary indexes
            "CREATE INDEX progress_total_sessions_idx IF NOT EXISTS FOR (pr:ProgressSummary) ON (pr.total_sessions)",
            "CREATE INDEX progress_milestones_idx IF NOT EXISTS FOR (pr:ProgressSummary) ON (pr.milestones_achieved)",
            "CREATE INDEX progress_last_session_idx IF NOT EXISTS FOR (pr:ProgressSummary) ON (pr.last_session_date)",
            # Composite indexes for common queries
            "CREATE INDEX player_active_login_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.is_active, p.last_login)",
            "CREATE INDEX player_created_active_idx IF NOT EXISTS FOR (p:PlayerProfile) ON (p.created_at, p.is_active)",
        ]

        try:
            with self.driver.session() as session:
                for index in indexes:
                    try:
                        session.run(index)
                        logger.debug(f"Created player profile index: {index}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(
                                f"Player profile index already exists: {index}"
                            )
                        else:
                            logger.error(
                                f"Failed to create player profile index: {index}, Error: {e}"
                            )
                            return False

            logger.info("All player profile indexes created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating player profile indexes: {e}")
            return False

    def setup_player_profile_schema(self) -> bool:
        """
        Set up the complete player profile schema including constraints and indexes.

        Returns:
            bool: True if schema setup was successful
        """
        logger.info("Setting up Neo4j schema for player profiles")

        try:
            # Create constraints first
            if not self.create_player_profile_constraints():
                logger.error("Failed to create player profile constraints")
                return False

            # Create indexes
            if not self.create_player_profile_indexes():
                logger.error("Failed to create player profile indexes")
                return False

            # Record schema version
            self._record_player_schema_version()

            logger.info("Player profile schema setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting up player profile schema: {e}")
            return False

    def _record_player_schema_version(self) -> None:
        """Record the current player profile schema version in the database."""
        if not self.driver:
            return

        query = """
        MERGE (psv:PlayerSchemaVersion {id: 'current'})
        SET psv.version = $version,
            psv.updated_at = datetime()
        """

        try:
            with self.driver.session() as session:
                session.run(query, version=self.player_schema_version)
            logger.info(
                f"Recorded player profile schema version: {self.player_schema_version}"
            )
        except Exception as e:
            logger.error(f"Failed to record player profile schema version: {e}")

    def get_player_schema_version(self) -> str | None:
        """
        Get the current player profile schema version from the database.

        Returns:
            Optional[str]: Current player profile schema version or None if not found
        """
        if not self.driver:
            return None

        query = "MATCH (psv:PlayerSchemaVersion {id: 'current'}) RETURN psv.version as version"

        try:
            with self.driver.session() as session:
                result = session.run(query)
                record = result.single()
                return record["version"] if record else None
        except Exception as e:
            logger.error(f"Failed to get player profile schema version: {e}")
            return None

    def validate_player_profile_schema(self) -> bool:
        """
        Validate that the player profile schema is properly set up.

        Returns:
            bool: True if schema is valid
        """
        if not self.driver:
            raise PlayerProfileSchemaError("Not connected to Neo4j")

        try:
            with self.driver.session() as session:
                # Check if player profile constraints exist
                constraints_result = session.run("SHOW CONSTRAINTS")
                constraints = [record["name"] for record in constraints_result]

                expected_constraints = [
                    "player_profile_id",
                    "player_username",
                    "player_email",
                    "therapeutic_prefs_id",
                    "privacy_settings_id",
                ]

                missing_constraints = []
                for expected in expected_constraints:
                    if not any(expected in constraint for constraint in constraints):
                        missing_constraints.append(expected)

                if missing_constraints:
                    logger.error(
                        f"Missing player profile constraints: {missing_constraints}"
                    )
                    return False

                # Check if player profile indexes exist
                indexes_result = session.run("SHOW INDEXES")
                indexes = [record["name"] for record in indexes_result]

                expected_indexes = [
                    "player_username_idx",
                    "player_email_idx",
                    "player_created_at_idx",
                ]

                missing_indexes = []
                for expected in expected_indexes:
                    if not any(expected in index for index in indexes):
                        missing_indexes.append(expected)

                if missing_indexes:
                    logger.warning(
                        f"Missing player profile indexes (non-critical): {missing_indexes}"
                    )

                logger.info("Player profile schema validation completed successfully")
                return True

        except Exception as e:
            logger.error(f"Error validating player profile schema: {e}")
            return False

    def drop_player_profile_schema(self) -> bool:
        """
        Drop all player profile schema elements (constraints and indexes).
        WARNING: This is destructive and should only be used for testing.

        Returns:
            bool: True if schema was dropped successfully
        """
        if not self.driver:
            raise PlayerProfileSchemaError("Not connected to Neo4j")

        logger.warning(
            "Dropping all player profile schema elements - this is destructive!"
        )

        try:
            with self.driver.session() as session:
                # Drop player profile specific constraints
                player_constraints = [
                    "player_profile_id",
                    "player_username",
                    "player_email",
                    "therapeutic_prefs_id",
                    "privacy_settings_id",
                    "crisis_contact_id",
                    "progress_summary_id",
                ]

                constraints_result = session.run("SHOW CONSTRAINTS")
                for record in constraints_result:
                    constraint_name = record["name"]
                    if any(pc in constraint_name for pc in player_constraints):
                        session.run(f"DROP CONSTRAINT {constraint_name}")
                        logger.debug(
                            f"Dropped player profile constraint: {constraint_name}"
                        )

                # Drop player profile specific indexes
                player_indexes = [
                    "player_username_idx",
                    "player_email_idx",
                    "player_created_at_idx",
                    "player_last_login_idx",
                    "player_is_active_idx",
                    "therapeutic_intensity_idx",
                    "privacy_consent_idx",
                    "progress_total_sessions_idx",
                ]

                indexes_result = session.run("SHOW INDEXES")
                for record in indexes_result:
                    index_name = record["name"]
                    if any(pi in index_name for pi in player_indexes):
                        session.run(f"DROP INDEX {index_name}")
                        logger.debug(f"Dropped player profile index: {index_name}")

                logger.info("Player profile schema dropped successfully")
                return True

        except Exception as e:
            logger.error(f"Error dropping player profile schema: {e}")
            return False


# Utility function for player profile schema setup
def setup_player_profile_schema(
    uri: str = "bolt://localhost:7687",
    username: str = "neo4j",
    password: str = "password",
) -> bool:
    """
    Utility function to set up player profile Neo4j schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if schema setup was successful
    """
    try:
        with PlayerProfileSchemaManager(uri, username, password) as schema_manager:
            return schema_manager.setup_player_profile_schema()
    except Exception as e:
        logger.error(f"Failed to setup player profile schema: {e}")
        return False
