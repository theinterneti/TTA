"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Proxy]]
OpenHands agent proxy for TTA integration.

Provides:
- OpenHandsAgentProxy: TTA Agent proxy for OpenHands
- Agent registration and lifecycle management
- Message coordination for task delegation
- Real-time event integration
- Circuit breaker protection
- Capability advertisement
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import SecretStr

from ..agents import Agent
from ..interfaces import MessageCoordinator
from ..models import AgentId, AgentType
from .adapter import OpenHandsAdapter
from .client import OpenHandsClient
from .config import OpenHandsConfig, OpenHandsIntegrationConfig

logger = logging.getLogger(__name__)


class OpenHandsAgentProxy(Agent):
    """
    Agent proxy for OpenHands development sub-agent.

    Follows TTA's agent proxy pattern (similar to WorldBuilderAgentProxy).

    Provides:
    - Agent registration and lifecycle management
    - Message coordination for task delegation
    - Real-time event integration
    - Circuit breaker protection
    - Capability advertisement

    Example:
        proxy = OpenHandsAgentProxy(
            coordinator=message_coordinator,
            instance="dev-1",
            openhands_config=config,
            agent_registry=registry,
            event_publisher=publisher
        )
        await proxy.start()
    """

    def __init__(
        self,
        *,
        coordinator: MessageCoordinator | None = None,
        instance: str | None = None,
        default_timeout_s: float = 300.0,
        enable_real_agent: bool | None = None,
        fallback_to_mock: bool = False,
        openhands_config: OpenHandsIntegrationConfig | None = None,
        agent_registry: Any = None,
        event_publisher: Any = None,
        circuit_breaker: Any = None,
    ) -> None:
        """
        Initialize OpenHands agent proxy.

        Args:
            coordinator: Message coordinator for agent communication
            instance: Agent instance identifier
            default_timeout_s: Default timeout for operations (300s for dev tasks)
            enable_real_agent: Whether to use real OpenHands SDK (None = use config value)
            fallback_to_mock: Whether to fall back to mock responses
            openhands_config: OpenHands configuration (auto-loaded if None)
            agent_registry: Agent registry for registration
            event_publisher: Event publisher for real-time updates
            circuit_breaker: Circuit breaker for fault tolerance
        """
        super().__init__(
            agent_id=AgentId(type=AgentType.OPENHANDS, instance=instance),
            name=f"openhands:{instance or 'default'}",
            coordinator=coordinator,
            default_timeout_s=default_timeout_s,
        )

        # Configuration
        self.openhands_config = openhands_config or self._load_config()
        # Use config's enable_real_agent if not explicitly provided
        self.enable_real_agent = (
            enable_real_agent
            if enable_real_agent is not None
            else self.openhands_config.enable_real_agent
        )
        self.fallback_to_mock = fallback_to_mock

        # Real-time event integration
        try:
            from ..realtime.agent_event_integration import (  # noqa: PLC0415
                get_agent_event_integrator,
            )

            self.event_integrator = get_agent_event_integrator(
                agent_id=str(self.agent_id),
                event_publisher=event_publisher,
                enabled=event_publisher is not None,
            )
        except ImportError:
            logger.warning("Agent event integration not available, events disabled")
            self.event_integrator = None

        # Circuit breaker for fault tolerance
        self.circuit_breaker = circuit_breaker

        # Initialize adapter and client
        if self.enable_real_agent:
            from ..adapters import RetryConfig  # noqa: PLC0415

            # Create OpenHandsConfig from integration config
            client_config = OpenHandsConfig(
                api_key=self.openhands_config.api_key,
                model=self.openhands_config.get_model_config().model_id,
                base_url=self.openhands_config.base_url,
                workspace_path=self.openhands_config.workspace_root,
                timeout_seconds=self.openhands_config.default_timeout_seconds,
            )

            client = OpenHandsClient(client_config)
            retry_config = RetryConfig(
                max_retries=self.openhands_config.max_retries,
                base_delay=self.openhands_config.retry_base_delay,
            )
            self.adapter = OpenHandsAdapter(
                client=client,
                retry_config=retry_config,
                fallback_to_mock=fallback_to_mock,
            )
        else:
            self.adapter = None

        # Register with agent registry
        if agent_registry:
            try:
                agent_registry.register(self)
                logger.info(
                    f"Registered OpenHands proxy {self.name} with agent registry"
                )
            except Exception as e:
                logger.warning(f"Failed to register with agent registry: {e}")

    def _load_config(self) -> OpenHandsIntegrationConfig:
        """Load OpenHands configuration from environment."""
        try:
            return OpenHandsIntegrationConfig.from_env()
        except ValueError as e:
            logger.warning(
                f"Failed to load config from environment: {e}. Using defaults with test API key."
            )
            # Return config with test API key for testing
            return OpenHandsIntegrationConfig(
                api_key=SecretStr("test-api-key"),
                enable_real_agent=False,
                fallback_to_mock=True,
            )

    async def execute_development_task(
        self,
        task_description: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a development task via OpenHands.

        Args:
            task_description: Natural language task description
            context: Optional context (workspace, files, etc.)

        Returns:
            Task result dictionary
        """
        if not self.enable_real_agent or self.adapter is None:
            return self._mock_development_task(task_description)

        # Publish start event
        if self.event_integrator:
            try:
                await self.event_integrator.publish_agent_event(
                    event_type="task_started",
                    data={"task": task_description, "context": context},
                )
            except Exception as e:
                logger.warning(f"Failed to publish start event: {e}")

        try:
            # Execute with circuit breaker if available
            if self.circuit_breaker:
                result = await self.circuit_breaker.execute(
                    self.adapter.execute_development_task,
                    task_description=task_description,
                    context=context,
                )
            else:
                result = await self.adapter.execute_development_task(
                    task_description=task_description,
                    context=context,
                )

            # Publish completion event
            if self.event_integrator:
                try:
                    await self.event_integrator.publish_agent_event(
                        event_type="task_completed",
                        data={"task": task_description, "result": result},
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish completion event: {e}")

            return result

        except Exception as e:
            # Publish error event
            if self.event_integrator:
                try:
                    await self.event_integrator.publish_agent_event(
                        event_type="task_failed",
                        data={"task": task_description, "error": str(e)},
                    )
                except Exception as event_error:
                    logger.warning(f"Failed to publish error event: {event_error}")
            raise

    def _mock_development_task(self, task_description: str) -> dict[str, Any]:
        """Generate mock response for development task."""
        return {
            "success": True,
            "output": f"[MOCK] Development task completed: {task_description}",
            "error": None,
            "execution_time": 0.1,
            "metadata": {"mock": True},
        }

    async def get_capabilities(self) -> dict[str, Any]:
        """
        Advertise OpenHands capabilities for discovery.

        Returns:
            Capability dictionary
        """
        return {
            "agent_type": "OPENHANDS",
            "capabilities": [
                "code_generation",
                "code_debugging",
                "code_refactoring",
                "file_editing",
                "bash_execution",
                "web_browsing",
            ],
            "supported_languages": [
                "python",
                "javascript",
                "typescript",
                "java",
                "go",
                "rust",
            ],
            "max_context_tokens": self.openhands_config.get_model_config().context_tokens,
            "timeout_seconds": self._default_timeout_s,
        }
