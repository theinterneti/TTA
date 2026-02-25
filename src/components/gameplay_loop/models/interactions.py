"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Models/Interactions]]

# Logseq: [[TTA/Components/Gameplay_loop/Models/Interactions]]
Interaction Models for Gameplay Loop

This module defines models for player interactions, choices, outcomes, and therapeutic interventions
within the therapeutic text adventure gameplay system.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .core import ChoiceType, DifficultyLevel, EmotionalState


class InterventionType(StrEnum):
    """Types of therapeutic interventions."""

    MINDFULNESS = "mindfulness"
    COGNITIVE_REFRAMING = "cognitive_reframing"
    GROUNDING = "grounding"
    BREATHING = "breathing"
    EMOTIONAL_REGULATION = "emotional_regulation"
    CRISIS_SUPPORT = "crisis_support"
    SKILL_PRACTICE = "skill_practice"


class OutcomeType(StrEnum):
    """Types of choice outcomes."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    NEUTRAL = "neutral"
    CHALLENGE = "challenge"
    FAILURE = "failure"
    THERAPEUTIC_OPPORTUNITY = "therapeutic_opportunity"


class EventType(StrEnum):
    """Types of narrative events."""

    SCENE_TRANSITION = "scene_transition"
    CHARACTER_INTERACTION = "character_interaction"
    SKILL_DEVELOPMENT = "skill_development"
    THERAPEUTIC_MOMENT = "therapeutic_moment"
    CRISIS_INTERVENTION = "crisis_intervention"
    ACHIEVEMENT = "achievement"


class UserChoice(BaseModel):
    """A choice made by the user during gameplay."""

    choice_id: str = Field(..., description="Choice identifier")
    session_id: str = Field(..., description="Session identifier")
    scene_id: str = Field(..., description="Scene identifier")

    # Choice details
    choice_text: str = Field(..., description="Text of the choice made")
    choice_type: ChoiceType = Field(..., description="Type of choice")
    therapeutic_value: float = Field(default=0.0, ge=0.0, le=1.0)
    therapeutic_tags: list[str] = Field(default_factory=list)
    agency_level: float = Field(default=0.5, ge=0.0, le=1.0)

    # Context
    emotional_state_before: EmotionalState = Field(
        ..., description="Emotional state before choice"
    )
    emotional_state_after: EmotionalState | None = Field(
        None, description="Emotional state after choice"
    )

    # Timing
    choice_made_at: datetime = Field(default_factory=datetime.utcnow)
    response_time: float = Field(
        default=0.0, description="Time taken to make choice in seconds"
    )

    # Metadata
    user_confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="User's confidence in choice"
    )
    difficulty_perceived: DifficultyLevel | None = Field(
        None, description="User's perceived difficulty"
    )


class ChoiceOutcome(BaseModel):
    """The outcome of a user choice."""

    outcome_id: str = Field(default_factory=lambda: str(uuid4()))
    choice_id: str = Field(..., description="Associated choice ID")
    session_id: str = Field(default="", description="Session identifier")

    # Outcome details
    outcome_type: str = Field(..., description="Type of outcome")
    narrative_response: str = Field(default="", description="Narrative response to the choice")

    # Effects
    immediate_effects: dict[str, Any] = Field(default_factory=dict)
    character_changes: dict[str, float] = Field(default_factory=dict)
    relationship_changes: dict[str, float] = Field(default_factory=dict)

    # Therapeutic impact
    therapeutic_progress: dict[str, float] = Field(default_factory=dict)
    therapeutic_impact: dict[str, Any] = Field(default_factory=dict)
    skills_developed: list[str] = Field(default_factory=list)
    insights_gained: list[str] = Field(default_factory=list)
    learning_opportunities: list[str] = Field(default_factory=list)
    skill_development: list[str] = Field(default_factory=list)
    progress_markers: list[Any] = Field(default_factory=list)

    # Narrative
    narrative_consequences: list[str] = Field(default_factory=list)
    emotional_response: str = Field(default="neutral")

    # Next steps
    next_scene_id: str | None = Field(default=None, description="Next scene to transition to")
    available_choices: list[str] = Field(
        default_factory=list, description="Next available choice IDs"
    )

    # Validation
    requires_therapeutic_intervention: bool = Field(default=False)
    safety_concerns: list[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NarrativeEvent(BaseModel):
    """A significant event in the narrative progression."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")
    scene_id: str | None = Field(None, description="Scene identifier")

    # Event details
    event_type: EventType = Field(..., description="Type of event")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")

    # Context
    triggered_by_choice: str | None = Field(
        None, description="Choice that triggered this event"
    )
    emotional_context: EmotionalState = Field(default=EmotionalState.CALM)

    # Impact
    narrative_impact: str = Field(..., description="Impact on the narrative")
    character_impact: dict[str, Any] = Field(default_factory=dict)
    therapeutic_significance: float = Field(default=0.0, ge=0.0, le=1.0)

    # Outcomes
    unlocked_content: list[str] = Field(default_factory=list)
    blocked_content: list[str] = Field(default_factory=list)

    # Metadata
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class TherapeuticIntervention(BaseModel):
    """A therapeutic intervention triggered during gameplay."""

    intervention_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")

    # Intervention details
    intervention_type: InterventionType = Field(..., description="Type of intervention")
    title: str = Field(..., description="Intervention title")
    description: str = Field(..., description="Intervention description")
    content: str = Field(..., description="Intervention content/instructions")

    # Context
    triggered_by: str = Field(..., description="What triggered this intervention")
    emotional_state: EmotionalState = Field(..., description="User's emotional state")
    urgency_level: str = Field(
        default="standard", description="Urgency level: standard, elevated, crisis"
    )

    # Execution
    is_mandatory: bool = Field(
        default=False, description="Whether intervention is mandatory"
    )
    estimated_duration: int = Field(
        default=300, description="Estimated duration in seconds"
    )

    # Outcomes
    completion_status: str = Field(
        default="pending", description="pending, completed, skipped, interrupted"
    )
    effectiveness_rating: float | None = Field(None, ge=0.0, le=1.0)
    user_feedback: str | None = Field(None, description="User feedback on intervention")

    # Follow-up
    follow_up_required: bool = Field(default=False)
    follow_up_scheduled: datetime | None = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(None)


class AgencyAssessment(BaseModel):
    """Assessment of player agency and empowerment for a choice."""

    choice_id: str = Field(..., description="Choice identifier")
    agency_level: str = Field(..., description="Agency level: HIGH, MODERATE, LOW")
    empowerment_score: float = Field(
        ..., ge=0.0, le=1.0, description="Empowerment score"
    )

    # Analysis
    empowerment_factors: list[str] = Field(
        default_factory=list, description="Factors that enhance empowerment"
    )
    agency_concerns: list[str] = Field(
        default_factory=list, description="Concerns about agency"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )

    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


class GameplaySession(BaseModel):
    """A gameplay session containing state and available choices."""

    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")

    # Session state
    current_scene_id: str | None = Field(None, description="Current scene ID")
    current_scene: Any | None = Field(None, description="Current scene data")
    available_choices: list[Any] = Field(
        default_factory=list, description="Available choices"
    )

    # Extended session state (holds SessionState object as dict)
    session_state: Any = Field(default=None, description="Full session state object")
    session_start_time: datetime | None = Field(default=None)
    session_end_time: datetime | None = Field(default=None)
    session_recap: str | None = Field(default=None)

    # Session metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_time: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Therapeutic context
    therapeutic_context: dict[str, Any] = Field(default_factory=dict)
