"""
OpenHands integration stage for spec-to-production workflow.

Provides:
- OpenHandsTestGenerationStage: Workflow stage for AI-powered test generation (blocking)
- AsyncOpenHandsTestGenerationStage: Non-blocking async task submission and result collection
- Integration with circuit breaker patterns
- Retry logic with exponential backoff
- Fallback mechanisms for graceful degradation

Example:
    ```python
    from scripts.workflow.openhands_stage import OpenHandsTestGenerationStage
    from pathlib import Path

    stage = OpenHandsTestGenerationStage(
        component_path=Path("src/components/my_component"),
        config={"coverage_threshold": 80},
    )
    result = stage.execute()
    ```

Async Example:
    ```python
    from scripts.workflow.openhands_stage import AsyncOpenHandsTestGenerationStage
    import asyncio

    stage = AsyncOpenHandsTestGenerationStage(
        component_path=Path("src/components/my_component"),
        config={"coverage_threshold": 80},
    )
    # Submit tasks without blocking
    task_ids = await stage.submit_tasks()

    # Later, collect results
    results = await stage.collect_results(task_ids)
    ```
"""

from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.observability.dev_metrics import track_execution
from src.agent_orchestration.circuit_breaker import CircuitBreakerOpenError
from src.agent_orchestration.openhands_integration.workflow_integration import (
    OpenHandsTestGenerator,
)

logger = logging.getLogger(__name__)


@dataclass
class OpenHandsStageResult:
    """Result from OpenHands test generation stage."""

    stage_name: str = "openhands_test_generation"
    success: bool = False
    outputs: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    generated_tests: list[str] = field(default_factory=list)
    coverage_improvement: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "success": self.success,
            "outputs": self.outputs,
            "errors": self.errors,
            "generated_tests": self.generated_tests,
            "coverage_improvement": self.coverage_improvement,
        }


class OpenHandsTestGenerationStage:
    """Workflow stage for AI-powered test generation via OpenHands."""

    def __init__(self, component_path: Path, config: dict[str, Any] | None = None):
        """
        Initialize test generation stage.

        Args:
            component_path: Path to component directory
            config: Optional configuration overrides
        """
        self.component_path = component_path
        self.config = config or {}
        self.coverage_threshold = self.config.get("coverage_threshold", 80)
        self.timeout = self.config.get("timeout_seconds", 300)

        logger.info(
            f"Initialized OpenHandsTestGenerationStage: "
            f"component={component_path}, coverage_threshold={self.coverage_threshold}%"
        )

    @track_execution("stage_openhands_test_generation")
    def execute(self) -> OpenHandsStageResult:
        """
        Execute test generation stage.

        Returns:
            OpenHandsStageResult with generation details
        """
        result = OpenHandsStageResult()

        try:
            # Initialize generator
            try:
                generator = OpenHandsTestGenerator.from_env(use_docker=True)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenHands: {e}")
                result.errors.append(f"Failed to initialize OpenHands: {str(e)}")
                return result

            # Find Python modules in component
            modules = self._find_modules()
            if not modules:
                result.errors.append(
                    f"No Python modules found in {self.component_path}"
                )
                return result

            logger.info(f"Found {len(modules)} modules to generate tests for")

            # Generate tests for each module
            generated_count = 0
            for module_path in modules:
                try:  # noqa: PERF203
                    # Generate tests
                    gen_result = self._generate_tests_for_module(generator, module_path)

                    if gen_result["success"]:
                        generated_count += 1
                        result.generated_tests.append(str(module_path))
                        logger.info(f"✓ Generated tests for {module_path}")
                    else:
                        error = gen_result.get("error", "Unknown error")
                        result.errors.append(
                            f"Failed to generate tests for {module_path}: {error}"
                        )
                        logger.warning(f"✗ Failed to generate tests for {module_path}")

                except CircuitBreakerOpenError:
                    logger.error("Circuit breaker open - skipping remaining modules")
                    result.errors.append(
                        "Circuit breaker open - service temporarily unavailable"
                    )
                    break

                except Exception as e:
                    logger.error(f"Error generating tests for {module_path}: {e}")
                    result.errors.append(
                        f"Error generating tests for {module_path}: {str(e)}"
                    )

            # Update result
            result.success = generated_count > 0
            result.outputs = {
                "component_path": str(self.component_path),
                "modules_found": len(modules),
                "tests_generated": generated_count,
                "coverage_threshold": self.coverage_threshold,
            }

            logger.info(
                f"Test generation stage completed: "
                f"{generated_count}/{len(modules)} modules processed"
            )

            return result

        except Exception as e:
            logger.error(f"Test generation stage failed: {e}")
            result.errors.append(f"Test generation stage failed: {str(e)}")
            return result

    def _find_modules(self) -> list[Path]:
        """
        Find Python modules in component.

        Returns:
            List of module paths
        """
        modules = []
        if not self.component_path.exists():
            return modules

        for py_file in self.component_path.rglob("*.py"):
            # Skip test files and __pycache__
            if py_file.name.startswith("test_") or "__pycache__" in py_file.parts:
                continue
            modules.append(py_file)

        return sorted(modules)

    def _generate_tests_for_module(
        self, generator: OpenHandsTestGenerator, module_path: Path
    ) -> dict[str, Any]:
        """
        Generate tests for a single module.

        Args:
            generator: OpenHands test generator
            module_path: Path to module

        Returns:
            Generation result
        """

        # Run async generation in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            generator.generate_tests(
                module_path=str(module_path),
                output_path=str(self._get_test_output_path(module_path)),
                coverage_threshold=self.coverage_threshold,
                timeout=self.timeout,
            )
        )

    def _get_test_output_path(self, module_path: Path) -> Path:
        """
        Get output path for generated tests.

        Args:
            module_path: Path to module

        Returns:
            Path where tests should be saved
        """
        # Convert src/components/my_component/file.py to tests/test_my_component_file.py
        relative = module_path.relative_to(self.component_path)
        test_name = f"test_{relative.stem}.py"
        return self.component_path.parent.parent / "tests" / test_name


@dataclass
class AsyncOpenHandsStageResult:
    """Result from async OpenHands test generation stage."""

    stage_name: str = "async_openhands_test_generation"
    success: bool = False
    outputs: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    submitted_tasks: dict[str, str] = field(
        default_factory=dict
    )  # module_path -> task_id
    completed_tasks: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )  # task_id -> result
    failed_tasks: dict[str, str] = field(default_factory=dict)  # task_id -> error
    total_execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "success": self.success,
            "outputs": self.outputs,
            "errors": self.errors,
            "submitted_tasks": self.submitted_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_execution_time_ms": self.total_execution_time_ms,
        }


class AsyncOpenHandsTestGenerationStage:
    """Async workflow stage for non-blocking test generation via OpenHands."""

    def __init__(self, component_path: Path, config: dict[str, Any] | None = None):
        """
        Initialize async test generation stage.

        Args:
            component_path: Path to component directory
            config: Optional configuration overrides
        """
        self.component_path = component_path
        self.config = config or {}
        self.coverage_threshold = self.config.get("coverage_threshold", 80)
        self.timeout = self.config.get("timeout_seconds", 300)
        self.poll_interval = self.config.get("poll_interval_seconds", 2.0)
        self.generator: OpenHandsTestGenerator | None = None

        logger.info(
            f"Initialized AsyncOpenHandsTestGenerationStage: "
            f"component={component_path}, coverage_threshold={self.coverage_threshold}%"
        )

    async def submit_tasks(self) -> AsyncOpenHandsStageResult:
        """
        Submit test generation tasks asynchronously (non-blocking).

        Returns:
            AsyncOpenHandsStageResult with submitted task IDs
        """
        result = AsyncOpenHandsStageResult()
        start_time = asyncio.get_event_loop().time()

        try:
            # Initialize generator
            try:
                self.generator = OpenHandsTestGenerator.from_env(use_docker=True)
                await self.generator.start()
            except Exception as e:
                logger.warning(f"Failed to initialize OpenHands: {e}")
                result.errors.append(f"Failed to initialize OpenHands: {str(e)}")
                return result

            # Find Python modules in component
            modules = self._find_modules()
            if not modules:
                result.errors.append(
                    f"No Python modules found in {self.component_path}"
                )
                return result

            logger.info(f"Found {len(modules)} modules to generate tests for")

            # Submit tasks for each module (non-blocking)
            for module_path in modules:
                try:  # noqa: PERF203
                    task_id = await self.generator.submit_test_generation_task(
                        module_path=str(module_path),
                        output_path=str(self._get_test_output_path(module_path)),
                        coverage_threshold=self.coverage_threshold,
                    )
                    result.submitted_tasks[str(module_path)] = task_id
                    logger.info(f"✓ Submitted test generation task for {module_path}")

                except Exception as e:
                    logger.error(f"Error submitting task for {module_path}: {e}")
                    result.errors.append(
                        f"Error submitting task for {module_path}: {str(e)}"
                    )

            # Update result
            result.success = len(result.submitted_tasks) > 0
            result.outputs = {
                "component_path": str(self.component_path),
                "modules_found": len(modules),
                "tasks_submitted": len(result.submitted_tasks),
                "coverage_threshold": self.coverage_threshold,
            }

            elapsed = asyncio.get_event_loop().time() - start_time
            result.total_execution_time_ms = elapsed * 1000

            logger.info(
                f"Task submission completed: "
                f"{len(result.submitted_tasks)}/{len(modules)} tasks submitted"
            )

            return result

        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            result.errors.append(f"Task submission failed: {str(e)}")
            return result

    async def collect_results(
        self, submitted_tasks: dict[str, str]
    ) -> AsyncOpenHandsStageResult:
        """
        Collect results for previously submitted tasks.

        Args:
            submitted_tasks: Dictionary mapping module_path -> task_id

        Returns:
            AsyncOpenHandsStageResult with collected results
        """
        result = AsyncOpenHandsStageResult()
        start_time = asyncio.get_event_loop().time()

        if not self.generator:
            result.errors.append("Generator not initialized")
            return result

        try:
            # Collect results for all tasks
            for module_path, task_id in submitted_tasks.items():
                try:  # noqa: PERF203
                    task_result = await self.generator.get_test_generation_results(
                        task_id=task_id,
                        timeout=self.timeout,
                        poll_interval=self.poll_interval,
                    )

                    if task_result.get("success"):
                        result.completed_tasks[task_id] = task_result
                        logger.info(f"✓ Collected results for {module_path}")
                    else:
                        error = task_result.get("error", "Unknown error")
                        result.failed_tasks[task_id] = error
                        logger.warning(f"✗ Task failed for {module_path}: {error}")

                except Exception as e:
                    logger.error(f"Error collecting results for {module_path}: {e}")
                    result.failed_tasks[task_id] = str(e)

            # Update result
            result.success = len(result.completed_tasks) > 0
            result.outputs = {
                "component_path": str(self.component_path),
                "tasks_completed": len(result.completed_tasks),
                "tasks_failed": len(result.failed_tasks),
            }

            elapsed = asyncio.get_event_loop().time() - start_time
            result.total_execution_time_ms = elapsed * 1000

            logger.info(
                f"Result collection completed: "
                f"{len(result.completed_tasks)} completed, "
                f"{len(result.failed_tasks)} failed"
            )

            return result

        except Exception as e:
            logger.error(f"Result collection failed: {e}")
            result.errors.append(f"Result collection failed: {str(e)}")
            return result
        finally:
            # Clean up generator
            if self.generator:
                await self.generator.stop()

    def _find_modules(self) -> list[Path]:
        """
        Find Python modules in component.

        Returns:
            List of module paths
        """
        modules = []
        if not self.component_path.exists():
            return modules

        for py_file in self.component_path.rglob("*.py"):
            # Skip test files and __pycache__
            if py_file.name.startswith("test_") or "__pycache__" in py_file.parts:
                continue
            modules.append(py_file)

        return sorted(modules)

    def _get_test_output_path(self, module_path: Path) -> Path:
        """
        Get output path for generated tests.

        Args:
            module_path: Path to module

        Returns:
            Path where tests should be saved
        """
        # Convert src/components/my_component/file.py to tests/test_my_component_file.py
        relative = module_path.relative_to(self.component_path)
        test_name = f"test_{relative.stem}.py"
        return self.component_path.parent.parent / "tests" / test_name
