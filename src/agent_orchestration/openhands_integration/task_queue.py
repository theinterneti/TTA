"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Task_queue]]
Task queue for OpenHands integration.

Provides:
- TaskQueue: FIFO queue for managing OpenHands tasks
- TaskStatus: Enumeration of task states
- QueuedTask: Task wrapper with metadata
- Priority-based task ordering
- Persistence to Redis (optional)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(StrEnum):
    """Task execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    """Task priority levels."""

    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class QueuedTask:
    """Task wrapper with metadata."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""  # "unit_test", "refactor", "document", etc.
    description: str = ""
    target_file: Path | None = None
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None
    retry_count: int = 0
    max_retries: int = 3

    def __lt__(self, other: QueuedTask) -> bool:
        """Compare tasks by priority (for heap queue)."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "target_file": str(self.target_file) if self.target_file else None,
            "priority": self.priority.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "metadata": self.metadata,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class TaskQueue:
    """FIFO task queue with priority support."""

    def __init__(self, max_size: int = 1000):
        """Initialize task queue.

        Args:
            max_size: Maximum queue size
        """
        self.max_size = max_size
        self._queue: asyncio.PriorityQueue[tuple[int, QueuedTask]] = (
            asyncio.PriorityQueue(maxsize=max_size)
        )
        self._tasks: dict[str, QueuedTask] = {}
        self._lock = asyncio.Lock()

    async def enqueue(self, task: QueuedTask) -> str:
        """Add task to queue.

        Args:
            task: Task to enqueue

        Returns:
            Task ID

        Raises:
            RuntimeError: If queue is full
        """
        async with self._lock:
            if self._queue.full():
                raise RuntimeError("Task queue is full")

            task.status = TaskStatus.QUEUED
            self._tasks[task.task_id] = task
            await self._queue.put((task.priority.value, task))
            logger.info(
                f"Task {task.task_id} enqueued (priority: {task.priority.name})"
            )
            return task.task_id

    async def dequeue(self) -> QueuedTask | None:
        """Get next task from queue.

        Returns:
            Next task or None if queue is empty
        """
        try:
            _, task = self._queue.get_nowait()
            async with self._lock:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now(UTC)
            logger.info(f"Task {task.task_id} dequeued")
            return task
        except asyncio.QueueEmpty:
            return None

    async def mark_completed(
        self, task_id: str, result: dict[str, Any]
    ) -> QueuedTask | None:
        """Mark task as completed.

        Args:
            task_id: Task ID
            result: Task result

        Returns:
            Updated task or None if not found
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(UTC)
                task.result = result
                logger.info(f"Task {task_id} completed")
            return task

    async def mark_failed(self, task_id: str, error: str) -> QueuedTask | None:
        """Mark task as failed.

        Args:
            task_id: Task ID
            error: Error message

        Returns:
            Updated task or None if not found
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = error
                task.retry_count += 1
                logger.error(f"Task {task_id} failed: {error}")
            return task

    async def get_task(self, task_id: str) -> QueuedTask | None:
        """Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        async with self._lock:
            return self._tasks.get(task_id)

    async def get_stats(self) -> dict[str, Any]:
        """Get queue statistics.

        Returns:
            Queue statistics
        """
        async with self._lock:
            total = len(self._tasks)
            pending = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.PENDING
            )
            queued = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.QUEUED
            )
            running = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING
            )
            completed = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED
            )
            failed = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.FAILED
            )

            return {
                "total_tasks": total,
                "pending": pending,
                "queued": queued,
                "running": running,
                "completed": completed,
                "failed": failed,
                "queue_size": self._queue.qsize(),
                "max_size": self.max_size,
            }
