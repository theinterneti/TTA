"""
App Component

This module provides a component for managing the TTA.prototype app.

Classes:
    AppComponent: Component for managing the TTA.prototype app

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components.app_component import AppComponent
    
    # Create a configuration object
    config = TTAConfig()
    
    # Create an App component
    app = AppComponent(config)
    
    # Start the App component
    app.start()
    
    # Stop the App component
    app.stop()
    ```
"""

import os
import time
import logging
import subprocess
from src.common.process_utils import run as safe_run
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from src.orchestration.component import Component, ComponentStatus
from src.orchestration.decorators import log_entry_exit, timing_decorator, retry, require_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppComponent(Component):
    """
    Component for managing the TTA.prototype app.
    
    This component manages the main application for the tta.prototype repository.
    It uses Docker Compose to start and stop the app container.
    
    Attributes:
        root_dir: Root directory of the project
        repo_dir: Directory of the repository
        port: Port that the app is running on
    """
    
    def __init__(self, config: Any):
        """
        Initialize the App component.
        
        Args:
            config: Configuration object
        """
        super().__init__(config, name="tta.prototype_app", dependencies=["tta.prototype_neo4j"])
        
        self.root_dir = Path(__file__).parent.parent.parent
        self.repo_dir = self.root_dir / "tta.prototype"
        
        # Get App configuration
        self.port = self.config.get("tta.prototype.components.app.port", 8501)
        
        logger.info(f"Initialized App component on port {self.port}")
    
    @log_entry_exit
    @timing_decorator
    @require_config([
        "tta.prototype.components.app.port"
    ])
    def _start_impl(self) -> bool:
        """
        Start the App component.
        
        This method starts the app using Docker Compose.
        
        Returns:
            bool: True if the component was started successfully, False otherwise
        """
        # Check if App is already running
        if self._is_app_running():
            logger.info(f"App is already running on port {self.port}")
            return True
        
        # Start App using Docker Compose
        try:
            logger.info("Starting App using Docker Compose")
            
            # Run docker-compose up -d app
            result = self._run_docker_compose(["up", "-d", "app"])
            
            if result.returncode != 0:
                logger.error(f"Failed to start App: {result.stderr}")
                return False
            
            # Wait for App to start
            logger.info("Waiting for App to start...")
            for _ in range(30):  # Wait up to 30 seconds
                if self._is_app_running():
                    logger.info(f"App started successfully on port {self.port}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for App to start on port {self.port}")
            return False
        
        except Exception as e:
            logger.error(f"Error starting App: {e}")
            return False
    
    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the App component.
        
        This method stops the app using Docker Compose.
        
        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        # Check if App is running
        if not self._is_app_running():
            logger.info(f"App is not running on port {self.port}")
            return True
        
        # Stop App using Docker Compose
        try:
            logger.info("Stopping App using Docker Compose")
            
            # Run docker-compose stop app
            result = self._run_docker_compose(["stop", "app"])
            
            if result.returncode != 0:
                logger.error(f"Failed to stop App: {result.stderr}")
                return False
            
            # Wait for App to stop
            logger.info("Waiting for App to stop...")
            for _ in range(10):  # Wait up to 10 seconds
                if not self._is_app_running():
                    logger.info(f"App stopped successfully on port {self.port}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for App to stop on port {self.port}")
            return False
        
        except Exception as e:
            logger.error(f"Error stopping App: {e}")
            return False
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError)
    def _run_docker_compose(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Run a Docker Compose command.
        
        Args:
            command: Docker Compose command to run
            
        Returns:
            subprocess.CompletedProcess: CompletedProcess instance with the command's output
            
        Raises:
            subprocess.SubprocessError: If the Docker Compose command fails
        """
        full_command = ["docker-compose", "-f", str(self.repo_dir / "docker-compose.yml")] + command
        logger.info(f"Running Docker Compose command: {' '.join(full_command)}")
        
        result = safe_run(
            full_command,
            cwd=str(self.repo_dir),
            text=True,
            timeout=180,
            capture_output=True,
            check=False,
        )
        
        return result
    
    def _is_app_running(self) -> bool:
        """
        Check if App is running.
        
        Returns:
            bool: True if App is running, False otherwise
        """
        try:
            # Check if the App port is open
            result = safe_run(
                ["docker", "ps", "--filter", f"publish={self.port}", "--format", "{{.Names}}"],
                text=True,
                timeout=60,
                capture_output=True,
                check=False,
            )
            
            return bool(result.stdout.strip())
        
        except Exception as e:
            logger.error(f"Error checking if App is running: {e}")
            return False
