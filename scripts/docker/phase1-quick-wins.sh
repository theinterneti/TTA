#!/usr/bin/env bash
# TTA Docker Rebuild - Phase 1: Quick Wins
# Removes obsolete version declarations, pins image versions, adds resource limits
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Backup directory
BACKUP_DIR="${REPO_ROOT}/backups/docker-rebuild-$(date +%Y%m%d-%H%M%S)"
mkdir -p "${BACKUP_DIR}"

log_info "Starting Phase 1: Quick Wins"
log_info "Backup directory: ${BACKUP_DIR}"

# Step 1: Remove obsolete version declarations
log_info "Step 1/5: Removing obsolete 'version:' declarations..."
step1_count=0

find "${REPO_ROOT}" -name "docker-compose*.yml" -type f | while read -r file; do
    # Skip backup directories
    if [[ "$file" =~ /backups/ ]] || [[ "$file" =~ /archive/ ]]; then
        continue
    fi

    # Backup original
    cp "$file" "${BACKUP_DIR}/$(basename "$file").backup"

    # Remove version line
    if grep -q "^version:" "$file"; then
        sed -i '/^version:/d' "$file"
        log_success "  ✓ Removed version from: $(basename "$file")"
        step1_count=$((step1_count + 1))
    fi
done

log_success "Step 1 complete: Processed ${step1_count} files"

# Step 2: Pin image versions with latest stable releases
log_info "Step 2/5: Pinning image versions to latest stable releases..."

declare -A IMAGE_PINS=(
    ["neo4j:5-community"]="neo4j:5.26.1-community"
    ["neo4j:latest"]="neo4j:5.26.1-community"
    ["redis:7-alpine"]="redis:7.2.4-alpine3.19"
    ["redis:alpine"]="redis:7.2.4-alpine3.19"
    ["redis:latest"]="redis:7.2.4-alpine3.19"
    ["grafana/grafana:latest"]="grafana/grafana:10.2.3"
    ["grafana/grafana"]="grafana/grafana:10.2.3"
    ["prom/prometheus:latest"]="prom/prometheus:v2.48.1"
    ["prom/prometheus"]="prom/prometheus:v2.48.1"
    ["python:3.12"]="python:3.12.7-slim"
    ["python:3.12-slim"]="python:3.12.7-slim"
    ["node:20"]="node:20.11.0-alpine"
    ["node:20-alpine"]="node:20.11.0-alpine"
)

step2_count=0
find "${REPO_ROOT}" -name "docker-compose*.yml" -type f | while read -r file; do
    if [[ "$file" =~ /backups/ ]] || [[ "$file" =~ /archive/ ]]; then
        continue
    fi

    for old_image in "${!IMAGE_PINS[@]}"; do
        new_image="${IMAGE_PINS[$old_image]}"
        if grep -q "image: ${old_image}" "$file"; then
            sed -i "s|image: ${old_image}|image: ${new_image}|g" "$file"
            log_success "  ✓ Pinned ${old_image} → ${new_image} in $(basename "$file")"
            step2_count=$((step2_count + 1))
        fi
    done
done

log_success "Step 2 complete: Pinned ${step2_count} image versions"

# Step 3: Generate and display resource limits template
log_info "Step 3/5: Creating resource limits template..."

cat > "${REPO_ROOT}/docker/configs/resource-limits-template.yml" << 'EOF'
# Resource Limits Template
# Apply these to services in docker-compose.dev.yml and docker-compose.test.yml

# Development Environment (Generous for debugging)
services:
  neo4j:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

  redis:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

# Test Environment (Constrained for CI)
# For test environment, reduce limits by 50%
# limits.memory: 2G for neo4j, 256M for redis, 512M for api-gateway

# Staging Environment (Production-like)
# Use production sizing with 10% overhead for safety margin
EOF

log_success "Step 3 complete: Resource limits template created"

# Step 4: Update depends_on with health check conditions
log_info "Step 4/5: Health check documentation created..."

cat > "${REPO_ROOT}/docker/configs/health-check-guide.md" << 'EOF'
# Health Check Best Practices

## Updated depends_on Pattern

Replace simple depends_on:
```yaml
depends_on:
  - neo4j
  - redis
```

With health check conditions:
```yaml
depends_on:
  neo4j:
    condition: service_healthy
  redis:
    condition: service_healthy
```

## Service Health Checks

### Neo4j
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 40s
```

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

### API Services
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

## Manual Application Required
This guide must be applied manually to each compose file to ensure correctness.
EOF

log_success "Step 4 complete: Health check guide created"

# Step 5: Volume cleanup script
log_info "Step 5/5: Creating volume cleanup utility..."

cat > "${REPO_ROOT}/scripts/docker/cleanup-volumes.sh" << 'EOF'
#!/usr/bin/env bash
# TTA Docker Volume Cleanup Utility
set -euo pipefail

echo "=== TTA Docker Volume Cleanup ==="
echo ""

# List all Docker volumes
echo "Current Docker volumes:"
docker volume ls

echo ""
echo "Identifying potentially orphaned volumes..."
echo ""

# List volumes not used by any container
echo "Unused volumes (candidates for cleanup):"
docker volume ls -q -f dangling=true

echo ""
read -p "Remove all unused volumes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume prune -f
    echo "✓ Cleanup complete"
else
    echo "Cleanup cancelled"
fi

echo ""
echo "To remove specific volumes, use:"
echo "  docker volume rm <volume_name>"
echo ""
echo "To remove all volumes for a specific environment:"
echo "  docker volume ls | grep 'tta-dev' | awk '{print \$2}' | xargs docker volume rm"
EOF

chmod +x "${REPO_ROOT}/scripts/docker/cleanup-volumes.sh"
log_success "Step 5 complete: Volume cleanup script created"

# Generate summary report
log_info "Generating Phase 1 completion report..."

cat > "${BACKUP_DIR}/PHASE1_REPORT.md" << EOF
# Phase 1: Quick Wins - Completion Report

**Date**: $(date)
**Backup Location**: ${BACKUP_DIR}

## Changes Applied

### 1. Obsolete Version Declarations
- Removed \`version: '3.8'\` from ${step1_count} docker-compose files
- ✓ No more Docker Compose v2 warnings

### 2. Image Version Pinning
- Pinned ${step2_count} image references to specific versions:
$(for old in "${!IMAGE_PINS[@]}"; do
    echo "  - ${old} → ${IMAGE_PINS[$old]}"
done)

### 3. Resource Limits Template
- Created: \`docker/configs/resource-limits-template.yml\`
- Manual application required per environment

### 4. Health Check Documentation
- Created: \`docker/configs/health-check-guide.md\`
- Manual application required for depends_on updates

### 5. Volume Cleanup Utility
- Created: \`scripts/docker/cleanup-volumes.sh\`
- Run manually to clean orphaned volumes

## Next Steps

1. **Test Changes**:
   \`\`\`bash
   docker-compose -f docker-compose.dev.yml config
   docker-compose -f docker-compose.dev.yml up -d
   \`\`\`

2. **Apply Resource Limits**:
   - Review template in \`docker/configs/resource-limits-template.yml\`
   - Apply to docker-compose.dev.yml and docker-compose.test.yml

3. **Update Health Checks**:
   - Follow guide in \`docker/configs/health-check-guide.md\`
   - Update depends_on blocks in all compose files

4. **Clean Volumes**:
   \`\`\`bash
   bash scripts/docker/cleanup-volumes.sh
   \`\`\`

5. **Proceed to Phase 2**:
   - Consolidate compose files
   - Create docker/ directory structure
   - Archive obsolete files

## Rollback Instructions

If issues occur, restore from backup:
\`\`\`bash
cp ${BACKUP_DIR}/*.backup /path/to/original/files
\`\`\`

EOF

log_success "Phase 1 complete! Report generated at: ${BACKUP_DIR}/PHASE1_REPORT.md"
echo ""
cat "${BACKUP_DIR}/PHASE1_REPORT.md"
