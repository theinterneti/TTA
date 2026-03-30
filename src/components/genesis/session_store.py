"""
Genesis Session Store — Redis-backed persistence for GenesisSessionState.

Serialises/deserialises the full session state to/from JSON so the stateless
HTTP layer can reconstruct each session per request.

Key pattern:  ``genesis:session:{session_id}``
TTL:          24 hours (sessions expire if the player walks away)

Fallback:     An in-memory dict is used when Redis is unavailable, so
              development and testing work without a running Redis instance.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .session_state import GenesisSessionState

logger = logging.getLogger(__name__)

_REDIS_KEY_PREFIX = "genesis:session:"
_TTL_SECONDS = 86_400  # 24 hours
_DEFAULT_REDIS_URL = "redis://localhost:6379"


# ── Serialisation helpers ─────────────────────────────────────────────────────


def _state_to_dict(state: GenesisSessionState) -> dict[str, Any]:
    """Convert GenesisSessionState to a JSON-serialisable dict."""
    turns_data = []
    for t in state.turns:
        turns_data.append(
            {
                "turn_number": t.turn_number,
                "act": t.act.value,
                "player_input": t.player_input,
                "agent_response": t.agent_response,
                "seed_fields_established": t.seed_fields_established,
                "is_slip": t.is_slip,
                "timestamp": t.timestamp.isoformat(),
            }
        )

    guide_data: dict[str, Any] | None = None
    if state.guide_character is not None:
        guide_data = state.guide_character.model_dump()

    return {
        "session_id": state.session_id,
        "act": state.act.value,
        "turns": turns_data,
        "seed_fields": state.seed_fields,
        "slips_delivered": state.slips_delivered,
        "first_light_confirmed": state.first_light_confirmed,
        "guide_introduced": state.guide_introduced,
        "guide_character": guide_data,
        "surprise_me": state.surprise_me,
        "first_light_paragraph": state.first_light_paragraph,
        "cultural_references": state.cultural_references,
        "created_at": state.created_at.isoformat(),
        "updated_at": state.updated_at.isoformat(),
    }


def _state_from_dict(data: dict[str, Any]) -> GenesisSessionState:
    """Reconstruct GenesisSessionState from a plain dict (loaded from Redis)."""
    from src.components.gameplay_loop.models.world_seed import GuideCharacter

    from .session_state import Act, GenesisSessionState, Turn

    turns = []
    for t in data.get("turns", []):
        turns.append(
            Turn(
                turn_number=t["turn_number"],
                act=Act(t["act"]),
                player_input=t["player_input"],
                agent_response=t["agent_response"],
                seed_fields_established=t.get("seed_fields_established", []),
                is_slip=t.get("is_slip", False),
                timestamp=datetime.fromisoformat(t["timestamp"]),
            )
        )

    guide_character: GuideCharacter | None = None
    if data.get("guide_character"):
        guide_character = GuideCharacter(**data["guide_character"])

    return GenesisSessionState(
        session_id=data["session_id"],
        act=Act(data["act"]),
        turns=turns,
        seed_fields=data.get("seed_fields", {}),
        slips_delivered=data.get("slips_delivered", 0),
        first_light_confirmed=data.get("first_light_confirmed", False),
        guide_introduced=data.get("guide_introduced", False),
        guide_character=guide_character,
        surprise_me=data.get("surprise_me", False),
        first_light_paragraph=data.get("first_light_paragraph"),
        cultural_references=data.get("cultural_references", []),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


# ── Store ─────────────────────────────────────────────────────────────────────


class GenesisSessionStore:
    """
    Async Redis-backed store for Genesis Session state.

    Falls back to an in-memory dict when Redis is unavailable (development /
    testing / environments without a Redis sidecar).

    Usage::

        store = GenesisSessionStore()
        await store.save(state)
        state = await store.load(session_id)
        await store.delete(session_id)
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis_url = redis_url
        self._client: Any | None = None
        self._fallback: dict[str, str] = {}
        self._use_fallback: bool = False

    async def _get_client(self) -> Any | None:
        """Return an initialised Redis client, or None if unavailable."""
        if self._use_fallback:
            return None
        if self._client is not None:
            return self._client

        try:
            import redis.asyncio as aioredis  # type: ignore[import-untyped]

            url = self._redis_url or os.environ.get("REDIS_URL", _DEFAULT_REDIS_URL)
            client = aioredis.from_url(url, decode_responses=True)
            await client.ping()  # type: ignore[union-attr]
            self._client = client
            logger.debug("genesis_session_store: Redis connected at %s", url)
            return client
        except Exception as exc:
            logger.warning(
                "genesis_session_store: Redis unavailable (%s) — using in-memory fallback",
                exc,
            )
            self._use_fallback = True
            return None

    def _make_key(self, session_id: str) -> str:
        return f"{_REDIS_KEY_PREFIX}{session_id}"

    async def save(self, state: GenesisSessionState) -> None:  # noqa: F821
        """Persist the session state, resetting the 24-hour TTL."""
        from .session_state import GenesisSessionState  # noqa: F401

        state.updated_at = datetime.now(UTC)
        payload = json.dumps(_state_to_dict(state))
        key = self._make_key(state.session_id)

        client = await self._get_client()
        if client is not None:
            try:
                await client.setex(key, _TTL_SECONDS, payload)
                return
            except Exception as exc:
                logger.warning(
                    "genesis_session_store: Redis write failed (%s) — falling back to memory",
                    exc,
                )
                self._use_fallback = True

        self._fallback[key] = payload

    async def load(self, session_id: str) -> GenesisSessionState | None:  # noqa: F821
        """Load session state by ID.  Returns None if not found."""
        key = self._make_key(session_id)

        client = await self._get_client()
        if client is not None:
            try:
                raw = await client.get(key)
                if raw is None:
                    return None
                return _state_from_dict(json.loads(raw))
            except Exception as exc:
                logger.warning(
                    "genesis_session_store: Redis read failed (%s) — trying memory fallback",
                    exc,
                )

        raw = self._fallback.get(key)
        if raw is None:
            return None
        return _state_from_dict(json.loads(raw))

    async def delete(self, session_id: str) -> None:
        """Remove a session from the store."""
        key = self._make_key(session_id)

        client = await self._get_client()
        if client is not None:
            try:
                await client.delete(key)
                return
            except Exception as exc:
                logger.warning("genesis_session_store: Redis delete failed (%s)", exc)

        self._fallback.pop(key, None)

    async def exists(self, session_id: str) -> bool:
        """Return True if a session with this ID is stored."""
        key = self._make_key(session_id)

        client = await self._get_client()
        if client is not None:
            try:
                return bool(await client.exists(key))
            except Exception as exc:
                logger.warning(
                    "genesis_session_store: Redis exists check failed (%s)", exc
                )

        return key in self._fallback
