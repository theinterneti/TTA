"""
In-memory fake Unit of Work for service-layer tests.

Groups one or more :class:`FakeRepository` instances under a single
transactional boundary.  ``commit()`` is a no-op (data is already in
memory); ``rollback()`` restores the snapshot taken at construction time.
"""

from __future__ import annotations

from typing import Any

from .fake_repository import FakeRepository


class FakeUnitOfWork:
    """Coordinates multiple :class:`FakeRepository` instances.

    Usage::

        uow = FakeUnitOfWork(sessions=FakeRepository(), players=FakeRepository())
        async with uow:
            await uow.sessions.add("s:1", {"status": "active"})
            await uow.commit()

    On ``rollback()`` every repository is restored to the state captured
    when the context manager was entered.
    """

    def __init__(self, **repositories: FakeRepository) -> None:
        self._repos: dict[str, FakeRepository] = repositories
        self._snapshots: dict[str, dict[str, Any]] = {}
        self.committed = False
        self.rolled_back = False

        # Expose each repository as an attribute for ergonomic access
        for name, repo in repositories.items():
            setattr(self, name, repo)

    # -- context manager -------------------------------------------------------

    async def __aenter__(self) -> "FakeUnitOfWork":
        self._take_snapshot()
        self.committed = False
        self.rolled_back = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()

    # -- transaction API -------------------------------------------------------

    async def commit(self) -> None:
        """Mark the unit of work as committed (data is already in memory)."""
        self.committed = True
        # Take a new snapshot so a subsequent rollback restores to *this* state
        self._take_snapshot()

    async def rollback(self) -> None:
        """Restore every repository to the last snapshot."""
        for name, snapshot in self._snapshots.items():
            repo = self._repos[name]
            repo._restore(snapshot)
        self.rolled_back = True

    # -- internals -------------------------------------------------------------

    def _take_snapshot(self) -> None:
        for name, repo in self._repos.items():
            self._snapshots[name] = repo._snapshot()
