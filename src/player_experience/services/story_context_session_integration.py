"""
Story Context Session Integration Service

This service integrates story initialization with the existing Redis-based session management
system to maintain narrative context and therapeutic progress across gameplay sessions.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

from src.components.gameplay_loop.services.personalization_service_manager import (
    PersonalizationServiceManager,
)
from src.components.gameplay_loop.services.session_integration_manager import (
    SessionIntegrationManager,
)

from .story_initialization_service import (
    StoryInitializationService,
)

logger = logging.getLogger(__name__)


@dataclass
class StorySessionContext:
    """Context for story session integration."""

    session_id: str
    player_id: str
    character_id: str
    world_id: str
    story_context: dict[str, Any]
    narrative_state: dict[str, Any]
    therapeutic_progress: dict[str, Any]
    session_metadata: dict[str, Any]
    created_at: datetime
    last_updated: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StorySessionContext":
        """Create from dictionary loaded from Redis."""
        # Convert ISO strings back to datetime objects
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class StoryContextSessionIntegration:
    """
    Service for integrating story context with Redis-based session management.

    Provides seamless integration between story initialization and session persistence,
    ensuring narrative context and therapeutic progress are maintained across sessions.
    """

    def __init__(
        self,
        session_manager: SessionIntegrationManager | None = None,
        personalization_manager: PersonalizationServiceManager | None = None,
        story_service: StoryInitializationService | None = None,
    ):
        """
        Initialize the Story Context Session Integration service.

        Args:
            session_manager: Session integration manager for Redis operations
            personalization_manager: Personalization service manager
            story_service: Story initialization service
        """
        self.session_manager = session_manager or SessionIntegrationManager()
        self.personalization_manager = (
            personalization_manager or PersonalizationServiceManager()
        )
        self.story_service = story_service or StoryInitializationService()

        # Redis key patterns
        self.story_context_key_pattern = "story_context:{session_id}"
        self.narrative_state_key_pattern = "narrative_state:{session_id}"
        self.therapeutic_progress_key_pattern = "therapeutic_progress:{session_id}"
        self.player_sessions_key_pattern = "player_story_sessions:{player_id}"

        # Configuration
        self.context_expiry_hours = 72  # 3 days
        self.auto_save_interval_minutes = 5
        self.max_sessions_per_player = 10

        # Metrics
        self.metrics = {
            "story_contexts_created": 0,
            "story_contexts_loaded": 0,
            "story_contexts_updated": 0,
            "narrative_states_saved": 0,
            "therapeutic_progress_tracked": 0,
            "session_integrations": 0,
            "context_load_failures": 0,
        }

        logger.info("StoryContextSessionIntegration service initialized")

    async def initialize_story_session_context(
        self,
        session_id: str,
        player_id: str,
        character_id: str,
        world_id: str,
        therapeutic_goals: list[str],
        story_preferences: dict[str, Any] | None = None,
    ) -> StorySessionContext | None:
        """
        Initialize story session context and integrate with session management.

        Args:
            session_id: Session identifier
            player_id: Player identifier
            character_id: Character identifier
            world_id: World identifier
            therapeutic_goals: List of therapeutic goals
            story_preferences: Optional story preferences

        Returns:
            StorySessionContext if successful, None otherwise
        """
        try:
            # Initialize story using the story service
            story_session_id = await self.story_service.initialize_story_session(
                player_id=player_id,
                character_id=character_id,
                world_id=world_id,
                therapeutic_goals=therapeutic_goals,
                story_preferences=story_preferences or {},
            )

            if not story_session_id:
                logger.error("Failed to initialize story session")
                return None

            # Get story initialization result details
            story_context = await self._get_story_initialization_context(
                story_session_id, character_id, world_id, therapeutic_goals
            )

            # Create story session context
            context = StorySessionContext(
                session_id=session_id,
                player_id=player_id,
                character_id=character_id,
                world_id=world_id,
                story_context=story_context,
                narrative_state={
                    "current_scene": "opening",
                    "scene_history": [],
                    "choice_history": [],
                    "narrative_variables": {},
                    "story_progression": 0.0,
                },
                therapeutic_progress={
                    "goals": therapeutic_goals,
                    "progress_markers": {},
                    "skills_practiced": [],
                    "milestones_achieved": [],
                    "session_insights": [],
                },
                session_metadata={
                    "story_session_id": story_session_id,
                    "initialization_timestamp": datetime.utcnow().isoformat(),
                    "session_type": "story_gameplay",
                    "preferences": story_preferences or {},
                },
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
            )

            # Save to Redis
            await self._save_story_context(context)

            # Integrate with session management
            await self._integrate_with_session_management(context)

            # Update player session tracking
            await self._update_player_session_tracking(player_id, session_id)

            # Update metrics
            self.metrics["story_contexts_created"] += 1
            self.metrics["session_integrations"] += 1

            logger.info(f"Initialized story session context for session {session_id}")
            return context

        except Exception as e:
            logger.error(f"Error initializing story session context: {e}")
            return None

    async def load_story_session_context(
        self, session_id: str
    ) -> StorySessionContext | None:
        """
        Load story session context from Redis.

        Args:
            session_id: Session identifier

        Returns:
            StorySessionContext if found, None otherwise
        """
        try:
            # Load context from Redis
            context_key = self.story_context_key_pattern.format(session_id=session_id)
            context_data = await self.session_manager.get_session_data(context_key)

            if not context_data:
                logger.warning(f"No story context found for session {session_id}")
                return None

            # Parse context data
            if isinstance(context_data, str):
                context_data = json.loads(context_data)

            context = StorySessionContext.from_dict(context_data)

            # Update metrics
            self.metrics["story_contexts_loaded"] += 1

            logger.debug(f"Loaded story session context for session {session_id}")
            return context

        except Exception as e:
            logger.error(f"Error loading story session context for {session_id}: {e}")
            self.metrics["context_load_failures"] += 1
            return None

    async def update_narrative_state(
        self, session_id: str, narrative_updates: dict[str, Any]
    ) -> bool:
        """
        Update narrative state for a story session.

        Args:
            session_id: Session identifier
            narrative_updates: Updates to apply to narrative state

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current context
            context = await self.load_story_session_context(session_id)
            if not context:
                logger.error(f"No context found for session {session_id}")
                return False

            # Update narrative state
            context.narrative_state.update(narrative_updates)
            context.last_updated = datetime.utcnow()

            # Save updated context
            await self._save_story_context(context)

            # Update metrics
            self.metrics["narrative_states_saved"] += 1

            logger.debug(f"Updated narrative state for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating narrative state for {session_id}: {e}")
            return False

    async def update_therapeutic_progress(
        self, session_id: str, progress_updates: dict[str, Any]
    ) -> bool:
        """
        Update therapeutic progress for a story session.

        Args:
            session_id: Session identifier
            progress_updates: Updates to apply to therapeutic progress

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current context
            context = await self.load_story_session_context(session_id)
            if not context:
                logger.error(f"No context found for session {session_id}")
                return False

            # Update therapeutic progress
            context.therapeutic_progress.update(progress_updates)
            context.last_updated = datetime.utcnow()

            # Save updated context
            await self._save_story_context(context)

            # Update personalization service with progress
            await self._update_personalization_progress(context)

            # Update metrics
            self.metrics["therapeutic_progress_tracked"] += 1

            logger.debug(f"Updated therapeutic progress for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating therapeutic progress for {session_id}: {e}")
            return False

    async def get_session_narrative_context(
        self, session_id: str
    ) -> dict[str, Any] | None:
        """
        Get narrative context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Narrative context dictionary or None
        """
        try:
            context = await self.load_story_session_context(session_id)
            if not context:
                return None

            return {
                "story_context": context.story_context,
                "narrative_state": context.narrative_state,
                "character_id": context.character_id,
                "world_id": context.world_id,
                "therapeutic_goals": context.therapeutic_progress.get("goals", []),
                "session_metadata": context.session_metadata,
            }

        except Exception as e:
            logger.error(f"Error getting narrative context for {session_id}: {e}")
            return None

    async def get_player_story_sessions(self, player_id: str) -> list[dict[str, Any]]:
        """
        Get all story sessions for a player.

        Args:
            player_id: Player identifier

        Returns:
            List of session information dictionaries
        """
        try:
            # Get player session list from Redis
            sessions_key = self.player_sessions_key_pattern.format(player_id=player_id)
            session_ids = await self.session_manager.get_session_data(sessions_key)

            if not session_ids:
                return []

            if isinstance(session_ids, str):
                session_ids = json.loads(session_ids)

            # Load context for each session
            sessions = []
            for session_id in session_ids:
                context = await self.load_story_session_context(session_id)
                if context:
                    sessions.append(
                        {
                            "session_id": session_id,
                            "character_id": context.character_id,
                            "world_id": context.world_id,
                            "created_at": context.created_at.isoformat(),
                            "last_updated": context.last_updated.isoformat(),
                            "therapeutic_goals": context.therapeutic_progress.get(
                                "goals", []
                            ),
                            "story_progression": context.narrative_state.get(
                                "story_progression", 0.0
                            ),
                        }
                    )

            return sessions

        except Exception as e:
            logger.error(f"Error getting player story sessions for {player_id}: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired story session contexts.

        Returns:
            Number of sessions cleaned up
        """
        try:
            cleaned_count = 0
            datetime.utcnow() - timedelta(
                hours=self.context_expiry_hours
            )

            # This would need to be implemented with a Redis scan operation
            # For now, we'll implement a basic cleanup approach
            logger.info("Story session cleanup would be performed here")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    # Private helper methods

    async def _get_story_initialization_context(
        self,
        story_session_id: str,
        character_id: str,
        world_id: str,
        therapeutic_goals: list[str],
    ) -> dict[str, Any]:
        """Get story initialization context details."""
        return {
            "story_session_id": story_session_id,
            "character_id": character_id,
            "world_id": world_id,
            "therapeutic_goals": therapeutic_goals,
            "initialization_timestamp": datetime.utcnow().isoformat(),
            "story_type": "therapeutic_adventure",
            "narrative_framework": "emergent_storytelling",
        }

    async def _save_story_context(self, context: StorySessionContext) -> None:
        """Save story context to Redis."""
        try:
            context_key = self.story_context_key_pattern.format(
                session_id=context.session_id
            )
            context_data = json.dumps(context.to_dict(), default=str)

            # Save with expiry
            expiry_seconds = self.context_expiry_hours * 3600
            await self.session_manager.set_session_data(
                context_key, context_data, expiry_seconds
            )

            # Update metrics
            self.metrics["story_contexts_updated"] += 1

        except Exception as e:
            logger.error(f"Error saving story context: {e}")
            raise

    async def _integrate_with_session_management(
        self, context: StorySessionContext
    ) -> None:
        """Integrate story context with existing session management."""
        try:
            # Create session state integration
            session_data = {
                "session_type": "story_gameplay",
                "story_context_key": self.story_context_key_pattern.format(
                    session_id=context.session_id
                ),
                "character_id": context.character_id,
                "world_id": context.world_id,
                "therapeutic_goals": context.therapeutic_progress.get("goals", []),
                "narrative_state": context.narrative_state,
                "created_at": context.created_at.isoformat(),
            }

            # Save session integration data
            integration_key = f"session_integration:{context.session_id}"
            await self.session_manager.set_session_data(
                integration_key,
                json.dumps(session_data),
                self.context_expiry_hours * 3600,
            )

        except Exception as e:
            logger.error(f"Error integrating with session management: {e}")
            raise

    async def _update_player_session_tracking(
        self, player_id: str, session_id: str
    ) -> None:
        """Update player session tracking in Redis."""
        try:
            sessions_key = self.player_sessions_key_pattern.format(player_id=player_id)

            # Get existing sessions
            existing_sessions = await self.session_manager.get_session_data(
                sessions_key
            )
            if existing_sessions:
                if isinstance(existing_sessions, str):
                    session_list = json.loads(existing_sessions)
                else:
                    session_list = existing_sessions
            else:
                session_list = []

            # Add new session
            if session_id not in session_list:
                session_list.append(session_id)

            # Limit number of sessions per player
            if len(session_list) > self.max_sessions_per_player:
                session_list = session_list[-self.max_sessions_per_player :]

            # Save updated list
            await self.session_manager.set_session_data(
                sessions_key, json.dumps(session_list), self.context_expiry_hours * 3600
            )

        except Exception as e:
            logger.error(f"Error updating player session tracking: {e}")
            raise

    async def _update_personalization_progress(
        self, context: StorySessionContext
    ) -> None:
        """Update personalization service with therapeutic progress."""
        try:
            {
                "player_id": context.player_id,
                "session_id": context.session_id,
                "therapeutic_progress": context.therapeutic_progress,
                "narrative_engagement": context.narrative_state.get(
                    "story_progression", 0.0
                ),
                "last_updated": context.last_updated.isoformat(),
            }

            # This would integrate with the personalization service
            # For now, we'll log the integration point
            logger.debug(
                f"Would update personalization service with progress for {context.player_id}"
            )

        except Exception as e:
            logger.error(f"Error updating personalization progress: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the story context session integration."""
        return {
            **self.metrics,
            "context_expiry_hours": self.context_expiry_hours,
            "max_sessions_per_player": self.max_sessions_per_player,
        }
