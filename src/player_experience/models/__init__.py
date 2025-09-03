"""
Data models for the Player Experience Interface.

This module contains all data models used in the player experience system,
including player profiles, characters, worlds, and session management.
"""

from .character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    CharacterUpdates,
    TherapeuticGoal,
    TherapeuticProfile,
)
from .enums import (
    CrisisType,
    DifficultyLevel,
    IntensityLevel,
    ProgressMarkerType,
    SessionStatus,
    TherapeuticApproach,
)
from .player import (
    CrisisContactInfo,
    PlayerProfile,
    PrivacySettings,
    TherapeuticPreferences,
)
from .player import ProgressSummary as PlayerProgressSummary
from .progress import (
    EngagementMetrics,
    Milestone,
    ProgressHighlight,
    ProgressSummary,
    ProgressVizSeries,
    TherapeuticEffectivenessReport,
    TherapeuticMetric,
)
from .session import (
    PlayerDashboard,
    ProgressMarker,
    Recommendation,
    SessionContext,
    SessionSummary,
    TherapeuticSettings,
)
from .therapeutic_settings import (
    EnhancedTherapeuticSettings,
    SettingsConflict,
    SettingsConflictType,
    SettingsMigrationManager,
    SettingsValidationLevel,
    TherapeuticBoundary,
    TherapeuticPreferencesValidator,
    TherapeuticSettingsVersion,
)
from .world import (
    CompatibilityFactor,
    CompatibilityReport,
    CustomizedWorld,
    WorldDetails,
    WorldParameters,
    WorldPrerequisite,
    WorldSummary,
)

__all__ = [
    # Player models
    "PlayerProfile",
    "TherapeuticPreferences",
    "PrivacySettings",
    "CrisisContactInfo",
    "PlayerProgressSummary",
    # Character models
    "Character",
    "CharacterAppearance",
    "CharacterBackground",
    "TherapeuticProfile",
    "TherapeuticGoal",
    "CharacterCreationData",
    "CharacterUpdates",
    # World models
    "WorldSummary",
    "WorldDetails",
    "WorldParameters",
    "CompatibilityReport",
    "CompatibilityFactor",
    "WorldPrerequisite",
    "CustomizedWorld",
    # Session models
    "SessionContext",
    "PlayerDashboard",
    "SessionSummary",
    "TherapeuticSettings",
    "ProgressMarker",
    "Recommendation",
    # Enhanced therapeutic settings models
    "EnhancedTherapeuticSettings",
    "TherapeuticBoundary",
    "SettingsConflict",
    "TherapeuticSettingsVersion",
    "TherapeuticPreferencesValidator",
    "SettingsMigrationManager",
    "SettingsConflictType",
    "SettingsValidationLevel",
    # Progress models
    "ProgressSummary",
    "ProgressHighlight",
    "Milestone",
    "EngagementMetrics",
    "TherapeuticMetric",
    "TherapeuticEffectivenessReport",
    "ProgressVizSeries",
    # Enums
    "IntensityLevel",
    "TherapeuticApproach",
    "DifficultyLevel",
    "CrisisType",
    "SessionStatus",
    "ProgressMarkerType",
]
