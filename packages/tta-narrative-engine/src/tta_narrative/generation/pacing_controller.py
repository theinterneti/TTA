"""
Pacing Controller for Therapeutic Text Adventure

This module implements pacing control functionality that manages the rhythm
and flow of therapeutic narrative experiences to optimize engagement,
learning, and therapeutic effectiveness.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from ..models.core import EmotionalState, Scene, SceneType, SessionState

logger = logging.getLogger(__name__)


class PacingStrategy(str, Enum):
    """Strategies for pacing control."""

    ACCELERATE = "accelerate"
    MAINTAIN = "maintain"
    DECELERATE = "decelerate"
    PAUSE = "pause"
    RESET = "reset"


class PacingDimension(str, Enum):
    """Dimensions of pacing that can be controlled."""

    NARRATIVE_FLOW = "narrative_flow"
    THERAPEUTIC_INTENSITY = "therapeutic_intensity"
    COGNITIVE_LOAD = "cognitive_load"
    EMOTIONAL_PACING = "emotional_pacing"
    INTERACTION_FREQUENCY = "interaction_frequency"


class SessionPhase(str, Enum):
    """Phases of a therapeutic session for pacing context."""

    OPENING = "opening"
    ENGAGEMENT = "engagement"
    WORKING = "working"
    INTEGRATION = "integration"
    CLOSURE = "closure"


class PacingController:
    """
    Controls the pacing of therapeutic narrative experiences to optimize
    engagement, learning retention, and therapeutic effectiveness.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Pacing configuration
        self.pacing_rules: dict[SessionPhase, dict[PacingDimension, PacingStrategy]] = {}
        self.emotional_pacing_adjustments: dict[
            EmotionalState, dict[PacingDimension, PacingStrategy]
        ] = {}
        self.optimal_durations: dict[SceneType, tuple[int, int]] = {}  # (min, max) seconds
        self.fatigue_thresholds: dict[str, int] = {}

        logger.info("PacingController initialized")

    async def initialize(self) -> bool:
        """Initialize pacing control rules and thresholds."""
        try:
            await self._load_pacing_rules()
            await self._load_emotional_adjustments()
            await self._load_optimal_durations()
            await self._load_fatigue_thresholds()

            logger.info("PacingController initialization completed")
            return True

        except Exception as e:
            logger.error(f"PacingController initialization failed: {e}")
            return False

    async def analyze_session_pacing(self, session_state: SessionState) -> dict[str, Any]:
        """
        Analyze current session pacing and recommend adjustments.

        Args:
            session_state: Current session state

        Returns:
            Dictionary with pacing analysis and recommendations
        """
        try:
            logger.info(f"Analyzing session pacing for session {session_state.session_id}")

            # Determine current session phase
            current_phase = await self._determine_session_phase(session_state)

            # Analyze pacing metrics
            pacing_metrics = await self._calculate_pacing_metrics(session_state)

            # Check for fatigue indicators
            fatigue_level = await self._assess_fatigue_level(session_state)

            # Determine needed adjustments
            adjustments = await self._determine_pacing_adjustments(
                current_phase,
                pacing_metrics,
                fatigue_level,
                session_state.emotional_state,
            )

            analysis = {
                "current_phase": current_phase,
                "pacing_metrics": pacing_metrics,
                "fatigue_level": fatigue_level,
                "recommended_adjustments": adjustments,
                "needs_acceleration": adjustments.get("overall_strategy")
                == PacingStrategy.ACCELERATE,
                "needs_deceleration": adjustments.get("overall_strategy")
                == PacingStrategy.DECELERATE,
                "needs_pause": adjustments.get("overall_strategy") == PacingStrategy.PAUSE,
            }

            logger.info(f"Session pacing analysis completed: {adjustments.get('overall_strategy')}")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze session pacing: {e}")
            return {}

    async def apply_pacing_adjustments(
        self, scene: Scene, pacing_analysis: dict[str, Any]
    ) -> Scene:
        """
        Apply pacing adjustments to a scene based on analysis.

        Args:
            scene: The scene to adjust
            pacing_analysis: Pacing analysis from analyze_session_pacing

        Returns:
            Scene with pacing adjustments applied
        """
        try:
            logger.info(f"Applying pacing adjustments to scene {scene.scene_id}")

            adjustments = pacing_analysis.get("recommended_adjustments", {})
            adjusted_scene = Scene(**scene.model_dump())

            # Apply adjustments for each dimension
            for dimension, strategy in adjustments.items():
                if dimension != "overall_strategy":
                    adjusted_scene = await self._apply_dimension_adjustment(
                        adjusted_scene, dimension, strategy
                    )

            # Apply overall pacing strategy
            overall_strategy = adjustments.get("overall_strategy", PacingStrategy.MAINTAIN)
            adjusted_scene = await self._apply_overall_pacing_strategy(
                adjusted_scene, overall_strategy
            )

            logger.info(f"Applied pacing adjustments: {overall_strategy}")
            return adjusted_scene

        except Exception as e:
            logger.error(f"Failed to apply pacing adjustments: {e}")
            return scene

    async def optimize_scene_duration(self, scene: Scene, session_context: dict[str, Any]) -> Scene:
        """
        Optimize scene duration based on type and context.

        Args:
            scene: The scene to optimize
            session_context: Context about the current session

        Returns:
            Scene with optimized duration
        """
        try:
            # Get optimal duration range for scene type
            duration_range = self.optimal_durations.get(scene.scene_type, (180, 600))
            min_duration, max_duration = duration_range

            # Adjust based on session context
            fatigue_level = session_context.get("fatigue_level", 0.0)
            emotional_state = session_context.get("emotional_state", EmotionalState.CALM)

            # Calculate optimal duration
            if fatigue_level > 0.7:
                # High fatigue - use shorter duration
                optimal_duration = min_duration
            elif emotional_state in [
                EmotionalState.ANXIOUS,
                EmotionalState.OVERWHELMED,
            ]:
                # Stressed states - use shorter duration
                optimal_duration = int(min_duration * 1.2)
            elif emotional_state == EmotionalState.ENGAGED:
                # Engaged state - can use longer duration
                optimal_duration = int(max_duration * 0.8)
            else:
                # Default to middle of range
                optimal_duration = (min_duration + max_duration) // 2

            scene.estimated_duration = optimal_duration
            logger.info(f"Optimized scene duration to {optimal_duration} seconds")
            return scene

        except Exception as e:
            logger.error(f"Failed to optimize scene duration: {e}")
            return scene

    # Initialization Methods
    async def _load_pacing_rules(self) -> None:
        """Load pacing rules for different session phases."""
        self.pacing_rules = {
            SessionPhase.OPENING: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.DECELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.DECELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.DECELERATE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.MAINTAIN,
                PacingDimension.INTERACTION_FREQUENCY: PacingStrategy.DECELERATE,
            },
            SessionPhase.ENGAGEMENT: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.ACCELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.MAINTAIN,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.MAINTAIN,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.ACCELERATE,
                PacingDimension.INTERACTION_FREQUENCY: PacingStrategy.ACCELERATE,
            },
            SessionPhase.WORKING: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.MAINTAIN,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.ACCELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.MAINTAIN,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.MAINTAIN,
                PacingDimension.INTERACTION_FREQUENCY: PacingStrategy.MAINTAIN,
            },
            SessionPhase.INTEGRATION: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.DECELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.MAINTAIN,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.DECELERATE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.DECELERATE,
                PacingDimension.INTERACTION_FREQUENCY: PacingStrategy.DECELERATE,
            },
            SessionPhase.CLOSURE: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.DECELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.DECELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.DECELERATE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.DECELERATE,
                PacingDimension.INTERACTION_FREQUENCY: PacingStrategy.DECELERATE,
            },
        }

    async def _load_emotional_adjustments(self) -> None:
        """Load emotional state adjustments for pacing."""
        self.emotional_pacing_adjustments = {
            EmotionalState.CALM: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.MAINTAIN,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.MAINTAIN,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.MAINTAIN,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.MAINTAIN,
            },
            EmotionalState.ENGAGED: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.ACCELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.ACCELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.MAINTAIN,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.ACCELERATE,
            },
            EmotionalState.ANXIOUS: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.DECELERATE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.DECELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.DECELERATE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.DECELERATE,
            },
            EmotionalState.OVERWHELMED: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.PAUSE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.DECELERATE,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.PAUSE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.PAUSE,
            },
            EmotionalState.DISTRESSED: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.PAUSE,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.RESET,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.PAUSE,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.RESET,
            },
            EmotionalState.CRISIS: {
                PacingDimension.NARRATIVE_FLOW: PacingStrategy.RESET,
                PacingDimension.THERAPEUTIC_INTENSITY: PacingStrategy.RESET,
                PacingDimension.COGNITIVE_LOAD: PacingStrategy.RESET,
                PacingDimension.EMOTIONAL_PACING: PacingStrategy.RESET,
            },
        }

    async def _load_optimal_durations(self) -> None:
        """Load optimal duration ranges for different scene types."""
        self.optimal_durations = {
            SceneType.INTRODUCTION: (120, 300),  # 2-5 minutes
            SceneType.EXPLORATION: (180, 480),  # 3-8 minutes
            SceneType.THERAPEUTIC: (240, 600),  # 4-10 minutes
            SceneType.CHALLENGE: (300, 720),  # 5-12 minutes
            SceneType.REFLECTION: (180, 420),  # 3-7 minutes
            SceneType.RESOLUTION: (120, 360),  # 2-6 minutes
        }

    async def _load_fatigue_thresholds(self) -> None:
        """Load fatigue thresholds for different metrics."""
        self.fatigue_thresholds = {
            "session_duration": 1800,  # 30 minutes
            "choice_count": 15,  # 15 choices
            "cognitive_load_time": 1200,  # 20 minutes of high cognitive load
            "emotional_intensity_time": 900,  # 15 minutes of high emotional intensity
        }

    # Analysis Methods
    async def _determine_session_phase(self, session_state: SessionState) -> SessionPhase:
        """Determine the current phase of the therapeutic session."""
        choice_count = len(session_state.choice_history)
        session_duration = choice_count * 300  # Estimate based on choices

        if choice_count <= 2:
            return SessionPhase.OPENING
        if choice_count <= 5:
            return SessionPhase.ENGAGEMENT
        if session_duration < 1200:  # Less than 20 minutes
            return SessionPhase.WORKING
        if session_duration < 1800:  # Less than 30 minutes
            return SessionPhase.INTEGRATION
        return SessionPhase.CLOSURE

    async def _calculate_pacing_metrics(self, session_state: SessionState) -> dict[str, float]:
        """Calculate current pacing metrics for the session."""
        choice_count = len(session_state.choice_history)
        estimated_duration = choice_count * 300  # Rough estimate

        return {
            "session_duration": estimated_duration,
            "choice_frequency": choice_count
            / max(estimated_duration / 60, 1),  # Choices per minute
            "therapeutic_intensity": self._calculate_therapeutic_intensity(session_state),
            "cognitive_load": self._calculate_cognitive_load(session_state),
            "emotional_engagement": self._calculate_emotional_engagement(session_state),
            "narrative_momentum": self._calculate_narrative_momentum(session_state),
        }

    async def _assess_fatigue_level(self, session_state: SessionState) -> float:
        """Assess current fatigue level (0.0-1.0)."""
        fatigue_score = 0.0

        # Session duration fatigue
        choice_count = len(session_state.choice_history)
        estimated_duration = choice_count * 300

        if estimated_duration > self.fatigue_thresholds["session_duration"]:
            duration_fatigue = min(
                (estimated_duration - self.fatigue_thresholds["session_duration"]) / 1800,
                1.0,
            )
            fatigue_score += duration_fatigue * 0.4

        # Choice count fatigue
        if choice_count > self.fatigue_thresholds["choice_count"]:
            choice_fatigue = min((choice_count - self.fatigue_thresholds["choice_count"]) / 10, 1.0)
            fatigue_score += choice_fatigue * 0.3

        # Emotional state fatigue
        if session_state.emotional_state in [
            EmotionalState.OVERWHELMED,
            EmotionalState.DISTRESSED,
        ]:
            fatigue_score += 0.3

        return min(fatigue_score, 1.0)

    async def _determine_pacing_adjustments(
        self,
        current_phase: SessionPhase,
        pacing_metrics: dict[str, float],
        fatigue_level: float,
        emotional_state: EmotionalState,
    ) -> dict[str, PacingStrategy]:
        """Determine needed pacing adjustments."""
        # Start with phase-based rules
        base_adjustments = self.pacing_rules.get(current_phase, {}).copy()

        # Apply emotional state adjustments
        emotional_adjustments = self.emotional_pacing_adjustments.get(emotional_state, {})
        for dimension, strategy in emotional_adjustments.items():
            if strategy in [PacingStrategy.PAUSE, PacingStrategy.RESET]:
                base_adjustments[dimension] = strategy  # Override with more urgent strategies

        # Apply fatigue adjustments
        if fatigue_level > 0.7:
            # High fatigue - decelerate everything
            for dimension in base_adjustments:
                if base_adjustments[dimension] == PacingStrategy.ACCELERATE:
                    base_adjustments[dimension] = PacingStrategy.MAINTAIN
                elif base_adjustments[dimension] == PacingStrategy.MAINTAIN:
                    base_adjustments[dimension] = PacingStrategy.DECELERATE

        # Determine overall strategy
        strategy_counts = {}
        for strategy in base_adjustments.values():
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        # Most common strategy becomes overall strategy
        overall_strategy = max(strategy_counts.keys(), key=lambda k: strategy_counts[k])
        base_adjustments["overall_strategy"] = overall_strategy

        return base_adjustments

    # Helper Calculation Methods
    def _calculate_therapeutic_intensity(self, session_state: SessionState) -> float:
        """Calculate current therapeutic intensity level."""
        # Base intensity on therapeutic context and goals
        goal_count = len(session_state.therapeutic_context.primary_goals)
        base_intensity = min(goal_count * 0.2, 0.8)

        # Adjust for emotional state
        if session_state.emotional_state == EmotionalState.ENGAGED:
            return min(base_intensity * 1.2, 1.0)
        if session_state.emotional_state in [
            EmotionalState.ANXIOUS,
            EmotionalState.OVERWHELMED,
        ]:
            return base_intensity * 0.7
        return base_intensity

    def _calculate_cognitive_load(self, session_state: SessionState) -> float:
        """Calculate current cognitive load level."""
        # Estimate based on choice complexity and frequency
        choice_count = len(session_state.choice_history)

        if choice_count == 0:
            return 0.3  # Default low load

        # Recent choices indicate current load
        recent_choices = session_state.choice_history[-3:]
        avg_complexity = sum(choice.get("complexity", 0.5) for choice in recent_choices) / len(
            recent_choices
        )

        return min(avg_complexity, 1.0)

    def _calculate_emotional_engagement(self, session_state: SessionState) -> float:
        """Calculate current emotional engagement level."""
        engagement_mapping = {
            EmotionalState.CALM: 0.5,
            EmotionalState.ENGAGED: 0.9,
            EmotionalState.ANXIOUS: 0.4,
            EmotionalState.OVERWHELMED: 0.2,
            EmotionalState.DISTRESSED: 0.1,
            EmotionalState.CRISIS: 0.0,
        }

        return engagement_mapping.get(session_state.emotional_state, 0.5)

    def _calculate_narrative_momentum(self, session_state: SessionState) -> float:
        """Calculate current narrative momentum."""
        choice_count = len(session_state.choice_history)

        if choice_count < 2:
            return 0.3  # Low momentum at start

        # Calculate momentum based on choice frequency and progression
        estimated_duration = choice_count * 300
        choice_frequency = choice_count / max(estimated_duration / 60, 1)

        # Normalize choice frequency to momentum score
        if choice_frequency > 0.3:  # More than 1 choice per 3 minutes
            return 0.8
        if choice_frequency > 0.2:  # More than 1 choice per 5 minutes
            return 0.6
        return 0.4

    # Adjustment Application Methods
    async def _apply_dimension_adjustment(
        self, scene: Scene, dimension: str, strategy: PacingStrategy
    ) -> Scene:
        """Apply pacing adjustment for a specific dimension."""
        if dimension == PacingDimension.NARRATIVE_FLOW:
            return await self._adjust_narrative_flow(scene, strategy)
        if dimension == PacingDimension.THERAPEUTIC_INTENSITY:
            return await self._adjust_therapeutic_intensity(scene, strategy)
        if dimension == PacingDimension.COGNITIVE_LOAD:
            return await self._adjust_cognitive_load(scene, strategy)
        if dimension == PacingDimension.EMOTIONAL_PACING:
            return await self._adjust_emotional_pacing(scene, strategy)
        if dimension == PacingDimension.INTERACTION_FREQUENCY:
            return await self._adjust_interaction_frequency(scene, strategy)
        return scene

    async def _apply_overall_pacing_strategy(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Apply overall pacing strategy to the scene."""
        if strategy == PacingStrategy.ACCELERATE:
            scene.narrative_content += " The energy of this moment invites you to engage more fully and explore with greater depth."
            scene.estimated_duration = int(scene.estimated_duration * 0.8)
        elif strategy == PacingStrategy.DECELERATE:
            scene.narrative_content += " Take your time here. There's no rush - allow yourself to fully absorb this experience."
            scene.estimated_duration = int(scene.estimated_duration * 1.3)
        elif strategy == PacingStrategy.PAUSE:
            scene.narrative_content += (
                " This is a moment to pause and breathe. Rest here as long as you need."
            )
            scene.estimated_duration = int(scene.estimated_duration * 1.5)
        elif strategy == PacingStrategy.RESET:
            scene.narrative_content = "You find yourself in a completely safe, calm space where you can reset and center yourself. Take all the time you need here."
            scene.estimated_duration = 300  # Fixed 5-minute reset

        return scene

    async def _adjust_narrative_flow(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Adjust narrative flow pacing."""
        if strategy == PacingStrategy.ACCELERATE:
            scene.narrative_content += " The story moves forward with engaging momentum."
        elif strategy == PacingStrategy.DECELERATE:
            scene.narrative_content += " The narrative unfolds at a gentle, contemplative pace."
        elif strategy == PacingStrategy.PAUSE:
            scene.narrative_content += " The story pauses here, giving you space to reflect."

        return scene

    async def _adjust_therapeutic_intensity(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Adjust therapeutic intensity pacing."""
        if strategy == PacingStrategy.ACCELERATE:
            if "self_awareness" not in scene.therapeutic_focus:
                scene.therapeutic_focus.append("self_awareness")
        elif strategy == PacingStrategy.DECELERATE:
            scene.therapeutic_focus = scene.therapeutic_focus[:2]  # Limit therapeutic focus
        elif strategy == PacingStrategy.RESET:
            scene.therapeutic_focus = ["safety", "grounding"]  # Reset to basics

        return scene

    async def _adjust_cognitive_load(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Adjust cognitive load pacing."""
        if strategy in (PacingStrategy.DECELERATE, PacingStrategy.PAUSE):
            # Simplify content
            sentences = scene.narrative_content.split(". ")
            if len(sentences) > 4:
                scene.narrative_content = ". ".join(sentences[:4]) + "."
            scene.learning_objectives = scene.learning_objectives[:2]

        return scene

    async def _adjust_emotional_pacing(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Adjust emotional pacing."""
        if strategy == PacingStrategy.DECELERATE:
            scene.emotional_tone = "gentle"
        elif strategy == PacingStrategy.PAUSE:
            scene.emotional_tone = "deeply_calming"
        elif strategy == PacingStrategy.RESET:
            scene.emotional_tone = "deeply_supportive"

        return scene

    async def _adjust_interaction_frequency(self, scene: Scene, strategy: PacingStrategy) -> Scene:
        """Adjust interaction frequency (affects future choice generation)."""
        # Store preference for choice generation
        if not hasattr(scene, "interaction_frequency_preference"):
            scene.interaction_frequency_preference = "standard"

        if strategy == PacingStrategy.ACCELERATE:
            scene.interaction_frequency_preference = "high"
        elif strategy == PacingStrategy.DECELERATE:
            scene.interaction_frequency_preference = "low"
        elif strategy == PacingStrategy.PAUSE:
            scene.interaction_frequency_preference = "minimal"

        return scene
