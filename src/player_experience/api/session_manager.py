"""

# Logseq: [[TTA.dev/Player_experience/Api/Session_manager]]
Redis-backed session manager for OpenRouter OAuth.

Replaces in-memory session storage with persistent Redis storage
for production-ready session management.
"""

from __future__ import annotations

import json
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """User session data structure."""

    session_id: str
    user_data: dict[str, Any]
    auth_method: str  # "oauth" or "api_key"
    encrypted_api_key: str | None
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        return {
            "session_id": self.session_id,
            "user_data": self.user_data,
            "auth_method": self.auth_method,
            "encrypted_api_key": self.encrypted_api_key,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionData:
        """Create from dictionary retrieved from Redis."""
        return cls(
            session_id=data["session_id"],
            user_data=data["user_data"],
            auth_method=data["auth_method"],
            encrypted_api_key=data.get("encrypted_api_key"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )


@dataclass
class OAuthState:
    """OAuth state data structure."""

    state: str
    code_verifier: str
    created_at: datetime
    expires_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        return {
            "state": self.state,
            "code_verifier": self.code_verifier,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OAuthState:
        """Create from dictionary retrieved from Redis."""
        return cls(
            state=data["state"],
            code_verifier=data["code_verifier"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )


class RedisSessionManager:
    """
    Redis-backed session manager for OpenRouter OAuth.

    Provides persistent session storage with automatic expiry,
    replacing in-memory dictionaries for production use.
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        session_ttl_seconds: int = 86400,  # 24 hours
        oauth_state_ttl_seconds: int = 600,  # 10 minutes
        key_prefix: str = "openrouter",
    ):
        """
        Initialize Redis session manager.

        Args:
            redis_client: Async Redis client instance
            session_ttl_seconds: Session expiry time (default: 24 hours)
            oauth_state_ttl_seconds: OAuth state expiry time (default: 10 minutes)
            key_prefix: Redis key prefix for namespacing
        """
        self.redis = redis_client
        self.session_ttl = session_ttl_seconds
        self.oauth_state_ttl = oauth_state_ttl_seconds
        self.prefix = key_prefix

    # ---- Key Management ----

    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"{self.prefix}:session:{session_id}"

    def _oauth_state_key(self, state: str) -> str:
        """Generate Redis key for OAuth state."""
        return f"{self.prefix}:oauth_state:{state}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Generate Redis key for user's session list."""
        return f"{self.prefix}:user_sessions:{user_id}"

    # ---- Session Management ----

    async def create_session(
        self,
        user_data: dict[str, Any],
        auth_method: str,
        encrypted_api_key: str | None = None,
    ) -> str:
        """
        Create a new user session.

        Args:
            user_data: User information from OAuth or API key validation
            auth_method: "oauth" or "api_key"
            encrypted_api_key: Encrypted API key (if using API key auth)

        Returns:
            session_id: Unique session identifier
        """
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()

        session = SessionData(
            session_id=session_id,
            user_data=user_data,
            auth_method=auth_method,
            encrypted_api_key=encrypted_api_key,
            created_at=now,
            last_accessed=now,
            expires_at=now + timedelta(seconds=self.session_ttl),
        )

        # Store session in Redis
        key = self._session_key(session_id)
        await self.redis.setex(
            key, self.session_ttl, json.dumps(session.to_dict(), default=str)
        )

        # Track session for user
        user_id = user_data.get("id", "unknown")
        await self.redis.sadd(self._user_sessions_key(user_id), session_id)  # type: ignore[misc]

        logger.info(
            f"Created session {session_id} for user {user_id} via {auth_method}"
        )
        return session_id

    async def get_session(self, session_id: str) -> SessionData | None:
        """
        Retrieve session data.

        Args:
            session_id: Session identifier

        Returns:
            SessionData if found and valid, None otherwise
        """
        key = self._session_key(session_id)
        data = await self.redis.get(key)

        if not data:
            return None

        try:
            session_dict = json.loads(data)
            session = SessionData.from_dict(session_dict)

            # Check expiry
            if datetime.utcnow() > session.expires_at:
                await self.delete_session(session_id)
                return None

            # Update last accessed time
            session.last_accessed = datetime.utcnow()
            await self.redis.setex(
                key, self.session_ttl, json.dumps(session.to_dict(), default=str)
            )

            return session

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse session {session_id}: {e}")
            await self.delete_session(session_id)
            return None

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        # Get session to find user_id for cleanup
        session = await self.get_session(session_id)
        if session:
            user_id = session.user_data.get("id", "unknown")
            await self.redis.srem(self._user_sessions_key(user_id), session_id)  # type: ignore[misc]

        # Delete session
        key = self._session_key(session_id)
        result = await self.redis.delete(key)

        logger.info(f"Deleted session {session_id}")
        return result > 0

    async def get_user_sessions(self, user_id: str) -> list[str]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of session IDs
        """
        key = self._user_sessions_key(user_id)
        session_ids = await self.redis.smembers(key)  # type: ignore[misc]
        return [sid.decode() if isinstance(sid, bytes) else sid for sid in session_ids]

    async def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of sessions deleted
        """
        session_ids = await self.get_user_sessions(user_id)
        count = 0
        for session_id in session_ids:
            if await self.delete_session(session_id):
                count += 1
        return count

    # ---- OAuth State Management ----

    async def store_oauth_state(self, code_verifier: str) -> str:
        """
        Store OAuth state for PKCE flow.

        Args:
            code_verifier: PKCE code verifier

        Returns:
            state: Unique state identifier
        """
        state = secrets.token_urlsafe(32)
        now = datetime.utcnow()

        oauth_state = OAuthState(
            state=state,
            code_verifier=code_verifier,
            created_at=now,
            expires_at=now + timedelta(seconds=self.oauth_state_ttl),
        )

        key = self._oauth_state_key(state)
        await self.redis.setex(
            key, self.oauth_state_ttl, json.dumps(oauth_state.to_dict(), default=str)
        )

        logger.debug(f"Stored OAuth state {state}")
        return state

    async def get_oauth_state(self, state: str) -> OAuthState | None:
        """
        Retrieve OAuth state.

        Args:
            state: State identifier

        Returns:
            OAuthState if found and valid, None otherwise
        """
        key = self._oauth_state_key(state)
        data = await self.redis.get(key)

        if not data:
            return None

        try:
            state_dict = json.loads(data)
            oauth_state = OAuthState.from_dict(state_dict)

            # Check expiry
            if datetime.utcnow() > oauth_state.expires_at:
                await self.delete_oauth_state(state)
                return None

            return oauth_state

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse OAuth state {state}: {e}")
            await self.delete_oauth_state(state)
            return None

    async def delete_oauth_state(self, state: str) -> bool:
        """
        Delete OAuth state (after successful callback).

        Args:
            state: State identifier

        Returns:
            True if state was deleted, False if not found
        """
        key = self._oauth_state_key(state)
        result = await self.redis.delete(key)
        logger.debug(f"Deleted OAuth state {state}")
        return result > 0

    # ---- Cleanup ----

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (Redis TTL handles this automatically).

        This method is provided for manual cleanup if needed.

        Returns:
            Number of sessions cleaned up
        """
        # Redis TTL handles automatic expiry, but we can scan for orphaned entries
        pattern = f"{self.prefix}:session:*"
        count = 0

        async for key in self.redis.scan_iter(match=pattern, count=100):
            ttl = await self.redis.ttl(key)
            if ttl == -1:  # No expiry set (shouldn't happen)
                await self.redis.expire(key, self.session_ttl)
                count += 1

        if count > 0:
            logger.info(f"Fixed {count} sessions without TTL")

        return count
