"""
Real-time error reporting and recovery notifications.

This module provides comprehensive error reporting and recovery notification
systems for agent operations and workflows.
"""

from __future__ import annotations

import asyncio
import logging
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from .event_publisher import EventPublisher
from .models import (
    AgentStatus,
    WorkflowStatus,
    create_agent_status_event,
    create_error_event,
    create_workflow_progress_event,
)

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStatus(str, Enum):
    """Recovery attempt status."""

    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class ErrorReport:
    """Comprehensive error report."""

    error_id: str
    timestamp: float
    error_type: str
    error_message: str
    severity: ErrorSeverity
    agent_id: str | None = None
    workflow_id: str | None = None
    operation_id: str | None = None
    user_id: str | None = None

    # Error details
    exception_type: str | None = None
    stack_trace: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    # Recovery information
    recovery_status: RecoveryStatus = RecoveryStatus.NOT_ATTEMPTED
    recovery_attempts: int = 0
    recovery_messages: list[str] = field(default_factory=list)
    recovery_success: bool = False

    # Notification tracking
    notifications_sent: set[str] = field(default_factory=set)
    escalation_level: int = 0


class ErrorReportingManager:
    """Manages real-time error reporting and recovery notifications."""

    def __init__(
        self,
        event_publisher: EventPublisher | None = None,
        max_recovery_attempts: int = 3,
        escalation_timeout: float = 300.0,  # 5 minutes
        cleanup_interval: float = 3600.0,  # 1 hour
        error_retention_hours: int = 24,
    ):
        self.event_publisher = event_publisher
        self.max_recovery_attempts = max_recovery_attempts
        self.escalation_timeout = escalation_timeout
        self.cleanup_interval = cleanup_interval
        self.error_retention_hours = error_retention_hours

        # Error tracking
        self.active_errors: dict[str, ErrorReport] = {}
        self.error_history: list[ErrorReport] = []

        # Recovery handlers
        self.recovery_handlers: dict[str, Callable] = {}  # error_type -> handler

        # Notification handlers
        self.notification_handlers: list[Callable] = []

        # Background tasks
        self.cleanup_task: asyncio.Task | None = None
        self.escalation_task: asyncio.Task | None = None
        self.is_running = False

        logger.info("ErrorReportingManager initialized")

    async def start(self) -> None:
        """Start the error reporting manager."""
        if self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.escalation_task = asyncio.create_task(self._escalation_loop())

        logger.info("ErrorReportingManager started")

    async def stop(self) -> None:
        """Stop the error reporting manager."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        for task in [self.cleanup_task, self.escalation_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("ErrorReportingManager stopped")

    async def report_error(
        self,
        error_type: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        agent_id: str | None = None,
        workflow_id: str | None = None,
        operation_id: str | None = None,
        user_id: str | None = None,
        exception: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Report an error with comprehensive details."""
        error_id = f"error_{uuid4().hex[:8]}_{int(time.time() * 1000)}"

        # Create error report
        error_report = ErrorReport(
            error_id=error_id,
            timestamp=time.time(),
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            agent_id=agent_id,
            workflow_id=workflow_id,
            operation_id=operation_id,
            user_id=user_id,
            context=context or {},
        )

        # Add exception details if provided
        if exception:
            error_report.exception_type = type(exception).__name__
            error_report.stack_trace = traceback.format_exc()

        # Store error report
        self.active_errors[error_id] = error_report
        self.error_history.append(error_report)

        # Broadcast error event
        await self._broadcast_error_event(error_report)

        # Attempt automatic recovery
        await self._attempt_recovery(error_report)

        # Send notifications
        await self._send_notifications(error_report)

        logger.error(f"Error reported: {error_id} - {error_message}")
        return error_id

    async def report_recovery_attempt(
        self, error_id: str, recovery_message: str, success: bool = False
    ) -> bool:
        """Report a recovery attempt for an error."""
        if error_id not in self.active_errors:
            return False

        error_report = self.active_errors[error_id]
        error_report.recovery_attempts += 1
        error_report.recovery_messages.append(recovery_message)

        if success:
            error_report.recovery_status = RecoveryStatus.SUCCEEDED
            error_report.recovery_success = True

            # Broadcast recovery success event
            await self._broadcast_recovery_event(error_report, success=True)

            # Move to history and remove from active
            self.active_errors.pop(error_id, None)

        else:
            error_report.recovery_status = RecoveryStatus.FAILED

            # Check if we should abandon recovery
            if error_report.recovery_attempts >= self.max_recovery_attempts:
                error_report.recovery_status = RecoveryStatus.ABANDONED
                await self._broadcast_recovery_event(
                    error_report, success=False, abandoned=True
                )
            else:
                await self._broadcast_recovery_event(error_report, success=False)

        logger.info(
            f"Recovery attempt for {error_id}: {recovery_message}, success: {success}"
        )
        return True

    async def _broadcast_error_event(self, error_report: ErrorReport) -> None:
        """Broadcast error event to WebSocket clients."""
        if not self.event_publisher:
            return

        try:
            if error_report.agent_id:
                # Agent-specific error
                event = create_agent_status_event(
                    agent_id=error_report.agent_id,
                    status=AgentStatus.ERROR,
                    message=error_report.error_message,
                    metadata={
                        "error_id": error_report.error_id,
                        "error_type": error_report.error_type,
                        "severity": error_report.severity.value,
                        "workflow_id": error_report.workflow_id,
                        "operation_id": error_report.operation_id,
                        "exception_type": error_report.exception_type,
                        "context": error_report.context,
                    },
                )
            elif error_report.workflow_id:
                # Workflow-specific error
                event = create_workflow_progress_event(
                    workflow_id=error_report.workflow_id,
                    status=WorkflowStatus.FAILED,
                    progress=0.0,
                    message=error_report.error_message,
                    metadata={
                        "error_id": error_report.error_id,
                        "error_type": error_report.error_type,
                        "severity": error_report.severity.value,
                        "exception_type": error_report.exception_type,
                        "context": error_report.context,
                    },
                )
            else:
                # System-wide error
                event = create_error_event(
                    error_type=error_report.error_type,
                    error_message=error_report.error_message,
                    metadata={
                        "error_id": error_report.error_id,
                        "severity": error_report.severity.value,
                        "exception_type": error_report.exception_type,
                        "context": error_report.context,
                    },
                )

            await self.event_publisher.publish_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast error event: {e}")

    async def _broadcast_recovery_event(
        self, error_report: ErrorReport, success: bool, abandoned: bool = False
    ) -> None:
        """Broadcast recovery event to WebSocket clients."""
        if not self.event_publisher:
            return

        try:
            if success:
                status = AgentStatus.COMPLETED
                message = f"Recovery successful for {error_report.error_type}"
            elif abandoned:
                status = AgentStatus.ERROR
                message = f"Recovery abandoned for {error_report.error_type}"
            else:
                status = AgentStatus.PROCESSING
                message = f"Recovery attempt {error_report.recovery_attempts} for {error_report.error_type}"

            if error_report.agent_id:
                event = create_agent_status_event(
                    agent_id=error_report.agent_id,
                    status=status,
                    message=message,
                    metadata={
                        "error_id": error_report.error_id,
                        "recovery_attempts": error_report.recovery_attempts,
                        "recovery_success": success,
                        "recovery_abandoned": abandoned,
                        "recovery_messages": error_report.recovery_messages,
                    },
                )
                await self.event_publisher.publish_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast recovery event: {e}")

    async def _attempt_recovery(self, error_report: ErrorReport) -> None:
        """Attempt automatic recovery for an error."""
        if error_report.error_type not in self.recovery_handlers:
            return

        error_report.recovery_status = RecoveryStatus.IN_PROGRESS

        try:
            handler = self.recovery_handlers[error_report.error_type]
            success = await handler(error_report)

            await self.report_recovery_attempt(
                error_report.error_id, "Automatic recovery attempt", success=success
            )

        except Exception as e:
            logger.error(f"Recovery handler failed for {error_report.error_id}: {e}")
            await self.report_recovery_attempt(
                error_report.error_id,
                f"Recovery handler failed: {str(e)}",
                success=False,
            )

    async def _send_notifications(self, error_report: ErrorReport) -> None:
        """Send notifications for an error."""
        for handler in self.notification_handlers:
            try:
                await handler(error_report)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up old errors."""
        while self.is_running:
            try:
                current_time = time.time()
                retention_cutoff = current_time - (self.error_retention_hours * 3600)

                # Clean up old errors from history
                self.error_history = [
                    error
                    for error in self.error_history
                    if error.timestamp > retention_cutoff
                ]

                # Clean up resolved errors from active list
                resolved_errors = [
                    error_id
                    for error_id, error in self.active_errors.items()
                    if error.recovery_success
                    or error.recovery_status == RecoveryStatus.ABANDONED
                ]

                for error_id in resolved_errors:
                    self.active_errors.pop(error_id, None)

                await asyncio.sleep(self.cleanup_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _escalation_loop(self) -> None:
        """Background task to handle error escalation."""
        while self.is_running:
            try:
                current_time = time.time()

                for error_report in self.active_errors.values():
                    # Check if error needs escalation
                    if (
                        current_time - error_report.timestamp > self.escalation_timeout
                        and error_report.escalation_level == 0
                        and error_report.severity
                        in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
                    ):

                        error_report.escalation_level = 1
                        await self._escalate_error(error_report)

                await asyncio.sleep(60.0)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in escalation loop: {e}")

    async def _escalate_error(self, error_report: ErrorReport) -> None:
        """Escalate an unresolved error."""
        logger.warning(
            f"Escalating error {error_report.error_id}: {error_report.error_message}"
        )

        # Send escalation notifications
        for handler in self.notification_handlers:
            try:
                await handler(error_report, escalated=True)
            except Exception as e:
                logger.error(f"Escalation notification failed: {e}")

    def add_recovery_handler(self, error_type: str, handler: Callable) -> None:
        """Add a recovery handler for a specific error type."""
        self.recovery_handlers[error_type] = handler
        logger.debug(f"Added recovery handler for {error_type}")

    def add_notification_handler(self, handler: Callable) -> None:
        """Add a notification handler."""
        self.notification_handlers.append(handler)
        logger.debug("Added notification handler")

    def get_error_statistics(self) -> dict[str, Any]:
        """Get error reporting statistics."""
        return {
            "active_errors": len(self.active_errors),
            "total_errors": len(self.error_history),
            "errors_by_severity": self._get_errors_by_severity(),
            "errors_by_type": self._get_errors_by_type(),
            "recovery_success_rate": self._get_recovery_success_rate(),
            "average_recovery_attempts": self._get_average_recovery_attempts(),
        }

    def _get_errors_by_severity(self) -> dict[str, int]:
        """Get error count by severity."""
        counts = {}
        for error in self.error_history:
            severity = error.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _get_errors_by_type(self) -> dict[str, int]:
        """Get error count by type."""
        counts = {}
        for error in self.error_history:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts

    def _get_recovery_success_rate(self) -> float:
        """Get recovery success rate."""
        attempted_recoveries = [
            e for e in self.error_history if e.recovery_attempts > 0
        ]
        if not attempted_recoveries:
            return 0.0

        successful_recoveries = [e for e in attempted_recoveries if e.recovery_success]
        return len(successful_recoveries) / len(attempted_recoveries)

    def _get_average_recovery_attempts(self) -> float:
        """Get average number of recovery attempts."""
        attempted_recoveries = [
            e for e in self.error_history if e.recovery_attempts > 0
        ]
        if not attempted_recoveries:
            return 0.0

        total_attempts = sum(e.recovery_attempts for e in attempted_recoveries)
        return total_attempts / len(attempted_recoveries)
