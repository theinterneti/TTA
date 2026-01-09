"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Client]]
OpenHands SDK client wrapper.

Provides:
- OpenHandsClient: Low-level wrapper around OpenHands Python SDK
- DockerOpenHandsClient: Docker runtime client for full tool access
- create_openhands_client: Factory function for client selection
- LLM initialization with OpenRouter configuration
- Task execution with timeout handling
- Conversation management
- Result parsing and error handling
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Protocol

from .config import OpenHandsConfig, OpenHandsIntegrationConfig
from .models import OpenHandsTaskResult

logger = logging.getLogger(__name__)


class OpenHandsClientProtocol(Protocol):
    """Protocol for OpenHands clients (SDK and Docker)."""

    async def execute_task(
        self,
        task_description: str,
        workspace_path: Path | None = None,
        timeout: float | None = None,
    ) -> OpenHandsTaskResult:
        """Execute a development task."""
        ...

    async def cleanup(self) -> None:
        """Clean up client resources."""
        ...


class OpenHandsClient:
    """
    Low-level wrapper around OpenHands Python SDK.

    Provides:
    - SDK initialization with OpenRouter configuration
    - Task execution with timeout handling
    - Conversation management
    - Result parsing and error handling
    - Logging and metrics

    Example:
        config = OpenHandsConfig(
            api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
            model="deepseek/deepseek-v3:free"
        )
        client = OpenHandsClient(config)
        result = await client.execute_task("Write a Python function to calculate fibonacci")
    """

    def __init__(self, config: OpenHandsConfig) -> None:
        """
        Initialize OpenHands client with configuration.

        Args:
            config: OpenHands configuration
        """
        self.config = config
        self._llm: Any | None = None
        self._agent: Any | None = None
        self._conversation: Any | None = None

        logger.info(
            f"Initialized OpenHandsClient with model={config.model}, "
            f"workspace={config.workspace_path}"
        )

    def _initialize_sdk(self) -> None:
        """Initialize OpenHands SDK components (LLM, Agent)."""
        if self._llm is None:
            try:
                from openhands.sdk import LLM

                self._llm = LLM(
                    model=self.config.model,
                    api_key=self.config.api_key.get_secret_value(),  # Extract secret value
                    base_url=self.config.base_url,
                    # OpenRouter-specific fields (litellm detects OpenRouter from model prefix)
                    openrouter_site_url="https://github.com/theinterneti/TTA",
                    openrouter_app_name="TTA-OpenHands-Integration",
                    # Limit output tokens to avoid exceeding model limits
                    max_output_tokens=4096,
                    extended_thinking_budget=0,  # Disable extended thinking to reduce token usage
                )
                logger.debug(f"Initialized LLM with model={self.config.model}")
            except ImportError as e:
                logger.error(f"Failed to import OpenHands SDK: {e}")
                raise RuntimeError(
                    "OpenHands SDK not installed. Install with: pip install openhands-sdk"
                ) from e

        if self._agent is None:
            try:
                from openhands.sdk import Agent

                # Create agent with LLM
                self._agent = Agent(llm=self._llm)
                logger.debug("Initialized OpenHands agent")
            except ImportError as e:
                logger.error(f"Failed to import OpenHands Agent: {e}")
                raise RuntimeError(
                    "OpenHands Agent not available. Check SDK installation."
                ) from e

    async def execute_task(
        self,
        task_description: str,
        workspace_path: Path | None = None,
        timeout: float | None = None,
    ) -> OpenHandsTaskResult:
        """
        Execute a development task using OpenHands SDK.

        Args:
            task_description: Natural language task description
            workspace_path: Optional workspace override
            timeout: Optional timeout override (seconds)

        Returns:
            OpenHandsTaskResult with execution details

        Raises:
            TimeoutError: If task execution exceeds timeout
            RuntimeError: If SDK initialization or execution fails
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout_seconds
        workspace = workspace_path or self.config.workspace_path

        try:
            # Initialize SDK components
            self._initialize_sdk()

            # Create conversation
            try:
                from openhands.sdk import Conversation

                self._conversation = Conversation(
                    agent=self._agent,
                    workspace=str(workspace),
                )
            except ImportError as e:
                logger.error(f"Failed to import Conversation: {e}")
                raise RuntimeError(
                    "OpenHands Conversation not available. Check SDK installation."
                ) from e

            # Send task message and run
            logger.info(f"Executing task: {task_description[:100]}...")
            self._conversation.send_message(task_description)

            # Run the conversation (this executes the task)
            self._conversation.run()

            execution_time = time.time() - start_time

            # Extract output from conversation history
            # Get the last agent message as output
            output_lines = []
            if hasattr(self._conversation, "history"):
                for event in reversed(self._conversation.history):
                    if hasattr(event, "source") and event.source == "agent":
                        if hasattr(event, "message"):
                            output_lines.append(event.message)
                        elif hasattr(event, "content"):
                            output_lines.append(event.content)
                        if len(output_lines) >= 5:  # Get last 5 agent messages
                            break

            output = (
                "\n\n".join(reversed(output_lines))
                if output_lines
                else "Task completed (no output captured)"
            )

            logger.info(f"Task completed successfully in {execution_time:.2f}s")

            return OpenHandsTaskResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={"workspace": str(workspace)},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"OpenHands task execution failed: {e}")

            return OpenHandsTaskResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
            )

    async def cleanup(self) -> None:
        """Clean up SDK resources."""
        self._conversation = None
        self._agent = None
        self._llm = None
        logger.debug("Cleaned up OpenHands client resources")


def create_openhands_client(
    config: OpenHandsConfig | OpenHandsIntegrationConfig,
    use_docker: bool | None = None,
) -> OpenHandsClientProtocol:
    """
    Factory function to create appropriate OpenHands client.

    Args:
        config: OpenHands configuration (OpenHandsConfig or OpenHandsIntegrationConfig)
        use_docker: Override Docker runtime mode (None = use config value)

    Returns:
        OpenHandsClient (SDK mode) or DockerOpenHandsClient (Docker mode)

    Example:
        # SDK mode (default)
        client = create_openhands_client(config)

        # Docker mode (explicit)
        client = create_openhands_client(config, use_docker=True)

        # Docker mode (from config)
        integration_config = OpenHandsIntegrationConfig.from_env()
        integration_config.use_docker_runtime = True
        client = create_openhands_client(integration_config)
    """
    # Determine whether to use Docker runtime
    should_use_docker = False

    if use_docker is not None:
        # Explicit override
        should_use_docker = use_docker
    elif isinstance(config, OpenHandsIntegrationConfig):
        # Use config value
        should_use_docker = config.use_docker_runtime

    # Convert OpenHandsIntegrationConfig to OpenHandsConfig if needed
    if isinstance(config, OpenHandsIntegrationConfig):
        client_config = config.to_client_config()
        docker_image = config.docker_image
        docker_runtime_image = config.docker_runtime_image
    else:
        client_config = config
        docker_image = None
        docker_runtime_image = None

    # Create appropriate client
    if should_use_docker:
        from .docker_client import DockerOpenHandsClient

        logger.info("Creating DockerOpenHandsClient (full tool access)")
        return DockerOpenHandsClient(
            config=client_config,
            openhands_image=docker_image,
            runtime_image=docker_runtime_image,
        )
    logger.info("Creating OpenHandsClient (SDK mode)")
    return OpenHandsClient(config=client_config)
