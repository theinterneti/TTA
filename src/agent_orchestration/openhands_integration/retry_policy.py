"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Retry_policy]]
Retry policy with exponential backoff for OpenHands integration.

Provides:
- RetryPolicy: Configurable retry with exponential backoff
- RetryConfig: Configuration for retry behavior
- Exponential backoff calculation
- Jitter support to prevent thundering herd

Usage:
------

```python
from src.agent_orchestration.openhands_integration.retry_policy import (
    RetryPolicy,
    RetryConfig,
)

# Create retry policy
config = RetryConfig(
    max_retries=5,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
)
retry_policy = RetryPolicy(config)


# Execute with retry
async def risky_operation():
    # Operation that might fail
    pass


result = await retry_policy.execute_with_retry(risky_operation)
```
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 5
    base_delay: float = 1.0  # Initial delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    exponential_base: float = 2.0  # Base for exponential backoff
    jitter: bool = True  # Add random jitter to prevent thundering herd

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = self.base_delay * (self.exponential_base**attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            # Add random jitter: ±20% of delay
            jitter_amount = delay * 0.2
            delay += random.uniform(-jitter_amount, jitter_amount)  # noqa: S311
            delay = max(0, delay)  # Ensure non-negative

        return delay


class RetryPolicy:
    """
    Retry policy with exponential backoff.

    Handles retries with configurable exponential backoff and jitter.
    """

    def __init__(self, config: RetryConfig | None = None) -> None:
        """
        Initialize retry policy.

        Args:
            config: Retry configuration (uses defaults if not provided)
        """
        self.config = config or RetryConfig()
        logger.info(
            f"RetryPolicy initialized: max_retries={self.config.max_retries}, "
            f"base_delay={self.config.base_delay}s, "
            f"exponential_base={self.config.exponential_base}"
        )

    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args,
        on_retry: Callable[[int, float, Exception], None] | None = None,
        **kwargs,
    ) -> Any:
        """
        Execute function with retry and exponential backoff.

        Args:
            func: Async function to execute
            *args: Function arguments
            on_retry: Optional callback on retry (attempt, delay, error)
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Success on retry attempt {attempt}")
                return result

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self.config.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, delay, e)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback error: {callback_error}")

                    # Wait before retry
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_retries + 1} attempts failed")

        # All retries failed
        raise last_error or RuntimeError("All retries failed")

    def execute_with_retry_sync(
        self,
        func: Callable[..., Any],
        *args,
        on_retry: Callable[[int, float, Exception], None] | None = None,
        **kwargs,
    ) -> Any:
        """
        Execute function with retry and exponential backoff (synchronous).

        Args:
            func: Sync function to execute
            *args: Function arguments
            on_retry: Optional callback on retry (attempt, delay, error)
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Success on retry attempt {attempt}")
                return result

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self.config.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, delay, e)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback error: {callback_error}")

                    # Wait before retry
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_retries + 1} attempts failed")

        # All retries failed
        raise last_error or RuntimeError("All retries failed")

    def get_config(self) -> RetryConfig:
        """Get current retry configuration."""
        return self.config

    def update_config(self, **kwargs) -> None:
        """Update retry configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated retry config: {key}={value}")
            else:
                logger.warning(f"Unknown retry config parameter: {key}")
