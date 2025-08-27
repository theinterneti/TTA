"""
Utility functions and helpers for the API Gateway system.

This module contains utility functions, helpers, and common functionality
used throughout the API Gateway system.
"""

# Authentication utilities
from .auth_utils import (
    require_auth,
    require_role,
    require_permission,
    require_therapeutic_access,
    require_crisis_access,
    require_service_access,
    check_mfa_required,
    get_user_context,
    is_authenticated,
    has_role,
    has_permission,
    is_therapeutic_user,
    get_rate_limit_multiplier,
    auth_required,
    role_required,
)

__all__ = [
    "require_auth",
    "require_role",
    "require_permission",
    "require_therapeutic_access",
    "require_crisis_access",
    "require_service_access",
    "check_mfa_required",
    "get_user_context",
    "is_authenticated",
    "has_role",
    "has_permission",
    "is_therapeutic_user",
    "get_rate_limit_multiplier",
    "auth_required",
    "role_required",
]
