"""
Core Gameplay Loop Data Models

This module defines the fundamental data structures for the therapeutic gameplay loop,
including sessions, scenes, choices, consequences, and therapeutic outcomes.
"""

from __future__ import annotations

from dataclasses import field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass


class GameplayState(str, Enum):
    """States of the gameplay session."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    COMPLETED = "completed"
    ERROR = "error"


class SceneType(str, Enum):
    """Types of narrative scenes."""

    INTRODUCTION = "introduction"
    EXPLORATION = "exploration"
    DIALOGUE = "dialogue"
    CHALLENGE = "challenge"
    REFLECTION = "reflection"
    THERAPEUTIC_MOMENT = "therapeutic_moment"
    TRANSITION = "transition"
    CONCLUSION = "conclusion"


class ChoiceType(str, Enum):
    """Types of user choices."""

    NARRATIVE = "narrative"
    THERAPEUTIC = "therapeutic"
    EXPLORATION = "exploration"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"
    SKILL_PRACTICE = "skill_practice"


class ConsequenceType(str, Enum):
    """Types of consequences from user choices."""

    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    THERAPEUTIC = "therapeutic"
    NARRATIVE = "narrative"
    CHARACTER_DEVELOPMENT = "character_development"


@dataclass
class SessionMetrics:
    """Metrics for tracking session performance and engagement."""

    session_duration: timedelta = field(default_factory=lambda: timedelta(0))
    choices_made: int = 0
    scenes_completed: int = 0
    therapeutic_moments: int = 0
    emotional_responses: int = 0
    skill_practices: int = 0
    reflection_depth_score: float = 0.0  # 0.0 to 1.0
    engagement_score: float = 0.0  # 0.0 to 1.0
    therapeutic_alignment_score: float = 0.0  # 0.0 to 1.0
    safety_incidents: int = 0
    support_requests: int = 0


class TherapeuticOutcome(BaseModel):
    """Represents a therapeutic outcome from gameplay interactions."""

    outcome_id: str = Field(default_factory=lambda: str(uuid4()))
    outcome_type: str = Field(..., description="Type of therapeutic outcome")
    description: str = Field(..., description="Description of the outcome")
    therapeutic_value: float = Field(
        ..., ge=0.0, le=1.0, description="Therapeutic value score"
    )
    skills_practiced: list[str] = Field(default_factory=list)
    emotional_growth: dict[str, float] = Field(default_factory=dict)
    behavioral_insights: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("therapeutic_value")
    @classmethod
    def validate_therapeutic_value(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Therapeutic value must be between 0.0 and 1.0")
        return v


class ConsequenceSet(BaseModel):
    """Set of consequences resulting from a user choice."""

    consequence_id: str = Field(default_factory=lambda: str(uuid4()))
    choice_id: str = Field(
        ..., description="ID of the choice that led to these consequences"
    )
    consequences: list[dict[str, Any]] = Field(default_factory=list)
    consequence_type: ConsequenceType = Field(default=ConsequenceType.IMMEDIATE)
    therapeutic_outcomes: list[TherapeuticOutcome] = Field(default_factory=list)
    narrative_impact: dict[str, Any] = Field(default_factory=dict)
    character_changes: dict[str, Any] = Field(default_factory=dict)
    emotional_impact: dict[str, float] = Field(default_factory=dict)
    learning_opportunities: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserChoice(BaseModel):
    """Represents a choice made by the user during gameplay."""

    choice_id: str = Field(default_factory=lambda: str(uuid4()))
    scene_id: str = Field(..., description="ID of the scene where choice was made")
    choice_text: str = Field(..., description="Text of the choice option")
    choice_type: ChoiceType = Field(default=ChoiceType.NARRATIVE)
    therapeutic_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    emotional_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    difficulty_level: float = Field(default=0.5, ge=0.0, le=1.0)
    prerequisites: list[str] = Field(default_factory=list)
    consequences: ConsequenceSet | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("therapeutic_relevance", "emotional_weight", "difficulty_level")
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class NarrativeScene(BaseModel):
    """Represents a scene in the therapeutic narrative."""

    scene_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="ID of the gameplay session")
    scene_type: SceneType = Field(default=SceneType.EXPLORATION)
    title: str = Field(..., description="Title of the scene")
    description: str = Field(..., description="Detailed scene description")
    narrative_content: str = Field(..., description="Main narrative content")
    therapeutic_focus: list[str] = Field(default_factory=list)
    emotional_tone: dict[str, float] = Field(default_factory=dict)
    available_choices: list[UserChoice] = Field(default_factory=list)
    scene_objectives: list[str] = Field(default_factory=list)
    completion_criteria: dict[str, Any] = Field(default_factory=dict)
    safety_considerations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    @field_validator("emotional_tone")
    @classmethod
    def validate_emotional_tone(cls, v):
        for emotion, intensity in v.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(
                    f"Emotional intensity for {emotion} must be between 0.0 and 1.0"
                )
        return v


class GameplaySession(BaseModel):
    """Represents a complete therapeutic gameplay session."""

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="ID of the user")
    character_id: str | None = Field(
        None, description="ID of the character being played"
    )
    world_id: str | None = Field(None, description="ID of the world/setting")
    session_state: GameplayState = Field(default=GameplayState.INITIALIZING)
    therapeutic_goals: list[str] = Field(default_factory=list)
    safety_level: str = Field(default="standard")  # standard, elevated, crisis
    current_scene: NarrativeScene | None = None
    scene_history: list[str] = Field(default_factory=list)  # Scene IDs
    choice_history: list[str] = Field(default_factory=list)  # Choice IDs
    therapeutic_outcomes: list[TherapeuticOutcome] = Field(default_factory=list)
    session_metrics: SessionMetrics = Field(default_factory=SessionMetrics)
    narrative_context: dict[str, Any] = Field(default_factory=dict)
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    @field_validator("safety_level")
    @classmethod
    def validate_safety_level(cls, v):
        valid_levels = ["standard", "elevated", "crisis"]
        if v not in valid_levels:
            raise ValueError(f"Safety level must be one of: {valid_levels}")
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_session_consistency(cls, values):
        if isinstance(values, dict):
            state = values.get("session_state")
            completed_at = values.get("completed_at")

            if state == GameplayState.COMPLETED and completed_at is None:
                values["completed_at"] = datetime.utcnow()
            elif state != GameplayState.COMPLETED and completed_at is not None:
                raise ValueError(
                    "Completed timestamp should only be set for completed sessions"
                )

        return values

    def add_scene(self, scene: NarrativeScene) -> None:
        """Add a scene to the session history."""
        self.scene_history.append(scene.scene_id)
        self.current_scene = scene
        self.last_activity = datetime.utcnow()

    def add_choice(self, choice: UserChoice) -> None:
        """Add a choice to the session history."""
        self.choice_history.append(choice.choice_id)
        self.session_metrics.choices_made += 1
        self.last_activity = datetime.utcnow()

    def add_therapeutic_outcome(self, outcome: TherapeuticOutcome) -> None:
        """Add a therapeutic outcome to the session."""
        self.therapeutic_outcomes.append(outcome)
        self.session_metrics.therapeutic_moments += 1
        self.last_activity = datetime.utcnow()
