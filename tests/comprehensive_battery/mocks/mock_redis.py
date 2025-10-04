"""
Mock Redis client implementation.

Provides mock Redis operations without requiring an actual Redis instance.
"""

import asyncio
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class MockRedisClient:
    """Mock Redis client."""

    def __init__(self, url: str = "redis://localhost:6379", **kwargs):
        self.url = url
        self._data: dict[str, Any] = {}
        self._expires: dict[str, float] = {}
        self._closed = False
        self._connection_count = 0

        logger.info(f"Mock Redis client initialized for {url}")

    async def ping(self) -> bool:
        """Ping the Redis server."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        await asyncio.sleep(0.01)  # Simulate network delay
        logger.debug("Mock Redis ping successful")
        return True

    async def set(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Set a key-value pair."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        # Convert value to string (like real Redis)
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        else:
            value = str(value)

        self._data[key] = value

        # Set expiration if provided
        if ex:
            self._expires[key] = time.time() + ex

        logger.debug(f"Mock Redis SET: {key} = {value[:50]}...")
        return True

    async def get(self, key: str) -> str | None:
        """Get a value by key."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        # Check if key has expired
        if key in self._expires and time.time() > self._expires[key]:
            del self._data[key]
            del self._expires[key]
            return None

        value = self._data.get(key)
        logger.debug(f"Mock Redis GET: {key} = {value[:50] if value else None}...")
        return value

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        deleted_count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                deleted_count += 1
            if key in self._expires:
                del self._expires[key]

        logger.debug(f"Mock Redis DELETE: {keys} (deleted {deleted_count})")
        return deleted_count

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        # Check expiration
        if key in self._expires and time.time() > self._expires[key]:
            del self._data[key]
            del self._expires[key]
            return False

        exists = key in self._data
        logger.debug(f"Mock Redis EXISTS: {key} = {exists}")
        return exists

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get all keys matching pattern."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        # Simple pattern matching (just * for now)
        if pattern == "*":
            # Remove expired keys first
            current_time = time.time()
            expired_keys = [
                key
                for key, exp_time in self._expires.items()
                if current_time > exp_time
            ]
            for key in expired_keys:
                self._data.pop(key, None)
                self._expires.pop(key, None)

            keys = list(self._data.keys())
        else:
            # Basic pattern matching
            keys = [key for key in self._data.keys() if pattern.replace("*", "") in key]

        logger.debug(f"Mock Redis KEYS: {pattern} = {len(keys)} keys")
        return keys

    async def flushdb(self) -> bool:
        """Flush all keys in current database."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        count = len(self._data)
        self._data.clear()
        self._expires.clear()

        logger.debug(f"Mock Redis FLUSHDB: cleared {count} keys")
        return True

    async def hset(self, name: str, mapping: dict[str, Any]) -> int:
        """Set hash fields."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if name not in self._data:
            self._data[name] = {}

        if not isinstance(self._data[name], dict):
            self._data[name] = {}

        # Convert values to strings
        for key, value in mapping.items():
            if isinstance(value, (dict, list)):
                self._data[name][key] = json.dumps(value)
            else:
                self._data[name][key] = str(value)

        logger.debug(f"Mock Redis HSET: {name} with {len(mapping)} fields")
        return len(mapping)

    async def hget(self, name: str, key: str) -> str | None:
        """Get hash field value."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if name not in self._data or not isinstance(self._data[name], dict):
            return None

        value = self._data[name].get(key)
        logger.debug(f"Mock Redis HGET: {name}.{key} = {value}")
        return value

    async def hgetall(self, name: str) -> dict[str, str]:
        """Get all hash fields."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if name not in self._data or not isinstance(self._data[name], dict):
            return {}

        result = self._data[name].copy()
        logger.debug(f"Mock Redis HGETALL: {name} = {len(result)} fields")
        return result

    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to list (left side)."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if name not in self._data:
            self._data[name] = []

        if not isinstance(self._data[name], list):
            self._data[name] = []

        # Convert values to strings and prepend
        for value in reversed(values):
            if isinstance(value, (dict, list)):
                self._data[name].insert(0, json.dumps(value))
            else:
                self._data[name].insert(0, str(value))

        length = len(self._data[name])
        logger.debug(f"Mock Redis LPUSH: {name} (new length: {length})")
        return length

    async def lrange(self, name: str, start: int, end: int) -> list[str]:
        """Get list range."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if name not in self._data or not isinstance(self._data[name], list):
            return []

        # Handle negative indices
        if end == -1:
            result = self._data[name][start:]
        else:
            result = self._data[name][start : end + 1]

        logger.debug(f"Mock Redis LRANGE: {name}[{start}:{end}] = {len(result)} items")
        return result

    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if key not in self._data:
            return False

        self._expires[key] = time.time() + seconds
        logger.debug(f"Mock Redis EXPIRE: {key} in {seconds}s")
        return True

    async def ttl(self, key: str) -> int:
        """Get key time to live."""
        if self._closed:
            raise ConnectionError("Redis client is closed")

        if key not in self._data:
            return -2  # Key doesn't exist

        if key not in self._expires:
            return -1  # Key exists but no expiration

        ttl = int(self._expires[key] - time.time())
        return max(0, ttl)

    async def close(self):
        """Close the Redis connection."""
        self._closed = True
        logger.info("Mock Redis client closed")

    async def aclose(self):
        """Async close (for compatibility)."""
        await self.close()

    @classmethod
    def from_url(cls, url: str, **kwargs) -> "MockRedisClient":
        """Create client from URL."""
        return cls(url=url, **kwargs)


def create_mock_redis_client(
    url: str = "redis://localhost:6379", **kwargs
) -> MockRedisClient:
    """Create a mock Redis client."""
    return MockRedisClient(url=url, **kwargs)
