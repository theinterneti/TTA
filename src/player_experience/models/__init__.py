"""
Data models for the Player Experience Interface.

This module contains all data models used in the player experience system,
including player profiles, characters, worlds, and session management.
"""

from .player import PlayerProfile, TherapeuticPreferences, PrivacySettings, CrisisContactInfo, ProgressSummary as PlayerProgressSummary
from .character import Character, CharacterAppearance, CharacterBackground, TherapeuticProfile, TherapeuticGoal, CharacterCreationData, CharacterUpdates
from .world import WorldSummary, WorldDetails, WorldParameters, CompatibilityReport, CompatibilityFactor, WorldPrerequisite, CustomizedWorld
from .session import SessionContext, PlayerDashboard, SessionSummary, TherapeuticSettings, ProgressMarker, Recommendation
from .therapeutic_settings import (
    EnhancedTherapeuticSettings, TherapeuticBoundary, SettingsConflict, 
    TherapeuticSettingsVersion, TherapeuticPreferencesValidator, SettingsMigrationManager,
    SettingsConflictType, SettingsValidationLevel
)
from .progress import ProgressSummary, ProgressHighlight, Milestone, EngagementMetrics, TherapeuticMetric, TherapeuticEffectivenessReport, ProgressVizSeries
from .enums import IntensityLevel, TherapeuticApproach, DifficultyLevel, CrisisType, SessionStatus, ProgressMarkerType

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