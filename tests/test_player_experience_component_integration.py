#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Tests/Test_player_experience_component_integration]]
Player Experience Component Integration Tests

This module tests the integration of the PlayerExperienceComponent with the TTA orchestration system.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.components.player_experience_component import PlayerExperienceComponent
from src.orchestration import TTAConfig, TTAOrchestrator
from src.orchestration.component import ComponentStatus


class TestPlayerExperienceComponentIntegration(unittest.TestCase):
    """Test the Player Experience Component integration with TTA orchestration."""

    def setUp(self):
        """Set up the test."""
        # Create a test configuration
        self.config = TTAConfig()

        # Ensure player experience is enabled in config
        self.config.set("player_experience.enabled", True)
        self.config.set("player_experience.api.port", 8080)
        self.config.set("player_experience.web.port", 3000)

        # Create the orchestrator
        self.orchestrator = TTAOrchestrator()

        # Create the player experience component
        self.player_experience = PlayerExperienceComponent(self.config)

    def test_component_initialization(self):
        """Test that the PlayerExperienceComponent initializes correctly."""
        # Check component properties
        self.assertEqual(self.player_experience.name, "player_experience")
        self.assertEqual(self.player_experience.status, ComponentStatus.STOPPED)
        self.assertEqual(self.player_experience.api_port, 8080)
        self.assertEqual(self.player_experience.web_port, 3000)

        # Check dependencies
        self.assertIn("redis", self.player_experience.dependencies)
        self.assertIn("neo4j", self.player_experience.dependencies)

    def test_component_registration_in_orchestrator(self):
        """Test that the PlayerExperienceComponent is registered in the orchestrator."""
        # Check that the component is registered
        self.assertIn("player_experience", self.orchestrator.components)

        # Check that it's the correct type
        component = self.orchestrator.components["player_experience"]
        self.assertIsInstance(component, PlayerExperienceComponent)

    def test_configuration_integration(self):
        """Test that the component correctly reads configuration from TTA config."""
        # Test default configuration values
        self.assertEqual(self.player_experience.api_port, 8080)
        self.assertEqual(self.player_experience.web_port, 3000)

        # Test configuration override
        new_config = TTAConfig()
        new_config.set("player_experience.api.port", 9090)
        new_config.set("player_experience.web.port", 4000)

        new_component = PlayerExperienceComponent(new_config)
        self.assertEqual(new_component.api_port, 9090)
        self.assertEqual(new_component.web_port, 4000)

    @patch("subprocess.run")
    @patch("requests.get")
    def test_component_start_integration(self, mock_requests, mock_subprocess):
        """Test that the component starts correctly through orchestration."""
        # Mock successful Docker Compose execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Mock successful health check
        mock_health_response = Mock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {"status": "healthy"}
        mock_requests.return_value = mock_health_response

        # Test starting the component
        result = self.player_experience.start()
        self.assertTrue(result)
        self.assertEqual(self.player_experience.status, ComponentStatus.RUNNING)

        # Verify Docker Compose was called
        mock_subprocess.assert_called()

        # Verify health check was called
        mock_requests.assert_called()

    @patch("subprocess.run")
    @patch("requests.get")
    def test_component_stop_integration(self, mock_requests, mock_subprocess):
        """Test that the component stops correctly through orchestration."""
        # First start the component (mocked)
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_health_response = Mock()
        mock_health_response.status_code = 200
        mock_requests.return_value = mock_health_response

        self.player_experience.start()

        # Mock stopping
        mock_requests.side_effect = [
            mock_health_response,  # Initial health check (running)
            Exception("Connection refused"),  # After stop (not running)
        ]

        # Test stopping the component
        result = self.player_experience.stop()
        self.assertTrue(result)
        self.assertEqual(self.player_experience.status, ComponentStatus.STOPPED)

    def test_health_status_integration(self):
        """Test that the component provides comprehensive health status."""
        health_status = self.player_experience.get_health_status()

        # Check required health status fields
        self.assertIn("api_running", health_status)
        self.assertIn("api_port", health_status)
        self.assertIn("web_port", health_status)
        self.assertIn("component_status", health_status)
        self.assertIn("dependencies_status", health_status)
        self.assertIn("container_status", health_status)
        self.assertIn("last_health_check", health_status)

        # Check port values
        self.assertEqual(health_status["api_port"], 8080)
        self.assertEqual(health_status["web_port"], 3000)

    def test_monitoring_metrics_integration(self):
        """Test that the component provides monitoring metrics."""
        metrics = self.player_experience.get_monitoring_metrics()

        # Check required metrics fields
        self.assertIn("component_name", metrics)
        self.assertIn("uptime", metrics)
        self.assertIn("status", metrics)
        self.assertIn("health_status", metrics)
        self.assertIn("configuration", metrics)

        # Check component name
        self.assertEqual(metrics["component_name"], "player_experience")

        # Check configuration section
        config = metrics["configuration"]
        self.assertIn("api_port", config)
        self.assertIn("web_port", config)
        self.assertIn("dependencies", config)

    @patch("subprocess.run")
    def test_docker_compose_integration(self, mock_subprocess):
        """Test Docker Compose integration."""
        # Mock successful Docker Compose execution
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="Services started", stderr=""
        )

        # Test Docker Compose command execution
        result = self.player_experience._run_docker_compose(["up", "-d"])

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Services started")

        # Verify the command was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("docker-compose", call_args)
        self.assertIn("up", call_args)
        self.assertIn("-d", call_args)

    @patch("redis.Redis")
    def test_dependency_health_checking(self, mock_redis):
        """Test dependency health checking."""
        # Mock Redis connection
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client

        # Test dependency health checking
        health = self.player_experience._check_dependencies_health()

        # Check that Redis health is checked
        self.assertIn("redis", health)
        self.assertTrue(health["redis"])

        # Check that Neo4j health is checked
        self.assertIn("neo4j", health)

    def test_orchestrator_component_lifecycle(self):
        """Test component lifecycle through orchestrator."""
        # Test that orchestrator can find the component
        self.assertTrue(self.orchestrator.has_component("player_experience"))

        # Test getting component status
        status = self.orchestrator.get_component_status("player_experience")
        self.assertEqual(status, ComponentStatus.STOPPED)

        # Test component dependencies are recognized
        component = self.orchestrator.components["player_experience"]
        self.assertIn("redis", component.dependencies)
        self.assertIn("neo4j", component.dependencies)

    def test_configuration_validation(self):
        """Test that the component validates required configuration."""
        # Test with missing configuration
        empty_config = TTAConfig()
        empty_config.data = {}  # Clear all configuration

        # Component should still initialize with defaults
        component = PlayerExperienceComponent(empty_config)
        self.assertIsNotNone(component.api_port)
        self.assertIsNotNone(component.web_port)

    @patch("subprocess.run")
    def test_container_status_checking(self, mock_subprocess):
        """Test container status checking functionality."""
        # Mock Docker ps command output
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="tta-player-experience-api,Up 5 minutes,tta/player-experience:latest",
            stderr="",
        )

        # Test container status checking
        container_status = self.player_experience._get_container_status()

        # Verify Docker ps was called
        mock_subprocess.assert_called()

        # Check that container status is parsed correctly
        if "api_container" in container_status:
            self.assertIn("name", container_status["api_container"])
            self.assertIn("status", container_status["api_container"])
            self.assertIn("image", container_status["api_container"])

    def test_error_handling_integration(self):
        """Test error handling in component integration."""
        # Test with invalid Docker Compose path
        invalid_component = PlayerExperienceComponent(self.config)
        invalid_component.player_experience_dir = Path("/nonexistent/path")

        # Starting should fail gracefully
        result = invalid_component.start()
        self.assertFalse(result)
        self.assertEqual(invalid_component.status, ComponentStatus.STOPPED)

    def test_component_decorators_integration(self):
        """Test that component methods use orchestration decorators correctly."""
        # Test that start method has proper decorators
        start_method = self.player_experience._start_impl

        # Check that the method exists and is callable
        self.assertTrue(callable(start_method))

        # Test that stop method has proper decorators
        stop_method = self.player_experience._stop_impl
        self.assertTrue(callable(stop_method))


class TestPlayerExperienceOrchestrationWorkflow(unittest.TestCase):
    """Test complete orchestration workflows with Player Experience Component."""

    def setUp(self):
        """Set up the test."""
        self.config = TTAConfig()
        self.config.set("player_experience.enabled", True)
        self.orchestrator = TTAOrchestrator()

    def test_full_system_startup_workflow(self):
        """Test that player experience component integrates into full system startup."""
        # Check that player experience is included in component list
        self.assertIn("player_experience", self.orchestrator.components)

        # Check that dependencies are properly configured
        pe_component = self.orchestrator.components["player_experience"]
        self.assertIn("redis", pe_component.dependencies)
        self.assertIn("neo4j", pe_component.dependencies)

    @patch("src.components.player_experience_component.PlayerExperienceComponent.start")
    def test_orchestrator_start_component_integration(self, mock_start):
        """Test starting player experience through orchestrator."""
        mock_start.return_value = True

        # Test starting through orchestrator
        result = self.orchestrator.start_component("player_experience")
        self.assertTrue(result)

        # Verify the component's start method was called
        mock_start.assert_called_once()

    @patch("src.components.player_experience_component.PlayerExperienceComponent.stop")
    def test_orchestrator_stop_component_integration(self, mock_stop):
        """Test stopping player experience through orchestrator."""
        mock_stop.return_value = True

        # Test stopping through orchestrator
        result = self.orchestrator.stop_component("player_experience")
        self.assertTrue(result)

        # Verify the component's stop method was called
        mock_stop.assert_called_once()

    def test_component_status_reporting(self):
        """Test that component status is properly reported through orchestrator."""
        # Get status through orchestrator
        status = self.orchestrator.get_component_status("player_experience")
        self.assertIsInstance(status, ComponentStatus)

        # Test status display (should not raise exceptions)
        try:
            self.orchestrator.display_status()
        except Exception as e:
            self.fail(f"Status display failed: {e}")


if __name__ == "__main__":
    # Set up test environment
    os.environ["TESTING"] = "true"

    # Run the tests
    unittest.main(verbosity=2)
