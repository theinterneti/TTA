"""
Adaptive Difficulty Engine for Therapeutic Narrative Engine

This module provides intelligent difficulty calibration, performance monitoring,
and adaptive challenge adjustment for therapeutic text adventures.
"""

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.services.session_state import SessionState

from .events import EventBus, EventType, NarrativeEvent

logger = logging.getLogger(__name__)


class DifficultyLevel(IntEnum):
    """Difficulty levels for adaptive calibration."""

    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    CHALLENGING = 4
    HARD = 5
    VERY_HARD = 6


class PerformanceMetric(str, Enum):
    """Performance metrics for difficulty assessment."""

    CHOICE_SUCCESS_RATE = "choice_success_rate"
    THERAPEUTIC_PROGRESS = "therapeutic_progress"
    EMOTIONAL_STABILITY = "emotional_stability"
    ENGAGEMENT_LEVEL = "engagement_level"
    COMPLETION_RATE = "completion_rate"
    TIME_TO_DECISION = "time_to_decision"
    HELP_SEEKING_FREQUENCY = "help_seeking_frequency"


class AdjustmentTrigger(str, Enum):
    """Triggers for difficulty adjustment."""

    POOR_PERFORMANCE = "poor_performance"
    EXCELLENT_PERFORMANCE = "excellent_performance"
    EMOTIONAL_DISTRESS = "emotional_distress"
    USER_REQUEST = "user_request"
    THERAPEUTIC_GOAL_CHANGE = "therapeutic_goal_change"
    PATTERN_RECOGNITION = "pattern_recognition"


class AdaptationStrategy(str, Enum):
    """Strategies for difficulty adaptation."""

    GRADUAL_INCREASE = "gradual_increase"
    GRADUAL_DECREASE = "gradual_decrease"
    IMMEDIATE_ADJUSTMENT = "immediate_adjustment"
    CONTEXTUAL_SUPPORT = "contextual_support"
    ALTERNATIVE_PATH = "alternative_path"
    SKILL_BUILDING = "skill_building"


@dataclass
class PerformanceSnapshot:
    """Snapshot of user performance at a point in time."""

    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""

    # Performance metrics
    success_rate: float = 0.0
    therapeutic_progress: float = 0.0
    emotional_stability: float = 0.0
    engagement_level: float = 0.0
    completion_rate: float = 0.0
    average_decision_time: float = 0.0
    help_requests: int = 0

    # Context
    current_difficulty: DifficultyLevel = DifficultyLevel.MODERATE
    recent_choices: list[str] = field(default_factory=list)
    therapeutic_goals: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0


@dataclass
class DifficultyAdjustment:
    """Record of a difficulty adjustment."""

    adjustment_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""

    # Adjustment details
    from_difficulty: DifficultyLevel = DifficultyLevel.MODERATE
    to_difficulty: DifficultyLevel = DifficultyLevel.MODERATE
    trigger: AdjustmentTrigger = AdjustmentTrigger.POOR_PERFORMANCE
    strategy: AdaptationStrategy = AdaptationStrategy.GRADUAL_INCREASE

    # Reasoning
    performance_indicators: dict[str, float] = field(default_factory=dict)
    adjustment_reason: str = ""
    expected_impact: str = ""

    # Implementation
    story_explanation: str = ""
    support_provided: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    effectiveness_score: float | None = None


@dataclass
class UserPreferences:
    """User preferences for difficulty and challenge."""

    user_id: str = ""

    # Difficulty preferences
    preferred_difficulty: DifficultyLevel = DifficultyLevel.MODERATE
    challenge_tolerance: float = 0.5  # 0.0 = low tolerance, 1.0 = high tolerance
    adaptation_speed: float = 0.5  # 0.0 = slow adaptation, 1.0 = fast adaptation

    # Support preferences
    wants_hints: bool = True
    wants_explanations: bool = True
    wants_encouragement: bool = True
    wants_alternative_paths: bool = True

    # Therapeutic preferences
    therapeutic_focus: list[str] = field(default_factory=list)
    learning_style: str = "balanced"  # visual, auditory, kinesthetic, balanced

    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AdaptiveDifficultyEngine:
    """Main engine for adaptive difficulty calibration and adjustment."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

        # Performance tracking
        self.performance_history: dict[str, list[PerformanceSnapshot]] = {}
        self.adjustment_history: dict[str, list[DifficultyAdjustment]] = {}
        self.user_preferences: dict[str, UserPreferences] = {}

        # Calibration parameters
        self.performance_window = timedelta(
            minutes=15
        )  # Window for performance analysis
        self.adjustment_threshold = 0.2  # Threshold for triggering adjustments
        self.min_data_points = 3  # Minimum data points before adjustment

        # Difficulty mapping
        self.difficulty_parameters = self._load_difficulty_parameters()
        self.adaptation_strategies = self._load_adaptation_strategies()

        # Metrics
        self.metrics = {
            "performance_snapshots_created": 0,
            "difficulty_adjustments_made": 0,
            "user_preferences_updated": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
        }

    def _load_difficulty_parameters(self) -> dict[DifficultyLevel, dict[str, Any]]:
        """Load difficulty parameters for each level."""
        return {
            DifficultyLevel.VERY_EASY: {
                "choice_complexity": 0.1,
                "emotional_intensity": 0.2,
                "therapeutic_challenge": 0.1,
                "time_pressure": 0.0,
                "support_availability": 1.0,
                "hint_frequency": 0.8,
                "explanation_detail": 0.9,
            },
            DifficultyLevel.EASY: {
                "choice_complexity": 0.3,
                "emotional_intensity": 0.4,
                "therapeutic_challenge": 0.3,
                "time_pressure": 0.1,
                "support_availability": 0.8,
                "hint_frequency": 0.6,
                "explanation_detail": 0.7,
            },
            DifficultyLevel.MODERATE: {
                "choice_complexity": 0.5,
                "emotional_intensity": 0.5,
                "therapeutic_challenge": 0.5,
                "time_pressure": 0.3,
                "support_availability": 0.6,
                "hint_frequency": 0.4,
                "explanation_detail": 0.5,
            },
            DifficultyLevel.CHALLENGING: {
                "choice_complexity": 0.7,
                "emotional_intensity": 0.6,
                "therapeutic_challenge": 0.7,
                "time_pressure": 0.5,
                "support_availability": 0.4,
                "hint_frequency": 0.2,
                "explanation_detail": 0.3,
            },
            DifficultyLevel.HARD: {
                "choice_complexity": 0.8,
                "emotional_intensity": 0.7,
                "therapeutic_challenge": 0.8,
                "time_pressure": 0.7,
                "support_availability": 0.2,
                "hint_frequency": 0.1,
                "explanation_detail": 0.2,
            },
            DifficultyLevel.VERY_HARD: {
                "choice_complexity": 0.9,
                "emotional_intensity": 0.8,
                "therapeutic_challenge": 0.9,
                "time_pressure": 0.8,
                "support_availability": 0.1,
                "hint_frequency": 0.0,
                "explanation_detail": 0.1,
            },
        }

    def _load_adaptation_strategies(self) -> dict[AdaptationStrategy, dict[str, Any]]:
        """Load adaptation strategies and their implementations."""
        return {
            AdaptationStrategy.GRADUAL_INCREASE: {
                "description": "Gradually increase difficulty over multiple interactions",
                "adjustment_rate": 0.1,
                "story_integration": "natural_progression",
                "support_reduction": "gradual",
            },
            AdaptationStrategy.GRADUAL_DECREASE: {
                "description": "Gradually decrease difficulty to build confidence",
                "adjustment_rate": -0.1,
                "story_integration": "supportive_context",
                "support_increase": "gradual",
            },
            AdaptationStrategy.IMMEDIATE_ADJUSTMENT: {
                "description": "Make immediate difficulty adjustment for urgent situations",
                "adjustment_rate": 0.3,
                "story_integration": "contextual_explanation",
                "support_change": "immediate",
            },
            AdaptationStrategy.CONTEXTUAL_SUPPORT: {
                "description": "Provide additional support without changing core difficulty",
                "adjustment_rate": 0.0,
                "story_integration": "helper_character",
                "support_increase": "contextual",
            },
            AdaptationStrategy.ALTERNATIVE_PATH: {
                "description": "Offer alternative path with different difficulty profile",
                "adjustment_rate": "variable",
                "story_integration": "branching_narrative",
                "support_change": "path_specific",
            },
            AdaptationStrategy.SKILL_BUILDING: {
                "description": "Focus on building specific skills before increasing difficulty",
                "adjustment_rate": 0.0,
                "story_integration": "training_scenario",
                "support_increase": "skill_focused",
            },
        }

    async def monitor_performance(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> PerformanceSnapshot:
        """Monitor user performance and create performance snapshot."""
        try:
            # Create performance snapshot
            snapshot = await self._create_performance_snapshot(
                session_state, interaction_data
            )

            # Store snapshot
            user_id = session_state.user_id
            if user_id not in self.performance_history:
                self.performance_history[user_id] = []

            self.performance_history[user_id].append(snapshot)

            # Keep only recent snapshots
            cutoff_time = datetime.utcnow() - timedelta(hours=2)
            self.performance_history[user_id] = [
                s
                for s in self.performance_history[user_id]
                if s.created_at > cutoff_time
            ]

            # Check if adjustment is needed
            if await self._should_adjust_difficulty(session_state, snapshot):
                await self._adjust_difficulty(session_state, snapshot)

            self.metrics["performance_snapshots_created"] += 1

            return snapshot

        except Exception as e:
            logger.error(
                f"Failed to monitor performance for user {session_state.user_id}: {e}"
            )
            # Return minimal snapshot
            return PerformanceSnapshot(
                user_id=session_state.user_id, session_id=session_state.session_id
            )

    def _calculate_success_rate(self, session_state: SessionState) -> float:
        """Calculate success rate from recent choices and consequences."""
        # Get recent consequence history
        consequence_history = session_state.context.get("consequence_history", [])

        if not consequence_history:
            return 0.5  # Default neutral success rate

        # Analyze recent consequences (last 10)
        recent_consequences = consequence_history[-10:]

        success_count = 0
        total_count = len(recent_consequences)

        for consequence in recent_consequences:
            # Consider therapeutic outcomes as success indicators
            therapeutic_count = consequence.get("therapeutic_outcomes_count", 0)
            learning_count = consequence.get("learning_opportunities_count", 0)

            # Success if there are therapeutic outcomes or learning opportunities
            if therapeutic_count > 0 or learning_count > 0:
                success_count += 1

        return success_count / total_count if total_count > 0 else 0.5

    def _calculate_therapeutic_progress(self, session_state: SessionState) -> float:
        """Calculate overall therapeutic progress."""
        progress_metrics = session_state.progress_metrics

        if not progress_metrics:
            return 0.0

        # Calculate average progress across all therapeutic goals
        total_progress = sum(progress_metrics.values())
        return total_progress / len(progress_metrics)

    def _calculate_emotional_stability(self, session_state: SessionState) -> float:
        """Calculate emotional stability from emotional state."""
        emotional_state = session_state.emotional_state

        if not emotional_state:
            return 0.5  # Default neutral stability

        # Calculate stability based on emotional balance
        positive_emotions = ["calm", "hopeful", "confident", "excited"]
        negative_emotions = ["anxious", "depressed", "angry", "fearful", "overwhelmed"]

        positive_score = sum(
            emotional_state.get(emotion, 0) for emotion in positive_emotions
        )
        negative_score = sum(
            emotional_state.get(emotion, 0) for emotion in negative_emotions
        )

        # Stability is higher when positive emotions dominate and negative emotions are low
        if positive_score + negative_score == 0:
            return 0.5

        stability = positive_score / (positive_score + negative_score)
        return max(0.0, min(1.0, stability))

    def _calculate_engagement_level(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> float:
        """Calculate user engagement level."""
        engagement_indicators = []

        # Check response time (faster responses often indicate engagement)
        if "response_time" in interaction_data:
            response_time = interaction_data["response_time"]
            # Normalize response time (5-60 seconds is optimal range)
            if 5 <= response_time <= 60:
                engagement_indicators.append(0.8)
            elif response_time < 5:
                engagement_indicators.append(0.6)  # Too fast might indicate rushing
            else:
                engagement_indicators.append(
                    0.3
                )  # Too slow might indicate disengagement

        # Check choice complexity (choosing complex options indicates engagement)
        if "choice_complexity" in interaction_data:
            complexity = interaction_data["choice_complexity"]
            engagement_indicators.append(complexity)

        # Check therapeutic relevance of choices
        if "therapeutic_relevance" in interaction_data:
            relevance = interaction_data["therapeutic_relevance"]
            engagement_indicators.append(relevance)

        # Check session duration (longer sessions often indicate engagement)
        session_duration = session_state.context.get("session_duration_minutes", 0)
        if session_duration > 0:
            # Optimal session length is 20-45 minutes
            if 20 <= session_duration <= 45:
                engagement_indicators.append(0.8)
            elif session_duration < 20:
                engagement_indicators.append(0.6)
            else:
                engagement_indicators.append(0.7)  # Long sessions still show engagement

        return (
            sum(engagement_indicators) / len(engagement_indicators)
            if engagement_indicators
            else 0.5
        )

    def _calculate_completion_rate(self, session_state: SessionState) -> float:
        """Calculate completion rate for scenes and choices."""
        # Get scene and choice history
        scenes_entered = len(session_state.context.get("scenes_visited", []))
        choices_made = len(session_state.context.get("choices_made", []))

        # Estimate expected completions based on session duration
        session_duration = session_state.context.get("session_duration_minutes", 1)
        expected_scenes = max(1, session_duration // 5)  # Expect 1 scene per 5 minutes
        expected_choices = max(
            1, session_duration // 2
        )  # Expect 1 choice per 2 minutes

        scene_completion_rate = min(1.0, scenes_entered / expected_scenes)
        choice_completion_rate = min(1.0, choices_made / expected_choices)

        return (scene_completion_rate + choice_completion_rate) / 2

    def _calculate_decision_time(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> float:
        """Calculate average decision time."""
        if "response_time" in interaction_data:
            return interaction_data["response_time"]

        # Get historical decision times from session context
        decision_times = session_state.context.get("decision_times", [])

        if decision_times:
            return statistics.mean(decision_times[-10:])  # Average of last 10 decisions

        return 30.0  # Default 30 seconds

    def _count_help_requests(self, session_state: SessionState) -> int:
        """Count help requests in current session."""
        return session_state.context.get("help_requests_count", 0)

    def _get_current_difficulty(self, session_state: SessionState) -> DifficultyLevel:
        """Get current difficulty level."""
        difficulty_value = session_state.context.get(
            "current_difficulty", DifficultyLevel.MODERATE.value
        )
        return DifficultyLevel(difficulty_value)

    def _get_recent_choices(self, session_state: SessionState) -> list[str]:
        """Get recent choice IDs."""
        choices_made = session_state.context.get("choices_made", [])
        return choices_made[-5:]  # Last 5 choices

    def _calculate_snapshot_confidence(self, snapshot: PerformanceSnapshot) -> float:
        """Calculate confidence in performance snapshot."""
        confidence = 0.5  # Base confidence

        # Higher confidence with more data points
        if len(snapshot.recent_choices) >= 3:
            confidence += 0.2

        # Higher confidence with recent therapeutic progress
        if snapshot.therapeutic_progress > 0.3:
            confidence += 0.2

        # Lower confidence with extreme values (might be outliers)
        extreme_values = [
            snapshot.success_rate < 0.1 or snapshot.success_rate > 0.9,
            snapshot.engagement_level < 0.1 or snapshot.engagement_level > 0.9,
        ]

        if any(extreme_values):
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    async def _should_adjust_difficulty(
        self, session_state: SessionState, snapshot: PerformanceSnapshot
    ) -> bool:
        """Determine if difficulty should be adjusted."""
        user_id = session_state.user_id

        # Need minimum data points
        if user_id not in self.performance_history:
            return False

        recent_snapshots = self.performance_history[user_id][-self.min_data_points :]

        if len(recent_snapshots) < self.min_data_points:
            return False

        # Calculate performance trends
        success_trend = self._calculate_trend(
            [s.success_rate for s in recent_snapshots]
        )
        engagement_trend = self._calculate_trend(
            [s.engagement_level for s in recent_snapshots]
        )
        stability_trend = self._calculate_trend(
            [s.emotional_stability for s in recent_snapshots]
        )

        # Check for adjustment triggers
        triggers = []

        # Poor performance trigger
        if (snapshot.success_rate < 0.3 and success_trend < -0.1) or (
            snapshot.engagement_level < 0.3 and engagement_trend < -0.1
        ):
            triggers.append(AdjustmentTrigger.POOR_PERFORMANCE)

        # Excellent performance trigger
        if (snapshot.success_rate > 0.8 and success_trend > 0.1) and (
            snapshot.engagement_level > 0.7
        ):
            triggers.append(AdjustmentTrigger.EXCELLENT_PERFORMANCE)

        # Emotional distress trigger
        if snapshot.emotional_stability < 0.3 and stability_trend < -0.2:
            triggers.append(AdjustmentTrigger.EMOTIONAL_DISTRESS)

        # Pattern recognition trigger
        if self._detect_performance_pattern(recent_snapshots):
            triggers.append(AdjustmentTrigger.PATTERN_RECOGNITION)

        return len(triggers) > 0

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend in a series of values."""
        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))

        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0

        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope

    def _detect_performance_pattern(self, snapshots: list[PerformanceSnapshot]) -> bool:
        """Detect patterns in performance that warrant adjustment."""
        if len(snapshots) < 3:
            return False

        # Check for consistent poor performance
        poor_performance_count = sum(1 for s in snapshots if s.success_rate < 0.4)
        if poor_performance_count >= len(snapshots) * 0.7:  # 70% poor performance
            return True

        # Check for consistent excellent performance
        excellent_performance_count = sum(1 for s in snapshots if s.success_rate > 0.8)
        if (
            excellent_performance_count >= len(snapshots) * 0.7
        ):  # 70% excellent performance
            return True

        # Check for declining engagement
        engagement_values = [s.engagement_level for s in snapshots]
        if all(
            engagement_values[i] > engagement_values[i + 1]
            for i in range(len(engagement_values) - 1)
        ):
            return True  # Consistently declining engagement

        return False

    async def _adjust_difficulty(
        self, session_state: SessionState, snapshot: PerformanceSnapshot
    ) -> None:
        """Adjust difficulty based on performance analysis."""
        try:
            # Determine adjustment trigger
            trigger = self._determine_adjustment_trigger(session_state, snapshot)

            # Select adaptation strategy
            strategy = self._select_adaptation_strategy(
                session_state, snapshot, trigger
            )

            # Calculate new difficulty level
            new_difficulty = self._calculate_new_difficulty(
                session_state, snapshot, strategy
            )

            # Create adjustment record
            adjustment = DifficultyAdjustment(
                user_id=session_state.user_id,
                session_id=session_state.session_id,
                from_difficulty=snapshot.current_difficulty,
                to_difficulty=new_difficulty,
                trigger=trigger,
                strategy=strategy,
                performance_indicators={
                    "success_rate": snapshot.success_rate,
                    "engagement_level": snapshot.engagement_level,
                    "emotional_stability": snapshot.emotional_stability,
                    "therapeutic_progress": snapshot.therapeutic_progress,
                },
                adjustment_reason=self._generate_adjustment_reason(trigger, snapshot),
                expected_impact=self._generate_expected_impact(
                    strategy, new_difficulty
                ),
                story_explanation=self._generate_story_explanation(
                    strategy, new_difficulty
                ),
            )

            # Apply the adjustment
            await self._apply_difficulty_adjustment(session_state, adjustment)

            # Store adjustment record
            user_id = session_state.user_id
            if user_id not in self.adjustment_history:
                self.adjustment_history[user_id] = []

            self.adjustment_history[user_id].append(adjustment)

            # Publish adjustment event
            await self._publish_adjustment_event(session_state, adjustment)

            self.metrics["difficulty_adjustments_made"] += 1

        except Exception as e:
            logger.error(
                f"Failed to adjust difficulty for user {session_state.user_id}: {e}"
            )

    def _determine_adjustment_trigger(
        self, session_state: SessionState, snapshot: PerformanceSnapshot
    ) -> AdjustmentTrigger:
        """Determine the primary trigger for difficulty adjustment."""
        # Check emotional distress first (highest priority)
        if snapshot.emotional_stability < 0.3:
            return AdjustmentTrigger.EMOTIONAL_DISTRESS

        # Check for poor performance
        if snapshot.success_rate < 0.3 or snapshot.engagement_level < 0.3:
            return AdjustmentTrigger.POOR_PERFORMANCE

        # Check for excellent performance
        if snapshot.success_rate > 0.8 and snapshot.engagement_level > 0.7:
            return AdjustmentTrigger.EXCELLENT_PERFORMANCE

        # Check for user request
        if session_state.context.get("difficulty_adjustment_requested", False):
            return AdjustmentTrigger.USER_REQUEST

        # Check for therapeutic goal changes
        if session_state.context.get("therapeutic_goals_changed", False):
            return AdjustmentTrigger.THERAPEUTIC_GOAL_CHANGE

        # Default to pattern recognition
        return AdjustmentTrigger.PATTERN_RECOGNITION

    def _select_adaptation_strategy(
        self,
        session_state: SessionState,
        snapshot: PerformanceSnapshot,
        trigger: AdjustmentTrigger,
    ) -> AdaptationStrategy:
        """Select appropriate adaptation strategy."""
        # Get user preferences
        user_preferences = self._get_user_preferences(session_state.user_id)

        # Strategy selection based on trigger
        if trigger == AdjustmentTrigger.EMOTIONAL_DISTRESS:
            return AdaptationStrategy.IMMEDIATE_ADJUSTMENT
        elif trigger == AdjustmentTrigger.POOR_PERFORMANCE:
            if user_preferences.adaptation_speed > 0.7:
                return AdaptationStrategy.IMMEDIATE_ADJUSTMENT
            else:
                return AdaptationStrategy.GRADUAL_DECREASE
        elif trigger == AdjustmentTrigger.EXCELLENT_PERFORMANCE:
            if user_preferences.challenge_tolerance > 0.7:
                return AdaptationStrategy.GRADUAL_INCREASE
            else:
                return AdaptationStrategy.CONTEXTUAL_SUPPORT
        elif trigger == AdjustmentTrigger.USER_REQUEST:
            requested_strategy = session_state.context.get("requested_strategy")
            if requested_strategy in [s.value for s in AdaptationStrategy]:
                return AdaptationStrategy(requested_strategy)
            return AdaptationStrategy.IMMEDIATE_ADJUSTMENT
        elif trigger == AdjustmentTrigger.THERAPEUTIC_GOAL_CHANGE:
            return AdaptationStrategy.SKILL_BUILDING
        else:
            # Pattern recognition or default
            if snapshot.success_rate < 0.5:
                return AdaptationStrategy.ALTERNATIVE_PATH
            else:
                return AdaptationStrategy.GRADUAL_INCREASE

    def _calculate_new_difficulty(
        self,
        session_state: SessionState,
        snapshot: PerformanceSnapshot,
        strategy: AdaptationStrategy,
    ) -> DifficultyLevel:
        """Calculate new difficulty level based on strategy."""
        current_difficulty = snapshot.current_difficulty
        strategy_config = self.adaptation_strategies[strategy]

        # Get adjustment rate
        adjustment_rate = strategy_config["adjustment_rate"]

        if adjustment_rate == "variable":
            # For alternative path strategy, choose based on user preference
            user_preferences = self._get_user_preferences(session_state.user_id)
            if user_preferences.preferred_difficulty != current_difficulty:
                return user_preferences.preferred_difficulty
            else:
                return current_difficulty

        if adjustment_rate == 0.0:
            # No difficulty change for contextual support or skill building
            return current_difficulty

        # Calculate new difficulty level
        current_value = current_difficulty.value
        adjustment = adjustment_rate * 6  # Scale to difficulty range (1-6)

        new_value = current_value + adjustment
        new_value = max(1, min(6, round(new_value)))  # Clamp to valid range

        return DifficultyLevel(int(new_value))

    def _generate_adjustment_reason(
        self, trigger: AdjustmentTrigger, snapshot: PerformanceSnapshot
    ) -> str:
        """Generate human-readable reason for adjustment."""
        reasons = {
            AdjustmentTrigger.POOR_PERFORMANCE: f"User showing difficulty with current challenges (success rate: {snapshot.success_rate:.1%})",
            AdjustmentTrigger.EXCELLENT_PERFORMANCE: f"User excelling at current level (success rate: {snapshot.success_rate:.1%})",
            AdjustmentTrigger.EMOTIONAL_DISTRESS: f"User experiencing emotional distress (stability: {snapshot.emotional_stability:.1%})",
            AdjustmentTrigger.USER_REQUEST: "User requested difficulty adjustment",
            AdjustmentTrigger.THERAPEUTIC_GOAL_CHANGE: "Therapeutic goals have changed, requiring difficulty recalibration",
            AdjustmentTrigger.PATTERN_RECOGNITION: "Performance patterns indicate need for difficulty adjustment",
        }
        return reasons.get(
            trigger, "Difficulty adjustment needed based on performance analysis"
        )

    def _generate_expected_impact(
        self, strategy: AdaptationStrategy, new_difficulty: DifficultyLevel
    ) -> str:
        """Generate expected impact description."""
        impacts = {
            AdaptationStrategy.GRADUAL_INCREASE: f"Gradually increase challenge to {new_difficulty.name} level for continued growth",
            AdaptationStrategy.GRADUAL_DECREASE: f"Reduce challenge to {new_difficulty.name} level to build confidence",
            AdaptationStrategy.IMMEDIATE_ADJUSTMENT: f"Immediate adjustment to {new_difficulty.name} level for optimal experience",
            AdaptationStrategy.CONTEXTUAL_SUPPORT: "Provide additional support while maintaining current challenge level",
            AdaptationStrategy.ALTERNATIVE_PATH: f"Offer alternative approach at {new_difficulty.name} difficulty level",
            AdaptationStrategy.SKILL_BUILDING: "Focus on skill development before increasing difficulty",
        }
        return impacts.get(
            strategy, f"Adjust to {new_difficulty.name} difficulty level"
        )

    def _generate_story_explanation(
        self, strategy: AdaptationStrategy, new_difficulty: DifficultyLevel
    ) -> str:
        """Generate story-appropriate explanation for difficulty change."""
        explanations = {
            AdaptationStrategy.GRADUAL_INCREASE: [
                "As you grow stronger and more confident, new challenges naturally present themselves.",
                "Your developing skills open doors to more complex situations.",
                "The world around you responds to your growing capabilities.",
            ],
            AdaptationStrategy.GRADUAL_DECREASE: [
                "You find yourself in a more supportive environment where you can build confidence.",
                "A helpful mentor appears to guide you through these challenges.",
                "The situation becomes more manageable as you find your footing.",
            ],
            AdaptationStrategy.IMMEDIATE_ADJUSTMENT: [
                "The situation suddenly shifts, requiring a different approach.",
                "New circumstances call for adapted strategies.",
                "The environment changes to better match your current needs.",
            ],
            AdaptationStrategy.CONTEXTUAL_SUPPORT: [
                "A wise companion joins you to offer guidance and support.",
                "You discover helpful resources that make the journey easier.",
                "The community around you rallies to provide assistance.",
            ],
            AdaptationStrategy.ALTERNATIVE_PATH: [
                "You discover an alternative route that better suits your style.",
                "A different approach becomes available that matches your strengths.",
                "New possibilities open up that align with your preferences.",
            ],
            AdaptationStrategy.SKILL_BUILDING: [
                "You find an opportunity to practice and develop your abilities.",
                "A training ground appears where you can hone your skills.",
                "Time is available to strengthen your foundation before moving forward.",
            ],
        }

        strategy_explanations = explanations.get(
            strategy, ["The path ahead adjusts to your journey."]
        )
        return strategy_explanations[0]  # Return first explanation for now

    def _get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences, creating defaults if not found."""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)

        return self.user_preferences[user_id]

    async def _apply_difficulty_adjustment(
        self, session_state: SessionState, adjustment: DifficultyAdjustment
    ) -> None:
        """Apply difficulty adjustment to session state."""
        # Update current difficulty in session
        session_state.context["current_difficulty"] = adjustment.to_difficulty.value

        # Apply difficulty parameters
        difficulty_params = self.difficulty_parameters[adjustment.to_difficulty]
        session_state.context["difficulty_parameters"] = difficulty_params

        # Provide support based on strategy
        support_provided = []

        if adjustment.strategy == AdaptationStrategy.CONTEXTUAL_SUPPORT:
            support_provided.extend(
                [
                    "Additional hints available",
                    "Detailed explanations provided",
                    "Encouragement and validation",
                ]
            )
        elif adjustment.strategy == AdaptationStrategy.SKILL_BUILDING:
            support_provided.extend(
                [
                    "Skill-building exercises available",
                    "Practice scenarios provided",
                    "Progress tracking enabled",
                ]
            )
        elif adjustment.strategy == AdaptationStrategy.ALTERNATIVE_PATH:
            support_provided.extend(
                [
                    "Alternative approaches available",
                    "Multiple solution paths",
                    "Flexible goal achievement",
                ]
            )

        # Store support information
        adjustment.support_provided = support_provided
        session_state.context["current_support"] = support_provided

        # Update story explanation
        session_state.context["difficulty_explanation"] = adjustment.story_explanation

        # Clear any adjustment request flags
        session_state.context.pop("difficulty_adjustment_requested", None)
        session_state.context.pop("requested_strategy", None)
        session_state.context.pop("therapeutic_goals_changed", None)

    async def _publish_adjustment_event(
        self, session_state: SessionState, adjustment: DifficultyAdjustment
    ) -> None:
        """Publish difficulty adjustment event."""
        event = NarrativeEvent(
            event_type=EventType.DIFFICULTY_ADJUSTED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "adjustment_id": adjustment.adjustment_id,
                "from_difficulty": adjustment.from_difficulty.name,
                "to_difficulty": adjustment.to_difficulty.name,
                "trigger": adjustment.trigger.value,
                "strategy": adjustment.strategy.value,
                "performance_indicators": adjustment.performance_indicators,
                "story_explanation": adjustment.story_explanation,
            },
        )

        await self.event_bus.publish(event)

    async def update_user_preferences(
        self, user_id: str, preferences: dict[str, Any]
    ) -> None:
        """Update user preferences for difficulty adaptation."""
        try:
            user_prefs = self._get_user_preferences(user_id)

            # Update preferences
            if "preferred_difficulty" in preferences:
                difficulty_value = preferences["preferred_difficulty"]
                if isinstance(difficulty_value, int) and 1 <= difficulty_value <= 6:
                    user_prefs.preferred_difficulty = DifficultyLevel(difficulty_value)

            if "challenge_tolerance" in preferences:
                tolerance = preferences["challenge_tolerance"]
                if 0.0 <= tolerance <= 1.0:
                    user_prefs.challenge_tolerance = tolerance

            if "adaptation_speed" in preferences:
                speed = preferences["adaptation_speed"]
                if 0.0 <= speed <= 1.0:
                    user_prefs.adaptation_speed = speed

            if "wants_hints" in preferences:
                user_prefs.wants_hints = bool(preferences["wants_hints"])

            if "wants_explanations" in preferences:
                user_prefs.wants_explanations = bool(preferences["wants_explanations"])

            if "wants_encouragement" in preferences:
                user_prefs.wants_encouragement = bool(
                    preferences["wants_encouragement"]
                )

            if "wants_alternative_paths" in preferences:
                user_prefs.wants_alternative_paths = bool(
                    preferences["wants_alternative_paths"]
                )

            if "therapeutic_focus" in preferences:
                user_prefs.therapeutic_focus = preferences["therapeutic_focus"]

            if "learning_style" in preferences:
                user_prefs.learning_style = preferences["learning_style"]

            user_prefs.last_updated = datetime.utcnow()
            self.metrics["user_preferences_updated"] += 1

        except Exception as e:
            logger.error(f"Failed to update user preferences for {user_id}: {e}")

    async def request_difficulty_adjustment(
        self,
        session_state: SessionState,
        requested_difficulty: DifficultyLevel | None = None,
        strategy: AdaptationStrategy | None = None,
    ) -> bool:
        """Request manual difficulty adjustment."""
        try:
            # Set adjustment request flags
            session_state.context["difficulty_adjustment_requested"] = True

            if requested_difficulty:
                session_state.context["requested_difficulty"] = (
                    requested_difficulty.value
                )

            if strategy:
                session_state.context["requested_strategy"] = strategy.value

            # Trigger immediate performance monitoring to process the request
            interaction_data = {
                "interaction_type": "difficulty_adjustment_request",
                "requested_difficulty": (
                    requested_difficulty.value if requested_difficulty else None
                ),
                "requested_strategy": strategy.value if strategy else None,
            }

            await self.monitor_performance(session_state, interaction_data)

            return True

        except Exception as e:
            logger.error(
                f"Failed to request difficulty adjustment for user {session_state.user_id}: {e}"
            )
            return False

    def get_current_difficulty_info(
        self, session_state: SessionState
    ) -> dict[str, Any]:
        """Get current difficulty information and parameters."""
        current_difficulty = self._get_current_difficulty(session_state)
        difficulty_params = self.difficulty_parameters[current_difficulty]

        return {
            "current_difficulty": current_difficulty.name,
            "difficulty_level": current_difficulty.value,
            "parameters": difficulty_params,
            "support_available": session_state.context.get("current_support", []),
            "explanation": session_state.context.get("difficulty_explanation", ""),
            "user_preferences": self._get_user_preferences(
                session_state.user_id
            ).__dict__,
        }

    def get_performance_summary(self, user_id: str, hours: int = 2) -> dict[str, Any]:
        """Get performance summary for a user."""
        if user_id not in self.performance_history:
            return {"error": "No performance data available"}

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_snapshots = [
            s for s in self.performance_history[user_id] if s.created_at > cutoff_time
        ]

        if not recent_snapshots:
            return {"error": "No recent performance data"}

        # Calculate summary statistics
        success_rates = [s.success_rate for s in recent_snapshots]
        engagement_levels = [s.engagement_level for s in recent_snapshots]
        stability_levels = [s.emotional_stability for s in recent_snapshots]

        return {
            "snapshots_count": len(recent_snapshots),
            "time_period_hours": hours,
            "success_rate": {
                "current": success_rates[-1],
                "average": statistics.mean(success_rates),
                "trend": self._calculate_trend(success_rates),
            },
            "engagement_level": {
                "current": engagement_levels[-1],
                "average": statistics.mean(engagement_levels),
                "trend": self._calculate_trend(engagement_levels),
            },
            "emotional_stability": {
                "current": stability_levels[-1],
                "average": statistics.mean(stability_levels),
                "trend": self._calculate_trend(stability_levels),
            },
            "current_difficulty": recent_snapshots[-1].current_difficulty.name,
            "therapeutic_progress": recent_snapshots[-1].therapeutic_progress,
        }

    def get_adjustment_history(
        self, user_id: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Get difficulty adjustment history for a user."""
        if user_id not in self.adjustment_history:
            return []

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_adjustments = [
            adj
            for adj in self.adjustment_history[user_id]
            if adj.created_at > cutoff_time
        ]

        return [
            {
                "adjustment_id": adj.adjustment_id,
                "from_difficulty": adj.from_difficulty.name,
                "to_difficulty": adj.to_difficulty.name,
                "trigger": adj.trigger.value,
                "strategy": adj.strategy.value,
                "reason": adj.adjustment_reason,
                "expected_impact": adj.expected_impact,
                "story_explanation": adj.story_explanation,
                "created_at": adj.created_at.isoformat(),
                "effectiveness_score": adj.effectiveness_score,
            }
            for adj in recent_adjustments
        ]

    def get_metrics(self) -> dict[str, Any]:
        """Get adaptive difficulty engine metrics."""
        return {
            **self.metrics,
            "active_users_monitored": len(self.performance_history),
            "total_performance_snapshots": sum(
                len(snapshots) for snapshots in self.performance_history.values()
            ),
            "total_adjustments": sum(
                len(adjustments) for adjustments in self.adjustment_history.values()
            ),
            "user_preferences_configured": len(self.user_preferences),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of adaptive difficulty engine."""
        return {
            "status": "healthy",
            "difficulty_levels_configured": len(self.difficulty_parameters),
            "adaptation_strategies_available": len(self.adaptation_strategies),
            "performance_window_minutes": self.performance_window.total_seconds() / 60,
            "adjustment_threshold": self.adjustment_threshold,
            "min_data_points": self.min_data_points,
            "metrics": self.get_metrics(),
        }

    async def _create_performance_snapshot(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> PerformanceSnapshot:
        """Create performance snapshot from session data."""
        snapshot = PerformanceSnapshot(
            user_id=session_state.user_id, session_id=session_state.session_id
        )

        # Calculate success rate from recent choices
        snapshot.success_rate = self._calculate_success_rate(session_state)

        # Get therapeutic progress
        snapshot.therapeutic_progress = self._calculate_therapeutic_progress(
            session_state
        )

        # Get emotional stability
        snapshot.emotional_stability = self._calculate_emotional_stability(
            session_state
        )

        # Calculate engagement level
        snapshot.engagement_level = self._calculate_engagement_level(
            session_state, interaction_data
        )

        # Calculate completion rate
        snapshot.completion_rate = self._calculate_completion_rate(session_state)

        # Get average decision time
        snapshot.average_decision_time = self._calculate_decision_time(
            session_state, interaction_data
        )

        # Count help requests
        snapshot.help_requests = self._count_help_requests(session_state)

        # Get current difficulty
        snapshot.current_difficulty = self._get_current_difficulty(session_state)

        # Store recent choices
        snapshot.recent_choices = self._get_recent_choices(session_state)

        # Get therapeutic goals
        snapshot.therapeutic_goals = session_state.therapeutic_goals

        # Calculate confidence
        snapshot.confidence = self._calculate_snapshot_confidence(snapshot)

        return snapshot
