"""
Gameplay WebSocket Message Schemas

This module defines Pydantic models for gameplay WebSocket messages including
story events, choice presentations, narrative responses, and therapeutic interventions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class GameplayMessageType(str, Enum):
    """Types of gameplay WebSocket messages."""

    # Client to Server Messages
    START_GAMEPLAY = "start_gameplay"
    PLAYER_ACTION = "player_action"
    CHOICE_SELECTION = "choice_selection"
    BREAK_RESPONSE = "break_response"
    END_SESSION = "end_session"
    PAUSE_SESSION = "pause_session"
    RESUME_SESSION = "resume_session"

    # Server to Client Messages
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    NARRATIVE_RESPONSE = "narrative_response"
    CHOICE_REQUEST = "choice_request"
    STORY_EVENT = "story_event"
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"
    BREAK_POINT_DETECTED = "break_point_detected"
    SESSION_UPDATE = "session_update"
    SYSTEM_MESSAGE = "system_message"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class ActionType(str, Enum):
    """Types of player actions."""

    NARRATIVE_INPUT = "narrative_input"
    DIALOGUE_RESPONSE = "dialogue_response"
    EXPLORATION = "exploration"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION = "reflection"
    THERAPEUTIC_EXERCISE = "therapeutic_exercise"


class InterventionType(str, Enum):
    """Types of therapeutic interventions."""

    SAFETY_GUIDANCE = "safety_guidance"
    EMOTIONAL_SUPPORT = "emotional_support"
    SKILL_REMINDER = "skill_reminder"
    CRISIS_RESPONSE = "crisis_response"
    ENCOURAGEMENT = "encouragement"
    REFLECTION_PROMPT = "reflection_prompt"


class BreakPointType(str, Enum):
    """Types of break points."""

    SCENE_TRANSITION = "scene_transition"
    SKILL_COMPLETION = "skill_completion"
    EMOTIONAL_PROCESSING = "emotional_processing"
    REFLECTION_MOMENT = "reflection_moment"
    MILESTONE_ACHIEVEMENT = "milestone_achievement"
    TIME_BASED = "time_based"
    USER_REQUESTED = "user_requested"
    THERAPEUTIC_CHECKPOINT = "therapeutic_checkpoint"


# Base Message Models


class BaseGameplayMessage(BaseModel):
    """Base model for all gameplay WebSocket messages."""

    type: GameplayMessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# Client to Server Messages


class StartGameplayMessage(BaseGameplayMessage):
    """Message to start a new gameplay session."""

    type: Literal[GameplayMessageType.START_GAMEPLAY] = (
        GameplayMessageType.START_GAMEPLAY
    )
    character_id: str = Field(..., description="Character ID for the gameplay session")
    world_id: str | None = Field(
        None, description="Optional world ID for story setting"
    )
    therapeutic_goals: list[str] = Field(
        default_factory=list, description="Therapeutic goals for the session"
    )
    session_preferences: dict[str, Any] = Field(
        default_factory=dict, description="Session preferences and settings"
    )


class PlayerActionMessage(BaseGameplayMessage):
    """Message representing a player action."""

    type: Literal[GameplayMessageType.PLAYER_ACTION] = GameplayMessageType.PLAYER_ACTION
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Action content")
    action_type: ActionType = Field(
        ActionType.NARRATIVE_INPUT, description="Type of player action"
    )

    class Config:
        schema_extra = {
            "example": {
                "type": "player_action",
                "session_id": "session_123",
                "content": {
                    "text": "I want to explore the mysterious door",
                    "context": "standing_in_hallway",
                },
                "action_type": "exploration",
            }
        }


class ChoiceSelectionMessage(BaseGameplayMessage):
    """Message for player choice selection."""

    type: Literal[GameplayMessageType.CHOICE_SELECTION] = (
        GameplayMessageType.CHOICE_SELECTION
    )
    session_id: str = Field(..., description="Active session ID")
    choice_id: str = Field(..., description="Selected choice ID")
    choice_text: str = Field(..., description="Text of the selected choice")
    choice_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional choice metadata"
    )


class BreakResponseMessage(BaseGameplayMessage):
    """Message responding to a break point."""

    type: Literal[GameplayMessageType.BREAK_RESPONSE] = (
        GameplayMessageType.BREAK_RESPONSE
    )
    session_id: str = Field(..., description="Active session ID")
    response: str = Field(
        ...,
        description="Break response: 'take_break', 'continue_playing', or 'end_session'",
    )
    break_duration: int | None = Field(
        None, description="Requested break duration in minutes"
    )


class EndSessionMessage(BaseGameplayMessage):
    """Message to end a gameplay session."""

    type: Literal[GameplayMessageType.END_SESSION] = GameplayMessageType.END_SESSION
    session_id: str = Field(..., description="Session ID to end")
    completion_reason: str = Field(
        "user_completed", description="Reason for ending the session"
    )


# Server to Client Messages


class SessionStartedMessage(BaseGameplayMessage):
    """Message confirming session start."""

    type: Literal[GameplayMessageType.SESSION_STARTED] = (
        GameplayMessageType.SESSION_STARTED
    )
    session_id: str = Field(..., description="Started session ID")
    content: dict[str, Any] = Field(..., description="Session start information")


class NarrativeResponseMessage(BaseGameplayMessage):
    """Message containing narrative response from the AI."""

    type: Literal[GameplayMessageType.NARRATIVE_RESPONSE] = (
        GameplayMessageType.NARRATIVE_RESPONSE
    )
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Narrative content")

    class Config:
        schema_extra = {
            "example": {
                "type": "narrative_response",
                "session_id": "session_123",
                "content": {
                    "text": "As you approach the mysterious door, you notice ancient symbols carved into its surface...",
                    "scene_id": "mysterious_hallway",
                    "emotional_tone": "mysterious",
                    "therapeutic_elements": ["curiosity", "courage"],
                },
            }
        }


class ChoiceRequestMessage(BaseGameplayMessage):
    """Message presenting choices to the player."""

    type: Literal[GameplayMessageType.CHOICE_REQUEST] = (
        GameplayMessageType.CHOICE_REQUEST
    )
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Choice presentation content")

    class Config:
        schema_extra = {
            "example": {
                "type": "choice_request",
                "session_id": "session_123",
                "content": {
                    "prompt": "What do you do?",
                    "choices": [
                        {
                            "id": "choice_1",
                            "text": "Open the door carefully",
                            "therapeutic_value": "courage_building",
                        },
                        {
                            "id": "choice_2",
                            "text": "Examine the symbols first",
                            "therapeutic_value": "mindful_observation",
                        },
                    ],
                },
            }
        }


class StoryEventMessage(BaseGameplayMessage):
    """Message for story events and narrative developments."""

    type: Literal[GameplayMessageType.STORY_EVENT] = GameplayMessageType.STORY_EVENT
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Story event content")

    class Config:
        schema_extra = {
            "example": {
                "type": "story_event",
                "session_id": "session_123",
                "content": {
                    "event_type": "character_introduction",
                    "title": "A Mysterious Stranger",
                    "description": "A hooded figure emerges from the shadows...",
                    "characters_involved": ["mysterious_stranger"],
                    "location": "dark_alley",
                    "therapeutic_themes": ["trust", "social_anxiety"],
                },
            }
        }


class TherapeuticInterventionMessage(BaseGameplayMessage):
    """Message for therapeutic interventions and guidance."""

    type: Literal[GameplayMessageType.THERAPEUTIC_INTERVENTION] = (
        GameplayMessageType.THERAPEUTIC_INTERVENTION
    )
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Intervention content")

    class Config:
        schema_extra = {
            "example": {
                "type": "therapeutic_intervention",
                "session_id": "session_123",
                "content": {
                    "intervention_type": "emotional_support",
                    "message": "I notice you're feeling anxious about this situation. That's completely normal.",
                    "resources": [
                        {
                            "type": "breathing_exercise",
                            "title": "4-7-8 Breathing",
                            "description": "A calming breathing technique",
                        }
                    ],
                    "severity": "low",
                },
            }
        }


class BreakPointDetectedMessage(BaseGameplayMessage):
    """Message for detected break points."""

    type: Literal[GameplayMessageType.BREAK_POINT_DETECTED] = (
        GameplayMessageType.BREAK_POINT_DETECTED
    )
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Break point information")

    class Config:
        schema_extra = {
            "example": {
                "type": "break_point_detected",
                "session_id": "session_123",
                "content": {
                    "break_point_type": "emotional_processing",
                    "message": "That was emotionally significant. Would you like some time to process?",
                    "suggested_duration": 5,
                    "options": ["take_break", "continue_playing", "end_session"],
                },
            }
        }


class SessionUpdateMessage(BaseGameplayMessage):
    """Message for session state updates."""

    type: Literal[GameplayMessageType.SESSION_UPDATE] = (
        GameplayMessageType.SESSION_UPDATE
    )
    session_id: str = Field(..., description="Active session ID")
    content: dict[str, Any] = Field(..., description="Update content")


class SystemMessage(BaseGameplayMessage):
    """System message for general notifications."""

    type: Literal[GameplayMessageType.SYSTEM_MESSAGE] = (
        GameplayMessageType.SYSTEM_MESSAGE
    )
    content: dict[str, Any] = Field(..., description="System message content")


class ErrorMessage(BaseGameplayMessage):
    """Error message for handling failures."""

    type: Literal[GameplayMessageType.ERROR] = GameplayMessageType.ERROR
    content: dict[str, Any] = Field(..., description="Error information")

    class Config:
        schema_extra = {
            "example": {
                "type": "error",
                "content": {
                    "error": "Invalid session ID",
                    "code": "INVALID_SESSION",
                    "details": "Session session_123 not found or expired",
                },
            }
        }


class HeartbeatMessage(BaseGameplayMessage):
    """Heartbeat message for connection monitoring."""

    type: Literal[GameplayMessageType.HEARTBEAT] = GameplayMessageType.HEARTBEAT
    content: dict[str, Any] = Field(default_factory=dict, description="Heartbeat data")


# Union Types for Message Validation

GameplayWebSocketMessage = (
    # Client to Server
    StartGameplayMessage
    | PlayerActionMessage
    | ChoiceSelectionMessage
    | BreakResponseMessage
    | EndSessionMessage
    # Server to Client
    | SessionStartedMessage
    | NarrativeResponseMessage
    | ChoiceRequestMessage
    | StoryEventMessage
    | TherapeuticInterventionMessage
    | BreakPointDetectedMessage
    | SessionUpdateMessage
    | SystemMessage
    | ErrorMessage
    | HeartbeatMessage
)


# Helper Models for Complex Content


class Choice(BaseModel):
    """Model for individual choices in choice requests."""

    id: str = Field(..., description="Unique choice identifier")
    text: str = Field(..., description="Choice text displayed to player")
    therapeutic_value: str | None = Field(
        None, description="Therapeutic benefit of this choice"
    )
    consequences: list[str] = Field(
        default_factory=list, description="Potential consequences"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional choice metadata"
    )


class TherapeuticResource(BaseModel):
    """Model for therapeutic resources and tools."""

    type: str = Field(..., description="Type of resource (exercise, article, etc.)")
    title: str = Field(..., description="Resource title")
    description: str = Field(..., description="Resource description")
    url: str | None = Field(None, description="Optional URL for external resources")
    duration_minutes: int | None = Field(
        None, description="Estimated duration in minutes"
    )
    difficulty_level: str | None = Field(
        None, description="Difficulty level (easy, medium, hard)"
    )


class SessionProgress(BaseModel):
    """Model for session progress information."""

    scenes_completed: int = Field(0, description="Number of scenes completed")
    choices_made: int = Field(0, description="Number of choices made")
    therapeutic_skills_practiced: list[str] = Field(
        default_factory=list, description="Skills practiced"
    )
    emotional_milestones: list[str] = Field(
        default_factory=list, description="Emotional milestones reached"
    )
    session_duration_minutes: int = Field(0, description="Current session duration")
    break_points_taken: int = Field(0, description="Number of breaks taken")


class NarrativeContext(BaseModel):
    """Model for narrative context information."""

    scene_id: str = Field(..., description="Current scene identifier")
    location: str = Field(..., description="Current location")
    characters_present: list[str] = Field(
        default_factory=list, description="Characters in current scene"
    )
    emotional_tone: str = Field("neutral", description="Current emotional tone")
    therapeutic_themes: list[str] = Field(
        default_factory=list, description="Active therapeutic themes"
    )
    player_state: dict[str, Any] = Field(
        default_factory=dict, description="Player character state"
    )


# Validation Functions


def validate_gameplay_message(message_data: dict[str, Any]) -> GameplayWebSocketMessage:
    """
    Validate and parse a gameplay WebSocket message.

    Args:
        message_data: Raw message data from WebSocket

    Returns:
        Validated GameplayWebSocketMessage instance

    Raises:
        ValidationError: If message format is invalid
    """
    message_type = message_data.get("type")

    # Map message types to their corresponding models
    message_type_map = {
        GameplayMessageType.START_GAMEPLAY: StartGameplayMessage,
        GameplayMessageType.PLAYER_ACTION: PlayerActionMessage,
        GameplayMessageType.CHOICE_SELECTION: ChoiceSelectionMessage,
        GameplayMessageType.BREAK_RESPONSE: BreakResponseMessage,
        GameplayMessageType.END_SESSION: EndSessionMessage,
        GameplayMessageType.SESSION_STARTED: SessionStartedMessage,
        GameplayMessageType.NARRATIVE_RESPONSE: NarrativeResponseMessage,
        GameplayMessageType.CHOICE_REQUEST: ChoiceRequestMessage,
        GameplayMessageType.STORY_EVENT: StoryEventMessage,
        GameplayMessageType.THERAPEUTIC_INTERVENTION: TherapeuticInterventionMessage,
        GameplayMessageType.BREAK_POINT_DETECTED: BreakPointDetectedMessage,
        GameplayMessageType.SESSION_UPDATE: SessionUpdateMessage,
        GameplayMessageType.SYSTEM_MESSAGE: SystemMessage,
        GameplayMessageType.ERROR: ErrorMessage,
        GameplayMessageType.HEARTBEAT: HeartbeatMessage,
    }

    message_class = message_type_map.get(message_type)
    if not message_class:
        raise ValueError(f"Unknown message type: {message_type}")

    return message_class(**message_data)


def create_error_message(
    error: str, code: str = "GENERAL_ERROR", details: str | None = None
) -> ErrorMessage:
    """
    Create a standardized error message.

    Args:
        error: Error message
        code: Error code
        details: Optional error details

    Returns:
        ErrorMessage instance
    """
    content = {"error": error, "code": code}
    if details:
        content["details"] = details

    return ErrorMessage(content=content)


def create_system_message(text: str, message_type: str = "info") -> SystemMessage:
    """
    Create a standardized system message.

    Args:
        text: Message text
        message_type: Type of system message (info, warning, success)

    Returns:
        SystemMessage instance
    """
    return SystemMessage(content={"text": text, "type": message_type})
