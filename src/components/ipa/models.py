"""Pydantic models for IPA (Input Processing Agent) output.

ProcessedInput is the structured result the IPA produces from raw player text.
It flows into the WBA as the first stage of the IPA → WBA → NGA pipeline.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Intent(StrEnum):
    """Player intent classifications."""

    EXPLORE = "explore"
    INTERACT = "interact"
    QUERY = "query"
    ACTION = "action"
    JOURNAL = "journal"
    UNKNOWN = "unknown"


class ExtractedEntity(BaseModel):
    """A named entity extracted from the player's input."""

    name: str
    entity_type: str  # "npc", "location", "item", "concept"
    confidence: float = Field(ge=0.0, le=1.0)
    canonical_id: str | None = None  # Resolved Neo4j node ID, if known


class EmotionalTone(BaseModel):
    """Emotional tone detected in the player's input."""

    primary: str = "neutral"
    intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    safety_signal: bool = False  # True → feed crisis detection


class ProcessedInput(BaseModel):
    """Structured output of the IPA — fed directly into the WBA.

    Carries all derived signals from raw player text: intent classification,
    extracted entities, and emotional tone for pacing / safety systems.
    """

    raw_text: str
    normalized_text: str
    intent: Intent = Intent.UNKNOWN
    intent_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    entities: list[ExtractedEntity] = Field(default_factory=list)
    emotional_tone: EmotionalTone = Field(default_factory=EmotionalTone)
    session_id: str = ""
    player_id: str = ""
    location_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def npc_names(self) -> list[str]:
        return [e.name for e in self.entities if e.entity_type == "npc"]

    @property
    def location_references(self) -> list[str]:
        return [e.name for e in self.entities if e.entity_type == "location"]

    @property
    def needs_safety_check(self) -> bool:
        return self.emotional_tone.safety_signal
