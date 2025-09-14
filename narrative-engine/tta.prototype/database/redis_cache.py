"""
Redis Caching Layer for TTA Prototype Session Management

This module provides Redis connection management, session caching utilities,
and cache invalidation mechanisms for the therapeutic text adventure system.

Classes:
    RedisConnectionManager: Manages Redis connections and configuration
    SessionCacheManager: Handles session state caching and retrieval
    CacheInvalidationManager: Manages cache cleanup and invalidation
"""

import logging
from datetime import datetime
from typing import Any

try:
    import redis
    from redis.exceptions import ConnectionError, RedisError, TimeoutError

    REDIS_AVAILABLE = True
except ImportError:
    print("Warning: redis package not installed. Install with: pip install redis")
    redis = None
    ConnectionError = Exception
    TimeoutError = Exception
    RedisError = Exception
    REDIS_AVAILABLE = False

# Import data models
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

try:
    from data_models import (
        CharacterState,
        EmotionalState,
        NarrativeContext,
        SessionState,
    )
except ImportError:
    # Fallback for different import contexts
    SessionState = None
    CharacterState = None
    EmotionalState = None
    NarrativeContext = None

logger = logging.getLogger(__name__)


class RedisCacheError(Exception):
    """Raised when Redis cache operations fail."""

    pass


class RedisConnectionManager:
    """
    Manages Redis connections and configuration for therapeutic text adventure.

    This class handles Redis connection pooling, configuration management,
    connection health monitoring, and automatic reconnection capabilities.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        max_connections: int = 50,
        decode_responses: bool = True,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30,
    ):
        """
        Initialize Redis connection manager with enhanced configuration.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Socket connection timeout in seconds
            max_connections: Maximum connections in pool
            decode_responses: Whether to decode responses to strings
            retry_on_timeout: Whether to retry operations on timeout
            health_check_interval: Health check interval in seconds
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required. Install with: pip install redis"
            )

        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.retry_on_timeout = retry_on_timeout
        self.health_check_interval = health_check_interval

        self._connection_pool: redis.ConnectionPool | None = None
        self._redis_client: redis.Redis | None = None
        self._last_health_check: datetime | None = None
        self._connection_failures = 0
        self._max_connection_failures = 3

        # Enhanced cache configuration with different TTLs for different data types
        self.default_ttl = 3600  # 1 hour default TTL
        self.session_ttl = 86400  # 24 hours for sessions
        self.character_ttl = 7200  # 2 hours for character states
        self.narrative_ttl = 1800  # 30 minutes for narrative context
        self.emotional_ttl = 3600  # 1 hour for emotional states
        self.therapeutic_ttl = 604800  # 1 week for therapeutic progress
        self.user_preferences_ttl = 2592000  # 30 days for user preferences

    def connect(self) -> None:
        """Establish connection to Redis server."""
        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                max_connections=self.max_connections,
                decode_responses=self.decode_responses,
            )

            # Create Redis client
            self._redis_client = redis.Redis(connection_pool=self._connection_pool)

            # Test connection
            self._redis_client.ping()

            logger.info(f"Connected to Redis at {self.host}:{self.port}")

        except ConnectionError as e:
            raise RedisCacheError(f"Failed to connect to Redis: {e}") from e
        except Exception as e:
            raise RedisCacheError(f"Unexpected error connecting to Redis: {e}") from e

    def disconnect(self) -> None:
        """Close connection to Redis server."""
        if self._connection_pool:
            self._connection_pool.disconnect()
            self._connection_pool = None

        if self._redis_client:
            self._redis_client = None

        logger.info("Disconnected from Redis")

    def get_client(self) -> redis.Redis:
        """
        Get Redis client instance.

        Returns:
            redis.Redis: Redis client instance

        Raises:
            RedisCacheError: If not connected to Redis
        """
        if not self._redis_client:
            raise RedisCacheError("Not connected to Redis. Call connect() first.")
        return self._redis_client

    def is_connected(self) -> bool:
        """
        Check if connected to Redis with health monitoring.

        Returns:
            bool: True if connected and responsive
        """
        if not self._redis_client:
            return False

        try:
            # Perform health check if interval has passed
            now = datetime.now()
            if (
                self._last_health_check is None
                or (now - self._last_health_check).seconds >= self.health_check_interval
            ):

                self._redis_client.ping()
                self._last_health_check = now
                self._connection_failures = 0  # Reset failure count on successful ping
                return True

            # If within health check interval, assume connected
            return True

        except Exception as e:
            self._connection_failures += 1
            logger.warning(
                f"Redis health check failed (attempt {self._connection_failures}): {e}"
            )

            # Attempt reconnection if failures exceed threshold
            if self._connection_failures >= self._max_connection_failures:
                logger.info("Attempting Redis reconnection due to repeated failures")
                try:
                    self.reconnect()
                    return True
                except Exception as reconnect_error:
                    logger.error(f"Redis reconnection failed: {reconnect_error}")

            return False

    def reconnect(self) -> None:
        """Attempt to reconnect to Redis server."""
        try:
            logger.info("Reconnecting to Redis...")
            self.disconnect()
            self.connect()
            logger.info("Redis reconnection successful")
        except Exception as e:
            logger.error(f"Redis reconnection failed: {e}")
            raise RedisCacheError(f"Failed to reconnect to Redis: {e}") from e

    def get_connection_stats(self) -> dict[str, Any]:
        """
        Get detailed connection statistics.

        Returns:
            Dict[str, Any]: Connection statistics and health metrics
        """
        stats = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "connected": self.is_connected(),
            "max_connections": self.max_connections,
            "connection_failures": self._connection_failures,
            "last_health_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "ttl_config": {
                "default": self.default_ttl,
                "session": self.session_ttl,
                "character": self.character_ttl,
                "narrative": self.narrative_ttl,
                "emotional": self.emotional_ttl,
                "therapeutic": self.therapeutic_ttl,
                "user_preferences": self.user_preferences_ttl,
            },
        }

        # Add Redis server info if connected
        if self.is_connected():
            try:
                redis_info = self._redis_client.info()
                stats.update(
                    {
                        "redis_version": redis_info.get("redis_version", "unknown"),
                        "used_memory": redis_info.get("used_memory", 0),
                        "connected_clients": redis_info.get("connected_clients", 0),
                        "total_commands_processed": redis_info.get(
                            "total_commands_processed", 0
                        ),
                        "keyspace_hits": redis_info.get("keyspace_hits", 0),
                        "keyspace_misses": redis_info.get("keyspace_misses", 0),
                    }
                )
            except Exception as e:
                logger.warning(f"Could not retrieve Redis server info: {e}")

        return stats


# Duplicate method removed - using the more comprehensive version above


# TODO: Implement per redis-cache-enhanced.kiro specification
# This is a minimal prototype implementation. Production systems should use
# the enhanced Redis cache implementation in src/components/gameplay_loop/services/redis_manager.py

# Export main classes
__all__ = [
    "RedisCacheError",
    "RedisConnectionManager",
]
