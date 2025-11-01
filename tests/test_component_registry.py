"""
Test the TTA Component Registry.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration.component import Component
from src.orchestration.component_registry import ComponentRegistry
from src.orchestration.config import TTAConfig


# Dummy Component for testing
class DummyComponent(Component):
    def __init__(
        self, name: str, config: TTAConfig, dependencies: list[str] | None = None
    ):
        super().__init__(config, name=name, dependencies=dependencies)

    def _start_impl(self) -> bool:
        return True

    def _stop_impl(self) -> bool:
        return True


# Another Dummy Component for testing subclass check
class NonComponentClass:
    pass


class TestComponentRegistry(unittest.TestCase):
    """Test the TTA Component Registry."""

    def setUp(self):
        """
        Set up the test.
        """
        self.root_dir = Path(__file__).parent.parent.parent

        # Mock TTAConfig
        self.mock_config = mock.Mock(spec=TTAConfig)
        self.mock_config.get.return_value = {
            "valid_component": {
                "path": "tests.temp_components.dummy_component",
                "class_name": "DummyComponent",
                "dependencies": ["dep1"],
            },
            "non_subclass_component": {
                "path": "tests.temp_components.non_component_class",
                "class_name": "NonComponentClass",
            },
            "non_existent_class_component": {
                "path": "tests.temp_components.dummy_component",
                "class_name": "NonExistentClass",
            },
            "import_error_component": {
                "path": "tests.temp_components.import_error_module",
                "class_name": "ImportErrorComponent",
            },
        }

        # Create temporary component files for dynamic loading
        self.temp_components_dir = self.root_dir / "tests" / "temp_components"
        self.temp_components_dir.mkdir(parents=True, exist_ok=True)

        (self.temp_components_dir / "__init__.py").touch()
        (self.temp_components_dir / "dummy_component.py").write_text(
            """from src.orchestration.component import Component
from tests.test_component_registry import DummyComponent
"""
        )
        (self.temp_components_dir / "non_component_class.py").write_text(
            """class NonComponentClass: pass"""
        )
        # For import_error_component, we'll simulate an import error by not creating the file

        self.registry = ComponentRegistry(self.mock_config, self.root_dir)

    def tearDown(self):
        """
        Clean up after the test.
        """
        # Clean up temporary component files
        import shutil

        if self.temp_components_dir.exists():
            shutil.rmtree(self.temp_components_dir)

    def test_load_component_definitions(self):
        """
        Test that component definitions are loaded correctly.
        """
        self.mock_config.get.assert_called_with("orchestration.components", {})
        self.assertIn("valid_component", self.registry._registered_components)
        self.assertNotIn("malformed_component_1", self.registry._registered_components)
        self.assertNotIn("malformed_component_2", self.registry._registered_components)
        self.assertIn("non_subclass_component", self.registry._registered_components)
        self.assertIn(
            "non_existent_class_component", self.registry._registered_components
        )
        self.assertIn("import_error_component", self.registry._registered_components)

        # Check details of a valid component
        valid_comp_info = self.registry._registered_components["valid_component"]
        self.assertEqual(
            valid_comp_info["path"], "tests.temp_components.dummy_component"
        )
        self.assertEqual(valid_comp_info["class_name"], "DummyComponent")
        self.assertEqual(valid_comp_info["dependencies"], ["dep1"])

    def test_get_registered_component_names(self):
        """
        Test that registered component names are returned correctly.
        """
        names = self.registry.get_registered_component_names()
        expected_names = [
            "valid_component",
            "non_subclass_component",
            "non_existent_class_component",
            "import_error_component",
        ]
        self.assertCountEqual(names, expected_names)

    @mock.patch("importlib.util.spec_from_file_location")
    def test_get_component_class_import_error(self, mock_spec_from_file_location):
        """
        Test get_component_class when importlib.util.spec_from_file_location returns None.
        """
        mock_spec_from_file_location.return_value = None
        with self.assertRaisesRegex(
            ValueError, "Could not load component 'import_error_component'"
        ):
            self.registry.get_component_class("import_error_component")

    def test_get_component_class_not_registered(self):
        """
        Test get_component_class with a component that is not registered.
        """
        with self.assertRaisesRegex(
            ValueError, "Component 'non_existent_component' is not registered."
        ):
            self.registry.get_component_class("non_existent_component")

    def test_get_component_class_non_existent_class(self):
        """
        Test get_component_class when the class_name does not exist in the module.
        """
        with self.assertRaisesRegex(
            ValueError, "Could not load component 'non_existent_class_component'"
        ):
            self.registry.get_component_class("non_existent_class_component")

    def test_get_component_class_non_subclass(self):
        """
        Test get_component_class when the loaded class is not a subclass of Component.
        """
        with self.assertRaisesRegex(
            TypeError,
            "Class 'NonComponentClass' in 'tests.temp_components.non_component_class' is not a subclass of Component.",
        ):
            self.registry.get_component_class("non_subclass_component")

    def test_get_component_class_success(self):
        """
        Test successful loading of a component class and its dependencies.
        """
        component_class, dependencies = self.registry.get_component_class(
            "valid_component"
        )
        self.assertEqual(component_class.__name__, "DummyComponent")
        self.assertEqual(dependencies, ["dep1"])
        self.assertTrue(issubclass(component_class, Component))


if __name__ == "__main__":
    unittest.main()
