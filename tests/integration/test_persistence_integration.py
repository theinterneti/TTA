"""Integration tests for Dolt + Redis persistence layer.

Requires live tta-dolt (port 3306) and tta-redis (port 6379) containers.
Run with:  uv run pytest -m integration tests/integration/test_persistence_integration.py
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from src.player_experience.database.dolt_session_store import DoltSessionStore
from src.player_experience.database.redis_cache import (
    TokenCache,
    _deserialize_token_data,
    _serialize_token_data,
)


def sid() -> str:
    return str(uuid.uuid4())


def pid() -> str:
    return str(uuid.uuid4())


# ── DoltSessionStore ──────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def dolt() -> DoltSessionStore:
    """Live DoltSessionStore — skips if Dolt is unreachable."""
    try:
        return DoltSessionStore()
    except Exception as exc:
        pytest.skip(f"Dolt unavailable: {exc}")


@pytest.mark.integration
class TestDoltSessionStore:
    def test_create_and_get_session(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        meta = dolt.create_session(session_id, player_id, character_name="Aria")
        assert meta["session_id"] == session_id
        assert meta["character_name"] == "Aria"

        result = dolt.get_session(session_id)
        assert result is not None
        assert result["session_id"] == session_id
        assert result["player_id"] == player_id

    def test_get_nonexistent_returns_none(self, dolt: DoltSessionStore):
        assert dolt.get_session("does-not-exist-ever") is None

    def test_list_sessions_for_player(self, dolt: DoltSessionStore):
        player_id = pid()
        ids = [sid() for _ in range(3)]
        for s in ids:
            dolt.create_session(s, player_id)
        sessions = dolt.list_sessions(player_id)
        assert len(sessions) == 3
        assert {s["session_id"] for s in sessions} == set(ids)

    def test_list_sessions_message_count(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        dolt.save_message(session_id, player_id, "user", "hello")
        dolt.save_message(session_id, player_id, "assistant", "world")
        sessions = dolt.list_sessions(player_id)
        target = next(s for s in sessions if s["session_id"] == session_id)
        assert target["message_count"] == 2

    def test_save_and_load_messages(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        dolt.save_message(session_id, player_id, "user", "Hello")
        dolt.save_message(session_id, player_id, "assistant", "Hi there")

        msgs = dolt.load_messages(session_id)
        assert len(msgs) == 2
        assert msgs[0] == {"role": "user", "content": "Hello"}
        assert msgs[1] == {"role": "assistant", "content": "Hi there"}

    def test_load_messages_full_includes_metadata(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        mid = dolt.save_message(session_id, player_id, "user", "Test")
        full = dolt.load_messages_full(session_id)
        assert len(full) == 1
        assert full[0]["message_id"] == mid
        assert "created_at" in full[0]

    def test_clear_messages(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        dolt.save_message(session_id, player_id, "user", "A")
        dolt.save_message(session_id, player_id, "assistant", "B")

        deleted = dolt.clear_messages(session_id)
        assert deleted == 2
        assert dolt.load_messages(session_id) == []

    def test_session_metadata_preserved_after_clear(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id, character_name="Aria")
        dolt.save_message(session_id, player_id, "user", "Hello")
        dolt.clear_messages(session_id)

        meta = dolt.get_session(session_id)
        assert meta is not None
        assert meta["character_name"] == "Aria"

    def test_copy_session(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(
            session_id, player_id, character_name="Aria", world_name="Crystal Caverns"
        )
        dolt.save_message(session_id, player_id, "user", "msg1")
        dolt.save_message(session_id, player_id, "assistant", "reply1")

        new_meta = dolt.copy_session(session_id)
        assert new_meta is not None
        assert new_meta["session_id"] != session_id
        assert new_meta["character_name"] == "Aria"
        assert new_meta["world_name"] == "Crystal Caverns"

        new_msgs = dolt.load_messages(new_meta["session_id"])
        assert len(new_msgs) == 2
        assert new_msgs[0]["content"] == "msg1"

    def test_copy_session_is_independent(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        dolt.save_message(session_id, player_id, "user", "original")

        new_meta = dolt.copy_session(session_id)
        assert new_meta is not None

        dolt.save_message(new_meta["session_id"], player_id, "user", "new only")

        original_msgs = dolt.load_messages(session_id)
        assert len(original_msgs) == 1  # original unchanged

    def test_copy_nonexistent_returns_none(self, dolt: DoltSessionStore):
        assert dolt.copy_session("does-not-exist-ever") is None

    def test_copy_accepts_explicit_new_id(self, dolt: DoltSessionStore):
        session_id, player_id = sid(), pid()
        dolt.create_session(session_id, player_id)
        new_id = sid()
        new_meta = dolt.copy_session(session_id, new_session_id=new_id)
        assert new_meta is not None
        assert new_meta["session_id"] == new_id


# ── TokenCache ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def token_cache() -> TokenCache:
    """Live TokenCache — skips if Redis is unreachable."""
    try:
        cache = TokenCache.from_env()
        # Quick connectivity check
        result = asyncio.get_event_loop().run_until_complete(cache.ping())
        if not result:
            pytest.skip("Redis ping returned False")
        return cache
    except Exception as exc:
        pytest.skip(f"Redis unavailable: {exc}")


@pytest.mark.integration
class TestTokenCache:
    async def test_set_and_get(self, token_cache: TokenCache):
        token = "test.fake.jwt." + sid()
        data = {"player_id": pid(), "username": "testuser", "email": None, "exp": None}
        await token_cache.set(token, data, ttl=60)
        result = await token_cache.get(token)
        assert result is not None
        assert result["player_id"] == data["player_id"]

    async def test_get_miss_returns_none(self, token_cache: TokenCache):
        result = await token_cache.get("not-a-real-token-" + sid())
        assert result is None

    async def test_delete_invalidates_entry(self, token_cache: TokenCache):
        token = "delete.test." + sid()
        await token_cache.set(token, {"player_id": "p1"}, ttl=60)
        await token_cache.delete(token)
        result = await token_cache.get(token)
        assert result is None

    async def test_zero_ttl_not_cached(self, token_cache: TokenCache):
        token = "zero.ttl." + sid()
        await token_cache.set(token, {"player_id": "p1"}, ttl=0)
        result = await token_cache.get(token)
        assert result is None

    async def test_serialize_round_trip(self, token_cache: TokenCache):
        """Verify serialize/deserialize produces equivalent TokenData kwargs."""
        from datetime import UTC, datetime

        from src.player_experience.api.auth import TokenData

        td = TokenData(
            player_id="player-123",
            username="hero",
            email="hero@tta.dev",
            exp=datetime(2099, 1, 1, tzinfo=UTC),
        )
        serialized = _serialize_token_data(td)
        deserialized = _deserialize_token_data(serialized)
        assert deserialized["player_id"] == "player-123"
        assert deserialized["username"] == "hero"
        assert deserialized["exp"] is not None
