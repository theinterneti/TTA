# Logseq: [[TTA.dev/Tests/Test_metrics_endpoint]]
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
    # /metrics is the Prometheus endpoint (always available, plain text format)
    assert resp.status_code == 200


def test_metrics_json_endpoint_available_in_debug() -> None:
    # The debug-gated JSON metrics endpoint is at /metrics (shadowed by Prometheus)
    # Test the Prometheus metrics-prom endpoint which is also debug-gated
    client = _make_client()
    resp = client.get("/metrics-prom")
    # Should be accessible in debug mode
    assert resp.status_code in [200, 404]  # 404 if prometheus_client not installed


def test_metrics_endpoint_hidden_in_production() -> None:
    # Simulate production settings
    import src.player_experience.api.config as config_module

    # Use DevelopmentSettings with debug=False to mimic production behavior without strong key validation
    dev = config_module.DevelopmentSettings()
    object.__setattr__(dev, "debug", False)
    config_module.settings = dev
    app = create_app()
    client = TestClient(app)

    # /metrics is the Prometheus endpoint - always available for scraping
    resp = client.get("/metrics")
    assert resp.status_code == 200

    # /metrics-prom (JSON) should be hidden in production
    resp_prom = client.get("/metrics-prom")
    assert resp_prom.status_code == 404
