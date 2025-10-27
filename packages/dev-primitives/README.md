# Development Primitives

Meta-level development primitives for error recovery, retry logic, circuit breakers, and observability.

## Features

- **Error Recovery**: Automatic retry with exponential backoff
- **Circuit Breakers**: Prevent cascading failures
- **Error Classification**: Categorize errors (network, rate limit, transient, permanent)
- **Observability**: Structured logging and metrics

## Installation

```bash
uv pip install -e packages/dev-primitives
```

## Quick Start

```python
from dev_primitives import with_retry, RetryConfig, CircuitBreaker

# Simple retry
@with_retry(RetryConfig(max_retries=3))
def flaky_operation():
    # Your code here
    pass

# Circuit breaker
cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
result = cb.call(risky_function, arg1, arg2)
```

## Usage

See the [scripts/primitives](../../scripts/primitives) directory for examples and the original implementation.

## License

Proprietary - TTA Storytelling Platform
