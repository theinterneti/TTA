"""
Gameplay Loop Data Models

This module provides comprehensive Pydantic models for therapeutic gameplay mechanics,
including user interactions, progress tracking, therapeutic metrics, and session management.
"""

from .core import (
    GameplaySession,
    NarrativeScene,
    UserChoice,
    ConsequenceSet,
    TherapeuticOutcome,
    GameplayState,
    SessionMetrics
)

from .interactions import (
    UserInteraction,
    InteractionType,
    InteractionContext,
    InteractionValidation,
    InteractionResponse
)

from .progress import (
    TherapeuticProgress,
    ProgressMetric,
    ProgressMilestone,
    SkillDevelopment,
    EmotionalGrowth,
    BehavioralChange
)

from .validation import (
    ValidationResult,
    ValidationRule,
    SafetyCheck,
    TherapeuticAlignment,
    ContentValidation
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
    "ContentValidation"
]
