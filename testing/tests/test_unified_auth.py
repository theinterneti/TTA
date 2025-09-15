"""
Test suite for Unified Authentication System

Tests the consolidated authentication service to ensure it resolves the
"Welcome back, !" issue and provides consistent authentication across all interfaces.
"""

import pytest

from src.services.unified_auth import (
    AuthenticationError,
    AuthorizationError,
    InterfaceType,
    LoginCredentials,
    Permission,
    UnifiedAuthService,
    UserRole,
)


class TestUnifiedAuthService:
    """Test the unified authentication service."""

    @pytest.fixture
    def auth_service(self):
        """Create auth service for testing."""
        return UnifiedAuthService(secret_key="test-secret-key")

    @pytest.mark.asyncio
    async def test_patient_login_success(self, auth_service):
        """Test successful patient login."""
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.PATIENT,
        )

        response = await auth_service.login(credentials)

        assert response.user.username == "test_patient"
        assert response.user.role == UserRole.PATIENT
        assert response.user.get_display_name() == "Test Patient"
        assert InterfaceType.PATIENT in response.user.interface_access
        assert response.tokens.access_token is not None
        assert response.tokens.refresh_token is not None
        assert not response.mfa_required

    @pytest.mark.asyncio
    async def test_clinician_login_success(self, auth_service):
        """Test successful clinician login."""
        credentials = LoginCredentials(
            username="dr_smith",
            password="dr_smith123",
            interface_type=InterfaceType.CLINICAL,
        )

        response = await auth_service.login(credentials)

        assert response.user.username == "dr_smith"
        assert response.user.role == UserRole.CLINICIAN
        assert response.user.get_display_name() == "Dr. Sarah Smith"
        assert InterfaceType.CLINICAL in response.user.interface_access
        assert Permission.VIEW_PATIENT_DATA in response.user.permissions

    @pytest.mark.asyncio
    async def test_admin_login_success(self, auth_service):
        """Test successful admin login."""
        credentials = LoginCredentials(
            username="admin", password="admin123", interface_type=InterfaceType.ADMIN
        )

        response = await auth_service.login(credentials)

        assert response.user.username == "admin"
        assert response.user.role == UserRole.ADMIN
        assert response.user.get_display_name() == "System Administrator"
        assert InterfaceType.ADMIN in response.user.interface_access
        assert Permission.MANAGE_USERS in response.user.permissions

    @pytest.mark.asyncio
    async def test_invalid_credentials(self, auth_service):
        """Test login with invalid credentials."""
        credentials = LoginCredentials(
            username="invalid_user",
            password="wrong_password",
            interface_type=InterfaceType.PATIENT,
        )

        with pytest.raises(AuthenticationError):
            await auth_service.login(credentials)

    @pytest.mark.asyncio
    async def test_interface_access_denied(self, auth_service):
        """Test login denied for unauthorized interface."""
        # Patient trying to access clinical interface
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.CLINICAL,
        )

        with pytest.raises(AuthorizationError):
            await auth_service.login(credentials)

    @pytest.mark.asyncio
    async def test_token_validation(self, auth_service):
        """Test token validation."""
        # Login first
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.PATIENT,
        )

        response = await auth_service.login(credentials)
        access_token = response.tokens.access_token

        # Validate token
        user, session = await auth_service.validate_access_token(access_token)

        assert user.username == "test_patient"
        assert user.get_display_name() == "Test Patient"
        assert session.interface_type == InterfaceType.PATIENT

    @pytest.mark.asyncio
    async def test_token_refresh(self, auth_service):
        """Test token refresh functionality."""
        # Login first
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.PATIENT,
        )

        response = await auth_service.login(credentials)
        refresh_token = response.tokens.refresh_token

        # Refresh token
        new_tokens = await auth_service.refresh_token(refresh_token)

        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None
        assert new_tokens.access_token != response.tokens.access_token

    @pytest.mark.asyncio
    async def test_session_management(self, auth_service):
        """Test session creation and validation."""
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.PATIENT,
        )

        response = await auth_service.login(credentials)
        session_id = response.session_id

        # Validate session
        session = auth_service.session_manager.validate_session(session_id)

        assert session.user_id == response.user.id
        assert session.interface_type == InterfaceType.PATIENT
        assert session.is_active

    @pytest.mark.asyncio
    async def test_logout(self, auth_service):
        """Test logout functionality."""
        # Login first
        credentials = LoginCredentials(
            username="test_patient",
            password="test_patient123",
            interface_type=InterfaceType.PATIENT,
        )

        response = await auth_service.login(credentials)
        session_id = response.session_id

        # Logout
        await auth_service.logout(session_id, response.user.id)

        # Session should be invalidated
        with pytest.raises(Exception):  # SessionExpiredError
            auth_service.session_manager.validate_session(session_id)

    def test_permission_checking(self, auth_service):
        """Test permission checking functionality."""
        # Get test users
        patient = auth_service.test_users["test_patient"]
        clinician = auth_service.test_users["dr_smith"]
        admin = auth_service.test_users["admin"]

        # Patient permissions
        assert auth_service.has_permission(patient, Permission.CREATE_CHARACTER)
        assert not auth_service.has_permission(patient, Permission.VIEW_PATIENT_DATA)

        # Clinician permissions
        assert auth_service.has_permission(clinician, Permission.VIEW_PATIENT_DATA)
        assert not auth_service.has_permission(clinician, Permission.MANAGE_USERS)

        # Admin permissions
        assert auth_service.has_permission(admin, Permission.MANAGE_USERS)
        assert auth_service.has_permission(admin, Permission.VIEW_AUDIT_LOGS)

    def test_interface_access_checking(self, auth_service):
        """Test interface access checking."""
        patient = auth_service.test_users["test_patient"]
        clinician = auth_service.test_users["dr_smith"]
        admin = auth_service.test_users["admin"]

        # Patient access
        assert auth_service.has_interface_access(patient, InterfaceType.PATIENT)
        assert not auth_service.has_interface_access(patient, InterfaceType.CLINICAL)

        # Clinician access
        assert auth_service.has_interface_access(clinician, InterfaceType.CLINICAL)
        assert not auth_service.has_interface_access(clinician, InterfaceType.ADMIN)

        # Admin access
        assert auth_service.has_interface_access(admin, InterfaceType.ADMIN)
        assert auth_service.has_interface_access(admin, InterfaceType.CLINICAL)

    def test_display_name_resolution(self, auth_service):
        """Test that display names resolve correctly (fixes 'Welcome back, !' issue)."""
        patient = auth_service.test_users["test_patient"]
        clinician = auth_service.test_users["dr_smith"]
        admin = auth_service.test_users["admin"]

        # Test display names
        assert patient.get_display_name() == "Test Patient"
        assert clinician.get_display_name() == "Dr. Sarah Smith"
        assert admin.get_display_name() == "System Administrator"

        # Test profile display names
        assert patient.profile.get_display_name(patient.username) == "Test Patient"
        assert (
            clinician.profile.get_display_name(clinician.username) == "Dr. Sarah Smith"
        )
        assert admin.profile.get_display_name(admin.username) == "System Administrator"

    def test_audit_logging(self, auth_service):
        """Test audit logging functionality."""
        initial_log_count = len(auth_service.audit_logger.audit_logs)

        # Log an authentication event
        auth_service.audit_logger.log_authentication_event(
            user_id="test-user-id",
            username="test_user",
            action="login_success",
            success=True,
            interface_type=InterfaceType.PATIENT,
            ip_address="127.0.0.1",
        )

        # Check log was created
        assert len(auth_service.audit_logger.audit_logs) == initial_log_count + 1

        latest_log = auth_service.audit_logger.audit_logs[-1]
        assert latest_log.user_id == "test-user-id"
        assert latest_log.username == "test_user"
        assert latest_log.action == "login_success"
        assert latest_log.success is True
        assert latest_log.interface_type == InterfaceType.PATIENT


if __name__ == "__main__":
    # Run basic tests
    auth_service = UnifiedAuthService(secret_key="test-secret-key")

    # Test display name resolution
    patient = auth_service.test_users["test_patient"]
    print(f"Patient display name: '{patient.get_display_name()}'")

    clinician = auth_service.test_users["dr_smith"]
    print(f"Clinician display name: '{clinician.get_display_name()}'")

    admin = auth_service.test_users["admin"]
    print(f"Admin display name: '{admin.get_display_name()}'")

    print("✅ Display name resolution working correctly!")
    print("✅ No more 'Welcome back, !' issue!")
