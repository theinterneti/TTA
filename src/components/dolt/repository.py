"""
# Logseq: [[TTA/Components/Dolt/Repository]]
DoltWorldRepository — async interface to the Dolt branching world state database.

Uses aiomysql for async MySQL-protocol connection to Dolt.

Issue: #282
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from .schema import ALL_SCHEMAS

logger = logging.getLogger(__name__)


class DoltConnectionError(Exception):
    """Raised when Dolt connection cannot be established."""


class DoltWorldRepository:
    """
    Async interface to Dolt for branching world state management.

    All methods require an active aiomysql connection pool.
    The pool is injected — this class does not manage connection lifecycle.

    Usage:
        pool = await aiomysql.create_pool(host=..., db=..., ...)
        repo = DoltWorldRepository(pool)
        await repo.initialize_schema()
    """

    def __init__(self, pool: Any) -> None:
        """
        Args:
            pool: aiomysql connection pool (or mock for testing).
        """
        self._pool = pool

    # ── Schema ─────────────────────────────────────────────────────────────────

    async def initialize_schema(self) -> None:
        """Create tables if they don't exist. Idempotent."""
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    for schema_sql in ALL_SCHEMAS:
                        await cur.execute(schema_sql)
                await conn.commit()
            logger.info("dolt: schema initialized")
        except Exception as exc:
            logger.error("dolt: schema initialization failed: %s", exc)
            raise DoltConnectionError(f"Schema init failed: {exc}") from exc

    # ── Branch management ──────────────────────────────────────────────────────

    async def create_player_branch(
        self, player_id: str, session_id: str, world_id: str
    ) -> str:
        """
        Create a Dolt branch for this player session.

        Branch name: player/{player_id}/session-{session_id[:8]}

        Returns:
            The branch name created.
        """
        branch_name = f"player/{player_id}/session-{session_id[:8]}"
        record_id = str(uuid.uuid4())

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Create the Dolt branch (Dolt-specific SQL)
                    await cur.execute("CALL DOLT_CHECKOUT('-b', %s)", (branch_name,))
                    # Record the branch mapping
                    await cur.execute(
                        """INSERT INTO player_branches
                           (id, player_id, session_id, world_id, branch_name)
                           VALUES (%s, %s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE
                             branch_name=VALUES(branch_name),
                             updated_at=CURRENT_TIMESTAMP""",
                        (record_id, player_id, session_id, world_id, branch_name),
                    )
                await conn.commit()
            logger.info("dolt: created branch=%s for player=%s", branch_name, player_id)
            return branch_name
        except Exception as exc:
            logger.error("dolt: create_player_branch failed: %s", exc)
            raise

    async def get_player_branch(self, player_id: str, session_id: str) -> str | None:
        """Get the branch name for a player session. Returns None if not found."""
        try:
            async with self._pool.acquire() as conn, conn.cursor() as cur:
                await cur.execute(
                    "SELECT branch_name FROM player_branches"
                    " WHERE player_id=%s AND session_id=%s",
                    (player_id, session_id),
                )
                row = await cur.fetchone()
                return row[0] if row else None
        except Exception as exc:
            logger.error("dolt: get_player_branch failed: %s", exc)
            return None

    # ── State snapshots ────────────────────────────────────────────────────────

    async def commit_snapshot(
        self,
        session_id: str,
        player_id: str,
        world_id: str,
        state: dict[str, Any],
        turn_number: int = 0,
        snapshot_type: str = "choice_point",
        commit_message: str = "",
    ) -> str:
        """
        Save a world state snapshot to Dolt.

        Creates a record in session_snapshots and makes a Dolt commit.

        Returns:
            Snapshot record ID.
        """
        snapshot_id = str(uuid.uuid4())
        msg = commit_message or f"snapshot: turn {turn_number} ({snapshot_type})"

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO session_snapshots
                           (id, session_id, player_id, world_id,
                            snapshot_type, state_json, turn_number)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (
                            snapshot_id,
                            session_id,
                            player_id,
                            world_id,
                            snapshot_type,
                            json.dumps(state),
                            turn_number,
                        ),
                    )
                    # Dolt commit
                    await cur.execute("CALL DOLT_COMMIT('-Am', %s)", (msg,))
                await conn.commit()
            logger.info(
                "dolt: snapshot id=%s session=%s turn=%d",
                snapshot_id,
                session_id,
                turn_number,
            )
            return snapshot_id
        except Exception as exc:
            logger.error("dolt: commit_snapshot failed: %s", exc)
            raise

    async def load_snapshot(
        self, session_id: str, player_id: str
    ) -> dict[str, Any] | None:
        """Load the most recent snapshot for a session. Returns None if not found."""
        try:
            async with self._pool.acquire() as conn, conn.cursor() as cur:
                await cur.execute(
                    """SELECT state_json FROM session_snapshots
                           WHERE session_id=%s AND player_id=%s
                           ORDER BY created_at DESC LIMIT 1""",
                    (session_id, player_id),
                )
                row = await cur.fetchone()
                if row:
                    return json.loads(row[0])  # type: ignore[no-any-return]
                return None
        except Exception as exc:
            logger.error("dolt: load_snapshot failed: %s", exc)
            return None

    async def list_snapshots(
        self, session_id: str, player_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """List snapshots for a session, most recent first."""
        try:
            async with self._pool.acquire() as conn, conn.cursor() as cur:
                await cur.execute(
                    """SELECT id, snapshot_type, turn_number, dolt_commit, created_at
                           FROM session_snapshots
                           WHERE session_id=%s AND player_id=%s
                           ORDER BY created_at DESC LIMIT %s""",
                    (session_id, player_id, limit),
                )
                rows = await cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "type": r[1],
                        "turn": r[2],
                        "commit": r[3],
                        "at": str(r[4]),
                    }
                    for r in rows
                ]
        except Exception as exc:
            logger.error("dolt: list_snapshots failed: %s", exc)
            return []
