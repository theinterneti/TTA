"""

# Logseq: [[TTA.dev/Tests/Test_orchestration_integration]]
Integration tests for orchestration module.

These tests focus on testing the orchestration module with more realistic
scenarios and less mocking to increase coverage.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.orchestration.component import Component, ComponentStatus
from src.orchestration.config import TTAConfig
from src.orchestration.orchestrator import TTAOrchestrator


class TestComponentIntegration:
    """Integration tests for Component class."""

    def test_component_lifecycle_complete(self):
        """Test complete component lifecycle: init -> start -> stop."""
        # Arrange
        mock_config = Mock()
        component = Component(
            config=mock_config, name="lifecycle_test", dependencies=[]
        )

        # Assert initial state
        assert component.status == ComponentStatus.STOPPED
        assert component.process is None

        # Act - Start
        with patch.object(component, "_start_impl", return_value=True):
            start_result = component.start()

        # Assert after start
        assert start_result is True
        assert component.status == ComponentStatus.RUNNING

        # Act - Stop
        with patch.object(component, "_stop_impl", return_value=True):
            stop_result = component.stop()

        # Assert after stop
        assert stop_result is True
        assert component.status == ComponentStatus.STOPPED

    def test_component_start_failure_sets_error_status(self):
        """Test that failed start sets ERROR status."""
        # Arrange
        mock_config = Mock()
        component = Component(config=mock_config, name="fail_test", dependencies=[])

        # Act - Start with failure
        with patch.object(component, "_start_impl", return_value=False):
            result = component.start()

        # Assert
        assert result is False
        assert component.status == ComponentStatus.ERROR

    def test_component_start_exception_sets_error_status(self):
        """Test that exception during start sets ERROR status."""
        # Arrange
        mock_config = Mock()
        component = Component(
            config=mock_config, name="exception_test", dependencies=[]
        )

        # Act - Start with exception
        with patch.object(
            component, "_start_impl", side_effect=RuntimeError("Test error")
        ):
            result = component.start()

        # Assert
        assert result is False
        assert component.status == ComponentStatus.ERROR

    def test_component_stop_failure_sets_error_status(self):
        """Test that failed stop sets ERROR status."""
        # Arrange
        mock_config = Mock()
        component = Component(
            config=mock_config, name="stop_fail_test", dependencies=[]
        )
        component.status = ComponentStatus.RUNNING

        # Act - Stop with failure
        with patch.object(component, "_stop_impl", return_value=False):
            result = component.stop()

        # Assert
        assert result is False
        assert component.status == ComponentStatus.ERROR


class TestConfigIntegration:
    """Integration tests for TTAConfig class."""

    def test_config_nested_set_and_get(self):
        """Test setting and getting deeply nested config values."""
        # Arrange
        config = TTAConfig()

        # Act
        config.set("level1.level2.level3.key", "deep_value")
        result = config.get("level1.level2.level3.key")

        # Assert
        assert result == "deep_value"

    def test_config_overwrite_existing_value(self):
        """Test overwriting existing config value."""
        # Arrange
        config = TTAConfig()
        config.set("test.key", "original")

        # Act
        config.set("test.key", "updated")
        result = config.get("test.key")

        # Assert
        assert result == "updated"

    def test_config_get_with_none_default(self):
        """Test getting nonexistent key with None default."""
        # Arrange
        config = TTAConfig()

        # Act
        result = config.get("nonexistent.key", default=None)

        # Assert
        assert result is None


class TestOrchestratorIntegration:
    """Integration tests for TTAOrchestrator."""

    @pytest.fixture
    def orchestrator_minimal(self, tmp_path):
        """Create minimal orchestrator for integration testing."""
        tta_dev = tmp_path / "tta.dev"
        tta_prototype = tmp_path / "tta.prototype"
        tta_dev.mkdir()
        tta_prototype.mkdir()

        with (
            patch.object(Path, "cwd", return_value=tmp_path),
            patch(
                "src.orchestration.orchestrator.TTAOrchestrator._validate_repositories"
            ),
            patch("src.orchestration.orchestrator.TTAOrchestrator._import_components"),
        ):
            orchestrator = TTAOrchestrator()
            orchestrator.tta_dev_path = tta_dev
            orchestrator.tta_prototype_path = tta_prototype
            yield orchestrator

    def test_orchestrator_component_registration_flow(self, orchestrator_minimal):
        """Test complete component registration and management flow."""
        # Arrange
        orchestrator = orchestrator_minimal
        mock_config = Mock()
        component = Component(config=mock_config, name="flow_test", dependencies=[])

        # Act - Register component
        orchestrator.components["flow_test"] = component

        # Assert - Component is registered
        assert orchestrator.has_component("flow_test")
        assert orchestrator.get_component_status("flow_test") == ComponentStatus.STOPPED

        # Act - Start component
        with patch.object(component, "_start_impl", return_value=True):
            start_result = orchestrator.start_component("flow_test")

        # Assert - Component is running
        assert start_result is True
        assert orchestrator.get_component_status("flow_test") == ComponentStatus.RUNNING

        # Act - Stop component
        with patch.object(component, "_stop_impl", return_value=True):
            stop_result = orchestrator.stop_component("flow_test")

        # Assert - Component is stopped
        assert stop_result is True
        assert orchestrator.get_component_status("flow_test") == ComponentStatus.STOPPED

    def test_orchestrator_multiple_components_lifecycle(self, orchestrator_minimal):
        """Test managing multiple components through lifecycle."""
        # Arrange
        orchestrator = orchestrator_minimal
        mock_config = Mock()

        comp1 = Component(config=mock_config, name="comp1", dependencies=[])
        comp2 = Component(config=mock_config, name="comp2", dependencies=[])
        comp3 = Component(config=mock_config, name="comp3", dependencies=[])

        orchestrator.components = {"comp1": comp1, "comp2": comp2, "comp3": comp3}

        # Act - Start all
        with patch.object(comp1, "_start_impl", return_value=True):
            with patch.object(comp2, "_start_impl", return_value=True):
                with patch.object(comp3, "_start_impl", return_value=True):
                    result = orchestrator.start_all()

        # Assert - All started
        assert result is True
        assert orchestrator.get_component_status("comp1") == ComponentStatus.RUNNING
        assert orchestrator.get_component_status("comp2") == ComponentStatus.RUNNING
        assert orchestrator.get_component_status("comp3") == ComponentStatus.RUNNING

        # Act - Stop all
        with patch.object(comp1, "_stop_impl", return_value=True):
            with patch.object(comp2, "_stop_impl", return_value=True):
                with patch.object(comp3, "_stop_impl", return_value=True):
                    result = orchestrator.stop_all()

        # Assert - All stopped
        assert result is True
        assert orchestrator.get_component_status("comp1") == ComponentStatus.STOPPED
        assert orchestrator.get_component_status("comp2") == ComponentStatus.STOPPED
        assert orchestrator.get_component_status("comp3") == ComponentStatus.STOPPED

    def test_orchestrator_get_all_statuses_multiple_states(self, orchestrator_minimal):
        """Test getting all statuses with components in different states."""
        # Arrange
        orchestrator = orchestrator_minimal
        mock_config = Mock()

        running_comp = Component(config=mock_config, name="running", dependencies=[])
        running_comp.status = ComponentStatus.RUNNING

        stopped_comp = Component(config=mock_config, name="stopped", dependencies=[])
        stopped_comp.status = ComponentStatus.STOPPED

        error_comp = Component(config=mock_config, name="error", dependencies=[])
        error_comp.status = ComponentStatus.ERROR

        orchestrator.components = {
            "running": running_comp,
            "stopped": stopped_comp,
            "error": error_comp,
        }

        # Act
        statuses = orchestrator.get_all_statuses()

        # Assert
        assert statuses == {
            "running": ComponentStatus.RUNNING,
            "stopped": ComponentStatus.STOPPED,
            "error": ComponentStatus.ERROR,
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
