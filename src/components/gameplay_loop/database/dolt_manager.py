"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Database/Dolt_manager]]

# Logseq: [[TTA/Components/Gameplay_loop/Database/Dolt_manager]]
Dolt-backed manager for the gameplay loop.

Implements the same async interface as Neo4jGameplayManager so the controller
can swap backends without code changes.  All synchronous pymysql calls are
wrapped in asyncio.to_thread to avoid blocking the event loop.

Falls back gracefully when Dolt is unreachable — initialize() returns False and
all subsequent operations are no-ops that return safe defaults.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any

import pymysql
import pymysql.cursors

from ..models.core import Scene, SessionState

logger = logging.getLogger(__name__)

# DDL for the three gameplay tables created on first connect.
_CREATE_STATE_TABLE = """
CREATE TABLE IF NOT EXISTS gameplay_state (
    session_id  VARCHAR(255) NOT NULL PRIMARY KEY,
    state_json  MEDIUMTEXT   NOT NULL,
    updated_at  DATETIME     NOT NULL
)
"""

_CREATE_SCENES_TABLE = """
CREATE TABLE IF NOT EXISTS gameplay_scenes (
    scene_id    VARCHAR(255) NOT NULL PRIMARY KEY,
    session_id  VARCHAR(255),
    scene_json  MEDIUMTEXT   NOT NULL,
    created_at  DATETIME     NOT NULL
)
"""

_CREATE_SUMMARIES_TABLE = """
CREATE TABLE IF NOT EXISTS gameplay_summaries (
    session_id    VARCHAR(255) NOT NULL PRIMARY KEY,
    summary_json  MEDIUMTEXT   NOT NULL,
    updated_at    DATETIME     NOT NULL
)
"""


class DoltGameplayManager:
    """Async gameplay manager backed by Dolt (MySQL-compatible).

    The public interface mirrors Neo4jGameplayManager so the controller treats
    both implementations interchangeably.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self._host = host or os.environ.get("DOLT_HOST", "127.0.0.1")
        self._port = port or int(os.environ.get("DOLT_PORT", "3306"))
        self._user = user or os.environ.get("DOLT_USER", "root")
        self._password = (
            password if password is not None else os.environ.get("DOLT_PASSWORD", "")
        )
        self._database = database or os.environ.get("DOLT_DATABASE", "tta_solo")
        self._available = False  # Set True after successful initialize()

    # ── Connection helpers (sync, called inside to_thread) ──────────────────

    def _connect(self) -> pymysql.Connection:  # type: ignore[type-arg]
        return pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=5,
        )

    def _ensure_tables(self) -> None:
        """Create gameplay tables if they don't exist (sync)."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(_CREATE_STATE_TABLE)
                cur.execute(_CREATE_SCENES_TABLE)
                cur.execute(_CREATE_SUMMARIES_TABLE)
            conn.commit()
        finally:
            conn.close()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def initialize(self) -> bool:
        """Connect to Dolt and create gameplay tables.

        Returns False (and logs a warning) if Dolt is unreachable so the
        caller can fall back to another backend.
        """
        try:
            await asyncio.to_thread(self._ensure_tables)
            self._available = True
            logger.info(
                "DoltGameplayManager: connected to %s:%s/%s",
                self._host,
                self._port,
                self._database,
            )
            return True
        except Exception as exc:
            logger.warning(
                "DoltGameplayManager: Dolt unreachable, gameplay will run without "
                "persistent storage: %s",
                exc,
            )
            return False

    async def close(self) -> None:
        """No persistent connection to close."""

    # ── Session Management ───────────────────────────────────────────────────

    async def create_session(self, session_state: SessionState) -> bool:
        """Persist a new SessionState as JSON."""
        if not self._available:
            return False

        def _write() -> bool:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO gameplay_state (session_id, state_json, updated_at)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            state_json = VALUES(state_json),
                            updated_at = VALUES(updated_at)
                        """,
                        (
                            session_state.session_id,
                            session_state.model_dump_json(),
                            datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                conn.commit()
                return True
            finally:
                conn.close()

        try:
            result: bool = await asyncio.to_thread(_write)
            logger.info("DoltGameplayManager: created session %s", session_state.session_id)
            return result
        except Exception as exc:
            logger.error("DoltGameplayManager: failed to create session: %s", exc)
            return False

    async def get_session(self, session_id: str) -> SessionState | None:
        """Retrieve a SessionState by ID, or None if not found."""
        if not self._available:
            return None

        def _read() -> str | None:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state_json FROM gameplay_state WHERE session_id = %s",
                        (session_id,),
                    )
                    row = cur.fetchone()
                    return row["state_json"] if row else None  # type: ignore[index]
            finally:
                conn.close()

        try:
            json_str: str | None = await asyncio.to_thread(_read)
            if json_str is None:
                return None
            return SessionState.model_validate_json(json_str)
        except Exception as exc:
            logger.error(
                "DoltGameplayManager: failed to get session %s: %s", session_id, exc
            )
            return None

    async def update_session(self, session_state: SessionState) -> bool:
        """Update an existing SessionState in place."""
        if not self._available:
            return False

        def _update() -> bool:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE gameplay_state
                        SET state_json = %s, updated_at = %s
                        WHERE session_id = %s
                        """,
                        (
                            session_state.model_dump_json(),
                            datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                            session_state.session_id,
                        ),
                    )
                    affected: int = cur.rowcount
                conn.commit()
                return affected > 0
            finally:
                conn.close()

        try:
            result: bool = await asyncio.to_thread(_update)
            return result
        except Exception as exc:
            logger.error(
                "DoltGameplayManager: failed to update session %s: %s",
                session_state.session_id,
                exc,
            )
            return False

    # ── Scene Management ─────────────────────────────────────────────────────

    async def create_scene(self, scene: Scene) -> bool:
        """Persist a Scene as JSON."""
        if not self._available:
            return False

        def _write() -> bool:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO gameplay_scenes
                            (scene_id, session_id, scene_json, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            scene_json = VALUES(scene_json)
                        """,
                        (
                            scene.scene_id,
                            None,  # scene is not directly tied to a session_id
                            scene.model_dump_json(),
                            datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                conn.commit()
                return True
            finally:
                conn.close()

        try:
            result: bool = await asyncio.to_thread(_write)
            return result
        except Exception as exc:
            logger.error("DoltGameplayManager: failed to create scene: %s", exc)
            return False

    async def get_scene(self, scene_id: str) -> Scene | None:
        """Retrieve a Scene by ID, or None if not found."""
        if not self._available:
            return None

        def _read() -> str | None:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT scene_json FROM gameplay_scenes WHERE scene_id = %s",
                        (scene_id,),
                    )
                    row = cur.fetchone()
                    return row["scene_json"] if row else None  # type: ignore[index]
            finally:
                conn.close()

        try:
            json_str: str | None = await asyncio.to_thread(_read)
            if json_str is None:
                return None
            return Scene.model_validate_json(json_str)
        except Exception as exc:
            logger.error(
                "DoltGameplayManager: failed to get scene %s: %s", scene_id, exc
            )
            return None

    # ── Session Summaries ────────────────────────────────────────────────────

    async def save_session_summary(
        self, session_id: str, summary: dict[str, Any]
    ) -> bool:
        """Persist a session summary dict as JSON."""
        if not self._available:
            return False

        import json as _json

        summary_json = _json.dumps(summary)

        def _write() -> bool:
            conn = self._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO gameplay_summaries
                            (session_id, summary_json, updated_at)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            summary_json = VALUES(summary_json),
                            updated_at   = VALUES(updated_at)
                        """,
                        (
                            session_id,
                            summary_json,
                            datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                conn.commit()
                return True
            finally:
                conn.close()

        try:
            result: bool = await asyncio.to_thread(_write)
            logger.info("DoltGameplayManager: saved summary for session %s", session_id)
            return result
        except Exception as exc:
            logger.warning(
                "DoltGameplayManager: failed to save session summary: %s", exc
            )
            return False
