"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Adapter]]
OpenHands adapter for TTA communication.

Provides:
- OpenHandsAdapter: Bridge between TTA orchestration and OpenHands client
- Retry logic with exponential backoff
- Error classification and handling
- Fallback to mock responses
- Integration with TTA's error recovery system
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from ..adapters import AgentCommunicationError, RetryConfig
from .client import OpenHandsClient

logger = logging.getLogger(__name__)


async def _retry_with_backoff(
    func: Any, retry_config: RetryConfig, *args: Any, **kwargs: Any
) -> Any:
    """Execute a function with exponential backoff retry logic (local to openhands)."""
    last_exception: BaseException | None = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt == retry_config.max_retries:
                break
            delay = min(
                retry_config.base_delay * (retry_config.exponential_base**attempt),
                retry_config.max_delay,
            )
            if retry_config.jitter:
                delay *= 0.5 + random.random() * 0.5
            logger.warning(
                "Attempt %d failed: %s. Retrying in %.2fs...", attempt + 1, e, delay
            )
            await asyncio.sleep(delay)

    raise AgentCommunicationError(
        f"All {retry_config.max_retries + 1} attempts failed. Last error: {last_exception}"
    )


class OpenHandsAdapter:
    """
    Adapter for OpenHands SDK communication following TTA patterns.

    Provides:
    - Retry logic with exponential backoff
    - Error classification and handling
    - Fallback to mock responses (optional)
    - Integration with TTA's error recovery system

    Example:
        adapter = OpenHandsAdapter(
            client=openhands_client,
            retry_config=RetryConfig(max_retries=3),
            fallback_to_mock=True
        )
        result = await adapter.execute_development_task("Fix bug in auth.py")
    """

    def __init__(
        self,
        client: OpenHandsClient,
        retry_config: RetryConfig | None = None,
        fallback_to_mock: bool = False,
    ) -> None:
        """
        Initialize OpenHands adapter.

        Args:
            client: OpenHandsClient instance
            retry_config: Retry configuration (defaults to 3 retries)
            fallback_to_mock: Whether to fall back to mock responses on failure
        """
        self.client = client
        self.retry_config = retry_config or RetryConfig(max_retries=3, base_delay=1.0)
        self.fallback_to_mock = fallback_to_mock

        logger.info(
            f"Initialized OpenHandsAdapter with retry_config={self.retry_config}, "
            f"fallback_to_mock={fallback_to_mock}"
        )

    async def execute_development_task(
        self,
        task_description: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a development task with retry logic.

        Args:
            task_description: Natural language task description
            context: Optional context (workspace path, files, etc.)

        Returns:
            Task result dictionary

        Raises:
            AgentCommunicationError: If all retries fail and no fallback
        """
        context = context or {}

        try:
            # Execute with retry
            result = await _retry_with_backoff(
                self.client.execute_task,
                self.retry_config,
                task_description=task_description,
                workspace_path=context.get("workspace_path"),
                timeout=context.get("timeout"),
            )

            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "metadata": result.metadata,
            }

        except Exception as e:
            logger.error(f"OpenHands adapter execution failed: {e}")

            if self.fallback_to_mock:
                return self._mock_response(task_description)

            raise AgentCommunicationError(f"OpenHands execution failed: {e}") from e

    def _mock_response(self, task_description: str) -> dict[str, Any]:
        """Generate mock response for fallback."""
        return {
            "success": True,
            "output": f"[MOCK] Task '{task_description}' completed",
            "error": None,
            "execution_time": 0.1,
            "metadata": {"mock": True},
        }
