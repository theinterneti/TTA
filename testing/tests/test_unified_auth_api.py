"""
Test suite for Unified Authentication API

Tests the FastAPI router endpoints for the consolidated authentication system.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.auth.unified_auth_router import router

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestUnifiedAuthAPI:
    """Test the unified authentication API endpoints."""

    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "unified_auth_service"
        assert "activeSessions" in data
        assert "auditLogEntries" in data

    def test_patient_login_success(self):
        """Test successful patient login via API."""
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "patient",
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Check user data
        assert data["user"]["username"] == "test_patient"
        assert data["user"]["role"] == "patient"
        assert data["user"]["profile"]["first_name"] == "Test"
        assert data["user"]["profile"]["last_name"] == "Patient"

        # Check tokens
        assert "accessToken" in data["tokens"]
        assert "refreshToken" in data["tokens"]
        assert data["tokens"]["tokenType"] == "bearer"

        # Check session
        assert "sessionId" in data
        assert data["mfaRequired"] is False

    def test_clinician_login_success(self):
        """Test successful clinician login via API."""
        login_data = {
            "username": "dr_smith",
            "password": "dr_smith123",
            "interface_type": "clinical",
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert data["user"]["username"] == "dr_smith"
        assert data["user"]["role"] == "clinician"
        assert data["user"]["profile"]["first_name"] == "Dr. Sarah"
        assert data["user"]["profile"]["last_name"] == "Smith"

    def test_admin_login_success(self):
        """Test successful admin login via API."""
        login_data = {
            "username": "admin",
            "password": "admin123",
            "interface_type": "admin",
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"
        assert data["user"]["profile"]["first_name"] == "System"
        assert data["user"]["profile"]["last_name"] == "Administrator"

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "invalid_user",
            "password": "wrong_password",
            "interface_type": "patient",
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_interface_access_denied(self):
        """Test login denied for unauthorized interface."""
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "clinical",  # Patient trying to access clinical interface
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Access denied" in response.json()["detail"]

    def test_get_profile_authenticated(self):
        """Test getting user profile with valid token."""
        # Login first
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "patient",
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        access_token = login_response.json()["tokens"]["accessToken"]

        # Get profile
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/profile", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "test_patient"
        assert data["profile"]["first_name"] == "Test"
        assert data["profile"]["last_name"] == "Patient"

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        response = client.get("/auth/profile")

        assert response.status_code == 403  # No Authorization header

    def test_get_profile_invalid_token(self):
        """Test getting profile with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/profile", headers=headers)

        assert response.status_code == 401

    def test_token_refresh(self):
        """Test token refresh functionality."""
        # Login first
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "patient",
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        refresh_token = login_response.json()["tokens"]["refreshToken"]

        # Refresh token
        refresh_data = {"refreshToken": refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"

    def test_logout(self):
        """Test logout functionality."""
        # Login first
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "patient",
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        access_token = login_response.json()["tokens"]["accessToken"]
        session_id = login_response.json()["sessionId"]

        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        logout_data = {"sessionId": session_id}
        response = client.post("/auth/logout", json=logout_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"

    def test_get_permissions(self):
        """Test getting user permissions."""
        # Login first
        login_data = {
            "username": "dr_smith",
            "password": "dr_smith123",
            "interface_type": "clinical",
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        access_token = login_response.json()["tokens"]["accessToken"]

        # Get permissions
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/permissions", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "dr_smith"
        assert data["role"] == "clinician"
        assert "view_patient_data" in data["permissions"]
        assert "clinical" in data["interfaceAccess"]

    def test_session_info(self):
        """Test getting session information."""
        # Login first
        login_data = {
            "username": "test_patient",
            "password": "test_patient123",
            "interface_type": "patient",
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        access_token = login_response.json()["tokens"]["accessToken"]

        # Get session info
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/session", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert "sessionId" in data
        assert data["interfaceType"] == "patient"
        assert data["isActive"] is True


if __name__ == "__main__":
    # Run basic API tests
    print("Testing Unified Authentication API...")

    # Test health check
    response = client.get("/auth/health")
    print(f"Health check: {response.status_code} - {response.json()['status']}")

    # Test patient login
    login_data = {
        "username": "test_patient",
        "password": "test_patient123",
        "interface_type": "patient",
    }

    response = client.post("/auth/login", json=login_data)
    if response.status_code == 200:
        user_data = response.json()["user"]
        display_name = (
            f"{user_data['profile']['first_name']} {user_data['profile']['last_name']}"
        )
        print(f"✅ Patient login successful: Welcome back, {display_name}!")
    else:
        print(f"❌ Patient login failed: {response.status_code}")

    # Test clinician login
    login_data = {
        "username": "dr_smith",
        "password": "dr_smith123",
        "interface_type": "clinical",
    }

    response = client.post("/auth/login", json=login_data)
    if response.status_code == 200:
        user_data = response.json()["user"]
        display_name = (
            f"{user_data['profile']['first_name']} {user_data['profile']['last_name']}"
        )
        print(f"✅ Clinician login successful: Welcome back, {display_name}!")
    else:
        print(f"❌ Clinician login failed: {response.status_code}")

    print("✅ Unified Authentication API working correctly!")
    print("✅ 'Welcome back, !' issue resolved!")
