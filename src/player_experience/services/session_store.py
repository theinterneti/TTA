"""
Logseq: [[TTA.dev/Player_experience/Services/Session_store]]
SQLite-backed session store for gameplay conversation history and metadata.

Provides full persistence (save/load/copy/clear) across server restarts
without requiring Redis or Neo4j. Can be swapped for a Redis/Postgres
backend in issue #63 with no interface changes.

Falls back to an in-memory store if SQLite is unavailable (e.g. read-only FS).
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = Path.home() / ".tta" / "sessions.db"

_SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS session_metadata (
    session_id     TEXT PRIMARY KEY,
    player_id      TEXT NOT NULL,
    character_id   TEXT,
    world_id       TEXT,
    character_name TEXT,
    world_name     TEXT,
    status         TEXT NOT NULL DEFAULT 'active',
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES session_metadata(session_id) ON DELETE CASCADE,
    message_id  TEXT NOT NULL UNIQUE,
    player_id   TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_msgs_session ON session_messages(session_id, id);
CREATE INDEX IF NOT EXISTS idx_meta_player  ON session_metadata(player_id);
"""


class SessionStore:
    """SQLite-backed store for session metadata and conversation messages.

    All public methods are synchronous and safe to call from async handlers
    via the default event loop (SQLite operations are fast enough for MVP).
    Falls back to an in-memory dict when SQLite is unavailable.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = str(db_path or _DEFAULT_DB_PATH)
        self._available = self._init_db()
        # In-memory fallback mirrors written when SQLite unavailable
        self._mem_meta: dict[str, dict[str, Any]] = {}
        self._mem_msgs: dict[str, list[dict[str, Any]]] = {}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _init_db(self) -> bool:
        try:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self._db_path, check_same_thread=False) as conn:
                conn.executescript(_SCHEMA)
            logger.info("SessionStore: SQLite at %s", self._db_path)
            return True
        except Exception as exc:
            logger.warning(
                "SessionStore: SQLite unavailable (%s); using in-memory fallback", exc
            )
            return False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    # ── Session Metadata ──────────────────────────────────────────────────────

    def create_session(
        self,
        session_id: str,
        player_id: str,
        character_id: str | None = None,
        world_id: str | None = None,
        character_name: str | None = None,
        world_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a new session record. Returns the metadata dict."""
        now = self._now()
        meta: dict[str, Any] = {
            "session_id": session_id,
            "player_id": player_id,
            "character_id": character_id,
            "world_id": world_id,
            "character_name": character_name,
            "world_name": world_name,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        if self._available:
            try:
                with self._connect() as conn:
                    conn.execute(
                        """INSERT INTO session_metadata
                           (session_id, player_id, character_id, world_id,
                            character_name, world_name, status, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
                        (
                            session_id,
                            player_id,
                            character_id,
                            world_id,
                            character_name,
                            world_name,
                            now,
                            now,
                        ),
                    )
                    conn.commit()
            except Exception as exc:
                logger.warning("create_session write failed: %s", exc)
        self._mem_meta[session_id] = meta
        return meta

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session metadata. Returns None if not found."""
        if self._available:
            try:
                with self._connect() as conn:
                    row = conn.execute(
                        "SELECT * FROM session_metadata WHERE session_id = ?",
                        (session_id,),
                    ).fetchone()
                    if row:
                        return dict(row)
            except Exception as exc:
                logger.warning("get_session read failed: %s", exc)
        return self._mem_meta.get(session_id)

    def list_sessions(self, player_id: str) -> list[dict[str, Any]]:
        """Return all sessions for a player, most-recently-updated first."""
        if self._available:
            try:
                with self._connect() as conn:
                    rows = conn.execute(
                        """SELECT m.*,
                                  COUNT(msg.id) AS message_count
                           FROM session_metadata m
                           LEFT JOIN session_messages msg ON msg.session_id = m.session_id
                           WHERE m.player_id = ?
                           GROUP BY m.session_id
                           ORDER BY m.updated_at DESC""",
                        (player_id,),
                    ).fetchall()
                    return [dict(r) for r in rows]
            except Exception as exc:
                logger.warning("list_sessions failed: %s", exc)
        return [s for s in self._mem_meta.values() if s["player_id"] == player_id]

    def _touch_session(self, session_id: str) -> None:
        """Update the updated_at timestamp for a session."""
        now = self._now()
        if self._available:
            try:
                with self._connect() as conn:
                    conn.execute(
                        "UPDATE session_metadata SET updated_at = ? WHERE session_id = ?",
                        (now, session_id),
                    )
                    conn.commit()
            except Exception as exc:
                logger.warning("_touch_session failed: %s", exc)
        if session_id in self._mem_meta:
            self._mem_meta[session_id]["updated_at"] = now

    # ── Message Persistence ───────────────────────────────────────────────────

    def save_message(
        self,
        session_id: str,
        player_id: str,
        role: str,
        content: str,
        message_id: str | None = None,
        created_at: str | None = None,
    ) -> str:
        """Persist a single message. Returns the message_id used."""
        mid = message_id or str(uuid.uuid4())
        ts = created_at or self._now()
        record: dict[str, Any] = {
            "message_id": mid,
            "role": role,
            "content": content,
            "created_at": ts,
        }
        if self._available:
            try:
                with self._connect() as conn:
                    conn.execute(
                        """INSERT INTO session_messages
                           (session_id, message_id, player_id, role, content, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (session_id, mid, player_id, role, content, ts),
                    )
                    conn.execute(
                        "UPDATE session_metadata SET updated_at = ? WHERE session_id = ?",
                        (ts, session_id),
                    )
                    conn.commit()
            except Exception as exc:
                logger.warning("save_message failed: %s", exc)
        self._mem_msgs.setdefault(session_id, []).append(record)
        return mid

    def load_messages(self, session_id: str) -> list[dict[str, str]]:
        """Return messages as [{role, content}] for LLM conversation context."""
        if self._available:
            try:
                with self._connect() as conn:
                    rows = conn.execute(
                        "SELECT role, content FROM session_messages"
                        " WHERE session_id = ? ORDER BY id ASC",
                        (session_id,),
                    ).fetchall()
                    return [dict(r) for r in rows]
            except Exception as exc:
                logger.warning("load_messages failed: %s", exc)
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self._mem_msgs.get(session_id, [])
        ]

    def load_messages_full(self, session_id: str) -> list[dict[str, Any]]:
        """Return full message records including message_id and created_at."""
        if self._available:
            try:
                with self._connect() as conn:
                    rows = conn.execute(
                        """SELECT message_id, role, content, created_at
                           FROM session_messages
                           WHERE session_id = ? ORDER BY id ASC""",
                        (session_id,),
                    ).fetchall()
                    return [dict(r) for r in rows]
            except Exception as exc:
                logger.warning("load_messages_full failed: %s", exc)
        return list(self._mem_msgs.get(session_id, []))

    def clear_messages(self, session_id: str) -> int:
        """Delete all messages for a session. Returns number of deleted rows."""
        count = 0
        if self._available:
            try:
                with self._connect() as conn:
                    cur = conn.execute(
                        "DELETE FROM session_messages WHERE session_id = ?",
                        (session_id,),
                    )
                    count = cur.rowcount
                    conn.execute(
                        "UPDATE session_metadata SET updated_at = ? WHERE session_id = ?",
                        (self._now(), session_id),
                    )
                    conn.commit()
            except Exception as exc:
                logger.warning("clear_messages failed: %s", exc)
        mem_count = len(self._mem_msgs.pop(session_id, []))
        return count if count else mem_count

    # ── Copy Session ──────────────────────────────────────────────────────────

    def copy_session(
        self,
        source_session_id: str,
        new_session_id: str | None = None,
        player_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Duplicate a session (metadata + all messages) into a new session.

        Returns the new session metadata, or None if the source was not found.
        The copy is independent — changes to either session don't affect the other.
        """
        source_meta = self.get_session(source_session_id)
        if source_meta is None:
            return None

        new_id = new_session_id or str(uuid.uuid4())
        now = self._now()
        owner = player_id or source_meta["player_id"]

        new_meta: dict[str, Any] = {
            **source_meta,
            "session_id": new_id,
            "player_id": owner,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }

        source_messages = self.load_messages_full(source_session_id)

        if self._available:
            try:
                with self._connect() as conn:
                    conn.execute(
                        """INSERT INTO session_metadata
                           (session_id, player_id, character_id, world_id,
                            character_name, world_name, status, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
                        (
                            new_id,
                            owner,
                            new_meta.get("character_id"),
                            new_meta.get("world_id"),
                            new_meta.get("character_name"),
                            new_meta.get("world_name"),
                            now,
                            now,
                        ),
                    )
                    for msg in source_messages:
                        conn.execute(
                            """INSERT INTO session_messages
                               (session_id, message_id, player_id, role, content, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (
                                new_id,
                                str(uuid.uuid4()),
                                owner,
                                msg["role"],
                                msg["content"],
                                msg.get("created_at", now),
                            ),
                        )
                    conn.commit()
            except Exception as exc:
                logger.warning("copy_session failed: %s", exc)

        self._mem_meta[new_id] = new_meta
        self._mem_msgs[new_id] = [
            {"role": m["role"], "content": m["content"], "message_id": str(uuid.uuid4()), "created_at": m.get("created_at", now)}
            for m in source_messages
        ]
        return new_meta
