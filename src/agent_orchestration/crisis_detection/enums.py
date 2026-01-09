"""Crisis detection enumerations."""

# Logseq: [[TTA.dev/Agent_orchestration/Crisis_detection/Enums]]

from enum import Enum


class CrisisType(str, Enum):
    """Types of crisis situations that can be detected."""

    SELF_HARM = "self_harm"
    SUICIDAL_IDEATION = "suicidal_ideation"
    SUBSTANCE_ABUSE = "substance_abuse"
    DOMESTIC_VIOLENCE = "domestic_violence"
    EATING_DISORDER = "eating_disorder"
    PANIC_ATTACK = "panic_attack"
    SEVERE_DEPRESSION = "severe_depression"


class CrisisLevel(str, Enum):
    """Crisis severity levels for intervention protocols."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(str, Enum):
    """Types of crisis interventions available."""

    AUTOMATED_RESPONSE = "automated_response"
    HUMAN_OVERSIGHT = "human_oversight"
    EMERGENCY_SERVICES = "emergency_services"
    THERAPEUTIC_REFERRAL = "therapeutic_referral"


class EscalationStatus(str, Enum):
    """Status of crisis escalation."""

    NONE = "none"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
