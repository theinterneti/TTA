# E2E Testing Quick Start Guide

Get started with comprehensive E2E testing in 5 minutes!

## 🚀 5-Minute Setup

### Step 1: Install Browsers (1 min)
```bash
npm run browsers:install
# Or: npx playwright install chromium firefox webkit --force
```

### Step 2: Start Staging Environment (2 min)
```bash
docker-compose -f docker-compose.staging-homelab.yml up -d
sleep 30  # Wait for services to start
```

### Step 3: Verify Services (1 min)
```bash
./scripts/validate-staging-environment.sh
```

### Step 4: Run Tests (1 min)
```bash
npm run test:staging
```

## 📋 Common Commands

### Run All Tests
```bash
npm run test:staging
```

### Run Specific Test Suite
```bash
# Complete user journey (OAuth → Gameplay)
npm run test:staging:journey

# Data persistence (Redis/Neo4j)
npm run test:staging:persistence

# Performance monitoring
npm run test:staging:performance

# All new comprehensive tests
npm run test:staging:all-comprehensive
```

### Run with Visible Browser
```bash
npm run test:staging:headed
```

### Run in Interactive Mode
```bash
npm run test:staging:ui
```

### Run in Debug Mode
```bash
npm run test:staging:debug
```

### Run on Specific Browser
```bash
npm run test:staging:chromium
npm run test:staging:firefox
npm run test:staging:webkit
```

### View Test Report
```bash
npm run test:staging:report
```

## 📊 What Gets Tested

### ✅ Complete User Journey
- Login with demo credentials
- Navigate dashboard
- Create character
- Select world
- Play collaborative storytelling game
- Verify data persists
- Logout

### ✅ Data Persistence
- Session data in Redis
- Character data in Neo4j
- Progress across sessions
- Database consistency
- Concurrent updates
- Database resilience

### ✅ Performance
- Page load times
- API response times
- AI response latency
- Layout stability
- Extended session performance

### ✅ Browser Compatibility
- Chromium
- Firefox
- WebKit
- Mobile viewports
- Tablet viewports

### ✅ Existing Tests
- Authentication flows
- UI/UX functionality
- API integration
- Error handling
- Responsive design
- Accessibility

## 📈 Expected Results

**Successful Test Run:**
```
✓ Complete User Journey - OAuth to Gameplay
  ✓ should complete full user journey from login to gameplay
  ✓ should maintain data consistency across page reloads
  ✓ should handle multiple interactions smoothly

✓ Data Persistence - Redis & Neo4j
  ✓ should verify Redis is accessible
  ✓ should verify Neo4j is accessible
  ✓ should persist session data in Redis
  ✓ should persist character data in Neo4j
  ✓ should persist game progress across sessions
  ✓ should maintain data consistency between Redis and Neo4j
  ✓ should handle concurrent data updates
  ✓ should recover from database connection loss

✓ Performance Monitoring
  ✓ should load login page within performance budget
  ✓ should load dashboard within performance budget
  ✓ should respond to API calls within budget
  ✓ should handle AI responses within acceptable time
  ✓ should maintain performance during extended gameplay
  ✓ should not have layout shifts during interaction
  ✓ should generate performance report
  ✓ should handle rapid interactions without degradation

Passed: 40+ tests
```

## 🔍 Viewing Results

### HTML Report
```bash
npm run test:staging:report
# Opens: playwright-staging-report/index.html
```

### JSON Results
```bash
cat test-results-staging/results.json
```

### JUnit XML
```bash
cat test-results-staging/results.xml
```

### Screenshots
```bash
ls test-results-staging/screenshots/
```

### Videos
```bash
ls test-results-staging/videos/
```

## 🐛 Troubleshooting

### Browsers Won't Install
```bash
# Kill stuck processes
pkill -f "chrome|firefox|webkit"

# Remove lockfiles
rm -rf ~/.cache/ms-playwright/__dirlock

# Try again
npm run browsers:install
```

### Tests Timeout
```bash
# Check if staging is running
docker-compose -f docker-compose.staging-homelab.yml ps

# Check logs
docker-compose -f docker-compose.staging-homelab.yml logs

# Restart services
docker-compose -f docker-compose.staging-homelab.yml restart
```

### Database Connection Issues
```bash
# Check Redis
redis-cli -p 6380 ping

# Check Neo4j
curl -u neo4j:password http://localhost:7474/db/neo4j/exec

# Check PostgreSQL
psql -h localhost -p 5433 -U tta_user -d tta_staging_db
```

### Tests Fail with "Page not found"
```bash
# Verify frontend is running
curl http://localhost:3001

# Check API is running
curl http://localhost:8081/api/v1/health

# Check environment variables
echo $STAGING_BASE_URL
echo $STAGING_API_URL
```

## 🎯 Success Criteria

Tests pass when:
- ✅ All user flows complete without errors
- ✅ Data persists in Redis and Neo4j
- ✅ Performance meets budgets
- ✅ No console errors
- ✅ All browsers compatible
- ✅ Responsive on all viewports

## 📚 More Information

- **Full Guide**: `COMPREHENSIVE_E2E_GUIDE.md`
- **Implementation Details**: `E2E_TESTING_IMPLEMENTATION_COMPLETE.md`
- **Original Docs**: `README.md`

## 💡 Tips

1. **First Time?** Start with `npm run test:staging:journey`
2. **Debugging?** Use `npm run test:staging:debug`
3. **Seeing Browser?** Use `npm run test:staging:headed`
4. **Interactive?** Use `npm run test:staging:ui`
5. **Reports?** Use `npm run test:staging:report`

## 🚀 Ready to Test?

```bash
# One command to run everything
npm run test:staging
```

That's it! 🎉


---
**Logseq:** [[TTA.dev/Tests/E2e-staging/Quick_start]]
