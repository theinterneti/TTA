# CRITICAL-001: Session Persistence Issue - Investigation Summary

**Status:** BLOCKED - Requires fresh investigation with different approach
**Priority:** CRITICAL
**Impact:** Users logged out immediately after page refresh - Production blocker
**Last Updated:** 2025-10-15

## Problem Statement

Users are unable to maintain their authenticated session after page refresh. The test `should persist session after page refresh` fails with a timeout waiting for login to complete, indicating the login endpoint is returning a 500 error.

## Attempted Fixes (5+ Attempts)

### 1. Backend Cookie Configuration ✅
- **Fix:** Made `secure` flag environment-aware (false for staging/dev, true for production)
- **File:** `src/player_experience/api/routers/auth.py`
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

### 2. Redis Session Creation ✅
- **Fix:** Added Redis session creation to login endpoint
- **File:** `src/player_experience/api/routers/auth.py` (lines 467-513)
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

### 3. Frontend Session Restoration ✅
- **Fix:** Updated session restoration to check backend session and set `isAuthenticated`
- **Files:**
  - `src/player_experience/frontend/src/utils/sessionRestoration.ts`
  - `src/player_experience/frontend/src/store/slices/authSlice.ts`
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

### 4. Demo User Fallback ✅
- **Fix:** Added fallback in `authenticate_user` to allow demo user login without database entry
- **File:** `src/player_experience/services/auth_service.py` (lines 348-413)
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

### 5. Neo4j Health Check Fix ✅
- **Fix:** Hardcoded correct password in health check, increased start_period from 30s to 60s
- **File:** `docker-compose.staging-homelab.yml` (lines 103-112)
- **Status:** Implemented successfully
- **Result:** Neo4j became healthy, but login endpoint still returns 500 error

### 6. Player Profile Repository Exception Handling ✅
- **Fix:** Modified `get_player_profile` to return `None` instead of raising exception on empty database
- **File:** `src/player_experience/database/player_profile_repository.py` (lines 660-664)
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

### 7. Player Profile By Username Exception Handling ✅
- **Fix:** Modified `get_player_by_username` to return `None` instead of raising exception on empty database
- **File:** `src/player_experience/database/player_profile_repository.py` (lines 789-819)
- **Status:** Implemented successfully
- **Result:** Did not resolve the issue

## Current Status

**Login Endpoint Behavior:**
- Returns 500 Internal Server Error
- Neo4j logs show warnings about unknown labels and properties (database is empty)
- Exception handling in repository methods is not preventing the 500 error

**Suspected Root Cause:**
The login endpoint is failing when trying to query the player profile repository, even though exception handling has been added. The issue appears to be in the player profile manager's `get_player_profile` or `create_player_profile` methods, which are called before the repository methods.

**Key Observation:**
- API container is healthy and running
- Health endpoint responds correctly
- Login endpoint is being called but returns 500 error
- The error occurs during player profile auto-creation or retrieval

## Recommended Next Steps for Future Investigation

1. **Add Comprehensive Error Logging:**
   - Add detailed logging to `PlayerProfileManager.get_player_profile()` and `create_player_profile()` methods
   - Log the exact exception being raised before it becomes a 500 error
   - Include stack traces in logs

2. **Seed Demo User Data:**
   - Create a Neo4j initialization script that seeds demo user data on startup
   - This would allow the player profile queries to succeed even on empty database
   - Alternative: Create player profiles on-demand without querying Neo4j

3. **Bypass Player Profile Requirement:**
   - Consider making player profile optional for initial login
   - Create player profile asynchronously after successful authentication
   - This would allow session persistence to work even if player profile creation fails

4. **Database Connection Verification:**
   - Verify that the player profile manager is properly connected to Neo4j
   - Check if the Neo4j driver is being initialized correctly
   - Verify connection pooling and session management

5. **Test with Populated Database:**
   - Manually create a demo user in Neo4j
   - Run the session persistence test with populated database
   - This would help isolate whether the issue is database-related or session-related

## Files Modified

- `src/player_experience/api/routers/auth.py` - Cookie configuration, Redis session creation
- `src/player_experience/services/auth_service.py` - Demo user fallback
- `src/player_experience/database/player_profile_repository.py` - Exception handling
- `src/player_experience/frontend/src/utils/sessionRestoration.ts` - Session restoration logic
- `src/player_experience/frontend/src/store/slices/authSlice.ts` - Redux state management
- `docker-compose.staging-homelab.yml` - Neo4j health check fix

## Test Results

**Test:** `should persist session after page refresh`
**Status:** FAILING
**Error:** TimeoutError: page.waitForURL timeout 30000ms exceeded
**Root Cause:** Login endpoint returns 500 error, preventing successful authentication

## Decision

Moving on to HIGH-002 (Landing page redirect) to maintain progress on other critical issues. This session persistence issue requires a fresh investigation approach, potentially with database seeding or architectural changes to player profile handling.


---
**Logseq:** [[TTA.dev/Docs/Issues/Critical-001-session-persistence-investigation]]
