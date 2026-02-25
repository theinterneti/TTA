"""

# Logseq: [[TTA.dev/Player_experience/Api/Routers/Auth]]
Enhanced authentication router for the Player Experience API.

This module provides endpoints for user authentication, registration,
token management, multi-factor authentication, and role-based access control.
"""

import contextlib
import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from ...database.user_repository import UserRepository
from ...managers.player_profile_manager import (
    PlayerProfileManager,
    PlayerProfileManagerError,
)
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
    UserRole,
)
from ...models.player import PlayerProfile
from ...services.auth_service import (
    AuthenticationError,
    AuthorizationError,
    EnhancedAuthService,
    MFAError,
)
from ..auth import (
    SECRET_KEY,
    AuthService,
    LoginRequest,
    RefreshTokenRequest,
    Token,
    _get_token_cache,
    security,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize user repository with fallback
user_repository = None
try:
    from ..config import get_settings

    settings = get_settings()
    user_repository = UserRepository(
        uri=settings.neo4j_uri,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
    user_repository.connect()
    logger.info("✅ UserRepository connected successfully")
except Exception as e:
    logger.warning(f"⚠️ UserRepository connection failed: {e}. Using Redis fallback.")
    # Create a simple Redis-based user repository as fallback
    try:
        from datetime import datetime

        import redis

        from ...database.user_repository import User

        class RedisUserRepository:
            def __init__(self):
                from ..config import get_settings

                settings = get_settings()
                # Parse Redis URL to get connection details
                import urllib.parse

                parsed = urllib.parse.urlparse(settings.redis_url)
                self.redis_client = redis.Redis(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 6379,
                    password=parsed.password,
                    decode_responses=True,
                )
                self.redis_client.ping()  # Test connection

            def create_user(
                self,
                username: str,
                email: str,
                password_hash: str,
                role=UserRole.PLAYER,
            ):
                user_id = str(__import__("uuid").uuid4())
                user_data = {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "role": role.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": "true",  # Convert boolean to string for Redis
                }

                # Store user data
                self.redis_client.hset(f"user:{user_id}", mapping=user_data)
                self.redis_client.set(f"username:{username}", user_id)
                self.redis_client.set(f"email:{email}", user_id)

                return User(
                    user_id, username, email, password_hash, role, datetime.utcnow()
                )

            def get_user_by_username(self, username: str):
                user_id = self.redis_client.get(f"username:{username}")
                if not user_id:
                    return None

                user_data: dict[str, str] = self.redis_client.hgetall(f"user:{user_id}")  # type: ignore[assignment]
                if not user_data:
                    return None

                return User(
                    user_data["user_id"],
                    user_data["username"],
                    user_data["email"],
                    user_data["password_hash"],
                    UserRole(user_data["role"]),
                    datetime.fromisoformat(user_data["created_at"]),
                )

            def username_exists(self, username: str) -> bool:
                return bool(self.redis_client.exists(f"username:{username}"))

            def email_exists(self, email: str) -> bool:
                return bool(self.redis_client.exists(f"email:{email}"))

            def update_last_login(self, user_id: str) -> bool:
                result = self.redis_client.hset(
                    f"user:{user_id}", "last_login", datetime.utcnow().isoformat()
                )
                return bool(result)

        user_repository = RedisUserRepository()
        logger.info("✅ Redis UserRepository fallback initialized")

    except Exception as redis_error:
        logger.error(
            f"❌ Redis fallback also failed: {redis_error}. Authentication will use in-memory storage."
        )

# Initialize enhanced auth service (in production, this would be dependency injected)
# Use the same secret key as the middleware to ensure token compatibility
_AUTH_SECRET = SECRET_KEY

auth_service = EnhancedAuthService(
    secret_key=_AUTH_SECRET,
    user_repository=user_repository,
    security_settings=SecuritySettings(),
    mfa_config=MFAConfig(enabled=True, email_enabled=True),
)


# Dependency to get player profile manager
def get_player_manager() -> PlayerProfileManager:
    """
    Get player profile manager instance for auto-creating player profiles.

    Uses the same repository pattern as the players router to ensure consistency.
    """

    # Prefer Neo4j repository if configured
    use_neo4j = os.getenv("TTA_USE_NEO4J", "0") == "1"
    if use_neo4j:
        with contextlib.suppress(Exception):
            from ...database.player_profile_repository import PlayerProfileRepository
            from ...managers.player_profile_manager import create_player_profile_manager
            from ..config import get_settings

            settings = get_settings()
            repository = PlayerProfileRepository(
                uri=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
            )
            repository.connect()
            return create_player_profile_manager(repository)

    # Fallback to in-memory repository for testing/development
    from ...managers.player_profile_manager import create_player_profile_manager

    class _InMemoryPlayerRepo:
        """In-memory player profile repository for testing."""

        def __init__(self):
            self.profiles = {}

        def username_exists(self, username: str) -> bool:
            return any(p.username == username for p in self.profiles.values())

        def email_exists(self, email: str) -> bool:
            return any(p.email == email for p in self.profiles.values())

        def create_player_profile(self, profile: PlayerProfile) -> bool:
            self.profiles[profile.player_id] = profile
            return True

        def get_player_profile(self, player_id: str) -> PlayerProfile | None:
            return self.profiles.get(player_id)

    repository = _InMemoryPlayerRepo()  # type: ignore
    return create_player_profile_manager(repository)  # type: ignore[arg-type]


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
            ) from e

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
            ) from e

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
        raise e from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        ) from e


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    player_manager: PlayerProfileManager = Depends(get_player_manager),
) -> LoginResponse:
    """
    Authenticate a user and return access tokens with MFA support.

    Automatically creates a player profile for new users on first successful login.
    The player_id is included in the JWT token for downstream authentication.

    Args:
        credentials: User login credentials
        request: HTTP request for IP tracking
        response: HTTP response for setting cookies
        player_manager: Player profile manager dependency

    Returns:
        LoginResponse: Access tokens and MFA challenge if required

    Raises:
        HTTPException: If authentication fails
    """
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")

        # Authenticate user - convert LoginRequest to UserCredentials
        from ...models.auth import UserCredentials

        user_creds = UserCredentials(
            username=credentials.username, password=credentials.password
        )
        user = auth_service.authenticate_user(user_creds, client_ip)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Auto-create player profile if it doesn't exist (Issue #4 fix)
        # This ensures every authenticated user has a player profile with a player_id
        player_id = user.user_id  # Default: player_id matches user_id
        autocreation_start_time = None
        autocreation_success = False
        autocreation_error_category = None

        try:
            logger.debug(
                f"Checking if player profile exists for user_id={user.user_id}"
            )
            # Check if player profile already exists
            existing_profile = player_manager.get_player_profile(user.user_id)
            if existing_profile:
                player_id = existing_profile.player_id
                logger.debug(f"Found existing player profile: {player_id}")
            else:
                # Create new player profile for first-time login
                import time

                autocreation_start_time = time.time()
                logger.debug(f"Creating new player profile for user {user.username}")

                new_profile = player_manager.create_player_profile(
                    username=user.username,
                    email=user.email,
                    player_id=user.user_id,  # Use user_id as player_id for consistency
                )
                player_id = new_profile.player_id
                autocreation_success = True
                logger.debug(
                    f"Auto-created player profile for user {user.username} (player_id: {player_id})"
                )
        except PlayerProfileManagerError as profile_error:
            # Log error but don't block login - player_id will default to user_id
            autocreation_error_category = "profile_manager_error"
            logger.error(
                f"Failed to auto-create player profile for {user.username}: {profile_error}",
                exc_info=True,
            )
            # Continue with login using user_id as player_id
        except Exception as e:
            autocreation_error_category = "unexpected_error"
            logger.error(
                f"Unexpected error during player profile auto-creation: {e}",
                exc_info=True,
            )
        # Auto-initialize default character and world for new players (Issue #60)
        try:
            from ...services.default_character_world_service import (
                DefaultCharacterWorldService,
            )

            default_service = DefaultCharacterWorldService()
            character_id, world_id, session_id = (
                default_service.initialize_default_character_and_world(player_id)
            )
            if character_id:
                logger.debug(
                    f"Auto-initialized default character {character_id}, world {world_id}, and session {session_id} for player {player_id}"
                )
        except Exception as e:
            logger.warning(
                f"Failed to auto-initialize default character/world for player {player_id}: {e}",
                exc_info=True,
            )
            # Don't block login if character/world initialization fails

        finally:
            # Record player profile auto-creation metrics
            if autocreation_start_time is not None:
                duration = time.time() - autocreation_start_time
                try:
                    from src.monitoring.prometheus_metrics import get_metrics_collector

                    collector = get_metrics_collector("player-experience")
                    collector.record_player_profile_autocreation(
                        trigger="first_login",
                        success=autocreation_success,
                        duration=duration,
                        error_category=autocreation_error_category,
                    )
                except Exception as metrics_error:
                    logger.debug(
                        f"Failed to record auto-creation metrics: {metrics_error}"
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

        # Create access token with player_id (Issue #4 fix)
        access_token = auth_service.create_access_token(
            user, session_id, player_id=player_id
        )

        # Create a Redis session for session persistence
        # This allows the session to persist across page refreshes
        import os

        import redis.asyncio as aioredis

        from ..session_manager import RedisSessionManager

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            logger.debug(f"Attempting to create Redis session with URL: {redis_url}")
            redis_client = aioredis.from_url(redis_url, decode_responses=True)
            session_manager = RedisSessionManager(redis_client)

            # Create a session with user data
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": [perm.value for perm in user.permissions],
            }

            # Create session in Redis
            logger.debug(f"Creating Redis session for user: {user.user_id}")
            redis_session_id = await session_manager.create_session(
                user_data=user_data, auth_method="standard"
            )
            logger.debug(f"Redis session created: {redis_session_id}")

            # Set secure session cookie for session persistence
            is_production = os.getenv("ENVIRONMENT", "development") == "production"
            logger.debug(f"Setting session cookie (secure={is_production})")
            response.set_cookie(
                key="openrouter_session_id",
                value=redis_session_id,
                httponly=True,
                secure=is_production,  # Only require HTTPS in production
                samesite="lax",
                max_age=86400,  # 24 hours
                path="/",  # Ensure cookie is sent for all paths
            )
            logger.debug("Session cookie set successfully")
        except Exception as e:
            logger.error(f"Failed to create Redis session: {e}", exc_info=True)
            # Continue without Redis session - the JWT token will still work

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
        ) from e
    except HTTPException as e:
        # Preserve explicitly raised HTTP errors
        raise e from e
    except Exception as e:
        logger.error(f"Login endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        ) from e


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
        ) from e
    except HTTPException as e:
        raise e from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA verification failed: {str(e)}",
        ) from e


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
        ) from e
    except HTTPException as e:
        raise e from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA setup failed: {str(e)}",
        ) from e


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
        ) from e


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, str]:
    """
    Logout the current user and revoke their session.

    Args:
        credentials: Raw HTTP Bearer credentials (used to invalidate Redis cache)
        user: The current authenticated user

    Returns:
        dict: Success message
    """
    try:
        # Evict token from Redis cache so subsequent requests are rejected immediately
        cache = _get_token_cache()
        if cache is not None:
            await cache.delete(credentials.credentials)

        # Revoke the user's session
        if user.session_id:
            auth_service.revoke_session(user.session_id)

        # Log security event
        from models.auth import SecurityEvent

        auth_service.log_security_event(
            SecurityEvent(
                event_type="user_logout",
                user_id=user.user_id,
                details={"username": user.username},
            )
        )

        return {"message": "Successfully logged out"}

    except HTTPException as e:
        raise e from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        ) from e


@router.post("/logout-all")
async def logout_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: AuthenticatedUser = Depends(get_current_authenticated_user),
) -> dict[str, str]:
    """
    Logout from all sessions for the current user.

    Args:
        credentials: Raw HTTP Bearer credentials (used to invalidate Redis cache)
        user: The current authenticated user

    Returns:
        dict: Success message
    """
    try:
        # Evict the current token from Redis cache immediately
        cache = _get_token_cache()
        if cache is not None:
            await cache.delete(credentials.credentials)

        # Revoke all user sessions
        auth_service.revoke_all_user_sessions(user.user_id)

        # Log security event
        from models.auth import SecurityEvent

        auth_service.log_security_event(
            SecurityEvent(
                event_type="user_logout_all",
                user_id=user.user_id,
                details={"username": user.username},
            )
        )

        return {"message": "Successfully logged out from all sessions"}

    except HTTPException as e:
        raise e from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout all failed: {str(e)}",
        ) from e


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
        ) from e


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
    from models.auth import DEFAULT_ROLE_PERMISSIONS

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
    from models.auth import SecurityEvent

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
    from models.auth import SecurityEvent

    auth_service.log_security_event(
        SecurityEvent(
            event_type="password_changed",
            user_id=user.user_id,
            details={"username": user.username},
        )
    )

    return {"message": "Password changed successfully"}
