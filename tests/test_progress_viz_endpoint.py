from __future__ import annotations

from fastapi.testclient import TestClient

from src.player_experience.api.app import create_app
from src.player_experience.api.config import TestingSettings
from src.player_experience.api.auth import create_access_token


def _client_with_token(player_id: str = "playerTest") -> tuple[TestClient, str]:
    import src.player_experience.api.config as config_module
    config_module.settings = TestingSettings()
    app = create_app()
    client = TestClient(app)

    # Create a simple JWT via the API auth util
    token = create_access_token({"sub": player_id})
    return client, token


def test_progress_viz_endpoint_returns_series() -> None:
    client, token = _client_with_token()
    resp = client.get("/api/v1/players/playerTest/progress/viz?days=7", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "time_buckets" in data and "series" in data
    assert isinstance(data["time_buckets"], list)
    assert isinstance(data["series"], dict)

