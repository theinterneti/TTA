"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Execution_engine]]
Execution engine for OpenHands task orchestration.

Provides:
- ExecutionEngine: Main orchestration engine
- Coordinates task queue, model selection, execution, validation, and metrics
- Handles retries, error recovery, and fallback strategies
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .adapter import OpenHandsAdapter
from .client import OpenHandsClient
from .config import OpenHandsConfig
from .metrics_collector import ExecutionMetrics, MetricsCollector
from .model_rotation import ModelRotationManager
from .model_selector import ModelSelector, TaskRequirements
from .result_validator import ResultValidator
from .task_queue import QueuedTask, TaskQueue

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Main execution engine for OpenHands task orchestration."""

    def __init__(
        self,
        config: OpenHandsConfig,
        queue_size: int = 1000,
        max_concurrent_tasks: int = 5,
    ):
        """Initialize execution engine.

        Args:
            config: OpenHands configuration
            queue_size: Task queue size
            max_concurrent_tasks: Maximum concurrent tasks
        """
        self.config = config
        self.queue = TaskQueue(max_size=queue_size)
        self.model_selector = ModelSelector()
        self.model_rotation = ModelRotationManager()
        self.result_validator = ResultValidator()
        self.metrics = MetricsCollector()
        self.max_concurrent_tasks = max_concurrent_tasks
        self._running = False
        self._workers: list[asyncio.Task] = []

        # Create OpenHands client and adapter
        self.client = OpenHandsClient(config)
        self.adapter = OpenHandsAdapter(client=self.client)

    async def start(self) -> None:
        """Start execution engine."""
        if self._running:
            logger.warning("Execution engine already running")
            return

        self._running = True
        logger.info(
            f"Starting execution engine with {self.max_concurrent_tasks} workers"
        )

        # Start worker tasks
        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)

    async def stop(self) -> None:
        """Stop execution engine."""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping execution engine")

        # Cancel all workers
        for worker in self._workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def submit_task(self, task: QueuedTask) -> str:
        """Submit task for execution.

        Args:
            task: Task to execute

        Returns:
            Task ID
        """
        task_id = await self.queue.enqueue(task)
        logger.info(f"Task {task_id} submitted ({task.task_type})")
        return task_id

    async def get_task_status(self, task_id: str) -> QueuedTask | None:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        return await self.queue.get_task(task_id)

    async def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics.

        Returns:
            Queue statistics
        """
        return await self.queue.get_stats()

    async def _worker(self, worker_id: int) -> None:
        """Worker task for processing queue.

        Args:
            worker_id: Worker ID
        """
        logger.info(f"Worker {worker_id} started")

        while self._running:
            try:
                # Get next task
                task = await self.queue.dequeue()
                if not task:
                    await asyncio.sleep(0.1)
                    continue

                # Execute task
                await self._execute_task(task)

            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_id} stopped")

    async def _execute_task(self, task: QueuedTask) -> None:
        """Execute a single task.

        Args:
            task: Task to execute
        """
        logger.info(f"Executing task {task.task_id} ({task.task_type})")

        # Create execution metrics
        metrics = ExecutionMetrics(
            task_id=task.task_id,
            model_id="",
            task_type=task.task_type,
        )

        try:
            # Select model
            from .model_selector import TaskCategory

            category = task.metadata.get("category", TaskCategory.CODE_GENERATION)
            if isinstance(category, str):
                try:
                    category = TaskCategory[category.upper()]
                except KeyError:
                    category = TaskCategory.CODE_GENERATION

            requirements = TaskRequirements(
                category=category,
                complexity=task.metadata.get("complexity", "moderate"),
                quality_threshold=task.metadata.get("quality_threshold", 0.7),
            )

            model = self.model_selector.select_model(requirements)
            if not model:
                raise RuntimeError(f"No suitable model found for {task.task_type}")

            metrics.model_id = model.model_id

            # Execute task with adapter
            result = await self.adapter.execute_development_task(task.description)

            # Validate result
            validation = self.result_validator.validate(result)

            if not validation.passed:
                # Retry if validation failed
                if task.retry_count < task.max_retries:
                    logger.warning(
                        f"Task {task.task_id} validation failed, retrying "
                        f"({task.retry_count + 1}/{task.max_retries})"
                    )
                    task.retry_count += 1
                    await self.queue.enqueue(task)
                    return

                raise RuntimeError(f"Validation failed: {validation.errors}")

            # Mark as completed
            metrics.success = True
            metrics.quality_score = validation.score
            metrics.validation_passed = validation.passed
            await self.queue.mark_completed(task.task_id, result)

            logger.info(f"Task {task.task_id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            metrics.success = False
            metrics.error = str(e)
            await self.queue.mark_failed(task.task_id, str(e))

        finally:
            # Record metrics
            self.metrics.record_execution(metrics)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get metrics summary.

        Returns:
            Metrics summary
        """
        return self.metrics.get_summary()
