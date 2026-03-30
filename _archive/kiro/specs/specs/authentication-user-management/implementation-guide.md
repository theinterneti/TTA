# Authentication & User Management - Implementation Guide

**Date:** November 2, 2025
**Status:** Active Implementation Guide
**Component:** Authentication & User Management System
**Spec Version:** 1.0
**Related Specs:** `requirements.md`, `design.md`, `tasks.md`

---

## Purpose

This document bridges the spec-to-implementation gap for the Authentication & User Management system, providing detailed implementation guidance for:
- Privacy controls and data rights (GDPR, CCPA compliance)
- Data export and deletion workflows
- Multi-character support implementation
- Security best practices and integration patterns

---

## 1. Privacy Controls Implementation

### 1.1 Privacy Settings Model

**Implementation:**

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class DataSharingLevel(Enum):
    """Granular data sharing control levels."""
    NONE = "none"  # No data sharing
    ANONYMOUS = "anonymous"  # Anonymized data only
    AGGREGATE = "aggregate"  # Aggregate statistics only
    FULL = "full"  # Full data sharing (with consent)

class CommunicationPreference(Enum):
    """User communication preferences."""
    ALL = "all"  # All communications
    ESSENTIAL_ONLY = "essential"  # Only essential communications
    NONE = "none"  # No communications

@dataclass
class PrivacySettings:
    """Comprehensive privacy control settings."""
    user_id: str

    # Data Sharing Controls
    research_data_sharing: DataSharingLevel = DataSharingLevel.NONE
    therapeutic_analytics_sharing: DataSharingLevel = DataSharingLevel.AGGREGATE
    platform_improvement_sharing: DataSharingLevel = DataSharingLevel.ANONYMOUS

    # Communication Preferences
    email_notifications: CommunicationPreference = CommunicationPreference.ESSENTIAL_ONLY
    security_alerts: bool = True  # Always enabled for safety
    therapeutic_reminders: bool = True
    platform_updates: bool = False

    # Visibility Controls
    profile_visibility: bool = False  # Private by default
    character_visibility: bool = False  # Private by default
    progress_visibility: bool = False  # Private by default

    # Data Retention
    therapeutic_session_retention_days: Optional[int] = 365  # 1 year default
    chat_history_retention_days: Optional[int] = 90  # 3 months default
    minimal_data_mode: bool = False  # When True, only essential data kept

    # Consent Tracking
    consent_version: str  # Version of privacy policy user consented to
    consent_date: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "research_data_sharing": self.research_data_sharing.value,
            "therapeutic_analytics_sharing": self.therapeutic_analytics_sharing.value,
            "platform_improvement_sharing": self.platform_improvement_sharing.value,
            "email_notifications": self.email_notifications.value,
            "security_alerts": self.security_alerts,
            "therapeutic_reminders": self.therapeutic_reminders,
            "platform_updates": self.platform_updates,
            "profile_visibility": self.profile_visibility,
            "character_visibility": self.character_visibility,
            "progress_visibility": self.progress_visibility,
            "therapeutic_session_retention_days": self.therapeutic_session_retention_days,
            "chat_history_retention_days": self.chat_history_retention_days,
            "minimal_data_mode": self.minimal_data_mode,
            "consent_version": self.consent_version,
            "consent_date": self.consent_date.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

### 1.2 Privacy Manager Implementation

```python
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PrivacyManager:
    """Manages user privacy settings and data access controls."""

    def __init__(self, neo4j_manager, audit_logger):
        self.db = neo4j_manager
        self.audit = audit_logger

    async def get_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Retrieve user's privacy settings."""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
        RETURN ps
        """
        result = await self.db.execute_read(query, user_id=user_id)
        if not result:
            return self._create_default_privacy_settings(user_id)
        return PrivacySettings(**result[0]['ps'])

    async def update_privacy_settings(
        self,
        user_id: str,
        updates: Dict[str, any],
        reason: str = "User requested update"
    ) -> bool:
        """Update privacy settings with audit logging."""
        try:
            # Validate updates
            self._validate_privacy_updates(updates)

            # Get current settings for audit trail
            current = await self.get_privacy_settings(user_id)

            # Apply updates
            query = """
            MATCH (u:User {user_id: $user_id})-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
            SET ps += $updates,
                ps.updated_at = datetime()
            RETURN ps
            """
            result = await self.db.execute_write(
                query,
                user_id=user_id,
                updates=updates
            )

            # Audit log
            await self.audit.log_privacy_change(
                user_id=user_id,
                field_changes=self._diff_settings(current, updates),
                reason=reason,
                timestamp=datetime.utcnow()
            )

            # Apply side effects (e.g., data deletion if retention reduced)
            await self._apply_privacy_side_effects(user_id, updates)

            logger.info(f"Privacy settings updated for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update privacy settings for {user_id}: {e}")
            return False

    async def explain_privacy_setting(self, setting_name: str) -> Dict[str, str]:
        """Provide clear explanation of privacy setting implications."""
        explanations = {
            "research_data_sharing": {
                "title": "Research Data Sharing",
                "description": "Controls whether your therapeutic data can be used for research purposes.",
                "none": "No data shared. Your data stays completely private.",
                "anonymous": "Only anonymized data (with identifying info removed) shared for research.",
                "aggregate": "Only aggregate statistics (no individual data) shared.",
                "full": "Full data shared with explicit consent. You can revoke anytime.",
                "implications": "Research helps improve therapeutic outcomes for all users.",
            },
            "minimal_data_mode": {
                "title": "Minimal Data Mode",
                "description": "When enabled, only essential data necessary for core functionality is stored.",
                "enabled": "Only basic profile and current session data kept. History and analytics disabled.",
                "disabled": "Full therapeutic history maintained for progress tracking and personalization.",
                "implications": "Minimal mode increases privacy but reduces personalization and progress tracking.",
            },
            # ... additional explanations
        }
        return explanations.get(setting_name, {})

    def _validate_privacy_updates(self, updates: Dict[str, any]) -> None:
        """Validate privacy setting updates."""
        # Security alerts cannot be disabled
        if "security_alerts" in updates and not updates["security_alerts"]:
            raise ValueError("Security alerts cannot be disabled for user safety")

        # Retention periods must be reasonable
        if "therapeutic_session_retention_days" in updates:
            retention = updates["therapeutic_session_retention_days"]
            if retention is not None and (retention < 1 or retention > 3650):
                raise ValueError("Retention period must be between 1 day and 10 years")

    async def _apply_privacy_side_effects(
        self,
        user_id: str,
        updates: Dict[str, any]
    ) -> None:
        """Apply side effects of privacy changes (e.g., data deletion)."""
        # If retention period reduced, trigger cleanup
        if "therapeutic_session_retention_days" in updates:
            await self._cleanup_old_sessions(
                user_id,
                updates["therapeutic_session_retention_days"]
            )

        # If minimal data mode enabled, trigger data minimization
        if updates.get("minimal_data_mode"):
            await self._minimize_user_data(user_id)

    def _diff_settings(
        self,
        current: PrivacySettings,
        updates: Dict[str, any]
    ) -> List[Dict[str, any]]:
        """Generate diff of setting changes for audit log."""
        changes = []
        for key, new_value in updates.items():
            old_value = getattr(current, key, None)
            if old_value != new_value:
                changes.append({
                    "field": key,
                    "old_value": str(old_value),
                    "new_value": str(new_value),
                })
        return changes
```

### 1.3 Privacy API Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

router = APIRouter(prefix="/api/v1/privacy", tags=["privacy"])

@router.get("/settings")
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Get current user's privacy settings."""
    settings = await privacy_manager.get_privacy_settings(current_user.user_id)
    return {"settings": settings.to_dict()}

@router.patch("/settings")
async def update_privacy_settings(
    updates: Dict[str, any],
    current_user: User = Depends(get_current_user),
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Update privacy settings with validation."""
    success = await privacy_manager.update_privacy_settings(
        user_id=current_user.user_id,
        updates=updates,
        reason="User requested update via API"
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update privacy settings")
    return {"message": "Privacy settings updated successfully"}

@router.get("/settings/{setting_name}/explain")
async def explain_privacy_setting(
    setting_name: str,
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Get detailed explanation of a privacy setting."""
    explanation = await privacy_manager.explain_privacy_setting(setting_name)
    if not explanation:
        raise HTTPException(status_code=404, detail="Setting not found")
    return explanation
```

---

## 2. Data Export Implementation

### 2.1 Data Export Format

**Standard Export Format (JSON):**

```json
{
  "export_metadata": {
    "user_id": "user_123",
    "export_date": "2025-11-02T10:30:00Z",
    "export_version": "1.0",
    "data_types_included": ["profile", "characters", "sessions", "progress"]
  },
  "user_profile": {
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z",
    "privacy_settings": {...},
    "therapeutic_preferences": {...}
  },
  "characters": [
    {
      "character_id": "char_123",
      "name": "Character Name",
      "created_at": "2025-01-15T10:00:00Z",
      "therapeutic_profile": {...},
      "progress_data": {...}
    }
  ],
  "therapeutic_sessions": [
    {
      "session_id": "session_123",
      "character_id": "char_123",
      "start_time": "2025-10-01T14:00:00Z",
      "duration_minutes": 45,
      "summary": "Session summary",
      "progress_metrics": {...}
    }
  ],
  "audit_trail": [
    {
      "timestamp": "2025-01-01T00:05:00Z",
      "action": "profile_created",
      "details": "User account created"
    }
  ]
}
```

### 2.2 Data Exporter Implementation

```python
import json
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta

class DataExporter:
    """Handles user data export requests (GDPR Article 20 compliance)."""

    def __init__(self, neo4j_manager, redis_cache, storage_service):
        self.db = neo4j_manager
        self.cache = redis_cache
        self.storage = storage_service

    async def request_data_export(self, user_id: str) -> str:
        """
        Initiate data export request.
        Returns export_request_id for tracking.
        """
        export_request_id = f"export_{user_id}_{datetime.utcnow().timestamp()}"

        # Store export request status
        await self.cache.setex(
            f"export_request:{export_request_id}",
            timedelta(days=30),
            json.dumps({
                "user_id": user_id,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
            })
        )

        # Queue async export job
        asyncio.create_task(self._generate_export(user_id, export_request_id))

        logger.info(f"Data export requested for user {user_id}: {export_request_id}")
        return export_request_id

    async def get_export_status(self, export_request_id: str) -> Dict[str, any]:
        """Check status of data export request."""
        status_json = await self.cache.get(f"export_request:{export_request_id}")
        if not status_json:
            raise ValueError(f"Export request {export_request_id} not found")
        return json.loads(status_json)

    async def _generate_export(self, user_id: str, export_request_id: str) -> None:
        """Generate complete data export (async background job)."""
        try:
            # Update status to processing
            await self._update_export_status(export_request_id, "processing")

            # Gather all user data
            export_data = {
                "export_metadata": await self._build_export_metadata(user_id),
                "user_profile": await self._export_user_profile(user_id),
                "characters": await self._export_characters(user_id),
                "therapeutic_sessions": await self._export_sessions(user_id),
                "chat_history": await self._export_chat_history(user_id),
                "audit_trail": await self._export_audit_trail(user_id),
            }

            # Save to secure storage
            file_path = await self.storage.save_export(
                user_id=user_id,
                export_id=export_request_id,
                data=export_data
            )

            # Update status to complete
            await self._update_export_status(
                export_request_id,
                "complete",
                file_path=file_path
            )

            # Send notification email
            await self._notify_export_ready(user_id, export_request_id)

            logger.info(f"Data export completed for user {user_id}")

        except Exception as e:
            logger.error(f"Data export failed for user {user_id}: {e}")
            await self._update_export_status(
                export_request_id,
                "failed",
                error=str(e)
            )

    async def _export_user_profile(self, user_id: str) -> Dict[str, any]:
        """Export user profile data."""
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[:HAS_PRIVACY_SETTINGS]->(ps:PrivacySettings)
        OPTIONAL MATCH (u)-[:HAS_PREFERENCES]->(tp:TherapeuticPreferences)
        RETURN u, ps, tp
        """
        result = await self.db.execute_read(query, user_id=user_id)
        # Sanitize and format
        return self._sanitize_for_export(result[0])

    async def _export_characters(self, user_id: str) -> List[Dict[str, any]]:
        """Export all character data."""
        query = """
        MATCH (u:User {user_id: $user_id})-[:OWNS]->(c:Character)
        OPTIONAL MATCH (c)-[:HAS_PROGRESS]->(p:Progress)
        RETURN c, collect(p) as progress
        """
        results = await self.db.execute_read(query, user_id=user_id)
        return [self._sanitize_for_export(r) for r in results]

    async def _export_sessions(self, user_id: str) -> List[Dict[str, any]]:
        """Export therapeutic session data."""
        # Implementation depends on session storage schema
        pass

    def _sanitize_for_export(self, data: Dict[str, any]) -> Dict[str, any]:
        """Remove internal IDs and sensitive system data."""
        # Remove internal implementation details
        sensitive_keys = ['password_hash', 'internal_id', 'system_metadata']
        return {k: v for k, v in data.items() if k not in sensitive_keys}
```

### 2.3 Data Export API Endpoints

```python
@router.post("/export/request")
async def request_data_export(
    current_user: User = Depends(get_current_user),
    data_exporter: DataExporter = Depends(get_data_exporter)
):
    """
    Request complete data export (GDPR Article 20).
    Export will be generated asynchronously and user notified when ready.
    """
    export_id = await data_exporter.request_data_export(current_user.user_id)
    return {
        "export_request_id": export_id,
        "message": "Data export requested. You will be notified via email when ready.",
        "estimated_time": "Within 24 hours"
    }

@router.get("/export/status/{export_request_id}")
async def get_export_status(
    export_request_id: str,
    current_user: User = Depends(get_current_user),
    data_exporter: DataExporter = Depends(get_data_exporter)
):
    """Check status of data export request."""
    status = await data_exporter.get_export_status(export_request_id)
    # Verify user owns this export request
    if status["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return status

@router.get("/export/download/{export_request_id}")
async def download_export(
    export_request_id: str,
    current_user: User = Depends(get_current_user),
    data_exporter: DataExporter = Depends(get_data_exporter)
):
    """Download completed data export."""
    status = await data_exporter.get_export_status(export_request_id)

    # Verify ownership and completion
    if status["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if status["status"] != "complete":
        raise HTTPException(status_code=400, detail="Export not ready")

    # Return file download
    return FileResponse(
        path=status["file_path"],
        filename=f"tta_data_export_{current_user.user_id}.json",
        media_type="application/json"
    )
```

---

## 3. Data Deletion Implementation

### 3.1 Account Deletion Workflow

**Deletion Process:**
1. User requests account deletion
2. System sends confirmation email with link
3. User confirms (or 14-day cooling-off period)
4. Account marked for deletion (soft delete)
5. 30-day retention period for recovery
6. Permanent deletion after 30 days

### 3.2 Account Deleter Implementation

```python
from datetime import datetime, timedelta
from enum import Enum

class DeletionStatus(Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AccountDeleter:
    """Handles account deletion requests (GDPR Article 17 compliance)."""

    def __init__(self, neo4j_manager, redis_cache, email_service):
        self.db = neo4j_manager
        self.cache = redis_cache
        self.email = email_service

    async def request_account_deletion(
        self,
        user_id: str,
        reason: Optional[str] = None
    ) -> str:
        """
        Initiate account deletion request.
        Returns deletion_request_id.
        """
        deletion_request_id = f"delete_{user_id}_{datetime.utcnow().timestamp()}"

        # Create deletion request
        deletion_request = {
            "deletion_request_id": deletion_request_id,
            "user_id": user_id,
            "status": DeletionStatus.REQUESTED.value,
            "requested_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "confirmation_deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "permanent_deletion_date": None,
        }

        # Store request
        await self.cache.setex(
            f"deletion_request:{deletion_request_id}",
            timedelta(days=45),  # 14 days confirm + 30 days retention + buffer
            json.dumps(deletion_request)
        )

        # Send confirmation email
        await self.email.send_deletion_confirmation(
            user_id=user_id,
            deletion_request_id=deletion_request_id,
            deadline=deletion_request["confirmation_deadline"]
        )

        logger.info(f"Account deletion requested for user {user_id}")
        return deletion_request_id

    async def confirm_account_deletion(self, deletion_request_id: str, token: str) -> None:
        """
        Confirm account deletion request (from email link).
        Schedules permanent deletion 30 days from confirmation.
        """
        # Validate token
        if not await self._validate_confirmation_token(deletion_request_id, token):
            raise ValueError("Invalid confirmation token")

        # Get deletion request
        request_json = await self.cache.get(f"deletion_request:{deletion_request_id}")
        if not request_json:
            raise ValueError("Deletion request not found or expired")

        deletion_request = json.loads(request_json)

        # Update status
        deletion_request["status"] = DeletionStatus.CONFIRMED.value
        deletion_request["confirmed_at"] = datetime.utcnow().isoformat()
        deletion_request["permanent_deletion_date"] = (
            datetime.utcnow() + timedelta(days=30)
        ).isoformat()

        # Save updated request
        await self.cache.setex(
            f"deletion_request:{deletion_request_id}",
            timedelta(days=31),
            json.dumps(deletion_request)
        )

        # Mark account as scheduled for deletion in database
        await self._mark_account_for_deletion(
            deletion_request["user_id"],
            deletion_request["permanent_deletion_date"]
        )

        # Schedule deletion job
        asyncio.create_task(self._schedule_deletion_job(deletion_request))

        logger.info(f"Account deletion confirmed: {deletion_request_id}")

    async def cancel_account_deletion(self, user_id: str) -> bool:
        """Cancel pending account deletion (during 30-day retention period)."""
        # Find active deletion request
        # Implementation depends on how requests are indexed
        pass

    async def execute_account_deletion(self, user_id: str) -> None:
        """
        Permanently delete user account and all associated data.
        This is irreversible.
        """
        try:
            logger.warning(f"PERMANENT DELETION starting for user {user_id}")

            # Delete all user data from Neo4j
            await self._delete_user_graph_data(user_id)

            # Delete all user sessions from Redis
            await self._delete_user_sessions(user_id)

            # Delete user files from storage
            await self._delete_user_files(user_id)

            # Anonymize any data that must be retained for legal reasons
            await self._anonymize_retained_data(user_id)

            # Log completion
            await self._log_deletion_completion(user_id)

            logger.warning(f"PERMANENT DELETION completed for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to delete account for user {user_id}: {e}")
            raise

    async def _delete_user_graph_data(self, user_id: str) -> None:
        """Delete all user nodes and relationships from Neo4j."""
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[r]-()
        DELETE r, u
        """
        await self.db.execute_write(query, user_id=user_id)

    async def _mark_account_for_deletion(
        self,
        user_id: str,
        deletion_date: str
    ) -> None:
        """Mark account as scheduled for deletion in database."""
        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.deletion_scheduled = true,
            u.deletion_date = $deletion_date,
            u.account_status = 'deletion_pending'
        """
        await self.db.execute_write(
            query,
            user_id=user_id,
            deletion_date=deletion_date
        )
```

### 3.3 Account Deletion API Endpoints

```python
@router.delete("/account")
async def request_account_deletion(
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    account_deleter: AccountDeleter = Depends(get_account_deleter)
):
    """
    Request account deletion (GDPR Article 17).
    Requires email confirmation within 14 days.
    Account will be permanently deleted 30 days after confirmation.
    """
    deletion_id = await account_deleter.request_account_deletion(
        user_id=current_user.user_id,
        reason=reason
    )
    return {
        "deletion_request_id": deletion_id,
        "message": "Deletion confirmation email sent. Please confirm within 14 days.",
        "timeline": {
            "confirmation_deadline": "14 days from now",
            "permanent_deletion": "30 days after confirmation"
        }
    }

@router.post("/account/deletion/confirm")
async def confirm_account_deletion(
    deletion_request_id: str,
    token: str,
    account_deleter: AccountDeleter = Depends(get_account_deleter)
):
    """Confirm account deletion via email link."""
    await account_deleter.confirm_account_deletion(deletion_request_id, token)
    return {
        "message": "Account deletion confirmed. You have 30 days to cancel if you change your mind.",
        "permanent_deletion_date": "30 days from now"
    }

@router.post("/account/deletion/cancel")
async def cancel_account_deletion(
    current_user: User = Depends(get_current_user),
    account_deleter: AccountDeleter = Depends(get_account_deleter)
):
    """Cancel pending account deletion (within 30-day retention period)."""
    success = await account_deleter.cancel_account_deletion(current_user.user_id)
    if not success:
        raise HTTPException(status_code=400, detail="No pending deletion request found")
    return {"message": "Account deletion cancelled successfully"}
```

---

## 4. Multi-Character Support Implementation

### 4.1 Character Management

```python
@dataclass
class Character:
    """Character profile with therapeutic context."""
    character_id: str
    user_id: str
    name: str
    created_at: datetime
    last_played: datetime
    is_active: bool

    # Therapeutic profile
    therapeutic_goals: List[str]
    comfort_level: int  # 1-10 scale
    content_preferences: Dict[str, any]
    progress_metrics: Dict[str, float]

    # Narrative state
    current_scenario_id: Optional[str]
    narrative_history: List[str]
    relationship_states: Dict[str, any]

    def to_dict(self) -> dict:
        return {
            "character_id": self.character_id,
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "last_played": self.last_played.isoformat(),
            "is_active": self.is_active,
            "therapeutic_goals": self.therapeutic_goals,
            "comfort_level": self.comfort_level,
            "content_preferences": self.content_preferences,
            "progress_metrics": self.progress_metrics,
            "current_scenario_id": self.current_scenario_id,
        }

class CharacterManager:
    """Manages character profiles and isolation between characters."""

    MAX_CHARACTERS_PER_USER = 5

    def __init__(self, neo4j_manager):
        self.db = neo4j_manager

    async def create_character(
        self,
        user_id: str,
        character_data: Dict[str, any]
    ) -> Character:
        """Create new character profile with validation."""
        # Check character limit
        existing_count = await self.get_character_count(user_id)
        if existing_count >= self.MAX_CHARACTERS_PER_USER:
            raise ValueError(
                f"Maximum {self.MAX_CHARACTERS_PER_USER} characters per user. "
                "Please delete an existing character to create a new one."
            )

        # Validate character name uniqueness for user
        if await self.character_name_exists(user_id, character_data["name"]):
            raise ValueError("Character name already exists for this user")

        # Create character
        character_id = f"char_{user_id}_{datetime.utcnow().timestamp()}"
        character = Character(
            character_id=character_id,
            user_id=user_id,
            name=character_data["name"],
            created_at=datetime.utcnow(),
            last_played=datetime.utcnow(),
            is_active=True,
            therapeutic_goals=character_data.get("therapeutic_goals", []),
            comfort_level=character_data.get("comfort_level", 5),
            content_preferences=character_data.get("content_preferences", {}),
            progress_metrics={},
            current_scenario_id=None,
            narrative_history=[],
            relationship_states={},
        )

        # Store in Neo4j
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (c:Character $character_props)
        CREATE (u)-[:OWNS]->(c)
        RETURN c
        """
        await self.db.execute_write(
            query,
            user_id=user_id,
            character_props=character.to_dict()
        )

        logger.info(f"Character created: {character_id} for user {user_id}")
        return character

    async def get_user_characters(self, user_id: str) -> List[Character]:
        """Retrieve all characters for a user."""
        query = """
        MATCH (u:User {user_id: $user_id})-[:OWNS]->(c:Character)
        RETURN c
        ORDER BY c.last_played DESC
        """
        results = await self.db.execute_read(query, user_id=user_id)
        return [Character(**r['c']) for r in results]

    async def switch_character(
        self,
        user_id: str,
        character_id: str
    ) -> Character:
        """
        Switch active character for user.
        Ensures proper session isolation.
        """
        # Verify ownership
        if not await self.user_owns_character(user_id, character_id):
            raise ValueError("Character not found or access denied")

        # Load character
        character = await self.get_character(character_id)

        # Update last_played timestamp
        await self._update_character_last_played(character_id)

        # Clear any cached session data for previous character
        await self._clear_character_session_cache(user_id)

        logger.info(f"User {user_id} switched to character {character_id}")
        return character

    async def delete_character(
        self,
        user_id: str,
        character_id: str,
        confirmation: bool = False
    ) -> bool:
        """
        Delete character and all associated data.
        Requires explicit confirmation.
        """
        if not confirmation:
            raise ValueError("Deletion requires explicit confirmation")

        # Verify ownership
        if not await self.user_owns_character(user_id, character_id):
            raise ValueError("Character not found or access denied")

        # Delete character and all relationships
        query = """
        MATCH (c:Character {character_id: $character_id})
        OPTIONAL MATCH (c)-[r]-()
        DELETE r, c
        """
        await self.db.execute_write(query, character_id=character_id)

        logger.info(f"Character deleted: {character_id}")
        return True
```

### 4.2 Character Isolation & Context Switching

```python
class CharacterContextManager:
    """Ensures proper isolation between character contexts."""

    def __init__(self, redis_cache, neo4j_manager):
        self.cache = redis_cache
        self.db = neo4j_manager

    async def get_character_context(
        self,
        user_id: str,
        character_id: str
    ) -> Dict[str, any]:
        """
        Load character-specific context for therapeutic session.
        Ensures no data leakage between characters.
        """
        # Check cache first
        cache_key = f"character_context:{user_id}:{character_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Load from database
        query = """
        MATCH (c:Character {character_id: $character_id})
        OPTIONAL MATCH (c)-[:IN_SCENARIO]->(s:Scenario)
        OPTIONAL MATCH (c)-[:HAS_PROGRESS]->(p:Progress)
        OPTIONAL MATCH (c)-[:HAS_RELATIONSHIP]->(r:Relationship)
        RETURN c, s, collect(p) as progress, collect(r) as relationships
        """
        result = await self.db.execute_read(
            query,
            character_id=character_id
        )

        context = {
            "character": result[0]['c'],
            "current_scenario": result[0]['s'],
            "progress": result[0]['progress'],
            "relationships": result[0]['relationships'],
        }

        # Cache for 5 minutes
        await self.cache.setex(
            cache_key,
            timedelta(minutes=5),
            json.dumps(context)
        )

        return context

    async def clear_character_context_cache(
        self,
        user_id: str,
        character_id: Optional[str] = None
    ) -> None:
        """Clear cached character context (on switch or update)."""
        if character_id:
            cache_key = f"character_context:{user_id}:{character_id}"
            await self.cache.delete(cache_key)
        else:
            # Clear all character contexts for user
            pattern = f"character_context:{user_id}:*"
            keys = await self.cache.keys(pattern)
            if keys:
                await self.cache.delete(*keys)
```

---

## 5. Integration Points

### 5.1 Therapeutic Engine Integration

**Character context should be passed to therapeutic engine:**

```python
async def start_therapeutic_session(
    user_id: str,
    character_id: str,
    therapeutic_engine: TherapeuticEngine
):
    """Start therapeutic session with character context."""
    # Load character context
    context = await character_context_manager.get_character_context(
        user_id,
        character_id
    )

    # Initialize session with character-specific therapeutic profile
    session = await therapeutic_engine.create_session(
        user_id=user_id,
        character_id=character_id,
        therapeutic_goals=context["character"]["therapeutic_goals"],
        comfort_level=context["character"]["comfort_level"],
        content_preferences=context["character"]["content_preferences"],
        current_scenario=context["current_scenario"],
        progress_history=context["progress"],
    )

    return session
```

### 5.2 Safety Validator Integration

**Privacy settings should inform content filtering:**

```python
async def validate_therapeutic_content(
    user_id: str,
    character_id: str,
    content: str,
    safety_validator: SafetyValidator
) -> bool:
    """Validate content against user privacy and character preferences."""
    # Get privacy settings
    privacy_settings = await privacy_manager.get_privacy_settings(user_id)

    # Get character preferences
    character = await character_manager.get_character(character_id)

    # Validate against both
    is_safe = await safety_validator.validate_content(
        content=content,
        comfort_level=character.comfort_level,
        content_restrictions=character.content_preferences,
        minimal_data_mode=privacy_settings.minimal_data_mode,
    )

    return is_safe
```

---

## 6. Testing Strategy

### 6.1 Privacy Controls Tests

```python
import pytest

@pytest.mark.asyncio
async def test_privacy_settings_update():
    """Test privacy settings can be updated with audit logging."""
    user_id = "test_user_123"
    updates = {"research_data_sharing": "none"}

    success = await privacy_manager.update_privacy_settings(
        user_id,
        updates
    )

    assert success

    # Verify audit log created
    audit_entry = await audit_logger.get_latest_entry(user_id)
    assert audit_entry["action"] == "privacy_settings_updated"

@pytest.mark.asyncio
async def test_security_alerts_cannot_be_disabled():
    """Test that security alerts cannot be disabled for safety."""
    user_id = "test_user_123"
    updates = {"security_alerts": False}

    with pytest.raises(ValueError, match="Security alerts cannot be disabled"):
        await privacy_manager.update_privacy_settings(user_id, updates)
```

### 6.2 Data Export Tests

```python
@pytest.mark.asyncio
async def test_data_export_request():
    """Test data export request creates proper tracking."""
    user_id = "test_user_123"

    export_id = await data_exporter.request_data_export(user_id)

    assert export_id.startswith("export_")

    # Check status
    status = await data_exporter.get_export_status(export_id)
    assert status["status"] == "pending"
    assert status["user_id"] == user_id

@pytest.mark.asyncio
async def test_data_export_contains_all_data():
    """Test exported data includes all required information."""
    user_id = "test_user_123"

    # Generate export (sync for testing)
    export_data = await data_exporter._generate_export_data(user_id)

    # Verify completeness
    assert "user_profile" in export_data
    assert "characters" in export_data
    assert "therapeutic_sessions" in export_data
    assert "audit_trail" in export_data
```

### 6.3 Account Deletion Tests

```python
@pytest.mark.asyncio
async def test_account_deletion_workflow():
    """Test full account deletion workflow."""
    user_id = "test_user_123"

    # Request deletion
    deletion_id = await account_deleter.request_account_deletion(user_id)

    # Confirm deletion
    token = await _get_confirmation_token(deletion_id)
    await account_deleter.confirm_account_deletion(deletion_id, token)

    # Verify scheduled
    user = await get_user(user_id)
    assert user.deletion_scheduled == True

    # Execute deletion
    await account_deleter.execute_account_deletion(user_id)

    # Verify user no longer exists
    with pytest.raises(ValueError):
        await get_user(user_id)
```

### 6.4 Multi-Character Tests

```python
@pytest.mark.asyncio
async def test_character_creation_limit():
    """Test character creation respects per-user limit."""
    user_id = "test_user_123"

    # Create max characters
    for i in range(CharacterManager.MAX_CHARACTERS_PER_USER):
        await character_manager.create_character(
            user_id,
            {"name": f"Character {i}"}
        )

    # Attempt to create one more
    with pytest.raises(ValueError, match="Maximum.*characters"):
        await character_manager.create_character(
            user_id,
            {"name": "Extra Character"}
        )

@pytest.mark.asyncio
async def test_character_context_isolation():
    """Test character contexts are properly isolated."""
    user_id = "test_user_123"
    char1_id = "char_1"
    char2_id = "char_2"

    # Get contexts
    context1 = await character_context_manager.get_character_context(
        user_id,
        char1_id
    )
    context2 = await character_context_manager.get_character_context(
        user_id,
        char2_id
    )

    # Verify no data leakage
    assert context1["character"]["character_id"] != context2["character"]["character_id"]
    assert context1["progress"] != context2["progress"]
```

---

## 7. Security Considerations

### 7.1 Data Encryption

**Implementation Requirements:**
- Passwords: bcrypt with work factor >= 12
- Session tokens: Secure random generation (256-bit)
- Data at rest: AES-256 encryption for sensitive fields
- Data in transit: TLS 1.3 for all API calls

### 7.2 Rate Limiting

**Privacy API Rate Limits:**
- Privacy settings updates: 10/hour per user
- Data export requests: 5/day per user
- Account deletion requests: 3/day per user

### 7.3 Audit Logging

**Required Audit Events:**
- Privacy settings changes
- Data export requests
- Account deletion requests
- Character creation/deletion
- Admin access to user data

---

## 8. Compliance Checklist

### GDPR Compliance

- [x] Right to access (Article 15) - Data export
- [x] Right to rectification (Article 16) - Profile updates
- [x] Right to erasure (Article 17) - Account deletion
- [x] Right to data portability (Article 20) - JSON export
- [x] Right to object (Article 21) - Privacy controls
- [x] Consent management - Privacy settings with version tracking
- [x] Data minimization - Minimal data mode option
- [x] Purpose limitation - Clear explanations of data use

### CCPA Compliance

- [x] Right to know - Data export with audit trail
- [x] Right to delete - Account deletion workflow
- [x] Right to opt-out - Data sharing controls
- [x] Non-discrimination - No penalty for opting out

---

## 9. Next Steps

**Implementation Priority:**

1. **Week 1:** Privacy controls and settings management
2. **Week 2:** Data export implementation
3. **Week 3:** Account deletion workflow
4. **Week 4:** Multi-character support and context isolation
5. **Week 5:** Integration testing and security audit

**Related Specs:**
- See `requirements.md` for detailed acceptance criteria
- See `design.md` for architecture diagrams
- See `tasks.md` for implementation task breakdown

---

**Document Version:** 1.0
**Last Updated:** November 2, 2025
**Next Review:** December 2, 2025
**Maintainer:** TTA Development Team


---
**Logseq:** [[TTA.dev/_archive/Kiro/Specs/Specs/Authentication-user-management/Implementation-guide]]
