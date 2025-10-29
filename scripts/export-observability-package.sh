#!/bin/bash
# Export Observability Package to TTA.dev Repository
# This script prepares the observability integration package for export

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Observability Package Export Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
PACKAGE_NAME="tta-observability-integration"
EXPORT_DIR="export/${PACKAGE_NAME}"
TTA_DEV_REPO="${TTA_DEV_REPO:-../TTA.dev}"

# Check if TTA.dev repository path is provided
if [ ! -d "$TTA_DEV_REPO" ]; then
    echo -e "${YELLOW}⚠️  TTA.dev repository not found at: $TTA_DEV_REPO${NC}"
    echo -e "${YELLOW}   Set TTA_DEV_REPO environment variable or clone to ../TTA.dev${NC}"
    echo ""
    echo "Creating local export directory instead..."
    TTA_DEV_REPO=""
fi

# Create export directory structure
echo -e "${BLUE}1️⃣  Creating export directory structure...${NC}"
mkdir -p "$EXPORT_DIR"/{src,tests,docs,specs}
mkdir -p "$EXPORT_DIR"/src/observability_integration/primitives
mkdir -p "$EXPORT_DIR"/tests/unit/observability_integration

# Copy source files
echo -e "${BLUE}2️⃣  Copying source files...${NC}"
cp src/observability_integration/__init__.py "$EXPORT_DIR"/src/observability_integration/
cp src/observability_integration/apm_setup.py "$EXPORT_DIR"/src/observability_integration/
cp src/observability_integration/primitives/__init__.py "$EXPORT_DIR"/src/observability_integration/primitives/
cp src/observability_integration/primitives/router.py "$EXPORT_DIR"/src/observability_integration/primitives/
cp src/observability_integration/primitives/cache.py "$EXPORT_DIR"/src/observability_integration/primitives/
cp src/observability_integration/primitives/timeout.py "$EXPORT_DIR"/src/observability_integration/primitives/

echo -e "${GREEN}   ✅ Copied 6 source files${NC}"

# Copy test files
echo -e "${BLUE}3️⃣  Copying test files...${NC}"
cp tests/unit/observability_integration/test_apm_setup.py "$EXPORT_DIR"/tests/unit/observability_integration/
cp tests/unit/observability_integration/test_router_primitive.py "$EXPORT_DIR"/tests/unit/observability_integration/
cp tests/unit/observability_integration/test_cache_primitive.py "$EXPORT_DIR"/tests/unit/observability_integration/
cp tests/unit/observability_integration/test_timeout_primitive.py "$EXPORT_DIR"/tests/unit/observability_integration/

echo -e "${GREEN}   ✅ Copied 4 test files${NC}"

# Copy documentation
echo -e "${BLUE}4️⃣  Copying documentation...${NC}"
cp specs/observability-integration.md "$EXPORT_DIR"/specs/
cp OBSERVABILITY_INTEGRATION_PROGRESS.md "$EXPORT_DIR"/docs/
cp OBSERVABILITY_PACKAGE_EXPORT_PLAN.md "$EXPORT_DIR"/docs/

echo -e "${GREEN}   ✅ Copied 3 documentation files${NC}"

# Create pyproject.toml
echo -e "${BLUE}5️⃣  Creating pyproject.toml...${NC}"
cat > "$EXPORT_DIR"/pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[project]
name = "tta-observability-integration"
version = "0.1.0"
description = "Comprehensive observability and monitoring integration for TTA platform"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "TTA Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "tta-dev-primitives>=0.1.0",
    "opentelemetry-api>=1.38.0",
    "opentelemetry-sdk>=1.38.0",
    "opentelemetry-exporter-prometheus>=0.59b0",
    "redis>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.11.0",
    "pyright>=1.1.350",
]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "C4", "UP"]
ignore = ["E501"]

[tool.pyright]
pythonVersion = "3.10"
typeCheckingMode = "basic"
EOF

echo -e "${GREEN}   ✅ Created pyproject.toml${NC}"

# Create README.md
echo -e "${BLUE}6️⃣  Creating README.md...${NC}"
cat > "$EXPORT_DIR"/README.md << 'EOF'
# TTA Observability Integration

Comprehensive observability and monitoring integration for the TTA (Therapeutic Text Adventure) platform.

## Features

- **OpenTelemetry APM Integration**: Distributed tracing and metrics collection
- **RouterPrimitive**: Route to optimal LLM provider (30% cost savings)
- **CachePrimitive**: Cache LLM responses (40% cost savings)
- **TimeoutPrimitive**: Enforce timeouts (prevent hanging workflows)

## Installation

```bash
uv add tta-observability-integration
```

## Quick Start

```python
from observability_integration import initialize_observability
from observability_integration.primitives import (
    RouterPrimitive,
    CachePrimitive,
    TimeoutPrimitive,
)

# Initialize APM (call this early in main.py)
initialize_observability(
    service_name="tta",
    enable_prometheus=True,
    prometheus_port=9464
)

# Use primitives with observability
workflow = (
    RouterPrimitive(routes={"fast": llama, "premium": gpt4})
    >> CachePrimitive(narrative_gen, ttl_seconds=3600)
    >> TimeoutPrimitive(timeout_seconds=30)
)
```

## Documentation

See `docs/` directory for complete documentation:
- `specs/observability-integration.md` - Complete specification
- `docs/OBSERVABILITY_INTEGRATION_PROGRESS.md` - Implementation progress
- `docs/OBSERVABILITY_PACKAGE_EXPORT_PLAN.md` - Export plan

## Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

## License

MIT (or as per TTA.dev repository)
EOF

echo -e "${GREEN}   ✅ Created README.md${NC}"

# Create CHANGELOG.md
echo -e "${BLUE}7️⃣  Creating CHANGELOG.md...${NC}"
cat > "$EXPORT_DIR"/CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-28

### Added
- Initial release of observability integration package
- OpenTelemetry APM setup with Prometheus export
- RouterPrimitive for LLM provider routing
- CachePrimitive for response caching
- TimeoutPrimitive for timeout enforcement
- Comprehensive test suite
- Complete documentation and specification

### Features
- Graceful degradation when OpenTelemetry unavailable
- Redis-based caching with configurable TTL
- Cost tracking and savings calculation
- OpenTelemetry metrics integration
- Environment-aware configuration
EOF

echo -e "${GREEN}   ✅ Created CHANGELOG.md${NC}"

# Create manifest file
echo -e "${BLUE}8️⃣  Creating file manifest...${NC}"
cat > "$EXPORT_DIR"/MANIFEST.txt << EOF
# Observability Package File Manifest
# Generated: $(date)

Source Files (6):
  src/observability_integration/__init__.py
  src/observability_integration/apm_setup.py
  src/observability_integration/primitives/__init__.py
  src/observability_integration/primitives/router.py
  src/observability_integration/primitives/cache.py
  src/observability_integration/primitives/timeout.py

Test Files (4):
  tests/unit/observability_integration/test_apm_setup.py
  tests/unit/observability_integration/test_router_primitive.py
  tests/unit/observability_integration/test_cache_primitive.py
  tests/unit/observability_integration/test_timeout_primitive.py

Documentation (3):
  specs/observability-integration.md
  docs/OBSERVABILITY_INTEGRATION_PROGRESS.md
  docs/OBSERVABILITY_PACKAGE_EXPORT_PLAN.md

Configuration Files (4):
  pyproject.toml
  README.md
  CHANGELOG.md
  MANIFEST.txt

Total Files: 17
EOF

echo -e "${GREEN}   ✅ Created MANIFEST.txt${NC}"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Export Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Package exported to: ${BLUE}$EXPORT_DIR${NC}"
echo ""
echo "Next steps:"
echo "  1. Review exported files in $EXPORT_DIR"
echo "  2. Copy to TTA.dev repository: packages/$PACKAGE_NAME/"
echo "  3. Run tests: cd $EXPORT_DIR && uv run pytest tests/"
echo "  4. Create PR in TTA.dev repository"
echo ""

if [ -n "$TTA_DEV_REPO" ]; then
    echo -e "${YELLOW}Would you like to copy to TTA.dev repository now? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        TARGET_DIR="$TTA_DEV_REPO/packages/$PACKAGE_NAME"
        echo -e "${BLUE}Copying to $TARGET_DIR...${NC}"
        mkdir -p "$TARGET_DIR"
        cp -r "$EXPORT_DIR"/* "$TARGET_DIR"/
        echo -e "${GREEN}✅ Copied to TTA.dev repository${NC}"
        echo ""
        echo "Next: cd $TARGET_DIR && uv run pytest tests/"
    fi
fi

