#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Test_api_endpoints]]
API Endpoint Testing Script for TTA Core Gameplay Loop Integration

This script performs comprehensive testing of the gameplay API endpoints
to validate the frontend-to-backend integration.
"""

import asyncio
import logging
import sys

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GameplayAPITester:
    """Comprehensive API tester for the TTA Gameplay Loop integration."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession | None = None
        self.auth_token: str | None = None
        self.session_id: str | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_headers(self) -> dict[str, str]:
        """Get headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def authenticate(self) -> bool:
        """Authenticate and get a valid JWT token."""
        logger.info("🔐 Authenticating user...")

        # Try multiple test user credentials
        test_credentials = [
            {"username": "demo_user", "password": "demo_password"},
            {"username": "testuser", "password": "testpass"},
            {"username": "api_test_user", "password": "TestPassword123!"},
        ]

        # First, try to register a test user (in case it doesn't exist)
        try:
            register_payload = {
                "username": "api_test_user",
                "email": "apitest@example.com",
                "password": "TestPassword123!",
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                headers={"Content-Type": "application/json"},
                json=register_payload,
            ) as response:
                if response.status == 200:
                    logger.info("✅ Test user registered successfully")
                elif response.status == 400:
                    # User might already exist, that's okay
                    logger.info("ℹ️  Test user already exists, proceeding to login")
                else:
                    logger.warning(f"⚠️  Registration returned {response.status}")
        except Exception as e:
            logger.warning(f"⚠️  Registration failed: {e}")

        # Now try to login with different credentials
        for credentials in test_credentials:
            try:
                logger.info(f"🔑 Trying credentials: {credentials['username']}")
                login_payload = credentials

                async with self.session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    headers={"Content-Type": "application/json"},
                    json=login_payload,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("access_token") or data.get("token")
                        logger.info(
                            f"✅ Authentication successful with {credentials['username']}"
                        )
                        return True
                    await response.text()
                    logger.warning(
                        f"⚠️  Login failed for {credentials['username']}: {response.status}"
                    )
                    continue  # Try next credentials
            except Exception as e:
                logger.warning(
                    f"⚠️  Authentication error for {credentials['username']}: {e}"
                )
                continue  # Try next credentials

        logger.error("❌ All authentication attempts failed")
        return False

    async def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        logger.info("🔍 Testing health endpoint...")
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/health", headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data}")
                    return True
                logger.error(f"❌ Health check failed: {response.status}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False

    async def test_create_session(self) -> bool:
        """Test session creation."""
        logger.info("🔍 Testing session creation...")
        try:
            payload = {
                "therapeutic_context": {
                    "goals": ["anxiety_management", "social_skills"]
                }
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/gameplay/sessions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.session_id = data.get("session_id")
                    logger.info(f"✅ Session created: {self.session_id}")
                    return True
                error_data = await response.text()
                logger.error(
                    f"❌ Session creation failed: {response.status} - {error_data}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            return False

    async def test_get_session_status(self) -> bool:
        """Test getting session status."""
        if not self.session_id:
            logger.error("❌ No session ID available for status test")
            return False

        logger.info("🔍 Testing session status retrieval...")
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/sessions/{self.session_id}",
                headers=self._get_headers(),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(
                        f"✅ Session status retrieved: {data.get('session_status', {}).get('is_active', 'unknown')}"
                    )
                    return True
                error_data = await response.text()
                logger.error(
                    f"❌ Session status failed: {response.status} - {error_data}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Session status error: {e}")
            return False

    async def test_process_choice(self) -> bool:
        """Test choice processing."""
        if not self.session_id:
            logger.error("❌ No session ID available for choice test")
            return False

        logger.info("🔍 Testing choice processing...")
        try:
            payload = {"choice_id": "test_choice_001"}

            async with self.session.post(
                f"{self.base_url}/api/v1/gameplay/sessions/{self.session_id}/choices",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                if response.status == 200:
                    await response.json()
                    logger.info("✅ Choice processed successfully")
                    return True
                error_data = await response.text()
                logger.error(
                    f"❌ Choice processing failed: {response.status} - {error_data}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Choice processing error: {e}")
            return False

    async def test_get_progress(self) -> bool:
        """Test progress retrieval."""
        if not self.session_id:
            logger.error("❌ No session ID available for progress test")
            return False

        logger.info("🔍 Testing progress retrieval...")
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/sessions/{self.session_id}/progress",
                headers=self._get_headers(),
            ) as response:
                if response.status == 200:
                    await response.json()
                    logger.info("✅ Progress retrieved successfully")
                    return True
                error_data = await response.text()
                logger.error(
                    f"❌ Progress retrieval failed: {response.status} - {error_data}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Progress retrieval error: {e}")
            return False

    async def test_end_session(self) -> bool:
        """Test session termination."""
        if not self.session_id:
            logger.error("❌ No session ID available for termination test")
            return False

        logger.info("🔍 Testing session termination...")
        try:
            async with self.session.delete(
                f"{self.base_url}/api/v1/gameplay/sessions/{self.session_id}",
                headers=self._get_headers(),
            ) as response:
                if response.status == 200:
                    await response.json()
                    logger.info("✅ Session terminated successfully")
                    return True
                error_data = await response.text()
                logger.error(
                    f"❌ Session termination failed: {response.status} - {error_data}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Session termination error: {e}")
            return False

    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests."""
        logger.info("🔍 Testing error handling...")

        # Test invalid session ID
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/sessions/invalid_session_id",
                headers=self._get_headers(),
            ) as response:
                if response.status == 404:
                    logger.info(
                        "✅ Error handling works: Invalid session ID returns 404"
                    )
                    return True
                logger.error(
                    f"❌ Error handling failed: Expected 404, got {response.status}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Error handling test error: {e}")
            return False

    async def run_comprehensive_test(self) -> dict[str, bool]:
        """Run all tests and return results."""
        logger.info("🚀 Starting comprehensive API testing...")

        results = {}

        # First authenticate
        auth_success = await self.authenticate()
        results["authentication"] = auth_success

        if not auth_success:
            logger.error("❌ Authentication failed, skipping other tests")
            return results

        # Test sequence
        test_sequence = [
            ("health_check", self.test_health_endpoint),
            ("create_session", self.test_create_session),
            ("get_session_status", self.test_get_session_status),
            ("process_choice", self.test_process_choice),
            ("get_progress", self.test_get_progress),
            ("error_handling", self.test_error_handling),
            ("end_session", self.test_end_session),
        ]

        for test_name, test_func in test_sequence:
            logger.info(f"\n--- Running {test_name} ---")
            results[test_name] = await test_func()

            # Add delay between tests
            await asyncio.sleep(1)

        return results


async def main():
    """Main test execution."""
    logger.info("🎮 TTA Core Gameplay Loop - API Integration Testing")
    logger.info("=" * 60)

    async with GameplayAPITester() as tester:
        results = await tester.run_comprehensive_test()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)

        passed = 0
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name:20} : {status}")
            if result:
                passed += 1

        logger.info("-" * 60)
        logger.info(
            f"TOTAL: {passed}/{total} tests passed ({passed / total * 100:.1f}%)"
        )

        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! Integration is working correctly.")
            return 0
        logger.error("⚠️  Some tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
