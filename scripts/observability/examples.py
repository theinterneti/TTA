"""

# Logseq: [[TTA.dev/Scripts/Observability/Examples]]
Development Observability Examples

Demonstrates how to use the dev_metrics framework for tracking
development operations.

Usage:
    python scripts/observability/examples.py
"""

import builtins
import contextlib
import subprocess
import time

from dashboard import generate_dashboard
from dev_metrics import get_collector, track_execution


# Example 1: Track test execution
@track_execution("pytest_unit_tests", metadata={"suite": "unit", "type": "test"})
def run_unit_tests():
    """Run unit tests with metrics tracking."""
    result = subprocess.run(
        ["uvx", "pytest", "tests/unit/", "-v", "--tb=short"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Unit tests failed: {result.stderr}")

    return result.stdout


@track_execution(
    "pytest_integration_tests", metadata={"suite": "integration", "type": "test"}
)
def run_integration_tests():
    """Run integration tests with metrics tracking."""
    result = subprocess.run(
        ["uvx", "pytest", "tests/integration/", "-v", "--tb=short"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Integration tests failed: {result.stderr}")

    return result.stdout


# Example 2: Track build operations
@track_execution("docker_build", metadata={"type": "build", "target": "development"})
def build_docker_image():
    """Build Docker image with metrics tracking."""
    result = subprocess.run(
        ["docker", "build", "-t", "tta:dev", "-f", "docker/Dockerfile.dev", "."],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Docker build failed: {result.stderr}")

    return result.stdout


# Example 3: Track quality checks
@track_execution("ruff_lint", metadata={"type": "quality", "tool": "ruff"})
def run_ruff_lint():
    """Run ruff linting with metrics tracking."""
    result = subprocess.run(
        ["uvx", "ruff", "check", "src/", "tests/"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ruff lint failed: {result.stderr}")

    return result.stdout


@track_execution("pyright_typecheck", metadata={"type": "quality", "tool": "pyright"})
def run_pyright():
    """Run pyright type checking with metrics tracking."""
    result = subprocess.run(
        ["uvx", "pyright", "src/"], check=False, capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Pyright failed: {result.stderr}")

    return result.stdout


# Example 4: Track custom operations
@track_execution("database_migration", metadata={"type": "database", "direction": "up"})
def run_database_migration():
    """Run database migration with metrics tracking."""
    # Simulate migration
    time.sleep(0.5)
    return "Migration completed successfully"


# Example 5: Demonstrate error tracking
@track_execution("flaky_operation", metadata={"type": "demo", "expected": "failure"})
def flaky_operation():
    """Demonstrate error tracking."""
    raise RuntimeError("Simulated failure for demonstration")


# Example 6: Complete development workflow
def run_complete_workflow():
    """Run complete development workflow with metrics tracking."""

    operations = [
        ("Linting", run_ruff_lint),
        ("Type Checking", run_pyright),
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
    ]

    results = {}
    for name, operation in operations:
        try:
            operation()
            results[name] = "✓ PASSED"
        except Exception as e:
            results[name] = f"✗ FAILED: {str(e)[:50]}"

    for name in results:
        pass


# Example 7: Generate and view metrics
def view_metrics_summary():
    """View metrics summary."""
    collector = get_collector()
    summary = collector.get_metrics_summary(days=7)

    if not summary:
        return

    for _name, _metrics in sorted(summary.items()):
        pass


# Example 8: Generate dashboard
def generate_metrics_dashboard():
    """Generate HTML dashboard."""

    generate_dashboard(output_file="dev_metrics_dashboard.html", days=30)


# Example 9: View recent metrics for specific operation
def view_recent_metrics(operation_name: str = None, limit: int = 5):
    """View recent metrics for a specific operation."""
    collector = get_collector()
    recent = collector.get_recent_metrics(name=operation_name, limit=limit)

    if operation_name:
        pass
    else:
        pass

    if not recent:
        return

    for metric in recent:
        "✓" if metric["status"] == "success" else "✗"
        if metric.get("error"):
            pass


# Example 10: Cleanup old metrics
def cleanup_old_metrics(days_to_keep: int = 30):
    """Cleanup metrics older than specified days."""
    collector = get_collector()
    collector.clear_old_metrics(days_to_keep=days_to_keep)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "workflow":
            run_complete_workflow()
        elif command == "summary":
            view_metrics_summary()
        elif command == "dashboard":
            generate_metrics_dashboard()
        elif command == "recent":
            operation = sys.argv[2] if len(sys.argv) > 2 else None
            view_recent_metrics(operation)
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            cleanup_old_metrics(days)
        elif command == "demo":
            # Run demo operations

            # Successful operations
            with contextlib.suppress(builtins.BaseException):
                run_ruff_lint()

            with contextlib.suppress(builtins.BaseException):
                run_pyright()

            # Failed operation
            with contextlib.suppress(builtins.BaseException):
                flaky_operation()

            # View results
            view_metrics_summary()
            generate_metrics_dashboard()
        else:
            pass
    else:
        pass
