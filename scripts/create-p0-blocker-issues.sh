#!/bin/bash
# Create GitHub issues for P0 components (ready for staging, just need code quality fixes)

set -e

echo "========================================="
echo "TTA P0 Component Blocker Issue Creator"
echo "========================================="
echo ""
echo "This script creates blocker issues for the 4 P0 components that are"
echo "ready for staging (already have sufficient test coverage)."
echo ""
echo "P0 Components:"
echo "  1. Carbon (69.7% coverage - 0.3% gap)"
echo "  2. Model Management (100% coverage)"
echo "  3. Gameplay Loop (100% coverage)"
echo "  4. Narrative Coherence (100% coverage)"
echo ""

read -p "Create P0 blocker issues? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Creating P0 blocker issues..."
echo ""

# ============================================================================
# CARBON - 69.7% coverage (0.3% gap)
# ============================================================================

echo "📊 Creating issues for Carbon..."

# Carbon - Test Coverage (0.3% gap)
gh issue create \
  --title "[P0] Carbon: Add 1-2 Tests to Reach 70% Coverage (Currently 69.7%)" \
  --label "component:carbon,target:staging,blocker:tests,promotion:blocked,priority:high" \
  --body "## Component Promotion Blocker

**Component**: Carbon
**Blocker Type**: Tests (minimal gap)
**Target Stage**: Staging
**Severity**: Low
**Priority**: **P0 (Quick Win!)**
**Current Coverage**: **69.7%**
**Gap**: **0.3%** (just 1-2 tests needed!)

---

## Blocker Description

Carbon component has **69.7% test coverage**, just **0.3% below** the 70% threshold for staging promotion.

This is the **easiest and fastest win** - add 1-2 simple tests and this component is ready!

---

## Acceptance Criteria

- [ ] Test coverage ≥70%
- [ ] All tests passing
- [ ] Coverage verified with: \`uv run pytest tests/test_components.py --cov=src/components/carbon_component.py --cov-report=term\`

---

## Proposed Solution

Add 1-2 simple tests to \`tests/test_components.py\`:

\`\`\`python
def test_carbon_health_check(self):
    \"\"\"Test Carbon component health check.\"\"\"
    config = TTAConfig()
    carbon = CarbonComponent(config)
    carbon.start()

    health = carbon.health_check()
    assert health is not None
    assert \"status\" in health

    carbon.stop()

def test_carbon_error_handling(self):
    \"\"\"Test Carbon component error handling.\"\"\"
    config = TTAConfig()
    carbon = CarbonComponent(config)

    # Test handling of invalid configuration
    # Add appropriate error handling test
\`\`\`

---

## Verification

\`\`\`bash
# Run tests with coverage
uv run pytest tests/test_components.py::TestComponents::test_carbon_component \\
  tests/test_components.py::TestComponents::test_carbon_health_check \\
  tests/test_components.py::TestComponents::test_carbon_error_handling \\
  --cov=src/components/carbon_component.py \\
  --cov-report=term

# Should show ≥70% coverage
\`\`\`

---

## Estimated Effort

**Time**: 0.5 days
**Complexity**: Very Low
**Impact**: HIGH (first component to staging!)

---

## Related Issues

- Part of P0 quick wins (Week 1)
- Blocks: Carbon → Staging promotion
- Related: Code quality blockers for Carbon

---

**This is the FASTEST path to your first staging promotion!** 🎉"

# Carbon - Code Quality (Linting)
gh issue create \
  --title "[P0] Carbon: Fix Code Quality Issues (69 Linting Errors, Type Checking)" \
  --label "component:carbon,target:staging,blocker:tests,promotion:blocked,priority:high" \
  --body "## Component Promotion Blocker

**Component**: Carbon
**Blocker Type**: Code Quality
**Target Stage**: Staging
**Severity**: Medium
**Priority**: **P0**
**Coverage**: 69.7% ✅ (will be ≥70% after test blocker resolved)

---

## Blocker Description

Carbon component has:
- **69 linting issues**
- **Type checking errors**

These must be resolved before staging promotion.

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/carbon_component.py\` passes
- [ ] \`uvx pyright src/components/carbon_component.py\` passes
- [ ] \`uvx bandit -r src/components/carbon_component.py -ll\` passes

---

## Proposed Solution

### 1. Auto-fix Linting

\`\`\`bash
# Auto-fix most issues
uvx ruff check --fix src/components/carbon_component.py

# Check remaining
uvx ruff check src/components/carbon_component.py
\`\`\`

### 2. Fix Type Checking

\`\`\`bash
# Identify type errors
uvx pyright src/components/carbon_component.py

# Fix manually (likely related to CODECARBON_AVAILABLE constant)
\`\`\`

### 3. Verify All Checks

\`\`\`bash
uvx ruff check src/components/carbon_component.py
uvx pyright src/components/carbon_component.py
uvx bandit -r src/components/carbon_component.py -ll
\`\`\`

---

## Estimated Effort

**Time**: 0.5 days
**Complexity**: Low (mostly auto-fixable)

---

## Related Issues

- Part of P0 quick wins (Week 1)
- Blocks: Carbon → Staging promotion"

echo "✅ Carbon issues created!"
echo ""

# ============================================================================
# MODEL MANAGEMENT - 100% coverage
# ============================================================================

echo "📊 Creating issues for Model Management..."

# Model Management - Code Quality
gh issue create \
  --title "[P0] Model Management: Fix Code Quality Issues (665 Linting, Type Errors, Security)" \
  --label "component:model-management,target:staging,blocker:tests,blocker:security,promotion:blocked,priority:high" \
  --body "## Component Promotion Blocker

**Component**: Model Management
**Blocker Type**: Code Quality + Security
**Target Stage**: Staging
**Severity**: High
**Priority**: **P0**
**Coverage**: **100%** ✅ (tests already sufficient!)

---

## Blocker Description

Model Management has **100% test coverage** but needs code quality fixes:
- **665 linting issues** (highest count)
- **Type checking errors**
- **Security issues** (Hugging Face unsafe downloads)

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/model_management/\` passes
- [ ] \`uvx pyright src/components/model_management/\` passes
- [ ] \`uvx bandit -r src/components/model_management/ -ll\` passes (no security issues)

---

## Proposed Solution

### 1. Fix Security Issues (PRIORITY)

**Issue**: Unsafe Hugging Face downloads without revision pinning

\`\`\`python
# BEFORE (unsafe)
model = AutoModel.from_pretrained(model_name)

# AFTER (safe - pin to specific revision)
model = AutoModel.from_pretrained(
    model_name,
    revision=\"abc123def456\"  # Specific commit hash
)
\`\`\`

**Files to update**:
- \`src/components/model_management/providers/local.py\`
- Any other files using \`from_pretrained()\`

### 2. Auto-fix Linting

\`\`\`bash
uvx ruff check --fix src/components/model_management/
\`\`\`

### 3. Fix Remaining Issues

\`\`\`bash
uvx ruff check src/components/model_management/
uvx pyright src/components/model_management/
\`\`\`

---

## Estimated Effort

**Time**: 2-3 days
**Complexity**: Medium (security fixes require careful testing)

---

## Related Issues

- Part of P0 quick wins (Week 1)
- Blocks: Model Management → Staging promotion"

echo "✅ Model Management issues created!"
echo ""

# ============================================================================
# GAMEPLAY LOOP - 100% coverage
# ============================================================================

echo "📊 Creating issues for Gameplay Loop..."

gh issue create \
  --title "[P0] Gameplay Loop: Fix Code Quality Issues (1,247 Linting, Type Errors) + Add README" \
  --label "component:gameplay-loop,target:staging,blocker:tests,blocker:documentation,promotion:blocked,priority:high" \
  --body "## Component Promotion Blocker

**Component**: Gameplay Loop
**Blocker Type**: Code Quality + Documentation
**Target Stage**: Staging
**Severity**: Medium
**Priority**: **P0**
**Coverage**: **100%** ✅ (tests already sufficient!)

---

## Blocker Description

Gameplay Loop has **100% test coverage** but needs:
- **1,247 linting issues** (second highest count)
- **Type checking errors**
- **Missing README**

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/gameplay_loop/\` passes
- [ ] \`uvx pyright src/components/gameplay_loop/\` passes
- [ ] README created with usage examples

---

## Proposed Solution

### 1. Auto-fix Linting

\`\`\`bash
uvx ruff check --fix src/components/gameplay_loop/
\`\`\`

### 2. Fix Remaining Issues

\`\`\`bash
uvx ruff check src/components/gameplay_loop/
uvx pyright src/components/gameplay_loop/
\`\`\`

### 3. Create README

\`\`\`bash
touch src/components/gameplay_loop/README.md
\`\`\`

**README should include**:
- Component overview
- Key features
- Usage examples
- API documentation
- Configuration options

---

## Estimated Effort

**Time**: 2-3 days
**Complexity**: Medium (many linting issues, but mostly auto-fixable)

---

## Related Issues

- Part of P0 quick wins (Week 1)
- Blocks: Gameplay Loop → Staging promotion"

echo "✅ Gameplay Loop issues created!"
echo ""

# ============================================================================
# NARRATIVE COHERENCE - 100% coverage
# ============================================================================

echo "📊 Creating issues for Narrative Coherence..."

gh issue create \
  --title "[P0] Narrative Coherence: Fix Code Quality Issues (433 Linting, Type Errors) + Add README" \
  --label "component:narrative-coherence,target:staging,blocker:tests,blocker:documentation,promotion:blocked,priority:high" \
  --body "## Component Promotion Blocker

**Component**: Narrative Coherence
**Blocker Type**: Code Quality + Documentation
**Target Stage**: Staging
**Severity**: Medium
**Priority**: **P0**
**Coverage**: **100%** ✅ (tests already sufficient!)

---

## Blocker Description

Narrative Coherence has **100% test coverage** but needs:
- **433 linting issues**
- **Type checking errors**
- **Missing README**

---

## Acceptance Criteria

- [ ] All linting issues resolved
- [ ] \`uvx ruff check src/components/narrative_coherence/\` passes
- [ ] \`uvx pyright src/components/narrative_coherence/\` passes
- [ ] README created with usage examples

---

## Proposed Solution

### 1. Auto-fix Linting

\`\`\`bash
uvx ruff check --fix src/components/narrative_coherence/
\`\`\`

### 2. Fix Remaining Issues

\`\`\`bash
uvx ruff check src/components/narrative_coherence/
uvx pyright src/components/narrative_coherence/
\`\`\`

### 3. Create README

\`\`\`bash
touch src/components/narrative_coherence/README.md
\`\`\`

**README should include**:
- Component overview
- Coherence validation features
- Usage examples
- API documentation

---

## Estimated Effort

**Time**: 1-2 days
**Complexity**: Low-Medium (mostly auto-fixable)

---

## Related Issues

- Part of P0 quick wins (Week 1)
- Blocks: Narrative Coherence → Staging promotion"

echo "✅ Narrative Coherence issues created!"
echo ""

echo "========================================="
echo "✅ All P0 Blocker Issues Created!"
echo "========================================="
echo ""
echo "View all blocker issues:"
echo "  gh issue list --label promotion:blocked"
echo ""
echo "Next steps:"
echo "  1. Start with Carbon (easiest win - 0.3% gap)"
echo "  2. Then Narrative Coherence (smallest linting count)"
echo "  3. Then Gameplay Loop"
echo "  4. Then Model Management (security fixes need care)"
