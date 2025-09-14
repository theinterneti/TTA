"""
Privacy API Endpoints

FastAPI endpoints for managing player privacy settings, consent, and GDPR compliance.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..privacy.data_protection import TherapeuticDataProtection
from ..privacy.privacy_manager import (
    ConsentType,
    DataRetentionPeriod,
    PrivacyManager,
    PrivacySettings,
)

# Import User model and authentication dependency
try:
    from ..models.user import User
    from ..services.auth_service import get_current_user
except ImportError:
    # Fallback for missing dependencies
    from typing import Any as User

    def get_current_user():
        """Fallback authentication dependency."""
        return {"user_id": "mock_user", "username": "mock"}


logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class ConsentUpdateRequest(BaseModel):
    consent_type: ConsentType
    granted: bool
    expires_at: datetime | None = None


class PrivacySettingsUpdateRequest(BaseModel):
    data_retention_period: DataRetentionPeriod | None = None
    allow_therapeutic_data_sharing: bool | None = None
    crisis_contact_sharing_allowed: bool | None = None
    export_format_preference: str | None = Field(None, regex="^(json|csv|pdf)$")
    notification_preferences: dict[str, bool] | None = None


class DataExportRequest(BaseModel):
    format: str = Field("json", regex="^(json|csv|pdf)$")
    include_encrypted_content: bool = False


class DataDeletionRequest(BaseModel):
    confirmation: str = Field(..., description="Must be 'DELETE_MY_DATA' to confirm")
    preserve_research_data: bool = True


class ConsentResponse(BaseModel):
    consent_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: datetime
    expires_at: datetime | None


# PrivacySettings is imported from privacy_manager - removing duplicate definition


# Initialize router
privacy_router = APIRouter(prefix="/api/privacy", tags=["privacy"])


# Dependency to get privacy manager
def get_privacy_manager() -> PrivacyManager:
    """Get privacy manager instance."""
    data_protection = TherapeuticDataProtection()
    return PrivacyManager(data_protection)


@privacy_router.get("/settings", response_model=PrivacySettings)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
) -> PrivacySettings:
    """Get user privacy settings."""
    privacy_manager = get_privacy_manager()
    return await privacy_manager.get_user_privacy_settings(current_user.id)
