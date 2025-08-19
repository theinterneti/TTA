import unittest
import asyncio
from datetime import datetime, timedelta

from src.player_experience.managers.player_experience_manager import PlayerExperienceManager
from src.player_experience.managers.progress_tracking_service import ProgressTrackingService
from src.player_experience.managers.personalization_service_manager import PersonalizationServiceManager, PlayerFeedback
from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.database.character_repository import CharacterRepository
from src.player_experience.models.session import SessionSummary, Recommendation, SessionContext, TherapeuticSettings
from src.player_experience.models.enums import SessionStatus


class MockSessionRepository(SessionRepository):
    def __init__(self, summaries):
        super().__init__(redis_client=None, neo4j_driver=None)
        self._summaries = summaries
        self._active_sessions = {}

    async def get_session_summaries(self, player_id: str, limit: int = 10):
        return self._summaries[:limit]

    async def get_player_active_sessions(self, player_id: str):
        return list(self._active_sessions.get(player_id, []))


class MockProgressService(ProgressTrackingService):
    def __init__(self):
        pass

    async def compute_progress_summary(self, player_id: str, *, summaries_limit: int = 30):
        class Dummy:
            therapeutic_momentum = 0.7
            engagement_metrics = type("E", (), {"current_streak_days": 3})()
            recent_highlights = []
        return Dummy()

    async def generate_progress_insights(self, player_id: str):
        return [
            Recommendation(
                recommendation_id="r1",
                title="Mindfulness practice",
                description="Try mindfulness.",
                recommendation_type="therapeutic_approach",
                priority=3,
            )
        ]


class MockPersonalizationManager(PersonalizationServiceManager):
    def __init__(self):
        pass

    def get_adaptive_recommendations(self, player_id, context=None):
        return [
            Recommendation(
                recommendation_id="r2",
                title="Stress Management Focus",
                description="Focus on stress management.",
                recommendation_type="therapeutic_focus",
                priority=2,
            )
        ]

    def process_feedback(self, player_id, feedback):
        class Dummy:
            adaptation_id = "a1"
            changes_made = ["reduce_intensity"]
            confidence_score = 0.8
            requires_player_approval = False
            reasoning = "Based on rating"
        return Dummy()


class TestPlayerExperienceManager(unittest.TestCase):
    def setUp(self):
        now = datetime.utcnow()
        self.summaries = []
        for i in range(3):
            self.summaries.append(
                SessionSummary(
                    session_id=f"s{i}",
                    character_name="Char",
                    world_name="World",
                    start_time=now - timedelta(days=i, hours=1),
                    end_time=now - timedelta(days=i),
                    duration_minutes=20,
                    status=SessionStatus.COMPLETED,
                    progress_markers_count=1,
                    therapeutic_interventions_count=1,
                )
            )
        self.session_repo = MockSessionRepository(self.summaries)
        self.character_repo = CharacterRepository()
        self.progress_service = MockProgressService()
        self.personalization = MockPersonalizationManager()
        self.mgr = PlayerExperienceManager(
            session_repository=self.session_repo,
            character_repository=self.character_repo,
            personalization_manager=self.personalization,
            progress_service=self.progress_service,
        )
        self.player_id = "playerA"

    def test_dashboard_aggregation(self):
        async def run():
            dashboard = await self.mgr.get_player_dashboard(self.player_id)
            self.assertEqual(dashboard.player_id, self.player_id)
            self.assertEqual(len(dashboard.recent_sessions), 3)
            self.assertGreaterEqual(dashboard.therapeutic_momentum, 0.7)
        asyncio.run(run())

    def test_recommendations_combined(self):
        async def run():
            recs = await self.mgr.get_recommendations(self.player_id)
            titles = [r.title for r in recs]
            self.assertIn("Mindfulness practice", titles)
            self.assertIn("Stress Management Focus", titles)
        asyncio.run(run())

    def test_feedback_processing(self):
        async def run():
            fb = PlayerFeedback(
                feedback_id="f1",
                player_id=self.player_id,
                session_id="s0",
                feedback_type="rating",
                content={"rating": 2},
            )
            result = await self.mgr.process_player_feedback(self.player_id, fb)
            self.assertEqual(result["adaptation_id"], "a1")
            self.assertIn("reduce_intensity", result["changes_made"])
        asyncio.run(run())
    def test_crisis_detection_integration(self):
        async def run():
            from src.player_experience.models.enums import CrisisType

            class Res:
                def __init__(self):
                    self.resource_id = "res1"
                    self.name = "988 Lifeline"
                    self.contact_method = "phone"
                    self.contact_info = "988"
                    self.priority = 1
                    self.is_emergency = True

            def fake_detect(pid, text, context=None):
                return True, [CrisisType.SUICIDAL_IDEATION], [Res()]

            # Patch the personalization manager's crisis detection
            self.mgr.personalization_manager.detect_crisis_situation = fake_detect

            out = await self.mgr.detect_crisis_and_get_resources(self.player_id, "I want to end it all.")
            self.assertTrue(out["crisis_detected"])
            self.assertIn("suicidal_ideation", out["crisis_types"])  # enum value
            self.assertEqual(len(out["resources"]), 1)
            r = out["resources"][0]
            self.assertEqual(r["resource_id"], "res1")
            self.assertEqual(r["contact"], "988")
            self.assertTrue(r["emergency"])
        asyncio.run(run())



if __name__ == "__main__":
    unittest.main()

