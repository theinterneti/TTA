"""
TTA Component

This module provides the base class for TTA components.
"""

import logging
import subprocess
from enum import Enum
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status of a component."""
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
    """
    
    def __init__(self, config, name: str = None, dependencies: List[str] = None):
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
        self.process: Optional[subprocess.Popen] = None
    
    def start(self) -> bool:
        """
        Start the component.
        
        Returns:
            True if the component was started successfully, False otherwise
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
                self.status = ComponentStatus.ERROR
                logger.error(f"Failed to start component {self.name}")
            
            return success
        except Exception as e:
            self.status = ComponentStatus.ERROR
            logger.error(f"Error starting component {self.name}: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the component.
        
        Returns:
            True if the component was stopped successfully, False otherwise
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
    
    def restart(self) -> bool:
        """
        Restart the component.
        
        Returns:
            True if the component was restarted successfully, False otherwise
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
            True if the component was started successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement _start_impl")
    
    def _stop_impl(self) -> bool:
        """
        Implementation of component-specific stop logic.
        
        This method should be overridden by subclasses.
        
        Returns:
            True if the component was stopped successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement _stop_impl")
    
    def get_status(self) -> ComponentStatus:
        """
        Get the current status of the component.
        
        Returns:
            Current status of the component
        """
        return self.status
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration for this component.
        
        Returns:
            Component configuration
        """
        # Get the repository-specific configuration
        repo = "tta.dev" if "tta.dev" in self.name.lower() else "tta.prototype"
        component_name = self.name.lower().replace(f"{repo}_", "")
        
        # Get the component configuration
        return self.config.get(f"{repo}.components.{component_name}", {})
