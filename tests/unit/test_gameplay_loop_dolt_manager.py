"""
Unit tests for DoltGameplayManager.

All pymysql calls are mocked so no live Dolt server is required.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.components.gameplay_loop.database.dolt_manager import DoltGameplayManager
from src.components.gameplay_loop.models.core import (
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session() -> SessionState:
    ss = SessionState(user_id="user-42")
    return ss


def _make_scene() -> Scene:
    return Scene(
        scene_id="scene-abc",
        title="Test Scene",
        description="A calm clearing.",
        narrative_content="The wind whispers through the trees.",
        scene_type=SceneType.THERAPEUTIC,
        difficulty_level=DifficultyLevel.GENTLE,
    )


def _mock_connection(fetchone_return: dict | None = None, rowcount: int = 1):
    """Return a fake pymysql connection whose cursor behaves as needed."""
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchone.return_value = fetchone_return
    cursor.rowcount = rowcount

    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.ping.return_value = None
    return conn


# ---------------------------------------------------------------------------
# Initialize
# ---------------------------------------------------------------------------


class TestDoltGameplayManagerInit:
    async def test_initialize_returns_true_when_dolt_up(self):
        mgr = DoltGameplayManager()
        with patch.object(mgr, "_ensure_tables") as mock_ensure:
            mock_ensure.return_value = None
            result = await mgr.initialize()
        assert result is True
        assert mgr._available is True

    async def test_initialize_returns_false_when_dolt_down(self):
        mgr = DoltGameplayManager()
        with patch.object(
            mgr,
            "_ensure_tables",
            side_effect=RuntimeError("connection refused"),
        ):
            result = await mgr.initialize()
        assert result is False
        assert mgr._available is False

    async def test_close_is_noop(self):
        mgr = DoltGameplayManager()
        # Should not raise
        await mgr.close()


# ---------------------------------------------------------------------------
# create_session
# ---------------------------------------------------------------------------


class TestCreateSession:
    async def test_returns_false_when_unavailable(self):
        mgr = DoltGameplayManager()
        # _available is False by default
        result = await mgr.create_session(_make_session())
        assert result is False

    async def test_returns_true_on_success(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection()
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.create_session(_make_session())
        assert result is True

    async def test_returns_false_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.create_session(_make_session())
        assert result is False


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------


class TestGetSession:
    async def test_returns_none_when_unavailable(self):
        mgr = DoltGameplayManager()
        result = await mgr.get_session("session-1")
        assert result is None

    async def test_returns_none_when_not_found(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection(fetchone_return=None)
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.get_session("missing-id")
        assert result is None

    async def test_returns_session_state_when_found(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        session = _make_session()
        json_str = session.model_dump_json()
        conn = _mock_connection(fetchone_return={"state_json": json_str})
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.get_session(session.session_id)
        assert isinstance(result, SessionState)
        assert result.session_id == session.session_id

    async def test_returns_none_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.get_session("session-1")
        assert result is None

    async def test_returns_none_on_invalid_json(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection(fetchone_return={"state_json": "{not valid json}"})
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.get_session("session-1")
        assert result is None


# ---------------------------------------------------------------------------
# update_session
# ---------------------------------------------------------------------------


class TestUpdateSession:
    async def test_returns_false_when_unavailable(self):
        mgr = DoltGameplayManager()
        result = await mgr.update_session(_make_session())
        assert result is False

    async def test_returns_true_when_row_updated(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection(rowcount=1)
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.update_session(_make_session())
        assert result is True

    async def test_returns_false_when_row_not_found(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection(rowcount=0)
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.update_session(_make_session())
        assert result is False

    async def test_returns_false_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.update_session(_make_session())
        assert result is False


# ---------------------------------------------------------------------------
# create_scene
# ---------------------------------------------------------------------------


class TestCreateScene:
    async def test_returns_false_when_unavailable(self):
        mgr = DoltGameplayManager()
        result = await mgr.create_scene(_make_scene())
        assert result is False

    async def test_returns_true_on_success(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection()
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.create_scene(_make_scene())
        assert result is True

    async def test_returns_false_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.create_scene(_make_scene())
        assert result is False


# ---------------------------------------------------------------------------
# get_scene
# ---------------------------------------------------------------------------


class TestGetScene:
    async def test_returns_none_when_unavailable(self):
        mgr = DoltGameplayManager()
        result = await mgr.get_scene("scene-1")
        assert result is None

    async def test_returns_none_when_not_found(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection(fetchone_return=None)
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.get_scene("missing-id")
        assert result is None

    async def test_returns_scene_when_found(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        scene = _make_scene()
        conn = _mock_connection(fetchone_return={"scene_json": scene.model_dump_json()})
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.get_scene(scene.scene_id)
        assert isinstance(result, Scene)
        assert result.scene_id == scene.scene_id

    async def test_returns_none_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.get_scene("scene-1")
        assert result is None


# ---------------------------------------------------------------------------
# save_session_summary
# ---------------------------------------------------------------------------


class TestSaveSessionSummary:
    async def test_returns_false_when_unavailable(self):
        mgr = DoltGameplayManager()
        result = await mgr.save_session_summary("session-1", {"key": "value"})
        assert result is False

    async def test_returns_true_on_success(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection()
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.save_session_summary(
                "session-1", {"summary": "player progressed", "score": 0.8}
            )
        assert result is True

    async def test_returns_false_on_db_error(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        with patch.object(
            mgr, "_connect", side_effect=RuntimeError("db error")
        ):
            result = await mgr.save_session_summary("session-1", {})
        assert result is False

    async def test_accepts_empty_summary(self):
        mgr = DoltGameplayManager()
        mgr._available = True
        conn = _mock_connection()
        with patch.object(mgr, "_connect", return_value=conn):
            result = await mgr.save_session_summary("session-1", {})
        assert result is True


# ---------------------------------------------------------------------------
# Round-trip: create + get
# ---------------------------------------------------------------------------


class TestRoundTrip:
    async def test_session_state_round_trip_via_json(self):
        """SessionState survives model_dump_json → model_validate_json."""
        ss = SessionState(user_id="user-rt")
        ss.emotional_state = EmotionalState.ANXIOUS
        json_str = ss.model_dump_json()
        restored = SessionState.model_validate_json(json_str)
        assert restored.session_id == ss.session_id
        assert restored.emotional_state == EmotionalState.ANXIOUS

    async def test_scene_round_trip_via_json(self):
        """Scene survives model_dump_json → model_validate_json."""
        scene = _make_scene()
        json_str = scene.model_dump_json()
        restored = Scene.model_validate_json(json_str)
        assert restored.scene_id == scene.scene_id
        assert restored.scene_type == SceneType.THERAPEUTIC
