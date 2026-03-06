# Logseq: [[TTA.dev/Tests/Test_orchestrator]]
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import pytest

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAConfig, TTAOrchestrator
from src.orchestration.component import Component, ComponentStatus


class MockComponent(Component):
    def __init__(
        self, name: str, config: TTAConfig, dependencies: list[str] | None = None
    ):
        super().__init__(config, name=name, dependencies=dependencies)
        self.status = ComponentStatus.STOPPED
        self.dependencies = dependencies if dependencies is not None else []
        self.start_success = True
        self.stop_success = True

    def _start_impl(self) -> bool:
        if self.start_success:
            self.status = ComponentStatus.RUNNING
            return True
        self.status = ComponentStatus.ERROR
        return False

    def _stop_impl(self) -> bool:
        if self.stop_success:
            self.status = ComponentStatus.STOPPED
            return True
        self.status = ComponentStatus.ERROR
        return False


class TestOrchestrator(unittest.TestCase):
    """Test the TTA Orchestrator."""

    @classmethod
    def setUpClass(cls):
        """Check if filesystem structure exists before running tests."""
        # Check if required directories exist
        root_dir = Path(__file__).parent.parent
        tta_dev_path = root_dir / "tta.dev"
        tta_prototype_path = root_dir / "tta.prototype"

        if not (tta_dev_path.exists() and tta_prototype_path.exists()):
            pytest.skip(
                "Skipping integration tests: tta.dev and/or tta.prototype directories not found. "
                "These tests require a complete filesystem structure."
            )

    def setUp(self):
        """
        Set up the test.
        """
        # Create a test configuration
        self.config = TTAConfig()

        # Mock ComponentRegistry
        self.mock_component_registry = mock.Mock()
        self.mock_component_registry.get_registered_component_names.return_value = [
            "mock_component_1",
            "mock_component_2",
            "mock_component_3",
        ]
        # Configure side_effect to return MockComponent instances with specific names and dependencies
        self.mock_component_registry.get_component_class.side_effect = [
            (MockComponent, ["mock_component_2"]),  # For mock_component_1
            (MockComponent, []),  # For mock_component_2
            (
                MockComponent,
                ["mock_component_1"],
            ),  # For mock_component_3 (circular dependency test)
        ]

        with mock.patch(
            "src.orchestration.orchestrator.ComponentRegistry",
            return_value=self.mock_component_registry,
        ):
            # Create the orchestrator
            self.orchestrator = TTAOrchestrator()

    def test_orchestrator_initialization(self):
        """
        Test that the orchestrator initializes correctly.
        """
        # Check that the orchestrator has initialized the component registry
        self.mock_component_registry.get_registered_component_names.assert_called_once()
        assert len(self.orchestrator.components) == 3
        assert "mock_component_1" in self.orchestrator.components
        assert "mock_component_2" in self.orchestrator.components
        assert "mock_component_3" in self.orchestrator.components

    def test_config_initialization(self):
        """
        Test that the configuration initializes correctly.
        """
        # Check that the configuration has the orchestration.components section
        orchestration_components = self.config.get("orchestration.components")
        assert orchestration_components is not None
        assert "player_experience" in orchestration_components

    def test_component_registration(self):
        """
        Test that components are registered correctly.
        """
        assert "mock_component_1" in self.orchestrator.components
        assert "mock_component_2" in self.orchestrator.components
        assert self.orchestrator.components["mock_component_1"].name == "mock_component_1"
        assert self.orchestrator.components["mock_component_2"].name == "mock_component_2"

    def test_component_dependencies(self):
        """
        Test that component dependencies are correct.
        """
        assert "mock_component_2" in self.orchestrator.components["mock_component_1"].dependencies
        assert len(self.orchestrator.components["mock_component_2"].dependencies) == 0

    def test_start_component_success_no_dependencies(self):
        """
        Test successful start of a component without dependencies.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        assert self.orchestrator.start_component(component_name)
        assert component.status == ComponentStatus.RUNNING

    def test_start_component_success_with_dependencies(self):
        """
        Test successful start of a component with dependencies.
        """
        component_name = "mock_component_1"
        component = self.orchestrator.components[component_name]
        dependency = self.orchestrator.components["mock_component_2"]

        assert self.orchestrator.start_component(component_name)
        assert component.status == ComponentStatus.RUNNING
        assert dependency.status == ComponentStatus.RUNNING

    def test_start_component_failure(self):
        """
        Test failure to start a component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.start_success = False

        assert not self.orchestrator.start_component(component_name)
        assert component.status == ComponentStatus.ERROR

    def test_start_component_dependency_failure(self):
        """
        Test failure to start a dependency.
        """
        component_name = "mock_component_1"
        dependency_name = "mock_component_2"
        dependency = self.orchestrator.components[dependency_name]
        dependency.start_success = False

        assert not self.orchestrator.start_component(component_name)
        assert dependency.status == ComponentStatus.ERROR
        assert self.orchestrator.components[component_name].status == ComponentStatus.STOPPED

    def test_start_component_already_running(self):
        """
        Test starting an already running component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING

        assert self.orchestrator.start_component(component_name)
        assert component.status == ComponentStatus.RUNNING

    def test_stop_component_success_no_dependents(self):
        """
        Test successful stop of a component without dependents.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING

        assert self.orchestrator.stop_component(component_name)
        assert component.status == ComponentStatus.STOPPED

    def test_stop_component_success_with_dependents(self):
        """
        Test successful stop of a component with dependents.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        dependent = self.orchestrator.components["mock_component_1"]

        # Start both components first
        self.orchestrator.start_component("mock_component_1")

        assert self.orchestrator.stop_component(component_name)
        assert component.status == ComponentStatus.STOPPED
        assert dependent.status == ComponentStatus.STOPPED

    def test_stop_component_failure(self):
        """
        Test failure to stop a component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING
        component.stop_success = False

        assert not self.orchestrator.stop_component(component_name)
        assert component.status == ComponentStatus.ERROR

    def test_stop_component_dependent_failure(self):
        """
        Test failure to stop a dependent.
        """
        component_name = "mock_component_2"
        dependent_name = "mock_component_1"
        dependent = self.orchestrator.components[dependent_name]

        # Start both components first
        self.orchestrator.start_component(dependent_name)

        dependent.stop_success = False

        assert not self.orchestrator.stop_component(component_name)
        assert dependent.status == ComponentStatus.ERROR
        assert self.orchestrator.components[component_name].status == ComponentStatus.RUNNING

    def test_stop_component_already_stopped(self):
        """
        Test stopping an already stopped component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.STOPPED

        assert self.orchestrator.stop_component(component_name)
        assert component.status == ComponentStatus.STOPPED

    def test_stop_all(self):
        """
        Test stopping all components.
        """
        # Start all components first
        self.orchestrator.start_component("mock_component_1")
        self.orchestrator.start_component("mock_component_3")

        # Stop all components
        self.orchestrator.stop_all()

        # Check that all components are stopped
        for component in self.orchestrator.components.values():
            assert component.status == ComponentStatus.STOPPED

    @mock.patch("src.orchestration.orchestrator.safe_run")
    def test_run_docker_command_success(self, mock_safe_run):
        """
        Test successful execution of a Docker command.
        """
        mock_safe_run.return_value = subprocess.CompletedProcess(
            args=["docker", "ps"],
            returncode=0,
            stdout="CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES",
            stderr="",
        )

        result = self.orchestrator.run_docker_command(["ps"])

        mock_safe_run.assert_called_once_with(
            ["docker", "ps"], text=True, timeout=120, capture_output=True, check=False
        )
        assert result.returncode == 0

    @mock.patch("src.orchestration.orchestrator.safe_run")
    def test_run_docker_command_failure(self, mock_safe_run):
        """
        Test failed execution of a Docker command.
        """
        mock_safe_run.return_value = subprocess.CompletedProcess(
            args=["docker", "ps"],
            returncode=1,
            stdout="",
            stderr="Cannot connect to the Docker daemon.",
        )

        with pytest.raises(subprocess.SubprocessError):
            self.orchestrator.run_docker_command(["ps"])

        calls = [
            mock.call(
                ["docker", "ps"],
                text=True,
                timeout=120,
                capture_output=True,
                check=False,
            )
        ] * 3
        mock_safe_run.assert_has_calls(calls)

    @mock.patch("src.orchestration.orchestrator.safe_run")
    def test_run_docker_compose_command_success(self, mock_safe_run):
        """
        Test successful execution of a Docker Compose command.
        """
        mock_safe_run.return_value = subprocess.CompletedProcess(
            args=["docker-compose", "up", "-d"],
            returncode=0,
            stdout='Creating network "tta-dev_default" with the default driver\nCreating tta-dev_redis_1 ... done',
            stderr="",
        )

        results = self.orchestrator.run_docker_compose_command(["up", "-d"])

        assert "tta.dev" in results
        assert results["tta.dev"].returncode == 0

    @mock.patch("src.orchestration.orchestrator.safe_run")
    def test_run_docker_compose_command_failure(self, mock_safe_run):
        """
        Test failed execution of a Docker Compose command.
        """
        mock_safe_run.return_value = subprocess.CompletedProcess(
            args=["docker-compose", "up", "-d"],
            returncode=1,
            stdout="",
            stderr="ERROR: Some services are not healthy",
        )

        with pytest.raises(subprocess.SubprocessError):
            self.orchestrator.run_docker_compose_command(["up", "-d"])

    @mock.patch("src.orchestration.orchestrator.safe_run")
    def test_run_docker_compose_command_tta_dev_only(self, mock_safe_run):
        """
        Test running Docker Compose command only in tta.dev.
        """
        mock_safe_run.return_value = subprocess.CompletedProcess(
            args=["docker-compose", "up", "-d"],
            returncode=0,
            stdout='Creating network "tta-dev_default" with the default driver\nCreating tta-dev_redis_1 ... done',
            stderr="",
        )

        results = self.orchestrator.run_docker_compose_command(
            ["up", "-d"], repository="tta.dev"
        )

        assert "tta.dev" in results
        assert results["tta.dev"].returncode == 0
        assert "tta.prototype" not in results


if __name__ == "__main__":
    unittest.main()
