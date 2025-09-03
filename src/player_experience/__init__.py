"""
Player Experience Interface Module

This module provides the player-facing interface for the TTA system,
including character management, world selection, and therapeutic personalization.
"""

from .managers import (
    CharacterAvatarManager,
    PersonalizationServiceManager,
    PlayerExperienceManager,
    PlayerProfileManager,
    ProgressTrackingService,
    SessionIntegrationManager,
    WorldManagementModule,
)
from .models import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    CharacterUpdates,
    CompatibilityFactor,
    CompatibilityReport,
    CrisisContactInfo,
    CrisisType,
    CustomizedWorld,
    DifficultyLevel,
    EngagementMetrics,
    EnhancedTherapeuticSettings,
    IntensityLevel,
    Milestone,
    PlayerDashboard,
    PlayerProfile,
    PlayerProgressSummary,
    PrivacySettings,
    ProgressHighlight,
    ProgressMarker,
    ProgressMarkerType,
    ProgressSummary,
    ProgressVizSeries,
    Recommendation,
    SessionContext,
    SessionStatus,
    SessionSummary,
    SettingsConflict,
    SettingsConflictType,
    SettingsMigrationManager,
    SettingsValidationLevel,
    TherapeuticApproach,
    TherapeuticBoundary,
    TherapeuticEffectivenessReport,
    TherapeuticGoal,
    TherapeuticMetric,
    TherapeuticPreferences,
    TherapeuticPreferencesValidator,
    TherapeuticProfile,
    TherapeuticSettings,
    TherapeuticSettingsVersion,
    WorldDetails,
    WorldParameters,
    WorldPrerequisite,
    WorldSummary,
)

# NOTE: Avoid importing API at package import time to prevent heavy deps during unit tests.
# Import API modules directly as needed, e.g., `from src.player_experience.api.app import create_app`

__version__ = "1.0.0"
