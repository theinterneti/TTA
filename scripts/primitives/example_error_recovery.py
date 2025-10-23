#!/usr/bin/env python3
"""
Example usage of the Error Recovery Framework.

This demonstrates how to use retry decorators, error classification,
and fallback strategies in development scripts.
"""

import subprocess
import logging
from pathlib import Path

from error_recovery import (
    with_retry,
    with_retry_async,
    RetryConfig,
    CircuitBreaker,
    ErrorCategory,
    classify_error
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Example 1: Simple retry with defaults
@with_retry()
def run_tests_simple():
    """Run tests with default retry configuration."""
    logger.info("Running tests...")
    result = subprocess.run(
        ["uvx", "pytest", "tests/", "-v"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


# Example 2: Custom retry configuration
@with_retry(RetryConfig(max_retries=5, base_delay=2.0, max_delay=30.0))
def install_dependencies():
    """Install dependencies with custom retry settings."""
    logger.info("Installing dependencies...")
    result = subprocess.run(
        ["uv", "sync"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


# Example 3: Retry with fallback
def fallback_cached_dependencies():
    """Fallback to cached dependencies if installation fails."""
    logger.info("Using cached dependencies...")
    # In a real scenario, this would use a local cache
    return "Using cached dependencies"


@with_retry(
    RetryConfig(max_retries=3),
    fallback=fallback_cached_dependencies
)
def ensure_dependencies():
    """Ensure dependencies are installed, with fallback to cache."""
    return install_dependencies()


# Example 4: Async retry
@with_retry_async(RetryConfig(max_retries=3, base_delay=1.0))
async def fetch_remote_data():
    """Fetch data from remote API with retry."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            response.raise_for_status()
            return await response.json()


# Example 5: Circuit breaker
def create_build_circuit_breaker():
    """Create a circuit breaker for build operations."""
    return CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60.0,
        expected_exception=subprocess.CalledProcessError
    )


def run_build_with_circuit_breaker():
    """Run build with circuit breaker protection."""
    circuit_breaker = create_build_circuit_breaker()

    def build():
        logger.info("Running build...")
        result = subprocess.run(
            ["uv", "run", "python", "-m", "build"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    try:
        return circuit_breaker.call(build)
    except Exception as e:
        logger.error(f"Build failed: {e}")
        logger.info(f"Circuit breaker state: {circuit_breaker.state}")
        raise


# Example 6: Error classification
def demonstrate_error_classification():
    """Demonstrate error classification."""
    test_errors = [
        ConnectionError("Connection timeout"),
        Exception("Rate limit exceeded"),
        MemoryError("Out of memory"),
        Exception("Service temporarily unavailable"),
        ValueError("Invalid input"),
    ]

    logger.info("\n=== Error Classification Demo ===")
    for error in test_errors:
        category, severity = classify_error(error)
        logger.info(
            f"Error: {error.__class__.__name__}: {error}\n"
            f"  Category: {category.value}\n"
            f"  Severity: {severity.value}\n"
        )


# Example 7: Practical development script with error recovery
@with_retry(RetryConfig(max_retries=3, base_delay=1.0))
def run_linting():
    """Run linting with retry on transient failures."""
    logger.info("Running linting...")
    result = subprocess.run(
        ["uvx", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Linting errors are permanent, not transient
        raise RuntimeError(f"Linting failed:\n{result.stdout}\n{result.stderr}")

    return result.stdout


@with_retry(RetryConfig(max_retries=3, base_delay=1.0))
def run_type_checking():
    """Run type checking with retry on transient failures."""
    logger.info("Running type checking...")
    result = subprocess.run(
        ["uvx", "pyright", "src/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Type checking failed:\n{result.stdout}\n{result.stderr}")

    return result.stdout


def run_quality_checks():
    """Run all quality checks with error recovery."""
    logger.info("\n=== Running Quality Checks ===\n")

    results = {}

    # Run linting
    try:
        results['linting'] = run_linting()
        logger.info("✓ Linting passed")
    except Exception as e:
        logger.error(f"✗ Linting failed: {e}")
        results['linting'] = None

    # Run type checking
    try:
        results['type_checking'] = run_type_checking()
        logger.info("✓ Type checking passed")
    except Exception as e:
        logger.error(f"✗ Type checking failed: {e}")
        results['type_checking'] = None

    # Run tests
    try:
        results['tests'] = run_tests_simple()
        logger.info("✓ Tests passed")
    except Exception as e:
        logger.error(f"✗ Tests failed: {e}")
        results['tests'] = None

    return results


# Example 8: Comprehensive development workflow
def development_workflow():
    """
    Complete development workflow with error recovery.

    This demonstrates a realistic development script that:
    1. Ensures dependencies are installed (with fallback)
    2. Runs quality checks (with retry)
    3. Builds the project (with circuit breaker)
    """
    logger.info("\n" + "=" * 60)
    logger.info("Development Workflow with Error Recovery")
    logger.info("=" * 60 + "\n")

    # Step 1: Ensure dependencies
    logger.info("Step 1: Ensuring dependencies...")
    try:
        deps_result = ensure_dependencies()
        logger.info(f"✓ Dependencies ready: {deps_result[:100]}...")
    except Exception as e:
        logger.error(f"✗ Failed to ensure dependencies: {e}")
        return False

    # Step 2: Run quality checks
    logger.info("\nStep 2: Running quality checks...")
    quality_results = run_quality_checks()

    all_passed = all(v is not None for v in quality_results.values())
    if not all_passed:
        logger.warning("⚠ Some quality checks failed")
        return False

    logger.info("\n✓ All quality checks passed!")

    # Step 3: Build (with circuit breaker)
    logger.info("\nStep 3: Building project...")
    try:
        build_result = run_build_with_circuit_breaker()
        logger.info("✓ Build successful")
    except Exception as e:
        logger.error(f"✗ Build failed: {e}")
        return False

    logger.info("\n" + "=" * 60)
    logger.info("✓ Development workflow completed successfully!")
    logger.info("=" * 60 + "\n")

    return True


def main():
    """Run all examples."""
    # Example 6: Error classification
    demonstrate_error_classification()

    # Example 7 & 8: Practical workflow
    # Uncomment to run (requires actual project setup)
    # development_workflow()

    logger.info("\n=== Error Recovery Examples Complete ===")
    logger.info("\nTo use in your scripts:")
    logger.info("1. Import: from error_recovery import with_retry, RetryConfig")
    logger.info("2. Decorate: @with_retry(RetryConfig(max_retries=3))")
    logger.info("3. Run: Your function will automatically retry on transient errors")


if __name__ == "__main__":
    main()
