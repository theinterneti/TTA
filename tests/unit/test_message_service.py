"""Unit tests for MessageService."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.player_experience.services.message_service import (
    MessageService,
    _SESSION_HISTORY,
)


@pytest.fixture(autouse=True)
def clear_history():
    """Wipe shared session history before every test."""
    _SESSION_HISTORY.clear()
    yield
    _SESSION_HISTORY.clear()


@pytest.fixture()
def service():
    return MessageService()


@pytest.fixture()
def mock_llm():
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=MagicMock(content="A peaceful garden awaits."))
    return llm


class TestSendMessage:
    async def test_returns_success_response(self, service, mock_llm):
        service._llm = mock_llm
        session_id = str(uuid.uuid4())

        result = await service.send_message(
            session_id=session_id,
            player_id="player-1",
            message="Hello, world",
        )

        assert result["success"] is True
        assert result["response"] == "A peaceful garden awaits."
        assert result["session_id"] == session_id
        assert "message_id" in result
        assert "timestamp" in result

    async def test_builds_conversation_history(self, service, mock_llm):
        mock_llm.ainvoke = AsyncMock(
            side_effect=[
                MagicMock(content="First response."),
                MagicMock(content="Second response."),
            ]
        )
        service._llm = mock_llm
        session_id = str(uuid.uuid4())

        await service.send_message(session_id=session_id, player_id="p1", message="Turn 1")
        await service.send_message(session_id=session_id, player_id="p1", message="Turn 2")

        history = _SESSION_HISTORY[session_id]
        assert len(history) == 4  # user + assistant × 2
        assert history[0] == {"role": "user", "content": "Turn 1"}
        assert history[1] == {"role": "assistant", "content": "First response."}
        assert history[2] == {"role": "user", "content": "Turn 2"}
        assert history[3] == {"role": "assistant", "content": "Second response."}

    async def test_sessions_are_isolated(self, service, mock_llm):
        service._llm = mock_llm
        sid_a = str(uuid.uuid4())
        sid_b = str(uuid.uuid4())

        await service.send_message(session_id=sid_a, player_id="p1", message="Session A")
        await service.send_message(session_id=sid_b, player_id="p2", message="Session B")

        assert len(_SESSION_HISTORY[sid_a]) == 2
        assert len(_SESSION_HISTORY[sid_b]) == 2
        assert _SESSION_HISTORY[sid_a][0]["content"] == "Session A"
        assert _SESSION_HISTORY[sid_b][0]["content"] == "Session B"

    async def test_fallback_on_llm_invocation_error(self, service, mock_llm):
        mock_llm.ainvoke = AsyncMock(side_effect=RuntimeError("upstream error"))
        service._llm = mock_llm

        result = await service.send_message(
            session_id=str(uuid.uuid4()),
            player_id="p1",
            message="Test",
        )

        assert result["success"] is True
        assert result["response"]  # non-empty fallback
        # Assistant turn still recorded in history
        history = _SESSION_HISTORY[result["session_id"]]
        assert history[-1]["role"] == "assistant"

    async def test_fallback_when_no_llm(self, service):
        with patch.object(service, "_get_llm", return_value=None):
            result = await service.send_message(
                session_id=str(uuid.uuid4()),
                player_id="p1",
                message="Test",
            )

        assert result["success"] is True
        assert result["response"]

    async def test_character_world_in_system_prompt(self, service, mock_llm):
        captured: list = []

        async def capture(messages):
            captured.extend(messages)
            return MagicMock(content="Story response.")

        mock_llm.ainvoke = capture
        service._llm = mock_llm

        await service.send_message(
            session_id=str(uuid.uuid4()),
            player_id="p1",
            message="I look around",
            character_name="Aria",
            world_name="Crystal Caverns",
        )

        system_content = captured[0].content
        assert "Aria" in system_content
        assert "Crystal Caverns" in system_content

    async def test_default_character_world_used(self, service, mock_llm):
        captured: list = []

        async def capture(messages):
            captured.extend(messages)
            return MagicMock(content="OK.")

        mock_llm.ainvoke = capture
        service._llm = mock_llm

        await service.send_message(
            session_id=str(uuid.uuid4()),
            player_id="p1",
            message="Hello",
        )

        system_content = captured[0].content
        assert "a brave soul" in system_content
        assert "mindfulness garden" in system_content

    async def test_message_id_is_unique(self, service, mock_llm):
        service._llm = mock_llm
        session_id = str(uuid.uuid4())
        mock_llm.ainvoke = AsyncMock(
            side_effect=[MagicMock(content="R1"), MagicMock(content="R2")]
        )

        r1 = await service.send_message(session_id=session_id, player_id="p1", message="A")
        r2 = await service.send_message(session_id=session_id, player_id="p1", message="B")

        assert r1["message_id"] != r2["message_id"]


class TestClearHistory:
    def test_clear_session_history(self, service):
        session_id = str(uuid.uuid4())
        _SESSION_HISTORY[session_id] = [{"role": "user", "content": "hi"}]

        service.clear_session_history(session_id)

        assert session_id not in _SESSION_HISTORY

    def test_clear_nonexistent_session_is_safe(self, service):
        service.clear_session_history("does-not-exist")  # must not raise

    def test_get_session_history_returns_copy(self, service):
        session_id = str(uuid.uuid4())
        _SESSION_HISTORY[session_id] = [{"role": "user", "content": "hi"}]

        history = service.get_session_history(session_id)
        history.append({"role": "user", "content": "injected"})

        # Original must be untouched
        assert len(_SESSION_HISTORY[session_id]) == 1

    def test_get_session_history_empty_for_unknown_session(self, service):
        assert service.get_session_history("unknown") == []
