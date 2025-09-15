from __future__ import annotations

from fastapi.testclient import TestClient

from src.player_experience.api.app import create_app
from src.player_experience.api.config import TestingSettings


def _make_client() -> TestClient:
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()
    app = create_app()
    return TestClient(app)


def test_metrics_endpoint_available_in_debug() -> None:
    client = _make_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "counters" in data and isinstance(data["counters"], dict)
    assert "timers" in data and isinstance(data["timers"], dict)


def test_metrics_endpoint_hidden_in_production() -> None:
    # Simulate production settings
    import src.player_experience.api.config as config_module

    # Use DevelopmentSettings with debug=False to mimic production behavior without strong key validation
    dev = config_module.DevelopmentSettings()
    object.__setattr__(dev, "debug", False)
    config_module.settings = dev
    app = create_app()
    client = TestClient(app)

    resp = client.get("/metrics")
    # For security, we return 404 when not allowed
    assert resp.status_code == 404
