"""
Conversation State Management Models

This module defines the data models for managing conversational character creation
state, including conversation progress, collected data, and WebSocket message schemas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..services.conversation_scripts import ConversationStage
from .character import CharacterCreationData


class ConversationStatus(str, Enum):
    """Status of a conversation session."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"


class MessageType(str, Enum):
    """Types of WebSocket messages for character creation conversations."""

    # Client to Server
    START_CONVERSATION = "start_conversation"
    USER_RESPONSE = "user_response"
    PAUSE_CONVERSATION = "pause_conversation"
    RESUME_CONVERSATION = "resume_conversation"
    ABANDON_CONVERSATION = "abandon_conversation"

    # Server to Client
    CONVERSATION_STARTED = "conversation_started"
    ASSISTANT_MESSAGE = "assistant_message"
    PROGRESS_UPDATE = "progress_update"
    CONVERSATION_PAUSED = "conversation_paused"
    CONVERSATION_COMPLETED = "conversation_completed"
    VALIDATION_ERROR = "validation_error"
    CRISIS_DETECTED = "crisis_detected"
    ERROR = "error"


@dataclass
class ConversationProgress:
    """Tracks progress through conversation stages."""

    current_stage: ConversationStage
    current_prompt_id: str
    completed_stages: list[ConversationStage] = field(default_factory=list)
    total_stages: int = 13
    stage_progress: dict[ConversationStage, float] = field(default_factory=dict)

    @property
    def overall_progress(self) -> float:
        """Calculate overall conversation progress (0.0 to 1.0)."""
        if not self.completed_stages:
            return 0.0
        return len(self.completed_stages) / self.total_stages

    @property
    def progress_percentage(self) -> int:
        """Get progress as percentage (0-100)."""
        return int(self.overall_progress * 100)


@dataclass
class CollectedData:
    """Data collected during conversation."""

    # Basic Information
    name: str | None = None
    age_range: str | None = None
    gender_identity: str | None = None

    # Appearance
    physical_description: str | None = None
    clothing_style: str | None = None
    distinctive_features: list[str] = field(default_factory=list)

    # Background
    backstory: str | None = None
    personality_traits: list[str] = field(default_factory=list)
    core_values: list[str] = field(default_factory=list)
    strengths_and_skills: list[str] = field(default_factory=list)
    fears_and_anxieties: list[str] = field(default_factory=list)
    life_goals: list[str] = field(default_factory=list)
    relationships: dict[str, str] = field(default_factory=dict)

    # Therapeutic Profile
    primary_concerns: list[str] = field(default_factory=list)
    therapeutic_goals: list[str] = field(default_factory=list)
    preferred_intensity: str | None = None
    comfort_zones: list[str] = field(default_factory=list)
    challenge_areas: list[str] = field(default_factory=list)
    readiness_level: float | None = None

    def to_character_creation_data(self) -> CharacterCreationData:
        """Convert collected data to CharacterCreationData."""
        from .character import (
            CharacterAppearance,
            CharacterBackground,
            TherapeuticProfile,
        )

        # Create appearance
        appearance = CharacterAppearance(
            age_range=self.age_range or "adult",
            gender_identity=self.gender_identity or "non-binary",
            physical_description=self.physical_description or "",
            clothing_style=self.clothing_style or "casual",
            distinctive_features=self.distinctive_features,
        )

        # Create background
        background = CharacterBackground(
            name=self.name or "",
            backstory=self.backstory or "",
            personality_traits=self.personality_traits,
            core_values=self.core_values,
            fears_and_anxieties=self.fears_and_anxieties,
            strengths_and_skills=self.strengths_and_skills,
            life_goals=self.life_goals,
            relationships=self.relationships,
        )

        # Create therapeutic profile
        therapeutic_profile = TherapeuticProfile(
            primary_concerns=self.primary_concerns,
            preferred_intensity=self.preferred_intensity or "medium",
            comfort_zones=self.comfort_zones,
            challenge_areas=self.challenge_areas,
            readiness_level=self.readiness_level or 0.5,
        )

        return CharacterCreationData(
            name=self.name or "",
            appearance=appearance,
            background=background,
            therapeutic_profile=therapeutic_profile,
        )


@dataclass
class ConversationMessage:
    """A message in the conversation history."""

    message_id: str
    timestamp: datetime
    sender: str  # "assistant" or "user"
    content: str
    message_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """Complete state of a character creation conversation."""

    conversation_id: str
    player_id: str
    status: ConversationStatus
    progress: ConversationProgress
    collected_data: CollectedData
    message_history: list[ConversationMessage] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    # Session management
    last_activity: datetime = field(default_factory=datetime.utcnow)
    session_timeout_minutes: int = 30

    # Crisis and safety
    crisis_detected: bool = False
    safety_notes: list[str] = field(default_factory=list)

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if conversation session has expired."""
        if self.status in [ConversationStatus.COMPLETED, ConversationStatus.ABANDONED]:
            return False

        time_diff = datetime.utcnow() - self.last_activity
        return time_diff.total_seconds() > (self.session_timeout_minutes * 60)

    def add_message(
        self,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a message to conversation history."""
        import uuid

        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            message_id=message_id,
            timestamp=datetime.utcnow(),
            sender=sender,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )

        self.message_history.append(message)
        self.update_activity()
        return message_id


# WebSocket Message Schemas (Pydantic models for validation)


class StartConversationMessage(BaseModel):
    """Message to start a character creation conversation."""

    type: Literal[MessageType.START_CONVERSATION] = MessageType.START_CONVERSATION
    player_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserResponseMessage(BaseModel):
    """User response message."""

    type: Literal[MessageType.USER_RESPONSE] = MessageType.USER_RESPONSE
    conversation_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssistantMessage(BaseModel):
    """Assistant message to client."""

    type: Literal[MessageType.ASSISTANT_MESSAGE] = MessageType.ASSISTANT_MESSAGE
    conversation_id: str
    content: str
    prompt_id: str
    stage: ConversationStage
    context_text: str | None = None
    follow_up_prompts: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProgressUpdateMessage(BaseModel):
    """Progress update message."""

    type: Literal[MessageType.PROGRESS_UPDATE] = MessageType.PROGRESS_UPDATE
    conversation_id: str
    progress: dict[str, Any]  # Serialized ConversationProgress
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationCompletedMessage(BaseModel):
    """Conversation completion message."""

    type: Literal[MessageType.CONVERSATION_COMPLETED] = (
        MessageType.CONVERSATION_COMPLETED
    )
    conversation_id: str
    character_preview: dict[str, Any]  # Serialized character data
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorMessage(BaseModel):
    """Validation error message."""

    type: Literal[MessageType.VALIDATION_ERROR] = MessageType.VALIDATION_ERROR
    conversation_id: str
    error_message: str
    field_name: str | None = None
    retry_prompt: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrisisDetectedMessage(BaseModel):
    """Crisis detection message."""

    type: Literal[MessageType.CRISIS_DETECTED] = MessageType.CRISIS_DETECTED
    conversation_id: str
    crisis_level: str  # "low", "medium", "high", "emergency"
    support_message: str
    resources: list[dict[str, str]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorMessage(BaseModel):
    """Error message."""

    type: Literal[MessageType.ERROR] = MessageType.ERROR
    conversation_id: str | None = None
    error_code: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Union type for all message types
WebSocketMessage = (
    StartConversationMessage
    | UserResponseMessage
    | AssistantMessage
    | ProgressUpdateMessage
    | ConversationCompletedMessage
    | ValidationErrorMessage
    | CrisisDetectedMessage
    | ErrorMessage
)


# API Response Models


class ConversationStateResponse(BaseModel):
    """Response model for conversation state."""

    conversation_id: str
    status: ConversationStatus
    progress: dict[str, Any]
    current_stage: ConversationStage
    current_prompt: str | None = None
    created_at: datetime
    updated_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""

    conversation_id: str
    messages: list[dict[str, Any]]
    total_messages: int
    page: int = 1
    page_size: int = 50


class CharacterPreviewResponse(BaseModel):
    """Response model for character preview."""

    conversation_id: str
    character_data: dict[str, Any]
    completeness_score: float  # 0.0 to 1.0
    missing_fields: list[str] = Field(default_factory=list)
    ready_for_creation: bool
