"""
Social and Collaborative Features for Core Gameplay Loop

This module provides comprehensive social and collaborative therapeutic experiences
including collaborative adventure framework, group experience management, privacy
and sharing controls, moderation tools, and conflict resolution processes.
"""

from .collaborative_system import (
    CollaborativeSystem,
    CollaborativeSession,
    CollaborativeParticipant,
    GroupChoice,
    SupportMessage,
    ConflictResolution,
    CollaborativeMode,
    ParticipantRole,
    PrivacyLevel,
    ModerationAction
)

__all__ = [
    # Main System
    "CollaborativeSystem",
    
    # Core Data Models
    "CollaborativeSession",
    "CollaborativeParticipant", 
    "GroupChoice",
    "SupportMessage",
    "ConflictResolution",
    
    # Enums
    "CollaborativeMode",
    "ParticipantRole",
    "PrivacyLevel",
    "ModerationAction"
]
