"""
Authentication utilities for the API Gateway.

This module provides utility functions for authentication, authorization,
and role-based access control.
"""

from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, Request, status

from ..models import AuthContext, PermissionLevel, UserRole


def require_auth(request: Request) -> AuthContext:
    """
    Require authentication for a request.

    Args:
        request: FastAPI request object

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated
    """
    auth_context = getattr(request.state, "auth_context", None)
    if not auth_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_context.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_context


def require_role(request: Request, required_roles: list[UserRole]) -> AuthContext:
    """
    Require specific user roles for a request.

    Args:
        request: FastAPI request object
        required_roles: List of required user roles

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated or insufficient role
    """
    auth_context = require_auth(request)

    if auth_context.permissions.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {[role.value for role in required_roles]}",
        )

    return auth_context


def require_permission(
    request: Request, required_permissions: list[PermissionLevel]
) -> AuthContext:
    """
    Require specific permissions for a request.

    Args:
        request: FastAPI request object
        required_permissions: List of required permissions

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated or insufficient permissions
    """
    auth_context = require_auth(request)

    user_permissions = set(auth_context.permissions.permissions)
    required_permissions_set = set(required_permissions)

    if not required_permissions_set.issubset(user_permissions):
        missing_permissions = required_permissions_set - user_permissions
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Missing: {[perm.value for perm in missing_permissions]}",
        )

    return auth_context


def require_therapeutic_access(request: Request) -> AuthContext:
    """
    Require therapeutic access for a request.

    Args:
        request: FastAPI request object

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated or no therapeutic access
    """
    auth_context = require_auth(request)

    if not auth_context.permissions.therapeutic.can_access_sessions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Therapeutic access required"
        )

    return auth_context


def require_crisis_access(request: Request) -> AuthContext:
    """
    Require crisis handling access for a request.

    Args:
        request: FastAPI request object

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated or no crisis access
    """
    auth_context = require_auth(request)

    if not auth_context.permissions.therapeutic.can_handle_crisis:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Crisis handling access required",
        )

    return auth_context


def require_service_access(
    request: Request, service_name: str, action: str = "read"
) -> AuthContext:
    """
    Require access to a specific service.

    Args:
        request: FastAPI request object
        service_name: Name of the service
        action: Required action (read, write, admin)

    Returns:
        AuthContext: Authentication context

    Raises:
        HTTPException: If not authenticated or no service access
    """
    auth_context = require_auth(request)

    if not auth_context.permissions.can_access_service(service_name, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access to service '{service_name}' with action '{action}' required",
        )

    return auth_context


def check_mfa_required(
    auth_context: AuthContext, sensitive_operation: bool = False
) -> bool:
    """
    Check if MFA is required for the current context.

    Args:
        auth_context: Authentication context
        sensitive_operation: Whether this is a sensitive operation

    Returns:
        bool: True if MFA is required
    """
    # MFA required for sensitive operations
    if sensitive_operation and not auth_context.mfa_verified:
        return True

    # MFA required for crisis mode
    if auth_context.crisis_mode and not auth_context.mfa_verified:
        return True

    # MFA required for high safety levels
    if auth_context.safety_level >= 4 and not auth_context.mfa_verified:
        return True

    return False


def get_user_context(request: Request) -> AuthContext | None:
    """
    Get user authentication context from request (if available).

    Args:
        request: FastAPI request object

    Returns:
        Optional[AuthContext]: Authentication context if available
    """
    return getattr(request.state, "auth_context", None)


def is_authenticated(request: Request) -> bool:
    """
    Check if request is authenticated.

    Args:
        request: FastAPI request object

    Returns:
        bool: True if authenticated
    """
    auth_context = get_user_context(request)
    return auth_context is not None and auth_context.is_valid()


def has_role(request: Request, role: UserRole) -> bool:
    """
    Check if user has a specific role.

    Args:
        request: FastAPI request object
        role: Required user role

    Returns:
        bool: True if user has the role
    """
    auth_context = get_user_context(request)
    return auth_context is not None and auth_context.permissions.role == role


def has_permission(request: Request, permission: PermissionLevel) -> bool:
    """
    Check if user has a specific permission.

    Args:
        request: FastAPI request object
        permission: Required permission

    Returns:
        bool: True if user has the permission
    """
    auth_context = get_user_context(request)
    return (
        auth_context is not None and permission in auth_context.permissions.permissions
    )


def is_therapeutic_user(request: Request) -> bool:
    """
    Check if user is in a therapeutic context.

    Args:
        request: FastAPI request object

    Returns:
        bool: True if user is in therapeutic context
    """
    auth_context = get_user_context(request)
    return auth_context is not None and auth_context.is_therapeutic_context()


def get_rate_limit_multiplier(request: Request) -> float:
    """
    Get rate limit multiplier for the user.

    Args:
        request: FastAPI request object

    Returns:
        float: Rate limit multiplier
    """
    auth_context = get_user_context(request)
    if auth_context:
        return auth_context.permissions.rate_limit_multiplier
    return 1.0


# Decorator functions for FastAPI dependencies
def auth_required(func: Callable) -> Callable:
    """
    Decorator to require authentication for a route.

    Args:
        func: Route function

    Returns:
        Callable: Decorated function
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request from args/kwargs
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request is None:
            request = kwargs.get("request")

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object not found",
            )

        # Require authentication
        require_auth(request)

        return await func(*args, **kwargs)

    return wrapper


def role_required(*roles: UserRole):
    """
    Decorator to require specific roles for a route.

    Args:
        roles: Required user roles

    Returns:
        Callable: Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                request = kwargs.get("request")

            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found",
                )

            # Require roles
            require_role(request, list(roles))

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def get_websocket_auth_context(token: str) -> AuthContext | None:
    """
    Get authentication context for WebSocket connections.

    Args:
        token: JWT token

    Returns:
        AuthContext if token is valid
    """
    try:
        # This would integrate with your JWT validation service
        # For now, return None to indicate authentication integration needed
        # TODO: Implement JWT token validation for WebSocket connections
        return None
    except Exception as e:
        logger.error(f"Error validating WebSocket token: {e}")
        return None
