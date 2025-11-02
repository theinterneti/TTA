"""Crisis detection data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import CrisisLevel, CrisisType, EscalationStatus, InterventionType


@dataclass
class CrisisAssessment:
    """Assessment of a crisis situation."""

    crisis_level: CrisisLevel
    crisis_types: list[CrisisType]
    confidence: float  # 0.0 to 1.0
    risk_factors: list[str]
    protective_factors: list[str]
    immediate_risk: bool
    intervention_recommended: InterventionType
    escalation_required: bool
    assessment_timestamp: float
    context: dict[str, Any] | None = None


@dataclass
class InterventionAction:
    """A specific intervention action taken."""

    action_type: InterventionType
    description: str
    timestamp: float
    success: bool
    response_time_ms: float
    metadata: dict[str, Any] | None = None


@dataclass
class CrisisIntervention:
    """Complete crisis intervention record."""

    intervention_id: str
    session_id: str
    user_id: str
    crisis_assessment: CrisisAssessment
    actions_taken: list[InterventionAction] = field(default_factory=list)
    escalation_status: EscalationStatus = EscalationStatus.NONE
    resolution_status: str = "active"
    created_timestamp: float = 0.0
    resolved_timestamp: float | None = None
    human_notified: bool = False
    emergency_contacted: bool = False
    follow_up_required: bool = True
