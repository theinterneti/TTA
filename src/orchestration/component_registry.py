"""Component Registry for TTA Orchestrator."""

# Logseq: [[TTA.dev/Orchestration/Component_registry]]

import importlib.util
import logging
import sys
from pathlib import Path

from src.orchestration.component import Component
from src.orchestration.config import TTAConfig

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """
    Manages the registration and loading of TTA components.

    This registry allows components to be dynamically discovered and instantiated
    based on configuration, decoupling the orchestrator from direct filesystem
    dependencies.
    """

    def __init__(self, config: TTAConfig, root_dir: Path):
        self.config = config
        self.root_dir = root_dir
        self._registered_components: dict[str, dict] = {}
        self._load_component_definitions()

    def _load_component_definitions(self):
        """Loads component definitions from the configuration."""
        # Example: Load from a 'components' section in tta_config.yaml
        # The config should define component_name: { path: "module.path", class_name: "ClassName" }
        component_configs = self.config.get("orchestration.components", {})
        for name, details in component_configs.items():
            if "path" not in details or "class_name" not in details:
                logger.warning(
                    f"Skipping malformed component definition for '{name}': {details}"
                )
                continue
            dependencies = details.get("dependencies", [])
            self._registered_components[name] = {
                "path": details["path"],
                "class_name": details["class_name"],
                "dependencies": dependencies,
            }
            logger.debug(f"Registered component '{name}' from config.")

    def get_component_class(
        self, component_name: str
    ) -> tuple[type[Component], list[str]]:
        """
        Dynamically loads and returns the class and dependencies for a registered component.

        Args:
            component_name: The name of the component to retrieve.

        Returns:
            A tuple containing the component class and its list of dependencies.

        Raises:
            ValueError: If the component is not registered or cannot be loaded.
        """
        component_info = self._registered_components.get(component_name)
        if not component_info:
            raise ValueError(f"Component '{component_name}' is not registered.")

        module_path = component_info["path"]
        class_name = component_info["class_name"]
        dependencies = component_info["dependencies"]

        try:
            # Convert module path to a filesystem path relative to root_dir
            # Assuming module_path is like "ai-components.tta_dev.src.my_component"
            # and needs to be converted to "ai-components/tta_dev/src/my_component.py"
            file_path_candidate = self.root_dir / Path(*module_path.split("."))

            if (file_path_candidate / "__init__.py").exists():  # It's a package
                file_path = file_path_candidate / "__init__.py"
            else:  # It's a module
                file_path = file_path_candidate.with_suffix(".py")

            spec = importlib.util.spec_from_file_location(module_path, file_path)
            if spec is None:
                raise ImportError(
                    f"Could not find spec for module {module_path} at {file_path}"
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_path] = module
            spec.loader.exec_module(module)  # type: ignore

            component_class = getattr(module, class_name)
            if not issubclass(component_class, Component):
                raise TypeError(
                    f"Class '{class_name}' in '{module_path}' is not a subclass of Component."
                )
            return component_class, dependencies
        except TypeError as e:  # Catch TypeError specifically
            logger.error(
                f"Failed to load component '{component_name}' from '{module_path}': {e}"
            )
            raise e  # Re-raise TypeError
        except Exception as e:
            logger.error(
                f"Failed to load component '{component_name}' from '{module_path}': {e}"
            )
            raise ValueError(f"Could not load component '{component_name}'.") from e

    def get_registered_component_names(self) -> list[str]:
        """Returns a list of all registered component names."""
        return list(self._registered_components.keys())
