"""
Logseq: [[TTA.dev/Player_experience/Database/Dolt_session_store]]
Dolt-backed session store for gameplay conversation history and metadata.

Uses the MySQL-compatible Dolt SQL server for version-controlled persistence.
Provides the same public interface as SessionStore (SQLite) so callers can swap
backends without code changes.

Falls back gracefully if Dolt is unreachable — caller should catch init failure
and fall back to SessionStore.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import pymysql
import pymysql.cursors

logger = logging.getLogger(__name__)

class DoltSessionStore:
    """Dolt MySQL-compatible session store.

    Mirrors the SessionStore (SQLite) public interface so callers can treat it
    as a drop-in replacement.  All public methods are synchronous.

    Raises RuntimeError from __init__ if the Dolt server is unreachable.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        # Read defaults from env at construction time (not module import time)
        self._host = host or os.environ.get("DOLT_HOST", "127.0.0.1")
        self._port = port or int(os.environ.get("DOLT_PORT", "3306"))
        self._user = user or os.environ.get("DOLT_USER", "root")
        self._password = (
            password if password is not None else os.environ.get("DOLT_PASSWORD", "")
        )
        self._database = database or os.environ.get("DOLT_DATABASE", "tta_solo")
        # Verify connectivity (will raise if Dolt is down)
        self._ping()
        logger.info(
            "DoltSessionStore: connected to %s:%s/%s",
            self._host,
            self._port,
            self._database,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _ping(self) -> None:
        """Raise RuntimeError if Dolt server is unreachable."""
        try:
            conn = self._connect()
            conn.ping()
            conn.close()
        except Exception as exc:
            raise RuntimeError(f"Dolt unreachable: {exc}") from exc

    def _connect(self) -> pymysql.Connection:  # type: ignore[type-arg]
        return pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

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
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO player_sessions
                       (session_id, player_id, character_id, world_id,
                        character_name, world_name, status, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)""",
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
            conn.rollback()
            logger.warning("DoltSessionStore.create_session failed: %s", exc)
            raise
        finally:
            conn.close()
        return meta

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session metadata. Returns None if not found."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM player_sessions WHERE session_id = %s",
                    (session_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as exc:
            logger.warning("DoltSessionStore.get_session failed: %s", exc)
            return None
        finally:
            conn.close()

    def list_sessions(self, player_id: str) -> list[dict[str, Any]]:
        """Return all sessions for a player, most-recently-updated first."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT ps.*,
                              COUNT(pm.id) AS message_count
                       FROM player_sessions ps
                       LEFT JOIN player_messages pm ON pm.session_id = ps.session_id
                       WHERE ps.player_id = %s
                       GROUP BY ps.session_id
                       ORDER BY ps.updated_at DESC""",
                    (player_id,),
                )
                return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.warning("DoltSessionStore.list_sessions failed: %s", exc)
            return []
        finally:
            conn.close()

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
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO player_messages
                       (message_id, session_id, player_id, role, content, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (mid, session_id, player_id, role, content, ts),
                )
                cur.execute(
                    "UPDATE player_sessions SET updated_at = %s WHERE session_id = %s",
                    (ts, session_id),
                )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.warning("DoltSessionStore.save_message failed: %s", exc)
            raise
        finally:
            conn.close()
        return mid

    def load_messages(self, session_id: str) -> list[dict[str, str]]:
        """Return messages as [{role, content}] for LLM conversation context."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT role, content FROM player_messages"
                    " WHERE session_id = %s ORDER BY id ASC",
                    (session_id,),
                )
                return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.warning("DoltSessionStore.load_messages failed: %s", exc)
            return []
        finally:
            conn.close()

    def load_messages_full(self, session_id: str) -> list[dict[str, Any]]:
        """Return full message records including message_id and created_at."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT message_id, role, content, created_at
                       FROM player_messages
                       WHERE session_id = %s ORDER BY id ASC""",
                    (session_id,),
                )
                return [dict(r) for r in cur.fetchall()]
        except Exception as exc:
            logger.warning("DoltSessionStore.load_messages_full failed: %s", exc)
            return []
        finally:
            conn.close()

    def clear_messages(self, session_id: str) -> int:
        """Delete all messages for a session. Returns number of deleted rows."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM player_messages WHERE session_id = %s",
                    (session_id,),
                )
                count = cur.rowcount
                cur.execute(
                    "UPDATE player_sessions SET updated_at = %s WHERE session_id = %s",
                    (self._now(), session_id),
                )
            conn.commit()
            return count
        except Exception as exc:
            conn.rollback()
            logger.warning("DoltSessionStore.clear_messages failed: %s", exc)
            return 0
        finally:
            conn.close()

    # ── Copy Session ──────────────────────────────────────────────────────────

    def copy_session(
        self,
        source_session_id: str,
        new_session_id: str | None = None,
        player_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Duplicate a session (metadata + all messages) into a new session.

        Returns the new session metadata, or None if the source was not found.
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

        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO player_sessions
                       (session_id, player_id, character_id, world_id,
                        character_name, world_name, status, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)""",
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
                    cur.execute(
                        """INSERT INTO player_messages
                           (message_id, session_id, player_id, role, content, created_at)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            str(uuid.uuid4()),
                            new_id,
                            owner,
                            msg["role"],
                            msg["content"],
                            msg.get("created_at", now),
                        ),
                    )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.warning("DoltSessionStore.copy_session failed: %s", exc)
            raise
        finally:
            conn.close()

        return new_meta
