"""
World and related data models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .enums import DifficultyLevel, TherapeuticApproach


@dataclass
class WorldParameters:
    """Customizable parameters for world instances."""

    therapeutic_intensity: float = 0.5  # 0.0 to 1.0
    narrative_pace: str = "medium"  # slow, medium, fast
    interaction_frequency: str = "balanced"  # minimal, balanced, frequent
    challenge_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    focus_areas: list[str] = field(default_factory=list)
    avoid_topics: list[str] = field(default_factory=list)
    session_length_preference: int = 30  # minutes

    def __post_init__(self):
        """Validate world parameters after initialization."""
        if not 0.0 <= self.therapeutic_intensity <= 1.0:
            raise ValueError("Therapeutic intensity must be between 0.0 and 1.0")

        valid_paces = ["slow", "medium", "fast"]
        if self.narrative_pace not in valid_paces:
            raise ValueError(f"Narrative pace must be one of: {valid_paces}")

        valid_frequencies = ["minimal", "balanced", "frequent"]
        if self.interaction_frequency not in valid_frequencies:
            raise ValueError(
                f"Interaction frequency must be one of: {valid_frequencies}"
            )

        if not 10 <= self.session_length_preference <= 120:
            raise ValueError(
                "Session length preference must be between 10 and 120 minutes"
            )


@dataclass
class WorldPrerequisite:
    """Prerequisites for accessing a world."""

    prerequisite_type: str  # therapeutic_readiness, completed_worlds, skill_level
    description: str
    required_value: Any
    is_met: bool = False


@dataclass
class CompatibilityFactor:
    """Individual compatibility factor between character and world."""

    factor_name: str
    score: float  # 0.0 to 1.0
    explanation: str
    weight: float = 1.0


@dataclass
class CompatibilityReport:
    """Detailed compatibility assessment between character and world."""

    character_id: str
    world_id: str
    overall_score: float  # 0.0 to 1.0
    compatibility_factors: list[CompatibilityFactor] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    prerequisites_met: bool = True
    unmet_prerequisites: list[WorldPrerequisite] = field(default_factory=list)

    def __post_init__(self):
        """Validate compatibility report after initialization."""
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError("Overall compatibility score must be between 0.0 and 1.0")

    def add_compatibility_factor(self, factor: CompatibilityFactor) -> None:
        """Add a compatibility factor to the report."""
        self.compatibility_factors.append(factor)
        self._recalculate_overall_score()

    def _recalculate_overall_score(self) -> None:
        """Recalculate the overall compatibility score based on factors."""
        if not self.compatibility_factors:
            self.overall_score = 0.0
            return

        weighted_sum = sum(
            factor.score * factor.weight for factor in self.compatibility_factors
        )
        total_weight = sum(factor.weight for factor in self.compatibility_factors)

        self.overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0


@dataclass
class WorldSummary:
    """Summary information about a world for browsing and selection."""

    world_id: str
    name: str
    description: str
    therapeutic_themes: list[str] = field(default_factory=list)
    therapeutic_approaches: list[TherapeuticApproach] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=2))
    compatibility_score: float = 0.0  # Set when retrieved for specific character
    preview_image: str | None = None
    tags: list[str] = field(default_factory=list)
    player_count: int = 0  # Number of players who have tried this world
    average_rating: float = 0.0
    is_featured: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate world summary after initialization."""
        if not self.world_id:
            raise ValueError("World ID cannot be empty")

        if not self.name or len(self.name.strip()) < 3:
            raise ValueError("World name must be at least 3 characters long")

        if not 0.0 <= self.compatibility_score <= 1.0:
            raise ValueError("Compatibility score must be between 0.0 and 1.0")

        if not 0.0 <= self.average_rating <= 5.0:
            raise ValueError("Average rating must be between 0.0 and 5.0")


@dataclass
class WorldDetails:
    """Detailed information about a world."""

    world_id: str
    name: str
    description: str
    long_description: str
    therapeutic_themes: list[str] = field(default_factory=list)
    therapeutic_approaches: list[TherapeuticApproach] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=2))

    # World content and structure
    setting_description: str = ""
    key_characters: list[dict[str, str]] = field(default_factory=list)
    main_storylines: list[str] = field(default_factory=list)
    therapeutic_techniques_used: list[str] = field(default_factory=list)

    # Prerequisites and requirements
    prerequisites: list[WorldPrerequisite] = field(default_factory=list)
    recommended_therapeutic_readiness: float = 0.5
    content_warnings: list[str] = field(default_factory=list)

    # Customization options
    available_parameters: list[str] = field(default_factory=list)
    default_parameters: WorldParameters = field(default_factory=WorldParameters)

    # Metadata
    tags: list[str] = field(default_factory=list)
    preview_images: list[str] = field(default_factory=list)
    creator_notes: str = ""
    therapeutic_goals_addressed: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)

    # Statistics
    player_count: int = 0
    completion_rate: float = 0.0
    average_rating: float = 0.0
    average_session_count: int = 0
    therapeutic_effectiveness_score: float = 0.0

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate world details after initialization."""
        if not self.world_id:
            raise ValueError("World ID cannot be empty")

        if not self.name or len(self.name.strip()) < 3:
            raise ValueError("World name must be at least 3 characters long")

        if not 0.0 <= self.recommended_therapeutic_readiness <= 1.0:
            raise ValueError(
                "Recommended therapeutic readiness must be between 0.0 and 1.0"
            )

        if not 0.0 <= self.completion_rate <= 1.0:
            raise ValueError("Completion rate must be between 0.0 and 1.0")

        if not 0.0 <= self.average_rating <= 5.0:
            raise ValueError("Average rating must be between 0.0 and 5.0")

        if not 0.0 <= self.therapeutic_effectiveness_score <= 1.0:
            raise ValueError(
                "Therapeutic effectiveness score must be between 0.0 and 1.0"
            )

    def check_prerequisites(
        self, character_therapeutic_profile
    ) -> list[WorldPrerequisite]:
        """Check which prerequisites are not met for a given character."""
        unmet_prerequisites = []

        for prerequisite in self.prerequisites:
            if prerequisite.prerequisite_type == "therapeutic_readiness":
                if (
                    character_therapeutic_profile.readiness_level
                    < prerequisite.required_value
                ):
                    prerequisite.is_met = False
                    unmet_prerequisites.append(prerequisite)
                else:
                    prerequisite.is_met = True
            # Add other prerequisite type checks as needed

        return unmet_prerequisites

    def get_compatibility_score(self, character_therapeutic_profile) -> float:
        """Calculate compatibility score with a character's therapeutic profile."""
        score_factors = []

        # Therapeutic readiness alignment
        readiness_diff = abs(
            character_therapeutic_profile.readiness_level
            - self.recommended_therapeutic_readiness
        )
        readiness_score = max(0.0, 1.0 - readiness_diff)
        score_factors.append(readiness_score * 0.3)

        # Therapeutic approach alignment
        character_approaches = set(
            approach.value
            for approach in character_therapeutic_profile.therapeutic_goals
        )
        world_approaches = set(
            approach.value for approach in self.therapeutic_approaches
        )
        approach_overlap = len(character_approaches.intersection(world_approaches))
        approach_score = (
            approach_overlap / max(len(world_approaches), 1)
            if world_approaches
            else 0.0
        )
        score_factors.append(approach_score * 0.4)

        # Content safety (avoid trigger topics)
        trigger_overlap = set(
            character_therapeutic_profile.trigger_topics
        ).intersection(set(self.content_warnings))
        safety_score = 1.0 - (
            len(trigger_overlap)
            / max(len(character_therapeutic_profile.trigger_topics), 1)
        )
        score_factors.append(safety_score * 0.3)

        return sum(score_factors)


@dataclass
class CustomizedWorld:
    """A world instance customized for a specific character."""

    world_id: str
    character_id: str
    customized_parameters: WorldParameters
    compatibility_report: CompatibilityReport
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
