# Dependency Resolution Plan - UV & Storybook/Vite 7 Compatibility

**Created**: October 27, 2025
**Status**: In Progress
**Priority**: High

## Executive Summary

**CORRECTED ANALYSIS**:

1. ✅ **UV Configuration**: Project correctly uses BOTH standards
   - `[dependency-groups]` (PEP 735) - **PRIMARY** for granular dependencies
   - `[project.optional-dependencies]` (PEP 621) - **LEGACY** for backwards compatibility

2. ⚠️ **Storybook + Vite 7**: Incompatibility requires strategic upgrade

## Issue 1: UV Dependency Configuration ✅

### Current State - CORRECT UNDERSTANDING

The project uses **BOTH** dependency systems:

**Primary (Modern)**: `[dependency-groups]` (PEP 735)
```toml
[dependency-groups]
dev = [...]
test = [...]
lint = [...]
type = [...]
```

**Legacy (Backwards Compat)**: `[project.optional-dependencies]` (PEP 621)
```toml
[project.optional-dependencies]
dev = [...]
minimal = [...]
```

### Correct UV Syntax

```bash
# ✅ CORRECT - For dependency-groups (PEP 735)
uv sync --group dev
uv sync --group test
uv sync --all-groups  # Install all groups

# ✅ ALSO CORRECT - For optional-dependencies (PEP 621)
uv sync --extra dev
uv sync --all-extras  # Install all extras

# ⚠️ MIXED (Works but inconsistent)
uv sync --all-extras --dev  # Used in some workflows
```

### Action Required

**NO CHANGES NEEDED** - The project is correctly configured!

However, **CONSISTENCY IMPROVEMENT** recommended:
- Migrate all workflows from `--all-extras --dev` to `--all-groups`
- Remove legacy `[project.optional-dependencies]` after migration
- Update documentation to reflect PEP 735 as primary

### Files Using OLD Syntax (Optional Migration)

```bash
# Find all files using old syntax
grep -r "uv sync --all-extras --dev" .github/workflows/
```

Results:
- `.github/workflows/tests.yml` (2 instances)
- `.github/workflows/code-quality.yml` (1 instance)
- `.github/workflows/comprehensive-test-battery.yml` (3 instances)
- `.github/workflows/security-scan.yml` (2 instances)
- `.github/workflows/performance-tracking.yml` (6 instances)
- `.github/workflows/codeql.yml` (1 instance)
- `.github/workflows/post-deployment-tests.yml` (1 instance)

**Migration Example**:
```yaml
# BEFORE
- name: Install dependencies
  run: uv sync --all-extras --dev

# AFTER
- name: Install dependencies
  run: uv sync --all-groups
```

## Issue 2: Storybook + Vite 7 Compatibility ⚠️

### Problem
- **Current**: Storybook 8.6.14 + Vite 7.1.6
- **Issue**: Storybook does NOT officially support Vite 7 (as of October 2025)
- **Max Support**: Storybook 9.1.0-alpha.6 supports Vite ^6.2.5
- **Reference**: [GitHub Issue #31858](https://github.com/storybookjs/storybook/issues/31858)

### Recommended Solution: Option A (Experimental)

Upgrade to Storybook 9.0+ alpha with npm overrides to force Vite 7 compatibility.

**Pros**:
- Bleeding-edge approach
- Aligns with project's modern tooling preference
- Likely to work (many projects successful)

**Cons**:
- Experimental/unsupported
- May break in future
- Requires manual testing

### Implementation Steps

#### Step 1: Upgrade Storybook
```bash
cd src/player_experience/frontend
npx storybook@latest upgrade
```

#### Step 2: Update package.json
```json
{
  "dependencies": {
    "@storybook/addon-essentials": "^9.1.0-alpha.6",
    "@storybook/addon-interactions": "^9.1.0-alpha.6",
    "@storybook/addon-links": "^9.1.0-alpha.6",
    "@storybook/addon-onboarding": "^9.1.0-alpha.6",
    "@storybook/blocks": "^9.1.0-alpha.6",
    "@storybook/react-vite": "^9.1.0-alpha.6",
    "@storybook/test-runner": "^0.23.0",
    "storybook": "^9.1.0-alpha.6",
    "vite": "^7.1.6"
  },
  "overrides": {
    "vite": "^7.1.6",  // Force Vite 7
    "nth-check": "^2.1.1",
    "postcss": "^8.4.31",
    "webpack-dev-server": "^5.2.1"
  }
}
```

#### Step 3: Test Storybook
```bash
npm install
npm run storybook
npm run build-storybook
npm run test:storybook
```

#### Step 4: Validate Visual Regression Tests
```bash
npm run test:visual
```

### Alternative: Option B (Conservative)

Remove Storybook temporarily until official Vite 7 support.

**Only if Option A fails after testing.**

## Risk Assessment

### Option A Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Build failures | Medium | High | Comprehensive testing before merge |
| Runtime errors | Low | Medium | Browser testing in dev/staging |
| Future breaking changes | High | Low | Monitor Storybook releases |
| Developer experience issues | Low | Low | Document workarounds |

### Option B Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Lost component documentation | High | High | Export existing stories |
| Visual regression testing gaps | High | High | Use Playwright alternatives |
| Developer productivity loss | Medium | Medium | Focus on Playwright tests |

## Testing Checklist

### Before Implementation
- [x] Backup current package.json
- [x] Document current Storybook functionality
- [x] Export existing stories to markdown

### After Implementation (Option A)
- [ ] Storybook dev server starts successfully
- [ ] All existing stories render correctly
- [ ] Storybook build completes without errors
- [ ] Test runner executes successfully
- [ ] Visual regression tests pass
- [ ] No console errors in browser
- [ ] Hot reload works correctly
- [ ] Addon functionality preserved

### Rollback Plan
If Option A fails:
1. Revert package.json changes
2. Run `npm install`
3. Verify Storybook works with Vite 6
4. Consider downgrading Vite to 6.x (last resort)

## Timeline

| Phase | Duration | Owner | Status |
|-------|----------|-------|--------|
| UV Config Updates | 1 hour | GitHub Copilot | ✅ Ready |
| Storybook Upgrade | 2 hours | GitHub Copilot | 🔄 Pending Approval |
| Testing | 3 hours | QA | ⏳ Blocked |
| Documentation | 1 hour | Dev | ⏳ Blocked |

## Decision Point

**Proceed with Option A?** YES / NO / WAIT

If YES:
- Continue with Storybook 9.x alpha + Vite 7 overrides
- Accept experimental status
- Monitor for issues

If NO:
- Implement Option B (remove Storybook)
- Wait for official Vite 7 support
- Re-evaluate in future

If WAIT:
- Keep current setup
- Downgrade Vite to 6.x temporarily
- Revisit when Storybook 9.x stable releases

## Notes

- Storybook team actively working on Vite 7 support
- Expected official support: Q1 2026 (estimated)
- Alternative component documentation: MDX files in `/docs/components`
- Visual testing can continue with Playwright regardless

## References

- [Storybook Issue #31858](https://github.com/storybookjs/storybook/issues/31858)
- [PEP 621 - Dependency Specification](https://peps.python.org/pep-0621/)
- [UV Documentation - Extras](https://docs.astral.sh/uv/concepts/dependencies/#extras)
- [Vite 7 Release Notes](https://vite.dev/guide/)

---

**Next Steps**: Await approval for Option A implementation.
