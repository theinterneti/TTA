#!/usr/bin/env python3
"""
Clinical Dashboard Integration Test Script

Tests the clinical dashboard integration with the live TTA API to verify
end-to-end functionality and data flow.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.components.clinical_dashboard import (
    AnalyticsTimeframe,
    APIConfig,
    ClinicalDashboardController,
    MetricType,
    OutcomeMeasure,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ClinicalDashboardIntegrationTest:
    """Integration test for clinical dashboard with live API."""

    def __init__(self):
        """Initialize the integration test."""
        self.api_config = APIConfig(
            base_url="http://0.0.0.0:8080",  # Live API URL from our testing
            timeout=30,
            max_retries=3,
            retry_delay=1.0,
        )
        self.controller = None
        self.test_user_id = (
            "test_user_auth"  # User we registered during authentication testing
        )
        self.test_password = "TestPass123!"

    async def setup(self):
        """Set up the test environment."""
        try:
            logger.info("Setting up clinical dashboard integration test")

            # Initialize controller
            self.controller = ClinicalDashboardController(api_config=self.api_config)
            await self.controller.initialize()

            logger.info("Clinical dashboard controller initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting up test environment: {e}")
            return False

    async def test_api_connectivity(self):
        """Test API connectivity."""
        try:
            logger.info("Testing API connectivity...")

            # Test API connectivity through the service
            connectivity = await self.controller.api_service._test_api_connectivity()

            if connectivity:
                logger.info("✅ API connectivity test passed")
                return True
            else:
                logger.error("❌ API connectivity test failed")
                return False

        except Exception as e:
            logger.error(f"❌ API connectivity test error: {e}")
            return False

    async def test_user_authentication(self):
        """Test user authentication."""
        try:
            # Register a fresh user for this test session
            import uuid

            fresh_username = f"test_auth_{str(uuid.uuid4())[:8]}"
            fresh_password = "FreshTest123!"

            logger.info(
                f"Registering fresh user {fresh_username} for authentication test..."
            )

            # Register user via API
            url = f"{self.api_config.base_url}/api/v1/auth/register"
            register_payload = {
                "username": fresh_username,
                "email": f"{fresh_username}@example.com",
                "password": fresh_password,
                "role": "player",
            }

            async with self.controller.api_service.session.post(
                url, json=register_payload
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ User {fresh_username} registered successfully")
                else:
                    logger.error(f"❌ Failed to register user: {response.status}")
                    return False

            logger.info(f"Testing user authentication for {fresh_username}...")

            # Attempt authentication with fresh user
            auth_token = await self.controller.api_service.authenticate_user(
                fresh_username, fresh_password
            )

            if auth_token:
                logger.info("✅ User authentication successful")
                logger.info(f"   Token type: {auth_token.token_type}")
                logger.info(f"   Expires in: {auth_token.expires_in} seconds")
                logger.info(f"   User ID: {auth_token.user_id}")
                return True
            else:
                logger.error("❌ User authentication failed")
                return False

        except Exception as e:
            logger.error(f"❌ User authentication error: {e}")
            return False

    async def test_metric_collection(self):
        """Test metric collection functionality."""
        try:
            logger.info("Testing metric collection...")

            # Test collecting various metrics
            test_metrics = [
                (MetricType.ENGAGEMENT, 0.85, "High engagement test"),
                (MetricType.PROGRESS, 0.72, "Progress tracking test"),
                (MetricType.SAFETY, 0.95, "Safety monitoring test"),
                (MetricType.THERAPEUTIC_VALUE, 0.78, "Therapeutic value test"),
            ]

            success_count = 0
            for metric_type, value, context_note in test_metrics:
                try:
                    success = await self.controller.monitoring_service.collect_metric(
                        user_id=self.test_user_id,
                        session_id="test_session_001",
                        metric_type=metric_type,
                        value=value,
                        context={"note": context_note, "source": "integration_test"},
                    )

                    if success:
                        success_count += 1
                        logger.info(f"   ✅ {metric_type.value}: {value}")
                    else:
                        logger.warning(f"   ⚠️ Failed to collect {metric_type.value}")

                except Exception as e:
                    logger.error(f"   ❌ Error collecting {metric_type.value}: {e}")

            if success_count == len(test_metrics):
                logger.info("✅ All metric collection tests passed")
                return True
            else:
                logger.warning(
                    f"⚠️ {success_count}/{len(test_metrics)} metric collection tests passed"
                )
                return success_count > 0

        except Exception as e:
            logger.error(f"❌ Metric collection test error: {e}")
            return False

    async def test_outcome_measurements(self):
        """Test outcome measurement recording."""
        try:
            logger.info("Testing outcome measurement recording...")

            # Test recording various outcome measures
            test_outcomes = [
                (OutcomeMeasure.THERAPEUTIC_ALLIANCE, 7.5, 6.0, "Improved alliance"),
                (OutcomeMeasure.FUNCTIONAL_IMPROVEMENT, 6.8, 5.5, "Better functioning"),
                (OutcomeMeasure.QUALITY_OF_LIFE, 8.2, 7.0, "Enhanced quality of life"),
            ]

            success_count = 0
            for measure_type, current_score, baseline_score, notes in test_outcomes:
                try:
                    outcome_id = (
                        await self.controller.monitoring_service.record_outcome_measure(
                            user_id=self.test_user_id,
                            measure_type=measure_type,
                            current_score=current_score,
                            baseline_score=baseline_score,
                            clinician_notes=notes,
                        )
                    )

                    if outcome_id:
                        success_count += 1
                        logger.info(
                            f"   ✅ {measure_type.value}: {current_score} (ID: {outcome_id[:8]}...)"
                        )
                    else:
                        logger.warning(f"   ⚠️ Failed to record {measure_type.value}")

                except Exception as e:
                    logger.error(f"   ❌ Error recording {measure_type.value}: {e}")

            if success_count == len(test_outcomes):
                logger.info("✅ All outcome measurement tests passed")
                return True
            else:
                logger.warning(
                    f"⚠️ {success_count}/{len(test_outcomes)} outcome measurement tests passed"
                )
                return success_count > 0

        except Exception as e:
            logger.error(f"❌ Outcome measurement test error: {e}")
            return False

    async def test_real_time_metrics(self):
        """Test real-time metrics retrieval."""
        try:
            logger.info("Testing real-time metrics retrieval...")

            # Get real-time metrics
            metrics = await self.controller.monitoring_service.get_real_time_metrics(
                self.test_user_id
            )

            if metrics:
                logger.info("✅ Real-time metrics retrieved successfully")
                for metric_name, metric_data in metrics.items():
                    if isinstance(metric_data, dict) and "current_value" in metric_data:
                        logger.info(f"   {metric_name}: {metric_data['current_value']}")
                return True
            else:
                logger.warning("⚠️ No real-time metrics available")
                return False

        except Exception as e:
            logger.error(f"❌ Real-time metrics test error: {e}")
            return False

    async def test_analytics_report(self):
        """Test analytics report generation."""
        try:
            logger.info("Testing analytics report generation...")

            # Generate analytics report
            report = await self.controller.monitoring_service.generate_analytics_report(
                self.test_user_id, AnalyticsTimeframe.WEEKLY
            )

            if report:
                logger.info("✅ Analytics report generated successfully")
                logger.info(f"   Report ID: {report.report_id[:8]}...")
                logger.info(f"   Timeframe: {report.timeframe.value}")
                logger.info(
                    f"   Metrics summary: {len(report.metrics_summary)} metrics"
                )
                logger.info(f"   Recommendations: {len(report.recommendations)} items")
                logger.info(f"   Risk factors: {len(report.risk_factors)} items")
                logger.info(
                    f"   Protective factors: {len(report.protective_factors)} items"
                )
                return True
            else:
                logger.warning("⚠️ No analytics report generated")
                return False

        except Exception as e:
            logger.error(f"❌ Analytics report test error: {e}")
            return False

    async def test_service_health(self):
        """Test service health checks."""
        try:
            logger.info("Testing service health checks...")

            # Get service status
            status = await self.controller.get_service_status()

            if status:
                logger.info("✅ Service health check completed")
                logger.info(f"   Overall status: {status.get('status', 'unknown')}")

                # Check individual services
                if "controller" in status:
                    controller_status = status["controller"]
                    logger.info(
                        f"   Controller initialized: {controller_status.get('initialized', False)}"
                    )
                    logger.info(
                        f"   Uptime: {controller_status.get('uptime_seconds', 0):.1f} seconds"
                    )

                if "monitoring_service" in status:
                    monitoring_status = status["monitoring_service"]
                    logger.info(
                        f"   Monitoring service: {monitoring_status.get('status', 'unknown')}"
                    )

                if "api_service" in status:
                    api_status = status["api_service"]
                    logger.info(
                        f"   API service: {api_status.get('status', 'unknown')}"
                    )

                return status.get("status") == "healthy"
            else:
                logger.error("❌ Failed to get service status")
                return False

        except Exception as e:
            logger.error(f"❌ Service health test error: {e}")
            return False

    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting Clinical Dashboard Integration Tests")
        logger.info("=" * 60)

        # Setup
        if not await self.setup():
            logger.error("❌ Setup failed, aborting tests")
            return False

        # Run tests
        test_results = {}

        tests = [
            ("API Connectivity", self.test_api_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Metric Collection", self.test_metric_collection),
            ("Outcome Measurements", self.test_outcome_measurements),
            ("Real-time Metrics", self.test_real_time_metrics),
            ("Analytics Report", self.test_analytics_report),
            ("Service Health", self.test_service_health),
        ]

        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name} test...")
            try:
                result = await test_func()
                test_results[test_name] = result
            except Exception as e:
                logger.error(f"❌ {test_name} test failed with exception: {e}")
                test_results[test_name] = False

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)

        passed = 0
        total = len(test_results)

        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
            if result:
                passed += 1

        logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")

        if passed == total:
            logger.info(
                "🎉 All tests passed! Clinical Dashboard integration is working correctly."
            )
        elif passed > total // 2:
            logger.info("⚠️ Most tests passed. Some issues need attention.")
        else:
            logger.error(
                "❌ Multiple test failures. Clinical Dashboard needs debugging."
            )

        return passed == total

    async def cleanup(self):
        """Clean up test resources."""
        try:
            if self.controller:
                await self.controller.shutdown()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")


async def main():
    """Main test execution."""
    test_runner = ClinicalDashboardIntegrationTest()

    try:
        success = await test_runner.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n⏹️ Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1
    finally:
        await test_runner.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
