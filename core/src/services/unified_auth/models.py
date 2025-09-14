"""
Unified Authentication Models

Data models for the consolidated TTA authentication system that serves all interfaces
with consistent user profiles, tokens, and session management.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """Standardized user roles across all TTA interfaces."""

    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"
    STAKEHOLDER = "stakeholder"
    DEVELOPER = "developer"


class InterfaceType(str, Enum):
    """Available TTA interface types."""

    PATIENT = "patient"
    CLINICAL = "clinical"
    ADMIN = "admin"
    PUBLIC = "public"
    DEVELOPER = "developer"


class Permission(str, Enum):
    """Granular permissions for role-based access control."""

    # Patient permissions
    CREATE_CHARACTER = "create_character"
    VIEW_PROGRESS = "view_progress"
    ACCESS_THERAPEUTIC_CONTENT = "access_therapeutic_content"

    # Clinical permissions
    VIEW_PATIENT_DATA = "view_patient_data"
    MANAGE_THERAPEUTIC_SESSIONS = "manage_therapeutic_sessions"
    ACCESS_CRISIS_TOOLS = "access_crisis_tools"
    GENERATE_REPORTS = "generate_reports"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_ROLES = "manage_roles"

    # Developer permissions
    ACCESS_DEBUG_TOOLS = "access_debug_tools"
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_SYSTEM_METRICS = "view_system_metrics"


class TherapeuticFramework(str, Enum):
    """Supported therapeutic frameworks."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based_therapy"
    HUMANISTIC = "humanistic_therapy"
    PSYCHODYNAMIC = "psychodynamic_therapy"
    SOLUTION_FOCUSED = "solution_focused_therapy"
    NARRATIVE_THERAPY = "narrative_therapy"


class IntensityLevel(str, Enum):
    """Therapeutic intensity levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRISIS = "crisis"


class PrivacySettings(BaseModel):
    """User privacy settings for HIPAA compliance."""

    share_progress: bool = False
    allow_research_participation: bool = False
    data_retention_days: int = 365
    audit_log_retention_days: int = 2555  # 7 years for HIPAA


class AccessibilitySettings(BaseModel):
    """User accessibility preferences."""

    high_contrast: bool = False
    large_text: bool = False
    screen_reader_support: bool = False
    reduced_motion: bool = False
    keyboard_navigation: bool = False


class TherapeuticPreferences(BaseModel):
    """User therapeutic preferences."""

    preferred_frameworks: list[TherapeuticFramework] = Field(default_factory=list)
    intensity_level: IntensityLevel = IntensityLevel.MODERATE
    privacy_settings: PrivacySettings = Field(default_factory=PrivacySettings)
    crisis_contact_enabled: bool = True
    session_reminders: bool = True


class UIPreferences(BaseModel):
    """User interface preferences."""

    theme: str = "therapeutic_calm"
    accessibility_settings: AccessibilitySettings = Field(
        default_factory=AccessibilitySettings
    )
    language: str = "en"
    timezone: str = "UTC"


class UserProfile(BaseModel):
    """Unified user profile structure."""

    # Display Information
    first_name: str | None = None
    last_name: str | None = None
    organization: str | None = None

    # Therapeutic Preferences
    therapeutic_preferences: TherapeuticPreferences | None = None

    # Interface Preferences
    ui_preferences: UIPreferences = Field(default_factory=UIPreferences)

    def get_display_name(self, username: str = "") -> str:
        """Get display name for user interfaces."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif username:
            return username
        else:
            return "User"


class TherapeuticContext(BaseModel):
    """Therapeutic context for clinical interfaces."""

    current_session_id: str | None = None
    active_character_id: str | None = None
    crisis_risk_level: IntensityLevel = IntensityLevel.LOW
    last_assessment_date: datetime | None = None
    therapeutic_goals: list[str] = Field(default_factory=list)


class UnifiedUser(BaseModel):
    """Unified user model for all TTA interfaces."""

    # Core Identity
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: str

    # Role and Permissions
    role: UserRole
    permissions: list[Permission] = Field(default_factory=list)
    interface_access: list[InterfaceType] = Field(default_factory=list)

    # Profile Information
    profile: UserProfile = Field(default_factory=UserProfile)

    # Security
    mfa_enabled: bool = False
    mfa_verified: bool | None = None
    last_login: datetime | None = None
    password_last_changed: datetime | None = None

    # Therapeutic Context
    therapeutic_context: TherapeuticContext | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    def get_display_name(self) -> str:
        """Get display name for user interfaces."""
        if self.profile.first_name or self.profile.last_name:
            return self.profile.get_display_name(self.username)
        return self.username


class AuthTokens(BaseModel):
    """Authentication tokens response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expiration
    refresh_expires_in: int  # Seconds until refresh token expiration


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    # Standard JWT Claims
    sub: str  # User ID
    iat: int  # Issued at
    exp: int  # Expires at
    iss: str = "tta-auth-service"  # Issuer
    aud: list[str] = Field(default_factory=list)  # Audience (interfaces)

    # TTA Custom Claims
    username: str
    email: str
    role: UserRole
    permissions: list[str] = Field(default_factory=list)
    interface_access: list[str] = Field(default_factory=list)
    mfa_verified: bool = False

    # Session Context
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    device_id: str | None = None
    ip_address: str | None = None


class LoginCredentials(BaseModel):
    """Login credentials."""

    username: str
    password: str
    interface_type: InterfaceType
    device_id: str | None = None
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response with user data and tokens."""

    user: UnifiedUser
    tokens: AuthTokens
    session_id: str
    mfa_required: bool = False
    mfa_challenge: dict[str, Any] | None = None


class SessionInfo(BaseModel):
    """Session information."""

    session_id: str
    user_id: str
    interface_type: InterfaceType
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str | None = None
    device_id: str | None = None
    is_active: bool = True


class AuditLogEntry(BaseModel):
    """HIPAA-compliant audit log entry."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str | None = None
    username: str | None = None
    action: str
    resource: str
    interface_type: InterfaceType | None = None
    ip_address: str | None = None
    device_id: str | None = None
    session_id: str | None = None
    success: bool
    details: dict[str, Any] = Field(default_factory=dict)

    # HIPAA-specific fields
    patient_id: str | None = None  # If accessing patient data
    phi_accessed: bool = False  # Protected Health Information accessed
    authorization_basis: str | None = None  # Legal basis for access


class AuthenticationError(Exception):
    """Authentication-related errors."""

    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class AuthorizationError(Exception):
    """Authorization-related errors."""

    def __init__(self, message: str, required_permission: str | None = None):
        self.message = message
        self.required_permission = required_permission
        super().__init__(message)


class SessionExpiredError(Exception):
    """Session expiration errors."""

    def __init__(self, message: str = "Session has expired"):
        self.message = message
        super().__init__(message)
