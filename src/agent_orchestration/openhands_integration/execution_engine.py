"""
Execution engine for OpenHands task orchestration.

Provides:
- ExecutionEngine: Main orchestration engine
- Coordinates task queue, model selection, execution, validation, and metrics
- Handles retries, error recovery, and fallback strategies
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

from .adapter import OpenHandsAdapter
from .config import OpenHandsConfig, OpenHandsIntegrationConfig
from .docker_client import DockerOpenHandsClient
from .metrics_collector import ExecutionMetrics, MetricsCollector
from .model_rotation import ModelRotationManager
from .model_selector import ModelSelector, TaskRequirements
from .optimized_client import OptimizedOpenHandsClient
from .result_validator import ResultValidator
from .task_queue import QueuedTask, TaskQueue

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Main execution engine for OpenHands task orchestration."""

    def __init__(
        self,
        config: OpenHandsConfig | OpenHandsIntegrationConfig,
        queue_size: int = 1000,
        max_concurrent_tasks: int = 5,
        state_file: str = "engine_state.json",
        persistence_file: str = "task_queue.json",
    ):
        """Initialize execution engine.

        Args:
            config: OpenHands configuration (OpenHandsConfig or OpenHandsIntegrationConfig)
            queue_size: Task queue size
            max_concurrent_tasks: Maximum concurrent tasks
            state_file: File to write engine state to (for monitoring)
            persistence_file: File to persist tasks to
        """
        # Convert OpenHandsIntegrationConfig to OpenHandsConfig if needed
        if isinstance(config, OpenHandsIntegrationConfig):
            self.config = config.to_client_config()
            self._integration_config = config
        else:
            self.config = config
            self._integration_config = None
        self.queue = TaskQueue(max_size=queue_size, persistence_file=persistence_file)
        self.model_selector = ModelSelector()
        self.model_rotation = ModelRotationManager()
        self.result_validator = ResultValidator()
        self.metrics = MetricsCollector()
        self.max_concurrent_tasks = max_concurrent_tasks
        self._running = False
        self._workers: list[asyncio.Task] = []
        self.state_file = state_file
        self._state_export_task: asyncio.Task | None = None
        self._persistence_task: asyncio.Task | None = None

        # Select client based on configuration
        use_docker = False
        if self._integration_config and self._integration_config.use_docker_runtime:
            use_docker = True

        if use_docker:
            logger.info("Using Docker runtime for full tool access")
            self.client = DockerOpenHandsClient(self.config)
            # Docker runtime doesn't need mock fallback (has full tool access)
            self.adapter = OpenHandsAdapter(client=self.client, fallback_to_mock=False)
        else:
            logger.info("Using SDK mode with optimized client caching")
            self.client = OptimizedOpenHandsClient(self.config)
            # SDK mode needs mock fallback (limited to 2 tools: finish, think)
            self.adapter = OpenHandsAdapter(client=self.client, fallback_to_mock=True)

        # Task batching for improved throughput
        self._task_batch: dict[str, list[QueuedTask]] = {}
        self._batch_size = 3  # Process 3 similar tasks before switching types

        # Progress tracking
        self._progress_task: asyncio.Task | None = None
        self._last_progress_report = 0
        self._progress_interval = 300  # Report progress every 5 minutes

    async def start(self) -> None:
        """Start execution engine."""
        if self._running:
            logger.warning("Execution engine already running")
            return

        self._running = True
        logger.info(
            f"Starting execution engine with {self.max_concurrent_tasks} workers"
        )

        # Load persisted tasks
        await self.queue.load_from_file()

        # Start worker tasks
        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)

        # Start state export task
        self._state_export_task = asyncio.create_task(self._export_state_periodically())

        # Start persistence task
        self._persistence_task = asyncio.create_task(self._persist_queue_periodically())

        # Start progress reporting task
        self._progress_task = asyncio.create_task(self._report_progress_periodically())

    async def stop(self) -> None:
        """Stop execution engine."""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping execution engine")

        # Cancel state export task
        if self._state_export_task:
            self._state_export_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._state_export_task

        # Cancel persistence task
        if self._persistence_task:
            self._persistence_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._persistence_task

        # Cancel progress reporting task
        if self._progress_task:
            self._progress_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._progress_task

        # Cancel all workers
        for worker in self._workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        # Final save
        await self.queue.save_to_file()

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
        """Execute a single task with detailed logging and progress tracking.

        Args:
            task: Task to execute
        """

        start_time = time.time()

        logger.info(
            f"[TASK START] {task.task_id[:8]}... | Type: {task.task_type} | "
            f"Desc: {task.description[:60]}..."
        )

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
            logger.debug(f"Selected model: {model.model_id}")

            # Execute task with adapter
            logger.debug("Executing task with adapter...")
            result = await self.adapter.execute_development_task(task.description)
            exec_time = time.time() - start_time
            logger.debug(f"Task execution completed in {exec_time:.2f}s")

            # Validate result
            logger.debug("Validating result...")
            validation = self.result_validator.validate(result)

            if not validation.passed:
                # Retry if validation failed
                if task.retry_count < task.max_retries:
                    logger.warning(
                        f"[VALIDATION FAILED] {task.task_id[:8]}... | "
                        f"Retry {task.retry_count + 1}/{task.max_retries}"
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

            total_time = time.time() - start_time
            logger.info(
                f"[TASK COMPLETE] {task.task_id[:8]}... | "
                f"Type: {task.task_type} | Time: {total_time:.2f}s | "
                f"Quality: {validation.score:.2f}"
            )

        except Exception as e:
            # Check if this is a rate limit error (429)
            error_str = str(e)
            is_rate_limit = "429" in error_str or "rate" in error_str.lower()

            if is_rate_limit and task.retry_count < task.max_retries:
                logger.warning(
                    f"[RATE LIMITED] {task.task_id[:8]}... | "
                    f"Retry {task.retry_count + 1}/{task.max_retries}"
                )
                task.retry_count += 1
                # Re-queue task for retry (will use different model on next attempt)
                await self.queue.enqueue(task)
                return

            total_time = time.time() - start_time
            logger.error(
                f"[TASK FAILED] {task.task_id[:8]}... | "
                f"Type: {task.task_type} | Time: {total_time:.2f}s | "
                f"Error: {str(e)[:80]}"
            )
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

    async def _export_state_periodically(self) -> None:
        """Periodically export engine state to file for monitoring."""
        while self._running:
            try:
                await asyncio.sleep(5)  # Export every 5 seconds
                await self._export_state()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error exporting state: {e}")

    async def _export_state(self) -> None:
        """Export current engine state to file."""
        try:
            stats = await self.get_queue_stats()
            metrics = self.get_metrics_summary()

            state = {
                "timestamp": json.dumps(
                    __import__("datetime")
                    .datetime.now(__import__("datetime").timezone.utc)
                    .isoformat()
                ),
                "queue_stats": stats,
                "metrics": metrics,
                "running": self._running,
            }

            # Write to file atomically
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

            # Atomic rename
            import os

            os.replace(temp_file, self.state_file)
            logger.debug(f"Engine state exported to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to export state: {e}")

    async def _persist_queue_periodically(self) -> None:
        """Periodically persist task queue to file."""
        while self._running:
            try:
                await asyncio.sleep(10)  # Persist every 10 seconds
                await self.queue.save_to_file()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error persisting queue: {e}")

    async def _report_progress_periodically(self) -> None:
        """Periodically report execution progress."""

        start_time = time.time()
        last_completed = 0

        while self._running:
            try:
                await asyncio.sleep(self._progress_interval)  # Report every 5 minutes

                stats = await self.get_queue_stats()
                elapsed = time.time() - start_time
                completed = stats.get("completed", 0)
                total = stats.get("total", 0)

                # Calculate throughput
                tasks_completed_this_period = completed - last_completed
                throughput = tasks_completed_this_period / self._progress_interval

                # Estimate remaining time
                remaining_tasks = total - completed
                if throughput > 0:
                    estimated_remaining = remaining_tasks / throughput
                else:
                    estimated_remaining = float("inf")

                logger.info(
                    f"[PROGRESS REPORT] Completed: {completed}/{total} ({100 * completed / total:.1f}%) | "
                    f"Throughput: {throughput:.2f} tasks/min | "
                    f"Elapsed: {elapsed / 60:.1f}min | "
                    f"Est. Remaining: {estimated_remaining / 60:.1f}min"
                )

                last_completed = completed

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error reporting progress: {e}")
