---
name: Authentication API Communication Failure
about: Critical blocker preventing user authentication due to Docker networking misconfiguration
title: '[CRITICAL] Frontend cannot communicate with API during authentication - Docker networking issue'
labels: ['bug', 'critical', 'component:player-experience', 'target:staging', 'blocker', 'infrastructure']
assignees: ''
---

## Issue Summary
Frontend container cannot communicate with API container during authentication due to Docker networking misconfiguration. The frontend is configured to use `localhost` for API calls, which fails inside Docker containers.

## Severity
🔴 **CRITICAL** - Blocks entire user journey from Phase 1 (Authentication)

## Component
- **Component**: `player_experience` (Frontend/API Communication)
- **Infrastructure**: Docker networking configuration
- **Current Maturity**: Development
- **Target Maturity**: Staging
- **Promotion Status**: ❌ BLOCKED by this issue

## Environment
- **Staging Frontend**: http://localhost:3001 (host) / http://tta-staging-player-frontend:3000 (Docker network)
- **Staging API**: http://localhost:8081 (host) / http://tta-staging-player-api:8080 (Docker network)
- **Docker Network**: `tta-staging-homelab_tta-staging`
- **Test Framework**: Playwright v1.55.0

## Steps to Reproduce
1. Start staging environment with `docker-compose.staging-homelab.yml`
2. Navigate to frontend at http://localhost:3001
3. Attempt to sign in with demo credentials:
   - Username: `demo_user`
   - Password: `DemoPassword123!`  <!-- pragma: allowlist secret -->
4. **Expected**: User authenticates and redirects to dashboard
5. **Actual**: Login fails with "Failed to fetch" error, user stuck on login page

## Root Cause Analysis

### Problem: Docker Networking Misconfiguration

**Incorrect Configuration** (Current):
```dockerfile
# In Dockerfile.staging
ARG VITE_API_BASE_URL=http://localhost:8081
```

**Why This Fails**:
- Inside a Docker container, `localhost` refers to the container itself, not the host machine
- The frontend container cannot reach the API container using `localhost`
- API calls fail with "Failed to fetch" network error

**Correct Configuration** (Required):
```dockerfile
# In Dockerfile.staging
ARG VITE_API_BASE_URL=http://tta-staging-player-api:8080
```

**Why This Works**:
- Docker containers on the same network can communicate using container names
- `tta-staging-player-api` is the API container's name on the Docker network
- Port 8080 is the internal container port (not the host-mapped 8081)

### Additional Context

**Vite Build-Time Environment Variables**:
- Vite bakes environment variables into the JavaScript bundle at build time
- Variables must be prefixed with `VITE_` to be exposed to client code
- Runtime environment variables (set with `docker run -e`) do NOT override build-time values
- **Solution**: Must rebuild container with correct build args

**Docker Compose Configuration**:
The `docker-compose.staging-homelab.yml` file needs to be updated to pass the correct build argument:

```yaml
services:
  player-frontend-staging:
    build:
      context: ./src/player_experience/frontend
      dockerfile: Dockerfile.staging
      args:
        VITE_API_BASE_URL: http://tta-staging-player-api:8080  # ← ADD THIS
```

## Impact Assessment

### User Experience
- ❌ **Complete journey blocker**: Users cannot sign in
- ❌ **Zero-instruction usability violated**: Error message is technical, not user-friendly
- ❌ **Higher priority than Issue #5**: Blocks earlier in user journey

### Component Maturity
- ❌ `player_experience` cannot be promoted to staging
- ❌ All dependent components blocked
- ❌ UAT cannot proceed

### Infrastructure
- ⚠️ **Configuration Drift**: Manual container creation differs from docker-compose
- ⚠️ **Deployment Risk**: Future deployments will have same issue
- ⚠️ **Documentation Gap**: Docker networking best practices not documented

## Proposed Solution

### Fix 1: Update Dockerfile Build Args (IMMEDIATE)
```bash
# Rebuild with correct API URL
docker compose -f docker-compose.staging-homelab.yml build \
  --build-arg VITE_API_BASE_URL=http://tta-staging-player-api:8080 \
  player-frontend-staging
```

### Fix 2: Update Docker Compose Configuration (PERMANENT)
```yaml
# docker-compose.staging-homelab.yml
services:
  player-frontend-staging:
    build:
      context: ./src/player_experience/frontend
      dockerfile: Dockerfile.staging
      args:
        VITE_API_BASE_URL: http://tta-staging-player-api:8080
        VITE_WS_URL: ws://tta-staging-player-api:8080
    environment:
      - NODE_ENV=staging
    networks:
      - tta-staging
    ports:
      - "3001:3000"
    depends_on:
      - player-api-staging
```

### Fix 3: Add Environment Variable Validation (RECOMMENDED)
```typescript
// src/player_experience/frontend/src/config/environment.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL environment variable is not set');
}

if (API_BASE_URL.includes('localhost') && import.meta.env.PROD) {
  console.warn('WARNING: Using localhost in production build - this may cause issues in Docker');
}

export const config = {
  apiBaseUrl: API_BASE_URL,
  // ... other config
};
```

### Fix 4: Add Health Check for API Connectivity (RECOMMENDED)
```typescript
// src/player_experience/frontend/src/utils/healthCheck.ts
export async function checkAPIConnectivity(): Promise<boolean> {
  try {
    const response = await fetch(`${config.apiBaseUrl}/health`, {
      method: 'GET',
      timeout: 5000,
    });
    return response.ok;
  } catch (error) {
    console.error('API connectivity check failed:', error);
    return false;
  }
}
```

## Acceptance Criteria

### Functional Requirements
- [ ] Frontend can communicate with API from within Docker container
- [ ] Authentication succeeds with demo credentials
- [ ] User redirects to dashboard after successful login
- [ ] E2E tests pass Phase 1 (Authentication)
- [ ] No "Failed to fetch" errors in browser console

### Infrastructure Requirements
- [ ] Docker Compose configuration updated with correct build args
- [ ] Container rebuild process documented
- [ ] Environment variable validation added
- [ ] API connectivity health check implemented

### Testing Requirements
- [ ] Manual testing: Sign in with demo credentials succeeds
- [ ] E2E tests: Complete user journey passes Phase 1
- [ ] Integration tests: API connectivity verified from frontend container
- [ ] Documentation: Docker networking guide created

## Related Issues
- Issue #5: Dashboard character fetch (RESOLVED - prerequisite for testing this fix)
- Issue #2: Session restoration infinite loop (may be related)
- Issue #3: WebSocket connection (may have same root cause)
- Issue #4: Player ID authentication (blocked by this issue)

## Validation Evidence
- **Test Report**: `VALIDATION_REPORT_2025-01-11.md`
- **Progress Summary**: `VALIDATION_PROGRESS_SUMMARY_2025-01-11.md`
- **Test Artifacts**: `test-results-staging/complete-user-journey.stag-4cc71-*/`
- **Screenshots**: Show "Login: Failed to fetch" error
- **Trace Files**: Available for debugging

## Definition of Done
- [ ] Docker Compose configuration updated
- [ ] Frontend container rebuilt with correct API URL
- [ ] Container redeployed and tested
- [ ] E2E tests pass complete user journey (Phases 1-6)
- [ ] Manual testing confirms authentication works
- [ ] Documentation updated with Docker networking best practices
- [ ] Environment variable validation added
- [ ] API connectivity health check implemented
- [ ] Code reviewed and approved
- [ ] Component promoted to staging

## Estimated Effort
- **Configuration Update**: 30 minutes
- **Container Rebuild**: 5 minutes
- **Testing**: 30 minutes
- **Documentation**: 30 minutes
- **Total**: 1.5 hours

## Priority
**P0 - CRITICAL**: Must be fixed before any staging promotion or UAT

## Labels
- `bug`
- `critical`
- `component:player-experience`
- `target:staging`
- `blocker`
- `infrastructure`
- `docker`
- `networking`

## Additional Notes

### Docker Networking Best Practices
1. **Never use `localhost` in Docker containers** for inter-container communication
2. **Use container names** as hostnames on the same Docker network
3. **Use internal ports** (not host-mapped ports) for container-to-container communication
4. **Document network topology** in deployment documentation
5. **Validate environment variables** at application startup

### Lessons Learned
1. **Build-time vs Runtime**: Vite environment variables are baked in at build time
2. **Container Isolation**: Each container has its own `localhost`
3. **Network Discovery**: Docker provides DNS resolution for container names
4. **Configuration Management**: Centralize environment configuration in docker-compose

---

**Discovered**: 2025-01-11
**Validation Phase**: Complete User Journey E2E Testing
**Reporter**: Augster AI Agent
**Status**: Fix implemented, pending verification


---
**Logseq:** [[TTA.dev/.github/Issue_template/Issue-6-authentication-api-communication]]
