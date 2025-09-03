"""
Scene Manager for Narrative Engine

This module handles individual scene logic, transitions, and state management
for therapeutic narrative experiences.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.gameplay_loop.models.core import (
    NarrativeScene,
    SceneType,
)
from src.components.gameplay_loop.services.session_state import SessionState

from .events import EventType, create_scene_event

logger = logging.getLogger(__name__)


class SceneStatus(str, Enum):
    """Scene processing status."""

    LOADING = "loading"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SceneContext:
    """Context for scene processing."""

    scene: NarrativeScene
    session_state: SessionState
    entry_time: datetime = field(default_factory=datetime.utcnow)
    status: SceneStatus = SceneStatus.LOADING

    # Scene-specific state
    variables: dict[str, Any] = field(default_factory=dict)
    choices_presented: list[str] = field(default_factory=list)
    user_interactions: list[dict[str, Any]] = field(default_factory=list)

    # Therapeutic tracking
    therapeutic_moments: list[dict[str, Any]] = field(default_factory=list)
    emotional_responses: dict[str, float] = field(default_factory=dict)
    skill_practice_opportunities: list[str] = field(default_factory=list)

    # Performance metrics
    time_spent: timedelta = field(default=timedelta())
    engagement_score: float = field(default=0.0)
    completion_rate: float = field(default=0.0)

    def update_time_spent(self) -> None:
        """Update time spent in scene."""
        self.time_spent = datetime.utcnow() - self.entry_time

    def add_interaction(self, interaction_type: str, data: dict[str, Any]) -> None:
        """Add user interaction to scene context."""
        interaction = {
            "type": interaction_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self.user_interactions.append(interaction)

    def record_therapeutic_moment(
        self, moment_type: str, description: str, relevance: float = 1.0
    ) -> None:
        """Record a therapeutic moment in the scene."""
        moment = {
            "type": moment_type,
            "description": description,
            "relevance": relevance,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.therapeutic_moments.append(moment)

    def update_emotional_response(self, emotion: str, intensity: float) -> None:
        """Update emotional response tracking."""
        if 0.0 <= intensity <= 1.0:
            self.emotional_responses[emotion] = intensity


@dataclass
class SceneTransition:
    """Represents a transition between scenes."""

    from_scene_id: str
    to_scene_id: str
    trigger_type: str  # choice, automatic, conditional
    trigger_data: dict[str, Any] = field(default_factory=dict)
    conditions: list[str] = field(default_factory=list)
    therapeutic_impact: float = field(default=0.0)

    def is_valid(self, session_state: SessionState) -> bool:
        """Check if transition is valid given current session state."""
        # Basic validation
        if not self.to_scene_id:
            return False

        # Check conditions
        for condition in self.conditions:
            if not self._evaluate_condition(condition, session_state):
                return False

        return True

    def _evaluate_condition(self, condition: str, session_state: SessionState) -> bool:
        """Evaluate a transition condition."""
        # Simple condition evaluation - can be extended
        if condition.startswith("has_variable:"):
            var_name = condition.split(":", 1)[1]
            return session_state.get_narrative_variable(var_name) is not None

        elif condition.startswith("emotional_state:"):
            parts = condition.split(":")
            if len(parts) == 3:
                emotion, operator, threshold = (
                    parts[1],
                    parts[2][0],
                    float(parts[2][1:]),
                )
                current_value = session_state.emotional_state.get(emotion, 0.0)

                if operator == ">":
                    return current_value > threshold
                elif operator == "<":
                    return current_value < threshold
                elif operator == "=":
                    return abs(current_value - threshold) < 0.1

        elif condition == "safety_cleared":
            return session_state.safety_level != "crisis"

        return True  # Default to true for unknown conditions


class SceneValidator:
    """Validates scene content and transitions."""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> dict[str, Any]:
        """Load scene validation rules."""
        return {
            "required_fields": ["scene_id", "title", "narrative_content"],
            "max_content_length": 5000,
            "min_content_length": 50,
            "allowed_scene_types": [t.value for t in SceneType],
            "therapeutic_focus_required": True,
            "safety_validation_required": True,
        }

    def validate_scene(self, scene: NarrativeScene) -> tuple[bool, list[str]]:
        """Validate scene content."""
        issues = []

        # Check required fields
        for field_name in self.validation_rules["required_fields"]:
            if not getattr(scene, field_name, None):
                issues.append(f"Missing required field: {field_name}")

        # Check content length
        content_length = len(scene.narrative_content or "")
        if content_length < self.validation_rules["min_content_length"]:
            issues.append(f"Content too short: {content_length} characters")
        elif content_length > self.validation_rules["max_content_length"]:
            issues.append(f"Content too long: {content_length} characters")

        # Check scene type
        if scene.scene_type not in self.validation_rules["allowed_scene_types"]:
            issues.append(f"Invalid scene type: {scene.scene_type}")

        # Check therapeutic focus
        if (
            self.validation_rules["therapeutic_focus_required"]
            and not scene.therapeutic_focus
        ):
            issues.append("Therapeutic focus is required")

        return len(issues) == 0, issues

    def validate_transition(
        self, transition: SceneTransition, session_state: SessionState
    ) -> tuple[bool, list[str]]:
        """Validate scene transition."""
        issues = []

        # Check basic transition validity
        if not transition.is_valid(session_state):
            issues.append("Transition conditions not met")

        # Check therapeutic appropriateness
        if transition.therapeutic_impact < -0.5:
            issues.append("Transition may have negative therapeutic impact")

        # Check safety considerations
        if (
            session_state.safety_level == "crisis"
            and transition.trigger_type != "safety"
        ):
            issues.append("Only safety transitions allowed in crisis mode")

        return len(issues) == 0, issues


class SceneManager:
    """Manages scene processing and transitions."""

    def __init__(self, narrative_engine):
        self.narrative_engine = narrative_engine
        self.validator = SceneValidator()

        # Scene cache
        self.scene_cache: dict[str, NarrativeScene] = {}
        self.scene_contexts: dict[str, SceneContext] = {}

        # Metrics
        self.metrics = {
            "scenes_loaded": 0,
            "scenes_entered": 0,
            "scenes_completed": 0,
            "transitions_processed": 0,
            "validation_failures": 0,
        }

    async def initialize(self) -> None:
        """Initialize the scene manager."""
        logger.info("Initializing scene manager...")

        # Subscribe to relevant events
        self.narrative_engine.event_bus.subscribe(
            EventType.SCENE_ENTERED, self._handle_scene_entered
        )
        self.narrative_engine.event_bus.subscribe(
            EventType.SCENE_COMPLETED, self._handle_scene_completed
        )

        logger.info("Scene manager initialized")

    async def load_scene(self, scene_id: str) -> NarrativeScene | None:
        """Load a scene by ID."""
        try:
            # Check cache first
            if scene_id in self.scene_cache:
                return self.scene_cache[scene_id]

            # Load from database
            scene_data = await self.narrative_engine.database_manager.narrative_manager.get_scene_by_id(
                scene_id
            )

            if not scene_data:
                logger.warning(f"Scene not found: {scene_id}")
                return None

            # Create scene object
            scene = NarrativeScene(
                scene_id=scene_data["scene_id"],
                session_id=scene_data.get("session_id", ""),
                title=scene_data["title"],
                description=scene_data.get("description", ""),
                narrative_content=scene_data["narrative_content"],
                scene_type=SceneType(
                    scene_data.get("scene_type", SceneType.EXPLORATION.value)
                ),
                therapeutic_focus=scene_data.get("therapeutic_focus", []),
                emotional_tone=scene_data.get("emotional_tone", {}),
                difficulty_level=scene_data.get("difficulty_level", 1),
                estimated_duration=scene_data.get("estimated_duration", 5),
            )

            # Validate scene
            is_valid, issues = self.validator.validate_scene(scene)
            if not is_valid:
                logger.error(f"Scene validation failed for {scene_id}: {issues}")
                self.metrics["validation_failures"] += 1
                return None

            # Cache scene
            if self.narrative_engine.config.cache_scenes:
                self.scene_cache[scene_id] = scene

            self.metrics["scenes_loaded"] += 1
            return scene

        except Exception as e:
            logger.error(f"Failed to load scene {scene_id}: {e}")
            return None

    async def enter_scene(
        self, session_state: SessionState, scene: NarrativeScene
    ) -> bool:
        """Enter a scene in the narrative."""
        try:
            # Create scene context
            context = SceneContext(scene=scene, session_state=session_state)

            # Store context
            context_key = f"{session_state.session_id}:{scene.scene_id}"
            self.scene_contexts[context_key] = context

            # Update session state
            session_state.current_scene_id = scene.scene_id
            session_state.update_activity()

            # Apply scene effects
            await self._apply_scene_effects(context)

            # Load available choices
            if self.narrative_engine.config.preload_choices:
                await self._preload_scene_choices(context)

            # Update context status
            context.status = SceneStatus.ACTIVE

            # Publish scene entered event
            event = create_scene_event(
                EventType.SCENE_ENTERED,
                session_state.session_id,
                session_state.user_id,
                scene.scene_id,
                scene.scene_type.value,
                scene.therapeutic_focus,
                data={
                    "scene_title": scene.title,
                    "difficulty_level": scene.difficulty_level,
                    "estimated_duration": scene.estimated_duration,
                },
            )
            await self.narrative_engine.event_bus.publish(event)

            self.metrics["scenes_entered"] += 1
            logger.debug(
                f"Entered scene {scene.scene_id} for session {session_state.session_id}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to enter scene {scene.scene_id}: {e}")
            return False

    async def exit_scene(
        self,
        session_state: SessionState,
        scene_id: str,
        completion_status: SceneStatus = SceneStatus.COMPLETED,
    ) -> bool:
        """Exit a scene."""
        try:
            context_key = f"{session_state.session_id}:{scene_id}"

            if context_key not in self.scene_contexts:
                logger.warning(f"Scene context not found: {context_key}")
                return False

            context = self.scene_contexts[context_key]
            context.status = completion_status
            context.update_time_spent()

            # Calculate completion metrics
            context.completion_rate = self._calculate_completion_rate(context)
            context.engagement_score = self._calculate_engagement_score(context)

            # Record scene completion in session state
            if completion_status == SceneStatus.COMPLETED:
                session_state.add_progress_snapshot(
                    {
                        "scene_id": scene_id,
                        "completion_status": completion_status.value,
                        "time_spent": context.time_spent.total_seconds(),
                        "engagement_score": context.engagement_score,
                        "therapeutic_moments": len(context.therapeutic_moments),
                    }
                )

            # Publish scene exited event
            event = create_scene_event(
                EventType.SCENE_EXITED,
                session_state.session_id,
                session_state.user_id,
                scene_id,
                context.scene.scene_type.value,
                context.scene.therapeutic_focus,
                data={
                    "completion_status": completion_status.value,
                    "time_spent": context.time_spent.total_seconds(),
                    "engagement_score": context.engagement_score,
                    "therapeutic_moments": len(context.therapeutic_moments),
                },
            )
            await self.narrative_engine.event_bus.publish(event)

            # Clean up context
            del self.scene_contexts[context_key]

            if completion_status == SceneStatus.COMPLETED:
                self.metrics["scenes_completed"] += 1

            logger.debug(
                f"Exited scene {scene_id} for session {session_state.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to exit scene {scene_id}: {e}")
            return False

    async def get_scene_context(
        self, session_id: str, scene_id: str
    ) -> SceneContext | None:
        """Get scene context."""
        context_key = f"{session_id}:{scene_id}"
        return self.scene_contexts.get(context_key)

    async def _apply_scene_effects(self, context: SceneContext) -> None:
        """Apply scene effects to session state."""
        scene = context.scene
        session_state = context.session_state

        # Apply emotional tone effects
        for emotion, intensity in scene.emotional_tone.items():
            current_intensity = session_state.emotional_state.get(emotion, 0.0)
            # Blend current and scene emotional tones
            new_intensity = (current_intensity + intensity) / 2
            session_state.update_emotional_state(emotion, new_intensity)
            context.update_emotional_response(emotion, new_intensity)

        # Set narrative variables based on scene
        session_state.set_narrative_variable(
            "current_scene_type", scene.scene_type.value
        )
        session_state.set_narrative_variable("scene_difficulty", scene.difficulty_level)

        # Track therapeutic focus
        for focus in scene.therapeutic_focus:
            session_state.set_narrative_variable(f"practicing_{focus}", True)

    async def _preload_scene_choices(self, context: SceneContext) -> None:
        """Preload available choices for the scene."""
        try:
            choices = await self.narrative_engine.database_manager.narrative_manager.get_scene_choices(
                context.scene.scene_id
            )

            context.choices_presented = [choice["choice_id"] for choice in choices]

        except Exception as e:
            logger.error(
                f"Failed to preload choices for scene {context.scene.scene_id}: {e}"
            )

    def _calculate_completion_rate(self, context: SceneContext) -> float:
        """Calculate scene completion rate."""
        # Simple completion rate based on interactions and time spent
        expected_interactions = max(len(context.choices_presented), 1)
        actual_interactions = len(context.user_interactions)

        interaction_rate = min(actual_interactions / expected_interactions, 1.0)

        # Factor in time spent (scenes have estimated duration)
        expected_time = context.scene.estimated_duration * 60  # Convert to seconds
        actual_time = context.time_spent.total_seconds()
        time_factor = (
            min(actual_time / expected_time, 2.0) / 2.0
        )  # Cap at 2x expected time

        return (interaction_rate + time_factor) / 2

    def _calculate_engagement_score(self, context: SceneContext) -> float:
        """Calculate engagement score for the scene."""
        score = 0.0

        # Base score from interactions
        if context.user_interactions:
            score += 0.3

        # Bonus for therapeutic moments
        if context.therapeutic_moments:
            score += 0.3 * min(len(context.therapeutic_moments) / 3, 1.0)

        # Bonus for emotional responses
        if context.emotional_responses:
            avg_intensity = sum(context.emotional_responses.values()) / len(
                context.emotional_responses
            )
            score += 0.2 * avg_intensity

        # Time-based engagement
        expected_time = context.scene.estimated_duration * 60
        actual_time = context.time_spent.total_seconds()
        if 0.5 * expected_time <= actual_time <= 2 * expected_time:
            score += 0.2

        return min(score, 1.0)

    async def _handle_scene_entered(self, event) -> None:
        """Handle scene entered events."""
        logger.debug(
            f"Scene entered: {event.context.get('scene_id')} in session {event.session_id}"
        )

    async def _handle_scene_completed(self, event) -> None:
        """Handle scene completed events."""
        logger.debug(
            f"Scene completed: {event.context.get('scene_id')} in session {event.session_id}"
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get scene manager metrics."""
        return {
            **self.metrics,
            "cached_scenes": len(self.scene_cache),
            "active_contexts": len(self.scene_contexts),
        }
