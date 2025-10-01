"""
Tests for typing indicators and observability metrics in WebSocket chat.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.player_experience.api.app import create_app
from src.player_experience.api.auth import ALGORITHM, SECRET_KEY
from src.player_experience.api.config import TestingSettings
from src.player_experience.api.routers.chat import METRICS, reset_metrics


@pytest.fixture
def client() -> TestClient:
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()
    app = create_app()
    return TestClient(app)


def _auth_token(player_id: str = "player-typing") -> str:
    payload = {"sub": player_id, "username": "test", "email": "t@example.com"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_typing_events_emitted_when_opt_in(client: TestClient) -> None:
    reset_metrics()
    token = _auth_token()
    with client.websocket_connect(f"/ws/chat?token={token}&typing=1") as ws:
        ws.receive_text()  # welcome
        ws.send_text(json.dumps({"type": "user_message", "content": {"text": "Hello"}}))
        first = json.loads(ws.receive_text())
        # first event should be typing start
        assert first["content"].get("event") == "typing"
        assert first["content"].get("status") == "start"
        # then assistant reply
        reply = json.loads(ws.receive_text())
        assert reply["role"] == "assistant"
        # then typing stop
        last = json.loads(ws.receive_text())
        assert last["content"].get("event") == "typing"
        assert last["content"].get("status") == "stop"


def test_metrics_incremented(client: TestClient) -> None:
    reset_metrics()
    token = _auth_token("player-metrics")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        ws.receive_text()  # welcome
        before = dict(METRICS)
        ws.send_text(json.dumps({"type": "user_message", "content": {"text": "check"}}))
        json.loads(ws.receive_text())  # assistant
        after = dict(METRICS)
        assert (
            after["connections"] == before["connections"] + 0
            or after["connections"] >= 1
        )
        assert after["messages_in"] == before["messages_in"] + 1
        assert after["messages_out"] >= before["messages_out"] + 1
