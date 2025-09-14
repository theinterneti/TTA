"""
Unified Authentication Service

Consolidated authentication system for all TTA interfaces with clinical-grade
security, HIPAA compliance, and consistent user experience.
"""

from .models import (
    AuthenticationError,
    AuthorizationError,
    AuthTokens,
    InterfaceType,
    LoginCredentials,
    LoginResponse,
    Permission,
    SessionExpiredError,
    SessionInfo,
    UnifiedUser,
    UserProfile,
    UserRole,
)
from .unified_auth_service import UnifiedAuthService

__all__ = [
    # Core service
    "UnifiedAuthService",
    # Models
    "UnifiedUser",
    "UserProfile",
    "UserRole",
    "InterfaceType",
    "Permission",
    "AuthTokens",
    "LoginCredentials",
    "LoginResponse",
    "SessionInfo",
    # Exceptions
    "AuthenticationError",
    "AuthorizationError",
    "SessionExpiredError",
]
