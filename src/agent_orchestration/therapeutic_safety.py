"""Backward compatibility shim for therapeutic_safety module.

This module re-exports all symbols from the new component structure
to maintain backward compatibility with existing code.

New code should import directly from the component modules:
- from agent_orchestration.safety_validation import SafetyLevel
- from agent_orchestration.crisis_detection import CrisisType
- from agent_orchestration.therapeutic_scoring import TherapeuticValidator
- from agent_orchestration.safety_monitoring import SafetyService
"""

# Logseq: [[TTA.dev/Agent_orchestration/Therapeutic_safety]]

# Re-export all symbols from new components
from .crisis_detection import (
    CrisisAssessment,
    CrisisIntervention,
    CrisisInterventionManager,
    CrisisLevel,
    CrisisType,
    EmergencyProtocolEngine,
    EscalationStatus,
    HumanOversightEscalation,
    InterventionAction,
    InterventionType,
)
from .safety_monitoring import (
    SafetyMonitoringDashboard,
    SafetyRulesProvider,
    SafetyService,
    get_global_safety_service,
    set_global_safety_service_for_testing,
)
from .safety_validation import (
    SafetyLevel,
    SafetyRule,
    SafetyRuleEngine,
    ValidationFinding,
    ValidationResult,
    ValidationType,
)
from .therapeutic_scoring import TherapeuticContext, TherapeuticValidator

__all__ = [
    # safety_validation
    "SafetyLevel",
    "ValidationType",
    "ValidationFinding",
    "ValidationResult",
    "SafetyRule",
    "SafetyRuleEngine",
    # crisis_detection
    "CrisisType",
    "CrisisLevel",
    "InterventionType",
    "EscalationStatus",
    "CrisisAssessment",
    "InterventionAction",
    "CrisisIntervention",
    "CrisisInterventionManager",
    "EmergencyProtocolEngine",
    "HumanOversightEscalation",
    # therapeutic_scoring
    "TherapeuticContext",
    "TherapeuticValidator",
    # safety_monitoring
    "SafetyMonitoringDashboard",
    "SafetyRulesProvider",
    "SafetyService",
    "get_global_safety_service",
    "set_global_safety_service_for_testing",
]
