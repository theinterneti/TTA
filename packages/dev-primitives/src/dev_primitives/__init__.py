"""Development primitives for error recovery, retry logic, and observability."""

from .recovery import (
    CircuitBreaker,
    ErrorCategory,
    ErrorSeverity,
    RetryConfig,
    calculate_delay,
    classify_error,
    should_retry,
    with_retry,
    with_retry_async,
)

__all__ = [
    "CircuitBreaker",
    "ErrorCategory",
    "ErrorSeverity",
    "RetryConfig",
    "calculate_delay",
    "classify_error",
    "should_retry",
    "with_retry",
    "with_retry_async",
]

__version__ = "0.1.0"
