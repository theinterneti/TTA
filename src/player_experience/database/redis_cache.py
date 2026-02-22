"""
Logseq: [[TTA.dev/Player_experience/Database/Redis_cache]]
Redis-backed token cache for fast authentication.

Caches decoded JWT TokenData in Redis to avoid repeated HMAC verification on
every authenticated request.  The cache key is a short SHA-256 digest of the
raw token — the token itself is never stored as a key.

TTL is set to the remaining lifetime of the JWT so the cache entry expires
automatically when the token does.

Usage::

    cache = TokenCache.from_env()
    cached = await cache.get(raw_token)
    if cached is None:
        token_data = verify_token(raw_token)
        await cache.set(raw_token, token_data, ttl=remaining_seconds)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import redis.asyncio as aioredis

_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
_KEY_PREFIX = "auth:tok:"


class TokenCache:
    """Async Redis cache for JWT TokenData.

    Intended as a singleton — use :meth:`from_env` to create one instance
    shared across the lifetime of the application process.
    """

    def __init__(self, client: aioredis.Redis) -> None:  # type: ignore[type-arg]
        self._client = client

    @classmethod
    def from_env(cls) -> TokenCache:
        """Create a TokenCache using REDIS_URL from environment."""
        import redis.asyncio as aioredis  # noqa: PLC0415

        redis_url = os.environ.get("REDIS_URL", _REDIS_URL)
        client = aioredis.from_url(redis_url, decode_responses=True)
        return cls(client)

    @staticmethod
    def _key(token: str) -> str:
        """Short, non-reversible key for the token (SHA-256 prefix)."""
        digest = hashlib.sha256(token.encode()).hexdigest()[:24]
        return f"{_KEY_PREFIX}{digest}"

    async def get(self, token: str) -> dict[str, Any] | None:
        """Return cached token data dict, or None on cache miss / error."""
        try:
            raw = await self._client.get(self._key(token))
            if raw:
                return json.loads(raw)
        except Exception as exc:
            logger.debug("TokenCache.get error (ignored): %s", exc)
        return None

    async def set(self, token: str, data: dict[str, Any], ttl: int) -> None:
        """Cache token data with the given TTL (seconds). Silently ignores errors."""
        if ttl <= 0:
            return
        try:
            await self._client.setex(self._key(token), ttl, json.dumps(data))
        except Exception as exc:
            logger.debug("TokenCache.set error (ignored): %s", exc)

    async def delete(self, token: str) -> None:
        """Invalidate a cached token (e.g. on logout). Silently ignores errors."""
        try:
            await self._client.delete(self._key(token))
        except Exception as exc:
            logger.debug("TokenCache.delete error (ignored): %s", exc)

    async def ping(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            return bool(await self._client.ping())
        except Exception:
            return False


def _serialize_token_data(token_data: Any) -> dict[str, Any]:
    """Convert a TokenData to a JSON-serialisable dict."""
    exp_iso: str | None = None
    if token_data.exp is not None:
        exp_val = token_data.exp
        exp_iso = exp_val.isoformat() if isinstance(exp_val, datetime) else str(exp_val)
    return {
        "player_id": token_data.player_id,
        "username": token_data.username,
        "email": token_data.email,
        "exp": exp_iso,
    }


def _deserialize_token_data(data: dict[str, Any]) -> dict[str, Any]:
    """Return a dict suitable for constructing TokenData(**...)."""
    exp = None
    if data.get("exp"):
        try:
            exp = datetime.fromisoformat(data["exp"])
        except (ValueError, TypeError):
            exp = None
    return {
        "player_id": data.get("player_id"),
        "username": data.get("username"),
        "email": data.get("email"),
        "exp": exp,
    }
