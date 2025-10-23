"""
Tests for TTAOrchestrator component lifecycle methods.

This module tests component start/stop, status retrieval, and lifecycle management
to improve coverage of orchestrator.py.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.orchestration import TTAOrchestrator
from src.orchestration.component import Component, ComponentStatus


class MockComponent(Component):
    """Mock component for testing."""

    def __init__(self, config=None, name: str = "mock_component", **kwargs):
        super().__init__(config=config or Mock(), name=name, **kwargs)
        self.start_called = False
        self.stop_called = False

    def start(self) -> bool:
        """Mock start method."""
        self.start_called = True
        self.status = ComponentStatus.RUNNING
        return True

    def stop(self) -> bool:
        """Mock stop method."""
        self.stop_called = True
        self.status = ComponentStatus.STOPPED
        return True


class TestOrchestratorComponentLifecycle:
    """Test suite for orchestrator component lifecycle methods."""

    @pytest.fixture
    def orchestrator_with_mock_components(self):
        """Create orchestrator with mock components for testing."""
        # Mock the validation and import methods to prevent filesystem operations
        with patch(
            "src.orchestration.orchestrator.TTAOrchestrator._validate_repositories"
        ):
            with patch(
                "src.orchestration.orchestrator.TTAOrchestrator._import_components"
            ):
                # Create orchestrator (validation and import are mocked)
                orchestrator = TTAOrchestrator()

                # Clear any components that might have been loaded
                orchestrator.components.clear()

                # Add mock components
                mock_comp1 = MockComponent(name="component1")
                mock_comp2 = MockComponent(name="component2")
                orchestrator.components["component1"] = mock_comp1
                orchestrator.components["component2"] = mock_comp2

                return orchestrator

    def test_has_component_true(self, orchestrator_with_mock_components):
        """Test has_component returns True for existing component."""
        assert orchestrator_with_mock_components.has_component("component1")

    def test_has_component_false(self, orchestrator_with_mock_components):
        """Test has_component returns False for non-existing component."""
        assert not orchestrator_with_mock_components.has_component("nonexistent")

    def test_start_component_success(self, orchestrator_with_mock_components):
        """Test start_component successfully starts a component."""
        result = orchestrator_with_mock_components.start_component("component1")

        assert result is True
        assert orchestrator_with_mock_components.components["component1"].start_called

    def test_start_component_nonexistent(self, orchestrator_with_mock_components):
        """Test start_component returns False for non-existing component."""
        result = orchestrator_with_mock_components.start_component("nonexistent")

        assert result is False

    def test_stop_component_success(self, orchestrator_with_mock_components):
        """Test stop_component successfully stops a component."""
        # Start component first
        orchestrator_with_mock_components.start_component("component1")

        # Stop component
        result = orchestrator_with_mock_components.stop_component("component1")

        assert result is True
        assert orchestrator_with_mock_components.components["component1"].stop_called

    def test_stop_component_nonexistent(self, orchestrator_with_mock_components):
        """Test stop_component returns False for non-existing component."""
        result = orchestrator_with_mock_components.stop_component("nonexistent")

        assert result is False

    def test_get_component_status_existing(self, orchestrator_with_mock_components):
        """Test get_component_status returns status for existing component."""
        status = orchestrator_with_mock_components.get_component_status("component1")

        assert status is not None
        assert status == ComponentStatus.STOPPED

    def test_get_component_status_nonexistent(self, orchestrator_with_mock_components):
        """Test get_component_status returns None for non-existing component."""
        status = orchestrator_with_mock_components.get_component_status("nonexistent")

        assert status is None

    def test_get_all_statuses(self, orchestrator_with_mock_components):
        """Test get_all_statuses returns status for all components."""
        statuses = orchestrator_with_mock_components.get_all_statuses()

        assert isinstance(statuses, dict)
        assert "component1" in statuses
        assert "component2" in statuses
        assert statuses["component1"] == ComponentStatus.STOPPED
        assert statuses["component2"] == ComponentStatus.STOPPED

    def test_start_all_components(self, orchestrator_with_mock_components):
        """Test start_all starts all components."""
        result = orchestrator_with_mock_components.start_all()

        assert result is True
        assert orchestrator_with_mock_components.components["component1"].start_called
        assert orchestrator_with_mock_components.components["component2"].start_called

    def test_stop_all_components(self, orchestrator_with_mock_components):
        """Test stop_all stops all components."""
        # Start components first
        orchestrator_with_mock_components.start_all()

        # Stop all
        result = orchestrator_with_mock_components.stop_all()

        assert result is True
        assert orchestrator_with_mock_components.components["component1"].stop_called
        assert orchestrator_with_mock_components.components["component2"].stop_called

    def test_display_status(self, orchestrator_with_mock_components, capsys):
        """Test display_status prints component statuses."""
        orchestrator_with_mock_components.display_status()

        # Capture output
        captured = capsys.readouterr()

        # Verify output contains component names
        assert "component1" in captured.out or "component1" in captured.err
        assert "component2" in captured.out or "component2" in captured.err

    def test_topological_sort_simple(self, orchestrator_with_mock_components):
        """Test _topological_sort with simple dependency graph."""
        # Create simple dependency graph: A -> B -> C
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }

        result = orchestrator_with_mock_components._topological_sort(graph)

        # C should come before B, B should come before A
        assert result.index("C") < result.index("B")
        assert result.index("B") < result.index("A")

    def test_topological_sort_no_dependencies(self, orchestrator_with_mock_components):
        """Test _topological_sort with no dependencies."""
        graph = {
            "A": [],
            "B": [],
            "C": [],
        }

        result = orchestrator_with_mock_components._topological_sort(graph)

        # All nodes should be in result
        assert len(result) == 3
        assert "A" in result
        assert "B" in result
        assert "C" in result

    def test_topological_sort_complex(self, orchestrator_with_mock_components):
        """Test _topological_sort with complex dependency graph."""
        # Create complex graph:
        #   A -> B
        #   A -> C
        #   B -> D
        #   C -> D
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        result = orchestrator_with_mock_components._topological_sort(graph)

        # D should come before B and C, B and C should come before A
        assert result.index("D") < result.index("B")
        assert result.index("D") < result.index("C")
        assert result.index("B") < result.index("A")
        assert result.index("C") < result.index("A")

    def test_start_component_with_failure(self, orchestrator_with_mock_components):
        """Test start_component handles component start failure."""
        # Create component that fails to start
        failing_component = MockComponent(name="failing_component")
        failing_component.start = Mock(return_value=False)
        orchestrator_with_mock_components.components["failing_component"] = failing_component

        result = orchestrator_with_mock_components.start_component("failing_component")

        assert result is False

    def test_stop_component_with_failure(self, orchestrator_with_mock_components):
        """Test stop_component handles component stop failure."""
        # Create component that fails to stop
        failing_component = MockComponent(name="failing_component")
        failing_component.stop = Mock(return_value=False)
        orchestrator_with_mock_components.components["failing_component"] = failing_component

        result = orchestrator_with_mock_components.stop_component("failing_component")

        assert result is False

    def test_start_all_with_partial_failure(self, orchestrator_with_mock_components):
        """Test start_all continues even if one component fails."""
        # Make component1 fail to start
        orchestrator_with_mock_components.components["component1"].start = Mock(return_value=False)

        result = orchestrator_with_mock_components.start_all()

        # Should still attempt to start component2
        assert orchestrator_with_mock_components.components["component2"].start_called

    def test_stop_all_with_partial_failure(self, orchestrator_with_mock_components):
        """Test stop_all continues even if one component fails."""
        # Start components first
        orchestrator_with_mock_components.start_all()

        # Make component1 fail to stop
        orchestrator_with_mock_components.components["component1"].stop = Mock(return_value=False)

        result = orchestrator_with_mock_components.stop_all()

        # Should still attempt to stop component2
        assert orchestrator_with_mock_components.components["component2"].stop_called

    def test_display_status(self, orchestrator_with_mock_components):
        """Test display_status method."""
        orchestrator = orchestrator_with_mock_components

        # Set component statuses
        orchestrator.components["component1"].status = ComponentStatus.RUNNING
        orchestrator.components["component2"].status = ComponentStatus.STOPPED

        # Call display_status (should print a table)
        # This method uses rich.console.print, so we just verify it runs without error
        orchestrator.display_status()

    def test_get_component_status_missing_component(self, orchestrator_with_mock_components):
        """Test get_component_status with missing component."""
        orchestrator = orchestrator_with_mock_components

        status = orchestrator.get_component_status("nonexistent")

        assert status is None
