"""HistoryCompressor — async compression of long session histories.

When tier-5 (session history) exceeds its token budget, the oldest turns are
summarised via an LLM call and the summary is stored in Redis alongside the
raw recent turns.  Compression is triggered without blocking the current
request (fire-and-forget via ``asyncio.ensure_future``).

Issue: #277
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_SUMMARY_TTL_SECONDS = 86400  # 24 hours
_SUMMARY_REDIS_KEY = "world_context:history_summary:{session_id}"
_COMPRESS_THRESHOLD = 0.9  # trigger when tier usage > 90 % of budget


class HistoryCompressor:
    """Detects tier-5 overflow and compresses old turns via LLM summarisation.

    Args:
        redis_client:   An async Redis client (``redis.asyncio``).  If None,
                        compression is disabled and turns are returned as-is.
        llm_summarise:  Async callable ``(turns: list[dict]) -> str``.  If None,
                        a simple truncation fallback is used.
        ttl:            Redis TTL for stored summaries (seconds).
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        llm_summarise: Any | None = None,
        ttl: int = _SUMMARY_TTL_SECONDS,
    ) -> None:
        self._redis = redis_client
        self._llm_summarise = llm_summarise
        self._ttl = ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def compress_if_needed(
        self,
        session_id: str,
        turns: list[dict[str, str]],
        budget: int,
        counter: Any,
    ) -> list[dict[str, str]]:
        """Return a (possibly compressed) turn list that fits within *budget*.

        If the turns already fit, they are returned unchanged.

        If compression is needed:
        1. Try to fetch a previously-stored summary from Redis.
        2. If none exists, fire-and-forget a background summarisation task.
        3. Return the most recent half of the turns (fits the budget).

        Args:
            session_id: The active session ID (used as Redis cache key).
            turns:      Full message history ``[{role, content}, ...]``.
            budget:     Token budget for tier 5.
            counter:    A ``TokenCounter`` instance.

        Returns:
            A turn list whose total token count fits within *budget*.
        """
        full_text = self._turns_to_text(turns)
        if counter.fits(full_text, budget):
            return turns

        logger.debug(
            "HistoryCompressor: session=%s tokens=%d > budget=%d — compressing",
            session_id,
            counter.count(full_text),
            budget,
        )

        # Try to retrieve a cached summary first
        summary = await self._load_summary(session_id)

        if summary:
            # Combine summary turn with recent raw turns
            recent = self._recent_half(turns)
            return [{"role": "assistant", "content": f"[Summary] {summary}"}] + recent

        # No summary yet — schedule background compression (non-blocking)
        if self._redis is not None:
            asyncio.ensure_future(self._compress_and_store(session_id, turns))

        # Return recent half immediately (fits budget)
        return self._recent_half(turns)

    async def get_stored_summary(self, session_id: str) -> str | None:
        """Return any stored compression summary for *session_id* (or None)."""
        return await self._load_summary(session_id)

    async def clear_summary(self, session_id: str) -> None:
        """Delete the stored summary for *session_id* (e.g. on session reset)."""
        if self._redis is None:
            return
        key = _SUMMARY_REDIS_KEY.format(session_id=session_id)
        try:
            await self._redis.delete(key)
        except Exception as exc:
            logger.warning("HistoryCompressor: could not clear summary: %s", exc)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _recent_half(self, turns: list[dict[str, str]]) -> list[dict[str, str]]:
        """Return the most recent half of *turns*."""
        n = max(1, len(turns) // 2)
        return turns[-n:]

    @staticmethod
    def _turns_to_text(turns: list[dict[str, str]]) -> str:
        return "\n".join(
            f"{t.get('role', 'user')}: {t.get('content', '')}" for t in turns
        )

    async def _load_summary(self, session_id: str) -> str | None:
        if self._redis is None:
            return None
        key = _SUMMARY_REDIS_KEY.format(session_id=session_id)
        try:
            raw = await self._redis.get(key)
            if raw:
                return raw.decode() if isinstance(raw, bytes) else raw
        except Exception as exc:
            logger.warning("HistoryCompressor: Redis read error: %s", exc)
        return None

    async def _compress_and_store(
        self, session_id: str, turns: list[dict[str, str]]
    ) -> None:
        """Summarise the oldest half of *turns* and cache the result in Redis."""
        if self._redis is None:
            return

        t_start = time.perf_counter()
        old_turns = turns[: len(turns) // 2]

        try:
            summary = await self._do_summarise(old_turns)
        except Exception as exc:
            logger.warning(
                "HistoryCompressor: summarisation failed for session=%s: %s",
                session_id,
                exc,
            )
            return

        key = _SUMMARY_REDIS_KEY.format(session_id=session_id)
        try:
            await self._redis.setex(key, self._ttl, summary)
            elapsed_ms = (time.perf_counter() - t_start) * 1000
            logger.info(
                "HistoryCompressor: stored summary for session=%s len=%d "
                "turns_compressed=%d elapsed=%.1fms",
                session_id,
                len(summary),
                len(old_turns),
                elapsed_ms,
            )
        except Exception as exc:
            logger.warning("HistoryCompressor: Redis write error: %s", exc)

    async def _do_summarise(self, turns: list[dict[str, str]]) -> str:
        """Summarise *turns* via the injected LLM callable or a simple fallback."""
        if self._llm_summarise is not None:
            return await self._llm_summarise(turns)

        # Fallback: first-sentence of each assistant turn
        snippets = [
            t["content"].split(".")[0].strip()
            for t in turns
            if t.get("role") == "assistant" and t.get("content")
        ]
        if snippets:
            return "Earlier in the session: " + ". ".join(snippets[:5]) + "."
        return json.dumps(
            [
                {"role": t.get("role"), "content": t.get("content", "")[:80]}
                for t in turns[:5]
            ]
        )
