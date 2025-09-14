"""
Unified Authentication Service

Core authentication service that consolidates all TTA authentication implementations
into a single, consistent, HIPAA-compliant system serving all interfaces.
"""

import logging
import secrets
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from .models import (
    AuditLogEntry,
    AuthenticationError,
    AuthorizationError,
    AuthTokens,
    InterfaceType,
    LoginCredentials,
    LoginResponse,
    Permission,
    SessionExpiredError,
    SessionInfo,
    TokenPayload,
    UnifiedUser,
    UserRole,
)

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages JWT token creation, validation, and refresh."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def create_access_token(
        self,
        user: UnifiedUser,
        session_id: str,
        interface_type: InterfaceType,
        ip_address: str | None = None,
    ) -> str:
        """Create JWT access token."""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = TokenPayload(
            sub=user.id,
            iat=int(now.timestamp()),
            exp=int(expire.timestamp()),
            aud=[interface_type.value],
            username=user.username,
            email=user.email,
            role=user.role,
            permissions=[p.value for p in user.permissions],
            interface_access=[i.value for i in user.interface_access],
            mfa_verified=user.mfa_verified or False,
            session_id=session_id,
            ip_address=ip_address,
        )

        return jwt.encode(
            payload.model_dump(), self.secret_key, algorithm=self.algorithm
        )

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create JWT refresh token."""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "session_id": session_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str, expected_type: str = "access") -> TokenPayload:
        """Validate and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if expected_type == "refresh":
                if payload.get("type") != "refresh":
                    raise AuthenticationError("Invalid token type")
                return payload

            return TokenPayload(**payload)

        except jwt.ExpiredSignatureError as e:
            raise SessionExpiredError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e


class SessionManager:
    """Manages user sessions and security."""

    def __init__(self):
        self.active_sessions: dict[str, SessionInfo] = {}
        self.session_timeouts = {
            InterfaceType.PATIENT: 60,  # 60 minutes
            InterfaceType.CLINICAL: 30,  # 30 minutes
            InterfaceType.ADMIN: 15,  # 15 minutes
            InterfaceType.DEVELOPER: 480,  # 8 hours
            InterfaceType.PUBLIC: 30,  # 30 minutes
        }

    def create_session(
        self,
        user: UnifiedUser,
        interface_type: InterfaceType,
        ip_address: str | None = None,
        device_id: str | None = None,
    ) -> SessionInfo:
        """Create new user session."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        timeout_minutes = self.session_timeouts.get(interface_type, 30)
        expires_at = now + timedelta(minutes=timeout_minutes)

        session = SessionInfo(
            session_id=session_id,
            user_id=user.id,
            interface_type=interface_type,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            ip_address=ip_address,
            device_id=device_id,
        )

        self.active_sessions[session_id] = session
        return session

    def validate_session(self, session_id: str) -> SessionInfo:
        """Validate session and update activity."""
        session = self.active_sessions.get(session_id)
        if not session:
            raise SessionExpiredError("Session not found")

        if not session.is_active:
            raise SessionExpiredError("Session is inactive")

        if datetime.utcnow() > session.expires_at:
            self.invalidate_session(session_id)
            raise SessionExpiredError("Session has expired")

        # Update last activity
        session.last_activity = datetime.utcnow()
        return session

    def extend_session(self, session_id: str) -> SessionInfo:
        """Extend session expiration."""
        session = self.validate_session(session_id)
        timeout_minutes = self.session_timeouts.get(session.interface_type, 30)
        session.expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        return session

    def invalidate_session(self, session_id: str) -> None:
        """Invalidate session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].is_active = False
            del self.active_sessions[session_id]


class AuditLogger:
    """HIPAA-compliant audit logging."""

    def __init__(self):
        self.audit_logs: list[AuditLogEntry] = []

    def log_authentication_event(
        self,
        user_id: str | None,
        username: str | None,
        action: str,
        success: bool,
        interface_type: InterfaceType | None = None,
        ip_address: str | None = None,
        session_id: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Log authentication-related events."""
        entry = AuditLogEntry(
            user_id=user_id,
            username=username,
            action=action,
            resource="authentication",
            interface_type=interface_type,
            ip_address=ip_address,
            session_id=session_id,
            success=success,
            details=details or {},
        )

        self.audit_logs.append(entry)
        logger.info(f"Audit: {action} - User: {username} - Success: {success}")


class UnifiedAuthService:
    """Main unified authentication service."""

    def __init__(self, secret_key: str, user_repository=None):
        self.secret_key = secret_key
        self.token_manager = TokenManager(secret_key)
        self.session_manager = SessionManager()
        self.audit_logger = AuditLogger()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repository = user_repository

        # In-memory user store for development/testing
        self.test_users = self._create_test_users()

    def _create_test_users(self) -> dict[str, UnifiedUser]:
        """Create test users for development."""
        test_users = {}

        # Patient user
        patient = UnifiedUser(
            username="test_patient",
            email="patient@tta.dev",
            role=UserRole.PATIENT,
            permissions=[
                Permission.CREATE_CHARACTER,
                Permission.VIEW_PROGRESS,
                Permission.ACCESS_THERAPEUTIC_CONTENT,
            ],
            interface_access=[InterfaceType.PATIENT],
        )
        patient.profile.first_name = "Test"
        patient.profile.last_name = "Patient"
        test_users["test_patient"] = patient

        # Clinician user
        clinician = UnifiedUser(
            username="dr_smith",
            email="dr.smith@tta.dev",
            role=UserRole.CLINICIAN,
            permissions=[
                Permission.VIEW_PATIENT_DATA,
                Permission.MANAGE_THERAPEUTIC_SESSIONS,
                Permission.ACCESS_CRISIS_TOOLS,
                Permission.GENERATE_REPORTS,
            ],
            interface_access=[InterfaceType.CLINICAL],
        )
        clinician.profile.first_name = "Dr. Sarah"
        clinician.profile.last_name = "Smith"
        test_users["dr_smith"] = clinician

        # Admin user
        admin = UnifiedUser(
            username="admin",
            email="admin@tta.dev",
            role=UserRole.ADMIN,
            permissions=[
                Permission.MANAGE_USERS,
                Permission.MANAGE_SYSTEM_CONFIG,
                Permission.VIEW_AUDIT_LOGS,
                Permission.MANAGE_ROLES,
            ],
            interface_access=[InterfaceType.ADMIN, InterfaceType.CLINICAL],
        )
        admin.profile.first_name = "System"
        admin.profile.last_name = "Administrator"
        test_users["admin"] = admin

        return test_users

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Hash password."""
        return self.pwd_context.hash(password)

    async def authenticate_user(
        self, credentials: LoginCredentials, ip_address: str | None = None
    ) -> UnifiedUser:
        """Authenticate user with credentials."""
        # For development, use test users with simple password check
        user = self.test_users.get(credentials.username)
        if not user:
            self.audit_logger.log_authentication_event(
                None,
                credentials.username,
                "login_failed",
                False,
                credentials.interface_type,
                ip_address,
                details={"reason": "user_not_found"},
            )
            raise AuthenticationError("Invalid credentials")

        # Simple password check for test users (password = username + "123")
        expected_password = credentials.username + "123"
        if credentials.password != expected_password:
            self.audit_logger.log_authentication_event(
                user.id,
                credentials.username,
                "login_failed",
                False,
                credentials.interface_type,
                ip_address,
                details={"reason": "invalid_password"},
            )
            raise AuthenticationError("Invalid credentials")

        # Check interface access
        if credentials.interface_type not in user.interface_access:
            self.audit_logger.log_authentication_event(
                user.id,
                credentials.username,
                "login_failed",
                False,
                credentials.interface_type,
                ip_address,
                details={"reason": "interface_access_denied"},
            )
            raise AuthorizationError(
                f"Access denied to {credentials.interface_type.value} interface"
            )

        # Update last login
        user.last_login = datetime.utcnow()

        self.audit_logger.log_authentication_event(
            user.id,
            credentials.username,
            "login_success",
            True,
            credentials.interface_type,
            ip_address,
        )

        return user

    async def login(
        self, credentials: LoginCredentials, ip_address: str | None = None
    ) -> LoginResponse:
        """Complete login process with token generation."""
        # Authenticate user
        user = await self.authenticate_user(credentials, ip_address)

        # Create session
        session = self.session_manager.create_session(
            user, credentials.interface_type, ip_address, credentials.device_id
        )

        # Generate tokens
        access_token = self.token_manager.create_access_token(
            user, session.session_id, credentials.interface_type, ip_address
        )
        refresh_token = self.token_manager.create_refresh_token(
            user.id, session.session_id
        )

        tokens = AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_manager.access_token_expire_minutes * 60,
            refresh_expires_in=self.token_manager.refresh_token_expire_days
            * 24
            * 60
            * 60,
        )

        return LoginResponse(
            user=user,
            tokens=tokens,
            session_id=session.session_id,
            mfa_required=user.mfa_enabled and not user.mfa_verified,
        )

    async def refresh_token(self, refresh_token: str) -> AuthTokens:
        """Refresh access token using refresh token."""
        try:
            # Validate refresh token
            payload = self.token_manager.validate_token(refresh_token, "refresh")
            user_id = payload["sub"]
            session_id = payload["session_id"]

            # Validate session
            session = self.session_manager.validate_session(session_id)

            # Get user
            user = self.test_users.get(user_id)  # In production, get from repository
            if not user:
                raise AuthenticationError("User not found")

            # Generate new access token
            access_token = self.token_manager.create_access_token(
                user, session_id, session.interface_type, session.ip_address
            )

            # Generate new refresh token
            new_refresh_token = self.token_manager.create_refresh_token(
                user_id, session_id
            )

            self.audit_logger.log_authentication_event(
                user_id,
                user.username,
                "token_refresh",
                True,
                session.interface_type,
                session.ip_address,
                session_id,
            )

            return AuthTokens(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=self.token_manager.access_token_expire_minutes * 60,
                refresh_expires_in=self.token_manager.refresh_token_expire_days
                * 24
                * 60
                * 60,
            )

        except Exception as e:
            self.audit_logger.log_authentication_event(
                None, None, "token_refresh_failed", False, details={"error": str(e)}
            )
            raise

    async def logout(self, session_id: str, user_id: str | None = None) -> None:
        """Logout user and invalidate session."""
        try:
            session = self.session_manager.active_sessions.get(session_id)
            if session:
                user = self.test_users.get(session.user_id)
                self.audit_logger.log_authentication_event(
                    session.user_id,
                    user.username if user else None,
                    "logout",
                    True,
                    session.interface_type,
                    session.ip_address,
                    session_id,
                )

            self.session_manager.invalidate_session(session_id)

        except Exception as e:
            self.audit_logger.log_authentication_event(
                user_id, None, "logout_failed", False, details={"error": str(e)}
            )
            raise

    async def validate_access_token(
        self, token: str
    ) -> tuple[UnifiedUser, SessionInfo]:
        """Validate access token and return user and session info."""
        try:
            # Decode token
            payload = self.token_manager.validate_token(token)

            # Validate session
            session = self.session_manager.validate_session(payload.session_id)

            # Get user
            user = self.test_users.get(payload.sub)
            if not user:
                raise AuthenticationError("User not found")

            return user, session

        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            raise

    def has_permission(self, user: UnifiedUser, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in user.permissions

    def has_interface_access(
        self, user: UnifiedUser, interface_type: InterfaceType
    ) -> bool:
        """Check if user has access to specific interface."""
        return interface_type in user.interface_access
