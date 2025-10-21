"""
TTA Components Tests

This module contains tests for the TTA components.

Usage:
    ```bash
    # Run the tests
    python3 tests/test_components.py
    ```
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
            from codecarbon import EmissionsTracker  # noqa: PLC0415, F401

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

    def test_carbon_stop_without_codecarbon(self):
        """Test Carbon component stop when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Mock codecarbon_available to False
        with patch("src.components.carbon_component.codecarbon_available", False):
            carbon.start()
            result = carbon.stop()
            self.assertTrue(
                result, "Carbon component should stop successfully without codecarbon"
            )

    def test_carbon_stop_with_emissions_data(self):
        """Test Carbon component stop with emissions data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Start the component first
        with patch("src.components.carbon_component.codecarbon_available", True):
            carbon.start()

            # Add some mock emissions data
            carbon.emissions_data = {
                "test_func": {
                    "emissions": 0.5,
                    "duration": 1.0,
                    "timestamp": "2025-10-21T00:00:00",
                }
            }

            # Mock the _save_emissions_data method
            with patch.object(carbon, "_save_emissions_data") as mock_save:
                result = carbon.stop()
                self.assertTrue(result, "Carbon component should stop successfully")
                mock_save.assert_called_once()

    def test_carbon_get_emissions_report_with_data(self):
        """Test getting emissions report with data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Add some mock emissions data
        carbon.emissions_data = {
            "func1": {"emissions": 0.5, "duration": 1.0},
            "func2": {"emissions": 0.3, "duration": 0.5},
        }

        with patch("src.components.carbon_component.codecarbon_available", True):
            report = carbon.get_emissions_report()
            self.assertIn("project_name", report)
            self.assertIn("total_emissions", report)
            self.assertIn("functions", report)
            self.assertEqual(report["total_emissions"], 0.8)
            self.assertEqual(report["unit"], "kg CO2eq")

    def test_carbon_save_emissions_data(self):
        """Test saving emissions data to file."""
        config = TTAConfig()

        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        try:
            carbon = CarbonComponent(config)
            carbon.output_dir = temp_dir

            # Add some mock emissions data
            carbon.emissions_data = {
                "test_func": {
                    "emissions": 0.5,
                    "duration": 1.0,
                    "timestamp": "2025-10-21T00:00:00",
                }
            }

            # Call _save_emissions_data
            carbon._save_emissions_data()

            # Check that a file was created
            files = list(Path(temp_dir).glob("emissions_*.json"))
            self.assertEqual(len(files), 1, "Should create one emissions file")

            # Verify file content
            content = json.loads(files[0].read_text())
            self.assertIn("project_name", content)
            self.assertIn("total_emissions", content)
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def test_carbon_save_emissions_data_empty(self):
        """Test saving emissions data when there's no data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Ensure emissions_data is empty
        carbon.emissions_data = {}

        # Call _save_emissions_data - should return early without error
        carbon._save_emissions_data()  # Should not raise an exception

    def test_carbon_get_decorator_without_codecarbon(self):
        """Test getting carbon decorator when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        with patch("src.components.carbon_component.codecarbon_available", False):
            decorator = carbon.get_carbon_decorator()
            self.assertIsNotNone(decorator, "Should return a no-op decorator")

            # Test that the decorator works as a no-op
            @decorator
            def test_func():
                return "test"

            result = test_func()
            self.assertEqual(
                result, "test", "Decorator should not affect function result"
            )

    def test_carbon_get_decorator_with_codecarbon(self):
        """Test getting carbon decorator when codecarbon is available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        with patch("src.components.carbon_component.codecarbon_available", True):
            decorator = carbon.get_carbon_decorator(project_name="test_project")
            self.assertIsNotNone(decorator, "Should return a decorator")

            # The decorator should be a callable that wraps functions
            # Test that it returns a function
            @decorator
            def test_func():
                return "test"

            # The decorated function should still be callable
            self.assertTrue(
                callable(test_func), "Decorated function should be callable"
            )


if __name__ == "__main__":
    # Run the tests
    unittest.main()
