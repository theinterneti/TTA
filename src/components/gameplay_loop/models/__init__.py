"""
Gameplay Loop Data Models

This module provides comprehensive Pydantic models for therapeutic gameplay mechanics,
including user interactions, progress tracking, therapeutic metrics, and session management.
"""

from .core import (
    ConsequenceSet,
    GameplaySession,
    GameplayState,
    NarrativeScene,
    SessionMetrics,
    TherapeuticOutcome,
    UserChoice,
)
from .interactions import (
    InteractionContext,
    InteractionResponse,
    InteractionType,
    InteractionValidation,
    UserInteraction,
)
from .progress import (
    BehavioralChange,
    EmotionalGrowth,
    ProgressMetric,
    ProgressMilestone,
    SkillDevelopment,
    TherapeuticProgress,
)
from .validation import (
    ContentValidation,
    SafetyCheck,
    TherapeuticAlignment,
    ValidationResult,
    ValidationRule,
)

__all__ = [
    # Core gameplay models
    "GameplaySession",
    "NarrativeScene",
    "UserChoice",
    "ConsequenceSet",
    "TherapeuticOutcome",
    "GameplayState",
    "SessionMetrics",
    # User interaction models
    "UserInteraction",
    "InteractionType",
    "InteractionContext",
    "InteractionValidation",
    "InteractionResponse",
    # Progress tracking models
    "TherapeuticProgress",
    "ProgressMetric",
    "ProgressMilestone",
    "SkillDevelopment",
    "EmotionalGrowth",
    "BehavioralChange",
    # Validation models
    "ValidationResult",
    "ValidationRule",
    "SafetyCheck",
    "TherapeuticAlignment",
    "ContentValidation",
]
