"""
Authentication middleware for the API Gateway.

This middleware integrates with the TTA authentication system to provide
JWT token validation, user context extraction, and role-based access control.
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_gateway_settings
from ..models import (
    AuthContext,
    AuthenticationMethod,
    PermissionLevel,
    TherapeuticPermission,
    UserPermissions,
    UserRole,
)

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication and user context management.

    Integrates with the completed TTA authentication system to:
    - Validate JWT tokens
    - Extract user context and roles
    - Handle token refresh
    - Manage therapeutic permissions
    """

    def __init__(self, app):
        super().__init__(app)
        self.settings = get_gateway_settings()
        self._auth_service = None
        self._public_paths = {
            "/",
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
        self._auth_optional_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/reset-password",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with authentication validation.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response from the next handler
        """
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Extract and validate authentication
        auth_context = await self._authenticate_request(request)

        # Handle authentication failure
        if not auth_context and not self._is_auth_optional_path(request.url.path):
            return self._create_auth_error_response("Authentication required")

        # Set authentication context in request state
        if auth_context:
            request.state.auth_context = auth_context
            request.state.user_id = auth_context.user_id
            request.state.username = auth_context.username
            request.state.user_role = auth_context.permissions.role
            request.state.is_therapeutic_context = auth_context.is_therapeutic_context()

            # Log authentication success
            logger.info(
                f"Authenticated user {auth_context.username} ({auth_context.user_id}) "
                f"for {request.method} {request.url.path}",
                extra={
                    "correlation_id": getattr(
                        request.state, "correlation_id", "unknown"
                    ),
                    "user_id": str(auth_context.user_id),
                    "username": auth_context.username,
                    "role": auth_context.permissions.role.value,
                    "therapeutic_context": auth_context.is_therapeutic_context(),
                    "event_type": "authentication_success",
                },
            )

        # Process request
        response = await call_next(request)

        # Update authentication context activity if present
        if auth_context:
            auth_context.update_activity()

        return response

    async def _authenticate_request(self, request: Request) -> AuthContext | None:
        """
        Authenticate the request and return authentication context.

        Args:
            request: The incoming request

        Returns:
            Optional[AuthContext]: Authentication context if successful
        """
        try:
            # Extract token from Authorization header
            token = self._extract_token(request)
            if not token:
                return None

            # Validate token using TTA authentication system
            user_data = await self._validate_token(token)
            if not user_data:
                return None

            # Create authentication context
            auth_context = self._create_auth_context(request, user_data, token)

            return auth_context

        except Exception as e:
            logger.warning(
                f"Authentication failed for {request.method} {request.url.path}: {e}",
                extra={
                    "correlation_id": getattr(
                        request.state, "correlation_id", "unknown"
                    ),
                    "client_ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "error": str(e),
                    "event_type": "authentication_failure",
                },
            )
            return None

    def _extract_token(self, request: Request) -> str | None:
        """
        Extract JWT token from request headers.

        Args:
            request: The incoming request

        Returns:
            Optional[str]: JWT token if found
        """
        # Check Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1]

        # Check query parameter (for WebSocket connections)
        token = request.query_params.get("token")
        if token:
            return token

        return None

    async def _validate_token(self, token: str) -> dict | None:
        """
        Validate JWT token using TTA authentication system.

        Args:
            token: JWT token to validate

        Returns:
            Optional[dict]: User data if token is valid
        """
        try:
            # Import TTA authentication components
            from src.player_experience.services.auth_service import AuthService

            # Initialize auth service if not already done
            if self._auth_service is None:
                self._auth_service = AuthService()

            # Verify token
            authenticated_user = self._auth_service.verify_access_token(token)

            # Convert to dictionary format
            return {
                "user_id": authenticated_user.user_id,
                "username": authenticated_user.username,
                "email": authenticated_user.email,
                "role": authenticated_user.role,
                "permissions": authenticated_user.permissions,
                "session_id": authenticated_user.session_id,
                "mfa_verified": authenticated_user.mfa_verified,
            }

        except Exception as e:
            logger.debug(f"Token validation failed: {e}")
            return None

    def _create_auth_context(
        self, request: Request, user_data: dict, token: str
    ) -> AuthContext:
        """
        Create authentication context from validated user data.

        Args:
            request: The incoming request
            user_data: Validated user data from token
            token: Original JWT token

        Returns:
            AuthContext: Authentication context
        """
        from datetime import datetime, timezone
        from uuid import UUID

        # Convert TTA user role to gateway user role
        tta_role = user_data["role"]
        gateway_role = self._convert_tta_role_to_gateway_role(tta_role)

        # Convert TTA permissions to gateway permissions
        tta_permissions = user_data.get("permissions", [])
        gateway_permissions = self._convert_tta_permissions_to_gateway_permissions(
            tta_permissions, tta_role
        )

        # Create user permissions
        user_permissions = UserPermissions(
            role=gateway_role,
            permissions=gateway_permissions.permissions,
            therapeutic=gateway_permissions.therapeutic,
            service_access=gateway_permissions.service_access,
            rate_limit_multiplier=gateway_permissions.rate_limit_multiplier,
        )

        # Determine if this is a therapeutic context
        is_therapeutic = (
            gateway_role in [UserRole.PATIENT, UserRole.THERAPIST]
            or user_permissions.therapeutic.can_access_sessions
        )

        # Create authentication context
        auth_context = AuthContext(
            user_id=UUID(user_data["user_id"]),
            username=user_data["username"],
            email=user_data.get("email"),
            authenticated=True,
            auth_method=AuthenticationMethod.JWT,
            token_type="Bearer",
            permissions=user_permissions,
            session_id=user_data.get("session_id"),
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent", "unknown"),
            mfa_verified=user_data.get("mfa_verified", False),
            authenticated_at=datetime.now(timezone.utc),
            in_therapeutic_session=is_therapeutic,
            safety_level=self._determine_safety_level(gateway_role, is_therapeutic),
            metadata={
                "original_token": token,
                "gateway_version": "1.0.0",
                "auth_source": "tta_player_experience",
            },
        )

        return auth_context

    def _convert_tta_role_to_gateway_role(self, tta_role) -> UserRole:
        """
        Convert TTA user role to gateway user role.

        Args:
            tta_role: TTA UserRole enum value

        Returns:
            UserRole: Gateway user role
        """
        # Import TTA UserRole for comparison
        from src.player_experience.models.auth import UserRole as TTAUserRole

        role_mapping = {
            TTAUserRole.PLAYER: UserRole.PATIENT,
            TTAUserRole.THERAPIST: UserRole.THERAPIST,
            TTAUserRole.ADMIN: UserRole.ADMIN,
            TTAUserRole.RESEARCHER: UserRole.ADMIN,  # Map to admin for now
            TTAUserRole.MODERATOR: UserRole.ADMIN,  # Map to admin for now
        }

        return role_mapping.get(tta_role, UserRole.GUEST)

    def _convert_tta_permissions_to_gateway_permissions(
        self, tta_permissions: list, tta_role
    ) -> UserPermissions:
        """
        Convert TTA permissions to gateway permissions.

        Args:
            tta_permissions: List of TTA Permission enum values
            tta_role: TTA UserRole enum value

        Returns:
            UserPermissions: Gateway user permissions
        """
        from src.player_experience.models.auth import Permission as TTAPermission
        from src.player_experience.models.auth import UserRole as TTAUserRole

        # Convert to gateway permission levels
        gateway_permissions = []

        # Basic permissions mapping
        if any(
            perm in tta_permissions
            for perm in [
                TTAPermission.CREATE_CHARACTER,
                TTAPermission.MANAGE_OWN_CHARACTERS,
                TTAPermission.MANAGE_OWN_PROFILE,
            ]
        ):
            gateway_permissions.append(PermissionLevel.WRITE)
        else:
            gateway_permissions.append(PermissionLevel.READ)

        # Therapeutic permissions
        therapeutic_permissions = TherapeuticPermission()

        if TTAPermission.ACCESS_THERAPEUTIC_CONTENT in tta_permissions:
            therapeutic_permissions.can_access_sessions = True

        if TTAPermission.VIEW_PATIENT_PROGRESS in tta_permissions:
            therapeutic_permissions.can_view_progress = True
            therapeutic_permissions.can_access_sensitive_data = True

        if TTAPermission.MANAGE_THERAPEUTIC_CONTENT in tta_permissions:
            therapeutic_permissions.can_modify_treatment = True

        if TTAPermission.ACCESS_CRISIS_PROTOCOLS in tta_permissions:
            therapeutic_permissions.can_handle_crisis = True
            gateway_permissions.append(PermissionLevel.CRISIS)

        # Admin permissions
        if any(
            perm in tta_permissions
            for perm in [
                TTAPermission.MANAGE_USERS,
                TTAPermission.MANAGE_SYSTEM_SETTINGS,
                TTAPermission.VIEW_SYSTEM_LOGS,
            ]
        ):
            gateway_permissions.append(PermissionLevel.ADMIN)

        # Therapeutic permission level
        if therapeutic_permissions.can_access_sessions:
            gateway_permissions.append(PermissionLevel.THERAPEUTIC)

        # Service access mapping
        service_access = {}

        if tta_role == TTAUserRole.PLAYER:
            service_access = {
                "player-experience-interface": ["read", "write"],
                "core-gameplay-loop": ["read", "write"],
                "authentication-service": ["read"],
            }
        elif tta_role == TTAUserRole.THERAPIST:
            service_access = {
                "player-experience-interface": ["read", "write"],
                "core-gameplay-loop": ["read", "write", "admin"],
                "authentication-service": ["read"],
                "agent-orchestration": ["read", "write"],
            }
        elif tta_role in [
            TTAUserRole.ADMIN,
            TTAUserRole.RESEARCHER,
            TTAUserRole.MODERATOR,
        ]:
            service_access = {
                "player-experience-interface": ["read", "write", "admin"],
                "core-gameplay-loop": ["read", "write", "admin"],
                "authentication-service": ["read", "write", "admin"],
                "agent-orchestration": ["read", "write", "admin"],
            }

        # Rate limit multiplier based on role
        rate_limit_multiplier = 1.0
        if tta_role == TTAUserRole.THERAPIST:
            rate_limit_multiplier = 2.0  # Higher limits for therapists
        elif tta_role in [TTAUserRole.ADMIN, TTAUserRole.RESEARCHER]:
            rate_limit_multiplier = 3.0  # Highest limits for admins

        # Supervision requirements
        if tta_role == TTAUserRole.PLAYER:
            therapeutic_permissions.supervision_required = True
        elif tta_role == TTAUserRole.THERAPIST:
            therapeutic_permissions.supervision_required = False

        return UserPermissions(
            role=self._convert_tta_role_to_gateway_role(tta_role),
            permissions=list(set(gateway_permissions)),  # Remove duplicates
            therapeutic=therapeutic_permissions,
            service_access=service_access,
            rate_limit_multiplier=rate_limit_multiplier,
        )

    def _determine_safety_level(self, role: UserRole, is_therapeutic: bool) -> int:
        """
        Determine safety monitoring level based on role and context.

        Args:
            role: User role
            is_therapeutic: Whether in therapeutic context

        Returns:
            int: Safety level (1-5)
        """
        if role == UserRole.PATIENT and is_therapeutic:
            return 4  # High monitoring for patients in therapeutic sessions
        elif role == UserRole.PATIENT:
            return 3  # Medium-high monitoring for patients
        elif role == UserRole.THERAPIST:
            return 2  # Medium monitoring for therapists
        elif role == UserRole.ADMIN:
            return 1  # Low monitoring for admins
        else:
            return 3  # Default medium-high for unknown roles

    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public and doesn't require authentication.

        Args:
            path: Request path

        Returns:
            bool: True if path is public
        """
        # Exact matches
        if path in self._public_paths:
            return True

        # Pattern matches
        public_patterns = [
            "/health/",
            "/metrics/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        return any(path.startswith(pattern) for pattern in public_patterns)

    def _is_auth_optional_path(self, path: str) -> bool:
        """
        Check if path has optional authentication (auth endpoints).

        Args:
            path: Request path

        Returns:
            bool: True if authentication is optional
        """
        return path in self._auth_optional_paths or any(
            path.startswith(pattern)
            for pattern in [
                "/api/v1/auth/",
                "/auth/",
            ]
        )

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: The incoming request

        Returns:
            str: Client IP address
        """
        # Check for forwarded headers (common in load balancer setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _create_auth_error_response(
        self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> JSONResponse:
        """
        Create authentication error response.

        Args:
            message: Error message
            status_code: HTTP status code

        Returns:
            JSONResponse: Error response
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Authentication Error",
                "message": message,
                "code": "AUTH_REQUIRED" if status_code == 401 else "AUTH_FORBIDDEN",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
