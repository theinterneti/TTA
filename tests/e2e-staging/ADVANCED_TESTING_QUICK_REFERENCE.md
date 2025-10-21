# Advanced Testing Infrastructure - Quick Reference

## 🚀 5-Minute Setup

```bash
# 1. Install browsers
npm run browsers:install

# 2. Start staging
npm run staging:start
sleep 30

# 3. Run tests
npm run test:staging:advanced
```

## 📋 Test Commands Cheat Sheet

### Load Testing
```bash
npm run test:staging:load
```
Tests: 10, 25, 50 concurrent users
Duration: ~15 minutes

### Chaos Engineering
```bash
npm run test:staging:chaos
```
Tests: Network failures, DB disconnection, timeouts
Duration: ~5 minutes

### Security Testing
```bash
npm run test:staging:security
```
Tests: XSS, SQL injection, CSRF, auth bypass
Duration: ~3 minutes

### Visual Regression
```bash
npm run test:staging:visual
```
Tests: Screenshots, cross-browser, responsive
Duration: ~10 minutes

### All Advanced Tests
```bash
npm run test:staging:advanced
```
Duration: ~30 minutes

### All Tests (Core + Advanced)
```bash
npm run test:staging:all
```
Duration: ~45 minutes

## 🔧 Common Tasks

### Generate Test Data
```typescript
import { generateTestCharacter, generateTestWorld } from './helpers/test-data-management';

const character = generateTestCharacter();
const world = generateTestWorld();
```

### Seed Database
```typescript
import { seedNeo4jTestData } from './helpers/test-data-management';

await seedNeo4jTestData(character, world);
```

### Cleanup After Tests
```typescript
import { cleanupTestData } from './helpers/test-data-management';

await cleanupTestData();
```

### Simulate Network Failure
```typescript
import { simulateNetworkFailure } from './helpers/chaos-engineering-helpers';

await simulateNetworkFailure(page);
```

### Test XSS Vulnerability
```typescript
import { testXSSVulnerability } from './helpers/security-testing-helpers';

const result = await testXSSVulnerability(page, 'input[name="username"]');
```

### Compare Screenshots
```typescript
import { compareScreenshot } from './helpers/visual-regression-helpers';

const result = await compareScreenshot(page, 'login-page');
```

## 📊 Performance Budgets

| Metric | Budget |
|--------|--------|
| Page Load | < 3000ms |
| API Response | < 1000ms |
| AI Response | < 15000ms |
| Navigation | < 2000ms |
| CLS | < 0.1 |

## 🔐 GitHub Secrets Setup

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Go to GitHub repo → Settings → Secrets and variables → Actions
3. Add secret: `SLACK_WEBHOOK_URL` = your webhook URL

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.github/workflows/e2e-staging-advanced.yml` | CI/CD workflow |
| `tests/e2e-staging/helpers/load-testing-helpers.ts` | Load testing utilities |
| `tests/e2e-staging/helpers/chaos-engineering-helpers.ts` | Chaos testing utilities |
| `tests/e2e-staging/helpers/security-testing-helpers.ts` | Security testing utilities |
| `tests/e2e-staging/helpers/test-data-management.ts` | Test data utilities |
| `tests/e2e-staging/helpers/visual-regression-helpers.ts` | Visual testing utilities |
| `scripts/send-slack-notification.js` | Slack integration |
| `scripts/process-performance-metrics.js` | Performance tracking |

## 🎯 Load Test Scenarios

| Scenario | Users | Ramp-up | Duration |
|----------|-------|---------|----------|
| Light | 5 | 15s | 60s |
| Normal | 10 | 30s | 120s |
| High | 25 | 60s | 180s |
| Stress | 50 | 60s | 300s |

## 🔍 Security Tests

- ✅ XSS detection
- ✅ SQL injection detection
- ✅ CSRF token validation
- ✅ Authentication bypass prevention
- ✅ Authorization bypass prevention
- ✅ Sensitive data exposure
- ✅ Secure headers
- ✅ HTTPS enforcement

## 🎨 Visual Components Tested

- Login page
- Dashboard
- Character creation
- Gameplay interface
- Chat interface
- World selection

## 📱 Responsive Viewports

- Mobile small: 320x568
- Mobile large: 414x896
- Tablet: 768x1024
- Desktop: 1920x1080
- Desktop large: 2560x1440

## 🔄 Chaos Scenarios

- High latency (5s)
- Network failure
- Database disconnection
- Partial failures (50%)
- Timeout (30s)
- Circuit breaker
- Retry logic
- Graceful degradation

## 📈 Performance Metrics Tracked

- Total tests
- Passed tests
- Failed tests
- Pass rate
- Page load time
- API response time
- AI response latency
- 7-day trends
- Regression detection

## 🚨 Troubleshooting

### Tests Timeout
```bash
# Increase timeout in test
test.setTimeout(300000); // 5 minutes
```

### Slack Not Sending
```bash
# Verify webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_WEBHOOK_URL
```

### Visual Regression Fails
```bash
# Update baseline
compareScreenshot(page, 'test-name', {
  updateBaseline: true
})
```

### Load Test Fails
```bash
# Reduce concurrent users
const config = {
  concurrentUsers: 5,  // Reduce from 10
  ...
}
```

## 📚 Documentation

- **ADVANCED_TESTING_INFRASTRUCTURE.md** - Complete guide
- **.github/ADVANCED_TESTING_SETUP.md** - Setup instructions
- **ADVANCED_TESTING_IMPLEMENTATION_SUMMARY.md** - Implementation details
- **COMPREHENSIVE_E2E_GUIDE.md** - Core E2E guide

## 🎓 Helper Functions Quick Reference

### Load Testing
```typescript
simulateConcurrentUsers(config, userScenario)
calculateLoadTestMetrics(total, failed, times)
validateLoadTestResults(result, thresholds)
generateLoadTestReport(result)
```

### Chaos Engineering
```typescript
simulateNetworkLatency(page, ms)
simulateNetworkFailure(page)
simulateDatabaseDisconnection(page)
testGracefulDegradation(page, action)
testRecoveryFromFailure(page, failure, recovery)
testCircuitBreaker(page, endpoint, maxFailures)
generateChaosTestReport(results)
```

### Security Testing
```typescript
testXSSVulnerability(page, selector)
testSQLInjection(page, selector)
testCSRFProtection(page)
testAuthenticationBypass(page, url)
testAuthorizationBypass(page, url, role)
testSensitiveDataExposure(page)
testSecureHeaders(page)
testHTTPSEnforcement(page)
generateSecurityTestReport(results)
```

### Test Data Management
```typescript
generateTestCharacter(seed)
generateTestWorld(seed)
generateTestUser(seed)
seedRedisTestData(sessionId, data)
seedNeo4jTestData(character, world)
clearRedisTestData(pattern)
clearNeo4jTestData()
resetDatabaseState()
populateTestDatabase(charCount, worldCount)
cleanupTestData()
getTestDataStatistics()
```

### Visual Regression
```typescript
compareScreenshot(page, testName, config)
compareComponentAcrossBrowsers(pages, selector, testName)
compareMultipleViewports(page, testName, viewports)
takeFullPageScreenshot(page, testName)
takeElementScreenshot(page, selector, testName)
generateVisualRegressionReport(results)
cleanupVisualRegressionFiles(config, daysOld)
```

## ✅ Pre-Test Checklist

- [ ] Staging environment running
- [ ] Browsers installed
- [ ] GitHub Secrets configured
- [ ] Network connectivity verified
- [ ] Disk space available
- [ ] No other tests running

## 🎉 You're Ready!

All advanced testing infrastructure is set up and ready to use. Start with:

```bash
npm run test:staging:advanced
```

For detailed information, see:
- ADVANCED_TESTING_INFRASTRUCTURE.md
- .github/ADVANCED_TESTING_SETUP.md

