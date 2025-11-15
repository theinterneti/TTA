#!/bin/bash
# TTA Repository Cleanup - Phase 1: Quick Wins
# Organizes logs, test results, and temporary files

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TTA Repository Cleanup - Phase 1${NC}"
echo "=================================================="
echo ""

# Navigate to repo root
cd "$(dirname "$0")/../.." || exit 1

# Create archive structure
echo -e "${YELLOW}📁 Creating archive structure...${NC}"
mkdir -p .archive/status-reports/2025-10
mkdir -p .archive/status-reports/2025-09
mkdir -p .archive/status-reports/2025-08
mkdir -p .archive/cicd/2025-10
mkdir -p .archive/testing/2025-10
mkdir -p .archive/database/2025-10
mkdir -p .archive/infrastructure/2025-10
mkdir -p .archive/observability/2025-10
mkdir -p .archive/tooling/2025-10
mkdir -p .archive/components/2025-10
mkdir -p .archive/packages/2025-10
mkdir -p .archive/logs/2025-10
mkdir -p .archive/logs/2025-09
mkdir -p .archive/test-results/2025-10
mkdir -p .archive/backups
mkdir -p .archive/versions
mkdir -p .archive/http-codes
echo -e "${GREEN}✓ Archive structure created${NC}"
echo ""

# 1.1 Archive Old Logs
echo -e "${YELLOW}📦 Archiving execution logs...${NC}"
count=0
for log in batch*_execution.log phase*_*.log test_*.log validation_*.log workflow_*.log *_execution.log; do
    if [ -f "$log" ]; then
        mv "$log" .archive/logs/2025-10/ 2>/dev/null && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Archived $count log files${NC}"
echo ""

# 1.2 Consolidate Test Results
echo -e "${YELLOW}📊 Archiving test results...${NC}"
count=0
for json in *_test_results.json *_results.json test_*.json coverage*.json; do
    if [ -f "$json" ] && [ "$json" != "package.json" ] && [ "$json" != "package-lock.json" ]; then
        mv "$json" .archive/test-results/2025-10/ 2>/dev/null && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Archived $count test result files${NC}"
echo ""

# 1.3 Clean Up Temporary Files
echo -e "${YELLOW}🧹 Cleaning temporary files...${NC}"
count=0

# Archive backup files
for backup in *.backup *.backup2; do
    if [ -f "$backup" ]; then
        mv "$backup" .archive/backups/ 2>/dev/null && ((count++)) || true
    fi
done

# Archive numbered directories
[ -d "400" ] && mv 400/ .archive/http-codes/ && ((count++)) || true
[ -d "500" ] && mv 500/ .archive/http-codes/ && ((count++)) || true
[ -d "=0.2.0" ] && mv =0.2.0/ .archive/versions/ && ((count++)) || true
[ -d "=0.3.0" ] && mv =0.3.0/ .archive/versions/ && ((count++)) || true

# Remove empty result file
[ -f "result" ] && rm result && ((count++)) || true

echo -e "${GREEN}✓ Cleaned $count temporary files${NC}"
echo ""

# 1.4 Organize Docker Compose Files
echo -e "${YELLOW}🐳 Organizing docker-compose files...${NC}"
count=0
for compose in docker-compose*.yml; do
    if [ -f "$compose" ] && [ "$compose" != "docker-compose.yml" ]; then
        # Keep main docker-compose.yml in root, move others
        mkdir -p docker/compose
        mv "$compose" docker/compose/ 2>/dev/null && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Organized $count docker-compose files${NC}"
echo ""

# Create archive README
echo -e "${YELLOW}📝 Creating archive README...${NC}"
cat > .archive/README.md << 'EOF'
# TTA Archive

Historical reports, logs, and documentation organized by category and date.

## Structure

- `status-reports/` - Phase completion reports, summaries
- `cicd/` - CI/CD setup and workflow reports
- `testing/` - Test execution and validation reports
- `database/` - Database setup and migration docs
- `infrastructure/` - Docker, deployment, infrastructure
- `observability/` - Monitoring and observability setup
- `tooling/` - OpenHands, Keploy, tool integration
- `components/` - Component development reports
- `packages/` - Package extraction and setup
- `logs/` - Execution logs by date
- `test-results/` - Test result JSON files
- `backups/` - Configuration backups
- `versions/` - Version-specific archives
- `http-codes/` - HTTP error code documentation

## Retention Policy

- **Logs:** Keep last 90 days
- **Status Reports:** Keep all (historical record)
- **Test Results:** Keep last 60 days
- **Backups:** Keep last 30 days

## Archive Date

Created: 2025-11-02
Last Updated: 2025-11-02
EOF
echo -e "${GREEN}✓ Archive README created${NC}"
echo ""

# Summary
echo "=================================================="
echo -e "${BLUE}✅ Phase 1 Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review .archive/ directory structure"
echo "  2. Run Phase 2: Status Report Consolidation"
echo "  3. Update README with new structure"
echo ""
echo "Rollback: All files are in .archive/ and git-tracked"
echo "=================================================="
