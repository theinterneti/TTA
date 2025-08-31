"""
Narrative Engine Core

This module provides the main narrative engine that orchestrates all narrative
components for therapeutic text adventures.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.gameplay_loop.database.neo4j_manager import Neo4jGameplayManager
from src.components.gameplay_loop.models.core import (
    GameplaySession,
)
from src.components.gameplay_loop.services.redis_manager import RedisSessionManager
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateType,
)

from .events import EventBus, EventType, NarrativeEvent

logger = logging.getLogger(__name__)


class NarrativeMode(str, Enum):
    """Narrative engine operating modes."""

    GUIDED = "guided"  # Structured, therapeutically focused
    EXPLORATORY = "exploratory"  # Open-ended, user-driven
    CRISIS = "crisis"  # Safety-focused with immediate support
    REFLECTION = "reflection"  # Processing and integration focused
    ADAPTIVE = "adaptive"  # AI-driven adaptation based on progress


class EngineState(str, Enum):
    """Narrative engine states."""

    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class NarrativeEngineConfig:
    """Configuration for the narrative engine."""

    # Core settings
    mode: NarrativeMode = NarrativeMode.GUIDED
    max_concurrent_sessions: int = 100
    session_timeout: timedelta = timedelta(hours=2)

    # Safety settings
    enable_safety_monitoring: bool = True
    crisis_intervention_threshold: float = 0.8
    safety_check_interval: timedelta = timedelta(minutes=5)

    # Therapeutic settings
    enable_progress_tracking: bool = True
    adaptation_sensitivity: float = 0.7
    therapeutic_alignment_threshold: float = 0.6

    # Performance settings
    cache_scenes: bool = True
    preload_choices: bool = True
    max_scene_history: int = 50

    # Event settings
    enable_event_logging: bool = True
    event_history_size: int = 1000

    # Integration settings
    redis_session_ttl: timedelta = timedelta(hours=24)
    neo4j_query_timeout: int = 30


class NarrativeEngine:
    """Main narrative engine orchestrator."""

    def __init__(
        self,
        config: NarrativeEngineConfig,
        session_manager: RedisSessionManager,
        database_manager: Neo4jGameplayManager,
        event_bus: EventBus = None,
    ):
        self.config = config
        self.session_manager = session_manager
        self.database_manager = database_manager
        self.event_bus = event_bus or event_bus

        # Engine state
        self.state = EngineState.INITIALIZING
        self.active_sessions: dict[str, SessionState] = {}
        self.session_locks: dict[str, asyncio.Lock] = {}

        # Component managers (will be initialized)
        self.scene_manager = None
        self.choice_processor = None
        self.flow_controller = None
        self.therapeutic_integrator = None

        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None

        # Metrics
        self.metrics = {
            "sessions_started": 0,
            "sessions_completed": 0,
            "scenes_processed": 0,
            "choices_made": 0,
            "safety_interventions": 0,
            "therapeutic_moments": 0,
        }

    async def initialize(self) -> bool:
        """Initialize the narrative engine."""
        try:
            logger.info("Initializing narrative engine...")

            # Initialize component managers
            from .choice_processor import ChoiceProcessor
            from .flow_controller import FlowController
            from .scene_manager import SceneManager
            from .therapeutic_integrator import TherapeuticIntegrator

            self.scene_manager = SceneManager(self)
            self.choice_processor = ChoiceProcessor(self)
            self.flow_controller = FlowController(self)
            self.therapeutic_integrator = TherapeuticIntegrator(self)

            # Initialize components
            await self.scene_manager.initialize()
            await self.choice_processor.initialize()
            await self.flow_controller.initialize()
            await self.therapeutic_integrator.initialize()

            # Start background tasks
            if self.config.enable_safety_monitoring:
                self._monitoring_task = asyncio.create_task(
                    self._safety_monitoring_loop()
                )

            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            # Subscribe to events
            self._setup_event_handlers()

            self.state = EngineState.READY
            logger.info("Narrative engine initialized successfully")

            # Publish initialization event
            await self.event_bus.publish(
                NarrativeEvent(
                    event_type=EventType.NARRATIVE_STARTED,
                    data={
                        "engine_state": self.state.value,
                        "config": self.config.__dict__,
                    },
                )
            )

            return True

        except Exception as e:
            logger.error(f"Failed to initialize narrative engine: {e}")
            self.state = EngineState.ERROR
            return False

    async def shutdown(self) -> None:
        """Shutdown the narrative engine."""
        logger.info("Shutting down narrative engine...")

        self.state = EngineState.SHUTDOWN

        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Wait for tasks to complete
        tasks = [t for t in [self._monitoring_task, self._cleanup_task] if t]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Save all active sessions
        for session_id, session_state in self.active_sessions.items():
            try:
                await self.session_manager.update_session(session_state)
            except Exception as e:
                logger.error(f"Failed to save session {session_id}: {e}")

        logger.info("Narrative engine shutdown complete")

    async def start_session(self, session: GameplaySession) -> bool:
        """Start a new narrative session."""
        try:
            # Check capacity
            if len(self.active_sessions) >= self.config.max_concurrent_sessions:
                logger.warning("Maximum concurrent sessions reached")
                return False

            # Create session state
            session_state = SessionState(
                session_id=session.session_id,
                user_id=session.user_id,
                state_type=SessionStateType.INITIALIZING,
                therapeutic_goals=session.therapeutic_goals,
                safety_level=session.safety_level,
            )

            # Initialize session in Redis
            success = await self.session_manager.create_session(
                session_state, ttl=self.config.redis_session_ttl
            )

            if not success:
                logger.error(f"Failed to create session in Redis: {session.session_id}")
                return False

            # Add to active sessions
            self.active_sessions[session.session_id] = session_state
            self.session_locks[session.session_id] = asyncio.Lock()

            # Initialize therapeutic context
            await self.therapeutic_integrator.initialize_session(session_state)

            # Transition to active state
            await self._transition_session_state(
                session.session_id, SessionStateType.ACTIVE, "Session started"
            )

            # Start with initial scene
            initial_scene = await self.flow_controller.get_initial_scene(session_state)
            if initial_scene:
                await self.enter_scene(session.session_id, initial_scene.scene_id)

            self.metrics["sessions_started"] += 1

            logger.info(f"Started narrative session: {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start session {session.session_id}: {e}")
            return False

    async def end_session(self, session_id: str, reason: str = "completed") -> bool:
        """End a narrative session."""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session not found: {session_id}")
                return False

            session_state = self.active_sessions[session_id]

            # Transition to completed state
            await self._transition_session_state(
                session_id, SessionStateType.COMPLETED, reason
            )

            # Finalize therapeutic progress
            await self.therapeutic_integrator.finalize_session(session_state)

            # Save final state
            await self.session_manager.update_session(session_state)

            # Remove from active sessions
            del self.active_sessions[session_id]
            del self.session_locks[session_id]

            self.metrics["sessions_completed"] += 1

            logger.info(f"Ended narrative session: {session_id} ({reason})")
            return True

        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False

    async def enter_scene(self, session_id: str, scene_id: str) -> bool:
        """Enter a new scene in the narrative."""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Session not found: {session_id}")
                return False

            async with self.session_locks[session_id]:
                session_state = self.active_sessions[session_id]

                # Validate scene transition
                if not await self.flow_controller.can_enter_scene(
                    session_state, scene_id
                ):
                    logger.warning(
                        f"Cannot enter scene {scene_id} for session {session_id}"
                    )
                    return False

                # Load scene
                scene = await self.scene_manager.load_scene(scene_id)
                if not scene:
                    logger.error(f"Scene not found: {scene_id}")
                    return False

                # Safety check
                if not await self.therapeutic_integrator.validate_scene_safety(
                    session_state, scene
                ):
                    logger.warning(f"Scene {scene_id} failed safety validation")
                    return False

                # Monitor emotional safety for scene content
                scene_interaction_data = {
                    "content": scene.description,
                    "scene_id": scene_id,
                    "scene_type": (
                        scene.scene_type.value
                        if hasattr(scene, "scene_type")
                        else "narrative"
                    ),
                    "interaction_type": "scene_entry",
                }
                await self.therapeutic_integrator.monitor_emotional_safety(
                    session_state, scene_interaction_data
                )

                # Enter scene
                success = await self.scene_manager.enter_scene(session_state, scene)
                if success:
                    session_state.add_scene(scene_id)
                    await self.session_manager.update_session(session_state)
                    self.metrics["scenes_processed"] += 1

                return success

        except Exception as e:
            logger.error(
                f"Failed to enter scene {scene_id} for session {session_id}: {e}"
            )
            return False

    async def process_choice(self, session_id: str, choice_id: str) -> bool:
        """Process a user choice."""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Session not found: {session_id}")
                return False

            async with self.session_locks[session_id]:
                session_state = self.active_sessions[session_id]

                # Load choice for emotional safety monitoring
                choice = await self.choice_processor.load_choice(choice_id)
                if choice:
                    # Monitor emotional safety for choice content
                    choice_interaction_data = {
                        "content": choice.text,
                        "choice_id": choice_id,
                        "choice_type": choice.choice_type.value,
                        "therapeutic_relevance": choice.therapeutic_relevance,
                        "emotional_weight": choice.emotional_weight,
                        "interaction_type": "choice_made",
                        "recent_choice": choice.text,
                    }
                    await self.therapeutic_integrator.monitor_emotional_safety(
                        session_state, choice_interaction_data
                    )

                # Process choice
                success = await self.choice_processor.process_choice(
                    session_state, choice_id
                )

                if success:
                    session_state.add_choice(choice_id)
                    await self.session_manager.update_session(session_state)
                    self.metrics["choices_made"] += 1

                return success

        except Exception as e:
            logger.error(
                f"Failed to process choice {choice_id} for session {session_id}: {e}"
            )
            return False

    async def get_session_state(self, session_id: str) -> SessionState | None:
        """Get current session state."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try to load from Redis
        return await self.session_manager.get_session(session_id)

    async def pause_session(self, session_id: str) -> bool:
        """Pause a narrative session."""
        return await self._transition_session_state(
            session_id, SessionStateType.PAUSED, "User requested pause"
        )

    async def resume_session(self, session_id: str) -> bool:
        """Resume a paused narrative session."""
        return await self._transition_session_state(
            session_id, SessionStateType.ACTIVE, "User requested resume"
        )

    async def _transition_session_state(
        self, session_id: str, new_state: SessionStateType, reason: str
    ) -> bool:
        """Transition session to new state."""
        try:
            if session_id not in self.active_sessions:
                return False

            session_state = self.active_sessions[session_id]
            old_state = session_state.state_type

            # Record state change
            session_state.record_state_change(old_state, new_state, reason)
            session_state.state_type = new_state

            # Update in Redis
            await self.session_manager.update_session(session_state)

            logger.debug(
                f"Session {session_id} transitioned from {old_state} to {new_state}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to transition session {session_id} state: {e}")
            return False

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for the engine."""
        # Safety event handlers
        self.event_bus.subscribe(
            EventType.SAFETY_CONCERN_DETECTED, self._handle_safety_concern
        )
        self.event_bus.subscribe(
            EventType.CRISIS_INTERVENTION_NEEDED, self._handle_crisis
        )

        # Progress event handlers
        self.event_bus.subscribe(EventType.MILESTONE_ACHIEVED, self._handle_milestone)
        self.event_bus.subscribe(
            EventType.THERAPEUTIC_MOMENT, self._handle_therapeutic_moment
        )

    async def _handle_safety_concern(self, event: NarrativeEvent) -> None:
        """Handle safety concern events."""
        session_id = event.session_id
        if session_id in self.active_sessions:
            # Pause session for safety review
            await self.pause_session(session_id)
            self.metrics["safety_interventions"] += 1

    async def _handle_crisis(self, event: NarrativeEvent) -> None:
        """Handle crisis intervention events."""
        session_id = event.session_id
        if session_id in self.active_sessions:
            # Switch to crisis mode
            session_state = self.active_sessions[session_id]
            session_state.safety_level = "crisis"
            await self.session_manager.update_session(session_state)

    async def _handle_milestone(self, event: NarrativeEvent) -> None:
        """Handle milestone achievement events."""
        # Log milestone achievement
        logger.info(f"Milestone achieved in session {event.session_id}: {event.data}")

    async def _handle_therapeutic_moment(self, event: NarrativeEvent) -> None:
        """Handle therapeutic moment events."""
        self.metrics["therapeutic_moments"] += 1

    async def _safety_monitoring_loop(self) -> None:
        """Background safety monitoring loop."""
        while self.state not in [EngineState.SHUTDOWN, EngineState.ERROR]:
            try:
                for session_id, session_state in self.active_sessions.items():
                    await self.therapeutic_integrator.monitor_session_safety(
                        session_state
                    )

                await asyncio.sleep(self.config.safety_check_interval.total_seconds())

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in safety monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self.state not in [EngineState.SHUTDOWN, EngineState.ERROR]:
            try:
                # Clean up expired sessions
                expired_sessions = []
                for session_id, session_state in self.active_sessions.items():
                    if session_state.is_expired():
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    await self.end_session(session_id, "expired")

                await asyncio.sleep(300)  # Run every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)

    def get_metrics(self) -> dict[str, Any]:
        """Get engine metrics."""
        return {
            **self.metrics,
            "active_sessions": len(self.active_sessions),
            "engine_state": self.state.value,
            "uptime": datetime.utcnow()
            - getattr(self, "_start_time", datetime.utcnow()),
        }
