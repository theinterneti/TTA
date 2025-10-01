from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NarrativeScale(Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    EPIC_TERM = "epic_term"


@dataclass
class PlayerChoice:
    choice_id: str
    session_id: str
    choice_text: str
    metadata: dict[str, Any] | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeResponse:
    content: str
    response_type: str = "narrative"
    choices: list[dict[str, Any]] = None
    metadata: dict[str, Any] | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeStatus:
    session_id: str
    current_scale: NarrativeScale
    active_threads: list[str]
    last_updated: datetime | None = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class NarrativeEvent:
    event_id: str
    scale: NarrativeScale
    timestamp: datetime
    causal_links: dict[str, float] = field(default_factory=dict)
    description: str = ""
    participants: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactAssessment:
    scale: NarrativeScale
    magnitude: float
    affected_elements: list[str] = field(default_factory=list)
    causal_strength: float = 0.0
    therapeutic_alignment: float = 0.0
    confidence_score: float = 0.0
    temporal_decay: float = 1.0
    cross_scale_influences: dict[NarrativeScale, float] = field(default_factory=dict)


@dataclass
class ScaleConflict:
    conflict_id: str
    involved_scales: set[NarrativeScale]
    conflict_type: str
    summary: str
    affected_events: list[str] = field(default_factory=list)
    resolution_priority: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    resolution_id: str
    conflict_id: str
    resolution_type: str
    description: str
    effectiveness_score: float = 0.0
    narrative_cost: float = 0.0
    player_impact: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergentEvent:
    event_id: str
    event_type: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
