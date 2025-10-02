"""
Enhanced Session Persistence Service with Redis Integration

This service provides comprehensive session persistence, recovery, and analytics
storage using Redis as the primary backend with intelligent caching and backup.
"""

import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class EnhancedSessionPersistence:
    """Enhanced session persistence with Redis backend and recovery mechanisms."""

    def __init__(self, redis_client: redis.Redis | None = None):
        """
        Initialize enhanced session persistence service.

        Args:
            redis_client: Redis client for persistence operations
        """
        self.redis_client = redis_client
        self.session_ttl = 86400  # 24 hours
        self.analytics_ttl = 604800  # 7 days
        self.recovery_ttl = 2592000  # 30 days

    async def save_session_state(
        self, session_id: str, session_data: dict[str, Any]
    ) -> bool:
        """
        Save session state to Redis with enhanced analytics.

        Args:
            session_id: Session identifier
            session_data: Complete session state data

        Returns:
            bool: True if saved successfully
        """
        if not self.redis_client:
            logger.warning("Redis client not available for session persistence")
            return False

        try:
            # Prepare session data for storage
            storage_data = {
                "session_data": session_data,
                "saved_at": datetime.utcnow().isoformat(),
                "version": "enhanced_v1",
            }

            # Store main session data
            session_key = f"tta:session:{session_id}"
            await self.redis_client.setex(
                session_key, self.session_ttl, json.dumps(storage_data)
            )

            # Store session analytics separately for longer retention
            if "session_analytics" in session_data:
                analytics_key = f"tta:analytics:{session_id}"
                analytics_data = {
                    "session_id": session_id,
                    "player_id": session_data.get("player_id"),
                    "analytics": session_data["session_analytics"],
                    "interaction_count": session_data.get("interaction_count", 0),
                    "emotional_themes": session_data.get("emotional_themes", []),
                    "saved_at": datetime.utcnow().isoformat(),
                }
                await self.redis_client.setex(
                    analytics_key, self.analytics_ttl, json.dumps(analytics_data)
                )

            # Store player session index
            player_id = session_data.get("player_id")
            if player_id:
                player_sessions_key = f"tta:player_sessions:{player_id}"
                await self.redis_client.sadd(player_sessions_key, session_id)
                await self.redis_client.expire(player_sessions_key, self.analytics_ttl)

            logger.info(f"Saved enhanced session state for {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session state {session_id}: {e}")
            return False

    async def load_session_state(self, session_id: str) -> dict[str, Any] | None:
        """
        Load session state from Redis.

        Args:
            session_id: Session identifier

        Returns:
            Dict containing session data or None if not found
        """
        if not self.redis_client:
            return None

        try:
            session_key = f"tta:session:{session_id}"
            stored_data = await self.redis_client.get(session_key)

            if stored_data:
                storage_data = json.loads(stored_data)
                session_data = storage_data.get("session_data", {})

                # Update last accessed time
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                await self.save_session_state(session_id, session_data)

                logger.info(f"Loaded session state for {session_id}")
                return session_data

            return None

        except Exception as e:
            logger.error(f"Failed to load session state {session_id}: {e}")
            return None

    async def save_session_recovery_data(
        self, session_id: str, recovery_data: dict[str, Any]
    ) -> bool:
        """
        Save session recovery data for potential restoration.

        Args:
            session_id: Session identifier
            recovery_data: Recovery data to store

        Returns:
            bool: True if saved successfully
        """
        if not self.redis_client:
            return False

        try:
            recovery_key = f"tta:recovery:{session_id}"
            recovery_storage = {
                "recovery_data": recovery_data,
                "saved_at": datetime.utcnow().isoformat(),
                "version": "recovery_v1",
            }

            await self.redis_client.setex(
                recovery_key, self.recovery_ttl, json.dumps(recovery_storage)
            )

            logger.info(f"Saved recovery data for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save recovery data {session_id}: {e}")
            return False

    async def get_player_session_analytics(
        self, player_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get analytics for all sessions of a player.

        Args:
            player_id: Player identifier
            limit: Maximum number of sessions to return

        Returns:
            List of session analytics
        """
        if not self.redis_client:
            return []

        try:
            # Get player's session IDs
            player_sessions_key = f"tta:player_sessions:{player_id}"
            session_ids = await self.redis_client.smembers(player_sessions_key)

            analytics_list = []
            for session_id in list(session_ids)[:limit]:
                analytics_key = f"tta:analytics:{session_id.decode()}"
                analytics_data = await self.redis_client.get(analytics_key)

                if analytics_data:
                    analytics = json.loads(analytics_data)
                    analytics_list.append(analytics)

            # Sort by saved_at timestamp (most recent first)
            analytics_list.sort(key=lambda x: x.get("saved_at", ""), reverse=True)

            return analytics_list

        except Exception as e:
            logger.error(f"Failed to get player session analytics {player_id}: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired session data and analytics.

        Returns:
            int: Number of sessions cleaned up
        """
        if not self.redis_client:
            return 0

        try:
            # Find expired session keys
            session_pattern = "tta:session:*"
            session_keys = await self.redis_client.keys(session_pattern)

            cleaned_count = 0
            for key in session_keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -1:  # No expiration set
                    await self.redis_client.expire(key, self.session_ttl)
                elif ttl == -2:  # Key doesn't exist
                    cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    async def get_session_statistics(self) -> dict[str, Any]:
        """
        Get overall session statistics.

        Returns:
            Dict containing session statistics
        """
        if not self.redis_client:
            return {"error": "Redis not available"}

        try:
            # Count active sessions
            session_keys = await self.redis_client.keys("tta:session:*")
            analytics_keys = await self.redis_client.keys("tta:analytics:*")
            recovery_keys = await self.redis_client.keys("tta:recovery:*")
            player_session_keys = await self.redis_client.keys("tta:player_sessions:*")

            return {
                "active_sessions": len(session_keys),
                "stored_analytics": len(analytics_keys),
                "recovery_data_entries": len(recovery_keys),
                "unique_players": len(player_session_keys),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {"error": str(e)}
