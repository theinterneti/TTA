"""
Pydantic models for OpenHands integration.

Provides:
- OpenHandsTaskResult: Task execution result
- OpenHandsErrorType: Error classification
- OpenHandsRecoveryStrategy: Recovery strategy enumeration
- RECOVERY_STRATEGIES: Error type to recovery strategy mapping
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OpenHandsTaskResult(BaseModel):
    """Result from OpenHands task execution."""

    success: bool = Field(description="Whether task completed successfully")
    output: str = Field(description="Task output/result")
    error: str | None = Field(default=None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (files created, actions taken, etc.)",
    )


class OpenHandsErrorType(str, Enum):
    """Classification of OpenHands errors for recovery strategy selection."""

    CONNECTION_ERROR = "connection_error"  # Network/API connectivity issues
    TIMEOUT_ERROR = "timeout_error"  # Task execution timeout
    AUTHENTICATION_ERROR = "authentication_error"  # Invalid API key
    RATE_LIMIT_ERROR = "rate_limit_error"  # OpenRouter rate limit
    VALIDATION_ERROR = "validation_error"  # Invalid task/configuration
    SDK_ERROR = "sdk_error"  # OpenHands SDK internal error
    UNKNOWN_ERROR = "unknown_error"  # Unclassified error


class OpenHandsRecoveryStrategy(str, Enum):
    """Recovery strategies for different error types."""

    RETRY = "retry"  # Retry with exponential backoff
    RETRY_WITH_BACKOFF = "retry_with_backoff"  # Retry with longer backoff
    FALLBACK_MODEL = "fallback_model"  # Try different free model
    FALLBACK_MOCK = "fallback_mock"  # Return mock response
    CIRCUIT_BREAK = "circuit_break"  # Open circuit breaker
    ESCALATE = "escalate"  # Escalate to human intervention


# Error type → Recovery strategies (in order of preference)
RECOVERY_STRATEGIES: dict[OpenHandsErrorType, list[OpenHandsRecoveryStrategy]] = {
    OpenHandsErrorType.CONNECTION_ERROR: [
        OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF,
        OpenHandsRecoveryStrategy.CIRCUIT_BREAK,
        OpenHandsRecoveryStrategy.FALLBACK_MOCK,
    ],
    OpenHandsErrorType.TIMEOUT_ERROR: [
        OpenHandsRecoveryStrategy.RETRY,
        OpenHandsRecoveryStrategy.FALLBACK_MOCK,
    ],
    OpenHandsErrorType.AUTHENTICATION_ERROR: [
        OpenHandsRecoveryStrategy.ESCALATE,  # Cannot auto-recover
    ],
    OpenHandsErrorType.RATE_LIMIT_ERROR: [
        OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF,
        OpenHandsRecoveryStrategy.FALLBACK_MODEL,
        OpenHandsRecoveryStrategy.CIRCUIT_BREAK,
    ],
    OpenHandsErrorType.VALIDATION_ERROR: [
        OpenHandsRecoveryStrategy.FALLBACK_MOCK,
        OpenHandsRecoveryStrategy.ESCALATE,
    ],
    OpenHandsErrorType.SDK_ERROR: [
        OpenHandsRecoveryStrategy.RETRY,
        OpenHandsRecoveryStrategy.CIRCUIT_BREAK,
        OpenHandsRecoveryStrategy.FALLBACK_MOCK,
    ],
    OpenHandsErrorType.UNKNOWN_ERROR: [
        OpenHandsRecoveryStrategy.RETRY,
        OpenHandsRecoveryStrategy.FALLBACK_MOCK,
    ],
}

