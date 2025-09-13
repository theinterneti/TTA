"""
Enhanced authentication router for the Player Experience API.

This module provides endpoints for user authentication, registration,
token management, multi-factor authentication, and role-based access control.
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ...database.user_auth_schema import UserAuthSchemaManager
from ...database.user_repository import UserRepository
from ...models.auth import (
    AuthenticatedUser,
    MFAChallenge,
    MFAConfig,
    MFAMethod,
    MFAVerification,
    PasswordReset,
    PasswordResetRequest,
    Permission,
    SecuritySettings,
    UserRegistration,
)
from ...services.auth_service import (
    AuthenticationError,
    AuthorizationError,
    EnhancedAuthService,
    MFAError,
)
from ..auth import (
    AuthService,
    LoginRequest,
    RefreshTokenRequest,
    Token,
    security,
)

router = APIRouter()

# Initialize enhanced auth service (in production, this would be dependency injected)
# Use the same JWT_SECRET_KEY as the rest of the authentication system for consistency
_AUTH_SECRET = os.getenv(
    "JWT_SECRET_KEY", "TTA_JWT_Secret_Key_Change_In_Production_2024!"
)
if not _AUTH_SECRET or _AUTH_SECRET == "your-secret-key-change-in-production":
    # Secure default behavior: use the same default as the main auth system
    _AUTH_SECRET = "TTA_JWT_Secret_Key_Change_In_Production_2024!"

# Initialize user repository and schema (with fallback for testing)
user_repository = None
try:
    # Try to initialize database components
    from ...api.config import get_settings

    settings = get_settings()

    # Setup user authentication schema
    schema_manager = UserAuthSchemaManager(
        uri=settings.neo4j_url,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
    schema_manager.connect()
    schema_manager.setup_user_auth_schema()
    schema_manager.disconnect()

    # Initialize user repository
    user_repository = UserRepository(
        uri=settings.neo4j_url,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
    user_repository.connect()

except Exception as e:
    # In development/testing, continue without database
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to initialize user database components: {e}")

auth_service = EnhancedAuthService(
    secret_key=_AUTH_SECRET,
    user_repository=user_repository,
    security_settings=SecuritySettings(),
    mfa_config=MFAConfig(enabled=True, email_enabled=True),
)


class LoginResponse(BaseModel):
    """Enhanced login response with MFA support."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: bool = False
    mfa_challenge: MFAChallenge | None = None
    user_info: dict[str, Any]


class MFASetupResponse(BaseModel):
    """MFA setup response model."""

    method: str
    secret: str | None = None
    qr_code: str | None = None
    backup_codes: list[str] | None = None


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_current_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthenticatedUser:
    """Get current authenticated user with enhanced validation."""
    try:
        return auth_service.verify_access_token(credentials.credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def require_permission(permission: Permission):
    """Dependency factory for permission-based access control."""

    def check_permission(
        user: AuthenticatedUser = Depends(get_current_authenticated_user),
    ) -> AuthenticatedUser:
        try:
            auth_service.require_permission(user, permission)
            return user
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
            ) from None

    return check_permission


def require_mfa_verification():
    """Dependency for requiring MFA verification."""

    def check_mfa(
        user: AuthenticatedUser = Depends(get_current_authenticated_user),
    ) -> AuthenticatedUser:
        try:
            auth_service.require_mfa_verification(user)
            return user
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
            ) from None

    return check_mfa


@router.post("/register", response_model=dict[str, Any])
async def register(registration: UserRegistration, request: Request) -> dict[str, Any]:
    """
    Register a new user account.

    Args:
        registration: User registration data
        request: HTTP request for IP tracking

    Returns:
        Dict with registration result

    Raises:
        HTTPException: If registration fails
    """
    try:
        success, errors = auth_service.register_user(registration)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Registration failed", "errors": errors},
            )

        return {
            "message": "User registered successfully",
            "username": registration.username,
            "email": registration.email,
            "role": registration.role.value,
        }

    except HTTPException as e:
        # Re-raise explicit HTTP errors without converting to 500
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        ) from None


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, request: Request) -> LoginResponse:
    """
    Authenticate a user and return access tokens with MFA support.

    Args:
        credentials: User login credentials
        request: HTTP request for IP tracking

    Returns:
        LoginResponse: Access tokens and MFA challenge if required

    Raises:
        HTTPException: If authentication fails
    """
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")

        # Convert LoginRequest to UserCredentials
        from ...models.auth import UserCredentials

        user_credentials = UserCredentials(
            username=credentials.username, password=credentials.password
        )

        # Authenticate user
        user = auth_service.authenticate_user(user_credentials, client_ip)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create session
        session_id = auth_service.create_session(user, client_ip, user_agent)

        # Check if MFA is required
        if user.mfa_enabled and not user.mfa_verified:
            # Create MFA challenge
            challenge = auth_service.mfa_service.create_mfa_challenge(
                user.user_id, MFAMethod.TOTP
            )

            return LoginResponse(
                access_token="",  # No token until MFA is completed
                refresh_token="",
                expires_in=0,
                mfa_required=True,
                mfa_challenge=challenge,
                user_info={
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role.value,
                },
            )

        # Create access token
        access_token = auth_service.create_access_token(user, session_id)

        return LoginResponse(
            access_token=access_token,
            refresh_token="",  # TODO: Implement refresh token
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            mfa_required=False,
            user_info={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": [perm.value for perm in user.permissions],
            },
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except HTTPException as e:
        # Preserve explicitly raised HTTP errors
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        ) from None


@router.post("/mfa/verify", response_model=LoginResponse)
async def verify_mfa(verification: MFAVerification, request: Request) -> LoginResponse:
    """
    Verify MFA challenge and complete authentication.

    Args:
        verification: MFA verification data
        request: HTTP request for IP tracking

    Returns:
        LoginResponse: Access tokens after successful MFA verification

    Raises:
        HTTPException: If MFA verification fails
    """
    try:
        # TODO: Get user's MFA secret from database
        # For now, we'll use a placeholder
        user_secrets = auth_service.mfa_secrets.get("user_id", [])
        if not user_secrets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA not set up for this user",
            )

        secret = user_secrets[0].secret  # Get TOTP secret

        # Verify MFA challenge
        is_valid = auth_service.mfa_service.verify_mfa_challenge(verification, secret)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
            )

        # TODO: Get user from database and create authenticated user
        # For now, return a placeholder response
        return LoginResponse(
            access_token="mfa_verified_token",
            refresh_token="",
            token_type="bearer",
            expires_in=1800,
            mfa_required=False,
            user_info={"message": "MFA verification successful"},
        )

    except MFAError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA verification failed: {str(e)}",
        ) from None


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    method: MFAMethod, user: AuthenticatedUser = Depends(get_current_authenticated_user)
) -> MFASetupResponse:
    """
    Set up multi-factor authentication for the current user.

    Args:
        method: MFA method to set up
        user: Current authenticated user

    Returns:
        MFASetupResponse: Setup information including QR code for TOTP

    Raises:
        HTTPException: If MFA setup fails
    """
    try:
        setup_info = auth_service.setup_mfa(user.user_id, method)

        return MFASetupResponse(
            method=method.value,
            secret=setup_info.get("secret"),
            qr_code=setup_info.get("qr_code"),
            backup_codes=setup_info.get("backup_codes"),
        )

    except MFAError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA setup failed: {str(e)}",
        ) from None


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshTokenRequest) -> Token:
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_request: The refresh token request

    Returns:
        Token: New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        return await AuthService.refresh_access_token(refresh_request.refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


@router.post("/logout")
async def logout(
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, str]:
    """
    Logout the current user and revoke their session.

    Args:
        user: The current authenticated user

    Returns:
        dict: Success message
    """
    try:
        # Revoke the user's session
        if user.session_id:
            auth_service.revoke_session(user.session_id)

        # Log security event
        from ...models.auth import SecurityEvent

        auth_service.log_security_event(
            SecurityEvent(
                event_type="user_logout",
                user_id=user.user_id,
                details={"username": user.username},
            )
        )

        return {"message": "Successfully logged out"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        ) from None


@router.post("/logout-all")
async def logout_all_sessions(
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, str]:
    """
    Logout from all sessions for the current user.

    Args:
        user: The current authenticated user

    Returns:
        dict: Success message
    """
    try:
        # Revoke all user sessions
        auth_service.revoke_all_user_sessions(user.user_id)

        # Log security event
        from ...models.auth import SecurityEvent

        auth_service.log_security_event(
            SecurityEvent(
                event_type="user_logout_all",
                user_id=user.user_id,
                details={"username": user.username},
            )
        )

        return {"message": "Successfully logged out from all sessions"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout all failed: {str(e)}",
        ) from None


@router.get("/me", response_model=dict[str, Any])
async def get_current_user_info(
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, Any]:
    """
    Get information about the current authenticated user.

    Args:
        user: The current authenticated user

    Returns:
        Dict: Current user information including role and permissions
    """
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "permissions": [perm.value for perm in user.permissions],
        "mfa_enabled": user.mfa_enabled,
        "mfa_verified": user.mfa_verified,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "session_id": user.session_id,
    }


@router.post("/verify-token")
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """
    Verify if a token is valid and return user information.

    Args:
        credentials: The HTTP authorization credentials

    Returns:
        dict: Token validity status and user information

    Raises:
        HTTPException: If token is invalid
    """
    try:
        user = auth_service.verify_access_token(credentials.credentials)
        return {
            "valid": True,
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [perm.value for perm in user.permissions],
            "mfa_verified": user.mfa_verified,
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


# Role-based access control endpoints
@router.get("/permissions")
async def get_user_permissions(
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, Any]:
    """
    Get current user's permissions.

    Args:
        user: Current authenticated user

    Returns:
        Dict: User permissions and role information
    """
    return {
        "role": user.role.value,
        "permissions": [perm.value for perm in user.permissions],
        "is_admin": user.is_admin(),
        "is_therapist": user.is_therapist(),
    }


@router.get("/roles", response_model=list[dict[str, Any]])
async def get_available_roles(
    user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_ROLES)),
) -> list[dict[str, Any]]:
    """
    Get all available roles and their permissions (admin only).

    Args:
        user: Current authenticated user (must have MANAGE_ROLES permission)

    Returns:
        List of roles with their permissions
    """
    from ...models.auth import DEFAULT_ROLE_PERMISSIONS

    return [
        {
            "role": role_perm.role.value,
            "description": role_perm.description,
            "permissions": [perm.value for perm in role_perm.permissions],
        }
        for role_perm in DEFAULT_ROLE_PERMISSIONS.values()
    ]


# Security and audit endpoints
@router.get("/security/events")
async def get_security_events(
    limit: int = 100,
    user: AuthenticatedUser = Depends(require_permission(Permission.ACCESS_AUDIT_LOGS)),
) -> list[dict[str, Any]]:
    """
    Get security events for audit purposes (admin only).

    Args:
        limit: Maximum number of events to return
        user: Current authenticated user (must have ACCESS_AUDIT_LOGS permission)

    Returns:
        List of security events
    """
    events = auth_service.security_events[-limit:]
    return [
        {
            "event_type": event.event_type,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "timestamp": event.timestamp.isoformat(),
            "details": event.details,
            "severity": event.severity,
        }
        for event in events
    ]


@router.get("/security/sessions")
async def get_active_sessions(
    user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_USERS)),
) -> list[dict[str, Any]]:
    """
    Get active sessions (admin only).

    Args:
        user: Current authenticated user (must have MANAGE_USERS permission)

    Returns:
        List of active sessions
    """
    return [
        {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "ip_address": session.ip_address,
            "is_active": session.is_active,
            "mfa_verified": session.mfa_verified,
        }
        for session in auth_service.active_sessions.values()
        if session.is_active
    ]


# Password management endpoints
@router.post("/password/reset-request")
async def request_password_reset(request_data: PasswordResetRequest) -> dict[str, str]:
    """
    Request a password reset for a user.

    Args:
        request_data: Password reset request data

    Returns:
        Dict: Success message
    """
    # TODO: Implement password reset email sending
    # For now, just return a success message

    # Log security event
    from ...models.auth import SecurityEvent

    auth_service.log_security_event(
        SecurityEvent(
            event_type="password_reset_requested", details={"email": request_data.email}
        )
    )

    return {"message": "Password reset email sent if account exists"}


@router.post("/password/reset")
async def reset_password(reset_data: PasswordReset) -> dict[str, str]:
    """
    Reset user password with token.

    Args:
        reset_data: Password reset data with token

    Returns:
        Dict: Success message
    """
    # TODO: Implement password reset token verification and password update
    # For now, just validate password strength

    is_valid, errors = auth_service.security_service.validate_password_strength(
        reset_data.new_password
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors},
        )

    return {"message": "Password reset successfully"}


@router.post("/password/change")
async def change_password(
    current_password: str,
    new_password: str,
    user: AuthenticatedUser = Depends(require_mfa_verification()),
) -> dict[str, str]:
    """
    Change user password (requires MFA verification for sensitive operation).

    Args:
        current_password: Current password
        new_password: New password
        user: Current authenticated user (must have MFA verified)

    Returns:
        Dict: Success message
    """
    # Validate new password strength
    is_valid, errors = auth_service.security_service.validate_password_strength(
        new_password
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors},
        )

    # TODO: Verify current password and update to new password in database

    # Log security event
    from ...models.auth import SecurityEvent

    auth_service.log_security_event(
        SecurityEvent(
            event_type="password_changed",
            user_id=user.user_id,
            details={"username": user.username},
        )
    )

    return {"message": "Password changed successfully"}


# OAuth 2.0 Endpoints for Dual Authentication System


@router.get("/oauth/providers", response_model=list[dict[str, Any]])
async def get_oauth_providers() -> list[dict[str, Any]]:
    """
    Get list of available OAuth providers.

    Returns:
        List of OAuth provider configurations
    """
    try:
        providers = auth_service.get_oauth_providers()
        return providers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth providers: {str(e)}",
        ) from None


@router.get("/oauth/{provider}/authorize", response_model=dict[str, str])
async def get_oauth_authorization_url(
    provider: str,
    interface_type: str = "patient",
    redirect_uri: str | None = None,
) -> dict[str, str]:
    """
    Get OAuth authorization URL for specified provider.

    Args:
        provider: OAuth provider (google, microsoft, apple, facebook)
        interface_type: Interface type (patient, clinical, admin)
        redirect_uri: Custom redirect URI (optional)

    Returns:
        Dict with authorization URL and state

    Raises:
        HTTPException: If provider is invalid or OAuth not available
    """
    try:
        auth_data = auth_service.get_oauth_authorization_url(
            provider, interface_type, redirect_uri
        )
        return auth_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}",
        ) from None


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request model."""

    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")
    interface_type: str = Field(default="patient", description="Interface type")


@router.post("/oauth/{provider}/callback", response_model=LoginResponse)
async def oauth_callback(
    provider: str,
    callback_data: OAuthCallbackRequest,
    request: Request,
) -> LoginResponse:
    """
    Handle OAuth callback and authenticate user.

    Args:
        provider: OAuth provider (google, microsoft, apple, facebook)
        callback_data: OAuth callback data with code and state
        request: HTTP request for IP tracking

    Returns:
        LoginResponse: Access tokens and user information

    Raises:
        HTTPException: If OAuth authentication fails
    """
    try:
        # Get client IP and user agent
        request.headers.get("user-agent", "unknown")

        # Authenticate with OAuth
        user = await auth_service.authenticate_with_oauth(
            provider,
            callback_data.code,
            callback_data.state,
            callback_data.interface_type,
        )

        # Create access token
        access_token = auth_service.create_access_token(user, user.session_id)

        return LoginResponse(
            access_token=access_token,
            refresh_token="",  # TODO: Implement OAuth refresh token
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            mfa_required=False,  # OAuth providers handle MFA
            user_info={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": [perm.value for perm in user.permissions],
                "authentication_method": "oauth",
                "oauth_provider": provider,
            },
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}",
        ) from None
