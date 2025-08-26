"""
Data Models for Therapeutic Safety Content Validation

This module defines all data models and structures used throughout the
therapeutic safety validation system.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .enums import (
    CrisisLevel, BiasType, ContentType, ValidationAction, SafetyLevel,
    TherapeuticFramework, ValidationStatus, RiskCategory, ProtectiveFactor,
    ValidationPriority, ContentSource, ValidationScope, AgeGroup, MaturityLevel,
    TherapeuticGoalCategory, InterventionType, ValidationComponent
)


@dataclass
class ContentPayload:
    """Payload containing content to be validated."""
    content_id: str = field(default_factory=lambda: str(uuid4()))
    content_type: ContentType = ContentType.NARRATIVE_SCENE
    content_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: ContentSource = ContentSource.AI_GENERATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Content structure
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Therapeutic context
    therapeutic_goals: List[TherapeuticGoalCategory] = field(default_factory=list)
    target_age_group: Optional[AgeGroup] = None
    maturity_level: MaturityLevel = MaturityLevel.ALL_AGES
    
    def get_word_count(self) -> int:
        """Get word count of content text."""
        return len(self.content_text.split()) if self.content_text else 0
    
    def get_character_count(self) -> int:
        """Get character count of content text."""
        return len(self.content_text) if self.content_text else 0


class ValidationContext(BaseModel):
    """Context for content validation."""
    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="User ID for context")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    
    # Validation settings
    validation_scope: ValidationScope = ValidationScope.STANDARD
    priority: ValidationPriority = ValidationPriority.NORMAL
    timeout_ms: int = Field(default=200, ge=50, le=5000)
    
    # User context
    user_age_group: Optional[AgeGroup] = None
    user_therapeutic_goals: List[TherapeuticGoalCategory] = Field(default_factory=list)
    user_risk_factors: List[RiskCategory] = Field(default_factory=list)
    user_protective_factors: List[ProtectiveFactor] = Field(default_factory=list)
    
    # Session context
    current_safety_level: SafetyLevel = SafetyLevel.SAFE
    recent_crisis_indicators: List[str] = Field(default_factory=list)
    therapeutic_framework: Optional[TherapeuticFramework] = None
    
    # Validation preferences
    strict_mode: bool = False
    allow_sensitive_content: bool = False
    require_human_review: bool = False
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    @field_validator('timeout_ms')
    @classmethod
    def validate_timeout(cls, v):
        if v < 50 or v > 5000:
            raise ValueError('Timeout must be between 50ms and 5000ms')
        return v


class ValidationResult(BaseModel):
    """Result of content validation."""
    validation_id: str = Field(..., description="Validation ID")
    content_id: str = Field(..., description="Content ID")
    
    # Overall result
    status: ValidationStatus = ValidationStatus.PENDING
    action: ValidationAction = ValidationAction.APPROVE
    overall_safety_level: SafetyLevel = SafetyLevel.SAFE
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Component results
    component_results: Dict[ValidationComponent, Dict[str, Any]] = Field(default_factory=dict)
    
    # Risk assessment
    identified_risks: List[RiskCategory] = Field(default_factory=list)
    risk_scores: Dict[RiskCategory, float] = Field(default_factory=dict)
    protective_factors: List[ProtectiveFactor] = Field(default_factory=list)
    
    # Crisis assessment
    crisis_level: CrisisLevel = CrisisLevel.NONE
    crisis_indicators: List[str] = Field(default_factory=list)
    immediate_intervention_needed: bool = False
    
    # Bias detection
    detected_biases: List[BiasType] = Field(default_factory=list)
    bias_scores: Dict[BiasType, float] = Field(default_factory=dict)
    
    # Therapeutic alignment
    therapeutic_alignment_score: float = Field(default=0.0, ge=0.0, le=1.0)
    aligned_frameworks: List[TherapeuticFramework] = Field(default_factory=list)
    misaligned_aspects: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    required_modifications: List[str] = Field(default_factory=list)
    alternative_content_suggestions: List[str] = Field(default_factory=list)
    
    # Processing metadata
    processing_time_ms: float = 0.0
    validation_components_used: List[ValidationComponent] = Field(default_factory=list)
    cache_hit: bool = False
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def is_safe(self) -> bool:
        """Check if content is considered safe."""
        return (self.action in [ValidationAction.APPROVE, ValidationAction.WARN] and
                self.crisis_level <= CrisisLevel.LOW and
                not self.immediate_intervention_needed)
    
    def requires_intervention(self) -> bool:
        """Check if immediate intervention is required."""
        return (self.immediate_intervention_needed or
                self.crisis_level >= CrisisLevel.HIGH or
                self.action == ValidationAction.ESCALATE)
    
    def get_processing_time(self) -> timedelta:
        """Get total processing time."""
        if self.completed_at:
            return self.completed_at - self.started_at
        return datetime.utcnow() - self.started_at


@dataclass
class CrisisAssessment:
    """Assessment of crisis indicators in content."""
    assessment_id: str = field(default_factory=lambda: str(uuid4()))
    content_id: str = ""
    
    # Crisis level assessment
    crisis_level: CrisisLevel = CrisisLevel.NONE
    confidence: float = 0.0
    
    # Specific indicators
    suicide_risk_indicators: List[str] = field(default_factory=list)
    self_harm_indicators: List[str] = field(default_factory=list)
    violence_indicators: List[str] = field(default_factory=list)
    substance_abuse_indicators: List[str] = field(default_factory=list)
    
    # Risk factors
    identified_risk_factors: List[RiskCategory] = field(default_factory=list)
    risk_factor_scores: Dict[RiskCategory, float] = field(default_factory=dict)
    
    # Protective factors
    identified_protective_factors: List[ProtectiveFactor] = field(default_factory=list)
    protective_factor_scores: Dict[ProtectiveFactor, float] = field(default_factory=dict)
    
    # Recommendations
    immediate_actions: List[InterventionType] = field(default_factory=list)
    recommended_resources: List[str] = field(default_factory=list)
    follow_up_needed: bool = False
    
    # Metadata
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    assessment_method: str = "rule_based"
    
    def get_overall_risk_score(self) -> float:
        """Calculate overall risk score."""
        if not self.risk_factor_scores:
            return 0.0
        return sum(self.risk_factor_scores.values()) / len(self.risk_factor_scores)
    
    def get_protective_score(self) -> float:
        """Calculate overall protective factor score."""
        if not self.protective_factor_scores:
            return 0.0
        return sum(self.protective_factor_scores.values()) / len(self.protective_factor_scores)


@dataclass
class BiasDetectionResult:
    """Result of bias detection analysis."""
    detection_id: str = field(default_factory=lambda: str(uuid4()))
    content_id: str = ""
    
    # Detected biases
    detected_biases: List[BiasType] = field(default_factory=list)
    bias_scores: Dict[BiasType, float] = field(default_factory=dict)
    bias_examples: Dict[BiasType, List[str]] = field(default_factory=dict)
    
    # Overall assessment
    overall_bias_score: float = 0.0
    bias_free_confidence: float = 0.0
    
    # Recommendations
    bias_mitigation_suggestions: List[str] = field(default_factory=list)
    inclusive_alternatives: List[str] = field(default_factory=list)
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.utcnow)
    detection_method: str = "rule_based"
    
    def has_significant_bias(self, threshold: float = 0.7) -> bool:
        """Check if content has significant bias."""
        return self.overall_bias_score > threshold


class TherapeuticContext(BaseModel):
    """Therapeutic context for validation."""
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = None
    
    # Therapeutic goals and progress
    primary_goals: List[TherapeuticGoalCategory] = Field(default_factory=list)
    secondary_goals: List[TherapeuticGoalCategory] = Field(default_factory=list)
    current_progress: Dict[TherapeuticGoalCategory, float] = Field(default_factory=dict)
    
    # Therapeutic framework
    preferred_framework: Optional[TherapeuticFramework] = None
    contraindicated_approaches: List[TherapeuticFramework] = Field(default_factory=list)
    
    # Risk profile
    risk_factors: List[RiskCategory] = Field(default_factory=list)
    protective_factors: List[ProtectiveFactor] = Field(default_factory=list)
    crisis_history: List[str] = Field(default_factory=list)
    
    # Current state
    current_emotional_state: Dict[str, float] = Field(default_factory=dict)
    recent_triggers: List[str] = Field(default_factory=list)
    coping_strategies: List[str] = Field(default_factory=list)
    
    # Preferences
    content_preferences: Dict[str, Any] = Field(default_factory=dict)
    trigger_warnings_enabled: bool = True
    safe_words: List[str] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserContext(BaseModel):
    """User context for validation."""
    user_id: str = Field(..., description="User ID")
    
    # Demographics
    age_group: Optional[AgeGroup] = None
    cultural_background: List[str] = Field(default_factory=list)
    language_preferences: List[str] = Field(default_factory=list)
    
    # Accessibility needs
    accessibility_requirements: List[str] = Field(default_factory=list)
    content_format_preferences: List[str] = Field(default_factory=list)
    
    # Safety preferences
    safety_level_preference: SafetyLevel = SafetyLevel.SAFE
    content_filtering_level: MaturityLevel = MaturityLevel.ALL_AGES
    trigger_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # History
    previous_crisis_events: List[str] = Field(default_factory=list)
    successful_interventions: List[str] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)


class ContentPreferences(BaseModel):
    """Content preferences for validation."""
    user_id: str = Field(..., description="User ID")
    
    # Content filtering
    allowed_content_types: List[ContentType] = Field(default_factory=list)
    blocked_content_types: List[ContentType] = Field(default_factory=list)
    
    # Topic preferences
    preferred_topics: List[str] = Field(default_factory=list)
    avoided_topics: List[str] = Field(default_factory=list)
    trigger_topics: List[str] = Field(default_factory=list)
    
    # Therapeutic preferences
    preferred_therapeutic_approaches: List[TherapeuticFramework] = Field(default_factory=list)
    avoided_therapeutic_approaches: List[TherapeuticFramework] = Field(default_factory=list)
    
    # Content characteristics
    preferred_tone: List[str] = Field(default_factory=list)
    preferred_complexity_level: int = Field(default=3, ge=1, le=5)
    preferred_length: str = "medium"  # short, medium, long
    
    # Safety settings
    enable_content_warnings: bool = True
    require_explicit_consent: bool = False
    auto_skip_sensitive_content: bool = False


@dataclass
class SafetyGuidelines:
    """Safety guidelines for content validation."""
    guideline_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    
    # Applicable contexts
    content_types: List[ContentType] = field(default_factory=list)
    age_groups: List[AgeGroup] = field(default_factory=list)
    therapeutic_frameworks: List[TherapeuticFramework] = field(default_factory=list)
    
    # Rules and criteria
    validation_rules: List[str] = field(default_factory=list)
    prohibited_content: List[str] = field(default_factory=list)
    required_elements: List[str] = field(default_factory=list)
    
    # Risk thresholds
    crisis_level_thresholds: Dict[CrisisLevel, float] = field(default_factory=dict)
    bias_score_thresholds: Dict[BiasType, float] = field(default_factory=dict)
    
    # Actions
    violation_actions: Dict[str, ValidationAction] = field(default_factory=dict)
    escalation_criteria: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"
    is_active: bool = True


@dataclass
class CrisisHistory:
    """Historical crisis events for context."""
    user_id: str = ""
    crisis_events: List[Dict[str, Any]] = field(default_factory=list)
    intervention_history: List[Dict[str, Any]] = field(default_factory=list)
    successful_strategies: List[str] = field(default_factory=list)
    ineffective_strategies: List[str] = field(default_factory=list)
    
    # Patterns
    common_triggers: List[str] = field(default_factory=list)
    warning_signs: List[str] = field(default_factory=list)
    protective_factors: List[ProtectiveFactor] = field(default_factory=list)
    
    # Timing patterns
    crisis_frequency: float = 0.0  # events per month
    last_crisis_date: Optional[datetime] = None
    average_recovery_time: Optional[timedelta] = None
    
    def get_risk_level(self) -> CrisisLevel:
        """Calculate current risk level based on history."""
        if not self.crisis_events:
            return CrisisLevel.NONE
        
        recent_events = [
            event for event in self.crisis_events
            if datetime.fromisoformat(event.get('date', '1970-01-01')) > 
            datetime.utcnow() - timedelta(days=30)
        ]
        
        if len(recent_events) >= 3:
            return CrisisLevel.HIGH
        elif len(recent_events) >= 1:
            return CrisisLevel.MODERATE
        else:
            return CrisisLevel.LOW
