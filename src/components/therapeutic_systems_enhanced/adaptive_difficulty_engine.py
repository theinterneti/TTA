"""
Therapeutic AdaptiveDifficultyEngine Implementation

This module provides production-ready adaptive difficulty adjustment for the TTA
therapeutic platform, implementing dynamic difficulty calibration based on user
performance, therapeutic goals, and emotional safety considerations.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class DifficultyLevel(IntEnum):
    """Difficulty levels for therapeutic scenarios (1-6 scale)."""

    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    CHALLENGING = 4
    HARD = 5
    VERY_HARD = 6


class AdaptationStrategy(Enum):
    """Strategies for adapting difficulty based on user performance."""

    IMMEDIATE_ADJUSTMENT = "immediate_adjustment"
    GRADUAL_INCREASE = "gradual_increase"
    GRADUAL_DECREASE = "gradual_decrease"
    CONTEXTUAL_SUPPORT = "contextual_support"
    SKILL_BUILDING = "skill_building"
    ALTERNATIVE_PATH = "alternative_path"


class AdjustmentTrigger(Enum):
    """Triggers that cause difficulty adjustments."""

    POOR_PERFORMANCE = "poor_performance"
    EXCELLENT_PERFORMANCE = "excellent_performance"
    EMOTIONAL_DISTRESS = "emotional_distress"
    USER_REQUEST = "user_request"
    THERAPEUTIC_GOAL_PROGRESS = "therapeutic_goal_progress"
    ENGAGEMENT_DECLINE = "engagement_decline"


class PerformanceMetrics:
    """Container for user performance metrics."""

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.success_rate = 0.0
        self.response_time = 0.0
        self.engagement_level = 0.0
        self.emotional_stability = 0.0
        self.therapeutic_progress = 0.0
        self.current_difficulty = DifficultyLevel.MODERATE
        self.timestamp = datetime.utcnow()


class TherapeuticAdaptiveDifficultyEngine:
    """
    Production AdaptiveDifficultyEngine that provides dynamic difficulty adjustment
    based on user performance, therapeutic goals, and emotional safety.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic adaptive difficulty engine."""
        self.config = config or {}

        # Performance tracking
        self.user_performance_history = {}
        self.difficulty_adjustments = {}
        self.user_preferences = {}

        # Configuration parameters
        self.performance_window_minutes = self.config.get(
            "performance_window_minutes", 10
        )
        self.adjustment_threshold = self.config.get("adjustment_threshold", 0.3)
        self.min_samples_for_adjustment = self.config.get(
            "min_samples_for_adjustment", 3
        )
        self.max_adjustments_per_session = self.config.get(
            "max_adjustments_per_session", 5
        )

        # Adaptation strategy configurations
        self.adaptation_strategies = {
            AdaptationStrategy.IMMEDIATE_ADJUSTMENT: {
                "adjustment_rate": 1.0,
                "therapeutic_focus": "crisis_management",
                "description": "Immediate difficulty change for crisis situations",
            },
            AdaptationStrategy.GRADUAL_INCREASE: {
                "adjustment_rate": 0.5,
                "therapeutic_focus": "skill_building",
                "description": "Gradual increase to build confidence",
            },
            AdaptationStrategy.GRADUAL_DECREASE: {
                "adjustment_rate": -0.5,
                "therapeutic_focus": "stress_reduction",
                "description": "Gradual decrease to reduce overwhelm",
            },
            AdaptationStrategy.CONTEXTUAL_SUPPORT: {
                "adjustment_rate": 0.0,
                "therapeutic_focus": "emotional_support",
                "description": "Provide support without changing difficulty",
            },
            AdaptationStrategy.SKILL_BUILDING: {
                "adjustment_rate": 0.0,
                "therapeutic_focus": "competency_development",
                "description": "Focus on skill development at current level",
            },
            AdaptationStrategy.ALTERNATIVE_PATH: {
                "adjustment_rate": "variable",
                "therapeutic_focus": "personalization",
                "description": "Offer alternative approaches to same goals",
            },
        }

        # Performance metrics
        self.metrics = {
            "assessments_performed": 0,
            "difficulty_adjustments": 0,
            "user_requests_processed": 0,
            "performance_improvements": 0,
            "therapeutic_goals_achieved": 0,
        }

        logger.info("TherapeuticAdaptiveDifficultyEngine initialized")

    async def initialize(self):
        """Initialize the adaptive difficulty engine."""
        # Any async initialization can go here
        logger.info("TherapeuticAdaptiveDifficultyEngine initialization complete")

    async def assess_user_capability(
        self,
        user_id: str,
        session_id: str | None = None,
        therapeutic_goals: list[str] | None = None,
        user_history: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Assess user capability and determine appropriate difficulty level.

        This method provides the interface expected by E2E tests for initial
        difficulty assessment and calibration.

        Args:
            user_id: Unique identifier for the user
            session_id: Current session identifier
            therapeutic_goals: List of therapeutic goals for the user
            user_history: Historical user performance data

        Returns:
            Dictionary containing capability assessment with keys:
            - difficulty_level: Recommended difficulty level
            - capability_score: Float between 0-1 indicating user capability
            - assessment_reasoning: Explanation of the assessment
        """
        try:
            start_time = datetime.utcnow()

            # Get user's performance history
            performance_history = self.user_performance_history.get(user_id, [])

            # Calculate baseline capability score
            capability_score = self._calculate_baseline_capability(
                user_id, performance_history, user_history
            )

            # Determine appropriate difficulty level
            difficulty_level = self._map_capability_to_difficulty(capability_score)

            # Generate assessment reasoning
            assessment_reasoning = self._generate_assessment_reasoning(
                capability_score, difficulty_level, therapeutic_goals
            )

            # Update metrics
            self.metrics["assessments_performed"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.debug(
                f"Assessed user capability for {user_id} in {processing_time.total_seconds():.3f}s"
            )

            return {
                "difficulty_level": difficulty_level.name,
                "capability_score": capability_score,
                "assessment_reasoning": assessment_reasoning,
                "recommended_strategies": self._recommend_strategies(capability_score),
                "processing_time": processing_time.total_seconds(),
                "assessment_id": str(uuid4()),
            }

        except Exception as e:
            logger.error(f"Error assessing user capability for {user_id}: {e}")

            # Return safe fallback
            return {
                "difficulty_level": DifficultyLevel.MODERATE.name,
                "capability_score": 0.5,
                "assessment_reasoning": "Default assessment due to error",
                "error": str(e),
            }

    async def adapt_difficulty(
        self,
        user_id: str,
        performance_data: dict[str, Any],
        session_context: Any | None = None,
        emotional_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Adapt difficulty based on user performance and emotional state.

        This method provides the interface expected by E2E tests for dynamic
        difficulty adjustment based on real-time performance data.

        Args:
            user_id: Unique identifier for the user
            performance_data: Current performance metrics
            session_context: Current session context
            emotional_state: Current emotional state from EmotionalSafetySystem

        Returns:
            Dictionary containing adaptation results with keys:
            - new_difficulty_level: Adjusted difficulty level
            - adaptation_reason: Explanation for the adjustment
            - strategy_applied: Strategy used for adaptation
        """
        try:
            start_time = datetime.utcnow()

            # Create performance metrics object
            metrics = self._create_performance_metrics(user_id, performance_data)

            # Analyze performance trends
            performance_trend = self._analyze_performance_trend(user_id, metrics)

            # Determine if adjustment is needed
            adjustment_trigger = self._determine_adjustment_trigger(
                metrics, performance_trend, emotional_state
            )

            if adjustment_trigger is None:
                # No adjustment needed
                current_difficulty = self._get_current_difficulty(user_id)
                processing_time = datetime.utcnow() - start_time
                return {
                    "new_difficulty_level": current_difficulty.name,
                    "adaptation_reason": "Performance stable, no adjustment needed",
                    "strategy_applied": AdaptationStrategy.CONTEXTUAL_SUPPORT.value,
                    "adjustment_made": False,
                    "processing_time": processing_time.total_seconds(),
                }

            # Select adaptation strategy
            strategy = self._select_adaptation_strategy(
                metrics, adjustment_trigger, emotional_state
            )

            # Calculate new difficulty level
            current_difficulty = self._get_current_difficulty(user_id)
            new_difficulty = self._calculate_new_difficulty(
                current_difficulty, strategy, metrics
            )

            # Apply the adjustment
            self._apply_difficulty_adjustment(user_id, new_difficulty, strategy)

            # Generate adaptation reasoning
            adaptation_reason = self._generate_adaptation_reasoning(
                adjustment_trigger, strategy, current_difficulty, new_difficulty
            )

            # Update metrics
            self.metrics["difficulty_adjustments"] += 1
            if new_difficulty > current_difficulty:
                self.metrics["performance_improvements"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Adapted difficulty for user {user_id}: {current_difficulty.name} -> {new_difficulty.name} "
                f"(Strategy: {strategy.value}, Trigger: {adjustment_trigger.value})"
            )

            return {
                "new_difficulty_level": new_difficulty.name,
                "adaptation_reason": adaptation_reason,
                "strategy_applied": strategy.value,
                "adjustment_made": True,
                "previous_difficulty": current_difficulty.name,
                "trigger": adjustment_trigger.value,
                "processing_time": processing_time.total_seconds(),
                "adaptation_id": str(uuid4()),
            }

        except Exception as e:
            logger.error(f"Error adapting difficulty for user {user_id}: {e}")

            # Return safe fallback
            current_difficulty = self._get_current_difficulty(user_id)
            return {
                "new_difficulty_level": current_difficulty.name,
                "adaptation_reason": f"Error during adaptation: {str(e)}",
                "strategy_applied": AdaptationStrategy.CONTEXTUAL_SUPPORT.value,
                "adjustment_made": False,
                "error": str(e),
            }

    def _calculate_baseline_capability(
        self,
        user_id: str,
        performance_history: list[Any],
        user_history: dict[str, Any] | None,
    ) -> float:
        """Calculate baseline capability score for the user."""
        if not performance_history and not user_history:
            return 0.5  # Default moderate capability

        # Use performance history if available
        if performance_history:
            recent_performance = performance_history[-5:]  # Last 5 sessions
            success_rates = [
                p.success_rate for p in recent_performance if hasattr(p, "success_rate")
            ]
            if success_rates:
                return sum(success_rates) / len(success_rates)

        # Use user history if available
        if user_history:
            previous_capability = user_history.get("capability_score", 0.5)
            therapeutic_progress = user_history.get("therapeutic_progress", 0.0)
            return min(1.0, previous_capability + (therapeutic_progress * 0.1))

        return 0.5

    def _map_capability_to_difficulty(self, capability_score: float) -> DifficultyLevel:
        """Map capability score to appropriate difficulty level."""
        if capability_score >= 0.9:
            return DifficultyLevel.VERY_HARD
        elif capability_score >= 0.75:
            return DifficultyLevel.HARD
        elif capability_score >= 0.6:
            return DifficultyLevel.CHALLENGING
        elif capability_score >= 0.4:
            return DifficultyLevel.MODERATE
        elif capability_score >= 0.25:
            return DifficultyLevel.EASY
        else:
            return DifficultyLevel.VERY_EASY

    def _generate_assessment_reasoning(
        self,
        capability_score: float,
        difficulty_level: DifficultyLevel,
        therapeutic_goals: list[str] | None,
    ) -> str:
        """Generate human-readable reasoning for the assessment."""
        base_reasoning = f"Based on capability score of {capability_score:.2f}, "

        if capability_score >= 0.75:
            base_reasoning += "user demonstrates high competency and can handle challenging scenarios."
        elif capability_score >= 0.5:
            base_reasoning += "user shows moderate competency with room for growth."
        else:
            base_reasoning += "user needs supportive environment to build confidence."

        if therapeutic_goals:
            primary_goal = therapeutic_goals[0].replace("_", " ")
            base_reasoning += (
                f" Difficulty calibrated for {primary_goal} therapeutic focus."
            )

        return base_reasoning

    def _recommend_strategies(self, capability_score: float) -> list[str]:
        """Recommend adaptation strategies based on capability."""
        strategies = []

        if capability_score < 0.3:
            strategies.extend(["gradual_decrease", "contextual_support"])
        elif capability_score < 0.6:
            strategies.extend(["skill_building", "contextual_support"])
        elif capability_score < 0.8:
            strategies.extend(["gradual_increase", "skill_building"])
        else:
            strategies.extend(["gradual_increase", "alternative_path"])

        return strategies

    def _create_performance_metrics(
        self, user_id: str, performance_data: dict[str, Any]
    ) -> PerformanceMetrics:
        """Create performance metrics object from performance data."""
        metrics = PerformanceMetrics(
            user_id, performance_data.get("session_id", "unknown")
        )

        metrics.success_rate = performance_data.get("success_rate", 0.5)
        metrics.response_time = performance_data.get("response_time", 30.0)
        metrics.engagement_level = performance_data.get("engagement_level", 0.5)
        metrics.emotional_stability = performance_data.get("emotional_stability", 0.5)
        metrics.therapeutic_progress = performance_data.get("therapeutic_progress", 0.0)
        metrics.current_difficulty = self._get_current_difficulty(user_id)

        return metrics

    def _analyze_performance_trend(
        self, user_id: str, current_metrics: PerformanceMetrics
    ) -> str:
        """Analyze performance trend over recent sessions."""
        history = self.user_performance_history.get(user_id, [])

        if len(history) < 2:
            return "insufficient_data"

        # Look at last 3 sessions
        recent_sessions = history[-3:]
        success_rates = [session.success_rate for session in recent_sessions]

        if len(success_rates) >= 2:
            if all(
                success_rates[i] < success_rates[i + 1]
                for i in range(len(success_rates) - 1)
            ):
                return "improving"
            elif all(
                success_rates[i] > success_rates[i + 1]
                for i in range(len(success_rates) - 1)
            ):
                return "declining"
            else:
                return "stable"

        return "stable"

    def _determine_adjustment_trigger(
        self,
        metrics: PerformanceMetrics,
        trend: str,
        emotional_state: dict[str, Any] | None,
    ) -> AdjustmentTrigger | None:
        """Determine if difficulty adjustment is needed and why."""
        # Check emotional distress first (highest priority)
        if emotional_state and emotional_state.get("crisis_detected", False):
            return AdjustmentTrigger.EMOTIONAL_DISTRESS

        # Check for poor performance
        if metrics.success_rate < 0.3 or trend == "declining":
            return AdjustmentTrigger.POOR_PERFORMANCE

        # Check for excellent performance
        if metrics.success_rate > 0.8 and metrics.engagement_level > 0.7:
            return AdjustmentTrigger.EXCELLENT_PERFORMANCE

        # Check for engagement decline
        if metrics.engagement_level < 0.4:
            return AdjustmentTrigger.ENGAGEMENT_DECLINE

        # Check therapeutic progress
        if metrics.therapeutic_progress > 0.8:
            return AdjustmentTrigger.THERAPEUTIC_GOAL_PROGRESS

        return None  # No adjustment needed

    def _select_adaptation_strategy(
        self,
        metrics: PerformanceMetrics,
        trigger: AdjustmentTrigger,
        emotional_state: dict[str, Any] | None,
    ) -> AdaptationStrategy:
        """Select appropriate adaptation strategy based on trigger and context."""
        if trigger == AdjustmentTrigger.EMOTIONAL_DISTRESS:
            return AdaptationStrategy.IMMEDIATE_ADJUSTMENT
        elif trigger == AdjustmentTrigger.POOR_PERFORMANCE:
            if metrics.emotional_stability < 0.4:
                return AdaptationStrategy.CONTEXTUAL_SUPPORT
            else:
                return AdaptationStrategy.GRADUAL_DECREASE
        elif trigger == AdjustmentTrigger.EXCELLENT_PERFORMANCE:
            if metrics.engagement_level >= 0.8:
                return AdaptationStrategy.GRADUAL_INCREASE
            else:
                return AdaptationStrategy.SKILL_BUILDING
        elif trigger == AdjustmentTrigger.ENGAGEMENT_DECLINE:
            return AdaptationStrategy.ALTERNATIVE_PATH
        elif trigger == AdjustmentTrigger.THERAPEUTIC_GOAL_PROGRESS:
            return AdaptationStrategy.GRADUAL_INCREASE
        else:
            return AdaptationStrategy.CONTEXTUAL_SUPPORT

    def _get_current_difficulty(self, user_id: str) -> DifficultyLevel:
        """Get current difficulty level for the user."""
        if user_id in self.difficulty_adjustments:
            return self.difficulty_adjustments[user_id]["current_difficulty"]
        return DifficultyLevel.MODERATE  # Default

    def _calculate_new_difficulty(
        self,
        current_difficulty: DifficultyLevel,
        strategy: AdaptationStrategy,
        metrics: PerformanceMetrics,
    ) -> DifficultyLevel:
        """Calculate new difficulty level based on strategy."""
        strategy_config = self.adaptation_strategies[strategy]
        adjustment_rate = strategy_config["adjustment_rate"]

        if adjustment_rate == 0.0:
            return current_difficulty  # No change
        elif adjustment_rate == "variable":
            # Alternative path - choose based on performance
            if metrics.success_rate < 0.5:
                return max(
                    DifficultyLevel.VERY_EASY,
                    DifficultyLevel(current_difficulty.value - 1),
                )
            else:
                return min(
                    DifficultyLevel.VERY_HARD,
                    DifficultyLevel(current_difficulty.value + 1),
                )
        else:
            # Calculate adjustment
            adjustment = int(adjustment_rate * 2)  # Scale to difficulty range
            new_value = current_difficulty.value + adjustment
            new_value = max(1, min(6, new_value))  # Clamp to valid range
            return DifficultyLevel(new_value)

    def _apply_difficulty_adjustment(
        self,
        user_id: str,
        new_difficulty: DifficultyLevel,
        strategy: AdaptationStrategy,
    ):
        """Apply the difficulty adjustment for the user."""
        if user_id not in self.difficulty_adjustments:
            self.difficulty_adjustments[user_id] = {
                "adjustments": [],
                "current_difficulty": DifficultyLevel.MODERATE,
            }

        adjustment_record = {
            "timestamp": datetime.utcnow(),
            "previous_difficulty": self.difficulty_adjustments[user_id][
                "current_difficulty"
            ],
            "new_difficulty": new_difficulty,
            "strategy": strategy,
            "adjustment_id": str(uuid4()),
        }

        self.difficulty_adjustments[user_id]["adjustments"].append(adjustment_record)
        self.difficulty_adjustments[user_id]["current_difficulty"] = new_difficulty

        # Keep only recent adjustments (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.difficulty_adjustments[user_id]["adjustments"] = [
            adj
            for adj in self.difficulty_adjustments[user_id]["adjustments"]
            if adj["timestamp"] > cutoff_time
        ]

    def _generate_adaptation_reasoning(
        self,
        trigger: AdjustmentTrigger,
        strategy: AdaptationStrategy,
        old_difficulty: DifficultyLevel,
        new_difficulty: DifficultyLevel,
    ) -> str:
        """Generate human-readable reasoning for the adaptation."""
        trigger_descriptions = {
            AdjustmentTrigger.POOR_PERFORMANCE: "performance below expectations",
            AdjustmentTrigger.EXCELLENT_PERFORMANCE: "consistently excellent performance",
            AdjustmentTrigger.EMOTIONAL_DISTRESS: "emotional distress detected",
            AdjustmentTrigger.ENGAGEMENT_DECLINE: "declining engagement levels",
            AdjustmentTrigger.THERAPEUTIC_GOAL_PROGRESS: "significant therapeutic progress",
        }

        strategy_descriptions = {
            AdaptationStrategy.IMMEDIATE_ADJUSTMENT: "immediate adjustment for safety",
            AdaptationStrategy.GRADUAL_INCREASE: "gradual increase to maintain challenge",
            AdaptationStrategy.GRADUAL_DECREASE: "gradual decrease to reduce overwhelm",
            AdaptationStrategy.CONTEXTUAL_SUPPORT: "additional support without difficulty change",
            AdaptationStrategy.SKILL_BUILDING: "focus on skill development",
            AdaptationStrategy.ALTERNATIVE_PATH: "alternative approach to same goals",
        }

        trigger_desc = trigger_descriptions.get(trigger, "performance analysis")
        strategy_desc = strategy_descriptions.get(strategy, "adaptive adjustment")

        if old_difficulty == new_difficulty:
            return f"Due to {trigger_desc}, applying {strategy_desc} while maintaining current difficulty level."
        else:
            direction = "increased" if new_difficulty > old_difficulty else "decreased"
            return f"Due to {trigger_desc}, difficulty {direction} from {old_difficulty.name} to {new_difficulty.name} using {strategy_desc}."

    async def get_difficulty_calibration(
        self, user_id: str, session_context: Any | None = None
    ) -> dict[str, Any]:
        """
        Get current difficulty calibration for the user.

        Args:
            user_id: Unique identifier for the user
            session_context: Current session context

        Returns:
            Dictionary containing current difficulty calibration information
        """
        try:
            current_difficulty = self._get_current_difficulty(user_id)
            adjustment_history = self.difficulty_adjustments.get(user_id, {}).get(
                "adjustments", []
            )

            # Calculate calibration confidence
            calibration_confidence = self._calculate_calibration_confidence(user_id)

            return {
                "difficulty_calibrated": True,
                "current_difficulty": current_difficulty.name,
                "calibration_confidence": calibration_confidence,
                "recent_adjustments": len(adjustment_history),
                "last_adjustment": (
                    adjustment_history[-1]["timestamp"].isoformat()
                    if adjustment_history
                    else None
                ),
                "calibration_id": str(uuid4()),
            }

        except Exception as e:
            logger.error(
                f"Error getting difficulty calibration for user {user_id}: {e}"
            )
            return {
                "difficulty_calibrated": False,
                "error": str(e),
            }

    def _calculate_calibration_confidence(self, user_id: str) -> float:
        """Calculate confidence in current difficulty calibration."""
        history = self.user_performance_history.get(user_id, [])
        adjustments = self.difficulty_adjustments.get(user_id, {}).get(
            "adjustments", []
        )

        if not history:
            return 0.5  # Default confidence

        # Higher confidence with more stable performance
        recent_performance = history[-5:] if len(history) >= 5 else history
        if recent_performance:
            success_rates = [
                p.success_rate for p in recent_performance if hasattr(p, "success_rate")
            ]
            if success_rates:
                variance = sum((sr - 0.6) ** 2 for sr in success_rates) / len(
                    success_rates
                )
                stability_score = max(0.0, 1.0 - variance)

                # Reduce confidence if too many recent adjustments
                adjustment_penalty = min(0.3, len(adjustments) * 0.1)

                return max(0.1, min(1.0, stability_score - adjustment_penalty))

        return 0.5

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the adaptive difficulty engine."""
        try:
            return {
                "status": "healthy",
                "difficulty_levels_configured": len(DifficultyLevel),
                "adaptation_strategies_available": len(self.adaptation_strategies),
                "performance_window_minutes": self.performance_window_minutes,
                "adjustment_threshold": self.adjustment_threshold,
                "users_tracked": len(self.user_performance_history),
                "active_adjustments": len(self.difficulty_adjustments),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in adaptive difficulty engine health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get adaptive difficulty engine metrics."""
        # Calculate success rate of adjustments
        total_adjustments = self.metrics["difficulty_adjustments"]
        successful_adjustments = self.metrics["performance_improvements"]
        adjustment_success_rate = 0.0
        if total_adjustments > 0:
            adjustment_success_rate = successful_adjustments / total_adjustments

        return {
            **self.metrics,
            "adjustment_success_rate": adjustment_success_rate,
            "users_tracked": len(self.user_performance_history),
            "active_difficulty_adjustments": len(self.difficulty_adjustments),
            "difficulty_levels_available": len(DifficultyLevel),
            "adaptation_strategies_available": len(self.adaptation_strategies),
        }


# Alias for backward compatibility
AdaptiveDifficultyEngine = TherapeuticAdaptiveDifficultyEngine
