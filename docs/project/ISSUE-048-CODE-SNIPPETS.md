# Issue #48: Session Persistence - Ready-to-Use Code Snippets

## 📋 Quick Reference for Implementation

---

## 1️⃣ secureStorage.ts - Add Token Persistence

### **Add this method to SecureStorage class** (after line 38):

```typescript
/**
 * Restore token from localStorage on app load
 */
restoreFromStorage(): void {
  try {
    const stored = localStorage.getItem('tta_token');
    if (!stored) {
      return;
    }

    const data = JSON.parse(stored);

    // Validate token hasn't expired
    if (Date.now() >= data.expiresAt) {
      localStorage.removeItem('tta_token');
      return;
    }

    // Restore to memory
    this.tokenData = data;
    this.scheduleTokenRefresh(data.expiresAt);
    console.info('Token restored from localStorage');
  } catch (error) {
    console.warn('Failed to restore token from localStorage:', error);
    localStorage.removeItem('tta_token');
  }
}
```

### **Modify setToken method** (add after line 37):

```typescript
// Persist to localStorage for session recovery
try {
  localStorage.setItem('tta_token', JSON.stringify({
    accessToken,
    expiresAt,
  }));
} catch (error) {
  console.warn('Failed to persist token to localStorage:', error);
}
```

### **Modify clearToken method** (add after line 73):

```typescript
// Clear from localStorage
try {
  localStorage.removeItem('tta_token');
} catch (error) {
  console.warn('Failed to clear token from localStorage:', error);
}
```

### **Add at end of file** (after line 276):

```typescript
// Restore token from localStorage on module load
secureStorage.restoreFromStorage();
```

---

## 2️⃣ sessionRestoration.ts - Restore Before Verification

### **Add at start of restoreAuthentication()** (line 96):

```typescript
// Restore token from storage first
secureStorage.restoreFromStorage();
```

---

## 3️⃣ authSlice.ts - Persist Auth State

### **In login.fulfilled case** (after line 149):

```typescript
// Persist auth state to localStorage
try {
  localStorage.setItem('tta_auth_state', JSON.stringify({
    user: action.payload.user,
    sessionId: action.payload.sessionId,
    isAuthenticated: true,
  }));
} catch (error) {
  console.warn('Failed to persist auth state:', error);
}
```

### **In logout.fulfilled case** (after line 165):

```typescript
// Clear persisted auth state
try {
  localStorage.removeItem('tta_auth_state');
} catch (error) {
  console.warn('Failed to clear auth state:', error);
}
```

### **In logout.rejected case** (after line 174):

```typescript
// Clear persisted auth state even on error
try {
  localStorage.removeItem('tta_auth_state');
} catch (error) {
  console.warn('Failed to clear auth state:', error);
}
```

---

## 4️⃣ Testing Code

### **Manual Test Script** (run in browser console):

```javascript
// Check if token is persisted
console.log('Token in localStorage:', localStorage.getItem('tta_token'));
console.log('Auth state in localStorage:', localStorage.getItem('tta_auth_state'));

// Check Redux store
console.log('Redux auth state:', store.getState().auth);

// Check session storage
console.log('Session data:', sessionStorage.getItem('tta_session_data'));
```

### **E2E Test Verification**:

```bash
# Run authentication tests
npm test -- tests/e2e-staging/01-authentication.staging.spec.ts

# Run specific test
npm test -- tests/e2e-staging/01-authentication.staging.spec.ts -g "persist session after page refresh"
```

---

## 5️⃣ Verification Checklist

### **After Implementation**:

- [ ] Token persists in localStorage after login
- [ ] Token restored from localStorage on page refresh
- [ ] Expired tokens are cleared automatically
- [ ] Auth state persists in localStorage
- [ ] Auth state cleared on logout
- [ ] E2E test "persist session after page refresh" passes
- [ ] E2E test "persist session across navigation" passes
- [ ] No console errors or warnings
- [ ] All other auth tests still pass

---

## 6️⃣ Rollback Plan

If issues occur, revert changes:

```bash
# Revert specific files
git checkout src/player_experience/frontend/src/utils/secureStorage.ts
git checkout src/player_experience/frontend/src/utils/sessionRestoration.ts
git checkout src/player_experience/frontend/src/store/slices/authSlice.ts

# Or revert entire commit
git revert <commit-hash>
```

---

## 7️⃣ Debugging Tips

### **If session not persisting**:
1. Check browser console for errors
2. Verify localStorage is enabled
3. Check token expiration time
4. Verify backend session cookie is set

### **If tests still failing**:
1. Check E2E test logs for specific error
2. Verify token is in localStorage after login
3. Check Redux store state after refresh
4. Verify session restoration log in window object

### **Debug Commands**:

```javascript
// Check session restoration log
window.__SESSION_RESTORATION_LOG__

// Check Redux store
store.getState().auth

// Check all storage
{
  localStorage: Object.fromEntries(Object.entries(localStorage)),
  sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
  cookies: document.cookie
}
```

---

## 📞 Support

For issues during implementation:
1. Check the Implementation Guide: `docs/ISSUE-048-IMPLEMENTATION-GUIDE.md`
2. Review the Analysis: `docs/ISSUE-048-SESSION-PERSISTENCE-ANALYSIS.md`
3. Check E2E test output for specific errors
4. Review browser console for JavaScript errors
