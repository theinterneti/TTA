"""
End-to-end smoke test for the complete gameplay loop.

Exercises the full session lifecycle without any live external services:
  start_session
  → get_session_status  (active, in-memory)
  → process_user_choice
  → get_session_status  (choice recorded)
  → pause_session       (persisted to DB, removed from active)
  → get_session_status  (DB fallback — is_active False)
  → resume_session      (reloaded from DB)
  → get_session_status  (active again)
  → end_session         (summary saved, removed from active)
  → get_session_status  (DB fallback — is_active False, summary exists)

All DB operations are handled by an in-memory FakeDb so no Neo4j / Dolt /
Redis is required.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.components.gameplay_loop.models.core import (
    Choice,
    ChoiceType,
    ConsequenceSet,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)


# ---------------------------------------------------------------------------
# FakeDb — in-memory stand-in for Neo4jGameplayManager / DoltGameplayManager
# ---------------------------------------------------------------------------


class FakeDb:
    """Synchronous in-memory store that implements the gameplay manager interface."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._scenes: dict[str, Scene] = {}
        self._summaries: dict[str, dict] = {}

        self.call_counts: dict[str, int] = {
            "initialize": 0,
            "create_session": 0,
            "get_session": 0,
            "update_session": 0,
            "create_scene": 0,
            "save_session_summary": 0,
        }

    async def initialize(self) -> bool:
        self.call_counts["initialize"] += 1
        return True

    async def create_session(self, session_state: SessionState) -> bool:
        self.call_counts["create_session"] += 1
        self._sessions[session_state.session_id] = session_state
        return True

    async def get_session(self, session_id: str) -> SessionState | None:
        self.call_counts["get_session"] += 1
        return self._sessions.get(session_id)

    async def update_session(self, session_state: SessionState) -> bool:
        self.call_counts["update_session"] += 1
        self._sessions[session_state.session_id] = session_state
        return True

    async def create_scene(self, scene: Scene) -> bool:
        self.call_counts["create_scene"] += 1
        self._scenes[scene.scene_id] = scene
        return True

    async def save_session_summary(
        self, session_id: str, summary: dict
    ) -> bool:
        self.call_counts["save_session_summary"] += 1
        self._summaries[session_id] = summary
        return True

    async def get_sessions_for_user(self, user_id: str) -> list:
        return [ss for ss in self._sessions.values() if ss.user_id == user_id]


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_scene(scene_id: str = "scene-1") -> Scene:
    return Scene(
        scene_id=scene_id,
        title="Test Scene",
        description="A peaceful space.",
        narrative_content="The light is warm.",
        scene_type=SceneType.INTRODUCTION,
    )


def _make_choice(choice_id: str = "choice-1") -> Choice:
    return Choice(
        choice_id=choice_id,
        choice_text="Take a deep breath",
        choice_type=ChoiceType.THERAPEUTIC,
        therapeutic_value=0.8,
        therapeutic_tags=["mindfulness", "grounding"],
        agency_level=0.7,
        meaningfulness_score=0.8,
    )


def _make_consequence(choice_id: str = "choice-1") -> ConsequenceSet:
    return ConsequenceSet(
        choice_id=choice_id,
        immediate_outcomes=["You feel calmer"],
        therapeutic_insights=["Breath is an anchor"],
        learning_opportunities=["mindfulness", "self_regulation"],
        causality_explanation="Your choice to pause brought calm.",
        therapeutic_value_realized=0.8,
        emotional_impact={"primary_emotion": "calm", "intensity": 0.6},
    )


# ---------------------------------------------------------------------------
# E2E Smoke Test
# ---------------------------------------------------------------------------


@pytest.fixture
async def controller_with_fake_db():
    """
    A real GameplayLoopController backed by FakeDb and lightweight mocks
    for the narrative/choice/consequence sub-systems.
    """
    fake_db = FakeDb()

    opening_scene = _make_scene("scene-opening")
    next_scene = _make_scene("scene-next")
    choices = [_make_choice("choice-1")]
    consequence = _make_consequence("choice-1")

    with (
        patch(
            "src.components.gameplay_loop.controller.get_llm",
            return_value=None,
        ),
        patch(
            "src.components.gameplay_loop.controller.Neo4jGameplayManager",
            autospec=True,
        ),
        patch(
            "src.components.gameplay_loop.controller.NarrativeEngine",
            autospec=True,
        ) as MockNarrative,
        patch(
            "src.components.gameplay_loop.controller.ChoiceArchitectureManager",
            autospec=True,
        ) as MockChoice,
        patch(
            "src.components.gameplay_loop.controller.ConsequenceSystem",
            autospec=True,
        ) as MockConsequence,
    ):
        from src.components.gameplay_loop.controller import GameplayLoopController

        ctrl = GameplayLoopController(db_manager=fake_db)

        # Wire sub-system mocks
        nar = MockNarrative.return_value
        nar.initialize = AsyncMock(return_value=True)
        nar.generate_opening_scene = AsyncMock(return_value=opening_scene)
        nar.generate_next_scene = AsyncMock(return_value=next_scene)

        cho = MockChoice.return_value
        cho.initialize = AsyncMock(return_value=True)
        cho.generate_choices_for_scene = AsyncMock(return_value=choices)

        csq = MockConsequence.return_value
        csq.initialize = AsyncMock(return_value=True)
        csq.generate_consequences = AsyncMock(return_value=consequence)

        ctrl.narrative_engine = nar
        ctrl.choice_architecture = cho
        ctrl.consequence_system = csq

        await ctrl.initialize()

        yield ctrl, fake_db


class TestFullLoopSmoke:
    async def test_start_session_creates_db_record(self, controller_with_fake_db):
        ctrl, db = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        assert session is not None
        assert session.session_id
        assert session.user_id == "player-1"
        assert db.call_counts["create_session"] == 1

    async def test_start_session_generates_opening_scene(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        assert session.current_scene is not None
        assert session.current_scene.scene_id == "scene-opening"

    async def test_start_session_generates_initial_choices(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        assert len(session.available_choices) == 1
        assert session.available_choices[0].choice_id == "choice-1"

    async def test_get_status_after_start_is_active(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        status = await ctrl.get_session_status(session.session_id)

        assert status is not None
        assert status["is_active"] is True
        assert status["user_id"] == "player-1"
        assert status["total_choices"] == 0

    async def test_process_choice_advances_scene(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        next_scene, new_choices, consequences = await ctrl.process_user_choice(
            session.session_id, "choice-1"
        )

        assert next_scene is not None
        assert next_scene.scene_id == "scene-next"
        assert len(new_choices) == 1
        assert consequences is not None

    async def test_process_choice_updates_db(self, controller_with_fake_db):
        ctrl, db = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        await ctrl.process_user_choice(session.session_id, "choice-1")

        assert db.call_counts["update_session"] >= 1

    async def test_get_status_records_choice_count(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        await ctrl.process_user_choice(session.session_id, "choice-1")

        status = await ctrl.get_session_status(session.session_id)

        assert status is not None
        assert status["total_choices"] == 1

    async def test_pause_removes_session_from_active(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        result = await ctrl.pause_session(session.session_id)

        assert result is True
        assert session.session_id not in ctrl.active_sessions

    async def test_get_status_after_pause_uses_db_fallback(
        self, controller_with_fake_db
    ):
        ctrl, db = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.pause_session(sid)

        # Not in active_sessions; controller must go to DB
        status = await ctrl.get_session_status(sid)

        assert status is not None
        assert status["is_active"] is False
        assert status["user_id"] == "player-1"
        assert db.call_counts["get_session"] >= 1

    async def test_paused_status_preserves_choice_history(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        await ctrl.process_user_choice(session.session_id, "choice-1")
        await ctrl.pause_session(session.session_id)

        status = await ctrl.get_session_status(session.session_id)

        assert status is not None
        assert status["total_choices"] == 1

    async def test_resume_restores_session_to_active(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.pause_session(sid)

        resumed = await ctrl.resume_session(sid)

        assert resumed is not None
        assert resumed.session_id == sid
        assert sid in ctrl.active_sessions

    async def test_get_status_after_resume_is_active(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.pause_session(sid)
        await ctrl.resume_session(sid)

        status = await ctrl.get_session_status(sid)

        assert status is not None
        assert status["is_active"] is True

    async def test_resume_includes_session_recap(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.pause_session(sid)

        resumed = await ctrl.resume_session(sid)

        assert resumed is not None
        assert isinstance(resumed.session_recap, str)
        assert len(resumed.session_recap) > 0

    async def test_end_session_removes_from_active(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id

        result = await ctrl.end_session(sid)

        assert result is True
        assert sid not in ctrl.active_sessions

    async def test_end_session_saves_summary(self, controller_with_fake_db):
        ctrl, db = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        await ctrl.end_session(session.session_id)

        assert db.call_counts["save_session_summary"] == 1

    async def test_end_session_status_falls_back_to_db(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.end_session(sid)

        # Session ended — falls back to DB
        status = await ctrl.get_session_status(sid)

        assert status is not None
        assert status["is_active"] is False

    async def test_unknown_session_returns_none(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db

        status = await ctrl.get_session_status("does-not-exist")

        assert status is None

    async def test_full_loop_sequence(self, controller_with_fake_db):
        """
        One test that runs the complete sequence and checks db call counts.
        """
        ctrl, db = controller_with_fake_db
        user_id = "player-full"

        # 1. Start
        session = await ctrl.start_session(user_id=user_id)
        sid = session.session_id
        assert db.call_counts["create_session"] == 1

        # 2. Status (active)
        s1 = await ctrl.get_session_status(sid)
        assert s1 is not None and s1["is_active"] is True

        # 3. Process choice
        next_scene, choices, csq = await ctrl.process_user_choice(sid, "choice-1")
        assert next_scene is not None
        assert csq is not None

        # 4. Status (choice recorded)
        s2 = await ctrl.get_session_status(sid)
        assert s2 is not None and s2["total_choices"] == 1

        # 5. Pause
        assert await ctrl.pause_session(sid) is True

        # 6. Status (DB fallback)
        s3 = await ctrl.get_session_status(sid)
        assert s3 is not None and s3["is_active"] is False

        # 7. Resume
        resumed = await ctrl.resume_session(sid)
        assert resumed is not None

        # 8. Status (active again)
        s4 = await ctrl.get_session_status(sid)
        assert s4 is not None and s4["is_active"] is True

        # 9. End
        assert await ctrl.end_session(sid) is True
        assert sid not in ctrl.active_sessions
        assert db.call_counts["save_session_summary"] == 1

        # 10. Status (DB fallback after end)
        s5 = await ctrl.get_session_status(sid)
        assert s5 is not None and s5["is_active"] is False

    async def test_therapeutic_engagement_tracked_through_loop(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        # Process a choice with therapeutic_value=0.8
        await ctrl.process_user_choice(session.session_id, "choice-1")

        status = await ctrl.get_session_status(session.session_id)
        assert status is not None
        assert status["therapeutic_engagement"] == pytest.approx(0.8)

    async def test_emotional_state_updated_by_consequence(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")

        # Consequence returns emotional_impact.primary_emotion = "calm"
        await ctrl.process_user_choice(session.session_id, "choice-1")

        status = await ctrl.get_session_status(session.session_id)
        assert status is not None
        assert status["emotional_state"] == EmotionalState.CALM.value


# ---------------------------------------------------------------------------
# Auto-resume in process_user_choice (Task 45)
# ---------------------------------------------------------------------------


class TestAutoResume:
    """process_user_choice auto-resumes from DB when session not in active_sessions."""

    async def test_choice_succeeds_after_pause_without_explicit_resume(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id

        # Pause the session (removes from active_sessions)
        await ctrl.pause_session(sid)
        assert sid not in ctrl.active_sessions

        # Send a choice without calling resume_session first
        next_scene, choices, consequences = await ctrl.process_user_choice(
            sid, "choice-1"
        )

        # Should succeed via auto-resume
        assert next_scene is not None
        assert consequences is not None

    async def test_choice_auto_resume_restores_session_to_active(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id
        await ctrl.pause_session(sid)

        await ctrl.process_user_choice(sid, "choice-1")

        # Session should be back in active_sessions after auto-resume
        assert sid in ctrl.active_sessions

    async def test_choice_for_truly_missing_session_returns_none_tuple(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db

        next_scene, choices, consequences = await ctrl.process_user_choice(
            "nonexistent-session", "choice-x"
        )

        assert next_scene is None
        assert choices == []
        assert consequences is None

    async def test_auto_resume_preserves_prior_choice_history(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-1")
        sid = session.session_id

        # Make one choice while active, then pause
        await ctrl.process_user_choice(sid, "choice-1")
        await ctrl.pause_session(sid)

        # Second choice via auto-resume
        await ctrl.process_user_choice(sid, "choice-1")

        status = await ctrl.get_session_status(sid)
        assert status is not None
        assert status["total_choices"] == 2


# ---------------------------------------------------------------------------
# get_sessions_for_user (Task 46)
# ---------------------------------------------------------------------------


class TestGetSessionsForUser:
    """Controller.get_sessions_for_user merges active + DB sessions for a user."""

    async def test_returns_active_session_for_user(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-alpha")

        sessions = await ctrl.get_sessions_for_user("player-alpha")

        assert len(sessions) == 1
        assert sessions[0]["user_id"] == "player-alpha"
        assert sessions[0]["session_id"] == session.session_id

    async def test_does_not_return_other_users_sessions(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        await ctrl.start_session(user_id="player-alpha")
        await ctrl.start_session(user_id="player-beta")

        sessions = await ctrl.get_sessions_for_user("player-alpha")

        assert all(s["user_id"] == "player-alpha" for s in sessions)
        assert len(sessions) == 1

    async def test_returns_paused_session_via_db(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-alpha")
        sid = session.session_id
        await ctrl.pause_session(sid)

        sessions = await ctrl.get_sessions_for_user("player-alpha")

        # FakeDb.get_sessions_for_user returns persisted sessions
        assert any(s["session_id"] == sid for s in sessions)

    async def test_returns_empty_for_unknown_user(self, controller_with_fake_db):
        ctrl, _ = controller_with_fake_db

        sessions = await ctrl.get_sessions_for_user("nobody")

        assert sessions == []

    async def test_active_session_not_duplicated_with_db(
        self, controller_with_fake_db
    ):
        ctrl, _ = controller_with_fake_db
        session = await ctrl.start_session(user_id="player-alpha")
        sid = session.session_id

        sessions = await ctrl.get_sessions_for_user("player-alpha")

        # Session is both in active_sessions AND in DB (created on start)
        # Should only appear once
        ids = [s["session_id"] for s in sessions]
        assert ids.count(sid) == 1
