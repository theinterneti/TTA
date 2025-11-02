"""Crisis detection and intervention component.

This component handles crisis detection, assessment, intervention protocols,
and escalation procedures for therapeutic safety.
"""

from .enums import CrisisLevel, CrisisType, EscalationStatus, InterventionType
from .escalation import HumanOversightEscalation
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
    "CrisisInterventionManager",
    "EmergencyProtocolEngine",
    "HumanOversightEscalation",
]
