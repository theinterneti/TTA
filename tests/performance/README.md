# Performance Testing for TTA Model Management

This directory contains performance benchmarks and regression tests for the Model Management component.

## What is Performance Regression Testing?

Performance regression testing uses **pytest-benchmark** to measure and track performance over time, ensuring new changes don't degrade performance.

**Benefits:**
- Prevents performance degradation
- Establishes performance baselines
- Tracks performance trends
- Validates performance requirements

## Quick Start

```bash
# Run all performance benchmarks
uvx pytest tests/performance/benchmarks/ --benchmark-only

# Compare to baseline
uvx pytest tests/performance/benchmarks/ --benchmark-compare=0001

# Fail if performance degrades > 20%
uvx pytest tests/performance/benchmarks/ --benchmark-compare-fail=mean:20%

# Save new baseline
uvx pytest tests/performance/benchmarks/ --benchmark-save=baseline
```

## Performance Targets

| Operation | Target (p95) | Measurement |
|-----------|--------------|-------------|
| Model selection | < 500ms | Time to select optimal model |
| Fallback activation | < 1s | Time to activate fallback |
| Metrics recording | < 10ms | Overhead of recording metrics |
| API key validation | < 200ms | Time to validate API key |

## Directory Structure

```
tests/performance/
├── benchmarks/                          # Performance benchmark tests
│   ├── test_model_selection_performance.py
│   ├── test_fallback_performance.py
│   ├── test_metrics_recording_performance.py
│   └── test_api_performance.py
├── regression/                          # Performance baselines
│   ├── performance_baselines.json      # Baseline performance data
│   └── history/                         # Historical performance data
└── README.md                            # This file
```

## Writing Performance Tests

### Basic Benchmark

```python
import pytest

def test_model_selection_latency(benchmark, model_selector, requirements):
    """Benchmark model selection latency."""
    result = benchmark(model_selector.select_model, requirements)

    # Verify result is correct
    assert result is not None

    # Performance assertion (optional)
    assert benchmark.stats['mean'] < 0.5  # 500ms
```

### Benchmark with Setup

```python
def test_with_setup(benchmark):
    """Benchmark with setup/teardown."""
    def setup():
        # Setup code (not timed)
        return expensive_setup()

    def teardown(data):
        # Teardown code (not timed)
        cleanup(data)

    # Only the function is timed
    benchmark.pedantic(
        function_to_benchmark,
        setup=setup,
        teardown=teardown,
        rounds=10
    )
```

### Throughput Benchmark

```python
def test_throughput(benchmark):
    """Benchmark throughput (ops/second)."""
    # Benchmark automatically calculates ops/second
    benchmark(function_to_benchmark, arg1, arg2)

    # Access throughput
    ops_per_second = 1 / benchmark.stats['mean']
    assert ops_per_second > 100  # At least 100 ops/second
```

## Running Benchmarks

### Local Development

```bash
# Run all benchmarks
uvx pytest tests/performance/benchmarks/ --benchmark-only

# Run specific benchmark
uvx pytest tests/performance/benchmarks/test_model_selection_performance.py --benchmark-only

# Run with verbose output
uvx pytest tests/performance/benchmarks/ --benchmark-only --benchmark-verbose

# Show statistics
uvx pytest tests/performance/benchmarks/ --benchmark-only --benchmark-columns=min,max,mean,stddev
```

### Baseline Management

```bash
# Save current performance as baseline
uvx pytest tests/performance/benchmarks/ --benchmark-save=baseline

# Compare to baseline
uvx pytest tests/performance/benchmarks/ --benchmark-compare=baseline

# Fail if performance degrades > 20%
uvx pytest tests/performance/benchmarks/ --benchmark-compare-fail=mean:20%

# List all saved baselines
uvx pytest tests/performance/benchmarks/ --benchmark-list
```

### CI/CD Integration

```bash
# Run in CI/CD with comparison
uvx pytest tests/performance/benchmarks/ \
  --benchmark-only \
  --benchmark-autosave \
  --benchmark-compare=0001 \
  --benchmark-compare-fail=mean:20%
```

## Interpreting Results

### Benchmark Output

```
Name (time in ms)                    Min      Max     Mean  StdDev
test_model_selection_latency      450.23   520.45   480.12   15.34
test_fallback_activation          890.12  1050.67   950.45   45.23
```

- **Min**: Fastest execution time
- **Max**: Slowest execution time
- **Mean**: Average execution time
- **StdDev**: Standard deviation (consistency)

### Performance Comparison

```
Comparing against baseline:
test_model_selection_latency: +5.2% (PASS)
test_fallback_activation: +25.3% (FAIL - exceeds 20% threshold)
```

- **Green (+/- 5%)**: No significant change
- **Yellow (5-20%)**: Minor degradation, monitor
- **Red (> 20%)**: Significant degradation, investigate

## Best Practices

1. **Establish baselines early** - Set performance expectations
2. **Use relative comparisons** - Compare % change, not absolute values
3. **Allow reasonable variance** - 20% threshold is typical
4. **Run on dedicated hardware** - Consistent environment for CI/CD
5. **Track trends over time** - Monitor performance evolution
6. **Warm up before benchmarking** - Avoid cold start effects
7. **Disable GC during benchmarks** - Reduce noise (done automatically)
8. **Run multiple rounds** - Get statistical significance (min 5 rounds)

## Configuration

Performance testing is configured in `pyproject.toml`:

```toml
[tool.pytest-benchmark]
min_rounds = 5                  # Minimum number of benchmark rounds
max_time = 1.0                  # Maximum time per benchmark (seconds)
warmup = true                   # Enable warmup rounds
disable_gc = true               # Disable GC during benchmarks
save_data = true                # Save benchmark data
autosave = true                 # Automatically save after each run
compare = "0001"                # Compare to baseline 0001 by default
```

## Troubleshooting

### Benchmarks Too Slow

**Problem:** Benchmarks take too long

**Solutions:**
- Reduce `max_time` in config
- Reduce `min_rounds` in config
- Use `@pytest.mark.slow` and skip in fast runs
- Optimize the code being benchmarked

### Inconsistent Results

**Problem:** High standard deviation

**Solutions:**
- Increase `min_rounds` for more samples
- Increase `warmup` iterations
- Run on dedicated hardware
- Close other applications
- Use `benchmark.pedantic()` for more control

### Comparison Failures

**Problem:** Benchmarks fail comparison unexpectedly

**Solutions:**
- Check if baseline is outdated
- Verify running on same hardware
- Allow higher variance threshold (e.g., 30%)
- Investigate actual performance changes

## CI/CD Integration

Performance tests run on every PR and nightly:

```yaml
performance-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - name: Run performance benchmarks
      run: |
        uvx pytest tests/performance/benchmarks/ \
          --benchmark-only \
          --benchmark-autosave \
          --benchmark-compare=0001 \
          --benchmark-compare-fail=mean:20%
    - name: Upload benchmark results
      uses: actions/upload-artifact@v4
      with:
        name: benchmark-results
        path: .benchmarks/
```

## Resources

- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Advanced Testing Methodology](../../docs/testing/ADVANCED_TESTING_METHODOLOGY.md)
- [Testing Strategy Summary](../../docs/testing/TESTING_STRATEGY_SUMMARY.md)

---

**Last Updated:** 2025-10-10
**Maintained by:** The Augster (AI Development Assistant)
