"""
Mock Redis Cache for Testing

This module provides a simple mock implementation of Redis cache
for testing purposes when Redis is not available.
"""

import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Mock Redis cache implementation for testing."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize mock Redis cache."""
        self._cache = {}
        self.host = host
        self.port = port
        self.db = db
        logger.info("Mock Redis cache initialized")

    def get(self, key: str) -> str | None:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set value in cache."""
        self._cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def clear(self) -> bool:
        """Clear all cache entries."""
        self._cache.clear()
        return True

    def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern."""
        if pattern == "*":
            return list(self._cache.keys())
        # Simple pattern matching for testing
        return [key for key in self._cache.keys() if pattern.replace("*", "") in key]

    def connect(self) -> bool:
        """Mock connection method."""
        return True

    def disconnect(self) -> None:
        """Mock disconnection method."""
        pass

    def ping(self) -> bool:
        """Mock ping method."""
        return True
