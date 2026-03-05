"""
Unit tests for session lifecycle DB wiring and API route changes.

Covers:
- GameplayLoopController.get_session_status DB fallback (Task 42)
- Gameplay router pause/resume endpoints (Task 43)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

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


def _make_session_state(user_id: str = "user-42") -> SessionState:
    ss = SessionState(user_id=user_id)
    ss.emotional_state = EmotionalState.CALM
    return ss


def _make_scene() -> Scene:
    return Scene(
        scene_id="scene-1",
        title="Test",
        description="Desc",
        narrative_content="Content",
        scene_type=SceneType.THERAPEUTIC,
        difficulty_level=DifficultyLevel.GENTLE,
    )


def _make_gameplay_session(session_state: SessionState) -> MagicMock:
    gs = MagicMock()
    gs.session_id = session_state.session_id
    gs.user_id = session_state.user_id
    gs.is_active = True
    gs.session_state = session_state
    gs.available_choices = []
    gs.last_activity_time = None
    return gs


# ---------------------------------------------------------------------------
# Task 42 — get_session_status DB fallback
# ---------------------------------------------------------------------------


class TestGetSessionStatusDbFallback:
    """Controller.get_session_status falls back to DB when not in active_sessions."""

    async def _make_controller(self, db_get_session_return=None):
        """Create a controller with a mocked db_manager."""
        from src.components.gameplay_loop.controller import GameplayLoopController

        mock_db = AsyncMock()
        mock_db.initialize = AsyncMock(return_value=True)
        mock_db.get_session = AsyncMock(return_value=db_get_session_return)

        with patch(
            "src.components.gameplay_loop.controller.Neo4jGameplayManager",
            autospec=True,
        ):
            ctrl = GameplayLoopController(db_manager=mock_db)
        return ctrl, mock_db

    async def test_active_session_returned_from_memory(self):
        ctrl, mock_db = await self._make_controller()
        ss = _make_session_state()
        gs = _make_gameplay_session(ss)
        ctrl.active_sessions[ss.session_id] = gs

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert result["is_active"] is True
        assert result["user_id"] == ss.user_id
        # DB not called when session is in active_sessions
        mock_db.get_session.assert_not_called()

    async def test_paused_session_returned_from_db(self):
        ss = _make_session_state()
        ctrl, mock_db = await self._make_controller(db_get_session_return=ss)

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert result["is_active"] is False
        assert result["user_id"] == ss.user_id
        mock_db.get_session.assert_called_once_with(ss.session_id)

    async def test_returns_none_when_not_in_memory_or_db(self):
        ctrl, mock_db = await self._make_controller(db_get_session_return=None)

        result = await ctrl.get_session_status("nonexistent-session")

        assert result is None

    async def test_paused_status_has_zero_available_choices(self):
        ss = _make_session_state()
        ctrl, _ = await self._make_controller(db_get_session_return=ss)

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert result["available_choices_count"] == 0
        assert result["available_choices"] == []

    async def test_paused_status_includes_emotional_state(self):
        ss = _make_session_state()
        ss.emotional_state = EmotionalState.ANXIOUS
        ctrl, _ = await self._make_controller(db_get_session_return=ss)

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert result["emotional_state"] == EmotionalState.ANXIOUS.value

    async def test_paused_status_includes_total_choices(self):
        ss = _make_session_state()
        ss.choice_history = [
            {"choice_id": "c1", "therapeutic_value": 0.8},
            {"choice_id": "c2", "therapeutic_value": 0.6},
        ]
        ctrl, _ = await self._make_controller(db_get_session_return=ss)

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert result["total_choices"] == 2

    async def test_paused_status_computes_therapeutic_engagement(self):
        ss = _make_session_state()
        ss.choice_history = [
            {"therapeutic_value": 0.8},
            {"therapeutic_value": 0.6},
        ]
        ctrl, _ = await self._make_controller(db_get_session_return=ss)

        result = await ctrl.get_session_status(ss.session_id)

        assert result is not None
        assert abs(result["therapeutic_engagement"] - 0.7) < 0.01

    async def test_db_error_returns_none(self):
        ctrl, mock_db = await self._make_controller()
        mock_db.get_session = AsyncMock(side_effect=RuntimeError("db error"))

        result = await ctrl.get_session_status("session-x")

        assert result is None


# ---------------------------------------------------------------------------
# Task 43 — Pause/Resume API routes
# ---------------------------------------------------------------------------


def _build_test_app(gameplay_service_mock: MagicMock) -> TestClient:
    """Build a minimal FastAPI app with the gameplay router and mocked service."""
    from src.player_experience.api.routers.gameplay import get_gameplay_service, router

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_gameplay_service] = lambda: gameplay_service_mock
    return TestClient(app, raise_server_exceptions=False)


def _make_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.pause_session = AsyncMock()
    svc.resume_session = AsyncMock()
    svc.create_authenticated_session = AsyncMock()
    svc.process_validated_choice = AsyncMock()
    svc.get_session_with_auth = AsyncMock()
    svc.end_session_with_auth = AsyncMock()
    svc.get_user_sessions = AsyncMock()
    svc.get_integration_status = MagicMock(return_value={})
    return svc


class TestPauseSessionRoute:
    def test_pause_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.pause_session.return_value = {
            "success": True,
            "session_id": "sess-1",
            "paused_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/pause",
            headers={"Authorization": "Bearer test-token"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["session_id"] == "sess-1"

    def test_pause_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.pause_session.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/pause",
            headers={"Authorization": "Bearer bad-token"},
        )

        assert resp.status_code == 401

    def test_pause_returns_404_on_session_not_found(self):
        svc = _make_service_mock()
        svc.pause_session.return_value = {
            "success": False,
            "error": "Session not found",
            "code": "SESSION_NOT_FOUND",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/missing/pause",
            headers={"Authorization": "Bearer test-token"},
        )

        assert resp.status_code == 404

    def test_pause_returns_403_on_access_denied(self):
        svc = _make_service_mock()
        svc.pause_session.return_value = {
            "success": False,
            "error": "Access denied",
            "code": "ACCESS_DENIED",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/pause",
            headers={"Authorization": "Bearer other-token"},
        )

        assert resp.status_code == 403

    def test_pause_calls_service_with_correct_session_id(self):
        svc = _make_service_mock()
        svc.pause_session.return_value = {
            "success": True,
            "session_id": "sess-abc",
            "paused_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        client.post(
            "/sessions/sess-abc/pause",
            headers={"Authorization": "Bearer tok"},
        )

        call_kwargs = svc.pause_session.call_args
        assert call_kwargs.kwargs["session_id"] == "sess-abc"


class TestResumeSessionRoute:
    def test_resume_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": True,
            "session_id": "sess-1",
            "session_data": {
                "session_id": "sess-1",
                "current_scene": None,
                "available_choices": [],
                "session_recap": "Welcome back!",
            },
            "resumed_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/resume",
            headers={"Authorization": "Bearer test-token"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["session_id"] == "sess-1"

    def test_resume_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/resume",
            headers={"Authorization": "Bearer bad"},
        )

        assert resp.status_code == 401

    def test_resume_returns_404_on_session_not_found(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": False,
            "error": "Session not found",
            "code": "SESSION_NOT_FOUND",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/missing/resume",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 404

    def test_resume_returns_403_on_access_denied(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": False,
            "error": "Access denied",
            "code": "ACCESS_DENIED",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/resume",
            headers={"Authorization": "Bearer other"},
        )

        assert resp.status_code == 403

    def test_resume_returns_404_on_session_error(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": False,
            "error": "Failed to resume",
            "code": "SESSION_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/resume",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 404

    def test_resume_calls_service_with_correct_session_id(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": True,
            "session_id": "sess-xyz",
            "session_data": {},
            "resumed_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        client.post(
            "/sessions/sess-xyz/resume",
            headers={"Authorization": "Bearer tok"},
        )

        call_kwargs = svc.resume_session.call_args
        assert call_kwargs.kwargs["session_id"] == "sess-xyz"

    def test_resume_includes_session_data_in_response(self):
        svc = _make_service_mock()
        svc.resume_session.return_value = {
            "success": True,
            "session_id": "sess-1",
            "session_data": {
                "session_recap": "You have made 3 choices.",
                "current_scene": {"title": "The Forest"},
                "available_choices": [{"choice_id": "c1", "choice_text": "Go left"}],
            },
            "resumed_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/resume",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["session_data"]["session_recap"] == "You have made 3 choices."


# ---------------------------------------------------------------------------
# POST /sessions — create session
# ---------------------------------------------------------------------------


class TestCreateSessionRoute:
    def test_create_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.create_authenticated_session.return_value = {
            "success": True,
            "session_id": "sess-new",
            "user_id": "user-1",
            "session_status": {"is_active": True},
            "created_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
            json={"therapeutic_context": {"goal": "reduce anxiety"}},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["session_id"] == "sess-new"

    def test_create_passes_therapeutic_context(self):
        svc = _make_service_mock()
        svc.create_authenticated_session.return_value = {
            "success": True,
            "session_id": "sess-x",
            "user_id": "u1",
            "created_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        client.post(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
            json={"therapeutic_context": {"focus": "stress"}},
        )

        svc.create_authenticated_session.assert_called_once_with(
            auth_token="tok",
            therapeutic_context={"focus": "stress"},
        )

    def test_create_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.create_authenticated_session.return_value = {
            "success": False,
            "error": "Authentication failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions",
            headers={"Authorization": "Bearer bad"},
            json={},
        )

        assert resp.status_code == 401

    def test_create_returns_422_on_safety_error(self):
        svc = _make_service_mock()
        svc.create_authenticated_session.return_value = {
            "success": False,
            "error": "Unsafe context",
            "code": "SAFETY_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
            json={},
        )

        assert resp.status_code == 422

    def test_create_accepts_empty_therapeutic_context(self):
        svc = _make_service_mock()
        svc.create_authenticated_session.return_value = {
            "success": True,
            "session_id": "sess-y",
            "user_id": "u2",
            "created_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
            json={},
        )

        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /sessions/{id}/choices — process choice
# ---------------------------------------------------------------------------


class TestProcessChoiceRoute:
    def test_choice_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.process_validated_choice.return_value = {
            "success": True,
            "session_id": "sess-1",
            "choice_result": {"next_scene": {"title": "The River"}},
            "session_status": {"total_choices": 1},
            "processed_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/choices",
            headers={"Authorization": "Bearer tok"},
            json={"choice_id": "choice-abc"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["choice_result"]["next_scene"]["title"] == "The River"

    def test_choice_passes_correct_args(self):
        svc = _make_service_mock()
        svc.process_validated_choice.return_value = {
            "success": True,
            "session_id": "sess-1",
            "processed_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        client.post(
            "/sessions/sess-1/choices",
            headers={"Authorization": "Bearer mytoken"},
            json={"choice_id": "choice-xyz"},
        )

        svc.process_validated_choice.assert_called_once_with(
            session_id="sess-1",
            choice_id="choice-xyz",
            auth_token="mytoken",
        )

    def test_choice_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.process_validated_choice.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/choices",
            headers={"Authorization": "Bearer bad"},
            json={"choice_id": "c1"},
        )

        assert resp.status_code == 401

    def test_choice_returns_404_on_session_not_found(self):
        svc = _make_service_mock()
        svc.process_validated_choice.return_value = {
            "success": False,
            "error": "Not found",
            "code": "SESSION_NOT_FOUND",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/missing/choices",
            headers={"Authorization": "Bearer tok"},
            json={"choice_id": "c1"},
        )

        assert resp.status_code == 404

    def test_choice_returns_403_on_access_denied(self):
        svc = _make_service_mock()
        svc.process_validated_choice.return_value = {
            "success": False,
            "error": "Access denied",
            "code": "ACCESS_DENIED",
        }
        client = _build_test_app(svc)

        resp = client.post(
            "/sessions/sess-1/choices",
            headers={"Authorization": "Bearer tok"},
            json={"choice_id": "c1"},
        )

        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /sessions/{id} — get session status
# ---------------------------------------------------------------------------


class TestGetSessionStatusRoute:
    def test_get_status_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.get_session_with_auth.return_value = {
            "success": True,
            "session_status": {"is_active": True, "total_choices": 2},
            "retrieved_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions/sess-1",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["session_status"]["is_active"] is True

    def test_get_status_returns_404_on_not_found(self):
        svc = _make_service_mock()
        svc.get_session_with_auth.return_value = {
            "success": False,
            "error": "Not found",
            "code": "SESSION_NOT_FOUND",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions/missing",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 404

    def test_get_status_returns_403_on_access_denied(self):
        svc = _make_service_mock()
        svc.get_session_with_auth.return_value = {
            "success": False,
            "error": "Denied",
            "code": "ACCESS_DENIED",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions/sess-other",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 403

    def test_get_status_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.get_session_with_auth.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions/sess-1",
            headers={"Authorization": "Bearer bad"},
        )

        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /sessions/{id} — end session
# ---------------------------------------------------------------------------


class TestEndSessionRoute:
    def test_end_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.end_session_with_auth.return_value = {
            "success": True,
            "session_id": "sess-1",
            "ended_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.delete(
            "/sessions/sess-1",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "sess-1"

    def test_end_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.end_session_with_auth.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.delete(
            "/sessions/sess-1",
            headers={"Authorization": "Bearer bad"},
        )

        assert resp.status_code == 401

    def test_end_returns_404_on_not_found(self):
        svc = _make_service_mock()
        svc.end_session_with_auth.return_value = {
            "success": False,
            "error": "Not found",
            "code": "SESSION_NOT_FOUND",
        }
        client = _build_test_app(svc)

        resp = client.delete(
            "/sessions/missing",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 404

    def test_end_returns_403_on_access_denied(self):
        svc = _make_service_mock()
        svc.end_session_with_auth.return_value = {
            "success": False,
            "error": "Denied",
            "code": "ACCESS_DENIED",
        }
        client = _build_test_app(svc)

        resp = client.delete(
            "/sessions/sess-other",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 403

    def test_end_calls_service_with_correct_args(self):
        svc = _make_service_mock()
        svc.end_session_with_auth.return_value = {
            "success": True,
            "session_id": "sess-abc",
            "ended_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        client.delete(
            "/sessions/sess-abc",
            headers={"Authorization": "Bearer mytoken"},
        )

        svc.end_session_with_auth.assert_called_once_with(
            session_id="sess-abc",
            auth_token="mytoken",
        )


# ---------------------------------------------------------------------------
# GET /sessions — list user sessions
# ---------------------------------------------------------------------------


class TestGetUserSessionsRoute:
    def test_list_returns_200_on_success(self):
        svc = _make_service_mock()
        svc.get_user_sessions.return_value = {
            "success": True,
            "user_id": "user-1",
            "session_metrics": {"sessions": [], "total_count": 0},
            "retrieved_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "user-1"

    def test_list_returns_sessions(self):
        svc = _make_service_mock()
        svc.get_user_sessions.return_value = {
            "success": True,
            "user_id": "user-1",
            "session_metrics": {
                "sessions": [{"session_id": "s1"}, {"session_id": "s2"}],
                "total_count": 2,
            },
            "retrieved_at": "2026-01-01T00:00:00",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions",
            headers={"Authorization": "Bearer tok"},
        )

        assert resp.status_code == 200
        assert resp.json()["session_metrics"]["total_count"] == 2

    def test_list_returns_401_on_auth_error(self):
        svc = _make_service_mock()
        svc.get_user_sessions.return_value = {
            "success": False,
            "error": "Auth failed",
            "code": "AUTH_ERROR",
        }
        client = _build_test_app(svc)

        resp = client.get(
            "/sessions",
            headers={"Authorization": "Bearer bad"},
        )

        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /health — health check
# ---------------------------------------------------------------------------


class TestHealthRoute:
    def test_health_returns_200(self):
        svc = _make_service_mock()
        svc.get_integration_status.return_value = {
            "gameplay_component": {"available": True}
        }
        client = _build_test_app(svc)

        resp = client.get("/health")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_includes_real_timestamp(self):
        svc = _make_service_mock()
        svc.get_integration_status.return_value = {}
        client = _build_test_app(svc)

        resp = client.get("/health")

        data = resp.json()
        # Must not be the old hardcoded value
        assert data["timestamp"] != "2024-01-01T00:00:00Z"
        assert "T" in data["timestamp"]  # ISO format

    def test_health_includes_integration_status(self):
        svc = _make_service_mock()
        svc.get_integration_status.return_value = {
            "gameplay_service": {"initialized": True}
        }
        client = _build_test_app(svc)

        resp = client.get("/health")

        data = resp.json()
        assert "integration_status" in data
        assert data["integration_status"]["gameplay_service"]["initialized"] is True
