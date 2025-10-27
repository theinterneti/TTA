"""
Development Observability Examples

Demonstrates how to use the dev_metrics framework for tracking
development operations.

Usage:
    python scripts/observability/examples.py
"""

import subprocess
import time
from dev_metrics import track_execution, get_collector
from dashboard import generate_dashboard


# Example 1: Track test execution
@track_execution("pytest_unit_tests", metadata={"suite": "unit", "type": "test"})
def run_unit_tests():
    """Run unit tests with metrics tracking."""
    print("Running unit tests...")
    result = subprocess.run(
        ["uvx", "pytest", "tests/unit/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Unit tests failed: {result.stderr}")
    
    return result.stdout


@track_execution("pytest_integration_tests", metadata={"suite": "integration", "type": "test"})
def run_integration_tests():
    """Run integration tests with metrics tracking."""
    print("Running integration tests...")
    result = subprocess.run(
        ["uvx", "pytest", "tests/integration/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Integration tests failed: {result.stderr}")
    
    return result.stdout


# Example 2: Track build operations
@track_execution("docker_build", metadata={"type": "build", "target": "development"})
def build_docker_image():
    """Build Docker image with metrics tracking."""
    print("Building Docker image...")
    result = subprocess.run(
        ["docker", "build", "-t", "tta:dev", "-f", "docker/Dockerfile.dev", "."],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Docker build failed: {result.stderr}")
    
    return result.stdout


# Example 3: Track quality checks
@track_execution("ruff_lint", metadata={"type": "quality", "tool": "ruff"})
def run_ruff_lint():
    """Run ruff linting with metrics tracking."""
    print("Running ruff lint...")
    result = subprocess.run(
        ["uvx", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Ruff lint failed: {result.stderr}")
    
    return result.stdout


@track_execution("pyright_typecheck", metadata={"type": "quality", "tool": "pyright"})
def run_pyright():
    """Run pyright type checking with metrics tracking."""
    print("Running pyright...")
    result = subprocess.run(
        ["uvx", "pyright", "src/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Pyright failed: {result.stderr}")
    
    return result.stdout


# Example 4: Track custom operations
@track_execution("database_migration", metadata={"type": "database", "direction": "up"})
def run_database_migration():
    """Run database migration with metrics tracking."""
    print("Running database migration...")
    # Simulate migration
    time.sleep(0.5)
    return "Migration completed successfully"


# Example 5: Demonstrate error tracking
@track_execution("flaky_operation", metadata={"type": "demo", "expected": "failure"})
def flaky_operation():
    """Demonstrate error tracking."""
    print("Running flaky operation (will fail)...")
    raise RuntimeError("Simulated failure for demonstration")


# Example 6: Complete development workflow
def run_complete_workflow():
    """Run complete development workflow with metrics tracking."""
    print("\n" + "="*60)
    print("Running Complete Development Workflow")
    print("="*60 + "\n")
    
    operations = [
        ("Linting", run_ruff_lint),
        ("Type Checking", run_pyright),
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
    ]
    
    results = {}
    for name, operation in operations:
        try:
            print(f"\n[{name}]")
            operation()
            results[name] = "✓ PASSED"
        except Exception as e:
            results[name] = f"✗ FAILED: {str(e)[:50]}"
    
    print("\n" + "="*60)
    print("Workflow Results:")
    print("="*60)
    for name, result in results.items():
        print(f"  {name}: {result}")
    print()


# Example 7: Generate and view metrics
def view_metrics_summary():
    """View metrics summary."""
    collector = get_collector()
    summary = collector.get_metrics_summary(days=7)
    
    print("\n" + "="*60)
    print("Development Metrics Summary (Last 7 Days)")
    print("="*60 + "\n")
    
    if not summary:
        print("No metrics available yet.")
        return
    
    for name, metrics in sorted(summary.items()):
        print(f"{name}:")
        print(f"  Total Executions: {metrics['total_executions']}")
        print(f"  Success Rate: {metrics['success_rate']:.1%}")
        print(f"  Avg Duration: {metrics['avg_duration_ms']:.0f}ms")
        print(f"  Min/Max Duration: {metrics['min_duration_ms']:.0f}ms / {metrics['max_duration_ms']:.0f}ms")
        print(f"  Successes: {metrics['successes']}")
        print(f"  Failures: {metrics['failures']}")
        print()


# Example 8: Generate dashboard
def generate_metrics_dashboard():
    """Generate HTML dashboard."""
    print("\n" + "="*60)
    print("Generating Metrics Dashboard")
    print("="*60 + "\n")
    
    generate_dashboard(
        output_file="dev_metrics_dashboard.html",
        days=30
    )
    
    print("\nDashboard generated: dev_metrics_dashboard.html")
    print("Open in browser to view visualizations.")


# Example 9: View recent metrics for specific operation
def view_recent_metrics(operation_name: str = None, limit: int = 5):
    """View recent metrics for a specific operation."""
    collector = get_collector()
    recent = collector.get_recent_metrics(name=operation_name, limit=limit)
    
    print("\n" + "="*60)
    if operation_name:
        print(f"Recent Metrics for: {operation_name}")
    else:
        print("Recent Metrics (All Operations)")
    print("="*60 + "\n")
    
    if not recent:
        print("No recent metrics found.")
        return
    
    for metric in recent:
        status_symbol = "✓" if metric["status"] == "success" else "✗"
        print(f"{status_symbol} {metric['name']}")
        print(f"  Started: {metric['started_at']}")
        print(f"  Duration: {metric.get('duration_ms', 0):.0f}ms")
        print(f"  Status: {metric['status']}")
        if metric.get('error'):
            print(f"  Error: {metric['error'][:100]}")
        print()


# Example 10: Cleanup old metrics
def cleanup_old_metrics(days_to_keep: int = 30):
    """Cleanup metrics older than specified days."""
    collector = get_collector()
    deleted = collector.clear_old_metrics(days_to_keep=days_to_keep)
    
    print(f"\nCleaned up {deleted} old metrics files (keeping last {days_to_keep} days)")


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
            print("Running demo operations...")
            
            # Successful operations
            try:
                run_ruff_lint()
            except:
                pass
            
            try:
                run_pyright()
            except:
                pass
            
            # Failed operation
            try:
                flaky_operation()
            except:
                pass
            
            # View results
            view_metrics_summary()
            generate_metrics_dashboard()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  workflow   - Run complete development workflow")
            print("  summary    - View metrics summary")
            print("  dashboard  - Generate HTML dashboard")
            print("  recent [operation] - View recent metrics")
            print("  cleanup [days] - Cleanup old metrics")
            print("  demo       - Run demo operations")
    else:
        print("Development Observability Examples")
        print("\nUsage:")
        print("  python scripts/observability/examples.py <command>")
        print("\nCommands:")
        print("  workflow   - Run complete development workflow")
        print("  summary    - View metrics summary")
        print("  dashboard  - Generate HTML dashboard")
        print("  recent [operation] - View recent metrics")
        print("  cleanup [days] - Cleanup old metrics")
        print("  demo       - Run demo operations")

