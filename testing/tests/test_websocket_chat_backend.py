"""
Tests for WebSocket Chat Interface Backend (Task 8).
"""

from __future__ import annotations

import json

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


def _auth_token(player_id: str = "player-1") -> str:
    payload = {"sub": player_id, "username": "test", "email": "t@example.com"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_ws_rejects_without_token(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as ws:  # Expect failure/close
        # When FastAPI closes policy violation, TestClient raises on receive
        with pytest.raises(Exception):
            ws.receive_text()


def test_ws_connects_with_token_and_welcome(client: TestClient) -> None:
    token = _auth_token()
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["role"] == "system"
        assert "Connected to therapeutic chat" in msg["content"]["text"]


def test_user_message_roundtrip(client: TestClient) -> None:
    token = _auth_token("player-xyz")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        # consume welcome
        ws.receive_text()
        payload = {
            "type": "user_message",
            "content": {"text": "Hello, I feel okay today."},
            "metadata": {"character_id": "char-1", "world_id": "world-1"},
        }
        ws.send_text(json.dumps(payload))
        reply = json.loads(ws.receive_text())
        assert reply["role"] == "assistant"
        assert "text" in reply["content"]
        assert reply["metadata"].get("safety", {}).get("crisis") is False


def test_feedback_processing_ack(client: TestClient) -> None:
    token = _auth_token("player-abc")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        ws.receive_text()  # welcome
        payload = {
            "type": "feedback",
            "content": {"rating": 5, "text": "Very helpful"},
        }
        ws.send_text(json.dumps(payload))
        note = json.loads(ws.receive_text())
        assert note["role"] == "system"
        assert "Feedback processed" in note["content"]["text"]
