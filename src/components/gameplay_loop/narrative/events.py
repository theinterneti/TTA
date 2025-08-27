"""
Narrative Engine Events

This module defines the event system for the narrative engine, enabling
decoupled communication between components and external integrations.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of narrative events."""
    # Scene events
    SCENE_ENTERED = "scene_entered"
    SCENE_EXITED = "scene_exited"
    SCENE_COMPLETED = "scene_completed"
    SCENE_FAILED = "scene_failed"
    
    # Choice events
    CHOICE_PRESENTED = "choice_presented"
    CHOICE_MADE = "choice_made"
    CHOICE_VALIDATED = "choice_validated"
    CHOICE_PROCESSED = "choice_processed"

    # Consequence events
    CONSEQUENCE_GENERATED = "consequence_generated"
    CONSEQUENCE_APPLIED = "consequence_applied"
    LEARNING_OPPORTUNITY_CREATED = "learning_opportunity_created"
    PATTERN_RECOGNIZED = "pattern_recognized"

    # Adaptive difficulty events
    DIFFICULTY_ADJUSTED = "difficulty_adjusted"
    PERFORMANCE_MONITORED = "performance_monitored"
    USER_PREFERENCES_UPDATED = "user_preferences_updated"

    # Therapeutic integration events
    THERAPEUTIC_CONCEPT_INTEGRATED = "therapeutic_concept_integrated"
    THERAPEUTIC_PROGRESS_UPDATED = "therapeutic_progress_updated"
    THERAPEUTIC_RESISTANCE_DETECTED = "therapeutic_resistance_detected"
    ADAPTIVE_INTERVENTION_TRIGGERED = "adaptive_intervention_triggered"

    # Character development events
    CHARACTER_DEVELOPED = "character_developed"
    CHARACTER_MILESTONE_ACHIEVED = "character_milestone_achieved"
    CHARACTER_ABILITY_UNLOCKED = "character_ability_unlocked"
    CHARACTER_LEVEL_UP = "character_level_up"

    # Session management events
    SESSION_MANAGEMENT = "session_management"
    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_ENDED = "session_ended"
    BREAK_POINT_DETECTED = "break_point_detected"
    BREAK_POINT_OFFERED = "break_point_offered"
    BREAK_POINT_ACCEPTED = "break_point_accepted"
    
    # Progress events
    PROGRESS_UPDATED = "progress_updated"
    MILESTONE_ACHIEVED = "milestone_achieved"
    SKILL_DEVELOPED = "skill_developed"
    GOAL_COMPLETED = "goal_completed"
    
    # Safety events
    SAFETY_CHECK_TRIGGERED = "safety_check_triggered"
    SAFETY_CONCERN_DETECTED = "safety_concern_detected"
    CRISIS_INTERVENTION_NEEDED = "crisis_intervention_needed"
    SAFETY_CLEARED = "safety_cleared"
    
    # Flow events
    NARRATIVE_STARTED = "narrative_started"
    NARRATIVE_PAUSED = "narrative_paused"
    NARRATIVE_RESUMED = "narrative_resumed"
    NARRATIVE_COMPLETED = "narrative_completed"
    BRANCH_TAKEN = "branch_taken"
    
    # Therapeutic events
    THERAPEUTIC_MOMENT = "therapeutic_moment"
    REFLECTION_TRIGGERED = "reflection_triggered"
    INTERVENTION_APPLIED = "intervention_applied"
    ADAPTATION_MADE = "adaptation_made"


class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NarrativeEvent:
    """Base class for all narrative events."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = field(default=EventType.NARRATIVE_STARTED)
    session_id: str = field(default="")
    user_id: str = field(default="")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = field(default=EventPriority.NORMAL)
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    processed: bool = field(default=False)
    processing_errors: List[str] = field(default_factory=list)
    retry_count: int = field(default=0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "data": self.data,
            "context": self.context,
            "processed": self.processed,
            "processing_errors": self.processing_errors,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NarrativeEvent:
        """Create event from dictionary."""
        return cls(
            event_id=data.get("event_id", str(uuid4())),
            event_type=EventType(data.get("event_type", EventType.NARRATIVE_STARTED.value)),
            session_id=data.get("session_id", ""),
            user_id=data.get("user_id", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
            priority=EventPriority(data.get("priority", EventPriority.NORMAL.value)),
            data=data.get("data", {}),
            context=data.get("context", {}),
            processed=data.get("processed", False),
            processing_errors=data.get("processing_errors", []),
            retry_count=data.get("retry_count", 0)
        )


@dataclass
class SceneEvent(NarrativeEvent):
    """Scene-specific event."""
    scene_id: str = field(default="")
    scene_type: str = field(default="")
    therapeutic_focus: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Add scene-specific data to context
        self.context.update({
            "scene_id": self.scene_id,
            "scene_type": self.scene_type,
            "therapeutic_focus": self.therapeutic_focus
        })


@dataclass
class ChoiceEvent(NarrativeEvent):
    """Choice-specific event."""
    choice_id: str = field(default="")
    choice_text: str = field(default="")
    choice_type: str = field(default="")
    therapeutic_relevance: float = field(default=0.0)
    
    def __post_init__(self):
        # Add choice-specific data to context
        self.context.update({
            "choice_id": self.choice_id,
            "choice_text": self.choice_text,
            "choice_type": self.choice_type,
            "therapeutic_relevance": self.therapeutic_relevance
        })


@dataclass
class ProgressEvent(NarrativeEvent):
    """Progress-specific event."""
    progress_type: str = field(default="")
    metric_name: str = field(default="")
    old_value: float = field(default=0.0)
    new_value: float = field(default=0.0)
    improvement: float = field(default=0.0)
    
    def __post_init__(self):
        # Calculate improvement
        self.improvement = self.new_value - self.old_value
        
        # Add progress-specific data to context
        self.context.update({
            "progress_type": self.progress_type,
            "metric_name": self.metric_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "improvement": self.improvement
        })


@dataclass
class SafetyEvent(NarrativeEvent):
    """Safety-specific event."""
    safety_level: str = field(default="standard")
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    intervention_needed: bool = field(default=False)
    
    def __post_init__(self):
        # Add safety-specific data to context
        self.context.update({
            "safety_level": self.safety_level,
            "risk_factors": self.risk_factors,
            "protective_factors": self.protective_factors,
            "intervention_needed": self.intervention_needed
        })


import asyncio


class EventBus:
    """Event bus for managing narrative events."""

    def __init__(self):
        self.subscribers: Dict[EventType, List[callable]] = {}
        self.event_history: List[NarrativeEvent] = []
        self.max_history_size = 1000

    def subscribe(self, event_type: EventType, handler: callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not found

    async def publish(self, event: NarrativeEvent) -> None:
        """Publish an event to all subscribers."""
        # Add to history
        self.event_history.append(event)

        # Trim history if needed
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]

        # Notify subscribers
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                event.processing_errors.append(str(e))
                event.retry_count += 1
    
    def get_events(self, event_type: Optional[EventType] = None,
                   session_id: Optional[str] = None,
                   limit: int = 100) -> List[NarrativeEvent]:
        """Get events from history with optional filtering."""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if session_id:
            events = [e for e in events if e.session_id == session_id]
        
        return events[-limit:] if limit else events
    
    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history.clear()


# Global event bus instance
event_bus = EventBus()


# Event factory functions
def create_scene_event(event_type: EventType, session_id: str, user_id: str,
                      scene_id: str, scene_type: str = "",
                      therapeutic_focus: List[str] = None,
                      **kwargs) -> SceneEvent:
    """Create a scene event."""
    return SceneEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        scene_id=scene_id,
        scene_type=scene_type,
        therapeutic_focus=therapeutic_focus or [],
        **kwargs
    )


def create_choice_event(event_type: EventType, session_id: str, user_id: str,
                       choice_id: str, choice_text: str = "",
                       choice_type: str = "", therapeutic_relevance: float = 0.0,
                       **kwargs) -> ChoiceEvent:
    """Create a choice event."""
    return ChoiceEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        choice_id=choice_id,
        choice_text=choice_text,
        choice_type=choice_type,
        therapeutic_relevance=therapeutic_relevance,
        **kwargs
    )


def create_progress_event(event_type: EventType, session_id: str, user_id: str,
                         progress_type: str, metric_name: str,
                         old_value: float, new_value: float,
                         **kwargs) -> ProgressEvent:
    """Create a progress event."""
    return ProgressEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        progress_type=progress_type,
        metric_name=metric_name,
        old_value=old_value,
        new_value=new_value,
        **kwargs
    )


def create_safety_event(event_type: EventType, session_id: str, user_id: str,
                       safety_level: str = "standard",
                       risk_factors: List[str] = None,
                       protective_factors: List[str] = None,
                       intervention_needed: bool = False,
                       **kwargs) -> SafetyEvent:
    """Create a safety event."""
    return SafetyEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        safety_level=safety_level,
        risk_factors=risk_factors or [],
        protective_factors=protective_factors or [],
        intervention_needed=intervention_needed,
        **kwargs
    )


def create_consequence_event(event_type: EventType, session_id: str, user_id: str,
                           consequence_id: str, choice_id: str = "",
                           consequence_type: str = "",
                           **kwargs) -> NarrativeEvent:
    """Create a consequence event."""
    return NarrativeEvent(
        event_type=event_type,
        session_id=session_id,
        user_id=user_id,
        context={
            "consequence_id": consequence_id,
            "choice_id": choice_id,
            "consequence_type": consequence_type,
            **kwargs.get("data", {})
        },
        **{k: v for k, v in kwargs.items() if k != "data"}
    )
