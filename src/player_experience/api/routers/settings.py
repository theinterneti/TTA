"""
Settings management router for the Player Experience API.

This module provides REST endpoints for managing player settings including
therapeutic preferences, privacy settings, notifications, and accessibility options.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..auth import TokenData, get_current_active_player

router = APIRouter()

# In-memory storage for settings (in production, use database)
_PLAYER_SETTINGS: dict[str, dict[str, Any]] = {}


class TherapeuticSettings(BaseModel):
    """Therapeutic settings model."""

    intensity_level: str = Field(
        default="MEDIUM", description="Therapeutic intensity level"
    )
    preferred_approaches: list[str] = Field(
        default_factory=list, description="Preferred therapeutic approaches"
    )
    trigger_warnings: list[str] = Field(
        default_factory=list, description="Trigger warnings and sensitive topics"
    )
    comfort_topics: list[str] = Field(
        default_factory=list, description="Comfort topics and interests"
    )
    avoid_topics: list[str] = Field(default_factory=list, description="Topics to avoid")
    crisis_contact_info: dict[str, Any] | None = Field(
        default=None, description="Crisis contact information"
    )


class PrivacySettings(BaseModel):
    """Privacy settings model."""

    data_sharing_consent: bool = Field(
        default=False, description="Consent to data sharing"
    )
    research_participation: bool = Field(
        default=False, description="Consent to research participation"
    )
    contact_preferences: list[str] = Field(
        default_factory=list, description="Contact preferences"
    )
    data_retention_period: int = Field(
        default=365, description="Data retention period in days"
    )
    anonymize_data: bool = Field(
        default=True, description="Automatically anonymize data"
    )


class NotificationSettings(BaseModel):
    """Notification settings model."""

    session_reminders: bool = Field(
        default=True, description="Session reminder notifications"
    )
    progress_updates: bool = Field(
        default=True, description="Progress update notifications"
    )
    milestone_celebrations: bool = Field(
        default=True, description="Milestone celebration notifications"
    )
    crisis_alerts: bool = Field(
        default=True, description="Crisis support alert notifications"
    )
    email_notifications: bool = Field(default=True, description="Email notifications")
    push_notifications: bool = Field(default=False, description="Push notifications")


class AccessibilitySettings(BaseModel):
    """Accessibility settings model."""

    high_contrast: bool = Field(default=False, description="High contrast mode")
    large_text: bool = Field(default=False, description="Large text mode")
    screen_reader_optimized: bool = Field(
        default=False, description="Screen reader optimization"
    )
    reduced_motion: bool = Field(default=False, description="Reduced motion mode")
    keyboard_navigation: bool = Field(
        default=False, description="Enhanced keyboard navigation"
    )


class PlayerSettings(BaseModel):
    """Complete player settings model."""

    therapeutic: TherapeuticSettings = Field(default_factory=TherapeuticSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings)


def get_default_settings() -> PlayerSettings:
    """Get default settings for a new player."""
    return PlayerSettings()


def get_player_settings(player_id: str) -> PlayerSettings:
    """Get settings for a specific player."""
    if player_id not in _PLAYER_SETTINGS:
        _PLAYER_SETTINGS[player_id] = get_default_settings().model_dump()

    settings_data = _PLAYER_SETTINGS[player_id]
    return PlayerSettings(**settings_data)


def update_player_settings(player_id: str, settings: PlayerSettings) -> PlayerSettings:
    """Update settings for a specific player."""
    _PLAYER_SETTINGS[player_id] = settings.model_dump()
    return settings


@router.get("/{player_id}/settings", response_model=PlayerSettings)
async def get_settings(
    player_id: str, current_player: TokenData = Depends(get_current_active_player)
) -> PlayerSettings:
    """
    Get player settings.

    Args:
        player_id: Player identifier
        current_player: Current authenticated player

    Returns:
        PlayerSettings: Player's current settings

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is accessing their own settings
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own settings",
        )

    return get_player_settings(player_id)


@router.put("/{player_id}/settings/therapeutic", response_model=TherapeuticSettings)
async def update_therapeutic_settings(
    player_id: str,
    therapeutic_settings: TherapeuticSettings,
    current_player: TokenData = Depends(get_current_active_player),
) -> TherapeuticSettings:
    """
    Update therapeutic settings for a player.

    Args:
        player_id: Player identifier
        therapeutic_settings: New therapeutic settings
        current_player: Current authenticated player

    Returns:
        TherapeuticSettings: Updated therapeutic settings

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is updating their own settings
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only update your own settings",
        )

    # Get current settings
    current_settings = get_player_settings(player_id)

    # Update therapeutic settings
    current_settings.therapeutic = therapeutic_settings

    # Save updated settings
    update_player_settings(player_id, current_settings)

    return therapeutic_settings


@router.put("/{player_id}/settings/privacy", response_model=PrivacySettings)
async def update_privacy_settings(
    player_id: str,
    privacy_settings: PrivacySettings,
    current_player: TokenData = Depends(get_current_active_player),
) -> PrivacySettings:
    """
    Update privacy settings for a player.

    Args:
        player_id: Player identifier
        privacy_settings: New privacy settings
        current_player: Current authenticated player

    Returns:
        PrivacySettings: Updated privacy settings

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is updating their own settings
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only update your own settings",
        )

    # Get current settings
    current_settings = get_player_settings(player_id)

    # Update privacy settings
    current_settings.privacy = privacy_settings

    # Save updated settings
    update_player_settings(player_id, current_settings)

    return privacy_settings


@router.put("/{player_id}/settings/notifications", response_model=NotificationSettings)
async def update_notification_settings(
    player_id: str,
    notification_settings: NotificationSettings,
    current_player: TokenData = Depends(get_current_active_player),
) -> NotificationSettings:
    """
    Update notification settings for a player.

    Args:
        player_id: Player identifier
        notification_settings: New notification settings
        current_player: Current authenticated player

    Returns:
        NotificationSettings: Updated notification settings

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is updating their own settings
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only update your own settings",
        )

    # Get current settings
    current_settings = get_player_settings(player_id)

    # Update notification settings
    current_settings.notifications = notification_settings

    # Save updated settings
    update_player_settings(player_id, current_settings)

    return notification_settings


@router.put("/{player_id}/settings/accessibility", response_model=AccessibilitySettings)
async def update_accessibility_settings(
    player_id: str,
    accessibility_settings: AccessibilitySettings,
    current_player: TokenData = Depends(get_current_active_player),
) -> AccessibilitySettings:
    """
    Update accessibility settings for a player.

    Args:
        player_id: Player identifier
        accessibility_settings: New accessibility settings
        current_player: Current authenticated player

    Returns:
        AccessibilitySettings: Updated accessibility settings

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is updating their own settings
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only update your own settings",
        )

    # Get current settings
    current_settings = get_player_settings(player_id)

    # Update accessibility settings
    current_settings.accessibility = accessibility_settings

    # Save updated settings
    update_player_settings(player_id, current_settings)

    return accessibility_settings


@router.get("/{player_id}/data/export")
async def export_player_data(
    player_id: str, current_player: TokenData = Depends(get_current_active_player)
) -> dict[str, Any]:
    """
    Export player data.

    Args:
        player_id: Player identifier
        current_player: Current authenticated player

    Returns:
        Dict: Exported player data

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is exporting their own data
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only export your own data",
        )

    settings = get_player_settings(player_id)

    return {
        "player_id": player_id,
        "settings": settings.model_dump(),
        "export_timestamp": "2024-01-01T00:00:00Z",
        "format": "json",
    }


@router.delete("/{player_id}/data")
async def delete_player_data(
    player_id: str, current_player: TokenData = Depends(get_current_active_player)
) -> dict[str, str]:
    """
    Delete player data.

    Args:
        player_id: Player identifier
        current_player: Current authenticated player

    Returns:
        Dict: Deletion confirmation

    Raises:
        HTTPException: If access denied
    """
    # Check if the current player is deleting their own data
    if current_player.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only delete your own data",
        )

    # Remove player settings
    if player_id in _PLAYER_SETTINGS:
        del _PLAYER_SETTINGS[player_id]

    return {"message": "Player data deleted successfully"}
