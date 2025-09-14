"""
Session management and context switching functionality.

Handles session lifecycle management, character-world switching, and integration
with the Interactive Narrative Engine for seamless therapeutic experiences.
"""

import logging
import uuid
from typing import Any

from ..database.session_repository import SessionRepository
from ..models.enums import SessionStatus
from ..models.session import ProgressMarker, SessionContext, TherapeuticSettings

logger = logging.getLogger(__name__)


class SessionIntegrationManager:
    """Manages session context and character-world switching."""

    def __init__(
        self, session_repository: SessionRepository, interactive_narrative_engine=None
    ):
        """
        Initialize the Session Integration Manager.

        Args:
            session_repository: Repository for session data persistence
            interactive_narrative_engine: Engine for narrative interactions
        """
        self.session_repository = session_repository
        self.interactive_narrative_engine = interactive_narrative_engine
        self._active_sessions: dict[str, SessionContext] = {}  # player_id -> session

    async def create_session(
        self,
        player_id: str,
        character_id: str,
        world_id: str,
        therapeutic_settings: TherapeuticSettings | None = None,
    ) -> SessionContext | None:
        """
        Create a new therapeutic session.

        Args:
            player_id: ID of the player
            character_id: ID of the character
            world_id: ID of the world
            therapeutic_settings: Optional therapeutic settings

        Returns:
            Created session context or None if creation failed
        """
        try:
            # Generate unique session ID
            session_id = f"session_{uuid.uuid4().hex[:12]}"

            # Use default therapeutic settings if none provided
            if therapeutic_settings is None:
                therapeutic_settings = TherapeuticSettings()

            # Create session context
            session_context = SessionContext(
                session_id=session_id,
                player_id=player_id,
                character_id=character_id,
                world_id=world_id,
                therapeutic_settings=therapeutic_settings,
            )

            # Initialize with Interactive Narrative Engine if available
            if self.interactive_narrative_engine:
                await self._initialize_narrative_context(session_context)

            # Persist session
            success = await self.session_repository.create_session(session_context)
            if success:
                self._active_sessions[player_id] = session_context
                logger.info(f"Created session {session_id} for player {player_id}")
                return session_context
            else:
                logger.error(f"Failed to persist session {session_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to create session for player {player_id}: {e}")
            return None

    async def switch_character_world_context(
        self, player_id: str, new_character_id: str, new_world_id: str
    ) -> SessionContext | None:
        """
        Switch to a different character-world combination, preserving session state.

        Args:
            player_id: ID of the player
            new_character_id: ID of the new character
            new_world_id: ID of the new world

        Returns:
            New session context or None if switch failed
        """
        try:
            # Pause current session if active
            current_session = self._active_sessions.get(player_id)
            if current_session:
                await self.pause_session(player_id)

            # Check if there's an existing session for this character-world combination
            existing_session = await self._find_existing_session(
                player_id, new_character_id, new_world_id
            )

            if existing_session:
                # Resume existing session
                logger.info(f"Resuming existing session {existing_session.session_id}")
                return await self.resume_session(existing_session.session_id)
            else:
                # Create new session with preserved therapeutic settings
                therapeutic_settings = (
                    current_session.therapeutic_settings if current_session else None
                )
                return await self.create_session(
                    player_id, new_character_id, new_world_id, therapeutic_settings
                )

        except Exception as e:
            logger.error(f"Failed to switch context for player {player_id}: {e}")
            return None

    async def pause_session(self, player_id: str) -> bool:
        """
        Pause the active session for a player.

        Args:
            player_id: ID of the player

        Returns:
            True if session was paused successfully
        """
        try:
            session = self._active_sessions.get(player_id)
            if not session:
                logger.warning(f"No active session found for player {player_id}")
                return False

            # Preserve current state with Interactive Narrative Engine
            if self.interactive_narrative_engine:
                await self._preserve_narrative_state(session)

            # Update session status
            success = await self.session_repository.pause_session(session.session_id)
            if success:
                session.status = SessionStatus.PAUSED
                logger.info(f"Paused session {session.session_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to pause session for player {player_id}: {e}")
            return False

    async def resume_session(self, session_id: str) -> SessionContext | None:
        """
        Resume a paused session.

        Args:
            session_id: ID of the session to resume

        Returns:
            Resumed session context or None if resume failed
        """
        try:
            # Get session from repository
            session = await self.session_repository.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None

            if session.status != SessionStatus.PAUSED:
                logger.warning(
                    f"Session {session_id} is not paused (status: {session.status})"
                )
                return None

            # Resume with Interactive Narrative Engine
            if self.interactive_narrative_engine:
                await self._restore_narrative_state(session)

            # Update session status
            success = await self.session_repository.resume_session(session_id)
            if success:
                session.status = SessionStatus.ACTIVE
                self._active_sessions[session.player_id] = session
                logger.info(f"Resumed session {session_id}")
                return session

            return None

        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return None

    async def end_session(self, player_id: str) -> bool:
        """
        End the active session for a player.

        Args:
            player_id: ID of the player

        Returns:
            True if session was ended successfully
        """
        try:
            session = self._active_sessions.get(player_id)
            if not session:
                logger.warning(f"No active session found for player {player_id}")
                return False

            # Finalize with Interactive Narrative Engine
            if self.interactive_narrative_engine:
                await self._finalize_narrative_session(session)

            # Update session status
            success = await self.session_repository.end_session(session.session_id)
            if success:
                session.status = SessionStatus.COMPLETED
                # Remove from active sessions
                del self._active_sessions[player_id]
                logger.info(f"Ended session {session.session_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to end session for player {player_id}: {e}")
            return False

    async def get_active_session(self, player_id: str) -> SessionContext | None:
        """
        Get the active session for a player.

        Args:
            player_id: ID of the player

        Returns:
            Active session context or None if no active session
        """
        # Check in-memory cache first
        session = self._active_sessions.get(player_id)
        if session and session.is_active():
            return session

        # Check repository for active sessions
        active_sessions = await self.session_repository.get_player_active_sessions(
            player_id
        )
        if active_sessions:
            # Use the most recent active session
            session = active_sessions[0]
            self._active_sessions[player_id] = session
            return session

        return None

    async def update_session_interaction(
        self, player_id: str, interaction_data: dict[str, Any]
    ) -> bool:
        """
        Update session with new interaction data.

        Args:
            player_id: ID of the player
            interaction_data: Data from the interaction

        Returns:
            True if session was updated successfully
        """
        try:
            session = await self.get_active_session(player_id)
            if not session:
                logger.warning(f"No active session found for player {player_id}")
                return False

            # Update interaction statistics
            session.update_interaction()

            # Process therapeutic interventions if present
            if "therapeutic_intervention" in interaction_data:
                session.add_therapeutic_intervention(
                    interaction_data["therapeutic_intervention"]
                )

            # Record emotional state if present
            if "emotional_state" in interaction_data:
                session.record_emotional_state(interaction_data["emotional_state"])

            # Update session variables
            if "session_variables" in interaction_data:
                session.session_variables.update(interaction_data["session_variables"])

            # Update current scene if present
            if "current_scene_id" in interaction_data:
                session.current_scene_id = interaction_data["current_scene_id"]

            # Persist changes
            return await self.session_repository.update_session(session)

        except Exception as e:
            logger.error(
                f"Failed to update session interaction for player {player_id}: {e}"
            )
            return False

    async def add_progress_marker(self, player_id: str, marker: ProgressMarker) -> bool:
        """
        Add a progress marker to the active session.

        Args:
            player_id: ID of the player
            marker: Progress marker to add

        Returns:
            True if marker was added successfully
        """
        try:
            session = await self.get_active_session(player_id)
            if not session:
                logger.warning(f"No active session found for player {player_id}")
                return False

            session.add_progress_marker(marker)
            return await self.session_repository.update_session(session)

        except Exception as e:
            logger.error(f"Failed to add progress marker for player {player_id}: {e}")
            return False

    async def update_therapeutic_settings(
        self, player_id: str, new_settings: TherapeuticSettings
    ) -> bool:
        """
        Update therapeutic settings for the active session.

        Args:
            player_id: ID of the player
            new_settings: New therapeutic settings

        Returns:
            True if settings were updated successfully
        """
        try:
            session = await self.get_active_session(player_id)
            if not session:
                logger.warning(f"No active session found for player {player_id}")
                return False

            session.therapeutic_settings = new_settings

            # Update Interactive Narrative Engine with new settings
            if self.interactive_narrative_engine:
                await self._update_narrative_therapeutic_settings(session, new_settings)

            return await self.session_repository.update_session(session)

        except Exception as e:
            logger.error(
                f"Failed to update therapeutic settings for player {player_id}: {e}"
            )
            return False

    async def get_session_continuity_data(self, session_id: str) -> dict[str, Any]:
        """
        Get data needed for session continuity across context switches.

        Args:
            session_id: ID of the session

        Returns:
            Dictionary containing continuity data
        """
        try:
            session = await self.session_repository.get_session(session_id)
            if not session:
                return {}

            return {
                "therapeutic_settings": session.therapeutic_settings,
                "progress_markers": session.progress_markers,
                "session_variables": session.session_variables,
                "therapeutic_interventions_used": session.therapeutic_interventions_used,
                "emotional_state_history": session.emotional_state_history[
                    -5:
                ],  # Last 5 states
                "interaction_count": session.interaction_count,
                "total_duration_minutes": session.total_duration_minutes,
            }

        except Exception as e:
            logger.error(f"Failed to get continuity data for session {session_id}: {e}")
            return {}

    async def _find_existing_session(
        self, player_id: str, character_id: str, world_id: str
    ) -> SessionContext | None:
        """Find existing paused session for character-world combination."""
        active_sessions = await self.session_repository.get_player_active_sessions(
            player_id
        )

        for session in active_sessions:
            if (
                session.character_id == character_id
                and session.world_id == world_id
                and session.status == SessionStatus.PAUSED
            ):
                return session

        return None

    async def _initialize_narrative_context(self, session: SessionContext) -> None:
        """Initialize narrative context with Interactive Narrative Engine."""
        if not self.interactive_narrative_engine:
            return

        try:
            # Initialize narrative engine with session context
            await self.interactive_narrative_engine.initialize_session(
                session_id=session.session_id,
                character_id=session.character_id,
                world_id=session.world_id,
                therapeutic_settings=session.therapeutic_settings,
            )
            logger.debug(
                f"Initialized narrative context for session {session.session_id}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize narrative context: {e}")

    async def _preserve_narrative_state(self, session: SessionContext) -> None:
        """Preserve narrative state when pausing session."""
        if not self.interactive_narrative_engine:
            return

        try:
            # Get current narrative state
            narrative_state = await self.interactive_narrative_engine.get_session_state(
                session.session_id
            )

            # Store in session variables
            session.session_variables["narrative_state"] = narrative_state
            logger.debug(f"Preserved narrative state for session {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to preserve narrative state: {e}")

    async def _restore_narrative_state(self, session: SessionContext) -> None:
        """Restore narrative state when resuming session."""
        if not self.interactive_narrative_engine:
            return

        try:
            # Get preserved narrative state
            narrative_state = session.session_variables.get("narrative_state")
            if narrative_state:
                # Restore state in narrative engine
                await self.interactive_narrative_engine.restore_session_state(
                    session.session_id, narrative_state
                )
                logger.debug(
                    f"Restored narrative state for session {session.session_id}"
                )

        except Exception as e:
            logger.error(f"Failed to restore narrative state: {e}")

    async def _finalize_narrative_session(self, session: SessionContext) -> None:
        """Finalize narrative session when ending."""
        if not self.interactive_narrative_engine:
            return

        try:
            # Finalize session with narrative engine
            await self.interactive_narrative_engine.finalize_session(session.session_id)
            logger.debug(f"Finalized narrative session {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to finalize narrative session: {e}")

    async def _update_narrative_therapeutic_settings(
        self, session: SessionContext, settings: TherapeuticSettings
    ) -> None:
        """Update therapeutic settings in narrative engine."""
        if not self.interactive_narrative_engine:
            return

        try:
            # Update settings in narrative engine
            await self.interactive_narrative_engine.update_therapeutic_settings(
                session.session_id, settings
            )
            logger.debug(
                f"Updated narrative therapeutic settings for session {session.session_id}"
            )

        except Exception as e:
            logger.error(f"Failed to update narrative therapeutic settings: {e}")
