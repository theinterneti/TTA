"""
Progress tracking and analytics data models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .enums import TherapeuticApproach


@dataclass
class ProgressVizSeries:
    """Visualization-friendly time series for progress charts."""

    time_buckets: list[str] = field(default_factory=list)
    series: dict[str, list[float]] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class TherapeuticMetric:
    """Individual therapeutic effectiveness metric."""

    metric_name: str
    value: float
    unit: str
    measured_at: datetime
    confidence_level: float = 0.8  # 0.0 to 1.0

    def __post_init__(self):
        """Validate therapeutic metric after initialization."""
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValueError("Confidence level must be between 0.0 and 1.0")


@dataclass
class ProgressHighlight:
    """Significant progress achievement or insight."""

    highlight_id: str
    title: str
    description: str
    highlight_type: str  # breakthrough, milestone, insight, skill_development
    achieved_at: datetime
    related_character_id: str | None = None
    related_world_id: str | None = None
    therapeutic_value: float = 0.0  # 0.0 to 1.0
    celebration_shown: bool = False

    def __post_init__(self):
        """Validate progress highlight after initialization."""
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValueError("Therapeutic value must be between 0.0 and 1.0")


@dataclass
class Milestone:
    """Therapeutic milestone with progress tracking."""

    milestone_id: str
    title: str
    description: str
    target_date: datetime | None = None
    achieved_date: datetime | None = None
    progress_percentage: float = 0.0
    required_actions: list[str] = field(default_factory=list)
    completed_actions: list[str] = field(default_factory=list)
    therapeutic_approaches_involved: list[TherapeuticApproach] = field(
        default_factory=list
    )
    reward_description: str = ""
    is_achieved: bool = False

    def __post_init__(self):
        """Validate milestone after initialization."""
        if not 0.0 <= self.progress_percentage <= 100.0:
            raise ValueError("Progress percentage must be between 0.0 and 100.0")

        if self.is_achieved and self.achieved_date is None:
            self.achieved_date = datetime.now()

    def add_completed_action(self, action: str) -> None:
        """Mark an action as completed and update progress."""
        if action in self.required_actions and action not in self.completed_actions:
            self.completed_actions.append(action)
            self._update_progress()

    def _update_progress(self) -> None:
        """Update progress percentage based on completed actions."""
        if self.required_actions:
            self.progress_percentage = (
                len(self.completed_actions) / len(self.required_actions)
            ) * 100.0

            if self.progress_percentage >= 100.0 and not self.is_achieved:
                self.is_achieved = True
                self.achieved_date = datetime.now()


@dataclass
class EngagementMetrics:
    """Player engagement and participation metrics."""

    total_sessions: int = 0
    total_time_minutes: int = 0
    average_session_length: float = 0.0
    sessions_this_week: int = 0
    sessions_this_month: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_session_date: datetime | None = None
    preferred_session_times: list[str] = field(default_factory=list)  # hour ranges
    dropout_risk_score: float = 0.0  # 0.0 to 1.0, higher = more risk

    def __post_init__(self):
        """Validate engagement metrics after initialization."""
        if not 0.0 <= self.dropout_risk_score <= 1.0:
            raise ValueError("Dropout risk score must be between 0.0 and 1.0")

    def update_session_stats(self, session_duration_minutes: int) -> None:
        """Update engagement metrics with new session data."""
        self.total_sessions += 1
        self.total_time_minutes += session_duration_minutes
        self.average_session_length = self.total_time_minutes / self.total_sessions
        self.last_session_date = datetime.now()

        # Update streak
        if self.last_session_date:
            days_since_last = (datetime.now() - self.last_session_date).days
            if days_since_last <= 1:
                self.current_streak_days += 1
                self.longest_streak_days = max(
                    self.longest_streak_days, self.current_streak_days
                )
            else:
                self.current_streak_days = 1


@dataclass
class TherapeuticEffectivenessReport:
    """Report on therapeutic effectiveness for a player."""

    player_id: str
    character_id: str | None = None
    report_period_start: datetime = field(
        default_factory=lambda: datetime.now() - timedelta(days=30)
    )
    report_period_end: datetime = field(default_factory=datetime.now)

    # Effectiveness metrics
    overall_effectiveness_score: float = 0.0  # 0.0 to 1.0
    therapeutic_metrics: list[TherapeuticMetric] = field(default_factory=list)
    most_effective_approaches: list[TherapeuticApproach] = field(default_factory=list)
    least_effective_approaches: list[TherapeuticApproach] = field(default_factory=list)

    # Progress indicators
    goals_achieved: int = 0
    goals_in_progress: int = 0
    milestones_reached: int = 0
    breakthrough_moments: int = 0

    # Behavioral changes
    emotional_regulation_improvement: float = 0.0  # -1.0 to 1.0
    coping_skills_development: float = 0.0  # -1.0 to 1.0
    self_awareness_growth: float = 0.0  # -1.0 to 1.0

    # Recommendations
    recommended_adjustments: list[str] = field(default_factory=list)
    suggested_next_steps: list[str] = field(default_factory=list)

    generated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate therapeutic effectiveness report after initialization."""
        if not 0.0 <= self.overall_effectiveness_score <= 1.0:
            raise ValueError("Overall effectiveness score must be between 0.0 and 1.0")

        for improvement in [
            self.emotional_regulation_improvement,
            self.coping_skills_development,
            self.self_awareness_growth,
        ]:
            if not -1.0 <= improvement <= 1.0:
                raise ValueError("Improvement scores must be between -1.0 and 1.0")


@dataclass
class ProgressSummary:
    """Comprehensive progress summary for a player."""

    player_id: str

    # Basic statistics
    engagement_metrics: EngagementMetrics = field(default_factory=EngagementMetrics)

    # Progress tracking
    milestones_achieved: list[Milestone] = field(default_factory=list)
    active_milestones: list[Milestone] = field(default_factory=list)
    recent_highlights: list[ProgressHighlight] = field(default_factory=list)

    # Therapeutic insights
    favorite_therapeutic_approach: TherapeuticApproach | None = None
    most_effective_world_type: str | None = None
    therapeutic_momentum: float = 0.5  # 0.0 to 1.0
    readiness_for_advancement: float = 0.5  # 0.0 to 1.0

    # Trends and patterns
    progress_trend: str = "stable"  # improving, stable, declining
    engagement_trend: str = "stable"  # increasing, stable, decreasing
    challenge_areas: list[str] = field(default_factory=list)
    strength_areas: list[str] = field(default_factory=list)

    # Future planning
    next_recommended_goals: list[str] = field(default_factory=list)
    suggested_therapeutic_adjustments: list[str] = field(default_factory=list)

    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate progress summary after initialization."""
        if not 0.0 <= self.therapeutic_momentum <= 1.0:
            raise ValueError("Therapeutic momentum must be between 0.0 and 1.0")

        if not 0.0 <= self.readiness_for_advancement <= 1.0:
            raise ValueError("Readiness for advancement must be between 0.0 and 1.0")

        valid_trends = ["improving", "stable", "declining"]
        if self.progress_trend not in valid_trends:
            raise ValueError(f"Progress trend must be one of: {valid_trends}")

        valid_engagement_trends = ["increasing", "stable", "decreasing"]
        if self.engagement_trend not in valid_engagement_trends:
            raise ValueError(
                f"Engagement trend must be one of: {valid_engagement_trends}"
            )

    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone to tracking."""
        if milestone.is_achieved:
            self.milestones_achieved.append(milestone)
        else:
            self.active_milestones.append(milestone)

    def achieve_milestone(self, milestone_id: str) -> None:
        """Move a milestone from active to achieved."""
        for i, milestone in enumerate(self.active_milestones):
            if milestone.milestone_id == milestone_id:
                milestone.is_achieved = True
                milestone.achieved_date = datetime.now()
                achieved_milestone = self.active_milestones.pop(i)
                self.milestones_achieved.append(achieved_milestone)
                break

    def add_progress_highlight(self, highlight: ProgressHighlight) -> None:
        """Add a progress highlight."""
        self.recent_highlights.append(highlight)

        # Keep only the most recent 10 highlights
        self.recent_highlights = sorted(
            self.recent_highlights, key=lambda h: h.achieved_at, reverse=True
        )[:10]

    def calculate_overall_progress_score(self) -> float:
        """Calculate an overall progress score based on various factors."""
        factors = []

        # Milestone achievement rate
        total_milestones = len(self.milestones_achieved) + len(self.active_milestones)
        if total_milestones > 0:
            milestone_score = len(self.milestones_achieved) / total_milestones
            factors.append(milestone_score * 0.4)

        # Therapeutic momentum
        factors.append(self.therapeutic_momentum * 0.3)

        # Engagement consistency
        engagement_score = min(1.0, self.engagement_metrics.current_streak_days / 30.0)
        factors.append(engagement_score * 0.3)

        return sum(factors) if factors else 0.0
