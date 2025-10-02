"""
Integration tests for Character Management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import create_app
from src.player_experience.api.config import TestingSettings


@pytest.fixture
def client() -> TestClient:
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()
    app = create_app()
    return TestClient(app)


def test_characters_root_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/characters/")
    assert resp.status_code == 401
    body = resp.json()
    assert body.get("error") in {
        "Authentication Required",
        "Authentication Failed",
        "Invalid Authorization Header",
    }


def test_list_characters_requires_auth(client: TestClient) -> None:
    # list endpoint shares same path as root but with response model
    resp = client.get("/api/v1/characters/")
    assert resp.status_code == 401


def test_get_character_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/characters/char-123")
    assert resp.status_code == 401


def test_update_therapeutic_profile_requires_auth(client: TestClient) -> None:
    resp = client.patch(
        "/api/v1/characters/char-123/therapeutic-profile",
        json={
            "primary_concerns": [],
            "therapeutic_goals": [],
            "preferred_intensity": "MEDIUM",
            "comfort_zones": [],
            "readiness_level": 0.5,
        },
    )
    assert resp.status_code == 401
