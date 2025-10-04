"""
Core Gameplay Loop Data Models

This module provides the foundational data models for the therapeutic text adventure
gameplay loop system, including session state, narrative scenes, choices, and consequences.
"""

from .core import (
    Choice,
    ConsequenceSet,
    DifficultyLevel,
    EmotionalState,
    GameplayMetrics,
    Scene,
    SessionState,
    TherapeuticContext,
)
from .interactions import (
    ChoiceOutcome,
    NarrativeEvent,
    TherapeuticIntervention,
    UserChoice,
)
from .progress import (
    CharacterState,
    ProgressMarker,
    SkillDevelopment,
    TherapeuticProgress,
)
from .validation import SafetyCheck, TherapeuticValidation, ValidationResult

__all__ = [
    # Core models
    "SessionState",
    "Scene",
    "Choice",
    "ConsequenceSet",
    "TherapeuticContext",
    "EmotionalState",
    "DifficultyLevel",
    "GameplayMetrics",
    # Interaction models
    "UserChoice",
    "ChoiceOutcome",
    "NarrativeEvent",
    "TherapeuticIntervention",
    # Progress models
    "ProgressMarker",
    "TherapeuticProgress",
    "CharacterState",
    "SkillDevelopment",
    # Validation models
    "ValidationResult",
    "SafetyCheck",
    "TherapeuticValidation",
]
