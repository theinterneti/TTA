"""
Neo4j Component

This module provides a component for managing Neo4j.
"""

import os
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional

from src.orchestration.component import Component, ComponentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jComponent(Component):
    """
    Component for managing Neo4j.
    """
    
    def __init__(self, config, repository: str = "tta.dev"):
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
    
    def _start_impl(self) -> bool:
        """
        Start the Neo4j component.
        
        Returns:
            True if the component was started successfully, False otherwise
        """
        # Check if Neo4j is already running
        if self._is_neo4j_running():
            logger.info(f"Neo4j is already running on port {self.port}")
            return True
        
        # Start Neo4j using Docker Compose
        try:
            logger.info(f"Starting Neo4j using Docker Compose in {self.repository}")
            
            # Run docker-compose up -d neo4j
            result = subprocess.run(
                ["docker-compose", "up", "-d", "neo4j"],
                cwd=str(self.repo_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
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
    
    def _stop_impl(self) -> bool:
        """
        Stop the Neo4j component.
        
        Returns:
            True if the component was stopped successfully, False otherwise
        """
        # Check if Neo4j is running
        if not self._is_neo4j_running():
            logger.info(f"Neo4j is not running on port {self.port}")
            return True
        
        # Stop Neo4j using Docker Compose
        try:
            logger.info(f"Stopping Neo4j using Docker Compose in {self.repository}")
            
            # Run docker-compose stop neo4j
            result = subprocess.run(
                ["docker-compose", "stop", "neo4j"],
                cwd=str(self.repo_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
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
    
    def _is_neo4j_running(self) -> bool:
        """
        Check if Neo4j is running.
        
        Returns:
            True if Neo4j is running, False otherwise
        """
        try:
            # Check if the Neo4j port is open
            result = subprocess.run(
                ["docker", "ps", "--filter", f"publish={self.port}", "--format", "{{.Names}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            return bool(result.stdout.strip())
        
        except Exception as e:
            logger.error(f"Error checking if Neo4j is running: {e}")
            return False
