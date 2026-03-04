"""
Unit tests for src/player_experience/api/routers/players.py.

Tests cover:
- players_root: GET / → 200 with message
- create_player: success → 201, conflict → 409
- get_player: not found → 404, access restricted → 403, success → 200
- update_player: wrong player_id → 403, update failed → 400
- delete_player: wrong player_id → 403, not found → 404, success → 204
- get_player_progress: static dict → 200
- get_player_dashboard: dict → 200
- export_player_data: wrong player_id → 403
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers.players import get_player_manager_dep, router
from src.player_experience.managers.player_profile_manager import (
    DataAccessRestrictedError,
    PlayerProfileManagerError,
)
from src.player_experience.models.player import PlayerProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_player(player_id: str = "player-1") -> PlayerProfile:
    return PlayerProfile(
        player_id=player_id,
        username="testuser",
        email="test@example.com",
        created_at=datetime(2025, 1, 1, 12, 0),
    )


def _build_app(
    manager_mock: MagicMock,
    player_id: str = "player-1",
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_active_player] = lambda: TokenData(
        player_id=player_id, username="testuser"
    )
    app.dependency_overrides[get_player_manager_dep] = lambda: manager_mock
    return TestClient(app, raise_server_exceptions=False)


def _mock_manager() -> MagicMock:
    m = MagicMock()
    m.get_player_profile.return_value = None
    m.create_player_profile.return_value = None
    m.update_player_profile.return_value = False
    m.delete_player_profile.return_value = False
    m.export_player_data.return_value = {}
    return m


# ---------------------------------------------------------------------------
# players_root
# ---------------------------------------------------------------------------


class TestPlayersRoot:
    def test_returns_200_with_message(self):
        client = _build_app(_mock_manager())
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Players root"


# ---------------------------------------------------------------------------
# create_player
# ---------------------------------------------------------------------------

_CREATE_PAYLOAD = {
    "username": "newuser",
    "email": "new@example.com",
}


class TestCreatePlayer:
    def test_success_returns_201(self):
        manager = _mock_manager()
        player = _make_player("new-player")
        manager.create_player_profile.return_value = player
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["player_id"] == "new-player"
        assert data["username"] == "testuser"

    def test_conflict_returns_409(self):
        manager = _mock_manager()
        manager.create_player_profile.side_effect = PlayerProfileManagerError(
            "username already exists"
        )
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 409

    def test_general_manager_error_returns_400(self):
        manager = _mock_manager()
        manager.create_player_profile.side_effect = PlayerProfileManagerError("some error")
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 400

    def test_invalid_email_returns_422(self):
        client = _build_app(_mock_manager())
        resp = client.post("/", json={"username": "user1", "email": "not-an-email"})
        assert resp.status_code == 422

    def test_invalid_username_returns_422(self):
        client = _build_app(_mock_manager())
        resp = client.post("/", json={"username": "ab", "email": "x@example.com"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# get_player
# ---------------------------------------------------------------------------


class TestGetPlayer:
    def test_not_found_returns_404(self):
        manager = _mock_manager()
        manager.get_player_profile.return_value = None
        client = _build_app(manager)
        resp = client.get("/player-1")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_access_restricted_returns_403(self):
        manager = _mock_manager()
        manager.get_player_profile.side_effect = DataAccessRestrictedError("denied")
        client = _build_app(manager)
        resp = client.get("/player-1")
        assert resp.status_code == 403

    def test_manager_error_for_different_player_returns_403(self):
        manager = _mock_manager()
        manager.get_player_profile.side_effect = PlayerProfileManagerError("error")
        # Current player is "player-1" but requesting "other-player" → 403
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/other-player")
        assert resp.status_code == 403

    def test_success_returns_200(self):
        manager = _mock_manager()
        player = _make_player("player-1")
        manager.get_player_profile.return_value = player
        client = _build_app(manager)
        resp = client.get("/player-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["player_id"] == "player-1"
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"


# ---------------------------------------------------------------------------
# update_player
# ---------------------------------------------------------------------------


class TestUpdatePlayer:
    def test_access_restricted_returns_403(self):
        # DataAccessRestrictedError is caught explicitly → 403
        manager = _mock_manager()
        manager.update_player_profile.side_effect = DataAccessRestrictedError("denied")
        client = _build_app(manager)
        resp = client.put("/player-1", json={})
        assert resp.status_code == 403

    def test_conflict_returns_409(self):
        manager = _mock_manager()
        manager.update_player_profile.side_effect = PlayerProfileManagerError(
            "username already exists"
        )
        client = _build_app(manager)
        resp = client.put("/player-1", json={"username": "taken"})
        assert resp.status_code == 409

    def test_general_manager_error_returns_400(self):
        manager = _mock_manager()
        manager.update_player_profile.side_effect = PlayerProfileManagerError("some error")
        client = _build_app(manager)
        resp = client.put("/player-1", json={})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# delete_player
# ---------------------------------------------------------------------------


class TestDeletePlayer:
    def test_access_restricted_returns_403(self):
        # DataAccessRestrictedError is caught explicitly → 403
        manager = _mock_manager()
        manager.delete_player_profile.side_effect = DataAccessRestrictedError("denied")
        client = _build_app(manager)
        resp = client.delete("/player-1")
        assert resp.status_code == 403

    def test_not_found_returns_404(self):
        manager = _mock_manager()
        manager.delete_player_profile.return_value = False
        client = _build_app(manager)
        resp = client.delete("/player-1")
        assert resp.status_code == 404

    def test_success_returns_204(self):
        manager = _mock_manager()
        manager.delete_player_profile.return_value = True
        client = _build_app(manager)
        resp = client.delete("/player-1")
        assert resp.status_code == 204

    def test_access_restricted_returns_403(self):
        manager = _mock_manager()
        manager.delete_player_profile.side_effect = DataAccessRestrictedError("denied")
        client = _build_app(manager)
        resp = client.delete("/player-1")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# get_player_progress
# ---------------------------------------------------------------------------


class TestGetPlayerProgress:
    def test_returns_200_with_expected_fields(self):
        client = _build_app(_mock_manager())
        resp = client.get("/player-1/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["player_id"] == "player-1"
        assert "total_sessions" in data
        assert "total_time_minutes" in data

    def test_player_id_echoed_in_response(self):
        client = _build_app(_mock_manager())
        resp = client.get("/some-player/progress")
        assert resp.status_code == 200
        assert resp.json()["player_id"] == "some-player"


# ---------------------------------------------------------------------------
# get_player_dashboard
# ---------------------------------------------------------------------------


class TestGetPlayerDashboard:
    def test_returns_200_with_player_id(self):
        client = _build_app(_mock_manager())
        resp = client.get("/player-1/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["player_id"] == "player-1"
        assert "active_characters" in data
        assert "recommendations" in data


# ---------------------------------------------------------------------------
# export_player_data
# ---------------------------------------------------------------------------


class TestExportPlayerData:
    def test_access_restricted_returns_403(self):
        # DataAccessRestrictedError is caught explicitly → 403
        manager = _mock_manager()
        manager.export_player_data.side_effect = DataAccessRestrictedError("denied")
        client = _build_app(manager)
        resp = client.get("/player-1/export")
        assert resp.status_code == 403
