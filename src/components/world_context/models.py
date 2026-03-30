"""Pydantic models for WorldContext — the structured output of Neo4j traversal.

Issue: #275
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LocationFact(BaseModel):
    """Properties of the player's current location node."""

    id: str
    name: str
    description: str | None = None
    region: str | None = None
    atmosphere: str | None = None
    is_accessible: bool = True
    extra: dict[str, Any] = Field(default_factory=dict)


class NPCState(BaseModel):
    """Snapshot of an NPC present in the current location."""

    id: str
    name: str
    role: str | None = None
    emotional_state: str | None = None
    disposition_toward_player: str | None = None
    is_active: bool = True
    extra: dict[str, Any] = Field(default_factory=dict)


class WorldEventSummary(BaseModel):
    """Summary of an active WorldEvent affecting the current context."""

    id: str
    name: str
    description: str | None = None
    event_type: str | None = None
    is_active: bool = True
    extra: dict[str, Any] = Field(default_factory=dict)


class WorldRuleSummary(BaseModel):
    """Summary of a WorldRule applicable in the current context."""

    id: str
    name: str
    rule_text: str
    rule_type: str | None = None
    scope: str | None = None
    priority: int = 0
    extra: dict[str, Any] = Field(default_factory=dict)


class ConnectedLocation(BaseModel):
    """A location reachable from the current location via CONNECTED_TO."""

    id: str
    name: str
    direction: str | None = None
    distance: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ZoneSummary(BaseModel):
    """Zone that contains the current location."""

    id: str
    name: str
    description: str | None = None
    zone_type: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class WorldContext(BaseModel):
    """Full traversal result assembled by WorldContextBuilder.

    Tiers:
    - depth >= 1: location + direct location rules
    - depth >= 2: + NPCs, active events, connected locations
    - depth >= 3: + zone, zone/faction rules
    """

    location_id: str
    location: LocationFact
    npcs: list[NPCState] = Field(default_factory=list)
    active_events: list[WorldEventSummary] = Field(default_factory=list)
    rules: list[WorldRuleSummary] = Field(default_factory=list)
    connected_locations: list[ConnectedLocation] = Field(default_factory=list)
    zone: ZoneSummary | None = None
    traversal_depth: int = Field(default=3, ge=1, le=3)
    query_time_ms: float | None = None
