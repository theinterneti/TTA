#!/usr/bin/env python3
"""
TTA API Structure Validation Test
This script validates the API endpoints are available and responding correctly.
"""

import json
from datetime import datetime

import requests

# API Configuration
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1"


class APIStructureValidator:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def log_result(
        self, endpoint, method, success, status_code, response_data=None, error=None
    ):
        """Log the result of each API test."""
        result = {
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": str(error) if error else None,
        }
        self.results.append(result)
        status = "✅ AVAILABLE" if success else "❌ FAILED"
        print(f"{method} {endpoint} - {status} ({status_code})")

    def test_endpoint(
        self, endpoint, method="GET", data=None, expect_auth_required=False
    ):
        """Test a single API endpoint."""
        try:
            url = f"{API_BASE}{endpoint}"

            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            else:
                response = self.session.request(method, url, json=data)

            # Consider 401 as success if we expect authentication to be required
            if expect_auth_required and response.status_code == 401:
                self.log_result(
                    endpoint,
                    method,
                    True,
                    response.status_code,
                    {"auth_required": True},
                )
                return True
            elif response.status_code in [
                200,
                201,
                405,
            ]:  # 405 = Method Not Allowed is also informative
                response_data = None
                try:
                    response_data = response.json()
                except (ValueError, TypeError, AttributeError) as e:
                    response_data = {
                        "raw_response": response.text[:200],
                        "json_error": str(e),
                    }

                self.log_result(
                    endpoint, method, True, response.status_code, response_data
                )
                return True
            else:
                try:
                    error_data = response.json()
                except (ValueError, TypeError, AttributeError) as e:
                    error_data = {
                        "raw_response": response.text[:200],
                        "json_error": str(e),
                    }

                self.log_result(
                    endpoint, method, False, response.status_code, error_data
                )
                return False

        except Exception as e:
            self.log_result(endpoint, method, False, 0, error=e)
            return False

    def validate_api_structure(self):
        """Validate the complete API structure."""
        print("🔍 Validating TTA API Structure")
        print("=" * 50)

        # Test public endpoints
        print("\n📋 Public Endpoints:")
        self.test_endpoint("/health", "GET")
        self.test_endpoint("/services/health", "GET")

        # Test authentication endpoints
        print("\n🔐 Authentication Endpoints:")
        self.test_endpoint(
            "/auth/register", "GET"
        )  # Should return 405 Method Not Allowed
        self.test_endpoint(
            "/auth/register",
            "POST",
            {"username": "test", "email": "test@example.com", "password": "test123"},
        )
        self.test_endpoint(
            "/auth/login", "POST", {"username": "test", "password": "test123"}
        )

        # Test protected endpoints (expect 401)
        print("\n🛡️ Protected Endpoints (expecting 401):")
        self.test_endpoint("/characters/", "GET", expect_auth_required=True)
        self.test_endpoint(
            "/characters/",
            "POST",
            {"name": "Test Character"},
            expect_auth_required=True,
        )
        self.test_endpoint("/worlds/", "GET", expect_auth_required=True)
        self.test_endpoint("/sessions/", "GET", expect_auth_required=True)
        self.test_endpoint(
            "/sessions/",
            "POST",
            {"character_id": "test", "world_id": "test"},
            expect_auth_required=True,
        )

        # Test specific resource endpoints
        print("\n🎯 Resource-Specific Endpoints:")
        self.test_endpoint(
            "/worlds/therapeutic_world_001", "GET", expect_auth_required=True
        )
        self.test_endpoint(
            "/worlds/therapeutic_world_001/compatibility/test-char-id",
            "GET",
            expect_auth_required=True,
        )
        self.test_endpoint(
            "/worlds/therapeutic_world_001/customize",
            "POST",
            {"parameters": {}},
            expect_auth_required=True,
        )

        # Test session management endpoints
        print("\n⏯️ Session Management Endpoints:")
        self.test_endpoint(
            "/sessions/test-session-id/progress",
            "PUT",
            {"progress": 0.5},
            expect_auth_required=True,
        )
        self.test_endpoint(
            "/sessions/test-session-id/pause", "POST", expect_auth_required=True
        )
        self.test_endpoint(
            "/sessions/test-session-id/resume", "POST", expect_auth_required=True
        )

        # Test export endpoints
        print("\n📤 Export Endpoints:")
        self.test_endpoint(
            "/characters/test-char-id/export", "GET", expect_auth_required=True
        )

        # Summary
        successful_tests = sum(1 for result in self.results if result["success"])
        total_tests = len(self.results)

        print("\n" + "=" * 50)
        print(
            f"🎯 API Structure Validation: {successful_tests}/{total_tests} endpoints responding correctly"
        )

        # Check if API is using live databases
        try:
            health_response = self.session.get(f"{API_BASE}/services/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                using_mocks = health_data.get("using_mocks", True)
                print(
                    f"📊 Database Status: {'Mock Services' if using_mocks else 'Live Databases'}"
                )

                # Show service details
                services = health_data.get("services", {})
                for service_name, service_info in services.items():
                    status = service_info.get("status", "unknown")
                    print(f"   - {service_name}: {status}")
        except Exception as e:
            print(f"📊 Database Status: Unable to determine - {str(e)}")

        return self.results

    def test_working_flow(self):
        """Test the parts of the API that are working (registration and login)."""
        print("\n🎮 Testing Working Authentication Flow")
        print("=" * 50)

        # Register a new user
        register_data = {
            "username": f"test_user_{int(datetime.now().timestamp())}",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "password": "TestPassword123!",
            "therapeutic_preferences": {
                "focus_areas": ["anxiety", "social_skills"],
                "intensity_preference": "moderate",
            },
        }

        print("1. Registering new user...")
        register_response = self.session.post(
            f"{API_BASE}/auth/register", json=register_data
        )

        if register_response.status_code in [200, 201]:
            print("   ✅ Registration successful")
            register_response.json()

            # Login with the new user
            print("2. Logging in...")
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"],
            }

            login_response = self.session.post(
                f"{API_BASE}/auth/login", json=login_data
            )

            if login_response.status_code == 200:
                print("   ✅ Login successful")
                auth_data = login_response.json()
                token = auth_data.get("access_token")

                if token:
                    print(f"   ✅ JWT token received (length: {len(token)})")

                    # Try to use the token
                    headers = {"Authorization": f"Bearer {token}"}
                    test_response = self.session.get(
                        f"{API_BASE}/characters/", headers=headers
                    )

                    print("3. Testing token with protected endpoint...")
                    print(f"   Status: {test_response.status_code}")

                    if test_response.status_code == 401:
                        print("   ⚠️ Token verification failed (signature issue)")
                    elif test_response.status_code == 200:
                        print("   ✅ Token working correctly")
                    else:
                        print(f"   ❓ Unexpected response: {test_response.status_code}")

                else:
                    print("   ❌ No token in login response")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")


if __name__ == "__main__":
    validator = APIStructureValidator()

    # Validate API structure
    results = validator.validate_api_structure()

    # Test working authentication flow
    validator.test_working_flow()

    # Save results
    with open("api_structure_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📝 Detailed results saved to api_structure_results.json")
