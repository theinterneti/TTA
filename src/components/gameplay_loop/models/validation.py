"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Models/Validation]]

# Logseq: [[TTA/Components/Gameplay_loop/Models/Validation]]
Validation Models for Gameplay Loop

This module defines models for validation, safety checks, and therapeutic validation
within the therapeutic text adventure system.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .core import DifficultyLevel, EmotionalState


class ValidationStatus(str, Enum):
    """Status of validation checks."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"
    SKIPPED = "skipped"


class SafetyLevel(str, Enum):
    """Safety levels for content and interactions."""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    CRISIS = "crisis"


class ValidationType(str, Enum):
    """Types of validation checks."""

    CONTENT_SAFETY = "content_safety"
    THERAPEUTIC_APPROPRIATENESS = "therapeutic_appropriateness"
    EMOTIONAL_SAFETY = "emotional_safety"
    CHOICE_VALIDITY = "choice_validity"
    PROGRESSION_LOGIC = "progression_logic"
    USER_READINESS = "user_readiness"


class ValidationResult(BaseModel):
    """Result of a validation check."""

    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")

    # Validation details
    validation_type: ValidationType = Field(..., description="Type of validation")
    status: ValidationStatus = Field(..., description="Validation status")

    # Content being validated
    content_type: str = Field(..., description="Type of content validated")
    content_id: str | None = Field(None, description="ID of content validated")

    # Results
    is_valid: bool = Field(..., description="Whether validation passed")
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in validation"
    )

    # Issues and recommendations
    issues_found: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    # Context
    user_context: dict[str, Any] = Field(default_factory=dict)
    therapeutic_context: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validator_version: str = Field(default="1.0.0")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SafetyCheck(BaseModel):
    """Safety check for user emotional state and content appropriateness."""

    check_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")

    # Safety assessment
    safety_level: SafetyLevel = Field(..., description="Assessed safety level")
    emotional_state: EmotionalState = Field(..., description="User's emotional state")

    # Risk factors
    risk_factors: list[str] = Field(default_factory=list)
    protective_factors: list[str] = Field(default_factory=list)

    # Triggers and concerns
    potential_triggers: list[str] = Field(default_factory=list)
    safety_concerns: list[str] = Field(default_factory=list)

    # Recommendations
    immediate_actions: list[str] = Field(default_factory=list)
    monitoring_required: bool = Field(default=False)
    intervention_recommended: bool = Field(default=False)

    # Crisis indicators
    crisis_indicators: list[str] = Field(default_factory=list)
    requires_immediate_attention: bool = Field(default=False)

    # Context
    triggering_content: str | None = Field(
        None, description="Content that triggered this check"
    )
    user_history: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = Field(None, description="When this check expires")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TherapeuticValidation(BaseModel):
    """Validation of therapeutic appropriateness and effectiveness."""

    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")

    # Content being validated
    content_type: str = Field(..., description="Type of therapeutic content")
    content_description: str = Field(..., description="Description of content")

    # Therapeutic assessment
    therapeutic_appropriateness: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_based: bool = Field(
        default=False, description="Whether content is evidence-based"
    )
    contraindications: list[str] = Field(default_factory=list)

    # User suitability
    user_readiness: float = Field(default=0.0, ge=0.0, le=1.0)
    difficulty_appropriate: bool = Field(default=True)
    timing_appropriate: bool = Field(default=True)

    # Therapeutic goals alignment
    aligned_goals: list[str] = Field(default_factory=list)
    conflicting_goals: list[str] = Field(default_factory=list)

    # Effectiveness prediction
    predicted_effectiveness: float = Field(default=0.0, ge=0.0, le=1.0)
    potential_benefits: list[str] = Field(default_factory=list)
    potential_risks: list[str] = Field(default_factory=list)

    # Recommendations
    modifications_suggested: list[str] = Field(default_factory=list)
    alternative_approaches: list[str] = Field(default_factory=list)
    follow_up_required: bool = Field(default=False)

    # Validation outcome
    is_approved: bool = Field(default=False)
    approval_conditions: list[str] = Field(default_factory=list)

    # Context
    user_therapeutic_profile: dict[str, Any] = Field(default_factory=dict)
    session_context: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validator_credentials: str | None = Field(None)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ContentValidation(BaseModel):
    """Validation of narrative content for safety and appropriateness."""

    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str = Field(..., description="Content identifier")

    # Content details
    content_type: str = Field(..., description="Type of content")
    content_text: str = Field(..., description="Content text")

    # Safety validation
    contains_triggers: bool = Field(default=False)
    trigger_types: list[str] = Field(default_factory=list)
    safety_rating: SafetyLevel = Field(default=SafetyLevel.SAFE)

    # Content quality
    narrative_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    therapeutic_value: float = Field(default=0.0, ge=0.0, le=1.0)
    age_appropriate: bool = Field(default=True)

    # Language and tone
    language_appropriate: bool = Field(default=True)
    tone_assessment: str = Field(default="neutral")
    complexity_level: DifficultyLevel = Field(default=DifficultyLevel.STANDARD)

    # Bias and sensitivity
    bias_detected: bool = Field(default=False)
    bias_types: list[str] = Field(default_factory=list)
    cultural_sensitivity: float = Field(default=1.0, ge=0.0, le=1.0)

    # Validation results
    is_approved: bool = Field(default=False)
    requires_modification: bool = Field(default=False)
    modification_suggestions: list[str] = Field(default_factory=list)

    # Metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validation_version: str = Field(default="1.0.0")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
