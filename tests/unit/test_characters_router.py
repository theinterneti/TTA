"""
Unit tests for src/player_experience/api/routers/characters.py.

Tests cover:
- list_characters: success (empty + populated), no player_id → 401, exception → 500
- get_character: not found → 404, wrong owner → 403, success → 200
- create_character: limit exceeded → 400, ValueError → 400, exception → 500, success → 201
- update_character: not found → 404, wrong owner → 403
- delete_character: not found → 404, wrong owner → 403, success → 204
- get_character_therapeutic_profile: not found → 404, wrong owner → 403, success → 200
- update_character_therapeutic_profile: not found → 404, wrong owner → 403
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers.characters import (
    get_character_manager_dep,
    router,
)
from src.player_experience.managers.character_avatar_manager import (
    CharacterLimitExceededError,
    CharacterNotFoundError,
)
from src.player_experience.models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    TherapeuticGoal,
    TherapeuticProfile,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_character(
    player_id: str = "player-1", character_id: str = "char-1"
) -> Character:
    goal = TherapeuticGoal(goal_id="g1", description="Reduce anxiety")
    profile = TherapeuticProfile(
        primary_concerns=["anxiety"],
        therapeutic_goals=[goal],
    )
    return Character(
        character_id=character_id,
        player_id=player_id,
        name="Hero",
        appearance=CharacterAppearance(physical_description="Tall and strong"),
        background=CharacterBackground(
            name="Hero",
            backstory="A brave wanderer",
            personality_traits=["brave"],
            life_goals=["defeat evil"],
        ),
        therapeutic_profile=profile,
        created_at=datetime(2025, 1, 1, 12, 0),
        last_active=datetime(2025, 1, 2, 12, 0),
    )


def _build_app(
    manager_mock: MagicMock,
    player_id: str | None = "player-1",
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_active_player] = lambda: TokenData(
        player_id=player_id, username="testuser"
    )
    app.dependency_overrides[get_character_manager_dep] = lambda: manager_mock
    return TestClient(app, raise_server_exceptions=False)


def _mock_manager() -> MagicMock:
    m = MagicMock()
    m.get_player_characters.return_value = []
    m.get_character.return_value = None
    m.create_character.return_value = None
    m.update_character.return_value = None
    m.delete_character.return_value = True
    m.get_character_therapeutic_profile.return_value = None
    m.update_character_therapeutic_profile.return_value = True
    return m


# ---------------------------------------------------------------------------
# list_characters
# ---------------------------------------------------------------------------


class TestListCharacters:
    def test_empty_list_returns_200(self):
        client = _build_app(_mock_manager())
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_serialized_characters(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_player_characters.return_value = [char]
        client = _build_app(manager)
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["character_id"] == "c1"
        assert data[0]["player_id"] == "player-1"
        assert data[0]["name"] == "Hero"

    def test_no_player_id_in_token_returns_401(self):
        client = _build_app(_mock_manager(), player_id=None)
        resp = client.get("/")
        assert resp.status_code == 401

    def test_manager_exception_returns_500(self):
        manager = _mock_manager()
        manager.get_player_characters.side_effect = RuntimeError("db failure")
        client = _build_app(manager)
        resp = client.get("/")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# get_character
# ---------------------------------------------------------------------------


class TestGetCharacter:
    def test_not_found_returns_404(self):
        client = _build_app(_mock_manager())
        resp = client.get("/char-x")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_wrong_owner_returns_403(self):
        manager = _mock_manager()
        char = _make_character(player_id="other-player", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/c1")
        assert resp.status_code == 403

    def test_own_character_returns_200(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/c1")
        assert resp.status_code == 200
        assert resp.json()["character_id"] == "c1"

    def test_exception_returns_500(self):
        manager = _mock_manager()
        manager.get_character.side_effect = RuntimeError("db error")
        client = _build_app(manager)
        resp = client.get("/c1")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# create_character
# ---------------------------------------------------------------------------

_CREATE_PAYLOAD = {
    "name": "Hero",
    "appearance": {
        "age_range": "adult",
        "gender_identity": "non-binary",
        "physical_description": "Tall and strong",
        "clothing_style": "casual",
    },
    "background": {
        "name": "Hero",
        "backstory": "A brave wanderer",
        "personality_traits": ["brave", "kind"],
        "life_goals": ["defeat evil"],
    },
    "therapeutic_profile": {
        "primary_concerns": ["anxiety"],
        "therapeutic_goals": [
            {
                "goal_id": "g1",
                "description": "Reduce anxiety",
            }
        ],
    },
}


class TestCreateCharacter:
    def test_character_limit_exceeded_returns_400(self):
        manager = _mock_manager()
        manager.create_character.side_effect = CharacterLimitExceededError(
            "Limit reached"
        )
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 400
        assert "Limit" in resp.json()["detail"]

    def test_value_error_returns_400(self):
        manager = _mock_manager()
        manager.create_character.side_effect = ValueError("Invalid value")
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 400

    def test_unexpected_exception_returns_500(self):
        manager = _mock_manager()
        manager.create_character.side_effect = RuntimeError("unexpected")
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 500

    def test_success_returns_201(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="new-char")
        manager.create_character.return_value = char
        client = _build_app(manager)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 201
        assert resp.json()["character_id"] == "new-char"

    def test_no_player_id_in_token_returns_401(self):
        client = _build_app(_mock_manager(), player_id=None)
        resp = client.post("/", json=_CREATE_PAYLOAD)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# update_character
# ---------------------------------------------------------------------------


class TestUpdateCharacter:
    def test_not_found_returns_404(self):
        manager = _mock_manager()
        manager.get_character.return_value = None
        client = _build_app(manager)
        resp = client.put("/c1", json={})
        assert resp.status_code == 404

    def test_wrong_owner_returns_403(self):
        manager = _mock_manager()
        char = _make_character(player_id="other", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.put("/c1", json={})
        assert resp.status_code == 403

    def test_character_not_found_error_from_update_returns_404(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.update_character.side_effect = CharacterNotFoundError("not found")
        client = _build_app(manager, player_id="player-1")
        resp = client.put("/c1", json={})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# delete_character
# ---------------------------------------------------------------------------


class TestDeleteCharacter:
    def test_not_found_returns_404(self):
        manager = _mock_manager()
        manager.get_character.return_value = None
        client = _build_app(manager)
        resp = client.delete("/c1")
        assert resp.status_code == 404

    def test_wrong_owner_returns_403(self):
        manager = _mock_manager()
        char = _make_character(player_id="other", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.delete("/c1")
        assert resp.status_code == 403

    def test_success_returns_204(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.delete_character.return_value = True
        client = _build_app(manager, player_id="player-1")
        resp = client.delete("/c1")
        assert resp.status_code == 204

    def test_delete_returns_false_means_404(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.delete_character.return_value = False
        client = _build_app(manager, player_id="player-1")
        resp = client.delete("/c1")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# get_character_therapeutic_profile
# ---------------------------------------------------------------------------


class TestGetTherapeuticProfile:
    def test_character_not_found_returns_404(self):
        client = _build_app(_mock_manager())
        resp = client.get("/c1/therapeutic-profile")
        assert resp.status_code == 404

    def test_wrong_owner_returns_403(self):
        manager = _mock_manager()
        char = _make_character(player_id="other", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/c1/therapeutic-profile")
        assert resp.status_code == 403

    def test_profile_not_found_returns_404(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.get_character_therapeutic_profile.return_value = None
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/c1/therapeutic-profile")
        assert resp.status_code == 404

    def test_success_returns_200_with_profile_data(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.get_character_therapeutic_profile.return_value = (
            char.therapeutic_profile
        )
        client = _build_app(manager, player_id="player-1")
        resp = client.get("/c1/therapeutic-profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "primary_concerns" in data
        assert data["primary_concerns"] == ["anxiety"]


# ---------------------------------------------------------------------------
# update_character_therapeutic_profile
# ---------------------------------------------------------------------------

_PROFILE_PAYLOAD = {
    "primary_concerns": ["stress"],
    "therapeutic_goals": [{"goal_id": "g2", "description": "Manage stress"}],
}


class TestUpdateTherapeuticProfile:
    def test_character_not_found_returns_404(self):
        client = _build_app(_mock_manager())
        resp = client.patch("/c1/therapeutic-profile", json=_PROFILE_PAYLOAD)
        assert resp.status_code == 404

    def test_wrong_owner_returns_403(self):
        manager = _mock_manager()
        char = _make_character(player_id="other", character_id="c1")
        manager.get_character.return_value = char
        client = _build_app(manager, player_id="player-1")
        resp = client.patch("/c1/therapeutic-profile", json=_PROFILE_PAYLOAD)
        assert resp.status_code == 403

    def test_update_returns_false_means_404(self):
        manager = _mock_manager()
        char = _make_character(player_id="player-1", character_id="c1")
        manager.get_character.return_value = char
        manager.update_character_therapeutic_profile.return_value = False
        client = _build_app(manager, player_id="player-1")
        resp = client.patch("/c1/therapeutic-profile", json=_PROFILE_PAYLOAD)
        assert resp.status_code == 404
