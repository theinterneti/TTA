"""
Enhanced therapeutic settings and preferences models.

This module provides comprehensive therapeutic personalization models including
settings validation, conflict resolution, and versioning capabilities.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .enums import IntensityLevel, TherapeuticApproach


class SettingsConflictType(Enum):
    """Types of conflicts that can occur in therapeutic settings."""

    INTENSITY_APPROACH_MISMATCH = "intensity_approach_mismatch"
    CONTRADICTORY_PREFERENCES = "contradictory_preferences"
    UNSAFE_COMBINATION = "unsafe_combination"
    WORLD_INCOMPATIBILITY = "world_incompatibility"
    THERAPEUTIC_BOUNDARY_VIOLATION = "therapeutic_boundary_violation"


class SettingsValidationLevel(Enum):
    """Validation levels for therapeutic settings."""

    BASIC = "basic"
    CLINICAL = "clinical"
    STRICT = "strict"


@dataclass
class TherapeuticBoundary:
    """Represents a therapeutic boundary or constraint."""

    boundary_id: str
    boundary_type: str  # "avoid_topic", "intensity_limit", "approach_restriction", etc.
    description: str
    severity: str  # "soft", "hard", "critical"
    parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def __post_init__(self):
        """Validate boundary after initialization."""
        if not self.boundary_id:
            self.boundary_id = str(uuid.uuid4())

        valid_severities = ["soft", "hard", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")


@dataclass
class SettingsConflict:
    """Represents a conflict between therapeutic settings."""

    conflict_id: str
    conflict_type: SettingsConflictType
    description: str
    severity: str  # "warning", "error", "critical"
    conflicting_settings: list[str]
    suggested_resolution: str | None = None
    auto_resolvable: bool = False
    resolution_options: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Validate conflict after initialization."""
        if not self.conflict_id:
            self.conflict_id = str(uuid.uuid4())

        valid_severities = ["warning", "error", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")


@dataclass
class TherapeuticSettingsVersion:
    """Version information for therapeutic settings."""

    version_id: str
    version_number: int
    created_at: datetime
    created_by: str  # player_id or system
    change_summary: str
    previous_version_id: str | None = None
    migration_notes: str | None = None

    def __post_init__(self):
        """Validate version after initialization."""
        if not self.version_id:
            self.version_id = str(uuid.uuid4())

        if self.version_number < 1:
            raise ValueError("Version number must be at least 1")


@dataclass
class EnhancedTherapeuticSettings:
    """Enhanced therapeutic settings with comprehensive personalization options."""

    settings_id: str
    player_id: str

    # Core intensity and approach settings
    intensity_level: IntensityLevel = IntensityLevel.MEDIUM
    preferred_approaches: list[TherapeuticApproach] = field(default_factory=list)
    secondary_approaches: list[TherapeuticApproach] = field(default_factory=list)

    # Detailed preference controls
    intervention_frequency: str = "balanced"  # minimal, balanced, frequent
    feedback_sensitivity: float = 0.5  # 0.0 to 1.0
    pacing_preference: str = "adaptive"  # slow, adaptive, fast
    challenge_tolerance: float = 0.5  # 0.0 to 1.0

    # Therapeutic boundaries
    boundaries: list[TherapeuticBoundary] = field(default_factory=list)
    trigger_warnings: list[str] = field(default_factory=list)
    comfort_topics: list[str] = field(default_factory=list)
    avoid_topics: list[str] = field(default_factory=list)

    # Safety and crisis settings
    crisis_monitoring_enabled: bool = True
    crisis_sensitivity: float = 0.7  # 0.0 to 1.0
    emergency_contact_enabled: bool = False
    safety_check_frequency: int = 5  # interactions between safety checks

    # Adaptation settings
    adaptive_difficulty: bool = True
    learning_style_preference: str | None = None  # visual, auditory, kinesthetic, mixed
    progress_celebration_style: str = "moderate"  # minimal, moderate, enthusiastic

    # Session preferences
    session_duration_preference: int = 30  # minutes
    break_reminder_enabled: bool = True
    break_reminder_interval: int = 20  # minutes

    # Versioning and metadata
    version: TherapeuticSettingsVersion = field(
        default_factory=lambda: TherapeuticSettingsVersion(
            version_id=str(uuid.uuid4()),
            version_number=1,
            created_at=datetime.now(),
            created_by="system",
            change_summary="Initial settings creation",
        )
    )
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def __post_init__(self):
        """Validate enhanced therapeutic settings after initialization."""
        if not self.settings_id:
            self.settings_id = str(uuid.uuid4())

        if not self.player_id:
            raise ValueError("Player ID cannot be empty")

        # Validate intensity level
        if not isinstance(self.intensity_level, IntensityLevel):
            raise ValueError(f"Invalid intensity level: {self.intensity_level}")

        # Validate approaches
        for approach in self.preferred_approaches + self.secondary_approaches:
            if not isinstance(approach, TherapeuticApproach):
                raise ValueError(f"Invalid therapeutic approach: {approach}")

        # Validate numeric ranges
        if not 0.0 <= self.feedback_sensitivity <= 1.0:
            raise ValueError("Feedback sensitivity must be between 0.0 and 1.0")

        if not 0.0 <= self.challenge_tolerance <= 1.0:
            raise ValueError("Challenge tolerance must be between 0.0 and 1.0")

        if not 0.0 <= self.crisis_sensitivity <= 1.0:
            raise ValueError("Crisis sensitivity must be between 0.0 and 1.0")

        # Validate session preferences
        if not 10 <= self.session_duration_preference <= 120:
            raise ValueError("Session duration must be between 10 and 120 minutes")

        if not 5 <= self.break_reminder_interval <= 60:
            raise ValueError("Break reminder interval must be between 5 and 60 minutes")

        if not 1 <= self.safety_check_frequency <= 20:
            raise ValueError(
                "Safety check frequency must be between 1 and 20 interactions"
            )

        # Validate string enums
        valid_frequencies = ["minimal", "balanced", "frequent"]
        if self.intervention_frequency not in valid_frequencies:
            raise ValueError(
                f"Intervention frequency must be one of: {valid_frequencies}"
            )

        valid_pacing = ["slow", "adaptive", "fast"]
        if self.pacing_preference not in valid_pacing:
            raise ValueError(f"Pacing preference must be one of: {valid_pacing}")

        valid_celebration = ["minimal", "moderate", "enthusiastic"]
        if self.progress_celebration_style not in valid_celebration:
            raise ValueError(
                f"Progress celebration style must be one of: {valid_celebration}"
            )

    def add_boundary(self, boundary: TherapeuticBoundary) -> None:
        """Add a therapeutic boundary to the settings."""
        # Check if boundary already exists
        existing_ids = {b.boundary_id for b in self.boundaries}
        if boundary.boundary_id in existing_ids:
            raise ValueError(f"Boundary {boundary.boundary_id} already exists")

        self.boundaries.append(boundary)
        self.updated_at = datetime.now()

    def remove_boundary(self, boundary_id: str) -> bool:
        """Remove a therapeutic boundary from the settings."""
        original_count = len(self.boundaries)
        self.boundaries = [b for b in self.boundaries if b.boundary_id != boundary_id]

        if len(self.boundaries) < original_count:
            self.updated_at = datetime.now()
            return True
        return False

    def get_active_boundaries(self) -> list[TherapeuticBoundary]:
        """Get all active therapeutic boundaries."""
        return [b for b in self.boundaries if b.is_active]

    def update_intensity(self, new_intensity: IntensityLevel) -> None:
        """Update intensity level with validation."""
        if not isinstance(new_intensity, IntensityLevel):
            raise ValueError(f"Invalid intensity level: {new_intensity}")

        self.intensity_level = new_intensity
        self.updated_at = datetime.now()

    def add_preferred_approach(self, approach: TherapeuticApproach) -> None:
        """Add a preferred therapeutic approach."""
        if not isinstance(approach, TherapeuticApproach):
            raise ValueError(f"Invalid therapeutic approach: {approach}")

        if approach not in self.preferred_approaches:
            self.preferred_approaches.append(approach)
            self.updated_at = datetime.now()

    def remove_preferred_approach(self, approach: TherapeuticApproach) -> bool:
        """Remove a preferred therapeutic approach."""
        if approach in self.preferred_approaches:
            self.preferred_approaches.remove(approach)
            self.updated_at = datetime.now()
            return True
        return False

    def get_all_approaches(self) -> list[TherapeuticApproach]:
        """Get all therapeutic approaches (preferred + secondary)."""
        return list(set(self.preferred_approaches + self.secondary_approaches))

    def create_new_version(
        self, change_summary: str, created_by: str
    ) -> "EnhancedTherapeuticSettings":
        """Create a new version of the settings."""
        new_version = TherapeuticSettingsVersion(
            version_id=str(uuid.uuid4()),
            version_number=self.version.version_number + 1,
            created_at=datetime.now(),
            created_by=created_by,
            change_summary=change_summary,
            previous_version_id=self.version.version_id,
        )

        # Create a copy of current settings with new version
        return EnhancedTherapeuticSettings(
            settings_id=self.settings_id,
            player_id=self.player_id,
            intensity_level=self.intensity_level,
            preferred_approaches=self.preferred_approaches.copy(),
            secondary_approaches=self.secondary_approaches.copy(),
            intervention_frequency=self.intervention_frequency,
            feedback_sensitivity=self.feedback_sensitivity,
            pacing_preference=self.pacing_preference,
            challenge_tolerance=self.challenge_tolerance,
            boundaries=self.boundaries.copy(),
            trigger_warnings=self.trigger_warnings.copy(),
            comfort_topics=self.comfort_topics.copy(),
            avoid_topics=self.avoid_topics.copy(),
            crisis_monitoring_enabled=self.crisis_monitoring_enabled,
            crisis_sensitivity=self.crisis_sensitivity,
            emergency_contact_enabled=self.emergency_contact_enabled,
            safety_check_frequency=self.safety_check_frequency,
            adaptive_difficulty=self.adaptive_difficulty,
            learning_style_preference=self.learning_style_preference,
            progress_celebration_style=self.progress_celebration_style,
            session_duration_preference=self.session_duration_preference,
            break_reminder_enabled=self.break_reminder_enabled,
            break_reminder_interval=self.break_reminder_interval,
            version=new_version,
            created_at=self.created_at,
            updated_at=datetime.now(),
            is_active=True,
        )


@dataclass
class TherapeuticPreferencesValidator:
    """Validator for therapeutic preferences and settings."""

    validation_level: SettingsValidationLevel = SettingsValidationLevel.CLINICAL

    def validate_settings(
        self, settings: EnhancedTherapeuticSettings
    ) -> tuple[bool, list[SettingsConflict]]:
        """Validate therapeutic settings and return conflicts if any."""
        conflicts = []

        # Check for intensity-approach mismatches
        intensity_conflicts = self._check_intensity_approach_compatibility(settings)
        conflicts.extend(intensity_conflicts)

        # Check for contradictory preferences
        preference_conflicts = self._check_preference_contradictions(settings)
        conflicts.extend(preference_conflicts)

        # Check for unsafe combinations
        safety_conflicts = self._check_safety_combinations(settings)
        conflicts.extend(safety_conflicts)

        # Check boundary violations
        boundary_conflicts = self._check_boundary_violations(settings)
        conflicts.extend(boundary_conflicts)

        # Determine if settings are valid (no critical or error conflicts)
        is_valid = not any(c.severity in ["critical", "error"] for c in conflicts)

        return is_valid, conflicts

    def _check_intensity_approach_compatibility(
        self, settings: EnhancedTherapeuticSettings
    ) -> list[SettingsConflict]:
        """Check for intensity-approach compatibility issues."""
        conflicts = []

        # High intensity with gentle approaches might be problematic
        if settings.intensity_level == IntensityLevel.HIGH:
            gentle_approaches = {
                TherapeuticApproach.MINDFULNESS,
                TherapeuticApproach.HUMANISTIC,
            }
            if any(
                approach in gentle_approaches
                for approach in settings.preferred_approaches
            ):
                conflicts.append(
                    SettingsConflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=SettingsConflictType.INTENSITY_APPROACH_MISMATCH,
                        description="High intensity setting may not be compatible with gentle therapeutic approaches",
                        severity="warning",
                        conflicting_settings=[
                            "intensity_level",
                            "preferred_approaches",
                        ],
                        suggested_resolution="Consider reducing intensity or selecting more structured approaches",
                        auto_resolvable=True,
                        resolution_options=[
                            {
                                "action": "reduce_intensity",
                                "target": IntensityLevel.MEDIUM.value,
                            },
                            {
                                "action": "add_structured_approach",
                                "target": TherapeuticApproach.CBT.value,
                            },
                        ],
                    )
                )

        return conflicts

    def _check_preference_contradictions(
        self, settings: EnhancedTherapeuticSettings
    ) -> list[SettingsConflict]:
        """Check for contradictory preferences."""
        conflicts = []

        # Check for topic contradictions
        overlap = set(settings.comfort_topics) & set(settings.avoid_topics)
        if overlap:
            conflicts.append(
                SettingsConflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=SettingsConflictType.CONTRADICTORY_PREFERENCES,
                    description=f"Topics appear in both comfort and avoid lists: {list(overlap)}",
                    severity="error",
                    conflicting_settings=["comfort_topics", "avoid_topics"],
                    suggested_resolution="Remove overlapping topics from one of the lists",
                    auto_resolvable=True,
                    resolution_options=[
                        {"action": "remove_from_avoid", "topics": list(overlap)},
                        {"action": "remove_from_comfort", "topics": list(overlap)},
                    ],
                )
            )

        # Check for conflicting pacing and challenge settings
        if settings.pacing_preference == "slow" and settings.challenge_tolerance > 0.8:
            conflicts.append(
                SettingsConflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=SettingsConflictType.CONTRADICTORY_PREFERENCES,
                    description="Slow pacing preference conflicts with high challenge tolerance",
                    severity="warning",
                    conflicting_settings=["pacing_preference", "challenge_tolerance"],
                    suggested_resolution="Adjust either pacing or challenge tolerance for consistency",
                    auto_resolvable=True,
                    resolution_options=[
                        {"action": "adjust_pacing", "target": "adaptive"},
                        {"action": "reduce_challenge_tolerance", "target": 0.5},
                    ],
                )
            )

        return conflicts

    def _check_safety_combinations(
        self, settings: EnhancedTherapeuticSettings
    ) -> list[SettingsConflict]:
        """Check for potentially unsafe setting combinations."""
        conflicts = []

        # High intensity with disabled crisis monitoring
        if (
            settings.intensity_level == IntensityLevel.HIGH
            and not settings.crisis_monitoring_enabled
        ):
            conflicts.append(
                SettingsConflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=SettingsConflictType.UNSAFE_COMBINATION,
                    description="High intensity therapy without crisis monitoring may be unsafe",
                    severity="critical",
                    conflicting_settings=[
                        "intensity_level",
                        "crisis_monitoring_enabled",
                    ],
                    suggested_resolution="Enable crisis monitoring for high intensity therapy",
                    auto_resolvable=True,
                    resolution_options=[
                        {"action": "enable_crisis_monitoring", "target": True}
                    ],
                )
            )

        # Very low crisis sensitivity with trauma-related approaches
        trauma_approaches = {TherapeuticApproach.DIALECTICAL_BEHAVIORAL}
        if settings.crisis_sensitivity < 0.3 and any(
            approach in trauma_approaches for approach in settings.preferred_approaches
        ):
            conflicts.append(
                SettingsConflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=SettingsConflictType.UNSAFE_COMBINATION,
                    description="Low crisis sensitivity with trauma-focused approaches may miss important signals",
                    severity="error",
                    conflicting_settings=["crisis_sensitivity", "preferred_approaches"],
                    suggested_resolution="Increase crisis sensitivity for trauma-focused therapy",
                    auto_resolvable=True,
                    resolution_options=[
                        {"action": "increase_crisis_sensitivity", "target": 0.7}
                    ],
                )
            )

        return conflicts

    def _check_boundary_violations(
        self, settings: EnhancedTherapeuticSettings
    ) -> list[SettingsConflict]:
        """Check for therapeutic boundary violations."""
        conflicts = []

        # Check for conflicting boundaries
        active_boundaries = settings.get_active_boundaries()

        # Look for contradictory boundaries
        avoid_boundaries = [
            b for b in active_boundaries if b.boundary_type == "avoid_topic"
        ]
        comfort_boundaries = [
            b for b in active_boundaries if b.boundary_type == "comfort_topic"
        ]

        avoid_topics = set()
        comfort_topics = set()

        for boundary in avoid_boundaries:
            if "topics" in boundary.parameters:
                avoid_topics.update(boundary.parameters["topics"])

        for boundary in comfort_boundaries:
            if "topics" in boundary.parameters:
                comfort_topics.update(boundary.parameters["topics"])

        overlap = avoid_topics & comfort_topics
        if overlap:
            conflicts.append(
                SettingsConflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=SettingsConflictType.THERAPEUTIC_BOUNDARY_VIOLATION,
                    description=f"Conflicting boundaries for topics: {list(overlap)}",
                    severity="error",
                    conflicting_settings=["boundaries"],
                    suggested_resolution="Resolve conflicting topic boundaries",
                    auto_resolvable=False,
                    resolution_options=[
                        {
                            "action": "review_boundaries",
                            "conflicting_topics": list(overlap),
                        }
                    ],
                )
            )

        return conflicts

    def resolve_conflict(
        self,
        settings: EnhancedTherapeuticSettings,
        conflict: SettingsConflict,
        resolution_option: dict[str, Any],
    ) -> EnhancedTherapeuticSettings:
        """Automatically resolve a conflict if possible."""
        if not conflict.auto_resolvable:
            raise ValueError(f"Conflict {conflict.conflict_id} is not auto-resolvable")

        # Create a copy of settings to modify
        resolved_settings = settings.create_new_version(
            change_summary=f"Auto-resolved conflict: {conflict.description}",
            created_by="system",
        )

        action = resolution_option.get("action")

        if action == "reduce_intensity":
            resolved_settings.intensity_level = IntensityLevel(
                resolution_option["target"]
            )
        elif action == "enable_crisis_monitoring":
            resolved_settings.crisis_monitoring_enabled = resolution_option["target"]
        elif action == "increase_crisis_sensitivity":
            resolved_settings.crisis_sensitivity = resolution_option["target"]
        elif action == "remove_from_avoid":
            for topic in resolution_option["topics"]:
                if topic in resolved_settings.avoid_topics:
                    resolved_settings.avoid_topics.remove(topic)
        elif action == "remove_from_comfort":
            for topic in resolution_option["topics"]:
                if topic in resolved_settings.comfort_topics:
                    resolved_settings.comfort_topics.remove(topic)
        elif action == "adjust_pacing":
            resolved_settings.pacing_preference = resolution_option["target"]
        elif action == "reduce_challenge_tolerance":
            resolved_settings.challenge_tolerance = resolution_option["target"]
        elif action == "add_structured_approach":
            approach = TherapeuticApproach(resolution_option["target"])
            resolved_settings.add_preferred_approach(approach)

        return resolved_settings


@dataclass
class SettingsMigrationManager:
    """Manages migration of therapeutic settings between versions."""

    def migrate_settings(
        self, old_settings: dict[str, Any], target_version: int
    ) -> EnhancedTherapeuticSettings:
        """Migrate settings from old format to current version."""
        if target_version == 1:
            return self._migrate_to_v1(old_settings)
        raise ValueError(f"Unsupported target version: {target_version}")

    def _migrate_to_v1(
        self, old_settings: dict[str, Any]
    ) -> EnhancedTherapeuticSettings:
        """Migrate settings to version 1 format."""
        # Handle migration from basic TherapeuticSettings to EnhancedTherapeuticSettings

        # Extract basic settings
        intensity_level = old_settings.get("intensity_level", IntensityLevel.MEDIUM)
        if isinstance(intensity_level, float):
            # Convert float intensity to enum
            if intensity_level <= 0.33:
                intensity_level = IntensityLevel.LOW
            elif intensity_level <= 0.66:
                intensity_level = IntensityLevel.MEDIUM
            else:
                intensity_level = IntensityLevel.HIGH

        preferred_approaches = old_settings.get("preferred_approaches", [])
        if isinstance(preferred_approaches, list) and preferred_approaches:
            # Ensure all approaches are valid enums
            preferred_approaches = [
                approach
                for approach in preferred_approaches
                if isinstance(approach, TherapeuticApproach)
            ]

        # Create enhanced settings with migrated data
        return EnhancedTherapeuticSettings(
            settings_id=old_settings.get("settings_id", str(uuid.uuid4())),
            player_id=old_settings.get("player_id", ""),
            intensity_level=intensity_level,
            preferred_approaches=preferred_approaches,
            intervention_frequency=old_settings.get(
                "intervention_frequency", "balanced"
            ),
            feedback_sensitivity=old_settings.get("feedback_sensitivity", 0.5),
            crisis_monitoring_enabled=old_settings.get(
                "crisis_monitoring_enabled", True
            ),
            adaptive_difficulty=old_settings.get("adaptive_difficulty", True),
            session_duration_preference=old_settings.get(
                "session_duration_preference", 30
            ),
            trigger_warnings=old_settings.get("trigger_warnings", []),
            comfort_topics=old_settings.get("comfort_topics", []),
            avoid_topics=old_settings.get("avoid_topics", []),
        )
