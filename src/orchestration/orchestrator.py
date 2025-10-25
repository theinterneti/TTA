"""TTA Orchestrator.

This module provides the main orchestration capabilities for the TTA project,
coordinating both tta.dev and tta.prototype components.

Classes:
    TTAOrchestrator: Main orchestrator for the TTA project

Example:
    ```python
    from src.orchestration import TTAOrchestrator

    # Create the orchestrator
    orchestrator = TTAOrchestrator()

    # Start all components
    orchestrator.start_all()

    # Start a specific component
    orchestrator.start_component("neo4j")

    # Stop all components
    orchestrator.stop_all()
    ```
"""

import logging
import subprocess
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.common.process_utils import run as safe_run

from .component import Component, ComponentStatus
from .component_registry import ComponentRegistry
from .config import TTAConfig
from .decorators import log_entry_exit, retry, timing_decorator, validate_args

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure rich console
console = Console()


class TTAOrchestrator:
    """
    Main orchestrator for the TTA project.

    This class coordinates the components from both tta.dev and tta.prototype,
    providing a unified interface for starting, stopping, and managing them.

    Attributes:
        config: Configuration object
        components: Dictionary of components
        root_dir: Root directory of the project
        component_registry: Registry for TTA components
    """

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize the TTA Orchestrator.

        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        self.config = TTAConfig(config_path)
        self.components: dict[str, Component] = {}
        self.root_dir = Path(__file__).parent.parent.parent

        # Initialize component registry
        self.component_registry = ComponentRegistry(self.config, self.root_dir)

        # Import components
        self._import_components()

        logger.info(
            f"TTAOrchestrator initialized with {len(self.components)} components"
        )

    @log_entry_exit
    @timing_decorator
    def _import_components(self) -> None:
        """
        Import core components.

        This method imports core components that are not repository-specific.
        """
        # Import core components (like player experience)

        for component_name in self.component_registry.get_registered_component_names():
            try:
                component_class, dependencies = (
                    self.component_registry.get_component_class(component_name)
                )
                comp = component_class(
                    component_name, self.config, dependencies=dependencies
                )  # Pass dependencies here
                self.components[comp.name] = comp
                logger.info(f"Imported component {comp.name}")
            except Exception as e:
                logger.error(f"Failed to import component {component_name}: {e}")

        logger.info(f"Imported {len(self.components)} components")

    def has_component(self, name: str) -> bool:
        """Return True if a component with the given name is registered."""
        return name in self.components

    @log_entry_exit
    @validate_args
    def start_component(self, component_name: str) -> bool:
        """
        Start a specific component.

        Args:
            component_name: Name of the component to start

        Returns:
            bool: True if the component was started successfully, False otherwise
        """
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return False

        component = self.components[component_name]

        # Check dependencies
        for dependency in component.dependencies:
            if dependency not in self.components:
                logger.warning(
                    f"Dependency {dependency} not found for {component_name} - skipping dependency start in test environment"
                )
                continue

            # Start dependency if not already running
            if self.components[
                dependency
            ].status != ComponentStatus.RUNNING and not self.start_component(
                dependency
            ):
                logger.error(
                    f"Failed to start dependency {dependency} for {component_name}"
                )
                return False

        # Start the component
        try:
            success = component.start()
            if success:
                logger.info(f"Started component {component_name}")
            else:
                logger.error(f"Failed to start component {component_name}")
            return success
        except Exception as e:
            logger.error(f"Error starting component {component_name}: {e}")
            return False

    @log_entry_exit
    @validate_args
    def stop_component(self, component_name: str) -> bool:
        """
        Stop a specific component.

        Args:
            component_name: Name of the component to stop

        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return False

        component = self.components[component_name]

        # Check for dependent components
        dependent_components = []
        for name, other_component in self.components.items():
            if component_name in other_component.dependencies:
                dependent_components.append(name)

        # Stop dependent components first
        for dependent in dependent_components:
            if self.components[
                dependent
            ].status == ComponentStatus.RUNNING and not self.stop_component(dependent):
                logger.error(
                    f"Failed to stop dependent component {dependent} for {component_name}"
                )
                return False

        # Stop the component
        try:
            success = component.stop()
            if success:
                logger.info(f"Stopped component {component_name}")
            else:
                logger.error(f"Failed to stop component {component_name}")
            return success
        except Exception as e:
            logger.error(f"Error stopping component {component_name}: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def start_all(self) -> bool:
        """
        Start all components.

        Returns:
            bool: True if all components were started successfully, False otherwise
        """
        success = True

        # Start components in dependency order
        # First, build a dependency graph
        dependency_graph = {}
        for name, component in self.components.items():
            dependency_graph[name] = component.dependencies

        # Then, determine the order to start components
        start_order = self._topological_sort(dependency_graph)

        # Start components in the determined order
        for component_name in start_order:
            if not self.start_component(component_name):
                success = False

        return success

    @log_entry_exit
    @timing_decorator
    def stop_all(self) -> bool:
        """
        Stop all components.

        Returns:
            bool: True if all components were stopped successfully, False otherwise
        """
        success = True

        # Stop components in reverse dependency order
        # First, build a dependency graph
        dependency_graph = {}
        for name, component in self.components.items():
            dependency_graph[name] = component.dependencies

        # Then, determine the order to stop components
        stop_order = self._topological_sort(dependency_graph)
        stop_order.reverse()  # Reverse to stop in the correct order

        # Stop components in the determined order
        for component_name in stop_order:
            if self.components[
                component_name
            ].status == ComponentStatus.RUNNING and not self.stop_component(
                component_name
            ):
                success = False

        return success

    def _topological_sort(self, graph: dict[str, list[str]]) -> list[str]:
        """
        Perform a topological sort of the dependency graph.

        Args:
            graph: Dependency graph where keys are component names and values are lists of dependencies

        Returns:
            List[str]: List of component names in topological order
        """
        visited: set[str] = set()
        temp: set[str] = set()
        order: list[str] = []

        def visit(node: str) -> None:
            """
            Visit a node in the dependency graph.

            Args:
                node: Name of the node to visit
            """
            if node in temp:
                # Circular dependency detected
                logger.warning(f"Circular dependency detected involving {node}")
                return
            if node in visited:
                return

            temp.add(node)
            for dependency in graph.get(node, []):
                visit(dependency)

            temp.remove(node)
            visited.add(node)
            order.append(node)

        for node in graph:
            if node not in visited:
                visit(node)

        return order

    @validate_args
    def get_component_status(self, component_name: str) -> ComponentStatus | None:
        """
        Get the status of a specific component.

        Args:
            component_name: Name of the component

        Returns:
            Optional[ComponentStatus]: Status of the component, or None if the component is not found
        """
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return None

        return self.components[component_name].status

    def get_all_statuses(self) -> dict[str, ComponentStatus]:
        """
        Get the status of all components.

        Returns:
            Dict[str, ComponentStatus]: Dictionary mapping component names to their statuses
        """
        return {name: component.status for name, component in self.components.items()}

    def display_status(self) -> None:
        """
        Display the status of all components in a table.

        This method uses the rich library to display a formatted table
        of component statuses.
        """
        table = Table(title="TTA Component Status")

        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Dependencies", style="yellow")

        for name, component in sorted(self.components.items()):
            status = component.status.value
            status_style = {
                "running": "green",
                "stopped": "red",
                "starting": "yellow",
                "stopping": "yellow",
                "error": "bold red",
            }.get(status, "white")

            dependencies = (
                ", ".join(component.dependencies) if component.dependencies else "None"
            )

            table.add_row(
                name, f"[{status_style}]{status}[/{status_style}]", dependencies
            )

        console.print(table)

    @log_entry_exit
    @retry(
        max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError
    )
    def run_docker_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """
        Run a Docker command.

        Args:
            command: Docker command to run

        Returns:
            subprocess.CompletedProcess: CompletedProcess instance with the command's output

        Raises:
            subprocess.SubprocessError: If the Docker command fails
        """
        full_command = ["docker"] + command
        logger.info(f"Running Docker command: {' '.join(full_command)}")

        result = safe_run(
            full_command,
            text=True,
            timeout=120,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            logger.error(f"Docker command failed: {result.stderr}")
            raise subprocess.SubprocessError(f"Docker command failed: {result.stderr}")

        return result

    @log_entry_exit
    @retry(
        max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError
    )
    def run_docker_compose_command(
        self, command: list[str], repository: str = "both"
    ) -> dict[str, subprocess.CompletedProcess]:
        """
        Run a Docker Compose command in one or both repositories.

        Args:
            command: Docker Compose command to run
            repository: Which repository to run the command in ("tta.dev", "tta.prototype", or "both")

        Returns:
            Dict[str, subprocess.CompletedProcess]: Dictionary mapping repository names to CompletedProcess instances

        Raises:
            subprocess.SubprocessError: If the Docker Compose command fails
        """
        results = {}

        if repository in ["tta.dev", "both"]:
            # Run in tta.dev
            tta_dev_path = self.root_dir / "ai-components" / "tta.dev"
            full_command = [
                "docker-compose",
                "-f",
                str(tta_dev_path / "docker-compose.yml"),
            ] + command
            logger.info(
                f"Running Docker Compose command in tta.dev: {' '.join(full_command)}"
            )

            result = safe_run(
                full_command,
                cwd=str(tta_dev_path),
                text=True,
                timeout=180,
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(
                    f"Docker Compose command failed in tta.dev: {result.stderr}"
                )
                raise subprocess.SubprocessError(
                    f"Docker Compose command failed in tta.dev: {result.stderr}"
                )

            results["tta.dev"] = result
        # Removed tta.prototype as it was not found and is being refactored out.
        # If tta.prototype functionality is needed, it should be registered as a component.

        return results
