# Frontend Deployment Fix - Issues #2 & #3

## Problem Summary

Frontend changes were not reflecting in the staging environment despite rebuilding Docker containers. This was caused by two critical issues in the Dockerfile.staging configuration.

## Root Causes

### Issue 1: Incorrect Build Output Directory
**Problem:** Dockerfile.staging was copying from `/app/dist` but Create React App builds to `/app/build`

**Location:** `src/player_experience/frontend/Dockerfile.staging` line 73

**Before:**
```dockerfile
COPY --from=builder /app/dist /usr/share/nginx/html
```

**After:**
```dockerfile
# CRA builds to 'build/' directory, not 'dist/'
COPY --from=builder /app/build /usr/share/nginx/html
```

### Issue 2: Non-existent Build Script
**Problem:** Dockerfile was running `yarn build:staging` which doesn't exist in package.json

**Location:** `src/player_experience/frontend/Dockerfile.staging` line 47

**Before:**
```dockerfile
RUN yarn build:staging
```

**After:**
```dockerfile
# Note: Using 'yarn build' as there's no separate build:staging script
# CRA builds to 'build/' directory by default
RUN yarn build
```

## Additional Improvements

### 1. Cache-Busting Mechanism
Added build timestamp argument to prevent Docker from using stale cached layers:

```dockerfile
# Cache-busting: Use build timestamp to ensure fresh builds
ARG CACHE_BUST=default_value
RUN echo "Cache bust: ${CACHE_BUST}"
```

### 2. Browser Cache Prevention for index.html
Added nginx configuration to prevent browsers from caching the main index.html file:

```nginx
# Never cache index.html to ensure fresh deployments
location = /index.html {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Pragma "no-cache";
    add_header Expires "0";
    add_header X-Environment "staging" always;
}
```

### 3. Automated Rebuild Script
Created `scripts/rebuild-frontend-staging.sh` to automate the rebuild process with proper cleanup:

```bash
./scripts/rebuild-frontend-staging.sh
```

This script:
1. Stops and removes the existing container
2. Removes old Docker images
3. Prunes build cache
4. Builds fresh image with cache-busting timestamp
5. Starts the new container
6. Verifies deployment health
7. Displays build information

## How to Deploy Frontend Changes

### Quick Method (Recommended)
```bash
./scripts/rebuild-frontend-staging.sh
```

### Manual Method
```bash
# Set cache-busting timestamp
export CACHE_BUST=$(date +%s)

# Rebuild with no cache
docker-compose -f docker-compose.staging-homelab.yml build --no-cache player-frontend-staging

# Restart the container
docker-compose -f docker-compose.staging-homelab.yml up -d player-frontend-staging

# Clear browser cache and reload
```

## Verification Steps

After deployment:

1. **Check container logs:**
   ```bash
   docker logs tta-staging-player-frontend --tail 50
   ```

2. **Verify nginx is serving files:**
   ```bash
   docker exec tta-staging-player-frontend ls -la /usr/share/nginx/html
   ```

3. **Test frontend endpoint:**
   ```bash
   curl -I http://localhost:3001/
   ```

4. **Check build configuration:**
   ```bash
   docker exec tta-staging-player-frontend cat /usr/share/nginx/html/config.js
   ```

5. **Clear browser cache:**
   - Chrome/Edge: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Firefox: `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (Mac)

6. **Navigate to frontend:**
   - Open http://localhost:3001 in your browser
   - Verify changes are reflected

## Technical Details

### Build Process Flow

1. **Builder Stage:**
   - Uses Node.js 18 Alpine image
   - Installs dependencies with `yarn install`
   - Copies source code
   - Runs `yarn build` (Create React App)
   - Outputs to `/app/build` directory

2. **Runtime Stage:**
   - Uses Nginx Alpine image
   - Copies built files from `/app/build` to `/usr/share/nginx/html`
   - Configures nginx with staging-specific settings
   - Serves static files on port 3000 (mapped to 3001 on host)

### Cache Strategy

- **Static Assets (JS, CSS, images, fonts):** Cached for 1 year with `immutable` flag
- **index.html:** Never cached (`no-cache, no-store, must-revalidate`)
- **Docker Build Layers:** Busted using `CACHE_BUST` argument with timestamp

## Troubleshooting

### Changes Still Not Reflecting

1. **Verify build output directory:**
   ```bash
   docker run --rm recovered-tta-storytelling-player-frontend-staging:latest ls -la /usr/share/nginx/html
   ```

2. **Check if build succeeded:**
   ```bash
   docker-compose -f docker-compose.staging-homelab.yml logs player-frontend-staging | grep -i error
   ```

3. **Ensure no volume mounts:**
   ```bash
   docker inspect tta-staging-player-frontend | grep -A 10 Mounts
   ```
   Should show no source code mounts.

4. **Force complete rebuild:**
   ```bash
   docker system prune -a -f
   ./scripts/rebuild-frontend-staging.sh
   ```

### Container Won't Start

1. **Check logs:**
   ```bash
   docker logs tta-staging-player-frontend
   ```

2. **Verify nginx configuration:**
   ```bash
   docker run --rm recovered-tta-storytelling-player-frontend-staging:latest nginx -t
   ```

3. **Check port conflicts:**
   ```bash
   lsof -i :3001
   ```

## Files Modified

- `src/player_experience/frontend/Dockerfile.staging` - Fixed build directory and added cache-busting
- `docker-compose.staging-homelab.yml` - Added CACHE_BUST build argument
- `scripts/rebuild-frontend-staging.sh` - New automated rebuild script
- `docs/FRONTEND_DEPLOYMENT_FIX.md` - This documentation

## Related Issues

- Issue #2: Frontend changes not reflecting in staging
- Issue #3: Docker cache preventing fresh builds
- Issue #4: JWT authentication (fixed in Priority 1)

## References

- Create React App Documentation: https://create-react-app.dev/docs/deployment/
- Docker Multi-Stage Builds: https://docs.docker.com/build/building/multi-stage/
- Nginx Caching: https://www.nginx.com/blog/nginx-caching-guide/



---
**Logseq:** [[TTA.dev/Docs/Frontend_deployment_fix]]
