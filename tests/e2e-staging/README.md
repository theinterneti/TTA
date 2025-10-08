# TTA Staging Environment E2E Tests

Comprehensive Playwright-based validation suite for the TTA staging environment. These tests validate the complete user journey from OAuth sign-in to playing the collaborative storytelling game.

## 🎯 Purpose

Ensure that users can **intuitively use the staging environment with ZERO instruction**:
- ✅ Sign in with OAuth
- ✅ Navigate dashboard
- ✅ Create character
- ✅ Select world
- ✅ Play/chat with AI
- ✅ Data persists correctly

## 🏗️ Architecture

```
tests/e2e-staging/
├── complete-user-journey.staging.spec.ts  # Main end-to-end test
├── global-setup.ts                        # Environment validation
├── global-teardown.ts                     # Cleanup
└── README.md                              # This file

playwright.staging.config.ts               # Staging-specific config
scripts/
├── validate-staging-environment.sh        # Pre-test validation
└── run-staging-tests.sh                   # Test runner
```

## 🚀 Quick Start

### 1. Start Staging Environment

```bash
# Start all staging services
docker-compose -f docker-compose.staging-homelab.yml up -d

# Wait for services to be ready (30-60 seconds)
docker-compose -f docker-compose.staging-homelab.yml ps
```

### 2. Validate Environment

```bash
# Check that all services are accessible
./scripts/validate-staging-environment.sh
```

### 3. Run Tests

```bash
# Run all staging tests
./scripts/run-staging-tests.sh

# Run with visible browser
./scripts/run-staging-tests.sh --headed

# Run with Playwright UI (interactive)
./scripts/run-staging-tests.sh --ui

# Run in debug mode
./scripts/run-staging-tests.sh --debug
```

## 📊 Test Coverage

### Complete User Journey Test

**File:** `complete-user-journey.staging.spec.ts`

**Phases:**
1. **Landing & Authentication**
   - Application loads correctly
   - Sign-in option is visible and discoverable
   - OAuth flow works (or demo credentials)
   - Authentication succeeds

2. **Dashboard & Orientation**
   - Dashboard loads with welcoming content
   - Clear next steps are visible
   - Navigation is intuitive

3. **Character Creation**
   - Character creation form is accessible
   - Form is intuitive and easy to fill
   - Character saves successfully

4. **World Selection**
   - Available worlds are displayed
   - World selection is clear
   - World loads successfully

5. **Gameplay / Chat Interface**
   - Chat interface loads
   - Initial story content appears
   - User can send messages
   - AI responds appropriately

6. **Data Persistence**
   - Session persists on page refresh
   - Character data is saved
   - Story progress is maintained

### Error Handling Test

Validates graceful error handling:
- Network errors
- API failures
- Invalid inputs
- Session timeouts

## 🔧 Configuration

### Environment Variables

Create `.env.staging` (or use defaults):

```bash
# Frontend
STAGING_BASE_URL=http://localhost:3001

# API
STAGING_API_URL=http://localhost:8081

# Databases
REDIS_URL=redis://localhost:6380
NEO4J_URI=bolt://localhost:7688
DATABASE_URL=postgresql://localhost:5433/tta_staging

# OAuth (for real OAuth testing)
USE_MOCK_OAUTH=true  # Set to false for real OAuth
OPENROUTER_CLIENT_ID=your_client_id
OPENROUTER_CLIENT_SECRET=your_client_secret
```

### Playwright Configuration

**File:** `playwright.staging.config.ts`

Key settings:
- **Base URL:** `http://localhost:3001`
- **Workers:** 1 (sequential execution)
- **Timeout:** 5 minutes per test
- **Retries:** 1 (staging environment)
- **Browsers:** Chromium (primary), Mobile Chrome

## 📈 Viewing Results

### HTML Report

```bash
# Open interactive HTML report
npx playwright show-report playwright-staging-report
```

### JSON Results

```bash
# View JSON results
cat test-results-staging/results.json | jq
```

### Screenshots & Videos

Failed tests automatically capture:
- Screenshots: `test-results-staging/*.png`
- Videos: `test-results-staging/*.webm`
- Traces: `test-results-staging/*.zip`

## 🐛 Debugging

### Run Single Test

```bash
npx playwright test \
  --config=playwright.staging.config.ts \
  complete-user-journey.staging.spec.ts
```

### Debug Mode

```bash
# Opens browser with Playwright Inspector
./scripts/run-staging-tests.sh --debug
```

### UI Mode

```bash
# Interactive test runner
./scripts/run-staging-tests.sh --ui
```

### View Trace

```bash
# Open trace for failed test
npx playwright show-trace test-results-staging/trace.zip
```

## 🔍 Troubleshooting

### Environment Not Ready

**Error:** `Frontend not accessible at http://localhost:3001`

**Solution:**
```bash
# Check if containers are running
docker-compose -f docker-compose.staging-homelab.yml ps

# Restart if needed
docker-compose -f docker-compose.staging-homelab.yml restart

# Check logs
docker-compose -f docker-compose.staging-homelab.yml logs -f
```

### OAuth Issues

**Error:** OAuth flow fails

**Solution:**
1. Use mock OAuth for testing: `USE_MOCK_OAUTH=true`
2. Or configure real OAuth credentials in `.env.staging`
3. Check OpenRouter configuration

### Database Connection Issues

**Error:** Redis/Neo4j not accessible

**Solution:**
```bash
# Check database containers
docker-compose -f docker-compose.staging-homelab.yml ps redis-staging neo4j-staging

# Check ports
netstat -an | grep -E "6380|7688"

# Restart databases
docker-compose -f docker-compose.staging-homelab.yml restart redis-staging neo4j-staging
```

### Test Timeouts

**Error:** Test times out

**Solution:**
1. Increase timeout in `playwright.staging.config.ts`
2. Check if AI model is responding (may be slow)
3. Check network connectivity
4. Run with `--headed` to see what's happening

## 📝 Writing New Tests

### Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await test.step('Step 1: Description', async () => {
      // Test code
      console.log('  ✓ Step completed');
    });

    await test.step('Step 2: Description', async () => {
      // Test code
      console.log('  ✓ Step completed');
    });
  });
});
```

### Best Practices

1. **Use test.step()** for clear test structure
2. **Add console.log()** for progress tracking
3. **Use descriptive selectors** (data-testid preferred)
4. **Wait for network idle** after navigation
5. **Validate both UI and data** persistence
6. **Test error states** not just happy path

## 🎯 Success Criteria

Tests pass when:
- ✅ All phases complete without errors
- ✅ UI is intuitive (no confusing states)
- ✅ Data persists correctly
- ✅ AI responses are received
- ✅ No console errors
- ✅ Performance is acceptable (<30s total)

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev)
- [TTA Staging Deployment Guide](../../docs/staging-homelab/README.md)
- [OAuth Integration Guide](../../docs/security/oauth-integration.md)
- [Database Setup Guide](../../docs/infrastructure/database-setup.md)

## 🤝 Contributing

When adding new tests:
1. Follow existing test structure
2. Add clear console logging
3. Update this README
4. Test locally before committing
5. Ensure tests are idempotent

## 📞 Support

Issues? Check:
1. [Troubleshooting Guide](#-troubleshooting)
2. [GitHub Issues](https://github.com/theinterneti/TTA/issues)
3. Project documentation in `docs/`
