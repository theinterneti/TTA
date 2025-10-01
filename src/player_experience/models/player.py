"""
Player profile and related data models.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .enums import IntensityLevel, TherapeuticApproach


@dataclass
class CrisisContactInfo:
    """Emergency contact information for crisis situations."""

    primary_contact_name: str | None = None
    primary_contact_phone: str | None = None
    therapist_name: str | None = None
    therapist_phone: str | None = None
    crisis_hotline_preference: str | None = None
    emergency_instructions: str | None = None


@dataclass
class TherapeuticPreferences:
    """Player's therapeutic preferences and settings."""

    intensity_level: IntensityLevel = IntensityLevel.MEDIUM
    preferred_approaches: list[TherapeuticApproach] = field(default_factory=list)
    trigger_warnings: list[str] = field(default_factory=list)
    comfort_topics: list[str] = field(default_factory=list)
    avoid_topics: list[str] = field(default_factory=list)
    crisis_contact_info: CrisisContactInfo | None = None
    session_duration_preference: int = 30  # minutes
    reminder_frequency: str = "weekly"

    def __post_init__(self):
        """Validate therapeutic preferences after initialization."""
        if not isinstance(self.intensity_level, IntensityLevel):
            raise ValueError(f"Invalid intensity level: {self.intensity_level}")

        for approach in self.preferred_approaches:
            if not isinstance(approach, TherapeuticApproach):
                raise ValueError(f"Invalid therapeutic approach: {approach}")

        if (
            self.session_duration_preference < 10
            or self.session_duration_preference > 120
        ):
            raise ValueError("Session duration must be between 10 and 120 minutes")


@dataclass
class PrivacySettings:
    """Player's privacy and data management preferences."""

    data_collection_consent: bool = True
    research_participation_consent: bool = False
    progress_sharing_enabled: bool = False
    anonymous_analytics_enabled: bool = True
    session_recording_enabled: bool = False
    data_retention_period_days: int = 365
    third_party_sharing_consent: bool = False

    # Granular data controls
    collect_interaction_patterns: bool = True
    collect_emotional_responses: bool = True
    collect_therapeutic_outcomes: bool = True
    collect_usage_statistics: bool = True

    def __post_init__(self):
        """Validate privacy settings after initialization."""
        if self.data_retention_period_days < 30:
            raise ValueError("Data retention period must be at least 30 days")

        if self.data_retention_period_days > 2555:  # ~7 years
            raise ValueError("Data retention period cannot exceed 7 years")


@dataclass
class ProgressSummary:
    """Summary of player's therapeutic progress."""

    total_sessions: int = 0
    total_time_minutes: int = 0
    milestones_achieved: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    favorite_therapeutic_approach: TherapeuticApproach | None = None
    most_effective_world_type: str | None = None
    last_session_date: datetime | None = None
    next_recommended_session: datetime | None = None


@dataclass
class PlayerProfile:
    """Complete player profile with all associated data."""

    player_id: str
    username: str
    email: str
    created_at: datetime
    therapeutic_preferences: TherapeuticPreferences = field(
        default_factory=TherapeuticPreferences
    )
    privacy_settings: PrivacySettings = field(default_factory=PrivacySettings)
    characters: list[str] = field(default_factory=list)  # Character IDs
    active_sessions: dict[str, str] = field(
        default_factory=dict
    )  # character_id -> session_id
    progress_summary: ProgressSummary = field(default_factory=ProgressSummary)
    last_login: datetime | None = None
    is_active: bool = True

    def __post_init__(self):
        """Validate player profile after initialization."""
        if not self.player_id:
            raise ValueError("Player ID cannot be empty")

        if not self.username or len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if not self.email or "@" not in self.email:
            raise ValueError("Valid email address is required")

        if len(self.characters) > 5:
            raise ValueError("Player cannot have more than 5 characters")

    def add_character(self, character_id: str) -> None:
        """Add a character to the player's character list."""
        if len(self.characters) >= 5:
            raise ValueError("Cannot add more than 5 characters per player")

        if character_id in self.characters:
            raise ValueError(f"Character {character_id} already exists for this player")

        self.characters.append(character_id)

    def remove_character(self, character_id: str) -> None:
        """Remove a character from the player's character list."""
        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found for this player")

        self.characters.remove(character_id)

        # Remove any active sessions for this character
        if character_id in self.active_sessions:
            del self.active_sessions[character_id]

    def set_active_session(self, character_id: str, session_id: str) -> None:
        """Set the active session for a character."""
        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found for this player")

        self.active_sessions[character_id] = session_id

    def get_active_session(self, character_id: str) -> str | None:
        """Get the active session ID for a character."""
        return self.active_sessions.get(character_id)

    def clear_active_session(self, character_id: str) -> None:
        """Clear the active session for a character."""
        if character_id in self.active_sessions:
            del self.active_sessions[character_id]
