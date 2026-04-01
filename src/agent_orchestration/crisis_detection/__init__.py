"""Crisis detection and intervention component.

This component handles crisis detection, assessment, intervention protocols,
and escalation procedures for therapeutic safety.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Crisis_detection/__init__]]

from .detector import CrisisDetector
from .enums import CrisisLevel, CrisisType, EscalationStatus, InterventionType
from .escalation import HumanOversightEscalation
from .interop import (
    CRISIS_TO_SAFETY,
    SAFETY_TO_CRISIS,
    crisis_level_to_safety_level,
    safety_level_to_crisis_level,
)
from .manager import CrisisInterventionManager
from .models import CrisisAssessment, CrisisIntervention, InterventionAction
from .protocols import EmergencyProtocolEngine

__all__ = [
    # Enums
    "CrisisType",
    "CrisisLevel",
    "InterventionType",
    "EscalationStatus",
    # Models
    "CrisisAssessment",
    "InterventionAction",
    "CrisisIntervention",
    # Classes
    "CrisisDetector",
    "CrisisInterventionManager",
    "EmergencyProtocolEngine",
    "HumanOversightEscalation",
    # Interop
    "SAFETY_TO_CRISIS",
    "CRISIS_TO_SAFETY",
    "safety_level_to_crisis_level",
    "crisis_level_to_safety_level",
]
