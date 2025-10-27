"""
Tests for TTAOrchestrator Docker command methods.

This module tests the Docker-related methods in TTAOrchestrator
to achieve comprehensive coverage of Docker command execution.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.orchestration.orchestrator import TTAOrchestrator


class TestDockerCommands:
    """Test suite for Docker command methods."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mocked dependencies for testing."""
        # Mock the validation and import methods to prevent filesystem operations
        with patch(
            "src.orchestration.orchestrator.TTAOrchestrator._validate_repositories"
        ):
            with patch(
                "src.orchestration.orchestrator.TTAOrchestrator._import_components"
            ):
                # Create orchestrator (validation and import are mocked)
                orchestrator = TTAOrchestrator()

                # Clear any components
                orchestrator.components.clear()

                return orchestrator

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_command_success(self, mock_safe_run, orchestrator):
        """Test successful Docker command execution."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        result = orchestrator.run_docker_command(["ps", "-a"])

        # Verify safe_run was called with correct arguments
        mock_safe_run.assert_called_once()
        call_args = mock_safe_run.call_args
        assert call_args[0][0] == ["docker", "ps", "-a"]
        assert call_args[1]["text"] is True
        assert call_args[1]["timeout"] == 120
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["check"] is False

        # Verify result
        assert result.returncode == 0
        assert result.stdout == "success output"

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_command_failure(self, mock_safe_run, orchestrator):
        """Test Docker command failure handling with retry."""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: command failed"
        mock_safe_run.return_value = mock_result

        with pytest.raises(subprocess.SubprocessError, match="Docker command failed"):
            orchestrator.run_docker_command(["invalid", "command"])

        # Verify safe_run was called 3 times (retry decorator)
        assert mock_safe_run.call_count == 3

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_compose_command_single_repo(self, mock_safe_run, orchestrator):
        """Test Docker Compose command on single repository."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        results = orchestrator.run_docker_compose_command(["up", "-d"], repository="tta.dev")

        # Should only run for tta.dev
        assert "tta.dev" in results
        assert "tta.prototype" not in results
        assert results["tta.dev"].returncode == 0

        # Verify safe_run was called once
        assert mock_safe_run.call_count == 1

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_compose_command_both_repos(self, mock_safe_run, orchestrator):
        """Test Docker Compose command on both repositories."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        results = orchestrator.run_docker_compose_command(["ps"], repository="both")

        # Should run for both repos
        assert "tta.dev" in results
        assert "tta.prototype" in results
        assert results["tta.dev"].returncode == 0
        assert results["tta.prototype"].returncode == 0

        # Verify safe_run was called twice
        assert mock_safe_run.call_count == 2

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_compose_command_tta_prototype(self, mock_safe_run, orchestrator):
        """Test Docker Compose command on tta.prototype repository."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        results = orchestrator.run_docker_compose_command(["down"], repository="tta.prototype")

        # Should only run for tta.prototype
        assert "tta.prototype" in results
        assert "tta.dev" not in results
        assert results["tta.prototype"].returncode == 0

        # Verify safe_run was called once
        assert mock_safe_run.call_count == 1

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_compose_command_with_failure(self, mock_safe_run, orchestrator):
        """Test Docker Compose command with failure and retry."""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "compose error"
        mock_safe_run.return_value = mock_result

        # Should raise exception after retries
        with pytest.raises(subprocess.SubprocessError):
            orchestrator.run_docker_compose_command(["invalid"], repository="tta.dev")

        # Verify retry decorator caused multiple attempts (max 3)
        assert mock_safe_run.call_count == 3

    @patch('src.orchestration.orchestrator.safe_run')
    def test_run_docker_compose_command_partial_failure(self, mock_safe_run, orchestrator):
        """Test Docker Compose command with partial failure (one repo fails)."""
        # First call (tta.dev) succeeds, second call (tta.prototype) fails
        success_result = Mock()
        success_result.returncode = 0
        success_result.stdout = "success"
        success_result.stderr = ""

        failure_result = Mock()
        failure_result.returncode = 1
        failure_result.stdout = ""
        failure_result.stderr = "error"

        mock_safe_run.side_effect = [success_result, failure_result, failure_result, failure_result]

        # Should raise exception due to tta.prototype failure
        with pytest.raises(subprocess.SubprocessError):
            orchestrator.run_docker_compose_command(["up"], repository="both")

        # First call succeeds, then 3 retries for tta.prototype
        assert mock_safe_run.call_count == 4

    @patch('src.orchestration.orchestrator.safe_run')
    def test_docker_command_with_complex_args(self, mock_safe_run, orchestrator):
        """Test Docker command with complex arguments."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "container_id"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        result = orchestrator.run_docker_command([
            "run",
            "-d",
            "--name", "test-container",
            "-p", "8080:80",
            "nginx:latest"
        ])

        # Verify command was constructed correctly
        call_args = mock_safe_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert call_args[1] == "run"
        assert "-d" in call_args
        assert "--name" in call_args
        assert "test-container" in call_args
        assert result.returncode == 0

    @patch('src.orchestration.orchestrator.safe_run')
    def test_docker_compose_command_with_env_vars(self, mock_safe_run, orchestrator):
        """Test Docker Compose command execution (env vars handled by safe_run)."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        results = orchestrator.run_docker_compose_command(
            ["up", "-d", "--build"],
            repository="tta.dev"
        )

        # Verify command structure
        call_args = mock_safe_run.call_args[0][0]
        # Command should be docker-compose (not docker compose)
        assert call_args[0] == "docker-compose" or (call_args[0] == "docker" and call_args[1] == "compose")
        assert "up" in call_args
        assert "-d" in call_args
        assert "--build" in call_args

    @patch('src.orchestration.orchestrator.safe_run')
    def test_docker_command_timeout_handling(self, mock_safe_run, orchestrator):
        """Test that Docker command uses correct timeout."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_safe_run.return_value = mock_result

        orchestrator.run_docker_command(["ps"])

        # Verify timeout was set to 120 seconds
        call_kwargs = mock_safe_run.call_args[1]
        assert call_kwargs["timeout"] == 120

    @patch('src.orchestration.orchestrator.safe_run')
    def test_docker_command_output_capture(self, mock_safe_run, orchestrator):
        """Test that Docker command captures output correctly."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "captured stdout"
        mock_result.stderr = "captured stderr"
        mock_safe_run.return_value = mock_result

        result = orchestrator.run_docker_command(["logs", "container"])

        # Verify output was captured
        assert result.stdout == "captured stdout"
        assert result.stderr == "captured stderr"

        # Verify capture_output was True
        call_kwargs = mock_safe_run.call_args[1]
        assert call_kwargs["capture_output"] is True
        assert call_kwargs["text"] is True

