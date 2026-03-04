"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Adaptive_difficulty_engine]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Adaptive_difficulty_engine]]
Adaptive Difficulty Engine for Therapeutic Text Adventure

This module implements adaptive difficulty calibration that adjusts challenge levels
based on player performance, ensuring therapeutic engagement without overwhelming
or under-stimulating the player.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

from ..models.core import DifficultyLevel, Scene, SessionState
from ..models.interactions import ChoiceOutcome

logger = logging.getLogger(__name__)


class PerformanceLevel(StrEnum):
    """Player performance assessment levels."""

    STRUGGLING = "struggling"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    ABOVE_AVERAGE = "above_average"
    EXCELLING = "excelling"


class AdjustmentType(StrEnum):
    """Types of difficulty adjustments."""

    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"
    GRADUAL_INCREASE = "gradual_increase"
    GRADUAL_DECREASE = "gradual_decrease"


# Ordered difficulty levels for stepping up/down
_DIFFICULTY_ORDER: list[DifficultyLevel] = [
    DifficultyLevel.GENTLE,
    DifficultyLevel.STANDARD,
    DifficultyLevel.CHALLENGING,
    DifficultyLevel.INTENSIVE,
]


class AdaptiveDifficultyEngine:
    """
    Calibrates challenge levels based on player performance metrics,
    therapeutic engagement, and emotional state to maintain optimal
    difficulty for therapeutic effectiveness.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.performance_history: list[dict[str, Any]] = []
        self.adjustment_thresholds: dict[PerformanceLevel, AdjustmentType] = {}
        self.current_difficulty: DifficultyLevel = DifficultyLevel.STANDARD

        logger.info("AdaptiveDifficultyEngine initialized")

    async def initialize(self) -> bool:
        """Load adjustment thresholds and default mappings."""
        try:
            self.adjustment_thresholds = {
                PerformanceLevel.STRUGGLING: AdjustmentType.DECREASE,
                PerformanceLevel.BELOW_AVERAGE: AdjustmentType.GRADUAL_DECREASE,
                PerformanceLevel.AVERAGE: AdjustmentType.MAINTAIN,
                PerformanceLevel.ABOVE_AVERAGE: AdjustmentType.GRADUAL_INCREASE,
                PerformanceLevel.EXCELLING: AdjustmentType.INCREASE,
            }

            self.current_difficulty = DifficultyLevel(
                self.config.get("default_difficulty", DifficultyLevel.STANDARD)
            )

            logger.info("AdaptiveDifficultyEngine initialization completed")
            return True

        except Exception as e:
            logger.error(f"AdaptiveDifficultyEngine initialization failed: {e}")
            return False

    async def assess_performance(self, session_state: SessionState) -> PerformanceLevel:
        """
        Assess player performance from session metrics.

        Args:
            session_state: Current session state with metrics

        Returns:
            Assessed performance level
        """
        try:
            metrics = session_state.metrics
            total = metrics.total_choices_made
            if total == 0:
                return PerformanceLevel.AVERAGE

            therapeutic_ratio = (
                metrics.therapeutic_choices_made / total if total > 0 else 0.0
            )
            engagement = metrics.engagement_score
            effectiveness = metrics.therapeutic_effectiveness

            composite = (
                (therapeutic_ratio * 0.3) + (engagement * 0.4) + (effectiveness * 0.3)
            )

            if composite >= 0.8:
                return PerformanceLevel.EXCELLING
            if composite >= 0.6:
                return PerformanceLevel.ABOVE_AVERAGE
            if composite >= 0.4:
                return PerformanceLevel.AVERAGE
            if composite >= 0.2:
                return PerformanceLevel.BELOW_AVERAGE
            return PerformanceLevel.STRUGGLING

        except Exception as e:
            logger.warning(f"Performance assessment failed, defaulting to AVERAGE: {e}")
            return PerformanceLevel.AVERAGE

    async def adjust_difficulty(
        self, session_state: SessionState, scene: Scene
    ) -> Scene:
        """
        Adjust scene difficulty based on player performance.

        Args:
            session_state: Current session state
            scene: Scene to adjust

        Returns:
            Scene with adjusted difficulty
        """
        try:
            performance = await self.assess_performance(session_state)
            adjustment = self.adjustment_thresholds.get(
                performance, AdjustmentType.MAINTAIN
            )
            recommended = await self._apply_adjustment(
                scene.difficulty_level, adjustment
            )

            logger.info(
                f"Adjusting scene {scene.scene_id} difficulty: "
                f"{scene.difficulty_level} -> {recommended} "
                f"(performance={performance}, adjustment={adjustment})"
            )

            scene.difficulty_level = recommended
            self.current_difficulty = recommended
            return scene

        except Exception as e:
            logger.error(
                f"Difficulty adjustment failed for scene {scene.scene_id}: {e}"
            )
            return scene

    async def get_recommended_difficulty(
        self, session_state: SessionState
    ) -> DifficultyLevel:
        """
        Return the recommended difficulty level for the next scene.

        Args:
            session_state: Current session state

        Returns:
            Recommended difficulty level
        """
        try:
            performance = await self.assess_performance(session_state)
            adjustment = self.adjustment_thresholds.get(
                performance, AdjustmentType.MAINTAIN
            )
            return await self._apply_adjustment(self.current_difficulty, adjustment)

        except Exception as e:
            logger.warning(f"Recommendation failed, returning current difficulty: {e}")
            return self.current_difficulty

    async def record_performance(
        self, session_state: SessionState, choice_outcome: ChoiceOutcome
    ) -> None:
        """
        Record a performance data point from a player choice outcome.

        Args:
            session_state: Current session state
            choice_outcome: Outcome of the player's choice
        """
        try:
            entry: dict[str, Any] = {
                "session_id": session_state.session_id,
                "difficulty": str(self.current_difficulty),
                "outcome_type": choice_outcome.outcome_type,
                "therapeutic_progress": dict(choice_outcome.therapeutic_progress),
                "skills_developed": list(choice_outcome.skills_developed),
            }
            self.performance_history.append(entry)

            max_history = int(self.config.get("max_history", 200))
            if len(self.performance_history) > max_history:
                self.performance_history = self.performance_history[-max_history:]

            logger.info(f"Recorded performance for session {session_state.session_id}")

        except Exception as e:
            logger.error(f"Failed to record performance: {e}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _apply_adjustment(
        self, current: DifficultyLevel, adjustment: AdjustmentType
    ) -> DifficultyLevel:
        """Apply an adjustment type to a difficulty level."""
        idx = _DIFFICULTY_ORDER.index(current) if current in _DIFFICULTY_ORDER else 1

        if adjustment == AdjustmentType.INCREASE:
            idx = min(idx + 1, len(_DIFFICULTY_ORDER) - 1)
        elif adjustment == AdjustmentType.DECREASE:
            idx = max(idx - 1, 0)
        elif adjustment == AdjustmentType.GRADUAL_INCREASE:
            # Only step up if we have enough positive history
            recent_positive = sum(
                1
                for entry in self.performance_history[-5:]
                if entry.get("outcome_type") in ("success", "partial_success")
            )
            if recent_positive >= 3:
                idx = min(idx + 1, len(_DIFFICULTY_ORDER) - 1)
        elif adjustment == AdjustmentType.GRADUAL_DECREASE:
            recent_negative = sum(
                1
                for entry in self.performance_history[-5:]
                if entry.get("outcome_type") in ("failure", "challenge")
            )
            if recent_negative >= 3:
                idx = max(idx - 1, 0)

        return _DIFFICULTY_ORDER[idx]
