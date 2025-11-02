# Remaining Priority Issues - E2E Validation Backlog

> **📋 NOTE**: This file has been migrated to [`../../.augment/TODO-AUDIT.md`](../../.augment/TODO-AUDIT.md) under "E2E Test Validation Backlog". See that file for current tracking of MEDIUM-001 and MEDIUM-002.

**Status:** Ready for prioritization (Migrated 2025-11-01)
**Date:** 2025-10-16
**Completed:** HIGH-002 (Landing Page Redirect) ✅
**Deferred:** CRITICAL-001 (Session Persistence) 📋

---

## MEDIUM-001: Missing/Incomplete Test Files

**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours
**Impact:** Test coverage gaps for phases 3-7 of E2E validation
**Status:** NOT STARTED

### Problem

The E2E validation suite has test files for phases 3, 4, 5, and 7, but they may have incomplete implementations or execution issues:

- `03-integration.staging.spec.ts` - Integration Points (API, Database, WebSocket)
- `04-error-handling.staging.spec.ts` - Error Handling (Network, Validation, Edge Cases)
- `05-responsive.staging.spec.ts` - Responsive Design (Mobile, Tablet, Desktop)
- `06-accessibility.staging.spec.ts` - Accessibility (WCAG Compliance)

### Current Status

✅ **Files exist** - All test files are present in `tests/e2e-staging/`
⚠️ **Execution status unknown** - Need to run tests to identify issues
❓ **Potential issues:**
- Tests may timeout due to backend login failures (CRITICAL-001)
- Tests may have incomplete implementations
- Tests may have environment-specific issues

### What Needs to Be Done

1. **Run each test file individually** to identify execution issues
2. **Analyze failures** to determine root causes:
   - Backend issues (login, API endpoints)
   - Frontend issues (UI rendering, state management)
   - Test infrastructure issues (timeouts, selectors)
3. **Fix or document** each issue
4. **Ensure all tests pass** or document blockers

### Files Involved

- `tests/e2e-staging/03-integration.staging.spec.ts`
- `tests/e2e-staging/04-error-handling.staging.spec.ts`
- `tests/e2e-staging/05-responsive.staging.spec.ts`
- `tests/e2e-staging/06-accessibility.staging.spec.ts`

### Recommended Approach

1. Run tests one by one to identify which ones pass/fail
2. For failures, check if they're due to:
   - CRITICAL-001 (login endpoint 500 error) - Document as blocker
   - Other issues - Fix or document
3. Create a test execution report showing status of each phase

---

## MEDIUM-002: WebSocket Port Mismatch

**Priority:** MEDIUM
**Estimated Effort:** 30 minutes
**Impact:** Real-time chat functionality may not work in staging
**Status:** NOT STARTED

### Problem

The WebSocket client is configured to connect to port 3000, but the staging frontend runs on port 3001. This causes WebSocket connection failures when trying to establish real-time chat connections.

### Root Cause

In `src/player_experience/frontend/src/services/websocket.ts` (lines 57-60):

```typescript
const apiUrl = process.env.REACT_APP_API_URL ||
               process.env.VITE_API_BASE_URL ||
               'http://localhost:8080';  // ← API is on 8080 (correct)
const wsUrl = apiUrl.replace(/^http/, 'ws') + '/ws/chat';
```

The WebSocket URL is derived from the API URL (which is correct at `http://localhost:8081` in staging), but the frontend itself runs on port 3001, not 3000.

### Current Configuration

- **Frontend:** Runs on port 3001 (docker-compose.staging-homelab.yml)
- **API:** Runs on port 8081 (docker-compose.staging-homelab.yml)
- **WebSocket:** Should connect to API at `ws://localhost:8081/ws/chat`

### What Needs to Be Done

1. **Verify the actual WebSocket URL** being used in staging
2. **Check environment variables** for API URL configuration
3. **Ensure WebSocket connects to correct API endpoint** (port 8081, not 3000)
4. **Test WebSocket connection** in staging environment
5. **Verify real-time chat works** after fix

### Files Involved

- `src/player_experience/frontend/src/services/websocket.ts` (lines 57-60)
- `.env.staging-homelab` (API URL configuration)
- `docker-compose.staging-homelab.yml` (port mappings)

### Recommended Approach

1. Check what `REACT_APP_API_URL` or `VITE_API_BASE_URL` is set to in staging
2. Verify the WebSocket URL is correctly derived from API URL
3. Test WebSocket connection by:
   - Opening browser console
   - Checking WebSocket connection in Network tab
   - Verifying connection to `ws://localhost:8081/ws/chat`
4. If still failing, add debug logging to WebSocket service
5. Test real-time chat functionality

---

## Comparison & Recommendation

| Issue | Effort | Impact | Complexity | Blocker |
|-------|--------|--------|-----------|---------|
| **MEDIUM-001** | 2-4 hrs | High | Medium | CRITICAL-001 |
| **MEDIUM-002** | 30 min | Medium | Low | None |

### Recommendation

**Start with MEDIUM-002 (WebSocket Port Mismatch):**
- ✅ Quick win (30 minutes)
- ✅ No blockers
- ✅ Enables real-time chat functionality
- ✅ Builds momentum

**Then tackle MEDIUM-001 (Missing Test Files):**
- ⚠️ Longer effort (2-4 hours)
- ⚠️ May be blocked by CRITICAL-001
- ✅ Comprehensive test coverage
- ✅ Identifies remaining issues

---

## Next Steps

1. **Confirm priority order** with user
2. **Start with selected issue**
3. **Document findings** as we go
4. **Update this file** with progress
