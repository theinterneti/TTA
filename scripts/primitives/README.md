# Development Primitives - Error Recovery Framework

**Phase 1 Agentic Primitive:** Error Handling and Recovery for Development Process

This directory contains error recovery patterns for development automation, implementing retry logic, fallback strategies, and circuit breakers at the meta-level (development process) before integrating into the TTA product.

## Quick Start

### Basic Retry

```python
from error_recovery import with_retry, RetryConfig

@with_retry(RetryConfig(max_retries=3))
def flaky_operation():
    # Your code that might fail transiently
    pass
```

### Retry with Fallback

```python
def fallback_function():
    return "default_value"

@with_retry(fallback=fallback_function)
def operation_with_fallback():
    # Try this first, use fallback if all retries fail
    pass
```

### Async Retry

```python
from error_recovery import with_retry_async

@with_retry_async(RetryConfig(max_retries=3))
async def async_operation():
    # Async code with retry
    pass
```

### Circuit Breaker

```python
from error_recovery import CircuitBreaker

cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

def protected_operation():
    return cb.call(risky_function, arg1, arg2)
```

## Features

### 1. Error Classification

Automatically classifies errors into categories:

- **NETWORK**: Connection errors, timeouts
- **RATE_LIMIT**: API rate limiting, quota exceeded
- **RESOURCE**: Memory, disk space issues
- **TRANSIENT**: Temporary service unavailability
- **PERMANENT**: Unrecoverable errors

```python
from error_recovery import classify_error, ErrorCategory

try:
    risky_operation()
except Exception as e:
    category, severity = classify_error(e)
    print(f"Error category: {category.value}, severity: {severity.value}")
```

### 2. Exponential Backoff with Jitter

Prevents thundering herd problem:

```python
RetryConfig(
    max_retries=5,
    base_delay=1.0,      # Start with 1 second
    max_delay=60.0,      # Cap at 60 seconds
    exponential_base=2.0, # Double each time
    jitter=True          # Add randomness
)
```

Delay progression: 1s → 2s → 4s → 8s → 16s (with jitter)

### 3. Intelligent Retry Logic

Only retries errors that make sense:

- ✅ Network errors → Retry
- ✅ Rate limits → Retry with backoff
- ✅ Transient failures → Retry
- ❌ Permanent errors → Fail immediately
- ❌ Critical errors → Fail immediately

### 4. Circuit Breaker Pattern

Prevents cascading failures:

- **CLOSED**: Normal operation
- **OPEN**: Too many failures, fail fast
- **HALF_OPEN**: Testing recovery

```python
cb = CircuitBreaker(
    failure_threshold=5,    # Open after 5 failures
    recovery_timeout=60.0,  # Wait 60s before testing
    expected_exception=ConnectionError
)
```

## Usage Examples

### Development Scripts

See `dev_with_recovery.py` for a complete example:

```python
@with_retry(RetryConfig(max_retries=3, base_delay=2.0))
def run_tests():
    """Run tests with retry on transient failures."""
    result = subprocess.run(
        ["uvx", "pytest", "tests/"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
```

### CI/CD Integration

See `.github/workflows/dev-with-error-recovery.yml`:

```yaml
- name: Install dependencies (with retry)
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 5
    retry_wait_seconds: 30
    command: uv sync
```

### Fallback Strategies

```python
def fallback_cached_dependencies():
    """Use cached dependencies if installation fails."""
    logger.info("Using cached dependencies...")
    # Load from cache
    return cached_deps

@with_retry(
    RetryConfig(max_retries=3),
    fallback=fallback_cached_dependencies
)
def ensure_dependencies():
    """Install dependencies with fallback to cache."""
    return install_dependencies()
```

## Configuration

### RetryConfig Options

```python
@dataclass
class RetryConfig:
    max_retries: int = 3          # Maximum retry attempts
    base_delay: float = 1.0       # Initial delay in seconds
    max_delay: float = 60.0       # Maximum delay cap
    exponential_base: float = 2.0 # Backoff multiplier
    jitter: bool = True           # Add randomness to delays
```

### Common Configurations

**Quick retries (network glitches):**
```python
RetryConfig(max_retries=3, base_delay=0.5, max_delay=5.0)
```

**Aggressive retries (API rate limits):**
```python
RetryConfig(max_retries=10, base_delay=2.0, max_delay=120.0)
```

**Conservative retries (expensive operations):**
```python
RetryConfig(max_retries=2, base_delay=5.0, max_delay=30.0)
```

## Files

```
scripts/primitives/
├── error_recovery.py              # Core framework (300 lines)
├── example_error_recovery.py      # Usage examples (200 lines)
└── README.md                      # This file

scripts/
└── dev_with_recovery.py           # Development commands with retry (300 lines)

.github/workflows/
└── dev-with-error-recovery.yml    # CI/CD integration (200 lines)
```

## Error Recovery Patterns

### Pattern 1: Retry with Logging

```python
@with_retry(RetryConfig(max_retries=3))
def operation():
    logger.info("Attempting operation...")
    # Operation code
    logger.info("✓ Operation successful")
```

Logs show:
```
WARNING - operation failed (attempt 1/4): Connection timeout. Retrying in 1.2s...
WARNING - operation failed (attempt 2/4): Connection timeout. Retrying in 2.4s...
INFO - ✓ Operation successful
```

### Pattern 2: Retry with Fallback

```python
@with_retry(fallback=lambda: "default")
def fetch_config():
    # Try to fetch from remote
    return remote_config()
```

### Pattern 3: Circuit Breaker for External Services

```python
api_circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

def call_external_api():
    return api_circuit.call(requests.get, "https://api.example.com")
```

### Pattern 4: Async Retry for Concurrent Operations

```python
@with_retry_async(RetryConfig(max_retries=3))
async def fetch_multiple():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Best Practices

### 1. Choose Appropriate Retry Counts

- **Network operations**: 3-5 retries
- **API calls**: 5-10 retries (respect rate limits)
- **Database operations**: 2-3 retries
- **File I/O**: 2 retries

### 2. Set Reasonable Delays

- **Fast operations**: 0.5-2s base delay
- **API calls**: 2-5s base delay
- **Heavy operations**: 5-10s base delay

### 3. Use Fallbacks for Critical Operations

```python
# Good: Has fallback
@with_retry(fallback=use_cache)
def fetch_critical_data():
    return fetch_from_api()

# Bad: No fallback for critical operation
@with_retry()
def fetch_critical_data():
    return fetch_from_api()
```

### 4. Log Appropriately

```python
# Good: Informative logging
logger.warning(f"Operation failed (attempt {attempt}): {error}. Retrying...")

# Bad: Silent failures
pass  # Don't do this
```

### 5. Classify Errors Correctly

```python
# Good: Only retry transient errors
if should_retry(error, attempt, max_retries):
    retry()
else:
    raise error

# Bad: Retry everything
retry()  # Don't do this
```

## Metrics and Monitoring

Track error recovery effectiveness:

```python
# In production, track:
- Retry success rate
- Average retries per operation
- Circuit breaker state changes
- Fallback usage frequency
```

## Integration with TTA

This is a Phase 1 meta-level implementation. For Phase 2 product integration:

1. Apply patterns to `src/agent_orchestration/`
2. Add retry logic to LLM API calls
3. Implement circuit breakers for external services
4. Add fallback strategies for agent failures

## Testing

Run examples:

```bash
# Test error classification
python scripts/primitives/example_error_recovery.py

# Test development commands with retry
python scripts/dev_with_recovery.py quality

# Test CI/CD integration
# See .github/workflows/dev-with-error-recovery.yml
```

## Success Metrics (Week 1)

- [ ] 90% reduction in manual build interventions
- [ ] <2% build failure rate (down from ~20%)
- [ ] Faster CI/CD pipeline completion
- [ ] Zero cascading failures from transient errors

## Next Steps

1. **Measure Impact**: Track retry rates and success rates
2. **Refine Configurations**: Adjust based on real usage patterns
3. **Add More Fallbacks**: Identify critical operations needing fallbacks
4. **Phase 2 Integration**: Apply to TTA agent orchestration

---

**Status:** ✅ Complete (Phase 1 - Meta-Level Implementation)  
**Last Updated:** 2025-10-20  
**Next:** Quick Win #3 - Development Observability (Days 5-6)

