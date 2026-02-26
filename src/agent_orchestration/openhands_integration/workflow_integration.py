"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Workflow_integration]]
OpenHands integration with TTA agentic workflow.

Provides:
- OpenHandsWorkflowStage: Workflow stage for test generation via OpenHands
- OpenHandsTestGenerator: High-level test generation interface
- Circuit breaker patterns for external calls
- Retry logic with exponential backoff
- Fallback mechanisms for graceful degradation

Example:
    ```python
    from src.agent_orchestration.openhands_integration.workflow_integration import (
        OpenHandsTestGenerator,
    )
    from pathlib import Path

    generator = OpenHandsTestGenerator.from_env()
    result = await generator.generate_tests(
        module_path="src/components/my_component.py",
        output_path="tests/test_my_component.py",
        coverage_threshold=80,
    )
    ```
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from src.agent_orchestration.circuit_breaker import (
    CircuitBreakerOpenError,
)

from .config import OpenHandsIntegrationConfig
from .execution_engine import ExecutionEngine
from .result_validator import ResultValidator
from .task_queue import QueuedTask, TaskPriority

logger = logging.getLogger(__name__)


class OpenHandsTestGenerator:
    """High-level interface for test generation via OpenHands."""

    def __init__(
        self,
        config: OpenHandsIntegrationConfig,
        use_docker: bool = True,
        circuit_breaker_name: str = "openhands_test_generation",
    ):
        """
        Initialize test generator.

        Args:
            config: OpenHands integration configuration
            use_docker: Whether to use Docker runtime (recommended)
            circuit_breaker_name: Name for circuit breaker
        """
        self.config = config
        self.use_docker = use_docker
        self.engine = ExecutionEngine(config.to_client_config(), max_concurrent_tasks=3)
        self.validator = ResultValidator()

        # Circuit breaker will be initialized lazily when needed
        # (requires Redis connection which may not be available in all contexts)
        self.circuit_breaker = None
        self.circuit_breaker_name = circuit_breaker_name

        logger.info(
            f"Initialized OpenHandsTestGenerator: "
            f"docker={use_docker}, model={config.model_preset}"
        )

    @classmethod
    def from_env(cls, use_docker: bool = True) -> OpenHandsTestGenerator:
        """
        Create generator from environment configuration.

        Args:
            use_docker: Whether to use Docker runtime

        Returns:
            OpenHandsTestGenerator instance
        """
        config = OpenHandsIntegrationConfig.from_env()
        return cls(config, use_docker=use_docker)

    async def submit_test_generation_task(
        self,
        module_path: str,
        output_path: str | None = None,
        coverage_threshold: int = 80,
    ) -> str:
        """
        Submit test generation task asynchronously (non-blocking).

        Submits a test generation task and returns immediately with task_id.
        Use get_test_generation_results() to retrieve results later.

        Args:
            module_path: Path to module to generate tests for
            output_path: Path where generated tests should be saved
            coverage_threshold: Target coverage percentage

        Returns:
            Task ID for later result retrieval

        Raises:
            RuntimeError: If task submission fails
        """
        # Create task description
        task_description = f"""
Generate comprehensive unit tests for the Python module at {module_path}.

Requirements:
- Target coverage: {coverage_threshold}%
- Use pytest framework
- Include edge cases and error conditions
- Add docstrings to test functions
- Follow existing test patterns in the codebase
"""

        if output_path:
            task_description += f"\nSave generated tests to: {output_path}"

        # Create queued task
        task = QueuedTask(
            task_type="unit_test",
            description=task_description,
            target_file=Path(module_path),
            priority=TaskPriority.HIGH,
            metadata={
                "coverage_threshold": coverage_threshold,
                "output_path": output_path,
                "module_path": module_path,
            },
        )

        # Submit task and return immediately
        task_id = await self.engine.submit_task(task)
        logger.info(f"Submitted test generation task: {task_id} for {module_path}")
        return task_id

    async def get_test_generation_results(
        self,
        task_id: str,
        timeout: float | None = None,
        poll_interval: float = 2.0,
    ) -> dict[str, Any]:
        """
        Retrieve results for previously submitted test generation task.

        Polls task status until completion or timeout.

        Args:
            task_id: Task ID from submit_test_generation_task()
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            Dictionary with generation results

        Raises:
            TimeoutError: If task doesn't complete within timeout
            RuntimeError: If task fails or not found
        """
        timeout = timeout or self.config.default_timeout_seconds
        start_time = asyncio.get_event_loop().time()

        while True:
            task_status = await self.engine.get_task_status(task_id)

            if not task_status:
                raise RuntimeError(f"Task {task_id} not found")

            # Check if completed
            if task_status.status == "completed":
                result = task_status.result or {}
                logger.info(f"Test generation completed: {task_id}")
                return {
                    "success": True,
                    "task_id": task_id,
                    "result": result,
                    "module_path": task_status.metadata.get("module_path"),
                    "output_path": task_status.metadata.get("output_path"),
                }

            # Check if failed
            if task_status.status == "failed":
                error = task_status.error or "Unknown error"
                logger.error(f"Test generation failed: {error}")
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": error,
                    "module_path": task_status.metadata.get("module_path"),
                }

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                logger.error(f"Test generation timeout after {elapsed:.1f}s")
                raise TimeoutError(f"Task {task_id} exceeded timeout of {timeout}s")

            # Wait before checking again
            await asyncio.sleep(poll_interval)

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        Get current status of a submitted task (non-blocking).

        Returns immediately with current task status without waiting.

        Args:
            task_id: Task ID from submit_test_generation_task()

        Returns:
            Dictionary with task status and metadata

        Raises:
            RuntimeError: If task not found
        """
        task = await self.engine.get_task_status(task_id)

        if not task:
            raise RuntimeError(f"Task {task_id} not found")

        return {
            "task_id": task_id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "error": task.error,
            "retry_count": task.retry_count,
            "metadata": task.metadata,
        }

    async def generate_tests(
        self,
        module_path: str,
        output_path: str | None = None,
        coverage_threshold: int = 80,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Generate tests for a module using OpenHands (blocking for backward compatibility).

        This method maintains backward compatibility by blocking until tests are generated.
        For non-blocking execution, use submit_test_generation_task() and
        get_test_generation_results() instead.

        Args:
            module_path: Path to module to generate tests for
            output_path: Path where generated tests should be saved
            coverage_threshold: Target coverage percentage
            timeout: Task timeout in seconds

        Returns:
            Dictionary with generation results

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            TimeoutError: If task exceeds timeout
        """
        try:
            # Execute test generation (circuit breaker is lazily initialized)
            return await self._execute_test_generation(
                module_path=module_path,
                output_path=output_path,
                coverage_threshold=coverage_threshold,
                timeout=timeout,
            )

        except CircuitBreakerOpenError:
            logger.error("Circuit breaker open for test generation")
            return {
                "success": False,
                "error": "Circuit breaker open - service temporarily unavailable",
                "fallback": True,
            }

    async def _execute_test_generation(
        self,
        module_path: str,
        output_path: str | None = None,
        coverage_threshold: int = 80,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Execute test generation task.

        Args:
            module_path: Path to module
            output_path: Output path for generated tests
            coverage_threshold: Target coverage
            timeout: Task timeout

        Returns:
            Generation results
        """
        # Create task description
        task_description = f"""
Generate comprehensive unit tests for the Python module at {module_path}.

Requirements:
- Target coverage: {coverage_threshold}%
- Use pytest framework
- Include edge cases and error conditions
- Add docstrings to test functions
- Follow existing test patterns in the codebase
"""

        if output_path:
            task_description += f"\nSave generated tests to: {output_path}"

        # Create queued task
        task = QueuedTask(
            task_type="unit_test",
            description=task_description,
            target_file=Path(module_path),
            priority=TaskPriority.HIGH,
            metadata={
                "coverage_threshold": coverage_threshold,
                "output_path": output_path,
            },
        )

        # Submit task
        task_id = await self.engine.submit_task(task)
        logger.info(f"Submitted test generation task: {task_id}")

        # Wait for completion
        timeout = timeout or self.config.default_timeout_seconds
        start_time = asyncio.get_event_loop().time()

        while True:
            # Check task status
            task_status = await self.get_task_status(task_id)

            if task_status.get("completed"):
                result = task_status.get("result", {})
                logger.info(f"Test generation completed: {task_id}")
                return {
                    "success": True,
                    "task_id": task_id,
                    "result": result,
                    "module_path": module_path,
                    "output_path": output_path,
                }

            if task_status.get("error"):
                error = task_status.get("error")
                logger.error(f"Test generation failed: {error}")
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": error,
                    "module_path": module_path,
                }

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                logger.error(f"Test generation timeout after {elapsed:.1f}s")
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": f"Timeout after {elapsed:.1f}s",
                    "module_path": module_path,
                }

            # Wait before checking again
            await asyncio.sleep(2)

    async def start(self) -> None:
        """Start the execution engine."""
        await self.engine.start()
        logger.info("OpenHandsTestGenerator started")

    async def stop(self) -> None:
        """Stop the execution engine."""
        await self.engine.stop()
        logger.info("OpenHandsTestGenerator stopped")

    async def __aenter__(self) -> OpenHandsTestGenerator:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
