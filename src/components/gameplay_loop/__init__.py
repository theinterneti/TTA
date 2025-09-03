"""
Core Gameplay Loop Components

This module provides the foundational components for the therapeutic text adventure
gameplay loop system, including narrative presentation, choice architecture,
consequence systems, and adaptive difficulty management.
"""

# Import social and collaborative features
from . import social
from .base import GameplayLoopComponent

# Import TTA system integration
from .integration import (
    IntegrationEndpoint,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationStatus,
    IntegrationType,
    TTASystemIntegration,
)

# Import models
from .models import (
    BehavioralChange,
    ConsequenceSet,
    ContentValidation,
    EmotionalGrowth,
    GameplaySession,
    GameplayState,
    InteractionContext,
    InteractionResponse,
    InteractionType,
    InteractionValidation,
    NarrativeScene,
    ProgressMetric,
    ProgressMilestone,
    SafetyCheck,
    SessionMetrics,
    SkillDevelopment,
    TherapeuticAlignment,
    TherapeuticOutcome,
    TherapeuticProgress,
    UserChoice,
    UserInteraction,
    ValidationResult,
    ValidationRule,
)

__all__ = [
    "GameplayLoopComponent",
    # Models will be added by the models.__init__.py
]
