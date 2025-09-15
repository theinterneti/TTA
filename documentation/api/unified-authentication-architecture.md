# TTA Unified Authentication Architecture

**Version**: 1.0
**Date**: December 2024
**Status**: DESIGN PHASE
**Target**: Production-Ready Clinical-Grade Authentication

## Architecture Overview

The Unified Authentication Architecture consolidates all 7 existing authentication implementations into a single, consistent, HIPAA-compliant system that serves all TTA interfaces with clinical-grade security and performance.

## Core Design Principles

1. **Single Source of Truth**: One authentication service for all interfaces
2. **Clinical-Grade Security**: HIPAA compliance with audit logging
3. **Performance**: <100ms authentication response time
4. **Scalability**: Support for 1000+ concurrent sessions
5. **Consistency**: Identical user experience across all interfaces
6. **Backward Compatibility**: Seamless migration from existing systems

## Unified Data Models

### Core User Model

```typescript
interface UnifiedUser {
  // Core Identity
  id: string;                           // UUID - primary identifier
  username: string;                     // Unique username
  email: string;                        // Email address

  // Role and Permissions
  role: UserRole;                       // Standardized role enum
  permissions: Permission[];            // Granular permissions array
  interface_access: InterfaceType[];    // Allowed interfaces

  // Profile Information
  profile: UserProfile;                 // Consistent profile structure

  // Security
  mfa_enabled: boolean;
  mfa_verified?: boolean;
  last_login?: Date;
  password_last_changed?: Date;

  // Therapeutic Context
  therapeutic_context?: TherapeuticContext;

  // Metadata
  created_at: Date;
  updated_at: Date;
  is_active: boolean;
}

interface UserProfile {
  // Display Information
  firstName?: string;
  lastName?: string;
  displayName: string;                  // Computed: firstName + lastName or username
  organization?: string;

  // Therapeutic Preferences
  therapeutic_preferences?: {
    preferred_frameworks: TherapeuticFramework[];
    intensity_level: IntensityLevel;
    privacy_settings: PrivacySettings;
  };

  // Interface Preferences
  ui_preferences?: {
    theme: string;
    accessibility_settings: AccessibilitySettings;
    language: string;
  };
}

enum UserRole {
  PATIENT = "patient",
  CLINICIAN = "clinician",
  ADMIN = "admin",
  STAKEHOLDER = "stakeholder",
  DEVELOPER = "developer"
}

enum InterfaceType {
  PATIENT = "patient",
  CLINICAL = "clinical",
  ADMIN = "admin",
  PUBLIC = "public",
  DEVELOPER = "developer"
}
```

### Authentication Tokens

```typescript
interface AuthTokens {
  access_token: string;                 // JWT access token
  refresh_token: string;                // JWT refresh token
  token_type: "bearer";
  expires_in: number;                   // Seconds until expiration
  refresh_expires_in: number;           // Refresh token expiration
}

interface TokenPayload {
  // Standard JWT Claims
  sub: string;                          // User ID
  iat: number;                          // Issued at
  exp: number;                          // Expires at
  iss: string;                          // Issuer
  aud: string[];                        // Audience (interfaces)

  // TTA Custom Claims
  username: string;
  email: string;
  role: UserRole;
  permissions: string[];
  interface_access: string[];
  mfa_verified: boolean;

  // Session Context
  session_id: string;
  device_id?: string;
  ip_address?: string;
}
```

## Service Architecture

### 1. Unified Authentication Service

**Location**: `src/services/unified_auth/`

**Core Components**:
- `UnifiedAuthService`: Main authentication orchestrator
- `TokenManager`: JWT token creation, validation, refresh
- `UserManager`: User profile management and validation
- `SessionManager`: Session lifecycle and security
- `PermissionManager`: Role-based access control
- `AuditLogger`: HIPAA-compliant audit logging

**Key Features**:
- Single authentication endpoint for all interfaces
- Automatic token refresh with sliding expiration
- Multi-factor authentication support
- Session management with configurable timeouts
- Comprehensive audit logging for HIPAA compliance

### 2. Interface-Specific Adapters

**Shared Authentication Provider**: `web-interfaces/shared/src/auth/UnifiedAuthProvider.tsx`

```typescript
interface UnifiedAuthContextType {
  // Authentication State
  user: UnifiedUser | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Authentication Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;

  // Permission Helpers
  hasRole: (role: UserRole) => boolean;
  hasPermission: (permission: Permission) => boolean;
  hasInterfaceAccess: (interfaceType: InterfaceType) => boolean;

  // Profile Management
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;

  // Session Management
  extendSession: () => Promise<void>;
  getSessionInfo: () => SessionInfo;
}
```

### 3. Backend Integration

**Authentication Router**: `src/api/auth/unified_auth_router.py`

**Endpoints**:
- `POST /auth/login` - Universal login endpoint
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - Secure logout
- `GET /auth/profile` - User profile retrieval
- `PUT /auth/profile` - Profile updates
- `GET /auth/session` - Session information

## Token Management Strategy

### Standardized Token Storage

**Storage Keys**:
- Access Token: `tta_access_token`
- Refresh Token: `tta_refresh_token`
- Session ID: `tta_session_id`

**Storage Strategy**:
- Primary: `localStorage` for persistence
- Fallback: `sessionStorage` for security-sensitive interfaces
- Memory: In-memory storage for temporary sessions

### Token Lifecycle

1. **Login**: Generate access + refresh tokens
2. **Usage**: Validate access token on each request
3. **Refresh**: Automatic refresh 5 minutes before expiration
4. **Logout**: Invalidate both tokens server-side
5. **Expiration**: Graceful handling with re-authentication prompt

## Interface-Specific Configurations

### Patient Interface
- Session Timeout: 60 minutes (therapeutic continuity)
- MFA: Optional (user preference)
- Audit Level: Standard
- Token Refresh: Automatic

### Clinical Dashboard
- Session Timeout: 30 minutes (HIPAA requirement)
- MFA: Required for sensitive operations
- Audit Level: Comprehensive (HIPAA compliance)
- Token Refresh: Manual confirmation required

### Admin Interface
- Session Timeout: 15 minutes (high security)
- MFA: Always required
- Audit Level: Maximum (all actions logged)
- Token Refresh: Manual with re-authentication

### Developer Interface
- Session Timeout: 8 hours (development workflow)
- MFA: Optional
- Audit Level: Development (debugging enabled)
- Token Refresh: Automatic

## Security Implementation

### HIPAA Compliance Features

1. **Audit Logging**: All authentication events logged with:
   - User identification
   - Timestamp
   - Action performed
   - IP address and device info
   - Success/failure status

2. **Data Protection**:
   - Encrypted token storage
   - Secure token transmission (HTTPS only)
   - Token rotation on suspicious activity
   - Automatic logout on inactivity

3. **Access Controls**:
   - Role-based interface access
   - Permission-based feature access
   - IP-based restrictions (configurable)
   - Device registration for MFA

### Performance Requirements

- **Authentication Response**: <100ms
- **Token Validation**: <10ms
- **Profile Loading**: <200ms
- **Session Refresh**: <50ms
- **Concurrent Sessions**: 1000+ supported

## Migration Strategy

### Phase 1: Core Service Implementation
1. Implement UnifiedAuthService
2. Create shared authentication provider
3. Set up token management system
4. Implement audit logging

### Phase 2: Interface Migration
1. Update shared components
2. Migrate clinical dashboard
3. Migrate patient interface
4. Migrate admin interface

### Phase 3: Legacy Cleanup
1. Remove old authentication implementations
2. Update API endpoints
3. Clean up unused dependencies
4. Comprehensive testing

### Phase 4: Production Deployment
1. Gradual rollout with feature flags
2. Monitor authentication metrics
3. Validate HIPAA compliance
4. Performance optimization

## Success Metrics

- **Zero Authentication Failures**: All interfaces use consistent auth
- **User Profile Loading**: 100% success rate for "Welcome back, {name}"
- **Cross-Interface Sessions**: Seamless authentication across interfaces
- **Security Compliance**: Full HIPAA audit trail
- **Performance**: All response time requirements met

---

**Architecture Designed By**: The Augster
**Next Phase**: Implementation of Consolidated Authentication Service
