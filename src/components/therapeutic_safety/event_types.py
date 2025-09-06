"""
Therapeutic Safety Event Types

This module defines event types and base classes for therapeutic safety validation,
breaking circular dependencies with the gameplay loop narrative events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from .enums import (
    BiasType,
    CrisisLevel,
    ProtectiveFactor,
    RiskCategory,
    SafetyLevel,
    ValidationAction,
    ValidationComponent,
)


class EventType(Enum):
    """Event types for safety validation."""

    SAFETY_VALIDATION_STARTED = "safety_validation_started"
    SAFETY_VALIDATION_COMPLETED = "safety_validation_completed"
    CRISIS_DETECTED = "crisis_detected"
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_TIMEOUT = "validation_timeout"
    BIAS_DETECTED = "bias_detected"
    THERAPEUTIC_ALIGNMENT_CHECKED = "therapeutic_alignment_checked"


class EventPriority(Enum):
    """Priority levels for events."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BaseSafetyEvent:
    """Base class for all safety validation events."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = field(default=EventType.SAFETY_VALIDATION_STARTED)
    session_id: str = field(default="")
    user_id: str = field(default="")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = field(default=EventPriority.NORMAL)

    # Event data
    data: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    # Processing metadata
    processed: bool = field(default=False)
    processing_errors: list[str] = field(default_factory=list)
    retry_count: int = field(default=0)

    def __post_init__(self):
        """Initialize event context."""
        if not self.context:
            self.context = {}

        # Add basic event metadata to context
        self.context.update(
            {
                "event_id": self.event_id,
                "event_type": self.event_type.value,
                "timestamp": self.timestamp.isoformat(),
                "priority": self.priority.value,
            }
        )


@dataclass
class SafetyValidationEvent(BaseSafetyEvent):
    """Event for safety validation processes."""

    content_id: str = field(default="")
    validation_id: str = field(default="")
    validation_action: ValidationAction = field(default=ValidationAction.APPROVE)
    safety_level: SafetyLevel = field(default=SafetyLevel.SAFE)
    confidence_score: float = field(default=0.0)

    def __post_init__(self):
        super().__post_init__()
        # Add safety-specific data to context
        self.context.update(
            {
                "content_id": self.content_id,
                "validation_id": self.validation_id,
                "validation_action": self.validation_action.value,
                "safety_level": self.safety_level.value,
                "confidence_score": self.confidence_score,
            }
        )


@dataclass
class CrisisDetectionEvent(BaseSafetyEvent):
    """Event for crisis detection."""

    content_id: str = field(default="")
    validation_id: str = field(default="")
    crisis_level: CrisisLevel = field(default=CrisisLevel.NONE)
    risk_categories: list[RiskCategory] = field(default_factory=list)
    protective_factors: list[ProtectiveFactor] = field(default_factory=list)
    immediate_intervention_needed: bool = field(default=False)
    crisis_indicators: list[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.context.update(
            {
                "content_id": self.content_id,
                "validation_id": self.validation_id,
                "crisis_level": self.crisis_level.value,
                "risk_categories": [risk.value for risk in self.risk_categories],
                "protective_factors": [
                    factor.value for factor in self.protective_factors
                ],
                "immediate_intervention_needed": self.immediate_intervention_needed,
                "crisis_indicators": self.crisis_indicators,
            }
        )


@dataclass
class ValidationFailureEvent(BaseSafetyEvent):
    """Event for validation failures."""

    content_id: str = field(default="")
    validation_id: str = field(default="")
    failure_reason: str = field(default="")
    component_failures: list[ValidationComponent] = field(default_factory=list)
    retry_count: int = field(default=0)
    max_retries_exceeded: bool = field(default=False)

    def __post_init__(self):
        super().__post_init__()
        self.context.update(
            {
                "content_id": self.content_id,
                "validation_id": self.validation_id,
                "failure_reason": self.failure_reason,
                "component_failures": [comp.value for comp in self.component_failures],
                "retry_count": self.retry_count,
                "max_retries_exceeded": self.max_retries_exceeded,
            }
        )


@dataclass
class ValidationTimeoutEvent(BaseSafetyEvent):
    """Event for validation timeouts."""

    content_id: str = field(default="")
    validation_id: str = field(default="")
    timeout_ms: int = field(default=0)
    completed_components: list[ValidationComponent] = field(default_factory=list)
    pending_components: list[ValidationComponent] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.context.update(
            {
                "content_id": self.content_id,
                "validation_id": self.validation_id,
                "timeout_ms": self.timeout_ms,
                "completed_components": [
                    comp.value for comp in self.completed_components
                ],
                "pending_components": [comp.value for comp in self.pending_components],
            }
        )


@dataclass
class BiasDetectionEvent(BaseSafetyEvent):
    """Event for bias detection."""

    content_id: str = field(default="")
    validation_id: str = field(default="")
    bias_types: list[BiasType] = field(default_factory=list)
    bias_confidence: float = field(default=0.0)
    bias_indicators: list[str] = field(default_factory=list)
    mitigation_suggestions: list[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.context.update(
            {
                "content_id": self.content_id,
                "validation_id": self.validation_id,
                "bias_types": [bias.value for bias in self.bias_types],
                "bias_confidence": self.bias_confidence,
                "bias_indicators": self.bias_indicators,
                "mitigation_suggestions": self.mitigation_suggestions,
            }
        )


# Event factory functions
def create_safety_event(
    event_type: EventType,
    session_id: str,
    user_id: str,
    content_id: str,
    validation_action: ValidationAction = ValidationAction.APPROVE,
    safety_level: SafetyLevel = SafetyLevel.SAFE,
    confidence_score: float = 0.0,
    **kwargs,
) -> SafetyValidationEvent:
    """Create a safety validation event."""
    return SafetyValidationEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_action=validation_action,
        safety_level=safety_level,
        confidence_score=confidence_score,
        **kwargs,
    )


def create_crisis_event(
    event_type: EventType,
    session_id: str,
    user_id: str,
    content_id: str,
    validation_id: str,
    crisis_level: CrisisLevel,
    risk_categories: list[RiskCategory] = None,
    protective_factors: list[ProtectiveFactor] = None,
    immediate_intervention_needed: bool = False,
    crisis_indicators: list[str] = None,
    **kwargs,
) -> CrisisDetectionEvent:
    """Create a crisis detection event."""
    return CrisisDetectionEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_id=validation_id,
        crisis_level=crisis_level,
        risk_categories=risk_categories or [],
        protective_factors=protective_factors or [],
        immediate_intervention_needed=immediate_intervention_needed,
        crisis_indicators=crisis_indicators or [],
        **kwargs,
    )


def create_validation_failure_event(
    event_type: EventType,
    session_id: str,
    user_id: str,
    content_id: str,
    validation_id: str,
    failure_reason: str,
    component_failures: list[ValidationComponent] = None,
    retry_count: int = 0,
    **kwargs,
) -> ValidationFailureEvent:
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
        **kwargs,
    )


def create_validation_timeout_event(
    session_id: str,
    user_id: str,
    content_id: str,
    validation_id: str,
    timeout_ms: int,
    completed_components: list[ValidationComponent] = None,
    **kwargs,
) -> ValidationTimeoutEvent:
    """Create a validation timeout event."""
    return ValidationTimeoutEvent(
        event_type=EventType.VALIDATION_TIMEOUT,
        session_id=session_id,
        user_id=user_id,
        content_id=content_id,
        validation_id=validation_id,
        timeout_ms=timeout_ms,
        completed_components=completed_components or [],
        **kwargs,
    )


# Export all event types and utilities
__all__ = [
    "EventType",
    "EventPriority",
    "BaseSafetyEvent",
    "SafetyValidationEvent",
    "CrisisDetectionEvent",
    "ValidationFailureEvent",
    "ValidationTimeoutEvent",
    "BiasDetectionEvent",
    "create_safety_event",
    "create_crisis_event",
    "create_validation_failure_event",
    "create_validation_timeout_event",
]
