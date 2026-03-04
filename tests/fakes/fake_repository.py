"""
In-memory fake repository for service-layer tests.

Mirrors the interface of the real repositories (e.g. ``SessionRepository``,
``PlayerProfileRepository``) but stores data in a plain ``dict`` so tests
never touch Neo4j or Redis.
"""

from __future__ import annotations

import copy
from typing import Any


class FakeRepository:
    """Generic in-memory repository backed by a ``dict``.

    Usage::

        repo = FakeRepository()
        await repo.add("player:1", {"name": "Alice", "health": 100})
        player = await repo.get("player:1")
        assert player["name"] == "Alice"
    """

    def __init__(self, initial_data: dict[str, Any] | None = None) -> None:
        self._store: dict[str, Any] = {}
        if initial_data:
            for key, value in initial_data.items():
                self._store[key] = copy.deepcopy(value)

    # -- core CRUD -------------------------------------------------------------

    async def add(self, key: str, value: Any) -> None:
        """Insert or replace an entity."""
        self._store[key] = copy.deepcopy(value)

    async def get(self, key: str) -> Any | None:
        """Return a deep copy of the stored entity or ``None``."""
        value = self._store.get(key)
        return copy.deepcopy(value) if value is not None else None

    async def update(self, key: str, value: Any) -> bool:
        """Update an existing entity. Returns ``False`` if key is absent."""
        if key not in self._store:
            return False
        self._store[key] = copy.deepcopy(value)
        return True

    async def delete(self, key: str) -> bool:
        """Remove an entity. Returns ``False`` if key was absent."""
        return self._store.pop(key, None) is not None

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def list_all(self) -> list[Any]:
        """Return deep copies of every stored value."""
        return [copy.deepcopy(v) for v in self._store.values()]

    async def list_keys(self) -> list[str]:
        return list(self._store.keys())

    async def count(self) -> int:
        return len(self._store)

    async def clear(self) -> None:
        """Remove all data – useful for per-test teardown."""
        self._store.clear()

    # -- helpers for test assertions -------------------------------------------

    @property
    def committed_data(self) -> dict[str, Any]:
        """Direct (non-copied) access for assertions inside tests."""
        return self._store

    def _restore(self, snapshot: dict[str, Any]) -> None:
        """Replace internal store from a snapshot (used by FakeUnitOfWork)."""
        self._store = copy.deepcopy(snapshot)

    def _snapshot(self) -> dict[str, Any]:
        """Return a deep copy of the internal store for snapshotting."""
        return copy.deepcopy(self._store)
