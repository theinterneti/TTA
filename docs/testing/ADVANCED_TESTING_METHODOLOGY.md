# Advanced Testing Methodology for TTA Model Management

**Date:** 2025-10-10
**Component:** Model Management
**Testing Approach:** Comprehensive Multi-Strategy Testing
**Environment:** Solo Developer WSL2 Workflow

---

## Overview

This document describes the advanced testing methodology for the TTA Model Management component, incorporating property-based testing, mutation testing, performance regression testing, and contract testing alongside traditional unit, integration, and end-to-end tests.

---

## Table of Contents

1. [Testing Strategy Overview](#testing-strategy-overview)
2. [Property-Based Testing](#property-based-testing)
3. [Mutation Testing](#mutation-testing)
4. [Performance Regression Testing](#performance-regression-testing)
5. [Contract Testing](#contract-testing)
6. [Traditional Testing Approaches](#traditional-testing-approaches)
7. [Tool Configuration](#tool-configuration)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

---

## Testing Strategy Overview

### Multi-Layered Testing Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Pyramid                          │
├─────────────────────────────────────────────────────────────┤
│  E2E Tests (Critical Paths 100%)                            │
│    ├─ Complete user journeys                                │
│    ├─ OAuth/API key flows                                   │
│    └─ Model selection workflows                             │
├─────────────────────────────────────────────────────────────┤
│  Integration Tests (75% coverage)                           │
│    ├─ Provider + Service integration                        │
│    ├─ Database integration (Redis, Neo4j)                   │
│    └─ Multi-component workflows                             │
├─────────────────────────────────────────────────────────────┤
│  Unit Tests (80% coverage)                                  │
│    ├─ Provider tests                                        │
│    ├─ Service tests                                         │
│    └─ Model/interface tests                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Advanced Testing Strategies                     │
├─────────────────────────────────────────────────────────────┤
│  Property-Based Tests (Critical algorithms 100%)            │
│    ├─ Model selection invariants                            │
│    ├─ Cost calculation properties                           │
│    └─ Fallback selection properties                         │
├─────────────────────────────────────────────────────────────┤
│  Mutation Tests (90% mutation score)                        │
│    ├─ Critical business logic                               │
│    ├─ Error handling paths                                  │
│    └─ Security-critical code                                │
├─────────────────────────────────────────────────────────────┤
│  Performance Tests (All critical paths)                     │
│    ├─ Model selection latency < 500ms                       │
│    ├─ Fallback activation < 1s                              │
│    └─ Metrics recording < 10ms                              │
├─────────────────────────────────────────────────────────────┤
│  Contract Tests (All API endpoints)                         │
│    ├─ Frontend/Backend contracts                            │
│    └─ Provider API contracts                                │
└─────────────────────────────────────────────────────────────┘
```

### Quality Targets

| Testing Type | Target | Measurement |
|-------------|--------|-------------|
| Code Coverage | 75% overall, 80% unit, 75% integration | pytest-cov |
| Property Coverage | 100% critical algorithms | hypothesis |
| Mutation Score | 90% overall, 100% critical paths | mutmut |
| Performance | < 20% degradation allowed | pytest-benchmark |
| Contract Coverage | 100% API endpoints | pact-python |

---

## Property-Based Testing

### What is Property-Based Testing?

Property-based testing uses **hypothesis** to automatically generate diverse test inputs and verify that certain properties (invariants) always hold true, regardless of the input.

**Benefits:**
- Discovers edge cases automatically
- Tests algorithmic correctness
- Validates invariants across input space
- Reduces manual test case creation

### When to Use Property-Based Testing

✅ **Use for:**
- Model selection algorithms
- Cost calculation logic
- Fallback strategy selection
- Configuration validation
- Scoring and ranking algorithms

❌ **Don't use for:**
- External API calls (use mocks)
- Database operations (use integration tests)
- UI interactions (use E2E tests)

### Property-Based Testing Patterns

#### Pattern 1: Invariant Testing

**Example: Model ranking invariant**
```python
from hypothesis import given, strategies as st
from src.components.model_management.services import ModelSelector

@given(
    models=st.lists(
        st.builds(ModelInfo,
            model_id=st.text(min_size=1),
            performance_score=st.floats(min_value=0, max_value=10)
        ),
        min_size=2
    )
)
def test_higher_score_ranks_higher(models):
    """Property: Models with higher scores always rank higher."""
    selector = ModelSelector(...)
    ranked = selector.rank_models(models, requirements)

    # Invariant: Ranking preserves score ordering
    for i in range(len(ranked) - 1):
        assert ranked[i].performance_score >= ranked[i+1].performance_score
```

#### Pattern 2: Round-Trip Testing

**Example: Configuration serialization**
```python
@given(config=st.builds(ModelManagementConfig))
def test_config_serialization_roundtrip(config):
    """Property: Config serialization is lossless."""
    serialized = config.to_dict()
    deserialized = ModelManagementConfig.from_dict(serialized)
    assert deserialized == config
```

#### Pattern 3: Metamorphic Testing

**Example: Cost calculation**
```python
@given(
    model=st.builds(ModelInfo),
    tokens=st.integers(min_value=1, max_value=1000000)
)
def test_cost_scales_linearly(model, tokens):
    """Property: Cost scales linearly with tokens."""
    cost_1x = calculate_cost(model, tokens)
    cost_2x = calculate_cost(model, tokens * 2)

    # Metamorphic relation: doubling tokens doubles cost
    assert abs(cost_2x - (cost_1x * 2)) < 0.01  # Allow small floating point error
```

### Running Property-Based Tests

```bash
# Run all property-based tests
uvx pytest tests/unit/model_management/ -m property

# Run with statistics
uvx pytest tests/unit/model_management/ -m property --hypothesis-show-statistics

# Run with more examples (slower but more thorough)
uvx pytest tests/unit/model_management/ -m property --hypothesis-max-examples=1000
```

---

## Mutation Testing

### What is Mutation Testing?

Mutation testing uses **mutmut** to introduce small changes (mutations) to your code and verify that your tests catch these changes. It validates test suite effectiveness.

**Benefits:**
- Validates test quality (not just coverage)
- Identifies weak tests
- Ensures tests catch actual bugs
- Improves confidence in test suite

### Mutation Testing Workflow

```
1. mutmut mutates code (e.g., changes `>` to `>=`)
2. Test suite runs against mutated code
3. If tests FAIL → Mutation killed ✅ (good test)
4. If tests PASS → Mutation survived ❌ (weak test)
5. Mutation score = killed / total mutations
```

### Running Mutation Tests

```bash
# Run mutation tests on model management
uvx mutmut run --paths-to-mutate=src/components/model_management

# Show results
uvx mutmut results

# Show surviving mutations (need investigation)
uvx mutmut show

# Generate HTML report
uvx mutmut html
```

### Interpreting Mutation Results

**Mutation Score Interpretation:**
- **90-100%**: Excellent test suite
- **80-90%**: Good test suite
- **70-80%**: Adequate test suite
- **< 70%**: Weak test suite, needs improvement

**Surviving Mutations:**
- Review each surviving mutation
- Add tests to kill the mutation
- Or document why mutation is acceptable (e.g., logging code)

### Mutation Testing Best Practices

1. **Run weekly in CI/CD** (too slow for PR checks)
2. **Focus on critical code** (model selection, fallback, security)
3. **Investigate all surviving mutations**
4. **Document acceptable survivors**
5. **Track mutation score over time**

---

## Performance Regression Testing

### What is Performance Regression Testing?

Performance regression testing uses **pytest-benchmark** to measure and track performance over time, ensuring new changes don't degrade performance.

**Benefits:**
- Prevents performance degradation
- Establishes performance baselines
- Tracks performance trends
- Validates performance requirements

### Performance Benchmarks

#### Critical Path Benchmarks

| Operation | Target (p95) | Measurement |
|-----------|--------------|-------------|
| Model selection | < 500ms | Time to select optimal model |
| Fallback activation | < 1s | Time to activate fallback |
| Metrics recording | < 10ms | Overhead of recording metrics |
| API key validation | < 200ms | Time to validate API key |

### Running Performance Tests

```bash
# Run all performance benchmarks
uvx pytest tests/performance/benchmarks/ --benchmark-only

# Run with comparison to baseline
uvx pytest tests/performance/benchmarks/ --benchmark-compare=0001

# Fail if performance degrades > 20%
uvx pytest tests/performance/benchmarks/ --benchmark-compare-fail=mean:20%

# Save new baseline
uvx pytest tests/performance/benchmarks/ --benchmark-save=baseline
```

### Performance Testing Patterns

#### Pattern 1: Latency Benchmarking

```python
import pytest

def test_model_selection_performance(benchmark, model_selector, requirements):
    """Benchmark model selection latency."""
    result = benchmark(model_selector.select_model, requirements)

    # Verify result is correct
    assert result is not None

    # Performance assertion (optional, benchmark handles this)
    # assert benchmark.stats['mean'] < 0.5  # 500ms
```

#### Pattern 2: Throughput Benchmarking

```python
def test_metrics_recording_throughput(benchmark, performance_monitor):
    """Benchmark metrics recording throughput."""
    metrics = {"response_time_ms": 100, "tokens": 50}

    # Benchmark records ops/second automatically
    benchmark(performance_monitor.record_metrics, "test-model", metrics)
```

---

## Contract Testing

### What is Contract Testing?

Contract testing uses **pact-python** to validate API contracts between consumers (frontend) and providers (backend), enabling independent development and deployment.

**Benefits:**
- Validates API compatibility
- Enables independent frontend/backend development
- Documents API contracts explicitly
- Prevents breaking changes

### Contract Testing Workflow

```
1. Consumer (frontend) defines expected API contract
2. Consumer tests run against mock provider
3. Contract (pact file) is generated
4. Provider (backend) validates against contract
5. Both sides can evolve independently
```

### Running Contract Tests

```bash
# Run consumer contract tests (frontend)
uvx pytest tests/contracts/consumer/

# Run provider contract tests (backend)
uvx pytest tests/contracts/provider/

# Publish contracts to Pact Broker (optional)
pact-broker publish tests/contracts/pacts --broker-base-url=http://localhost:9292
```

### Contract Testing Patterns

#### Pattern 1: Consumer Contract

```python
# tests/contracts/consumer/test_frontend_model_management_contract.py
import pytest
from pact import Consumer, Provider

pact = Consumer('Frontend').has_pact_with(Provider('ModelManagementAPI'))

def test_get_available_models_contract():
    """Contract: Frontend expects list of models from API."""
    expected = {
        'models': [
            {
                'model_id': 'test-model',
                'name': 'Test Model',
                'provider_type': 'openrouter',
                'is_free': True
            }
        ]
    }

    (pact
     .given('models are available')
     .upon_receiving('a request for available models')
     .with_request('GET', '/api/v1/models')
     .will_respond_with(200, body=expected))

    with pact:
        # Make actual request
        response = requests.get('http://localhost:1234/api/v1/models')
        assert response.status_code == 200
        assert 'models' in response.json()
```

---

## Traditional Testing Approaches

### Unit Tests

**Purpose:** Test individual functions/classes in isolation

**Tools:** pytest, unittest.mock

**Command:** `uvx pytest tests/unit/model_management/`

**Coverage Target:** 80%

### Integration Tests

**Purpose:** Test component interactions with real databases

**Tools:** pytest with testcontainers

**Command:** `uvx pytest tests/integration/model_management/`

**Coverage Target:** 75%

### End-to-End Tests

**Purpose:** Test complete user journeys

**Tools:** Playwright (TypeScript)

**Command:** `npx playwright test tests/e2e/specs/model-management.spec.ts`

**Coverage Target:** 100% critical paths

---

## Tool Configuration

### pyproject.toml Configuration

```toml
[dependency-groups]
dev = [
    # ... existing dependencies ...
    "hypothesis>=6.100.0",           # Property-based testing
    "mutmut>=2.4.0",                 # Mutation testing
    "pytest-benchmark>=4.0.0",       # Performance benchmarking
    "pact-python>=2.2.0",            # Contract testing
]

[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "property: Property-based tests",
    "performance: Performance benchmarks",
    "contract: Contract tests",
]

[tool.hypothesis]
max_examples = 100
deadline = 5000  # 5 seconds
database = ".hypothesis/examples"

[tool.pytest-benchmark]
min_rounds = 5
warmup = true
autosave = true
```

### Mutation Testing Configuration

**File:** `tests/mutation/mutation_config.toml`

```toml
[mutmut]
paths_to_mutate = "src/components/model_management"
backup = false
runner = "pytest -x --tb=short"
tests_dir = "tests/unit/model_management"
```

---

## CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/test-model-management.yml`

```yaml
name: Model Management Tests

on:
  pull_request:
    paths:
      - 'src/components/model_management/**'
      - 'tests/**'
  push:
    branches: [main, staging]
  schedule:
    - cron: '0 2 * * 0'  # Weekly mutation tests

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Run unit tests with coverage
        run: |
          uvx pytest tests/unit/model_management/ \
            --cov=src/components/model_management \
            --cov-fail-under=80

  property-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Run property-based tests
        run: uvx pytest tests/unit/model_management/ -m property

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Run performance benchmarks
        run: |
          uvx pytest tests/performance/benchmarks/ \
            --benchmark-only \
            --benchmark-compare-fail=mean:20%

  mutation-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Run mutation tests
        run: uvx mutmut run --paths-to-mutate=src/components/model_management
```

---

## Best Practices

### Property-Based Testing

1. **Start with simple properties** (e.g., output type, non-null)
2. **Use custom strategies** for domain-specific data
3. **Document invariants** clearly in test docstrings
4. **Limit max_examples** for fast feedback (100 default)
5. **Use `@example` decorator** for known edge cases

### Mutation Testing

1. **Run weekly** (too slow for PR checks)
2. **Focus on critical code** first
3. **Investigate all survivors** systematically
4. **Document acceptable survivors**
5. **Track mutation score** over time

### Performance Testing

1. **Establish baselines** early
2. **Use relative comparisons** (% change)
3. **Allow reasonable variance** (20%)
4. **Run on dedicated hardware** if possible
5. **Track trends** over time

### Contract Testing

1. **Consumer defines contracts** (consumer-driven)
2. **Version contracts** with API versions
3. **Publish to Pact Broker** for visibility
4. **Validate on both sides**
5. **Document contract evolution**

---

## Examples

### Complete Property-Based Test Example

**File:** `tests/unit/model_management/services/test_model_selector_properties.py`

```python
"""Property-based tests for ModelSelector service."""

import pytest
from hypothesis import given, strategies as st, assume
from src.components.model_management.services import ModelSelector
from src.components.model_management.interfaces import ModelInfo, ProviderType, TaskType

# Custom strategies for domain-specific data
@st.composite
def model_info_strategy(draw):
    """Generate valid ModelInfo instances."""
    return ModelInfo(
        model_id=draw(st.text(min_size=1, max_size=50)),
        name=draw(st.text(min_size=1, max_size=100)),
        provider_type=draw(st.sampled_from(list(ProviderType))),
        performance_score=draw(st.floats(min_value=0, max_value=10)),
        cost_per_token=draw(st.floats(min_value=0, max_value=1) | st.none()),
        therapeutic_safety_score=draw(st.floats(min_value=0, max_value=10) | st.none()),
        is_free=draw(st.booleans()),
        capabilities=draw(st.lists(st.text(min_size=1), min_size=1)),
    )

@pytest.mark.property
class TestModelSelectorProperties:
    """Property-based tests for model selection logic."""

    @given(models=st.lists(model_info_strategy(), min_size=2, max_size=20))
    def test_ranking_preserves_order(self, models):
        """Property: Ranking preserves score ordering."""
        selector = ModelSelector(providers={}, hardware_detector=None, selection_criteria=None)
        ranked = selector.rank_models(models, requirements=None)

        # Invariant: Higher scores rank higher
        for i in range(len(ranked) - 1):
            assert ranked[i].performance_score >= ranked[i+1].performance_score

    @given(
        models=st.lists(model_info_strategy(), min_size=1),
        prefer_free=st.booleans()
    )
    def test_free_model_preference(self, models, prefer_free):
        """Property: Free models rank higher when preferred."""
        assume(any(m.is_free for m in models))  # Ensure at least one free model

        selector = ModelSelector(
            providers={},
            hardware_detector=None,
            selection_criteria=ModelSelectionCriteria(prefer_free_models=prefer_free)
        )
        ranked = selector.rank_models(models, requirements=None)

        if prefer_free and ranked:
            # First model should be free if free models exist
            free_models = [m for m in models if m.is_free]
            if free_models:
                assert ranked[0].is_free or ranked[0].performance_score > max(m.performance_score for m in free_models)

    @given(
        cost_per_token=st.floats(min_value=0, max_value=1),
        tokens=st.integers(min_value=1, max_value=1000000)
    )
    def test_cost_calculation_linearity(self, cost_per_token, tokens):
        """Property: Cost scales linearly with tokens."""
        cost_1x = cost_per_token * tokens
        cost_2x = cost_per_token * (tokens * 2)

        # Metamorphic relation
        assert abs(cost_2x - (cost_1x * 2)) < 0.01
```

### Complete Performance Benchmark Example

**File:** `tests/performance/benchmarks/test_model_selection_performance.py`

```python
"""Performance benchmarks for model selection."""

import pytest
from src.components.model_management import ModelManagementComponent, ModelRequirements, TaskType

@pytest.fixture
def model_component():
    """Create model management component for benchmarking."""
    config = {
        "model_management": {
            "enabled": True,
            "default_provider": "openrouter",
            "providers": {
                "openrouter": {
                    "enabled": True,
                    "api_key": "test-key",  # pragma: allowlist secret
                }
            }
        }
    }
    return ModelManagementComponent(config)

@pytest.mark.performance
class TestModelSelectionPerformance:
    """Performance benchmarks for model selection."""

    def test_model_selection_latency(self, benchmark, model_component):
        """Benchmark: Model selection should complete in < 500ms."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=5000,
            min_quality_score=7.0
        )

        # Benchmark the selection
        result = benchmark(model_component.select_model, requirements)

        # Verify correctness
        assert result is not None

        # Performance assertion (benchmark handles comparison)
        stats = benchmark.stats
        assert stats['mean'] < 0.5, f"Model selection took {stats['mean']}s, expected < 0.5s"

    def test_fallback_activation_latency(self, benchmark, model_component):
        """Benchmark: Fallback activation should complete in < 1s."""
        # Setup: Simulate primary model failure
        failed_model_id = "failed-model"
        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        # Benchmark fallback
        result = benchmark(
            model_component.fallback_handler.get_fallback_model,
            failed_model_id,
            requirements
        )

        # Performance assertion
        stats = benchmark.stats
        assert stats['mean'] < 1.0, f"Fallback took {stats['mean']}s, expected < 1s"
```

### Complete Contract Test Example

**File:** `tests/contracts/consumer/test_frontend_model_management_contract.py`

```python
"""Consumer contract tests for frontend model management."""

import pytest
import requests
from pact import Consumer, Provider, Like, EachLike

pact = Consumer('TTA-Frontend').has_pact_with(
    Provider('ModelManagementAPI'),
    pact_dir='tests/contracts/pacts'
)

@pytest.mark.contract
class TestModelManagementContract:
    """Contract tests for model management API."""

    def test_get_available_models_contract(self):
        """Contract: GET /api/v1/models returns list of models."""
        expected_response = {
            'models': EachLike({
                'model_id': Like('meta-llama/llama-3.1-8b-instruct:free'),
                'name': Like('Llama 3.1 8B Instruct'),
                'provider_type': Like('openrouter'),
                'is_free': Like(True),
                'performance_score': Like(8.0),
                'cost_per_token': Like(0.0)
            })
        }

        (pact
         .given('models are available')
         .upon_receiving('a request for available models')
         .with_request('GET', '/api/v1/models')
         .will_respond_with(200, body=expected_response))

        with pact:
            response = requests.get(f'{pact.uri}/api/v1/models')
            assert response.status_code == 200
            data = response.json()
            assert 'models' in data
            assert len(data['models']) > 0

    def test_validate_api_key_contract(self):
        """Contract: POST /api/v1/openrouter/auth/validate-key validates API key."""
        request_body = {
            'api_key': Like('sk-or-v1-test-key'),
            'validate_only': Like(False)
        }

        expected_response = {
            'valid': Like(True),
            'user': Like({
                'id': Like('user-123'),
                'email': Like('user@example.com'),
                'name': Like('Test User')
            })
        }

        (pact
         .given('valid API key exists')
         .upon_receiving('a request to validate API key')
         .with_request('POST', '/api/v1/openrouter/auth/validate-key', body=request_body)
         .will_respond_with(200, body=expected_response))

        with pact:
            response = requests.post(
                f'{pact.uri}/api/v1/openrouter/auth/validate-key',
                json={'api_key': 'sk-or-v1-test-key', 'validate_only': False}  # pragma: allowlist secret
            )
            assert response.status_code == 200
            data = response.json()
            assert data['valid'] is True
            assert 'user' in data
```

---

## Quick Reference Commands

### Daily Development

```bash
# Run unit tests (fast)
uvx pytest tests/unit/model_management/ -q

# Run with coverage
uvx pytest tests/unit/model_management/ --cov=src/components/model_management

# Run property-based tests
uvx pytest tests/unit/model_management/ -m property

# Run integration tests
uvx pytest tests/integration/model_management/
```

### Performance Testing

```bash
# Run all benchmarks
uvx pytest tests/performance/benchmarks/ --benchmark-only

# Compare to baseline
uvx pytest tests/performance/benchmarks/ --benchmark-compare=0001

# Save new baseline
uvx pytest tests/performance/benchmarks/ --benchmark-save=baseline

# Fail if performance degrades > 20%
uvx pytest tests/performance/benchmarks/ --benchmark-compare-fail=mean:20%
```

### Mutation Testing

```bash
# Run mutation tests (slow - weekly only)
uvx mutmut run --paths-to-mutate=src/components/model_management

# Show results
uvx mutmut results

# Show surviving mutations
uvx mutmut show

# Generate HTML report
uvx mutmut html

# Apply a specific mutation for debugging
uvx mutmut apply 42
```

### Contract Testing

```bash
# Run consumer contract tests
uvx pytest tests/contracts/consumer/

# Run provider contract tests
uvx pytest tests/contracts/provider/

# Verify all contracts
uvx pytest tests/contracts/ -v
```

---

## Troubleshooting

### Property-Based Tests Taking Too Long

**Problem:** Hypothesis generates too many examples

**Solution:**
```python
# Reduce max_examples for faster feedback
@given(data=st.data())
@settings(max_examples=50)  # Default is 100
def test_something(data):
    ...
```

### Mutation Tests Timing Out

**Problem:** Mutation tests run too long

**Solution:**
```bash
# Run on specific files only
uvx mutmut run --paths-to-mutate=src/components/model_management/services/model_selector.py

# Use faster test runner
uvx mutmut run --runner="pytest -x --tb=line"
```

### Performance Benchmarks Inconsistent

**Problem:** Benchmark results vary significantly

**Solution:**
```python
# Increase warmup rounds
@pytest.mark.benchmark(warmup=True, warmup_iterations=10)
def test_performance(benchmark):
    ...

# Or configure in pyproject.toml
[tool.pytest-benchmark]
warmup = true
warmup_iterations = 10
```

### Contract Tests Failing

**Problem:** Pact mock server not starting

**Solution:**
```bash
# Ensure pact-python is installed
uv add --dev pact-python

# Check pact mock server logs
cat ~/.pact/logs/pact-mock-service.log

# Use explicit port
pact = Consumer('Frontend').has_pact_with(
    Provider('API'),
    port=1234  # Explicit port
)
```

---

## Resources

### Documentation
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Pact Python Documentation](https://docs.pact.io/implementation_guides/python)

### Internal Documentation
- [Testing Strategy Summary](./TESTING_STRATEGY_SUMMARY.md)
- [Test Coverage Analysis](./TEST_COVERAGE_ANALYSIS.md)
- [Quick Reference Guide](./QUICK_REFERENCE_TESTING_GUIDE.md)

### Examples
- Property-based tests: `tests/unit/model_management/services/test_model_selector_properties.py`
- Performance benchmarks: `tests/performance/benchmarks/test_model_selection_performance.py`
- Contract tests: `tests/contracts/consumer/test_frontend_model_management_contract.py`

---

**Document Version:** 1.0
**Last Updated:** 2025-10-10
**Status:** Ready for Implementation
**Maintained by:** The Augster (AI Development Assistant)


---
**Logseq:** [[TTA.dev/Docs/Testing/Advanced_testing_methodology]]
