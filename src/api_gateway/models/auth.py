"""
Authentication-related data models for the API Gateway.

This module contains models for user authentication, authorization,
and integration with the TTA authentication system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User role enumeration."""

    PATIENT = "patient"
    THERAPIST = "therapist"
    ADMIN = "admin"
    SYSTEM = "system"
    GUEST = "guest"


class AuthenticationMethod(str, Enum):
    """Authentication method enumeration."""

    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    MFA = "mfa"


class PermissionLevel(str, Enum):
    """Permission level enumeration."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    THERAPEUTIC = "therapeutic"
    CRISIS = "crisis"


class TherapeuticPermission(BaseModel):
    """Therapeutic-specific permissions."""

    can_access_sessions: bool = Field(
        default=False, description="Can access therapeutic sessions"
    )
    can_view_progress: bool = Field(
        default=False, description="Can view patient progress"
    )
    can_modify_treatment: bool = Field(
        default=False, description="Can modify treatment plans"
    )
    can_handle_crisis: bool = Field(
        default=False, description="Can handle crisis situations"
    )
    can_access_sensitive_data: bool = Field(
        default=False, description="Can access sensitive patient data"
    )
    supervision_required: bool = Field(
        default=True, description="Requires supervision for therapeutic actions"
    )


class UserPermissions(BaseModel):
    """User permissions and access control."""

    role: UserRole = Field(..., description="Primary user role")
    permissions: list[PermissionLevel] = Field(
        default_factory=list, description="General permissions"
    )
    therapeutic: TherapeuticPermission = Field(
        default_factory=TherapeuticPermission, description="Therapeutic permissions"
    )
    service_access: dict[str, list[str]] = Field(
        default_factory=dict, description="Service-specific access permissions"
    )
    rate_limit_multiplier: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Rate limit multiplier"
    )

    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def can_access_service(self, service_name: str, action: str = "read") -> bool:
        """Check if user can access a specific service."""
        if service_name not in self.service_access:
            return False
        return action in self.service_access[service_name]

    def is_therapeutic_user(self) -> bool:
        """Check if user has therapeutic permissions."""
        return (
            self.role in [UserRole.THERAPIST, UserRole.PATIENT]
            or self.therapeutic.can_access_sessions
        )


class AuthContext(BaseModel):
    """Authentication context for requests."""

    # User identification
    user_id: UUID = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str | None = Field(default=None, description="User email address")

    # Authentication details
    authenticated: bool = Field(default=False, description="Authentication status")
    auth_method: AuthenticationMethod = Field(
        ..., description="Authentication method used"
    )
    token_type: str = Field(default="Bearer", description="Token type")

    # User permissions and roles
    permissions: UserPermissions = Field(..., description="User permissions")

    # Session information
    session_id: str | None = Field(default=None, description="Session identifier")
    therapeutic_session_id: UUID | None = Field(
        default=None, description="Active therapeutic session ID"
    )

    # Security context
    client_ip: str = Field(..., description="Client IP address")
    user_agent: str = Field(default="unknown", description="Client user agent")
    mfa_verified: bool = Field(default=False, description="MFA verification status")

    # Timestamps
    authenticated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Authentication timestamp"
    )
    expires_at: datetime | None = Field(
        default=None, description="Token expiration timestamp"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow, description="Last activity timestamp"
    )

    # Therapeutic context
    in_therapeutic_session: bool = Field(
        default=False, description="Currently in therapeutic session"
    )
    crisis_mode: bool = Field(default=False, description="Crisis mode activated")
    safety_level: int = Field(
        default=1, ge=1, le=5, description="Safety monitoring level (1-5)"
    )

    # Additional context
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional authentication metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    def is_valid(self) -> bool:
        """Check if authentication context is valid."""
        if not self.authenticated:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        return True

    def is_therapeutic_context(self) -> bool:
        """Check if this is a therapeutic context."""
        return (
            self.in_therapeutic_session
            or self.therapeutic_session_id is not None
            or self.permissions.is_therapeutic_user()
        )

    def requires_elevated_permissions(self) -> bool:
        """Check if context requires elevated permissions."""
        return (
            self.crisis_mode
            or self.safety_level >= 4
            or self.permissions.therapeutic.can_handle_crisis
        )

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()


class AuthenticationRequest(BaseModel):
    """Authentication request model."""

    token: str = Field(..., description="Authentication token")
    token_type: str = Field(default="Bearer", description="Token type")
    client_ip: str = Field(..., description="Client IP address")
    user_agent: str = Field(default="unknown", description="Client user agent")
    service_name: str | None = Field(
        default=None, description="Requesting service name"
    )
    therapeutic_context: bool = Field(
        default=False, description="Request is in therapeutic context"
    )


class AuthenticationResponse(BaseModel):
    """Authentication response model."""

    success: bool = Field(..., description="Authentication success status")
    auth_context: AuthContext | None = Field(
        default=None, description="Authentication context if successful"
    )
    error: str | None = Field(default=None, description="Error message if failed")
    error_code: str | None = Field(default=None, description="Error code if failed")
    requires_mfa: bool = Field(default=False, description="Requires MFA verification")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class TokenValidationResult(BaseModel):
    """Token validation result."""

    valid: bool = Field(..., description="Token validity status")
    user_id: UUID | None = Field(default=None, description="User ID if valid")
    username: str | None = Field(default=None, description="Username if valid")
    permissions: UserPermissions | None = Field(
        default=None, description="User permissions if valid"
    )
    expires_at: datetime | None = Field(
        default=None, description="Token expiration if valid"
    )
    error: str | None = Field(default=None, description="Error message if invalid")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
