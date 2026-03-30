#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Player_experience/Test_deployment]]
Player Experience Interface Deployment Validation Tests

This script validates that the Player Experience Interface deployment is working correctly
by testing all major endpoints and functionality.

Usage:
    python test_deployment.py [--host HOST] [--port PORT] [--environment ENV]
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Any

import requests
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentValidator:
    """Validates Player Experience Interface deployment."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        environment: str = "development",
    ):
        self.host = host
        self.port = port
        self.environment = environment
        # Use secure protocols in production environments
        if environment in ["production", "staging"]:
            self.base_url = f"https://{host}:{port}"
            self.ws_url = f"wss://{host}:{port}"
        else:
            self.base_url = f"http://{host}:{port}"
            # nosemgrep: javascript.lang.security.detect-insecure-websocket.detect-insecure-websocket
            self.ws_url = f"ws://{host}:{port}"
        self.session = requests.Session()
        self.test_results: list[dict[str, Any]] = []

    def log_test_result(
        self,
        test_name: str,
        success: bool,
        message: str = "",
        details: dict[str, Any] | None = None,
    ):
        """Log a test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")

        if not success and details:
            logger.error(f"Details: {json.dumps(details, indent=2)}")

    def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                health_data = response.json()
                self.log_test_result(
                    "Health Endpoint", True, "Service is healthy", health_data
                )
                return True
            self.log_test_result(
                "Health Endpoint",
                False,
                f"Health check failed with status {response.status_code}",
                {"status_code": response.status_code, "response": response.text},
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Health Endpoint",
                False,
                f"Health check failed with exception: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_api_documentation(self) -> bool:
        """Test that API documentation is accessible."""
        try:
            # Test OpenAPI/Swagger docs
            response = self.session.get(f"{self.base_url}/docs", timeout=10)

            if response.status_code == 200:
                self.log_test_result(
                    "API Documentation", True, "API documentation is accessible"
                )
                return True
            self.log_test_result(
                "API Documentation",
                False,
                f"API docs not accessible, status: {response.status_code}",
            )
            return False

        except Exception as e:
            self.log_test_result(
                "API Documentation", False, f"API docs check failed: {str(e)}"
            )
            return False

    def test_player_management_endpoints(self) -> bool:
        """Test player management API endpoints."""
        try:
            # Test creating a player profile
            player_data = {
                "username": "test_player_deployment",
                "email": "test@example.com",
                "therapeutic_preferences": {
                    "intensity_level": "medium",
                    "preferred_approaches": ["CBT"],
                    "trigger_warnings": ["violence"],
                    "session_duration_preference": 45,
                },
            }

            # Create player
            response = self.session.post(
                f"{self.base_url}/api/v1/players", json=player_data, timeout=10
            )

            if response.status_code == 201:
                player = response.json()
                player_id = player.get("player_id")

                # Test getting player
                get_response = self.session.get(
                    f"{self.base_url}/api/v1/players/{player_id}", timeout=10
                )

                if get_response.status_code == 200:
                    # Clean up - delete player
                    self.session.delete(f"{self.base_url}/api/v1/players/{player_id}")

                    self.log_test_result(
                        "Player Management API",
                        True,
                        "Player CRUD operations working correctly",
                    )
                    return True
                self.log_test_result(
                    "Player Management API",
                    False,
                    f"Failed to retrieve created player, status: {get_response.status_code}",
                )
                return False
            self.log_test_result(
                "Player Management API",
                False,
                f"Failed to create player, status: {response.status_code}",
                {"response": response.text},
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Player Management API",
                False,
                f"Player management test failed: {str(e)}",
            )
            return False

    def test_character_management_endpoints(self) -> bool:
        """Test character management API endpoints."""
        try:
            # First create a player
            player_data = {
                "username": "test_char_player",
                "email": "testchar@example.com",
            }

            player_response = self.session.post(
                f"{self.base_url}/api/v1/players", json=player_data, timeout=10
            )

            if player_response.status_code != 201:
                self.log_test_result(
                    "Character Management API",
                    False,
                    "Failed to create test player for character tests",
                )
                return False

            player_id = player_response.json()["player_id"]

            # Create character
            character_data = {
                "name": "Test Character",
                "appearance": {
                    "age_range": "adult",
                    "gender_identity": "non-binary",
                    "physical_description": "Test description",
                },
                "background": {
                    "backstory": "Test backstory",
                    "personality_traits": ["brave", "kind"],
                },
            }

            char_response = self.session.post(
                f"{self.base_url}/api/v1/players/{player_id}/characters",
                json=character_data,
                timeout=10,
            )

            if char_response.status_code == 201:
                character = char_response.json()
                character_id = character.get("character_id")

                # Test getting character
                get_response = self.session.get(
                    f"{self.base_url}/api/v1/players/{player_id}/characters/{character_id}",
                    timeout=10,
                )

                success = get_response.status_code == 200

                # Clean up
                self.session.delete(f"{self.base_url}/api/v1/players/{player_id}")

                self.log_test_result(
                    "Character Management API",
                    success,
                    (
                        "Character CRUD operations working correctly"
                        if success
                        else "Character retrieval failed"
                    ),
                )
                return success
            # Clean up player
            self.session.delete(f"{self.base_url}/api/v1/players/{player_id}")

            self.log_test_result(
                "Character Management API",
                False,
                f"Failed to create character, status: {char_response.status_code}",
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Character Management API",
                False,
                f"Character management test failed: {str(e)}",
            )
            return False

    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection and basic messaging."""
        try:
            uri = f"{self.ws_url}/ws/chat"

            async with websockets.connect(uri) as websocket:
                # Send a test message
                test_message = {
                    "type": "chat_message",
                    "content": "Hello, this is a deployment test",
                    "player_id": "test_player",
                    "character_id": "test_character",
                }

                await websocket.send(json.dumps(test_message))

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)

                if response_data.get("type") == "assistant_response":
                    self.log_test_result(
                        "WebSocket Connection",
                        True,
                        "WebSocket connection and messaging working correctly",
                    )
                    return True
                self.log_test_result(
                    "WebSocket Connection",
                    False,
                    f"Unexpected WebSocket response: {response_data}",
                )
                return False

        except Exception as e:
            self.log_test_result(
                "WebSocket Connection", False, f"WebSocket test failed: {str(e)}"
            )
            return False

    def test_database_connectivity(self) -> bool:
        """Test database connectivity through health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health/detailed", timeout=10)

            if response.status_code == 200:
                health_data = response.json()

                # Check database connections
                redis_ok = health_data.get("redis", {}).get("status") == "healthy"
                neo4j_ok = health_data.get("neo4j", {}).get("status") == "healthy"

                if redis_ok and neo4j_ok:
                    self.log_test_result(
                        "Database Connectivity",
                        True,
                        "All database connections are healthy",
                    )
                    return True
                self.log_test_result(
                    "Database Connectivity",
                    False,
                    f"Database connectivity issues - Redis: {redis_ok}, Neo4j: {neo4j_ok}",
                    health_data,
                )
                return False
            self.log_test_result(
                "Database Connectivity",
                False,
                f"Failed to get detailed health status: {response.status_code}",
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Database Connectivity",
                False,
                f"Database connectivity test failed: {str(e)}",
            )
            return False

    def test_security_headers(self) -> bool:
        """Test that proper security headers are present."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            headers = response.headers

            # Check for important security headers
            security_checks = {
                "X-Content-Type-Options": headers.get("X-Content-Type-Options")
                == "nosniff",
                "X-Frame-Options": "X-Frame-Options" in headers,
                "X-XSS-Protection": "X-XSS-Protection" in headers,
            }

            # For production, also check HTTPS-related headers
            if self.environment == "production":
                security_checks["Strict-Transport-Security"] = (
                    "Strict-Transport-Security" in headers
                )

            passed_checks = sum(security_checks.values())
            total_checks = len(security_checks)

            success = passed_checks >= (
                total_checks * 0.7
            )  # At least 70% of checks should pass

            self.log_test_result(
                "Security Headers",
                success,
                f"Security headers check: {passed_checks}/{total_checks} passed",
                security_checks,
            )
            return success

        except Exception as e:
            self.log_test_result(
                "Security Headers", False, f"Security headers test failed: {str(e)}"
            )
            return False

    def test_performance_metrics(self) -> bool:
        """Test basic performance metrics."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time

            # Response time should be under 2 seconds for health endpoint
            performance_ok = response_time < 2.0 and response.status_code == 200

            self.log_test_result(
                "Performance Metrics",
                performance_ok,
                f"Health endpoint response time: {response_time:.3f}s",
                {"response_time": response_time, "threshold": 2.0},
            )
            return performance_ok

        except Exception as e:
            self.log_test_result(
                "Performance Metrics", False, f"Performance test failed: {str(e)}"
            )
            return False

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all deployment validation tests."""
        logger.info(
            f"Starting deployment validation for {self.environment} environment"
        )
        logger.info(f"Testing endpoint: {self.base_url}")

        # Run synchronous tests
        sync_tests = [
            self.test_health_endpoint,
            self.test_api_documentation,
            self.test_player_management_endpoints,
            self.test_character_management_endpoints,
            self.test_database_connectivity,
            self.test_security_headers,
            self.test_performance_metrics,
        ]

        for test in sync_tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")

        # Run async tests
        try:
            await self.test_websocket_connection()
        except Exception as e:
            logger.error(f"WebSocket test failed with exception: {e}")

        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        return {
            "environment": self.environment,
            "endpoint": self.base_url,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "overall_success": success_rate >= 80,  # 80% pass rate required
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
        }

    def print_summary(self, summary: dict[str, Any]):
        """Print test summary."""

        (
            "✅ DEPLOYMENT SUCCESSFUL"
            if summary["overall_success"]
            else "❌ DEPLOYMENT FAILED"
        )

        if not summary["overall_success"]:
            for result in summary["test_results"]:
                if not result["success"]:
                    pass


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate Player Experience Interface deployment"
    )
    parser.add_argument(
        "--host", default="localhost", help="API host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="API port (default: 8080)"
    )
    parser.add_argument(
        "--environment",
        default="development",
        choices=["development", "staging", "production"],
        help="Environment being tested (default: development)",
    )
    parser.add_argument("--output", help="Output file for test results (JSON format)")

    args = parser.parse_args()

    # Create validator and run tests
    validator = DeploymentValidator(args.host, args.port, args.environment)
    summary = await validator.run_all_tests()

    # Print summary
    validator.print_summary(summary)

    # Save results if output file specified
    if args.output:
        with open(args.output, "w") as f:  # noqa: PTH123
            json.dump(summary, f, indent=2)
        logger.info(f"Test results saved to {args.output}")

    # Exit with appropriate code
    sys.exit(0 if summary["overall_success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
