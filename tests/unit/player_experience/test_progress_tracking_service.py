import pytest
# Logseq: [[TTA.dev/Tests/Test_progress_tracking_service]]
import asyncio
import unittest
from datetime import UTC, datetime, timedelta

from src.player_experience.managers.progress_tracking_service import (
    ProgressTrackingService,
)
from src.player_experience.models.enums import (
    ProgressMarkerType,
    SessionStatus,
)
from src.player_experience.models.progress import Milestone
from src.player_experience.models.session import (
    ProgressMarker,
    SessionContext,
    SessionSummary,
    TherapeuticSettings,
)

pytestmark = pytest.mark.unit


class MockSessionRepository:
    def __init__(self, summaries: list[SessionSummary], sessions: list[SessionContext]):
        self._summaries = summaries
        self._sessions = sessions

    async def get_session_summaries(
        self, player_id: str, limit: int = 10
    ) -> list[SessionSummary]:
        return self._summaries[:limit]

    async def get_player_active_sessions(self, player_id: str) -> list[SessionContext]:
        return [
            s
            for s in self._sessions
            if s.player_id == player_id and s.status == SessionStatus.ACTIVE
        ]


class TestProgressTrackingService(unittest.TestCase):
    def setUp(self):
        now = datetime.now(UTC)
        # Create 5 daily session summaries
        self.summaries = []
        for i in range(5):
            start = now - timedelta(days=i, hours=1)
            end = now - timedelta(days=i)
            self.summaries.append(
                SessionSummary(
                    session_id=f"s{i}",
                    character_name="Char",
                    world_name="World",
                    start_time=start,
                    end_time=end,
                    duration_minutes=30,
                    status=SessionStatus.COMPLETED,
                    progress_markers_count=1,
                    therapeutic_interventions_count=1,
                )
            )

        # Active session with 5 skill markers
        settings = TherapeuticSettings()
        active = SessionContext(
            session_id="active1",
            player_id="playerA",
            character_id="charA",
            world_id="worldA",
            therapeutic_settings=settings,
        )
        for j in range(5):
            active.add_progress_marker(
                ProgressMarker(
                    marker_id=f"pm{j}",
                    marker_type=ProgressMarkerType.SKILL_ACQUIRED,
                    description="skill",
                    achieved_at=now - timedelta(minutes=j),
                    therapeutic_value=0.2,
                )
            )

        self.repo = MockSessionRepository(self.summaries, [active])
        self.service = ProgressTrackingService(self.repo)
        self.player_id = "playerA"

    def test_compute_progress_summary(self):
        """Progress Tracking Service: compute progress summary."""
        async def run():
            summary = await self.service.compute_progress_summary(self.player_id)
            assert summary.player_id == self.player_id
            assert summary.engagement_metrics.total_sessions == 5
            assert summary.therapeutic_momentum >= 0.4
            assert summary.progress_trend in ["stable", "improving"]

        asyncio.run(run())

    def test_detect_and_update_milestones(self):
        """Progress Tracking Service: detect and update milestones."""
        async def run():
            milestones, highlights = await self.service.detect_and_update_milestones(
                self.player_id
            )
            # Skill milestone should trigger
            titles = [m.title for m in milestones]
            assert "Skill Builder Level 1" in titles
            assert len(highlights) > 0

        asyncio.run(run())

    def test_generate_progress_insights(self):
        """Progress Tracking Service: generate progress insights."""
        async def run():
            recs = await self.service.generate_progress_insights(self.player_id)
            assert isinstance(recs, list)
            # Expect at least one recommendation based on momentum
            assert len(recs) > 0

        asyncio.run(run())

    def test_get_visualization_data(self):
        """Progress Tracking Service: get visualization data."""
        async def run():
            viz = await self.service.get_visualization_data(self.player_id, days=7)
            assert len(viz.time_buckets) == 7
            assert "sessions" in viz.series
            assert "duration_minutes" in viz.series
            assert len(viz.series["sessions"]) == 7

        asyncio.run(run())

    def test_therapeutic_effectiveness_report(self):
        """Progress Tracking Service: therapeutic effectiveness report."""
        async def run():
            report = await self.service.generate_therapeutic_effectiveness_report(
                self.player_id
            )
            assert report.player_id == self.player_id
            assert isinstance(report.overall_effectiveness_score, float)
            assert report.overall_effectiveness_score >= 0.0
            assert report.overall_effectiveness_score <= 1.0
            assert isinstance(report.therapeutic_metrics, list)
            assert len(report.therapeutic_metrics) > 0

        asyncio.run(run())

    def test_milestone_celebration(self):
        """Progress Tracking Service: milestone celebration."""
        async def run():
            milestone = Milestone(
                milestone_id="test_milestone",
                title="Test Achievement",
                description="A test milestone",
                is_achieved=True,
            )
            celebration = await self.service.celebrate_milestone_achievement(
                self.player_id, milestone
            )
            assert "milestone_id" in celebration
            assert "celebration_message" in celebration
            assert "therapeutic_value" in celebration
            assert isinstance(celebration["therapeutic_value"], float)

        asyncio.run(run())

    def test_enhanced_progress_summary_with_therapeutic_integration(self):
        """Progress Tracking Service: enhanced progress summary with therapeutic integration."""
        async def run():
            # Add more diverse progress markers
            settings = TherapeuticSettings()
            enhanced_session = SessionContext(
                session_id="enhanced1",
                player_id=self.player_id,
                character_id="charA",
                world_id="worldA",
                therapeutic_settings=settings,
            )

            # Add various types of progress markers
            marker_types = [
                ProgressMarkerType.SKILL_ACQUIRED,
                ProgressMarkerType.BREAKTHROUGH,
                ProgressMarkerType.INSIGHT,
                ProgressMarkerType.THERAPEUTIC_GOAL,
                ProgressMarkerType.MILESTONE,
            ]

            for i, marker_type in enumerate(marker_types):
                enhanced_session.add_progress_marker(
                    ProgressMarker(
                        marker_id=f"enhanced_pm{i}",
                        marker_type=marker_type,
                        description=f"Enhanced {marker_type.value}",
                        achieved_at=datetime.now(UTC) - timedelta(minutes=i),
                        therapeutic_value=0.3,
                    )
                )

            # Update mock repository
            self.repo._sessions = [enhanced_session]

            summary = await self.service.compute_progress_summary(self.player_id)

            # Verify enhanced functionality
            assert isinstance(summary.strength_areas, list)
            assert isinstance(summary.challenge_areas, list)
            assert isinstance(summary.next_recommended_goals, list)
            assert isinstance(summary.suggested_therapeutic_adjustments, list)

            # Verify therapeutic momentum calculation
            assert summary.therapeutic_momentum > 0.5
            assert summary.readiness_for_advancement > 0.3

        asyncio.run(run())

    def test_comprehensive_milestone_detection(self):
        """Progress Tracking Service: comprehensive milestone detection."""
        async def run():
            # Create session summaries for streak detection
            now = datetime.now(UTC)
            streak_summaries = []
            for i in range(10):  # 10 consecutive days
                start = now - timedelta(days=i, hours=1)
                end = now - timedelta(days=i)
                streak_summaries.append(
                    SessionSummary(
                        session_id=f"streak_s{i}",
                        character_name="Char",
                        world_name="World",
                        start_time=start,
                        end_time=end,
                        duration_minutes=25,
                        status=SessionStatus.COMPLETED,
                        progress_markers_count=1,
                        therapeutic_interventions_count=2,
                    )
                )

            # Update mock repository with streak data
            self.repo._summaries = streak_summaries

            milestones, highlights = await self.service.detect_and_update_milestones(
                self.player_id
            )

            # Should detect multiple milestones for 7+ day streak
            milestone_titles = [m.title for m in milestones]
            assert any("7" in title for title in milestone_titles)

            # Should have celebration highlights
            assert len(highlights) > 0
            highlight_types = [h.highlight_type for h in highlights]
            assert "milestone" in highlight_types

        asyncio.run(run())

    def test_enhanced_progress_insights_generation(self):
        """Progress Tracking Service: enhanced progress insights generation."""
        async def run():
            # Create a scenario with high therapeutic momentum
            high_momentum_summaries = []
            now = datetime.now(UTC)
            for i in range(15):  # 15 sessions
                start = now - timedelta(days=i, hours=1)
                end = now - timedelta(days=i)
                high_momentum_summaries.append(
                    SessionSummary(
                        session_id=f"momentum_s{i}",
                        character_name="Char",
                        world_name="World",
                        start_time=start,
                        end_time=end,
                        duration_minutes=35,  # Longer sessions
                        status=SessionStatus.COMPLETED,
                        progress_markers_count=2,
                        therapeutic_interventions_count=3,
                    )
                )

            self.repo._summaries = high_momentum_summaries

            insights = await self.service.generate_progress_insights(self.player_id)

            # Should generate multiple relevant recommendations
            assert len(insights) > 0
            assert len(insights) <= 6  # Should limit to top 6

            # Recommendations should be sorted by priority
            priorities = [rec.priority for rec in insights]
            assert priorities == sorted(priorities)

            # Should include diverse recommendation types
            rec_types = [rec.recommendation_type for rec in insights]
            assert len(set(rec_types)) > 1  # Multiple types

        asyncio.run(run())

    def test_dropout_risk_calculation(self):
        """Progress Tracking Service: dropout risk calculation."""
        async def run():
            # Create scenario with very high dropout risk (no recent sessions, very old activity)
            old_summaries = []
            old_date = datetime.now(UTC) - timedelta(days=15)  # Even older sessions
            for i in range(2):  # Fewer sessions
                start = old_date - timedelta(days=i, hours=1)
                end = old_date - timedelta(days=i)
                old_summaries.append(
                    SessionSummary(
                        session_id=f"old_s{i}",
                        character_name="Char",
                        world_name="World",
                        start_time=start,
                        end_time=end,
                        duration_minutes=5,  # Very short sessions
                        status=SessionStatus.COMPLETED,
                        progress_markers_count=0,
                        therapeutic_interventions_count=0,
                    )
                )

            self.repo._summaries = old_summaries
            self.repo._sessions = []  # No active sessions

            summary = await self.service.compute_progress_summary(self.player_id)

            # Should detect elevated dropout risk
            assert summary.engagement_metrics.dropout_risk_score >= 0.5

            # Should suggest therapeutic support (flexible approach or engagement support)
            insights = await self.service.generate_progress_insights(self.player_id)
            rec_types = [rec.recommendation_type for rec in insights]
            rec_titles = [rec.title for rec in insights]

            # Check for any dropout-related recommendations
            dropout_support_found = any(
                "engagement" in rec_type.lower() for rec_type in rec_types
            ) or any(
                "flexible" in title.lower()
                or "reconnect" in title.lower()
                or "approach" in title.lower()
                for title in rec_titles
            )
            assert dropout_support_found, (
                f"Expected dropout support recommendations but got types: {rec_types}, titles: {rec_titles}"
            )

        asyncio.run(run())

    def test_therapeutic_value_assessment(self):
        # Test the therapeutic value assessment helper method
        """Progress Tracking Service: therapeutic value assessment."""
        session_summary = SessionSummary(
            session_id="test_session",
            character_name="Test Char",
            world_name="Test World",
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            duration_minutes=30,
            status=SessionStatus.COMPLETED,
            progress_markers_count=1,
            therapeutic_interventions_count=3,  # High intervention count
        )

        # Test breakthrough achievement
        breakthrough_value = self.service._assess_therapeutic_value(
            "Major breakthrough in understanding", session_summary
        )
        assert breakthrough_value > 0.3

        # Test skill achievement
        skill_value = self.service._assess_therapeutic_value(
            "New coping skill acquired", session_summary
        )
        assert skill_value > 0.2

        # Test regular achievement
        regular_value = self.service._assess_therapeutic_value(
            "Completed session", session_summary
        )
        assert regular_value > 0.1

        # All values should be <= 1.0
        assert breakthrough_value <= 1.0
        assert skill_value <= 1.0
        assert regular_value <= 1.0

    def test_streak_calculation_accuracy(self):
        # Test streak calculation with various scenarios
        """Progress Tracking Service: streak calculation accuracy."""
        now = datetime.now().date()

        # Test consecutive streak
        consecutive_dates = [now - timedelta(days=i) for i in range(5)]
        streak = self.service._calculate_current_streak(consecutive_dates)
        assert streak == 5

        # Test broken streak
        broken_dates = [now - timedelta(days=i) for i in [0, 1, 3, 4]]  # Missing day 2
        broken_streak = self.service._calculate_current_streak(broken_dates)
        assert broken_streak == 2  # Only counts from today

        # Test no recent activity
        old_dates = [now - timedelta(days=i) for i in range(10, 15)]
        no_streak = self.service._calculate_current_streak(old_dates)
        assert no_streak == 0

    def test_visualization_data_accuracy(self):
        """Progress Tracking Service: visualization data accuracy."""
        async def run():
            # Test visualization data generation
            viz_data = await self.service.get_visualization_data(self.player_id, days=7)

            assert len(viz_data.time_buckets) == 7
            assert "sessions" in viz_data.series
            assert "duration_minutes" in viz_data.series
            assert len(viz_data.series["sessions"]) == 7
            assert len(viz_data.series["duration_minutes"]) == 7

            # Verify metadata
            assert "period_days" in viz_data.meta
            assert viz_data.meta["period_days"] == 7

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
