# Development Observability Framework

**Quick Win #3** - Track and visualize development operation metrics for improved velocity and debugging.

## Overview

The Development Observability Framework provides automatic metrics collection, persistence, and visualization for development operations like tests, builds, and quality checks.

**Key Features:**
- 📊 **Automatic Metrics Collection** - Track execution time, success/failure, metadata
- 💾 **Persistent Storage** - JSONL files organized by date in `.metrics/`
- 📈 **Visual Dashboard** - HTML dashboard with charts and detailed metrics
- 🎯 **Simple Integration** - Single decorator to add metrics to any function
- 🔍 **Query Interface** - Get summaries, recent metrics, filter by operation

---

## Quick Start

### 1. Track an Operation

```python
from observability.dev_metrics import track_execution

@track_execution("pytest_unit_tests", metadata={"suite": "unit"})
def run_unit_tests():
    """Run unit tests with automatic metrics tracking."""
    # Your test execution code
    pass
```

### 2. View Metrics Summary

```python
from observability.dev_metrics import get_collector

collector = get_collector()
summary = collector.get_metrics_summary(days=7)

for name, metrics in summary.items():
    print(f"{name}:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Avg Duration: {metrics['avg_duration_ms']:.0f}ms")
```

### 3. Generate Dashboard

```python
from observability.dashboard import generate_dashboard

generate_dashboard(output_file="dev_metrics_dashboard.html", days=30)
```

---

## Installation

No additional dependencies required for basic functionality.

**Optional (for dashboard charts):**
```bash
uv add --dev matplotlib
```

---

## Usage Patterns

### Pattern 1: Track Test Execution

```python
from observability.dev_metrics import track_execution
import subprocess

@track_execution("pytest_unit_tests", metadata={"suite": "unit", "type": "test"})
def run_unit_tests():
    result = subprocess.run(
        ["uvx", "pytest", "tests/unit/", "-v"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Tests failed: {result.stderr}")
    
    return result.stdout
```

### Pattern 2: Track Build Operations

```python
@track_execution("docker_build", metadata={"type": "build", "target": "dev"})
def build_docker_image():
    result = subprocess.run(
        ["docker", "build", "-t", "tta:dev", "."],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Build failed: {result.stderr}")
    
    return result.stdout
```

### Pattern 3: Track Quality Checks

```python
@track_execution("ruff_lint", metadata={"type": "quality", "tool": "ruff"})
def run_ruff_lint():
    result = subprocess.run(
        ["uvx", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Lint failed: {result.stderr}")
    
    return result.stdout
```

### Pattern 4: Manual Tracking

```python
from observability.dev_metrics import get_collector

collector = get_collector()

# Start tracking
exec_id = collector.start_execution("custom_operation", metadata={"key": "value"})

try:
    # Your operation
    result = perform_operation()
    
    # End tracking (success)
    collector.end_execution(exec_id, status="success")
except Exception as e:
    # End tracking (failure)
    collector.end_execution(exec_id, status="failed", error=str(e))
    raise
```

---

## Configuration

### Metrics Storage Location

Default: `.metrics/` directory

```python
from observability.dev_metrics import DevMetricsCollector

# Custom location
collector = DevMetricsCollector(metrics_dir="/path/to/metrics")
```

### Dashboard Customization

```python
from observability.dashboard import generate_dashboard

generate_dashboard(
    output_file="custom_dashboard.html",
    days=30,  # Number of days to include
    metrics_dir=".metrics"  # Metrics directory
)
```

---

## Metrics Data Structure

### ExecutionMetric

```python
{
    "name": "pytest_unit_tests",
    "started_at": "2025-10-20T10:30:00.000000",
    "ended_at": "2025-10-20T10:30:05.123000",
    "duration_ms": 5123.0,
    "status": "success",  # or "failed"
    "metadata": {
        "suite": "unit",
        "type": "test"
    },
    "error": null  # or error message if failed
}
```

### Summary Metrics

```python
{
    "pytest_unit_tests": {
        "total_executions": 10,
        "successes": 9,
        "failures": 1,
        "success_rate": 0.9,
        "avg_duration_ms": 5123.0,
        "min_duration_ms": 4500.0,
        "max_duration_ms": 6000.0
    }
}
```

---

## API Reference

### `track_execution(name, metadata=None)`

Decorator to track function execution.

**Parameters:**
- `name` (str): Name of the operation
- `metadata` (dict, optional): Additional metadata to attach

**Returns:** Decorated function

**Example:**
```python
@track_execution("my_operation", metadata={"type": "test"})
def my_function():
    pass
```

---

### `DevMetricsCollector`

Main class for metrics collection.

#### Methods

**`start_execution(name, metadata=None) -> str`**
- Start tracking an execution
- Returns execution ID

**`end_execution(exec_id, status="success", error=None)`**
- End tracking an execution
- `status`: "success" or "failed"
- `error`: Error message if failed

**`get_metrics_summary(days=7) -> dict`**
- Get aggregated metrics for last N days
- Returns summary dictionary

**`get_recent_metrics(name=None, limit=10) -> list`**
- Get recent metrics, optionally filtered by name
- Returns list of metric dictionaries

**`clear_old_metrics(days_to_keep=30) -> int`**
- Delete metrics older than specified days
- Returns number of files deleted

---

### `generate_dashboard(output_file, days=30, metrics_dir=".metrics")`

Generate HTML dashboard with visualizations.

**Parameters:**
- `output_file` (str): Path to output HTML file
- `days` (int): Number of days to include
- `metrics_dir` (str): Metrics directory path

---

## Examples

See `scripts/observability/examples.py` for comprehensive examples:

```bash
# Run demo operations
python scripts/observability/examples.py demo

# View metrics summary
python scripts/observability/examples.py summary

# Generate dashboard
python scripts/observability/examples.py dashboard

# View recent metrics
python scripts/observability/examples.py recent

# View recent metrics for specific operation
python scripts/observability/examples.py recent pytest_unit_tests

# Cleanup old metrics (keep last 30 days)
python scripts/observability/examples.py cleanup 30
```

---

## Integration with Existing Scripts

### Option 1: Wrap Existing Functions

```python
from observability.dev_metrics import track_execution

# Existing function
def run_tests():
    # Test execution code
    pass

# Wrap with tracking
tracked_run_tests = track_execution("run_tests")(run_tests)
```

### Option 2: Add Decorator

```python
from observability.dev_metrics import track_execution

@track_execution("run_tests", metadata={"type": "test"})
def run_tests():
    # Test execution code
    pass
```

### Option 3: Manual Integration

```python
from observability.dev_metrics import get_collector

def run_tests():
    collector = get_collector()
    exec_id = collector.start_execution("run_tests")
    
    try:
        # Test execution code
        collector.end_execution(exec_id, status="success")
    except Exception as e:
        collector.end_execution(exec_id, status="failed", error=str(e))
        raise
```

---

## Best Practices

1. **Use Descriptive Names** - Make operation names clear and consistent
   ```python
   @track_execution("pytest_unit_tests")  # Good
   @track_execution("tests")              # Too vague
   ```

2. **Add Meaningful Metadata** - Include context for filtering/analysis
   ```python
   @track_execution("pytest", metadata={
       "suite": "unit",
       "type": "test",
       "coverage": True
   })
   ```

3. **Track at Appropriate Granularity** - Not too fine, not too coarse
   ```python
   # Good: Track test suite execution
   @track_execution("pytest_unit_tests")
   def run_unit_tests():
       pass
   
   # Too fine: Don't track individual test functions
   # Too coarse: Don't track entire CI/CD pipeline as one operation
   ```

4. **Regular Cleanup** - Prevent metrics directory from growing indefinitely
   ```python
   # In CI/CD or scheduled task
   collector.clear_old_metrics(days_to_keep=30)
   ```

5. **Monitor Dashboard** - Review metrics regularly to identify issues
   - Slow tests
   - Flaky operations
   - Performance regressions

---

## Success Metrics

**Before Observability:**
- ❌ No visibility into development operations
- ❌ Slow tests go unnoticed
- ❌ Performance regressions not caught early
- ❌ Hard to identify bottlenecks

**After Observability:**
- ✅ 100% visibility into all tracked operations
- ✅ Performance trends visible in dashboard
- ✅ Identify slow/flaky operations immediately
- ✅ Data-driven development decisions

**Target Goals:**
- Identify and fix 3+ performance bottlenecks in first week
- Reduce average test execution time by 20%
- Achieve >95% success rate for all operations

---

## Troubleshooting

**Issue: No metrics appearing**
- Check that `.metrics/` directory exists and is writable
- Verify operations are being executed
- Check for exceptions in tracked functions

**Issue: Dashboard has no charts**
- Install matplotlib: `uv add --dev matplotlib`
- Check for errors in dashboard generation

**Issue: Metrics files growing too large**
- Run cleanup: `collector.clear_old_metrics(days_to_keep=30)`
- Consider reducing retention period

---

## Phase 2 Considerations

When integrating into TTA application (Phase 2):
- Track LLM API calls (latency, tokens, costs)
- Track agent orchestration operations
- Track database queries (Redis, Neo4j)
- Track user session metrics
- Integrate with distributed tracing (OpenTelemetry)

---

**Status:** Ready for use  
**Next Steps:** Integrate with development scripts and CI/CD workflows

