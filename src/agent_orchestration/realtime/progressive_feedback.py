"""

# Logseq: [[TTA.dev/Agent_orchestration/Realtime/Progressive_feedback]]
Progressive feedback mechanisms for long-running agent orchestration operations.

This module provides streaming response systems, incremental update mechanisms,
and progress tracking for workflows and operations that take significant time
to complete.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .models import (
    AgentStatus,
    create_agent_status_event,
    create_progressive_feedback_event,
)

logger = logging.getLogger(__name__)


@dataclass
class OperationProgress:
    """Tracks progress for a long-running operation."""

    operation_id: str
    operation_type: str
    user_id: str | None = None
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    current_stage: str = "initializing"
    progress_percentage: float = 0.0
    total_steps: int | None = None
    completed_steps: int = 0
    estimated_completion: float | None = None
    intermediate_results: dict[str, Any] = field(default_factory=dict)
    status: str = "running"
    error_message: str | None = None

    def update_progress(
        self,
        stage: str | None = None,
        progress_percentage: float | None = None,
        completed_steps: int | None = None,
        estimated_completion: float | None = None,
        intermediate_result: dict[str, Any] | None = None,
    ) -> None:
        """Update operation progress."""
        self.last_update = time.time()

        if stage is not None:
            self.current_stage = stage

        if progress_percentage is not None:
            self.progress_percentage = max(0.0, min(100.0, progress_percentage))

        if completed_steps is not None:
            self.completed_steps = completed_steps
            if self.total_steps:
                self.progress_percentage = (completed_steps / self.total_steps) * 100.0

        if estimated_completion is not None:
            self.estimated_completion = estimated_completion

        if intermediate_result is not None:
            self.intermediate_results.update(intermediate_result)

    def get_estimated_remaining(self) -> float | None:
        """Calculate estimated remaining time."""
        if self.estimated_completion:
            return max(0.0, self.estimated_completion - time.time())

        if self.progress_percentage > 0:
            elapsed = time.time() - self.start_time
            total_estimated = elapsed / (self.progress_percentage / 100.0)
            return max(0.0, total_estimated - elapsed)

        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "last_update": self.last_update,
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "estimated_completion": self.estimated_completion,
            "estimated_remaining": self.get_estimated_remaining(),
            "intermediate_results": self.intermediate_results,
            "status": self.status,
            "error_message": self.error_message,
            "duration": time.time() - self.start_time,
        }


class ProgressiveFeedbackManager:
    """Manages progressive feedback for long-running operations."""

    def __init__(
        self,
        event_publisher: Any | None = None,
        update_interval: float = 1.0,
        max_updates_per_operation: int = 100,
        stream_intermediate_results: bool = True,
        cleanup_interval: float = 300.0,  # 5 minutes
        operation_timeout: float = 3600.0,  # 1 hour
    ):
        self.event_publisher = event_publisher
        self.update_interval = update_interval
        self.max_updates_per_operation = max_updates_per_operation
        self.stream_intermediate_results = stream_intermediate_results
        self.cleanup_interval = cleanup_interval
        self.operation_timeout = operation_timeout

        # Operation tracking
        self.active_operations: dict[str, OperationProgress] = {}
        self.operation_update_counts: dict[str, int] = {}
        self.operation_callbacks: dict[str, set[Callable]] = {}

        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._is_running = False

        logger.info("ProgressiveFeedbackManager initialized")

    async def start(self) -> None:
        """Start the progressive feedback manager."""
        if self._is_running:
            return

        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("ProgressiveFeedbackManager started")

    async def stop(self) -> None:
        """Stop the progressive feedback manager."""
        if not self._is_running:
            return

        self._is_running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        # Complete all active operations
        for operation_id in list(self.active_operations.keys()):
            await self.complete_operation(operation_id, "manager_shutdown")

        logger.info("ProgressiveFeedbackManager stopped")

    async def start_operation(
        self,
        operation_type: str,
        user_id: str | None = None,
        operation_id: str | None = None,
        total_steps: int | None = None,
        estimated_duration: float | None = None,
    ) -> str:
        """Start tracking a new long-running operation."""
        if operation_id is None:
            operation_id = uuid4().hex

        # Create operation progress tracker
        operation = OperationProgress(
            operation_id=operation_id,
            operation_type=operation_type,
            user_id=user_id,
            total_steps=total_steps,
        )

        if estimated_duration:
            operation.estimated_completion = time.time() + estimated_duration

        # Store operation
        self.active_operations[operation_id] = operation
        self.operation_update_counts[operation_id] = 0
        self.operation_callbacks[operation_id] = set()

        # Send initial progress event
        await self._send_progress_event(operation, "Operation started")

        logger.info(f"Started tracking operation: {operation_id} ({operation_type})")
        return operation_id

    async def update_operation_progress(
        self,
        operation_id: str,
        stage: str | None = None,
        message: str | None = None,
        progress_percentage: float | None = None,
        completed_steps: int | None = None,
        estimated_completion: float | None = None,
        intermediate_result: dict[str, Any] | None = None,
    ) -> bool:
        """Update progress for an operation."""
        operation = self.active_operations.get(operation_id)
        if not operation:
            logger.warning(f"Operation not found: {operation_id}")
            return False

        # Check update limits
        update_count = self.operation_update_counts.get(operation_id, 0)
        if update_count >= self.max_updates_per_operation:
            logger.warning(f"Max updates reached for operation: {operation_id}")
            return False

        # Update operation progress
        operation.update_progress(
            stage=stage,
            progress_percentage=progress_percentage,
            completed_steps=completed_steps,
            estimated_completion=estimated_completion,
            intermediate_result=intermediate_result,
        )

        # Send progress event
        await self._send_progress_event(
            operation, message or f"Progress update: {stage or 'continuing'}"
        )

        # Increment update count
        self.operation_update_counts[operation_id] = update_count + 1

        # Call registered callbacks
        await self._call_operation_callbacks(operation_id, operation)

        return True

    async def complete_operation(
        self,
        operation_id: str,
        final_message: str = "Operation completed",
        final_result: dict[str, Any] | None = None,
        success: bool = True,
    ) -> bool:
        """Complete an operation."""
        operation = self.active_operations.get(operation_id)
        if not operation:
            logger.warning(f"Operation not found: {operation_id}")
            return False

        # Update final status
        operation.status = "completed" if success else "failed"
        operation.progress_percentage = (
            100.0 if success else operation.progress_percentage
        )

        if final_result:
            operation.intermediate_results.update(final_result)

        # Send final progress event
        await self._send_progress_event(operation, final_message)

        # Call final callbacks
        await self._call_operation_callbacks(operation_id, operation)

        # Clean up
        self.active_operations.pop(operation_id, None)
        self.operation_update_counts.pop(operation_id, None)
        self.operation_callbacks.pop(operation_id, None)

        logger.info(
            f"Completed operation: {operation_id} ({'success' if success else 'failed'})"
        )
        return True

    async def fail_operation(
        self,
        operation_id: str,
        error_message: str,
        error_details: dict[str, Any] | None = None,
    ) -> bool:
        """Mark an operation as failed."""
        operation = self.active_operations.get(operation_id)
        if not operation:
            logger.warning(f"Operation not found: {operation_id}")
            return False

        operation.status = "failed"
        operation.error_message = error_message

        if error_details:
            operation.intermediate_results["error_details"] = error_details

        return await self.complete_operation(
            operation_id, f"Operation failed: {error_message}", success=False
        )

    def add_operation_callback(
        self, operation_id: str, callback: Callable[[OperationProgress], None]
    ) -> bool:
        """Add a callback for operation updates."""
        if operation_id not in self.active_operations:
            return False

        self.operation_callbacks[operation_id].add(callback)
        return True

    def remove_operation_callback(
        self, operation_id: str, callback: Callable[[OperationProgress], None]
    ) -> bool:
        """Remove a callback for operation updates."""
        if operation_id not in self.operation_callbacks:
            return False

        self.operation_callbacks[operation_id].discard(callback)
        return True

    def get_operation_status(self, operation_id: str) -> dict[str, Any] | None:
        """Get current status of an operation."""
        operation = self.active_operations.get(operation_id)
        return operation.to_dict() if operation else None

    def get_active_operations(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Get all active operations, optionally filtered by user."""
        operations = []

        for operation in self.active_operations.values():
            if user_id is None or operation.user_id == user_id:
                operations.append(operation.to_dict())

        return operations

    async def _send_progress_event(
        self, operation: OperationProgress, message: str
    ) -> None:
        """Send a progressive feedback event."""
        if not self.event_publisher:
            return

        try:
            intermediate_result = None
            if self.stream_intermediate_results and operation.intermediate_results:
                intermediate_result = operation.intermediate_results.copy()

            await self.event_publisher.publish_progressive_feedback_event(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                stage=operation.current_stage,
                message=message,
                progress_percentage=operation.progress_percentage,
                intermediate_result=intermediate_result,
                estimated_remaining=operation.get_estimated_remaining(),
                user_id=operation.user_id,
            )

        except Exception as e:
            logger.error(f"Failed to send progress event: {e}")

    async def _call_operation_callbacks(
        self, operation_id: str, operation: OperationProgress
    ) -> None:
        """Call all registered callbacks for an operation."""
        callbacks = self.operation_callbacks.get(operation_id, set())

        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(operation)
                else:
                    callback(operation)
            except Exception as e:
                logger.error(f"Error in operation callback: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up stale operations."""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                current_time = time.time()
                stale_operations = []

                for operation_id, operation in self.active_operations.items():
                    # Check for timeout
                    if current_time - operation.start_time > self.operation_timeout or (
                        current_time - operation.last_update > self.cleanup_interval * 2
                    ):
                        stale_operations.append(operation_id)

                # Clean up stale operations
                for operation_id in stale_operations:
                    await self.fail_operation(
                        operation_id,
                        "Operation timed out or became stale",
                        {"cleanup_reason": "timeout_or_stale"},
                    )

                if stale_operations:
                    logger.info(f"Cleaned up {len(stale_operations)} stale operations")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """Get progressive feedback manager statistics."""
        return {
            "is_running": self._is_running,
            "active_operations": len(self.active_operations),
            "total_updates": sum(self.operation_update_counts.values()),
            "configuration": {
                "update_interval": self.update_interval,
                "max_updates_per_operation": self.max_updates_per_operation,
                "stream_intermediate_results": self.stream_intermediate_results,
                "cleanup_interval": self.cleanup_interval,
                "operation_timeout": self.operation_timeout,
            },
            "operations_by_type": self._get_operations_by_type(),
            "operations_by_user": self._get_operations_by_user(),
        }

    def _get_operations_by_type(self) -> dict[str, int]:
        """Get count of operations by type."""
        counts = {}
        for operation in self.active_operations.values():
            counts[operation.operation_type] = (
                counts.get(operation.operation_type, 0) + 1
            )
        return counts

    def _get_operations_by_user(self) -> dict[str, int]:
        """Get count of operations by user."""
        counts = {}
        for operation in self.active_operations.values():
            user_id = operation.user_id or "anonymous"
            counts[user_id] = counts.get(user_id, 0) + 1
        return counts

    async def track_agent_operation(
        self,
        agent_id: str,
        operation_type: str,
        user_id: str | None = None,
        workflow_id: str | None = None,
        estimated_duration: float | None = None,
    ) -> str:
        """Start tracking a specific agent operation with enhanced feedback."""
        operation_id = f"{agent_id}_{operation_type}_{uuid4().hex[:8]}"

        # Create operation progress tracker
        operation = OperationProgress(
            operation_id=operation_id,
            operation_type=f"agent_{operation_type}",
            user_id=user_id,
        )

        # Add agent-specific metadata
        operation.intermediate_results.update(
            {
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "estimated_duration": estimated_duration,
                "operation_start": time.time(),
            }
        )

        self.active_operations[operation_id] = operation
        self.operation_update_counts[operation_id] = 0

        # Send initial agent status event
        if self.event_publisher:
            initial_event = create_agent_status_event(
                agent_id=agent_id,
                agent_type="unknown",
                status=AgentStatus.PROCESSING,
                metadata={
                    "message": f"Started {operation_type} operation",
                    "operation_id": operation_id,
                    "workflow_id": workflow_id,
                    "estimated_duration": estimated_duration,
                },
            )
            await self.event_publisher._publish_event(initial_event)  # type: ignore[union-attr]

        logger.debug(f"Started tracking agent operation: {operation_id}")
        return operation_id

    async def update_agent_operation(
        self,
        operation_id: str,
        progress: float,
        stage: str,
        message: str = "",
        intermediate_result: dict[str, Any] | None = None,
    ) -> bool:
        """Update progress for an agent operation."""
        if operation_id not in self.active_operations:
            return False

        operation = self.active_operations[operation_id]

        # Update operation progress
        operation.update_progress(
            stage=stage,
            progress_percentage=progress * 100,
            intermediate_result=intermediate_result,
        )

        # Increment update count
        self.operation_update_counts[operation_id] = (
            self.operation_update_counts.get(operation_id, 0) + 1
        )

        # Send progressive feedback event
        if self.event_publisher:
            feedback_event = create_progressive_feedback_event(
                operation_id=operation_id,
                operation_type=operation.operation_type,
                stage=stage,
                message=message or f"Stage: {stage}",
                progress_percentage=progress * 100,
                intermediate_result=intermediate_result,
            )
            await self.event_publisher._publish_event(feedback_event)  # type: ignore[union-attr]

        return True

    async def complete_agent_operation(
        self,
        operation_id: str,
        final_result: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> bool:
        """Complete an agent operation."""
        if operation_id not in self.active_operations:
            return False

        operation = self.active_operations[operation_id]
        agent_id = operation.intermediate_results.get("agent_id")

        # Update operation status
        operation.status = "completed" if success else "failed"
        operation.progress_percentage = 100.0
        operation.error_message = error_message

        if final_result:
            operation.intermediate_results.update(final_result)

        # Send completion event
        if self.event_publisher and agent_id:
            status = AgentStatus.COMPLETED if success else AgentStatus.ERROR
            completion_event = create_agent_status_event(
                agent_id=agent_id,
                agent_type="unknown",
                status=status,
                metadata={
                    "message": error_message or f"Completed {operation.operation_type}",
                    "operation_id": operation_id,
                    "duration": time.time() - operation.start_time,
                    "final_result": final_result,
                    "success": success,
                },
            )
            await self.event_publisher._publish_event(completion_event)  # type: ignore[union-attr]

        # Mark for cleanup
        operation.last_update = time.time()

        logger.debug(f"Completed agent operation: {operation_id}, success: {success}")
        return True
