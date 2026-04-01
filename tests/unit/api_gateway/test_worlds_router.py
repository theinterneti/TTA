"""
Unit tests for src/player_experience/api/routers/worlds.py.

Tests cover:
- list_worlds: success (empty list) → 200
- get_world: not found → 404 (HTTPException)
- check_world_compatibility: world not found → 404
- customize_world: world not found → 404
"""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers.worlds import get_world_manager_dep, router

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_app(manager_mock: MagicMock) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_active_player] = lambda: TokenData(
        player_id="player-1", username="testuser"
    )
    app.dependency_overrides[get_world_manager_dep] = lambda: manager_mock
    return TestClient(app, raise_server_exceptions=False)


def _mock_manager() -> MagicMock:
    m = MagicMock()
    m.get_available_worlds.return_value = []
    m.get_world_details.return_value = None
    m.check_world_compatibility_by_id.return_value = None
    m.customize_world_parameters.return_value = None
    return m


# ---------------------------------------------------------------------------
# list_worlds
# ---------------------------------------------------------------------------


class TestListWorlds:
    def test_empty_list_returns_200(self):
        client = _build_app(_mock_manager())
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_pagination_params_accepted(self):
        client = _build_app(_mock_manager())
        resp = client.get("/?limit=5&offset=0")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_character_id_filter_accepted(self):
        client = _build_app(_mock_manager())
        resp = client.get("/?character_id=char-1")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# get_world
# ---------------------------------------------------------------------------


class TestGetWorld:
    def test_not_found_returns_404(self):
        client = _build_app(_mock_manager())
        resp = client.get("/world-x")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "World not found"

    def test_calls_manager_with_world_id(self):
        manager = _mock_manager()
        client = _build_app(manager)
        client.get("/world-123")
        manager.get_world_details.assert_called_once_with("world-123")


# ---------------------------------------------------------------------------
# check_world_compatibility
# ---------------------------------------------------------------------------


class TestCheckWorldCompatibility:
    def test_world_not_found_returns_404(self):
        manager = _mock_manager()
        manager.check_world_compatibility_by_id.return_value = None
        manager.get_world_details.return_value = None
        client = _build_app(manager)
        resp = client.get("/world-x/compatibility/char-1")
        assert resp.status_code == 404

    def test_compatibility_check_failed_returns_400(self):
        manager = _mock_manager()
        # Compatibility returns None but world exists → 400
        manager.check_world_compatibility_by_id.return_value = None
        # Create a minimal world mock for the fallback check
        world_mock = MagicMock()
        manager.get_world_details.return_value = world_mock
        client = _build_app(manager)
        resp = client.get("/world-x/compatibility/char-1")
        assert resp.status_code == 400
        assert "Compatibility check failed" in resp.json()["detail"]

    def test_calls_manager_with_correct_ids(self):
        manager = _mock_manager()
        client = _build_app(manager)
        client.get("/world-99/compatibility/char-42")
        manager.check_world_compatibility_by_id.assert_called_once_with(
            character_id="char-42", world_id="world-99"
        )


# ---------------------------------------------------------------------------
# customize_world
# ---------------------------------------------------------------------------


class TestCustomizeWorld:
    def test_world_not_found_returns_404(self):
        client = _build_app(_mock_manager())
        resp = client.post("/world-x/customize", json={})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "World not found"

    def test_calls_manager_with_world_id(self):
        manager = _mock_manager()
        client = _build_app(manager)
        client.post("/world-123/customize", json={})
        manager.get_world_details.assert_called_once_with("world-123")
