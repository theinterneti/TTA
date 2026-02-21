# Advanced Testing Infrastructure - Getting Started Guide

## 🎯 Your Complete Setup Roadmap

This guide walks you through setting up and using the advanced testing infrastructure step-by-step.

---

## 📋 Prerequisites

- Node.js 18+ installed
- Docker and Docker Compose installed
- GitHub repository access
- Slack workspace (for notifications)
- WSL2 environment (recommended)

---

## 🚀 Phase 1: Local Setup (15 minutes)

### Step 1.1: Install Playwright Browsers
```bash
cd /home/thein/recovered-tta-storytelling
npm run browsers:install
```
**What it does:** Downloads Chromium, Firefox, and WebKit browsers (~500MB)
**Time:** ~5 minutes
**Note:** Only needed once, browsers are cached locally

### Step 1.2: Start Staging Environment
```bash
npm run staging:start
sleep 30
```
**What it does:** Starts Docker containers for Redis, Neo4j, PostgreSQL, and APIs
**Time:** ~2 minutes
**Verify:** Run `npm run staging:ps` to see running containers

### Step 1.3: Verify Setup
```bash
npm run staging:validate
```
**What it does:** Checks that all services are running and accessible
**Expected output:** All services should show as "healthy"

---

## 🧪 Phase 2: Run Tests Locally (varies)

### Option A: Quick Test (3 minutes)
```bash
npm run test:staging:security
```
**Tests:** Security vulnerabilities only
**Good for:** Quick verification that setup works

### Option B: Load Testing (15 minutes)
```bash
npm run test:staging:load
```
**Tests:** 10, 25, and 50 concurrent users
**Good for:** Performance validation

### Option C: Chaos Engineering (5 minutes)
```bash
npm run test:staging:chaos
```
**Tests:** Network failures, timeouts, database disconnections
**Good for:** Resilience validation

### Option D: Visual Regression (10 minutes)
```bash
npm run test:staging:visual
```
**Tests:** UI consistency across browsers and viewports
**Good for:** UI regression detection

### Option E: All Advanced Tests (30 minutes)
```bash
npm run test:staging:advanced
```
**Tests:** All of the above combined
**Good for:** Comprehensive validation

### View Test Results
```bash
npm run test:staging:report
```
**What it does:** Opens HTML report in browser
**Shows:** Detailed test results, screenshots, videos

---

## 🔔 Phase 3: GitHub Setup (10 minutes)

### Step 3.1: Create Slack Webhook

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "TTA E2E Testing"
4. Select your workspace
5. Go to "Incoming Webhooks" → Toggle ON
6. Click "Add New Webhook to Workspace"
7. Select channel (e.g., #testing)
8. Copy the webhook URL

### Step 3.2: Add to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SLACK_WEBHOOK_URL`
5. Value: Paste webhook URL from step 3.1
6. Click "Add secret"

### Step 3.3: Verify Workflow

1. Go to Actions tab
2. Find "E2E Staging - Advanced Testing"
3. Click "Run workflow"
4. Select test type: "comprehensive"
5. Click "Run workflow"
6. Wait for completion (~30 minutes)
7. Check Slack for notification

---

## 📊 Phase 4: Monitor & Maintain (ongoing)

### Daily Checks
```bash
# Check staging health
npm run staging:ps

# View recent test results
npm run test:staging:report
```

### Weekly Tasks
```bash
# Run full test suite
npm run test:staging:all

# Check performance trends
# (View in GitHub Actions artifacts)
```

### Monthly Tasks
```bash
# Update visual regression baselines if UI changed
npm run test:staging:visual

# Review performance history
# (Check .github/performance-history.json)
```

---

## 🎯 Common Workflows

### Workflow 1: Before Merging PR
```bash
# 1. Run quick security check
npm run test:staging:security

# 2. Run load test
npm run test:staging:load

# 3. View results
npm run test:staging:report
```

### Workflow 2: After Deploying to Staging
```bash
# 1. Run all tests
npm run test:staging:all

# 2. Check for regressions
npm run test:staging:visual

# 3. Monitor performance
npm run test:staging:performance
```

### Workflow 3: Investigating Failures
```bash
# 1. Run specific test with debug output
npm run test:staging:debug

# 2. View detailed report
npm run test:staging:report

# 3. Check logs
npm run staging:logs
```

---

## 🔧 Troubleshooting

### Issue: Tests Timeout
**Solution:**
```bash
# Reduce concurrent users in load test
# Edit: tests/e2e-staging/helpers/load-testing-helpers.ts
# Change: concurrentUsers: 10 → concurrentUsers: 5
```

### Issue: Slack Notifications Not Sending
**Solution:**
1. Verify `SLACK_WEBHOOK_URL` is set in GitHub Secrets
2. Test webhook manually:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_WEBHOOK_URL
```

### Issue: Visual Regression Fails
**Solution:**
```bash
# Update baselines if UI intentionally changed
# Edit: tests/e2e-staging/13-visual-regression.staging.spec.ts
# Change: updateBaseline: false → updateBaseline: true
# Run test, then change back to false
```

### Issue: Staging Services Won't Start
**Solution:**
```bash
# Stop and restart
npm run staging:stop
sleep 5
npm run staging:start
sleep 30

# Check logs
npm run staging:logs
```

---

## 📚 Documentation Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| ADVANCED_TESTING_INFRASTRUCTURE.md | Complete feature guide | Need detailed info |
| ADVANCED_TESTING_QUICK_REFERENCE.md | Quick lookup | Need quick answers |
| ADVANCED_TESTING_SETUP.md | GitHub setup | Setting up GitHub |
| ADVANCED_TESTING_IMPLEMENTATION_SUMMARY.md | Implementation details | Understanding architecture |
| ADVANCED_TESTING_VERIFICATION_REPORT.md | Verification status | Confirming completeness |

---

## ✅ Success Checklist

- [ ] Browsers installed (`npm run browsers:install`)
- [ ] Staging environment running (`npm run staging:start`)
- [ ] Staging validated (`npm run staging:validate`)
- [ ] Quick test passed (`npm run test:staging:security`)
- [ ] Slack webhook created
- [ ] GitHub Secret added (`SLACK_WEBHOOK_URL`)
- [ ] GitHub Actions workflow enabled
- [ ] First workflow run completed
- [ ] Slack notification received
- [ ] Test report viewed

---

## 🎓 Learning Path

### Beginner (Day 1)
1. Read this guide
2. Run `npm run test:staging:security`
3. View test report
4. Setup GitHub Secrets

### Intermediate (Week 1)
1. Run all test types
2. Review test output
3. Enable GitHub Actions
4. Monitor first workflow run

### Advanced (Week 2+)
1. Customize test configurations
2. Add custom test scenarios
3. Integrate with monitoring tools
4. Optimize performance budgets

---

## 🚀 Next Steps

1. **Start Now:** Follow Phase 1 above
2. **Run Tests:** Follow Phase 2 above
3. **Setup GitHub:** Follow Phase 3 above
4. **Monitor:** Follow Phase 4 above

---

## 💡 Pro Tips

1. **Use `--headed` flag to see browser:**
   ```bash
   npx playwright test --config=playwright.staging.config.ts \
     tests/e2e-staging/10-load-testing.staging.spec.ts --headed
   ```

2. **Use `--debug` flag to step through tests:**
   ```bash
   npm run test:staging:debug
   ```

3. **Use `--ui` flag for interactive mode:**
   ```bash
   npm run test:staging:ui
   ```

4. **Run specific test only:**
   ```bash
   npx playwright test --config=playwright.staging.config.ts \
     tests/e2e-staging/10-load-testing.staging.spec.ts \
     -g "should handle 10 concurrent users"
   ```

---

## 📞 Need Help?

1. Check troubleshooting section above
2. Review ADVANCED_TESTING_INFRASTRUCTURE.md
3. Check GitHub Actions logs
4. Review test output and reports

---

## 🎉 You're Ready!

Everything is set up and ready to use. Start with Phase 1 and work your way through the phases. Good luck! 🚀

---

**Last Updated:** 2024
**Version:** 1.0.0
**Status:** Production-Ready


---
**Logseq:** [[TTA.dev/Docs/Project/Advanced_testing_getting_started]]
