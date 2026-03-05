"""Unit tests for session_service using FakeSessionUnitOfWork — no DB required."""
# Logseq: [[TTA.dev/Tests/Player_experience/Services/Test_session_service]]

from __future__ import annotations

from src.player_experience.services import session_service
from src.player_experience.uow.fake_unit_of_work import FakeSessionUnitOfWork


class TestCreateSession:
    def test_returns_session_with_correct_fields(self) -> None:
        uow = FakeSessionUnitOfWork()
        result = session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        assert result["player_id"] == "p1"
        assert result["character_id"] == "c1"
        assert result["world_id"] == "w1"
        assert result["status"] == "active"
        assert "session_id" in result

    def test_commits(self) -> None:
        uow = FakeSessionUnitOfWork()
        session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        assert uow.committed is True

    def test_each_call_gets_unique_session_id(self) -> None:
        ids = set()
        for _ in range(5):
            uow = FakeSessionUnitOfWork()
            result = session_service.create_session(
                uow, player_id="p1", character_id="c1", world_id="w1"
            )
            ids.add(result["session_id"])
        assert len(ids) == 5


class TestGetSession:
    def test_returns_none_for_missing(self) -> None:
        uow = FakeSessionUnitOfWork()
        assert session_service.get_session(uow, "nonexistent") is None

    def test_returns_session_after_create(self) -> None:
        uow = FakeSessionUnitOfWork()
        created = session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        session_id = created["session_id"]

        # Reuse same UoW (sessions persisted in FakeSessionRepository)
        fetched = session_service.get_session(uow, session_id)
        assert fetched is not None
        assert fetched["session_id"] == session_id


class TestListSessions:
    def test_empty_for_unknown_player(self) -> None:
        uow = FakeSessionUnitOfWork()
        assert session_service.list_sessions(uow, "unknown") == []

    def test_returns_sessions_for_player(self) -> None:
        uow = FakeSessionUnitOfWork()
        session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        session_service.create_session(
            uow, player_id="p1", character_id="c2", world_id="w2"
        )
        session_service.create_session(
            uow, player_id="p2", character_id="c1", world_id="w1"
        )

        results = session_service.list_sessions(uow, "p1")
        assert len(results) == 2
        assert all(r["player_id"] == "p1" for r in results)


class TestSaveMessage:
    def test_commits_and_returns_message_id(self) -> None:
        uow = FakeSessionUnitOfWork()
        created = session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        uow.committed = False  # reset to check save_message commit

        mid = session_service.save_message(
            uow,
            session_id=created["session_id"],
            player_id="p1",
            role="user",
            content="Hello",
        )
        assert isinstance(mid, str)
        assert len(mid) > 0
        assert uow.committed is True

    def test_load_messages_after_save(self) -> None:
        uow = FakeSessionUnitOfWork()
        created = session_service.create_session(
            uow, player_id="p1", character_id="c1", world_id="w1"
        )
        sid = created["session_id"]

        session_service.save_message(
            uow, session_id=sid, player_id="p1", role="user", content="Hi"
        )
        session_service.save_message(
            uow, session_id=sid, player_id="p1", role="assistant", content="Hello!"
        )

        messages = session_service.load_messages(uow, sid)
        assert len(messages) == 2
        assert messages[0] == {"role": "user", "content": "Hi"}
        assert messages[1] == {"role": "assistant", "content": "Hello!"}
