"""
TTA Components Tests

This module contains tests for the TTA components.

Usage:
    ```bash
    # Run the tests
    python3 tests/test_components.py
    ```
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.components import CarbonComponent, DockerComponent
from src.orchestration import TTAConfig


class TestComponents(unittest.TestCase):
    """Test case for TTA components."""

    def test_config_validation(self):
        """Test configuration validation."""
        config = TTAConfig()
        self.assertTrue(config.validate(), "Configuration validation failed")

    def test_docker_component(self):
        """Test the Docker component."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Test initialization
        self.assertEqual(docker.name, "docker", "Docker component name is incorrect")
        self.assertEqual(
            docker.status.value, "stopped", "Docker component status is incorrect"
        )

        # Test starting the component
        if os.environ.get("RUN_DOCKER_TESTS", "false").lower() == "true":
            self.assertTrue(docker.start(), "Docker component failed to start")
            self.assertEqual(
                docker.status.value,
                "running",
                "Docker component status is incorrect after starting",
            )

            # Test stopping the component
            self.assertTrue(docker.stop(), "Docker component failed to stop")
            self.assertEqual(
                docker.status.value,
                "stopped",
                "Docker component status is incorrect after stopping",
            )

    def test_carbon_component(self):
        """Test the Carbon component."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test initialization
        self.assertEqual(carbon.name, "carbon", "Carbon component name is incorrect")
        self.assertEqual(
            carbon.status.value, "stopped", "Carbon component status is incorrect"
        )

        # Test starting the component
        try:
            from codecarbon import EmissionsTracker

            has_codecarbon = True
        except ImportError:
            has_codecarbon = False

        if has_codecarbon:
            self.assertTrue(carbon.start(), "Carbon component failed to start")
            self.assertEqual(
                carbon.status.value,
                "running",
                "Carbon component status is incorrect after starting",
            )

            # Test tracking a function
            def test_function():
                return "test"

            result = carbon.track_function(test_function)
            self.assertEqual(
                result, "test", "Carbon component failed to track function"
            )

            # Test getting emissions report
            report = carbon.get_emissions_report()
            self.assertIn(
                "project_name", report, "Emissions report is missing project_name"
            )
            self.assertIn(
                "total_emissions", report, "Emissions report is missing total_emissions"
            )

            # Test stopping the component
            self.assertTrue(carbon.stop(), "Carbon component failed to stop")
            self.assertEqual(
                carbon.status.value,
                "stopped",
                "Carbon component status is incorrect after stopping",
            )

    def test_carbon_decorator(self):
        """Test the Carbon component decorator functionality."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test getting the carbon decorator
        decorator = carbon.get_carbon_decorator()
        self.assertIsNotNone(decorator, "Carbon decorator should not be None")

        # Test that the decorator can be applied to a function
        @decorator
        def test_function():
            return "decorated"

        result = test_function()
        self.assertEqual(result, "decorated", "Decorated function should work")

    def test_carbon_without_codecarbon(self):
        """Test Carbon component behavior when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test that get_emissions_report handles missing codecarbon gracefully
        # This test will pass regardless of whether codecarbon is installed
        # because the component handles both cases
        report = carbon.get_emissions_report()
        self.assertIsNotNone(report, "Emissions report should not be None")


if __name__ == "__main__":
    # Run the tests
    unittest.main()
