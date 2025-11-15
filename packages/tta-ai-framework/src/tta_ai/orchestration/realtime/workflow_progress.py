"""
Incremental update mechanisms for workflow progress tracking.

This module provides workflow progress tracking with incremental updates,
milestone tracking, and integration with the progressive feedback system.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from .models import (
    WorkflowStatus,
)

logger = logging.getLogger(__name__)


class WorkflowStage(str, Enum):
    """Workflow execution stages."""

    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowMilestone:
    """Represents a milestone in workflow execution."""

    milestone_id: str
    name: str
    description: str
    stage: WorkflowStage
    weight: float = 1.0  # Relative weight for progress calculation
    completed: bool = False
    completed_at: float | None = None
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def complete(self, metadata: dict[str, Any] | None = None) -> None:
        """Mark milestone as completed."""
        self.completed = True
        self.completed_at = time.time()
        if metadata:
            self.metadata.update(metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "milestone_id": self.milestone_id,
            "name": self.name,
            "description": self.description,
            "stage": self.stage.value,
            "weight": self.weight,
            "completed": self.completed,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class WorkflowProgress:
    """Tracks progress for a workflow execution."""

    workflow_id: str
    workflow_type: str
    user_id: str | None = None
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    current_stage: WorkflowStage = WorkflowStage.INITIALIZING
    status: WorkflowStatus = WorkflowStatus.PENDING
    progress_percentage: float = 0.0
    milestones: list[WorkflowMilestone] = field(default_factory=list)
    current_step: str | None = None
    total_steps: int | None = None
    completed_steps: int = 0
    estimated_completion: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    def add_milestone(
        self,
        name: str,
        description: str,
        stage: WorkflowStage,
        weight: float = 1.0,
        milestone_id: str | None = None,
    ) -> str:
        """Add a milestone to the workflow."""
        if milestone_id is None:
            milestone_id = uuid4().hex

        milestone = WorkflowMilestone(
            milestone_id=milestone_id,
            name=name,
            description=description,
            stage=stage,
            weight=weight,
        )

        self.milestones.append(milestone)
        return milestone_id

    def complete_milestone(self, milestone_id: str, metadata: dict[str, Any] | None = None) -> bool:
        """Complete a milestone."""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                milestone.complete(metadata)
                self._update_progress()
                return True
        return False

    def update_progress(
        self,
        stage: WorkflowStage | None = None,
        status: WorkflowStatus | None = None,
        current_step: str | None = None,
        completed_steps: int | None = None,
        total_steps: int | None = None,
        estimated_completion: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Update workflow progress."""
        self.last_update = time.time()

        if stage is not None:
            self.current_stage = stage

        if status is not None:
            self.status = status

        if current_step is not None:
            self.current_step = current_step

        if completed_steps is not None:
            self.completed_steps = completed_steps

        if total_steps is not None:
            self.total_steps = total_steps

        if estimated_completion is not None:
            self.estimated_completion = estimated_completion

        if metadata is not None:
            self.metadata.update(metadata)

        self._update_progress()

    def _update_progress(self) -> None:
        """Update progress percentage based on milestones and steps."""
        # Calculate progress from milestones
        if self.milestones:
            total_weight = sum(m.weight for m in self.milestones)
            completed_weight = sum(m.weight for m in self.milestones if m.completed)
            milestone_progress = (
                (completed_weight / total_weight) * 100.0 if total_weight > 0 else 0.0
            )
        else:
            milestone_progress = 0.0

        # Calculate progress from steps
        if self.total_steps and self.total_steps > 0:
            step_progress = (self.completed_steps / self.total_steps) * 100.0
        else:
            step_progress = 0.0

        # Use the higher of the two progress calculations
        self.progress_percentage = max(milestone_progress, step_progress)

        # Ensure progress doesn't exceed 100%
        self.progress_percentage = min(100.0, self.progress_percentage)

    def get_estimated_remaining(self) -> float | None:
        """Calculate estimated remaining time."""
        if self.estimated_completion:
            return max(0.0, self.estimated_completion - time.time())

        if self.progress_percentage > 0:
            elapsed = time.time() - self.start_time
            total_estimated = elapsed / (self.progress_percentage / 100.0)
            return max(0.0, total_estimated - elapsed)

        return None

    def get_completed_milestones(self) -> list[WorkflowMilestone]:
        """Get all completed milestones."""
        return [m for m in self.milestones if m.completed]

    def get_pending_milestones(self) -> list[WorkflowMilestone]:
        """Get all pending milestones."""
        return [m for m in self.milestones if not m.completed]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "last_update": self.last_update,
            "current_stage": self.current_stage.value,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "estimated_completion": self.estimated_completion,
            "estimated_remaining": self.get_estimated_remaining(),
            "milestones": [m.to_dict() for m in self.milestones],
            "completed_milestones": len(self.get_completed_milestones()),
            "pending_milestones": len(self.get_pending_milestones()),
            "metadata": self.metadata,
            "error_message": self.error_message,
            "duration": time.time() - self.start_time,
        }


class WorkflowProgressTracker:
    """Manages workflow progress tracking with incremental updates."""

    def __init__(
        self,
        event_publisher: Any | None = None,
        update_interval: float = 2.0,
        auto_publish_updates: bool = True,
        cleanup_interval: float = 600.0,  # 10 minutes
        workflow_timeout: float = 7200.0,  # 2 hours
    ):
        self.event_publisher = event_publisher
        self.update_interval = update_interval
        self.auto_publish_updates = auto_publish_updates
        self.cleanup_interval = cleanup_interval
        self.workflow_timeout = workflow_timeout

        # Workflow tracking
        self.active_workflows: dict[str, WorkflowProgress] = {}
        self.workflow_callbacks: dict[str, set[Callable]] = {}

        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._is_running = False

        logger.info("WorkflowProgressTracker initialized")

    async def start(self) -> None:
        """Start the workflow progress tracker."""
        if self._is_running:
            return

        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("WorkflowProgressTracker started")

    async def stop(self) -> None:
        """Stop the workflow progress tracker."""
        if not self._is_running:
            return

        self._is_running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        # Complete all active workflows
        for workflow_id in list(self.active_workflows.keys()):
            await self.complete_workflow(workflow_id, "tracker_shutdown")

        logger.info("WorkflowProgressTracker stopped")

    async def start_workflow(
        self,
        workflow_type: str,
        user_id: str | None = None,
        workflow_id: str | None = None,
        total_steps: int | None = None,
        estimated_duration: float | None = None,
        milestones: list[dict[str, Any]] | None = None,
    ) -> str:
        """Start tracking a new workflow."""
        if workflow_id is None:
            workflow_id = uuid4().hex

        # Create workflow progress tracker
        workflow = WorkflowProgress(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            user_id=user_id,
            total_steps=total_steps,
            status=WorkflowStatus.RUNNING,
        )

        if estimated_duration:
            workflow.estimated_completion = time.time() + estimated_duration

        # Add predefined milestones
        if milestones:
            for milestone_data in milestones:
                workflow.add_milestone(
                    name=milestone_data["name"],
                    description=milestone_data.get("description", ""),
                    stage=WorkflowStage(milestone_data.get("stage", WorkflowStage.EXECUTING)),
                    weight=milestone_data.get("weight", 1.0),
                )

        # Store workflow
        self.active_workflows[workflow_id] = workflow
        self.workflow_callbacks[workflow_id] = set()

        # Publish initial progress event
        if self.auto_publish_updates:
            await self._publish_progress_event(workflow)

        logger.info(f"Started tracking workflow: {workflow_id} ({workflow_type})")
        return workflow_id

    async def update_workflow_progress(
        self,
        workflow_id: str,
        stage: WorkflowStage | str | None = None,
        status: WorkflowStatus | str | None = None,
        current_step: str | None = None,
        completed_steps: int | None = None,
        total_steps: int | None = None,
        estimated_completion: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update workflow progress."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.warning(f"Workflow not found: {workflow_id}")
            return False

        # Convert string enums if needed
        if isinstance(stage, str):
            stage = WorkflowStage(stage)
        if isinstance(status, str):
            status = WorkflowStatus(status)

        # Update workflow progress
        workflow.update_progress(
            stage=stage,
            status=status,
            current_step=current_step,
            completed_steps=completed_steps,
            total_steps=total_steps,
            estimated_completion=estimated_completion,
            metadata=metadata,
        )

        # Publish progress event
        if self.auto_publish_updates:
            await self._publish_progress_event(workflow)

        # Call registered callbacks
        await self._call_workflow_callbacks(workflow_id, workflow)

        return True

    async def complete_milestone(
        self,
        workflow_id: str,
        milestone_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Complete a workflow milestone."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.warning(f"Workflow not found: {workflow_id}")
            return False

        success = workflow.complete_milestone(milestone_id, metadata)

        if success and self.auto_publish_updates:
            await self._publish_progress_event(workflow)
            await self._call_workflow_callbacks(workflow_id, workflow)

        return success

    async def complete_workflow(
        self,
        workflow_id: str,
        final_message: str = "Workflow completed",
        final_metadata: dict[str, Any] | None = None,
        success: bool = True,
    ) -> bool:
        """Complete a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.warning(f"Workflow not found: {workflow_id}")
            return False

        # Update final status
        workflow.status = WorkflowStatus.COMPLETED if success else WorkflowStatus.FAILED
        workflow.current_stage = WorkflowStage.COMPLETED if success else WorkflowStage.FAILED
        workflow.progress_percentage = 100.0 if success else workflow.progress_percentage

        if final_metadata:
            workflow.metadata.update(final_metadata)

        # Publish final progress event
        if self.auto_publish_updates:
            await self._publish_progress_event(workflow)

        # Call final callbacks
        await self._call_workflow_callbacks(workflow_id, workflow)

        # Clean up
        self.active_workflows.pop(workflow_id, None)
        self.workflow_callbacks.pop(workflow_id, None)

        logger.info(f"Completed workflow: {workflow_id} ({'success' if success else 'failed'})")
        return True

    async def fail_workflow(
        self,
        workflow_id: str,
        error_message: str,
        error_metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Mark a workflow as failed."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.warning(f"Workflow not found: {workflow_id}")
            return False

        workflow.error_message = error_message
        workflow.status = WorkflowStatus.FAILED
        workflow.current_stage = WorkflowStage.FAILED

        if error_metadata:
            workflow.metadata.update(error_metadata)

        return await self.complete_workflow(
            workflow_id, f"Workflow failed: {error_message}", success=False
        )

    def add_workflow_callback(
        self, workflow_id: str, callback: Callable[[WorkflowProgress], None]
    ) -> bool:
        """Add a callback for workflow updates."""
        if workflow_id not in self.active_workflows:
            return False

        self.workflow_callbacks[workflow_id].add(callback)
        return True

    def remove_workflow_callback(
        self, workflow_id: str, callback: Callable[[WorkflowProgress], None]
    ) -> bool:
        """Remove a callback for workflow updates."""
        if workflow_id not in self.workflow_callbacks:
            return False

        self.workflow_callbacks[workflow_id].discard(callback)
        return True

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
        """Get current status of a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        return workflow.to_dict() if workflow else None

    def get_active_workflows(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Get all active workflows, optionally filtered by user."""
        workflows = []

        for workflow in self.active_workflows.values():
            if user_id is None or workflow.user_id == user_id:
                workflows.append(workflow.to_dict())

        return workflows

    async def _publish_progress_event(self, workflow: WorkflowProgress) -> None:
        """Publish a workflow progress event."""
        if not self.event_publisher:
            return

        try:
            await self.event_publisher.publish_workflow_progress_event(
                workflow_id=workflow.workflow_id,
                workflow_type=workflow.workflow_type,
                status=workflow.status,
                progress_percentage=workflow.progress_percentage,
                current_step=workflow.current_step,
                total_steps=workflow.total_steps,
                completed_steps=workflow.completed_steps,
                estimated_completion=workflow.estimated_completion,
                user_id=workflow.user_id,
            )

        except Exception as e:
            logger.error(f"Failed to publish workflow progress event: {e}")

    async def _call_workflow_callbacks(self, workflow_id: str, workflow: WorkflowProgress) -> None:
        """Call all registered callbacks for a workflow."""
        callbacks = self.workflow_callbacks.get(workflow_id, set())

        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(workflow)
                else:
                    callback(workflow)
            except Exception as e:
                logger.error(f"Error in workflow callback: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up stale workflows."""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                current_time = time.time()
                stale_workflows = []

                for workflow_id, workflow in self.active_workflows.items():
                    # Check for timeout
                    if current_time - workflow.start_time > self.workflow_timeout or (
                        current_time - workflow.last_update > self.cleanup_interval * 2
                    ):
                        stale_workflows.append(workflow_id)

                # Clean up stale workflows
                for workflow_id in stale_workflows:
                    await self.fail_workflow(
                        workflow_id,
                        "Workflow timed out or became stale",
                        {"cleanup_reason": "timeout_or_stale"},
                    )

                if stale_workflows:
                    logger.info(f"Cleaned up {len(stale_workflows)} stale workflows")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """Get workflow progress tracker statistics."""
        return {
            "is_running": self._is_running,
            "active_workflows": len(self.active_workflows),
            "configuration": {
                "update_interval": self.update_interval,
                "auto_publish_updates": self.auto_publish_updates,
                "cleanup_interval": self.cleanup_interval,
                "workflow_timeout": self.workflow_timeout,
            },
            "workflows_by_type": self._get_workflows_by_type(),
            "workflows_by_user": self._get_workflows_by_user(),
            "workflows_by_stage": self._get_workflows_by_stage(),
            "workflows_by_status": self._get_workflows_by_status(),
        }

    def _get_workflows_by_type(self) -> dict[str, int]:
        """Get count of workflows by type."""
        counts = {}
        for workflow in self.active_workflows.values():
            counts[workflow.workflow_type] = counts.get(workflow.workflow_type, 0) + 1
        return counts

    def _get_workflows_by_user(self) -> dict[str, int]:
        """Get count of workflows by user."""
        counts = {}
        for workflow in self.active_workflows.values():
            user_id = workflow.user_id or "anonymous"
            counts[user_id] = counts.get(user_id, 0) + 1
        return counts

    def _get_workflows_by_stage(self) -> dict[str, int]:
        """Get count of workflows by stage."""
        counts = {}
        for workflow in self.active_workflows.values():
            counts[workflow.current_stage.value] = counts.get(workflow.current_stage.value, 0) + 1
        return counts

    def _get_workflows_by_status(self) -> dict[str, int]:
        """Get count of workflows by status."""
        counts = {}
        for workflow in self.active_workflows.values():
            counts[workflow.status.value] = counts.get(workflow.status.value, 0) + 1
        return counts
