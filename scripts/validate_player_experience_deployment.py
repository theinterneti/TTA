# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Player Experience Deployment Validation Script

This script validates that the Player Experience Interface is properly integrated
with the TTA orchestration system and can be deployed successfully.

Usage:
    python scripts/validate_player_experience_deployment.py [--config CONFIG_PATH] [--environment ENV]
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAConfig, TTAOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PlayerExperienceDeploymentValidator:
    """Validates Player Experience deployment integration with TTA orchestration."""

    def __init__(
        self, config_path: str | None = None, environment: str = "development"
    ):
        self.config_path = config_path
        self.environment = environment
        self.test_results: list[dict[str, Any]] = []
        self.orchestrator: TTAOrchestrator | None = None

    def log_test_result(
        self,
        test_name: str,
        success: bool,
        message: str = "",
        details: dict[str, Any] = None,
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

    def test_configuration_loading(self) -> bool:
        """Test that the configuration loads correctly."""
        try:
            config = TTAConfig(self.config_path)

            # Check player experience configuration
            pe_enabled = config.get("player_experience.enabled", False)
            api_port = config.get("player_experience.api.port", 8080)
            web_port = config.get("player_experience.web.port", 3000)

            if pe_enabled:
                self.log_test_result(
                    "Configuration Loading",
                    True,
                    f"Player Experience enabled with API port {api_port}, Web port {web_port}",
                    {"enabled": pe_enabled, "api_port": api_port, "web_port": web_port},
                )
                return True
            self.log_test_result(
                "Configuration Loading",
                False,
                "Player Experience is not enabled in configuration",
                {"enabled": pe_enabled},
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Configuration Loading",
                False,
                f"Failed to load configuration: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_orchestrator_initialization(self) -> bool:
        """Test that the orchestrator initializes with player experience component."""
        try:
            self.orchestrator = TTAOrchestrator(self.config_path)

            # Check if player experience component is registered
            if "player_experience" in self.orchestrator.components:
                pe_component = self.orchestrator.components["player_experience"]

                self.log_test_result(
                    "Orchestrator Initialization",
                    True,
                    f"Player Experience component registered with dependencies: {pe_component.dependencies}",
                    {
                        "component_name": pe_component.name,
                        "dependencies": pe_component.dependencies,
                        "status": pe_component.status.value,
                    },
                )
                return True
            available_components = list(self.orchestrator.components.keys())
            self.log_test_result(
                "Orchestrator Initialization",
                False,
                f"Player Experience component not found. Available: {available_components}",
                {"available_components": available_components},
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Orchestrator Initialization",
                False,
                f"Failed to initialize orchestrator: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_component_configuration(self) -> bool:
        """Test that the player experience component is properly configured."""
        if not self.orchestrator:
            self.log_test_result(
                "Component Configuration", False, "Orchestrator not initialized"
            )
            return False

        try:
            pe_component = self.orchestrator.components.get("player_experience")
            if not pe_component:
                self.log_test_result(
                    "Component Configuration",
                    False,
                    "Player Experience component not found",
                )
                return False

            # Check component configuration
            config_valid = (
                hasattr(pe_component, "api_port")
                and hasattr(pe_component, "web_port")
                and hasattr(pe_component, "dependencies")
            )

            if config_valid:
                self.log_test_result(
                    "Component Configuration",
                    True,
                    f"Component properly configured - API: {pe_component.api_port}, Web: {pe_component.web_port}",
                    {
                        "api_port": pe_component.api_port,
                        "web_port": pe_component.web_port,
                        "dependencies": pe_component.dependencies,
                    },
                )
                return True
            self.log_test_result(
                "Component Configuration",
                False,
                "Component missing required configuration attributes",
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Component Configuration",
                False,
                f"Failed to check component configuration: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_component_dependencies(self) -> bool:
        """Test that component dependencies are properly defined."""
        if not self.orchestrator:
            self.log_test_result(
                "Component Dependencies", False, "Orchestrator not initialized"
            )
            return False

        try:
            pe_component = self.orchestrator.components.get("player_experience")
            if not pe_component:
                self.log_test_result(
                    "Component Dependencies",
                    False,
                    "Player Experience component not found",
                )
                return False

            # Check dependencies
            expected_deps = ["redis", "neo4j"]
            actual_deps = pe_component.dependencies

            deps_correct = all(dep in actual_deps for dep in expected_deps)

            if deps_correct:
                self.log_test_result(
                    "Component Dependencies",
                    True,
                    f"Dependencies correctly defined: {actual_deps}",
                    {"expected": expected_deps, "actual": actual_deps},
                )
                return True
            missing_deps = [dep for dep in expected_deps if dep not in actual_deps]
            self.log_test_result(
                "Component Dependencies",
                False,
                f"Missing dependencies: {missing_deps}",
                {
                    "expected": expected_deps,
                    "actual": actual_deps,
                    "missing": missing_deps,
                },
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Component Dependencies",
                False,
                f"Failed to check component dependencies: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_component_status_monitoring(self) -> bool:
        """Test that component status can be monitored through orchestrator."""
        if not self.orchestrator:
            self.log_test_result(
                "Component Status Monitoring", False, "Orchestrator not initialized"
            )
            return False

        try:
            # Test getting component status
            status = self.orchestrator.get_component_status("player_experience")

            if status is not None:
                # Test getting all statuses
                all_statuses = self.orchestrator.get_all_statuses()

                if "player_experience" in all_statuses:
                    self.log_test_result(
                        "Component Status Monitoring",
                        True,
                        f"Status monitoring working - Current status: {status.value}",
                        {
                            "current_status": status.value,
                            "all_components": list(all_statuses.keys()),
                        },
                    )
                    return True
                self.log_test_result(
                    "Component Status Monitoring",
                    False,
                    "Component not found in all statuses",
                )
                return False
            self.log_test_result(
                "Component Status Monitoring",
                False,
                "Failed to get component status",
            )
            return False

        except Exception as e:
            self.log_test_result(
                "Component Status Monitoring",
                False,
                f"Failed to test status monitoring: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_health_check_integration(self) -> bool:
        """Test that health check functionality is integrated."""
        if not self.orchestrator:
            self.log_test_result(
                "Health Check Integration", False, "Orchestrator not initialized"
            )
            return False

        try:
            pe_component = self.orchestrator.components.get("player_experience")
            if not pe_component:
                self.log_test_result(
                    "Health Check Integration",
                    False,
                    "Player Experience component not found",
                )
                return False

            # Test health check methods exist
            has_health_methods = (
                hasattr(pe_component, "get_health_status")
                and hasattr(pe_component, "get_monitoring_metrics")
                and callable(pe_component.get_health_status)
                and callable(pe_component.get_monitoring_metrics)
            )

            if has_health_methods:
                # Try to call health check methods
                try:
                    health_status = pe_component.get_health_status()
                    monitoring_metrics = pe_component.get_monitoring_metrics()

                    self.log_test_result(
                        "Health Check Integration",
                        True,
                        "Health check methods available and callable",
                        {
                            "health_status_keys": (
                                list(health_status.keys())
                                if isinstance(health_status, dict)
                                else "not_dict"
                            ),
                            "monitoring_metrics_keys": (
                                list(monitoring_metrics.keys())
                                if isinstance(monitoring_metrics, dict)
                                else "not_dict"
                            ),
                        },
                    )
                    return True
                except Exception as e:
                    self.log_test_result(
                        "Health Check Integration",
                        False,
                        f"Health check methods exist but failed to execute: {str(e)}",
                        {"exception": str(e)},
                    )
                    return False
            else:
                self.log_test_result(
                    "Health Check Integration",
                    False,
                    "Health check methods not available",
                )
                return False

        except Exception as e:
            self.log_test_result(
                "Health Check Integration",
                False,
                f"Failed to test health check integration: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def test_deployment_readiness(self) -> bool:
        """Test overall deployment readiness."""
        if not self.orchestrator:
            self.log_test_result(
                "Deployment Readiness", False, "Orchestrator not initialized"
            )
            return False

        try:
            pe_component = self.orchestrator.components.get("player_experience")
            if not pe_component:
                self.log_test_result(
                    "Deployment Readiness",
                    False,
                    "Player Experience component not found",
                )
                return False

            # Check deployment readiness criteria
            readiness_checks = {
                "component_registered": "player_experience"
                in self.orchestrator.components,
                "dependencies_defined": len(pe_component.dependencies) > 0,
                "configuration_valid": hasattr(pe_component, "api_port")
                and hasattr(pe_component, "web_port"),
                "health_checks_available": hasattr(pe_component, "get_health_status"),
                "monitoring_available": hasattr(pe_component, "get_monitoring_metrics"),
                "docker_integration": hasattr(pe_component, "_run_docker_compose"),
            }

            passed_checks = sum(readiness_checks.values())
            total_checks = len(readiness_checks)
            readiness_score = (passed_checks / total_checks) * 100

            deployment_ready = readiness_score >= 80  # 80% threshold

            self.log_test_result(
                "Deployment Readiness",
                deployment_ready,
                f"Deployment readiness: {readiness_score:.1f}% ({passed_checks}/{total_checks} checks passed)",
                {
                    "readiness_score": readiness_score,
                    "passed_checks": passed_checks,
                    "total_checks": total_checks,
                    "check_details": readiness_checks,
                },
            )
            return deployment_ready

        except Exception as e:
            self.log_test_result(
                "Deployment Readiness",
                False,
                f"Failed to assess deployment readiness: {str(e)}",
                {"exception": str(e)},
            )
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run all deployment validation tests."""
        logger.info(
            f"Starting Player Experience deployment validation for {self.environment} environment"
        )

        # Run all tests
        tests = [
            self.test_configuration_loading,
            self.test_orchestrator_initialization,
            self.test_component_configuration,
            self.test_component_dependencies,
            self.test_component_status_monitoring,
            self.test_health_check_integration,
            self.test_deployment_readiness,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.log_test_result(
                    test.__name__,
                    False,
                    f"Test failed with exception: {str(e)}",
                    {"exception": str(e)},
                )

        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        summary = {
            "environment": self.environment,
            "config_path": self.config_path,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "overall_success": success_rate >= 80,  # 80% pass rate required
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
        }

        return summary

    def print_summary(self, summary: dict[str, Any]):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("PLAYER EXPERIENCE DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Environment: {summary['environment']}")
        print(f"Config Path: {summary['config_path'] or 'default'}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        overall_status = (
            "✅ DEPLOYMENT READY"
            if summary["overall_success"]
            else "❌ DEPLOYMENT NOT READY"
        )
        print(f"\nOverall Status: {overall_status}")

        if not summary["overall_success"]:
            print("\nFailed Tests:")
            for result in summary["test_results"]:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")

        print("=" * 70)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate Player Experience deployment integration"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--environment",
        default="development",
        choices=["development", "staging", "production"],
        help="Environment being validated (default: development)",
    )
    parser.add_argument("--output", help="Output file for test results (JSON format)")

    args = parser.parse_args()

    # Create validator and run tests
    validator = PlayerExperienceDeploymentValidator(args.config, args.environment)
    summary = validator.run_all_tests()

    # Print summary
    validator.print_summary(summary)

    # Save results if output file specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Test results saved to {args.output}")

    # Exit with appropriate code
    sys.exit(0 if summary["overall_success"] else 1)


if __name__ == "__main__":
    main()
