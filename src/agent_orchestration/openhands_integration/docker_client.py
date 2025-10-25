"""
Docker runtime client for OpenHands integration.

Provides full OpenHands capabilities (bash, file operations, Jupyter) via Docker
headless mode, resolving the file creation limitation of the SDK wrapper.

Architecture:
- Executes OpenHands as Docker container with full runtime environment
- Mounts workspace directory for direct file access
- Parses container output to extract structured results
- Handles container lifecycle (automatic cleanup)

Example:
    config = OpenHandsConfig(
        api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
        model="openrouter/deepseek/deepseek-chat",
        workspace_path=Path("/path/to/workspace")
    )
    client = DockerOpenHandsClient(config)
    result = await client.execute_task("Create a file named test.txt")
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from .config import OpenHandsConfig
from .models import OpenHandsTaskResult

logger = logging.getLogger(__name__)


class DockerOpenHandsClient:
    """
    OpenHands client using Docker runtime for full tool access.

    Provides:
    - Full tool access (bash, file operations, Jupyter, browser)
    - Direct workspace mounting (no file copying)
    - Container lifecycle management (automatic cleanup)
    - Structured output parsing from container logs
    - Timeout and error handling

    Example:
        config = OpenHandsConfig(
            api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
            model="openrouter/deepseek/deepseek-chat"
        )
        client = DockerOpenHandsClient(config)
        result = await client.execute_task("Write a Python function")
    """

    # Default Docker images (OpenHands 0.54)
    DEFAULT_OPENHANDS_IMAGE = "docker.all-hands.dev/all-hands-ai/openhands:0.54"
    DEFAULT_RUNTIME_IMAGE = "docker.all-hands.dev/all-hands-ai/runtime:0.54-nikolaik"

    def __init__(
        self,
        config: OpenHandsConfig,
        openhands_image: str | None = None,
        runtime_image: str | None = None,
    ) -> None:
        """
        Initialize Docker OpenHands client.

        Args:
            config: OpenHands configuration
            openhands_image: OpenHands Docker image (default: 0.54)
            runtime_image: Sandbox runtime image (default: 0.54-nikolaik)
        """
        self.config = config
        self.openhands_image = openhands_image or self.DEFAULT_OPENHANDS_IMAGE
        self.runtime_image = runtime_image or self.DEFAULT_RUNTIME_IMAGE

        logger.info(
            f"Initialized DockerOpenHandsClient with model={config.model}, "
            f"workspace={config.workspace_path}, "
            f"image={self.openhands_image}"
        )

    def _build_docker_command(
        self,
        task_description: str,
        workspace_path: Path,
    ) -> list[str]:
        """
        Build Docker command for OpenHands headless mode.

        Args:
            task_description: Natural language task description
            workspace_path: Workspace directory to mount

        Returns:
            Docker command as list of strings
        """
        # Ensure workspace path is absolute
        workspace_abs = workspace_path.resolve()

        # Build Docker command
        cmd = [
            "docker",
            "run",
            "--rm",  # Automatic cleanup
            "-i",  # Interactive (for stdin)
            # Environment variables
            "-e",
            f"SANDBOX_RUNTIME_CONTAINER_IMAGE={self.runtime_image}",
            "-e",
            f"SANDBOX_VOLUMES={workspace_abs}:/workspace:rw",
            "-e",
            f"LLM_API_KEY={self.config.api_key.get_secret_value()}",
            "-e",
            f"LLM_MODEL={self.config.model}",
            "-e",
            f"LLM_BASE_URL={self.config.base_url}",
            "-e",
            "LOG_ALL_EVENTS=true",  # Enable JSON event logging
            # Volume mounts
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",  # Docker-in-Docker
            "-v",
            f"{Path.home()}/.openhands:/.openhands",  # OpenHands config
            # Networking
            "--add-host",
            "host.docker.internal:host-gateway",
            # Image and command
            self.openhands_image,
            "python",
            "-m",
            "openhands.core.main",
            "-t",
            task_description,
        ]

        return cmd

    def _parse_output(
        self, stdout: str, stderr: str, exit_code: int, execution_time: float
    ) -> OpenHandsTaskResult:
        """
        Parse Docker container output to extract structured results.

        Args:
            stdout: Container stdout
            stderr: Container stderr
            exit_code: Container exit code
            execution_time: Task execution time

        Returns:
            OpenHandsTaskResult with parsed data
        """
        success = exit_code == 0
        error = None if success else f"Docker exit code: {exit_code}"

        # Try to parse JSON events from stdout
        events = []
        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    continue

        # Extract metadata from events
        metadata: dict[str, Any] = {
            "docker_mode": True,
            "exit_code": exit_code,
            "events_count": len(events),
        }

        # Look for completion events
        for event in events:
            if event.get("event_type") == "task_complete":
                metadata["task_complete"] = True
                metadata["completion_data"] = event.get("data", {})

        # Include stderr if present
        if stderr:
            metadata["stderr"] = stderr

        return OpenHandsTaskResult(
            success=success,
            output=stdout,
            error=error,
            execution_time=execution_time,
            metadata=metadata,
        )

    async def execute_task(
        self,
        task_description: str,
        workspace_path: Path | None = None,
        timeout: float | None = None,
    ) -> OpenHandsTaskResult:
        """
        Execute a development task using OpenHands Docker runtime.

        Args:
            task_description: Natural language task description
            workspace_path: Optional workspace override
            timeout: Optional timeout override (seconds)

        Returns:
            OpenHandsTaskResult with execution details

        Raises:
            TimeoutError: If task execution exceeds timeout
            RuntimeError: If Docker execution fails
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout_seconds
        workspace = workspace_path or self.config.workspace_path

        # Ensure workspace exists
        workspace.mkdir(parents=True, exist_ok=True)

        # Build Docker command
        cmd = self._build_docker_command(task_description, workspace)

        logger.info(f"Executing OpenHands task via Docker: {task_description[:100]}...")
        logger.debug(f"Docker command: {' '.join(cmd)}")

        try:
            # Execute Docker container
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    result.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill container on timeout
                result.kill()
                await result.wait()
                raise TimeoutError(
                    f"Docker execution exceeded timeout of {timeout}s"
                )

            # Decode output
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            exit_code = result.returncode or 0

            execution_time = time.time() - start_time

            # Parse output
            task_result = self._parse_output(stdout, stderr, exit_code, execution_time)

            logger.info(
                f"Docker execution completed in {execution_time:.2f}s "
                f"(success={task_result.success})"
            )

            return task_result

        except FileNotFoundError as e:
            logger.error("Docker not found. Is Docker installed and in PATH?")
            raise RuntimeError(
                "Docker not available. Install Docker to use Docker runtime mode."
            ) from e
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Docker execution failed: {e}")
            raise RuntimeError(f"Docker execution failed: {e}") from e

    async def cleanup(self) -> None:
        """Clean up Docker client resources (no-op for Docker mode)."""
        # Docker containers are automatically cleaned up with --rm flag
        logger.debug("Docker client cleanup (no-op - containers auto-removed)")

