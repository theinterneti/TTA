from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConsistencyIssueType(Enum):
    LORE_VIOLATION = "lore_violation"
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    WORLD_RULE_VIOLATION = "world_rule_violation"
    TEMPORAL_PARADOX = "temporal_paradox"
    CAUSAL_INCONSISTENCY = "causal_inconsistency"
    THEMATIC_CONFLICT = "thematic_conflict"
    THERAPEUTIC_MISALIGNMENT = "therapeutic_misalignment"


@dataclass
class ConsistencyIssue:
    issue_id: str
    issue_type: ConsistencyIssueType
    severity: ValidationSeverity
    description: str
    related_content_ids: list[str] = field(default_factory=list)
    affected_elements: list[str] = field(default_factory=list)
    suggested_fix: str = ""
    confidence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    is_valid: bool
    consistency_score: float
    detected_issues: list[ConsistencyIssue] = field(default_factory=list)
    lore_consistency: float = 0.0
    lore_compliance: float = 0.0
    character_consistency: float = 0.0
    world_rule_consistency: float = 0.0
    causal_consistency: float = 0.0
    therapeutic_alignment: float = 0.0
    suggested_corrections: list[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NarrativeContent:
    content_id: str
    content_type: str
    text: str
    related_characters: list[str] = field(default_factory=list)
    related_locations: list[str] = field(default_factory=list)
    related_events: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    therapeutic_concepts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    # Aliases for backward compatibility
    @property
    def characters(self) -> list[str]:
        """Alias for related_characters."""
        return self.related_characters

    @property
    def locations(self) -> list[str]:
        """Alias for related_locations."""
        return self.related_locations


@dataclass
class LoreEntry:
    lore_id: str
    category: str
    title: str
    description: str
    canonical: bool = True
    related_entries: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    importance_weight: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Contradiction:
    contradiction_id: str
    type: str
    severity: ValidationSeverity
    description: str
    related_issues: list[str] = field(default_factory=list)
    resolution_suggestions: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativeSolution:
    solution_id: str
    solution_type: str
    description: str
    benefits: list[str] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)
    narrative_cost: float = 0.0
    player_impact: float = 0.0
    required_changes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NarrativeResolution:
    resolution_id: str
    conflict_id: str
    solution_used: CreativeSolution
    outcome_description: str
    is_successful: bool
    resolution_timestamp: datetime = field(default_factory=datetime.now)
    effectiveness_rating: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetroactiveChange:
    change_id: str
    target_content_id: str
    change_type: str
    description: str
    justification: str = ""
    in_world_explanation: str = ""
    impact_scope: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StorylineThread:
    thread_id: str
    title: str
    participants: list[str] = field(default_factory=list)
    related_events: list[str] = field(default_factory=list)
    convergence_points: list[str] = field(default_factory=list)
    resolution_target: str | None = None
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConvergenceValidation:
    session_id: str
    storyline_count: int
    is_convergent: bool
    strong_connections: list[str] = field(default_factory=list)
    weak_connections: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    convergence_score: float = 0.0
