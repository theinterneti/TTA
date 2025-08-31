"""
Enhanced authentication service with MFA and RBAC support.

This service provides comprehensive authentication, authorization, and security
features including multi-factor authentication and role-based access control.
"""

import base64
import io
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pyotp
import qrcode
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..database.user_repository import User, UserRepository
from ..models.auth import (
    DEFAULT_ROLE_PERMISSIONS,
    AuthenticatedUser,
    MFAChallenge,
    MFAConfig,
    MFAMethod,
    MFASecret,
    MFAVerification,
    Permission,
    SecurityEvent,
    SecuritySettings,
    SessionInfo,
    UserCredentials,
    UserRegistration,
    UserRole,
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class AuthorizationError(Exception):
    """Raised when authorization fails."""

    pass


class MFAError(Exception):
    """Raised when MFA operations fail."""

    pass


class SecurityService:
    """Service for security-related operations."""

    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """
        Validate password strength according to security settings.

        Args:
            password: The password to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if len(password) < self.settings.password_min_length:
            errors.append(
                f"Password must be at least {self.settings.password_min_length} characters long"
            )

        if self.settings.password_require_uppercase and not any(
            c.isupper() for c in password
        ):
            errors.append("Password must contain at least one uppercase letter")

        if self.settings.password_require_lowercase and not any(
            c.islower() for c in password
        ):
            errors.append("Password must contain at least one lowercase letter")

        if self.settings.password_require_numbers and not any(
            c.isdigit() for c in password
        ):
            errors.append("Password must contain at least one number")

        if self.settings.password_require_special and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)

    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """Generate backup codes for MFA recovery."""
        return [secrets.token_hex(4).upper() for _ in range(count)]


class MFAService:
    """Service for multi-factor authentication operations."""

    def __init__(self, config: MFAConfig):
        self.config = config
        self.active_challenges: dict[str, MFAChallenge] = {}

    def generate_totp_secret(self, user_id: str, username: str) -> tuple[str, str]:
        """
        Generate TOTP secret and QR code for user.

        Args:
            user_id: The user ID
            username: The username

        Returns:
            Tuple of (secret, qr_code_data_url)
        """
        secret = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username, issuer_name=self.config.totp_issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        qr_code_data = base64.b64encode(img_buffer.getvalue()).decode()
        qr_code_data_url = f"data:image/png;base64,{qr_code_data}"

        return secret, qr_code_data_url

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code against secret.

        Args:
            secret: The TOTP secret
            code: The code to verify
            window: Time window for verification (default 1 = 30 seconds)

        Returns:
            bool: True if code is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)

    def create_mfa_challenge(self, user_id: str, method: MFAMethod) -> MFAChallenge:
        """
        Create an MFA challenge for a user.

        Args:
            user_id: The user ID
            method: The MFA method

        Returns:
            MFAChallenge: The challenge object
        """
        challenge_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=5)  # 5-minute expiry

        challenge = MFAChallenge(
            challenge_id=challenge_id, method=method, expires_at=expires_at
        )

        self.active_challenges[challenge_id] = challenge
        return challenge

    def verify_mfa_challenge(self, verification: MFAVerification, secret: str) -> bool:
        """
        Verify an MFA challenge response.

        Args:
            verification: The verification request
            secret: The user's MFA secret

        Returns:
            bool: True if verification succeeds
        """
        challenge = self.active_challenges.get(verification.challenge_id)
        if not challenge:
            raise MFAError("Invalid or expired challenge")

        if datetime.utcnow() > challenge.expires_at:
            del self.active_challenges[verification.challenge_id]
            raise MFAError("Challenge has expired")

        if challenge.attempts_remaining <= 0:
            del self.active_challenges[verification.challenge_id]
            raise MFAError("Too many failed attempts")

        # Verify the code based on method
        is_valid = False
        if verification.method == MFAMethod.TOTP:
            is_valid = self.verify_totp_code(secret, verification.code)
        elif verification.method == MFAMethod.BACKUP_CODES:
            # TODO: Implement backup code verification
            pass

        if is_valid:
            del self.active_challenges[verification.challenge_id]
            return True
        else:
            challenge.attempts_remaining -= 1
            if challenge.attempts_remaining <= 0:
                del self.active_challenges[verification.challenge_id]
            return False

    def cleanup_expired_challenges(self):
        """Remove expired challenges from memory."""
        now = datetime.utcnow()
        expired_challenges = [
            challenge_id
            for challenge_id, challenge in self.active_challenges.items()
            if now > challenge.expires_at
        ]
        for challenge_id in expired_challenges:
            del self.active_challenges[challenge_id]


class EnhancedAuthService:
    """Enhanced authentication service with MFA and RBAC."""

    def __init__(
        self,
        secret_key: str,
        user_repository: UserRepository | None = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        security_settings: SecuritySettings | None = None,
        mfa_config: MFAConfig | None = None,
    ):
        """
        Initialize the Enhanced Authentication Service.

        Args:
            secret_key: Secret key for JWT token signing
            user_repository: User repository for database operations
            algorithm: JWT algorithm to use
            access_token_expire_minutes: Access token expiration time
            refresh_token_expire_days: Refresh token expiration time
            security_settings: Security configuration settings
            mfa_config: Multi-factor authentication configuration
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.user_repository = user_repository

        self.security_settings = security_settings or SecuritySettings()
        self.mfa_config = mfa_config or MFAConfig()

        self.security_service = SecurityService(self.security_settings)
        self.mfa_service = MFAService(self.mfa_config)

        # In-memory stores (in production, use Redis or database)
        self.active_sessions: dict[str, SessionInfo] = {}
        self.failed_login_attempts: dict[str, list[datetime]] = {}
        self.mfa_secrets: dict[str, list[MFASecret]] = {}
        self.security_events: list[SecurityEvent] = []

    def register_user(self, registration: UserRegistration) -> tuple[bool, list[str]]:
        """
        Register a new user with validation.

        Args:
            registration: User registration data

        Returns:
            Tuple of (success, errors)
        """
        errors = []

        # Validate password strength
        is_valid, password_errors = self.security_service.validate_password_strength(
            registration.password
        )
        if not is_valid:
            errors.extend(password_errors)

        # Check if username/email already exists in database
        if self.user_repository:
            if self.user_repository.username_exists(registration.username):
                errors.append("Username already exists")
            if self.user_repository.email_exists(registration.email):
                errors.append("Email already exists")

        if errors:
            return False, errors

        # Hash password
        hashed_password = self.security_service.hash_password(registration.password)

        # Store user in database with hashed password
        if self.user_repository:
            from uuid import uuid4

            user = User(
                user_id=str(uuid4()),
                username=registration.username,
                email=registration.email,
                password_hash=hashed_password,
                role=registration.role,
                email_verified=False,
                created_at=datetime.utcnow(),
                account_status="active",
                failed_login_attempts=0,
            )

            try:
                success = self.user_repository.create_user(user)
                if not success:
                    errors.append("Failed to create user account")
                    return False, errors
            except Exception as e:
                logger.error(f"Error creating user in database: {e}")
                errors.append("Failed to create user account")
                return False, errors

        # Log security event
        self.log_security_event(
            SecurityEvent(
                event_type="user_registration",
                details={
                    "username": registration.username,
                    "email": registration.email,
                    "role": registration.role.value,
                },
            )
        )

        return True, []

    def authenticate_user(
        self, credentials: UserCredentials, ip_address: str | None = None
    ) -> AuthenticatedUser | None:
        """
        Authenticate a user with username/password.

        Args:
            credentials: User credentials
            ip_address: Client IP address

        Returns:
            AuthenticatedUser if successful, None otherwise
        """
        # Check for account lockout
        if self.is_account_locked(credentials.username):
            self.log_security_event(
                SecurityEvent(
                    event_type="login_attempt_locked_account",
                    details={"username": credentials.username},
                    ip_address=ip_address,
                    severity="warning",
                )
            )
            raise AuthenticationError(
                "Account is temporarily locked due to too many failed attempts"
            )

        # Retrieve user from database
        user = None
        if self.user_repository:
            try:
                user = self.user_repository.get_user_by_username(credentials.username)
            except Exception as e:
                logger.error(f"Error retrieving user from database: {e}")
                raise AuthenticationError(
                    "Authentication service temporarily unavailable"
                )

        if not user:
            self.record_failed_login(credentials.username)
            self.log_security_event(
                SecurityEvent(
                    event_type="login_failed",
                    details={
                        "username": credentials.username,
                        "reason": "invalid_credentials",
                    },
                    ip_address=ip_address,
                    severity="warning",
                )
            )
            return None

        # Verify password against stored hash
        if not self.security_service.verify_password(
            credentials.password, user.password_hash
        ):
            self.record_failed_login(credentials.username)
            self.log_security_event(
                SecurityEvent(
                    event_type="login_failed",
                    details={
                        "username": credentials.username,
                        "reason": "invalid_password",
                    },
                    ip_address=ip_address,
                    severity="warning",
                )
            )
            return None

        # Clear failed login attempts on successful authentication
        self.clear_failed_login_attempts(credentials.username)

        # Update user's last login timestamp in database
        if self.user_repository:
            try:
                user.last_login = datetime.utcnow()
                user.failed_login_attempts = 0  # Reset failed attempts
                self.user_repository.update_user(user)
            except Exception as e:
                logger.warning(f"Failed to update user last login: {e}")

        # Create authenticated user object
        role_permissions = DEFAULT_ROLE_PERMISSIONS.get(
            user.role, DEFAULT_ROLE_PERMISSIONS[UserRole.PLAYER]
        )

        authenticated_user = AuthenticatedUser(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            permissions=role_permissions.permissions,
            mfa_enabled=self.is_mfa_enabled(user.user_id),
            last_login=user.last_login,
        )

        self.log_security_event(
            SecurityEvent(
                event_type="login_success",
                user_id=user.user_id,
                details={"username": credentials.username},
                ip_address=ip_address,
            )
        )

        return authenticated_user

    def create_session(
        self,
        user: AuthenticatedUser,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        """
        Create a new session for an authenticated user.

        Args:
            user: The authenticated user
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            str: Session ID
        """
        session_id = str(uuid4())
        session = SessionInfo(
            session_id=session_id,
            user_id=user.user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=not user.mfa_enabled,  # If MFA not enabled, consider it verified
        )

        self.active_sessions[session_id] = session
        return session_id

    def create_access_token(self, user: AuthenticatedUser, session_id: str) -> str:
        """Create JWT access token for authenticated user."""
        data = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "permissions": [perm.value for perm in user.permissions],
            "session_id": session_id,
            "mfa_verified": user.mfa_verified,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_token_expire_minutes),
        }
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> AuthenticatedUser:
        """
        Verify and decode access token.

        Args:
            token: JWT access token

        Returns:
            AuthenticatedUser: The authenticated user

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            user_id = payload.get("sub")
            username = payload.get("username")
            email = payload.get("email")
            role_str = payload.get("role")
            permissions_str = payload.get("permissions", [])
            session_id = payload.get("session_id")
            mfa_verified = payload.get("mfa_verified", False)

            if not user_id or not username:
                raise AuthenticationError("Invalid token payload")

            # Verify session is still active
            session = self.active_sessions.get(session_id)
            if not session or not session.is_active:
                raise AuthenticationError("Session is no longer active")

            # Update session activity
            session.last_activity = datetime.utcnow()

            # Convert role and permissions back to enums
            role = UserRole(role_str)
            permissions = [Permission(perm) for perm in permissions_str]

            return AuthenticatedUser(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                permissions=permissions,
                mfa_enabled=self.is_mfa_enabled(user_id),
                mfa_verified=mfa_verified,
                session_id=session_id,
            )

        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def require_permission(
        self, user: AuthenticatedUser, permission: Permission
    ) -> bool:
        """
        Check if user has required permission.

        Args:
            user: The authenticated user
            permission: Required permission

        Returns:
            bool: True if user has permission

        Raises:
            AuthorizationError: If user lacks permission
        """
        if not user.has_permission(permission):
            self.log_security_event(
                SecurityEvent(
                    event_type="authorization_denied",
                    user_id=user.user_id,
                    details={"required_permission": permission.value},
                    severity="warning",
                )
            )
            raise AuthorizationError(
                f"User lacks required permission: {permission.value}"
            )
        return True

    def require_mfa_verification(self, user: AuthenticatedUser) -> bool:
        """
        Check if user has completed MFA verification for sensitive operations.

        Args:
            user: The authenticated user

        Returns:
            bool: True if MFA is verified or not required

        Raises:
            AuthenticationError: If MFA verification is required but not completed
        """
        if user.mfa_enabled and not user.mfa_verified:
            raise AuthenticationError(
                "Multi-factor authentication verification required"
            )

        # Check if MFA is required for this user's role
        if (
            user.role in self.security_settings.require_mfa_for_roles
            and not user.mfa_verified
        ):
            raise AuthenticationError(
                "Multi-factor authentication is required for this role"
            )

        return True

    def setup_mfa(self, user_id: str, method: MFAMethod) -> dict[str, Any]:
        """
        Set up MFA for a user.

        Args:
            user_id: The user ID
            method: The MFA method to set up

        Returns:
            Dict with setup information (e.g., QR code for TOTP)
        """
        if method == MFAMethod.TOTP:
            # Get username from database
            username = "user"  # Default fallback
            if self.user_repository:
                try:
                    user = self.user_repository.get_user_by_id(user_id)
                    if user:
                        username = user.username
                except Exception as e:
                    logger.warning(f"Failed to get username for MFA setup: {e}")

            secret, qr_code = self.mfa_service.generate_totp_secret(user_id, username)

            # Store encrypted secret (in production, encrypt before storing)
            mfa_secret = MFASecret(
                user_id=user_id,
                method=method,
                secret=secret,  # TODO: Encrypt this
            )

            if user_id not in self.mfa_secrets:
                self.mfa_secrets[user_id] = []
            self.mfa_secrets[user_id].append(mfa_secret)

            return {
                "method": method.value,
                "secret": secret,
                "qr_code": qr_code,
                "backup_codes": self.security_service.generate_backup_codes(),
            }

        raise MFAError(f"Unsupported MFA method: {method}")

    def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for a user."""
        return user_id in self.mfa_secrets and len(self.mfa_secrets[user_id]) > 0

    def is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed login attempts."""
        # Check database first for persistent lockout status
        if self.user_repository:
            try:
                user = self.user_repository.get_user_by_username(username)
                if user and user.locked_until:
                    if datetime.utcnow() < user.locked_until:
                        return True
                    else:
                        # Lockout period expired, clear it
                        user.locked_until = None
                        user.failed_login_attempts = 0
                        self.user_repository.update_user(user)
                        return False
            except Exception as e:
                logger.warning(
                    f"Failed to check account lockout status in database: {e}"
                )

        # Fallback to in-memory tracking
        if username not in self.failed_login_attempts:
            return False

        attempts = self.failed_login_attempts[username]
        recent_attempts = [
            attempt
            for attempt in attempts
            if datetime.utcnow() - attempt
            < timedelta(minutes=self.security_settings.lockout_duration_minutes)
        ]

        return len(recent_attempts) >= self.security_settings.max_login_attempts

    def record_failed_login(self, username: str):
        """Record a failed login attempt."""
        now = datetime.utcnow()
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []

        self.failed_login_attempts[username].append(now)

        # Update failed login attempts in database
        if self.user_repository:
            try:
                user = self.user_repository.get_user_by_username(username)
                if user:
                    user.failed_login_attempts += 1
                    # Lock account if max attempts reached
                    if (
                        user.failed_login_attempts
                        >= self.security_settings.max_login_attempts
                    ):
                        user.locked_until = now + timedelta(
                            minutes=self.security_settings.lockout_duration_minutes
                        )
                    self.user_repository.update_user(user)
            except Exception as e:
                logger.warning(
                    f"Failed to update failed login attempts in database: {e}"
                )

        # Clean up old attempts
        cutoff = now - timedelta(
            minutes=self.security_settings.lockout_duration_minutes
        )
        self.failed_login_attempts[username] = [
            attempt
            for attempt in self.failed_login_attempts[username]
            if attempt > cutoff
        ]

    def clear_failed_login_attempts(self, username: str):
        """Clear failed login attempts for a user."""
        if username in self.failed_login_attempts:
            del self.failed_login_attempts[username]

        # Clear failed login attempts in database
        if self.user_repository:
            try:
                user = self.user_repository.get_user_by_username(username)
                if user:
                    user.failed_login_attempts = 0
                    user.locked_until = None
                    self.user_repository.update_user(user)
            except Exception as e:
                logger.warning(
                    f"Failed to clear failed login attempts in database: {e}"
                )

    def log_security_event(self, event: SecurityEvent):
        """Log a security event."""
        self.security_events.append(event)

        # In production, this would write to a secure audit log
        # For now, we'll just keep them in memory

        # Keep only recent events to prevent memory issues
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-5000:]

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        timeout = timedelta(minutes=self.security_settings.session_timeout_minutes)

        expired_sessions = [
            session_id
            for session_id, session in self.active_sessions.items()
            if now - session.last_activity > timeout
        ]

        for session_id in expired_sessions:
            del self.active_sessions[session_id]

    def revoke_session(self, session_id: str):
        """Revoke a specific session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].is_active = False

    def revoke_all_user_sessions(self, user_id: str):
        """Revoke all sessions for a specific user."""
        for session in self.active_sessions.values():
            if session.user_id == user_id:
                session.is_active = False
