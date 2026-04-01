"""Unit tests for DoltWorldRepository and schema.

All aiomysql calls are mocked — no live Dolt server required.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.components.dolt.repository import DoltConnectionError, DoltWorldRepository
from src.components.dolt.schema import (
    ALL_SCHEMAS,
    PLAYER_BRANCH_SCHEMA,
    SESSION_SNAPSHOT_SCHEMA,
    WORLD_STATE_SCHEMA,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_pool(rows: list | None = None) -> tuple:
    """Create a mock aiomysql pool that returns the given rows on fetchone/fetchall."""
    cur = AsyncMock()
    cur.execute = AsyncMock()
    cur.fetchone = AsyncMock(return_value=rows[0] if rows else None)
    cur.fetchall = AsyncMock(return_value=rows or [])
    cur.__aenter__ = AsyncMock(return_value=cur)
    cur.__aexit__ = AsyncMock(return_value=None)

    conn = AsyncMock()
    conn.cursor = MagicMock(return_value=cur)
    conn.commit = AsyncMock()
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)

    pool = MagicMock()
    pool.acquire = MagicMock(return_value=conn)
    return pool, conn, cur


def make_error_pool(exc: Exception | None = None) -> tuple:
    """Create a pool whose acquire().__aenter__ raises exc."""
    err = exc or RuntimeError("connection refused")
    conn = AsyncMock()
    conn.__aenter__ = AsyncMock(side_effect=err)
    conn.__aexit__ = AsyncMock(return_value=None)
    pool = MagicMock()
    pool.acquire = MagicMock(return_value=conn)
    return pool, conn


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestDoltSchema:
    def test_all_schemas_non_empty(self) -> None:
        for schema in ALL_SCHEMAS:
            assert len(schema) > 0

    def test_world_state_schema_has_primary_key(self) -> None:
        assert "PRIMARY KEY" in WORLD_STATE_SCHEMA

    def test_world_state_schema_has_required_columns(self) -> None:
        for col in ("world_id", "player_id", "session_id", "tension_level"):
            assert col in WORLD_STATE_SCHEMA

    def test_session_snapshots_schema_has_state_json(self) -> None:
        assert "state_json" in SESSION_SNAPSHOT_SCHEMA

    def test_session_snapshots_schema_has_primary_key(self) -> None:
        assert "PRIMARY KEY" in SESSION_SNAPSHOT_SCHEMA

    def test_player_branches_schema_has_branch_name(self) -> None:
        assert "branch_name" in PLAYER_BRANCH_SCHEMA

    def test_player_branches_schema_has_unique_constraint(self) -> None:
        assert "UNIQUE KEY" in PLAYER_BRANCH_SCHEMA

    def test_all_schemas_list_length(self) -> None:
        assert len(ALL_SCHEMAS) == 3

    def test_all_schemas_contain_create_table(self) -> None:
        for schema in ALL_SCHEMAS:
            assert "CREATE TABLE IF NOT EXISTS" in schema

    def test_all_schemas_use_innodb(self) -> None:
        for schema in ALL_SCHEMAS:
            assert "InnoDB" in schema

    def test_world_state_schema_has_json_columns(self) -> None:
        assert "world_flags" in WORLD_STATE_SCHEMA
        assert "npc_states" in WORLD_STATE_SCHEMA


# ---------------------------------------------------------------------------
# initialize_schema tests
# ---------------------------------------------------------------------------


class TestDoltWorldRepositoryInitSchema:
    @pytest.mark.asyncio
    async def test_initialize_schema_calls_execute_for_each_schema(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
        assert cur.execute.call_count == len(ALL_SCHEMAS)

    @pytest.mark.asyncio
    async def test_initialize_schema_commits(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
        conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_schema_raises_dolt_connection_error_on_failure(
        self,
    ) -> None:
        pool, _ = make_error_pool()
        repo = DoltWorldRepository(pool)
        with pytest.raises(DoltConnectionError):
            await repo.initialize_schema()

    @pytest.mark.asyncio
    async def test_initialize_schema_executes_world_state_sql(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("world_state" in c for c in calls)

    @pytest.mark.asyncio
    async def test_initialize_schema_executes_session_snapshots_sql(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("session_snapshots" in c for c in calls)

    @pytest.mark.asyncio
    async def test_initialize_schema_executes_player_branches_sql(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("player_branches" in c for c in calls)


# ---------------------------------------------------------------------------
# Branch management tests
# ---------------------------------------------------------------------------


class TestDoltWorldRepositoryBranches:
    @pytest.mark.asyncio
    async def test_create_player_branch_returns_branch_name(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        result = await repo.create_player_branch("p1", "ses-abcdef12", "world-1")
        assert result == "player/p1/session-ses-abcd"

    @pytest.mark.asyncio
    async def test_create_player_branch_uses_first_8_chars_of_session(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        session_id = "12345678-abcd-efgh"
        result = await repo.create_player_branch("p2", session_id, "world-x")
        assert result.endswith(session_id[:8])

    @pytest.mark.asyncio
    async def test_create_player_branch_calls_dolt_checkout(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.create_player_branch("p1", "sess-0001", "world-1")
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("DOLT_CHECKOUT" in c for c in calls)

    @pytest.mark.asyncio
    async def test_create_player_branch_inserts_into_player_branches(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.create_player_branch("p1", "sess-0001", "world-1")
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("player_branches" in c for c in calls)

    @pytest.mark.asyncio
    async def test_create_player_branch_commits(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.create_player_branch("p1", "sess-0001", "world-1")
        conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_player_branch_reraises_on_error(self) -> None:
        pool, _ = make_error_pool(RuntimeError("branch conflict"))
        repo = DoltWorldRepository(pool)
        with pytest.raises(RuntimeError, match="branch conflict"):
            await repo.create_player_branch("p1", "sess-0001", "world-1")

    @pytest.mark.asyncio
    async def test_get_player_branch_returns_name_when_found(self) -> None:
        pool, conn, cur = make_mock_pool(rows=[("player/p1/session-abcdef12",)])
        repo = DoltWorldRepository(pool)
        result = await repo.get_player_branch("p1", "sess-1")
        assert result == "player/p1/session-abcdef12"

    @pytest.mark.asyncio
    async def test_get_player_branch_returns_none_when_not_found(self) -> None:
        pool, conn, cur = make_mock_pool(rows=None)
        repo = DoltWorldRepository(pool)
        result = await repo.get_player_branch("p1", "sess-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_player_branch_returns_none_on_error(self) -> None:
        pool, _ = make_error_pool()
        repo = DoltWorldRepository(pool)
        result = await repo.get_player_branch("p1", "sess-1")
        assert result is None


# ---------------------------------------------------------------------------
# Snapshot tests
# ---------------------------------------------------------------------------


class TestDoltWorldRepositorySnapshots:
    @pytest.mark.asyncio
    async def test_commit_snapshot_returns_id(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        result = await repo.commit_snapshot(
            "sess-1", "player-1", "world-1", {"loc": "forest"}
        )
        assert isinstance(result, str)
        assert len(result) == 36  # UUID

    @pytest.mark.asyncio
    async def test_commit_snapshot_calls_dolt_commit(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.commit_snapshot("sess-1", "p1", "w1", {})
        calls = [str(c.args[0]) for c in cur.execute.call_args_list]
        assert any("DOLT_COMMIT" in c for c in calls)

    @pytest.mark.asyncio
    async def test_commit_snapshot_stores_state_as_json(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        state = {"location": "cave", "tension": 0.7}
        await repo.commit_snapshot("sess-1", "p1", "w1", state)
        # Find INSERT call and verify state_json is JSON-encoded
        insert_calls = [
            c for c in cur.execute.call_args_list if "session_snapshots" in str(c)
        ]
        assert insert_calls
        args = insert_calls[0].args[1]
        assert json.loads(args[5]) == state

    @pytest.mark.asyncio
    async def test_commit_snapshot_uses_custom_commit_message(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.commit_snapshot(
            "sess-1", "p1", "w1", {}, commit_message="my custom msg"
        )
        dolt_calls = [
            c for c in cur.execute.call_args_list if "DOLT_COMMIT" in str(c)
        ]
        assert dolt_calls
        assert "my custom msg" in str(dolt_calls[0])

    @pytest.mark.asyncio
    async def test_commit_snapshot_generates_default_message(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.commit_snapshot("sess-1", "p1", "w1", {}, turn_number=5)
        dolt_calls = [
            c for c in cur.execute.call_args_list if "DOLT_COMMIT" in str(c)
        ]
        assert dolt_calls
        assert "5" in str(dolt_calls[0])

    @pytest.mark.asyncio
    async def test_commit_snapshot_commits_connection(self) -> None:
        pool, conn, cur = make_mock_pool()
        repo = DoltWorldRepository(pool)
        await repo.commit_snapshot("sess-1", "p1", "w1", {})
        conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_commit_snapshot_reraises_on_error(self) -> None:
        pool, _ = make_error_pool(ValueError("bad state"))
        repo = DoltWorldRepository(pool)
        with pytest.raises(ValueError, match="bad state"):
            await repo.commit_snapshot("s", "p", "w", {})

    @pytest.mark.asyncio
    async def test_load_snapshot_returns_dict_when_found(self) -> None:
        state = {"location": "forest", "tension": 0.3}
        pool, _, cur = make_mock_pool(rows=[(json.dumps(state),)])
        repo = DoltWorldRepository(pool)
        result = await repo.load_snapshot("sess-1", "player-1")
        assert result == state

    @pytest.mark.asyncio
    async def test_load_snapshot_returns_none_when_not_found(self) -> None:
        pool, conn, cur = make_mock_pool(rows=None)
        repo = DoltWorldRepository(pool)
        result = await repo.load_snapshot("sess-1", "player-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_snapshot_returns_none_on_error(self) -> None:
        pool, _ = make_error_pool()
        repo = DoltWorldRepository(pool)
        result = await repo.load_snapshot("sess-1", "player-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_snapshot_queries_by_session_and_player(self) -> None:
        pool, conn, cur = make_mock_pool(rows=None)
        repo = DoltWorldRepository(pool)
        await repo.load_snapshot("my-sess", "my-player")
        call_args = cur.execute.call_args
        assert call_args.args[1] == ("my-sess", "my-player")

    @pytest.mark.asyncio
    async def test_list_snapshots_returns_list(self) -> None:
        rows = [
            ("id-1", "choice_point", 3, "abc123", "2024-01-01 00:00:00"),
            ("id-2", "session_end", 7, "def456", "2024-01-02 00:00:00"),
        ]
        pool, conn, cur = make_mock_pool(rows=rows)
        repo = DoltWorldRepository(pool)
        result = await repo.list_snapshots("sess-1", "player-1")
        assert len(result) == 2
        assert result[0]["id"] == "id-1"
        assert result[0]["type"] == "choice_point"
        assert result[0]["turn"] == 3

    @pytest.mark.asyncio
    async def test_list_snapshots_returns_empty_on_error(self) -> None:
        pool, _ = make_error_pool()
        repo = DoltWorldRepository(pool)
        result = await repo.list_snapshots("sess-1", "player-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_list_snapshots_respects_limit(self) -> None:
        pool, conn, cur = make_mock_pool(rows=[])
        repo = DoltWorldRepository(pool)
        await repo.list_snapshots("sess-1", "player-1", limit=5)
        call_args = cur.execute.call_args
        assert 5 in call_args.args[1]

    @pytest.mark.asyncio
    async def test_list_snapshots_returns_empty_when_none_found(self) -> None:
        pool, conn, cur = make_mock_pool(rows=[])
        repo = DoltWorldRepository(pool)
        result = await repo.list_snapshots("sess-1", "player-1")
        assert result == []
