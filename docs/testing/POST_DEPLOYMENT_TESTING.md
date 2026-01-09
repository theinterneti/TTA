# Post-Deployment Testing Guide

## Overview

Post-deployment tests are automated integration tests that run after each deployment to verify that critical bug fixes remain effective in production environments. These tests validate that Issues #2, #3, and #4 have not regressed.

## Critical Issues Validated

### Issue #2: JWT Token Missing `player_id` Field
**Problem:** JWT tokens were missing the explicit `player_id` field, causing authentication issues.

**Fix:** JWT tokens now include both `sub` (user_id) and `player_id` fields.

**Tests:** `tests/post_deployment/test_jwt_token_validation.py`
- Verifies JWT contains `player_id` field
- Validates `player_id` matches user ID
- Tests backward compatibility with `sub` field
- Verifies token refresh maintains `player_id`

### Issue #3: Player Profile Auto-Creation Failing
**Problem:** Player profiles were not automatically created on first login, causing downstream errors.

**Fix:** Player profiles are now automatically created during authentication with fallback to user_id if creation fails.

**Tests:** `tests/post_deployment/test_player_profile_creation.py`
- Validates automatic profile creation on first login
- Verifies profile persistence in Neo4j
- Tests that existing users don't get duplicate profiles
- Validates graceful degradation if profile creation fails

### Issue #4: Frontend Deployment Cache Issues
**Problem:** Frontend changes weren't reflecting due to incorrect Docker build configuration and browser caching.

**Fix:** Dockerfile now copies from correct build directory (`/app/build`), uses proper build script, and includes cache-busting mechanisms.

**Tests:** `tests/post_deployment/test_frontend_deployment.py`
- Verifies frontend serves fresh builds
- Validates `index.html` has no-cache headers
- Tests static assets have proper cache headers
- Verifies environment variables are injected
- Validates frontend-backend communication

## Running Post-Deployment Tests

### Quick Start

```bash
# Run verification for staging environment
./scripts/verify-deployment.sh staging

# Run verification for production environment
./scripts/verify-deployment.sh production

# Run verification for local environment
./scripts/verify-deployment.sh local
```

### Manual Test Execution

```bash
# Set environment
export DEPLOYMENT_ENV=staging
export API_BASE_URL=http://localhost:8081
export FRONTEND_BASE_URL=http://localhost:3001

# Run all tests
uv run pytest tests/post_deployment/ -v

# Run specific test file
uv run pytest tests/post_deployment/test_jwt_token_validation.py -v

# Skip database tests (for production)
uv run pytest tests/post_deployment/ -v -m "not neo4j"
```

### Using the Test Runner Script

```bash
# Run with default settings
./scripts/run-post-deployment-tests.sh

# Specify environment
./scripts/run-post-deployment-tests.sh -e production

# Custom URLs
./scripts/run-post-deployment-tests.sh \
  -a http://localhost:8081 \
  -f http://localhost:3001

# Skip database tests
./scripts/run-post-deployment-tests.sh -m "not neo4j"
```

## CI/CD Integration

### Automatic Execution

Post-deployment tests run automatically after successful deployments:

1. **Staging Deployment** (`.github/workflows/deploy-staging.yml`)
   - Runs after health checks pass
   - Executes all tests including database validation
   - Fails deployment if tests fail

2. **Production Deployment** (`.github/workflows/deploy-production.yml`)
   - Runs after health checks pass
   - Skips tests that create test data (uses `-m "not neo4j"`)
   - Alerts on failure but doesn't block deployment

### Manual Trigger

```bash
# Trigger via GitHub Actions UI
# Navigate to: Actions → Post-Deployment Tests → Run workflow
# Select environment and optionally override URLs
```

## Configuration

### Environment Variables

| Variable | Description | Default (Staging) | Default (Production) |
|----------|-------------|-------------------|----------------------|
| `DEPLOYMENT_ENV` | Environment name | `staging` | `production` |
| `API_BASE_URL` | API base URL | `http://localhost:8081` | `https://api.tta.example.com` |
| `FRONTEND_BASE_URL` | Frontend base URL | `http://localhost:3001` | `https://tta.example.com` |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` | (from secrets) |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` | (from secrets) |
| `NEO4J_PASSWORD` | Neo4j password | `test_password` | (from secrets) |
| `REDIS_HOST` | Redis host | `localhost` | (from secrets) |
| `REDIS_PORT` | Redis port | `6379` | (from secrets) |
| `TEST_USER_USERNAME` | Test user username | `test_deployment_user` | (from secrets) |
| `TEST_USER_PASSWORD` | Test user password | `TestPassword123!` | (from secrets) |
| `TEST_USER_EMAIL` | Test user email | `test_deployment@example.com` | (from secrets) |

### GitHub Secrets

Configure these secrets in GitHub repository settings:

**Staging:**
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `TEST_USER_USERNAME`
- `TEST_USER_PASSWORD`
- `TEST_USER_EMAIL`

**Production:**
- `NEO4J_URI_PROD`
- `NEO4J_USERNAME_PROD`
- `NEO4J_PASSWORD_PROD`
- `REDIS_HOST_PROD`
- `REDIS_PORT_PROD`
- `REDIS_PASSWORD_PROD`
- `TEST_USER_USERNAME_PROD`
- `TEST_USER_PASSWORD_PROD`
- `TEST_USER_EMAIL_PROD`

## Test Structure

```
tests/post_deployment/
├── __init__.py                          # Package initialization
├── conftest.py                          # Shared fixtures
├── test_jwt_token_validation.py         # Issue #2 tests
├── test_player_profile_creation.py      # Issue #3 tests
└── test_frontend_deployment.py          # Issue #4 tests
```

## Writing New Post-Deployment Tests

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
        health_check: Health check result
    """
    auth_client, token_data = authenticated_client

    # Test implementation
    response = await auth_client.get("/api/v1/new-feature")
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "expected_field" in data
```

### Best Practices

1. **Read-Only Operations:** Tests should not modify production data
2. **Idempotent:** Tests should be repeatable without side effects
3. **Fast Execution:** Keep tests under 30 seconds each
4. **Clear Assertions:** Use descriptive assertion messages
5. **Environment Awareness:** Use `skip_if_production` fixture when needed
6. **Health Checks:** Always depend on `health_check` fixture

## Troubleshooting

### Tests Failing After Deployment

1. **Check Health Status:**
   ```bash
   curl http://localhost:8081/api/v1/health/
   ```

2. **Verify Environment Variables:**
   ```bash
   echo $API_BASE_URL
   echo $FRONTEND_BASE_URL
   ```

3. **Run Tests Locally:**
   ```bash
   ./scripts/verify-deployment.sh staging
   ```

4. **Check Test Logs:**
   - View GitHub Actions logs
   - Check `post-deployment-report.html`

### Common Issues

**Issue:** Tests timeout waiting for services
**Solution:** Increase health check retries or wait time

**Issue:** JWT validation fails
**Solution:** Verify Issue #2 fix is deployed, check token generation code

**Issue:** Player profile tests fail
**Solution:** Verify Neo4j is accessible, check Issue #3 fix deployment

**Issue:** Frontend tests fail
**Solution:** Verify frontend rebuild, check cache-busting, clear browser cache

## Maintenance

### Adding Tests for New Fixes

1. Create new test file in `tests/post_deployment/`
2. Follow naming convention: `test_<feature>_<issue_number>.py`
3. Add tests with clear documentation
4. Update this guide with new test coverage

### Updating Test Configuration

1. Modify `tests/post_deployment/conftest.py` for shared fixtures
2. Update environment URLs in deployment workflows
3. Add new secrets to GitHub repository settings
4. Update documentation

## References

- [Test Coverage Analysis](./TEST_COVERAGE_ANALYSIS.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Production Readiness Fixes](../PRODUCTION_READINESS_FIXES.md)
- [Frontend Deployment Fix](../FRONTEND_DEPLOYMENT_FIX.md)


---
**Logseq:** [[TTA.dev/Docs/Testing/Post_deployment_testing]]
