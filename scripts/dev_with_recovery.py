#!/usr/bin/env python3
"""
Development commands with error recovery.

This is a Python wrapper around common development tasks that adds
error recovery, retry logic, and fallback strategies using the
error recovery framework.

Usage:
    python scripts/dev_with_recovery.py lint
    python scripts/dev_with_recovery.py test
    python scripts/dev_with_recovery.py check-all
"""

import subprocess
import sys
import logging
from pathlib import Path
from typing import NoReturn

# Add scripts/primitives to path
sys.path.insert(0, str(Path(__file__).parent / "primitives"))

from error_recovery import (
    with_retry,
    RetryConfig,
    ErrorCategory,
    classify_error
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Development Commands with Error Recovery
# ============================================================================

@with_retry(RetryConfig(max_retries=2, base_delay=1.0))
def run_linting() -> str:
    """Run linting with retry on transient failures."""
    logger.info("Running Ruff linter...")
    result = subprocess.run(
        ["uvx", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Linting errors are permanent, not transient
        # But we still wrap in retry in case uvx itself has issues
        raise RuntimeError(f"Linting failed:\n{result.stdout}")

    logger.info("✓ Linting passed")
    return result.stdout


@with_retry(RetryConfig(max_retries=2, base_delay=1.0))
def run_linting_fix() -> str:
    """Run linting with auto-fix and retry on transient failures."""
    logger.info("Running Ruff linter with auto-fix...")
    result = subprocess.run(
        ["uvx", "ruff", "check", "--fix", "src/", "tests/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Linting with auto-fix failed:\n{result.stdout}")

    logger.info("✓ Linting fixes applied")
    return result.stdout


@with_retry(RetryConfig(max_retries=2, base_delay=1.0))
def run_formatting() -> str:
    """Run code formatting with retry on transient failures."""
    logger.info("Formatting code with Ruff...")
    result = subprocess.run(
        ["uvx", "ruff", "format", "src/", "tests/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Formatting failed:\n{result.stdout}")

    logger.info("✓ Code formatted")
    return result.stdout


@with_retry(RetryConfig(max_retries=2, base_delay=1.0))
def run_format_check() -> str:
    """Check code formatting with retry on transient failures."""
    logger.info("Checking code formatting...")
    result = subprocess.run(
        ["uvx", "ruff", "format", "--check", "src/", "tests/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Format check failed:\n{result.stdout}")

    logger.info("✓ Format check passed")
    return result.stdout


@with_retry(RetryConfig(max_retries=2, base_delay=2.0))
def run_type_checking() -> str:
    """Run type checking with retry on transient failures."""
    logger.info("Running Pyright type checker...")
    result = subprocess.run(
        ["uvx", "pyright", "src/"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Type checking failed:\n{result.stdout}")

    logger.info("✓ Type checking passed")
    return result.stdout


@with_retry(RetryConfig(max_retries=3, base_delay=2.0))
def run_tests(args: list[str] | None = None) -> str:
    """Run tests with retry on transient failures."""
    logger.info("Running tests...")

    cmd = ["uvx", "pytest", "tests/"]
    if args:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Tests failed:\n{result.stdout}")

    logger.info("✓ Tests passed")
    return result.stdout


@with_retry(RetryConfig(max_retries=3, base_delay=2.0))
def run_tests_with_coverage() -> str:
    """Run tests with coverage and retry on transient failures."""
    logger.info("Running tests with coverage...")
    result = subprocess.run(
        ["uvx", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Tests with coverage failed:\n{result.stdout}")

    logger.info("✓ Tests with coverage passed")
    logger.info("Coverage report: htmlcov/index.html")
    return result.stdout


@with_retry(RetryConfig(max_retries=5, base_delay=2.0, max_delay=30.0))
def install_dependencies() -> str:
    """Install dependencies with aggressive retry on network failures."""
    logger.info("Installing dependencies...")
    result = subprocess.run(
        ["uv", "sync"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Dependency installation failed:\n{result.stderr}")

    logger.info("✓ Dependencies installed")
    return result.stdout


# ============================================================================
# Composite Commands
# ============================================================================

def cmd_quality() -> bool:
    """Run quality checks (lint + format-check)."""
    logger.info("=" * 60)
    logger.info("Running quality checks...")
    logger.info("=" * 60)

    try:
        run_linting()
        run_format_check()
        logger.info("\n✓ All quality checks passed!\n")
        return True
    except Exception as e:
        logger.error(f"\n✗ Quality checks failed: {e}\n")
        return False


def cmd_quality_fix() -> bool:
    """Run quality fixes (lint-fix + format)."""
    logger.info("=" * 60)
    logger.info("Running quality fixes...")
    logger.info("=" * 60)

    try:
        run_linting_fix()
        run_formatting()
        logger.info("\n✓ All quality fixes applied!\n")
        return True
    except Exception as e:
        logger.error(f"\n✗ Quality fixes failed: {e}\n")
        return False


def cmd_check_all() -> bool:
    """Run full validation (quality + typecheck + test)."""
    logger.info("=" * 60)
    logger.info("Running full validation...")
    logger.info("=" * 60)

    try:
        run_linting()
        run_format_check()
        run_type_checking()
        run_tests()
        logger.info("\n✓ All checks passed!\n")
        return True
    except Exception as e:
        logger.error(f"\n✗ Validation failed: {e}\n")
        return False


def cmd_dev_check() -> bool:
    """Run quick dev workflow (quality-fix + test-fast)."""
    logger.info("=" * 60)
    logger.info("Running quick dev check...")
    logger.info("=" * 60)

    try:
        run_linting_fix()
        run_formatting()
        run_tests(["-x", "--ff"])  # Stop on first failure, run failed tests first
        logger.info("\n✓ Dev check complete!\n")
        return True
    except Exception as e:
        logger.error(f"\n✗ Dev check failed: {e}\n")
        return False


def cmd_setup() -> bool:
    """Setup development environment with dependencies."""
    logger.info("=" * 60)
    logger.info("Setting up development environment...")
    logger.info("=" * 60)

    try:
        install_dependencies()
        logger.info("\n✓ Development environment ready!\n")
        return True
    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}\n")
        return False


# ============================================================================
# CLI
# ============================================================================

def print_usage() -> None:
    """Print usage information."""
    print("""
Development Commands with Error Recovery

Usage: python scripts/dev_with_recovery.py <command>

Commands:
  lint              Run linting
  lint-fix          Run linting with auto-fix
  format            Format code
  format-check      Check code formatting
  typecheck         Run type checking
  test              Run tests
  test-cov          Run tests with coverage

  quality           Run quality checks (lint + format-check)
  quality-fix       Run quality fixes (lint-fix + format)
  check-all         Run full validation (quality + typecheck + test)
  dev-check         Quick dev workflow (quality-fix + test-fast)
  setup             Setup development environment

All commands include automatic retry on transient failures.
""")


def main() -> NoReturn:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "lint": lambda: run_linting() and True,
        "lint-fix": lambda: run_linting_fix() and True,
        "format": lambda: run_formatting() and True,
        "format-check": lambda: run_format_check() and True,
        "typecheck": lambda: run_type_checking() and True,
        "test": lambda: run_tests() and True,
        "test-cov": lambda: run_tests_with_coverage() and True,
        "quality": cmd_quality,
        "quality-fix": cmd_quality_fix,
        "check-all": cmd_check_all,
        "dev-check": cmd_dev_check,
        "setup": cmd_setup,
    }

    if command not in commands:
        logger.error(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)

    try:
        success = commands[command]()
        sys.exit(0 if success else 1)
    except Exception as e:
        category, severity = classify_error(e)
        logger.error(
            f"Command failed: {e}\n"
            f"Category: {category.value}, Severity: {severity.value}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
