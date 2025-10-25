"""Therapeutic scoring enumerations."""

from enum import Enum


class TherapeuticContext(str, Enum):
    """Therapeutic contexts for content validation."""

    GENERAL_THERAPY = "general_therapy"
    CRISIS_INTERVENTION = "crisis_intervention"
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS = "mindfulness"
    TRAUMA_INFORMED = "trauma_informed"
    ADDICTION_RECOVERY = "addiction_recovery"
