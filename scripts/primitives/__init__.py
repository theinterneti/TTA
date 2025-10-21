"""
Agentic Primitives - Error Recovery

Reusable error recovery patterns for development operations.

Quick Start:
    from primitives import with_retry, RetryConfig, CircuitBreaker

    @with_retry()
    def flaky_operation():
        # Your code here
        pass

For more details, see scripts/primitives/README.md
"""

from .error_recovery import (
    # Circuit breaker
    CircuitBreaker,
    # Error classification
    ErrorCategory,
    ErrorSeverity,
    # Configuration
    RetryConfig,
    calculate_delay,
    classify_error,
    should_retry,
    # Core decorators
    with_retry,
    with_retry_async,
)

__all__ = [
    # Decorators
    "with_retry",
    "with_retry_async",

    # Configuration
    "RetryConfig",

    # Error classification
    "ErrorCategory",
    "ErrorSeverity",
    "classify_error",
    "should_retry",
    "calculate_delay",

    # Circuit breaker
    "CircuitBreaker",
]

__version__ = "1.0.0"

