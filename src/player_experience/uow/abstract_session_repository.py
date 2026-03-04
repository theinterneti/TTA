"""Domain-specific abstract repository for player sessions."""

# Logseq: [[TTA.dev/Player_experience/Uow/Abstract_session_repository]]

from __future__ import annotations

import abc
from typing import Any


class AbstractSessionRepository(abc.ABC):
    """Abstract interface for session persistence, shared by all backends."""

    @abc.abstractmethod
    def create_session(
        self,
        session_id: str,
        player_id: str,
        character_id: str,
        world_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]: ...

    @abc.abstractmethod
    def get_session(self, session_id: str) -> dict[str, Any] | None: ...

    @abc.abstractmethod
    def list_sessions(self, player_id: str) -> list[dict[str, Any]]: ...

    @abc.abstractmethod
    def save_message(
        self,
        session_id: str,
        player_id: str,
        role: str,
        content: str,
        **kwargs: Any,
    ) -> str: ...

    @abc.abstractmethod
    def load_messages(self, session_id: str) -> list[dict[str, str]]: ...

    @abc.abstractmethod
    def load_messages_full(self, session_id: str) -> list[dict[str, Any]]: ...

    @abc.abstractmethod
    def clear_messages(self, session_id: str) -> int: ...

    @abc.abstractmethod
    def copy_session(
        self,
        source_session_id: str,
        new_session_id: str | None = None,
        player_id: str | None = None,
    ) -> dict[str, Any] | None: ...
