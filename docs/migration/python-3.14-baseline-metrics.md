# Python 3.14 Baseline Metrics & Compatibility Assessment

> **Status**: In Progress
> **Created**: 2026-03-04
> **Python Version**: 3.14 (pre-release)
> **Baseline Python**: 3.12

## Overview

This document establishes baseline performance metrics for TTA running on Python 3.14
and tracks compatibility status of all dependencies. Python 3.14 introduces significant
performance improvements including a JIT compiler, deferred evaluation of annotations
(PEP 649), and `t-string` support (PEP 750).

## Environment Setup

### Prerequisites

```bash
# Install Python 3.14 via uv
uv python install 3.14

# Create isolated test environment
uv venv --python 3.14 .venv-py314

# Activate and install dependencies
source .venv-py314/bin/activate
uv sync --all-extras
```

### CI Workflow

The `python314-compat.yml` workflow runs the test suite against Python 3.14 on every
push to `main`, `staging`, and `development` branches, as well as on pull requests.

## Dependency Compatibility Matrix

### Core Dependencies

| Package | Min Version | Py3.14 Status | Notes |
|---|---|---|---|
| numpy | >=1.24.0 | ⚠️ Verify | C extensions may need rebuild |
| pandas | >=2.0.0 | ⚠️ Verify | Depends on numpy compatibility |
| scikit-learn | >=1.2.0 | ⚠️ Verify | C/Cython extensions |
| scipy | >=1.15.0 | ⚠️ Verify | Fortran/C extensions |
| torch | >=2.0.0 | ⚠️ Verify | Complex C++ extensions |
| transformers | >=4.30.0 | ✅ Likely | Pure Python + optional C |
| fastapi | >=0.115.0 | ✅ Likely | Pure Python |
| pydantic | >=2.10.0 | ⚠️ Verify | Rust extensions (pydantic-core) |
| uvicorn | >=0.32.0 | ✅ Likely | Pure Python |

### Database Drivers

| Package | Min Version | Py3.14 Status | Notes |
|---|---|---|---|
| neo4j | >=6.0.0 | ✅ Likely | Pure Python driver |
| redis | >=7.0.0 | ✅ Likely | Pure Python + optional hiredis |
| sqlalchemy | >=2.0.46 | ⚠️ Verify | C extensions (greenlet) |

### Testing Stack

| Package | Min Version | Py3.14 Status | Notes |
|---|---|---|---|
| pytest | >=7.3.1 | ✅ Likely | Pure Python |
| pytest-asyncio | >=0.23.0 | ✅ Likely | Pure Python |
| hypothesis | >=6.100.0 | ✅ Likely | Pure Python |
| mutmut | >=2.4.0 | ❌ Known Issue | setproctitle segfault on 3.14 |
| pytest-benchmark | >=4.0.0 | ⚠️ Verify | Uses C timer extensions |

### TTA Platform Packages

| Package | Version | Py3.14 Status | Notes |
|---|---|---|---|
| tta-dev-primitives | >=1.3.0 | ⚠️ Verify | Internal package |
| tta-observability-integration | >=1.0.0 | ⚠️ Verify | Internal package |
| universal-agent-context | >=1.0.0 | ⚠️ Verify | Internal package |
| tta-dev-integrations | >=0.1.0 | ⚠️ Verify | Internal package |

## Known Compatibility Issues

### 1. mutmut Segfault (Critical)

**Issue**: mutmut 3.x segfaults on Python 3.14 due to `setproctitle` incompatibility.

**Impact**: Mutation testing cannot run on Python 3.14 until upstream fix.

**Workaround**: Skip mutation testing in Python 3.14 CI jobs. Continue running on 3.12.

### 2. Deferred Annotation Evaluation (PEP 649)

**Impact**: Code using `from __future__ import annotations` may behave differently.
TTA uses Pydantic v2 which is compatible, but custom validators should be verified.

**Action**: Audit `@validator` and `@field_validator` usage for annotation-dependent behavior.

### 3. C Extension Rebuild

**Impact**: Packages with C extensions (numpy, scipy, pydantic-core) require wheels
built for Python 3.14 or compilation from source.

**Action**: Check PyPI for 3.14 wheel availability before environment setup.

## Baseline Performance Metrics

### How to Collect Metrics

Run the baseline benchmark script:

```bash
# Collect baselines on Python 3.12 (reference)
uv run python scripts/python314_baseline_benchmarks.py --output docs/migration/baselines/py312.json

# Collect baselines on Python 3.14 (comparison)
# Activate the 3.14 environment first
source .venv-py314/bin/activate
uv run python scripts/python314_baseline_benchmarks.py --output docs/migration/baselines/py314.json
```

### Metric Categories

#### 1. Agent Orchestration Latency

Measures the round-trip time for agent message processing through the orchestration layer.

| Metric | Target | Py3.12 Baseline | Py3.14 Result |
|---|---|---|---|
| IPA processing (p50) | <100ms | _pending_ | _pending_ |
| IPA processing (p95) | <250ms | _pending_ | _pending_ |
| WBA processing (p50) | <200ms | _pending_ | _pending_ |
| WBA processing (p95) | <500ms | _pending_ | _pending_ |
| NGA processing (p50) | <500ms | _pending_ | _pending_ |
| NGA processing (p95) | <1000ms | _pending_ | _pending_ |
| Circuit breaker overhead | <5ms | _pending_ | _pending_ |

#### 2. Redis Message Throughput

Measures message publish/subscribe performance through RedisMessageCoordinator.

| Metric | Target | Py3.12 Baseline | Py3.14 Result |
|---|---|---|---|
| Publish rate (msg/s) | >1000 | _pending_ | _pending_ |
| Subscribe latency (p50) | <10ms | _pending_ | _pending_ |
| Subscribe latency (p95) | <50ms | _pending_ | _pending_ |
| Queue depth handling | 10k msgs | _pending_ | _pending_ |

#### 3. Neo4j Query Performance

Measures graph database query execution times.

| Metric | Target | Py3.12 Baseline | Py3.14 Result |
|---|---|---|---|
| Player state read (p50) | <50ms | _pending_ | _pending_ |
| Player state write (p50) | <100ms | _pending_ | _pending_ |
| Narrative history query | <200ms | _pending_ | _pending_ |
| World state traversal | <500ms | _pending_ | _pending_ |

#### 4. Memory Usage

Measures process memory consumption under various workloads.

| Metric | Target | Py3.12 Baseline | Py3.14 Result |
|---|---|---|---|
| Idle RSS | <200MB | _pending_ | _pending_ |
| Under load (10 sessions) | <500MB | _pending_ | _pending_ |
| Peak (100 concurrent) | <2GB | _pending_ | _pending_ |
| GC pause time (p95) | <50ms | _pending_ | _pending_ |

#### 5. Test Suite Execution Time

Measures CI test pipeline durations.

| Metric | Py3.12 Baseline | Py3.14 Result | Change |
|---|---|---|---|
| Unit test suite | _pending_ | _pending_ | _pending_ |
| Integration test suite | _pending_ | _pending_ | _pending_ |
| Full test suite | _pending_ | _pending_ | _pending_ |
| Import time (cold start) | _pending_ | _pending_ | _pending_ |

## Python 3.14 Feature Opportunities

### JIT Compiler (PEP 744)

Python 3.14's experimental JIT compiler may improve hot-path performance in:
- Agent orchestration loops
- Message serialization/deserialization
- Narrative text processing pipelines

**Action**: Benchmark with `PYTHON_JIT=1` environment variable.

### Deferred Evaluation of Annotations (PEP 649)

Reduces import-time overhead for heavily annotated modules. Expected benefit for:
- Pydantic model-heavy modules (`src/common/`, `src/api_gateway/`)
- Agent orchestration models (`src/agent_orchestration/models.py`)

### Template Strings (PEP 750)

New `t-string` syntax for safe string interpolation. Potential use in:
- Prompt engineering templates
- Narrative generation
- Logging format strings

**Action**: Evaluate adoption after 3.14 stable release.

## CI Integration

### Workflow: `python314-compat.yml`

The Python 3.14 compatibility workflow:
- Runs unit tests against Python 3.14
- Collects performance baselines via `pytest-benchmark`
- Uploads benchmark results as artifacts
- Uses `continue-on-error: true` during pre-release phase

### Running Locally

```bash
# Quick compatibility check
uv run --python 3.14 pytest -q --tb=short \
  -m "not integration and not neo4j and not redis" \
  tests/unit/

# Full benchmark run
uv run --python 3.14 python scripts/python314_baseline_benchmarks.py
```

## Performance Dashboard

### Grafana Integration

The existing analytics stack (`docker/compose/docker-compose.analytics.yml`) includes
Prometheus and Grafana. Python 3.14 metrics can be visualized by:

1. Running benchmarks with JSON output
2. Importing results into Prometheus via the pushgateway
3. Viewing the "Python Version Comparison" dashboard in Grafana (port 3004)

### Dashboard Panels

- **Test Suite Duration**: Side-by-side comparison of 3.12 vs 3.14 test times
- **Import Time**: Module import latency comparison
- **Memory Profile**: RSS memory over time for both versions
- **Benchmark Trends**: Historical benchmark results across CI runs

## Next Steps

1. ☐ Wait for Python 3.14 stable release (expected October 2026)
2. ☐ Verify all C-extension dependencies have 3.14 wheels
3. ☐ Collect initial baselines on 3.14 pre-release
4. ☐ Fill in baseline metric tables above
5. ☐ Evaluate JIT compiler impact on hot paths
6. ☐ Update `requires-python` to `">=3.12"` (already compatible)
7. ☐ Add `"Programming Language :: Python :: 3.14"` classifier

## References

- [PEP 649 – Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/)
- [PEP 744 – JIT Compilation](https://peps.python.org/pep-0744/)
- [PEP 750 – Template Strings](https://peps.python.org/pep-0750/)
- [Python 3.14 Release Schedule](https://peps.python.org/pep-0745/)
- [TTA CI Workflow: tests.yml](.github/workflows/tests.yml)
- [TTA CI Workflow: python314-compat.yml](.github/workflows/python314-compat.yml)
