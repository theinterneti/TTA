"""
Redis-backed ToolRegistry with lifecycle management and caching (Task 7.1/7.2).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from typing import Any

from redis.asyncio import Redis

from .models import ToolSpec, ToolStatus


class _LRU:
    def __init__(self, max_items: int = 512, ttl_s: float = 300.0) -> None:
        self._max = max_items
        self._ttl = ttl_s
        self._data: dict[str, tuple[float, Any]] = {}
        self._order: list[str] = []
        self._lock = asyncio.Lock()
        self.hits: int = 0
        self.misses: int = 0

    async def get(self, k: str) -> Any | None:
        async with self._lock:
            item = self._data.get(k)
            if not item:
                self.misses += 1
                return None
            ts, v = item
            if self._ttl and (time.time() - ts) > self._ttl:
                self._data.pop(k, None)
                with contextlib.suppress(ValueError):
                    self._order.remove(k)
                self.misses += 1
                return None
            # move to end
            with contextlib.suppress(ValueError):
                self._order.remove(k)
            self._order.append(k)
            self.hits += 1
            return v

    async def set(self, k: str, v: Any) -> None:
        async with self._lock:
            now = time.time()
            self._data[k] = (now, v)
            with contextlib.suppress(ValueError):
                self._order.remove(k)
            self._order.append(k)
            while len(self._order) > self._max:
                old = self._order.pop(0)
                self._data.pop(old, None)

    async def stats(self) -> dict[str, int]:
        async with self._lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "size": len(self._order),
                "capacity": self._max,
            }


class RedisToolRegistry:
    def __init__(
        self,
        redis: Redis,
        key_prefix: str = "ao",
        *,
        cache_ttl_s: float = 300.0,
        cache_max_items: int = 512,
    ) -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        self._idx = f"{self._pfx}:tools:index"
        self._cache = _LRU(cache_max_items, cache_ttl_s)
        self._locks: dict[str, asyncio.Lock] = {}

    def _key(self, name: str, version: str) -> str:
        return f"{self._pfx}:tools:{name}:{version}"

    def _status_key(self, name: str, version: str) -> str:
        return f"{self._pfx}:tools:status:{name}:{version}"

    def _lock_for(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def register_tool(self, spec: ToolSpec) -> bool:
        key = self._key(spec.name, spec.version)
        async with self._lock_for(key):
            # Do not overwrite existing definitions (idempotent)
            exists = await self._redis.exists(key)
            if exists:
                return False
            payload = json.dumps(spec.model_dump())
            await self._redis.set(key, payload)
            await self._redis.sadd(self._idx, f"{spec.name}:{spec.version}")
            await self._redis.set(
                self._status_key(spec.name, spec.version), ToolStatus.ACTIVE.value
            )
            await self._cache.set(key, spec)
            return True

    async def get_tool(self, name: str, version: str | None = None) -> ToolSpec | None:
        if version is None:
            # pick latest by lexicographic version ordering (simple heuristic)
            members = await self._redis.smembers(self._idx)
            candidates: list[tuple[str, str]] = []
            for b in members:
                s = b.decode() if isinstance(b, (bytes, bytearray)) else b
                if not s.startswith(f"{name}:"):
                    continue
                _, ver = s.split(":", 1)
                candidates.append((name, ver))
            if not candidates:
                return None

            # sort by version segments numeric
            def _ver_key(v: str) -> tuple[int, ...]:
                parts = v.split(".")
                return tuple(int(p) for p in parts)

            candidates.sort(key=lambda t: _ver_key(t[1]), reverse=True)
            name, version = candidates[0]
        key = self._key(name, version)
        cached = await self._cache.get(key)
        if cached is not None:
            return cached
        b = await self._redis.get(key)
        if not b:
            return None
        data = json.loads(b)
        spec = ToolSpec(**data)
        await self._cache.set(key, spec)
        return spec

    async def list_tools(self, prefix: str | None = None) -> list[ToolSpec]:
        members = await self._redis.smembers(self._idx)
        out: list[ToolSpec] = []
        for b in members:
            s = b.decode() if isinstance(b, (bytes, bytearray)) else b
            nm, ver = s.split(":", 1)
            if prefix and not nm.startswith(prefix):
                continue
            spec = await self.get_tool(nm, ver)
            if spec:
                out.append(spec)
        return out

    async def list_tool_ids(self) -> list[str]:
        members = await self._redis.smembers(self._idx)
        ids: list[str] = []
        for b in members:
            s = b.decode() if isinstance(b, (bytes, bytearray)) else b
            ids.append(s)
        return ids

    async def get_status(self, name: str, version: str) -> str:
        s = await self._redis.get(self._status_key(name, version))
        return (
            (s.decode() if isinstance(s, (bytes, bytearray)) else s)
            if s
            else ToolStatus.ACTIVE.value
        )

    async def cache_stats(self) -> dict[str, int]:
        return await self._cache.stats()

    async def deprecate_tool(self, name: str, version: str) -> None:
        await self._redis.set(
            self._status_key(name, version), ToolStatus.DEPRECATED.value
        )
        key = self._key(name, version)
        cached = await self._cache.get(key)
        if cached:
            cached.status = ToolStatus.DEPRECATED
            await self._cache.set(key, cached)

    async def touch_last_used(self, name: str, version: str) -> None:
        key = self._key(name, version)
        b = await self._redis.get(key)
        if not b:
            return
        data = json.loads(b)
        data["last_used_at"] = time.time()
        await self._redis.set(key, json.dumps(data))

    async def cleanup_expired(self, max_idle_seconds: float) -> int:
        members = await self._redis.smembers(self._idx)
        removed = 0
        now = time.time()
        for b in members:
            s = b.decode() if isinstance(b, (bytes, bytearray)) else b
            nm, ver = s.split(":", 1)
            key = self._key(nm, ver)
            raw = await self._redis.get(key)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except Exception:
                continue
            last = float(data.get("last_used_at", 0.0))
            status = data.get("status", ToolStatus.ACTIVE.value)
            if status == ToolStatus.ACTIVE.value and (now - last) > max_idle_seconds:
                # soft deprecate then remove index to allow GC by external retention policies
                await self._redis.set(
                    self._status_key(nm, ver), ToolStatus.DEPRECATED.value
                )
                await self._redis.srem(self._idx, f"{nm}:{ver}")
                removed += 1
        return removed
