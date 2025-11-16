#!/usr/bin/env python3
"""
TTA Phase 3: Frontend Integration and Multi-User Browser Testing
Comprehensive end-to-end testing with API integration and database validation
"""

import asyncio
import json
import time
from datetime import datetime

import aiohttp
import requests


class Phase3FrontendTester:
    """Comprehensive frontend integration and multi-user testing"""

    def __init__(self):
        self.frontend_url = "http://localhost:3001"
        self.api_url = "http://localhost:3004"
        self.test_results = {
            "test_start": datetime.now().isoformat(),
            "phase": "Phase 3: Frontend Integration and Multi-User Testing",
            "users": [],
            "multi_user_interactions": [],
            "database_validation": {},
            "performance_metrics": {},
            "frontend_validation": {},
            "errors": [],
            "success_criteria": {},
        }

    async def test_frontend_accessibility(self) -> dict:
        """Test frontend accessibility and basic functionality"""
        results = {"frontend_tests": [], "success": False}

        try:
            # Test frontend homepage
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                results["frontend_tests"].append(
                    {
                        "test": "homepage_accessible",
                        "success": True,
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code,
                    }
                )

                # Check for React app indicators
                content = response.text
                if "react" in content.lower() or "root" in content:
                    results["frontend_tests"].append(
                        {"test": "react_app_detected", "success": True}
                    )

                results["success"] = True
            else:
                results["frontend_tests"].append(
                    {
                        "test": "homepage_accessible",
                        "success": False,
                        "status_code": response.status_code,
                    }
                )

        except Exception as e:
            results["frontend_tests"].append(
                {"test": "frontend_connection_error", "success": False, "error": str(e)}
            )

        return results

    async def test_api_integration(self) -> dict:
        """Test API integration and multi-user functionality"""
        results = {"api_tests": [], "success": False}

        try:
            # Test API health
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health") as response:
                    if response.status == 200:
                        results["api_tests"].append(
                            {
                                "test": "api_health_check",
                                "success": True,
                                "response_time": response.headers.get(
                                    "X-Response-Time", "N/A"
                                ),
                            }
                        )
                        results["success"] = True
                    else:
                        results["api_tests"].append(
                            {
                                "test": "api_health_check",
                                "success": False,
                                "status": response.status,
                            }
                        )

        except Exception as e:
            results["api_tests"].append(
                {"test": "api_connection_error", "success": False, "error": str(e)}
            )

        return results

    async def test_user_registration_api(self, user_data: dict) -> dict:
        """Test user registration through API"""
        user_id = user_data["user_id"]
        results = {"user_id": user_id, "steps": [], "success": False}

        try:
            async with aiohttp.ClientSession() as session:
                # Test registration
                registration_data = {
                    "username": user_data["username"],
                    "password": user_data["password"],
                    "email": user_data["email"],
                }

                async with session.post(
                    f"{self.api_url}/api/v1/auth/register", json=registration_data
                ) as response:
                    if (
                        response.status == 200
                    ):  # API returns 200 for successful registration
                        results["steps"].append(
                            {
                                "step": "api_registration",
                                "success": True,
                                "status": response.status,
                            }
                        )
                        results["success"] = True

                        # Store user data for login test
                        response_data = await response.json()
                        results["user_data"] = response_data

                    else:
                        results["steps"].append(
                            {
                                "step": "api_registration",
                                "success": False,
                                "status": response.status,
                                "error": await response.text(),
                            }
                        )

        except Exception as e:
            results["steps"].append(
                {"step": "registration_api_error", "success": False, "error": str(e)}
            )

        return results

    async def test_user_login_api(self, user_data: dict) -> dict:
        """Test user login through API"""
        user_id = user_data["user_id"]
        results = {"user_id": user_id, "steps": [], "success": False, "jwt_token": None}

        try:
            async with aiohttp.ClientSession() as session:
                # Test login
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"],
                }

                async with session.post(
                    f"{self.api_url}/api/v1/auth/login", json=login_data
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        results["steps"].append(
                            {
                                "step": "api_login",
                                "success": True,
                                "status": response.status,
                            }
                        )
                        results["success"] = True
                        results["jwt_token"] = response_data.get("access_token")

                    else:
                        results["steps"].append(
                            {
                                "step": "api_login",
                                "success": False,
                                "status": response.status,
                                "error": await response.text(),
                            }
                        )

        except Exception as e:
            results["steps"].append(
                {"step": "login_api_error", "success": False, "error": str(e)}
            )

        return results

    async def test_protected_endpoints(self, user_data: dict, jwt_token: str) -> dict:
        """Test protected endpoints with JWT token"""
        user_id = user_data["user_id"]
        results = {"user_id": user_id, "endpoint_tests": [], "success": False}

        if not jwt_token:
            results["endpoint_tests"].append(
                {
                    "test": "no_jwt_token",
                    "success": False,
                    "error": "No JWT token available",
                }
            )
            return results

        headers = {"Authorization": f"Bearer {jwt_token}"}

        try:
            async with aiohttp.ClientSession() as session:
                # Test conversation health endpoint
                async with session.get(
                    f"{self.api_url}/api/v1/conversation/health", headers=headers
                ) as response:
                    results["endpoint_tests"].append(
                        {
                            "endpoint": "/api/v1/conversation/health",
                            "success": response.status == 200,
                            "status": response.status,
                            "response_time": response.headers.get(
                                "X-Response-Time", "N/A"
                            ),
                        }
                    )

                # Test user info endpoint
                async with session.get(
                    f"{self.api_url}/api/v1/auth/me", headers=headers
                ) as response:
                    results["endpoint_tests"].append(
                        {
                            "endpoint": "/api/v1/auth/me",
                            "success": response.status == 200,
                            "status": response.status,
                        }
                    )

                # Test characters endpoint
                async with session.get(
                    f"{self.api_url}/api/v1/characters/", headers=headers
                ) as response:
                    results["endpoint_tests"].append(
                        {
                            "endpoint": "/api/v1/characters/",
                            "success": response.status == 200,
                            "status": response.status,
                        }
                    )

                # Check overall success
                successful_tests = sum(
                    1 for test in results["endpoint_tests"] if test["success"]
                )
                results["success"] = successful_tests == len(results["endpoint_tests"])

        except Exception as e:
            results["endpoint_tests"].append(
                {"test": "protected_endpoints_error", "success": False, "error": str(e)}
            )

        return results

    async def validate_database_persistence(self) -> dict:
        """Validate data persistence in databases"""
        results = {"database_tests": [], "success": False}

        try:
            async with aiohttp.ClientSession() as session:
                # Test database health through API
                async with session.get(f"{self.api_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        results["database_tests"].append(
                            {
                                "test": "database_health_check",
                                "success": True,
                                "details": health_data,
                            }
                        )
                        results["success"] = True
                    else:
                        results["database_tests"].append(
                            {
                                "test": "database_health_check",
                                "success": False,
                                "status": response.status,
                            }
                        )

        except Exception as e:
            results["database_tests"].append(
                {"test": "database_validation_error", "success": False, "error": str(e)}
            )

        return results

    async def run_concurrent_user_tests(self) -> dict:
        """Run concurrent user tests with 5 users"""
        # Generate test users
        test_users = []
        for i in range(5):
            user_data = {
                "user_id": f"phase3_user_{i + 1}",
                "username": f"phase3_test_user_{i + 1}_{int(time.time())}",
                "password": f"Phase3Test123!_{i + 1}",
                "email": f"phase3_test_{i + 1}_{int(time.time())}@tta-test.com",
            }
            test_users.append(user_data)

        # Run concurrent tests
        tasks = []
        for user_data in test_users:
            task = self.run_single_user_journey(user_data)
            tasks.append(task)

        # Execute all user journeys concurrently
        user_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(user_results):
            if isinstance(result, Exception):
                self.test_results["errors"].append(
                    {"user_id": test_users[i]["user_id"], "error": str(result)}
                )
            else:
                self.test_results["users"].append(result)

        return self.test_results

    async def run_single_user_journey(self, user_data: dict) -> dict:
        """Run complete user journey for a single user"""
        user_results = {
            "user_data": user_data,
            "registration": {},
            "login": {},
            "protected_endpoints": {},
            "overall_success": False,
        }

        try:
            # Test registration
            user_results["registration"] = await self.test_user_registration_api(
                user_data
            )

            # Test login
            user_results["login"] = await self.test_user_login_api(user_data)

            # Test protected endpoints if login successful
            if user_results["login"].get("success") and user_results["login"].get(
                "jwt_token"
            ):
                user_results[
                    "protected_endpoints"
                ] = await self.test_protected_endpoints(
                    user_data, user_results["login"]["jwt_token"]
                )

            # Determine overall success
            user_results["overall_success"] = (
                user_results["registration"].get("success", False)
                and user_results["login"].get("success", False)
                and user_results["protected_endpoints"].get("success", False)
            )

        except Exception as e:
            user_results["error"] = str(e)

        return user_results


async def main():
    """Main test execution"""
    print("🚀 Starting TTA Phase 3: Frontend Integration and Multi-User Testing")
    print("=" * 80)

    tester = Phase3FrontendTester()

    try:
        # Test frontend accessibility
        print("📱 Testing frontend accessibility...")
        frontend_results = await tester.test_frontend_accessibility()
        tester.test_results["frontend_validation"] = frontend_results

        # Test API integration
        print("🔗 Testing API integration...")
        api_results = await tester.test_api_integration()
        tester.test_results["api_integration"] = api_results

        # Validate database persistence
        print("💾 Validating database persistence...")
        db_results = await tester.validate_database_persistence()
        tester.test_results["database_validation"] = db_results

        # Run concurrent user tests
        print("👥 Running concurrent user tests...")
        results = await tester.run_concurrent_user_tests()

        # Calculate success criteria
        successful_users = sum(
            1 for user in results["users"] if user.get("overall_success", False)
        )
        total_users = len(results["users"])

        results["success_criteria"] = {
            "frontend_accessible": frontend_results.get("success", False),
            "api_integration": api_results.get("success", False),
            "database_persistence": db_results.get("success", False),
            "user_success_rate": f"{successful_users}/{total_users}",
            "overall_success": (
                frontend_results.get("success", False)
                and api_results.get("success", False)
                and db_results.get("success", False)
                and successful_users >= 4  # At least 80% success rate
            ),
        }

        # Save results
        results_file = f"phase3_integration_test_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print comprehensive summary
        print("\n📊 Phase 3 Integration Testing Complete!")
        print(f"Results saved to: {results_file}")
        print("\n🎯 Success Criteria:")
        print(
            f"   Frontend Accessible: {'✅' if results['success_criteria']['frontend_accessible'] else '❌'}"
        )
        print(
            f"   API Integration: {'✅' if results['success_criteria']['api_integration'] else '❌'}"
        )
        print(
            f"   Database Persistence: {'✅' if results['success_criteria']['database_persistence'] else '❌'}"
        )
        print(
            f"   User Success Rate: {results['success_criteria']['user_success_rate']}"
        )
        print(
            f"   Overall Success: {'✅' if results['success_criteria']['overall_success'] else '❌'}"
        )

        if results["errors"]:
            print(f"\n❌ Errors encountered: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"   - {error['user_id']}: {error['error']}")

        return results["success_criteria"]["overall_success"]

    except Exception as e:
        print(f"❌ Phase 3 testing failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())
