"""
TTA Orchestrator

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
    orchestrator.start_component('neo4j')

    # Stop all components
    orchestrator.stop_all()
    ```
"""

import os
import sys
import logging
import importlib.util
import subprocess
from src.common.process_utils import run as safe_run
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set, Tuple, cast

from rich.console import Console
from rich.table import Table

from .config import TTAConfig
from .component import Component, ComponentStatus
from .decorators import log_entry_exit, timing_decorator, retry, validate_args

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
        tta_dev_path: Path to the tta.dev repository
        tta_prototype_path: Path to the tta.prototype repository
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the TTA Orchestrator.

        Args:
            config_path: Path to the configuration file. If None, uses default.

        Raises:
            FileNotFoundError: If a repository path does not exist.
        """
        self.config = TTAConfig(config_path)
        self.components: Dict[str, Component] = {}
        self.root_dir = Path(__file__).parent.parent.parent

        # Initialize paths to repositories
        self.tta_dev_path = self.root_dir / "tta.dev"
        self.tta_prototype_path = self.root_dir / "tta.prototype"

        # Validate repository paths
        self._validate_repositories()

        # Import components
        self._import_components()

        logger.info(f"TTAOrchestrator initialized with {len(self.components)} components")

    @log_entry_exit
    def _validate_repositories(self) -> None:
        """
        Validate that the repository paths exist and are properly structured.

        Raises:
            FileNotFoundError: If a repository path does not exist.
        """
        if not self.tta_dev_path.exists():
            raise FileNotFoundError(f"tta.dev repository not found at {self.tta_dev_path}")

        if not self.tta_prototype_path.exists():
            raise FileNotFoundError(f"tta.prototype repository not found at {self.tta_prototype_path}")

        logger.info(f"Found tta.dev at {self.tta_dev_path}")
        logger.info(f"Found tta.prototype at {self.tta_prototype_path}")

    @log_entry_exit
    @timing_decorator
    def _import_components(self) -> None:
        """
        Import components from both repositories.

        This method scans both repositories for component definitions and
        imports them into the orchestrator.
        """
        # Import tta.dev components (call unbound to be friendly to patch side_effect signatures)
        TTAOrchestrator._import_repository_components(self, self.tta_dev_path, "tta.dev")

        # Import tta.prototype components
        TTAOrchestrator._import_repository_components(self, self.tta_prototype_path, "tta.prototype")

        # Import core components (like player experience)
        TTAOrchestrator._import_core_components(self)

        logger.info(f"Imported {len(self.components)} components")

    def has_component(self, name: str) -> bool:
        """Return True if a component with the given name is registered."""
        return name in self.components

    def _import_repository_components(self, repo_path: Path, repo_name: str) -> None:
        """
        Import components from a repository.

        Args:
            repo_path: Path to the repository
            repo_name: Name of the repository
        """
        # Add repository to Python path if not already there
        if str(repo_path) not in sys.path:
            sys.path.append(str(repo_path))

        # Look for component definitions
        components_path = repo_path / "src" / "components"
        if not components_path.exists():
            logger.warning(f"No components directory found in {repo_name}; falling back to core components")
            self._register_core_components_for_repo(repo_name)
            return

        # Import each component
        pre_count = len(self.components)
        found_any = False
        for component_file in components_path.glob("*.py"):
            if component_file.name == "__init__.py":
                continue
            found_any = True
            try:
                # Import the module
                module_name = f"{repo_name}.components.{component_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, component_file)
                if spec is None or spec.loader is None:
                    logger.warning(f"Could not load {component_file}")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for Component subclasses
                imported_one = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, Component) and
                        attr is not Component):

                        # Create an instance of the component
                        component = attr(self.config)
                        self.components[component.name] = component
                        imported_one = True
                        logger.info(f"Imported component {component.name} from {repo_name}")
                if not imported_one:
                    logger.debug(f"No Component subclasses found in module {component_file.name}")

            except Exception as e:
                logger.error(f"Error importing {component_file}: {e}")

        # Fallback if no modules or no components were imported
        if not found_any or len(self.components) == pre_count:
            logger.warning(f"No components imported from {repo_name}; falling back to core components")
            self._register_core_components_for_repo(repo_name)

    def _register_core_components_for_repo(self, repo_name: str) -> None:
        """
        Register core components from src/components as a fallback when a repository's
        components directory is missing.
        """
        try:
            from src.components.neo4j_component import Neo4jComponent
        except Exception as e:
            Neo4jComponent = None  # type: ignore[assignment]
            logger.warning(f"Failed to import Neo4jComponent: {e}")
        try:
            from src.components.llm_component import LLMComponent
        except Exception as e:
            LLMComponent = None  # type: ignore[assignment]
            logger.warning(f"Failed to import LLMComponent: {e}")
        try:
            from src.components.app_component import AppComponent
        except Exception as e:
            AppComponent = None  # type: ignore[assignment]
            logger.warning(f"Failed to import AppComponent: {e}")
        try:
            from src.components.player_experience_component import PlayerExperienceComponent
        except Exception as e:
            PlayerExperienceComponent = None  # type: ignore[assignment]
            logger.warning(f"Failed to import PlayerExperienceComponent: {e}")

        # For tta.dev, register neo4j and llm if enabled
        if repo_name == "tta.dev":
            if Neo4jComponent and self.config.get("tta.dev.components.neo4j.enabled", False):
                comp = Neo4jComponent(self.config, repository="tta.dev")
                self.components[comp.name] = comp
                logger.info(f"Fallback-registered component {comp.name} from core")
            if LLMComponent and self.config.get("tta.dev.components.llm.enabled", False):
                comp = LLMComponent(self.config, repository="tta.dev")
                self.components[comp.name] = comp
                logger.info(f"Fallback-registered component {comp.name} from core")

        # For tta.prototype, register neo4j and app if enabled
        if repo_name == "tta.prototype":
            if Neo4jComponent and self.config.get("tta.prototype.components.neo4j.enabled", False):
                comp = Neo4jComponent(self.config, repository="tta.prototype")
                self.components[comp.name] = comp
                logger.info(f"Fallback-registered component {comp.name} from core")
            if AppComponent and self.config.get("tta.prototype.components.app.enabled", False):
                comp = AppComponent(self.config)
                self.components[comp.name] = comp
                logger.info(f"Fallback-registered component {comp.name} from core")

        # Register player experience component if enabled (independent of repository)
        if PlayerExperienceComponent and self.config.get("player_experience.enabled", False):
            comp = PlayerExperienceComponent(self.config)
            self.components[comp.name] = comp
            logger.info(f"Fallback-registered component {comp.name} from core")

    def _import_core_components(self) -> None:
        """
        Import core components that are not repository-specific.
        """
        # Import player experience component if enabled
        if self.config.get("player_experience.enabled", False):
            try:
                from src.components.player_experience_component import PlayerExperienceComponent
                comp = PlayerExperienceComponent(self.config)
                self.components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.error(f"Failed to import PlayerExperienceComponent: {e}")

        # Import agent orchestration component if enabled
        if self.config.get("agent_orchestration.enabled", False):
            try:
                from src.components.agent_orchestration_component import AgentOrchestrationComponent
                comp = AgentOrchestrationComponent(self.config)
                self.components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.error(f"Failed to import AgentOrchestrationComponent: {e}")

        # Import other core components (docker, carbon) if they exist and are enabled
        try:
            from src.components.docker_component import DockerComponent
            if self.config.get("docker.enabled", False):
                comp = DockerComponent(self.config)
                self.components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
        except Exception as e:
            logger.debug(f"DockerComponent not available: {e}")

        try:
            from src.components.carbon_component import CarbonComponent
            if self.config.get("carbon.enabled", False):
                comp = CarbonComponent(self.config)
                self.components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
        except Exception as e:
            logger.debug(f"CarbonComponent not available: {e}")


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
                logger.warning(f"Dependency {dependency} not found for {component_name} - skipping dependency start in test environment")
                continue

            # Start dependency if not already running
            if self.components[dependency].status != ComponentStatus.RUNNING:
                if not self.start_component(dependency):
                    logger.error(f"Failed to start dependency {dependency} for {component_name}")
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
            if self.components[dependent].status == ComponentStatus.RUNNING:
                if not self.stop_component(dependent):
                    logger.error(f"Failed to stop dependent component {dependent} for {component_name}")
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
            if self.components[component_name].status == ComponentStatus.RUNNING:
                if not self.stop_component(component_name):
                    success = False

        return success

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Perform a topological sort of the dependency graph.

        Args:
            graph: Dependency graph where keys are component names and values are lists of dependencies

        Returns:
            List[str]: List of component names in topological order
        """
        visited: Set[str] = set()
        temp: Set[str] = set()
        order: List[str] = []

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
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
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

    def get_all_statuses(self) -> Dict[str, ComponentStatus]:
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
        table.add_column("Repository", style="blue")
        table.add_column("Dependencies", style="yellow")

        for name, component in sorted(self.components.items()):
            repo = "tta.dev" if "tta.dev" in name.lower() else "tta.prototype"
            status = component.status.value
            status_style = {
                "running": "green",
                "stopped": "red",
                "starting": "yellow",
                "stopping": "yellow",
                "error": "bold red"
            }.get(status, "white")

            dependencies = ", ".join(component.dependencies) if component.dependencies else "None"

            table.add_row(
                name,
                f"[{status_style}]{status}[/{status_style}]",
                repo,
                dependencies
            )

        console.print(table)

    @log_entry_exit
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError)
    def run_docker_command(self, command: List[str]) -> subprocess.CompletedProcess:
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
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError)
    def run_docker_compose_command(self,
                                  command: List[str],
                                  repository: str = "both") -> Dict[str, subprocess.CompletedProcess]:
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
            full_command = ["docker-compose", "-f", str(self.tta_dev_path / "docker-compose.yml")] + command
            logger.info(f"Running Docker Compose command in tta.dev: {' '.join(full_command)}")

            result = safe_run(
                full_command,
                cwd=str(self.tta_dev_path),
                text=True,
                timeout=180,
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"Docker Compose command failed in tta.dev: {result.stderr}")
                raise subprocess.SubprocessError(f"Docker Compose command failed in tta.dev: {result.stderr}")

            results["tta.dev"] = result

        if repository in ["tta.prototype", "both"]:
            # Run in tta.prototype
            full_command = ["docker-compose", "-f", str(self.tta_prototype_path / "docker-compose.yml")] + command
            logger.info(f"Running Docker Compose command in tta.prototype: {' '.join(full_command)}")

            result = safe_run(
                full_command,
                cwd=str(self.tta_prototype_path),
                text=True,
                timeout=180,
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"Docker Compose command failed in tta.prototype: {result.stderr}")
                raise subprocess.SubprocessError(f"Docker Compose command failed in tta.prototype: {result.stderr}")

            results["tta.prototype"] = result

        return results
