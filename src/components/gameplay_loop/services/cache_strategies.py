"""
Cache Strategies for Session Management

This module defines various caching strategies for session state management,
including TTL, LRU, write-back, and write-through strategies.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CacheEventType(str, Enum):
    """Types of cache events."""

    HIT = "hit"
    MISS = "miss"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    EVICT = "evict"
    FLUSH = "flush"


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    expirations: int = 0
    total_requests: int = 0

    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate()


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    expires_at: datetime | None = None
    size_bytes: int = 0
    dirty: bool = False

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def touch(self) -> None:
        """Update access metadata."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1

    def age(self) -> timedelta:
        """Get entry age."""
        return datetime.utcnow() - self.created_at

    def idle_time(self) -> timedelta:
        """Get time since last access."""
        return datetime.utcnow() - self.last_accessed


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""

    def __init__(self, max_size: int = 1000, default_ttl: timedelta | None = None):
        self.max_size = max_size
        self.default_ttl = default_ttl or timedelta(hours=2)
        self.cache: dict[str, CacheEntry] = {}
        self.metrics = CacheMetrics()
        self._lock = asyncio.Lock()

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def evict_if_needed(self) -> None:
        """Evict entries if cache is full."""
        pass

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        async with self._lock:
            return key in self.cache and not self.cache[key].is_expired()

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            self.metrics = CacheMetrics()

    async def size(self) -> int:
        """Get current cache size."""
        async with self._lock:
            return len(self.cache)

    async def cleanup_expired(self) -> int:
        """Remove expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                del self.cache[key]
                self.metrics.expirations += 1

            return len(expired_keys)

    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics."""
        return self.metrics


class TTLCacheStrategy(CacheStrategy):
    """Time-To-Live cache strategy with automatic expiration."""

    def __init__(
        self, max_size: int = 1000, default_ttl: timedelta = timedelta(hours=2)
    ):
        super().__init__(max_size, default_ttl)
        self._cleanup_task = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Cleanup every 5 minutes
                    await self.cleanup_expired()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in TTL cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def get(self, key: str) -> Any | None:
        """Get value from cache with TTL check."""
        async with self._lock:
            self.metrics.total_requests += 1

            if key not in self.cache:
                self.metrics.misses += 1
                return None

            entry = self.cache[key]

            if entry.is_expired():
                del self.cache[key]
                self.metrics.misses += 1
                self.metrics.expirations += 1
                return None

            entry.touch()
            self.metrics.hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache with TTL."""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = datetime.utcnow() + ttl if ttl else None

            # Evict if needed
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_oldest()

            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                size_bytes=self._estimate_size(value),
            )

            self.cache[key] = entry
            self.metrics.sets += 1
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self.metrics.deletes += 1
                return True
            return False

    async def evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        async with self._lock:
            while len(self.cache) >= self.max_size:
                await self._evict_oldest()

    async def _evict_oldest(self) -> None:
        """Evict the oldest entry."""
        if not self.cache:
            return

        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        del self.cache[oldest_key]
        self.metrics.evictions += 1

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return len(str(value).encode("utf-8"))
        else:
            return len(str(value).encode("utf-8"))

    async def close(self):
        """Close the cache and cleanup tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


class LRUCacheStrategy(CacheStrategy):
    """Least Recently Used cache strategy."""

    def __init__(self, max_size: int = 1000, default_ttl: timedelta | None = None):
        super().__init__(max_size, default_ttl)
        self._access_order: list[str] = []

    async def get(self, key: str) -> Any | None:
        """Get value from cache and update LRU order."""
        async with self._lock:
            self.metrics.total_requests += 1

            if key not in self.cache:
                self.metrics.misses += 1
                return None

            entry = self.cache[key]

            if entry.is_expired():
                del self.cache[key]
                self._access_order.remove(key)
                self.metrics.misses += 1
                self.metrics.expirations += 1
                return None

            # Update LRU order
            self._access_order.remove(key)
            self._access_order.append(key)

            entry.touch()
            self.metrics.hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache with LRU tracking."""
        async with self._lock:
            expires_at = None
            if ttl or self.default_ttl:
                ttl = ttl or self.default_ttl
                expires_at = datetime.utcnow() + ttl

            # Evict if needed
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_lru()

            # Remove from old position if exists
            if key in self._access_order:
                self._access_order.remove(key)

            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                size_bytes=self._estimate_size(value),
            )

            self.cache[key] = entry
            self._access_order.append(key)
            self.metrics.sets += 1
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self._access_order.remove(key)
                self.metrics.deletes += 1
                return True
            return False

    async def evict_if_needed(self) -> None:
        """Evict LRU entries if cache is full."""
        async with self._lock:
            while len(self.cache) >= self.max_size:
                await self._evict_lru()

    async def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._access_order:
            return

        lru_key = self._access_order.pop(0)
        if lru_key in self.cache:
            del self.cache[lru_key]
            self.metrics.evictions += 1

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return len(str(value).encode("utf-8"))
        else:
            return len(str(value).encode("utf-8"))


class WriteBackCacheStrategy(CacheStrategy):
    """Write-back cache strategy with delayed persistence."""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: timedelta | None = None,
        write_back_interval: timedelta = timedelta(seconds=30),
    ):
        super().__init__(max_size, default_ttl)
        self.write_back_interval = write_back_interval
        self._dirty_keys: set[str] = set()
        self._write_back_task = None
        self._persistence_callback = None
        self._start_write_back_task()

    def set_persistence_callback(self, callback):
        """Set callback for persistence operations."""
        self._persistence_callback = callback

    def _start_write_back_task(self):
        """Start background write-back task."""

        async def write_back_loop():
            while True:
                try:
                    await asyncio.sleep(self.write_back_interval.total_seconds())
                    await self._flush_dirty_entries()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in write-back task: {e}")

        self._write_back_task = asyncio.create_task(write_back_loop())

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            self.metrics.total_requests += 1

            if key not in self.cache:
                self.metrics.misses += 1
                return None

            entry = self.cache[key]

            if entry.is_expired():
                del self.cache[key]
                self._dirty_keys.discard(key)
                self.metrics.misses += 1
                self.metrics.expirations += 1
                return None

            entry.touch()
            self.metrics.hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache and mark as dirty."""
        async with self._lock:
            expires_at = None
            if ttl or self.default_ttl:
                ttl = ttl or self.default_ttl
                expires_at = datetime.utcnow() + ttl

            # Evict if needed
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_oldest()

            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                size_bytes=self._estimate_size(value),
                dirty=True,
            )

            self.cache[key] = entry
            self._dirty_keys.add(key)
            self.metrics.sets += 1
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self._dirty_keys.discard(key)
                self.metrics.deletes += 1
                return True
            return False

    async def evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        async with self._lock:
            while len(self.cache) >= self.max_size:
                await self._evict_oldest()

    async def _evict_oldest(self) -> None:
        """Evict the oldest entry, flushing if dirty."""
        if not self.cache:
            return

        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)

        # Flush if dirty
        if oldest_key in self._dirty_keys:
            await self._persist_entry(oldest_key)

        del self.cache[oldest_key]
        self._dirty_keys.discard(oldest_key)
        self.metrics.evictions += 1

    async def _flush_dirty_entries(self) -> None:
        """Flush all dirty entries to persistence."""
        async with self._lock:
            dirty_keys = list(self._dirty_keys)

        for key in dirty_keys:
            await self._persist_entry(key)

    async def _persist_entry(self, key: str) -> None:
        """Persist a single entry."""
        if self._persistence_callback and key in self.cache:
            try:
                entry = self.cache[key]
                await self._persistence_callback(key, entry.value)
                entry.dirty = False
                self._dirty_keys.discard(key)
            except Exception as e:
                logger.error(f"Failed to persist entry {key}: {e}")

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return len(str(value).encode("utf-8"))
        else:
            return len(str(value).encode("utf-8"))

    async def flush(self) -> None:
        """Force flush all dirty entries."""
        await self._flush_dirty_entries()

    async def close(self):
        """Close the cache and cleanup tasks."""
        # Flush any remaining dirty entries
        await self._flush_dirty_entries()

        if self._write_back_task:
            self._write_back_task.cancel()
            try:
                await self._write_back_task
            except asyncio.CancelledError:
                pass


class WriteThroughCacheStrategy(CacheStrategy):
    """Write-through cache strategy with immediate persistence."""

    def __init__(self, max_size: int = 1000, default_ttl: timedelta | None = None):
        super().__init__(max_size, default_ttl)
        self._persistence_callback = None

    def set_persistence_callback(self, callback):
        """Set callback for persistence operations."""
        self._persistence_callback = callback

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            self.metrics.total_requests += 1

            if key not in self.cache:
                self.metrics.misses += 1
                return None

            entry = self.cache[key]

            if entry.is_expired():
                del self.cache[key]
                self.metrics.misses += 1
                self.metrics.expirations += 1
                return None

            entry.touch()
            self.metrics.hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache and persist immediately."""
        # Persist first
        if self._persistence_callback:
            try:
                await self._persistence_callback(key, value)
            except Exception as e:
                logger.error(f"Failed to persist entry {key}: {e}")
                return False

        async with self._lock:
            expires_at = None
            if ttl or self.default_ttl:
                ttl = ttl or self.default_ttl
                expires_at = datetime.utcnow() + ttl

            # Evict if needed
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_oldest()

            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                size_bytes=self._estimate_size(value),
            )

            self.cache[key] = entry
            self.metrics.sets += 1
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache and persistence."""
        # Delete from persistence first
        if self._persistence_callback:
            try:
                await self._persistence_callback(key, None)  # None indicates deletion
            except Exception as e:
                logger.error(f"Failed to delete entry {key} from persistence: {e}")

        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self.metrics.deletes += 1
                return True
            return False

    async def evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        async with self._lock:
            while len(self.cache) >= self.max_size:
                await self._evict_oldest()

    async def _evict_oldest(self) -> None:
        """Evict the oldest entry."""
        if not self.cache:
            return

        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        del self.cache[oldest_key]
        self.metrics.evictions += 1

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return len(str(value).encode("utf-8"))
        else:
            return len(str(value).encode("utf-8"))
