"""

# Logseq: [[TTA.dev/Tests/Test_component_loader]]
Tests for Component Loader abstraction.

This module tests the component loader protocol and implementations
to ensure proper dependency injection functionality.
"""

from unittest.mock import Mock, patch

import pytest

from src.orchestration import (
    FilesystemComponentLoader,
    MockComponentLoader,
    TTAOrchestrator,
)
from src.orchestration.component import Component, ComponentStatus


class MockComponent(Component):
    """Simple mock component for testing."""

    def __init__(
        self, name: str = "test_component", dependencies: list[str] | None = None
    ):
        mock_config = Mock()
        super().__init__(config=mock_config, name=name, dependencies=dependencies or [])
        self.start_called = False
        self.stop_called = False

    def _start_impl(self) -> bool:
        """Mock start implementation."""
        self.start_called = True
        self._status = ComponentStatus.RUNNING
        return True

    def _stop_impl(self) -> bool:
        """Mock stop implementation."""
        self.stop_called = True
        self._status = ComponentStatus.STOPPED
        return True


class TestMockComponentLoader:
    """Test the MockComponentLoader implementation."""

    def test_mock_loader_initialization_empty(self):
        """Test MockComponentLoader with no components."""
        loader = MockComponentLoader()

        loader.validate_paths()  # Should not raise
        components = loader.discover_components()

        assert components == {}

    def test_mock_loader_initialization_with_components(self):
        """Test MockComponentLoader with pre-configured components."""
        comp1 = MockComponent(name="comp1")
        comp2 = MockComponent(name="comp2")

        loader = MockComponentLoader(components={"comp1": comp1, "comp2": comp2})

        loader.validate_paths()  # Should not raise
        components = loader.discover_components()

        assert len(components) == 2
        assert "comp1" in components
        assert "comp2" in components
        assert components["comp1"] == comp1
        assert components["comp2"] == comp2

    def test_mock_loader_returns_copy(self):
        """Test that discover_components returns a copy, not the original."""
        comp1 = MockComponent(name="comp1")
        loader = MockComponentLoader(components={"comp1": comp1})

        components1 = loader.discover_components()
        components2 = loader.discover_components()

        # Should be equal but not the same object
        assert components1 == components2
        assert components1 is not components2


class TestFilesystemComponentLoader:
    """Test the FilesystemComponentLoader implementation."""

    def test_filesystem_loader_validate_paths_missing_tta_dev(self, tmp_path):
        """Test validation fails when tta.dev is missing."""
        mock_config = Mock()
        tta_prototype = tmp_path / "tta.prototype"
        tta_prototype.mkdir()

        loader = FilesystemComponentLoader(
            config=mock_config,
            root_dir=tmp_path,
            tta_dev_path=tmp_path / "tta.dev",  # Doesn't exist
            tta_prototype_path=tta_prototype,
        )

        with pytest.raises(FileNotFoundError, match="tta.dev repository not found"):
            loader.validate_paths()

    def test_filesystem_loader_validate_paths_missing_tta_prototype(self, tmp_path):
        """Test validation fails when tta.prototype is missing."""
        mock_config = Mock()
        tta_dev = tmp_path / "tta.dev"
        tta_dev.mkdir()

        loader = FilesystemComponentLoader(
            config=mock_config,
            root_dir=tmp_path,
            tta_dev_path=tta_dev,
            tta_prototype_path=tmp_path / "tta.prototype",  # Doesn't exist
        )

        with pytest.raises(
            FileNotFoundError, match="tta.prototype repository not found"
        ):
            loader.validate_paths()

    def test_filesystem_loader_validate_paths_success(self, tmp_path):
        """Test validation succeeds when both paths exist."""
        mock_config = Mock()
        tta_dev = tmp_path / "tta.dev"
        tta_prototype = tmp_path / "tta.prototype"
        tta_dev.mkdir()
        tta_prototype.mkdir()

        loader = FilesystemComponentLoader(
            config=mock_config,
            root_dir=tmp_path,
            tta_dev_path=tta_dev,
            tta_prototype_path=tta_prototype,
        )

        # Should not raise
        loader.validate_paths()

    def test_filesystem_loader_discover_no_components_enabled(self, tmp_path):
        """Test discover_components when no components are enabled."""
        mock_config = Mock()
        mock_config.get = Mock(return_value=False)  # All disabled

        tta_dev = tmp_path / "tta.dev"
        tta_prototype = tmp_path / "tta.prototype"
        tta_dev.mkdir()
        tta_prototype.mkdir()

        loader = FilesystemComponentLoader(
            config=mock_config,
            root_dir=tmp_path,
            tta_dev_path=tta_dev,
            tta_prototype_path=tta_prototype,
        )

        components = loader.discover_components()

        assert components == {}


class TestOrchestratorWithComponentLoader:
    """Test TTAOrchestrator with dependency injection."""

    def test_orchestrator_with_mock_loader(self):
        """Test orchestrator initialization with MockComponentLoader."""
        comp1 = MockComponent(name="test_comp1")
        comp2 = MockComponent(name="test_comp2")

        loader = MockComponentLoader(
            components={
                "test_comp1": comp1,
                "test_comp2": comp2,
            }
        )

        # Create orchestrator with injected loader
        orchestrator = TTAOrchestrator(component_loader=loader)

        # Verify components were loaded
        assert len(orchestrator.components) == 2
        assert "test_comp1" in orchestrator.components
        assert "test_comp2" in orchestrator.components
        assert orchestrator.components["test_comp1"] == comp1
        assert orchestrator.components["test_comp2"] == comp2

    def test_orchestrator_with_empty_mock_loader(self):
        """Test orchestrator with empty MockComponentLoader."""
        loader = MockComponentLoader()

        orchestrator = TTAOrchestrator(component_loader=loader)

        assert len(orchestrator.components) == 0

    def test_orchestrator_without_loader_uses_filesystem(self, tmp_path):
        """Test orchestrator falls back to FilesystemComponentLoader when no loader provided."""
        # This test verifies backward compatibility
        # We'll mock the filesystem loader creation to avoid actual filesystem operations

        with patch(
            "src.orchestration.orchestrator.FilesystemComponentLoader"
        ) as mock_loader_class:
            mock_loader_instance = Mock()
            mock_loader_instance.validate_paths = Mock()
            mock_loader_instance.discover_components = Mock(return_value={})
            mock_loader_class.return_value = mock_loader_instance

            TTAOrchestrator()

            # Verify FilesystemComponentLoader was created
            assert mock_loader_class.called
            # Verify validate_paths was called
            assert mock_loader_instance.validate_paths.called
            # Verify discover_components was called
            assert mock_loader_instance.discover_components.called

    def test_orchestrator_component_lifecycle_with_mock_loader(self):
        """Test component lifecycle methods work with injected loader."""
        comp1 = MockComponent(name="lifecycle_comp")

        loader = MockComponentLoader(components={"lifecycle_comp": comp1})
        orchestrator = TTAOrchestrator(component_loader=loader)

        # Test has_component
        assert orchestrator.has_component("lifecycle_comp")
        assert not orchestrator.has_component("nonexistent")

        # Test start_component
        result = orchestrator.start_component("lifecycle_comp")
        assert result is True
        assert comp1.start_called

        # Test stop_component
        result = orchestrator.stop_component("lifecycle_comp")
        assert result is True
        assert comp1.stop_called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
