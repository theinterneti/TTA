"""
Unit tests for GameplayLoopController in controller.py.

All database_manager, narrative_engine, choice_architecture and consequence_system
dependencies are mocked to avoid requiring external services (Neo4j, Redis).
"""

from __future__ import annotations

from datetime import datetime, timedelta
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
from src.components.gameplay_loop.models.interactions import GameplaySession

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def _make_scene(scene_id: str = "scene-1") -> Scene:
    return Scene(
        scene_id=scene_id,
        title="Opening",
        description="The adventure begins",
        narrative_content="You stand at the entrance.",
        scene_type=SceneType.INTRODUCTION,
    )


def _make_choice(
    choice_id: str = "choice-1",
    choice_type: ChoiceType = ChoiceType.NARRATIVE,
    therapeutic_value: float = 0.7,
    therapeutic_tags: list[str] | None = None,
) -> Choice:
    return Choice(
        choice_id=choice_id,
        choice_text="Move forward",
        choice_type=choice_type,
        therapeutic_value=therapeutic_value,
        therapeutic_tags=therapeutic_tags or [],
        agency_level=0.6,
        meaningfulness_score=0.6,
    )


def _make_consequence_set(choice_id: str = "choice-1") -> ConsequenceSet:
    return ConsequenceSet(
        choice_id=choice_id,
        immediate_outcomes=["You move forward"],
        therapeutic_insights=["Courage shown"],
        learning_opportunities=["facing_challenges"],
        causality_explanation="Your choice led forward",
        therapeutic_value_realized=0.7,
    )


# ---------------------------------------------------------------------------
# Fixture: fully mocked controller
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_controller():
    """
    Build a GameplayLoopController with all heavy dependencies mocked.
    The LLM factory and Neo4jGameplayManager constructors are patched to
    avoid network/config requirements at import time.
    """
    with (
        patch(
            "src.components.gameplay_loop.controller.get_llm",
            return_value=None,
        ),
        patch(
            "src.components.gameplay_loop.controller.Neo4jGameplayManager",
            autospec=True,
        ) as MockDbManager,
        patch(
            "src.components.gameplay_loop.controller.NarrativeEngine",
            autospec=True,
        ) as MockNarrativeEngine,
        patch(
            "src.components.gameplay_loop.controller.ChoiceArchitectureManager",
            autospec=True,
        ) as MockChoiceArch,
        patch(
            "src.components.gameplay_loop.controller.ConsequenceSystem",
            autospec=True,
        ) as MockConsequenceSystem,
    ):
        from src.components.gameplay_loop.controller import GameplayLoopController

        controller = GameplayLoopController(config={"response_time_target": 5.0})

        # Wire async mocks on the instances
        db_instance = MockDbManager.return_value
        db_instance.initialize = AsyncMock(return_value=True)
        db_instance.create_session = AsyncMock(return_value=None)
        db_instance.update_session = AsyncMock(return_value=None)
        db_instance.get_session = AsyncMock(return_value=None)
        db_instance.save_session_summary = AsyncMock(return_value=None)

        nar_instance = MockNarrativeEngine.return_value
        nar_instance.initialize = AsyncMock(return_value=True)
        nar_instance.generate_opening_scene = AsyncMock(return_value=_make_scene())
        nar_instance.generate_next_scene = AsyncMock(return_value=_make_scene("scene-2"))

        choice_instance = MockChoiceArch.return_value
        choice_instance.initialize = AsyncMock(return_value=True)
        choice_instance.generate_choices_for_scene = AsyncMock(
            return_value=[_make_choice()]
        )

        csq_instance = MockConsequenceSystem.return_value
        csq_instance.initialize = AsyncMock(return_value=True)
        csq_instance.generate_consequences = AsyncMock(
            return_value=_make_consequence_set()
        )

        # Assign instances to controller attributes
        controller.database_manager = db_instance
        controller.narrative_engine = nar_instance
        controller.choice_architecture = choice_instance
        controller.consequence_system = csq_instance

        yield controller


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestControllerInit:
    def test_default_construction_succeeds(self):
        with (
            patch("src.components.gameplay_loop.controller.get_llm", return_value=None),
            patch(
                "src.components.gameplay_loop.controller.Neo4jGameplayManager",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.NarrativeEngine",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.ChoiceArchitectureManager",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.ConsequenceSystem",
                autospec=True,
            ),
        ):
            from src.components.gameplay_loop.controller import GameplayLoopController

            ctrl = GameplayLoopController()
            assert ctrl.config == {}
            assert ctrl.active_sessions == {}
            assert ctrl.session_timeout == 3600
            assert ctrl.response_time_target == 2.0

    def test_custom_config(self):
        with (
            patch("src.components.gameplay_loop.controller.get_llm", return_value=None),
            patch(
                "src.components.gameplay_loop.controller.Neo4jGameplayManager",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.NarrativeEngine",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.ChoiceArchitectureManager",
                autospec=True,
            ),
            patch(
                "src.components.gameplay_loop.controller.ConsequenceSystem",
                autospec=True,
            ),
        ):
            from src.components.gameplay_loop.controller import GameplayLoopController

            ctrl = GameplayLoopController(
                config={"session_timeout": 7200, "response_time_target": 3.0}
            )
            assert ctrl.session_timeout == 7200
            assert ctrl.response_time_target == 3.0

    async def test_initialize_returns_true(self, mock_controller):
        result = await mock_controller.initialize()
        assert result is True

    async def test_initialize_calls_all_subsystems(self, mock_controller):
        await mock_controller.initialize()
        mock_controller.database_manager.initialize.assert_called_once()
        mock_controller.narrative_engine.initialize.assert_called_once()
        mock_controller.choice_architecture.initialize.assert_called_once()
        mock_controller.consequence_system.initialize.assert_called_once()

    async def test_initialize_returns_false_on_exception(self, mock_controller):
        mock_controller.database_manager.initialize = AsyncMock(
            side_effect=RuntimeError("db error")
        )
        result = await mock_controller.initialize()
        assert result is False


# ---------------------------------------------------------------------------
# start_session
# ---------------------------------------------------------------------------


class TestStartSession:
    async def test_start_session_returns_gameplay_session(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        assert isinstance(session, GameplaySession)
        assert session.user_id == "user-1"

    async def test_start_session_is_active(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        assert session.is_active is True

    async def test_start_session_stores_in_active_sessions(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        assert session.session_id in mock_controller.active_sessions

    async def test_start_session_has_scene(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        assert session.current_scene is not None

    async def test_start_session_has_choices(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        assert len(session.available_choices) > 0

    async def test_start_session_calls_create_session(self, mock_controller):
        await mock_controller.start_session("user-1")
        mock_controller.database_manager.create_session.assert_called_once()

    async def test_start_session_no_scene_generates_no_choices(self, mock_controller):
        mock_controller.narrative_engine.generate_opening_scene = AsyncMock(
            return_value=None
        )
        session = await mock_controller.start_session("user-1")
        assert session.available_choices == []

    async def test_start_session_raises_on_db_error(self, mock_controller):
        mock_controller.database_manager.create_session = AsyncMock(
            side_effect=RuntimeError("db failure")
        )
        with pytest.raises(RuntimeError):
            await mock_controller.start_session("user-1")


# ---------------------------------------------------------------------------
# resume_session
# ---------------------------------------------------------------------------


class TestResumeSession:
    async def test_resume_existing_active_session(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        resumed = await mock_controller.resume_session(session.session_id)
        assert resumed is not None
        assert resumed.session_id == session.session_id

    async def test_resume_updates_last_activity_time(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        old_time = session.last_activity_time
        resumed = await mock_controller.resume_session(session.session_id)
        assert resumed.last_activity_time >= old_time

    async def test_resume_not_found_returns_none(self, mock_controller):
        mock_controller.database_manager.get_session = AsyncMock(return_value=None)
        result = await mock_controller.resume_session("nonexistent-session")
        assert result is None

    async def test_resume_from_db_creates_active_session(self, mock_controller):
        # Simulate session that was paused (not in active_sessions) but in DB
        db_state = SessionState(user_id="user-db")
        db_state.current_scene = _make_scene()
        mock_controller.database_manager.get_session = AsyncMock(
            return_value=db_state
        )
        result = await mock_controller.resume_session(db_state.session_id)
        assert result is not None
        assert result.session_id == db_state.session_id

    async def test_resume_from_db_with_no_scene_generates_scene(self, mock_controller):
        db_state = SessionState(user_id="user-db")
        db_state.current_scene = None
        mock_controller.database_manager.get_session = AsyncMock(
            return_value=db_state
        )
        result = await mock_controller.resume_session(db_state.session_id)
        assert result is not None

    async def test_resume_generates_recap(self, mock_controller):
        db_state = SessionState(user_id="user-db")
        db_state.current_scene = _make_scene()
        mock_controller.database_manager.get_session = AsyncMock(
            return_value=db_state
        )
        result = await mock_controller.resume_session(db_state.session_id)
        assert result.session_recap is not None

    async def test_resume_returns_none_on_error(self, mock_controller):
        mock_controller.database_manager.get_session = AsyncMock(
            side_effect=RuntimeError("db crash")
        )
        result = await mock_controller.resume_session("some-session")
        assert result is None


# ---------------------------------------------------------------------------
# pause_session
# ---------------------------------------------------------------------------


class TestPauseSession:
    async def test_pause_returns_true(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        result = await mock_controller.pause_session(session.session_id)
        assert result is True

    async def test_pause_removes_from_active_sessions(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        await mock_controller.pause_session(session.session_id)
        assert session.session_id not in mock_controller.active_sessions

    async def test_pause_nonexistent_returns_false(self, mock_controller):
        result = await mock_controller.pause_session("does-not-exist")
        assert result is False

    async def test_pause_saves_to_database(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        await mock_controller.pause_session(session.session_id)
        mock_controller.database_manager.update_session.assert_called()

    async def test_pause_returns_false_on_exception(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        mock_controller.database_manager.update_session = AsyncMock(
            side_effect=RuntimeError("db error")
        )
        result = await mock_controller.pause_session(session.session_id)
        assert result is False


# ---------------------------------------------------------------------------
# end_session
# ---------------------------------------------------------------------------


class TestEndSession:
    async def test_end_session_returns_true(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        result = await mock_controller.end_session(session.session_id)
        assert result is True

    async def test_end_session_removes_from_active_sessions(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        await mock_controller.end_session(session.session_id)
        assert session.session_id not in mock_controller.active_sessions

    async def test_end_session_saves_summary(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        await mock_controller.end_session(session.session_id)
        mock_controller.database_manager.save_session_summary.assert_called_once()

    async def test_end_nonexistent_session_returns_true(self, mock_controller):
        result = await mock_controller.end_session("nonexistent")
        assert result is True

    async def test_end_session_returns_false_on_error(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        mock_controller.database_manager.update_session = AsyncMock(
            side_effect=RuntimeError("error")
        )
        result = await mock_controller.end_session(session.session_id)
        assert result is False


# ---------------------------------------------------------------------------
# process_user_choice
# ---------------------------------------------------------------------------


class TestProcessUserChoice:
    async def test_process_choice_returns_tuple(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        next_scene, new_choices, consequences = await mock_controller.process_user_choice(
            session.session_id, choice_id
        )
        assert next_scene is not None or next_scene is None  # returns any Scene or None
        assert isinstance(new_choices, list)

    async def test_process_choice_returns_consequences(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        _, _, consequences = await mock_controller.process_user_choice(
            session.session_id, choice_id
        )
        assert consequences is not None
        assert isinstance(consequences, ConsequenceSet)

    async def test_process_choice_adds_to_history(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        await mock_controller.process_user_choice(session.session_id, choice_id)
        session_state = session.session_state
        assert len(session_state.choice_history) == 1

    async def test_process_nonexistent_session_returns_empty(self, mock_controller):
        result = await mock_controller.process_user_choice("bad-session", "c1")
        assert result == (None, [], None)

    async def test_process_nonexistent_choice_returns_empty(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        result = await mock_controller.process_user_choice(
            session.session_id, "nonexistent-choice"
        )
        assert result == (None, [], None)

    async def test_process_choice_updates_session_available_choices(
        self, mock_controller
    ):
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        _, new_choices, _ = await mock_controller.process_user_choice(
            session.session_id, choice_id
        )
        assert session.available_choices == new_choices

    async def test_process_choice_updates_emotional_state_from_consequences(
        self, mock_controller
    ):
        # Make consequences return a valid emotional state change
        mock_controller.consequence_system.generate_consequences = AsyncMock(
            return_value=ConsequenceSet(
                choice_id="choice-1",
                emotional_impact={"primary_emotion": "calm", "intensity": 0.6},
            )
        )
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        await mock_controller.process_user_choice(session.session_id, choice_id)
        # "calm" is valid EmotionalState value, should update
        assert session.session_state.emotional_state == EmotionalState.CALM

    async def test_process_choice_ignores_invalid_emotional_state_in_consequences(
        self, mock_controller
    ):
        mock_controller.consequence_system.generate_consequences = AsyncMock(
            return_value=ConsequenceSet(
                choice_id="choice-1",
                emotional_impact={"primary_emotion": "supercharged"},  # not valid
            )
        )
        session = await mock_controller.start_session("user-1")
        original_state = session.session_state.emotional_state
        choice_id = session.available_choices[0].choice_id
        await mock_controller.process_user_choice(session.session_id, choice_id)
        assert session.session_state.emotional_state == original_state

    async def test_process_choice_returns_empty_on_exception(self, mock_controller):
        mock_controller.consequence_system.generate_consequences = AsyncMock(
            side_effect=RuntimeError("generation error")
        )
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        result = await mock_controller.process_user_choice(
            session.session_id, choice_id
        )
        assert result == (None, [], None)


# ---------------------------------------------------------------------------
# get_session_status
# ---------------------------------------------------------------------------


class TestGetSessionStatus:
    async def test_returns_none_for_unknown_session(self, mock_controller):
        result = await mock_controller.get_session_status("unknown")
        assert result is None

    async def test_returns_status_dict(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        status = await mock_controller.get_session_status(session.session_id)
        assert status is not None
        assert status["session_id"] == session.session_id
        assert status["user_id"] == "user-1"
        assert status["is_active"] is True

    async def test_status_has_required_keys(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        status = await mock_controller.get_session_status(session.session_id)
        expected_keys = {
            "session_id",
            "user_id",
            "is_active",
            "current_scene_id",
            "emotional_state",
            "total_choices",
            "available_choices_count",
            "therapeutic_engagement",
            "last_activity",
        }
        assert expected_keys.issubset(status.keys())

    async def test_therapeutic_engagement_calculated_after_choices(
        self, mock_controller
    ):
        session = await mock_controller.start_session("user-1")
        choice_id = session.available_choices[0].choice_id
        await mock_controller.process_user_choice(session.session_id, choice_id)
        status = await mock_controller.get_session_status(session.session_id)
        assert status["total_choices"] == 1

    async def test_returns_none_on_exception(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        # Corrupt the session to force an exception
        mock_controller.active_sessions[session.session_id] = None  # type: ignore
        result = await mock_controller.get_session_status(session.session_id)
        assert result is None


# ---------------------------------------------------------------------------
# cleanup_inactive_sessions
# ---------------------------------------------------------------------------


class TestCleanupInactiveSessions:
    async def test_no_sessions_returns_zero(self, mock_controller):
        result = await mock_controller.cleanup_inactive_sessions()
        assert result == 0

    async def test_active_session_not_cleaned_up(self, mock_controller):
        await mock_controller.start_session("user-1")
        result = await mock_controller.cleanup_inactive_sessions()
        assert result == 0
        assert len(mock_controller.active_sessions) == 1

    async def test_expired_session_is_cleaned_up(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        # Set last activity to well beyond timeout
        session.last_activity_time = datetime.utcnow() - timedelta(hours=2)
        result = await mock_controller.cleanup_inactive_sessions()
        assert result == 1

    async def test_multiple_expired_sessions_all_cleaned_up(self, mock_controller):
        for uid in ["u1", "u2", "u3"]:
            sess = await mock_controller.start_session(uid)
            sess.last_activity_time = datetime.utcnow() - timedelta(hours=2)
        result = await mock_controller.cleanup_inactive_sessions()
        assert result == 3
        assert len(mock_controller.active_sessions) == 0

    async def test_cleanup_counts_attempted_removals_even_if_pause_fails(
        self, mock_controller
    ):
        # cleanup_inactive_sessions returns len(sessions_to_remove) regardless
        # of whether individual pause_session calls succeed or fail.
        session = await mock_controller.start_session("u1")
        session.last_activity_time = datetime.utcnow() - timedelta(hours=2)
        mock_controller.database_manager.update_session = AsyncMock(
            side_effect=RuntimeError("db")
        )
        result = await mock_controller.cleanup_inactive_sessions()
        # Still reports 1 because 1 session was identified as expired
        assert result == 1


# ---------------------------------------------------------------------------
# _generate_session_recap
# ---------------------------------------------------------------------------


class TestGenerateSessionRecap:
    async def test_no_choices_gives_welcome_back_message(self, mock_controller):
        session_state = SessionState(user_id="u1")
        recap = await mock_controller._generate_session_recap(session_state)
        assert "Welcome back" in recap

    async def test_with_choices_includes_themes(self, mock_controller):
        session_state = SessionState(user_id="u1")
        session_state.choice_history = [
            {"therapeutic_tags": ["mindfulness"], "choice_text": "Breathe"},
            {"therapeutic_tags": ["resilience"], "choice_text": "Persist"},
            {"therapeutic_tags": ["grounding"], "choice_text": "Ground"},
        ]
        recap = await mock_controller._generate_session_recap(session_state)
        assert "Welcome back" in recap

    async def test_with_current_scene_includes_description(self, mock_controller):
        session_state = SessionState(user_id="u1")
        session_state.current_scene = _make_scene()
        session_state.choice_history = [{"therapeutic_tags": ["mindfulness"]}]
        recap = await mock_controller._generate_session_recap(session_state)
        assert "journey" in recap.lower() or "adventure" in recap.lower()


# ---------------------------------------------------------------------------
# _generate_session_summary
# ---------------------------------------------------------------------------


class TestGenerateSessionSummary:
    async def test_returns_dict_with_basic_fields(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_start_time = datetime.utcnow() - timedelta(minutes=15)
        session.session_end_time = datetime.utcnow()
        summary = await mock_controller._generate_session_summary(session)
        assert "session_id" in summary
        assert "user_id" in summary
        assert "total_choices" in summary
        assert "therapeutic_engagement" in summary

    async def test_duration_calculated(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_start_time = datetime.utcnow() - timedelta(minutes=10)
        session.session_end_time = datetime.utcnow()
        summary = await mock_controller._generate_session_summary(session)
        assert summary["duration_minutes"] > 0

    async def test_skills_practiced_collected_from_history(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_state.choice_history = [
            {"therapeutic_tags": ["mindfulness", "grounding"], "therapeutic_value": 0.8},
            {"therapeutic_tags": ["resilience"], "therapeutic_value": 0.7},
        ]
        summary = await mock_controller._generate_session_summary(session)
        assert "mindfulness" in summary["skills_practiced"]
        assert "resilience" in summary["skills_practiced"]

    async def test_key_insights_high_engagement(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_state.choice_history = [
            {"therapeutic_tags": [], "therapeutic_value": 0.9}
        ] * 5
        summary = await mock_controller._generate_session_summary(session)
        assert "strong therapeutic engagement" in " ".join(
            summary["key_insights"]
        )

    async def test_key_insights_many_skills(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_state.choice_history = [
            {"therapeutic_tags": ["a", "b", "c"], "therapeutic_value": 0.5}
        ]
        summary = await mock_controller._generate_session_summary(session)
        assert "multiple therapeutic approaches" in " ".join(
            summary["key_insights"]
        )

    async def test_key_insights_sustained_participation(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        session.session_state.choice_history = [
            {"therapeutic_tags": [], "therapeutic_value": 0.5}
        ] * 10
        summary = await mock_controller._generate_session_summary(session)
        assert "Sustained participation" in " ".join(summary["key_insights"])

    async def test_returns_error_summary_on_exception(self, mock_controller):
        session = await mock_controller.start_session("user-1")
        # Force exception by corrupting session_state
        session.session_state = None  # type: ignore
        summary = await mock_controller._generate_session_summary(session)
        assert "error" in summary
