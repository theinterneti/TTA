"""
Redis Session Manager for Gameplay Loop

This module provides comprehensive Redis-based session management for the therapeutic
gameplay loop, including session persistence, caching strategies, and lifecycle management.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError

from src.components.gameplay_loop.services.cache_strategies import (
    CacheStrategy,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
    SessionStateManager,
)

logger = logging.getLogger(__name__)


class RedisConnectionManager:
    """Manages Redis connections with retry logic and health monitoring."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int = 0,
        max_connections: int = 20,
        retry_attempts: int = 3,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.retry_attempts = retry_attempts
        self.pool = None
        self.redis_client = None

    async def connect(self) -> bool:
        """Connect to Redis with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(
                    f"Redis connection attempt {attempt + 1}/{self.retry_attempts}"
                )

                self.pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    max_connections=self.max_connections,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )

                self.redis_client = redis.Redis(connection_pool=self.pool)

                # Test connection
                await self.redis_client.ping()

                logger.info("Successfully connected to Redis")
                return True

            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to connect to Redis after {self.retry_attempts} attempts"
                    )
                    raise e

            except Exception as e:
                logger.error(f"Unexpected error connecting to Redis: {e}")
                raise e

        return False

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

        if self.pool:
            await self.pool.disconnect()
            self.pool = None

        logger.info("Disconnected from Redis")

    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return True
            return False
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_client(self):
        """Context manager for Redis client."""
        if not self.redis_client:
            await self.connect()

        try:
            yield self.redis_client
        except Exception as e:
            logger.error(f"Redis operation failed: {e}")
            raise


class RedisSessionManager:
    """Main Redis session manager for gameplay loop."""

    def __init__(
        self,
        connection_manager: RedisConnectionManager,
        key_prefix: str = "tta:session:",
        default_ttl: timedelta = timedelta(hours=24),
    ):
        self.connection_manager = connection_manager
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.state_manager = SessionStateManager()

    def _make_key(self, session_id: str) -> str:
        """Create Redis key for session."""
        return f"{self.key_prefix}{session_id}"

    async def create_session(
        self, session_state: SessionState, ttl: timedelta | None = None
    ) -> bool:
        """Create a new session in Redis."""
        try:
            ttl = ttl or self.default_ttl
            key = self._make_key(session_state.session_id)

            # Serialize session state
            session_data = session_state.model_dump_json()

            async with self.connection_manager.get_client() as client:
                # Use SET with NX (only if not exists) and EX (expiration)
                result = await client.set(
                    key,
                    session_data,
                    nx=True,  # Only set if key doesn't exist
                    ex=int(ttl.total_seconds()),
                )

                if result:
                    logger.debug(f"Created session: {session_state.session_id}")
                    return True
                else:
                    logger.warning(
                        f"Session already exists: {session_state.session_id}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Failed to create session {session_state.session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> SessionState | None:
        """Get session from Redis."""
        try:
            key = self._make_key(session_id)

            async with self.connection_manager.get_client() as client:
                session_data = await client.get(key)

                if session_data:
                    # Deserialize session state
                    session_dict = json.loads(session_data)
                    session_state = SessionState(**session_dict)

                    # Update last activity
                    session_state.update_activity()

                    # Save updated state back to Redis
                    await self.update_session(session_state)

                    logger.debug(f"Retrieved session: {session_id}")
                    return session_state
                else:
                    logger.debug(f"Session not found: {session_id}")
                    return None

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session(
        self, session_state: SessionState, ttl: timedelta | None = None
    ) -> bool:
        """Update session in Redis."""
        try:
            ttl = ttl or self.default_ttl
            key = self._make_key(session_state.session_id)

            # Serialize session state
            session_data = session_state.model_dump_json()

            async with self.connection_manager.get_client() as client:
                # Update with new TTL
                result = await client.set(
                    key, session_data, ex=int(ttl.total_seconds())
                )

                if result:
                    session_state.clear_dirty_fields()
                    logger.debug(f"Updated session: {session_state.session_id}")
                    return True
                else:
                    logger.warning(
                        f"Failed to update session: {session_state.session_id}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Failed to update session {session_state.session_id}: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis."""
        try:
            key = self._make_key(session_id)

            async with self.connection_manager.get_client() as client:
                result = await client.delete(key)

                if result:
                    logger.debug(f"Deleted session: {session_id}")
                    return True
                else:
                    logger.warning(f"Session not found for deletion: {session_id}")
                    return False

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def extend_session_ttl(
        self, session_id: str, additional_time: timedelta
    ) -> bool:
        """Extend session TTL."""
        try:
            key = self._make_key(session_id)

            async with self.connection_manager.get_client() as client:
                # Get current TTL
                current_ttl = await client.ttl(key)

                if current_ttl > 0:
                    new_ttl = current_ttl + int(additional_time.total_seconds())
                    result = await client.expire(key, new_ttl)

                    if result:
                        logger.debug(f"Extended TTL for session: {session_id}")
                        return True

                return False

        except Exception as e:
            logger.error(f"Failed to extend TTL for session {session_id}: {e}")
            return False

    async def get_session_ttl(self, session_id: str) -> int | None:
        """Get remaining TTL for session."""
        try:
            key = self._make_key(session_id)

            async with self.connection_manager.get_client() as client:
                ttl = await client.ttl(key)
                return ttl if ttl > 0 else None

        except Exception as e:
            logger.error(f"Failed to get TTL for session {session_id}: {e}")
            return None

    async def list_user_sessions(self, user_id: str, limit: int = 10) -> list[str]:
        """List session IDs for a user."""
        try:
            pattern = f"{self.key_prefix}*"
            session_ids = []

            async with self.connection_manager.get_client() as client:
                async for key in client.scan_iter(match=pattern):
                    # Get session data to check user_id
                    session_data = await client.get(key)
                    if session_data:
                        session_dict = json.loads(session_data)
                        if session_dict.get("user_id") == user_id:
                            session_id = key.decode().replace(self.key_prefix, "")
                            session_ids.append(session_id)

                            if len(session_ids) >= limit:
                                break

            return session_ids

        except Exception as e:
            logger.error(f"Failed to list sessions for user {user_id}: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically, but useful for metrics)."""
        try:
            pattern = f"{self.key_prefix}*"
            expired_count = 0

            async with self.connection_manager.get_client() as client:
                async for key in client.scan_iter(match=pattern):
                    ttl = await client.ttl(key)
                    if ttl == -2:  # Key doesn't exist (expired)
                        expired_count += 1

            logger.debug(f"Found {expired_count} expired sessions")
            return expired_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0


class SessionCacheManager:
    """Manages session caching with different strategies."""

    def __init__(
        self, redis_manager: RedisSessionManager, cache_strategy: CacheStrategy
    ):
        self.redis_manager = redis_manager
        self.cache_strategy = cache_strategy

        # Set up persistence callback for write-back strategies
        if hasattr(cache_strategy, "set_persistence_callback"):
            cache_strategy.set_persistence_callback(self._persist_to_redis)

    async def _persist_to_redis(
        self, session_id: str, session_state: SessionState | None
    ):
        """Persist session to Redis."""
        if session_state is None:
            # Delete from Redis
            await self.redis_manager.delete_session(session_id)
        else:
            # Update in Redis
            await self.redis_manager.update_session(session_state)

    async def get_session(self, session_id: str) -> SessionState | None:
        """Get session from cache or Redis."""
        # Try cache first
        cached_session = await self.cache_strategy.get(session_id)
        if cached_session:
            return cached_session

        # Fall back to Redis
        session_state = await self.redis_manager.get_session(session_id)
        if session_state:
            # Cache for future requests
            await self.cache_strategy.set(session_id, session_state)

        return session_state

    async def set_session(
        self, session_state: SessionState, ttl: timedelta | None = None
    ) -> bool:
        """Set session in cache and Redis."""
        # Set in cache
        await self.cache_strategy.set(session_state.session_id, session_state, ttl)

        # Set in Redis (for persistence)
        return await self.redis_manager.update_session(session_state, ttl)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from cache and Redis."""
        # Delete from cache
        await self.cache_strategy.delete(session_id)

        # Delete from Redis
        return await self.redis_manager.delete_session(session_id)

    def get_cache_metrics(self):
        """Get cache performance metrics."""
        return self.cache_strategy.get_metrics()


class NarrativeContextCache:
    """Specialized cache for narrative context data."""

    def __init__(
        self,
        connection_manager: RedisConnectionManager,
        key_prefix: str = "tta:narrative:",
        default_ttl: timedelta = timedelta(hours=4),
    ):
        self.connection_manager = connection_manager
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    def _make_key(self, session_id: str, context_type: str) -> str:
        """Create Redis key for narrative context."""
        return f"{self.key_prefix}{session_id}:{context_type}"

    async def set_context(
        self,
        session_id: str,
        context_type: str,
        context_data: dict[str, Any],
        ttl: timedelta | None = None,
    ) -> bool:
        """Set narrative context data."""
        try:
            ttl = ttl or self.default_ttl
            key = self._make_key(session_id, context_type)

            # Add timestamp
            context_data["timestamp"] = datetime.utcnow().isoformat()

            async with self.connection_manager.get_client() as client:
                result = await client.set(
                    key, json.dumps(context_data), ex=int(ttl.total_seconds())
                )

                return bool(result)

        except Exception as e:
            logger.error(
                f"Failed to set narrative context {context_type} for session {session_id}: {e}"
            )
            return False

    async def get_context(
        self, session_id: str, context_type: str
    ) -> dict[str, Any] | None:
        """Get narrative context data."""
        try:
            key = self._make_key(session_id, context_type)

            async with self.connection_manager.get_client() as client:
                context_data = await client.get(key)

                if context_data:
                    return json.loads(context_data)
                return None

        except Exception as e:
            logger.error(
                f"Failed to get narrative context {context_type} for session {session_id}: {e}"
            )
            return None

    async def invalidate_context(self, session_id: str, context_type: str) -> bool:
        """Invalidate specific narrative context."""
        try:
            key = self._make_key(session_id, context_type)

            async with self.connection_manager.get_client() as client:
                result = await client.delete(key)
                return bool(result)

        except Exception as e:
            logger.error(
                f"Failed to invalidate narrative context {context_type} for session {session_id}: {e}"
            )
            return False

    async def invalidate_all_context(self, session_id: str) -> int:
        """Invalidate all narrative context for a session."""
        try:
            pattern = f"{self.key_prefix}{session_id}:*"
            deleted_count = 0

            async with self.connection_manager.get_client() as client:
                async for key in client.scan_iter(match=pattern):
                    await client.delete(key)
                    deleted_count += 1

            return deleted_count

        except Exception as e:
            logger.error(
                f"Failed to invalidate all narrative context for session {session_id}: {e}"
            )
            return 0


class ProgressCacheManager:
    """Manages caching of progress and metrics data."""

    def __init__(
        self,
        connection_manager: RedisConnectionManager,
        key_prefix: str = "tta:progress:",
        default_ttl: timedelta = timedelta(hours=12),
    ):
        self.connection_manager = connection_manager
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    def _make_key(self, user_id: str, metric_type: str) -> str:
        """Create Redis key for progress data."""
        return f"{self.key_prefix}{user_id}:{metric_type}"

    async def cache_progress_snapshot(
        self,
        user_id: str,
        progress_data: dict[str, Any],
        ttl: timedelta | None = None,
    ) -> bool:
        """Cache progress snapshot."""
        try:
            ttl = ttl or self.default_ttl
            key = self._make_key(user_id, "snapshot")

            # Add timestamp
            progress_data["cached_at"] = datetime.utcnow().isoformat()

            async with self.connection_manager.get_client() as client:
                result = await client.set(
                    key, json.dumps(progress_data), ex=int(ttl.total_seconds())
                )

                return bool(result)

        except Exception as e:
            logger.error(f"Failed to cache progress snapshot for user {user_id}: {e}")
            return False

    async def get_progress_snapshot(self, user_id: str) -> dict[str, Any] | None:
        """Get cached progress snapshot."""
        try:
            key = self._make_key(user_id, "snapshot")

            async with self.connection_manager.get_client() as client:
                progress_data = await client.get(key)

                if progress_data:
                    return json.loads(progress_data)
                return None

        except Exception as e:
            logger.error(f"Failed to get progress snapshot for user {user_id}: {e}")
            return None


class SessionLifecycleManager:
    """Manages session lifecycle events and cleanup."""

    def __init__(
        self,
        session_manager: RedisSessionManager,
        cleanup_interval: timedelta = timedelta(minutes=30),
    ):
        self.session_manager = session_manager
        self.cleanup_interval = cleanup_interval
        self._cleanup_task = None
        self._lifecycle_callbacks: dict[str, list[Callable]] = {
            "session_created": [],
            "session_updated": [],
            "session_expired": [],
            "session_deleted": [],
        }

    def register_callback(self, event_type: str, callback: Callable):
        """Register lifecycle callback."""
        if event_type in self._lifecycle_callbacks:
            self._lifecycle_callbacks[event_type].append(callback)

    async def _trigger_callbacks(self, event_type: str, session_id: str, **kwargs):
        """Trigger registered callbacks for an event."""
        for callback in self._lifecycle_callbacks.get(event_type, []):
            try:
                await callback(session_id, **kwargs)
            except Exception as e:
                logger.error(f"Error in lifecycle callback for {event_type}: {e}")

    def start_cleanup_task(self):
        """Start background cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval.total_seconds())
                    await self._cleanup_expired_sessions()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in session cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        expired_count = await self.session_manager.cleanup_expired_sessions()
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")

    async def stop_cleanup_task(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
