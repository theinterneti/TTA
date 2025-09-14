"""
Progress Tracking and Personalization System for TTA Prototype

This module implements comprehensive user progress tracking and personalization capabilities
for the therapeutic text adventure system. It monitors therapeutic progress, analyzes user
patterns, and provides personalized content recommendations based on individual therapeutic
journeys and emotional growth metrics.

Classes:
    ProgressTrackingPersonalization: Main class for progress monitoring and personalization
    TherapeuticProgressAnalyzer: Analyzes therapeutic progress and patterns
    PersonalizationEngine: Generates personalized content and recommendations
    EmotionalGrowthTracker: Tracks emotional development over time
    GoalAchievementMonitor: Monitors therapeutic goal progress and achievements
"""

import logging
import statistics

# Import system components
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Add paths for imports
core_path = Path(__file__).parent
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    # Try relative imports first (when running as part of package)
    from ..models.data_models import (
        CharacterState,
        CompletedIntervention,
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticGoal,
        TherapeuticGoalStatus,
        TherapeuticProgress,
        ValidationError,
    )
    from ..models.therapeutic_llm_client import (
        SafetyLevel,
        TherapeuticContentType,
        TherapeuticContext,
        TherapeuticLLMClient,
        TherapeuticResponse,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            CharacterState,
            CompletedIntervention,
            CopingStrategy,
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticGoal,
            TherapeuticGoalStatus,
            TherapeuticProgress,
            ValidationError,
        )
        from therapeutic_llm_client import (
            SafetyLevel,
            TherapeuticContentType,
            TherapeuticContext,
            TherapeuticLLMClient,
            TherapeuticResponse,
        )
    except ImportError:
        # Final fallback - create minimal mock classes for testing
        import logging
        logging.warning("Could not import required classes, using mock implementations")

        class MockTherapeuticLLMClient:
            def generate_therapeutic_content(self, context, content_type):
                return MockTherapeuticResponse()

        class MockTherapeuticResponse:
            def __init__(self):
                self.content = '{"recommendation": "Continue current therapeutic approach"}'
                self.content_type = "recommendation"
                self.safety_level = "safe"
                self.therapeutic_value = 0.7
                self.confidence = 0.8
                self.metadata = {}

        TherapeuticLLMClient = MockTherapeuticLLMClient
        TherapeuticResponse = MockTherapeuticResponse

logger = logging.getLogger(__name__)


class ProgressMetricType(Enum):
    """Types of progress metrics tracked."""
    EMOTIONAL_REGULATION = "emotional_regulation"
    COPING_SKILLS_USAGE = "coping_skills_usage"
    GOAL_ACHIEVEMENT = "goal_achievement"
    INTERVENTION_EFFECTIVENESS = "intervention_effectiveness"
    ENGAGEMENT_LEVEL = "engagement_level"
    RESILIENCE_BUILDING = "resilience_building"
    SELF_AWARENESS = "self_awareness"
    RELATIONSHIP_QUALITY = "relationship_quality"
    STRESS_MANAGEMENT = "stress_management"
    BEHAVIORAL_CHANGE = "behavioral_change"


class PersonalizationDimension(Enum):
    """Dimensions for content personalization."""
    THERAPEUTIC_APPROACH = "therapeutic_approach"
    CONTENT_DIFFICULTY = "content_difficulty"
    INTERACTION_STYLE = "interaction_style"
    PACING_PREFERENCE = "pacing_preference"
    EMOTIONAL_SENSITIVITY = "emotional_sensitivity"
    LEARNING_STYLE = "learning_style"
    MOTIVATION_TYPE = "motivation_type"
    SUPPORT_LEVEL = "support_level"


@dataclass
class ProgressMetric:
    """Represents a single progress metric measurement."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: ProgressMetricType = ProgressMetricType.EMOTIONAL_REGULATION
    value: float = 0.0  # Normalized 0.0 to 1.0
    raw_value: float | None = None
    measurement_context: str = ""
    confidence_level: float = 0.8  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str | None = None
    contributing_factors: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate progress metric data."""
        if not 0.0 <= self.value <= 1.0:
            raise ValidationError("Metric value must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        return True


@dataclass
class PersonalizationProfile:
    """User's personalization profile based on preferences and progress."""
    user_id: str
    therapeutic_preferences: dict[PersonalizationDimension, float] = field(default_factory=dict)
    content_adaptation_settings: dict[str, Any] = field(default_factory=dict)
    interaction_patterns: dict[str, float] = field(default_factory=dict)
    learning_velocity: float = 0.5  # How quickly user learns/adapts
    engagement_patterns: dict[str, list[float]] = field(default_factory=dict)
    preferred_intervention_types: list[InterventionType] = field(default_factory=list)
    avoided_triggers: list[str] = field(default_factory=list)
    optimal_session_length: int = 30  # minutes
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate personalization profile."""
        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty")
        if not 0.0 <= self.learning_velocity <= 1.0:
            raise ValidationError("Learning velocity must be between 0.0 and 1.0")
        if self.optimal_session_length <= 0:
            raise ValidationError("Optimal session length must be positive")
        return True


@dataclass
class ProgressAnalysisResult:
    """Result of progress analysis with insights and recommendations."""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    analysis_period: tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now() - timedelta(days=30), datetime.now()))
    overall_progress_score: float = 0.0  # 0.0 to 1.0
    metric_trends: dict[ProgressMetricType, dict[str, float]] = field(default_factory=dict)
    achievement_highlights: list[str] = field(default_factory=list)
    areas_for_improvement: list[str] = field(default_factory=list)
    recommended_interventions: list[InterventionType] = field(default_factory=list)
    personalization_adjustments: dict[PersonalizationDimension, float] = field(default_factory=dict)
    next_therapeutic_focus: str = ""
    confidence_level: float = 0.8
    generated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate progress analysis result."""
        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty")
        if not 0.0 <= self.overall_progress_score <= 1.0:
            raise ValidationError("Overall progress score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        return True


class TherapeuticProgressAnalyzer:
    """Analyzes therapeutic progress and identifies patterns."""

    def __init__(self):
        """Initialize the therapeutic progress analyzer."""
        self.metric_weights = self._initialize_metric_weights()
        self.trend_analysis_window = 14  # days
        self.minimum_data_points = 3
        logger.info("TherapeuticProgressAnalyzer initialized")

    def _initialize_metric_weights(self) -> dict[ProgressMetricType, float]:
        """Initialize weights for different progress metrics."""
        return {
            ProgressMetricType.EMOTIONAL_REGULATION: 0.20,
            ProgressMetricType.COPING_SKILLS_USAGE: 0.18,
            ProgressMetricType.GOAL_ACHIEVEMENT: 0.15,
            ProgressMetricType.INTERVENTION_EFFECTIVENESS: 0.12,
            ProgressMetricType.ENGAGEMENT_LEVEL: 0.10,
            ProgressMetricType.RESILIENCE_BUILDING: 0.10,
            ProgressMetricType.SELF_AWARENESS: 0.08,
            ProgressMetricType.RELATIONSHIP_QUALITY: 0.07
        }

    def analyze_progress_metrics(self, metrics: list[ProgressMetric],
                               timeframe: tuple[datetime, datetime] | None = None) -> dict[ProgressMetricType, dict[str, float]]:
        """Analyze progress metrics and calculate trends."""
        if not metrics:
            return {}

        # Filter metrics by timeframe if provided
        if timeframe:
            start_time, end_time = timeframe
            metrics = [m for m in metrics if start_time <= m.timestamp <= end_time]

        # Group metrics by type
        grouped_metrics = defaultdict(list)
        for metric in metrics:
            grouped_metrics[metric.metric_type].append(metric)

        # Analyze each metric type
        analysis_results = {}
        for metric_type, metric_list in grouped_metrics.items():
            if len(metric_list) < self.minimum_data_points:
                continue

            # Sort by timestamp
            metric_list.sort(key=lambda x: x.timestamp)

            # Calculate trend analysis
            values = [m.value for m in metric_list]
            timestamps = [m.timestamp.timestamp() for m in metric_list]

            # Calculate basic statistics
            current_value = values[-1]
            average_value = statistics.mean(values)
            trend_slope = self._calculate_trend_slope(timestamps, values)
            volatility = statistics.stdev(values) if len(values) > 1 else 0.0
            improvement_rate = self._calculate_improvement_rate(values)

            analysis_results[metric_type] = {
                "current_value": current_value,
                "average_value": average_value,
                "trend_slope": trend_slope,
                "volatility": volatility,
                "improvement_rate": improvement_rate,
                "data_points": len(values),
                "confidence": min(1.0, len(values) / 10.0)  # More data = higher confidence
            }

        return analysis_results

    def _calculate_trend_slope(self, timestamps: list[float], values: list[float]) -> float:
        """Calculate the trend slope using linear regression."""
        if len(timestamps) < 2:
            return 0.0

        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values, strict=False))
        sum_x2 = sum(x * x for x in timestamps)

        # Linear regression slope calculation
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def _calculate_improvement_rate(self, values: list[float]) -> float:
        """Calculate the rate of improvement over time."""
        if len(values) < 2:
            return 0.0

        # Compare recent values to earlier values
        mid_point = len(values) // 2
        early_avg = statistics.mean(values[:mid_point]) if mid_point > 0 else values[0]
        recent_avg = statistics.mean(values[mid_point:])

        if early_avg == 0:
            return 0.0

        improvement_rate = (recent_avg - early_avg) / early_avg
        return max(-1.0, min(1.0, improvement_rate))  # Clamp to [-1, 1]

    def calculate_overall_progress_score(self, metric_analysis: dict[ProgressMetricType, dict[str, float]]) -> float:
        """Calculate overall progress score from metric analysis."""
        if not metric_analysis:
            return 0.0

        weighted_score = 0.0
        total_weight = 0.0

        for metric_type, analysis in metric_analysis.items():
            weight = self.metric_weights.get(metric_type, 0.1)

            # Combine current value, trend, and improvement rate
            current_score = analysis.get("current_value", 0.0)
            trend_bonus = max(0, analysis.get("trend_slope", 0.0)) * 0.1
            improvement_bonus = max(0, analysis.get("improvement_rate", 0.0)) * 0.1

            metric_score = min(1.0, current_score + trend_bonus + improvement_bonus)

            # Weight by confidence
            confidence = analysis.get("confidence", 0.5)
            weighted_score += metric_score * weight * confidence
            total_weight += weight * confidence

        if total_weight == 0:
            return 0.0

        return weighted_score / total_weight

    def identify_achievement_highlights(self, metric_analysis: dict[ProgressMetricType, dict[str, float]]) -> list[str]:
        """Identify notable achievements and improvements."""
        highlights = []

        for metric_type, analysis in metric_analysis.items():
            current_value = analysis.get("current_value", 0.0)
            improvement_rate = analysis.get("improvement_rate", 0.0)
            trend_slope = analysis.get("trend_slope", 0.0)

            # High current performance
            if current_value >= 0.8:
                highlights.append(f"Excellent progress in {metric_type.value.replace('_', ' ')}")

            # Significant improvement
            if improvement_rate >= 0.3:
                highlights.append(f"Strong improvement in {metric_type.value.replace('_', ' ')} ({improvement_rate:.1%} increase)")

            # Positive trend
            if trend_slope > 0.001 and current_value >= 0.6:
                highlights.append(f"Consistent upward trend in {metric_type.value.replace('_', ' ')}")

        return highlights[:5]  # Limit to top 5 highlights

    def identify_improvement_areas(self, metric_analysis: dict[ProgressMetricType, dict[str, float]]) -> list[str]:
        """Identify areas that need improvement."""
        improvement_areas = []

        for metric_type, analysis in metric_analysis.items():
            current_value = analysis.get("current_value", 0.0)
            improvement_rate = analysis.get("improvement_rate", 0.0)
            trend_slope = analysis.get("trend_slope", 0.0)
            volatility = analysis.get("volatility", 0.0)

            # Low current performance
            if current_value <= 0.4:
                improvement_areas.append(f"Focus needed on {metric_type.value.replace('_', ' ')}")

            # Declining trend
            if trend_slope < -0.001:
                improvement_areas.append(f"Address declining trend in {metric_type.value.replace('_', ' ')}")

            # High volatility
            if volatility >= 0.3 and current_value < 0.7:
                improvement_areas.append(f"Stabilize progress in {metric_type.value.replace('_', ' ')}")

            # Stagnant improvement
            if abs(improvement_rate) < 0.05 and current_value < 0.6:
                improvement_areas.append(f"Boost progress in {metric_type.value.replace('_', ' ')}")

        return improvement_areas[:5]  # Limit to top 5 areas


class EmotionalGrowthTracker:
    """Tracks emotional development and growth patterns over time."""

    def __init__(self):
        """Initialize the emotional growth tracker."""
        self.emotional_baseline_window = 7  # days for establishing baseline
        self.growth_measurement_window = 30  # days for measuring growth
        logger.info("EmotionalGrowthTracker initialized")

    def track_emotional_patterns(self, emotional_states: list[EmotionalState],
                                timeframe: tuple[datetime, datetime] | None = None) -> dict[str, Any]:
        """Track emotional patterns and growth over time."""
        if not emotional_states:
            return {}

        # Filter by timeframe if provided
        if timeframe:
            start_time, end_time = timeframe
            emotional_states = [es for es in emotional_states if start_time <= es.timestamp <= end_time]

        if not emotional_states:
            return {}

        # Sort by timestamp
        emotional_states.sort(key=lambda x: x.timestamp)

        # Analyze emotional patterns
        emotion_frequency = defaultdict(int)
        intensity_trends = defaultdict(list)
        emotional_stability = []

        for state in emotional_states:
            emotion_frequency[state.primary_emotion] += 1
            intensity_trends[state.primary_emotion].append(state.intensity)
            emotional_stability.append(state.intensity)

        # Calculate emotional growth metrics
        growth_metrics = {
            "dominant_emotions": dict(sorted(emotion_frequency.items(), key=lambda x: x[1], reverse=True)[:5]),
            "emotional_diversity": len(emotion_frequency),
            "average_intensity": statistics.mean(emotional_stability) if emotional_stability else 0.0,
            "emotional_stability_score": 1.0 - (statistics.stdev(emotional_stability) if len(emotional_stability) > 1 else 0.0),
            "positive_emotion_ratio": self._calculate_positive_emotion_ratio(emotional_states),
            "emotional_regulation_trend": self._calculate_regulation_trend(emotional_states),
            "growth_indicators": self._identify_growth_indicators(emotional_states)
        }

        return growth_metrics

    def _calculate_positive_emotion_ratio(self, emotional_states: list[EmotionalState]) -> float:
        """Calculate the ratio of positive to total emotions."""
        positive_emotions = {EmotionalStateType.CALM, EmotionalStateType.EXCITED, EmotionalStateType.HOPEFUL}

        positive_count = sum(1 for state in emotional_states if state.primary_emotion in positive_emotions)
        total_count = len(emotional_states)

        return positive_count / total_count if total_count > 0 else 0.0

    def _calculate_regulation_trend(self, emotional_states: list[EmotionalState]) -> float:
        """Calculate emotional regulation improvement trend."""
        if len(emotional_states) < 4:
            return 0.0

        # Split into early and recent periods
        mid_point = len(emotional_states) // 2
        early_states = emotional_states[:mid_point]
        recent_states = emotional_states[mid_point:]

        # Calculate average intensity for each period
        statistics.mean([state.intensity for state in early_states])
        statistics.mean([state.intensity for state in recent_states])

        # Calculate regulation improvement (lower intensity = better regulation for negative emotions)
        negative_emotions = {EmotionalStateType.ANXIOUS, EmotionalStateType.DEPRESSED,
                           EmotionalStateType.ANGRY, EmotionalStateType.OVERWHELMED}

        early_negative_intensity = statistics.mean([
            state.intensity for state in early_states
            if state.primary_emotion in negative_emotions
        ]) if any(state.primary_emotion in negative_emotions for state in early_states) else 0.0

        recent_negative_intensity = statistics.mean([
            state.intensity for state in recent_states
            if state.primary_emotion in negative_emotions
        ]) if any(state.primary_emotion in negative_emotions for state in recent_states) else 0.0

        # Improvement = reduction in negative emotion intensity
        if early_negative_intensity > 0:
            regulation_improvement = (early_negative_intensity - recent_negative_intensity) / early_negative_intensity
            return max(-1.0, min(1.0, regulation_improvement))

        return 0.0

    def _identify_growth_indicators(self, emotional_states: list[EmotionalState]) -> list[str]:
        """Identify specific indicators of emotional growth."""
        indicators = []

        if len(emotional_states) < 5:
            return indicators

        # Analyze recent vs. early emotional patterns
        recent_states = emotional_states[-5:]
        early_states = emotional_states[:5]

        # Check for increased emotional awareness (higher confidence)
        recent_confidence = statistics.mean([state.confidence_level for state in recent_states])
        early_confidence = statistics.mean([state.confidence_level for state in early_states])

        if recent_confidence > early_confidence + 0.1:
            indicators.append("Increased emotional self-awareness")

        # Check for better coping resources utilization
        recent_coping = sum(len(state.coping_resources) for state in recent_states) / len(recent_states)
        early_coping = sum(len(state.coping_resources) for state in early_states) / len(early_states)

        if recent_coping > early_coping + 0.5:
            indicators.append("Improved coping resource utilization")

        # Check for reduced trigger sensitivity
        recent_triggers = sum(len(state.triggers) for state in recent_states) / len(recent_states)
        early_triggers = sum(len(state.triggers) for state in early_states) / len(early_states)

        if recent_triggers < early_triggers - 0.3:
            indicators.append("Reduced emotional trigger sensitivity")

        return indicators


class GoalAchievementMonitor:
    """Monitors therapeutic goal progress and achievements."""

    def __init__(self):
        """Initialize the goal achievement monitor."""
        self.achievement_threshold = 0.8  # 80% progress for achievement
        self.stagnation_threshold = 0.05  # 5% progress in 2 weeks = stagnation
        logger.info("GoalAchievementMonitor initialized")

    def monitor_goal_progress(self, goals: list[TherapeuticGoal]) -> dict[str, Any]:
        """Monitor progress across all therapeutic goals."""
        if not goals:
            return {}

        # Categorize goals by status
        active_goals = [g for g in goals if g.status == TherapeuticGoalStatus.ACTIVE]
        completed_goals = [g for g in goals if g.status == TherapeuticGoalStatus.COMPLETED]

        # Calculate achievement metrics
        total_goals = len(goals)
        completion_rate = len(completed_goals) / total_goals if total_goals > 0 else 0.0

        # Analyze active goal progress
        active_progress = []
        stagnant_goals = []
        near_completion_goals = []

        for goal in active_goals:
            active_progress.append(goal.progress_percentage)

            if goal.progress_percentage >= self.achievement_threshold * 100:
                near_completion_goals.append(goal)
            elif self._is_goal_stagnant(goal):
                stagnant_goals.append(goal)

        average_progress = statistics.mean(active_progress) if active_progress else 0.0

        # Generate achievement insights
        achievement_insights = {
            "total_goals": total_goals,
            "active_goals": len(active_goals),
            "completed_goals": len(completed_goals),
            "completion_rate": completion_rate,
            "average_active_progress": average_progress,
            "near_completion_count": len(near_completion_goals),
            "stagnant_goals_count": len(stagnant_goals),
            "achievement_momentum": self._calculate_achievement_momentum(goals),
            "goal_difficulty_distribution": self._analyze_goal_difficulty(goals),
            "recommended_actions": self._generate_goal_recommendations(active_goals, stagnant_goals, near_completion_goals)
        }

        return achievement_insights

    def _is_goal_stagnant(self, goal: TherapeuticGoal) -> bool:
        """Determine if a goal has stagnated."""
        # This is a simplified check - in a real implementation, you'd track progress history
        # For now, we'll consider goals with very low progress as potentially stagnant
        days_since_creation = (datetime.now() - goal.created_at).days
        expected_progress = min(50.0, days_since_creation * 2)  # 2% per day expected

        return goal.progress_percentage < expected_progress and days_since_creation > 7

    def _calculate_achievement_momentum(self, goals: list[TherapeuticGoal]) -> float:
        """Calculate the momentum of goal achievement."""
        if not goals:
            return 0.0

        # Recent completions boost momentum
        recent_completions = [
            g for g in goals
            if g.status == TherapeuticGoalStatus.COMPLETED and
            (datetime.now() - g.created_at).days <= 30
        ]

        # Active goals near completion boost momentum
        near_completion = [
            g for g in goals
            if g.status == TherapeuticGoalStatus.ACTIVE and
            g.progress_percentage >= 70
        ]

        momentum_score = (len(recent_completions) * 0.3 + len(near_completion) * 0.2) / len(goals)
        return min(1.0, momentum_score)

    def _analyze_goal_difficulty(self, goals: list[TherapeuticGoal]) -> dict[str, int]:
        """Analyze the distribution of goal difficulty levels."""
        # Simplified difficulty assessment based on target behaviors count
        difficulty_distribution = {"easy": 0, "medium": 0, "hard": 0}

        for goal in goals:
            behavior_count = len(goal.target_behaviors)
            if behavior_count <= 2:
                difficulty_distribution["easy"] += 1
            elif behavior_count <= 4:
                difficulty_distribution["medium"] += 1
            else:
                difficulty_distribution["hard"] += 1

        return difficulty_distribution

    def _generate_goal_recommendations(self, active_goals: list[TherapeuticGoal],
                                     stagnant_goals: list[TherapeuticGoal],
                                     near_completion_goals: list[TherapeuticGoal]) -> list[str]:
        """Generate recommendations for goal management."""
        recommendations = []

        if near_completion_goals:
            recommendations.append(f"Focus on completing {len(near_completion_goals)} goals that are near completion")

        if stagnant_goals:
            recommendations.append(f"Review and adjust {len(stagnant_goals)} stagnant goals - consider breaking them into smaller steps")

        if len(active_goals) > 5:
            recommendations.append("Consider focusing on fewer goals simultaneously for better progress")

        if not active_goals:
            recommendations.append("Set new therapeutic goals to maintain progress momentum")

        # Check for goal balance
        easy_goals = sum(1 for g in active_goals if len(g.target_behaviors) <= 2)
        hard_goals = sum(1 for g in active_goals if len(g.target_behaviors) > 4)

        if easy_goals == 0 and hard_goals > 0:
            recommendations.append("Add some easier goals to build confidence and momentum")
        elif hard_goals == 0 and easy_goals > 2:
            recommendations.append("Consider adding more challenging goals to accelerate growth")

        return recommendations


class ProgressTrackingPersonalization:
    """Main class for progress monitoring and personalization."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the progress tracking and personalization system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.progress_analyzer = TherapeuticProgressAnalyzer()
        self.emotional_tracker = EmotionalGrowthTracker()
        self.goal_monitor = GoalAchievementMonitor()

        # Storage for progress metrics (in production, this would be database-backed)
        self.progress_metrics: dict[str, list[ProgressMetric]] = defaultdict(list)
        self.personalization_profiles: dict[str, PersonalizationProfile] = {}

        logger.info("ProgressTrackingPersonalization system initialized")

    def track_therapeutic_progress(self, user_id: str, session_data: SessionState) -> dict[str, Any]:
        """Track therapeutic progress from session data."""
        try:
            # Extract progress metrics from session
            metrics = self._extract_progress_metrics(user_id, session_data)

            # Store metrics
            self.progress_metrics[user_id].extend(metrics)

            # Analyze current progress
            analysis_result = self._analyze_user_progress(user_id)

            # Update personalization profile
            self._update_personalization_profile(user_id, session_data, analysis_result)

            logger.info(f"Tracked therapeutic progress for user {user_id}")
            return {
                "metrics_recorded": len(metrics),
                "overall_progress_score": analysis_result.overall_progress_score,
                "analysis_confidence": analysis_result.confidence_level,
                "next_focus": analysis_result.next_therapeutic_focus
            }

        except Exception as e:
            logger.error(f"Error tracking therapeutic progress for user {user_id}: {e}")
            return {"error": str(e)}

    def _extract_progress_metrics(self, user_id: str, session_data: SessionState) -> list[ProgressMetric]:
        """Extract progress metrics from session data."""
        metrics = []

        if not session_data.therapeutic_progress:
            return metrics

        progress = session_data.therapeutic_progress

        # Goal achievement metric
        if progress.therapeutic_goals:
            avg_goal_progress = statistics.mean([g.progress_percentage for g in progress.therapeutic_goals]) / 100.0
            metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.GOAL_ACHIEVEMENT,
                value=avg_goal_progress,
                raw_value=avg_goal_progress * 100,
                measurement_context="Average goal progress",
                session_id=session_data.session_id
            ))

        # Intervention effectiveness metric
        if progress.completed_interventions:
            recent_interventions = [i for i in progress.completed_interventions
                                  if (datetime.now() - i.completed_at).days <= 7]
            if recent_interventions:
                avg_effectiveness = statistics.mean([i.effectiveness_rating for i in recent_interventions]) / 10.0
                metrics.append(ProgressMetric(
                    metric_type=ProgressMetricType.INTERVENTION_EFFECTIVENESS,
                    value=avg_effectiveness,
                    raw_value=avg_effectiveness * 10,
                    measurement_context="Recent intervention effectiveness",
                    session_id=session_data.session_id
                ))

        # Coping skills usage metric
        if progress.coping_strategies_learned:
            active_strategies = [s for s in progress.coping_strategies_learned if s.usage_count > 0]
            usage_ratio = len(active_strategies) / len(progress.coping_strategies_learned)
            metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.COPING_SKILLS_USAGE,
                value=usage_ratio,
                raw_value=len(active_strategies),
                measurement_context="Coping strategies utilization",
                session_id=session_data.session_id
            ))

        # Emotional regulation metric
        if session_data.emotional_state:
            # Higher regulation = lower intensity for negative emotions
            emotional_state = session_data.emotional_state
            negative_emotions = {EmotionalStateType.ANXIOUS, EmotionalStateType.DEPRESSED,
                               EmotionalStateType.ANGRY, EmotionalStateType.OVERWHELMED}

            if emotional_state.primary_emotion in negative_emotions:
                regulation_score = 1.0 - emotional_state.intensity
            else:
                regulation_score = 0.5 + (emotional_state.intensity * 0.5)  # Positive emotions are good

            metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.EMOTIONAL_REGULATION,
                value=regulation_score,
                raw_value=emotional_state.intensity,
                measurement_context=f"Emotional state: {emotional_state.primary_emotion.value}",
                session_id=session_data.session_id
            ))

        # Engagement level metric (based on session activity)
        engagement_indicators = [
            len(session_data.user_inventory),
            len(session_data.character_states),
            session_data.narrative_position
        ]
        engagement_score = min(1.0, sum(engagement_indicators) / 10.0)  # Normalize
        metrics.append(ProgressMetric(
            metric_type=ProgressMetricType.ENGAGEMENT_LEVEL,
            value=engagement_score,
            raw_value=sum(engagement_indicators),
            measurement_context="Session engagement indicators",
            session_id=session_data.session_id
        ))

        return metrics

    def _analyze_user_progress(self, user_id: str,
                             timeframe: tuple[datetime, datetime] | None = None) -> ProgressAnalysisResult:
        """Analyze user's therapeutic progress."""
        user_metrics = self.progress_metrics.get(user_id, [])

        if not user_metrics:
            return ProgressAnalysisResult(
                user_id=user_id,
                overall_progress_score=0.0,
                next_therapeutic_focus="Begin therapeutic journey",
                confidence_level=0.0
            )

        # Analyze progress metrics
        metric_analysis = self.progress_analyzer.analyze_progress_metrics(user_metrics, timeframe)

        # Calculate overall progress score
        overall_score = self.progress_analyzer.calculate_overall_progress_score(metric_analysis)

        # Identify achievements and improvement areas
        achievements = self.progress_analyzer.identify_achievement_highlights(metric_analysis)
        improvements = self.progress_analyzer.identify_improvement_areas(metric_analysis)

        # Determine next therapeutic focus
        next_focus = self._determine_next_therapeutic_focus(metric_analysis, improvements)

        # Generate recommended interventions
        recommended_interventions = self._recommend_interventions(metric_analysis, improvements)

        return ProgressAnalysisResult(
            user_id=user_id,
            overall_progress_score=overall_score,
            metric_trends=metric_analysis,
            achievement_highlights=achievements,
            areas_for_improvement=improvements,
            recommended_interventions=recommended_interventions,
            next_therapeutic_focus=next_focus,
            confidence_level=min(1.0, len(user_metrics) / 20.0)  # More data = higher confidence
        )

    def _determine_next_therapeutic_focus(self, metric_analysis: dict[ProgressMetricType, dict[str, float]],
                                        improvement_areas: list[str]) -> str:
        """Determine the next therapeutic focus area."""
        if not metric_analysis:
            return "Establish therapeutic baseline and initial goals"

        # Find the metric with the lowest current value
        lowest_metric = None
        lowest_value = 1.0

        for metric_type, analysis in metric_analysis.items():
            current_value = analysis.get("current_value", 0.0)
            if current_value < lowest_value:
                lowest_value = current_value
                lowest_metric = metric_type

        if lowest_metric:
            focus_mapping = {
                ProgressMetricType.EMOTIONAL_REGULATION: "Emotional regulation and mindfulness practices",
                ProgressMetricType.COPING_SKILLS_USAGE: "Developing and practicing coping strategies",
                ProgressMetricType.GOAL_ACHIEVEMENT: "Goal setting and achievement strategies",
                ProgressMetricType.INTERVENTION_EFFECTIVENESS: "Optimizing therapeutic intervention approaches",
                ProgressMetricType.ENGAGEMENT_LEVEL: "Increasing therapeutic engagement and motivation",
                ProgressMetricType.RESILIENCE_BUILDING: "Building resilience and stress management skills",
                ProgressMetricType.SELF_AWARENESS: "Developing self-awareness and insight",
                ProgressMetricType.RELATIONSHIP_QUALITY: "Improving interpersonal relationships"
            }
            return focus_mapping.get(lowest_metric, "Comprehensive therapeutic support")

        return "Maintaining therapeutic progress and exploring advanced techniques"

    def _recommend_interventions(self, metric_analysis: dict[ProgressMetricType, dict[str, float]],
                               improvement_areas: list[str]) -> list[InterventionType]:
        """Recommend therapeutic interventions based on analysis."""
        recommendations = []

        for metric_type, analysis in metric_analysis.items():
            current_value = analysis.get("current_value", 0.0)
            trend_slope = analysis.get("trend_slope", 0.0)

            # Recommend interventions for low-performing or declining metrics
            if current_value < 0.5 or trend_slope < -0.001:
                intervention_mapping = {
                    ProgressMetricType.EMOTIONAL_REGULATION: InterventionType.MINDFULNESS,
                    ProgressMetricType.COPING_SKILLS_USAGE: InterventionType.COPING_SKILLS,
                    ProgressMetricType.GOAL_ACHIEVEMENT: InterventionType.BEHAVIORAL_ACTIVATION,
                    ProgressMetricType.INTERVENTION_EFFECTIVENESS: InterventionType.COGNITIVE_RESTRUCTURING,
                    ProgressMetricType.ENGAGEMENT_LEVEL: InterventionType.BEHAVIORAL_ACTIVATION,
                    ProgressMetricType.RESILIENCE_BUILDING: InterventionType.COPING_SKILLS,
                    ProgressMetricType.SELF_AWARENESS: InterventionType.COGNITIVE_RESTRUCTURING,
                    ProgressMetricType.RELATIONSHIP_QUALITY: InterventionType.EMOTIONAL_REGULATION
                }

                intervention = intervention_mapping.get(metric_type)
                if intervention and intervention not in recommendations:
                    recommendations.append(intervention)

        # Limit to top 3 recommendations
        return recommendations[:3]

    def _update_personalization_profile(self, user_id: str, session_data: SessionState,
                                      analysis_result: ProgressAnalysisResult) -> None:
        """Update user's personalization profile based on progress analysis."""
        profile = self.personalization_profiles.get(user_id)

        if not profile:
            profile = PersonalizationProfile(user_id=user_id)
            self.personalization_profiles[user_id] = profile

        # Update learning velocity based on progress trends
        if analysis_result.metric_trends:
            avg_improvement = statistics.mean([
                analysis.get("improvement_rate", 0.0)
                for analysis in analysis_result.metric_trends.values()
            ])
            profile.learning_velocity = max(0.1, min(1.0, 0.5 + avg_improvement))

        # Update preferred intervention types based on effectiveness
        if session_data.therapeutic_progress and session_data.therapeutic_progress.completed_interventions:
            effective_interventions = [
                intervention.intervention_type
                for intervention in session_data.therapeutic_progress.completed_interventions
                if intervention.effectiveness_rating >= 7.0
            ]
            profile.preferred_intervention_types = list(set(effective_interventions))

        # Update engagement patterns
        engagement_score = next(
            (analysis.get("current_value", 0.0)
             for metric_type, analysis in analysis_result.metric_trends.items()
             if metric_type == ProgressMetricType.ENGAGEMENT_LEVEL),
            0.5
        )

        if "engagement" not in profile.engagement_patterns:
            profile.engagement_patterns["engagement"] = []
        profile.engagement_patterns["engagement"].append(engagement_score)

        # Keep only recent engagement data (last 10 sessions)
        if len(profile.engagement_patterns["engagement"]) > 10:
            profile.engagement_patterns["engagement"] = profile.engagement_patterns["engagement"][-10:]

        profile.last_updated = datetime.now()
        profile.validate()

    def analyze_user_patterns(self, user_id: str, timeframe: tuple[datetime, datetime] | None = None) -> dict[str, Any]:
        """Analyze user patterns and behaviors."""
        try:
            user_metrics = self.progress_metrics.get(user_id, [])

            if not user_metrics:
                return {"error": "No data available for pattern analysis"}

            # Filter by timeframe if provided
            if timeframe:
                start_time, end_time = timeframe
                user_metrics = [m for m in user_metrics if start_time <= m.timestamp <= end_time]

            # Analyze patterns
            patterns = {
                "progress_trends": self.progress_analyzer.analyze_progress_metrics(user_metrics, timeframe),
                "temporal_patterns": self._analyze_temporal_patterns(user_metrics),
                "intervention_patterns": self._analyze_intervention_patterns(user_id),
                "engagement_patterns": self._analyze_engagement_patterns(user_metrics),
                "personalization_insights": self._generate_personalization_insights(user_id)
            }

            logger.info(f"Analyzed patterns for user {user_id}")
            return patterns

        except Exception as e:
            logger.error(f"Error analyzing patterns for user {user_id}: {e}")
            return {"error": str(e)}

    def _analyze_temporal_patterns(self, metrics: list[ProgressMetric]) -> dict[str, Any]:
        """Analyze temporal patterns in user progress."""
        if not metrics:
            return {}

        # Group metrics by hour of day and day of week
        hourly_patterns = defaultdict(list)
        daily_patterns = defaultdict(list)

        for metric in metrics:
            hour = metric.timestamp.hour
            day = metric.timestamp.strftime("%A")

            hourly_patterns[hour].append(metric.value)
            daily_patterns[day].append(metric.value)

        # Calculate average performance by time
        hourly_avg = {hour: statistics.mean(values) for hour, values in hourly_patterns.items()}
        daily_avg = {day: statistics.mean(values) for day, values in daily_patterns.items()}

        # Find optimal times
        best_hour = max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else (12, 0.5)
        best_day = max(daily_avg.items(), key=lambda x: x[1]) if daily_avg else ("Monday", 0.5)

        return {
            "hourly_performance": hourly_avg,
            "daily_performance": daily_avg,
            "optimal_hour": best_hour[0],
            "optimal_day": best_day[0],
            "performance_variance": {
                "hourly": statistics.stdev(hourly_avg.values()) if len(hourly_avg) > 1 else 0.0,
                "daily": statistics.stdev(daily_avg.values()) if len(daily_avg) > 1 else 0.0
            }
        }

    def _analyze_intervention_patterns(self, user_id: str) -> dict[str, Any]:
        """Analyze patterns in intervention effectiveness."""
        # This would typically query intervention history from database
        # For now, return a simplified analysis
        return {
            "most_effective_interventions": ["mindfulness", "cognitive_restructuring"],
            "least_effective_interventions": ["exposure_therapy"],
            "intervention_frequency": {"mindfulness": 5, "cognitive_restructuring": 3},
            "effectiveness_trends": {"improving": ["mindfulness"], "stable": ["cognitive_restructuring"]}
        }

    def _analyze_engagement_patterns(self, metrics: list[ProgressMetric]) -> dict[str, Any]:
        """Analyze user engagement patterns."""
        engagement_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.ENGAGEMENT_LEVEL]

        if not engagement_metrics:
            return {}

        engagement_values = [m.value for m in engagement_metrics]

        return {
            "average_engagement": statistics.mean(engagement_values),
            "engagement_trend": self.progress_analyzer._calculate_trend_slope(
                [m.timestamp.timestamp() for m in engagement_metrics],
                engagement_values
            ),
            "engagement_consistency": 1.0 - (statistics.stdev(engagement_values) if len(engagement_values) > 1 else 0.0),
            "peak_engagement_periods": self._identify_peak_engagement_periods(engagement_metrics)
        }

    def _identify_peak_engagement_periods(self, engagement_metrics: list[ProgressMetric]) -> list[dict[str, Any]]:
        """Identify periods of peak engagement."""
        if len(engagement_metrics) < 3:
            return []

        # Sort by timestamp
        engagement_metrics.sort(key=lambda x: x.timestamp)

        # Find periods where engagement is above average
        avg_engagement = statistics.mean([m.value for m in engagement_metrics])
        peak_periods = []

        current_period = None
        for metric in engagement_metrics:
            if metric.value > avg_engagement + 0.1:  # 10% above average
                if current_period is None:
                    current_period = {"start": metric.timestamp, "values": [metric.value]}
                else:
                    current_period["values"].append(metric.value)
                    current_period["end"] = metric.timestamp
            else:
                if current_period is not None:
                    current_period["average_engagement"] = statistics.mean(current_period["values"])
                    current_period["duration_hours"] = (current_period["end"] - current_period["start"]).total_seconds() / 3600
                    peak_periods.append(current_period)
                    current_period = None

        # Handle ongoing period
        if current_period is not None:
            current_period["end"] = engagement_metrics[-1].timestamp
            current_period["average_engagement"] = statistics.mean(current_period["values"])
            current_period["duration_hours"] = (current_period["end"] - current_period["start"]).total_seconds() / 3600
            peak_periods.append(current_period)

        return peak_periods

    def _generate_personalization_insights(self, user_id: str) -> dict[str, Any]:
        """Generate insights for personalization."""
        profile = self.personalization_profiles.get(user_id)

        if not profile:
            return {"message": "Insufficient data for personalization insights"}

        insights = {
            "learning_velocity": profile.learning_velocity,
            "optimal_session_length": profile.optimal_session_length,
            "preferred_interventions": [intervention.value for intervention in profile.preferred_intervention_types],
            "engagement_stability": self._calculate_engagement_stability(profile),
            "personalization_recommendations": self._generate_personalization_recommendations(profile)
        }

        return insights

    def _calculate_engagement_stability(self, profile: PersonalizationProfile) -> float:
        """Calculate engagement stability score."""
        engagement_history = profile.engagement_patterns.get("engagement", [])

        if len(engagement_history) < 2:
            return 0.5  # Neutral stability

        stability = 1.0 - statistics.stdev(engagement_history)
        return max(0.0, min(1.0, stability))

    def _generate_personalization_recommendations(self, profile: PersonalizationProfile) -> list[str]:
        """Generate personalization recommendations."""
        recommendations = []

        if profile.learning_velocity < 0.3:
            recommendations.append("Slow down content delivery and provide more reinforcement")
        elif profile.learning_velocity > 0.7:
            recommendations.append("Increase content complexity and introduce advanced concepts")

        if profile.optimal_session_length < 20:
            recommendations.append("Use shorter, more focused therapeutic interventions")
        elif profile.optimal_session_length > 45:
            recommendations.append("Leverage longer sessions for deeper therapeutic work")

        engagement_stability = self._calculate_engagement_stability(profile)
        if engagement_stability < 0.5:
            recommendations.append("Focus on consistency and routine to improve engagement stability")

        return recommendations

    def recommend_next_steps(self, user_id: str, current_progress: ProgressAnalysisResult | None = None) -> list[dict[str, Any]]:
        """Recommend next therapeutic steps for the user."""
        try:
            if not current_progress:
                current_progress = self._analyze_user_progress(user_id)

            recommendations = []

            # Priority 1: Address critical improvement areas
            for area in current_progress.areas_for_improvement[:2]:
                recommendations.append({
                    "type": "improvement_focus",
                    "priority": "high",
                    "title": f"Focus on {area}",
                    "description": f"Dedicate attention to improving {area.lower()}",
                    "estimated_duration": "2-3 sessions",
                    "expected_impact": "high"
                })

            # Priority 2: Leverage strengths
            for achievement in current_progress.achievement_highlights[:1]:
                recommendations.append({
                    "type": "strength_building",
                    "priority": "medium",
                    "title": f"Build on {achievement}",
                    "description": f"Continue developing this strength: {achievement.lower()}",
                    "estimated_duration": "1-2 sessions",
                    "expected_impact": "medium"
                })

            # Priority 3: Try recommended interventions
            for intervention in current_progress.recommended_interventions[:2]:
                recommendations.append({
                    "type": "intervention",
                    "priority": "medium",
                    "title": f"Try {intervention.value.replace('_', ' ').title()}",
                    "description": f"Explore {intervention.value.replace('_', ' ')} techniques",
                    "estimated_duration": "1 session",
                    "expected_impact": "medium"
                })

            # Priority 4: Personalization adjustments
            profile = self.personalization_profiles.get(user_id)
            if profile:
                personalization_recs = self._generate_personalization_recommendations(profile)
                for rec in personalization_recs[:1]:
                    recommendations.append({
                        "type": "personalization",
                        "priority": "low",
                        "title": "Adjust Approach",
                        "description": rec,
                        "estimated_duration": "Ongoing",
                        "expected_impact": "low"
                    })

            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return [{"type": "error", "description": str(e)}]


# Utility functions for testing and validation
def create_sample_progress_data(user_id: str, days: int = 30) -> list[ProgressMetric]:
    """Create sample progress data for testing."""
    import random

    metrics = []
    base_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        current_date = base_date + timedelta(days=day)

        # Simulate improving progress over time with some variance
        progress_factor = (day / days) * 0.6 + 0.2  # 0.2 to 0.8 range

        for metric_type in ProgressMetricType:
            if random.random() < 0.7:  # 70% chance of having data for each metric type
                value = max(0.0, min(1.0, progress_factor + random.gauss(0, 0.1)))

                metrics.append(ProgressMetric(
                    metric_type=metric_type,
                    value=value,
                    timestamp=current_date + timedelta(hours=random.randint(8, 20)),
                    confidence_level=random.uniform(0.6, 0.9)
                ))

    return metrics


if __name__ == "__main__":
    # Test the progress tracking system
    logging.basicConfig(level=logging.INFO)

    # Create test instance
    progress_system = ProgressTrackingPersonalization()

    # Create sample data
    test_user_id = "test_user_123"
    sample_metrics = create_sample_progress_data(test_user_id, 30)

    # Store sample metrics
    progress_system.progress_metrics[test_user_id] = sample_metrics

    # Test progress analysis
    analysis = progress_system._analyze_user_progress(test_user_id)
    print(f"Overall Progress Score: {analysis.overall_progress_score:.2f}")
    print(f"Achievement Highlights: {analysis.achievement_highlights}")
    print(f"Areas for Improvement: {analysis.areas_for_improvement}")
    print(f"Next Focus: {analysis.next_therapeutic_focus}")

    # Test pattern analysis
    patterns = progress_system.analyze_user_patterns(test_user_id)
    print(f"Temporal Patterns: {patterns.get('temporal_patterns', {})}")

    # Test recommendations
    recommendations = progress_system.recommend_next_steps(test_user_id, analysis)
    print(f"Recommendations: {len(recommendations)} generated")
    for rec in recommendations:
        print(f"  - {rec['title']}: {rec['description']}")

    print("Progress tracking system test completed successfully!")
