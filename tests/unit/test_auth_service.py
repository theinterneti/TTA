"""
Unit tests for src/player_experience/services/auth_service.py.

Covers:
- SecurityService: password validation, hashing, token/backup-code generation
- MFAService: TOTP secret generation, challenge lifecycle, expired/exhausted paths
- EnhancedAuthService: registration, authentication, JWT round-trip, session
  management, permission checks, account lockout
"""

from __future__ import annotations

import pytest

from src.player_experience.models.auth import (
    AuthenticatedUser,
    MFAConfig,
    MFAMethod,
    MFAVerification,
    Permission,
    SecuritySettings,
    UserCredentials,
    UserRegistration,
    UserRole,
)
from src.player_experience.services.auth_service import (
    AuthenticationError,
    AuthorizationError,
    EnhancedAuthService,
    MFAError,
    MFAService,
    SecurityService,
)

_SECRET = "test-secret-key-for-unit-tests"

# Valid password meeting all SecuritySettings defaults
_VALID_PW = "SecurePass123!"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(**kwargs) -> EnhancedAuthService:
    return EnhancedAuthService(secret_key=_SECRET, **kwargs)


def _make_player_user(user_id: str = "u1") -> AuthenticatedUser:
    from src.player_experience.models.auth import DEFAULT_ROLE_PERMISSIONS

    return AuthenticatedUser(
        user_id=user_id,
        username="alice",
        email="alice@example.com",
        role=UserRole.PLAYER,
        permissions=DEFAULT_ROLE_PERMISSIONS[UserRole.PLAYER].permissions,
    )


# ===========================================================================
# SecurityService
# ===========================================================================


class TestSecurityServicePasswordValidation:
    def test_valid_password_passes_all_requirements(self):
        svc = SecurityService(SecuritySettings())
        ok, errors = svc.validate_password_strength(_VALID_PW)
        assert ok is True
        assert errors == []

    def test_too_short_fails(self):
        settings = SecuritySettings(
            password_min_length=12,
            password_require_uppercase=False,
            password_require_lowercase=False,
            password_require_numbers=False,
            password_require_special=False,
        )
        svc = SecurityService(settings)
        ok, errors = svc.validate_password_strength("short")
        assert ok is False
        assert any("12 characters" in e for e in errors)

    def test_missing_uppercase_fails(self):
        svc = SecurityService(SecuritySettings(password_require_uppercase=True))
        ok, errors = svc.validate_password_strength("nouppercase1!")
        assert ok is False
        assert any("uppercase" in e for e in errors)

    def test_missing_lowercase_fails(self):
        svc = SecurityService(SecuritySettings(password_require_lowercase=True))
        ok, errors = svc.validate_password_strength("NOLOWERCASE1!")
        assert ok is False
        assert any("lowercase" in e for e in errors)

    def test_missing_numbers_fails(self):
        svc = SecurityService(SecuritySettings(password_require_numbers=True))
        ok, errors = svc.validate_password_strength("NoNumbers!!")
        assert ok is False
        assert any("number" in e for e in errors)

    def test_missing_special_fails(self):
        svc = SecurityService(SecuritySettings(password_require_special=True))
        ok, errors = svc.validate_password_strength("NoSpecial12")
        assert ok is False
        assert any("special" in e for e in errors)

    def test_multiple_failures_returns_all_errors(self):
        settings = SecuritySettings(
            password_min_length=20,
            password_require_uppercase=True,
        )
        svc = SecurityService(settings)
        ok, errors = svc.validate_password_strength("short")
        assert ok is False
        assert len(errors) >= 2


class TestSecurityServiceHashAndToken:
    def test_hash_and_verify_password_round_trip(self):
        svc = SecurityService(SecuritySettings())
        hashed = svc.hash_password("my-password-123!")
        assert svc.verify_password("my-password-123!", hashed) is True

    def test_verify_wrong_password_returns_false(self):
        svc = SecurityService(SecuritySettings())
        hashed = svc.hash_password("correct-pass-1!")
        assert svc.verify_password("wrong-pass-1!", hashed) is False

    def test_generate_secure_token_is_string(self):
        svc = SecurityService(SecuritySettings())
        token = svc.generate_secure_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_backup_codes_default_count(self):
        svc = SecurityService(SecuritySettings())
        codes = svc.generate_backup_codes()
        assert len(codes) == 10

    def test_generate_backup_codes_custom_count(self):
        svc = SecurityService(SecuritySettings())
        codes = svc.generate_backup_codes(count=5)
        assert len(codes) == 5

    def test_backup_codes_are_uppercase_hex(self):
        svc = SecurityService(SecuritySettings())
        codes = svc.generate_backup_codes(count=3)
        for code in codes:
            assert code == code.upper()
            assert all(c in "0123456789ABCDEF" for c in code)


# ===========================================================================
# MFAService
# ===========================================================================


class TestMFAService:
    def _svc(self) -> MFAService:
        return MFAService(MFAConfig())

    def test_generate_totp_secret_returns_secret_and_qr(self):
        svc = self._svc()
        secret, qr_url = svc.generate_totp_secret("u1", "alice")
        assert isinstance(secret, str)
        assert len(secret) > 0
        assert qr_url.startswith("data:image/png;base64,")

    def test_verify_totp_code_with_valid_current_code(self):
        import pyotp

        svc = self._svc()
        secret, _ = svc.generate_totp_secret("u1", "alice")
        valid_code = pyotp.TOTP(secret).now()
        assert svc.verify_totp_code(secret, valid_code) is True

    def test_verify_totp_code_wrong_code_returns_false(self):
        svc = self._svc()
        secret, _ = svc.generate_totp_secret("u1", "alice")
        assert svc.verify_totp_code(secret, "000000") is False

    def test_create_mfa_challenge_stored_in_active_challenges(self):
        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.TOTP)
        assert challenge.challenge_id in svc.active_challenges
        assert challenge.method == MFAMethod.TOTP

    def test_verify_mfa_challenge_invalid_id_raises(self):
        svc = self._svc()
        verification = MFAVerification(
            challenge_id="nonexistent", code="123456", method=MFAMethod.TOTP
        )
        with pytest.raises(MFAError, match="Invalid or expired"):
            svc.verify_mfa_challenge(verification, secret="dummy")

    def test_verify_mfa_challenge_expired_raises(self):
        from datetime import UTC, datetime, timedelta

        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.TOTP)
        # Manually expire the challenge
        svc.active_challenges[challenge.challenge_id].expires_at = datetime.now(
            UTC
        ) - timedelta(minutes=1)
        verification = MFAVerification(
            challenge_id=challenge.challenge_id, code="123456", method=MFAMethod.TOTP
        )
        with pytest.raises(MFAError, match="expired"):
            svc.verify_mfa_challenge(verification, secret="dummy")

    def test_verify_mfa_challenge_too_many_attempts_raises(self):
        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.TOTP)
        challenge_id = challenge.challenge_id
        svc.active_challenges[challenge_id].attempts_remaining = 0

        verification = MFAVerification(
            challenge_id=challenge_id, code="000000", method=MFAMethod.TOTP
        )
        with pytest.raises(MFAError, match="Too many"):
            svc.verify_mfa_challenge(verification, secret="dummy")

    def test_cleanup_expired_challenges_removes_expired(self):
        from datetime import UTC, datetime, timedelta

        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.TOTP)
        svc.active_challenges[challenge.challenge_id].expires_at = datetime.now(
            UTC
        ) - timedelta(minutes=1)

        svc.cleanup_expired_challenges()
        assert challenge.challenge_id not in svc.active_challenges

    def test_cleanup_leaves_active_challenges_intact(self):
        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.TOTP)
        svc.cleanup_expired_challenges()
        assert challenge.challenge_id in svc.active_challenges

    def test_verify_backup_code_succeeds_and_consumes_code(self):
        svc = self._svc()
        challenge = svc.create_mfa_challenge("u1", MFAMethod.BACKUP_CODES)
        backup_codes = ["ABC12345", "DEF67890"]
        verification = MFAVerification(
            challenge_id=challenge.challenge_id,
            code="ABC12345",
            method=MFAMethod.BACKUP_CODES,
        )

        assert (
            svc.verify_mfa_challenge(
                verification,
                secret="unused",
                backup_codes=backup_codes,
            )
            is True
        )
        assert backup_codes == ["DEF67890"]


# ===========================================================================
# EnhancedAuthService
# ===========================================================================


class TestEnhancedAuthServiceRegistration:
    def test_register_user_success_without_repository(self):
        svc = _make_service()
        reg = UserRegistration(
            username="alice", email="alice@ex.com", password=_VALID_PW
        )
        success, errors = svc.register_user(reg)
        assert success is True
        assert errors == []

    def test_register_user_weak_password_fails(self):
        svc = _make_service()
        # lowercase-only password fails uppercase/numbers/special checks
        reg = UserRegistration(
            username="bob", email="bob@ex.com", password="alllowercase"
        )
        success, errors = svc.register_user(reg)
        assert success is False
        assert len(errors) > 0

    def test_register_user_logs_security_event(self):
        svc = _make_service()
        reg = UserRegistration(
            username="carol", email="carol@ex.com", password=_VALID_PW
        )
        svc.register_user(reg)
        event_types = [e.event_type for e in svc.security_events]
        assert "user_registration" in event_types

    def test_register_with_repo_checks_duplicate_username(self):
        from unittest.mock import MagicMock

        repo = MagicMock()
        repo.username_exists.return_value = True
        repo.email_exists.return_value = False

        svc = _make_service(user_repository=repo)
        reg = UserRegistration(
            username="alice", email="alice@ex.com", password=_VALID_PW
        )
        success, errors = svc.register_user(reg)
        assert success is False
        assert any("Username" in e for e in errors)


class TestEnhancedAuthServiceAuthentication:
    def test_authenticate_demo_user_success(self):
        svc = _make_service()
        creds = UserCredentials(username="demo_user", password="DemoPassword123!")
        user = svc.authenticate_user(creds)
        assert user is not None
        assert user.username == "demo_user"
        assert user.role == UserRole.PLAYER

    def test_authenticate_demo_user_wrong_password_returns_none(self):
        svc = _make_service()
        creds = UserCredentials(username="demo_user", password="WrongPassword123!")
        user = svc.authenticate_user(creds)
        assert user is None

    def test_authenticate_unknown_user_returns_none(self):
        svc = _make_service()
        creds = UserCredentials(username="unknown_user", password=_VALID_PW)
        user = svc.authenticate_user(creds)
        assert user is None

    def test_authenticate_unknown_user_records_failed_attempt(self):
        svc = _make_service()
        creds = UserCredentials(username="ghost", password=_VALID_PW)
        svc.authenticate_user(creds)
        assert "ghost" in svc.failed_login_attempts

    def test_authenticate_locked_account_raises(self):
        svc = _make_service()
        for _ in range(5):  # max_login_attempts = 5
            svc.record_failed_login("alice")

        creds = UserCredentials(username="alice", password=_VALID_PW)
        with pytest.raises(AuthenticationError, match="locked"):
            svc.authenticate_user(creds)

    def test_authenticate_logs_success_event(self):
        svc = _make_service()
        creds = UserCredentials(username="demo_user", password="DemoPassword123!")
        svc.authenticate_user(creds)
        event_types = [e.event_type for e in svc.security_events]
        assert "login_success" in event_types


class TestEnhancedAuthServiceSessionAndToken:
    def test_create_session_stored_in_active_sessions(self):
        svc = _make_service()
        user = _make_player_user()
        session_id = svc.create_session(user)
        assert session_id in svc.active_sessions
        assert svc.active_sessions[session_id].user_id == user.user_id

    def test_create_access_token_returns_string(self):
        svc = _make_service()
        user = _make_player_user()
        session_id = svc.create_session(user)
        token = svc.create_access_token(user, session_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_uses_player_id_field(self):
        from jose import jwt as _jwt

        svc = _make_service()
        user = _make_player_user("u42")
        session_id = svc.create_session(user)
        token = svc.create_access_token(user, session_id, player_id="player-99")
        payload = _jwt.decode(token, _SECRET, algorithms=["HS256"])
        assert payload["player_id"] == "player-99"

    def test_create_access_token_defaults_player_id_to_user_id(self):
        from jose import jwt as _jwt

        svc = _make_service()
        user = _make_player_user("u42")
        session_id = svc.create_session(user)
        token = svc.create_access_token(user, session_id)
        payload = _jwt.decode(token, _SECRET, algorithms=["HS256"])
        assert payload["player_id"] == "u42"

    def test_verify_access_token_round_trip(self):
        svc = _make_service()
        user = _make_player_user()
        session_id = svc.create_session(user)
        token = svc.create_access_token(user, session_id)
        verified = svc.verify_access_token(token)
        assert verified.user_id == user.user_id
        assert verified.username == user.username

    def test_verify_invalid_token_raises(self):
        svc = _make_service()
        with pytest.raises(AuthenticationError):
            svc.verify_access_token("this.is.invalid")

    def test_verify_token_after_session_revoked_raises(self):
        svc = _make_service()
        user = _make_player_user()
        session_id = svc.create_session(user)
        token = svc.create_access_token(user, session_id)
        svc.revoke_session(session_id)
        with pytest.raises(AuthenticationError, match="no longer active"):
            svc.verify_access_token(token)

    def test_revoke_all_user_sessions(self):
        svc = _make_service()
        user = _make_player_user()
        s1 = svc.create_session(user)
        s2 = svc.create_session(user)
        svc.revoke_all_user_sessions(user.user_id)
        assert not svc.active_sessions[s1].is_active
        assert not svc.active_sessions[s2].is_active

    def test_cleanup_expired_sessions(self):
        from datetime import UTC, datetime, timedelta

        svc = _make_service()
        user = _make_player_user()
        session_id = svc.create_session(user)
        # Backdating last_activity to exceed the 8-hour timeout
        svc.active_sessions[session_id].last_activity = datetime.now(UTC) - timedelta(
            minutes=500
        )
        svc.cleanup_expired_sessions()
        assert session_id not in svc.active_sessions


class TestEnhancedAuthServiceMFASetup:
    def test_setup_mfa_uses_passed_username_and_stores_backup_codes(self):
        svc = _make_service()

        setup_info = svc.setup_mfa("u1", MFAMethod.TOTP, username="alice")

        assert setup_info["backup_codes"]
        assert svc.mfa_secrets["u1"][0].backup_codes == setup_info["backup_codes"]


class TestEnhancedAuthServicePermissions:
    def test_require_permission_returns_true_when_granted(self):
        svc = _make_service()
        user = _make_player_user()
        result = svc.require_permission(user, Permission.CREATE_CHARACTER)
        assert result is True

    def test_require_permission_raises_when_missing(self):
        svc = _make_service()
        user = _make_player_user()
        with pytest.raises(AuthorizationError):
            svc.require_permission(user, Permission.MANAGE_USERS)

    def test_require_permission_logs_denial_event(self):
        svc = _make_service()
        user = _make_player_user()
        with pytest.raises(AuthorizationError):
            svc.require_permission(user, Permission.MANAGE_USERS)
        event_types = [e.event_type for e in svc.security_events]
        assert "authorization_denied" in event_types


class TestAccountLockout:
    def test_not_locked_by_default(self):
        svc = _make_service()
        assert svc.is_account_locked("alice") is False

    def test_locked_after_max_attempts(self):
        svc = _make_service()
        for _ in range(5):
            svc.record_failed_login("alice")
        assert svc.is_account_locked("alice") is True

    def test_not_locked_below_max_attempts(self):
        svc = _make_service()
        for _ in range(4):
            svc.record_failed_login("alice")
        assert svc.is_account_locked("alice") is False

    def test_clear_failed_attempts(self):
        svc = _make_service()
        for _ in range(5):
            svc.record_failed_login("alice")
        svc.clear_failed_login_attempts("alice")
        assert svc.is_account_locked("alice") is False
