"""
Progress Tracking Service.

Aggregates session data and progress markers to compute summaries, detect milestones,
produce insights/recommendations, and provide visualization-friendly series.

Enhanced with therapeutic component integration, sophisticated milestone detection,
and comprehensive progress insight generation.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from ..database.session_repository import SessionRepository
from ..models.enums import ProgressMarkerType, TherapeuticApproach
from ..models.progress import (
    EngagementMetrics,
    Milestone,
    ProgressHighlight,
    ProgressSummary,
    ProgressVizSeries,
    TherapeuticEffectivenessReport,
    TherapeuticMetric,
)
from ..models.session import Recommendation, SessionContext, SessionSummary

logger = logging.getLogger(__name__)


class ProgressTrackingService:
    """
    Service for progress tracking and analytics.

    Enhanced with therapeutic component integration, sophisticated milestone detection,
    achievement celebration, and comprehensive progress insight generation.
    """

    def __init__(self, session_repository: SessionRepository, therapeutic_engine=None):
        self.session_repository = session_repository
        self.therapeutic_engine = (
            therapeutic_engine  # Optional integration with therapeutic components
        )

        # Milestone thresholds for achievement detection
        self.milestone_thresholds = {
            "engagement_streak": [3, 7, 14, 30, 60],  # days
            "session_count": [5, 10, 25, 50, 100],
            "total_time": [60, 180, 360, 720, 1440],  # minutes
            "skills_acquired": [3, 5, 10, 20, 35],
            "breakthroughs": [1, 3, 5, 10, 15],
            "therapeutic_goals": [1, 3, 5, 8, 12],
        }

        # Therapeutic effectiveness thresholds
        self.effectiveness_thresholds = {
            "high_effectiveness": 0.8,
            "moderate_effectiveness": 0.6,
            "improvement_needed": 0.4,
        }

    async def compute_progress_summary(
        self, player_id: str, *, summaries_limit: int = 30
    ) -> ProgressSummary:
        """
        Compute a comprehensive ProgressSummary for a player by aggregating sessions and markers.
        Enhanced with therapeutic component integration and sophisticated analytics.
        """
        # Gather recent session summaries and active sessions
        summaries: list[
            SessionSummary
        ] = await self.session_repository.get_session_summaries(
            player_id, summaries_limit
        )
        active_sessions: list[
            SessionContext
        ] = await self.session_repository.get_player_active_sessions(player_id)

        # Initialize metrics and collections
        engagement = EngagementMetrics()
        milestones_achieved: list[Milestone] = []
        active_milestones: list[Milestone] = []
        highlights: list[ProgressHighlight] = []

        # Enhanced engagement metrics calculation
        total_minutes = 0
        therapeutic_approaches_used = Counter()
        session_dates = []

        for s in summaries:
            engagement.total_sessions += 1
            total_minutes += max(0, s.duration_minutes)
            session_dates.append(s.start_time.date())

            # Track therapeutic approaches if available
            if hasattr(s, "therapeutic_approaches_used"):
                for approach in s.therapeutic_approaches_used:  # type: ignore[attr-defined]
                    therapeutic_approaches_used[approach] += 1

            # Enhanced highlight collection with therapeutic value assessment
            if s.key_achievements:
                for title in s.key_achievements:
                    therapeutic_value = self._assess_therapeutic_value(title, s)
                    highlights.append(
                        ProgressHighlight(
                            highlight_id=f"hl_{player_id}_{s.session_id}_{title[:8]}",
                            title=title,
                            description=self._enhance_achievement_description(title, s),
                            highlight_type="achievement",
                            achieved_at=s.end_time or s.start_time,
                            therapeutic_value=therapeutic_value,
                        )
                    )

        # Calculate engagement metrics
        engagement.total_time_minutes = total_minutes
        engagement.average_session_length = (
            (total_minutes / engagement.total_sessions)
            if engagement.total_sessions
            else 0.0
        )
        engagement.last_session_date = max(session_dates) if session_dates else None

        # Enhanced streak calculation
        engagement.current_streak_days = self._calculate_current_streak(session_dates)
        engagement.longest_streak_days = self._calculate_longest_streak(session_dates)

        # Calculate weekly and monthly sessions
        now_date = datetime.utcnow().date()
        week_ago = now_date - timedelta(days=7)
        month_ago = now_date - timedelta(days=30)

        engagement.sessions_this_week = sum(
            1 for date in session_dates if date >= week_ago
        )
        engagement.sessions_this_month = sum(
            1 for date in session_dates if date >= month_ago
        )

        # Calculate dropout risk
        engagement.dropout_risk_score = self._calculate_dropout_risk(
            engagement, session_dates
        )

        # Analyze progress markers from active sessions
        marker_analysis = self._analyze_progress_markers(active_sessions)
        marker_analysis["skills_acquired"]
        marker_analysis["breakthroughs"]
        marker_analysis["therapeutic_goals"]

        # Detect and create milestones
        (
            new_milestones,
            milestone_highlights,
        ) = await self._detect_comprehensive_milestones(
            player_id, engagement, marker_analysis, summaries
        )
        milestones_achieved.extend(new_milestones)
        highlights.extend(milestone_highlights)

        # Build comprehensive summary
        summary = ProgressSummary(
            player_id=player_id,
            engagement_metrics=engagement,
            milestones_achieved=milestones_achieved,
            active_milestones=active_milestones,
            recent_highlights=highlights,
        )

        # Enhanced trend analysis
        summary.progress_trend = self._analyze_progress_trend(
            marker_analysis, engagement
        )
        summary.engagement_trend = self._analyze_engagement_trend(
            session_dates, engagement
        )

        # Therapeutic insights
        summary.favorite_therapeutic_approach = (
            therapeutic_approaches_used.most_common(1)[0][0]
            if therapeutic_approaches_used
            else None
        )
        summary.therapeutic_momentum = self._calculate_therapeutic_momentum(
            marker_analysis, engagement
        )
        summary.readiness_for_advancement = self._calculate_readiness_for_advancement(
            summary
        )

        # Identify strengths and challenges
        summary.strength_areas = self._identify_strength_areas(
            marker_analysis, engagement
        )
        summary.challenge_areas = self._identify_challenge_areas(
            marker_analysis, engagement
        )

        # Generate future planning recommendations
        summary.next_recommended_goals = self._generate_next_goals(
            summary, marker_analysis
        )
        summary.suggested_therapeutic_adjustments = (
            self._suggest_therapeutic_adjustments(summary)
        )

        summary.last_updated = datetime.now()
        return summary

    async def detect_and_update_milestones(
        self, player_id: str
    ) -> tuple[list[Milestone], list[ProgressHighlight]]:
        """
        Detect milestones from current activity and return new milestones and highlights.
        Enhanced with comprehensive milestone detection and achievement celebration.
        """
        summaries: list[
            SessionSummary
        ] = await self.session_repository.get_session_summaries(player_id, 90)
        active_sessions: list[
            SessionContext
        ] = await self.session_repository.get_player_active_sessions(player_id)

        # Calculate engagement metrics
        session_dates = [s.start_time.date() for s in summaries]
        current_streak_days = self._calculate_current_streak(session_dates)
        total_sessions = len(summaries)
        total_time = sum(s.duration_minutes for s in summaries)

        # Analyze progress markers
        marker_analysis = self._analyze_progress_markers(active_sessions)

        # Use the comprehensive milestone detection
        engagement_metrics = EngagementMetrics(
            total_sessions=total_sessions,
            total_time_minutes=total_time,
            current_streak_days=current_streak_days,
        )

        new_milestones, highlights = await self._detect_comprehensive_milestones(
            player_id, engagement_metrics, marker_analysis, summaries
        )

        # Add achievement celebration enhancements
        for highlight in highlights:
            highlight.celebration_shown = False  # Mark for celebration display

        logger.info(
            f"Detected {len(new_milestones)} new milestones and {len(highlights)} highlights for player {player_id}"
        )

        return new_milestones, highlights

    async def generate_progress_insights(self, player_id: str) -> list[Recommendation]:
        """
        Generate comprehensive recommendations based on engagement, skill development,
        and therapeutic progress patterns.
        """
        summary = await self.compute_progress_summary(player_id)
        recs: list[Recommendation] = []

        # High momentum recommendations
        if (
            summary.engagement_metrics.current_streak_days >= 7
            and summary.therapeutic_momentum >= 0.7
        ):
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_advanced_techniques",
                    title="Ready for advanced therapeutic techniques",
                    description="Your consistent progress shows you're ready for more challenging therapeutic work. Consider exploring deeper techniques.",
                    recommendation_type="therapeutic_advancement",
                    priority=1,
                )
            )

        # Maintain momentum for good progress
        elif (
            summary.engagement_metrics.current_streak_days >= 3
            and summary.therapeutic_momentum >= 0.6
        ):
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_maintain_momentum",
                    title="Maintain your excellent pace",
                    description="Your engagement and momentum look strong. Keep going with your current routine to build on this progress.",
                    recommendation_type="therapeutic_approach",
                    priority=2,
                )
            )

        # Dropout risk interventions
        if summary.engagement_metrics.dropout_risk_score > 0.7:
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_engagement_support",
                    title="Let's reconnect with your therapeutic journey",
                    description="It looks like engagement has been challenging lately. Consider shorter, more manageable sessions to rebuild momentum.",
                    recommendation_type="engagement_support",
                    priority=1,
                )
            )
        elif summary.engagement_metrics.dropout_risk_score > 0.4:
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_flexible_schedule",
                    title="Try a more flexible approach",
                    description="Consider adjusting your session schedule or length to better fit your current needs and availability.",
                    recommendation_type="therapeutic_approach",
                    priority=2,
                )
            )

        # Skill development recommendations
        if "Skill Development" in summary.strength_areas:
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_skill_mastery",
                    title="Focus on skill mastery",
                    description="You're excelling at learning new skills. Consider practicing advanced applications of your acquired techniques.",
                    recommendation_type="skill_building",
                    priority=3,
                )
            )
        elif "Skill Acquisition" in summary.challenge_areas:
            recs.append(
                Recommendation(
                    recommendation_id=f"rec_{player_id}_skill_focus",
                    title="Strengthen skill-building foundation",
                    description="Focus on completing guided exercises and practicing therapeutic techniques to build your toolkit.",
                    recommendation_type="skill_building",
                    priority=2,
                )
            )

        # Sort by priority and return top recommendations
        recs.sort(key=lambda r: r.priority)
        return recs[:6]  # Return top 6 recommendations

    async def generate_therapeutic_effectiveness_report(
        self, player_id: str, character_id: str | None = None
    ) -> TherapeuticEffectivenessReport:
        """
        Generate a comprehensive therapeutic effectiveness report for a player.
        This integrates with therapeutic components to assess treatment outcomes.
        """
        now = datetime.utcnow()
        report_start = now - timedelta(days=30)

        # Get session data for analysis
        summaries = await self.session_repository.get_session_summaries(player_id, 60)
        active_sessions = await self.session_repository.get_player_active_sessions(
            player_id
        )

        # Calculate therapeutic metrics
        therapeutic_metrics = []

        # Engagement effectiveness
        engagement_score = min(
            1.0, len(summaries) / 20.0
        )  # Target: 20 sessions per month
        therapeutic_metrics.append(
            TherapeuticMetric(
                metric_name="engagement_consistency",
                value=engagement_score,
                unit="score",
                measured_at=now,
                confidence_level=0.9,
            )
        )

        # Skill acquisition rate
        marker_analysis = self._analyze_progress_markers(active_sessions)
        skill_rate = min(
            1.0, marker_analysis["skills_acquired"] / 10.0
        )  # Target: 10 skills
        therapeutic_metrics.append(
            TherapeuticMetric(
                metric_name="skill_acquisition_rate",
                value=skill_rate,
                unit="rate",
                measured_at=now,
                confidence_level=0.8,
            )
        )

        # Breakthrough frequency
        breakthrough_rate = min(
            1.0, marker_analysis["breakthroughs"] / 3.0
        )  # Target: 3 breakthroughs
        therapeutic_metrics.append(
            TherapeuticMetric(
                metric_name="breakthrough_frequency",
                value=breakthrough_rate,
                unit="frequency",
                measured_at=now,
                confidence_level=0.7,
            )
        )

        # Calculate overall effectiveness
        overall_score = sum(
            metric.value * metric.confidence_level for metric in therapeutic_metrics
        ) / len(therapeutic_metrics)

        # Determine most/least effective approaches
        approach_effectiveness = defaultdict(list)
        for summary in summaries:
            if hasattr(summary, "therapeutic_approaches_used"):
                for approach in summary.therapeutic_approaches_used:  # type: ignore[attr-defined]
                    # Use session duration as proxy for effectiveness
                    effectiveness = min(1.0, summary.duration_minutes / 30.0)
                    approach_effectiveness[approach].append(effectiveness)

        most_effective = []
        least_effective = []
        for approach, scores in approach_effectiveness.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 0.7:
                most_effective.append(approach)
            elif avg_score <= 0.4:
                least_effective.append(approach)

        # Generate recommendations
        recommendations = []
        if overall_score < self.effectiveness_thresholds["improvement_needed"]:
            recommendations.append(
                "Consider adjusting therapeutic intensity or approach"
            )
            recommendations.append("Focus on engagement-building activities")
        elif overall_score >= self.effectiveness_thresholds["high_effectiveness"]:
            recommendations.append("Maintain current therapeutic approach")
            recommendations.append("Consider advancing to more complex interventions")

        suggested_steps = []
        if marker_analysis["skills_acquired"] < 5:
            suggested_steps.append("Increase focus on skill-building exercises")
        if marker_analysis["breakthroughs"] == 0:
            suggested_steps.append("Incorporate more insight-oriented activities")

        return TherapeuticEffectivenessReport(
            player_id=player_id,
            character_id=character_id,
            report_period_start=report_start,
            report_period_end=now,
            overall_effectiveness_score=overall_score,
            therapeutic_metrics=therapeutic_metrics,
            most_effective_approaches=most_effective,
            least_effective_approaches=least_effective,
            goals_achieved=len([m for m in marker_analysis.values() if m > 0]),
            goals_in_progress=len(active_sessions),
            milestones_reached=marker_analysis["milestones"],
            breakthrough_moments=marker_analysis["breakthroughs"],
            emotional_regulation_improvement=min(
                1.0, marker_analysis["skills_acquired"] * 0.1
            ),
            coping_skills_development=min(
                1.0, marker_analysis["skills_acquired"] * 0.15
            ),
            self_awareness_growth=min(1.0, marker_analysis["insights"] * 0.2),
            recommended_adjustments=recommendations,
            suggested_next_steps=suggested_steps,
            generated_at=now,
        )

    async def celebrate_milestone_achievement(
        self, player_id: str, milestone: Milestone
    ) -> dict[str, Any]:
        """
        Create a celebration response for milestone achievement.
        This can be used to trigger UI celebrations or notifications.
        """
        celebration_data = {
            "milestone_id": milestone.milestone_id,
            "title": milestone.title,
            "description": milestone.description,
            "celebration_message": self._generate_celebration_message(milestone),
            "reward_unlocked": milestone.reward_description,
            "therapeutic_value": self._calculate_milestone_therapeutic_value(milestone),
            "suggested_next_milestone": await self._suggest_next_milestone(
                player_id, milestone
            ),
            "celebration_type": self._determine_celebration_type(milestone),
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Celebrating milestone achievement for player {player_id}: {milestone.title}"
        )
        return celebration_data

    def _generate_celebration_message(self, milestone: Milestone) -> str:
        """Generate a personalized celebration message for a milestone."""
        if "streak" in milestone.title.lower():
            return f"🔥 Amazing consistency! {milestone.title} shows your dedication to growth!"
        if "skill" in milestone.title.lower():
            return f"🎯 Excellent progress! {milestone.title} demonstrates your commitment to learning!"
        if "breakthrough" in milestone.title.lower():
            return f"💡 Incredible insight! {milestone.title} marks a significant therapeutic achievement!"
        return f"🌟 Congratulations! {milestone.title} is a meaningful step in your journey!"

    def _calculate_milestone_therapeutic_value(self, milestone: Milestone) -> float:
        """Calculate the therapeutic value of achieving a milestone."""
        base_value = 0.3

        # Increase value based on milestone type
        if "breakthrough" in milestone.title.lower():
            base_value += 0.4
        elif "skill" in milestone.title.lower():
            base_value += 0.3
        elif "streak" in milestone.title.lower():
            base_value += 0.2

        # Adjust based on therapeutic approaches involved
        if milestone.therapeutic_approaches_involved:
            base_value += len(milestone.therapeutic_approaches_involved) * 0.05

        return min(1.0, base_value)

    async def _suggest_next_milestone(
        self, player_id: str, achieved_milestone: Milestone
    ) -> str | None:
        """Suggest the next logical milestone based on what was just achieved."""
        if "streak" in achieved_milestone.title.lower():
            if "7" in achieved_milestone.title:
                return "14-Day Engagement Streak"
            if "14" in achieved_milestone.title:
                return "30-Day Engagement Streak"
        elif "skill" in achieved_milestone.title.lower():
            if "Level 1" in achieved_milestone.title:
                return "Skill Builder Level 2"
            if "Level 2" in achieved_milestone.title:
                return "Skill Builder Level 3"

        return None

    def _determine_celebration_type(self, milestone: Milestone) -> str:
        """Determine the type of celebration appropriate for the milestone."""
        if (
            "breakthrough" in milestone.title.lower()
            or "streak" in milestone.title.lower()
            and any(num in milestone.title for num in ["30", "60", "90"])
        ):
            return "major_achievement"
        if "skill" in milestone.title.lower():
            return "skill_mastery"
        return "progress_milestone"

    async def get_visualization_data(
        self, player_id: str, *, days: int = 14
    ) -> ProgressVizSeries:
        """Return daily buckets for counts and durations for the last `days` days."""
        days = max(1, min(days, 60))
        summaries: list[
            SessionSummary
        ] = await self.session_repository.get_session_summaries(player_id, days * 2)

        # Build bucket keys YYYY-MM-DD
        today = datetime.utcnow().date()
        bucket_keys = [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)
        ][::-1]
        counts = dict.fromkeys(bucket_keys, 0)
        durations = dict.fromkeys(bucket_keys, 0.0)

        for s in summaries:
            d = (s.end_time or s.start_time).strftime("%Y-%m-%d")
            if d in counts:
                counts[d] += 1
                durations[d] += max(0, s.duration_minutes)

        return ProgressVizSeries(
            time_buckets=bucket_keys,
            series={
                "sessions": [counts[k] for k in bucket_keys],
                "duration_minutes": [durations[k] for k in bucket_keys],
            },
            meta={"period_days": days, "units": {"duration_minutes": "minutes"}},
        )

    # Enhanced helper methods for therapeutic integration

    def _assess_therapeutic_value(
        self, achievement_title: str, session_summary: SessionSummary
    ) -> float:
        """Assess the therapeutic value of an achievement based on context."""
        # Base therapeutic value
        base_value = 0.1

        # Increase value based on achievement type
        if any(
            keyword in achievement_title.lower()
            for keyword in ["breakthrough", "insight", "realization"]
        ):
            base_value += 0.3
        elif any(
            keyword in achievement_title.lower()
            for keyword in ["skill", "technique", "coping"]
        ):
            base_value += 0.2
        elif any(
            keyword in achievement_title.lower()
            for keyword in ["goal", "milestone", "progress"]
        ):
            base_value += 0.15

        # Adjust based on session therapeutic interventions
        if session_summary.therapeutic_interventions_count > 2:
            base_value += 0.1

        return min(1.0, base_value)

    def _enhance_achievement_description(
        self, title: str, session_summary: SessionSummary
    ) -> str:
        """Enhance achievement description with therapeutic context."""
        base_description = title

        # Add context based on session data
        if session_summary.therapeutic_interventions_count > 0:
            base_description += f" (achieved through {session_summary.therapeutic_interventions_count} therapeutic interventions)"

        return base_description

    def _calculate_current_streak(
        self, session_dates: list[datetime] | list[date]
    ) -> int:
        """Calculate current consecutive days with sessions (timezone-robust)."""
        if not session_dates:
            return 0
        # Normalize inputs to date objects
        from datetime import datetime as _dt

        from src.common.time_utils import (
            consecutive_streak_ending_today,
            pick_reference_today,
        )

        dates = [(d.date() if isinstance(d, datetime) else d) for d in session_dates]
        ref_today = pick_reference_today(dates)
        # Guard: if ref_today is not today (local or UTC), there is no current streak
        today_local = _dt.now().date()
        today_utc = _dt.utcnow().date()
        if ref_today not in (today_local, today_utc):
            return 0
        return consecutive_streak_ending_today(dates, ref_today)

    def _calculate_longest_streak(self, session_dates: list[datetime]) -> int:
        """Calculate the longest consecutive streak in session history."""
        if not session_dates:
            return 0

        sorted_dates = sorted(set(session_dates))
        longest_streak = 0
        current_streak = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1

        return max(longest_streak, current_streak)

    def _calculate_dropout_risk(
        self, engagement: EngagementMetrics, session_dates: list[datetime]
    ) -> float:
        """Calculate dropout risk based on engagement patterns."""
        risk_score = 0.0

        # Risk increases with time since last session
        if engagement.last_session_date:
            days_since_last = (
                datetime.now().date() - engagement.last_session_date
            ).days
            if days_since_last > 7:
                risk_score += 0.3
            elif days_since_last > 3:
                risk_score += 0.1
        else:
            risk_score += 0.5

        # Risk increases with low session frequency
        if engagement.sessions_this_week == 0:
            risk_score += 0.2
        elif engagement.sessions_this_week < 2:
            risk_score += 0.1

        # Risk decreases with consistent engagement
        if engagement.current_streak_days >= 7:
            risk_score -= 0.2
        elif engagement.current_streak_days >= 3:
            risk_score -= 0.1

        # Risk increases with very short sessions
        if engagement.average_session_length < 10:
            risk_score += 0.1

        return max(0.0, min(1.0, risk_score))

    def _analyze_progress_markers(
        self, active_sessions: list[SessionContext]
    ) -> dict[str, int]:
        """Analyze progress markers across active sessions."""
        analysis = {
            "skills_acquired": 0,
            "breakthroughs": 0,
            "therapeutic_goals": 0,
            "milestones": 0,
            "insights": 0,
            "total_markers": 0,
        }

        for session in active_sessions:
            for marker in session.progress_markers:
                analysis["total_markers"] += 1

                if marker.marker_type == ProgressMarkerType.SKILL_ACQUIRED:
                    analysis["skills_acquired"] += 1
                elif marker.marker_type == ProgressMarkerType.BREAKTHROUGH:
                    analysis["breakthroughs"] += 1
                elif marker.marker_type == ProgressMarkerType.MILESTONE:
                    analysis["milestones"] += 1
                elif marker.marker_type == ProgressMarkerType.INSIGHT:
                    analysis["insights"] += 1
                elif marker.marker_type == ProgressMarkerType.THERAPEUTIC_GOAL:
                    analysis["therapeutic_goals"] += 1

        return analysis

    async def _detect_comprehensive_milestones(
        self,
        player_id: str,
        engagement: EngagementMetrics,
        marker_analysis: dict[str, int],
        summaries: list[SessionSummary],
    ) -> tuple[list[Milestone], list[ProgressHighlight]]:
        """Detect milestones with comprehensive criteria and create celebration highlights."""
        new_milestones: list[Milestone] = []
        highlights: list[ProgressHighlight] = []
        now = datetime.utcnow()

        # Engagement-based milestones
        for threshold in self.milestone_thresholds["engagement_streak"]:
            if engagement.current_streak_days >= threshold:
                milestone_id = f"ms_{player_id}_streak_{threshold}"
                milestone = Milestone(
                    milestone_id=milestone_id,
                    title=f"{threshold}-Day Engagement Streak",
                    description=f"Maintained consistent therapeutic engagement for {threshold} consecutive days",
                    is_achieved=True,
                    achieved_date=now,
                    therapeutic_approaches_involved=[
                        TherapeuticApproach.BEHAVIORAL_ACTIVATION
                    ],
                    reward_description="Unlocked advanced therapeutic techniques and personalized content",
                )
                new_milestones.append(milestone)

                # Create celebration highlight
                highlights.append(
                    ProgressHighlight(
                        highlight_id=f"hl_{milestone_id}",
                        title=f"🔥 {threshold}-Day Streak Achievement!",
                        description=f"Incredible consistency! You've maintained therapeutic engagement for {threshold} days straight.",
                        highlight_type="milestone",
                        achieved_at=now,
                        therapeutic_value=min(1.0, 0.2 + (threshold * 0.01)),
                    )
                )

        # If a significant streak milestone was achieved, add a celebration highlight
        if engagement.current_streak_days >= 7:
            threshold = max(
                t
                for t in self.milestone_thresholds["engagement_streak"]
                if t <= engagement.current_streak_days
            )
            milestone_id = f"ms_{player_id}_streak_{threshold}"
            highlights.append(
                ProgressHighlight(
                    highlight_id=f"hl_{milestone_id}",
                    title=f"🔥 {threshold}-Day Streak Achievement!",
                    description=f"Incredible consistency! You've maintained therapeutic engagement for {threshold} days straight.",
                    highlight_type="milestone",
                    achieved_at=now,
                    therapeutic_value=min(1.0, 0.2 + (threshold * 0.01)),
                )
            )

        # Session count milestones
        for threshold in self.milestone_thresholds["session_count"]:
            if engagement.total_sessions >= threshold:
                milestone_id = f"ms_{player_id}_sessions_{threshold}"
                milestone = Milestone(
                    milestone_id=milestone_id,
                    title=f"{threshold} Sessions Completed",
                    description=f"Completed {threshold} therapeutic sessions, showing strong commitment to growth",
                    is_achieved=True,
                    achieved_date=now,
                    reward_description="Unlocked advanced progress tracking and insights",
                )
                new_milestones.append(milestone)

        # Also add a small highlight for achieving any session count milestone
        if any(m.title.endswith("Sessions Completed") for m in new_milestones):
            highlights.append(
                ProgressHighlight(
                    highlight_id=f"hl_{player_id}_sessions_milestone",
                    title="👏 Session Milestone Achieved",
                    description="Great job maintaining your practice!",
                    highlight_type="milestone",
                    achieved_at=now,
                    therapeutic_value=0.25,
                )
            )

        # Skill acquisition milestones
        skills_count = marker_analysis["skills_acquired"]
        for threshold in self.milestone_thresholds["skills_acquired"]:
            if skills_count >= threshold:
                milestone_id = f"ms_{player_id}_skills_{threshold}"
                milestone = Milestone(
                    milestone_id=milestone_id,
                    title=f"Skill Builder Level {threshold // 5 + 1}",
                    description=f"Acquired {threshold} therapeutic skills through guided exercises and practice",
                    is_achieved=True,
                    achieved_date=now,
                    therapeutic_approaches_involved=[
                        TherapeuticApproach.CBT,
                        TherapeuticApproach.SKILL_BUILDING,
                    ],
                    reward_description="Unlocked advanced skill-building exercises",
                )
                new_milestones.append(milestone)

        # Breakthrough milestones
        breakthroughs_count = marker_analysis["breakthroughs"]
        for threshold in self.milestone_thresholds["breakthroughs"]:
            if breakthroughs_count >= threshold:
                milestone_id = f"ms_{player_id}_breakthroughs_{threshold}"
                milestone = Milestone(
                    milestone_id=milestone_id,
                    title=f"Breakthrough Explorer Level {threshold}",
                    description=f"Achieved {threshold} significant therapeutic breakthroughs",
                    is_achieved=True,
                    achieved_date=now,
                    therapeutic_approaches_involved=[
                        TherapeuticApproach.INSIGHT_ORIENTED
                    ],
                    reward_description="Unlocked deeper therapeutic exploration content",
                )
                new_milestones.append(milestone)

        return new_milestones, highlights

    def _analyze_progress_trend(
        self, marker_analysis: dict[str, int], engagement: EngagementMetrics
    ) -> str:
        """Analyze overall progress trend based on multiple factors."""
        # Calculate progress indicators
        total_progress_markers = marker_analysis["total_markers"]
        recent_engagement = engagement.sessions_this_week
        streak = engagement.current_streak_days

        # Determine trend
        if total_progress_markers >= 10 and recent_engagement >= 3 and streak >= 5:
            return "improving"
        if total_progress_markers >= 5 and recent_engagement >= 2 and streak >= 2:
            return "stable"
        if recent_engagement == 0 or engagement.dropout_risk_score > 0.6:
            return "declining"
        return "stable"

    def _analyze_engagement_trend(
        self, session_dates: list[datetime], engagement: EngagementMetrics
    ) -> str:
        """Analyze engagement trend over time."""
        if not session_dates:
            return "stable"

        # Compare recent vs older engagement
        now = datetime.now().date()
        recent_week = sum(1 for date in session_dates if (now - date).days <= 7)
        previous_week = sum(1 for date in session_dates if 7 < (now - date).days <= 14)

        if recent_week > previous_week:
            return "increasing"
        if recent_week < previous_week and engagement.dropout_risk_score > 0.4:
            return "decreasing"
        return "stable"

    def _calculate_therapeutic_momentum(
        self, marker_analysis: dict[str, int], engagement: EngagementMetrics
    ) -> float:
        """Calculate therapeutic momentum based on progress and engagement."""
        base_momentum = 0.3

        # Add momentum from progress markers
        base_momentum += min(0.3, marker_analysis["total_markers"] * 0.02)

        # Add momentum from consistent engagement
        base_momentum += min(0.2, engagement.current_streak_days * 0.01)

        # Add momentum from recent activity
        base_momentum += min(0.2, engagement.sessions_this_week * 0.05)

        return min(1.0, base_momentum)

    def _calculate_readiness_for_advancement(self, summary: ProgressSummary) -> float:
        """Calculate readiness for therapeutic advancement."""
        readiness = 0.2

        # Factor in therapeutic momentum
        readiness += summary.therapeutic_momentum * 0.3

        # Factor in milestone achievements
        readiness += min(0.3, len(summary.milestones_achieved) * 0.05)

        # Factor in engagement consistency
        readiness += min(0.2, summary.engagement_metrics.current_streak_days * 0.01)

        return min(1.0, readiness)

    def _identify_strength_areas(
        self, marker_analysis: dict[str, int], engagement: EngagementMetrics
    ) -> list[str]:
        """Identify areas where the player shows strength."""
        strengths = []

        if engagement.current_streak_days >= 7:
            strengths.append("Consistent Engagement")

        if marker_analysis["skills_acquired"] >= 5:
            strengths.append("Skill Development")

        if marker_analysis["breakthroughs"] >= 2:
            strengths.append("Insight Generation")

        if engagement.average_session_length >= 30:
            strengths.append("Deep Therapeutic Work")

        if engagement.sessions_this_week >= 4:
            strengths.append("High Engagement Frequency")

        return strengths

    def _identify_challenge_areas(
        self, marker_analysis: dict[str, int], engagement: EngagementMetrics
    ) -> list[str]:
        """Identify areas that need attention or improvement."""
        challenges = []

        if engagement.dropout_risk_score > 0.6:
            challenges.append("Engagement Consistency")

        if marker_analysis["skills_acquired"] < 2:
            challenges.append("Skill Acquisition")

        if engagement.average_session_length < 15:
            challenges.append("Session Depth")

        if marker_analysis["breakthroughs"] == 0:
            challenges.append("Breakthrough Achievement")

        if engagement.sessions_this_week == 0:
            challenges.append("Recent Activity")

        return challenges

    def _generate_next_goals(
        self, summary: ProgressSummary, marker_analysis: dict[str, int]
    ) -> list[str]:
        """Generate recommended next goals based on current progress."""
        goals = []

        # Engagement goals
        if summary.engagement_metrics.current_streak_days < 7:
            goals.append("Maintain a 7-day engagement streak")
        elif summary.engagement_metrics.current_streak_days < 14:
            goals.append("Extend engagement streak to 14 days")

        # Skill development goals
        if marker_analysis["skills_acquired"] < 5:
            goals.append("Complete 5 skill-building exercises")
        elif marker_analysis["skills_acquired"] < 10:
            goals.append("Master 10 therapeutic techniques")

        # Breakthrough goals
        if marker_analysis["breakthroughs"] == 0:
            goals.append("Achieve your first therapeutic breakthrough")
        elif marker_analysis["breakthroughs"] < 3:
            goals.append("Explore deeper insights and breakthroughs")

        # Session quality goals
        if summary.engagement_metrics.average_session_length < 20:
            goals.append("Engage in longer, more focused sessions")

        return goals[:3]  # Return top 3 goals

    def _suggest_therapeutic_adjustments(self, summary: ProgressSummary) -> list[str]:
        """Suggest therapeutic adjustments based on progress analysis."""
        adjustments = []

        # Engagement-based adjustments
        if summary.engagement_metrics.dropout_risk_score > 0.6:
            adjustments.append(
                "Consider shorter, more frequent sessions to maintain engagement"
            )

        if summary.engagement_metrics.average_session_length < 15:
            adjustments.append(
                "Gradually increase session length for deeper therapeutic work"
            )

        # Progress-based adjustments
        if summary.therapeutic_momentum < 0.5:
            adjustments.append("Focus on skill-building exercises to build momentum")

        if "Breakthrough Achievement" in summary.challenge_areas:
            adjustments.append(
                "Incorporate more insight-oriented therapeutic approaches"
            )

        # Readiness-based adjustments
        if summary.readiness_for_advancement > 0.7:
            adjustments.append(
                "Ready for more advanced therapeutic techniques and challenges"
            )

        return adjustments
