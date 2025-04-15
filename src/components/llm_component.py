"""
LLM Component

This module provides a component for managing the LLM service.
"""

import os
import time
import logging
import subprocess
import requests
from pathlib import Path
from typing import Optional

from src.orchestration.component import Component, ComponentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMComponent(Component):
    """
    Component for managing the LLM service.
    """
    
    def __init__(self, config, repository: str = "tta.dev"):
        """
        Initialize the LLM component.
        
        Args:
            config: Configuration object
            repository: Repository that this component belongs to ("tta.dev" or "tta.prototype")
        """
        name = f"{repository}_llm"
        super().__init__(config, name=name, dependencies=[])
        
        self.repository = repository
        self.root_dir = Path(__file__).parent.parent.parent
        self.repo_dir = self.root_dir / repository
        
        # Get LLM configuration
        self.model = self.config.get(f"{repository}.components.llm.model", "qwen2.5-7b-instruct")
        self.api_base = self.config.get(f"{repository}.components.llm.api_base", "http://localhost:1234/v1")
        self.use_gpu = self.config.get("docker.use_gpu", False)
    
    def _start_impl(self) -> bool:
        """
        Start the LLM component.
        
        Returns:
            True if the component was started successfully, False otherwise
        """
        # Check if LLM service is already running
        if self._is_llm_running():
            logger.info(f"LLM service is already running at {self.api_base}")
            return True
        
        # Start LLM service using Docker Compose
        try:
            logger.info(f"Starting LLM service using Docker Compose in {self.repository}")
            
            # Set environment variables for the model
            env = os.environ.copy()
            env["MODEL"] = self.model
            
            # Add GPU profile if enabled
            profile_arg = ["--profile", "with-gpu"] if self.use_gpu else []
            
            # Run docker-compose up -d llm
            result = subprocess.run(
                ["docker-compose", "up", "-d", "llm"] + profile_arg,
                cwd=str(self.repo_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to start LLM service: {result.stderr}")
                return False
            
            # Wait for LLM service to start
            logger.info("Waiting for LLM service to start...")
            for _ in range(60):  # Wait up to 60 seconds
                if self._is_llm_running():
                    logger.info(f"LLM service started successfully at {self.api_base}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for LLM service to start at {self.api_base}")
            return False
        
        except Exception as e:
            logger.error(f"Error starting LLM service: {e}")
            return False
    
    def _stop_impl(self) -> bool:
        """
        Stop the LLM component.
        
        Returns:
            True if the component was stopped successfully, False otherwise
        """
        # Check if LLM service is running
        if not self._is_llm_running():
            logger.info(f"LLM service is not running at {self.api_base}")
            return True
        
        # Stop LLM service using Docker Compose
        try:
            logger.info(f"Stopping LLM service using Docker Compose in {self.repository}")
            
            # Run docker-compose stop llm
            result = subprocess.run(
                ["docker-compose", "stop", "llm"],
                cwd=str(self.repo_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to stop LLM service: {result.stderr}")
                return False
            
            # Wait for LLM service to stop
            logger.info("Waiting for LLM service to stop...")
            for _ in range(10):  # Wait up to 10 seconds
                if not self._is_llm_running():
                    logger.info(f"LLM service stopped successfully at {self.api_base}")
                    return True
                time.sleep(1)
            
            logger.error(f"Timed out waiting for LLM service to stop at {self.api_base}")
            return False
        
        except Exception as e:
            logger.error(f"Error stopping LLM service: {e}")
            return False
    
    def _is_llm_running(self) -> bool:
        """
        Check if LLM service is running.
        
        Returns:
            True if LLM service is running, False otherwise
        """
        try:
            # Check if the LLM service is responding
            response = requests.get(f"{self.api_base}/models", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
