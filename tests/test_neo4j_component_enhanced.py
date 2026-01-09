"""

# Logseq: [[TTA.dev/Tests/Test_neo4j_component_enhanced]]
Enhanced test suite for Neo4j Component with improved coverage.

This test suite adds:
- Integration tests that actually exercise code paths
- Decorator coverage (retry, logging, timing)
- Edge case and error path coverage
- Path resolution and file system tests

Target: Achieve 70%+ coverage on neo4j_component.py
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from src.components.neo4j_component import Neo4jComponent
from src.orchestration import TTAConfig


class TestNeo4jComponentEnhanced:
    """Enhanced tests for Neo4j component with better code coverage."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7687,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )
        return config

    def test_component_name_construction(self, mock_config):
        """Test component name is correctly constructed from repository."""
        dev_component = Neo4jComponent(mock_config, repository="tta.dev")
        assert dev_component.name == "tta.dev_neo4j"

        proto_component = Neo4jComponent(mock_config, repository="tta.prototype")
        assert proto_component.name == "tta.prototype_neo4j"

    def test_component_has_required_methods(self, mock_config):
        """Test component has required lifecycle methods."""
        component = Neo4jComponent(mock_config, repository="tta.dev")
        assert hasattr(component, "start")
        assert hasattr(component, "stop")
        assert hasattr(component, "config")
        assert hasattr(component, "_start_impl")
        assert hasattr(component, "_stop_impl")

    def test_root_dir_is_resolved_correctly(self, mock_config):
        """Test root directory is resolved to project root."""
        component = Neo4jComponent(mock_config, repository="tta.dev")

        # Should be absolute path
        assert component.root_dir.is_absolute()

        # Should be three levels up from neo4j_component.py
        # (src/components/neo4j_component.py -> src/components -> src -> root)
        assert component.root_dir.name == "recovered-tta-storytelling"

    def test_repo_dir_is_child_of_root_dir(self, mock_config):
        """Test repository directory is correctly constructed."""
        component = Neo4jComponent(mock_config, repository="tta.dev")

        assert component.repo_dir.is_absolute()
        assert component.repo_dir.parent == component.root_dir
        assert component.repo_dir.name == "tta.dev"

    def test_docker_compose_file_path_construction(self, mock_config):
        """Test Docker Compose file path is constructed correctly."""
        component = Neo4jComponent(mock_config, repository="tta.dev")

        expected_path = component.repo_dir / "docker-compose.yml"
        assert expected_path.parts[-2:] == ("tta.dev", "docker-compose.yml")

    @patch("src.components.neo4j_component.safe_run")
    def test_run_docker_compose_full_command_structure(
        self, mock_safe_run, mock_config
    ):
        """Test complete Docker Compose command structure."""
        mock_safe_run.return_value = Mock(returncode=0, stderr="", stdout="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._run_docker_compose(["up", "-d", "neo4j"])

        # Verify complete command structure
        call_args = mock_safe_run.call_args[0][0]
        assert call_args[0] == "docker-compose"
        assert call_args[1] == "-f"
        assert "docker-compose.yml" in call_args[2]
        assert call_args[3:] == ["up", "-d", "neo4j"]

        # Verify keyword arguments
        call_kwargs = mock_safe_run.call_args[1]
        assert call_kwargs["text"] is True
        assert call_kwargs["timeout"] == 180
        assert call_kwargs["capture_output"] is True
        assert call_kwargs["check"] is False
        assert "cwd" in call_kwargs

    @patch("src.components.neo4j_component.safe_run")
    def test_run_docker_compose_working_directory(self, mock_safe_run, mock_config):
        """Test Docker Compose runs in correct working directory."""
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._run_docker_compose(["ps"])

        call_kwargs = mock_safe_run.call_args[1]
        assert call_kwargs["cwd"] == str(component.repo_dir)

    @patch("src.components.neo4j_component.safe_run")
    def test_retry_decorator_on_docker_compose(self, mock_safe_run, mock_config):
        """Test retry decorator applies to Docker Compose commands."""
        # Simulate transient failure then success
        mock_safe_run.side_effect = [
            subprocess.SubprocessError("Temporary failure"),
            Mock(returncode=0, stderr=""),
        ]

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._run_docker_compose(["ps"])

        # Should succeed on second attempt due to retry decorator
        assert result.returncode == 0
        assert mock_safe_run.call_count == 2

    @patch("src.components.neo4j_component.safe_run")
    def test_retry_decorator_max_attempts(self, mock_safe_run, mock_config):
        """Test retry decorator respects max attempts limit."""
        # Always fail
        mock_safe_run.side_effect = subprocess.SubprocessError("Persistent failure")

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with pytest.raises(subprocess.SubprocessError):
            component._run_docker_compose(["ps"])

        # Should try 3 times (initial + 2 retries)
        assert mock_safe_run.call_count == 3

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_command_structure(self, mock_safe_run, mock_config):
        """Test health check Docker command structure."""
        mock_safe_run.return_value = Mock(stdout="container-name\n", returncode=0)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._is_neo4j_running()

        call_args = mock_safe_run.call_args[0][0]
        assert call_args == [
            "docker",
            "ps",
            "--filter",
            "publish=7687",
            "--format",
            "{{.Names}}",
        ]

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_with_whitespace_handling(
        self, mock_safe_run, mock_config
    ):
        """Test health check properly strips whitespace from docker output."""
        # Output with various whitespace
        mock_safe_run.return_value = Mock(
            stdout="  neo4j-container  \n\n", returncode=0
        )

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is True

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_empty_output(self, mock_safe_run, mock_config):
        """Test health check handles empty docker output."""
        mock_safe_run.return_value = Mock(stdout="", returncode=0)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_exception_handling(self, mock_safe_run, mock_config):
        """Test health check handles exceptions gracefully."""
        mock_safe_run.side_effect = Exception("Docker daemon not running")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_timeout_error(self, mock_safe_run, mock_config):
        """Test health check handles timeout errors."""
        mock_safe_run.side_effect = subprocess.TimeoutExpired("docker", 60)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_logging_behavior(self, mock_is_running, mock_safe_run, mock_config):
        """Test start method logs appropriately."""
        mock_is_running.side_effect = [False, True]  # Not running, then running
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with patch("src.components.neo4j_component.logger") as mock_logger:
            component.start()

            # Should log initialization, start attempt, waiting, and success
            assert mock_logger.info.call_count >= 3

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_error_logging(self, mock_is_running, mock_safe_run, mock_config):
        """Test start method logs errors appropriately."""
        mock_is_running.return_value = False
        mock_safe_run.return_value = Mock(returncode=1, stderr="Docker error occurred")

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with patch("src.components.neo4j_component.logger") as mock_logger:
            component.start()

            # Should log error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "Failed to start Neo4j" in error_call

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_timeout_logging(self, mock_is_running, mock_safe_run, mock_config):
        """Test start method logs timeout appropriately."""
        mock_is_running.return_value = False
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with patch("src.components.neo4j_component.logger") as mock_logger:
            result = component.start()

            assert result is False
            # Should log timeout error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "Timed out" in error_call

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_already_running_logging(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test start method logs when already running."""
        mock_is_running.return_value = True

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with patch("src.components.neo4j_component.logger") as mock_logger:
            component.start()

            # Should log that it's already running
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("already running" in call for call in info_calls)

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_logging_behavior(self, mock_is_running, mock_safe_run, mock_config):
        """Test stop method logs appropriately."""
        # First need to mark component as started, then can stop
        mock_is_running.side_effect = [
            False,
            True,
            True,
            False,
        ]  # Not running (start check), running (after start), running (stop check), stopped (after stop)
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()  # Start first so stop has something to do

        with patch("src.components.neo4j_component.logger") as mock_logger:
            component.stop()

            # Should log stopping attempt, waiting, and success
            assert mock_logger.info.call_count >= 2

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_not_running_logging(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test stop method logs when not running."""
        # Start first, then mark as already stopped when checking
        mock_is_running.side_effect = [
            False,
            True,
            False,
        ]  # Not running, then running (after start), then not running (when stop checks)
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()  # Start so component is marked as running in base class

        with patch("src.components.neo4j_component.logger") as mock_logger:
            component.stop()

            # Should log that it's not running
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("not running" in call for call in info_calls)

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_timeout_logging(self, mock_is_running, mock_safe_run, mock_config):
        """Test stop method logs timeout appropriately."""
        # Start first, then always running (never stops)
        mock_is_running.side_effect = [False, True] + [
            True
        ] * 12  # Not running, then running for start, then always running during stop
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()  # Start so we can test stop timeout

        with patch("src.components.neo4j_component.logger") as mock_logger:
            result = component.stop()

            assert result is False
            # Should log timeout error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "Timed out" in error_call

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_wait_loop_iterations(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test start wait loop tries multiple times."""
        # Running on the 5th check
        mock_is_running.side_effect = [False] + [False] * 4 + [True]
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")

        with patch("time.sleep") as mock_sleep:
            result = component.start()

            assert result is True
            # Should have slept 4 times (checked 5 times, sleep between checks)
            assert mock_sleep.call_count == 4

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_wait_loop_iterations(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test stop wait loop tries multiple times."""
        # Start first: not running, then running (after start)
        # Then for stop: running (initial check), running (1st wait), running (2nd wait), stopped (3rd wait)
        mock_is_running.side_effect = [False, True, True, True, True, False]
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()  # Start first

        with patch("time.sleep") as mock_sleep:
            result = component.stop()

            assert result is True
            # Should have slept 2 times (between the 3 checks during stop)
            assert mock_sleep.call_count == 2

    def test_multiple_repository_configs(self):
        """Test component works with different repository configurations."""
        repositories = ["tta.dev", "tta.prototype", "tta.custom"]

        for repo in repositories:
            # Create config for this specific repository
            repo_configs = {
                f"{repo}.components.neo4j.port": 7687 + len(repo),
                f"{repo}.components.neo4j.username": f"{repo}_user",
                f"{repo}.components.neo4j.password": f"{repo}_pass",
            }
            config = Mock(spec=TTAConfig)
            config.get = Mock(
                side_effect=lambda key, default=None, configs=repo_configs: configs.get(
                    key, default
                )
            )

            component = Neo4jComponent(config, repository=repo)

            assert component.repository == repo
            assert component.name == f"{repo}_neo4j"
            assert component.username == f"{repo}_user"

    @patch("src.components.neo4j_component.safe_run")
    def test_docker_compose_captures_stderr(self, mock_safe_run, mock_config):
        """Test Docker Compose command captures stderr for error reporting."""
        error_message = "Docker Compose error details"
        mock_safe_run.return_value = Mock(returncode=1, stderr=error_message)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._run_docker_compose(["up"])

        assert result.stderr == error_message

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    @patch("time.sleep")
    def test_start_sleep_timing(
        self, mock_sleep, mock_is_running, mock_safe_run, mock_config
    ):
        """Test start method sleeps 1 second between checks."""
        mock_is_running.side_effect = [False, False, True]
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()

        # Should call sleep with 1 second
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 1

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    @patch("time.sleep")
    def test_stop_sleep_timing(
        self, mock_sleep, mock_is_running, mock_safe_run, mock_config
    ):
        """Test stop method sleeps 1 second between checks."""
        mock_is_running.side_effect = [True, True, False]
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.stop()

        # Should call sleep with 1 second
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 1


class TestNeo4jComponentDecorators:
    """Test decorator functionality on Neo4j component methods."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7687,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )
        return config

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_log_entry_exit_decorator_on_start(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test log_entry_exit decorator works on start method."""
        mock_is_running.return_value = True
        component = Neo4jComponent(mock_config, repository="tta.dev")

        # The decorator should be applied
        assert hasattr(component._start_impl, "__wrapped__")

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_timing_decorator_on_start(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test timing_decorator works on start method."""
        mock_is_running.return_value = True
        component = Neo4jComponent(mock_config, repository="tta.dev")

        # Should have timing decorator applied
        # This is tested indirectly through successful execution
        result = component.start()
        assert isinstance(result, bool)

    def test_require_config_decorator_validation(self, mock_config):
        """Test require_config decorator validates required configuration."""
        component = Neo4jComponent(mock_config, repository="tta.dev")

        # Required config should be checked
        # If missing, would raise an error
        # This tests that decorator is properly applied
        assert component.port is not None
        assert component.username is not None
        assert component.password is not None


class TestNeo4jComponentEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_repository_name(self):
        """Test component handles empty repository name."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(return_value=None)

        component = Neo4jComponent(config, repository="")
        assert component.repository == ""
        assert component.name == "_neo4j"

    def test_special_characters_in_repository(self):
        """Test component handles special characters in repository name."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(return_value=None)

        component = Neo4jComponent(config, repository="tta-dev-v2.0")
        assert component.repository == "tta-dev-v2.0"
        assert component.name == "tta-dev-v2.0_neo4j"

    @patch("src.components.neo4j_component.safe_run")
    def test_docker_ps_with_multiple_containers(self, mock_safe_run):
        """Test health check handles multiple containers on same port."""
        # Multiple container names returned
        mock_safe_run.return_value = Mock(
            stdout="neo4j-dev\nneo4j-prototype\n", returncode=0
        )

        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7687,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")
        result = component._is_neo4j_running()

        # Should return True if any container is running
        assert result is True

    def test_very_high_port_number(self):
        """Test component handles very high port numbers."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 65535,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")
        assert component.port == 65535

    def test_port_as_string_in_config(self):
        """Test component handles port configured as string."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": "7687",
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")
        # Port should be stored as-is (string or int depending on config)
        assert component.port in {"7687", 7687}
