"""

# Logseq: [[TTA.dev/Api_gateway/SSE/Stream]]
SSE stream producer for TTA turn processing.

TurnStream manages an asyncio.Queue-backed event queue for one player turn.
It applies backpressure when the client is too slow and supports replay
from a Last-Event-ID for reconnection.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from .models import (
    CrisisSignalEvent,
    DoneEvent,
    ErrorEvent,
    TokenEvent,
    WorldUpdateEvent,
)

logger = logging.getLogger(__name__)

QUEUE_MAXSIZE = 50
BACKPRESSURE_TIMEOUT = 5.0  # seconds before error event on full queue
REPLAY_TTL_SECONDS = 60


def _format_sse(event_id: str, data: dict[str, Any]) -> str:
    """Format a Server-Sent Event string."""
    payload = json.dumps(data)
    return f"id: {event_id}\ndata: {payload}\n\n"


class TurnStream:
    """Manages the SSE event queue for one player turn.

    The underlying queue has 2 extra slots beyond QUEUE_MAXSIZE reserved for
    a backpressure error event and the stream sentinel.  Token producers are
    blocked (via backpressure) once the queue reaches QUEUE_MAXSIZE.
    """

    def __init__(self, turn_id: str, session_id: str) -> None:
        self.turn_id = turn_id
        self.session_id = session_id
        # +2 reserved slots for backpressure error event + sentinel
        self.queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(
            maxsize=QUEUE_MAXSIZE + 2
        )
        self._token_index = 0
        self._events: list[tuple[str, dict[str, Any]]] = []  # for replay

    def _next_event_id(self) -> str:
        idx = self._token_index
        self._token_index += 1
        return f"{self.turn_id}:{idx}"

    async def put_token(self, content: str) -> None:
        """Enqueue a token event.

        If the queue already contains QUEUE_MAXSIZE items (token limit reached),
        an error event and a sentinel are pushed into the two reserved slots and
        no further tokens are accepted.
        """
        event_id = self._next_event_id()
        data = TokenEvent(content=content).model_dump()

        if self.queue.qsize() >= QUEUE_MAXSIZE:
            # Token limit hit — signal the client and close the stream.
            logger.warning("turn=%s backpressure: client too slow", self.turn_id)
            error_data = ErrorEvent(
                code="BACKPRESSURE", message="Client too slow"
            ).model_dump()
            self.queue.put_nowait({"id": event_id, "data": error_data})
            self.queue.put_nowait(None)  # sentinel; fits in reserved slot
            return

        try:
            await asyncio.wait_for(
                self.queue.put({"id": event_id, "data": data}),
                timeout=BACKPRESSURE_TIMEOUT,
            )
            self._events.append((event_id, data))
        except TimeoutError:
            # Concurrent producers pushed the queue to maxsize between our
            # qsize() check and the actual put — degrade gracefully.
            logger.warning(
                "turn=%s backpressure timeout after size check", self.turn_id
            )
            error_data = ErrorEvent(
                code="BACKPRESSURE", message="Client too slow"
            ).model_dump()
            try:
                self.queue.put_nowait({"id": event_id, "data": error_data})
            except asyncio.QueueFull:
                logger.error(
                    "turn=%s reserved slots exhausted; error dropped", self.turn_id
                )
            try:
                self.queue.put_nowait(None)
            except asyncio.QueueFull:
                logger.error(
                    "turn=%s reserved slots exhausted; sentinel dropped", self.turn_id
                )

    async def put_crisis_signal(
        self, level: str, resource_url: str | None = None
    ) -> None:
        """Enqueue a crisis signal event."""
        event_id = self._next_event_id()
        data = CrisisSignalEvent(level=level, resource_url=resource_url).model_dump()
        self._events.append((event_id, data))
        await self.queue.put({"id": event_id, "data": data})

    async def put_world_update(
        self, updates: list[dict[str, Any]] | None = None
    ) -> None:
        """Enqueue a world update event."""
        event_id = self._next_event_id()
        data = WorldUpdateEvent(updates=updates or []).model_dump()
        self._events.append((event_id, data))
        await self.queue.put({"id": event_id, "data": data})

    async def put_done(self, tension_level: float = 0.0) -> None:
        """Enqueue a done event and a sentinel to close the stream."""
        event_id = self._next_event_id()
        data = DoneEvent(turn_id=self.turn_id, tension_level=tension_level).model_dump()
        self._events.append((event_id, data))
        await self.queue.put({"id": event_id, "data": data})
        await self.queue.put(None)  # sentinel

    async def put_error(self, code: str, message: str) -> None:
        """Enqueue an error event and close the stream."""
        event_id = self._next_event_id()
        data = ErrorEvent(code=code, message=message).model_dump()
        await self.queue.put({"id": event_id, "data": data})
        await self.queue.put(None)

    async def generate(self, last_event_id: str | None = None) -> AsyncGenerator[str]:
        """Yield formatted SSE strings. Handles replay from last_event_id."""
        if last_event_id is not None:
            # Replay events after last_event_id
            replayed = False
            for eid, data in self._events:
                if replayed:
                    yield _format_sse(eid, data)
                elif eid == last_event_id:
                    replayed = True
            if not replayed:
                # last_event_id not found — replay unavailable
                yield _format_sse(
                    f"{self.turn_id}:replay-unavailable",
                    DoneEvent(turn_id=self.turn_id).model_dump(),
                )
                return

        while True:
            item = await self.queue.get()
            if item is None:
                break
            yield _format_sse(item["id"], item["data"])
