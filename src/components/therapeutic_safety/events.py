"""
Safety Validation Events

This module defines events for the therapeutic safety validation system,
integrating with the existing narrative engine event system.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from uuid import uuid4

from src.components.gameplay_loop.narrative.events import NarrativeEvent, EventType, EventPriority
from .enums import (
    CrisisLevel, ValidationAction, SafetyLevel, ValidationStatus,
    RiskCategory, ProtectiveFactor, BiasType, ValidationComponent
)


@dataclass
class SafetyValidationEvent(NarrativeEvent):
    """Event for safety validation processes."""
    content_id: str = field(default="")
    validation_id: str = field(default="")
    validation_action: ValidationAction = field(default=ValidationAction.APPROVE)
    safety_level: SafetyLevel = field(default=SafetyLevel.SAFE)
    confidence_score: float = field(default=0.0)
    
    def __post_init__(self):
        super().__post_init__()
        # Add safety-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "validation_id": self.validation_id,
            "validation_action": self.validation_action.value,
            "safety_level": self.safety_level.value,
            "confidence_score": self.confidence_score
        })


@dataclass
class CrisisDetectionEvent(NarrativeEvent):
    """Event for crisis detection in content."""
    content_id: str = field(default="")
    crisis_level: CrisisLevel = field(default=CrisisLevel.NONE)
    crisis_indicators: List[str] = field(default_factory=list)
    immediate_intervention_needed: bool = field(default=False)
    risk_factors: List[RiskCategory] = field(default_factory=list)
    protective_factors: List[ProtectiveFactor] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        # Set priority based on crisis level
        if self.crisis_level >= CrisisLevel.HIGH:
            self.priority = EventPriority.CRITICAL
        elif self.crisis_level >= CrisisLevel.MODERATE:
            self.priority = EventPriority.HIGH
        else:
            self.priority = EventPriority.NORMAL
        
        # Add crisis-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "crisis_level": self.crisis_level.value,
            "crisis_indicators": self.crisis_indicators,
            "immediate_intervention_needed": self.immediate_intervention_needed,
            "risk_factors": [rf.value for rf in self.risk_factors],
            "protective_factors": [pf.value for pf in self.protective_factors]
        })


@dataclass
class ValidationFailureEvent(NarrativeEvent):
    """Event for validation failures and errors."""
    content_id: str = field(default="")
    validation_id: str = field(default="")
    failure_reason: str = field(default="")
    component_failures: List[ValidationComponent] = field(default_factory=list)
    retry_count: int = field(default=0)
    max_retries: int = field(default=3)
    
    def __post_init__(self):
        super().__post_init__()
        # Set priority based on failure severity
        if self.retry_count >= self.max_retries:
            self.priority = EventPriority.HIGH
        else:
            self.priority = EventPriority.NORMAL
        
        # Add failure-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "validation_id": self.validation_id,
            "failure_reason": self.failure_reason,
            "component_failures": [cf.value for cf in self.component_failures],
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        })


@dataclass
class BiasDetectionEvent(NarrativeEvent):
    """Event for bias detection in content."""
    content_id: str = field(default="")
    detected_biases: List[BiasType] = field(default_factory=list)
    bias_scores: Dict[BiasType, float] = field(default_factory=dict)
    overall_bias_score: float = field(default=0.0)
    mitigation_suggestions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        # Set priority based on bias severity
        if self.overall_bias_score > 0.8:
            self.priority = EventPriority.HIGH
        elif self.overall_bias_score > 0.5:
            self.priority = EventPriority.NORMAL
        else:
            self.priority = EventPriority.LOW
        
        # Add bias-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "detected_biases": [bias.value for bias in self.detected_biases],
            "bias_scores": {bias.value: score for bias, score in self.bias_scores.items()},
            "overall_bias_score": self.overall_bias_score,
            "mitigation_suggestions": self.mitigation_suggestions
        })


@dataclass
class TherapeuticAlignmentEvent(NarrativeEvent):
    """Event for therapeutic alignment assessment."""
    content_id: str = field(default="")
    alignment_score: float = field(default=0.0)
    aligned_goals: List[str] = field(default_factory=list)
    misaligned_aspects: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        # Add alignment-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "alignment_score": self.alignment_score,
            "aligned_goals": self.aligned_goals,
            "misaligned_aspects": self.misaligned_aspects,
            "recommendations": self.recommendations
        })


@dataclass
class ValidationTimeoutEvent(NarrativeEvent):
    """Event for validation timeouts."""
    content_id: str = field(default="")
    validation_id: str = field(default="")
    timeout_ms: int = field(default=200)
    components_completed: List[ValidationComponent] = field(default_factory=list)
    components_pending: List[ValidationComponent] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.priority = EventPriority.HIGH
        
        # Add timeout-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "validation_id": self.validation_id,
            "timeout_ms": self.timeout_ms,
            "components_completed": [comp.value for comp in self.components_completed],
            "components_pending": [comp.value for comp in self.components_pending]
        })


@dataclass
class InterventionTriggeredEvent(NarrativeEvent):
    """Event for triggered therapeutic interventions."""
    content_id: str = field(default="")
    intervention_type: str = field(default="")
    trigger_reason: str = field(default="")
    intervention_data: Dict[str, Any] = field(default_factory=dict)
    requires_human_review: bool = field(default=False)
    
    def __post_init__(self):
        super().__post_init__()
        self.priority = EventPriority.HIGH
        
        # Add intervention-specific data to context
        self.context.update({
            "content_id": self.content_id,
            "intervention_type": self.intervention_type,
            "trigger_reason": self.trigger_reason,
            "intervention_data": self.intervention_data,
            "requires_human_review": self.requires_human_review
        })


# Event factory functions
def create_safety_event(event_type: EventType, session_id: str, user_id: str,
                       content_id: str, validation_action: ValidationAction = ValidationAction.APPROVE,
                       safety_level: SafetyLevel = SafetyLevel.SAFE,
                       confidence_score: float = 0.0,
                       **kwargs) -> SafetyValidationEvent:
    """Create a safety validation event."""
    return SafetyValidationEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_action=validation_action,
        safety_level=safety_level,
        confidence_score=confidence_score,
        **kwargs
    )


def create_crisis_event(event_type: EventType, session_id: str, user_id: str,
                       content_id: str, crisis_level: CrisisLevel = CrisisLevel.NONE,
                       crisis_indicators: List[str] = None,
                       immediate_intervention_needed: bool = False,
                       risk_factors: List[RiskCategory] = None,
                       protective_factors: List[ProtectiveFactor] = None,
                       **kwargs) -> CrisisDetectionEvent:
    """Create a crisis detection event."""
    return CrisisDetectionEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        crisis_level=crisis_level,
        crisis_indicators=crisis_indicators or [],
        immediate_intervention_needed=immediate_intervention_needed,
        risk_factors=risk_factors or [],
        protective_factors=protective_factors or [],
        **kwargs
    )


def create_validation_failure_event(event_type: EventType, session_id: str, user_id: str,
                                   content_id: str, validation_id: str,
                                   failure_reason: str,
                                   component_failures: List[ValidationComponent] = None,
                                   retry_count: int = 0,
                                   **kwargs) -> ValidationFailureEvent:
    """Create a validation failure event."""
    return ValidationFailureEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_id=validation_id,
        failure_reason=failure_reason,
        component_failures=component_failures or [],
        retry_count=retry_count,
        **kwargs
    )


def create_bias_detection_event(event_type: EventType, session_id: str, user_id: str,
                               content_id: str,
                               detected_biases: List[BiasType] = None,
                               bias_scores: Dict[BiasType, float] = None,
                               overall_bias_score: float = 0.0,
                               mitigation_suggestions: List[str] = None,
                               **kwargs) -> BiasDetectionEvent:
    """Create a bias detection event."""
    return BiasDetectionEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        detected_biases=detected_biases or [],
        bias_scores=bias_scores or {},
        overall_bias_score=overall_bias_score,
        mitigation_suggestions=mitigation_suggestions or [],
        **kwargs
    )


def create_therapeutic_alignment_event(event_type: EventType, session_id: str, user_id: str,
                                     content_id: str,
                                     alignment_score: float = 0.0,
                                     aligned_goals: List[str] = None,
                                     misaligned_aspects: List[str] = None,
                                     recommendations: List[str] = None,
                                     **kwargs) -> TherapeuticAlignmentEvent:
    """Create a therapeutic alignment event."""
    return TherapeuticAlignmentEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        alignment_score=alignment_score,
        aligned_goals=aligned_goals or [],
        misaligned_aspects=misaligned_aspects or [],
        recommendations=recommendations or [],
        **kwargs
    )


def create_validation_timeout_event(session_id: str, user_id: str,
                                   content_id: str, validation_id: str,
                                   timeout_ms: int = 200,
                                   components_completed: List[ValidationComponent] = None,
                                   components_pending: List[ValidationComponent] = None,
                                   **kwargs) -> ValidationTimeoutEvent:
    """Create a validation timeout event."""
    return ValidationTimeoutEvent(
        event_type=EventType.SAFETY_CHECK_TRIGGERED,  # Using existing event type
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_id=validation_id,
        timeout_ms=timeout_ms,
        components_completed=components_completed or [],
        components_pending=components_pending or [],
        **kwargs
    )


def create_intervention_event(session_id: str, user_id: str,
                             content_id: str, intervention_type: str,
                             trigger_reason: str,
                             intervention_data: Dict[str, Any] = None,
                             requires_human_review: bool = False,
                             **kwargs) -> InterventionTriggeredEvent:
    """Create an intervention triggered event."""
    return InterventionTriggeredEvent(
        event_type=EventType.CRISIS_INTERVENTION_NEEDED,  # Using existing event type
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        intervention_type=intervention_type,
        trigger_reason=trigger_reason,
        intervention_data=intervention_data or {},
        requires_human_review=requires_human_review,
        **kwargs
    )
