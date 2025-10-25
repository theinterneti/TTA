"""
Error recovery manager for OpenHands integration.

Provides:
- OpenHandsErrorRecovery: Comprehensive error handling
- Error classification
- Recovery strategy selection
- Retry with exponential backoff
- Circuit breaker integration
- Fallback mechanisms

Integration with TTA Patterns:
-----------------------------

1. **Retry Pattern Integration**
   - Uses scripts.primitives.error_recovery.RetryConfig for retry configuration
   - Integrates with_retry_async decorator for automatic retry with exponential backoff
   - Supports configurable max_retries, base_delay, max_delay, exponential_base, jitter
   - Falls back to basic retry if primitives not available

2. **Circuit Breaker Integration**
   - Accepts optional circuit_breaker instance (from packages/tta-ai-framework)
   - Executes operations through circuit breaker when available
   - Circuit breaker handles OPEN/CLOSED/HALF_OPEN states automatically
   - Prevents cascading failures by failing fast when circuit is OPEN

3. **Error Classification**
   - Classifies errors into OpenHandsErrorType (CONNECTION, TIMEOUT, AUTH, RATE_LIMIT, etc.)
   - Maps error types to recovery strategies (RECOVERY_STRATEGIES dict)
   - Supports error reporting through optional error_reporter service

4. **Recovery Strategies**
   - RETRY: Let retry decorator handle with exponential backoff
   - RETRY_WITH_BACKOFF: Increase backoff delay dynamically
   - CIRCUIT_BREAK: Let circuit breaker handle (fail fast when open)
   - FALLBACK_MOCK: Return mock response (when config.fallback_to_mock=True)
   - ESCALATE: Log error and re-raise for human intervention

Error Scenarios and Recovery:
------------------------------

1. **Missing API Key (AUTHENTICATION_ERROR)**
   - Classification: Detects "auth", "api key", "401" in error message
   - Recovery: ESCALATE (cannot auto-recover, requires human intervention)
   - Behavior: Logs error and re-raises immediately

2. **Timeout (TIMEOUT_ERROR)**
   - Classification: Detects "timeout" in error message or TimeoutError type
   - Recovery: RETRY → FALLBACK_MOCK
   - Behavior: Retries with exponential backoff, falls back to mock if enabled

3. **Validation Failure (VALIDATION_ERROR)**
   - Classification: Detects "validation" in error message or ValueError type
   - Recovery: FALLBACK_MOCK → ESCALATE
   - Behavior: Returns mock response if enabled, otherwise escalates

4. **Connection Error (CONNECTION_ERROR)**
   - Classification: Detects "connection" or "network" in error message
   - Recovery: RETRY_WITH_BACKOFF → CIRCUIT_BREAK → FALLBACK_MOCK
   - Behavior: Retries with increasing backoff, opens circuit breaker if persistent

5. **Rate Limit (RATE_LIMIT_ERROR)**
   - Classification: Detects "rate limit" or "429" in error message
   - Recovery: RETRY_WITH_BACKOFF → FALLBACK_MODEL → CIRCUIT_BREAK
   - Behavior: Retries with backoff, tries different model, opens circuit if needed

Usage Example:
--------------

```python
from src.agent_orchestration.openhands_integration.error_recovery import (
    OpenHandsErrorRecovery,
)
from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)

# Create recovery manager
config = OpenHandsIntegrationConfig.from_env()
recovery = OpenHandsErrorRecovery(config)


# Execute with automatic recovery
async def risky_operation():
    # Operation that might fail
    pass


result = await recovery.execute_with_recovery(risky_operation)
```
"""

from __future__ import annotations

import logging
from typing import Any

from .config import OpenHandsIntegrationConfig
from .models import (
    RECOVERY_STRATEGIES,
    OpenHandsErrorType,
    OpenHandsRecoveryStrategy,
)

logger = logging.getLogger(__name__)


class OpenHandsErrorRecovery:
    """
    Error recovery manager for OpenHands integration.

    Provides:
    - Error classification
    - Recovery strategy selection
    - Retry with exponential backoff
    - Circuit breaker integration
    - Fallback mechanisms
    - Error reporting
    """

    def __init__(
        self,
        config: OpenHandsIntegrationConfig,
        circuit_breaker: Any | None = None,
        error_reporter: Any | None = None,
    ) -> None:
        """
        Initialize error recovery manager.

        Args:
            config: OpenHands integration configuration
            circuit_breaker: Circuit breaker instance
            error_reporter: Error reporting service
        """
        self.config = config
        self.circuit_breaker = circuit_breaker
        self.error_reporter = error_reporter

        # Retry configuration
        try:
            from scripts.primitives.error_recovery import RetryConfig

            self.retry_config = RetryConfig(
                max_retries=config.max_retries,
                base_delay=config.retry_base_delay,
                max_delay=60.0,
                exponential_base=2.0,
                jitter=True,
            )
        except ImportError:
            # Fallback if primitives not available
            logger.warning(
                "scripts.primitives.error_recovery not available, using basic retry"
            )
            self.retry_config = None

    def classify_openhands_error(self, error: Exception) -> OpenHandsErrorType:
        """
        Classify error into OpenHands error type.

        Args:
            error: Exception to classify

        Returns:
            OpenHandsErrorType classification
        """
        error_str = str(error).lower()

        # Connection errors
        if "connection" in error_str or "network" in error_str:
            return OpenHandsErrorType.CONNECTION_ERROR

        # Timeout errors
        if "timeout" in error_str or isinstance(error, TimeoutError):
            return OpenHandsErrorType.TIMEOUT_ERROR

        # Authentication errors
        if "auth" in error_str or "api key" in error_str or "401" in error_str:
            return OpenHandsErrorType.AUTHENTICATION_ERROR

        # Rate limit errors
        if "rate limit" in error_str or "429" in error_str:
            return OpenHandsErrorType.RATE_LIMIT_ERROR

        # Validation errors
        if "validation" in error_str or isinstance(error, ValueError):
            return OpenHandsErrorType.VALIDATION_ERROR

        # SDK errors
        if "openhands" in error_str or "sdk" in error_str:
            return OpenHandsErrorType.SDK_ERROR

        return OpenHandsErrorType.UNKNOWN_ERROR

    async def execute_with_recovery(
        self,
        func: Any,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with comprehensive error recovery.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all recovery strategies fail
        """
        # Try with retry decorator if available
        if self.retry_config:
            try:
                from scripts.primitives.error_recovery import (
                    with_retry_async,
                )

                @with_retry_async(self.retry_config)
                async def execute_with_retry():
                    return await self._execute_with_circuit_breaker(
                        func, *args, **kwargs
                    )

                return await execute_with_retry()
            except ImportError:
                logger.warning(
                    "with_retry_async not available, executing without retry"
                )

        # Fallback: execute without retry
        return await self._execute_with_circuit_breaker(func, *args, **kwargs)

    async def _execute_with_circuit_breaker(self, func: Any, *args, **kwargs) -> Any:
        """Execute function with circuit breaker if available."""
        try:
            # Execute with circuit breaker if available
            if self.circuit_breaker:
                return await self.circuit_breaker.execute(func, *args, **kwargs)
            return await func(*args, **kwargs)

        except Exception as e:
            # Classify error
            error_type = self.classify_openhands_error(e)
            logger.error(f"OpenHands error: {error_type.value} - {e}")

            # Report error
            if self.error_reporter:
                try:
                    await self.error_reporter.report_error(
                        error_type=error_type.value,
                        error_message=str(e),
                        context={"function": func.__name__},
                    )
                except Exception as report_error:
                    logger.warning(f"Failed to report error: {report_error}")

            # Apply recovery strategy
            recovery_strategies = RECOVERY_STRATEGIES.get(
                error_type,
                [
                    OpenHandsRecoveryStrategy.RETRY,
                    OpenHandsRecoveryStrategy.FALLBACK_MOCK,
                ],
            )

            for strategy in recovery_strategies:
                if strategy == OpenHandsRecoveryStrategy.RETRY:
                    # Let retry decorator handle this
                    raise

                if strategy == OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF:
                    # Increase backoff delay
                    if self.retry_config:
                        self.retry_config.base_delay *= 2
                    raise

                if strategy == OpenHandsRecoveryStrategy.CIRCUIT_BREAK:
                    # Circuit breaker will handle this
                    raise

                if strategy == OpenHandsRecoveryStrategy.FALLBACK_MOCK:
                    if self.config.fallback_to_mock:
                        logger.warning("Falling back to mock response")
                        return self._generate_mock_response()
                    raise

                if strategy == OpenHandsRecoveryStrategy.ESCALATE:
                    logger.error(f"Escalating error: {error_type.value}")
                    raise

            # No recovery strategy succeeded
            raise

    def _generate_mock_response(self) -> dict[str, Any]:
        """Generate mock response for fallback."""
        return {
            "success": True,
            "output": "[MOCK] Task completed (fallback response)",
            "error": None,
            "execution_time": 0.1,
            "metadata": {"mock": True, "fallback": True},
        }
