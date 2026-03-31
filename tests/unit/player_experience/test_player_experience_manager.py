# Logseq: [[TTA.dev/Tests/Test_player_experience_manager]]

import asyncio
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

from src.player_experience.database.character_repository import CharacterRepository
from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.managers.personalization_service_manager import (
    PersonalizationServiceManager,
    PlayerFeedback,
)
from src.player_experience.managers.player_experience_manager import (
    PlayerExperienceManager,
)
from src.player_experience.managers.progress_tracking_service import (
    ProgressTrackingService,
)
from src.player_experience.models.enums import SessionStatus
from src.player_experience.models.session import (
    Recommendation,
    SessionSummary,
)


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

    async def compute_progress_summary(
        self, player_id: str, *, summaries_limit: int = 30
    ):
        class Dummy:
            therapeutic_momentum = 0.7
            engagement_metrics = type(
                "E",
                (),
                {
                    "current_streak_days": 3,
                    "total_sessions": 0,
                    "total_time_minutes": 0,
                },
            )()
            recent_highlights = []
            progress_trend = "stable"
            engagement_trend = "stable"
            milestones_achieved = []
            last_updated = datetime.now(UTC)

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


class MockSessionStore:
    def __init__(self, sessions):
        self._sessions = sessions

    def list_sessions(self, player_id: str):
        return list(self._sessions)


class MockCharacterManager:
    def __init__(self, character_ids: list[str]):
        self._characters = [
            type("CharacterSummary", (), {"character_id": character_id})()
            for character_id in character_ids
        ]

    def get_player_characters(self, player_id: str):
        return list(self._characters)


class TestPlayerExperienceManager(unittest.TestCase):
    def setUp(self):
        now = datetime.now(UTC)
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
            assert dashboard.player_id == self.player_id
            assert len(dashboard.recent_sessions) == 3
            assert dashboard.therapeutic_momentum >= 0.7

        asyncio.run(run())

    def test_recommendations_combined(self):
        async def run():
            recs = await self.mgr.get_recommendations(self.player_id)
            titles = [r.title for r in recs]
            assert "Mindfulness practice" in titles
            assert "Stress Management Focus" in titles

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
            assert result["adaptation_id"] == "a1"
            assert "reduce_intensity" in result["changes_made"]

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

            out = await self.mgr.detect_crisis_and_get_resources(
                self.player_id, "I want to end it all."
            )
            assert out["crisis_detected"]
            assert "suicidal_ideation" in out["crisis_types"]  # enum value
            assert len(out["resources"]) == 1
            r = out["resources"][0]
            assert r["resource_id"] == "res1"
            assert r["contact"] == "988"
            assert r["emergency"]

        asyncio.run(run())

    def test_dashboard_api_payload_includes_narrative_summary(self):
        async def run():
            session_store = MockSessionStore(
                [{"session_id": "session-1", "updated_at": "2026-03-24T05:00:00+00:00"}]
            )
            character_manager = MockCharacterManager(["char-1", "char-2"])

            with patch(
                "src.player_experience.managers.player_experience_manager.enrich_session_payloads",
                new=AsyncMock(
                    return_value=(
                        [
                            {
                                "session_id": "session-1",
                                "narrative_orchestration": {
                                    "player_signals": {"coherence_status": "stable"}
                                },
                            }
                        ],
                        {"stable_sessions": 1, "strained_sessions": 0},
                    )
                ),
            ):
                payload = await self.mgr.get_dashboard_api_payload(
                    self.player_id,
                    session_store=session_store,
                    character_manager=character_manager,
                )

            assert payload["player_id"] == self.player_id
            assert payload["active_characters"] == ["char-1", "char-2"]
            assert (
                payload["session_metrics"]["narrative_summary"]["stable_sessions"] == 1
            )
            assert payload["recommendations"][0]["recommendation_id"] == "r2"
            assert payload["recommendations"][0]["recommendation_type"] == (
                "therapeutic_focus"
            )
            assert (
                payload["recent_sessions"][0]["narrative_orchestration"][
                    "player_signals"
                ]["coherence_status"]
                == "stable"
            )

        asyncio.run(run())

    def test_dashboard_api_payload_gracefully_handles_enrichment_failure(self):
        async def run():
            session_store = MockSessionStore([{"session_id": "session-1"}])
            character_manager = MockCharacterManager(["char-1"])

            with patch(
                "src.player_experience.managers.player_experience_manager.enrich_session_payloads",
                new=AsyncMock(side_effect=RuntimeError("boom")),
            ):
                payload = await self.mgr.get_dashboard_api_payload(
                    self.player_id,
                    session_store=session_store,
                    character_manager=character_manager,
                )

            assert payload["active_characters"] == ["char-1"]
            assert payload["recent_sessions"] == [{"session_id": "session-1"}]
            assert payload["session_metrics"]["narrative_summary"] == {
                "stable_sessions": 0,
                "strained_sessions": 0,
            }
            assert payload["recommendations"][0]["title"] == "Stress Management Focus"

        asyncio.run(run())

    def test_session_list_api_payload_without_narrative(self):
        async def run():
            session_store = MockSessionStore(
                [
                    {"session_id": "session-1", "status": "active"},
                    {"session_id": "session-2", "status": "paused"},
                ]
            )

            payload = await self.mgr.get_session_list_api_payload(
                self.player_id,
                session_store=session_store,
                include_narrative=False,
            )

            assert payload["count"] == 2
            assert payload["sessions"][0]["session_id"] == "session-1"
            assert "narrative_summary" not in payload

        asyncio.run(run())

    def test_session_list_api_payload_with_narrative_summary(self):
        async def run():
            session_store = MockSessionStore([{"session_id": "session-1"}])

            with patch(
                "src.player_experience.managers.player_experience_manager.enrich_session_payloads",
                new=AsyncMock(
                    return_value=(
                        [
                            {
                                "session_id": "session-1",
                                "narrative_orchestration": {
                                    "player_signals": {"coherence_status": "stable"}
                                },
                            }
                        ],
                        {"stable_sessions": 1, "strained_sessions": 0},
                    )
                ),
            ):
                payload = await self.mgr.get_session_list_api_payload(
                    self.player_id,
                    session_store=session_store,
                    include_narrative=True,
                )

            assert payload["count"] == 1
            assert payload["narrative_summary"]["stable_sessions"] == 1
            assert (
                payload["sessions"][0]["narrative_orchestration"]["player_signals"][
                    "coherence_status"
                ]
                == "stable"
            )

        asyncio.run(run())

    def test_progress_api_payload_uses_real_summary_data(self):
        async def run():
            payload = await self.mgr.get_progress_api_payload(self.player_id)

            assert payload["player_id"] == self.player_id
            assert payload["total_sessions"] == 0
            assert payload["total_time_minutes"] == 0
            assert payload["milestones_achieved"] == 0
            assert payload["current_streak_days"] == 3
            assert payload["therapeutic_momentum"] == 0.7
            assert payload["progress_trend"] == "stable"
            assert payload["engagement_trend"] == "stable"
            assert isinstance(payload["last_updated"], str)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
