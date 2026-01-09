"""

# Logseq: [[TTA.dev/Tests/Test_world_management_api]]
Integration tests for World Management API endpoints (7.4).
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.player_experience.api.app import create_app
from src.player_experience.api.auth import ALGORITHM, SECRET_KEY
from src.player_experience.api.config import TestingSettings


@pytest.fixture
def client() -> TestClient:
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    token_data = {"sub": "player-1", "username": "test", "email": "t@example.com"}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


def test_worlds_root_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/worlds/")
    assert resp.status_code == 401


def test_get_world_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/worlds/world_mindfulness_garden")
    assert resp.status_code == 401


def test_check_compatibility_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/worlds/world_mindfulness_garden/compatibility/char-123")
    assert resp.status_code == 401


def test_customize_requires_auth(client: TestClient) -> None:
    resp = client.post("/api/v1/worlds/world_mindfulness_garden/customize", json={})
    assert resp.status_code == 401


# Happy paths


def test_list_worlds_happy_path(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/worlds/?limit=1&offset=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "world_id" in data[0]


def test_get_world_details_happy_path(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/worlds/world_mindfulness_garden", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["world_id"] == "world_mindfulness_garden"
    assert "default_parameters" in data


def test_compatibility_happy_path(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get(
        "/api/v1/worlds/world_mindfulness_garden/compatibility/char-xyz",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["world_id"] == "world_mindfulness_garden"
    assert "overall_score" in data


def test_customize_world_happy_path(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    payload = {"therapeutic_intensity": 0.7, "session_length_preference": 45}
    resp = client.post(
        "/api/v1/worlds/world_mindfulness_garden/customize",
        headers=auth_headers,
        json=payload,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["world_id"] == "world_mindfulness_garden"
    assert data["customized_parameters"]["therapeutic_intensity"] == 0.7


# Error cases


def test_get_world_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/worlds/does-not-exist", headers=auth_headers)
    assert resp.status_code == 404


def test_customize_world_not_found(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/worlds/does-not-exist/customize",
        headers=auth_headers,
        json={},
    )
    assert resp.status_code == 404


def test_customize_world_invalid_params(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # invalid session length < 10
    payload = {"session_length_preference": 5}
    resp = client.post(
        "/api/v1/worlds/world_mindfulness_garden/customize",
        headers=auth_headers,
        json=payload,
    )
    assert resp.status_code in (400, 422)


def test_list_worlds_pagination(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp_all = client.get("/api/v1/worlds/", headers=auth_headers)
    assert resp_all.status_code == 200
    total = len(resp_all.json())

    resp_page = client.get("/api/v1/worlds/?limit=1&offset=1", headers=auth_headers)
    assert resp_page.status_code == 200
    assert len(resp_page.json()) == 1 or (total <= 1 and len(resp_page.json()) == 0)
