"""Safety rules provider with Redis caching and file fallback."""

# Logseq: [[TTA.dev/Agent_orchestration/Safety_monitoring/Provider]]

from __future__ import annotations

import contextlib  # BUG FIX: Added missing import (line 3375 uses contextlib.suppress())
import json
import time
from typing import Any, cast

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Optional; JSON works without it

try:
    from redis.asyncio import Redis as _Redis
except Exception:  # pragma: no cover
    _Redis = None  # type: ignore


class SafetyRulesProvider:
    """Loads safety rules from Redis with TTL caching and file fallback.

    - Redis key: "ao:safety:rules"
    - TTL-based reload for live updates
    - Fallback to file path (env TTA_SAFETY_RULES_CONFIG) if Redis unavailable or key missing
    """

    def __init__(
        self,
        redis_client: _Redis | None = None,
        *,
        redis_key: str = "ao:safety:rules",
        cache_ttl_s: float = 2.0,
        file_fallback_path: str | None = None,
    ) -> None:
        self._redis = redis_client
        self._key = redis_key
        self._ttl = float(cache_ttl_s)
        self._file = file_fallback_path
        self._cached_raw: str | None = None
        self._cached_at: float = 0.0
        self._last_source: str | None = None

    async def get_config(self) -> dict[str, Any]:
        now = time.time()
        if self._cached_raw is not None and (now - self._cached_at) < self._ttl:
            with contextlib.suppress(Exception):
                return json.loads(self._cached_raw)
        # Try Redis first
        cfg: dict[str, Any] | None = None
        raw: str | None = None
        if self._redis is not None:
            try:
                b = await cast("_Redis", self._redis).get(self._key)
                if b:
                    raw = b.decode() if isinstance(b, (bytes, bytearray)) else str(b)
                    cfg = json.loads(raw)
                    self._last_source = f"redis:{self._key}"
            except Exception:
                cfg = None
        # Fallback to file
        if cfg is None:
            try:
                path = self._file
                if not path:
                    import os

                    path = os.environ.get("TTA_SAFETY_RULES_CONFIG")
                if path:
                    from pathlib import Path as _Path

                    if path.lower().endswith((".yaml", ".yml")) and yaml is not None:
                        with _Path(path).open(encoding="utf-8") as f:
                            cfg = yaml.safe_load(f)
                    else:
                        with _Path(path).open(encoding="utf-8") as f:
                            cfg = json.load(f)
                    raw = json.dumps(cfg)
                    self._last_source = f"file:{path}"
            except Exception:
                cfg = None
        if cfg is None:
            # Default config - import here to avoid circular dependency
            from ..therapeutic_scoring.validator import TherapeuticValidator

            cfg = TherapeuticValidator()._default_config()
            raw = json.dumps(cfg)
            self._last_source = "default"
        self._cached_raw = raw
        self._cached_at = now
        return cfg

    def status(self) -> dict[str, Any]:
        return {
            "last_reload_ts": self._cached_at or None,
            "source": self._last_source,
            "redis_key": self._key,
            "cache_ttl_s": self._ttl,
        }

    def invalidate(self) -> None:
        self._cached_raw = None
        self._cached_at = 0.0
        # do not clear last_source; next load will update
