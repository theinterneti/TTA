"""
Unit tests for Dolt world state schema definitions and DoltWorldRepository.

The schema tests verify SQL string content and structure; they do NOT require
a real Dolt/MySQL connection.

The repository tests mock the aiomysql connection pool to verify:
- initialize_schema() executes all schema statements and commits
- create_player_branch() builds correct branch name and inserts a record
- get_player_branch() returns branch name from query result
- get_player_branch() returns None when no record found
- commit_snapshot() inserts into session_snapshots
- DoltConnectionError is raised when schema initialization fails
- All methods are exception-safe (return None/raise domain error on DB failure)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.components.dolt.repository import DoltConnectionError, DoltWorldRepository
from src.components.dolt.schema import (
    ALL_SCHEMAS,
    PLAYER_BRANCH_SCHEMA,
    SESSION_SNAPSHOT_SCHEMA,
    WORLD_STATE_SCHEMA,
)

pytestmark = pytest.mark.unit


# ── Schema content tests (no DB required) ─────────────────────────────────────


def test_world_state_schema_contains_table_name() -> None:
    """WORLD_STATE_SCHEMA SQL string creates the world_state table."""
    assert "world_state" in WORLD_STATE_SCHEMA
    assert "CREATE TABLE IF NOT EXISTS" in WORLD_STATE_SCHEMA


def test_world_state_schema_has_required_columns() -> None:
    """world_state schema includes id, world_id, player_id, session_id columns."""
    for column in ("id", "world_id", "player_id", "session_id", "tension_level"):
        assert column in WORLD_STATE_SCHEMA


def test_session_snapshot_schema_creates_correct_table() -> None:
    """SESSION_SNAPSHOT_SCHEMA SQL string creates the session_snapshots table."""
    assert "session_snapshots" in SESSION_SNAPSHOT_SCHEMA
    assert "CREATE TABLE IF NOT EXISTS" in SESSION_SNAPSHOT_SCHEMA


def test_session_snapshot_schema_has_state_json_column() -> None:
    """session_snapshots schema includes state_json JSON column."""
    assert "state_json" in SESSION_SNAPSHOT_SCHEMA
    assert "JSON" in SESSION_SNAPSHOT_SCHEMA


def test_player_branch_schema_creates_correct_table() -> None:
    """PLAYER_BRANCH_SCHEMA SQL string creates the player_branches table."""
    assert "player_branches" in PLAYER_BRANCH_SCHEMA
    assert "CREATE TABLE IF NOT EXISTS" in PLAYER_BRANCH_SCHEMA


def test_player_branch_schema_has_unique_constraint() -> None:
    """player_branches schema has unique constraint on player_id + session_id."""
    assert "player_id" in PLAYER_BRANCH_SCHEMA
    assert "session_id" in PLAYER_BRANCH_SCHEMA
    assert "UNIQUE" in PLAYER_BRANCH_SCHEMA


def test_all_schemas_contains_three_entries() -> None:
    """ALL_SCHEMAS list contains exactly three SQL migration strings."""
    assert len(ALL_SCHEMAS) == 3


def test_all_schemas_are_strings() -> None:
    """ALL_SCHEMAS entries are non-empty strings."""
    for schema in ALL_SCHEMAS:
        assert isinstance(schema, str)
        assert len(schema) > 20


# ── Mock pool helper ──────────────────────────────────────────────────────────


def _make_pool(fetchone_result: Any = None) -> MagicMock:
    """Build a mock aiomysql pool with async context manager support."""
    cursor = AsyncMock()
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=fetchone_result)

    # cursor as async context manager
    cursor_ctx = MagicMock()
    cursor_ctx.__aenter__ = AsyncMock(return_value=cursor)
    cursor_ctx.__aexit__ = AsyncMock(return_value=False)

    conn = AsyncMock()
    conn.commit = AsyncMock()
    conn.cursor = MagicMock(return_value=cursor_ctx)

    # conn as async context manager
    conn_ctx = MagicMock()
    conn_ctx.__aenter__ = AsyncMock(return_value=conn)
    conn_ctx.__aexit__ = AsyncMock(return_value=False)

    pool = MagicMock()
    pool.acquire = MagicMock(return_value=conn_ctx)

    return pool


# ── DoltWorldRepository.initialize_schema ─────────────────────────────────────


@pytest.mark.asyncio
async def test_initialize_schema_executes_all_schemas() -> None:
    """initialize_schema() calls cursor.execute for each schema in ALL_SCHEMAS."""
    # Arrange
    pool = _make_pool()
    repo = DoltWorldRepository(pool)

    # Act
    await repo.initialize_schema()

    # Assert — one execute call per schema + commit
    conn_ctx = pool.acquire.return_value
    conn = await conn_ctx.__aenter__()
    cursor_ctx = conn.cursor.return_value
    cursor = await cursor_ctx.__aenter__()

    assert cursor.execute.call_count == len(ALL_SCHEMAS)
    conn.commit.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_schema_raises_dolt_connection_error_on_failure() -> None:
    """initialize_schema() raises DoltConnectionError when pool.acquire fails."""
    # Arrange
    pool = MagicMock()
    pool.acquire = MagicMock(side_effect=Exception("connection refused"))
    repo = DoltWorldRepository(pool)

    # Act & Assert
    with pytest.raises(DoltConnectionError):
        await repo.initialize_schema()


# ── DoltWorldRepository.create_player_branch ─────────────────────────────────


@pytest.mark.asyncio
async def test_create_player_branch_returns_formatted_branch_name() -> None:
    """create_player_branch() returns branch in format player/{id}/session-{short}."""
    # Arrange
    pool = _make_pool()
    repo = DoltWorldRepository(pool)

    player_id = "player-abc"
    session_id = "session-12345678-rest"
    world_id = "world-001"

    # Act
    branch_name = await repo.create_player_branch(player_id, session_id, world_id)

    # Assert
    assert branch_name == f"player/{player_id}/session-{session_id[:8]}"


@pytest.mark.asyncio
async def test_create_player_branch_executes_dolt_checkout() -> None:
    """create_player_branch() calls DOLT_CHECKOUT SQL procedure."""
    # Arrange
    pool = _make_pool()
    repo = DoltWorldRepository(pool)

    # Act
    await repo.create_player_branch("p1", "s12345678", "w1")

    # Assert — verify DOLT_CHECKOUT was called
    conn_ctx = pool.acquire.return_value
    conn = await conn_ctx.__aenter__()
    cursor_ctx = conn.cursor.return_value
    cursor = await cursor_ctx.__aenter__()

    calls = [str(call) for call in cursor.execute.call_args_list]
    assert any("DOLT_CHECKOUT" in c for c in calls)


# ── DoltWorldRepository.get_player_branch ─────────────────────────────────────


@pytest.mark.asyncio
async def test_get_player_branch_returns_branch_name_when_found() -> None:
    """get_player_branch() returns branch_name string when row exists."""
    # Arrange
    expected_branch = "player/p1/session-abc12345"
    pool = _make_pool(fetchone_result=(expected_branch,))
    repo = DoltWorldRepository(pool)

    # Act
    result = await repo.get_player_branch("p1", "abc12345-rest")

    # Assert
    assert result == expected_branch


@pytest.mark.asyncio
async def test_get_player_branch_returns_none_when_not_found() -> None:
    """get_player_branch() returns None when no matching row exists."""
    # Arrange — fetchone returns None (no row)
    pool = _make_pool(fetchone_result=None)
    repo = DoltWorldRepository(pool)

    # Act
    result = await repo.get_player_branch("unknown-player", "session-999")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_player_branch_returns_none_on_db_error() -> None:
    """get_player_branch() returns None (does not raise) when pool fails."""
    # Arrange
    pool = MagicMock()
    pool.acquire = MagicMock(side_effect=Exception("DB down"))
    repo = DoltWorldRepository(pool)

    # Act
    result = await repo.get_player_branch("p1", "s1")

    # Assert — exception is swallowed, None returned
    assert result is None


# ── DoltWorldRepository.commit_snapshot ───────────────────────────────────────


@pytest.mark.asyncio
async def test_commit_snapshot_returns_snapshot_id_string() -> None:
    """commit_snapshot() returns a non-empty string snapshot ID."""
    # Arrange
    pool = _make_pool()
    repo = DoltWorldRepository(pool)

    state = {"location": "The Mill", "turn": 5, "flags": {}}

    # Act
    snapshot_id = await repo.commit_snapshot(
        session_id="sess-1",
        player_id="player-1",
        world_id="world-1",
        state=state,
        turn_number=5,
        snapshot_type="choice_point",
    )

    # Assert
    assert isinstance(snapshot_id, str)
    assert len(snapshot_id) > 0


@pytest.mark.asyncio
async def test_commit_snapshot_executes_insert_into_snapshots() -> None:
    """commit_snapshot() executes an INSERT INTO session_snapshots statement."""
    # Arrange
    pool = _make_pool()
    repo = DoltWorldRepository(pool)

    # Act
    await repo.commit_snapshot(
        session_id="sess-2",
        player_id="player-2",
        world_id="world-2",
        state={"location": "Gate"},
    )

    # Assert — verify INSERT was called
    conn_ctx = pool.acquire.return_value
    conn = await conn_ctx.__aenter__()
    cursor_ctx = conn.cursor.return_value
    cursor = await cursor_ctx.__aenter__()

    calls = [str(call) for call in cursor.execute.call_args_list]
    assert any("session_snapshots" in c for c in calls)
