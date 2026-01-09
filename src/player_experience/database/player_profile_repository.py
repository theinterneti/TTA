"""

# Logseq: [[TTA.dev/Player_experience/Database/Player_profile_repository]]
Repository for Player Profile database operations.

This module provides data access layer for player profiles,
handling CRUD operations and data persistence in Neo4j.
"""

import contextlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

try:
    from neo4j import Driver, GraphDatabase, Result, Session
    from neo4j.exceptions import ClientError, ServiceUnavailable
except ImportError:
    logger.warning(
        "Warning: neo4j package not installed. Install with: pip install neo4j"
    )
    GraphDatabase = None
    Driver = None
    Session = None
    Result = None
    ServiceUnavailable = Exception
    ClientError = Exception

from ..models.enums import IntensityLevel, TherapeuticApproach
from ..models.player import (
    CrisisContactInfo,
    PlayerProfile,
    PrivacySettings,
    ProgressSummary,
    TherapeuticPreferences,
)

logger = logging.getLogger(__name__)


class PlayerProfileRepositoryError(Exception):
    """Raised when player profile repository operations fail."""

    pass


class PlayerProfileRepository:
    """
    Repository for player profile data access operations.

    This class handles all database operations for player profiles,
    including CRUD operations, data validation, and relationship management.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize Player Profile Repository.

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
        self.driver: Driver | None = None  # type: ignore[name-defined]

    def connect(self) -> None:
        """Establish connection to Neo4j database with retry/backoff for readiness races."""
        try:
            from neo4j.exceptions import (
                AuthError,
            )
            from neo4j.exceptions import (
                ClientError as _ClientError,
            )
            from neo4j.exceptions import (
                ServiceUnavailable as _ServiceUnavailable,
            )
        except Exception:  # pragma: no cover - neo4j not installed path
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = ServiceUnavailable  # type: ignore
            _ClientError = Exception  # type: ignore
        base_delay = 0.5
        last_exc: Exception | None = None
        # Option B: increase attempts to 6 (0.5,1,2,4,8,8)
        attempts = 6
        for attempt in range(attempts):
            try:
                assert GraphDatabase is not None, "GraphDatabase must be available"
                self.driver = GraphDatabase.driver(
                    self.uri, auth=(self.username, self.password)
                )
                assert self.driver is not None, "Driver must be initialized"
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"PlayerProfileRepository connected to Neo4j at {self.uri}")
                return
            except (AuthError, _ServiceUnavailable) as e:
                last_exc = e
                delay = min(base_delay * (2**attempt), 8.0)
                logger.debug(
                    f"Neo4j connect attempt {attempt + 1}/{attempts} failed ({e!s}); retrying in {delay:.1f}s"
                )
                with contextlib.suppress(Exception):
                    if self.driver:
                        self.driver.close()
                self.driver = None
                import time as _t

                if attempt < (attempts - 1):
                    _t.sleep(delay)
                elif isinstance(e, (AuthError, _ServiceUnavailable)):
                    raise PlayerProfileRepositoryError(
                        f"Failed to connect to Neo4j after retries: {e}"
                    ) from e
            except _ClientError as e:
                emsg = str(e)
                if ("AuthenticationRateLimit" in emsg) or (
                    "authentication details too many times" in emsg
                ):
                    last_exc = e
                    delay = min(base_delay * (2**attempt), 8.0)
                    logger.debug(
                        f"Neo4j connect attempt {attempt + 1}/5 hit AuthenticationRateLimit; retrying in {delay:.1f}s"
                    )
                    with contextlib.suppress(Exception):
                        if self.driver:
                            self.driver.close()
                    self.driver = None
                    import time as _t

                    if attempt < (attempts - 1):
                        _t.sleep(delay)
                    else:
                        raise PlayerProfileRepositoryError(
                            f"Failed to connect to Neo4j after retries: {e}"
                        ) from e
                else:
                    raise PlayerProfileRepositoryError(
                        f"Unexpected error connecting to Neo4j: {e}"
                    ) from e
            except Exception as e:
                raise PlayerProfileRepositoryError(
                    f"Unexpected error connecting to Neo4j: {e}"
                ) from e
        if last_exc is not None:
            raise PlayerProfileRepositoryError(
                f"Failed to connect to Neo4j after retries: {last_exc}"
            )

    def disconnect(self) -> None:
        """Close connection to Neo4j database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("PlayerProfileRepository disconnected from Neo4j")

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

    def _serialize_therapeutic_preferences(
        self, prefs: TherapeuticPreferences
    ) -> dict[str, Any]:
        """
        Serialize therapeutic preferences for database storage.

        Args:
            prefs: TherapeuticPreferences object

        Returns:
            Dict[str, Any]: Serialized preferences data
        """
        return {
            "preferences_id": str(uuid.uuid4()),
            "intensity_level": prefs.intensity_level.value,
            "preferred_approaches": [
                approach.value for approach in prefs.preferred_approaches
            ],
            "trigger_warnings": prefs.trigger_warnings,
            "comfort_topics": prefs.comfort_topics,
            "avoid_topics": prefs.avoid_topics,
            "session_duration_preference": prefs.session_duration_preference,
            "reminder_frequency": prefs.reminder_frequency,
            "crisis_contact_info": (
                json.dumps(
                    {
                        "primary_contact_name": (
                            prefs.crisis_contact_info.primary_contact_name
                            if prefs.crisis_contact_info
                            else None
                        ),
                        "primary_contact_phone": (
                            prefs.crisis_contact_info.primary_contact_phone
                            if prefs.crisis_contact_info
                            else None
                        ),
                        "therapist_name": (
                            prefs.crisis_contact_info.therapist_name
                            if prefs.crisis_contact_info
                            else None
                        ),
                        "therapist_phone": (
                            prefs.crisis_contact_info.therapist_phone
                            if prefs.crisis_contact_info
                            else None
                        ),
                        "crisis_hotline_preference": (
                            prefs.crisis_contact_info.crisis_hotline_preference
                            if prefs.crisis_contact_info
                            else None
                        ),
                        "emergency_instructions": (
                            prefs.crisis_contact_info.emergency_instructions
                            if prefs.crisis_contact_info
                            else None
                        ),
                    }
                )
                if prefs.crisis_contact_info
                else None
            ),
        }

    def _serialize_privacy_settings(self, privacy: PrivacySettings) -> dict[str, Any]:
        """
        Serialize privacy settings for database storage.

        Args:
            privacy: PrivacySettings object

        Returns:
            Dict[str, Any]: Serialized privacy settings data
        """
        data = {
            "settings_id": str(uuid.uuid4()),
            "data_collection_consent": privacy.data_collection_consent,
            "research_participation_consent": privacy.research_participation_consent,
            "progress_sharing_enabled": privacy.progress_sharing_enabled,
            "anonymous_analytics_enabled": privacy.anonymous_analytics_enabled,
            "session_recording_enabled": privacy.session_recording_enabled,
            "data_retention_period_days": privacy.data_retention_period_days,
            "third_party_sharing_consent": privacy.third_party_sharing_consent,
            "collect_interaction_patterns": privacy.collect_interaction_patterns,
            "collect_emotional_responses": privacy.collect_emotional_responses,
            "collect_therapeutic_outcomes": privacy.collect_therapeutic_outcomes,
            "collect_usage_statistics": privacy.collect_usage_statistics,
        }

        # Include authentication data if present (temporary solution)
        if hasattr(privacy, "__dict__"):
            auth_data = getattr(privacy, "__dict__", {})
            if "password_hash" in auth_data:
                data["password_hash"] = auth_data["password_hash"]
            if "role" in auth_data:
                data["role"] = auth_data["role"]

        return data

    def _serialize_progress_summary(self, progress: ProgressSummary) -> dict[str, Any]:
        """
        Serialize progress summary for database storage.

        Args:
            progress: ProgressSummary object

        Returns:
            Dict[str, Any]: Serialized progress summary data
        """
        return {
            "summary_id": str(uuid.uuid4()),
            "total_sessions": progress.total_sessions,
            "total_time_minutes": progress.total_time_minutes,
            "milestones_achieved": progress.milestones_achieved,
            "current_streak_days": progress.current_streak_days,
            "longest_streak_days": progress.longest_streak_days,
            "favorite_therapeutic_approach": (
                progress.favorite_therapeutic_approach.value
                if progress.favorite_therapeutic_approach
                else None
            ),
            "most_effective_world_type": progress.most_effective_world_type,
            "last_session_date": (
                progress.last_session_date.isoformat()
                if progress.last_session_date
                else None
            ),
            "next_recommended_session": (
                progress.next_recommended_session.isoformat()
                if progress.next_recommended_session
                else None
            ),
        }

    def create_player_profile(self, profile: PlayerProfile) -> bool:
        """
        Create a new player profile in the database.

        Args:
            profile: PlayerProfile object to create

        Returns:
            bool: True if profile was created successfully
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        # Serialize related objects
        therapeutic_prefs_data = self._serialize_therapeutic_preferences(
            profile.therapeutic_preferences
        )
        privacy_settings_data = self._serialize_privacy_settings(
            profile.privacy_settings
        )
        progress_summary_data = self._serialize_progress_summary(
            profile.progress_summary
        )

        query = """
        // Create player profile
        CREATE (p:PlayerProfile {
            player_id: $player_id,
            username: $username,
            email: $email,
            created_at: datetime($created_at),
            last_login: datetime($last_login),
            is_active: $is_active,
            characters: $characters,
            active_sessions: $active_sessions
        })

        // Create therapeutic preferences
        CREATE (tp:TherapeuticPreferences $therapeutic_prefs)
        CREATE (p)-[:HAS_THERAPEUTIC_PREFERENCES]->(tp)

        // Create privacy settings
        CREATE (ps:PrivacySettings $privacy_settings)
        CREATE (p)-[:HAS_PRIVACY_SETTINGS]->(ps)

        // Create progress summary
        CREATE (pr:ProgressSummary $progress_summary)
        CREATE (p)-[:HAS_PROGRESS_SUMMARY]->(pr)

        RETURN p
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player_id=profile.player_id,
                    username=profile.username,
                    email=profile.email,
                    created_at=profile.created_at.isoformat(),
                    last_login=(
                        profile.last_login.isoformat() if profile.last_login else None
                    ),
                    is_active=profile.is_active,
                    characters=profile.characters,
                    active_sessions=json.dumps(profile.active_sessions),
                    therapeutic_prefs=therapeutic_prefs_data,
                    privacy_settings=privacy_settings_data,
                    progress_summary=progress_summary_data,
                )

                record = result.single()
                if record:
                    logger.info(f"Created player profile: {profile.player_id}")
                    return True
                logger.error(f"Failed to create player profile: {profile.player_id}")
                return False

        except ClientError as e:
            if "already exists" in str(e).lower():
                logger.error(f"Player profile already exists: {profile.player_id}")
                raise PlayerProfileRepositoryError(
                    f"Player profile already exists: {profile.player_id}"
                ) from e
            logger.error(f"Error creating player profile: {e}")
            raise PlayerProfileRepositoryError(
                f"Error creating player profile: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error creating player profile: {e}")
            raise PlayerProfileRepositoryError(
                f"Unexpected error creating player profile: {e}"
            ) from e

    def get_player_profile(self, player_id: str) -> PlayerProfile | None:
        """
        Retrieve a player profile by ID.

        Args:
            player_id: Player identifier

        Returns:
            Optional[PlayerProfile]: Player profile if found, None otherwise
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {player_id: $player_id})
        OPTIONAL MATCH (p)-[:HAS_THERAPEUTIC_PREFERENCES]->(tp:TherapeuticPreferences)
        OPTIONAL MATCH (p)-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
        OPTIONAL MATCH (p)-[:HAS_PROGRESS_SUMMARY]->(pr:ProgressSummary)
        RETURN p, tp, ps, pr
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, player_id=player_id)
                record = result.single()

                if not record or not record["p"]:
                    return None

                # Deserialize player profile data
                player_data = dict(record["p"])
                therapeutic_prefs_data = dict(record["tp"]) if record["tp"] else {}
                privacy_settings_data = dict(record["ps"]) if record["ps"] else {}
                progress_summary_data = dict(record["pr"]) if record["pr"] else {}

                # Reconstruct therapeutic preferences
                therapeutic_prefs = TherapeuticPreferences()
                if therapeutic_prefs_data:
                    therapeutic_prefs.intensity_level = IntensityLevel(
                        therapeutic_prefs_data.get("intensity_level", "medium")
                    )
                    therapeutic_prefs.preferred_approaches = [
                        TherapeuticApproach(approach)
                        for approach in therapeutic_prefs_data.get(
                            "preferred_approaches", []
                        )
                    ]
                    therapeutic_prefs.trigger_warnings = therapeutic_prefs_data.get(
                        "trigger_warnings", []
                    )
                    therapeutic_prefs.comfort_topics = therapeutic_prefs_data.get(
                        "comfort_topics", []
                    )
                    therapeutic_prefs.avoid_topics = therapeutic_prefs_data.get(
                        "avoid_topics", []
                    )
                    therapeutic_prefs.session_duration_preference = (
                        therapeutic_prefs_data.get("session_duration_preference", 30)
                    )
                    therapeutic_prefs.reminder_frequency = therapeutic_prefs_data.get(
                        "reminder_frequency", "weekly"
                    )

                    # Deserialize crisis contact info
                    crisis_info_json = therapeutic_prefs_data.get("crisis_contact_info")
                    if crisis_info_json:
                        crisis_info_data = json.loads(crisis_info_json)
                        therapeutic_prefs.crisis_contact_info = CrisisContactInfo(
                            primary_contact_name=crisis_info_data.get(
                                "primary_contact_name"
                            ),
                            primary_contact_phone=crisis_info_data.get(
                                "primary_contact_phone"
                            ),
                            therapist_name=crisis_info_data.get("therapist_name"),
                            therapist_phone=crisis_info_data.get("therapist_phone"),
                            crisis_hotline_preference=crisis_info_data.get(
                                "crisis_hotline_preference"
                            ),
                            emergency_instructions=crisis_info_data.get(
                                "emergency_instructions"
                            ),
                        )

                # Reconstruct privacy settings
                privacy_settings = PrivacySettings()
                if privacy_settings_data:
                    privacy_settings.data_collection_consent = (
                        privacy_settings_data.get("data_collection_consent", True)
                    )
                    privacy_settings.research_participation_consent = (
                        privacy_settings_data.get(
                            "research_participation_consent", False
                        )
                    )
                    privacy_settings.progress_sharing_enabled = (
                        privacy_settings_data.get("progress_sharing_enabled", False)
                    )
                    privacy_settings.anonymous_analytics_enabled = (
                        privacy_settings_data.get("anonymous_analytics_enabled", True)
                    )
                    privacy_settings.session_recording_enabled = (
                        privacy_settings_data.get("session_recording_enabled", False)
                    )
                    privacy_settings.data_retention_period_days = (
                        privacy_settings_data.get("data_retention_period_days", 365)
                    )
                    privacy_settings.third_party_sharing_consent = (
                        privacy_settings_data.get("third_party_sharing_consent", False)
                    )
                    privacy_settings.collect_interaction_patterns = (
                        privacy_settings_data.get("collect_interaction_patterns", True)
                    )
                    privacy_settings.collect_emotional_responses = (
                        privacy_settings_data.get("collect_emotional_responses", True)
                    )
                    privacy_settings.collect_therapeutic_outcomes = (
                        privacy_settings_data.get("collect_therapeutic_outcomes", True)
                    )
                    privacy_settings.collect_usage_statistics = (
                        privacy_settings_data.get("collect_usage_statistics", True)
                    )

                    # Restore authentication data if present (temporary solution)
                    # Using setattr for dynamic attributes not in PrivacySettings dataclass
                    if "password_hash" in privacy_settings_data:
                        privacy_settings.password_hash = privacy_settings_data[
                            "password_hash"
                        ]
                    if "role" in privacy_settings_data:
                        privacy_settings.role = privacy_settings_data["role"]

                # Reconstruct progress summary
                progress_summary = ProgressSummary()
                if progress_summary_data:
                    progress_summary.total_sessions = progress_summary_data.get(
                        "total_sessions", 0
                    )
                    progress_summary.total_time_minutes = progress_summary_data.get(
                        "total_time_minutes", 0
                    )
                    progress_summary.milestones_achieved = progress_summary_data.get(
                        "milestones_achieved", 0
                    )
                    progress_summary.current_streak_days = progress_summary_data.get(
                        "current_streak_days", 0
                    )
                    progress_summary.longest_streak_days = progress_summary_data.get(
                        "longest_streak_days", 0
                    )

                    fav_approach = progress_summary_data.get(
                        "favorite_therapeutic_approach"
                    )
                    if fav_approach:
                        progress_summary.favorite_therapeutic_approach = (
                            TherapeuticApproach(fav_approach)
                        )

                    progress_summary.most_effective_world_type = (
                        progress_summary_data.get("most_effective_world_type")
                    )

                    def _to_datetime(val: Any) -> datetime | None:
                        if isinstance(val, datetime):
                            return val
                        if val is None:
                            return None
                        # Neo4j temporal objects often expose to_native()
                        conv = getattr(val, "to_native", None)
                        if callable(conv):
                            with contextlib.suppress(Exception):
                                result = conv()
                                if isinstance(result, datetime):
                                    return result
                        if isinstance(val, str):
                            try:
                                return datetime.fromisoformat(val)
                            except Exception:
                                return None
                        return None

                    last_session_val = progress_summary_data.get("last_session_date")
                    parsed_last = _to_datetime(last_session_val)
                    if parsed_last:
                        progress_summary.last_session_date = parsed_last

                    next_session_val = progress_summary_data.get(
                        "next_recommended_session"
                    )
                    parsed_next = _to_datetime(next_session_val)
                    if parsed_next:
                        progress_summary.next_recommended_session = parsed_next

                # Reconstruct player profile
                def _to_dt_profile(val: Any) -> datetime | None:
                    if isinstance(val, datetime):
                        return val
                    conv = getattr(val, "to_native", None)
                    if callable(conv):
                        with contextlib.suppress(Exception):
                            result = conv()
                            if isinstance(result, datetime):
                                return result
                    if isinstance(val, str):
                        try:
                            return datetime.fromisoformat(val)
                        except Exception:
                            return None
                    return None

                created_at_val = player_data.get("created_at")
                created_at_dt = _to_dt_profile(created_at_val) or datetime.utcnow()
                last_login_val = player_data.get("last_login")
                last_login_dt = (
                    _to_dt_profile(last_login_val) if last_login_val else None
                )

                # Safely parse active_sessions whether stored as JSON string or already a dict
                _active_raw = player_data.get("active_sessions", "{}")
                if isinstance(_active_raw, str):
                    try:
                        _active_parsed = json.loads(_active_raw)
                    except Exception:
                        _active_parsed = {}
                else:
                    _active_parsed = _active_raw or {}

                return PlayerProfile(
                    player_id=player_data["player_id"],
                    username=player_data["username"],
                    email=player_data["email"],
                    created_at=created_at_dt,
                    therapeutic_preferences=therapeutic_prefs,
                    privacy_settings=privacy_settings,
                    characters=player_data.get("characters", []),
                    active_sessions=_active_parsed,
                    progress_summary=progress_summary,
                    last_login=last_login_dt,
                    is_active=player_data.get("is_active", True),
                )

        except Exception as e:
            # If the query fails (e.g., label doesn't exist), return None
            # This allows the system to gracefully handle empty databases
            logger.warning(f"Error retrieving player profile {player_id}: {e}")
            return None

    def update_player_profile(self, profile: PlayerProfile) -> bool:
        """
        Update an existing player profile.

        Args:
            profile: Updated PlayerProfile object

        Returns:
            bool: True if profile was updated successfully
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        # Serialize related objects
        therapeutic_prefs_data = self._serialize_therapeutic_preferences(
            profile.therapeutic_preferences
        )
        privacy_settings_data = self._serialize_privacy_settings(
            profile.privacy_settings
        )
        progress_summary_data = self._serialize_progress_summary(
            profile.progress_summary
        )

        query = """
        MATCH (p:PlayerProfile {player_id: $player_id})
        SET p.username = $username,
            p.email = $email,
            p.last_login = datetime($last_login),
            p.is_active = $is_active,
            p.characters = $characters,
            p.active_sessions = $active_sessions

        WITH p
        // Update therapeutic preferences
        OPTIONAL MATCH (p)-[:HAS_THERAPEUTIC_PREFERENCES]->(tp:TherapeuticPreferences)
        SET tp += $therapeutic_prefs

        WITH p
        // Update privacy settings
        OPTIONAL MATCH (p)-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
        SET ps += $privacy_settings

        WITH p
        // Update progress summary
        OPTIONAL MATCH (p)-[:HAS_PROGRESS_SUMMARY]->(pr:ProgressSummary)
        SET pr += $progress_summary

        RETURN p
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player_id=profile.player_id,
                    username=profile.username,
                    email=profile.email,
                    last_login=(
                        profile.last_login.isoformat() if profile.last_login else None
                    ),
                    is_active=profile.is_active,
                    characters=profile.characters,
                    active_sessions=json.dumps(profile.active_sessions),
                    therapeutic_prefs=therapeutic_prefs_data,
                    privacy_settings=privacy_settings_data,
                    progress_summary=progress_summary_data,
                )

                record = result.single()
                if record:
                    logger.info(f"Updated player profile: {profile.player_id}")
                    return True
                logger.error(
                    f"Player profile not found for update: {profile.player_id}"
                )
                return False

        except Exception as e:
            logger.error(f"Error updating player profile {profile.player_id}: {e}")
            raise PlayerProfileRepositoryError(
                f"Error updating player profile: {e}"
            ) from e

    def delete_player_profile(self, player_id: str) -> bool:
        """
        Delete a player profile and all related data.

        Args:
            player_id: Player identifier

        Returns:
            bool: True if profile was deleted successfully
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {player_id: $player_id})
        OPTIONAL MATCH (p)-[:HAS_THERAPEUTIC_PREFERENCES]->(tp:TherapeuticPreferences)
        OPTIONAL MATCH (p)-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
        OPTIONAL MATCH (p)-[:HAS_PROGRESS_SUMMARY]->(pr:ProgressSummary)
        DETACH DELETE p, tp, ps, pr
        RETURN count(p) as deleted_count
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, player_id=player_id)
                record = result.single()

                if record and record["deleted_count"] > 0:
                    logger.info(f"Deleted player profile: {player_id}")
                    return True
                logger.warning(f"Player profile not found for deletion: {player_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting player profile {player_id}: {e}")
            raise PlayerProfileRepositoryError(
                f"Error deleting player profile: {e}"
            ) from e

    def get_player_by_username(self, username: str) -> PlayerProfile | None:
        """
        Retrieve a player profile by username.

        Args:
            username: Player username

        Returns:
            Optional[PlayerProfile]: Player profile if found, None otherwise
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {username: $username})
        RETURN p.player_id as player_id
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, username=username)
                record = result.single()

                if record:
                    return self.get_player_profile(record["player_id"])
                return None
        except Exception as e:
            # If the query fails (e.g., label doesn't exist), return None
            # This allows the system to gracefully handle empty databases
            logger.warning(f"Error retrieving player by username {username}: {e}")
            return None

    def get_player_by_email(self, email: str) -> PlayerProfile | None:
        """
        Retrieve a player profile by email.

        Args:
            email: Player email

        Returns:
            Optional[PlayerProfile]: Player profile if found, None otherwise
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {email: $email})
        RETURN p.player_id as player_id
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, email=email)
                record = result.single()

                if record:
                    return self.get_player_profile(record["player_id"])
                return None

        except Exception as e:
            # If the query fails (e.g., label doesn't exist), return None
            # This allows the system to gracefully handle empty databases
            logger.warning(f"Error retrieving player by email {email}: {e}")
            return None

    def list_active_players(self, limit: int = 100) -> list[PlayerProfile]:
        """
        List active player profiles.

        Args:
            limit: Maximum number of profiles to return

        Returns:
            List[PlayerProfile]: List of active player profiles
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {is_active: true})
        RETURN p.player_id as player_id
        ORDER BY p.last_login DESC
        LIMIT $limit
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                player_ids = [record["player_id"] for record in result]

                profiles = []
                for player_id in player_ids:
                    profile = self.get_player_profile(player_id)
                    if profile:
                        profiles.append(profile)

                return profiles

        except Exception as e:
            logger.error(f"Error listing active players: {e}")
            raise PlayerProfileRepositoryError(
                f"Error listing active players: {e}"
            ) from e

    def username_exists(self, username: str) -> bool:
        """
        Check if a username already exists.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {username: $username})
        RETURN count(p) > 0 as exists
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, username=username)
                record = result.single()
                return record["exists"] if record else False

        except Exception as e:
            logger.error(f"Error checking username existence {username}: {e}")
            raise PlayerProfileRepositoryError(
                f"Error checking username existence: {e}"
            ) from e

    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists.

        Args:
            email: Email to check

        Returns:
            bool: True if email exists
        """
        if not self.driver:
            raise PlayerProfileRepositoryError("Not connected to Neo4j")

        query = """
        MATCH (p:PlayerProfile {email: $email})
        RETURN count(p) > 0 as exists
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, email=email)
                record = result.single()
                return record["exists"] if record else False

        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            raise PlayerProfileRepositoryError(
                f"Error checking email existence: {e}"
            ) from e


# Utility functions for player profile repository operations
def create_player_profile_repository(
    uri: str = "bolt://localhost:7687",
    username: str = "neo4j",
    password: str = "password",
) -> PlayerProfileRepository:
    """
    Create and connect a player profile repository.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        PlayerProfileRepository: Connected repository instance
    """
    repository = PlayerProfileRepository(uri, username, password)
    repository.connect()
    return repository
