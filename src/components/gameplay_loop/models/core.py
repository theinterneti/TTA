"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Models/Core]]

# Logseq: [[TTA/Components/Gameplay_loop/Models/Core]]
Core Data Models for Gameplay Loop

This module defines the fundamental data structures for the therapeutic text adventure
gameplay loop system, including session state, scenes, choices, and consequences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Adaptive difficulty levels for therapeutic content."""

    GENTLE = "gentle"
    STANDARD = "standard"
    CHALLENGING = "challenging"
    INTENSIVE = "intensive"


class EmotionalState(str, Enum):
    """Current emotional state indicators."""

    CALM = "calm"
    ENGAGED = "engaged"
    ANXIOUS = "anxious"
    OVERWHELMED = "overwhelmed"
    DISTRESSED = "distressed"
    CRISIS = "crisis"


class SceneType(str, Enum):
    """Types of narrative scenes."""

    INTRODUCTION = "introduction"
    EXPLORATION = "exploration"
    CHALLENGE = "challenge"
    REFLECTION = "reflection"
    THERAPEUTIC = "therapeutic"
    RESOLUTION = "resolution"


class ChoiceType(str, Enum):
    """Types of player choices."""

    NARRATIVE = "narrative"
    THERAPEUTIC = "therapeutic"
    SKILL_BUILDING = "skill_building"
    EMOTIONAL_REGULATION = "emotional_regulation"
    SOCIAL_INTERACTION = "social_interaction"


@dataclass
class TherapeuticContext:
    """Therapeutic context and goals for a session."""

    primary_goals: list[str] = field(default_factory=list)
    secondary_goals: list[str] = field(default_factory=list)
    therapeutic_modalities: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    safety_protocols: list[str] = field(default_factory=list)

    # Progress tracking
    session_objectives: list[str] = field(default_factory=list)
    completed_objectives: list[str] = field(default_factory=list)
    therapeutic_insights: list[str] = field(default_factory=list)


@dataclass
class GameplayMetrics:
    """Performance and engagement metrics for a session."""

    total_choices_made: int = 0
    therapeutic_choices_made: int = 0
    average_response_time: float = 0.0
    engagement_score: float = 0.0
    therapeutic_effectiveness: float = 0.0

    # Timing metrics
    session_duration: float = 0.0
    active_time: float = 0.0
    pause_time: float = 0.0

    # Safety metrics
    safety_interventions: int = 0
    crisis_alerts: int = 0
    emotional_state_changes: list[str] = field(default_factory=list)


class Scene(BaseModel):
    """A narrative scene within the therapeutic text adventure."""

    scene_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Scene title")
    description: str = Field(..., description="Scene description")
    narrative_content: str = Field(..., description="Main narrative text")

    # Scene metadata
    scene_type: SceneType = Field(default=SceneType.EXPLORATION)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.STANDARD)
    estimated_duration: int = Field(
        default=300, description="Estimated duration in seconds"
    )

    # Therapeutic elements
    therapeutic_focus: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(default_factory=list)
    emotional_tone: str = Field(default="neutral")

    # Scene state
    is_completed: bool = Field(default=False)
    completion_time: datetime | None = Field(default=None)
    player_choices_made: list[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Choice(BaseModel):
    """A player choice option within a scene."""

    choice_id: str = Field(default_factory=lambda: str(uuid4()))
    scene_id: str = Field(..., description="Parent scene ID")

    # Choice content
    text: str = Field(..., description="Choice text displayed to player")
    description: str | None = Field(None, description="Additional choice description")

    # Choice metadata
    choice_type: ChoiceType = Field(default=ChoiceType.NARRATIVE)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.STANDARD)
    therapeutic_value: float = Field(default=0.0, ge=0.0, le=1.0)

    # Requirements and conditions
    prerequisites: list[str] = Field(default_factory=list)
    emotional_requirements: list[EmotionalState] = Field(default_factory=list)
    skill_requirements: list[str] = Field(default_factory=list)

    # Consequences
    immediate_consequences: list[str] = Field(default_factory=list)
    long_term_consequences: list[str] = Field(default_factory=list)
    therapeutic_outcomes: list[str] = Field(default_factory=list)

    # Availability
    is_available: bool = Field(default=True)
    availability_reason: str | None = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsequenceSet(BaseModel):
    """A set of consequences resulting from player choices."""

    consequence_id: str = Field(default_factory=lambda: str(uuid4()))
    choice_id: str = Field(..., description="Triggering choice ID")
    session_id: str = Field(..., description="Session ID")

    # Consequence details
    immediate_effects: dict[str, Any] = Field(default_factory=dict)
    delayed_effects: dict[str, Any] = Field(default_factory=dict)
    narrative_changes: list[str] = Field(default_factory=list)

    # Character impact
    character_attribute_changes: dict[str, float] = Field(default_factory=dict)
    skill_developments: list[str] = Field(default_factory=list)
    relationship_changes: dict[str, float] = Field(default_factory=dict)

    # Therapeutic impact
    therapeutic_progress: dict[str, float] = Field(default_factory=dict)
    emotional_impact: dict[EmotionalState, float] = Field(default_factory=dict)
    learning_outcomes: list[str] = Field(default_factory=list)

    # Execution state
    is_applied: bool = Field(default=False)
    application_time: datetime | None = Field(default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionState(BaseModel):
    """Complete state of a therapeutic gameplay session."""

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="User identifier")
    character_id: str | None = Field(None, description="Character identifier")
    world_id: str | None = Field(None, description="World identifier")

    # Current state
    current_scene: Scene | None = Field(None, description="Current active scene")
    current_scene_id: str | None = Field(None, description="Current scene ID")

    # Session context
    therapeutic_context: TherapeuticContext = Field(default_factory=TherapeuticContext)
    emotional_state: EmotionalState = Field(default=EmotionalState.CALM)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.STANDARD)

    # History and progress
    choice_history: list[dict[str, Any]] = Field(default_factory=list)
    scene_history: list[str] = Field(default_factory=list)
    consequence_stack: list[ConsequenceSet] = Field(default_factory=list)

    # Session timing
    session_start_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity_time: datetime = Field(default_factory=datetime.utcnow)
    total_session_time: float = Field(default=0.0)

    # Performance metrics
    metrics: GameplayMetrics = Field(default_factory=GameplayMetrics)

    # Session state flags
    is_active: bool = Field(default=True)
    is_paused: bool = Field(default=False)
    requires_therapeutic_intervention: bool = Field(default=False)

    # Safety and validation
    safety_level: str = Field(default="standard")
    last_safety_check: datetime | None = Field(default=None)
    safety_alerts: list[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_activity(self) -> None:
        """Update last activity time and session duration."""
        now = datetime.utcnow()
        if not self.is_paused:
            time_delta = (now - self.last_activity_time).total_seconds()
            self.total_session_time += time_delta
            self.metrics.active_time += time_delta

        self.last_activity_time = now
        self.updated_at = now

    def add_choice_to_history(self, choice: Choice, outcome: dict[str, Any]) -> None:
        """Add a choice and its outcome to the session history."""
        choice_record = {
            "choice_id": choice.choice_id,
            "choice_text": choice.text,
            "choice_type": choice.choice_type,
            "therapeutic_value": choice.therapeutic_value,
            "timestamp": datetime.utcnow().isoformat(),
            "outcome": outcome,
        }
        self.choice_history.append(choice_record)
        self.metrics.total_choices_made += 1

        if choice.choice_type in [
            ChoiceType.THERAPEUTIC,
            ChoiceType.SKILL_BUILDING,
            ChoiceType.EMOTIONAL_REGULATION,
        ]:
            self.metrics.therapeutic_choices_made += 1

    def transition_to_scene(self, scene: Scene) -> None:
        """Transition to a new scene."""
        if self.current_scene_id:
            self.scene_history.append(self.current_scene_id)

        self.current_scene = scene
        self.current_scene_id = scene.scene_id
        self.update_activity()

    def calculate_engagement_score(self) -> float:
        """Calculate current engagement score based on activity."""
        if self.total_session_time == 0:
            return 0.0

        # Base engagement on choice frequency and therapeutic participation
        choice_rate = self.metrics.total_choices_made / (
            self.total_session_time / 60
        )  # choices per minute
        therapeutic_ratio = self.metrics.therapeutic_choices_made / max(
            self.metrics.total_choices_made, 1
        )

        # Normalize and combine metrics
        engagement = min(1.0, (choice_rate / 2.0) * 0.7 + therapeutic_ratio * 0.3)
        self.metrics.engagement_score = engagement
        return engagement
