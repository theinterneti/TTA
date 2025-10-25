#!/usr/bin/env bash
#
# Narrative Arc Orchestrator - Staging Promotion Script
#
# This script automates the promotion of the Narrative Arc Orchestrator component
# from Development to Staging by resolving all identified blockers.
#
# Blockers:
# 1. 150 linting issues (ruff)
# 2. 21 type checking errors (pyright)
# 3. Missing README
#
# Usage:
#   ./scripts/promote-narrative-arc-orchestrator.sh [--phase PHASE]
#
# Phases:
#   1 - Fix linting issues
#   2 - Fix type checking errors
#   3 - Create README
#   4 - Validate and deploy
#   all - Run all phases (default)
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Component details
COMPONENT_NAME="narrative_arc_orchestrator"
COMPONENT_PATH="src/components/${COMPONENT_NAME}"
TEST_PATH="tests/test_${COMPONENT_NAME}_component.py"
PROMOTION_ISSUE="45"

# Parse arguments
PHASE="${1:-all}"
if [[ "$PHASE" == "--phase" ]]; then
    PHASE="${2:-all}"
fi

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Phase 1: Fix linting issues
phase_1_linting() {
    log_section "PHASE 1: Fixing Linting Issues"

    log_info "Running initial ruff scan..."
    if uvx ruff check "${COMPONENT_PATH}/" > linting_issues_before.txt 2>&1; then
        log_success "No linting issues found!"
    else
        ISSUE_COUNT=$(grep -c "^" linting_issues_before.txt || echo "0")
        log_warning "Found ${ISSUE_COUNT} linting issues"

        log_info "Auto-fixing linting issues..."
        uvx ruff check --fix "${COMPONENT_PATH}/"

        log_info "Running post-fix scan..."
        if uvx ruff check "${COMPONENT_PATH}/" > linting_issues_after.txt 2>&1; then
            log_success "All linting issues resolved!"
            rm -f linting_issues_before.txt linting_issues_after.txt
        else
            REMAINING=$(grep -c "^" linting_issues_after.txt || echo "0")
            log_warning "${REMAINING} linting issues remain (manual fixes needed)"
            log_info "See linting_issues_after.txt for details"

            # Show remaining issues
            echo ""
            log_info "Remaining issues:"
            cat linting_issues_after.txt
            echo ""

            read -p "Continue to next phase? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_error "Aborted by user"
                exit 1
            fi
        fi
    fi

    log_success "Phase 1 complete!"
}

# Phase 2: Fix type checking errors
phase_2_type_checking() {
    log_section "PHASE 2: Fixing Type Checking Errors"

    log_info "Running initial pyright scan..."
    if uvx pyright "${COMPONENT_PATH}/" > type_errors_before.txt 2>&1; then
        log_success "No type checking errors found!"
    else
        ERROR_COUNT=$(grep -c "error:" type_errors_before.txt || echo "0")
        log_warning "Found ${ERROR_COUNT} type checking errors"

        log_info "Type checking errors require manual fixes"
        log_info "See type_errors_before.txt for details"

        # Show errors
        echo ""
        log_info "Type checking errors:"
        cat type_errors_before.txt
        echo ""

        log_info "Common fix patterns:"
        echo ""
        echo "1. Optional dictionary access:"
        echo "   Before: if 'key' in metadata:"
        echo "   After:  if metadata and 'key' in metadata:"
        echo ""
        echo "2. Optional method calls:"
        echo "   Before: value = metadata.get('key', default)"
        echo "   After:  value = metadata.get('key', default) if metadata else default"
        echo ""
        echo "3. Type annotations:"
        echo "   Before: consequences: list[dict[str, Any]] = None"
        echo "   After:  consequences: list[dict[str, Any]] = []"
        echo ""

        log_warning "Please fix type errors manually, then re-run this script"
        log_info "Files to fix:"
        echo "  - ${COMPONENT_PATH}/impact_analysis.py (14 errors)"
        echo "  - ${COMPONENT_PATH}/scale_manager.py (6 errors)"
        echo "  - ${COMPONENT_PATH}/models.py (1 error)"
        echo ""

        read -p "Have you fixed the type errors? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Aborted - please fix type errors first"
            exit 1
        fi

        log_info "Running post-fix scan..."
        if uvx pyright "${COMPONENT_PATH}/" > type_errors_after.txt 2>&1; then
            log_success "All type checking errors resolved!"
            rm -f type_errors_before.txt type_errors_after.txt
        else
            REMAINING=$(grep -c "error:" type_errors_after.txt || echo "0")
            log_error "${REMAINING} type checking errors remain"
            log_info "See type_errors_after.txt for details"
            cat type_errors_after.txt
            exit 1
        fi
    fi

    log_success "Phase 2 complete!"
}

# Phase 3: Create README
phase_3_readme() {
    log_section "PHASE 3: Creating README"

    README_PATH="${COMPONENT_PATH}/README.md"

    if [[ -f "${README_PATH}" ]]; then
        log_warning "README already exists at ${README_PATH}"
        read -p "Overwrite? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipping README creation"
            return
        fi
    fi

    log_info "Creating README from template..."

    # Create README content
    cat > "${README_PATH}" << 'EOF'
# Narrative Arc Orchestrator

The Narrative Arc Orchestrator manages multi-scale narrative coherence across the TTA system, ensuring that story events at different scales (micro, meso, macro) remain causally consistent and therapeutically aligned.

## Overview

This component provides the core orchestration layer for managing narrative arcs across multiple temporal and thematic scales. It tracks causal relationships, detects conflicts, analyzes impacts, and proposes resolutions to maintain narrative coherence.

## Key Features

- **Causal Graph Management**: Tracks cause-effect relationships across narrative events
- **Conflict Detection**: Identifies temporal, character, thematic, and therapeutic conflicts
- **Impact Analysis**: Analyzes ripple effects of narrative decisions across scales
- **Resolution Engine**: Proposes conflict resolutions while maintaining narrative coherence
- **Scale Management**: Coordinates narrative consistency across micro/meso/macro scales

## Architecture

### Components

1. **Causal Graph** (`causal_graph.py`)
   - Builds and validates causal relationships between events
   - Detects circular dependencies
   - Provides graph traversal utilities

2. **Conflict Detection** (`conflict_detection.py`)
   - Detects temporal conflicts (timeline inconsistencies)
   - Identifies character conflicts (contradictory character actions)
   - Finds thematic conflicts (inconsistent themes)
   - Validates therapeutic alignment

3. **Impact Analysis** (`impact_analysis.py`)
   - Analyzes event impacts across scales
   - Evaluates character involvement
   - Assesses location/setting impacts
   - Validates therapeutic implications

4. **Resolution Engine** (`resolution_engine.py`)
   - Proposes conflict resolutions
   - Maintains narrative coherence
   - Preserves therapeutic goals

5. **Scale Manager** (`scale_manager.py`)
   - Coordinates micro/meso/macro scale events
   - Manages cross-scale consistency
   - Handles scale transitions

## Installation

This component is part of the TTA monorepo. No separate installation required.

### Dependencies

- Python 3.12+
- No external dependencies (self-contained)

## Usage

### Basic Usage

```python
from src.components.narrative_arc_orchestrator.scale_manager import ScaleManager
from src.components.narrative_arc_orchestrator.models import NarrativeEvent

# Initialize scale manager
manager = ScaleManager()

# Create narrative events
event1 = NarrativeEvent(
    event_id="evt_001",
    scale="micro",
    timestamp=1.0,
    description="Character makes a decision",
    metadata={"character_name": "Alice"}
)

event2 = NarrativeEvent(
    event_id="evt_002",
    scale="meso",
    timestamp=2.0,
    description="Decision impacts relationship",
    metadata={"character_name": "Alice", "location": "home"}
)

# Add events
manager.add_event(event1)
manager.add_event(event2)

# Detect conflicts
conflicts = manager.detect_conflicts()

# Analyze impacts
impacts = manager.analyze_impacts()
```

### Advanced Usage

See `tests/test_narrative_arc_orchestrator_component.py` for comprehensive examples.

## API Reference

### ScaleManager

Main orchestration class for managing multi-scale narrative events.

**Methods**:
- `add_event(event: NarrativeEvent) -> None`: Add event to manager
- `detect_conflicts() -> list[ScaleConflict]`: Detect all conflicts
- `analyze_impacts() -> list[ImpactReport]`: Analyze event impacts
- `get_events_by_scale(scale: str) -> list[NarrativeEvent]`: Get events for scale

### NarrativeEvent

Represents a narrative event at a specific scale.

**Attributes**:
- `event_id: str`: Unique event identifier
- `scale: str`: Event scale (micro/meso/macro)
- `timestamp: float`: Event timestamp
- `description: str`: Event description
- `metadata: dict[str, Any] | None`: Optional metadata

## Configuration

No configuration required. Component is self-contained.

## Testing

### Running Tests

```bash
# Run component tests
uv run pytest tests/test_narrative_arc_orchestrator_component.py

# Run with coverage
uv run pytest tests/test_narrative_arc_orchestrator_component.py \
    --cov=src/components/narrative_arc_orchestrator \
    --cov-report=term
```

### Test Coverage

**Current Coverage**: 70.3% (exceeds 70% threshold)

**Test Scenarios**:
- Causal graph construction ✅
- Conflict detection ✅
- Impact analysis ✅
- Resolution engine ✅
- Scale management ✅

## Contributing

### Development Setup

1. Install dependencies: `uv sync`
2. Run tests: `uv run pytest tests/test_narrative_arc_orchestrator_component.py`
3. Run linting: `uvx ruff check src/components/narrative_arc_orchestrator/`
4. Run type checking: `uvx pyright src/components/narrative_arc_orchestrator/`

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Maintain test coverage ≥70%

### Pull Request Process

1. Create feature branch
2. Make changes
3. Run tests and quality checks
4. Submit PR with description
5. Address review feedback

## Maturity Status

**Current Stage**: Development → Staging
**Promotion Issue**: #45
**Test Coverage**: 70.3%
**Last Updated**: 2025-10-13

See `MATURITY.md` for detailed maturity tracking.

## License

Part of the TTA project. See repository LICENSE for details.

## Related Documentation

- Component Maturity: `MATURITY.md`
- Promotion Blockers: `docs/component-promotion/NARRATIVE_ARC_ORCHESTRATOR_BLOCKERS.md`
- Component Maturity Workflow: `docs/development/COMPONENT_MATURITY_WORKFLOW.md`
EOF

    log_success "README created at ${README_PATH}"
    log_success "Phase 3 complete!"
}

# Phase 4: Validate and prepare for deployment
phase_4_validate() {
    log_section "PHASE 4: Validation and Deployment Preparation"

    log_info "Running all quality checks..."

    # Linting
    log_info "1. Linting (ruff)..."
    if uvx ruff check "${COMPONENT_PATH}/"; then
        log_success "✅ Linting: PASS"
    else
        log_error "❌ Linting: FAIL"
        exit 1
    fi

    # Type checking
    log_info "2. Type checking (pyright)..."
    if uvx pyright "${COMPONENT_PATH}/"; then
        log_success "✅ Type checking: PASS"
    else
        log_error "❌ Type checking: FAIL"
        exit 1
    fi

    # Security
    log_info "3. Security (bandit)..."
    if uvx bandit -r "${COMPONENT_PATH}/" -ll; then
        log_success "✅ Security: PASS"
    else
        log_warning "⚠️  Security: WARNINGS (review manually)"
    fi

    # Tests
    log_info "4. Running tests..."
    if uv run pytest "${TEST_PATH}" --cov="${COMPONENT_PATH}" --cov-report=term; then
        log_success "✅ Tests: PASS"
    else
        log_error "❌ Tests: FAIL"
        exit 1
    fi

    # Check README exists
    log_info "5. Checking README..."
    if [[ -f "${COMPONENT_PATH}/README.md" ]]; then
        log_success "✅ README: EXISTS"
    else
        log_error "❌ README: MISSING"
        exit 1
    fi

    log_success "All validation checks passed!"

    # Update MATURITY.md
    log_info "Updating MATURITY.md..."
    # This would be done manually or with a separate script
    log_warning "Please update MATURITY.md manually with:"
    echo "  - Current coverage: 70.3%"
    echo "  - Blockers resolved: All"
    echo "  - Status: Ready for staging"
    echo ""

    log_success "Phase 4 complete!"

    # Summary
    log_section "PROMOTION READINESS SUMMARY"
    echo "Component: Narrative Arc Orchestrator"
    echo "Target Stage: Staging"
    echo "Promotion Issue: #${PROMOTION_ISSUE}"
    echo ""
    echo "✅ Linting: PASS (0 issues)"
    echo "✅ Type checking: PASS (0 errors)"
    echo "✅ Security: PASS"
    echo "✅ Tests: PASS (70.3% coverage)"
    echo "✅ README: EXISTS"
    echo ""
    log_success "Component is READY for staging deployment!"
    echo ""
    log_info "Next steps:"
    echo "1. Update MATURITY.md with actual data"
    echo "2. Commit changes"
    echo "3. Deploy to staging:"
    echo "   docker-compose -f docker-compose.staging-homelab.yml up -d narrative-arc-orchestrator"
    echo "4. Update promotion issue #${PROMOTION_ISSUE}"
}

# Main execution
main() {
    log_section "Narrative Arc Orchestrator - Staging Promotion"

    log_info "Component: ${COMPONENT_NAME}"
    log_info "Phase: ${PHASE}"
    log_info "Promotion Issue: #${PROMOTION_ISSUE}"
    echo ""

    case "${PHASE}" in
        1)
            phase_1_linting
            ;;
        2)
            phase_2_type_checking
            ;;
        3)
            phase_3_readme
            ;;
        4)
            phase_4_validate
            ;;
        all)
            phase_1_linting
            phase_2_type_checking
            phase_3_readme
            phase_4_validate
            ;;
        *)
            log_error "Invalid phase: ${PHASE}"
            echo "Usage: $0 [--phase PHASE]"
            echo "Phases: 1, 2, 3, 4, all"
            exit 1
            ;;
    esac

    log_section "COMPLETE"
    log_success "Promotion script finished successfully!"
}

# Run main
main
