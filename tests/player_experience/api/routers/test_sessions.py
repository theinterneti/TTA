"""Tests for player_experience.api.routers.sessions module."""

# Logseq: [[TTA.dev/Tests/Player_experience/Api/Routers/Test_sessions]]

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers.sessions import (
    get_player_experience_manager_dep,
    get_session_store,
    router,
)


def _build_client(store: Mock, manager: Mock | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_active_player] = lambda: TokenData(
        player_id="player-1", username="player"
    )
    app.dependency_overrides[get_session_store] = lambda: store
    app.dependency_overrides[get_player_experience_manager_dep] = lambda: (
        manager or _mock_manager()
    )
    return TestClient(app, raise_server_exceptions=False)


def _mock_manager() -> Mock:
    manager = Mock()
    manager.get_session_list_api_payload = AsyncMock(
        return_value={"sessions": [], "count": 0}
    )
    return manager


class TestSessionsRouter:
    """Tests for sessions router module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from src.player_experience.api.routers import sessions

        assert sessions is not None

    def test_module_has_expected_structure(self):
        """Test that module has expected structure."""
        from src.player_experience.api.routers import sessions

        assert hasattr(sessions, "__name__")

    def test_list_sessions_can_include_narrative_summary(self):
        store = Mock()
        manager = _mock_manager()
        manager.get_session_list_api_payload = AsyncMock(
            return_value={
                "sessions": [
                    {
                        "session_id": "session-1",
                        "narrative_orchestration": {
                            "player_signals": {"coherence_status": "stable"}
                        },
                    }
                ],
                "count": 1,
                "narrative_summary": {"stable_sessions": 1, "strained_sessions": 0},
            }
        )
        client = _build_client(store, manager)

        response = client.get("/?include_narrative=true")

        assert response.status_code == 200
        payload = response.json()
        assert payload["count"] == 1
        assert payload["narrative_summary"]["stable_sessions"] == 1
        assert (
            payload["sessions"][0]["narrative_orchestration"]["player_signals"][
                "coherence_status"
            ]
            == "stable"
        )
        manager.get_session_list_api_payload.assert_awaited_once_with(
            "player-1",
            session_store=store,
            include_narrative=True,
        )
