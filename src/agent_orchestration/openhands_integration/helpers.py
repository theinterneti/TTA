"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Helpers]]
Helper utilities for OpenHands integration.

Provides convenience functions for common test generation operations,
reducing boilerplate and improving usability.

Example:
    # Generate tests for single file
    result = await generate_tests_for_file(
        "src/module/file.py",
        coverage_threshold=70.0,
    )

    # Generate tests for package
    results = await generate_tests_for_package(
        "src/module/",
        coverage_threshold=75.0,
    )

    # Validate result
    success, issues = validate_test_result(result)
"""

import logging
from pathlib import Path

from .config import OpenHandsIntegrationConfig
from .test_generation_models import TestTaskSpecification, TestValidationResult
from .test_generation_service import UnitTestGenerationService

# Import development observability
try:
    import sys
    from pathlib import Path as PathLib

    # Add scripts/observability to path if not already there
    observability_path = (
        PathLib(__file__).resolve().parents[3] / "scripts" / "observability"
    )
    if str(observability_path) not in sys.path:
        sys.path.insert(0, str(observability_path))

    from dev_metrics import get_collector

    _OBSERVABILITY_AVAILABLE = True
except ImportError:
    _OBSERVABILITY_AVAILABLE = False
    logging.warning(
        "Development observability not available, metrics tracking disabled"
    )


# Create async-compatible track_execution decorator
def track_execution_async(name: str, metadata: dict | None = None):
    """
    Async-compatible decorator to track function execution with metrics.

    Supports both sync and async functions.
    """

    def decorator(func):
        import functools  # noqa: PLC0415
        import inspect  # noqa: PLC0415

        if not _OBSERVABILITY_AVAILABLE:
            # No-op if observability not available
            return func

        if inspect.iscoroutinefunction(func):
            # Async function
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                collector = get_collector()
                exec_id = collector.start_execution(name, metadata)
                try:
                    result = await func(*args, **kwargs)
                    collector.end_execution(exec_id, status="success")
                    return result
                except Exception as e:
                    collector.end_execution(exec_id, status="failed", error=str(e))
                    raise

            return async_wrapper

        # Sync function
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            collector = get_collector()
            exec_id = collector.start_execution(name, metadata)
            try:
                result = func(*args, **kwargs)
                collector.end_execution(exec_id, status="success")
                return result
            except Exception as e:
                collector.end_execution(exec_id, status="failed", error=str(e))
                raise

        return sync_wrapper

    return decorator


logger = logging.getLogger(__name__)


@track_execution_async(
    "openhands_generate_tests_file",
    metadata={
        "type": "test_generation",
        "scope": "file",
    },
)
async def generate_tests_for_file(
    file_path: str | Path,
    coverage_threshold: float = 70.0,
    max_iterations: int = 5,
    config: OpenHandsIntegrationConfig | None = None,
) -> TestValidationResult:
    """
    Generate tests for a single file (convenience wrapper).

    This is a simplified interface to UnitTestGenerationService that handles
    configuration loading and service creation automatically.

    Args:
        file_path: Path to file for which to generate tests
        coverage_threshold: Minimum coverage percentage (default: 70.0)
        max_iterations: Maximum retry iterations (default: 5)
        config: Optional OpenHandsIntegrationConfig (loads from env if None)

    Returns:
        TestValidationResult with validation results

    Raises:
        ValueError: If file_path doesn't exist or is not a Python file
        FileNotFoundError: If file_path doesn't exist

    Example:
        >>> result = await generate_tests_for_file(
        ...     "src/agent_orchestration/tools/callable_registry.py",
        ...     coverage_threshold=70.0,
        ... )
        >>> print(f"Coverage: {result.coverage_percentage}%")
        Coverage: 85.0%
    """
    # Validate file path
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if file_path.suffix != ".py":
        raise ValueError(f"File is not a Python file: {file_path}")

    # Load configuration if not provided
    if config is None:
        config = OpenHandsIntegrationConfig.from_env()

    # Create service (pass full config to preserve Docker runtime settings)
    service = UnitTestGenerationService(config)

    # Create specification
    spec = TestTaskSpecification(
        target_file=file_path,
        coverage_threshold=coverage_threshold,
    )

    # Generate tests
    logger.info(f"Generating tests for {file_path} (threshold: {coverage_threshold}%)")

    try:
        result = await service.generate_tests(spec, max_iterations=max_iterations)

        logger.info(
            f"Test generation completed: "
            f"syntax_valid={result.syntax_valid}, "
            f"tests_pass={result.tests_pass}, "
            f"coverage={result.coverage_percentage}%"
        )

        # Track additional metrics if observability available
        if _OBSERVABILITY_AVAILABLE:
            try:
                collector = get_collector()
                # Get the most recent metric for this operation
                recent_metrics = collector.get_recent_metrics(
                    name="openhands_generate_tests_file", limit=1
                )
                if recent_metrics:
                    # Update the metric with additional metadata
                    metric = recent_metrics[0]
                    metric["metadata"].update(
                        {
                            "target_file": str(file_path),
                            "coverage_threshold": coverage_threshold,
                            "coverage_achieved": result.coverage_percentage,
                            "syntax_valid": result.syntax_valid,
                            "tests_pass": result.tests_pass,
                            "max_iterations": max_iterations,
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to update observability metrics: {e}")

        return result
    finally:
        # Clean up OpenHands client resources
        await service.client.cleanup()


@track_execution_async(
    "openhands_generate_tests_package",
    metadata={
        "type": "test_generation",
        "scope": "package",
    },
)
async def generate_tests_for_package(
    package_path: str | Path,
    coverage_threshold: float = 70.0,
    max_iterations: int = 5,
    config: OpenHandsIntegrationConfig | None = None,
) -> dict[Path, TestValidationResult]:
    """
    Generate tests for all Python files in a package (convenience wrapper).

    This function discovers all Python files in the package directory and
    generates tests for each file sequentially.

    Args:
        package_path: Path to package directory
        coverage_threshold: Minimum coverage percentage (default: 70.0)
        max_iterations: Maximum retry iterations per file (default: 5)
        config: Optional OpenHandsIntegrationConfig (loads from env if None)

    Returns:
        Dictionary mapping file paths to validation results

    Raises:
        ValueError: If package_path is not a directory
        FileNotFoundError: If package_path doesn't exist

    Example:
        >>> results = await generate_tests_for_package(
        ...     "src/agent_orchestration/tools/",
        ...     coverage_threshold=75.0,
        ... )
        >>> for file, result in results.items():
        ...     print(f"{file}: {result.coverage_percentage}%")
        src/agent_orchestration/tools/callable_registry.py: 85.0%
        src/agent_orchestration/tools/coordinator.py: 78.0%
    """
    # Validate package path
    package_path = Path(package_path)
    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")

    if not package_path.is_dir():
        raise ValueError(f"Path is not a directory: {package_path}")

    # Load configuration if not provided
    if config is None:
        config = OpenHandsIntegrationConfig.from_env()

    # Discover Python files
    python_files = list(package_path.glob("*.py"))
    python_files = [f for f in python_files if f.name != "__init__.py"]

    if not python_files:
        logger.warning(f"No Python files found in {package_path}")
        return {}

    logger.info(
        f"Generating tests for {len(python_files)} files in {package_path} "
        f"(threshold: {coverage_threshold}%)"
    )

    # Generate tests for each file
    results: dict[Path, TestValidationResult] = {}
    for file_path in python_files:
        try:
            result = await generate_tests_for_file(
                file_path,
                coverage_threshold=coverage_threshold,
                max_iterations=max_iterations,
                config=config,
            )
            results[file_path] = result
        except Exception as e:
            logger.error(f"Failed to generate tests for {file_path}: {e}")
            # Continue with other files even if one fails
            continue

    # Log summary
    successful = sum(1 for r in results.values() if r.syntax_valid and r.tests_pass)
    logger.info(
        f"Package test generation completed: "
        f"{successful}/{len(python_files)} files successful"
    )

    # Track additional metrics if observability available
    if _OBSERVABILITY_AVAILABLE:
        try:
            collector = get_collector()
            # Get the most recent metric for this operation
            recent_metrics = collector.get_recent_metrics(
                name="openhands_generate_tests_package", limit=1
            )
            if recent_metrics:
                # Calculate average coverage
                avg_coverage = (
                    sum(r.coverage_percentage for r in results.values()) / len(results)
                    if results
                    else 0.0
                )

                # Update the metric with additional metadata
                metric = recent_metrics[0]
                metric["metadata"].update(
                    {
                        "package_path": str(package_path),
                        "coverage_threshold": coverage_threshold,
                        "total_files": len(python_files),
                        "successful_files": successful,
                        "failed_files": len(python_files) - successful,
                        "success_rate": successful / len(python_files)
                        if python_files
                        else 0.0,
                        "avg_coverage": avg_coverage,
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to update observability metrics: {e}")

    return results


@track_execution_async(
    "openhands_validate_test_result",
    metadata={
        "type": "validation",
        "scope": "result",
    },
)
def validate_test_result(
    result: TestValidationResult,
    coverage_threshold: float = 70.0,
) -> tuple[bool, list[str]]:
    """
    Validate test generation result against criteria.

    This function provides a simplified interface for validating test generation
    results, returning a boolean success flag and list of issues.

    Args:
        result: TestValidationResult to validate
        coverage_threshold: Minimum coverage percentage (default: 70.0)

    Returns:
        Tuple of (success: bool, issues: list[str])
        - success: True if all validation checks passed
        - issues: List of validation issues (empty if success=True)

    Example:
        >>> result = await generate_tests_for_file("src/module/file.py")
        >>> success, issues = validate_test_result(result, coverage_threshold=70.0)
        >>> if success:
        ...     print("✓ All validation checks passed")
        ... else:
        ...     print(f"✗ Issues: {issues}")
        ✗ Issues: ['Coverage 65.0% below threshold 70.0%']
    """
    issues: list[str] = []

    # Check syntax validity
    if not result.syntax_valid:
        issues.append("Syntax errors in generated tests")

    # Check conventions
    if not result.conventions_followed:
        issues.append("Tests don't follow TTA conventions")

    # Check test execution
    if not result.tests_pass:
        issues.append("Generated tests don't pass")

    # Check coverage threshold
    if result.coverage_percentage < coverage_threshold:
        issues.append(
            f"Coverage {result.coverage_percentage}% below threshold {coverage_threshold}%"
        )

    # Add any issues from result
    if result.issues:
        issues.extend(result.issues)

    success = len(issues) == 0

    if success:
        logger.info(
            f"Validation successful: "
            f"coverage={result.coverage_percentage}%, "
            f"quality_score={result.quality_score}"
        )
    else:
        logger.warning(f"Validation failed: {len(issues)} issues found")

    # Track additional metrics if observability available
    if _OBSERVABILITY_AVAILABLE:
        try:
            collector = get_collector()
            # Get the most recent metric for this operation
            recent_metrics = collector.get_recent_metrics(
                name="openhands_validate_test_result", limit=1
            )
            if recent_metrics:
                # Update the metric with additional metadata
                metric = recent_metrics[0]
                metric["metadata"].update(
                    {
                        "coverage_threshold": coverage_threshold,
                        "coverage_achieved": result.coverage_percentage,
                        "validation_success": success,
                        "issue_count": len(issues),
                        "syntax_valid": result.syntax_valid,
                        "tests_pass": result.tests_pass,
                        "quality_score": result.quality_score,
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to update observability metrics: {e}")

    return success, issues


__all__ = [
    "generate_tests_for_file",
    "generate_tests_for_package",
    "validate_test_result",
]
