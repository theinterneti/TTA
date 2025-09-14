"""
Unified Authentication Router

FastAPI router for the consolidated TTA authentication system that serves all interfaces
with consistent authentication endpoints and HIPAA-compliant audit logging.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...services.unified_auth.models import (
    AuthTokens,
    LoginCredentials,
    LoginResponse,
    UnifiedUser,
)
from ...services.unified_auth.unified_auth_service import UnifiedAuthService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer()

# Initialize auth service (in production, this would be dependency injected)
auth_service = UnifiedAuthService(
    secret_key="your-secret-key-here"  # In production, use environment variable
)


async def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> tuple[UnifiedUser, str]:
    """
    Dependency to get current authenticated user from token.
    Returns user and session_id.
    """
    try:
        token = credentials.credentials
        user, session = await auth_service.validate_access_token(token)

        # Log access for audit
        ip_address = request.client.host if request.client else None
        auth_service.audit_logger.log_authentication_event(
            user.id,
            user.username,
            "api_access",
            True,
            session.interface_type,
            ip_address,
            session.session_id,
        )

        return user, session.session_id

    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginCredentials, request: Request):
    """
    Universal login endpoint for all TTA interfaces.

    Authenticates user credentials and returns user data with JWT tokens.
    Supports interface-specific access control and session management.
    """
    try:
        ip_address = request.client.host if request.client else None

        # Perform login
        login_response = await auth_service.login(credentials, ip_address)

        logger.info(
            f"Successful login: {credentials.username} -> {credentials.interface_type.value}"
        )

        return login_response

    except Exception as e:
        logger.warning(f"Login failed for {credentials.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.post("/refresh", response_model=AuthTokens)
async def refresh_token(refresh_token_data: dict, request: Request):
    """
    Refresh access token using refresh token.

    Validates refresh token and generates new access and refresh tokens.
    """
    try:
        refresh_token = refresh_token_data.get("refreshToken")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required",
            )

        # Refresh tokens
        new_tokens = await auth_service.refresh_token(refresh_token)

        logger.info("Token refresh successful")

        return new_tokens

    except Exception as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from e


@router.post("/logout")
async def logout(
    logout_data: dict,
    request: Request,
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Logout user and invalidate session.

    Invalidates the current session and logs the logout event.
    """
    try:
        user, session_id = current_user_data

        # Use session_id from logout data if provided, otherwise use current session
        logout_session_id = logout_data.get("sessionId", session_id)

        await auth_service.logout(logout_session_id, user.id)

        logger.info(f"User logged out: {user.username}")

        return {"message": "Logout successful"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        ) from e


@router.get("/profile", response_model=UnifiedUser)
async def get_profile(
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Get current user profile.

    Returns the authenticated user's profile information.
    """
    user, _ = current_user_data
    return user


@router.put("/profile", response_model=UnifiedUser)
async def update_profile(
    profile_updates: dict,
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Update user profile.

    Updates the authenticated user's profile information.
    """
    try:
        user, session_id = current_user_data

        # Update profile fields
        if "firstName" in profile_updates:
            user.profile.first_name = profile_updates["firstName"]
        if "lastName" in profile_updates:
            user.profile.last_name = profile_updates["lastName"]
        if "organization" in profile_updates:
            user.profile.organization = profile_updates["organization"]

        # In production, save to database
        # For now, just return updated user

        logger.info(f"Profile updated for user: {user.username}")

        return user

    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        ) from e


@router.get("/session")
async def get_session_info(
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Get current session information.

    Returns information about the current user session.
    """
    try:
        user, session_id = current_user_data

        # Get session from session manager
        session = auth_service.session_manager.active_sessions.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        return {
            "sessionId": session.session_id,
            "userId": session.user_id,
            "interfaceType": session.interface_type.value,
            "createdAt": session.created_at.isoformat(),
            "lastActivity": session.last_activity.isoformat(),
            "expiresAt": session.expires_at.isoformat(),
            "isActive": session.is_active,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session info",
        ) from e


@router.post("/extend-session")
async def extend_session(
    session_data: dict,
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Extend current session expiration.

    Extends the session timeout for the current user.
    """
    try:
        user, current_session_id = current_user_data

        # Use provided session_id or current session
        session_id = session_data.get("sessionId", current_session_id)

        # Extend session
        extended_session = auth_service.session_manager.extend_session(session_id)

        logger.info(f"Session extended for user: {user.username}")

        return {
            "message": "Session extended successfully",
            "expiresAt": extended_session.expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Session extension error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extend session",
        ) from e


@router.get("/permissions")
async def get_user_permissions(
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Get current user's permissions and interface access.

    Returns the user's role, permissions, and interface access rights.
    """
    user, _ = current_user_data

    return {
        "userId": user.id,
        "username": user.username,
        "role": user.role.value,
        "permissions": [p.value for p in user.permissions],
        "interfaceAccess": [i.value for i in user.interface_access],
        "mfaEnabled": user.mfa_enabled,
        "mfaVerified": user.mfa_verified,
    }


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    current_user_data: tuple[UnifiedUser, str] = Depends(get_current_user),
):
    """
    Get audit logs (admin only).

    Returns recent audit log entries for HIPAA compliance.
    Requires admin permissions.
    """
    user, _ = current_user_data

    # Check admin permission
    from ...services.unified_auth.models import Permission

    if not auth_service.has_permission(user, Permission.VIEW_AUDIT_LOGS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit logs",
        )

    # Get recent audit logs
    recent_logs = auth_service.audit_logger.audit_logs[-limit:]

    return {
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "userId": log.user_id,
                "username": log.username,
                "action": log.action,
                "resource": log.resource,
                "interfaceType": (
                    log.interface_type.value if log.interface_type else None
                ),
                "success": log.success,
                "ipAddress": log.ip_address,
                "sessionId": log.session_id,
            }
            for log in recent_logs
        ],
        "total": len(recent_logs),
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for authentication service.

    Returns the health status of the authentication service.
    """
    return {
        "status": "healthy",
        "service": "unified_auth_service",
        "timestamp": "2024-12-01T00:00:00Z",
        "activeSessions": len(auth_service.session_manager.active_sessions),
        "auditLogEntries": len(auth_service.audit_logger.audit_logs),
    }
