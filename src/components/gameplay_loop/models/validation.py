"""
Validation Models

This module defines data structures for content validation, safety checks,
therapeutic alignment, and validation rules in the gameplay loop.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ValidationLevel(str, Enum):
    """Levels of validation severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SafetyLevel(str, Enum):
    """Safety assessment levels."""
    SAFE = "safe"
    CAUTION = "caution"
    CONCERN = "concern"
    DANGER = "danger"
    CRISIS = "crisis"


class ValidationRuleType(str, Enum):
    """Types of validation rules."""
    CONTENT_SAFETY = "content_safety"
    THERAPEUTIC_ALIGNMENT = "therapeutic_alignment"
    EMOTIONAL_APPROPRIATENESS = "emotional_appropriateness"
    AGE_APPROPRIATENESS = "age_appropriateness"
    CRISIS_DETECTION = "crisis_detection"
    BOUNDARY_ENFORCEMENT = "boundary_enforcement"
    PROGRESS_VALIDATION = "progress_validation"


class TherapeuticAlignmentType(str, Enum):
    """Types of therapeutic alignment."""
    GOAL_ALIGNED = "goal_aligned"
    SKILL_BUILDING = "skill_building"
    EMOTIONAL_SUPPORT = "emotional_support"
    BEHAVIORAL_CHANGE = "behavioral_change"
    INSIGHT_DEVELOPMENT = "insight_development"
    COPING_STRATEGY = "coping_strategy"
    RELATIONSHIP_BUILDING = "relationship_building"


class ValidationRule(BaseModel):
    """Individual validation rule definition."""
    rule_id: str = Field(default_factory=lambda: str(uuid4()))
    rule_name: str = Field(..., description="Name of the validation rule")
    rule_type: ValidationRuleType = Field(..., description="Type of validation rule")
    description: str = Field(..., description="Description of what the rule validates")
    validation_criteria: Dict[str, Any] = Field(default_factory=dict)
    severity_level: ValidationLevel = Field(default=ValidationLevel.WARNING)
    is_active: bool = Field(default=True)
    therapeutic_context: List[str] = Field(default_factory=list)
    age_restrictions: Optional[Dict[str, Any]] = Field(None)
    cultural_considerations: List[str] = Field(default_factory=list)
    error_message: str = Field(..., description="Message to display when rule fails")
    remediation_suggestions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def applies_to_context(self, context: Dict[str, Any]) -> bool:
        """Check if rule applies to given context."""
        if not self.is_active:
            return False
        
        # Check therapeutic context
        if self.therapeutic_context:
            user_context = context.get('therapeutic_context', [])
            if not any(ctx in user_context for ctx in self.therapeutic_context):
                return False
        
        # Check age restrictions
        if self.age_restrictions:
            user_age = context.get('user_age')
            if user_age is not None:
                min_age = self.age_restrictions.get('min_age')
                max_age = self.age_restrictions.get('max_age')
                if min_age and user_age < min_age:
                    return False
                if max_age and user_age > max_age:
                    return False
        
        return True


class SafetyCheck(BaseModel):
    """Safety assessment result."""
    check_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str = Field(..., description="ID of content being checked")
    safety_level: SafetyLevel = Field(..., description="Assessed safety level")
    safety_score: float = Field(..., ge=0.0, le=1.0, description="Numerical safety score")
    risk_factors: List[str] = Field(default_factory=list)
    protective_factors: List[str] = Field(default_factory=list)
    crisis_indicators: List[str] = Field(default_factory=list)
    intervention_recommendations: List[str] = Field(default_factory=list)
    requires_human_review: bool = Field(default=False)
    escalation_required: bool = Field(default=False)
    safety_notes: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('safety_score')
    @classmethod
    def validate_safety_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Safety score must be between 0.0 and 1.0')
        return v
    
    def is_safe_for_user(self, user_context: Dict[str, Any]) -> bool:
        """Check if content is safe for specific user context."""
        if self.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRISIS]:
            return False
        
        if self.safety_level == SafetyLevel.CONCERN:
            # Check user's current emotional state and history
            emotional_state = user_context.get('emotional_state', {})
            if any(emotion in ['distress', 'crisis', 'panic'] for emotion in emotional_state.keys()):
                return False
        
        return True
    
    def requires_intervention(self) -> bool:
        """Check if safety check requires immediate intervention."""
        return (
            self.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRISIS] or
            self.escalation_required or
            len(self.crisis_indicators) > 0
        )


class TherapeuticAlignment(BaseModel):
    """Therapeutic alignment assessment."""
    alignment_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str = Field(..., description="ID of content being assessed")
    alignment_type: TherapeuticAlignmentType = Field(..., description="Type of therapeutic alignment")
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment score")
    therapeutic_goals: List[str] = Field(default_factory=list)
    supported_skills: List[str] = Field(default_factory=list)
    emotional_benefits: List[str] = Field(default_factory=list)
    behavioral_targets: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    enhancement_suggestions: List[str] = Field(default_factory=list)
    evidence_base: List[str] = Field(default_factory=list)
    cultural_sensitivity: float = Field(default=0.8, ge=0.0, le=1.0)
    age_appropriateness: float = Field(default=0.8, ge=0.0, le=1.0)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('alignment_score', 'cultural_sensitivity', 'age_appropriateness')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    def is_therapeutically_beneficial(self) -> bool:
        """Check if content is therapeutically beneficial."""
        return (
            self.alignment_score >= 0.6 and
            len(self.contraindications) == 0 and
            len(self.therapeutic_goals) > 0
        )


class ContentValidation(BaseModel):
    """Comprehensive content validation result."""
    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    content_id: str = Field(..., description="ID of content being validated")
    content_type: str = Field(..., description="Type of content (scene, choice, response, etc.)")
    validation_rules_applied: List[str] = Field(default_factory=list)  # Rule IDs
    safety_check: SafetyCheck = Field(..., description="Safety assessment")
    therapeutic_alignment: TherapeuticAlignment = Field(..., description="Therapeutic alignment")
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)
    validation_warnings: List[Dict[str, Any]] = Field(default_factory=list)
    validation_notes: List[str] = Field(default_factory=list)
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_approved: bool = Field(default=False)
    requires_revision: bool = Field(default=False)
    revision_suggestions: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: str = Field(default="system", description="Who/what performed validation")
    
    @field_validator('overall_score')
    @classmethod
    def validate_overall_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Overall score must be between 0.0 and 1.0')
        return v
    
    def calculate_overall_score(self) -> float:
        """Calculate overall validation score."""
        safety_weight = 0.4
        therapeutic_weight = 0.4
        error_penalty = 0.2
        
        safety_component = self.safety_check.safety_score * safety_weight
        therapeutic_component = self.therapeutic_alignment.alignment_score * therapeutic_weight
        
        # Penalty for errors
        error_penalty_value = len(self.validation_errors) * 0.1
        error_component = max(0.0, error_penalty - error_penalty_value)
        
        return min(1.0, safety_component + therapeutic_component + error_component)
    
    def is_ready_for_use(self) -> bool:
        """Check if content is ready for use."""
        return (
            self.is_approved and
            not self.requires_revision and
            len(self.validation_errors) == 0 and
            self.safety_check.safety_level not in [SafetyLevel.DANGER, SafetyLevel.CRISIS]
        )
    
    def get_blocking_issues(self) -> List[str]:
        """Get issues that block content from being used."""
        blocking_issues = []
        
        # Critical validation errors
        for error in self.validation_errors:
            if error.get('severity') == ValidationLevel.CRITICAL:
                blocking_issues.append(error.get('message', 'Critical validation error'))
        
        # Safety concerns
        if self.safety_check.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRISIS]:
            blocking_issues.append(f"Safety level: {self.safety_check.safety_level}")
        
        # Therapeutic contraindications
        if self.therapeutic_alignment.contraindications:
            blocking_issues.extend(self.therapeutic_alignment.contraindications)
        
        return blocking_issues


class ValidationResult(BaseModel):
    """Overall validation result for gameplay content."""
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="ID of the session")
    content_validations: List[ContentValidation] = Field(default_factory=list)
    batch_safety_score: float = Field(default=1.0, ge=0.0, le=1.0)
    batch_therapeutic_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_approval: bool = Field(default=True)
    blocking_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    requires_human_review: bool = Field(default=False)
    validation_summary: str = Field(default="", description="Summary of validation results")
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('batch_safety_score', 'batch_therapeutic_score')
    @classmethod
    def validate_batch_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Batch score must be between 0.0 and 1.0')
        return v
    
    def add_content_validation(self, validation: ContentValidation) -> None:
        """Add a content validation to the result."""
        self.content_validations.append(validation)
        self._update_batch_scores()
        self._update_approval_status()
    
    def _update_batch_scores(self) -> None:
        """Update batch scores based on content validations."""
        if not self.content_validations:
            return
        
        safety_scores = [cv.safety_check.safety_score for cv in self.content_validations]
        therapeutic_scores = [cv.therapeutic_alignment.alignment_score for cv in self.content_validations]
        
        self.batch_safety_score = sum(safety_scores) / len(safety_scores)
        self.batch_therapeutic_score = sum(therapeutic_scores) / len(therapeutic_scores)
    
    def _update_approval_status(self) -> None:
        """Update overall approval status."""
        self.blocking_issues = []
        
        for validation in self.content_validations:
            if not validation.is_ready_for_use():
                self.blocking_issues.extend(validation.get_blocking_issues())
        
        self.overall_approval = len(self.blocking_issues) == 0
        self.requires_human_review = any(
            cv.safety_check.requires_human_review for cv in self.content_validations
        )
