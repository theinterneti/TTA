"""
Unit tests for Neo4j Component.

Tests cover:
- Component lifecycle (initialization, start, stop)
- Health checks and monitoring
- Configuration management
- Error handling
- Docker integration

This test suite ensures the Neo4j component meets the 70% coverage threshold
required for staging promotion.
"""

from unittest.mock import Mock, patch

import pytest

from src.components.neo4j_component import Neo4jComponent
from src.orchestration import TTAConfig


class TestNeo4jComponentLifecycle:
    """Test Neo4j component lifecycle operations."""

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

    def test_initialization_with_default_config(self, mock_config):
        """Test component initializes correctly with default configuration."""
        component = Neo4jComponent(mock_config, repository="tta.dev")

        assert component is not None
        assert component.name == "tta.dev_neo4j"
        assert component.repository == "tta.dev"
        assert component.port == 7687
        assert component.username == "neo4j"
        assert component.password == "test_password"  # noqa: S105

    def test_initialization_with_prototype_repository(self, mock_config):
        """Test component initializes correctly for prototype repository."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.prototype.components.neo4j.port": 7688,
                "tta.prototype.components.neo4j.username": "neo4j",
                "tta.prototype.components.neo4j.password": "proto_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.prototype")

        assert component.name == "tta.prototype_neo4j"
        assert component.repository == "tta.prototype"
        assert component.port == 7688
        assert component.password == "proto_password"  # noqa: S105

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_success(self, mock_is_running, mock_safe_run, mock_config):
        """Test component starts successfully when not already running."""
        # Setup mocks
        mock_is_running.side_effect = [False] + [True] * 30  # Not running, then running
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component.start()

        assert result is True
        mock_safe_run.assert_called_once()
        # Verify docker-compose command was called
        call_args = mock_safe_run.call_args[0][0]
        assert "docker-compose" in call_args
        assert "up" in call_args
        assert "-d" in call_args
        assert "neo4j" in call_args

    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_already_running(self, mock_is_running, mock_config):
        """Test component start is idempotent when already running."""
        mock_is_running.return_value = True

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component.start()

        assert result is True
        # Should not attempt to start if already running

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_timeout(self, mock_is_running, mock_safe_run, mock_config):
        """Test component handles timeout when Neo4j doesn't start."""
        # Setup: docker-compose succeeds but Neo4j never becomes running
        mock_is_running.return_value = False
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component.start()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_start_docker_compose_failure(
        self, mock_is_running, mock_safe_run, mock_config
    ):
        """Test component handles Docker Compose command failure."""
        mock_is_running.return_value = False
        mock_safe_run.return_value = Mock(returncode=1, stderr="Docker error")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component.start()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_success(self, mock_is_running, mock_safe_run, mock_config):
        """Test component stops successfully."""
        # Setup: component starts running, then stops
        # For start: not running initially, then running
        # For stop: running initially, then stopped
        mock_is_running.side_effect = [
            False,  # start: initial check (not running)
            True,
            True,
            True,  # start: waiting for start (running)
            True,  # stop: initial check (running)
            False,
            False,  # stop: waiting for stop (stopped)
        ]
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        # Start the component first
        start_result = component.start()
        assert start_result is True

        # Then stop it
        stop_result = component.stop()
        assert stop_result is True

        # Verify both docker-compose commands were called
        assert mock_safe_run.call_count == 2
        # First call should be 'up', second should be 'stop'
        first_call_args = mock_safe_run.call_args_list[0][0][0]
        second_call_args = mock_safe_run.call_args_list[1][0][0]
        assert "up" in first_call_args
        assert "stop" in second_call_args

    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_not_running(self, mock_is_running, mock_config):
        """Test component stop when not running."""
        mock_is_running.return_value = False

        component = Neo4jComponent(mock_config, repository="tta.dev")
        # Component not started, but stop should still succeed
        result = component.stop()

        assert result is True


class TestNeo4jHealthChecks:
    """Test Neo4j health check functionality."""

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
    def test_is_neo4j_running_when_healthy(self, mock_safe_run, mock_config):
        """Test health check returns True when Neo4j is running."""
        # Mock docker ps returning a container name
        mock_safe_run.return_value = Mock(stdout="neo4j-container\n", returncode=0)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is True
        # Verify docker ps command was called with correct port
        call_args = mock_safe_run.call_args[0][0]
        assert "docker" in call_args
        assert "ps" in call_args
        assert "publish=7687" in call_args

    @patch("src.components.neo4j_component.safe_run")
    def test_is_neo4j_running_when_down(self, mock_safe_run, mock_config):
        """Test health check returns False when Neo4j is down."""
        # Mock docker ps returning empty output
        mock_safe_run.return_value = Mock(stdout="", returncode=0)

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component._is_neo4j_running()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    def test_health_check_uses_correct_port(self, mock_safe_run, mock_config):
        """Test health check uses the configured port."""
        mock_safe_run.return_value = Mock(stdout="neo4j-container\n", returncode=0)

        # Test with custom port
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 9999,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")
        component._is_neo4j_running()

        # Verify the correct port was used in docker ps command
        call_args = mock_safe_run.call_args[0][0]
        assert "publish=9999" in call_args


class TestNeo4jConfiguration:
    """Test Neo4j configuration management."""

    def test_config_port_loading(self):
        """Test component loads port from configuration."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7777,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")

        assert component.port == 7777

    def test_config_auth_loading(self):
        """Test component loads authentication from configuration."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7687,
                "tta.dev.components.neo4j.username": "custom_user",
                "tta.dev.components.neo4j.password": "custom_pass",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")

        assert component.username == "custom_user"
        assert component.password == "custom_pass"  # noqa: S105

    def test_config_defaults(self):
        """Test component uses defaults when config values missing."""
        config = Mock(spec=TTAConfig)
        # Return default values when config.get is called with a default parameter
        config.get = Mock(side_effect=lambda key, default=None: default)

        component = Neo4jComponent(config, repository="tta.dev")

        # Should use defaults provided in get() calls
        assert component.port == 7687
        assert component.username == "neo4j"
        assert component.password == "password"  # noqa: S105

    def test_repository_path_resolution(self):
        """Test component resolves repository path correctly."""
        config = Mock(spec=TTAConfig)
        config.get = Mock(
            side_effect=lambda key, default=None: {
                "tta.dev.components.neo4j.port": 7687,
                "tta.dev.components.neo4j.username": "neo4j",
                "tta.dev.components.neo4j.password": "test_password",
            }.get(key, default)
        )

        component = Neo4jComponent(config, repository="tta.dev")

        assert component.repo_dir.name == "tta.dev"
        assert component.repo_dir.is_absolute()


class TestNeo4jDockerIntegration:
    """Test Neo4j Docker integration."""

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
    def test_docker_compose_command_construction(self, mock_safe_run, mock_config):
        """Test Docker Compose command is constructed correctly."""
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._run_docker_compose(["up", "-d", "neo4j"])

        call_args = mock_safe_run.call_args[0][0]
        assert call_args[0] == "docker-compose"
        assert "-f" in call_args
        assert "up" in call_args
        assert "-d" in call_args
        assert "neo4j" in call_args

    @patch("src.components.neo4j_component.safe_run")
    def test_docker_compose_uses_correct_compose_file(self, mock_safe_run, mock_config):
        """Test Docker Compose uses correct compose file path."""
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._run_docker_compose(["ps"])

        call_args = mock_safe_run.call_args[0][0]
        # Find the -f flag and check the next argument
        f_index = call_args.index("-f")
        compose_file_path = call_args[f_index + 1]

        assert "tta.dev" in compose_file_path
        assert "docker-compose.yml" in compose_file_path

    @patch("src.components.neo4j_component.safe_run")
    def test_docker_compose_timeout_configuration(self, mock_safe_run, mock_config):
        """Test Docker Compose command has appropriate timeout."""
        mock_safe_run.return_value = Mock(returncode=0, stderr="")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component._run_docker_compose(["up", "-d"])

        # Check timeout parameter in safe_run call
        call_kwargs = mock_safe_run.call_args[1]
        assert call_kwargs.get("timeout") == 180


class TestNeo4jErrorHandling:
    """Test Neo4j error handling."""

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
    def test_start_handles_exception(self, mock_is_running, mock_safe_run, mock_config):
        """Test component handles exceptions during start."""
        mock_is_running.return_value = False
        mock_safe_run.side_effect = Exception("Unexpected error")

        component = Neo4jComponent(mock_config, repository="tta.dev")
        result = component.start()

        assert result is False

    @patch("src.components.neo4j_component.safe_run")
    @patch.object(Neo4jComponent, "_is_neo4j_running")
    def test_stop_handles_exception(self, mock_is_running, mock_safe_run, mock_config):
        """Test component handles exceptions during stop."""
        # Setup: component is running, but docker-compose throws exception
        mock_is_running.return_value = True
        # First call succeeds (for start), second call fails (for stop)
        mock_safe_run.side_effect = [
            Mock(returncode=0, stderr=""),  # start succeeds
            Exception("Unexpected error"),  # stop fails
        ]

        component = Neo4jComponent(mock_config, repository="tta.dev")
        component.start()  # Start first
        result = component.stop()  # Then try to stop (will fail)

        assert result is False
