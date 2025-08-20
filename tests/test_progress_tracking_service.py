import unittest
import asyncio
from datetime import datetime, timedelta
from typing import List

from src.player_experience.managers.progress_tracking_service import ProgressTrackingService
from src.player_experience.models.session import SessionSummary, SessionContext, ProgressMarker, TherapeuticSettings
from src.player_experience.models.enums import SessionStatus, ProgressMarkerType, TherapeuticApproach
from src.player_experience.models.progress import Milestone, ProgressHighlight


class MockSessionRepository:
    def __init__(self, summaries: List[SessionSummary], sessions: List[SessionContext]):
        self._summaries = summaries
        self._sessions = sessions

    async def get_session_summaries(self, player_id: str, limit: int = 10) -> List[SessionSummary]:
        return self._summaries[:limit]

    async def get_player_active_sessions(self, player_id: str) -> List[SessionContext]:
        return [s for s in self._sessions if s.player_id == player_id and s.status == SessionStatus.ACTIVE]


class TestProgressTrackingService(unittest.TestCase):
    def setUp(self):
        now = datetime.utcnow()
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
        async def run():
            summary = await self.service.compute_progress_summary(self.player_id)
            self.assertEqual(summary.player_id, self.player_id)
            self.assertEqual(summary.engagement_metrics.total_sessions, 5)
            self.assertGreaterEqual(summary.therapeutic_momentum, 0.4)
            self.assertIn(summary.progress_trend, ["stable", "improving"])
        asyncio.run(run())

    def test_detect_and_update_milestones(self):
        async def run():
            milestones, highlights = await self.service.detect_and_update_milestones(self.player_id)
            # Skill milestone should trigger
            titles = [m.title for m in milestones]
            self.assertIn("Skill Builder Level 1", titles)
            self.assertGreater(len(highlights), 0)
        asyncio.run(run())

    def test_generate_progress_insights(self):
        async def run():
            recs = await self.service.generate_progress_insights(self.player_id)
            self.assertIsInstance(recs, list)
            # Expect at least one recommendation based on momentum
            self.assertGreater(len(recs), 0)
        asyncio.run(run())

    def test_get_visualization_data(self):
        async def run():
            viz = await self.service.get_visualization_data(self.player_id, days=7)
            self.assertEqual(len(viz.time_buckets), 7)
            self.assertIn("sessions", viz.series)
            self.assertIn("duration_minutes", viz.series)
            self.assertEqual(len(viz.series["sessions"]), 7)
        asyncio.run(run())


    def test_therapeutic_effectiveness_report(self):
        async def run():
            report = await self.service.generate_therapeutic_effectiveness_report(self.player_id)
            self.assertEqual(report.player_id, self.player_id)
            self.assertIsInstance(report.overall_effectiveness_score, float)
            self.assertGreaterEqual(report.overall_effectiveness_score, 0.0)
            self.assertLessEqual(report.overall_effectiveness_score, 1.0)
            self.assertIsInstance(report.therapeutic_metrics, list)
            self.assertGreater(len(report.therapeutic_metrics), 0)
        asyncio.run(run())

    def test_milestone_celebration(self):
        async def run():
            milestone = Milestone(
                milestone_id="test_milestone",
                title="Test Achievement",
                description="A test milestone",
                is_achieved=True
            )
            celebration = await self.service.celebrate_milestone_achievement(self.player_id, milestone)
            self.assertIn("milestone_id", celebration)
            self.assertIn("celebration_message", celebration)
            self.assertIn("therapeutic_value", celebration)
            self.assertIsInstance(celebration["therapeutic_value"], float)
        asyncio.run(run())

    def test_enhanced_progress_summary_with_therapeutic_integration(self):
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
                ProgressMarkerType.MILESTONE
            ]
            
            for i, marker_type in enumerate(marker_types):
                enhanced_session.add_progress_marker(
                    ProgressMarker(
                        marker_id=f"enhanced_pm{i}",
                        marker_type=marker_type,
                        description=f"Enhanced {marker_type.value}",
                        achieved_at=datetime.utcnow() - timedelta(minutes=i),
                        therapeutic_value=0.3,
                    )
                )
            
            # Update mock repository
            self.repo._sessions = [enhanced_session]
            
            summary = await self.service.compute_progress_summary(self.player_id)
            
            # Verify enhanced functionality
            self.assertIsInstance(summary.strength_areas, list)
            self.assertIsInstance(summary.challenge_areas, list)
            self.assertIsInstance(summary.next_recommended_goals, list)
            self.assertIsInstance(summary.suggested_therapeutic_adjustments, list)
            
            # Verify therapeutic momentum calculation
            self.assertGreater(summary.therapeutic_momentum, 0.5)
            self.assertGreater(summary.readiness_for_advancement, 0.3)
            
        asyncio.run(run())

    def test_comprehensive_milestone_detection(self):
        async def run():
            # Create session summaries for streak detection
            now = datetime.utcnow()
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
            
            milestones, highlights = await self.service.detect_and_update_milestones(self.player_id)
            
            # Should detect multiple milestones for 7+ day streak
            milestone_titles = [m.title for m in milestones]
            self.assertTrue(any("7" in title for title in milestone_titles))
            
            # Should have celebration highlights
            self.assertGreater(len(highlights), 0)
            highlight_types = [h.highlight_type for h in highlights]
            self.assertIn("milestone", highlight_types)
            
        asyncio.run(run())

    def test_enhanced_progress_insights_generation(self):
        async def run():
            # Create a scenario with high therapeutic momentum
            high_momentum_summaries = []
            now = datetime.utcnow()
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
            self.assertGreater(len(insights), 0)
            self.assertLessEqual(len(insights), 6)  # Should limit to top 6
            
            # Recommendations should be sorted by priority
            priorities = [rec.priority for rec in insights]
            self.assertEqual(priorities, sorted(priorities))
            
            # Should include diverse recommendation types
            rec_types = [rec.recommendation_type for rec in insights]
            self.assertGreater(len(set(rec_types)), 1)  # Multiple types
            
        asyncio.run(run())

    def test_dropout_risk_calculation(self):
        async def run():
            # Create scenario with very high dropout risk (no recent sessions, very old activity)
            old_summaries = []
            old_date = datetime.utcnow() - timedelta(days=15)  # Even older sessions
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
            self.assertGreaterEqual(summary.engagement_metrics.dropout_risk_score, 0.5)
            
            # Should suggest therapeutic support (flexible approach or engagement support)
            insights = await self.service.generate_progress_insights(self.player_id)
            rec_types = [rec.recommendation_type for rec in insights]
            rec_titles = [rec.title for rec in insights]
            
            # Check for any dropout-related recommendations
            dropout_support_found = (
                any("engagement" in rec_type.lower() for rec_type in rec_types) or
                any("flexible" in title.lower() or "reconnect" in title.lower() or "approach" in title.lower() for title in rec_titles)
            )
            self.assertTrue(dropout_support_found, f"Expected dropout support recommendations but got types: {rec_types}, titles: {rec_titles}")
            
        asyncio.run(run())

    def test_therapeutic_value_assessment(self):
        # Test the therapeutic value assessment helper method
        session_summary = SessionSummary(
            session_id="test_session",
            character_name="Test Char",
            world_name="Test World",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_minutes=30,
            status=SessionStatus.COMPLETED,
            progress_markers_count=1,
            therapeutic_interventions_count=3,  # High intervention count
        )
        
        # Test breakthrough achievement
        breakthrough_value = self.service._assess_therapeutic_value("Major breakthrough in understanding", session_summary)
        self.assertGreater(breakthrough_value, 0.3)
        
        # Test skill achievement
        skill_value = self.service._assess_therapeutic_value("New coping skill acquired", session_summary)
        self.assertGreater(skill_value, 0.2)
        
        # Test regular achievement
        regular_value = self.service._assess_therapeutic_value("Completed session", session_summary)
        self.assertGreater(regular_value, 0.1)
        
        # All values should be <= 1.0
        self.assertLessEqual(breakthrough_value, 1.0)
        self.assertLessEqual(skill_value, 1.0)
        self.assertLessEqual(regular_value, 1.0)

    def test_streak_calculation_accuracy(self):
        # Test streak calculation with various scenarios
        now = datetime.now().date()
        
        # Test consecutive streak
        consecutive_dates = [now - timedelta(days=i) for i in range(5)]
        streak = self.service._calculate_current_streak(consecutive_dates)
        self.assertEqual(streak, 5)
        
        # Test broken streak
        broken_dates = [now - timedelta(days=i) for i in [0, 1, 3, 4]]  # Missing day 2
        broken_streak = self.service._calculate_current_streak(broken_dates)
        self.assertEqual(broken_streak, 2)  # Only counts from today
        
        # Test no recent activity
        old_dates = [now - timedelta(days=i) for i in range(10, 15)]
        no_streak = self.service._calculate_current_streak(old_dates)
        self.assertEqual(no_streak, 0)

    def test_visualization_data_accuracy(self):
        async def run():
            # Test visualization data generation
            viz_data = await self.service.get_visualization_data(self.player_id, days=7)
            
            self.assertEqual(len(viz_data.time_buckets), 7)
            self.assertIn("sessions", viz_data.series)
            self.assertIn("duration_minutes", viz_data.series)
            self.assertEqual(len(viz_data.series["sessions"]), 7)
            self.assertEqual(len(viz_data.series["duration_minutes"]), 7)
            
            # Verify metadata
            self.assertIn("period_days", viz_data.meta)
            self.assertEqual(viz_data.meta["period_days"], 7)
            
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

