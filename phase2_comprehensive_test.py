#!/usr/bin/env python3
"""
TTA Phase 2: End-to-End User Journey Testing
Comprehensive test suite for validating TTA system functionality
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TTAPhase2Tester:
    def __init__(self, base_url: str = "http://localhost:3004"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        self.auth_token = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, status: str, details: dict[str, Any]):
        """Log test result with timestamp"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }
        self.test_results.append(result)
        logger.info(f"TEST: {test_name} - {status}")
        if details.get("error"):
            logger.error(f"ERROR: {details['error']}")

    async def test_system_health(self):
        """Test basic system health and availability"""
        logger.info("=== Testing System Health ===")

        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "system_health",
                        "PASS",
                        {"status_code": response.status, "response": data},
                    )
                    return True
                self.log_test_result(
                    "system_health",
                    "FAIL",
                    {"status_code": response.status, "error": "Health check failed"},
                )
                return False
        except Exception as e:
            self.log_test_result("system_health", "FAIL", {"error": str(e)})
            return False

    async def test_metrics_endpoint(self):
        """Test Prometheus metrics exposure"""
        logger.info("=== Testing Metrics Endpoint ===")

        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics_data = await response.text()
                    # Check for key metrics
                    has_python_metrics = (
                        "python_gc_objects_collected_total" in metrics_data
                    )
                    has_process_metrics = (
                        "process_resident_memory_bytes" in metrics_data
                    )

                    self.log_test_result(
                        "metrics_endpoint",
                        "PASS",
                        {
                            "status_code": response.status,
                            "has_python_metrics": has_python_metrics,
                            "has_process_metrics": has_process_metrics,
                            "metrics_size": len(metrics_data),
                        },
                    )
                    return True
                self.log_test_result(
                    "metrics_endpoint",
                    "FAIL",
                    {
                        "status_code": response.status,
                        "error": "Metrics endpoint failed",
                    },
                )
                return False
        except Exception as e:
            self.log_test_result("metrics_endpoint", "FAIL", {"error": str(e)})
            return False

    async def test_user_registration(self):
        """Test user registration functionality"""
        logger.info("=== Testing User Registration ===")

        # Test valid registration
        test_user = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test{int(time.time())}@example.com",
            "password": "SecurePass123!",
            "role": "player",
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "user_registration_valid",
                        "PASS",
                        {
                            "status_code": response.status,
                            "response": data,
                            "username": test_user["username"],
                        },
                    )

                    # Store user for login testing
                    self.test_user = test_user
                    return True
                error_data = await response.json()
                self.log_test_result(
                    "user_registration_valid",
                    "FAIL",
                    {"status_code": response.status, "error": error_data},
                )
                return False
        except Exception as e:
            self.log_test_result("user_registration_valid", "FAIL", {"error": str(e)})
            return False

    async def test_user_registration_validation(self):
        """Test user registration input validation"""
        logger.info("=== Testing Registration Validation ===")

        # Test invalid data
        invalid_user = {
            "username": "",
            "email": "invalid-email",
            "password": "weak",
            "role": "player",
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=invalid_user,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status in [400, 422]:  # Expected validation error
                    error_data = await response.json()
                    self.log_test_result(
                        "user_registration_validation",
                        "PASS",
                        {
                            "status_code": response.status,
                            "validation_errors": error_data,
                            "note": "Validation correctly rejected invalid input",
                        },
                    )
                    return True
                self.log_test_result(
                    "user_registration_validation",
                    "FAIL",
                    {
                        "status_code": response.status,
                        "error": "Validation should have failed but didn't",
                    },
                )
                return False
        except Exception as e:
            self.log_test_result(
                "user_registration_validation", "FAIL", {"error": str(e)}
            )
            return False

    async def test_user_authentication(self):
        """Test user login functionality"""
        logger.info("=== Testing User Authentication ===")

        if not hasattr(self, "test_user"):
            self.log_test_result(
                "user_authentication",
                "SKIP",
                {"reason": "No test user available from registration"},
            )
            return False

        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "access_token" in data:
                        self.auth_token = data["access_token"]
                        self.log_test_result(
                            "user_authentication",
                            "PASS",
                            {
                                "status_code": response.status,
                                "has_token": True,
                                "token_type": data.get("token_type", "unknown"),
                            },
                        )
                        return True
                    self.log_test_result(
                        "user_authentication",
                        "FAIL",
                        {
                            "status_code": response.status,
                            "error": "No access token in response",
                            "response": data,
                        },
                    )
                    return False
                error_data = await response.json()
                self.log_test_result(
                    "user_authentication",
                    "FAIL",
                    {
                        "status_code": response.status,
                        "error": error_data,
                        "note": "Authentication failed - possible database connectivity issue",
                    },
                )
                return False
        except Exception as e:
            self.log_test_result("user_authentication", "FAIL", {"error": str(e)})
            return False

    async def test_protected_endpoints(self):
        """Test protected endpoints with authentication"""
        logger.info("=== Testing Protected Endpoints ===")

        if not self.auth_token:
            self.log_test_result(
                "protected_endpoints",
                "SKIP",
                {"reason": "No authentication token available"},
            )
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test conversation health endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/conversation/health", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "conversation_health_protected",
                        "PASS",
                        {"status_code": response.status, "response": data},
                    )
                else:
                    error_data = await response.json()
                    self.log_test_result(
                        "conversation_health_protected",
                        "FAIL",
                        {"status_code": response.status, "error": error_data},
                    )
                    return False
        except Exception as e:
            self.log_test_result(
                "conversation_health_protected", "FAIL", {"error": str(e)}
            )
            return False

        # Test character listing endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/characters/", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.text()
                    self.log_test_result(
                        "character_list_protected",
                        "PASS",
                        {
                            "status_code": response.status,
                            "response_preview": data[:200] if len(data) > 200 else data,
                        },
                    )
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "character_list_protected",
                        "FAIL",
                        {"status_code": response.status, "error": error_data},
                    )
                    return False
        except Exception as e:
            self.log_test_result("character_list_protected", "FAIL", {"error": str(e)})
            return False

        # Test user info endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/auth/me", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "user_info_protected",
                        "PASS",
                        {"status_code": response.status, "user_data": data},
                    )
                    return True
                error_data = await response.json()
                self.log_test_result(
                    "user_info_protected",
                    "FAIL",
                    {"status_code": response.status, "error": error_data},
                )
                return False
        except Exception as e:
            self.log_test_result("user_info_protected", "FAIL", {"error": str(e)})
            return False

    async def test_database_connectivity(self):
        """Test database connectivity indirectly through API responses"""
        logger.info("=== Testing Database Connectivity ===")

        # Test Redis connectivity by checking if registration persists
        # Test Neo4j connectivity by checking user retrieval

        # This is indirect testing since we don't have direct DB access
        # We infer connectivity from API behavior

        registration_works = hasattr(self, "test_user")
        auth_works = self.auth_token is not None

        self.log_test_result(
            "database_connectivity",
            "PARTIAL",
            {
                "registration_persists": registration_works,
                "authentication_works": auth_works,
                "note": "Indirect testing through API behavior",
                "recommendation": "Direct database connectivity testing needed",
            },
        )

        return registration_works

    async def run_all_tests(self):
        """Run all Phase 2 tests"""
        logger.info("Starting TTA Phase 2: End-to-End User Journey Testing")
        start_time = time.time()

        # Test sequence
        tests = [
            self.test_system_health,
            self.test_metrics_endpoint,
            self.test_user_registration,
            self.test_user_registration_validation,
            self.test_user_authentication,
            self.test_protected_endpoints,
            self.test_database_connectivity,
        ]

        passed = 0
        failed = 0
        skipped = 0

        for test in tests:
            try:
                result = await test()
                if result is True:
                    passed += 1
                elif result is False:
                    failed += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
                failed += 1

        end_time = time.time()
        duration = end_time - start_time

        # Generate summary
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "success_rate": (passed / len(tests)) * 100 if len(tests) > 0 else 0,
        }

        logger.info("=== TEST SUMMARY ===")
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Skipped: {summary['skipped']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Duration: {summary['duration_seconds']:.2f} seconds")

        return {"summary": summary, "detailed_results": self.test_results}


async def main():
    """Main test execution"""
    async with TTAPhase2Tester() as tester:
        results = await tester.run_all_tests()

        # Save results to file
        with open("phase2_test_results.json", "w") as f:
            json.dump(results, f, indent=2)

        logger.info("Test results saved to phase2_test_results.json")

        # Exit with appropriate code
        if results["summary"]["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
