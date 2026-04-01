"""Tests for in-memory FakeRepository and FakeUnitOfWork."""

import pytest

from tests.fakes import FakeRepository, FakeUnitOfWork

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# FakeRepository
# ---------------------------------------------------------------------------


class TestFakeRepository:
    @pytest.fixture
    def repo(self):
        return FakeRepository()

    async def test_add_and_get(self, repo):
        """Fake Repository: add and get."""
        await repo.add("k1", {"name": "Alice"})
        result = await repo.get("k1")
        assert result == {"name": "Alice"}

    async def test_get_returns_none_for_missing_key(self, repo):
        """Fake Repository: get returns none for missing key."""
        assert await repo.get("missing") is None

    async def test_get_returns_deep_copy(self, repo):
        """Fake Repository: get returns deep copy."""
        original = {"items": [1, 2, 3]}
        await repo.add("k1", original)
        fetched = await repo.get("k1")
        fetched["items"].append(4)
        assert await repo.get("k1") == {"items": [1, 2, 3]}

    async def test_update_existing_key(self, repo):
        """Fake Repository: update existing key."""
        await repo.add("k1", {"v": 1})
        assert await repo.update("k1", {"v": 2}) is True
        assert (await repo.get("k1"))["v"] == 2

    async def test_update_missing_key(self, repo):
        """Fake Repository: update missing key."""
        assert await repo.update("missing", {"v": 1}) is False

    async def test_delete(self, repo):
        """Fake Repository: delete."""
        await repo.add("k1", "val")
        assert await repo.delete("k1") is True
        assert await repo.exists("k1") is False
        assert await repo.delete("k1") is False

    async def test_list_all(self, repo):
        """Fake Repository: list all."""
        await repo.add("a", 1)
        await repo.add("b", 2)
        values = await repo.list_all()
        assert sorted(values) == [1, 2]

    async def test_count(self, repo):
        """Fake Repository: count."""
        assert await repo.count() == 0
        await repo.add("x", "y")
        assert await repo.count() == 1

    async def test_clear(self, repo):
        """Fake Repository: clear."""
        await repo.add("x", 1)
        await repo.clear()
        assert await repo.count() == 0

    def test_initial_data(self):
        """Fake Repository: initial data."""
        repo = FakeRepository(initial_data={"a": 1, "b": 2})
        assert repo.committed_data == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# FakeUnitOfWork
# ---------------------------------------------------------------------------


class TestFakeUnitOfWork:
    async def test_commit_marks_committed(self):
        """Fake Unit Of Work: commit marks committed."""
        uow = FakeUnitOfWork(sessions=FakeRepository())
        async with uow:
            await uow.sessions.add("s1", {"status": "active"})
            await uow.commit()
        assert uow.committed is True

    async def test_rollback_restores_data(self):
        """Fake Unit Of Work: rollback restores data."""
        repo = FakeRepository(initial_data={"s1": {"status": "active"}})
        uow = FakeUnitOfWork(sessions=repo)
        async with uow:
            await uow.sessions.delete("s1")
            await uow.rollback()
        assert await repo.get("s1") == {"status": "active"}

    async def test_exception_triggers_rollback(self):
        """Fake Unit Of Work: exception triggers rollback."""
        repo = FakeRepository(initial_data={"s1": "before"})
        uow = FakeUnitOfWork(sessions=repo)
        with pytest.raises(RuntimeError):
            async with uow:
                await uow.sessions.add("s1", "after")
                raise RuntimeError("boom")
        assert await repo.get("s1") == "before"
        assert uow.rolled_back is True

    async def test_multiple_repositories(self):
        """Fake Unit Of Work: multiple repositories."""
        sessions = FakeRepository()
        players = FakeRepository()
        uow = FakeUnitOfWork(sessions=sessions, players=players)
        async with uow:
            await uow.sessions.add("s1", "data")
            await uow.players.add("p1", "alice")
            await uow.commit()
        assert await sessions.get("s1") == "data"
        assert await players.get("p1") == "alice"
