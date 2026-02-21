# TTA Staging E2E Validation - Issues and Fixes Tracker

**Status:** 🔴 ACTIVE - 8 issues identified, 0 resolved
**Last Updated:** 2025-10-15
**Next Review:** After CRITICAL issues resolved

---

## Issue Priority Legend

- 🔴 **CRITICAL** - Production blocker, must fix immediately
- 🟠 **HIGH** - Significant impact, fix before production
- 🟡 **MEDIUM** - Should fix, but not blocking
- 🟢 **LOW** - Nice to have, can defer

---

## 🔴 CRITICAL ISSUES

### CRITICAL-001: Session Persistence Failure ⏳ NOT STARTED

**Priority:** 🔴 CRITICAL
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 4-8 hours
**Blocking:** Production deployment

**Problem:**
Users are logged out immediately after page refresh. Session cookies not persisting.

**Impact:**
- Users cannot use the application normally
- Every page refresh requires re-login
- Breaks core user experience
- Production blocker

**Reproduction:**
1. Login with demo credentials
2. Reach dashboard successfully
3. Refresh page (F5)
4. **BUG:** Redirected to login page

**Root Cause Hypotheses:**
1. Session cookie attributes incorrect (httpOnly, secure, sameSite, path, domain)
2. Redis session not being created/stored
3. Session validation failing on page load
4. Frontend not sending cookie with requests
5. Cookie domain/path mismatch

**Investigation Steps:**

```bash
# Step 1: Check if session is created in Redis
docker exec -it tta-staging-redis redis-cli
KEYS session:*
# Should show session keys after login

# Step 2: Inspect session data
GET session:<session-id>
# Should show session data

# Step 3: Check session TTL
TTL session:<session-id>
# Should show positive number (seconds until expiration)

# Step 4: Monitor Redis during login
MONITOR
# Then login in browser and watch Redis commands
```

**Browser DevTools Investigation:**
1. Open DevTools → Network tab
2. Login with demo credentials
3. Check Response Headers for Set-Cookie
4. Verify cookie attributes:
   - `httpOnly=true`
   - `secure=false` (for localhost)
   - `sameSite=Lax` or `Strict`
   - `path=/`
   - `domain=localhost`
5. Check Application → Cookies
6. Verify cookie is present after login
7. Refresh page and check if cookie is sent in Request Headers

**Code Locations to Check:**

```
Backend (player-api-staging):
- Session middleware configuration
- Cookie options in session setup
- Session store (Redis) configuration
- Authentication endpoint response

Frontend (player-frontend-staging):
- Axios/fetch configuration (withCredentials)
- API client setup
- Auth context/provider
- Protected route logic
```

**Recommended Fix (Backend):**

```typescript
// In session middleware configuration
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: false, // Set to true in production with HTTPS
    sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    path: '/',
    domain: 'localhost' // Or appropriate domain
  }
}));
```

**Recommended Fix (Frontend):**

```typescript
// In API client configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8081',
  withCredentials: true, // CRITICAL: Send cookies with requests
  headers: {
    'Content-Type': 'application/json'
  }
});
```

**Verification:**
1. Login with demo credentials
2. Verify session cookie in DevTools
3. Refresh page
4. Verify still on dashboard (not redirected to login)
5. Check Redis for active session
6. Run Phase 1 authentication tests
7. Verify "should persist session after page refresh" test passes

**Success Criteria:**
- ✅ Session cookie visible in DevTools after login
- ✅ Session data in Redis after login
- ✅ Page refresh keeps user authenticated
- ✅ Test "should persist session after page refresh" passes

---

### CRITICAL-002: Dashboard Heading Mismatch ⏳ NOT STARTED

**Priority:** 🟡 MEDIUM (Test Issue) / 🟢 LOW (UX Issue)
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 30 minutes
**Blocking:** Test validation (not production)

**Problem:**
Tests expect dashboard heading to contain "Dashboard", "Welcome", or "Home", but actual heading is "Adventure Platform".

**Impact:**
- Test failures even though functionality works
- False negative in validation results
- Not a production blocker (UI works correctly)

**Current State:**
```yaml
# Actual page content
heading "Adventure Platform" [level=1]
paragraph: Your Personal Story Experience
```

**Test Expectation:**
```typescript
// In DashboardPage.ts
await this.expectText('h1, h2', /dashboard|welcome|home/i);
```

**Recommended Fix (OPTION A - Update Tests):**

```typescript
// File: tests/e2e-staging/page-objects/DashboardPage.ts
// Line: ~183

async expectDashboardLoaded(): Promise<void> {
  // Update regex to accept "Adventure Platform"
  await this.expectText('h1, h2', /adventure platform|dashboard|welcome|home/i);

  // Or be more specific
  await this.expectText('h1', /adventure platform/i);
}
```

**Alternative Fix (OPTION B - Update Frontend):**

```typescript
// File: tta.dev/player-frontend/src/pages/Dashboard.tsx
// Change heading to match test expectations

<h1>Welcome to Your Dashboard</h1>
<p>Your Personal Story Experience</p>
```

**Recommendation:**
**Use OPTION A** - "Adventure Platform" is better branding and more engaging than generic "Dashboard". Update tests to match the intentional UI design.

**Files to Update:**
1. `tests/e2e-staging/page-objects/DashboardPage.ts` - Update `expectDashboardLoaded()`
2. `tests/e2e-staging/01-authentication.staging.spec.ts` - Verify test passes
3. `tests/e2e-staging/02-ui-functionality.staging.spec.ts` - Update responsive test

**Verification:**
1. Update test expectations
2. Run Phase 1 authentication tests
3. Verify "should login successfully with demo credentials" passes
4. Run Phase 2 UI/UX tests
5. Verify responsive design test passes

**Success Criteria:**
- ✅ Test "should login successfully with demo credentials" passes
- ✅ Test "should adapt to different viewport sizes" passes
- ✅ No changes to production code needed

---

## 🟠 HIGH PRIORITY ISSUES

### HIGH-001: Test Code Error - Page Object Undefined ⏳ NOT STARTED

**Priority:** 🟠 HIGH
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 15 minutes
**Blocking:** Phase 2 validation

**Problem:**
```
TypeError: Cannot read properties of undefined (reading 'locator')
at tests/e2e-staging/02-ui-functionality.staging.spec.ts:129
```

**Root Cause:**
Test step callback incorrectly destructures `{ page }` parameter, but `page` is undefined in nested test.step().

**Current Code (BROKEN):**
```typescript
// Line 128-132 in 02-ui-functionality.staging.spec.ts
await test.step('Buttons respond to hover', async ({ page }) => {
  const firstButton = page.locator('button:visible').first();
  // page is undefined here!
});
```

**Recommended Fix:**
```typescript
// Remove destructured parameter, use page from outer scope
await test.step('Buttons respond to hover', async () => {
  const firstButton = page.locator('button:visible').first();
  if (await firstButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    await firstButton.hover();
    console.log('  ✓ Buttons respond to hover');
  }
});
```

**File to Update:**
- `tests/e2e-staging/02-ui-functionality.staging.spec.ts` (line 128-132)

**Verification:**
1. Update test code
2. Run Phase 2 UI/UX tests
3. Verify "should have working buttons with clear labels" passes

**Success Criteria:**
- ✅ No TypeError
- ✅ Test "should have working buttons with clear labels" passes

---

### HIGH-002: Landing Page Redirect Missing ⏳ NOT STARTED

**Priority:** 🟠 HIGH
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 1 hour
**Blocking:** Zero-instruction usability

**Problem:**
Landing page (/) doesn't redirect unauthenticated users to /login, breaking zero-instruction usability.

**Impact:**
- Users visiting root URL see blank/error page
- Doesn't meet "zero-instruction usability" requirement
- Poor first-time user experience

**Expected Behavior:**
- Unauthenticated user visits `/` → Redirect to `/login`
- Authenticated user visits `/` → Redirect to `/dashboard`

**Recommended Fix:**

```typescript
// File: tta.dev/player-frontend/src/router/index.tsx (or similar)

import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function RootRedirect() {
  const { isAuthenticated } = useAuth();
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />;
}

// In router configuration
{
  path: '/',
  element: <RootRedirect />
}
```

**Verification:**
1. Logout (clear session)
2. Navigate to `http://localhost:3001/`
3. Verify redirect to `/login`
4. Login with demo credentials
5. Navigate to `http://localhost:3001/`
6. Verify redirect to `/dashboard`
7. Run Phase 2 test "should be usable without instructions"

**Success Criteria:**
- ✅ Root URL redirects unauthenticated users to /login
- ✅ Root URL redirects authenticated users to /dashboard
- ✅ Test "should be usable without instructions" passes

---

### HIGH-003: Responsive Design Test - Dashboard Heading ⏳ NOT STARTED

**Priority:** 🟡 MEDIUM
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 5 minutes
**Blocking:** Phase 2 validation

**Problem:**
Duplicate of CRITICAL-002 in responsive design test.

**Recommended Fix:**
Same as CRITICAL-002 - Update test expectations to accept "Adventure Platform".

**File to Update:**
- `tests/e2e-staging/02-ui-functionality.staging.spec.ts` (line 292)

**Verification:**
1. Apply CRITICAL-002 fix
2. Run Phase 2 test "should adapt to different viewport sizes"
3. Verify test passes

**Success Criteria:**
- ✅ Test "should adapt to different viewport sizes" passes

---

## 🟡 MEDIUM PRIORITY ISSUES

### MEDIUM-001: Missing/Broken Test Files ⏳ NOT STARTED

**Priority:** 🟡 MEDIUM
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 2-4 hours
**Blocking:** Complete validation coverage

**Problem:**
Test files for phases 3, 4, 5, and 7 are missing or have execution issues.

**Missing/Broken Files:**
- `tests/e2e-staging/03-integration.staging.spec.ts`
- `tests/e2e-staging/04-error-handling.staging.spec.ts`
- `tests/e2e-staging/05-responsive.staging.spec.ts`
- `tests/e2e-staging/complete-user-journey.staging.spec.ts`

**Investigation Steps:**
```bash
# Check if files exist
ls -la tests/e2e-staging/*.spec.ts

# Try running each individually
npx playwright test tests/e2e-staging/03-integration.staging.spec.ts --config=playwright.staging.config.ts --project=chromium
npx playwright test tests/e2e-staging/04-error-handling.staging.spec.ts --config=playwright.staging.config.ts --project=chromium
npx playwright test tests/e2e-staging/05-responsive.staging.spec.ts --config=playwright.staging.config.ts --project=chromium
npx playwright test tests/e2e-staging/complete-user-journey.staging.spec.ts --config=playwright.staging.config.ts --project=chromium
```

**Recommended Action:**
1. Verify file existence
2. Check for syntax errors
3. Check for import errors
4. Create missing files if needed
5. Run each phase individually
6. Fix any errors found

**Success Criteria:**
- ✅ All test files exist
- ✅ All test files execute without errors
- ✅ Phases 3, 4, 5, 7 can be validated

---

### MEDIUM-002: WebSocket Port Mismatch ⏳ NOT STARTED

**Priority:** 🟢 LOW
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 30 minutes
**Blocking:** Real-time features

**Problem:**
WebSocket client tries to connect to port 3000, but staging frontend runs on port 3001.

**Error:**
```
WebSocket connection to 'ws://localhost:3000/ws' failed:
Error in connection establishment: net::ERR_CONNECTION_REFUSED
```

**Recommended Fix:**

```typescript
// File: tta.dev/player-frontend/src/services/websocket.ts (or similar)

// Dynamic port detection
const wsPort = window.location.port || '3001';
const wsUrl = `ws://localhost:${wsPort}/ws`;

// Or use environment variable
const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:3001/ws';
```

**Verification:**
1. Update WebSocket configuration
2. Rebuild frontend
3. Check browser console for WebSocket errors
4. Verify real-time features work (if any)

**Success Criteria:**
- ✅ No WebSocket connection errors in console
- ✅ Real-time features work correctly

---

### MEDIUM-003: Missing Environment Variables ⏳ NOT STARTED

**Priority:** 🟢 LOW
**Status:** ⏳ NOT STARTED
**Assignee:** TBD
**Estimated Effort:** 15 minutes
**Blocking:** Production deployment

**Problem:**
Environment variables not set, using default values.

**Warning:**
```
⚠ Missing environment variables: REDIS_URL, NEO4J_URI, DATABASE_URL
⚠ Using default staging values
```

**Recommended Fix:**

```bash
# Create .env.staging file
cat > .env.staging << EOF
REDIS_URL=redis://localhost:6380
NEO4J_URI=bolt://localhost:7688
DATABASE_URL=postgresql://localhost:5433/tta_staging
SESSION_SECRET=your-secret-key-here
NODE_ENV=staging
EOF
```

**Verification:**
1. Create `.env.staging` file
2. Restart staging services
3. Check logs for environment variable warnings
4. Verify services connect correctly

**Success Criteria:**
- ✅ No environment variable warnings
- ✅ Services connect to correct databases

---

## Summary Statistics

**Total Issues:** 8
**Critical:** 2 (25%)
**High:** 3 (37.5%)
**Medium:** 3 (37.5%)
**Low:** 0 (0%)

**Status Breakdown:**
- ⏳ Not Started: 8 (100%)
- 🔄 In Progress: 0 (0%)
- ✅ Resolved: 0 (0%)

**Estimated Total Effort:** 12-20 hours
**Estimated Time to Production:** 3-5 days

---

## Next Actions

1. **IMMEDIATE:** Assign CRITICAL-001 (Session Persistence) to developer
2. **TODAY:** Fix CRITICAL-002 (Dashboard Heading) - Quick win
3. **TODAY:** Fix HIGH-001 (Test Code Error) - Quick win
4. **TOMORROW:** Fix HIGH-002 (Landing Page Redirect)
5. **THIS WEEK:** Investigate MEDIUM-001 (Missing Test Files)
6. **THIS WEEK:** Fix MEDIUM-002 and MEDIUM-003
7. **AFTER FIXES:** Re-run complete validation suite
8. **AFTER VALIDATION:** Generate production readiness report

---

**Document Owner:** QA Team
**Last Updated:** 2025-10-15
**Next Review:** After CRITICAL issues resolved


---
**Logseq:** [[TTA.dev/.archive/Testing/2025-10/E2e_validation_issues_and_fixes]]
