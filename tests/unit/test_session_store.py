"""Unit tests for SessionStore (SQLite-backed session persistence)."""

from __future__ import annotations

import uuid

import pytest

from src.player_experience.services.session_store import SessionStore


@pytest.fixture()
def store(tmp_path):
    """Fresh in-memory SQLite store per test."""
    return SessionStore(db_path=tmp_path / "test_sessions.db")


@pytest.fixture()
def mem_store():
    """Pure in-memory fallback store (simulates unavailable SQLite)."""
    s = SessionStore.__new__(SessionStore)
    s._db_path = ":bad-path:"
    s._available = False
    s._mem_meta = {}
    s._mem_msgs = {}
    return s


def sid() -> str:
    return str(uuid.uuid4())


def pid() -> str:
    return str(uuid.uuid4())


# ── Session Metadata ──────────────────────────────────────────────────────────


class TestCreateAndGetSession:
    def test_create_returns_metadata(self, store):
        session_id, player_id = sid(), pid()
        meta = store.create_session(session_id, player_id, character_name="Aria")
        assert meta["session_id"] == session_id
        assert meta["player_id"] == player_id
        assert meta["character_name"] == "Aria"
        assert meta["status"] == "active"
        assert "created_at" in meta

    def test_get_returns_persisted_session(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        result = store.get_session(session_id)
        assert result is not None
        assert result["session_id"] == session_id

    def test_get_returns_none_for_unknown(self, store):
        assert store.get_session("does-not-exist") is None

    def test_create_persists_across_new_connection(self, tmp_path):
        """Verify data survives creating a new store instance (same DB file)."""
        db = tmp_path / "sessions.db"
        session_id, player_id = sid(), pid()

        store1 = SessionStore(db_path=db)
        store1.create_session(session_id, player_id)

        store2 = SessionStore(db_path=db)
        result = store2.get_session(session_id)
        assert result is not None
        assert result["session_id"] == session_id


class TestListSessions:
    def test_lists_sessions_for_player(self, store):
        player_id = pid()
        ids = [sid() for _ in range(3)]
        for s in ids:
            store.create_session(s, player_id)
        sessions = store.list_sessions(player_id)
        assert len(sessions) == 3
        assert {s["session_id"] for s in sessions} == set(ids)

    def test_does_not_list_other_players_sessions(self, store):
        p1, p2 = pid(), pid()
        store.create_session(sid(), p1)
        store.create_session(sid(), p2)
        assert len(store.list_sessions(p1)) == 1
        assert len(store.list_sessions(p2)) == 1

    def test_empty_for_unknown_player(self, store):
        assert store.list_sessions("ghost") == []

    def test_includes_message_count(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        store.save_message(session_id, player_id, "user", "hello")
        store.save_message(session_id, player_id, "assistant", "world")
        sessions = store.list_sessions(player_id)
        assert sessions[0]["message_count"] == 2


# ── Message Persistence ───────────────────────────────────────────────────────


class TestSaveAndLoadMessages:
    def test_save_and_load_round_trip(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        store.save_message(session_id, player_id, "user", "Hello")
        store.save_message(session_id, player_id, "assistant", "Hi there")

        msgs = store.load_messages(session_id)
        assert len(msgs) == 2
        assert msgs[0] == {"role": "user", "content": "Hello"}
        assert msgs[1] == {"role": "assistant", "content": "Hi there"}

    def test_load_full_includes_message_id_and_timestamp(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        mid = store.save_message(session_id, player_id, "user", "Test")

        full = store.load_messages_full(session_id)
        assert len(full) == 1
        assert full[0]["message_id"] == mid
        assert "created_at" in full[0]

    def test_messages_ordered_by_insertion(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        for i in range(5):
            store.save_message(session_id, player_id, "user", f"msg {i}")

        msgs = store.load_messages(session_id)
        contents = [m["content"] for m in msgs]
        assert contents == [f"msg {i}" for i in range(5)]

    def test_load_empty_for_unknown_session(self, store):
        assert store.load_messages("ghost") == []

    def test_persists_across_new_connection(self, tmp_path):
        db = tmp_path / "sessions.db"
        session_id, player_id = sid(), pid()

        s1 = SessionStore(db_path=db)
        s1.create_session(session_id, player_id)
        s1.save_message(session_id, player_id, "user", "Persisted?")

        s2 = SessionStore(db_path=db)
        msgs = s2.load_messages(session_id)
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Persisted?"


# ── Clear Messages ────────────────────────────────────────────────────────────


class TestClearMessages:
    def test_clears_all_messages(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        store.save_message(session_id, player_id, "user", "A")
        store.save_message(session_id, player_id, "assistant", "B")

        deleted = store.clear_messages(session_id)
        assert deleted == 2
        assert store.load_messages(session_id) == []

    def test_session_metadata_preserved_after_clear(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id, character_name="Aria")
        store.save_message(session_id, player_id, "user", "Hello")
        store.clear_messages(session_id)

        meta = store.get_session(session_id)
        assert meta is not None
        assert meta["character_name"] == "Aria"

    def test_clear_nonexistent_session_returns_zero(self, store):
        assert store.clear_messages("ghost") == 0


# ── Copy Session ──────────────────────────────────────────────────────────────


class TestCopySession:
    def test_copy_creates_new_session(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id, character_name="Aria", world_name="Forest")
        store.save_message(session_id, player_id, "user", "Hello")
        store.save_message(session_id, player_id, "assistant", "Hi")

        new_meta = store.copy_session(session_id)
        assert new_meta is not None
        assert new_meta["session_id"] != session_id

    def test_copy_duplicates_messages(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        store.save_message(session_id, player_id, "user", "msg1")
        store.save_message(session_id, player_id, "assistant", "reply1")

        new_meta = store.copy_session(session_id)
        assert new_meta is not None

        new_msgs = store.load_messages(new_meta["session_id"])
        assert len(new_msgs) == 2
        assert new_msgs[0]["content"] == "msg1"
        assert new_msgs[1]["content"] == "reply1"

    def test_copy_preserves_character_and_world(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(
            session_id, player_id, character_name="Aria", world_name="Crystal Caverns"
        )
        new_meta = store.copy_session(session_id)
        assert new_meta is not None
        assert new_meta["character_name"] == "Aria"
        assert new_meta["world_name"] == "Crystal Caverns"

    def test_copy_is_independent(self, store):
        """Changes to the copy must not affect the original."""
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        store.save_message(session_id, player_id, "user", "original")

        new_meta = store.copy_session(session_id)
        assert new_meta is not None

        store.save_message(new_meta["session_id"], player_id, "user", "new only")

        original_msgs = store.load_messages(session_id)
        assert len(original_msgs) == 1  # original unchanged

    def test_copy_nonexistent_returns_none(self, store):
        assert store.copy_session("does-not-exist") is None

    def test_copy_accepts_explicit_new_id(self, store):
        session_id, player_id = sid(), pid()
        store.create_session(session_id, player_id)
        new_id = sid()
        new_meta = store.copy_session(session_id, new_session_id=new_id)
        assert new_meta is not None
        assert new_meta["session_id"] == new_id


# ── In-memory Fallback ────────────────────────────────────────────────────────


class TestInMemoryFallback:
    def test_create_and_get_in_memory(self, mem_store):
        session_id, player_id = sid(), pid()
        mem_store.create_session(session_id, player_id)
        result = mem_store.get_session(session_id)
        assert result is not None
        assert result["session_id"] == session_id

    def test_save_and_load_in_memory(self, mem_store):
        session_id, player_id = sid(), pid()
        mem_store.create_session(session_id, player_id)
        mem_store.save_message(session_id, player_id, "user", "hello")
        msgs = mem_store.load_messages(session_id)
        assert len(msgs) == 1
        assert msgs[0]["content"] == "hello"

    def test_clear_in_memory(self, mem_store):
        session_id, player_id = sid(), pid()
        mem_store.create_session(session_id, player_id)
        mem_store.save_message(session_id, player_id, "user", "hi")
        mem_store.clear_messages(session_id)
        assert mem_store.load_messages(session_id) == []
