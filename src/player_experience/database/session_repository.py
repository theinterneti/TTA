"""

# Logseq: [[TTA.dev/Player_experience/Database/Session_repository]]
Session repository for database operations.

Handles persistence and retrieval of session data including session context,
progress markers, and session state management.
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any

from ..models.enums import ProgressMarkerType, SessionStatus, TherapeuticApproach
from ..models.session import (
    ProgressMarker,
    SessionContext,
    SessionSummary,
    TherapeuticSettings,
)

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for session data persistence and retrieval."""

    def __init__(self, redis_client=None, neo4j_driver=None):
        """
        Initialize session repository with database connections.

        Args:
            redis_client: Redis client for session state caching
            neo4j_driver: Neo4j driver for persistent session storage
        """
        self.redis_client = redis_client
        self.neo4j_driver = neo4j_driver
        self._session_cache_ttl = 3600  # 1 hour cache TTL

    async def create_session(self, session_context: SessionContext) -> bool:
        """
        Create a new session in the database.

        Args:
            session_context: Session context to create

        Returns:
            bool: True if session was created successfully
        """
        try:
            # Store in Redis for fast access
            if self.redis_client:
                session_key = f"session:{session_context.session_id}"
                session_data = self._serialize_session_context(session_context)
                await self.redis_client.setex(
                    session_key, self._session_cache_ttl, json.dumps(session_data)
                )

            # Store in Neo4j for persistence
            if self.neo4j_driver:
                await self._create_session_in_neo4j(session_context)

            logger.info(f"Created session {session_context.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create session {session_context.session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> SessionContext | None:
        """
        Retrieve a session by ID.

        Args:
            session_id: ID of the session to retrieve

        Returns:
            SessionContext if found, None otherwise
        """
        try:
            # Try Redis cache first
            if self.redis_client:
                session_key = f"session:{session_id}"
                cached_data = await self.redis_client.get(session_key)
                if cached_data:
                    session_data = json.loads(cached_data)
                    return self._deserialize_session_context(session_data)

            # Fall back to Neo4j
            if self.neo4j_driver:
                return await self._get_session_from_neo4j(session_id)

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            return None

    async def update_session(self, session_context: SessionContext) -> bool:
        """
        Update an existing session.

        Args:
            session_context: Updated session context

        Returns:
            bool: True if session was updated successfully
        """
        try:
            # Update Redis cache
            if self.redis_client:
                session_key = f"session:{session_context.session_id}"
                session_data = self._serialize_session_context(session_context)
                await self.redis_client.setex(
                    session_key, self._session_cache_ttl, json.dumps(session_data)
                )

            # Update Neo4j
            if self.neo4j_driver:
                await self._update_session_in_neo4j(session_context)

            logger.info(f"Updated session {session_context.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update session {session_context.session_id}: {e}")
            return False

    async def pause_session(self, session_id: str) -> bool:
        """
        Pause an active session.

        Args:
            session_id: ID of the session to pause

        Returns:
            bool: True if session was paused successfully
        """
        session = await self.get_session(session_id)
        if session and session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.PAUSED
            session.last_interaction = datetime.now()
            return await self.update_session(session)
        return False

    async def resume_session(self, session_id: str) -> bool:
        """
        Resume a paused session.

        Args:
            session_id: ID of the session to resume

        Returns:
            bool: True if session was resumed successfully
        """
        session = await self.get_session(session_id)
        if session and session.status == SessionStatus.PAUSED:
            session.status = SessionStatus.ACTIVE
            session.last_interaction = datetime.now()
            return await self.update_session(session)
        return False

    async def end_session(self, session_id: str) -> bool:
        """
        End an active or paused session.

        Args:
            session_id: ID of the session to end

        Returns:
            bool: True if session was ended successfully
        """
        session = await self.get_session(session_id)
        if session and session.status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            session.status = SessionStatus.COMPLETED
            session.last_interaction = datetime.now()

            # Calculate total duration
            duration = session.get_session_duration()
            session.total_duration_minutes = int(duration.total_seconds() / 60)

            return await self.update_session(session)
        return False

    async def get_player_active_sessions(self, player_id: str) -> list[SessionContext]:
        """
        Get all active sessions for a player.

        Args:
            player_id: ID of the player

        Returns:
            List of active session contexts
        """
        try:
            if self.neo4j_driver:
                return await self._get_player_sessions_from_neo4j(
                    player_id, [SessionStatus.ACTIVE, SessionStatus.PAUSED]
                )
            return []

        except Exception as e:
            logger.error(f"Failed to get active sessions for player {player_id}: {e}")
            return []

    async def get_character_active_session(
        self, character_id: str
    ) -> SessionContext | None:
        """
        Get the active session for a specific character.

        Args:
            character_id: ID of the character

        Returns:
            Active session context if found, None otherwise
        """
        try:
            if self.neo4j_driver:
                sessions = await self._get_character_sessions_from_neo4j(
                    character_id, [SessionStatus.ACTIVE]
                )
                return sessions[0] if sessions else None
            return None

        except Exception as e:
            logger.error(
                f"Failed to get active session for character {character_id}: {e}"
            )
            return None

    async def get_session_summaries(
        self, player_id: str, limit: int = 10
    ) -> list[SessionSummary]:
        """
        Get recent session summaries for a player.

        Args:
            player_id: ID of the player
            limit: Maximum number of summaries to return

        Returns:
            List of session summaries
        """
        try:
            if self.neo4j_driver:
                return await self._get_session_summaries_from_neo4j(player_id, limit)
            return []

        except Exception as e:
            logger.error(f"Failed to get session summaries for player {player_id}: {e}")
            return []

    def _serialize_session_context(self, session: SessionContext) -> dict[str, Any]:
        """Serialize session context for storage."""
        data = asdict(session)

        # Convert datetime objects to ISO strings
        data["created_at"] = session.created_at.isoformat()
        data["last_interaction"] = session.last_interaction.isoformat()

        # Convert enums to strings
        data["status"] = session.status.value
        data["therapeutic_settings"]["preferred_approaches"] = [
            approach.value
            for approach in session.therapeutic_settings.preferred_approaches
        ]

        # Convert progress markers
        for marker_data in data["progress_markers"]:
            marker_data["marker_type"] = marker_data["marker_type"].value
            marker_data["achieved_at"] = marker_data["achieved_at"].isoformat()

        return data

    def _deserialize_session_context(self, data: dict[str, Any]) -> SessionContext:
        """Deserialize session context from storage."""
        # Convert ISO strings back to datetime objects
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_interaction"] = datetime.fromisoformat(data["last_interaction"])

        # Convert string back to enum
        data["status"] = SessionStatus(data["status"])

        # Convert therapeutic settings
        therapeutic_data = data["therapeutic_settings"]
        therapeutic_data["preferred_approaches"] = [
            TherapeuticApproach(approach)
            for approach in therapeutic_data["preferred_approaches"]
        ]
        therapeutic_settings = TherapeuticSettings(**therapeutic_data)
        data["therapeutic_settings"] = therapeutic_settings

        # Convert progress markers
        progress_markers = []
        for marker_data in data["progress_markers"]:
            marker_data["marker_type"] = ProgressMarkerType(marker_data["marker_type"])
            marker_data["achieved_at"] = datetime.fromisoformat(
                marker_data["achieved_at"]
            )
            progress_markers.append(ProgressMarker(**marker_data))
        data["progress_markers"] = progress_markers

        return SessionContext(**data)

    async def _create_session_in_neo4j(self, session: SessionContext) -> None:
        """Create session in Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            CREATE (s:Session {
                session_id: $session_id,
                player_id: $player_id,
                character_id: $character_id,
                world_id: $world_id,
                status: $status,
                created_at: $created_at,
                last_interaction: $last_interaction,
                interaction_count: $interaction_count,
                total_duration_minutes: $total_duration_minutes,
                current_scene_id: $current_scene_id,
                session_variables: $session_variables,
                therapeutic_interventions_used: $therapeutic_interventions_used,
                therapeutic_settings: $therapeutic_settings
            })
            """

            # Use serializer to ensure enums and datetimes are converted
            _data = self._serialize_session_context(session)
            await neo4j_session.run(
                query,
                {
                    "session_id": _data["session_id"],
                    "player_id": _data["player_id"],
                    "character_id": _data["character_id"],
                    "world_id": _data["world_id"],
                    "status": _data["status"],
                    "created_at": _data["created_at"],
                    "last_interaction": _data["last_interaction"],
                    "interaction_count": _data["interaction_count"],
                    "total_duration_minutes": _data["total_duration_minutes"],
                    "current_scene_id": _data["current_scene_id"],
                    "session_variables": json.dumps(_data["session_variables"]),
                    "therapeutic_interventions_used": _data[
                        "therapeutic_interventions_used"
                    ],
                    "therapeutic_settings": json.dumps(_data["therapeutic_settings"]),
                },
            )

    async def _update_session_in_neo4j(self, session: SessionContext) -> None:
        """Update session in Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            MATCH (s:Session {session_id: $session_id})
            SET s.status = $status,
                s.last_interaction = $last_interaction,
                s.interaction_count = $interaction_count,
                s.total_duration_minutes = $total_duration_minutes,
                s.current_scene_id = $current_scene_id,
                s.session_variables = $session_variables,
                s.therapeutic_interventions_used = $therapeutic_interventions_used,
                s.therapeutic_settings = $therapeutic_settings
            """

            _data = self._serialize_session_context(session)
            await neo4j_session.run(
                query,
                {
                    "session_id": _data["session_id"],
                    "status": _data["status"],
                    "last_interaction": _data["last_interaction"],
                    "interaction_count": _data["interaction_count"],
                    "total_duration_minutes": _data["total_duration_minutes"],
                    "current_scene_id": _data["current_scene_id"],
                    "session_variables": json.dumps(_data["session_variables"]),
                    "therapeutic_interventions_used": _data[
                        "therapeutic_interventions_used"
                    ],
                    "therapeutic_settings": json.dumps(_data["therapeutic_settings"]),
                },
            )

    async def _get_session_from_neo4j(self, session_id: str) -> SessionContext | None:
        """Retrieve session from Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            MATCH (s:Session {session_id: $session_id})
            RETURN s
            """

            result = await neo4j_session.run(query, {"session_id": session_id})
            record = await result.single()

            if record:
                session_data = dict(record["s"])
                return self._neo4j_record_to_session_context(session_data)

            return None

    async def _get_player_sessions_from_neo4j(
        self, player_id: str, statuses: list[SessionStatus]
    ) -> list[SessionContext]:
        """Get player sessions from Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            MATCH (s:Session {player_id: $player_id})
            WHERE s.status IN $statuses
            RETURN s
            ORDER BY s.last_interaction DESC
            """

            status_values = [status.value for status in statuses]
            result = await neo4j_session.run(
                query, {"player_id": player_id, "statuses": status_values}
            )

            sessions = []
            async for record in result:
                session_data = dict(record["s"])
                session = self._neo4j_record_to_session_context(session_data)
                sessions.append(session)

            return sessions

    async def _get_character_sessions_from_neo4j(
        self, character_id: str, statuses: list[SessionStatus]
    ) -> list[SessionContext]:
        """Get character sessions from Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            MATCH (s:Session {character_id: $character_id})
            WHERE s.status IN $statuses
            RETURN s
            ORDER BY s.last_interaction DESC
            """

            status_values = [status.value for status in statuses]
            result = await neo4j_session.run(
                query, {"character_id": character_id, "statuses": status_values}
            )

            sessions = []
            async for record in result:
                session_data = dict(record["s"])
                session = self._neo4j_record_to_session_context(session_data)
                sessions.append(session)

            return sessions

    async def _get_session_summaries_from_neo4j(
        self, player_id: str, limit: int
    ) -> list[SessionSummary]:
        """Get session summaries from Neo4j database."""
        assert self.neo4j_driver is not None, "Neo4j driver must be initialized"
        async with self.neo4j_driver.session() as neo4j_session:
            query = """
            MATCH (s:Session {player_id: $player_id})
            MATCH (c:Character {character_id: s.character_id})
            MATCH (w:World {world_id: s.world_id})
            RETURN s, c.name as character_name, w.name as world_name
            ORDER BY s.last_interaction DESC
            LIMIT $limit
            """

            result = await neo4j_session.run(
                query, {"player_id": player_id, "limit": limit}
            )

            summaries = []
            async for record in result:
                session_data = dict(record["s"])
                summary = SessionSummary(
                    session_id=session_data["session_id"],
                    character_name=record["character_name"],
                    world_name=record["world_name"],
                    start_time=datetime.fromisoformat(session_data["created_at"]),
                    end_time=(
                        datetime.fromisoformat(session_data["last_interaction"])
                        if session_data["status"] == "completed"
                        else None
                    ),
                    duration_minutes=session_data["total_duration_minutes"],
                    status=SessionStatus(session_data["status"]),
                    progress_markers_count=len(
                        session_data.get("progress_markers", [])
                    ),
                    therapeutic_interventions_count=len(
                        session_data.get("therapeutic_interventions_used", [])
                    ),
                )
                summaries.append(summary)

            return summaries

    def _neo4j_record_to_session_context(
        self, session_data: dict[str, Any]
    ) -> SessionContext:
        """Convert Neo4j record to SessionContext."""
        # Parse JSON fields
        session_variables = json.loads(session_data.get("session_variables", "{}"))
        therapeutic_settings_data = json.loads(
            session_data.get("therapeutic_settings", "{}")
        )

        # Create therapeutic settings
        therapeutic_settings_data["preferred_approaches"] = [
            TherapeuticApproach(approach)
            for approach in therapeutic_settings_data.get("preferred_approaches", [])
        ]
        therapeutic_settings = TherapeuticSettings(**therapeutic_settings_data)

        return SessionContext(
            session_id=session_data["session_id"],
            player_id=session_data["player_id"],
            character_id=session_data["character_id"],
            world_id=session_data["world_id"],
            therapeutic_settings=therapeutic_settings,
            status=SessionStatus(session_data["status"]),
            created_at=datetime.fromisoformat(session_data["created_at"]),
            last_interaction=datetime.fromisoformat(session_data["last_interaction"]),
            current_scene_id=session_data.get("current_scene_id"),
            session_variables=session_variables,
            interaction_count=session_data.get("interaction_count", 0),
            total_duration_minutes=session_data.get("total_duration_minutes", 0),
            therapeutic_interventions_used=session_data.get(
                "therapeutic_interventions_used", []
            ),
            emotional_state_history=session_data.get("emotional_state_history", []),
            crisis_alerts_triggered=session_data.get("crisis_alerts_triggered", []),
        )
