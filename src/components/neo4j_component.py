"""
Neo4j Component

This module provides a component for managing Neo4j.

Classes:
    Neo4jComponent: Component for managing Neo4j

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components.neo4j_component import Neo4jComponent
    
    # Create a configuration object
    config = TTAConfig()
    
    # Create a Neo4j component
    neo4j = Neo4jComponent(config, repository="tta.dev")
    
    # Start the Neo4j component
    neo4j.start()
    
    # Stop the Neo4j component
    neo4j.stop()
    ```
"""

import os
import time
import logging
import subprocess
from src.common.process_utils import run as safe_run
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from src.orchestration.component import Component, ComponentStatus
from src.orchestration.decorators import log_entry_exit, timing_decorator, retry, require_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jComponent(Component):
    """
    Component for managing Neo4j.
    
    This component manages the Neo4j database for both tta.dev and tta.prototype
    repositories. It uses Docker Compose to start and stop the Neo4j container.
    
    Attributes:
        repository: Repository that this component belongs to
        root_dir: Root directory of the project
        repo_dir: Directory of the repository
        port: Port that Neo4j is running on
        username: Neo4j username
        password: Neo4j password
    """
    
    def __init__(self, config: Any, repository: str = "tta.dev"):
        """
        Initialize the Neo4j component.
        
        Args:
            config: Configuration object
            repository: Repository that this component belongs to ("tta.dev" or "tta.prototype")
        """
        name = f"{repository}_neo4j"
        super().__init__(config, name=name, dependencies=[])
        
        self.repository = repository
        self.root_dir = Path(__file__).parent.parent.parent
        self.repo_dir = self.root_dir / repository
        
        # Get Neo4j configuration
        self.port = self.config.get(f"{repository}.components.neo4j.port", 7687)
        self.username = self.config.get(f"{repository}.components.neo4j.username", "neo4j")
        self.password = self.config.get(f"{repository}.components.neo4j.password", "password")
        
        logger.info(f"Initialized Neo4j component for {repository} on port {self.port}")
    
    @log_entry_exit
    @timing_decorator
    @require_config([
        "tta.dev.components.neo4j.port",
        "tta.dev.components.neo4j.username",
        "tta.dev.components.neo4j.password"
    ])
    def _start_impl(self) -> bool:
        """
        Start the Neo4j component.
        
        This method starts the Neo4j database using Docker Compose.
        
        Returns:
            bool: True if the component was started successfully, False otherwise
        """
        # Check if Neo4j is already running
        if self._is_neo4j_running():
            logger.info(f"Neo4j is already running on port {self.port}")
            return True
        
        # Start Neo4j using Docker Compose
        try:
            logger.info(f"Starting Neo4j using Docker Compose in {self.repository}")
            
            # Run docker-compose up -d neo4j
            result = self._run_docker_compose(["up", "-d", "neo4j"])
            
            if result.returncode != 0:
                logger.error(f"Failed to start Neo4j: {result.stderr}")
                return False
            
            # Wait for Neo4j to start
            logger.info("Waiting for Neo4j to start...")
            for _ in range(30):  # Wait up to 30 seconds
                if self._is_neo4j_running():
                    logger.info(f"Neo4j started successfully on port {self.port}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for Neo4j to start on port {self.port}")
            return False
        
        except Exception as e:
            logger.error(f"Error starting Neo4j: {e}")
            return False
    
    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the Neo4j component.
        
        This method stops the Neo4j database using Docker Compose.
        
        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        # Check if Neo4j is running
        if not self._is_neo4j_running():
            logger.info(f"Neo4j is not running on port {self.port}")
            return True
        
        # Stop Neo4j using Docker Compose
        try:
            logger.info(f"Stopping Neo4j using Docker Compose in {self.repository}")
            
            # Run docker-compose stop neo4j
            result = self._run_docker_compose(["stop", "neo4j"])
            
            if result.returncode != 0:
                logger.error(f"Failed to stop Neo4j: {result.stderr}")
                return False
            
            # Wait for Neo4j to stop
            logger.info("Waiting for Neo4j to stop...")
            for _ in range(10):  # Wait up to 10 seconds
                if not self._is_neo4j_running():
                    logger.info(f"Neo4j stopped successfully on port {self.port}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for Neo4j to stop on port {self.port}")
            return False
        
        except Exception as e:
            logger.error(f"Error stopping Neo4j: {e}")
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
    
    def _is_neo4j_running(self) -> bool:
        """
        Check if Neo4j is running.
        
        Returns:
            bool: True if Neo4j is running, False otherwise
        """
        try:
            # Check if the Neo4j port is open
            result = safe_run(
                ["docker", "ps", "--filter", f"publish={self.port}", "--format", "{{.Names}}"],
                text=True,
                timeout=60,
                capture_output=True,
                check=False,
            )
            
            return bool(result.stdout.strip())
        
        except Exception as e:
            logger.error(f"Error checking if Neo4j is running: {e}")
            return False
