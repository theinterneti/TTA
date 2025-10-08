# Post-Deployment Integration Tests

## Purpose

This directory contains automated integration tests that run after each deployment to verify that critical bug fixes remain effective in production environments.

## Critical Issues Validated

### Issue #2: JWT Token Missing `player_id` Field
- **Test File:** `test_jwt_token_validation.py`
- **Validates:** JWT tokens contain explicit `player_id` field
- **Prevents:** Authentication failures due to missing player identification

### Issue #3: Player Profile Auto-Creation Failing
- **Test File:** `test_player_profile_creation.py`
- **Validates:** Automatic player profile creation on first login
- **Prevents:** Downstream errors from missing player profiles

### Issue #4: Frontend Deployment Cache Issues
- **Test File:** `test_frontend_deployment.py`
- **Validates:** Fresh frontend builds are deployed without cache issues
- **Prevents:** Stale frontend code being served to users

## Quick Start

### Run All Post-Deployment Tests

```bash
# Using verification script (recommended)
./scripts/verify-deployment.sh staging

# Using pytest directly
export DEPLOYMENT_ENV=staging
export API_BASE_URL=http://localhost:8081
export FRONTEND_BASE_URL=http://localhost:3001
uv run pytest tests/post_deployment/ -v
```

### Run Specific Test Suite

```bash
# JWT validation tests
uv run pytest tests/post_deployment/test_jwt_token_validation.py -v

# Player profile tests
uv run pytest tests/post_deployment/test_player_profile_creation.py -v

# Frontend deployment tests
uv run pytest tests/post_deployment/test_frontend_deployment.py -v
```

### Skip Database Tests (Production)

```bash
# Skip tests that require Neo4j access
uv run pytest tests/post_deployment/ -v -m "not neo4j"
```

## Test Structure

```
tests/post_deployment/
├── __init__.py                          # Package initialization
├── conftest.py                          # Shared fixtures and configuration
├── test_jwt_token_validation.py         # Issue #2: JWT token tests
├── test_player_profile_creation.py      # Issue #3: Player profile tests
└── test_frontend_deployment.py          # Issue #4: Frontend deployment tests
```

## Fixtures

### Environment Configuration
- `deployment_env` - Environment name (staging, production, local)
- `api_base_url` - API base URL for the environment
- `frontend_base_url` - Frontend base URL for the environment

### API Clients
- `api_client` - Async HTTP client for API requests
- `authenticated_client` - Pre-authenticated client with test user

### Health Checks
- `health_check` - Validates system health before running tests

### Database Configuration
- `neo4j_config` - Neo4j connection settings
- `redis_config` - Redis connection settings

### Test Data
- `test_user_credentials` - Test user credentials for authentication

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_ENV` | Environment to test | `staging` |
| `API_BASE_URL` | API base URL | `http://localhost:8081` |
| `FRONTEND_BASE_URL` | Frontend base URL | `http://localhost:3001` |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `test_password` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `TEST_USER_USERNAME` | Test user username | `test_deployment_user` |
| `TEST_USER_PASSWORD` | Test user password | `TestPassword123!` |

## CI/CD Integration

These tests run automatically after deployments:

### Staging
- Workflow: `.github/workflows/deploy-staging.yml`
- Trigger: After successful staging deployment
- Markers: All tests (including database tests)
- Failure: Blocks deployment

### Production
- Workflow: `.github/workflows/deploy-production.yml`
- Trigger: After successful production deployment
- Markers: `-m "not neo4j"` (skips database tests)
- Failure: Alerts but doesn't block

### Manual Trigger
- Workflow: `.github/workflows/post-deployment-tests.yml`
- Trigger: Manual via GitHub Actions UI
- Configuration: Select environment and override URLs

## Writing New Tests

### Test Template

```python
import pytest

@pytest.mark.asyncio
async def test_new_feature_validation(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that new feature works after deployment.

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result (ensures system is ready)
    """
    auth_client, token_data = authenticated_client

    # Make API request
    response = await auth_client.get("/api/v1/new-feature")

    # Validate response
    assert response.status_code == 200, (
        f"New feature endpoint failed: {response.text}"
    )

    data = response.json()
    assert "expected_field" in data, (
        "Response missing expected field. "
        "Feature may have regressed."
    )
```

### Best Practices

1. **Read-Only:** Tests should not modify production data
2. **Idempotent:** Tests should be repeatable without side effects
3. **Fast:** Keep tests under 30 seconds each
4. **Clear Messages:** Use descriptive assertion messages
5. **Health Checks:** Always depend on `health_check` fixture
6. **Environment Aware:** Use `skip_if_production` when needed

## Troubleshooting

### Tests Timeout
**Cause:** Services not ready
**Solution:** Check health endpoints, increase wait time

### JWT Validation Fails
**Cause:** Issue #2 fix regressed
**Solution:** Verify token generation includes `player_id` field

### Player Profile Tests Fail
**Cause:** Issue #3 fix regressed or Neo4j unavailable
**Solution:** Check auto-creation logic, verify Neo4j connection

### Frontend Tests Fail
**Cause:** Issue #4 fix regressed or cache issues
**Solution:** Verify Docker build, check cache-busting, rebuild frontend

## Documentation

- **Detailed Guide:** [docs/testing/POST_DEPLOYMENT_TESTING.md](../../docs/testing/POST_DEPLOYMENT_TESTING.md)
- **Test Coverage:** [docs/testing/TEST_COVERAGE_ANALYSIS.md](../../docs/testing/TEST_COVERAGE_ANALYSIS.md)
- **Production Fixes:** [docs/PRODUCTION_READINESS_FIXES.md](../../docs/PRODUCTION_READINESS_FIXES.md)
- **Frontend Fix:** [docs/FRONTEND_DEPLOYMENT_FIX.md](../../docs/FRONTEND_DEPLOYMENT_FIX.md)

## Maintenance

### Adding New Tests

1. Create test file: `test_<feature>_<issue_number>.py`
2. Add tests with clear documentation
3. Update this README
4. Update main documentation

### Updating Configuration

1. Modify `conftest.py` for shared fixtures
2. Update environment variables in workflows
3. Add secrets to GitHub repository settings
4. Update documentation
