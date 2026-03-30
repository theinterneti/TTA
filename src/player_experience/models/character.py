"""

# Logseq: [[TTA.dev/Player_experience/Models/Character]]
Character and related data models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import IntensityLevel, TherapeuticApproach


@dataclass
class CharacterAppearance:
    """Physical appearance and visual characteristics of a character."""

    age_range: str = "adult"  # child, teen, adult, elder
    gender_identity: str = "non-binary"
    physical_description: str = ""
    clothing_style: str = "casual"
    distinctive_features: list[str] = field(default_factory=list)
    avatar_image_url: str | None = None

    def __post_init__(self):
        """Validate character appearance after initialization."""
        valid_age_ranges = ["child", "teen", "adult", "elder"]
        if self.age_range not in valid_age_ranges:
            raise ValueError(f"Age range must be one of: {valid_age_ranges}")


@dataclass
class CharacterBackground:
    """Character's background story and personality traits."""

    name: str
    backstory: str = ""
    personality_traits: list[str] = field(default_factory=list)
    core_values: list[str] = field(default_factory=list)
    fears_and_anxieties: list[str] = field(default_factory=list)
    strengths_and_skills: list[str] = field(default_factory=list)
    life_goals: list[str] = field(default_factory=list)
    relationships: dict[str, str] = field(
        default_factory=dict
    )  # relationship_type -> description

    def __post_init__(self):
        """Validate character background after initialization."""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Character name must be at least 2 characters long")

        if len(self.name) > 50:
            raise ValueError("Character name cannot exceed 50 characters")

        # Ensure name contains only valid characters (letters, spaces, hyphens, apostrophes)
        import re

        # Allow letters, spaces, hyphens, and apostrophes only (tests expect rejection of digits)
        if not re.match(r"^[a-zA-Z\s\-']+$", self.name.strip()):
            raise ValueError(
                "Character name can only contain letters, spaces, hyphens, and apostrophes"
            )


@dataclass
class TherapeuticGoal:
    """Individual therapeutic goal for a character."""

    goal_id: str
    description: str
    target_date: datetime | None = None
    progress_percentage: float = 0.0
    therapeutic_approaches: list[TherapeuticApproach] = field(default_factory=list)
    milestones: list[str] = field(default_factory=list)
    is_active: bool = True

    def __post_init__(self):
        """Validate therapeutic goal after initialization."""
        if self.progress_percentage < 0.0 or self.progress_percentage > 100.0:
            raise ValueError("Progress percentage must be between 0.0 and 100.0")


@dataclass
class TherapeuticProfile:
    """Character's therapeutic profile and treatment preferences."""

    primary_concerns: list[str] = field(default_factory=list)
    therapeutic_goals: list[TherapeuticGoal] = field(default_factory=list)
    preferred_intensity: IntensityLevel = IntensityLevel.MEDIUM
    comfort_zones: list[str] = field(default_factory=list)
    challenge_areas: list[str] = field(default_factory=list)
    coping_strategies: list[str] = field(default_factory=list)
    trigger_topics: list[str] = field(default_factory=list)
    therapeutic_history: dict[str, Any] = field(default_factory=dict)
    readiness_level: float = 0.5  # 0.0 to 1.0 scale
    therapeutic_approaches: list[TherapeuticApproach] = field(default_factory=list)

    def __post_init__(self):
        """Validate therapeutic profile after initialization."""
        if self.readiness_level < 0.0 or self.readiness_level > 1.0:
            raise ValueError("Readiness level must be between 0.0 and 1.0")
        # Validate approaches are enums
        for a in self.therapeutic_approaches:
            if not isinstance(a, TherapeuticApproach):
                raise ValueError(f"Invalid therapeutic approach: {a}")

    def add_therapeutic_goal(self, goal: TherapeuticGoal) -> None:
        """Add a new therapeutic goal."""
        if any(g.goal_id == goal.goal_id for g in self.therapeutic_goals):
            raise ValueError(f"Goal with ID {goal.goal_id} already exists")

        self.therapeutic_goals.append(goal)

    def update_goal_progress(self, goal_id: str, progress: float) -> None:
        """Update progress for a specific therapeutic goal."""
        for goal in self.therapeutic_goals:
            if goal.goal_id == goal_id:
                goal.progress_percentage = max(0.0, min(100.0, progress))
                return

        raise ValueError(f"Goal with ID {goal_id} not found")

    def get_active_goals(self) -> list[TherapeuticGoal]:
        """Get all active therapeutic goals."""
        return [goal for goal in self.therapeutic_goals if goal.is_active]


@dataclass
class CharacterCreationData:
    """Data structure for creating a new character."""

    name: str
    appearance: CharacterAppearance
    background: CharacterBackground
    therapeutic_profile: TherapeuticProfile

    def __post_init__(self):
        """Validate character creation data."""
        # Validation is handled by individual components
        pass


@dataclass
class CharacterUpdates:
    """Data structure for updating an existing character."""

    appearance: CharacterAppearance | None = None
    background: CharacterBackground | None = None
    therapeutic_profile: TherapeuticProfile | None = None


@dataclass
class Character:
    """Complete character model with all associated data."""

    character_id: str
    player_id: str
    name: str
    appearance: CharacterAppearance
    background: CharacterBackground
    therapeutic_profile: TherapeuticProfile
    created_at: datetime
    last_active: datetime
    active_worlds: list[str] = field(default_factory=list)  # World IDs
    total_session_time: int = 0  # minutes
    session_count: int = 0
    is_active: bool = True

    def __post_init__(self):
        """Validate character after initialization."""
        if not self.character_id:
            raise ValueError("Character ID cannot be empty")

        if not self.player_id:
            raise ValueError("Player ID cannot be empty")

        if not self.name:
            raise ValueError("Character name cannot be empty")

        # Ensure names are consistent after sanitization; allow display names with digits by comparing letters-only
        import re

        def norm(s):
            return re.sub(r"[^a-zA-Z\s\-']+", "", (s or "")).strip().lower()

        if norm(self.name) != norm(self.background.name):
            raise ValueError("Character name must match background name")

    def add_active_world(self, world_id: str) -> None:
        """Add a world to the character's active worlds."""
        if world_id not in self.active_worlds:
            self.active_worlds.append(world_id)

    def remove_active_world(self, world_id: str) -> None:
        """Remove a world from the character's active worlds."""
        if world_id in self.active_worlds:
            self.active_worlds.remove(world_id)

    def update_session_stats(self, session_duration_minutes: int) -> None:
        """Update character's session statistics."""
        self.total_session_time += session_duration_minutes
        self.session_count += 1
        self.last_active = datetime.now()

    def get_therapeutic_readiness(self) -> float:
        """Get the character's therapeutic readiness level."""
        return self.therapeutic_profile.readiness_level

    def update_therapeutic_readiness(self, new_readiness: float) -> None:
        """Update the character's therapeutic readiness level."""
        if 0.0 <= new_readiness <= 1.0:
            self.therapeutic_profile.readiness_level = new_readiness
        else:
            raise ValueError("Readiness level must be between 0.0 and 1.0")
