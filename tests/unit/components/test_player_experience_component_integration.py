import pytest
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

pytestmark = pytest.mark.unit


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
        assert self.player_experience.name == "player_experience"
        assert self.player_experience.status == ComponentStatus.STOPPED
        assert self.player_experience.api_port == 8080
        assert self.player_experience.web_port == 3000

        # Check dependencies
        assert "redis" in self.player_experience.dependencies
        assert "neo4j" in self.player_experience.dependencies

    def test_component_registration_in_orchestrator(self):
        """Test that the PlayerExperienceComponent is registered in the orchestrator."""
        # Check that the component is registered
        assert "player_experience" in self.orchestrator.components

        # Check that it's the correct type
        component = self.orchestrator.components["player_experience"]
        assert isinstance(component, PlayerExperienceComponent)

    def test_configuration_integration(self):
        """Test that the component correctly reads configuration from TTA config."""
        # Test default configuration values
        assert self.player_experience.api_port == 8080
        assert self.player_experience.web_port == 3000

        # Test configuration override
        new_config = TTAConfig()
        new_config.set("player_experience.api.port", 9090)
        new_config.set("player_experience.web.port", 4000)

        new_component = PlayerExperienceComponent(new_config)
        assert new_component.api_port == 9090
        assert new_component.web_port == 4000

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
        assert result
        assert self.player_experience.status == ComponentStatus.RUNNING

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
        assert result
        assert self.player_experience.status == ComponentStatus.STOPPED

    def test_health_status_integration(self):
        """Test that the component provides comprehensive health status."""
        health_status = self.player_experience.get_health_status()

        # Check required health status fields
        assert "api_running" in health_status
        assert "api_port" in health_status
        assert "web_port" in health_status
        assert "component_status" in health_status
        assert "dependencies_status" in health_status
        assert "container_status" in health_status
        assert "last_health_check" in health_status

        # Check port values
        assert health_status["api_port"] == 8080
        assert health_status["web_port"] == 3000

    def test_monitoring_metrics_integration(self):
        """Test that the component provides monitoring metrics."""
        metrics = self.player_experience.get_monitoring_metrics()

        # Check required metrics fields
        assert "component_name" in metrics
        assert "uptime" in metrics
        assert "status" in metrics
        assert "health_status" in metrics
        assert "configuration" in metrics

        # Check component name
        assert metrics["component_name"] == "player_experience"

        # Check configuration section
        config = metrics["configuration"]
        assert "api_port" in config
        assert "web_port" in config
        assert "dependencies" in config

    @patch("subprocess.run")
    def test_docker_compose_integration(self, mock_subprocess):
        """Test Docker Compose integration."""
        # Mock successful Docker Compose execution
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="Services started", stderr=""
        )

        # Test Docker Compose command execution
        result = self.player_experience._run_docker_compose(["up", "-d"])

        assert result.returncode == 0
        assert result.stdout == "Services started"

        # Verify the command was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "docker-compose" in call_args
        assert "up" in call_args
        assert "-d" in call_args

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
        assert "redis" in health
        assert health["redis"]

        # Check that Neo4j health is checked
        assert "neo4j" in health

    def test_orchestrator_component_lifecycle(self):
        """Test component lifecycle through orchestrator."""
        # Test that orchestrator can find the component
        assert self.orchestrator.has_component("player_experience")

        # Test getting component status
        status = self.orchestrator.get_component_status("player_experience")
        assert status == ComponentStatus.STOPPED

        # Test component dependencies are recognized
        component = self.orchestrator.components["player_experience"]
        assert "redis" in component.dependencies
        assert "neo4j" in component.dependencies

    def test_configuration_validation(self):
        """Test that the component validates required configuration."""
        # Test with missing configuration
        empty_config = TTAConfig()
        empty_config.data = {}  # Clear all configuration

        # Component should still initialize with defaults
        component = PlayerExperienceComponent(empty_config)
        assert component.api_port is not None
        assert component.web_port is not None

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
            assert "name" in container_status["api_container"]
            assert "status" in container_status["api_container"]
            assert "image" in container_status["api_container"]

    def test_error_handling_integration(self):
        """Test error handling in component integration."""
        # Test with invalid Docker Compose path
        invalid_component = PlayerExperienceComponent(self.config)
        invalid_component.player_experience_dir = Path("/nonexistent/path")

        # Starting should fail gracefully
        result = invalid_component.start()
        assert not result
        assert invalid_component.status == ComponentStatus.STOPPED

    def test_component_decorators_integration(self):
        """Test that component methods use orchestration decorators correctly."""
        # Test that start method has proper decorators
        start_method = self.player_experience._start_impl

        # Check that the method exists and is callable
        assert callable(start_method)

        # Test that stop method has proper decorators
        stop_method = self.player_experience._stop_impl
        assert callable(stop_method)


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
        assert "player_experience" in self.orchestrator.components

        # Check that dependencies are properly configured
        pe_component = self.orchestrator.components["player_experience"]
        assert "redis" in pe_component.dependencies
        assert "neo4j" in pe_component.dependencies

    @patch("src.components.player_experience_component.PlayerExperienceComponent.start")
    def test_orchestrator_start_component_integration(self, mock_start):
        """Test starting player experience through orchestrator."""
        mock_start.return_value = True

        # Test starting through orchestrator
        result = self.orchestrator.start_component("player_experience")
        assert result

        # Verify the component's start method was called
        mock_start.assert_called_once()

    @patch("src.components.player_experience_component.PlayerExperienceComponent.stop")
    def test_orchestrator_stop_component_integration(self, mock_stop):
        """Test stopping player experience through orchestrator."""
        mock_stop.return_value = True

        # Test stopping through orchestrator
        result = self.orchestrator.stop_component("player_experience")
        assert result

        # Verify the component's stop method was called
        mock_stop.assert_called_once()

    def test_component_status_reporting(self):
        """Test that component status is properly reported through orchestrator."""
        # Get status through orchestrator
        status = self.orchestrator.get_component_status("player_experience")
        assert isinstance(status, ComponentStatus)

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
