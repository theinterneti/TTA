#!/usr/bin/env python3
"""
Phase 2: Frontend Analytics Integration Test
Validates complete frontend-to-backend analytics pipeline
"""

import asyncio
import sys
import time

import aiohttp


class Phase2IntegrationTester:
    def __init__(self):
        self.api_base = "http://localhost:3004"
        self.frontend_base = "http://localhost:3001"
        self.grafana_base = "http://localhost:3003"
        self.health_check_base = "http://localhost:8090"

        self.test_results = []
        self.auth_token = None
        self.test_user_id = None

    async def run_complete_test_suite(self):
        """Run complete Phase 2 integration test suite"""
        print("🚀 Phase 2: Frontend Analytics Integration Test")
        print("=" * 60)

        async with aiohttp.ClientSession() as session:
            # Test 1: Validate Phase 1 Infrastructure
            await self.test_phase1_infrastructure(session)

            # Test 2: Test API Endpoints
            await self.test_analytics_api_endpoints(session)

            # Test 3: Test Frontend Accessibility
            await self.test_frontend_accessibility(session)

            # Test 4: Test Grafana Dashboard Integration
            await self.test_grafana_dashboard_integration(session)

            # Test 5: Test Real-time Data Flow
            await self.test_realtime_data_flow(session)

            # Test 6: Test Complete User Journey
            await self.test_complete_user_journey(session)

        # Generate test report
        self.generate_test_report()

        return all(result["success"] for result in self.test_results)

    async def test_phase1_infrastructure(self, session: aiohttp.ClientSession):
        """Test that Phase 1 infrastructure is operational"""
        print("\n📊 Testing Phase 1 Infrastructure...")

        tests = [
            ("Health Check Service", f"{self.health_check_base}/health"),
            ("Prometheus Metrics", f"{self.health_check_base}/metrics"),
            ("Grafana Health", f"{self.grafana_base}/api/health"),
            ("Player API Health", f"{self.api_base}/"),
            ("Frontend Accessibility", f"{self.frontend_base}/"),
        ]

        for test_name, url in tests:
            try:
                async with session.get(url, timeout=10) as response:
                    success = response.status == 200
                    self.test_results.append(
                        {
                            "test": f"Phase1 - {test_name}",
                            "success": success,
                            "status_code": response.status,
                            "response_time": time.time(),
                            "details": f"Status: {response.status}",
                        }
                    )
                    print(
                        f"  {'✅' if success else '❌'} {test_name}: {response.status}"
                    )
            except Exception as e:
                self.test_results.append(
                    {
                        "test": f"Phase1 - {test_name}",
                        "success": False,
                        "error": str(e),
                        "details": f"Connection failed: {e}",
                    }
                )
                print(f"  ❌ {test_name}: Connection failed - {e}")

    async def test_analytics_api_endpoints(self, session: aiohttp.ClientSession):
        """Test analytics API endpoints with authentication"""
        print("\n🔗 Testing Analytics API Endpoints...")

        # First, get auth token (using test credentials)
        auth_success = await self.authenticate_test_user(session)
        if not auth_success:
            print("  ❌ Authentication failed - skipping API tests")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test analytics endpoints
        endpoints = [
            (
                "Progress Visualization",
                f"/api/v1/players/{self.test_user_id}/progress/viz?days=14",
            ),
            ("Player Dashboard", f"/api/v1/players/{self.test_user_id}/dashboard"),
            ("Player Progress", f"/api/v1/players/{self.test_user_id}/progress"),
            ("Player Analytics", "/api/v1/conversation/player/analytics"),
        ]

        for test_name, endpoint in endpoints:
            try:
                async with session.get(
                    f"{self.api_base}{endpoint}", headers=headers, timeout=10
                ) as response:
                    success = response.status == 200
                    if success:
                        data = await response.json()
                        self.test_results.append(
                            {
                                "test": f"API - {test_name}",
                                "success": True,
                                "status_code": response.status,
                                "data_keys": list(data.keys())
                                if isinstance(data, dict)
                                else "non-dict",
                                "details": f"Returned {len(data) if isinstance(data, (dict, list)) else 'unknown'} items",
                            }
                        )
                        print(f"  ✅ {test_name}: {response.status} - Data received")
                    else:
                        self.test_results.append(
                            {
                                "test": f"API - {test_name}",
                                "success": False,
                                "status_code": response.status,
                                "details": f"HTTP {response.status}",
                            }
                        )
                        print(f"  ❌ {test_name}: {response.status}")
            except Exception as e:
                self.test_results.append(
                    {
                        "test": f"API - {test_name}",
                        "success": False,
                        "error": str(e),
                        "details": f"Request failed: {e}",
                    }
                )
                print(f"  ❌ {test_name}: {e}")

    async def test_frontend_accessibility(self, session: aiohttp.ClientSession):
        """Test frontend accessibility and routing"""
        print("\n🌐 Testing Frontend Accessibility...")

        routes = [
            ("Main App", "/"),
            ("Dashboard", "/dashboard"),
            ("Analytics Page", "/analytics"),
            ("Login Page", "/login"),
        ]

        for test_name, route in routes:
            try:
                async with session.get(
                    f"{self.frontend_base}{route}", timeout=10
                ) as response:
                    success = response.status == 200
                    content = await response.text()

                    # Check for React app indicators
                    has_react = "react" in content.lower() or "root" in content

                    self.test_results.append(
                        {
                            "test": f"Frontend - {test_name}",
                            "success": success and has_react,
                            "status_code": response.status,
                            "has_react_content": has_react,
                            "details": f"Status: {response.status}, React content: {has_react}",
                        }
                    )
                    print(
                        f"  {'✅' if success and has_react else '❌'} {test_name}: {response.status} {'(React app)' if has_react else ''}"
                    )
            except Exception as e:
                self.test_results.append(
                    {
                        "test": f"Frontend - {test_name}",
                        "success": False,
                        "error": str(e),
                        "details": f"Request failed: {e}",
                    }
                )
                print(f"  ❌ {test_name}: {e}")

    async def test_grafana_dashboard_integration(self, session: aiohttp.ClientSession):
        """Test Grafana dashboard integration"""
        print("\n📈 Testing Grafana Dashboard Integration...")

        auth = aiohttp.BasicAuth("admin", "tta-admin-2024")

        tests = [
            ("Grafana Authentication", "/api/health"),
            ("Dashboard List", "/api/search?type=dash-db"),
            ("TTA System Overview", "/api/dashboards/uid/tta-system-overview"),
            ("Prometheus Data Source", "/api/datasources"),
            (
                "TTA Metrics Query",
                "/api/datasources/proxy/1/api/v1/query?query=tta_service_up",
            ),
        ]

        for test_name, endpoint in tests:
            try:
                async with session.get(
                    f"{self.grafana_base}{endpoint}", auth=auth, timeout=10
                ) as response:
                    success = response.status == 200
                    if success and endpoint.endswith("tta_service_up"):
                        data = await response.json()
                        has_metrics = "data" in data and "result" in data["data"]
                        success = success and has_metrics
                        details = f"Metrics available: {has_metrics}"
                    else:
                        details = f"Status: {response.status}"

                    self.test_results.append(
                        {
                            "test": f"Grafana - {test_name}",
                            "success": success,
                            "status_code": response.status,
                            "details": details,
                        }
                    )
                    print(
                        f"  {'✅' if success else '❌'} {test_name}: {response.status}"
                    )
            except Exception as e:
                self.test_results.append(
                    {
                        "test": f"Grafana - {test_name}",
                        "success": False,
                        "error": str(e),
                        "details": f"Request failed: {e}",
                    }
                )
                print(f"  ❌ {test_name}: {e}")

    async def test_realtime_data_flow(self, session: aiohttp.ClientSession):
        """Test real-time data flow from health check to Grafana"""
        print("\n⚡ Testing Real-time Data Flow...")

        try:
            # Get current metrics from health check service
            async with session.get(
                f"{self.health_check_base}/metrics", timeout=10
            ) as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    has_tta_metrics = "tta_service_up" in metrics_text

                    self.test_results.append(
                        {
                            "test": "Data Flow - Health Check Metrics",
                            "success": has_tta_metrics,
                            "details": f"TTA metrics present: {has_tta_metrics}",
                        }
                    )
                    print(
                        f"  {'✅' if has_tta_metrics else '❌'} Health Check Metrics: TTA metrics {'found' if has_tta_metrics else 'missing'}"
                    )

                    if has_tta_metrics:
                        # Wait a moment for Prometheus to scrape
                        await asyncio.sleep(2)

                        # Check if Prometheus has the data
                        auth = aiohttp.BasicAuth("admin", "tta-admin-2024")
                        async with session.get(
                            f"{self.grafana_base}/api/datasources/proxy/1/api/v1/query?query=tta_service_up",
                            auth=auth,
                            timeout=10,
                        ) as prom_response:
                            if prom_response.status == 200:
                                prom_data = await prom_response.json()
                                has_prom_data = (
                                    "data" in prom_data
                                    and len(prom_data["data"].get("result", [])) > 0
                                )

                                self.test_results.append(
                                    {
                                        "test": "Data Flow - Prometheus Query",
                                        "success": has_prom_data,
                                        "details": f"Prometheus data available: {has_prom_data}",
                                    }
                                )
                                print(
                                    f"  {'✅' if has_prom_data else '❌'} Prometheus Query: Data {'available' if has_prom_data else 'missing'}"
                                )
                            else:
                                print(
                                    f"  ❌ Prometheus Query: HTTP {prom_response.status}"
                                )
                else:
                    print(f"  ❌ Health Check Metrics: HTTP {response.status}")
        except Exception as e:
            print(f"  ❌ Real-time Data Flow: {e}")

    async def test_complete_user_journey(self, session: aiohttp.ClientSession):
        """Test complete user journey through analytics"""
        print("\n👤 Testing Complete User Journey...")

        if not self.auth_token:
            print("  ❌ No auth token available - skipping user journey test")
            return

        # Simulate user accessing analytics data
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        journey_steps = [
            ("Get Dashboard Data", f"/api/v1/players/{self.test_user_id}/dashboard"),
            (
                "Get Progress Visualization",
                f"/api/v1/players/{self.test_user_id}/progress/viz?days=7",
            ),
            ("Get Session Analytics", "/api/v1/conversation/player/analytics"),
        ]

        journey_success = True
        for step_name, endpoint in journey_steps:
            try:
                async with session.get(
                    f"{self.api_base}{endpoint}", headers=headers, timeout=10
                ) as response:
                    success = response.status == 200
                    if not success:
                        journey_success = False
                    print(
                        f"  {'✅' if success else '❌'} {step_name}: {response.status}"
                    )
            except Exception as e:
                journey_success = False
                print(f"  ❌ {step_name}: {e}")

        self.test_results.append(
            {
                "test": "User Journey - Complete Analytics Flow",
                "success": journey_success,
                "details": f"All steps {'completed' if journey_success else 'failed'}",
            }
        )

    async def authenticate_test_user(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate test user and get token"""
        try:
            # Try to register a test user first
            register_data = {
                "username": f"test_user_{int(time.time())}",
                "password": "test_password_123",
                "email": f"test_{int(time.time())}@example.com",
            }

            async with session.post(
                f"{self.api_base}/api/v1/auth/register", json=register_data, timeout=10
            ) as response:
                if response.status == 200:
                    reg_data = await response.json()
                    self.auth_token = reg_data.get("access_token")
                    self.test_user_id = reg_data.get("player_id")
                    return True
                print(f"  ⚠️  Registration failed: {response.status}")
                return False
        except Exception as e:
            print(f"  ⚠️  Authentication error: {e}")
            return False

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 PHASE 2 INTEGRATION TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests

        print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
        print(f"❌ Failed Tests: {failed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(successful_tests / total_tests) * 100:.1f}%")

        if failed_tests > 0:
            print("\n⚠️  Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(
                        f"  - {result['test']}: {result.get('details', result.get('error', 'Unknown error'))}"
                    )

        # Test categories summary
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"total": 0, "success": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["success"] += 1

        print("\n📋 Test Categories:")
        for category, stats in categories.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            print(
                f"  {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)"
            )

        # Overall assessment
        if successful_tests == total_tests:
            print("\n🎉 PHASE 2: FRONTEND ANALYTICS INTEGRATION - COMPLETE")
            print("All tests passed! The analytics pipeline is fully operational.")
        elif successful_tests >= total_tests * 0.8:
            print("\n✅ PHASE 2: FRONTEND ANALYTICS INTEGRATION - MOSTLY COMPLETE")
            print("Most tests passed. Minor issues may need attention.")
        else:
            print("\n⚠️  PHASE 2: FRONTEND ANALYTICS INTEGRATION - NEEDS ATTENTION")
            print("Several tests failed. Please review and fix issues.")

        print("\n🌐 Access Points:")
        print(f"  - Frontend: {self.frontend_base}")
        print(f"  - Analytics Page: {self.frontend_base}/analytics")
        print(f"  - Grafana Dashboards: {self.grafana_base}")
        print(f"  - API Documentation: {self.api_base}/docs")


async def main():
    tester = Phase2IntegrationTester()
    success = await tester.run_complete_test_suite()
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
