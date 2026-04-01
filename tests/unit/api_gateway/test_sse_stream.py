"""Tests for the SSE stream module (TurnStream) and SSE event models."""

from __future__ import annotations

import pytest

from src.api_gateway.sse import TurnStream
from src.api_gateway.sse.models import (
    CrisisSignalEvent,
    DoneEvent,
    ErrorEvent,
    SSEEventType,
    TokenEvent,
    WorldUpdateEvent,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _drain(stream: TurnStream, last_event_id: str | None = None) -> list[str]:
    """Collect all SSE chunks from a stream into a list."""
    chunks: list[str] = []
    async for chunk in stream.generate(last_event_id=last_event_id):
        chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# Token streaming
# ---------------------------------------------------------------------------


class TestTurnStreamTokens:
    @pytest.mark.asyncio
    async def test_put_and_generate_single_token(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("Hello")
        await stream.put_done()

        events = await _drain(stream)

        assert len(events) == 2  # token + done
        assert '"type": "token"' in events[0]
        assert '"content": "Hello"' in events[0]
        assert "id: t1:0" in events[0]

    @pytest.mark.asyncio
    async def test_event_ids_increment(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("a")
        await stream.put_token("b")
        await stream.put_token("c")
        await stream.put_done()

        events = await _drain(stream)

        assert "id: t1:0" in events[0]
        assert "id: t1:1" in events[1]
        assert "id: t1:2" in events[2]
        assert "id: t1:3" in events[3]  # done

    @pytest.mark.asyncio
    async def test_multiple_tokens(self) -> None:
        stream = TurnStream(turn_id="t2", session_id="s1")
        for word in ["The", "forest", "whispers."]:
            await stream.put_token(word)
        await stream.put_done()

        events = await _drain(stream)
        assert len(events) == 4  # 3 tokens + done
        assert '"content": "The"' in events[0]
        assert '"content": "forest"' in events[1]

    @pytest.mark.asyncio
    async def test_crisis_signal_event(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_crisis_signal("critical", "https://988lifeline.org")
        await stream.put_done()

        events = await _drain(stream)

        assert len(events) == 2
        assert '"type": "crisis_signal"' in events[0]
        assert '"level": "critical"' in events[0]
        assert "988lifeline" in events[0]

    @pytest.mark.asyncio
    async def test_crisis_signal_without_url(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_crisis_signal("high")
        await stream.put_done()

        events = await _drain(stream)
        assert '"type": "crisis_signal"' in events[0]
        assert '"level": "high"' in events[0]

    @pytest.mark.asyncio
    async def test_error_event_terminates_stream(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("before")
        await stream.put_error("PIPELINE_ERROR", "something broke")

        events = await _drain(stream)

        # token + error; no done sentinel needed (error puts None)
        assert any('"type": "error"' in e for e in events)
        assert any('"code": "PIPELINE_ERROR"' in e for e in events)

    @pytest.mark.asyncio
    async def test_done_event_terminates_stream(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("word")
        await stream.put_done(tension_level=0.5)

        events = await _drain(stream)

        assert any('"type": "done"' in e for e in events)
        assert any('"tension_level": 0.5' in e for e in events)
        # Stream should be finite
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_done_event_contains_turn_id(self) -> None:
        stream = TurnStream(turn_id="my-turn-123", session_id="s1")
        await stream.put_done()

        events = await _drain(stream)
        assert '"turn_id": "my-turn-123"' in events[0]

    @pytest.mark.asyncio
    async def test_world_update_event(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_world_update([{"key": "door", "state": "open"}])
        await stream.put_done()

        events = await _drain(stream)
        assert '"type": "world_update"' in events[0]
        assert '"door"' in events[0]


# ---------------------------------------------------------------------------
# Backpressure
# ---------------------------------------------------------------------------


class TestTurnStreamBackpressure:
    @pytest.mark.asyncio
    async def test_backpressure_timeout_emits_error(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        # Fill to QUEUE_MAXSIZE (50) — the token limit that triggers backpressure
        for i in range(50):
            stream.queue.put_nowait({"id": f"t1:{i}", "data": {}})

        # put_token detects qsize() >= 50 and uses the 2 reserved slots
        await stream.put_token("overflow")

        # Drain all items; the last two should be error event + sentinel
        items = []
        while not stream.queue.empty():
            items.append(stream.queue.get_nowait())

        assert items[-1] is None  # sentinel
        error_item = items[-2]
        assert error_item is not None
        assert error_item["data"]["code"] == "BACKPRESSURE"

    @pytest.mark.asyncio
    async def test_queue_maxsize_is_fifty(self) -> None:
        # Effective token limit is QUEUE_MAXSIZE (50); internal queue is +2
        stream = TurnStream(turn_id="t1", session_id="s1")
        from src.api_gateway.sse.stream import QUEUE_MAXSIZE

        assert stream.queue.maxsize == QUEUE_MAXSIZE + 2


# ---------------------------------------------------------------------------
# Replay / reconnection
# ---------------------------------------------------------------------------


class TestTurnStreamReplay:
    @pytest.mark.asyncio
    async def test_replay_from_last_event_id(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("Hello")  # id: t1:0
        await stream.put_token("world")  # id: t1:1
        await stream.put_done()  # id: t1:2

        # Reconnect from t1:0 — should get t1:1 and t1:2 from _events,
        # then consume the queue (which only has the sentinel by now).
        # Note: queue was already consumed by the first drain above? No —
        # we didn't call _drain. Queue still has items.

        # Re-build stream to isolate replay logic (events list is preserved)
        replay_stream = TurnStream(turn_id="t1", session_id="s1")
        replay_stream._events = list(stream._events)
        replay_stream._token_index = stream._token_index
        # Queue is empty — put sentinel so generate() stops after replay
        replay_stream.queue.put_nowait(None)

        events = await _drain(replay_stream, last_event_id="t1:0")

        # Replayed events after t1:0 → t1:1 (world) and t1:2 (done)
        assert len(events) == 2
        assert "t1:1" in events[0]
        assert '"content": "world"' in events[0]

    @pytest.mark.asyncio
    async def test_replay_unknown_event_id_sends_done(self) -> None:
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("Hello")
        await stream.put_done()

        replay_stream = TurnStream(turn_id="t1", session_id="s1")
        replay_stream._events = list(stream._events)

        events = await _drain(replay_stream, last_event_id="t1:999")

        # Should get a single replay-unavailable done event
        assert len(events) == 1
        assert "replay-unavailable" in events[0]
        assert '"type": "done"' in events[0]

    @pytest.mark.asyncio
    async def test_replay_from_first_event(self) -> None:
        """last_event_id pointing to t1:0 replays from t1:1 onwards."""
        stream = TurnStream(turn_id="t1", session_id="s1")
        await stream.put_token("a")  # t1:0
        await stream.put_token("b")  # t1:1
        await stream.put_token("c")  # t1:2
        await stream.put_done()  # t1:3

        replay_stream = TurnStream(turn_id="t1", session_id="s1")
        replay_stream._events = list(stream._events)
        replay_stream.queue.put_nowait(None)

        events = await _drain(replay_stream, last_event_id="t1:0")
        assert len(events) == 3  # t1:1, t1:2, t1:3


# ---------------------------------------------------------------------------
# SSE models
# ---------------------------------------------------------------------------


class TestSSEModels:
    def test_token_event_serializes(self) -> None:
        event = TokenEvent(content="Hello world")
        data = event.model_dump()
        assert data["type"] == SSEEventType.TOKEN
        assert data["content"] == "Hello world"

    def test_token_event_default_type(self) -> None:
        event = TokenEvent(content="x")
        assert event.type == SSEEventType.TOKEN

    def test_crisis_signal_event_serializes(self) -> None:
        event = CrisisSignalEvent(level="critical", resource_url="https://example.com")
        data = event.model_dump()
        assert data["type"] == SSEEventType.CRISIS_SIGNAL
        assert data["level"] == "critical"
        assert data["resource_url"] == "https://example.com"

    def test_crisis_signal_no_url(self) -> None:
        event = CrisisSignalEvent(level="high")
        assert event.resource_url is None

    def test_done_event_has_turn_id(self) -> None:
        event = DoneEvent(turn_id="abc-123", tension_level=0.7)
        data = event.model_dump()
        assert data["turn_id"] == "abc-123"
        assert data["tension_level"] == 0.7

    def test_done_event_default_tension(self) -> None:
        event = DoneEvent(turn_id="t1")
        assert event.tension_level == 0.0

    def test_error_event_has_code(self) -> None:
        event = ErrorEvent(code="PIPELINE_ERROR", message="boom")
        data = event.model_dump()
        assert data["code"] == "PIPELINE_ERROR"
        assert data["message"] == "boom"

    def test_world_update_event_empty_updates(self) -> None:
        event = WorldUpdateEvent()
        assert event.updates == []

    def test_world_update_event_with_updates(self) -> None:
        event = WorldUpdateEvent(updates=[{"door": "open"}])
        assert len(event.updates) == 1

    def test_sse_event_type_values(self) -> None:
        assert SSEEventType.TOKEN == "token"
        assert SSEEventType.DONE == "done"
        assert SSEEventType.ERROR == "error"
        assert SSEEventType.CRISIS_SIGNAL == "crisis_signal"

    def test_guide_voice_event_default_intensity(self) -> None:
        from src.api_gateway.sse.models import GuideVoiceEvent

        event = GuideVoiceEvent(content="Take your time.")
        assert event.intensity == "gentle"


# ---------------------------------------------------------------------------
# SSE format helper
# ---------------------------------------------------------------------------


class TestFormatSSE:
    def test_sse_format_contains_id_and_data(self) -> None:
        from src.api_gateway.sse.stream import _format_sse

        result = _format_sse("t1:0", {"type": "token", "content": "Hi"})
        assert result.startswith("id: t1:0\n")
        assert "data: " in result
        assert result.endswith("\n\n")

    def test_sse_format_json_payload(self) -> None:
        import json

        from src.api_gateway.sse.stream import _format_sse

        result = _format_sse("t1:1", {"type": "done", "turn_id": "abc"})
        data_line = [line for line in result.split("\n") if line.startswith("data:")][0]
        payload = json.loads(data_line[len("data: ") :])
        assert payload["turn_id"] == "abc"
