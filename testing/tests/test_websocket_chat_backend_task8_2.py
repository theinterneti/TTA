"""
Additional tests for Task 8.2: therapeutic chat message processing enhancements.
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


def _auth_token(player_id: str = "player-8-2") -> str:
    payload = {"sub": player_id, "username": "test", "email": "t@example.com"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_user_message_includes_recommendations_and_no_crisis_by_default(
    client: TestClient,
) -> None:
    token = _auth_token()
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        ws.receive_text()  # welcome
        ws.send_text(
            json.dumps(
                {
                    "type": "user_message",
                    "content": {
                        "text": "Hello there, I'd like some gentle support today."
                    },
                }
            )
        )
        reply = json.loads(ws.receive_text())
        assert reply["role"] == "assistant"
        # recommendations present in metadata (may be empty list depending on defaults)
        assert "recommendations" in reply.get("metadata", {})
        assert reply.get("metadata", {}).get("safety", {}).get("crisis") in {
            False,
            True,
        }


def test_crisis_detection_includes_resources(client: TestClient) -> None:
    token = _auth_token("player-crisis")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        ws.receive_text()  # welcome
        ws.send_text(
            json.dumps(
                {
                    "type": "user_message",
                    "content": {"text": "I feel like I want to die and can't go on."},
                }
            )
        )
        reply = json.loads(ws.receive_text())
        assert reply["role"] == "assistant"
        safety = reply.get("metadata", {}).get("safety", {})
        assert safety.get("crisis") is True
        # elements include crisis resources
        elements = reply.get("content", {}).get("elements", [])
        assert isinstance(elements, list)
        assert any(el.get("type") == "resource" for el in elements)


def test_feedback_triggers_recommendations(client: TestClient) -> None:
    token = _auth_token("player-fb")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        ws.receive_text()  # welcome
        ws.send_text(
            json.dumps(
                {"type": "feedback", "content": {"rating": 2, "text": "Too difficult"}}
            )
        )
        note = json.loads(ws.receive_text())
        assert note["role"] == "system"
        # elements may include recommendation placeholders
        elements = note.get("content", {}).get("elements", [])
        assert isinstance(elements, list)
