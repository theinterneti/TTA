"""
Safety Validation Events

This module provides event classes and factory functions for the therapeutic safety
validation system. All event classes are now defined in event_types.py to avoid
circular dependencies.
"""

# Import all event classes and factory functions from event_types
from .event_types import (
    BaseSafetyEvent,
    BiasDetectionEvent,
    CrisisDetectionEvent,
    EventPriority,
    EventType,
    SafetyValidationEvent,
    ValidationFailureEvent,
    create_crisis_event,
    create_safety_event,
    create_validation_failure_event,
)

# Re-export everything for backward compatibility
__all__ = [
    "EventPriority",
    "EventType",
    "BaseSafetyEvent",
    "SafetyValidationEvent",
    "CrisisDetectionEvent",
    "ValidationFailureEvent",
    "BiasDetectionEvent",
    "create_safety_event",
    "create_crisis_event",
    "create_validation_failure_event",
]
