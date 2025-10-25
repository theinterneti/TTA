# Contract Testing for TTA Model Management

This directory contains contract tests for validating API compatibility between the frontend and backend.

## What is Contract Testing?

Contract testing uses **Pact** to validate API contracts between consumers (frontend) and providers (backend), enabling independent development and deployment.

**Benefits:**
- Validates API compatibility
- Enables independent frontend/backend development
- Documents API contracts explicitly
- Prevents breaking changes

## Quick Start

```bash
# Run consumer contract tests (frontend)
uvx pytest tests/contracts/consumer/

# Run provider contract tests (backend)
uvx pytest tests/contracts/provider/

# Verify all contracts
uvx pytest tests/contracts/ -v
```

## Contract Testing Workflow

```
1. Consumer (frontend) defines expected API contract
2. Consumer tests run against mock provider
3. Contract (pact file) is generated
4. Provider (backend) validates against contract
5. Both sides can evolve independently
```

## Directory Structure

```
tests/contracts/
├── consumer/                            # Consumer contract tests (frontend)
│   ├── test_frontend_model_management_contract.py
│   └── test_frontend_auth_contract.py
├── provider/                            # Provider contract tests (backend)
│   ├── test_openrouter_api_contract.py
│   └── test_model_management_api_contract.py
├── pacts/                               # Generated pact files
│   ├── tta-frontend-modelmanagementapi.json
│   └── tta-frontend-authapi.json
└── README.md                            # This file
```

## Writing Contract Tests

### Consumer Contract Test

```python
import pytest
import requests
from pact import Consumer, Provider, Like, EachLike

pact = Consumer('TTA-Frontend').has_pact_with(
    Provider('ModelManagementAPI'),
    pact_dir='tests/contracts/pacts'
)

def test_get_available_models_contract():
    """Contract: GET /api/v1/models returns list of models."""
    expected_response = {
        'models': EachLike({
            'model_id': Like('meta-llama/llama-3.1-8b-instruct:free'),
            'name': Like('Llama 3.1 8B Instruct'),
            'provider_type': Like('openrouter'),
            'is_free': Like(True),
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
        assert 'models' in response.json()
```

### Provider Contract Test

```python
import pytest
from pact import Verifier

def test_provider_honors_contract():
    """Verify provider honors the contract."""
    verifier = Verifier(
        provider='ModelManagementAPI',
        provider_base_url='http://localhost:8080'
    )

    # Verify against pact file
    output, logs = verifier.verify_pacts(
        'tests/contracts/pacts/tta-frontend-modelmanagementapi.json',
        provider_states_setup_url='http://localhost:8080/_pact/provider_states'
    )

    assert output == 0, f"Pact verification failed: {logs}"
```

## Pact Matchers

### Like (Type Matching)

```python
Like('example')  # Matches any string
Like(123)        # Matches any integer
Like(True)       # Matches any boolean
```

### EachLike (Array Matching)

```python
EachLike({
    'id': Like(1),
    'name': Like('test')
})  # Matches array of objects with this structure
```

### Term (Regex Matching)

```python
from pact import Term

Term(r'\d{4}-\d{2}-\d{2}', '2025-10-10')  # Matches date format
```

### Enum (Specific Values)

```python
from pact import Enum

Enum(['openrouter', 'ollama', 'local'])  # Matches one of these values
```

## Running Contract Tests

### Local Development

```bash
# Run all contract tests
uvx pytest tests/contracts/ -v

# Run consumer tests only
uvx pytest tests/contracts/consumer/ -v

# Run provider tests only
uvx pytest tests/contracts/provider/ -v

# Run specific contract test
uvx pytest tests/contracts/consumer/test_frontend_model_management_contract.py -v
```

### With Pact Broker (Optional)

```bash
# Publish contracts to Pact Broker
pact-broker publish tests/contracts/pacts \
  --broker-base-url=http://localhost:9292 \
  --consumer-app-version=1.0.0

# Verify provider against broker
pact-broker verify \
  --broker-base-url=http://localhost:9292 \
  --provider=ModelManagementAPI \
  --provider-app-version=1.0.0
```

## Provider States

Provider states set up the backend in a specific state for testing:

```python
# In consumer test
(pact
 .given('models are available')  # Provider state
 .upon_receiving('a request for available models')
 .with_request('GET', '/api/v1/models')
 .will_respond_with(200, body=expected_response))
```

```python
# In provider (FastAPI example)
@app.post("/_pact/provider_states")
async def provider_states(state: dict):
    """Set up provider state for contract testing."""
    if state['state'] == 'models are available':
        # Set up test data
        await setup_test_models()
    return {"result": "success"}
```

## Best Practices

1. **Consumer defines contracts** - Consumer-driven contract testing
2. **Version contracts** - Align with API versions
3. **Use matchers wisely** - Balance flexibility and specificity
4. **Test happy paths** - Focus on successful scenarios
5. **Document provider states** - Clear state setup requirements
6. **Publish to Pact Broker** - Centralize contract management (optional)
7. **Validate on both sides** - Consumer and provider tests
8. **Evolve contracts carefully** - Avoid breaking changes

## Contract Versioning

### Semantic Versioning

```
v1.0.0 - Initial contract
v1.1.0 - Add new optional field (backward compatible)
v2.0.0 - Remove field or change type (breaking change)
```

### Pact Tagging

```bash
# Tag pact with version
pact-broker create-version-tag \
  --pacticipant=TTA-Frontend \
  --version=1.0.0 \
  --tag=production
```

## Troubleshooting

### Pact Mock Server Not Starting

**Problem:** Mock server fails to start

**Solutions:**
- Check port availability
- Use explicit port: `pact = Consumer('Frontend').has_pact_with(Provider('API'), port=1234)`
- Check pact-python installation: `uv add --dev pact-python`
- Check logs: `cat ~/.pact/logs/pact-mock-service.log`

### Contract Verification Failing

**Problem:** Provider doesn't match contract

**Solutions:**
- Check provider state setup
- Verify API endpoint URLs
- Check response format matches contract
- Review pact file for expected format
- Ensure provider is running

### Matcher Issues

**Problem:** Matchers not working as expected

**Solutions:**
- Use `Like()` for type matching
- Use `Term()` for regex matching
- Use `EachLike()` for arrays
- Check matcher documentation
- Test matchers in isolation

## CI/CD Integration

Contract tests run on every PR:

```yaml
contract-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - name: Run contract tests
      run: uvx pytest tests/contracts/ -v
    - name: Upload pact files
      uses: actions/upload-artifact@v4
      with:
        name: pact-files
        path: tests/contracts/pacts/
```

## Resources

- [Pact Python Documentation](https://docs.pact.io/implementation_guides/python)
- [Pact Specification](https://github.com/pact-foundation/pact-specification)
- [Advanced Testing Methodology](../../docs/testing/ADVANCED_TESTING_METHODOLOGY.md)
- [Testing Strategy Summary](../../docs/testing/TESTING_STRATEGY_SUMMARY.md)

---

**Last Updated:** 2025-10-10
**Maintained by:** The Augster (AI Development Assistant)
