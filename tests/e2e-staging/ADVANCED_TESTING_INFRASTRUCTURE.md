# Advanced Testing Infrastructure for TTA Staging E2E Tests

## 📋 Overview

This document describes the advanced testing infrastructure enhancements for the TTA staging environment E2E test suite, including CI/CD integration, advanced monitoring, extended test coverage, test data management, and visual regression testing.

## 🚀 Quick Start

### 1. Install Browsers
```bash
npm run browsers:install
```

### 2. Start Staging Environment
```bash
npm run staging:start
sleep 30
```

### 3. Run Advanced Tests
```bash
# Load testing
npm run test:staging:load

# Chaos engineering
npm run test:staging:chaos

# Security testing
npm run test:staging:security

# Visual regression
npm run test:staging:visual

# All advanced tests
npm run test:staging:advanced
```

## 📊 1. CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/e2e-staging-advanced.yml`

**Features:**
- Automated E2E test execution on PRs and pushes
- Scheduled nightly tests (2 AM UTC)
- Performance trend tracking
- Slack notifications
- PR comments with test results

**Triggers:**
- Pull requests to `main` or `staging`
- Pushes to `staging` or `main`
- Scheduled nightly runs
- Manual workflow dispatch

**Jobs:**
1. **Setup** - Determines test type based on trigger
2. **Core E2E Tests** - Runs comprehensive test suite
3. **Load Testing** - Simulates concurrent users
4. **Performance Tracking** - Processes metrics and detects regressions
5. **Slack Notification** - Sends results to Slack

### Configuration

**Environment Variables:**
```bash
STAGING_BASE_URL=http://localhost:3001
STAGING_API_URL=http://localhost:8081
REDIS_URL=redis://localhost:6380
NEO4J_URI=bolt://localhost:7688
DATABASE_URL=postgresql://localhost:5433/tta_staging
USE_MOCK_OAUTH=true
```

**GitHub Secrets Required:**
- `SLACK_WEBHOOK_URL` - For Slack notifications

## 🔄 2. Advanced Monitoring

### Slack Notifications

**File:** `scripts/send-slack-notification.js`

**Features:**
- Test pass/fail summary
- Performance metrics
- Failed test details
- Links to full reports
- Color-coded status

**Setup:**
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add to GitHub Secrets as `SLACK_WEBHOOK_URL`
3. Notifications sent automatically on test completion

### Performance Tracking

**File:** `scripts/process-performance-metrics.js`

**Features:**
- Baseline establishment
- Regression detection (20% threshold)
- 7-day trend analysis
- Historical comparison
- Automatic baseline updates

**Metrics Tracked:**
- Page load time
- API response time
- AI response latency
- Test pass rate

## 📈 3. Extended Test Coverage

### Load Testing

**File:** `tests/e2e-staging/10-load-testing.staging.spec.ts`

**Helper:** `tests/e2e-staging/helpers/load-testing-helpers.ts`

**Test Scenarios:**
- 10 concurrent users (normal load)
- 25 concurrent users (high load)
- 50 concurrent users (stress test)

**Metrics:**
- Total requests
- Success/failure rates
- Response time percentiles (P95, P99)
- Throughput (req/s)
- Error rate

**Run:**
```bash
npm run test:staging:load
```

### Chaos Engineering

**File:** `tests/e2e-staging/11-chaos-engineering.staging.spec.ts`

**Helper:** `tests/e2e-staging/helpers/chaos-engineering-helpers.ts`

**Scenarios:**
- High network latency (5s)
- Network failure
- Database disconnection
- Partial service failure (50%)
- Timeout simulation
- Circuit breaker validation
- Retry logic testing

**Run:**
```bash
npm run test:staging:chaos
```

### Security Testing

**File:** `tests/e2e-staging/12-security-testing.staging.spec.ts`

**Helper:** `tests/e2e-staging/helpers/security-testing-helpers.ts`

**Tests:**
- XSS (Cross-Site Scripting) detection
- SQL Injection detection
- CSRF token validation
- Authentication bypass prevention
- Authorization bypass prevention
- Sensitive data exposure checks
- Secure headers validation
- HTTPS enforcement

**Run:**
```bash
npm run test:staging:security
```

## 🗂️ 4. Test Data Management

**File:** `tests/e2e-staging/helpers/test-data-management.ts`

**Features:**
- Automated test data generation
- Database seeding (Redis & Neo4j)
- Test data cleanup
- Database state reset
- Test dataset creation

**Functions:**
```typescript
// Generate test data
generateTestCharacter(seed?: number): TestCharacter
generateTestWorld(seed?: number): TestWorld
generateTestUser(seed?: number): TestUser

// Seed databases
seedRedisTestData(sessionId: string, userData: Record<string, any>)
seedNeo4jTestData(character: TestCharacter, world: TestWorld)

// Cleanup
clearRedisTestData(pattern?: string)
clearNeo4jTestData()
resetDatabaseState()

// Utilities
populateTestDatabase(characterCount?: number, worldCount?: number)
cleanupTestData()
getTestDataStatistics()
```

**Usage:**
```typescript
import { generateTestCharacter, seedNeo4jTestData, cleanupTestData } from './helpers/test-data-management';

// Generate test data
const character = generateTestCharacter();
const world = generateTestWorld();

// Seed database
await seedNeo4jTestData(character, world);

// Cleanup after tests
await cleanupTestData();
```

## 🎨 5. Visual Regression Testing

**File:** `tests/e2e-staging/13-visual-regression.staging.spec.ts`

**Helper:** `tests/e2e-staging/helpers/visual-regression-helpers.ts`

**Features:**
- Screenshot comparison with baselines
- Cross-browser visual validation
- Responsive design testing
- Visual diff generation
- Component snapshot testing

**Critical Components:**
- Login page
- Dashboard
- Character creation
- Gameplay interface
- Chat interface
- World selection

**Viewports Tested:**
- Mobile small (320x568)
- Mobile large (414x896)
- Tablet (768x1024)
- Desktop (1920x1080)
- Desktop large (2560x1440)

**Run:**
```bash
npm run test:staging:visual
```

## 📝 Test Commands

### Individual Test Suites
```bash
npm run test:staging:load          # Load testing
npm run test:staging:chaos         # Chaos engineering
npm run test:staging:security      # Security testing
npm run test:staging:visual        # Visual regression
```

### Combined Suites
```bash
npm run test:staging:advanced      # All advanced tests
npm run test:staging:all           # All tests (core + advanced)
npm run test:staging:all-comprehensive  # Core comprehensive tests
```

### Existing Test Suites
```bash
npm run test:staging:auth          # Authentication
npm run test:staging:ui-func       # UI functionality
npm run test:staging:integration   # Integration
npm run test:staging:errors        # Error handling
npm run test:staging:responsive    # Responsive design
npm run test:staging:a11y          # Accessibility
npm run test:staging:journey       # Complete user journey
npm run test:staging:persistence   # Data persistence
npm run test:staging:performance   # Performance monitoring
```

### Browser-Specific
```bash
npm run test:staging:chromium      # Chromium only
npm run test:staging:firefox       # Firefox only
npm run test:staging:webkit        # WebKit only
```

### Interactive Modes
```bash
npm run test:staging:headed        # Visible browser
npm run test:staging:ui            # UI mode
npm run test:staging:debug         # Debug mode
```

## 📊 Performance Budgets

- **Page Load:** < 3000ms
- **API Response:** < 1000ms
- **AI Response:** < 15000ms
- **Navigation:** < 2000ms
- **CLS (Cumulative Layout Shift):** < 0.1

## 🔐 Security Considerations

- Store `SLACK_WEBHOOK_URL` in GitHub Secrets
- Never commit sensitive credentials
- Use environment variables for configuration
- Validate all test data before use
- Sanitize test output in logs

## 📁 File Structure

```
tests/e2e-staging/
├── helpers/
│   ├── load-testing-helpers.ts
│   ├── chaos-engineering-helpers.ts
│   ├── security-testing-helpers.ts
│   ├── test-data-management.ts
│   └── visual-regression-helpers.ts
├── 10-load-testing.staging.spec.ts
├── 11-chaos-engineering.staging.spec.ts
├── 12-security-testing.staging.spec.ts
├── 13-visual-regression.staging.spec.ts
└── visual-baselines/
    └── (baseline screenshots)

.github/workflows/
└── e2e-staging-advanced.yml

scripts/
├── send-slack-notification.js
└── process-performance-metrics.js
```

## 🎯 Success Criteria

- ✅ GitHub Actions workflow runs successfully
- ✅ Performance trends tracked over time
- ✅ Slack notifications sent within 1 minute
- ✅ Load tests handle 10+ concurrent users
- ✅ Visual regression tests catch UI changes
- ✅ Security tests identify vulnerabilities
- ✅ Chaos tests validate resilience
- ✅ Test data management reduces setup time to zero

## 🚨 Troubleshooting

### Tests Timing Out
- Increase timeout in test configuration
- Check staging environment is running
- Verify network connectivity

### Slack Notifications Not Sending
- Verify `SLACK_WEBHOOK_URL` is set in GitHub Secrets
- Check webhook URL is valid
- Review GitHub Actions logs

### Visual Regression Failures
- Update baselines: `updateBaseline: true`
- Check for intentional UI changes
- Review diff files in `visual-diffs/`

### Load Test Failures
- Reduce concurrent user count
- Increase test duration
- Check system resources

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Slack API Documentation](https://api.slack.com)
- [Performance Testing Best Practices](https://web.dev/performance/)

## ✅ Implementation Complete

All advanced testing infrastructure enhancements are ready for use. Start with the quick start guide and gradually integrate advanced tests into your CI/CD pipeline.


---
**Logseq:** [[TTA.dev/Tests/E2e-staging/Advanced_testing_infrastructure]]
