"""
User Interaction Models

This module defines data structures for user interactions, validation,
and response handling in the therapeutic gameplay loop.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class InteractionType(str, Enum):
    """Types of user interactions."""
    TEXT_INPUT = "text_input"
    CHOICE_SELECTION = "choice_selection"
    EMOTIONAL_RESPONSE = "emotional_response"
    REFLECTION_INPUT = "reflection_input"
    SKILL_PRACTICE = "skill_practice"
    SAFETY_REQUEST = "safety_request"
    PAUSE_REQUEST = "pause_request"
    HELP_REQUEST = "help_request"


class ValidationStatus(str, Enum):
    """Status of interaction validation."""
    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_REVIEW = "requires_review"
    SAFETY_CONCERN = "safety_concern"
    THERAPEUTIC_OPPORTUNITY = "therapeutic_opportunity"


class ResponseType(str, Enum):
    """Types of responses to user interactions."""
    ACKNOWLEDGMENT = "acknowledgment"
    CLARIFICATION = "clarification"
    THERAPEUTIC_GUIDANCE = "therapeutic_guidance"
    SAFETY_INTERVENTION = "safety_intervention"
    NARRATIVE_CONTINUATION = "narrative_continuation"
    SKILL_REINFORCEMENT = "skill_reinforcement"


class InteractionContext(BaseModel):
    """Context information for user interactions."""
    session_id: str = Field(..., description="ID of the current session")
    scene_id: Optional[str] = Field(None, description="ID of the current scene")
    user_emotional_state: Dict[str, float] = Field(default_factory=dict)
    therapeutic_goals: List[str] = Field(default_factory=list)
    recent_interactions: List[str] = Field(default_factory=list)  # Recent interaction IDs
    narrative_context: Dict[str, Any] = Field(default_factory=dict)
    safety_level: str = Field(default="standard")
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('user_emotional_state')
    @classmethod
    def validate_emotional_state(cls, v):
        for emotion, intensity in v.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(f'Emotional intensity for {emotion} must be between 0.0 and 1.0')
        return v


class InteractionValidation(BaseModel):
    """Validation result for user interactions."""
    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    interaction_id: str = Field(..., description="ID of the interaction being validated")
    status: ValidationStatus = Field(..., description="Validation status")
    safety_score: float = Field(..., ge=0.0, le=1.0, description="Safety assessment score")
    therapeutic_relevance: float = Field(..., ge=0.0, le=1.0, description="Therapeutic relevance score")
    emotional_appropriateness: float = Field(..., ge=0.0, le=1.0, description="Emotional appropriateness score")
    validation_notes: List[str] = Field(default_factory=list)
    safety_concerns: List[str] = Field(default_factory=list)
    therapeutic_opportunities: List[str] = Field(default_factory=list)
    recommended_responses: List[str] = Field(default_factory=list)
    requires_human_review: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('safety_score', 'therapeutic_relevance', 'emotional_appropriateness')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v


class InteractionResponse(BaseModel):
    """Response to a user interaction."""
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    interaction_id: str = Field(..., description="ID of the interaction being responded to")
    response_type: ResponseType = Field(..., description="Type of response")
    response_content: str = Field(..., description="Content of the response")
    therapeutic_intent: List[str] = Field(default_factory=list)
    emotional_tone: Dict[str, float] = Field(default_factory=dict)
    follow_up_actions: List[str] = Field(default_factory=list)
    narrative_impact: Dict[str, Any] = Field(default_factory=dict)
    safety_considerations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('emotional_tone')
    @classmethod
    def validate_emotional_tone(cls, v):
        for emotion, intensity in v.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(f'Emotional intensity for {emotion} must be between 0.0 and 1.0')
        return v


class UserInteraction(BaseModel):
    """Represents a user interaction during gameplay."""
    interaction_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="ID of the session")
    user_id: str = Field(..., description="ID of the user")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    content: str = Field(..., description="Content of the interaction")
    context: InteractionContext = Field(..., description="Context of the interaction")
    validation: Optional[InteractionValidation] = Field(None, description="Validation result")
    response: Optional[InteractionResponse] = Field(None, description="Response to the interaction")
    processing_time_ms: Optional[float] = Field(None, description="Time taken to process interaction")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(None, description="When interaction was processed")
    
    def mark_processed(self, processing_time_ms: float = None) -> None:
        """Mark the interaction as processed."""
        self.processed_at = datetime.utcnow()
        if processing_time_ms is not None:
            self.processing_time_ms = processing_time_ms
    
    def add_validation(self, validation: InteractionValidation) -> None:
        """Add validation result to the interaction."""
        self.validation = validation
    
    def add_response(self, response: InteractionResponse) -> None:
        """Add response to the interaction."""
        self.response = response
    
    def is_safe(self) -> bool:
        """Check if the interaction is considered safe."""
        if self.validation is None:
            return True  # Default to safe if not validated
        return (
            self.validation.status not in [ValidationStatus.SAFETY_CONCERN] and
            self.validation.safety_score >= 0.7
        )
    
    def requires_therapeutic_attention(self) -> bool:
        """Check if the interaction requires therapeutic attention."""
        if self.validation is None:
            return False
        return (
            self.validation.status == ValidationStatus.THERAPEUTIC_OPPORTUNITY or
            self.validation.therapeutic_relevance >= 0.8
        )
    
    def get_emotional_intensity(self) -> float:
        """Get the overall emotional intensity of the interaction."""
        if not self.context.user_emotional_state:
            return 0.0
        return sum(self.context.user_emotional_state.values()) / len(self.context.user_emotional_state)


class InteractionBatch(BaseModel):
    """Batch of interactions for processing efficiency."""
    batch_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="ID of the session")
    interactions: List[UserInteraction] = Field(default_factory=list)
    batch_context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(None)
    processing_time_ms: Optional[float] = Field(None)
    
    def add_interaction(self, interaction: UserInteraction) -> None:
        """Add an interaction to the batch."""
        self.interactions.append(interaction)
    
    def mark_processed(self, processing_time_ms: float = None) -> None:
        """Mark the batch as processed."""
        self.processed_at = datetime.utcnow()
        if processing_time_ms is not None:
            self.processing_time_ms = processing_time_ms
        
        # Mark all interactions as processed
        for interaction in self.interactions:
            interaction.mark_processed()
    
    def get_safety_concerns(self) -> List[UserInteraction]:
        """Get interactions with safety concerns."""
        return [
            interaction for interaction in self.interactions
            if not interaction.is_safe()
        ]
    
    def get_therapeutic_opportunities(self) -> List[UserInteraction]:
        """Get interactions with therapeutic opportunities."""
        return [
            interaction for interaction in self.interactions
            if interaction.requires_therapeutic_attention()
        ]
