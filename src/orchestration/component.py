"""
TTA Component

This module provides the base class for TTA components.

Classes:
    ComponentStatus: Enum representing the status of a component
    Component: Base class for TTA components

Example:
    ```python
    from src.orchestration.component import Component, ComponentStatus

    class MyComponent(Component):
        def __init__(self, config):
            super().__init__(config, name="my_component", dependencies=["neo4j"])

        def _start_impl(self) -> bool:
            # Implement component-specific start logic
            return True

        def _stop_impl(self) -> bool:
            # Implement component-specific stop logic
            return True
    ```
"""

import logging
import subprocess
from enum import Enum
from typing import Any

from .decorators import log_entry_exit, timing_decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status of a component.

    Attributes:
        STOPPED: Component is stopped
        STARTING: Component is in the process of starting
        RUNNING: Component is running
        STOPPING: Component is in the process of stopping
        ERROR: Component encountered an error
    """

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class Component:
    """
    Base class for TTA components.

    This class defines the interface for components that can be managed
    by the TTA Orchestrator.

    Attributes:
        config: Configuration object
        name: Name of the component
        dependencies: List of component names that this component depends on
        status: Current status of the component
        process: Process object if the component is running as a subprocess
    """

    def __init__(
        self,
        config: Any,
        name: str | None = None,
        dependencies: list[str] | None = None,
    ):
        """
        Initialize a component.

        Args:
            config: Configuration object
            name: Name of the component. If None, uses the class name.
            dependencies: List of component names that this component depends on
        """
        self.config = config
        self.name = name or self.__class__.__name__
        self.dependencies = dependencies or []
        self.status = ComponentStatus.STOPPED
        self.process: subprocess.Popen | None = None

    @log_entry_exit
    @timing_decorator
    def start(self) -> bool:
        """
        Start the component.

        This method handles the component lifecycle and delegates to _start_impl
        for component-specific start logic.

        Returns:
            bool: True if the component was started successfully, False otherwise

        Raises:
            Exception: If an error occurs during startup
        """
        if self.status == ComponentStatus.RUNNING:
            logger.info(f"Component {self.name} is already running")
            return True

        logger.info(f"Starting component {self.name}")
        self.status = ComponentStatus.STARTING

        try:
            # Implement component-specific start logic in subclasses
            success = self._start_impl()

            if success:
                self.status = ComponentStatus.RUNNING
                logger.info(f"Component {self.name} started successfully")
            else:
                # Allow subclass to signal a graceful STOPPED state on failure
                if self.status not in (
                    ComponentStatus.STOPPED,
                    ComponentStatus.RUNNING,
                ):
                    self.status = ComponentStatus.ERROR
                logger.error(f"Failed to start component {self.name}")

            return success
        except Exception as e:
            # Allow subclass to pre-set STOPPED; otherwise mark as ERROR
            if self.status not in (ComponentStatus.STOPPED, ComponentStatus.RUNNING):
                self.status = ComponentStatus.ERROR
            logger.error(f"Error starting component {self.name}: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def stop(self) -> bool:
        """
        Stop the component.

        This method handles the component lifecycle and delegates to _stop_impl
        for component-specific stop logic.

        Returns:
            bool: True if the component was stopped successfully, False otherwise

        Raises:
            Exception: If an error occurs during shutdown
        """
        if self.status == ComponentStatus.STOPPED:
            logger.info(f"Component {self.name} is already stopped")
            return True

        logger.info(f"Stopping component {self.name}")
        self.status = ComponentStatus.STOPPING

        try:
            # Implement component-specific stop logic in subclasses
            success = self._stop_impl()

            if success:
                self.status = ComponentStatus.STOPPED
                logger.info(f"Component {self.name} stopped successfully")
            else:
                self.status = ComponentStatus.ERROR
                logger.error(f"Failed to stop component {self.name}")

            return success
        except Exception as e:
            self.status = ComponentStatus.ERROR
            logger.error(f"Error stopping component {self.name}: {e}")
            return False

    @log_entry_exit
    def restart(self) -> bool:
        """
        Restart the component.

        This method stops the component if it's running and then starts it again.

        Returns:
            bool: True if the component was restarted successfully, False otherwise
        """
        logger.info(f"Restarting component {self.name}")

        # Stop the component if it's running
        if self.status in [ComponentStatus.RUNNING, ComponentStatus.STARTING]:
            if not self.stop():
                logger.error(f"Failed to stop component {self.name} during restart")
                return False

        # Start the component
        return self.start()

    def _start_impl(self) -> bool:
        """
        Implementation of component-specific start logic.

        This method should be overridden by subclasses.

        Returns:
            bool: True if the component was started successfully, False otherwise

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        raise NotImplementedError("Subclasses must implement _start_impl")

    def _stop_impl(self) -> bool:
        """
        Implementation of component-specific stop logic.

        This method should be overridden by subclasses.

        Returns:
            bool: True if the component was stopped successfully, False otherwise

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        raise NotImplementedError("Subclasses must implement _stop_impl")

    def get_status(self) -> ComponentStatus:
        """
        Get the current status of the component.

        Returns:
            ComponentStatus: Current status of the component
        """
        return self.status

    def get_config(self) -> dict[str, Any]:
        """
        Get the configuration for this component.

        Returns:
            Dict[str, Any]: Component configuration dictionary
        """
        # Get the repository-specific configuration
        repo = "tta.dev" if "tta.dev" in self.name.lower() else "tta.prototype"
        component_name = self.name.lower().replace(f"{repo}_", "")

        # Get the component configuration
        return self.config.get(f"{repo}.components.{component_name}", {})
