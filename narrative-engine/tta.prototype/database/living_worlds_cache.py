"""
Living Worlds Redis Caching Facade

Provides namespaced keys, convenience methods, and simple hit/miss metrics
for world state, flags, entity state, and recent timeline events. Wraps the
existing RedisCache (mock or real) to maintain backward compatibility while
introducing a new keyspace per .kiro spec.
"""
from __future__ import annotations

import json
import logging
from typing import Any

try:
    from .redis_cache import RedisCache
except Exception:  # pragma: no cover - import fallbacks
    from redis_cache import RedisCache  # type: ignore

logger = logging.getLogger(__name__)


class LivingWorldsCache:
    """High-level cache helper with namespaced keys and metrics."""

    def __init__(self, redis_cache: RedisCache | None = None):
        self.redis = redis_cache or RedisCache()
        # simple in-process counters for tests/metrics
        self.metrics = {
            "world_state_hits": 0,
            "world_state_misses": 0,
            "flags_hits": 0,
            "flags_misses": 0,
            "recent_hits": 0,
            "recent_misses": 0,
            "history_hits": 0,
            "history_misses": 0,
            "invalidations": 0,
        }

    # Key helpers
    def _k_world_state(self, world_id: str) -> str:
        return f"lw:world:{world_id}:state"

    def _k_flags(self, world_id: str) -> str:
        return f"lw:world:{world_id}:flags"

    def _k_recent(self, world_id: str, entity_id: str) -> str:
        return f"lw:world:{world_id}:timeline:{entity_id}:recent"

    def _k_entity_state(self, world_id: str, etype: str, entity_id: str) -> str:
        return f"lw:world:{world_id}:{etype}:{entity_id}:state"

    def _k_history(self, world_id: str, etype: str, entity_id: str, detail: int, days: int | None) -> str:
        suffix = f":d{days}" if days else ""
        return f"lw:world:{world_id}:history:{etype}:{entity_id}:dl{detail}{suffix}"

    def _k_version(self, world_id: str) -> str:
        return f"lw:world:{world_id}:ver"

    # Versioning
    def increment_version(self, world_id: str) -> None:
        try:
            ver_key = self._k_version(world_id)
            current = self.redis.get(ver_key) or 0
            try:
                current = int(current)
            except Exception:
                current = 0
            self.redis.set(ver_key, current + 1)
        except Exception:
            logger.debug("Failed to increment version key", exc_info=True)

    # World state
    def get_world_state(self, world_id: str) -> str | None:
        try:
            val = self.redis.get(self._k_world_state(world_id))
            if val is None:
                self.metrics["world_state_misses"] += 1
            else:
                self.metrics["world_state_hits"] += 1
            return val
        except Exception:
            self.metrics["world_state_misses"] += 1
            logger.debug("get_world_state cache error", exc_info=True)
            return None

    def set_world_state(self, world_id: str, value: str, ttl: int | None = None) -> bool:
        try:
            return bool(self.redis.set(self._k_world_state(world_id), value, ttl=ttl))
        except Exception:
            logger.debug("set_world_state cache error", exc_info=True)
            return False

    def invalidate_world_state(self, world_id: str) -> None:
        try:
            self.redis.delete(self._k_world_state(world_id))
            self.metrics["invalidations"] += 1
        except Exception:
            logger.debug("invalidate_world_state cache error", exc_info=True)

    # Flags
    def get_flags(self, world_id: str) -> dict[str, Any]:
        try:
            val = self.redis.get(self._k_flags(world_id))
            if val is None:
                self.metrics["flags_misses"] += 1
                return {}
            self.metrics["flags_hits"] += 1
            if isinstance(val, str):
                return json.loads(val)
            return val
        except Exception:
            self.metrics["flags_misses"] += 1
            logger.debug("get_flags cache error", exc_info=True)
            return {}

    def set_flags(self, world_id: str, flags: dict[str, Any], ttl: int | None = None) -> bool:
        try:
            data = json.dumps(flags)
            return bool(self.redis.set(self._k_flags(world_id), data, ttl=ttl))
        except Exception:
            logger.debug("set_flags cache error", exc_info=True)
            return False

    def invalidate_flags(self, world_id: str) -> None:
        try:
            self.redis.delete(self._k_flags(world_id))
            self.metrics["invalidations"] += 1
        except Exception:
            logger.debug("invalidate_flags cache error", exc_info=True)

    # Recent timeline events
    def get_recent_timeline_events(self, world_id: str, entity_id: str) -> list[dict[str, Any]]:
        try:
            val = self.redis.get(self._k_recent(world_id, entity_id))
            if val is None:
                self.metrics["recent_misses"] += 1
                return []
            self.metrics["recent_hits"] += 1
            if isinstance(val, str):
                return json.loads(val)
            return val
        except Exception:
            self.metrics["recent_misses"] += 1
            logger.debug("get_recent_timeline_events cache error", exc_info=True)
            return []

    def set_recent_timeline_events(self, world_id: str, entity_id: str, events: list[dict[str, Any]], ttl: int | None = None) -> bool:
        try:
            data = json.dumps(events)
            return bool(self.redis.set(self._k_recent(world_id, entity_id), data, ttl=ttl))
        except Exception:
            logger.debug("set_recent_timeline_events cache error", exc_info=True)
            return False

    def invalidate_recent_timeline(self, world_id: str, entity_id: str) -> None:
        try:
            self.redis.delete(self._k_recent(world_id, entity_id))
            self.metrics["invalidations"] += 1
        except Exception:
            logger.debug("invalidate_recent_timeline cache error", exc_info=True)

    # Entity state helpers (optional use)
    def set_entity_state(self, world_id: str, etype: str, entity_id: str, state: dict[str, Any], ttl: int | None = None) -> bool:
        try:
            data = json.dumps(state)
            return bool(self.redis.set(self._k_entity_state(world_id, etype, entity_id), data, ttl=ttl))
        except Exception:
            logger.debug("set_entity_state cache error", exc_info=True)
            return False

    def get_entity_state(self, world_id: str, etype: str, entity_id: str) -> dict[str, Any]:
        try:
            val = self.redis.get(self._k_entity_state(world_id, etype, entity_id))
            if not val:
                return {}
            if isinstance(val, str):
                return json.loads(val)
            return val
        except Exception:
            logger.debug("get_entity_state cache error", exc_info=True)
            return {}

    # History helpers
    def get_history(self, world_id: str, etype: str, entity_id: str, detail: int, days: int | None) -> dict[str, Any]:
        try:
            val = self.redis.get(self._k_history(world_id, etype, entity_id, detail, days))
            if val is None:
                self.metrics["history_misses"] += 1
                return {}
            self.metrics["history_hits"] += 1
            if isinstance(val, str):
                return json.loads(val)
            return val
        except Exception:
            self.metrics["history_misses"] += 1
            logger.debug("get_history cache error", exc_info=True)
            return {}

    def set_history(self, world_id: str, etype: str, entity_id: str, detail: int, days: int | None, history: dict[str, Any], ttl: int | None = 900) -> bool:
        try:
            data = json.dumps(history)
            return bool(self.redis.set(self._k_history(world_id, etype, entity_id, detail, days), data, ttl=ttl))
        except Exception:
            logger.debug("set_history cache error", exc_info=True)
            return False

    def invalidate_history(self, world_id: str, etype: str, entity_id: str) -> None:
        try:
            # We can't easily wildcard-invalidate by detail/days; invalidate common variants
            for d in (1, 3, 5, 7, 9):
                self.redis.delete(self._k_history(world_id, etype, entity_id, d, None))
            self.metrics["invalidations"] += 1
        except Exception:
            logger.debug("invalidate_history cache error", exc_info=True)

    # Warming helpers
    def warm_world(self, world_state) -> None:  # world_state is WorldState-like
        try:
            self.set_world_state(world_state.world_id, world_state.to_json())
            self.set_flags(world_state.world_id, getattr(world_state, 'world_flags', {}))
            # pre-create empty recent lists for active entities
            for cid in getattr(world_state, 'active_characters', {}).keys():
                self.set_recent_timeline_events(world_state.world_id, cid, [], ttl=600)
            for lid in getattr(world_state, 'active_locations', {}).keys():
                self.set_recent_timeline_events(world_state.world_id, lid, [], ttl=600)
            for oid in getattr(world_state, 'active_objects', {}).keys():
                self.set_recent_timeline_events(world_state.world_id, oid, [], ttl=600)
        except Exception:
            logger.debug("warm_world cache error", exc_info=True)

