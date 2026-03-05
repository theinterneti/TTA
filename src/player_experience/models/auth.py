"""

# Logseq: [[TTA.dev/Player_experience/Models/Auth]]
Authentication and authorization models for the Player Experience system.

This module defines user roles, permissions, and multi-factor authentication
models for enhanced security.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    """User roles for role-based access control."""

    PLAYER = "player"
    THERAPIST = "therapist"
    ADMIN = "admin"
    RESEARCHER = "researcher"
    MODERATOR = "moderator"


class Permission(StrEnum):
    """System permissions for fine-grained access control."""

    # Player permissions
    CREATE_CHARACTER = "create_character"
    MANAGE_OWN_CHARACTERS = "manage_own_characters"
    ACCESS_THERAPEUTIC_CONTENT = "access_therapeutic_content"
    MANAGE_OWN_PROFILE = "manage_own_profile"
    EXPORT_OWN_DATA = "export_own_data"
    DELETE_OWN_DATA = "delete_own_data"

    # Therapist permissions
    VIEW_PATIENT_PROGRESS = "view_patient_progress"
    MANAGE_THERAPEUTIC_CONTENT = "manage_therapeutic_content"
    ACCESS_CRISIS_PROTOCOLS = "access_crisis_protocols"
    VIEW_ANONYMIZED_DATA = "view_anonymized_data"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    ACCESS_AUDIT_LOGS = "access_audit_logs"
    MANAGE_ROLES = "manage_roles"
    SYSTEM_MAINTENANCE = "system_maintenance"

    # Researcher permissions
    ACCESS_RESEARCH_DATA = "access_research_data"
    EXPORT_ANONYMIZED_DATA = "export_anonymized_data"
    MANAGE_RESEARCH_STUDIES = "manage_research_studies"

    # Moderator permissions
    MODERATE_CONTENT = "moderate_content"
    HANDLE_REPORTS = "handle_reports"
    TEMPORARY_USER_ACTIONS = "temporary_user_actions"


class MFAMethod(StrEnum):
    """Multi-factor authentication methods."""

    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, etc.)
    SMS = "sms"  # SMS-based verification
    EMAIL = "email"  # Email-based verification
    BACKUP_CODES = "backup_codes"  # Recovery backup codes


@dataclass
class RolePermissions:
    """Defines permissions for each role."""

    role: UserRole
    permissions: list[Permission]
    description: str


# Default role permissions mapping
DEFAULT_ROLE_PERMISSIONS = {
    UserRole.PLAYER: RolePermissions(
        role=UserRole.PLAYER,
        permissions=[
            Permission.CREATE_CHARACTER,
            Permission.MANAGE_OWN_CHARACTERS,
            Permission.ACCESS_THERAPEUTIC_CONTENT,
            Permission.MANAGE_OWN_PROFILE,
            Permission.EXPORT_OWN_DATA,
            Permission.DELETE_OWN_DATA,
        ],
        description="Standard player with access to therapeutic content and character management",
    ),
    UserRole.THERAPIST: RolePermissions(
        role=UserRole.THERAPIST,
        permissions=[
            Permission.VIEW_PATIENT_PROGRESS,
            Permission.MANAGE_THERAPEUTIC_CONTENT,
            Permission.ACCESS_CRISIS_PROTOCOLS,
            Permission.VIEW_ANONYMIZED_DATA,
            Permission.MANAGE_OWN_PROFILE,
            Permission.EXPORT_OWN_DATA,
        ],
        description="Licensed therapist with access to patient data and therapeutic tools",
    ),
    UserRole.RESEARCHER: RolePermissions(
        role=UserRole.RESEARCHER,
        permissions=[
            Permission.ACCESS_RESEARCH_DATA,
            Permission.EXPORT_ANONYMIZED_DATA,
            Permission.MANAGE_RESEARCH_STUDIES,
            Permission.VIEW_ANONYMIZED_DATA,
            Permission.MANAGE_OWN_PROFILE,
        ],
        description="Researcher with access to anonymized data for studies",
    ),
    UserRole.MODERATOR: RolePermissions(
        role=UserRole.MODERATOR,
        permissions=[
            Permission.MODERATE_CONTENT,
            Permission.HANDLE_REPORTS,
            Permission.TEMPORARY_USER_ACTIONS,
            Permission.MANAGE_OWN_PROFILE,
        ],
        description="Content moderator with limited administrative capabilities",
    ),
    UserRole.ADMIN: RolePermissions(
        role=UserRole.ADMIN,
        permissions=list(Permission),  # All permissions
        description="System administrator with full access",
    ),
}


@dataclass
class MFAConfig:
    """Multi-factor authentication configuration."""

    enabled: bool = False
    required_methods: list[MFAMethod] = field(default_factory=list)
    backup_codes_count: int = 10
    totp_issuer: str = "TTA Therapeutic Platform"
    sms_enabled: bool = False
    email_enabled: bool = True
    recovery_codes_enabled: bool = True


@dataclass
class MFASecret:
    """MFA secret information for a user."""

    user_id: str
    method: MFAMethod
    secret: str  # Encrypted secret
    backup_codes: list[str] = field(default_factory=list)  # Encrypted backup codes
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime | None = None
    is_verified: bool = False


class MFAChallenge(BaseModel):
    """MFA challenge request model."""

    challenge_id: str
    method: MFAMethod
    expires_at: datetime
    attempts_remaining: int = 3


class MFAVerification(BaseModel):
    """MFA verification request model."""

    challenge_id: str
    code: str
    method: MFAMethod


class UserCredentials(BaseModel):
    """User credentials for authentication."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: str | None = None
    phone: str | None = None


class UserRegistration(BaseModel):
    """User registration request model."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8)
    phone: str | None = None
    role: UserRole = UserRole.PLAYER
    therapeutic_preferences: dict[str, Any] | None = None
    privacy_settings: dict[str, Any] | None = None


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")


class PasswordReset(BaseModel):
    """Password reset confirmation model."""

    token: str
    new_password: str = Field(..., min_length=8)


class SecurityEvent(BaseModel):
    """Security event for audit logging."""

    event_type: str
    user_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical


@dataclass
class AuthenticatedUser:
    """Authenticated user with role and permissions."""

    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: list[Permission]
    mfa_enabled: bool = False
    mfa_verified: bool = False
    last_login: datetime | None = None
    session_id: str | None = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(perm in self.permissions for perm in permissions)

    def has_all_permissions(self, permissions: list[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(perm in self.permissions for perm in permissions)

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def is_therapist(self) -> bool:
        """Check if user is a therapist."""
        return self.role == UserRole.THERAPIST

    def can_access_user_data(self, target_user_id: str) -> bool:
        """Check if user can access another user's data."""
        # Users can always access their own data
        if self.user_id == target_user_id:
            return True

        # Admins can access any user's data
        if self.is_admin():
            return True

        # Therapists can access their patients' data (would need additional logic)
        if self.is_therapist() and self.has_permission(
            Permission.VIEW_PATIENT_PROGRESS
        ):
            # TODO: Implement therapist-patient relationship checking
            return False

        return False


class SessionInfo(BaseModel):
    """Session information model."""

    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True
    mfa_verified: bool = False


class SecuritySettings(BaseModel):
    """Security settings for the authentication system."""

    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    password_max_age_days: int = 90
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 480  # 8 hours
    mfa_required_for_sensitive_ops: bool = True
    require_mfa_for_roles: list[UserRole] = field(
        default_factory=lambda: [UserRole.ADMIN, UserRole.THERAPIST]
    )
