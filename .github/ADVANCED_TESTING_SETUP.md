# Advanced Testing Infrastructure Setup Guide

## 🔧 Prerequisites

- GitHub repository with Actions enabled
- Slack workspace (for notifications)
- Staging environment running (Docker Compose)
- Node.js 18+ installed

## 📋 Step 1: Create Slack Webhook

### 1.1 Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "TTA E2E Testing"
5. Select your workspace
6. Click "Create App"

### 1.2 Enable Incoming Webhooks

1. In the app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to ON
3. Click "Add New Webhook to Workspace"
4. Select channel (e.g., #testing or #ci-cd)
5. Click "Allow"
6. Copy the webhook URL

### 1.3 Add to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SLACK_WEBHOOK_URL`
5. Value: Paste the webhook URL from step 1.2
6. Click "Add secret"

## 🔐 Step 2: Configure GitHub Secrets

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX` |

### Optional Secrets

| Secret Name | Description |
|-------------|-------------|
| `OPENROUTER_STAGING_KEY` | OpenRouter API key for staging |
| `SENTRY_STAGING_DSN` | Sentry DSN for error tracking |

## 🌍 Step 3: Configure Environment Variables

### Repository Variables

Go to Settings → Secrets and variables → Variables and add:

```
STAGING_BASE_URL=http://localhost:3001
STAGING_API_URL=http://localhost:8081
REDIS_URL=redis://localhost:6380
NEO4J_URI=bolt://localhost:7688
DATABASE_URL=postgresql://localhost:5433/tta_staging
USE_MOCK_OAUTH=true
```

## 🚀 Step 4: Enable GitHub Actions Workflow

### 4.1 Verify Workflow File

The workflow file is located at:
```
.github/workflows/e2e-staging-advanced.yml
```

### 4.2 Enable Workflow

1. Go to your GitHub repository
2. Click "Actions" tab
3. Find "E2E Staging - Advanced Testing"
4. Click "Enable workflow" if disabled

### 4.3 Test Workflow

1. Create a test branch
2. Make a small change to trigger workflow
3. Create a pull request
4. Workflow should run automatically
5. Check Slack for notification

## 📊 Step 5: Configure Performance Tracking

### 5.1 Create Performance History File

The workflow automatically creates:
```
.github/performance-history.json
```

This file tracks performance metrics over time.

### 5.2 Review Performance Trends

1. Go to Actions tab
2. Click on a completed workflow run
3. Download "performance-baseline" artifact
4. Review metrics and trends

## 🔔 Step 6: Test Slack Notifications

### 6.1 Manual Workflow Dispatch

1. Go to Actions tab
2. Select "E2E Staging - Advanced Testing"
3. Click "Run workflow"
4. Select test type: "comprehensive"
5. Click "Run workflow"
6. Wait for completion
7. Check Slack for notification

### 6.2 Verify Notification Format

Slack message should include:
- ✅ or ❌ status emoji
- Test statistics (passed/failed)
- Performance metrics
- Link to full report

## 🧪 Step 7: Run Tests Locally

### 7.1 Install Dependencies

```bash
npm install
npm run browsers:install
```

### 7.2 Start Staging Environment

```bash
npm run staging:start
sleep 30
```

### 7.3 Run Advanced Tests

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

### 7.4 View Reports

```bash
npm run test:staging:report
```

## 📈 Step 8: Monitor Performance Trends

### 8.1 Access Performance History

Performance metrics are stored in:
```
.github/performance-history.json
```

### 8.2 Analyze Trends

The file contains:
- Historical metrics (last 90 days)
- Performance baselines
- Regression detection results

### 8.3 Set Up Alerts

Configure GitHub Actions to fail if:
- Performance degrades > 20%
- Error rate exceeds threshold
- Tests fail

## 🔍 Step 9: Troubleshooting

### Workflow Not Running

**Problem:** Workflow doesn't trigger on PR
**Solution:**
1. Verify workflow file exists: `.github/workflows/e2e-staging-advanced.yml`
2. Check branch protection rules
3. Ensure Actions are enabled
4. Review workflow syntax

### Slack Notifications Not Sending

**Problem:** No Slack messages received
**Solution:**
1. Verify `SLACK_WEBHOOK_URL` is set correctly
2. Test webhook URL manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test"}' \
     YOUR_WEBHOOK_URL
   ```
3. Check GitHub Actions logs for errors
4. Verify Slack channel permissions

### Tests Timing Out

**Problem:** Tests exceed timeout
**Solution:**
1. Increase timeout in workflow: `timeout-minutes: 60`
2. Reduce concurrent user count in load tests
3. Check staging environment performance
4. Review system resources

### Performance Regression Detected

**Problem:** Workflow fails due to performance regression
**Solution:**
1. Review performance metrics in artifact
2. Identify which tests regressed
3. Investigate code changes
4. Optimize or revert changes
5. Re-run workflow

## 📚 Additional Configuration

### Custom Performance Budgets

Edit `tests/e2e-staging/helpers/staging-config.ts`:

```typescript
export const PERFORMANCE_BUDGETS = {
  pageLoad: 3000,      // ms
  apiResponse: 1000,   // ms
  aiResponse: 15000,   // ms
  navigation: 2000,    // ms
  cls: 0.1,           // Cumulative Layout Shift
};
```

### Custom Load Test Scenarios

Edit `tests/e2e-staging/helpers/load-testing-helpers.ts`:

```typescript
export const CUSTOM_LOAD_CONFIG: LoadTestConfig = {
  concurrentUsers: 100,
  rampUpTime: 120,
  testDuration: 600,
  thinkTime: 500,
};
```

### Custom Security Tests

Add new security tests in `tests/e2e-staging/12-security-testing.staging.spec.ts`

## ✅ Verification Checklist

- [ ] Slack webhook created and tested
- [ ] `SLACK_WEBHOOK_URL` added to GitHub Secrets
- [ ] Workflow file exists and is enabled
- [ ] Environment variables configured
- [ ] Tests run successfully locally
- [ ] Workflow triggers on PR
- [ ] Slack notifications received
- [ ] Performance metrics tracked
- [ ] All test suites passing

## 🎉 Setup Complete!

Your advanced testing infrastructure is now configured and ready to use. The workflow will:

1. Run on every PR to main/staging
2. Run nightly at 2 AM UTC
3. Send Slack notifications on completion
4. Track performance trends
5. Detect regressions automatically

## 📞 Support

For issues or questions:
1. Check GitHub Actions logs
2. Review test output
3. Consult Playwright documentation
4. Check Slack webhook status

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Slack API Documentation](https://api.slack.com)
- [Playwright Documentation](https://playwright.dev)
- [Advanced Testing Infrastructure Guide](../tests/e2e-staging/ADVANCED_TESTING_INFRASTRUCTURE.md)

