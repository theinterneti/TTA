"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Controller]]

# Logseq: [[TTA/Components/Gameplay_loop/Controller]]
Gameplay Loop Controller for Therapeutic Text Adventure

This module implements the main gameplay loop controller that orchestrates
all gameplay components including narrative engine, choice architecture,
consequence system, and session lifecycle management.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.ai_components.llm_factory import get_llm

from .choice_architecture.manager import ChoiceArchitectureManager
from .consequence_system.system import ConsequenceSystem
from .database.neo4j_manager import Neo4jGameplayManager
from .models.core import Choice, ConsequenceSet, EmotionalState, Scene, SessionState
from .models.interactions import GameplaySession, UserChoice
from .narrative.engine import NarrativeEngine

logger = logging.getLogger(__name__)


class GameplayLoopController:
    """
    Main controller that orchestrates the complete gameplay loop including
    session lifecycle management, narrative progression, choice processing,
    and consequence generation.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Initialize core components
        db_config = config.get("database", {})
        self.database_manager = Neo4jGameplayManager(
            neo4j_uri=db_config.get("neo4j_uri", "bolt://localhost:7688"),
            neo4j_user=db_config.get("neo4j_user", "neo4j"),
            neo4j_password=db_config.get("neo4j_password", "password"),
            redis_url=db_config.get("redis_url", "redis://localhost:6379"),
        )
        # Build LLM — gracefully skip if no provider is configured
        try:
            _llm = get_llm()
        except Exception as _exc:
            logger.warning(
                "No LLM configured; narrative engine will use templates: %s", _exc
            )
            _llm = None

        self.narrative_engine = NarrativeEngine(
            self.database_manager, config.get("narrative", {}), llm=_llm
        )
        self.choice_architecture = ChoiceArchitectureManager(
            config.get("choice_architecture", {})
        )
        self.consequence_system = ConsequenceSystem(
            config.get("consequence_system", {})
        )

        # Session management
        self.active_sessions: dict[str, GameplaySession] = {}
        self.session_timeout = self.config.get(
            "session_timeout", 3600
        )  # 1 hour default

        # Performance tracking
        self.response_time_target = self.config.get(
            "response_time_target", 2.0
        )  # 2 seconds

        logger.info("GameplayLoopController initialized")

    async def initialize(self) -> bool:
        """Initialize the gameplay loop controller and all components."""
        try:
            # Initialize all components
            await self.database_manager.initialize()
            await self.narrative_engine.initialize()
            await self.choice_architecture.initialize()
            await self.consequence_system.initialize()

            logger.info("GameplayLoopController initialization completed")
            return True

        except Exception as e:
            logger.error(f"GameplayLoopController initialization failed: {e}")
            return False

    # Session Lifecycle Management
    async def start_session(
        self, user_id: str, therapeutic_context: dict[str, Any] | None = None
    ) -> GameplaySession:
        """
        Start a new gameplay session for a user.

        Args:
            user_id: User identifier
            therapeutic_context: Optional therapeutic context and goals

        Returns:
            GameplaySession object with initial state
        """
        try:
            logger.info(f"Starting new session for user {user_id}")

            # Create session state
            session_state = SessionState(
                user_id=user_id,
                therapeutic_context=therapeutic_context or {},
                emotional_state=EmotionalState.CALM,
            )

            # Generate opening scene
            opening_scene = await self.narrative_engine.generate_opening_scene(
                session_state
            )
            if opening_scene:
                session_state.current_scene = opening_scene

            # Generate initial choices
            initial_choices = (
                await self.choice_architecture.generate_choices_for_scene(
                    opening_scene, session_state
                )
                if opening_scene
                else []
            )

            # Create gameplay session
            gameplay_session = GameplaySession(
                session_id=session_state.session_id,
                user_id=user_id,
                session_state=session_state,
                current_scene=opening_scene,
                available_choices=initial_choices,
                session_start_time=datetime.utcnow(),
                is_active=True,
            )

            # Store session
            self.active_sessions[session_state.session_id] = gameplay_session
            await self.database_manager.create_session(session_state)

            logger.info(f"Session {session_state.session_id} started successfully")
            return gameplay_session

        except Exception as e:
            logger.error(f"Failed to start session for user {user_id}: {e}")
            raise

    async def resume_session(self, session_id: str) -> GameplaySession | None:
        """
        Resume an existing session with a recap of previous progress.

        Args:
            session_id: Session identifier to resume

        Returns:
            GameplaySession object or None if session not found
        """
        try:
            logger.info(f"Resuming session {session_id}")

            # Check if session is already active
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.last_activity_time = datetime.utcnow()
                return session

            # Load session from database
            session_state = await self.database_manager.load_session_state(session_id)
            if not session_state:
                logger.warning(f"Session {session_id} not found")
                return None

            # Generate session recap
            recap = await self._generate_session_recap(session_state)

            # Update current scene if needed
            current_scene = session_state.current_scene
            if not current_scene:
                current_scene = await self.narrative_engine.generate_next_scene(
                    session_state
                )
                session_state.current_scene = current_scene

            # Generate current choices
            available_choices = (
                await self.choice_architecture.generate_choices_for_scene(
                    current_scene, session_state
                )
                if current_scene
                else []
            )

            # Create gameplay session
            gameplay_session = GameplaySession(
                session_id=session_id,
                user_id=session_state.user_id,
                session_state=session_state,
                current_scene=current_scene,
                available_choices=available_choices,
                session_start_time=datetime.utcnow(),  # Resume time
                is_active=True,
                session_recap=recap,
            )

            # Store active session
            self.active_sessions[session_id] = gameplay_session

            logger.info(f"Session {session_id} resumed successfully")
            return gameplay_session

        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return None

    async def pause_session(self, session_id: str) -> bool:
        """
        Pause a session and save current progress.

        Args:
            session_id: Session identifier to pause

        Returns:
            True if successfully paused
        """
        try:
            logger.info(f"Pausing session {session_id}")

            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not active")
                return False

            session = self.active_sessions[session_id]
            session.is_active = False
            session.last_activity_time = datetime.utcnow()

            # Save session state to database
            await self.database_manager.save_session_state(session.session_state)

            # Remove from active sessions
            del self.active_sessions[session_id]

            logger.info(f"Session {session_id} paused successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            return False

    async def end_session(self, session_id: str) -> bool:
        """
        End a session and perform cleanup.

        Args:
            session_id: Session identifier to end

        Returns:
            True if successfully ended
        """
        try:
            logger.info(f"Ending session {session_id}")

            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.is_active = False
                session.session_end_time = datetime.utcnow()

                # Save final session state
                await self.database_manager.save_session_state(session.session_state)

                # Generate session summary
                session_summary = await self._generate_session_summary(session)

                # Store session summary
                await self.database_manager.save_session_summary(
                    session_id, session_summary
                )

                # Remove from active sessions
                del self.active_sessions[session_id]

            logger.info(f"Session {session_id} ended successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False

    # Core Gameplay Loop
    async def process_user_choice(
        self, session_id: str, choice_id: str
    ) -> tuple[Scene | None, list[Choice], ConsequenceSet | None]:
        """
        Process a user's choice and advance the gameplay loop.

        Args:
            session_id: Session identifier
            choice_id: ID of the choice made by the user

        Returns:
            Tuple of (next_scene, new_choices, consequences)
        """
        try:
            start_time = datetime.utcnow()
            logger.info(f"Processing choice {choice_id} for session {session_id}")

            # Get active session
            if session_id not in self.active_sessions:
                logger.error(f"Session {session_id} not active")
                return None, [], None

            session = self.active_sessions[session_id]
            session_state = session.session_state

            # Find the selected choice
            selected_choice = None
            for choice in session.available_choices:
                if choice.choice_id == choice_id:
                    selected_choice = choice
                    break

            if not selected_choice:
                logger.error(f"Choice {choice_id} not found in available choices")
                return None, [], None

            # Create user choice object
            user_choice = UserChoice(
                choice_id=choice_id,
                choice_text=selected_choice.choice_text,
                choice_type=selected_choice.choice_type,
                therapeutic_tags=selected_choice.therapeutic_tags,
                therapeutic_value=selected_choice.therapeutic_value,
                agency_level=selected_choice.agency_level,
                timestamp=datetime.utcnow(),
            )

            # Generate consequences
            consequences = await self.consequence_system.generate_consequences(
                user_choice, session_state.current_scene, session_state
            )

            # Update session state with choice
            session_state.choice_history.append(
                {
                    "choice_id": choice_id,
                    "choice_text": selected_choice.choice_text,
                    "choice_type": selected_choice.choice_type.value,
                    "therapeutic_value": selected_choice.therapeutic_value,
                    "therapeutic_tags": selected_choice.therapeutic_tags,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Update emotional state based on consequences
            if consequences.emotional_impact:
                new_emotion = consequences.emotional_impact.get(
                    "primary_emotion", "neutral"
                )
                if new_emotion in [state.value for state in EmotionalState]:
                    session_state.emotional_state = EmotionalState(new_emotion)

            # Generate next scene
            next_scene = await self.narrative_engine.generate_next_scene(session_state)
            session_state.current_scene = next_scene

            # Generate new choices for next scene
            new_choices = (
                await self.choice_architecture.generate_choices_for_scene(
                    next_scene, session_state
                )
                if next_scene
                else []
            )

            # Update session
            session.current_scene = next_scene
            session.available_choices = new_choices
            session.last_activity_time = datetime.utcnow()

            # Save updated session state
            await self.database_manager.save_session_state(session_state)

            # Check response time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            if processing_time > self.response_time_target:
                logger.warning(
                    f"Choice processing took {processing_time:.2f}s (target: {self.response_time_target}s)"
                )

            logger.info(f"Choice processed successfully in {processing_time:.2f}s")
            return next_scene, new_choices, consequences

        except Exception as e:
            logger.error(
                f"Failed to process choice {choice_id} for session {session_id}: {e}"
            )
            return None, [], None

    # Helper Methods
    async def _generate_session_recap(self, session_state: SessionState) -> str:
        """Generate a recap of the session for resuming."""
        try:
            choice_count = len(session_state.choice_history)

            if choice_count == 0:
                return "Welcome back! You're just beginning your therapeutic journey."

            # Get recent therapeutic progress
            recent_choices = (
                session_state.choice_history[-3:]
                if choice_count >= 3
                else session_state.choice_history
            )
            therapeutic_themes = []

            for choice in recent_choices:
                therapeutic_themes.extend(choice.get("therapeutic_tags", []))

            # Create recap based on progress
            if therapeutic_themes:
                main_themes = list(set(therapeutic_themes))[:2]  # Top 2 themes
                recap = f"Welcome back! In your recent journey, you've been exploring {', '.join(main_themes)}. "
            else:
                recap = "Welcome back to your therapeutic adventure! "

            # Add current scene context
            if session_state.current_scene:
                recap += f"You find yourself {session_state.current_scene.description[:100]}..."

            recap += " Your journey of growth and self-discovery continues."

            return recap

        except Exception as e:
            logger.error(f"Failed to generate session recap: {e}")
            return "Welcome back! Your therapeutic journey continues."

    async def _generate_session_summary(
        self, session: GameplaySession
    ) -> dict[str, Any]:
        """Generate a summary of the completed session."""
        try:
            session_state = session.session_state
            choice_history = session_state.choice_history

            summary = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "duration_minutes": 0,
                "total_choices": len(choice_history),
                "therapeutic_engagement": 0.0,
                "skills_practiced": [],
                "emotional_journey": [],
                "key_insights": [],
                "progress_markers": [],
            }

            # Calculate session duration
            if session.session_start_time and session.session_end_time:
                duration = session.session_end_time - session.session_start_time
                summary["duration_minutes"] = duration.total_seconds() / 60

            # Analyze therapeutic engagement
            if choice_history:
                therapeutic_values = [
                    choice.get("therapeutic_value", 0) for choice in choice_history
                ]
                summary["therapeutic_engagement"] = sum(therapeutic_values) / len(
                    therapeutic_values
                )

                # Collect skills practiced
                all_tags = []
                for choice in choice_history:
                    all_tags.extend(choice.get("therapeutic_tags", []))

                summary["skills_practiced"] = list(set(all_tags))

            # Track emotional journey
            summary["emotional_journey"] = [session_state.emotional_state.value]

            # Generate key insights
            if summary["therapeutic_engagement"] > 0.7:
                summary["key_insights"].append(
                    "Demonstrated strong therapeutic engagement"
                )

            if len(summary["skills_practiced"]) >= 3:
                summary["key_insights"].append(
                    "Explored multiple therapeutic approaches"
                )

            if summary["total_choices"] >= 10:
                summary["key_insights"].append(
                    "Sustained participation in therapeutic process"
                )

            return summary

        except Exception as e:
            logger.error(f"Failed to generate session summary: {e}")
            return {
                "session_id": session.session_id,
                "error": "Summary generation failed",
            }

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get current status of a session."""
        try:
            if session_id not in self.active_sessions:
                return None

            session = self.active_sessions[session_id]
            session_state = session.session_state

            status = {
                "session_id": session_id,
                "user_id": session.user_id,
                "is_active": session.is_active,
                "current_scene_id": (
                    session_state.current_scene.scene_id
                    if session_state.current_scene
                    else None
                ),
                "emotional_state": session_state.emotional_state.value,
                "total_choices": len(session_state.choice_history),
                "available_choices_count": len(session.available_choices),
                "therapeutic_engagement": 0.0,
                "last_activity": (
                    session.last_activity_time.isoformat()
                    if session.last_activity_time
                    else None
                ),
            }

            # Calculate therapeutic engagement
            if session_state.choice_history:
                therapeutic_values = [
                    choice.get("therapeutic_value", 0)
                    for choice in session_state.choice_history
                ]
                status["therapeutic_engagement"] = sum(therapeutic_values) / len(
                    therapeutic_values
                )

            return status

        except Exception as e:
            logger.error(f"Failed to get session status for {session_id}: {e}")
            return None

    async def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions that have exceeded timeout."""
        try:
            current_time = datetime.utcnow()
            sessions_to_remove = []

            for session_id, session in self.active_sessions.items():
                if session.last_activity_time:
                    inactive_duration = (
                        current_time - session.last_activity_time
                    ).total_seconds()
                    if inactive_duration > self.session_timeout:
                        sessions_to_remove.append(session_id)

            # Clean up expired sessions
            for session_id in sessions_to_remove:
                await self.pause_session(session_id)

            logger.info(f"Cleaned up {len(sessions_to_remove)} inactive sessions")
            return len(sessions_to_remove)

        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
            return 0
