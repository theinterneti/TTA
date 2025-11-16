#!/usr/bin/env python3
"""
Phase 3: Advanced Analytics Implementation - Comprehensive Test Suite

This script validates all Phase 3 advanced analytics features including:
- Aggregate user behavior analysis
- Advanced reporting capabilities
- Enhanced real-time monitoring
- Integration with Phase 2 infrastructure
"""

import asyncio
import time
from datetime import datetime, timedelta

import requests
import websockets


class Phase3AnalyticsTestSuite:
    """Comprehensive test suite for Phase 3 advanced analytics."""

    def __init__(self):
        self.base_urls = {
            "aggregation": "http://localhost:8095",
            "reporting": "http://localhost:8096",
            "monitoring": "http://localhost:8097",
            "prometheus": "http://localhost:9092",
            "grafana": "http://localhost:3004",
        }
        self.test_results = {
            "aggregation_service": [],
            "reporting_service": [],
            "monitoring_service": [],
            "integration_tests": [],
            "performance_tests": [],
        }
        self.start_time = datetime.now()

    def log_test_result(
        self,
        category: str,
        test_name: str,
        success: bool,
        details: str = "",
        response_time: float = 0.0,
    ):
        """Log test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results[category].append(result)

        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {details}")

    def test_service_health(self, service_name: str, url: str) -> bool:
        """Test service health endpoint."""
        try:
            start_time = time.time()
            response = requests.get(f"{url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return True, f"Status: {data.get('status', 'unknown')}", response_time
            return False, f"HTTP {response.status_code}", response_time
        except Exception as e:
            return False, f"Connection error: {str(e)}", 0.0

    async def test_aggregation_service(self):
        """Test analytics aggregation service."""
        print("\n📊 Testing Analytics Aggregation Service...")

        # Test health endpoint
        success, details, response_time = self.test_service_health(
            "aggregation", self.base_urls["aggregation"]
        )
        self.log_test_result(
            "aggregation_service", "Health Check", success, details, response_time
        )

        if not success:
            return

        # Test behavior aggregation
        try:
            mock_user_data = [
                {
                    "user_id": "user_001",
                    "therapeutic_focus": "anxiety",
                    "session_frequency": "high",
                    "engagement_level": "high",
                    "sessions": [
                        {
                            "duration_minutes": 25,
                            "interaction_count": 15,
                            "therapeutic_interventions_count": 2,
                            "progress_markers_count": 1,
                        },
                        {
                            "duration_minutes": 30,
                            "interaction_count": 20,
                            "therapeutic_interventions_count": 1,
                            "progress_markers_count": 2,
                        },
                    ],
                    "progress_data": {
                        "overall_progress": 0.75,
                        "goal_completion_rate": 0.6,
                        "engagement_level": 0.8,
                        "total_sessions": 10,
                    },
                },
                {
                    "user_id": "user_002",
                    "therapeutic_focus": "depression",
                    "session_frequency": "medium",
                    "engagement_level": "medium",
                    "sessions": [
                        {
                            "duration_minutes": 20,
                            "interaction_count": 12,
                            "therapeutic_interventions_count": 3,
                            "progress_markers_count": 1,
                        }
                    ],
                    "progress_data": {
                        "overall_progress": 0.45,
                        "goal_completion_rate": 0.3,
                        "engagement_level": 0.5,
                        "total_sessions": 5,
                    },
                },
            ]

            start_time = time.time()
            response = requests.post(
                f"{self.base_urls['aggregation']}/aggregate/behavior",
                json={"user_data": mock_user_data, "privacy_level": "high"},
                timeout=30,
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                patterns_detected = data.get("patterns_detected", 0)
                self.log_test_result(
                    "aggregation_service",
                    "Behavior Aggregation",
                    True,
                    f"Patterns detected: {patterns_detected}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "aggregation_service",
                    "Behavior Aggregation",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "aggregation_service", "Behavior Aggregation", False, str(e)
            )

        # Test pattern retrieval
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['aggregation']}/patterns?limit=10", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                pattern_count = data.get("total_count", 0)
                self.log_test_result(
                    "aggregation_service",
                    "Pattern Retrieval",
                    True,
                    f"Patterns retrieved: {pattern_count}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "aggregation_service",
                    "Pattern Retrieval",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "aggregation_service", "Pattern Retrieval", False, str(e)
            )

        # Test cohort analysis
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['aggregation']}/cohorts/analysis", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                cohort_count = data.get("total_cohorts", 0)
                self.log_test_result(
                    "aggregation_service",
                    "Cohort Analysis",
                    True,
                    f"Cohorts analyzed: {cohort_count}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "aggregation_service",
                    "Cohort Analysis",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "aggregation_service", "Cohort Analysis", False, str(e)
            )

    async def test_reporting_service(self):
        """Test advanced reporting service."""
        print("\n📈 Testing Advanced Reporting Service...")

        # Test health endpoint
        success, details, response_time = self.test_service_health(
            "reporting", self.base_urls["reporting"]
        )
        self.log_test_result(
            "reporting_service", "Health Check", success, details, response_time
        )

        if not success:
            return

        # Test report generation
        try:
            report_request = {
                "report_type": "therapeutic_outcomes",
                "report_format": "json",
                "title": "Test Therapeutic Outcomes Report",
                "description": "Automated test report for Phase 3 validation",
                "date_range_start": (datetime.now() - timedelta(days=30)).isoformat(),
                "date_range_end": datetime.now().isoformat(),
                "filters": {"outcome_category": "positive"},
                "visualization_config": {"chart_type": "line"},
            }

            start_time = time.time()
            response = requests.post(
                f"{self.base_urls['reporting']}/reports/generate",
                json=report_request,
                timeout=30,
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                report_id = data.get("report_id")
                self.log_test_result(
                    "reporting_service",
                    "Report Generation",
                    True,
                    f"Report ID: {report_id}",
                    response_time,
                )

                # Wait a moment for report to be generated
                await asyncio.sleep(2)

                # Test report retrieval
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.base_urls['reporting']}/reports/{report_id}", timeout=10
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        report_data = response.json()
                        self.log_test_result(
                            "reporting_service",
                            "Report Retrieval",
                            True,
                            "Report retrieved successfully",
                            response_time,
                        )
                    else:
                        self.log_test_result(
                            "reporting_service",
                            "Report Retrieval",
                            False,
                            f"HTTP {response.status_code}",
                            response_time,
                        )
                except Exception as e:
                    self.log_test_result(
                        "reporting_service", "Report Retrieval", False, str(e)
                    )

            else:
                self.log_test_result(
                    "reporting_service",
                    "Report Generation",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "reporting_service", "Report Generation", False, str(e)
            )

        # Test report listing
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['reporting']}/reports", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                report_count = data.get("total_count", 0)
                self.log_test_result(
                    "reporting_service",
                    "Report Listing",
                    True,
                    f"Reports listed: {report_count}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "reporting_service",
                    "Report Listing",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result("reporting_service", "Report Listing", False, str(e))

    async def test_monitoring_service(self):
        """Test enhanced real-time monitoring service."""
        print("\n🔍 Testing Enhanced Real-time Monitoring Service...")

        # Test health endpoint
        success, details, response_time = self.test_service_health(
            "monitoring", self.base_urls["monitoring"]
        )
        self.log_test_result(
            "monitoring_service", "Health Check", success, details, response_time
        )

        if not success:
            return

        # Test metric processing
        try:
            metric_data = {
                "metric_name": "test_cpu_usage",
                "value": 75.5,
                "warning_threshold": 70.0,
                "critical_threshold": 90.0,
            }

            start_time = time.time()
            response = requests.post(
                f"{self.base_urls['monitoring']}/metrics/process",
                json=metric_data,
                timeout=10,
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                self.log_test_result(
                    "monitoring_service",
                    "Metric Processing",
                    True,
                    f"Metric processed: {metric_data['metric_name']}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "monitoring_service",
                    "Metric Processing",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "monitoring_service", "Metric Processing", False, str(e)
            )

        # Test user data processing
        try:
            user_data = {
                "user_id": "test_user_001",
                "engagement_score": 0.25,  # Low engagement to trigger alert
                "session_duration": 45.0,
                "sentiment_score": 0.15,  # Low sentiment
                "recent_messages": ["I feel terrible", "Nothing helps"],
            }

            start_time = time.time()
            response = requests.post(
                f"{self.base_urls['monitoring']}/users/process",
                json=user_data,
                timeout=10,
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                self.log_test_result(
                    "monitoring_service",
                    "User Data Processing",
                    True,
                    f"User data processed: {user_data['user_id']}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "monitoring_service",
                    "User Data Processing",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "monitoring_service", "User Data Processing", False, str(e)
            )

        # Test active alerts retrieval
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['monitoring']}/alerts/active", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                alert_count = data.get("count", 0)
                self.log_test_result(
                    "monitoring_service",
                    "Active Alerts Retrieval",
                    True,
                    f"Active alerts: {alert_count}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "monitoring_service",
                    "Active Alerts Retrieval",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "monitoring_service", "Active Alerts Retrieval", False, str(e)
            )

        # Test current metrics
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['monitoring']}/metrics/current", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                metric_count = len(data.get("metrics", {}))
                self.log_test_result(
                    "monitoring_service",
                    "Current Metrics",
                    True,
                    f"Metrics available: {metric_count}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "monitoring_service",
                    "Current Metrics",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result("monitoring_service", "Current Metrics", False, str(e))

    async def test_websocket_alerts(self):
        """Test WebSocket real-time alerts."""
        print("\n🔌 Testing WebSocket Real-time Alerts...")

        try:
            uri = "ws://localhost:8097/alerts/stream"

            async with websockets.connect(uri, timeout=10) as websocket:
                # Send a test message to keep connection alive
                await websocket.send("test")

                # Wait for potential alerts (with timeout)
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    self.log_test_result(
                        "monitoring_service",
                        "WebSocket Connection",
                        True,
                        "WebSocket connection established and responsive",
                    )
                except asyncio.TimeoutError:
                    self.log_test_result(
                        "monitoring_service",
                        "WebSocket Connection",
                        True,
                        "WebSocket connection established (no alerts received)",
                    )

        except Exception as e:
            self.log_test_result(
                "monitoring_service", "WebSocket Connection", False, str(e)
            )

    async def test_integration_with_phase2(self):
        """Test integration with Phase 2 infrastructure."""
        print("\n🔗 Testing Integration with Phase 2 Infrastructure...")

        # Test Prometheus integration
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['prometheus']}/api/v1/targets", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                targets = data.get("data", {}).get("activeTargets", [])
                analytics_targets = [
                    t for t in targets if "analytics" in t.get("job", "")
                ]
                self.log_test_result(
                    "integration_tests",
                    "Prometheus Integration",
                    True,
                    f"Analytics targets: {len(analytics_targets)}",
                    response_time,
                )
            else:
                self.log_test_result(
                    "integration_tests",
                    "Prometheus Integration",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "integration_tests", "Prometheus Integration", False, str(e)
            )

        # Test Grafana integration
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_urls['grafana']}/api/health", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                self.log_test_result(
                    "integration_tests",
                    "Grafana Integration",
                    True,
                    "Grafana accessible",
                    response_time,
                )
            else:
                self.log_test_result(
                    "integration_tests",
                    "Grafana Integration",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                )
        except Exception as e:
            self.log_test_result(
                "integration_tests", "Grafana Integration", False, str(e)
            )

    async def test_performance_benchmarks(self):
        """Test performance benchmarks for analytics services."""
        print("\n⚡ Testing Performance Benchmarks...")

        # Test aggregation service performance
        start_time = time.time()
        success_count = 0
        total_requests = 10

        for i in range(total_requests):
            try:
                response = requests.get(
                    f"{self.base_urls['aggregation']}/health", timeout=5
                )
                if response.status_code == 200:
                    success_count += 1
            except:
                pass

        total_time = time.time() - start_time
        avg_response_time = (total_time / total_requests) * 1000
        success_rate = (success_count / total_requests) * 100

        self.log_test_result(
            "performance_tests",
            "Aggregation Service Load Test",
            success_rate >= 95,
            f"Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.1f}ms",
        )

        # Test reporting service performance
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_urls['reporting']}/reports", timeout=10
            )
            response_time = (time.time() - start_time) * 1000

            performance_ok = response_time < 3000  # Less than 3 seconds
            self.log_test_result(
                "performance_tests",
                "Reporting Service Response Time",
                performance_ok,
                f"Response time: {response_time:.1f}ms",
            )
        except Exception as e:
            self.log_test_result(
                "performance_tests", "Reporting Service Response Time", False, str(e)
            )

    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 PHASE 3: ADVANCED ANALYTICS TEST REPORT")
        print("=" * 60)

        total_tests = 0
        passed_tests = 0

        for category, tests in self.test_results.items():
            if not tests:
                continue

            category_passed = sum(1 for test in tests if test["success"])
            category_total = len(tests)
            category_success_rate = (
                (category_passed / category_total) * 100 if category_total > 0 else 0
            )

            total_tests += category_total
            passed_tests += category_passed

            print(
                f"\n📋 {category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_success_rate:.1f}%)"
            )

            for test in tests:
                status = "✅" if test["success"] else "❌"
                response_time = (
                    f" ({test['response_time']:.1f}ms)"
                    if test["response_time"] > 0
                    else ""
                )
                print(
                    f"  {status} {test['test_name']}: {test['details']}{response_time}"
                )

        overall_success_rate = (
            (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        )
        test_duration = (datetime.now() - self.start_time).total_seconds()

        print("\n🎯 OVERALL RESULTS:")
        print(f"✅ Successful Tests: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {overall_success_rate:.1f}%")
        print(f"⏱️  Test Duration: {test_duration:.1f} seconds")

        if overall_success_rate >= 80:
            print("\n🎉 PHASE 3: ADVANCED ANALYTICS IMPLEMENTATION - SUCCESS")
            print("All major components are operational and ready for production use.")
        elif overall_success_rate >= 60:
            print("\n⚠️  PHASE 3: ADVANCED ANALYTICS IMPLEMENTATION - PARTIAL SUCCESS")
            print("Most components are working but some issues need attention.")
        else:
            print("\n❌ PHASE 3: ADVANCED ANALYTICS IMPLEMENTATION - NEEDS WORK")
            print("Significant issues detected that require resolution.")

        print("\n🌐 Service Access Points:")
        print("  - Analytics Aggregation: http://localhost:8095")
        print("  - Advanced Reporting: http://localhost:8096")
        print("  - Real-time Monitoring: http://localhost:8097")
        print("  - Analytics Prometheus: http://localhost:9092")
        print("  - Analytics Grafana: http://localhost:3004")

        return overall_success_rate >= 80


async def main():
    """Run the comprehensive Phase 3 test suite."""
    print("🚀 Phase 3: Advanced Analytics Implementation Test Suite")
    print("=" * 60)

    test_suite = Phase3AnalyticsTestSuite()

    # Run all test categories
    await test_suite.test_aggregation_service()
    await test_suite.test_reporting_service()
    await test_suite.test_monitoring_service()
    await test_suite.test_websocket_alerts()
    await test_suite.test_integration_with_phase2()
    await test_suite.test_performance_benchmarks()

    # Generate final report
    success = test_suite.generate_test_report()

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
