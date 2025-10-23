import sys
import unittest
from pathlib import Path
from unittest import mock

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
        self.assertEqual(len(self.orchestrator.components), 3)
        self.assertIn("mock_component_1", self.orchestrator.components)
        self.assertIn("mock_component_2", self.orchestrator.components)
        self.assertIn("mock_component_3", self.orchestrator.components)

    def test_config_initialization(self):
        """
        Test that the configuration initializes correctly.
        """
        # Check that the configuration has the orchestration.components section
        orchestration_components = self.config.get("orchestration.components")
        self.assertIsNotNone(orchestration_components)
        self.assertIn("player_experience", orchestration_components)

    def test_component_registration(self):
        """
        Test that components are registered correctly.
        """
        self.assertIn("mock_component_1", self.orchestrator.components)
        self.assertIn("mock_component_2", self.orchestrator.components)
        self.assertEqual(
            self.orchestrator.components["mock_component_1"].name, "mock_component_1"
        )
        self.assertEqual(
            self.orchestrator.components["mock_component_2"].name, "mock_component_2"
        )

    def test_component_dependencies(self):
        """
        Test that component dependencies are correct.
        """
        self.assertIn(
            "mock_component_2",
            self.orchestrator.components["mock_component_1"].dependencies,
        )
        self.assertEqual(
            len(self.orchestrator.components["mock_component_2"].dependencies), 0
        )

    def test_start_component_success_no_dependencies(self):
        """
        Test successful start of a component without dependencies.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        self.assertTrue(self.orchestrator.start_component(component_name))
        self.assertEqual(component.status, ComponentStatus.RUNNING)

    def test_start_component_success_with_dependencies(self):
        """
        Test successful start of a component with dependencies.
        """
        component_name = "mock_component_1"
        component = self.orchestrator.components[component_name]
        dependency = self.orchestrator.components["mock_component_2"]

        self.assertTrue(self.orchestrator.start_component(component_name))
        self.assertEqual(component.status, ComponentStatus.RUNNING)
        self.assertEqual(dependency.status, ComponentStatus.RUNNING)

    def test_start_component_failure(self):
        """
        Test failure to start a component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.start_success = False

        self.assertFalse(self.orchestrator.start_component(component_name))
        self.assertEqual(component.status, ComponentStatus.ERROR)

    def test_start_component_dependency_failure(self):
        """
        Test failure to start a dependency.
        """
        component_name = "mock_component_1"
        dependency_name = "mock_component_2"
        dependency = self.orchestrator.components[dependency_name]
        dependency.start_success = False

        self.assertFalse(self.orchestrator.start_component(component_name))
        self.assertEqual(dependency.status, ComponentStatus.ERROR)
        self.assertEqual(
            self.orchestrator.components[component_name].status, ComponentStatus.STOPPED
        )

    def test_start_component_already_running(self):
        """
        Test starting an already running component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING

        self.assertTrue(self.orchestrator.start_component(component_name))
        self.assertEqual(component.status, ComponentStatus.RUNNING)

    def test_stop_component_success_no_dependents(self):
        """
        Test successful stop of a component without dependents.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING

        self.assertTrue(self.orchestrator.stop_component(component_name))
        self.assertEqual(component.status, ComponentStatus.STOPPED)

    def test_stop_component_success_with_dependents(self):
        """
        Test successful stop of a component with dependents.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        dependent = self.orchestrator.components["mock_component_1"]

        # Start both components first
        self.orchestrator.start_component("mock_component_1")

        self.assertTrue(self.orchestrator.stop_component(component_name))
        self.assertEqual(component.status, ComponentStatus.STOPPED)
        self.assertEqual(dependent.status, ComponentStatus.STOPPED)

    def test_stop_component_failure(self):
        """
        Test failure to stop a component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.RUNNING
        component.stop_success = False

        self.assertFalse(self.orchestrator.stop_component(component_name))
        self.assertEqual(component.status, ComponentStatus.ERROR)

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

        self.assertFalse(self.orchestrator.stop_component(component_name))
        self.assertEqual(dependent.status, ComponentStatus.ERROR)
        self.assertEqual(
            self.orchestrator.components[component_name].status, ComponentStatus.RUNNING
        )

    def test_stop_component_already_stopped(self):
        """
        Test stopping an already stopped component.
        """
        component_name = "mock_component_2"
        component = self.orchestrator.components[component_name]
        component.status = ComponentStatus.STOPPED

        self.assertTrue(self.orchestrator.stop_component(component_name))
        self.assertEqual(component.status, ComponentStatus.STOPPED)


if __name__ == "__main__":
    unittest.main()
