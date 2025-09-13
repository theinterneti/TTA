"""
Narrative Engine for Therapeutic Gameplay Loop

This module provides the comprehensive narrative engine for therapeutic text adventures,
including scene management, choice processing, flow control, and therapeutic integration.
"""

from .character_development_system import (
    AbilityType,
    CharacterAbility,
    CharacterAttribute,
    CharacterAttributeLevel,
    CharacterDevelopmentEvent,
    CharacterDevelopmentSystem,
    CharacterMilestone,
    CharacterMilestoneAchievement,
    DevelopmentTrigger,
)
from .choice_processor import (
    ChoiceConsequence,
    ChoiceContext,
    ChoiceProcessor,
    ChoiceValidator,
)
from .engine import EngineState, NarrativeEngine, NarrativeEngineConfig, NarrativeMode
from .events import ChoiceEvent, NarrativeEvent, ProgressEvent, SafetyEvent, SceneEvent
from .flow_controller import BranchingLogic, FlowController, FlowDecision, NarrativeFlow
from .narrative_loader import (
    ChoiceDefinition,
    NarrativeDefinition,
    NarrativeLoader,
    SceneDefinition,
)
from .replayability_system import (
    AlternativePath,
    ComparisonMetric,
    ExplorationMode,
    ExplorationSession,
    ExplorationSnapshot,
    PathComparison,
    PathType,
    ReplayabilitySystem,
)
from .scene_manager import SceneContext, SceneManager, SceneTransition, SceneValidator
from .therapeutic_integration_system import (
    IntegrationStrategy,
    ProgressMilestone,
    ResistancePattern,
    ResistanceType,
    TherapeuticApproach,
    TherapeuticConcept,
    TherapeuticIntegration,
    TherapeuticIntegrationSystem,
    TherapeuticProgress,
)
from .therapeutic_integrator import (
    ProgressTracker,
    SafetyMonitor,
    TherapeuticContext,
    TherapeuticIntegrator,
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
    "CharacterAttributeLevel",
    # Replayability and Exploration System
    "ReplayabilitySystem",
    "ExplorationSnapshot",
    "AlternativePath",
    "PathComparison",
    "ExplorationSession",
    "ExplorationMode",
    "PathType",
    "ComparisonMetric",
]
