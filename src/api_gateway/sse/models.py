"""

# Logseq: [[TTA.dev/Api_gateway/SSE/Models]]
Pydantic models for the SSE event payload types streamed to the player client.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class SSEEventType(StrEnum):
    TOKEN = "token"
    GUIDE_VOICE = "guide_voice"
    WORLD_UPDATE = "world_update"
    CRISIS_SIGNAL = "crisis_signal"
    DONE = "done"
    ERROR = "error"


class TokenEvent(BaseModel):
    type: SSEEventType = SSEEventType.TOKEN
    content: str


class GuideVoiceEvent(BaseModel):
    type: SSEEventType = SSEEventType.GUIDE_VOICE
    content: str
    intensity: str = "gentle"  # "gentle" | "firm" | "urgent"


class WorldUpdateEvent(BaseModel):
    type: SSEEventType = SSEEventType.WORLD_UPDATE
    updates: list[dict[str, Any]] = []


class CrisisSignalEvent(BaseModel):
    type: SSEEventType = SSEEventType.CRISIS_SIGNAL
    level: str
    resource_url: str | None = None


class DoneEvent(BaseModel):
    type: SSEEventType = SSEEventType.DONE
    turn_id: str
    tension_level: float = 0.0


class ErrorEvent(BaseModel):
    type: SSEEventType = SSEEventType.ERROR
    code: str
    message: str
