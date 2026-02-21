# Logseq: [[TTA.dev/Tests/Test_progress_tracking_highlights]]
import asyncio
from datetime import datetime, timedelta

from src.player_experience.managers.progress_tracking_service import (
    ProgressTrackingService,
)
from src.player_experience.models.enums import SessionStatus
from src.player_experience.models.session import (
    SessionSummary,
)


class MockSessionRepository:
    def __init__(self, summaries, sessions):
        self._summaries = summaries
        self._sessions = sessions

    async def get_session_summaries(self, player_id: str, limit: int = 10):
        return self._summaries[:limit]

    async def get_player_active_sessions(self, player_id: str):
        return [
            s
            for s in self._sessions
            if s.player_id == player_id and s.status == SessionStatus.ACTIVE
        ]


def test_highlights_created_for_session_milestone():
    now = datetime.utcnow()
    # 10 completed sessions to trigger session milestone
    summaries = []
    for i in range(10):
        start = now - timedelta(days=i, hours=1)
        end = now - timedelta(days=i)
        summaries.append(
            SessionSummary(
                session_id=f"s{i}",
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

    repo = MockSessionRepository(summaries, [])
    service = ProgressTrackingService(repo)

    async def run():
        ms, hl = await service.detect_and_update_milestones("p1")
        assert any(h.highlight_type == "milestone" for h in hl)
        titles = [h.title for h in hl]
        assert any("Session Milestone" in t for t in titles)

    asyncio.run(run())


def test_highlights_created_for_streak_milestone():
    now = datetime.utcnow()
    # 8 consecutive daily sessions triggers 7-day streak highlight
    summaries = []
    for i in range(8):
        start = now - timedelta(days=i, hours=1)
        end = now - timedelta(days=i)
        summaries.append(
            SessionSummary(
                session_id=f"s{i}",
                character_name="Char",
                world_name="World",
                start_time=start,
                end_time=end,
                duration_minutes=25,
                status=SessionStatus.COMPLETED,
                progress_markers_count=1,
                therapeutic_interventions_count=1,
            )
        )

    repo = MockSessionRepository(summaries, [])
    service = ProgressTrackingService(repo)

    async def run():
        ms, hl = await service.detect_and_update_milestones("p2")
        assert any(h.highlight_type == "milestone" for h in hl)
        titles = [h.title for h in hl]
        assert any("Streak Achievement" in t for t in titles)

    asyncio.run(run())
