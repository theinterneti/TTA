"""
Progress Tracking Models for Gameplay Loop

This module defines models for tracking therapeutic progress, character development,
and skill acquisition within the therapeutic text adventure system.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from .core import DifficultyLevel, EmotionalState


class ProgressType(str, Enum):
    """Types of progress markers."""

    SKILL_ACQUIRED = "skill_acquired"
    MILESTONE_REACHED = "milestone_reached"
    THERAPEUTIC_BREAKTHROUGH = "therapeutic_breakthrough"
    EMOTIONAL_REGULATION = "emotional_regulation"
    SOCIAL_INTERACTION = "social_interaction"
    COPING_STRATEGY = "coping_strategy"
    INSIGHT_GAINED = "insight_gained"


class SkillCategory(str, Enum):
    """Categories of skills that can be developed."""

    EMOTIONAL_REGULATION = "emotional_regulation"
    MINDFULNESS = "mindfulness"
    COMMUNICATION = "communication"
    PROBLEM_SOLVING = "problem_solving"
    STRESS_MANAGEMENT = "stress_management"
    SELF_AWARENESS = "self_awareness"
    RESILIENCE = "resilience"
    EMPATHY = "empathy"


class CharacterAttribute(str, Enum):
    """Character attributes that can be developed."""

    CONFIDENCE = "confidence"
    EMPATHY = "empathy"
    RESILIENCE = "resilience"
    WISDOM = "wisdom"
    COURAGE = "courage"
    COMPASSION = "compassion"
    PATIENCE = "patience"
    CREATIVITY = "creativity"


class ProgressMarker(BaseModel):
    """A marker indicating progress in therapeutic development."""

    marker_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")

    # Progress details
    progress_type: ProgressType = Field(..., description="Type of progress")
    title: str = Field(..., description="Progress title")
    description: str = Field(..., description="Progress description")

    # Context
    triggered_by_choice: str | None = Field(
        None, description="Choice that triggered this progress"
    )
    scene_context: str | None = Field(None, description="Scene where progress occurred")

    # Measurement
    progress_value: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Quantified progress value"
    )
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.STANDARD)

    # Therapeutic significance
    therapeutic_domains: list[str] = Field(default_factory=list)
    skills_involved: list[SkillCategory] = Field(default_factory=list)

    # Metadata
    achieved_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SkillDevelopment(BaseModel):
    """Tracking of skill development over time."""

    skill_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="User identifier")

    # Skill details
    skill_category: SkillCategory = Field(..., description="Category of skill")
    skill_name: str = Field(..., description="Specific skill name")
    description: str = Field(..., description="Skill description")

    # Progress tracking
    current_level: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Current skill level"
    )
    target_level: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Target skill level"
    )

    # Development history
    practice_sessions: int = Field(default=0, description="Number of practice sessions")
    successful_applications: int = Field(
        default=0, description="Successful applications"
    )
    total_attempts: int = Field(default=0, description="Total attempts")

    # Learning curve
    learning_rate: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Rate of learning"
    )
    retention_rate: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Skill retention rate"
    )

    # Context
    therapeutic_goals: list[str] = Field(default_factory=list)
    related_skills: list[str] = Field(default_factory=list)

    # Metadata
    first_practiced: datetime = Field(default_factory=datetime.utcnow)
    last_practiced: datetime | None = Field(None)
    mastery_achieved: datetime | None = Field(None)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def update_skill_level(self, practice_outcome: float) -> None:
        """Update skill level based on practice outcome."""
        self.total_attempts += 1
        if practice_outcome > 0.5:
            self.successful_applications += 1

        # Calculate new skill level using learning rate
        improvement = self.learning_rate * (practice_outcome - self.current_level)
        self.current_level = min(1.0, self.current_level + improvement)

        # Apply retention decay if not practiced recently
        if self.last_practiced:
            days_since_practice = (datetime.utcnow() - self.last_practiced).days
            if days_since_practice > 7:
                decay = (1 - self.retention_rate) * (days_since_practice / 30)
                self.current_level = max(0.0, self.current_level - decay)

        self.last_practiced = datetime.utcnow()

        # Check for mastery
        if self.current_level >= self.target_level and not self.mastery_achieved:
            self.mastery_achieved = datetime.utcnow()


class CharacterState(BaseModel):
    """Current state of the player's character."""

    character_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Current session identifier")

    # Character identity
    name: str = Field(..., description="Character name")
    background: str = Field(default="", description="Character background")

    # Attributes
    attributes: dict[CharacterAttribute, float] = Field(
        default_factory=lambda: dict.fromkeys(CharacterAttribute, 0.5)
    )

    # Relationships
    relationships: dict[str, float] = Field(
        default_factory=dict, description="Relationships with other characters"
    )

    # Current state
    current_emotional_state: EmotionalState = Field(default=EmotionalState.CALM)
    energy_level: float = Field(default=1.0, ge=0.0, le=1.0)
    stress_level: float = Field(default=0.0, ge=0.0, le=1.0)

    # Progress
    total_experience: int = Field(default=0, description="Total experience points")
    level: int = Field(default=1, description="Character level")

    # Inventory and resources
    inventory: list[str] = Field(default_factory=list)
    resources: dict[str, int] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def modify_attribute(self, attribute: CharacterAttribute, change: float) -> None:
        """Modify a character attribute."""
        current_value = self.attributes.get(attribute, 0.5)
        new_value = max(0.0, min(1.0, current_value + change))
        self.attributes[attribute] = new_value
        self.updated_at = datetime.utcnow()

    def add_experience(self, amount: int) -> bool:
        """Add experience and check for level up."""
        self.total_experience += amount

        # Simple level calculation: level = sqrt(experience / 100)
        new_level = int((self.total_experience / 100) ** 0.5) + 1

        if new_level > self.level:
            self.level = new_level
            self.updated_at = datetime.utcnow()
            return True  # Level up occurred

        return False


class TherapeuticProgress(BaseModel):
    """Overall therapeutic progress tracking."""

    progress_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(..., description="User identifier")

    # Goals and objectives
    primary_therapeutic_goals: list[str] = Field(default_factory=list)
    secondary_goals: list[str] = Field(default_factory=list)
    completed_goals: list[str] = Field(default_factory=list)

    # Progress metrics
    overall_progress: float = Field(default=0.0, ge=0.0, le=1.0)
    goal_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    engagement_level: float = Field(default=0.0, ge=0.0, le=1.0)

    # Skill development
    developed_skills: list[str] = Field(default_factory=list)
    skills_in_progress: list[str] = Field(default_factory=list)

    # Therapeutic milestones
    milestones_achieved: list[str] = Field(default_factory=list)
    breakthrough_moments: list[str] = Field(default_factory=list)

    # Session statistics
    total_sessions: int = Field(default=0)
    total_session_time: float = Field(default=0.0)
    average_session_length: float = Field(default=0.0)

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
