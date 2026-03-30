"""Pure-function session service — delegates to AbstractSessionUnitOfWork."""
# Logseq: [[TTA.dev/Player_experience/Services/Session_service]]

from __future__ import annotations

import uuid
from typing import Any

from ..uow.session_unit_of_work import AbstractSessionUnitOfWork


def create_session(
    uow: AbstractSessionUnitOfWork,
    player_id: str,
    character_id: str,
    world_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a new session and commit."""
    session_id = str(uuid.uuid4())
    with uow:
        result = uow.sessions.create_session(
            session_id=session_id,
            player_id=player_id,
            character_id=character_id,
            world_id=world_id,
            **kwargs,
        )
        uow.commit()
    return result


def get_session(
    uow: AbstractSessionUnitOfWork, session_id: str
) -> dict[str, Any] | None:
    """Retrieve a session by ID."""
    with uow:
        return uow.sessions.get_session(session_id)


def list_sessions(
    uow: AbstractSessionUnitOfWork, player_id: str
) -> list[dict[str, Any]]:
    """List all sessions for a player."""
    with uow:
        return uow.sessions.list_sessions(player_id)


def save_message(
    uow: AbstractSessionUnitOfWork,
    session_id: str,
    player_id: str,
    role: str,
    content: str,
    **kwargs: Any,
) -> str:
    """Save a message to a session and commit."""
    with uow:
        message_id = uow.sessions.save_message(
            session_id, player_id, role, content, **kwargs
        )
        uow.commit()
    return message_id


def load_messages(
    uow: AbstractSessionUnitOfWork, session_id: str
) -> list[dict[str, str]]:
    """Load condensed messages (role + content) for a session."""
    with uow:
        return uow.sessions.load_messages(session_id)
