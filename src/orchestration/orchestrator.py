"""
TTA Orchestrator

This module provides the main orchestration capabilities for the TTA project,
coordinating both tta.dev and tta.prototype components.
"""

import os
import sys
import logging
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from .config import TTAConfig
from .component import Component, ComponentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTAOrchestrator:
    """
    Main orchestrator for the TTA project.
    
    This class coordinates the components from both tta.dev and tta.prototype,
    providing a unified interface for starting, stopping, and managing them.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the TTA Orchestrator.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
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
    
    def _import_components(self) -> None:
        """
        Import components from both repositories.
        """
        # Import tta.dev components
        self._import_repository_components(self.tta_dev_path, "tta.dev")
        
        # Import tta.prototype components
        self._import_repository_components(self.tta_prototype_path, "tta.prototype")
        
        logger.info(f"Imported {len(self.components)} components")
    
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
            logger.warning(f"No components directory found in {repo_name}")
            return
        
        # Import each component
        for component_file in components_path.glob("*.py"):
            if component_file.name == "__init__.py":
                continue
            
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
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Component) and 
                        attr is not Component):
                        
                        # Create an instance of the component
                        component = attr(self.config)
                        self.components[component.name] = component
                        logger.info(f"Imported component {component.name} from {repo_name}")
            
            except Exception as e:
                logger.error(f"Error importing {component_file}: {e}")
    
    def start_component(self, component_name: str) -> bool:
        """
        Start a specific component.
        
        Args:
            component_name: Name of the component to start
            
        Returns:
            True if the component was started successfully, False otherwise
        """
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return False
        
        component = self.components[component_name]
        
        # Check dependencies
        for dependency in component.dependencies:
            if dependency not in self.components:
                logger.error(f"Dependency {dependency} not found for {component_name}")
                return False
            
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
    
    def stop_component(self, component_name: str) -> bool:
        """
        Stop a specific component.
        
        Args:
            component_name: Name of the component to stop
            
        Returns:
            True if the component was stopped successfully, False otherwise
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
    
    def start_all(self) -> bool:
        """
        Start all components.
        
        Returns:
            True if all components were started successfully, False otherwise
        """
        success = True
        for component_name in self.components:
            if not self.start_component(component_name):
                success = False
        
        return success
    
    def stop_all(self) -> bool:
        """
        Stop all components.
        
        Returns:
            True if all components were stopped successfully, False otherwise
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
            List of component names in topological order
        """
        visited = set()
        temp = set()
        order = []
        
        def visit(node: str) -> None:
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
    
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
        """
        Get the status of a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Status of the component, or None if the component is not found
        """
        if component_name not in self.components:
            logger.error(f"Component {component_name} not found")
            return None
        
        return self.components[component_name].status
    
    def get_all_statuses(self) -> Dict[str, ComponentStatus]:
        """
        Get the status of all components.
        
        Returns:
            Dictionary mapping component names to their statuses
        """
        return {name: component.status for name, component in self.components.items()}
    
    def run_docker_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Run a Docker command.
        
        Args:
            command: Docker command to run
            
        Returns:
            CompletedProcess instance with the command's output
        """
        full_command = ["docker"] + command
        logger.info(f"Running Docker command: {' '.join(full_command)}")
        
        result = subprocess.run(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Docker command failed: {result.stderr}")
        
        return result
    
    def run_docker_compose_command(self, 
                                  command: List[str], 
                                  repository: str = "both") -> Dict[str, subprocess.CompletedProcess]:
        """
        Run a Docker Compose command in one or both repositories.
        
        Args:
            command: Docker Compose command to run
            repository: Which repository to run the command in ("tta.dev", "tta.prototype", or "both")
            
        Returns:
            Dictionary mapping repository names to CompletedProcess instances
        """
        results = {}
        
        if repository in ["tta.dev", "both"]:
            # Run in tta.dev
            full_command = ["docker-compose", "-f", str(self.tta_dev_path / "docker-compose.yml")] + command
            logger.info(f"Running Docker Compose command in tta.dev: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                cwd=str(self.tta_dev_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Docker Compose command failed in tta.dev: {result.stderr}")
            
            results["tta.dev"] = result
        
        if repository in ["tta.prototype", "both"]:
            # Run in tta.prototype
            full_command = ["docker-compose", "-f", str(self.tta_prototype_path / "docker-compose.yml")] + command
            logger.info(f"Running Docker Compose command in tta.prototype: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                cwd=str(self.tta_prototype_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Docker Compose command failed in tta.prototype: {result.stderr}")
            
            results["tta.prototype"] = result
        
        return results
