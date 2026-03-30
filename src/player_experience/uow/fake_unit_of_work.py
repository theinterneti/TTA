"""Fake Unit of Work for use in tests — no database, no network."""
# Logseq: [[TTA.dev/Player_experience/Uow/Fake_unit_of_work]]

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from .abstract_session_repository import AbstractSessionRepository
from .session_unit_of_work import AbstractSessionUnitOfWork


class FakeSessionRepository(AbstractSessionRepository):
    """Pure in-memory repository for unit tests."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._messages: dict[str, list[dict[str, Any]]] = {}

    def create_session(
        self,
        session_id: str,
        player_id: str,
        character_id: str,
        world_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        record: dict[str, Any] = {
            "session_id": session_id,
            "player_id": player_id,
            "character_id": character_id,
            "world_id": world_id,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            **kwargs,
        }
        self._sessions[session_id] = record
        return record

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    def list_sessions(self, player_id: str) -> list[dict[str, Any]]:
        return [s for s in self._sessions.values() if s.get("player_id") == player_id]

    def save_message(
        self,
        session_id: str,
        player_id: str,
        role: str,
        content: str,
        **kwargs: Any,
    ) -> str:
        message_id = str(uuid.uuid4())
        if session_id not in self._messages:
            self._messages[session_id] = []
        self._messages[session_id].append(
            {
                "message_id": message_id,
                "session_id": session_id,
                "player_id": player_id,
                "role": role,
                "content": content,
                "created_at": datetime.now(UTC).isoformat(),
                **kwargs,
            }
        )
        return message_id

    def load_messages(self, session_id: str) -> list[dict[str, str]]:
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self._messages.get(session_id, [])
        ]

    def load_messages_full(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._messages.get(session_id, []))

    def clear_messages(self, session_id: str) -> int:
        msgs = self._messages.pop(session_id, [])
        return len(msgs)

    def copy_session(
        self,
        source_session_id: str,
        new_session_id: str | None = None,
        player_id: str | None = None,
    ) -> dict[str, Any] | None:
        source = self._sessions.get(source_session_id)
        if source is None:
            return None
        new_id = new_session_id or str(uuid.uuid4())
        new_record = {
            **source,
            "session_id": new_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        if player_id is not None:
            new_record["player_id"] = player_id
        self._sessions[new_id] = new_record
        return new_record


class FakeSessionUnitOfWork(AbstractSessionUnitOfWork):
    """Fake UoW for unit tests — uses FakeSessionRepository (in-memory)."""

    def __init__(self) -> None:
        self.sessions = FakeSessionRepository()
        self.committed = False

    def __enter__(self) -> FakeSessionUnitOfWork:
        return self

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass
