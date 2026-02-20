"""

# Logseq: [[TTA.dev/Tests/Test_websocket_chat_interactive]]
Tests for interactive therapeutic elements over WebSocket (Task 8.3).
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


def _auth_token(player_id: str = "player-interactive") -> str:
    payload = {"sub": player_id, "username": "test", "email": "t@example.com"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _recv_json(ws) -> dict:
    return json.loads(ws.receive_text())


def _recv_assistant(ws, max_messages: int = 20) -> dict:
    """Receive messages until we get a non-system (assistant) message."""
    for _ in range(max_messages):
        msg = _recv_json(ws)
        if msg.get("role") != "system":
            return msg
    raise AssertionError("Did not receive an assistant message within expected count")


def test_interactive_buttons_suggested_on_anxiety(client: TestClient) -> None:
    token = _auth_token("player-anxious")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        _recv_json(ws)  # welcome
        ws.send_text(
            json.dumps(
                {
                    "type": "user_message",
                    "content": {"text": "I'm feeling very anxious and overwhelmed"},
                }
            )
        )
        reply = _recv_assistant(ws)
        assert reply["role"] == "assistant"
        elements = reply["content"].get("elements", [])
        # Expect two interactive buttons for exercises
        button_ids = {e.get("id") for e in elements if e.get("type") == "button"}
        assert "ex_breathing" in button_ids
        assert "ex_grounding" in button_ids


def test_guided_exercise_flow_records_progress(client: TestClient) -> None:
    token = _auth_token("player-exercise")
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        _recv_json(ws)  # welcome
        # Start exercise via button click
        ws.send_text(
            json.dumps(
                {
                    "type": "interaction",
                    "content": {"action": "button_click", "id": "ex_breathing"},
                }
            )
        )
        resp = _recv_json(ws)
        assert resp["role"] == "interactive"
        elems = resp["content"].get("elements", [])
        # Should include instruction and a completion button
        types = {e.get("type") for e in elems}
        assert "instruction" in types
        complete_btn = next(
            (
                e
                for e in elems
                if e.get("type") == "button" and e.get("id", "").endswith("_complete")
            ),
            None,
        )
        assert complete_btn is not None

        # Complete the exercise
        ws.send_text(
            json.dumps(
                {
                    "type": "interaction",
                    "content": {"action": "button_click", "id": complete_btn["id"]},
                }
            )
        )
        done = _recv_json(ws)
        assert done["role"] == "interactive"
        done_elems = done["content"].get("elements", [])
        # Expect a progress element acknowledging recording
        assert any(e.get("type") == "progress" for e in done_elems)
