# TTA Authentication Migration Guide

**Version**: 1.0
**Date**: December 2024
**Status**: IMPLEMENTATION READY

## Overview

This guide provides step-by-step instructions for migrating all TTA interfaces from their current authentication implementations to the new Unified Authentication System.

## Migration Benefits

✅ **Resolves "Welcome back, !" Issue**: Consistent user profile loading
✅ **Single Token Storage**: Eliminates token storage conflicts
✅ **Cross-Interface Sessions**: Users stay authenticated across interfaces
✅ **HIPAA Compliance**: Comprehensive audit logging
✅ **Clinical-Grade Security**: Enhanced security features

## Pre-Migration Checklist

- [ ] Backup existing authentication configurations
- [ ] Test unified authentication service in development
- [ ] Prepare rollback procedures
- [ ] Notify users of maintenance window (if needed)

## Migration Steps

### Step 1: Update Shared Components

**File**: `web-interfaces/shared/src/auth/index.ts`

```typescript
// Replace existing exports with unified auth
export {
  UnifiedAuthProvider as AuthProvider,
  useUnifiedAuth as useAuth,
  UserRole,
  InterfaceType,
  Permission
} from './UnifiedAuthProvider';

// Keep backward compatibility
export type {
  UnifiedUser as User,
  UnifiedAuthContextType as AuthContextType
} from './UnifiedAuthProvider';
```

### Step 2: Update Clinical Dashboard

**File**: `web-interfaces/clinical-dashboard/src/App.tsx`

```typescript
// Replace existing AuthProvider import
import { UnifiedAuthProvider as AuthProvider } from '@tta/shared-components';

// Update provider configuration
<AuthProvider
  apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
  interfaceType="clinical"
>
  {/* Existing app content */}
</AuthProvider>
```

**File**: `web-interfaces/clinical-dashboard/src/pages/dashboard/Dashboard.tsx`

```typescript
// Update user display
const Dashboard: React.FC = () => {
  const { user, getDisplayName } = useAuth();

  return (
    <div>
      <h1>Welcome back, {getDisplayName()}!</h1>
      {/* Rest of dashboard */}
    </div>
  );
};
```

### Step 3: Update Patient Interface

**File**: `web-interfaces/patient-interface/src/App.tsx`

```typescript
// Update AuthProvider configuration
<AuthProvider
  apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
  interfaceType="patient"
>
  {/* Existing app content */}
</AuthProvider>
```

### Step 4: Update Admin Interface

**File**: `web-interfaces/admin-interface/src/App.tsx`

```typescript
// Update AuthProvider configuration
<AuthProvider
  apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
  interfaceType="admin"
>
  {/* Existing app content */}
</AuthProvider>
```

### Step 5: Update Player Experience Frontend

**File**: `src/player_experience/frontend/src/App.tsx`

```typescript
// Replace existing auth context with unified provider
import { UnifiedAuthProvider } from '@tta/shared-components';

function App() {
  return (
    <UnifiedAuthProvider
      apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
      interfaceType="patient"
    >
      {/* Existing app content */}
    </UnifiedAuthProvider>
  );
}
```

**Remove Legacy Files**:
- `src/player_experience/frontend/src/contexts/AuthContext.tsx`
- `src/player_experience/frontend/src/store/slices/authSlice.ts`

### Step 6: Update Backend API Integration

**File**: `src/player_experience/api/main.py` (or equivalent)

```python
from src.api.auth import unified_auth_router

# Add unified auth router
app.include_router(unified_auth_router)
```

**Remove Legacy Routers**:
- Remove old authentication routers
- Update middleware to use unified auth service

### Step 7: Environment Variables

Update all interface `.env` files:

```env
# Standardized API URL
REACT_APP_API_URL=http://localhost:8080

# Remove old token keys (handled automatically by unified auth)
# REACT_APP_JWT_STORAGE_KEY - REMOVE
# REACT_APP_REFRESH_TOKEN_KEY - REMOVE
```

## Testing Migration

### 1. Authentication Flow Testing

```bash
# Test login for each interface
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_patient",
    "password": "test_patient123",
    "interfaceType": "patient"
  }'
```

### 2. Cross-Interface Session Testing

1. Login to Patient Interface
2. Navigate to Clinical Dashboard (if user has access)
3. Verify user remains authenticated
4. Check display name shows correctly

### 3. Token Refresh Testing

1. Login and wait for token to near expiration
2. Verify automatic token refresh
3. Confirm session continues seamlessly

## Rollback Procedures

If issues occur during migration:

### 1. Immediate Rollback

```bash
# Restore backup authentication files
git checkout HEAD~1 -- web-interfaces/shared/src/auth/
git checkout HEAD~1 -- web-interfaces/clinical-dashboard/src/
git checkout HEAD~1 -- web-interfaces/patient-interface/src/
git checkout HEAD~1 -- web-interfaces/admin-interface/src/
```

### 2. Database Rollback

```sql
-- If user data was migrated, restore from backup
-- (Implementation depends on database structure)
```

### 3. Clear Browser Storage

```javascript
// Clear all authentication data
localStorage.removeItem('tta_access_token');
localStorage.removeItem('tta_refresh_token');
localStorage.removeItem('tta_session_id');

// Clear old token keys
localStorage.removeItem('tta_token_patient');
localStorage.removeItem('tta_token_clinical');
localStorage.removeItem('tta_token_admin');
```

## Post-Migration Validation

### 1. User Experience Validation

- [ ] All interfaces show correct user names (no more "Welcome back, !")
- [ ] Cross-interface navigation maintains authentication
- [ ] Session timeouts work correctly per interface
- [ ] Logout works from all interfaces

### 2. Security Validation

- [ ] Audit logs capture all authentication events
- [ ] Token storage is consistent across interfaces
- [ ] HIPAA compliance requirements met
- [ ] No token leakage between interfaces

### 3. Performance Validation

- [ ] Authentication response time <100ms
- [ ] Token validation <10ms
- [ ] Profile loading <200ms
- [ ] Session refresh <50ms

## Troubleshooting

### Common Issues

**Issue**: "Welcome back, !" still appears
**Solution**: Clear browser cache and localStorage

**Issue**: Cross-interface authentication fails
**Solution**: Verify interfaceAccess in user profile

**Issue**: Token refresh fails
**Solution**: Check token expiration settings

**Issue**: Audit logs not appearing
**Solution**: Verify audit logger configuration

### Support Contacts

- **Technical Issues**: Development Team
- **Security Concerns**: Security Team
- **HIPAA Compliance**: Compliance Team

## Success Criteria

Migration is considered successful when:

✅ All interfaces use unified authentication
✅ User display names show correctly
✅ Cross-interface sessions work seamlessly
✅ All security requirements met
✅ HIPAA audit logging functional
✅ Performance benchmarks achieved

---

**Migration Guide Prepared By**: The Augster
**Next Phase**: Interface Component Updates
