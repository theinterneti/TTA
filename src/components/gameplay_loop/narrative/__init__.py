"""
Narrative Engine for Therapeutic Gameplay Loop

This module provides the comprehensive narrative engine for therapeutic text adventures,
including scene management, choice processing, flow control, and therapeutic integration.
"""

from .engine import (
    NarrativeEngine,
    NarrativeEngineConfig,
    NarrativeMode,
    EngineState
)

from .scene_manager import (
    SceneManager,
    SceneContext,
    SceneTransition,
    SceneValidator
)

from .choice_processor import (
    ChoiceProcessor,
    ChoiceContext,
    ChoiceValidator,
    ChoiceConsequence
)

from .flow_controller import (
    FlowController,
    NarrativeFlow,
    FlowDecision,
    BranchingLogic
)

from .therapeutic_integrator import (
    TherapeuticIntegrator,
    TherapeuticContext,
    SafetyMonitor,
    ProgressTracker
)

from .therapeutic_integration_system import (
    TherapeuticIntegrationSystem,
    TherapeuticConcept,
    TherapeuticProgress,
    ResistancePattern,
    TherapeuticIntegration,
    TherapeuticApproach,
    IntegrationStrategy,
    ProgressMilestone,
    ResistanceType
)

from .character_development_system import (
    CharacterDevelopmentSystem,
    CharacterAttribute,
    CharacterMilestone,
    DevelopmentTrigger,
    AbilityType,
    CharacterDevelopmentEvent,
    CharacterMilestoneAchievement,
    CharacterAbility,
    CharacterAttributeLevel
)

from .narrative_loader import (
    NarrativeLoader,
    NarrativeDefinition,
    SceneDefinition,
    ChoiceDefinition
)

from .events import (
    NarrativeEvent,
    SceneEvent,
    ChoiceEvent,
    ProgressEvent,
    SafetyEvent
)

__all__ = [
    # Core engine
    "NarrativeEngine",
    "NarrativeEngineConfig",
    "NarrativeMode",
    "EngineState",
    
    # Scene management
    "SceneManager",
    "SceneContext",
    "SceneTransition",
    "SceneValidator",
    
    # Choice processing
    "ChoiceProcessor",
    "ChoiceContext",
    "ChoiceValidator",
    "ChoiceConsequence",
    
    # Flow control
    "FlowController",
    "NarrativeFlow",
    "FlowDecision",
    "BranchingLogic",
    
    # Therapeutic integration
    "TherapeuticIntegrator",
    "TherapeuticContext",
    "SafetyMonitor",
    "ProgressTracker",
    
    # Narrative loading
    "NarrativeLoader",
    "NarrativeDefinition",
    "SceneDefinition",
    "ChoiceDefinition",
    
    # Events
    "NarrativeEvent",
    "SceneEvent",
    "ChoiceEvent",
    "ProgressEvent",
    "SafetyEvent",

    # Therapeutic Integration System
    "TherapeuticIntegrationSystem",
    "TherapeuticConcept",
    "TherapeuticProgress",
    "ResistancePattern",
    "TherapeuticIntegration",
    "TherapeuticApproach",
    "IntegrationStrategy",
    "ProgressMilestone",
    "ResistanceType",

    # Character Development System
    "CharacterDevelopmentSystem",
    "CharacterAttribute",
    "CharacterMilestone",
    "DevelopmentTrigger",
    "AbilityType",
    "CharacterDevelopmentEvent",
    "CharacterMilestoneAchievement",
    "CharacterAbility",
    "CharacterAttributeLevel"
]
