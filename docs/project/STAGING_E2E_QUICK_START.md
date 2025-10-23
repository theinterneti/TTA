# TTA Staging E2E Testing - Quick Start Guide

This guide will help you systematically validate your staging environment using Playwright to ensure users can play the game without any instruction.

## 🎯 Goal

Validate that a user with **ZERO instruction** can:
1. ✅ Sign in with OAuth
2. ✅ Navigate the dashboard intuitively
3. ✅ Create a character
4. ✅ Select a world
5. ✅ Start playing/chatting with AI
6. ✅ Have their data persist correctly

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Staging Environment

```bash
# Start all staging services
npm run staging:start

# Wait 30-60 seconds for services to initialize
# Check status
npm run staging:ps
```

**Expected Output:**
```
NAME                          STATUS
tta-staging-player-api        Up
tta-staging-frontend          Up
tta-staging-redis             Up
tta-staging-neo4j             Up
tta-staging-postgres          Up
```

### Step 2: Validate Environment

```bash
# Run validation checks
npm run staging:validate
```

**Expected Output:**
```
✓ Frontend (http://localhost:3001)... Running
✓ API Health (http://localhost:8081/health)... Accessible
✓ Redis (localhost:6380)... Running
✓ Neo4j (localhost:7688)... Running
✓ PostgreSQL (localhost:5433)... Running

✅ All checks passed! Staging environment is ready.
```

### Step 3: Run E2E Tests

```bash
# Run complete user journey test
npm run test:staging
```

**Expected Output:**
```
Running 1 test using 1 worker

  ✓ Complete User Journey - Staging Environment
    ✓ should complete full user journey from sign-in to gameplay (45s)

✅ All tests passed!
```

## 📊 What Gets Tested

### Complete User Journey Test

The test validates the entire user experience:

#### Phase 1: Landing & Authentication
- Application loads correctly
- Sign-in button is visible and discoverable
- OAuth flow works (or demo credentials)
- User successfully authenticates

#### Phase 2: Dashboard & Orientation
- Dashboard loads with welcoming content
- Clear next steps are visible
- Navigation is intuitive

#### Phase 3: Character Creation
- Character creation form is accessible
- Form is intuitive and easy to fill
- Character saves successfully to database

#### Phase 4: World Selection
- Available worlds are displayed clearly
- World selection is intuitive
- Selected world loads successfully

#### Phase 5: Gameplay / Chat Interface
- Chat interface loads properly
- Initial story content appears
- User can send messages
- AI responds appropriately
- Interaction is engaging

#### Phase 6: Data Persistence
- Session persists on page refresh
- Character data is saved (Neo4j)
- Story progress is maintained (Redis)
- No data loss

## 🎮 Interactive Testing

### Run with Visible Browser

```bash
# See the test run in real-time
npm run test:staging:headed
```

### Run with Playwright UI

```bash
# Interactive test runner with time-travel debugging
npm run test:staging:ui
```

### Debug Mode

```bash
# Step through tests with Playwright Inspector
npm run test:staging:debug
```

## 📈 Viewing Results

### HTML Report

```bash
# Open interactive HTML report
npm run test:staging:report
```

The report includes:
- ✅ Test results and timing
- 📸 Screenshots of failures
- 🎥 Videos of test runs
- 📊 Detailed step-by-step logs

### Console Output

The test provides detailed console output:

```
🎮 Starting Complete User Journey Test

📍 Phase 1: Landing & Authentication
  ✓ Application loaded
  ✓ Sign-in option is visible and discoverable
  ✓ Sign-in initiated
  ✓ Authentication successful

📍 Phase 2: Dashboard & Orientation
  ✓ Dashboard loaded
  ✓ Clear call-to-action visible

📍 Phase 3: Character Creation
  ✓ Navigated to character creation
  ✓ Character name entered
  ✓ Character created

📍 Phase 4: World Selection
  ✓ 5 worlds available
  ✓ World selected

📍 Phase 5: Gameplay / Chat Interface
  ✓ Chat interface loaded
  ✓ Initial story content received
  ✓ User input entered
  ✓ Message sent, awaiting response
  ✓ AI response received

📍 Phase 6: Data Persistence Validation
  ✓ Session persisted after refresh

✅ Complete User Journey Test PASSED!

🎉 User can successfully:
   ✓ Sign in with OAuth
   ✓ Navigate dashboard intuitively
   ✓ Create character
   ✓ Select world
   ✓ Play/chat with AI
   ✓ Data persists correctly
```

## 🔧 Configuration

### Environment Variables

Create `.env.staging` (optional, defaults work):

```bash
# Frontend
STAGING_BASE_URL=http://localhost:3001

# API
STAGING_API_URL=http://localhost:8081

# OAuth
USE_MOCK_OAUTH=true  # Use demo credentials for testing

# Databases (auto-configured by docker-compose)
REDIS_URL=redis://localhost:6380
NEO4J_URI=bolt://localhost:7688
DATABASE_URL=postgresql://localhost:5433/tta_staging
```

## 🐛 Troubleshooting

### Issue: Environment validation fails

**Error:** `Frontend not accessible at http://localhost:3001`

**Solution:**
```bash
# Check if containers are running
npm run staging:ps

# View logs
npm run staging:logs

# Restart if needed
npm run staging:stop
npm run staging:start
```

### Issue: Tests timeout

**Error:** `Test timeout of 300000ms exceeded`

**Solution:**
1. Check if AI model is responding (may be slow on first run)
2. Verify network connectivity
3. Run with `--headed` to see what's happening:
   ```bash
   npm run test:staging:headed
   ```

### Issue: OAuth fails

**Error:** OAuth flow doesn't complete

**Solution:**
1. Ensure `USE_MOCK_OAUTH=true` in `.env.staging`
2. Or configure real OAuth credentials
3. Check that demo credentials work: `demo_user` / `DemoPassword123!`

### Issue: Database connection fails

**Error:** `Redis not accessible`

**Solution:**
```bash
# Check database containers
docker ps | grep -E "redis|neo4j|postgres"

# Restart databases
docker-compose -f docker-compose.staging-homelab.yml restart redis-staging neo4j-staging postgres-staging
```

## 📚 Additional Resources

- **Detailed Documentation:** `tests/e2e-staging/README.md`
- **Test Code:** `tests/e2e-staging/complete-user-journey.staging.spec.ts`
- **Configuration:** `playwright.staging.config.ts`
- **Validation Script:** `scripts/validate-staging-environment.sh`

## 🎯 Success Criteria

Your staging environment is ready when:

✅ **All validation checks pass**
```bash
npm run staging:validate
# All services show ✓ Running
```

✅ **Complete user journey test passes**
```bash
npm run test:staging
# Test completes in <60 seconds
# All phases show ✓
```

✅ **Manual verification**
- Open http://localhost:3001 in browser
- Sign in with demo credentials
- Create character without confusion
- Select world intuitively
- Start chatting and get AI responses
- Refresh page - session persists

## 🚀 Next Steps

Once staging tests pass:

1. **Deploy to production** with confidence
2. **Run tests regularly** to catch regressions
3. **Add more test scenarios** as needed
4. **Monitor real user behavior** to validate assumptions

## 💡 Tips

- **Run tests before deploying** to catch issues early
- **Use headed mode** when developing new features
- **Check HTML report** for detailed failure analysis
- **Keep staging environment running** for faster test iterations
- **Update tests** when UI changes

## 🤝 Contributing

When adding new features:
1. Update the user journey test if flow changes
2. Add new test scenarios for new features
3. Ensure tests remain intuitive and clear
4. Document any new configuration needed

---

**Questions?** Check `tests/e2e-staging/README.md` for detailed documentation.

