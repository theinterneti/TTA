#!/bin/bash
# Create GitHub issues for all component blockers based on maturity analysis

set -e

ANALYSIS_FILE="component-maturity-analysis.json"

if [ ! -f "$ANALYSIS_FILE" ]; then
    echo "❌ Error: $ANALYSIS_FILE not found"
    echo "Run: python scripts/analyze-component-maturity.py first"
    exit 1
fi

echo "========================================="
echo "TTA Component Blocker Issue Creator"
echo "========================================="
echo ""
echo "This script will create GitHub issues for component blockers."
echo "Issues will be created for components based on priority."
echo ""
echo "Priority Order:"
echo "  P0: Neo4j (PILOT) - Already created (#16, #17)"
echo "  P1: Docker, Carbon"
echo "  P2: Model Management, LLM, Agent Orchestration, Narrative Arc Orchestrator"
echo "  P3: Gameplay Loop, Character Arc Manager, Player Experience, Narrative Coherence, Therapeutic Systems"
echo ""

read -p "Create blocker issues for which priority? (P0/P1/P2/P3/all/skip): " PRIORITY

case $PRIORITY in
    P0)
        echo "✅ P0 (Neo4j) issues already created:"
        echo "  - Issue #16: Test Coverage"
        echo "  - Issue #17: Code Quality"
        ;;

    P1)
        echo ""
        echo "Creating P1 blocker issues (Docker, Carbon)..."
        echo ""

        # Docker - Test Coverage
        gh issue create \
          --title "[BLOCKER] Docker: Insufficient Test Coverage (0% → 70%)" \
          --label "component:docker,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Docker
**Blocker Type**: Tests (insufficient coverage)
**Target Stage**: Staging
**Severity**: Critical
**Priority**: P1

---

## Blocker Description

Docker component currently has **0% test coverage**, which is below the **70% threshold** required for promotion to Staging.

**Coverage Gap**: 70.0%

---

## Acceptance Criteria

- [ ] Unit test coverage ≥70% for core paths
- [ ] All unit tests passing
- [ ] Tests cover Docker lifecycle, health checks, error handling

---

## Estimated Effort

**Time**: 2-3 days
**Complexity**: Medium

---

## Related Documentation

- [Component Maturity Assessment Report](docs/development/COMPONENT_MATURITY_ASSESSMENT_REPORT.md)"

        # Docker - Linting
        gh issue create \
          --title "[BLOCKER] Docker: Code Quality Issues (148 Linting Errors)" \
          --label "component:docker,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Docker
**Blocker Type**: Code Quality (linting)
**Target Stage**: Staging
**Severity**: High
**Priority**: P1

---

## Blocker Description

Docker component has **148 linting issues** that must be resolved.

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/docker_component.py\` passes

---

## Estimated Effort

**Time**: 1 day
**Complexity**: Medium"

        # Docker - Type Checking
        gh issue create \
          --title "[BLOCKER] Docker: Type Checking Errors" \
          --label "component:docker,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Docker
**Blocker Type**: Code Quality (type checking)
**Target Stage**: Staging
**Severity**: High
**Priority**: P1

---

## Blocker Description

Docker component has type checking errors that must be resolved.

---

## Acceptance Criteria

- [ ] All type checking errors resolved
- [ ] \`uvx pyright src/components/docker_component.py\` passes

---

## Estimated Effort

**Time**: 0.5 days
**Complexity**: Low"

        # Carbon - Test Coverage
        gh issue create \
          --title "[BLOCKER] Carbon: Insufficient Test Coverage (0% → 70%)" \
          --label "component:carbon,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Carbon
**Blocker Type**: Tests (insufficient coverage)
**Target Stage**: Staging
**Severity**: Critical
**Priority**: P1

---

## Blocker Description

Carbon component currently has **0% test coverage**, which is below the **70% threshold** required for promotion to Staging.

**Coverage Gap**: 70.0%

---

## Acceptance Criteria

- [ ] Unit test coverage ≥70% for core paths
- [ ] All unit tests passing

---

## Estimated Effort

**Time**: 2-3 days
**Complexity**: Medium"

        # Carbon - Linting
        gh issue create \
          --title "[BLOCKER] Carbon: Code Quality Issues (69 Linting Errors)" \
          --label "component:carbon,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Carbon
**Blocker Type**: Code Quality (linting)
**Target Stage**: Staging
**Severity**: High
**Priority**: P1

---

## Blocker Description

Carbon component has **69 linting issues** that must be resolved.

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/carbon_component.py\` passes

---

## Estimated Effort

**Time**: 0.5-1 day
**Complexity**: Low"

        # Carbon - Type Checking
        gh issue create \
          --title "[BLOCKER] Carbon: Type Checking Errors" \
          --label "component:carbon,target:staging,blocker:tests,promotion:blocked" \
          --body "## Component Promotion Blocker

**Component**: Carbon
**Blocker Type**: Code Quality (type checking)
**Target Stage**: Staging
**Severity**: High
**Priority**: P1

---

## Blocker Description

Carbon component has type checking errors that must be resolved.

---

## Acceptance Criteria

- [ ] All type checking errors resolved
- [ ] \`uvx pyright src/components/carbon_component.py\` passes

---

## Estimated Effort

**Time**: 0.5 days
**Complexity**: Low"

        echo "✅ P1 blocker issues created!"
        ;;

    P2|P3|all)
        echo "⚠️  Creating issues for $PRIORITY would create 20+ issues."
        echo "Recommend creating issues incrementally as you work through components."
        echo ""
        echo "Use this script with P1 first, then P2, then P3 as needed."
        ;;

    skip)
        echo "Skipping issue creation."
        ;;

    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Issue Creation Complete!"
echo "========================================="
echo ""
echo "View all blocker issues:"
echo "  gh issue list --label promotion:blocked"
echo ""
echo "Next steps:"
echo "  1. Review created issues"
echo "  2. Begin work on Neo4j (pilot component)"
echo "  3. Create additional issues as needed"
