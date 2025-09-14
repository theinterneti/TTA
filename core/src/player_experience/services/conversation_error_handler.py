"""
Conversation Error Handler and Recovery System

This module provides comprehensive error handling and recovery mechanisms
for conversational character creation, including connection failures,
data corruption, and conversation state recovery.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..models.conversation_state import (
    ConversationState,
    ConversationStatus,
)
from ..services.conversational_character_service import ConversationalCharacterService

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can occur during conversation."""

    CONNECTION_ERROR = "connection_error"
    VALIDATION_ERROR = "validation_error"
    DATA_CORRUPTION = "data_corruption"
    SERVICE_ERROR = "service_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    CRISIS_ERROR = "crisis_error"
    STORAGE_ERROR = "storage_error"


class RecoveryStrategy(str, Enum):
    """Recovery strategies for different error types."""

    RETRY = "retry"
    RECONNECT = "reconnect"
    RESTORE_STATE = "restore_state"
    FALLBACK_MODE = "fallback_mode"
    MANUAL_INTERVENTION = "manual_intervention"
    ABANDON_CONVERSATION = "abandon_conversation"


class ConversationError(Exception):
    """Custom exception for conversation-related errors."""

    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        conversation_id: str | None = None,
        recoverable: bool = True,
        recovery_strategy: RecoveryStrategy | None = None,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.conversation_id = conversation_id
        self.recoverable = recoverable
        self.recovery_strategy = recovery_strategy
        self.timestamp = datetime.utcnow()


class ConversationErrorHandler:
    """Handles errors and recovery for conversational character creation."""

    def __init__(self, conversational_service: ConversationalCharacterService):
        self.conversational_service = conversational_service
        self.error_history: dict[str, list[ConversationError]] = {}
        self.recovery_attempts: dict[str, int] = {}
        self.max_recovery_attempts = 3

        # Error handling strategies
        self.error_strategies = self._initialize_error_strategies()

        logger.info("ConversationErrorHandler initialized")

    def _initialize_error_strategies(self) -> dict[ErrorType, dict[str, Any]]:
        """Initialize error handling strategies for different error types."""
        return {
            ErrorType.CONNECTION_ERROR: {
                "recovery_strategy": RecoveryStrategy.RECONNECT,
                "max_retries": 3,
                "retry_delay": 2.0,
                "exponential_backoff": True,
                "user_message": "Connection lost. Attempting to reconnect...",
                "fallback_message": "Unable to reconnect. Please refresh the page.",
            },
            ErrorType.VALIDATION_ERROR: {
                "recovery_strategy": RecoveryStrategy.RETRY,
                "max_retries": 1,
                "retry_delay": 0.5,
                "exponential_backoff": False,
                "user_message": "Please check your input and try again.",
                "fallback_message": "Input validation failed. Please contact support.",
            },
            ErrorType.DATA_CORRUPTION: {
                "recovery_strategy": RecoveryStrategy.RESTORE_STATE,
                "max_retries": 2,
                "retry_delay": 1.0,
                "exponential_backoff": True,
                "user_message": "Restoring conversation state...",
                "fallback_message": "Unable to restore conversation. Starting fresh.",
            },
            ErrorType.SERVICE_ERROR: {
                "recovery_strategy": RecoveryStrategy.RETRY,
                "max_retries": 2,
                "retry_delay": 3.0,
                "exponential_backoff": True,
                "user_message": "Service temporarily unavailable. Retrying...",
                "fallback_message": "Service is currently unavailable. Please try again later.",
            },
            ErrorType.TIMEOUT_ERROR: {
                "recovery_strategy": RecoveryStrategy.RETRY,
                "max_retries": 2,
                "retry_delay": 1.0,
                "exponential_backoff": False,
                "user_message": "Request timed out. Retrying...",
                "fallback_message": "Connection is too slow. Please check your internet.",
            },
            ErrorType.AUTHENTICATION_ERROR: {
                "recovery_strategy": RecoveryStrategy.MANUAL_INTERVENTION,
                "max_retries": 0,
                "retry_delay": 0.0,
                "exponential_backoff": False,
                "user_message": "Authentication failed. Please log in again.",
                "fallback_message": "Please refresh the page and log in again.",
            },
            ErrorType.RATE_LIMIT_ERROR: {
                "recovery_strategy": RecoveryStrategy.RETRY,
                "max_retries": 3,
                "retry_delay": 5.0,
                "exponential_backoff": True,
                "user_message": "Please slow down. Waiting before retrying...",
                "fallback_message": "Rate limit exceeded. Please wait before continuing.",
            },
            ErrorType.CRISIS_ERROR: {
                "recovery_strategy": RecoveryStrategy.MANUAL_INTERVENTION,
                "max_retries": 0,
                "retry_delay": 0.0,
                "exponential_backoff": False,
                "user_message": "Crisis detected. Connecting you with support resources.",
                "fallback_message": "Please contact emergency services if you're in immediate danger.",
            },
            ErrorType.STORAGE_ERROR: {
                "recovery_strategy": RecoveryStrategy.FALLBACK_MODE,
                "max_retries": 2,
                "retry_delay": 2.0,
                "exponential_backoff": True,
                "user_message": "Saving conversation locally...",
                "fallback_message": "Unable to save progress. Please export your conversation.",
            },
        }

    async def handle_error(
        self, error: Exception, conversation_id: str | None = None
    ) -> tuple[bool, str]:
        """
        Handle an error and attempt recovery.

        Args:
            error: The exception that occurred
            conversation_id: ID of the conversation where error occurred

        Returns:
            Tuple of (recovery_successful, user_message)
        """
        try:
            # Convert exception to ConversationError if needed
            if isinstance(error, ConversationError):
                conv_error = error
            else:
                conv_error = self._classify_error(error, conversation_id)

            # Log the error
            logger.error(
                f"Conversation error: {conv_error.error_type.value} - {str(conv_error)}"
            )

            # Track error history
            self._track_error(conv_error)

            # Check if recovery should be attempted
            if not conv_error.recoverable:
                return False, self._get_fallback_message(conv_error.error_type)

            # Check recovery attempt limits
            if not self._can_attempt_recovery(conv_error):
                return False, self._get_fallback_message(conv_error.error_type)

            # Attempt recovery
            recovery_successful = await self._attempt_recovery(conv_error)

            if recovery_successful:
                return True, self._get_user_message(conv_error.error_type)
            else:
                return False, self._get_fallback_message(conv_error.error_type)

        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return False, "An unexpected error occurred. Please refresh the page."

    def _classify_error(
        self, error: Exception, conversation_id: str | None = None
    ) -> ConversationError:
        """Classify an exception into a ConversationError."""
        error_message = str(error)
        error_type = ErrorType.SERVICE_ERROR  # Default

        # Classify based on error message or type
        if (
            "connection" in error_message.lower()
            or "websocket" in error_message.lower()
        ):
            error_type = ErrorType.CONNECTION_ERROR
        elif (
            "validation" in error_message.lower() or "invalid" in error_message.lower()
        ):
            error_type = ErrorType.VALIDATION_ERROR
        elif "timeout" in error_message.lower():
            error_type = ErrorType.TIMEOUT_ERROR
        elif "auth" in error_message.lower() or "unauthorized" in error_message.lower():
            error_type = ErrorType.AUTHENTICATION_ERROR
        elif (
            "rate limit" in error_message.lower() or "too many" in error_message.lower()
        ):
            error_type = ErrorType.RATE_LIMIT_ERROR
        elif "crisis" in error_message.lower() or "emergency" in error_message.lower():
            error_type = ErrorType.CRISIS_ERROR
        elif "storage" in error_message.lower() or "database" in error_message.lower():
            error_type = ErrorType.STORAGE_ERROR
        elif (
            "corrupt" in error_message.lower()
            or "invalid state" in error_message.lower()
        ):
            error_type = ErrorType.DATA_CORRUPTION

        strategy = self.error_strategies.get(error_type, {}).get("recovery_strategy")

        return ConversationError(
            error_type=error_type,
            message=error_message,
            conversation_id=conversation_id,
            recoverable=error_type != ErrorType.AUTHENTICATION_ERROR,
            recovery_strategy=strategy,
        )

    def _track_error(self, error: ConversationError) -> None:
        """Track error in history for analysis."""
        conversation_id = error.conversation_id or "unknown"

        if conversation_id not in self.error_history:
            self.error_history[conversation_id] = []

        self.error_history[conversation_id].append(error)

        # Limit history size
        if len(self.error_history[conversation_id]) > 10:
            self.error_history[conversation_id] = self.error_history[conversation_id][
                -10:
            ]

    def _can_attempt_recovery(self, error: ConversationError) -> bool:
        """Check if recovery should be attempted based on error history."""
        conversation_id = error.conversation_id or "unknown"

        # Check total recovery attempts
        current_attempts = self.recovery_attempts.get(conversation_id, 0)
        if current_attempts >= self.max_recovery_attempts:
            return False

        # Check error-specific limits
        strategy = self.error_strategies.get(error.error_type, {})
        max_retries = strategy.get("max_retries", 0)

        # Count recent errors of the same type
        recent_errors = [
            e
            for e in self.error_history.get(conversation_id, [])
            if e.error_type == error.error_type
            and (datetime.utcnow() - e.timestamp) < timedelta(minutes=5)
        ]

        return len(recent_errors) <= max_retries

    async def _attempt_recovery(self, error: ConversationError) -> bool:
        """Attempt to recover from the error."""
        conversation_id = error.conversation_id or "unknown"
        strategy = error.recovery_strategy

        # Increment recovery attempts
        self.recovery_attempts[conversation_id] = (
            self.recovery_attempts.get(conversation_id, 0) + 1
        )

        try:
            if strategy == RecoveryStrategy.RETRY:
                return await self._retry_operation(error)
            elif strategy == RecoveryStrategy.RECONNECT:
                return await self._reconnect_conversation(error)
            elif strategy == RecoveryStrategy.RESTORE_STATE:
                return await self._restore_conversation_state(error)
            elif strategy == RecoveryStrategy.FALLBACK_MODE:
                return await self._enable_fallback_mode(error)
            else:
                return False

        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return False

    async def _retry_operation(self, error: ConversationError) -> bool:
        """Retry the failed operation."""
        strategy = self.error_strategies.get(error.error_type, {})
        delay = strategy.get("retry_delay", 1.0)

        # Apply exponential backoff if configured
        if strategy.get("exponential_backoff", False):
            attempt_count = self.recovery_attempts.get(
                error.conversation_id or "unknown", 1
            )
            delay *= 2 ** (attempt_count - 1)

        # Wait before retry
        import asyncio

        await asyncio.sleep(delay)

        # The actual retry would be handled by the calling code
        return True

    async def _reconnect_conversation(self, error: ConversationError) -> bool:
        """Attempt to reconnect the conversation."""
        if not error.conversation_id:
            return False

        try:
            # Get conversation state
            conversation_state = (
                await self.conversational_service.get_conversation_state(
                    error.conversation_id
                )
            )
            if not conversation_state:
                return False

            # Resume conversation if it was paused
            if conversation_state.status == ConversationStatus.PAUSED:
                result = await self.conversational_service.resume_conversation(
                    error.conversation_id
                )
                return result is not None

            return True

        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False

    async def _restore_conversation_state(self, error: ConversationError) -> bool:
        """Restore conversation state from backup or last known good state."""
        if not error.conversation_id:
            return False

        try:
            # This would typically restore from a backup or reconstruct state
            # For now, we'll just validate the current state
            conversation_state = (
                await self.conversational_service.get_conversation_state(
                    error.conversation_id
                )
            )

            if conversation_state:
                # Validate state integrity
                if self._validate_conversation_state(conversation_state):
                    return True
                else:
                    # Attempt to repair state
                    return await self._repair_conversation_state(conversation_state)

            return False

        except Exception as e:
            logger.error(f"State restoration failed: {e}")
            return False

    async def _enable_fallback_mode(self, error: ConversationError) -> bool:
        """Enable fallback mode for degraded functionality."""
        # This would enable a simplified mode of operation
        # For example, local storage instead of server storage
        logger.info(f"Enabling fallback mode for conversation {error.conversation_id}")
        return True

    def _validate_conversation_state(
        self, conversation_state: ConversationState
    ) -> bool:
        """Validate conversation state integrity."""
        try:
            # Check required fields
            if not conversation_state.conversation_id:
                return False
            if not conversation_state.player_id:
                return False

            # Check message history integrity
            for message in conversation_state.message_history:
                if not message.message_id or not message.timestamp:
                    return False

            # Check progress consistency
            if (
                conversation_state.progress.progress_percentage < 0
                or conversation_state.progress.progress_percentage > 100
            ):
                return False

            return True

        except Exception as e:
            logger.error(f"State validation failed: {e}")
            return False

    async def _repair_conversation_state(
        self, conversation_state: ConversationState
    ) -> bool:
        """Attempt to repair corrupted conversation state."""
        try:
            # Remove invalid messages
            valid_messages = []
            for message in conversation_state.message_history:
                if message.message_id and message.timestamp:
                    valid_messages.append(message)

            conversation_state.message_history = valid_messages

            # Fix progress if invalid
            if conversation_state.progress.progress_percentage < 0:
                conversation_state.progress.progress_percentage = 0
            elif conversation_state.progress.progress_percentage > 100:
                conversation_state.progress.progress_percentage = 100

            # Update timestamp
            conversation_state.update_activity()

            logger.info(
                f"Repaired conversation state for {conversation_state.conversation_id}"
            )
            return True

        except Exception as e:
            logger.error(f"State repair failed: {e}")
            return False

    def _get_user_message(self, error_type: ErrorType) -> str:
        """Get user-friendly message for error type."""
        return self.error_strategies.get(error_type, {}).get(
            "user_message", "An error occurred. Retrying..."
        )

    def _get_fallback_message(self, error_type: ErrorType) -> str:
        """Get fallback message when recovery fails."""
        return self.error_strategies.get(error_type, {}).get(
            "fallback_message", "Unable to recover. Please try again later."
        )

    def get_error_summary(self, conversation_id: str) -> dict[str, Any]:
        """Get error summary for a conversation."""
        errors = self.error_history.get(conversation_id, [])

        if not errors:
            return {"total_errors": 0, "error_types": {}, "last_error": None}

        error_types = {}
        for error in errors:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "last_error": {
                "type": errors[-1].error_type.value,
                "message": str(errors[-1]),
                "timestamp": errors[-1].timestamp.isoformat(),
            },
            "recovery_attempts": self.recovery_attempts.get(conversation_id, 0),
        }

    def clear_error_history(self, conversation_id: str) -> None:
        """Clear error history for a conversation."""
        if conversation_id in self.error_history:
            del self.error_history[conversation_id]
        if conversation_id in self.recovery_attempts:
            del self.recovery_attempts[conversation_id]
