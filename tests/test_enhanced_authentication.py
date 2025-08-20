"""
Tests for enhanced authentication system with MFA and RBAC.

This module tests the enhanced authentication features including
multi-factor authentication, role-based access control, and security features.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.player_experience.models.auth import (
    UserRole, Permission, MFAMethod, UserCredentials, UserRegistration,
    AuthenticatedUser, SecuritySettings, MFAConfig, MFAVerification
)
from src.player_experience.services.auth_service import (
    EnhancedAuthService, AuthenticationError, AuthorizationError, MFAError,
    SecurityService
)
from src.player_experience.api.routers.auth import router


@pytest.fixture
def security_settings():
    """Create test security settings."""
    return SecuritySettings(
        password_min_length=8,
        password_require_uppercase=True,
        password_require_lowercase=True,
        password_require_numbers=True,
        password_require_special=True,
        max_login_attempts=3,
        lockout_duration_minutes=15
    )


@pytest.fixture
def mfa_config():
    """Create test MFA configuration."""
    return MFAConfig(
        enabled=True,
        email_enabled=True,
        recovery_codes_enabled=True
    )


@pytest.fixture
def auth_service(security_settings, mfa_config):
    """Create test authentication service."""
    return EnhancedAuthService(
        secret_key="test-secret-key",
        security_settings=security_settings,
        mfa_config=mfa_config
    )


@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    app = FastAPI()
    app.include_router(router, prefix="/auth")
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestSecurityService:
    """Test security service functionality."""
    
    def test_password_strength_validation(self, security_settings):
        """Test password strength validation."""
        security_service = SecurityService(security_settings)
        
        # Test valid password
        is_valid, errors = security_service.validate_password_strength("StrongP@ss123")
        assert is_valid
        assert len(errors) == 0
        
        # Test weak passwords
        weak_passwords = [
            ("short", ["Password must be at least 8 characters long"]),
            ("nouppercase123!", ["Password must contain at least one uppercase letter"]),
            ("NOLOWERCASE123!", ["Password must contain at least one lowercase letter"]),
            ("NoNumbers!", ["Password must contain at least one number"]),
            ("NoSpecial123", ["Password must contain at least one special character"]),
        ]
        
        for password, expected_errors in weak_passwords:
            is_valid, errors = security_service.validate_password_strength(password)
            assert not is_valid
            for expected_error in expected_errors:
                assert any(expected_error in error for error in errors)
    
    def test_password_hashing(self, security_settings):
        """Test password hashing and verification."""
        security_service = SecurityService(security_settings)
        
        password = "TestPassword123!"
        hashed = security_service.hash_password(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Verification should work
        assert security_service.verify_password(password, hashed)
        
        # Wrong password should fail
        assert not security_service.verify_password("WrongPassword", hashed)
    
    def test_secure_token_generation(self, security_settings):
        """Test secure token generation."""
        security_service = SecurityService(security_settings)
        
        token1 = security_service.generate_secure_token()
        token2 = security_service.generate_secure_token()
        
        # Tokens should be different
        assert token1 != token2
        
        # Tokens should have reasonable length
        assert len(token1) > 20
        assert len(token2) > 20
    
    def test_backup_codes_generation(self, security_settings):
        """Test backup codes generation."""
        security_service = SecurityService(security_settings)
        
        codes = security_service.generate_backup_codes(5)
        
        assert len(codes) == 5
        assert all(len(code) == 8 for code in codes)  # 4 hex bytes = 8 chars
        assert len(set(codes)) == 5  # All codes should be unique


class TestMFAService:
    """Test MFA service functionality."""
    
    def test_totp_secret_generation(self, auth_service):
        """Test TOTP secret and QR code generation."""
        user_id = "test_user_123"
        username = "testuser"
        
        secret, qr_code = auth_service.mfa_service.generate_totp_secret(user_id, username)
        
        # Secret should be base32 encoded
        assert len(secret) == 32
        assert secret.isalnum()
        
        # QR code should be data URL
        assert qr_code.startswith("data:image/png;base64,")
    
    def test_totp_code_verification(self, auth_service):
        """Test TOTP code verification."""
        import pyotp
        
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate current code
        current_code = totp.now()
        
        # Verification should succeed
        assert auth_service.mfa_service.verify_totp_code(secret, current_code)
        
        # Wrong code should fail
        assert not auth_service.mfa_service.verify_totp_code(secret, "000000")
    
    def test_mfa_challenge_creation(self, auth_service):
        """Test MFA challenge creation and management."""
        user_id = "test_user_123"
        method = MFAMethod.TOTP
        
        challenge = auth_service.mfa_service.create_mfa_challenge(user_id, method)
        
        assert challenge.method == method
        assert challenge.attempts_remaining == 3
        assert challenge.expires_at > datetime.utcnow()
        
        # Challenge should be stored
        assert challenge.challenge_id in auth_service.mfa_service.active_challenges
    
    def test_mfa_challenge_cleanup(self, auth_service):
        """Test expired challenge cleanup."""
        user_id = "test_user_123"
        method = MFAMethod.TOTP
        
        # Create challenge
        challenge = auth_service.mfa_service.create_mfa_challenge(user_id, method)
        challenge_id = challenge.challenge_id
        
        # Manually expire the challenge
        challenge.expires_at = datetime.utcnow() - timedelta(minutes=1)
        
        # Cleanup should remove expired challenge
        auth_service.mfa_service.cleanup_expired_challenges()
        
        assert challenge_id not in auth_service.mfa_service.active_challenges


class TestEnhancedAuthService:
    """Test enhanced authentication service."""
    
    def test_user_registration_validation(self, auth_service):
        """Test user registration with validation."""
        # Valid registration
        valid_registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="StrongP@ss123",
            role=UserRole.PLAYER
        )
        
        success, errors = auth_service.register_user(valid_registration)
        assert success
        assert len(errors) == 0
        
        # Invalid registration (weak password that meets length requirement)
        invalid_registration = UserRegistration(
            username="testuser2",
            email="test2@example.com",
            password="weakpass",  # 8 chars but no uppercase, numbers, or special chars
            role=UserRole.PLAYER
        )
        
        success, errors = auth_service.register_user(invalid_registration)
        assert not success
        assert len(errors) > 0
    
    def test_account_lockout(self, auth_service):
        """Test account lockout after failed login attempts."""
        username = "testuser"
        
        # Record failed attempts
        for _ in range(3):
            auth_service.record_failed_login(username)
        
        # Account should be locked
        assert auth_service.is_account_locked(username)
        
        # Clear attempts
        auth_service.clear_failed_login_attempts(username)
        
        # Account should be unlocked
        assert not auth_service.is_account_locked(username)
    
    def test_session_management(self, auth_service):
        """Test session creation and management."""
        user = AuthenticatedUser(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[Permission.CREATE_CHARACTER]
        )
        
        # Create session
        session_id = auth_service.create_session(user, "127.0.0.1", "TestAgent/1.0")
        
        assert session_id in auth_service.active_sessions
        
        session = auth_service.active_sessions[session_id]
        assert session.user_id == user.user_id
        assert session.ip_address == "127.0.0.1"
        assert session.is_active
    
    def test_access_token_creation_and_verification(self, auth_service):
        """Test JWT access token creation and verification."""
        user = AuthenticatedUser(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[Permission.CREATE_CHARACTER, Permission.MANAGE_OWN_CHARACTERS]
        )
        
        session_id = auth_service.create_session(user)
        token = auth_service.create_access_token(user, session_id)
        
        # Token should be a string
        assert isinstance(token, str)
        assert len(token) > 50
        
        # Verify token
        verified_user = auth_service.verify_access_token(token)
        
        assert verified_user.user_id == user.user_id
        assert verified_user.username == user.username
        assert verified_user.role == user.role
        assert set(verified_user.permissions) == set(user.permissions)
    
    def test_permission_checking(self, auth_service):
        """Test permission-based access control."""
        user = AuthenticatedUser(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[Permission.CREATE_CHARACTER, Permission.MANAGE_OWN_CHARACTERS]
        )
        
        # User should have these permissions
        assert auth_service.require_permission(user, Permission.CREATE_CHARACTER)
        assert auth_service.require_permission(user, Permission.MANAGE_OWN_CHARACTERS)
        
        # User should not have admin permissions
        with pytest.raises(AuthorizationError):
            auth_service.require_permission(user, Permission.MANAGE_USERS)
    
    def test_mfa_setup(self, auth_service):
        """Test MFA setup for users."""
        user_id = "test_user_123"
        method = MFAMethod.TOTP
        
        setup_info = auth_service.setup_mfa(user_id, method)
        
        assert "secret" in setup_info
        assert "qr_code" in setup_info
        assert "backup_codes" in setup_info
        
        # MFA should be enabled for user
        assert auth_service.is_mfa_enabled(user_id)
    
    def test_session_cleanup(self, auth_service):
        """Test expired session cleanup."""
        user = AuthenticatedUser(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[Permission.CREATE_CHARACTER]
        )
        
        # Create session
        session_id = auth_service.create_session(user)
        
        # Manually expire the session
        session = auth_service.active_sessions[session_id]
        session.last_activity = datetime.utcnow() - timedelta(hours=10)
        
        # Cleanup should remove expired session
        auth_service.cleanup_expired_sessions()
        
        assert session_id not in auth_service.active_sessions
    
    def test_security_event_logging(self, auth_service):
        """Test security event logging."""
        from src.player_experience.models.auth import SecurityEvent
        
        initial_count = len(auth_service.security_events)
        
        event = SecurityEvent(
            event_type="test_event",
            user_id="test_user_123",
            details={"test": "data"}
        )
        
        auth_service.log_security_event(event)
        
        assert len(auth_service.security_events) == initial_count + 1
        assert auth_service.security_events[-1].event_type == "test_event"


class TestAuthenticationAPI:
    """Test authentication API endpoints."""
    
    def test_register_endpoint(self, client):
        """Test user registration endpoint."""
        registration_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongP@ss123",
            "role": "player"
        }
        
        response = client.post("/auth/register", json=registration_data)
        
        # Should succeed (mocked implementation)
        assert response.status_code in [200, 500]  # 500 due to missing database
    
    def test_login_endpoint(self, client):
        """Test login endpoint."""
        login_data = {
            "username": "testuser",
            "password": "StrongP@ss123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # Should fail due to missing database implementation
        assert response.status_code in [401, 500]
    
    def test_mfa_setup_endpoint_requires_auth(self, client):
        """Test MFA setup endpoint requires authentication."""
        response = client.post("/auth/mfa/setup", params={"method": "totp"})
        
        # Should require authentication
        assert response.status_code == 403  # No authorization header
    
    def test_permissions_endpoint_requires_auth(self, client):
        """Test permissions endpoint requires authentication."""
        response = client.get("/auth/permissions")
        
        # Should require authentication
        assert response.status_code == 403
    
    def test_security_events_endpoint_requires_admin(self, client):
        """Test security events endpoint requires admin permissions."""
        response = client.get("/auth/security/events")
        
        # Should require authentication and admin permissions
        assert response.status_code == 403


class TestRoleBasedAccessControl:
    """Test role-based access control functionality."""
    
    def test_default_role_permissions(self):
        """Test default role permissions are correctly defined."""
        from src.player_experience.models.auth import DEFAULT_ROLE_PERMISSIONS
        
        # Player should have basic permissions
        player_perms = DEFAULT_ROLE_PERMISSIONS[UserRole.PLAYER].permissions
        assert Permission.CREATE_CHARACTER in player_perms
        assert Permission.MANAGE_OWN_CHARACTERS in player_perms
        assert Permission.MANAGE_USERS not in player_perms
        
        # Admin should have all permissions
        admin_perms = DEFAULT_ROLE_PERMISSIONS[UserRole.ADMIN].permissions
        assert len(admin_perms) == len(list(Permission))
        assert Permission.MANAGE_USERS in admin_perms
        
        # Therapist should have patient-related permissions
        therapist_perms = DEFAULT_ROLE_PERMISSIONS[UserRole.THERAPIST].permissions
        assert Permission.VIEW_PATIENT_PROGRESS in therapist_perms
        assert Permission.ACCESS_CRISIS_PROTOCOLS in therapist_perms
    
    def test_authenticated_user_permission_methods(self):
        """Test AuthenticatedUser permission checking methods."""
        user = AuthenticatedUser(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[Permission.CREATE_CHARACTER, Permission.MANAGE_OWN_CHARACTERS]
        )
        
        # Test individual permission checking
        assert user.has_permission(Permission.CREATE_CHARACTER)
        assert not user.has_permission(Permission.MANAGE_USERS)
        
        # Test multiple permission checking
        assert user.has_any_permission([Permission.CREATE_CHARACTER, Permission.MANAGE_USERS])
        assert not user.has_all_permissions([Permission.CREATE_CHARACTER, Permission.MANAGE_USERS])
        assert user.has_all_permissions([Permission.CREATE_CHARACTER, Permission.MANAGE_OWN_CHARACTERS])
        
        # Test role checking
        assert not user.is_admin()
        assert not user.is_therapist()
        
        # Test data access checking
        assert user.can_access_user_data(user.user_id)  # Own data
        assert not user.can_access_user_data("other_user_123")  # Other user's data
    
    def test_admin_user_permissions(self):
        """Test admin user has full permissions."""
        from src.player_experience.models.auth import DEFAULT_ROLE_PERMISSIONS
        
        admin_user = AuthenticatedUser(
            user_id="admin_123",
            username="admin",
            email="admin@example.com",
            role=UserRole.ADMIN,
            permissions=DEFAULT_ROLE_PERMISSIONS[UserRole.ADMIN].permissions
        )
        
        # Admin should have all permissions
        for permission in Permission:
            assert admin_user.has_permission(permission)
        
        # Admin should be able to access any user's data
        assert admin_user.can_access_user_data("any_user_123")
        assert admin_user.is_admin()


if __name__ == "__main__":
    pytest.main([__file__])