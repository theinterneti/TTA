# TTA Staging - Prioritized Issues and Next Steps

**Date:** 2025-10-06
**Status:** 📋 ACTION PLAN
**Purpose:** Clear roadmap for addressing issues and completing testing

---

## Executive Summary

This document provides a prioritized list of all issues discovered during comprehensive testing, along with clear next steps for resolution. The issues are categorized by severity and impact, with specific recommendations for each.

**Critical Path:** Fix character creation → Re-test complete journey → Execute UAT/Performance/Accessibility testing

---

## 1. Critical Blockers (MUST FIX IMMEDIATELY)

### Issue #1: Character Creation Unavailable 🔴 CRITICAL

**Severity:** CRITICAL
**Impact:** Blocks complete user journey testing across all phases
**Priority:** P0 (Highest)
**Estimated Effort:** 4-8 hours

**Description:**
Character creation modal displays "Character creation is temporarily unavailable" error. The "Create Character" button on the dashboard is disabled, preventing users from creating characters and progressing through the application.

**Evidence:**
- Manual testing: Modal error message
- E2E testing: `TimeoutError: element is not enabled`
- Screenshots: `phase1-04-character-creation-unavailable.png`

**Root Cause Investigation Steps:**
1. Check API endpoint availability:
   ```bash
   curl -X POST http://localhost:8081/api/v1/characters \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"name":"Test Character","archetype":"hero"}'
   ```

2. Check backend logs:
   ```bash
   docker logs tta-staging-player-api --tail 100 | grep -i character
   ```

3. Verify database connectivity:
   ```bash
   # Check PostgreSQL
   docker exec -it tta-staging-postgres psql -U tta_user -d tta_db -c "SELECT * FROM characters LIMIT 1;"

   # Check Neo4j
   docker exec -it tta-staging-neo4j cypher-shell -u neo4j -p neo4j_password "MATCH (c:Character) RETURN c LIMIT 1;"
   ```

4. Check authentication token:
   - Verify token is being sent in request headers
   - Verify token is valid and not expired
   - Check token permissions

**Recommended Fix:**
1. Identify why API endpoint is unavailable or returning errors
2. Fix backend issue (database connection, authentication, validation, etc.)
3. Enable character creation button in frontend
4. Test character creation flow end-to-end
5. Verify data persists in database

**Verification:**
- [ ] API endpoint returns 200 OK
- [ ] Character creation modal opens successfully
- [ ] Character can be created with valid data
- [ ] Character appears in character list
- [ ] Character data persists in database
- [ ] E2E test passes

---

### Issue #2: Session Retrieval Infinite Loop 🔴 CRITICAL

**Severity:** CRITICAL
**Impact:** May cause data loss, performance issues, browser crashes
**Priority:** P0 (Highest)
**Estimated Effort:** 2-4 hours

**Description:**
Session restoration logic has infinite recursion, causing `RangeError: Maximum call stack size exceeded`. Console shows repeated "Failed to retrieve session data" errors.

**Evidence:**
- Browser console: `RangeError: Maximum call stack size exceeded`
- Location: `src/utils/sessionRestoration.ts`
- Repeated error messages in console

**Root Cause:**
Likely a recursive function call without proper base case or error handling.

**Recommended Fix:**
1. Review `sessionRestoration.ts` for recursive calls
2. Add proper base case to stop recursion
3. Add error handling to prevent infinite loops
4. Add retry limit (e.g., max 3 retries)
5. Add logging to track recursion depth

**Example Fix:**
```typescript
// Before (problematic)
async function retrieveSession() {
  try {
    const session = await api.getSession();
    return session;
  } catch (error) {
    return retrieveSession(); // Infinite recursion!
  }
}

// After (fixed)
async function retrieveSession(retries = 0, maxRetries = 3) {
  try {
    const session = await api.getSession();
    return session;
  } catch (error) {
    if (retries >= maxRetries) {
      console.error('Max retries reached for session retrieval');
      return null;
    }
    console.warn(`Session retrieval failed, retry ${retries + 1}/${maxRetries}`);
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s
    return retrieveSession(retries + 1, maxRetries);
  }
}
```

**Verification:**
- [ ] No more infinite loop errors in console
- [ ] Session retrieval works correctly
- [ ] Error handling prevents crashes
- [ ] Retry logic works as expected

---

### Issue #3: WebSocket Connection Failure 🟠 HIGH

**Severity:** HIGH
**Impact:** Real-time features unavailable (live updates, notifications)
**Priority:** P1
**Estimated Effort:** 1-2 hours

**Description:**
WebSocket attempting to connect to wrong port (3000 instead of 3001), causing connection failures.

**Evidence:**
- Browser console: `WebSocket connection to 'ws://localhost:3000/ws' failed`
- Expected: `ws://localhost:3001/ws`

**Root Cause:**
Hardcoded or misconfigured WebSocket URL in frontend.

**Recommended Fix:**
1. Find WebSocket URL configuration in frontend code
2. Update to use correct port (3001) or environment variable
3. Test WebSocket connection

**Locations to Check:**
```bash
# Search for WebSocket configuration
grep -r "ws://localhost:3000" src/
grep -r "WebSocket" src/ | grep -i "3000"
```

**Example Fix:**
```typescript
// Before
const ws = new WebSocket('ws://localhost:3000/ws');

// After
const ws = new WebSocket(`ws://${window.location.host}/ws`);
// Or use environment variable
const ws = new WebSocket(import.meta.env.VITE_WS_URL || 'ws://localhost:3001/ws');
```

**Verification:**
- [ ] WebSocket connects successfully
- [ ] No connection errors in console
- [ ] Real-time features work (if implemented)

---

## 2. High Priority Issues (FIX SOON)

### Issue #4: Frontend Health Check Failing 🟡 MEDIUM

**Severity:** MEDIUM
**Impact:** Container shows unhealthy status, may affect monitoring
**Priority:** P2
**Estimated Effort:** 1-2 hours

**Description:**
Frontend container shows "unhealthy" status despite service being accessible and functional.

**Evidence:**
- `docker ps`: Shows "unhealthy" status
- HTTP requests: Return 200 OK
- Service is functional

**Recommended Fix:**
1. Check health check configuration in `docker-compose.staging-homelab.yml`
2. Verify health check endpoint exists and returns correct status
3. Adjust health check interval/timeout if needed

**Verification:**
- [ ] Container shows "healthy" status
- [ ] Health check endpoint returns 200 OK
- [ ] Monitoring systems recognize healthy status

---

### Issue #5: TypeScript Type Errors 🟡 MEDIUM

**Severity:** MEDIUM
**Impact:** May cause runtime errors, reduces code quality
**Priority:** P2
**Estimated Effort:** 2-3 hours

**Description:**
Multiple TypeScript warnings in `sessionRestoration.ts` about properties not defined on response types.

**Recommended Fix:**
1. Define proper TypeScript interfaces for API responses
2. Add type guards for runtime validation
3. Fix type errors in `sessionRestoration.ts`

**Example:**
```typescript
interface SessionResponse {
  id: string;
  userId: string;
  characterId?: string;
  worldId?: string;
  storyId?: string;
  createdAt: string;
  updatedAt: string;
}

async function retrieveSession(): Promise<SessionResponse | null> {
  const response = await api.getSession();
  // Type-safe access to properties
  return response;
}
```

---

## 3. Medium Priority Issues (FIX WHEN POSSIBLE)

### Issue #6: Username Not Displayed on Dashboard 🟢 LOW

**Severity:** LOW
**Impact:** Minor UX issue, user doesn't see their name
**Priority:** P3
**Estimated Effort:** 1 hour

**Recommended Fix:**
1. Verify user data is being fetched
2. Add username display to dashboard
3. Handle cases where username is not available

---

### Issue #7: No Worlds Available for Browsing 🟢 LOW

**Severity:** LOW
**Impact:** Cannot test world selection (may be expected for new user)
**Priority:** P3
**Estimated Effort:** 2-4 hours

**Recommended Fix:**
1. Seed database with sample worlds
2. Or implement world creation functionality
3. Or document that this is expected for new users

---

### Issue #8: Grafana in Restart Loop 🟢 LOW

**Severity:** LOW
**Impact:** Monitoring dashboard unavailable (non-blocking)
**Priority:** P4
**Estimated Effort:** 1-2 hours

**Recommended Fix:**
1. Check Grafana logs for errors
2. Verify Grafana configuration
3. Fix configuration or disable if not needed for staging

---

### Issue #9: Nginx Not Started 🟢 LOW

**Severity:** LOW
**Impact:** Reverse proxy unavailable (services accessible directly)
**Priority:** P4
**Estimated Effort:** 1-2 hours

**Recommended Fix:**
1. Check Nginx configuration
2. Verify port mappings
3. Start Nginx or disable if not needed for staging

---

## 4. Test Infrastructure Improvements

### Improvement #1: Add data-testid Attributes 🟡 MEDIUM

**Priority:** P2
**Estimated Effort:** 4-6 hours

**Description:**
Add `data-testid` attributes to all interactive elements for more reliable test selectors.

**Recommended Implementation:**
```typescript
// Dashboard
<button data-testid="dashboard-create-character-button">Create First Character</button>

// Character Management
<button data-testid="character-create-button">Create Character</button>
<div data-testid="character-card-{id}">Character Card</div>

// World Selection
<div data-testid="world-card-{id}">World Card</div>
<button data-testid="world-select-button-{id}">Select World</button>

// Gameplay
<button data-testid="story-start-button">Start Story</button>
<button data-testid="choice-button-{index}">Choice Button</button>
```

**Benefits:**
- More reliable tests
- Easier to maintain
- Less brittle to UI changes

---

### Improvement #2: Implement Mock API Server 🟡 MEDIUM

**Priority:** P2
**Estimated Effort:** 8-12 hours

**Description:**
Create mock API server for E2E tests to enable UI testing when backend is incomplete.

**Recommended Implementation:**
1. Create `tests/e2e/mocks/api-server.ts`
2. Mock critical endpoints:
   - `POST /api/v1/characters`
   - `GET /api/v1/worlds`
   - `POST /api/v1/sessions`
   - `POST /api/v1/gameplay/action`
3. Add environment variable to toggle real/mock API
4. Update tests to use mock API when needed

**Benefits:**
- Can test UI flows independently
- Faster test execution
- More reliable tests (no external dependencies)

---

### Improvement #3: Enable Cross-Browser Testing 🟢 LOW

**Priority:** P3
**Estimated Effort:** 2-3 hours

**Description:**
Enable Firefox and WebKit testing in Playwright configuration.

**Recommended Implementation:**
```typescript
// playwright.staging.config.ts
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
],
```

**Benefits:**
- Catch browser-specific issues
- Ensure cross-browser compatibility
- Better test coverage

---

## 5. Next Steps Roadmap

### Week 1: Fix Critical Blockers

**Day 1-2: Character Creation**
- [ ] Investigate API endpoint issue
- [ ] Fix backend/database connectivity
- [ ] Enable character creation button
- [ ] Test end-to-end
- [ ] Verify E2E test passes

**Day 3: Session Restoration**
- [ ] Fix infinite loop in sessionRestoration.ts
- [ ] Add proper error handling
- [ ] Test session persistence
- [ ] Verify no console errors

**Day 4: WebSocket & Health Check**
- [ ] Fix WebSocket URL configuration
- [ ] Fix frontend health check
- [ ] Test real-time features
- [ ] Verify container health

**Day 5: Re-test Phases 1 & 2**
- [ ] Re-run manual testing
- [ ] Re-run E2E tests
- [ ] Verify complete user journey works
- [ ] Document results

---

### Week 2: Execute Full Testing Suite

**Day 1-2: Phase 3 (UAT)**
- [ ] Recruit 3-5 participants
- [ ] Conduct UAT sessions
- [ ] Collect feedback
- [ ] Analyze results
- [ ] Create UAT report

**Day 3: Phase 4 (Performance)**
- [ ] Run Lighthouse audits
- [ ] Measure API response times
- [ ] Test form submission times
- [ ] Test AI response times
- [ ] Create performance report

**Day 4: Phase 5 (Accessibility)**
- [ ] Run axe-core scans
- [ ] Test keyboard navigation
- [ ] Test with screen reader (if available)
- [ ] Check color contrast
- [ ] Create accessibility report

**Day 5: Final Report**
- [ ] Compile all findings
- [ ] Create prioritized issue list
- [ ] Document recommendations
- [ ] Present to stakeholders

---

### Week 3-4: Improvements & Optimization

**Test Infrastructure:**
- [ ] Add data-testid attributes
- [ ] Implement mock API server
- [ ] Enable cross-browser testing
- [ ] Fix TypeScript type errors

**Application Improvements:**
- [ ] Fix username display
- [ ] Seed sample worlds
- [ ] Fix Grafana/Nginx (if needed)
- [ ] Implement performance optimizations

**Documentation:**
- [ ] Update test documentation
- [ ] Create developer guide
- [ ] Document known issues
- [ ] Create troubleshooting guide

---

## 6. Success Criteria

### Phase 1 & 2 Re-test Success Criteria

- [ ] All staging services healthy (10/10)
- [ ] Authentication works flawlessly
- [ ] Character creation works end-to-end
- [ ] World selection works
- [ ] Story initialization works
- [ ] Gameplay works (3-5 choices)
- [ ] Data persists in databases
- [ ] E2E tests pass (100%)
- [ ] No critical errors in console

### Phase 3 (UAT) Success Criteria

- [ ] 3-5 participants recruited
- [ ] Task completion rate ≥80%
- [ ] Time to first story <5 minutes
- [ ] User satisfaction ≥7/10
- [ ] Engagement score ≥7/10
- [ ] Zero critical bugs
- [ ] Intuitive UI score ≥8/10

### Phase 4 (Performance) Success Criteria

- [ ] Form submissions <3 seconds
- [ ] AI responses <10 seconds
- [ ] Page load time <2 seconds
- [ ] API response time <200ms (95th percentile)
- [ ] Lighthouse performance score ≥80
- [ ] No performance bottlenecks identified

### Phase 5 (Accessibility) Success Criteria

- [ ] Zero critical accessibility violations
- [ ] All functionality keyboard accessible
- [ ] Screen reader compatible
- [ ] Color contrast ≥4.5:1 for normal text
- [ ] WCAG 2.1 Level AA compliant
- [ ] Lighthouse accessibility score ≥90

---

## 7. Conclusion

This prioritized action plan provides a clear roadmap for addressing all issues discovered during comprehensive testing. The critical path is:

1. **Fix character creation** (P0, 4-8 hours)
2. **Fix session restoration** (P0, 2-4 hours)
3. **Fix WebSocket URL** (P1, 1-2 hours)
4. **Re-test Phases 1 & 2** (1 day)
5. **Execute Phases 3-5** (1 week)
6. **Implement improvements** (2 weeks)

**Total Estimated Effort:** 3-4 weeks to complete all testing and improvements.

**Immediate Action:** Start with Issue #1 (Character Creation) as it blocks all other testing.

---

**Document Created:** 2025-10-06
**Created By:** The Augster (AI Development Assistant)
**Status:** ✅ ACTION PLAN READY
