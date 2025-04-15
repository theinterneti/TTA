"""
LLM Component

This module provides a component for managing the LLM service.

Classes:
    LLMComponent: Component for managing the LLM service

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components.llm_component import LLMComponent
    
    # Create a configuration object
    config = TTAConfig()
    
    # Create an LLM component
    llm = LLMComponent(config, repository="tta.dev")
    
    # Start the LLM component
    llm.start()
    
    # Stop the LLM component
    llm.stop()
    ```
"""

import os
import time
import logging
import subprocess
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from src.orchestration.component import Component, ComponentStatus
from src.orchestration.decorators import log_entry_exit, timing_decorator, retry, require_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMComponent(Component):
    """
    Component for managing the LLM service.
    
    This component manages the LLM service for the tta.dev repository.
    It uses Docker Compose to start and stop the LLM container.
    
    Attributes:
        repository: Repository that this component belongs to
        root_dir: Root directory of the project
        repo_dir: Directory of the repository
        model: Name of the LLM model to use
        api_base: Base URL for the LLM API
        use_gpu: Whether to use GPU acceleration
    """
    
    def __init__(self, config: Any, repository: str = "tta.dev"):
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
        
        logger.info(f"Initialized LLM component for {repository} with model {self.model}")
    
    @log_entry_exit
    @timing_decorator
    @require_config([
        "tta.dev.components.llm.model",
        "tta.dev.components.llm.api_base"
    ])
    def _start_impl(self) -> bool:
        """
        Start the LLM component.
        
        This method starts the LLM service using Docker Compose.
        
        Returns:
            bool: True if the component was started successfully, False otherwise
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
            result = self._run_docker_compose(["up", "-d", "llm"] + profile_arg, env=env)
            
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
    
    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the LLM component.
        
        This method stops the LLM service using Docker Compose.
        
        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        # Check if LLM service is running
        if not self._is_llm_running():
            logger.info(f"LLM service is not running at {self.api_base}")
            return True
        
        # Stop LLM service using Docker Compose
        try:
            logger.info(f"Stopping LLM service using Docker Compose in {self.repository}")
            
            # Run docker-compose stop llm
            result = self._run_docker_compose(["stop", "llm"])
            
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
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=subprocess.SubprocessError)
    def _run_docker_compose(self, command: List[str], env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Run a Docker Compose command.
        
        Args:
            command: Docker Compose command to run
            env: Environment variables to pass to the command
            
        Returns:
            subprocess.CompletedProcess: CompletedProcess instance with the command's output
            
        Raises:
            subprocess.SubprocessError: If the Docker Compose command fails
        """
        full_command = ["docker-compose", "-f", str(self.repo_dir / "docker-compose.yml")] + command
        logger.info(f"Running Docker Compose command: {' '.join(full_command)}")
        
        result = subprocess.run(
            full_command,
            cwd=str(self.repo_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env=env
        )
        
        return result
    
    def _is_llm_running(self) -> bool:
        """
        Check if LLM service is running.
        
        Returns:
            bool: True if LLM service is running, False otherwise
        """
        try:
            # Check if the LLM service is responding
            response = requests.get(f"{self.api_base}/models", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
