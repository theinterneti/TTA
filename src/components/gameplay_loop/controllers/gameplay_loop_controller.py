"""
Gameplay Loop Controller for Session Management

This module provides comprehensive session lifecycle management, progress saving/restoration,
session pacing, and integration with all therapeutic systems for production-ready
therapeutic session orchestration.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.narrative.choice_processor import ChoiceProcessor
from src.components.gameplay_loop.narrative.engine import NarrativeEngine
from src.components.gameplay_loop.narrative.events import (
    EventBus,
    EventType,
    NarrativeEvent,
)
from src.components.gameplay_loop.services.redis_manager import (
    RedisSessionManager,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateType,
)

logger = logging.getLogger(__name__)


class SessionPhase(str, Enum):
    """Phases of a therapeutic session."""

    INITIALIZATION = "initialization"
    WARM_UP = "warm_up"
    ACTIVE_ENGAGEMENT = "active_engagement"
    SKILL_PRACTICE = "skill_practice"
    EMOTIONAL_PROCESSING = "emotional_processing"
    REFLECTION = "reflection"
    INTEGRATION = "integration"
    CONCLUSION = "conclusion"
    WRAP_UP = "wrap_up"


class BreakPointType(str, Enum):
    """Types of natural break points in sessions."""

    SCENE_TRANSITION = "scene_transition"
    SKILL_COMPLETION = "skill_completion"
    EMOTIONAL_PROCESSING = "emotional_processing"
    REFLECTION_MOMENT = "reflection_moment"
    MILESTONE_ACHIEVEMENT = "milestone_achievement"
    TIME_BASED = "time_based"
    USER_REQUESTED = "user_requested"
    THERAPEUTIC_CHECKPOINT = "therapeutic_checkpoint"


class SessionPacing(str, Enum):
    """Session pacing preferences."""

    RELAXED = "relaxed"  # 45-60 minutes
    STANDARD = "standard"  # 30-45 minutes
    FOCUSED = "focused"  # 20-30 minutes
    BRIEF = "brief"  # 10-20 minutes
    MICRO = "micro"  # 5-10 minutes


@dataclass
class SessionConfiguration:
    """Configuration for session management."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""

    # Session timing
    target_duration_minutes: int = 30
    max_duration_minutes: int = 60
    break_reminder_interval_minutes: int = 15

    # Session pacing
    pacing: SessionPacing = SessionPacing.STANDARD
    allow_extended_sessions: bool = True
    auto_save_interval_minutes: int = 5

    # Therapeutic settings
    therapeutic_goals: list[str] = field(default_factory=list)
    session_focus: str | None = None
    difficulty_preference: str | None = None

    # User preferences
    break_point_notifications: bool = True
    time_reminders: bool = True
    progress_summaries: bool = True

    # Recovery settings
    auto_recovery_enabled: bool = True
    recovery_timeout_minutes: int = 30

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SessionBreakPoint:
    """Represents a natural break point in a session."""

    break_point_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""

    # Break point details
    break_type: BreakPointType = BreakPointType.SCENE_TRANSITION
    detected_at: datetime = field(default_factory=datetime.utcnow)

    # Context
    current_scene_id: str | None = None
    narrative_context: str = ""
    therapeutic_context: str = ""

    # Timing
    session_duration_minutes: float = 0.0
    time_since_last_break_minutes: float = 0.0

    # User state
    engagement_level: float = 0.5  # 0.0-1.0
    emotional_intensity: float = 0.5  # 0.0-1.0
    cognitive_load: float = 0.5  # 0.0-1.0

    # Break point quality
    appropriateness_score: float = 0.5  # 0.0-1.0
    therapeutic_value: float = 0.5  # 0.0-1.0
    narrative_coherence: float = 0.5  # 0.0-1.0

    # Actions
    break_offered: bool = False
    break_accepted: bool = False
    break_message: str = ""
    continuation_message: str = ""


@dataclass
class SessionSummary:
    """Summary of session progress and achievements."""

    session_id: str = ""
    user_id: str = ""

    # Session details
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    duration_minutes: float = 0.0

    # Progress metrics
    scenes_completed: int = 0
    choices_made: int = 0
    therapeutic_concepts_encountered: int = 0
    character_development_events: int = 0
    milestones_achieved: int = 0

    # Therapeutic outcomes
    therapeutic_goals_addressed: list[str] = field(default_factory=list)
    skills_practiced: list[str] = field(default_factory=list)
    emotional_regulation_moments: int = 0

    # Character development
    character_attributes_improved: dict[str, float] = field(default_factory=dict)
    character_abilities_unlocked: list[str] = field(default_factory=list)
    character_milestones_achieved: list[str] = field(default_factory=list)

    # Session quality
    engagement_score: float = 0.0  # 0.0-1.0
    therapeutic_effectiveness: float = 0.0  # 0.0-1.0
    user_satisfaction: float | None = None  # 0.0-1.0

    # Next session preparation
    recommended_focus: str | None = None
    suggested_goals: list[str] = field(default_factory=list)
    continuation_context: str = ""


class GameplayLoopController:
    """Main controller for session lifecycle management and therapeutic session orchestration."""

    def __init__(
        self,
        narrative_engine: NarrativeEngine,
        choice_processor: ChoiceProcessor,
        session_manager: RedisSessionManager,
        event_bus: EventBus,
    ):
        self.narrative_engine = narrative_engine
        self.choice_processor = choice_processor
        self.session_manager = session_manager
        self.event_bus = event_bus

        # Session tracking
        self.active_sessions: dict[str, SessionConfiguration] = {}
        self.session_break_points: dict[str, list[SessionBreakPoint]] = {}
        self.session_summaries: dict[str, SessionSummary] = {}

        # Session management configuration
        self.pacing_configurations = self._load_pacing_configurations()
        self.break_point_detectors = self._load_break_point_detectors()
        self.session_templates = self._load_session_templates()

        # Auto-save and monitoring
        self.auto_save_tasks: dict[str, asyncio.Task] = {}
        self.session_monitors: dict[str, asyncio.Task] = {}

        # Metrics
        self.metrics = {
            "sessions_started": 0,
            "sessions_completed": 0,
            "sessions_paused": 0,
            "sessions_resumed": 0,
            "break_points_detected": 0,
            "break_points_accepted": 0,
            "auto_saves_performed": 0,
            "session_recoveries": 0,
        }

    def _load_pacing_configurations(self) -> dict[SessionPacing, dict[str, Any]]:
        """Load session pacing configurations."""
        return {
            SessionPacing.RELAXED: {
                "target_duration": 50,
                "max_duration": 75,
                "break_interval": 20,
                "scene_pace": "leisurely",
                "reflection_frequency": "high",
                "skill_practice_depth": "thorough",
            },
            SessionPacing.STANDARD: {
                "target_duration": 35,
                "max_duration": 50,
                "break_interval": 15,
                "scene_pace": "moderate",
                "reflection_frequency": "moderate",
                "skill_practice_depth": "balanced",
            },
            SessionPacing.FOCUSED: {
                "target_duration": 25,
                "max_duration": 35,
                "break_interval": 12,
                "scene_pace": "efficient",
                "reflection_frequency": "targeted",
                "skill_practice_depth": "focused",
            },
            SessionPacing.BRIEF: {
                "target_duration": 15,
                "max_duration": 25,
                "break_interval": 8,
                "scene_pace": "brisk",
                "reflection_frequency": "minimal",
                "skill_practice_depth": "essential",
            },
            SessionPacing.MICRO: {
                "target_duration": 8,
                "max_duration": 15,
                "break_interval": 5,
                "scene_pace": "rapid",
                "reflection_frequency": "brief",
                "skill_practice_depth": "core",
            },
        }

    def _load_break_point_detectors(self) -> dict[BreakPointType, dict[str, Any]]:
        """Load break point detection configurations."""
        return {
            BreakPointType.SCENE_TRANSITION: {
                "trigger_conditions": ["scene_completed", "narrative_pause"],
                "appropriateness_factors": ["narrative_coherence", "emotional_state"],
                "message_templates": [
                    "You've reached a natural pause in your adventure. Would you like to take a break?",
                    "This seems like a good place to pause and reflect. Take a break?",
                ],
            },
            BreakPointType.SKILL_COMPLETION: {
                "trigger_conditions": [
                    "therapeutic_skill_practiced",
                    "learning_objective_met",
                ],
                "appropriateness_factors": ["skill_mastery", "cognitive_load"],
                "message_templates": [
                    "You've just practiced an important skill. Perfect time for a break to let it sink in.",
                    "Great work on that therapeutic technique! Ready for a brief pause?",
                ],
            },
            BreakPointType.EMOTIONAL_PROCESSING: {
                "trigger_conditions": [
                    "high_emotional_intensity",
                    "emotional_breakthrough",
                ],
                "appropriateness_factors": ["emotional_safety", "processing_need"],
                "message_templates": [
                    "That was emotionally significant. Would you like some time to process?",
                    "You've been working through some deep feelings. A break might be helpful.",
                ],
            },
            BreakPointType.REFLECTION_MOMENT: {
                "trigger_conditions": ["insight_achieved", "pattern_recognized"],
                "appropriateness_factors": ["insight_depth", "integration_opportunity"],
                "message_templates": [
                    "You've gained some valuable insights. Time to pause and reflect?",
                    "This is a great moment for reflection. Would you like to take a break?",
                ],
            },
            BreakPointType.MILESTONE_ACHIEVEMENT: {
                "trigger_conditions": ["character_milestone", "therapeutic_milestone"],
                "appropriateness_factors": [
                    "achievement_significance",
                    "celebration_value",
                ],
                "message_templates": [
                    "Congratulations on this achievement! Perfect time to pause and celebrate.",
                    "You've reached an important milestone. Ready to take a well-deserved break?",
                ],
            },
            BreakPointType.TIME_BASED: {
                "trigger_conditions": ["duration_threshold", "break_interval_reached"],
                "appropriateness_factors": ["engagement_level", "fatigue_indicators"],
                "message_templates": [
                    "You've been engaged for a while. How about a quick break?",
                    "Time for a brief pause to recharge. Ready for a break?",
                ],
            },
        }

    def _load_session_templates(self) -> dict[str, dict[str, Any]]:
        """Load session templates for different therapeutic focuses."""
        return {
            "anxiety_management": {
                "phases": [
                    SessionPhase.WARM_UP,
                    SessionPhase.SKILL_PRACTICE,
                    SessionPhase.REFLECTION,
                    SessionPhase.INTEGRATION,
                ],
                "therapeutic_goals": [
                    "anxiety_reduction",
                    "coping_skills",
                    "emotional_regulation",
                ],
                "recommended_duration": 35,
                "break_point_emphasis": [
                    BreakPointType.EMOTIONAL_PROCESSING,
                    BreakPointType.SKILL_COMPLETION,
                ],
            },
            "communication_skills": {
                "phases": [
                    SessionPhase.WARM_UP,
                    SessionPhase.ACTIVE_ENGAGEMENT,
                    SessionPhase.SKILL_PRACTICE,
                    SessionPhase.REFLECTION,
                ],
                "therapeutic_goals": [
                    "communication_improvement",
                    "social_skills",
                    "relationship_building",
                ],
                "recommended_duration": 40,
                "break_point_emphasis": [
                    BreakPointType.SKILL_COMPLETION,
                    BreakPointType.REFLECTION_MOMENT,
                ],
            },
            "emotional_regulation": {
                "phases": [
                    SessionPhase.WARM_UP,
                    SessionPhase.SKILL_PRACTICE,
                    SessionPhase.EMOTIONAL_PROCESSING,
                    SessionPhase.INTEGRATION,
                ],
                "therapeutic_goals": [
                    "emotional_awareness",
                    "regulation_skills",
                    "emotional_intelligence",
                ],
                "recommended_duration": 30,
                "break_point_emphasis": [
                    BreakPointType.EMOTIONAL_PROCESSING,
                    BreakPointType.SKILL_COMPLETION,
                ],
            },
            "general_wellbeing": {
                "phases": [
                    SessionPhase.WARM_UP,
                    SessionPhase.ACTIVE_ENGAGEMENT,
                    SessionPhase.REFLECTION,
                    SessionPhase.CONCLUSION,
                ],
                "therapeutic_goals": [
                    "self_awareness",
                    "personal_growth",
                    "life_skills",
                ],
                "recommended_duration": 35,
                "break_point_emphasis": [
                    BreakPointType.REFLECTION_MOMENT,
                    BreakPointType.MILESTONE_ACHIEVEMENT,
                ],
            },
        }

    async def start_session(
        self, user_id: str, session_config: SessionConfiguration | None = None
    ) -> tuple[SessionState, SessionSummary]:
        """Start a new therapeutic session with comprehensive initialization."""
        try:
            # Create or use provided configuration
            if session_config is None:
                session_config = SessionConfiguration(user_id=user_id)

            session_id = session_config.session_id

            # Check for existing session recovery
            existing_session = await self._check_session_recovery(user_id)
            if existing_session and session_config.auto_recovery_enabled:
                return await self._recover_session(existing_session, session_config)

            # Create new session state
            session_state = SessionState(
                session_id=session_id,
                user_id=user_id,
                state=SessionStateType.INITIALIZING,
                therapeutic_goals=session_config.therapeutic_goals,
                user_preferences={
                    "pacing": session_config.pacing.value,
                    "target_duration": session_config.target_duration_minutes,
                    "break_notifications": session_config.break_point_notifications,
                    "time_reminders": session_config.time_reminders,
                },
            )

            # Initialize session summary
            session_summary = SessionSummary(
                session_id=session_id, user_id=user_id, start_time=datetime.utcnow()
            )

            # Store session configuration and summary
            self.active_sessions[session_id] = session_config
            self.session_summaries[session_id] = session_summary
            self.session_break_points[session_id] = []

            # Initialize narrative engine for session
            await self.narrative_engine.initialize_session(session_state)

            # Set up session monitoring and auto-save
            await self._setup_session_monitoring(session_id, session_config)

            # Transition to active state
            session_state.state = SessionStateType.ACTIVE
            session_state.update_activity()

            # Persist initial session state
            await self.session_manager.save_session(session_state)

            # Publish session start event
            await self._publish_session_event(
                session_state,
                "session_started",
                {
                    "session_config": {
                        "pacing": session_config.pacing.value,
                        "target_duration": session_config.target_duration_minutes,
                        "therapeutic_goals": session_config.therapeutic_goals,
                    }
                },
            )

            self.metrics["sessions_started"] += 1

            return session_state, session_summary

        except Exception as e:
            logger.error(f"Failed to start session for user {user_id}: {e}")
            raise

    async def pause_session(
        self, session_id: str, pause_reason: str | None = None
    ) -> SessionState:
        """Pause an active session with state preservation."""
        try:
            # Get current session state
            session_state = await self.session_manager.get_session(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")

            if session_state.state != SessionStateType.ACTIVE:
                raise ValueError(f"Cannot pause session in state {session_state.state}")

            # Update session state
            session_state.state = SessionStateType.PAUSED
            session_state.update_activity()

            # Add pause context
            pause_context = {
                "paused_at": datetime.utcnow().isoformat(),
                "pause_reason": pause_reason or "user_requested",
                "current_scene": session_state.current_scene_id,
                "narrative_context": session_state.context.get(
                    "current_narrative_context", ""
                ),
                "emotional_state": dict(session_state.emotional_state),
                "therapeutic_progress": session_state.context.get(
                    "therapeutic_progress", {}
                ),
            }

            session_state.context["pause_context"] = pause_context

            # Create session recap for resumption
            session_recap = await self._generate_session_recap(session_state)
            session_state.context["session_recap"] = session_recap

            # Persist session state
            await self.session_manager.save_session(session_state)

            # Stop session monitoring
            await self._stop_session_monitoring(session_id)

            # Publish session pause event
            await self._publish_session_event(
                session_state,
                "session_paused",
                {
                    "pause_reason": pause_reason,
                    "session_duration": (
                        datetime.utcnow() - session_state.created_at
                    ).total_seconds()
                    / 60,
                },
            )

            self.metrics["sessions_paused"] += 1

            return session_state

        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            raise

    async def resume_session(self, session_id: str) -> tuple[SessionState, str]:
        """Resume a paused session with context restoration."""
        try:
            # Get paused session state
            session_state = await self.session_manager.get_session(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")

            if session_state.state != SessionStateType.PAUSED:
                raise ValueError(
                    f"Cannot resume session in state {session_state.state}"
                )

            # Check session expiration
            if session_state.is_expired():
                raise ValueError(f"Session {session_id} has expired")

            # Update session state
            session_state.state = SessionStateType.ACTIVE
            session_state.update_activity()

            # Get session recap
            session_recap = session_state.context.get(
                "session_recap", "Welcome back to your therapeutic adventure!"
            )

            # Restore session configuration
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                # Recreate configuration from session state
                session_config = SessionConfiguration(
                    session_id=session_id,
                    user_id=session_state.user_id,
                    therapeutic_goals=session_state.therapeutic_goals,
                    target_duration_minutes=session_state.user_preferences.get(
                        "target_duration", 30
                    ),
                )
                self.active_sessions[session_id] = session_config

            # Restore session monitoring
            await self._setup_session_monitoring(session_id, session_config)

            # Update narrative engine context
            await self.narrative_engine.restore_session_context(session_state)

            # Persist updated session state
            await self.session_manager.save_session(session_state)

            # Publish session resume event
            await self._publish_session_event(
                session_state,
                "session_resumed",
                {
                    "pause_duration": (
                        datetime.utcnow()
                        - datetime.fromisoformat(
                            session_state.context.get("pause_context", {}).get(
                                "paused_at", datetime.utcnow().isoformat()
                            )
                        )
                    ).total_seconds()
                    / 60
                },
            )

            self.metrics["sessions_resumed"] += 1

            return session_state, session_recap

        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            raise

    async def end_session(
        self, session_id: str, completion_reason: str = "user_completed"
    ) -> SessionSummary:
        """End a session with comprehensive summary generation."""
        try:
            # Get current session state
            session_state = await self.session_manager.get_session(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")

            # Update session state
            session_state.state = SessionStateType.COMPLETED
            session_state.completed_at = datetime.utcnow()
            session_state.update_activity()

            # Generate comprehensive session summary
            session_summary = await self._generate_comprehensive_session_summary(
                session_state, completion_reason
            )

            # Store final session summary
            self.session_summaries[session_id] = session_summary

            # Clean up session resources
            await self._cleanup_session_resources(session_id)

            # Persist final session state
            await self.session_manager.save_session(session_state)

            # Publish session end event
            await self._publish_session_event(
                session_state,
                "session_ended",
                {
                    "completion_reason": completion_reason,
                    "total_duration": session_summary.duration_minutes,
                    "therapeutic_effectiveness": session_summary.therapeutic_effectiveness,
                    "engagement_score": session_summary.engagement_score,
                },
            )

            self.metrics["sessions_completed"] += 1

            return session_summary

        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise

    async def detect_break_points(
        self, session_state: SessionState
    ) -> SessionBreakPoint | None:
        """Detect natural break points in the session."""
        try:
            session_id = session_state.session_id
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                return None

            # Calculate session timing
            session_duration = (
                datetime.utcnow() - session_state.created_at
            ).total_seconds() / 60
            last_break_time = self._get_last_break_time(session_id)
            time_since_break = (
                datetime.utcnow() - last_break_time
            ).total_seconds() / 60

            # Check various break point conditions
            break_points = []

            # Time-based break points
            if time_since_break >= session_config.break_reminder_interval_minutes:
                break_point = await self._create_break_point(
                    session_state,
                    BreakPointType.TIME_BASED,
                    session_duration,
                    time_since_break,
                )
                break_points.append(break_point)

            # Scene transition break points
            if session_state.context.get("scene_transition_detected", False):
                break_point = await self._create_break_point(
                    session_state,
                    BreakPointType.SCENE_TRANSITION,
                    session_duration,
                    time_since_break,
                )
                break_points.append(break_point)

            # Therapeutic milestone break points
            if session_state.context.get("recent_milestone_achievement"):
                break_point = await self._create_break_point(
                    session_state,
                    BreakPointType.MILESTONE_ACHIEVEMENT,
                    session_duration,
                    time_since_break,
                )
                break_points.append(break_point)

            # Emotional processing break points
            emotional_intensity = (
                max(session_state.emotional_state.values())
                if session_state.emotional_state
                else 0.0
            )
            if emotional_intensity > 0.7:
                break_point = await self._create_break_point(
                    session_state,
                    BreakPointType.EMOTIONAL_PROCESSING,
                    session_duration,
                    time_since_break,
                )
                break_points.append(break_point)

            # Skill completion break points
            if session_state.context.get("recent_skill_practice"):
                break_point = await self._create_break_point(
                    session_state,
                    BreakPointType.SKILL_COMPLETION,
                    session_duration,
                    time_since_break,
                )
                break_points.append(break_point)

            # Select best break point
            if break_points:
                best_break_point = max(
                    break_points, key=lambda bp: bp.appropriateness_score
                )

                # Store break point
                if session_id not in self.session_break_points:
                    self.session_break_points[session_id] = []
                self.session_break_points[session_id].append(best_break_point)

                self.metrics["break_points_detected"] += 1

                return best_break_point

            return None

        except Exception as e:
            logger.error(
                f"Failed to detect break points for session {session_state.session_id}: {e}"
            )
            return None

    async def offer_break(
        self, session_state: SessionState, break_point: SessionBreakPoint
    ) -> dict[str, Any]:
        """Offer a break to the user with appropriate messaging."""
        try:
            # Get break point configuration
            break_config = self.break_point_detectors.get(break_point.break_type, {})
            message_templates = break_config.get(
                "message_templates",
                ["This seems like a good time for a break. Would you like to pause?"],
            )

            # Select appropriate message
            break_message = (
                message_templates[0]
                if message_templates
                else "Would you like to take a break?"
            )

            # Customize message based on context
            if break_point.break_type == BreakPointType.MILESTONE_ACHIEVEMENT:
                milestone_info = session_state.context.get(
                    "recent_milestone_achievement", {}
                )
                if milestone_info:
                    break_message = f"Congratulations on achieving '{milestone_info.get('name', 'a milestone')}'! Perfect time to pause and celebrate."

            elif break_point.break_type == BreakPointType.EMOTIONAL_PROCESSING:
                break_message = "You've been working through some important feelings. A break might help you process and integrate what you've experienced."

            elif break_point.break_type == BreakPointType.SKILL_COMPLETION:
                skill_info = session_state.context.get("recent_skill_practice", {})
                if skill_info:
                    break_message = f"Great work practicing {skill_info.get('skill_name', 'that skill')}! A break will help it sink in."

            # Update break point
            break_point.break_offered = True
            break_point.break_message = break_message
            break_point.continuation_message = (
                "Ready to continue your adventure when you are!"
            )

            # Create break offer response
            break_offer = {
                "break_point_id": break_point.break_point_id,
                "break_type": break_point.break_type.value,
                "message": break_message,
                "continuation_message": break_point.continuation_message,
                "session_duration_minutes": break_point.session_duration_minutes,
                "appropriateness_score": break_point.appropriateness_score,
                "therapeutic_value": break_point.therapeutic_value,
                "options": [
                    {
                        "id": "accept_break",
                        "text": "Yes, I'd like to take a break",
                        "action": "pause_session",
                    },
                    {
                        "id": "decline_break",
                        "text": "No, I'd like to continue",
                        "action": "continue_session",
                    },
                    {
                        "id": "short_break",
                        "text": "Just a quick moment",
                        "action": "micro_break",
                    },
                ],
            }

            return break_offer

        except Exception as e:
            logger.error(
                f"Failed to offer break for session {session_state.session_id}: {e}"
            )
            return {
                "message": "Would you like to take a break?",
                "options": [
                    {"id": "accept_break", "text": "Yes", "action": "pause_session"},
                    {"id": "decline_break", "text": "No", "action": "continue_session"},
                ],
            }

    async def handle_break_response(
        self, session_state: SessionState, break_point_id: str, response: str
    ) -> dict[str, Any]:
        """Handle user response to break offer."""
        try:
            # Find break point
            break_point = None
            session_break_points = self.session_break_points.get(
                session_state.session_id, []
            )
            for bp in session_break_points:
                if bp.break_point_id == break_point_id:
                    break_point = bp
                    break

            if not break_point:
                return {"action": "continue", "message": "Continuing your adventure..."}

            # Handle response
            if response == "accept_break":
                break_point.break_accepted = True
                self.metrics["break_points_accepted"] += 1

                # Pause session
                await self.pause_session(
                    session_state.session_id, "user_requested_break"
                )

                return {
                    "action": "session_paused",
                    "message": "Session paused. Take your time, and resume when you're ready!",
                    "break_point_id": break_point_id,
                }

            elif response == "decline_break":
                return {
                    "action": "continue",
                    "message": break_point.continuation_message
                    or "Continuing your adventure...",
                }

            elif response == "short_break":
                # Implement micro-break (brief pause without full session pause)
                return {
                    "action": "micro_break",
                    "message": "Take a moment to breathe and center yourself. Ready to continue?",
                    "duration_seconds": 30,
                }

            else:
                return {"action": "continue", "message": "Continuing your adventure..."}

        except Exception as e:
            logger.error(
                f"Failed to handle break response for session {session_state.session_id}: {e}"
            )
            return {"action": "continue", "message": "Continuing your adventure..."}

    async def _check_session_recovery(self, user_id: str) -> SessionState | None:
        """Check for recoverable sessions for a user."""
        try:
            # Get recent sessions for user
            recent_sessions = await self.session_manager.get_user_sessions(
                user_id, limit=5
            )

            for session_state in recent_sessions:
                # Check if session is recoverable (paused and not expired)
                if (
                    session_state.state == SessionStateType.PAUSED
                    and not session_state.is_expired()
                    and session_state.last_activity
                    > datetime.utcnow() - timedelta(hours=24)
                ):
                    return session_state

            return None

        except Exception as e:
            logger.error(f"Failed to check session recovery for user {user_id}: {e}")
            return None

    async def _recover_session(
        self, session_state: SessionState, session_config: SessionConfiguration
    ) -> tuple[SessionState, SessionSummary]:
        """Recover an existing session."""
        try:
            # Update session configuration
            self.active_sessions[session_state.session_id] = session_config

            # Get or create session summary
            session_summary = self.session_summaries.get(session_state.session_id)
            if not session_summary:
                session_summary = SessionSummary(
                    session_id=session_state.session_id,
                    user_id=session_state.user_id,
                    start_time=session_state.created_at,
                )
                self.session_summaries[session_state.session_id] = session_summary

            # Resume session
            session_state, recap = await self.resume_session(session_state.session_id)

            self.metrics["session_recoveries"] += 1

            return session_state, session_summary

        except Exception as e:
            logger.error(f"Failed to recover session {session_state.session_id}: {e}")
            raise

    async def _setup_session_monitoring(
        self, session_id: str, session_config: SessionConfiguration
    ) -> None:
        """Set up session monitoring and auto-save tasks."""
        try:
            # Set up auto-save task
            auto_save_task = asyncio.create_task(
                self._auto_save_loop(
                    session_id, session_config.auto_save_interval_minutes
                )
            )
            self.auto_save_tasks[session_id] = auto_save_task

            # Set up session monitoring task
            monitor_task = asyncio.create_task(
                self._session_monitor_loop(session_id, session_config)
            )
            self.session_monitors[session_id] = monitor_task

        except Exception as e:
            logger.error(f"Failed to setup session monitoring for {session_id}: {e}")

    async def _stop_session_monitoring(self, session_id: str) -> None:
        """Stop session monitoring and auto-save tasks."""
        try:
            # Stop auto-save task
            if session_id in self.auto_save_tasks:
                self.auto_save_tasks[session_id].cancel()
                del self.auto_save_tasks[session_id]

            # Stop monitoring task
            if session_id in self.session_monitors:
                self.session_monitors[session_id].cancel()
                del self.session_monitors[session_id]

        except Exception as e:
            logger.error(f"Failed to stop session monitoring for {session_id}: {e}")

    async def _auto_save_loop(self, session_id: str, interval_minutes: int) -> None:
        """Auto-save session state at regular intervals."""
        try:
            while True:
                await asyncio.sleep(interval_minutes * 60)  # Convert to seconds

                # Get current session state
                session_state = await self.session_manager.get_session(session_id)
                if session_state and session_state.state == SessionStateType.ACTIVE:
                    # Save session state
                    await self.session_manager.save_session(session_state)
                    self.metrics["auto_saves_performed"] += 1
                else:
                    # Session no longer active, stop auto-save
                    break

        except asyncio.CancelledError:
            # Task was cancelled, normal shutdown
            pass
        except Exception as e:
            logger.error(f"Auto-save loop error for session {session_id}: {e}")

    async def _session_monitor_loop(
        self, session_id: str, session_config: SessionConfiguration
    ) -> None:
        """Monitor session for break points and time management."""
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute

                # Get current session state
                session_state = await self.session_manager.get_session(session_id)
                if not session_state or session_state.state != SessionStateType.ACTIVE:
                    break

                # Check for break points
                break_point = await self.detect_break_points(session_state)
                if break_point and session_config.break_point_notifications:
                    # Publish break point detection event
                    await self._publish_session_event(
                        session_state,
                        "break_point_detected",
                        {
                            "break_point_id": break_point.break_point_id,
                            "break_type": break_point.break_type.value,
                            "appropriateness_score": break_point.appropriateness_score,
                        },
                    )

                # Check session duration limits
                session_duration = (
                    datetime.utcnow() - session_state.created_at
                ).total_seconds() / 60
                if session_duration >= session_config.max_duration_minutes:
                    # Suggest session conclusion
                    await self._publish_session_event(
                        session_state,
                        "session_duration_limit_reached",
                        {
                            "duration_minutes": session_duration,
                            "max_duration": session_config.max_duration_minutes,
                        },
                    )

        except asyncio.CancelledError:
            # Task was cancelled, normal shutdown
            pass
        except Exception as e:
            logger.error(f"Session monitor loop error for session {session_id}: {e}")

    async def _generate_session_recap(self, session_state: SessionState) -> str:
        """Generate a session recap for resumption."""
        try:
            # Get session progress
            scenes_completed = len(session_state.scene_history)
            choices_made = len(session_state.choice_history)

            # Get therapeutic progress
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            character_development = session_state.context.get(
                "recent_character_development", {}
            )

            # Build recap
            recap_parts = []

            # Basic progress
            if scenes_completed > 0:
                recap_parts.append(
                    f"You've explored {scenes_completed} scenes in your therapeutic adventure"
                )

            if choices_made > 0:
                recap_parts.append(
                    f"and made {choices_made} meaningful choices along the way"
                )

            # Therapeutic progress
            if therapeutic_progress:
                concepts_learned = therapeutic_progress.get("concepts_integrated", 0)
                if concepts_learned > 0:
                    recap_parts.append(
                        f"You've engaged with {concepts_learned} therapeutic concepts"
                    )

            # Character development
            if character_development:
                attribute_changes = character_development.get("attribute_changes", {})
                if attribute_changes:
                    improved_attributes = [
                        attr for attr, change in attribute_changes.items() if change > 0
                    ]
                    if improved_attributes:
                        recap_parts.append(
                            f"Your character has grown in {', '.join(improved_attributes[:2])}"
                        )

            # Current context
            current_scene = session_state.current_scene_id
            if current_scene:
                recap_parts.append(f"You're currently in scene '{current_scene}'")

            # Combine recap
            if recap_parts:
                recap = ". ".join(recap_parts) + ". Ready to continue your journey?"
            else:
                recap = "Welcome back to your therapeutic adventure! Ready to continue your journey?"

            return recap

        except Exception as e:
            logger.error(
                f"Failed to generate session recap for {session_state.session_id}: {e}"
            )
            return "Welcome back to your therapeutic adventure! Ready to continue?"

    async def _generate_comprehensive_session_summary(
        self, session_state: SessionState, completion_reason: str
    ) -> SessionSummary:
        """Generate comprehensive session summary."""
        try:
            session_summary = self.session_summaries.get(
                session_state.session_id,
                SessionSummary(
                    session_id=session_state.session_id,
                    user_id=session_state.user_id,
                    start_time=session_state.created_at,
                ),
            )

            # Update basic metrics
            session_summary.end_time = datetime.utcnow()
            session_summary.duration_minutes = (
                session_summary.end_time - session_summary.start_time
            ).total_seconds() / 60
            session_summary.scenes_completed = len(session_state.scene_history)
            session_summary.choices_made = len(session_state.choice_history)

            # Therapeutic metrics
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            session_summary.therapeutic_concepts_encountered = therapeutic_progress.get(
                "concepts_integrated", 0
            )
            session_summary.emotional_regulation_moments = therapeutic_progress.get(
                "emotional_regulation_events", 0
            )

            # Character development metrics
            character_development = session_state.context.get(
                "character_development_summary", {}
            )
            session_summary.character_development_events = character_development.get(
                "development_events", 0
            )
            session_summary.character_attributes_improved = character_development.get(
                "attributes_improved", {}
            )
            session_summary.character_abilities_unlocked = character_development.get(
                "abilities_unlocked", []
            )
            session_summary.character_milestones_achieved = character_development.get(
                "milestones_achieved", []
            )

            # Calculate engagement and effectiveness scores
            session_summary.engagement_score = self._calculate_engagement_score(
                session_state
            )
            session_summary.therapeutic_effectiveness = (
                self._calculate_therapeutic_effectiveness(session_state)
            )

            # Generate recommendations for next session
            session_summary.recommended_focus = self._recommend_next_session_focus(
                session_state
            )
            session_summary.suggested_goals = self._suggest_next_session_goals(
                session_state
            )
            session_summary.continuation_context = (
                await self._generate_continuation_context(session_state)
            )

            return session_summary

        except Exception as e:
            logger.error(
                f"Failed to generate comprehensive session summary for {session_state.session_id}: {e}"
            )
            return SessionSummary(
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                start_time=session_state.created_at,
                end_time=datetime.utcnow(),
            )

    def _calculate_engagement_score(self, session_state: SessionState) -> float:
        """Calculate user engagement score based on session activity."""
        try:
            score = 0.0

            # Choice frequency (0.0-0.3)
            session_duration = (
                datetime.utcnow() - session_state.created_at
            ).total_seconds() / 60
            if session_duration > 0:
                choices_per_minute = (
                    len(session_state.choice_history) / session_duration
                )
                score += min(0.3, choices_per_minute * 0.1)

            # Scene progression (0.0-0.3)
            scenes_per_minute = len(session_state.scene_history) / max(
                session_duration, 1
            )
            score += min(0.3, scenes_per_minute * 0.15)

            # Therapeutic engagement (0.0-0.2)
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            concepts_engaged = therapeutic_progress.get("concepts_integrated", 0)
            score += min(0.2, concepts_engaged * 0.05)

            # Character development engagement (0.0-0.2)
            character_development = session_state.context.get(
                "character_development_summary", {}
            )
            development_events = character_development.get("development_events", 0)
            score += min(0.2, development_events * 0.04)

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Failed to calculate engagement score: {e}")
            return 0.5

    def _calculate_therapeutic_effectiveness(
        self, session_state: SessionState
    ) -> float:
        """Calculate therapeutic effectiveness score."""
        try:
            score = 0.0

            # Therapeutic goal progress (0.0-0.4)
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            goals_addressed = len(therapeutic_progress.get("goals_addressed", []))
            total_goals = len(session_state.therapeutic_goals)
            if total_goals > 0:
                score += (goals_addressed / total_goals) * 0.4

            # Skill practice and application (0.0-0.3)
            skills_practiced = len(therapeutic_progress.get("skills_practiced", []))
            score += min(0.3, skills_practiced * 0.1)

            # Emotional regulation success (0.0-0.2)
            emotional_regulation_events = therapeutic_progress.get(
                "emotional_regulation_events", 0
            )
            score += min(0.2, emotional_regulation_events * 0.05)

            # Character development alignment (0.0-0.1)
            character_development = session_state.context.get(
                "character_development_summary", {}
            )
            therapeutic_aligned_development = character_development.get(
                "therapeutic_aligned_events", 0
            )
            score += min(0.1, therapeutic_aligned_development * 0.02)

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Failed to calculate therapeutic effectiveness: {e}")
            return 0.5

    def _recommend_next_session_focus(self, session_state: SessionState) -> str | None:
        """Recommend focus for next session based on current progress."""
        try:
            # Analyze therapeutic progress
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})

            # Check for areas needing more work
            goals_progress = therapeutic_progress.get("goals_progress", {})
            if goals_progress:
                # Find goal with lowest progress
                min_progress_goal = min(goals_progress.items(), key=lambda x: x[1])
                if min_progress_goal[1] < 0.5:  # Less than 50% progress
                    return min_progress_goal[0]

            # Check for resistance patterns
            resistance_patterns = therapeutic_progress.get("resistance_patterns", [])
            if resistance_patterns:
                return f"addressing_{resistance_patterns[0]}_resistance"

            # Check character development opportunities
            character_development = session_state.context.get(
                "character_development_summary", {}
            )
            underdeveloped_attributes = character_development.get(
                "underdeveloped_attributes", []
            )
            if underdeveloped_attributes:
                return f"character_development_{underdeveloped_attributes[0]}"

            # Default to general wellbeing
            return "general_wellbeing"

        except Exception as e:
            logger.error(f"Failed to recommend next session focus: {e}")
            return "general_wellbeing"

    def _suggest_next_session_goals(self, session_state: SessionState) -> list[str]:
        """Suggest goals for next session."""
        try:
            suggestions = []

            # Continue incomplete therapeutic goals
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            incomplete_goals = therapeutic_progress.get("incomplete_goals", [])
            suggestions.extend(incomplete_goals[:2])  # Top 2 incomplete goals

            # Add character development goals
            character_development = session_state.context.get(
                "character_development_summary", {}
            )
            development_opportunities = character_development.get(
                "development_opportunities", []
            )
            suggestions.extend(
                development_opportunities[:1]
            )  # Top development opportunity

            # Add skill practice goals
            skills_to_practice = therapeutic_progress.get("skills_needing_practice", [])
            if skills_to_practice:
                suggestions.append(f"practice_{skills_to_practice[0]}")

            return suggestions[:3]  # Limit to 3 suggestions

        except Exception as e:
            logger.error(f"Failed to suggest next session goals: {e}")
            return ["continue_therapeutic_journey"]

    async def _generate_continuation_context(self, session_state: SessionState) -> str:
        """Generate context for continuing the therapeutic journey."""
        try:
            context_parts = []

            # Current narrative position
            if session_state.current_scene_id:
                context_parts.append(
                    f"Continue from scene: {session_state.current_scene_id}"
                )

            # Therapeutic progress context
            therapeutic_progress = session_state.context.get("therapeutic_progress", {})
            if therapeutic_progress.get("active_concepts"):
                active_concepts = therapeutic_progress["active_concepts"][:2]
                context_parts.append(
                    f"Active therapeutic concepts: {', '.join(active_concepts)}"
                )

            # Character development context
            character_development = session_state.context.get(
                "recent_character_development", {}
            )
            if character_development.get("attribute_changes"):
                context_parts.append("Character development in progress")

            # Emotional context
            if session_state.emotional_state:
                dominant_emotion = max(
                    session_state.emotional_state.items(), key=lambda x: x[1]
                )
                if dominant_emotion[1] > 0.3:
                    context_parts.append(f"Emotional context: {dominant_emotion[0]}")

            return (
                "; ".join(context_parts)
                if context_parts
                else "Ready for next therapeutic adventure"
            )

        except Exception as e:
            logger.error(f"Failed to generate continuation context: {e}")
            return "Ready for next therapeutic adventure"

    async def _cleanup_session_resources(self, session_id: str) -> None:
        """Clean up session resources."""
        try:
            # Stop monitoring tasks
            await self._stop_session_monitoring(session_id)

            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            # Keep session summary and break points for analytics
            # (Don't delete these as they may be needed for reporting)

        except Exception as e:
            logger.error(f"Failed to cleanup session resources for {session_id}: {e}")

    async def _create_break_point(
        self,
        session_state: SessionState,
        break_type: BreakPointType,
        session_duration: float,
        time_since_break: float,
    ) -> SessionBreakPoint:
        """Create a break point with appropriateness scoring."""
        try:
            break_point = SessionBreakPoint(
                session_id=session_state.session_id,
                break_type=break_type,
                current_scene_id=session_state.current_scene_id,
                narrative_context=session_state.context.get(
                    "current_narrative_context", ""
                ),
                therapeutic_context=session_state.context.get(
                    "current_therapeutic_context", ""
                ),
                session_duration_minutes=session_duration,
                time_since_last_break_minutes=time_since_break,
            )

            # Calculate user state metrics
            break_point.engagement_level = session_state.engagement_metrics.get(
                "current_engagement", 0.5
            )
            break_point.emotional_intensity = (
                max(session_state.emotional_state.values())
                if session_state.emotional_state
                else 0.5
            )
            break_point.cognitive_load = session_state.context.get(
                "cognitive_load", 0.5
            )

            # Calculate appropriateness score
            break_point.appropriateness_score = (
                self._calculate_break_point_appropriateness(break_point, session_state)
            )
            break_point.therapeutic_value = (
                self._calculate_break_point_therapeutic_value(
                    break_point, session_state
                )
            )
            break_point.narrative_coherence = (
                self._calculate_break_point_narrative_coherence(
                    break_point, session_state
                )
            )

            return break_point

        except Exception as e:
            logger.error(f"Failed to create break point: {e}")
            return SessionBreakPoint(
                session_id=session_state.session_id, break_type=break_type
            )

    def _calculate_break_point_appropriateness(
        self, break_point: SessionBreakPoint, session_state: SessionState
    ) -> float:
        """Calculate break point appropriateness score."""
        try:
            score = 0.0

            # Time-based factors (0.0-0.4)
            if break_point.time_since_last_break_minutes >= 15:
                score += 0.4
            elif break_point.time_since_last_break_minutes >= 10:
                score += 0.2

            # Engagement factors (0.0-0.3)
            if break_point.engagement_level < 0.3:  # Low engagement
                score += 0.3
            elif (
                break_point.engagement_level > 0.8
            ):  # High engagement, might not want break
                score -= 0.1

            # Emotional factors (0.0-0.2)
            if break_point.emotional_intensity > 0.7:  # High emotional intensity
                score += 0.2

            # Cognitive load factors (0.0-0.1)
            if break_point.cognitive_load > 0.7:  # High cognitive load
                score += 0.1

            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"Failed to calculate break point appropriateness: {e}")
            return 0.5

    def _calculate_break_point_therapeutic_value(
        self, break_point: SessionBreakPoint, session_state: SessionState
    ) -> float:
        """Calculate therapeutic value of break point."""
        try:
            # Break points after therapeutic milestones have high value
            if break_point.break_type == BreakPointType.MILESTONE_ACHIEVEMENT:
                return 0.9

            # Break points during emotional processing have high value
            if break_point.break_type == BreakPointType.EMOTIONAL_PROCESSING:
                return 0.8

            # Break points after skill practice have moderate value
            if break_point.break_type == BreakPointType.SKILL_COMPLETION:
                return 0.7

            # Other break points have moderate value
            return 0.5

        except Exception as e:
            logger.error(f"Failed to calculate break point therapeutic value: {e}")
            return 0.5

    def _calculate_break_point_narrative_coherence(
        self, break_point: SessionBreakPoint, session_state: SessionState
    ) -> float:
        """Calculate narrative coherence of break point."""
        try:
            # Scene transitions have high narrative coherence
            if break_point.break_type == BreakPointType.SCENE_TRANSITION:
                return 0.9

            # Reflection moments have high coherence
            if break_point.break_type == BreakPointType.REFLECTION_MOMENT:
                return 0.8

            # Time-based breaks have lower coherence
            if break_point.break_type == BreakPointType.TIME_BASED:
                return 0.4

            # Other break points have moderate coherence
            return 0.6

        except Exception as e:
            logger.error(f"Failed to calculate break point narrative coherence: {e}")
            return 0.5

    def _get_last_break_time(self, session_id: str) -> datetime:
        """Get the time of the last break for a session."""
        try:
            break_points = self.session_break_points.get(session_id, [])
            if break_points:
                last_break = max(break_points, key=lambda bp: bp.detected_at)
                return last_break.detected_at

            # If no breaks yet, use session start time
            session_config = self.active_sessions.get(session_id)
            if session_config:
                return session_config.created_at

            return datetime.utcnow() - timedelta(hours=1)  # Default fallback

        except Exception as e:
            logger.error(f"Failed to get last break time for session {session_id}: {e}")
            return datetime.utcnow() - timedelta(hours=1)

    async def _publish_session_event(
        self, session_state: SessionState, event_type: str, context: dict[str, Any]
    ) -> None:
        """Publish session management event."""
        try:
            narrative_event = NarrativeEvent(
                event_type=EventType.SESSION_MANAGEMENT,
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                context={
                    "session_event_type": event_type,
                    "session_state": session_state.state.value,
                    **context,
                },
            )

            await self.event_bus.publish(narrative_event)

        except Exception as e:
            logger.error(f"Failed to publish session event {event_type}: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get session management metrics."""
        return {
            **self.metrics,
            "active_sessions_count": len(self.active_sessions),
            "total_break_points": sum(
                len(bp_list) for bp_list in self.session_break_points.values()
            ),
            "auto_save_tasks_active": len(self.auto_save_tasks),
            "session_monitors_active": len(self.session_monitors),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of session management system."""
        return {
            "status": "healthy",
            "active_sessions": len(self.active_sessions),
            "pacing_configurations_loaded": len(self.pacing_configurations),
            "break_point_detectors_loaded": len(self.break_point_detectors),
            "session_templates_loaded": len(self.session_templates),
            "auto_save_tasks_running": len(self.auto_save_tasks),
            "session_monitors_running": len(self.session_monitors),
            "metrics": self.get_metrics(),
        }
