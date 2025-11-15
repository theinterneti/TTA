# UV & Storybook Dependency Resolution Summary

**Date**: October 27, 2025
**Prepared By**: GitHub Copilot
**Status**: Analysis Complete - Awaiting Decision

---

## TLDR

✅ **UV Configuration**: Already correct, optional consistency improvements available
⚠️ **Storybook + Vite 7**: Requires decision - Upgrade to experimental alpha OR remove temporarily

---

## Part 1: UV Dependency Configuration

### What You Thought Was Wrong
> "Your project uses `[project.optional-dependencies]` (not `[dependency-groups]`), which is the standard PEP 621 format. This means you should use `--extra` instead of `--group`."

### The Reality ✅

**Your project is CORRECT** - it uses BOTH systems intentionally:

1. **Primary (Modern)**: `[dependency-groups]` - PEP 735 standard
   - Enables granular dependency installation
   - Faster CI/CD with `uv sync --group test` vs full sync
   - Used in: tests.yml, code-quality.yml

2. **Legacy (Backwards Compat)**: `[project.optional-dependencies]` - PEP 621 standard
   - Maintained for tools that don't support PEP 735 yet
   - Deprecated per comments in pyproject.toml
   - Used in: some older workflows

### What This Means

**NO URGENT CHANGES REQUIRED**

Both syntaxes work correctly:
```bash
# ✅ Modern (PEP 735) - PREFERRED
uv sync --group dev
uv sync --group test
uv sync --all-groups

# ✅ Legacy (PEP 621) - STILL WORKS
uv sync --extra dev
uv sync --all-extras

# ⚠️ Mixed (INCONSISTENT but functional)
uv sync --all-extras --dev  # Used in 16 workflow files
```

### Optional Improvement: Consistency Migration

**Why?** Standardize on modern PEP 735 syntax project-wide

**Effort**: ~30 minutes
**Risk**: Low (both work, just for consistency)
**Impact**: Cleaner codebase, easier onboarding

**Files to Update** (16 total):
```
.github/workflows/tests.yml (2x)
.github/workflows/code-quality.yml (1x)
.github/workflows/comprehensive-test-battery.yml (3x)
.github/workflows/security-scan.yml (2x)
.github/workflows/performance-tracking.yml (6x)
.github/workflows/codeql.yml (1x)
.github/workflows/post-deployment-tests.yml (1x)
```

**Simple Find & Replace**:
```yaml
# FIND
run: uv sync --all-extras --dev

# REPLACE WITH
run: uv sync --all-groups
```

**Do you want me to make this change?** (Optional, non-urgent)

---

## Part 2: Storybook + Vite 7 Compatibility

### The Problem

- **Your Setup**: Storybook 8.6.14 + Vite 7.1.6
- **Storybook Support**: Only up to Vite ^6.2.5
- **Latest Alpha**: Storybook 9.1.0-alpha.6 (still Vite 6 max)
- **Official Vite 7 Support**: Not available (Q1 2026 estimated)

**Reference**: [Storybook Issue #31858](https://github.com/storybookjs/storybook/issues/31858)

### Option A: Experimental Upgrade (Recommended)

**Upgrade to Storybook 9.x alpha + force Vite 7 via npm overrides**

**Pros**:
- Keeps cutting-edge Vite 7 features
- Likely to work (community success stories)
- Aligns with your modern tooling philosophy
- Get Storybook 9.x improvements

**Cons**:
- Unsupported/experimental
- May break on future updates
- Requires manual testing
- No official guarantees

**Implementation**:
```bash
cd src/player_experience/frontend
npx storybook@latest upgrade
```

Then update `package.json`:
```json
{
  "dependencies": {
    "@storybook/addon-essentials": "^9.1.0-alpha.6",
    "@storybook/blocks": "^9.1.0-alpha.6",
    "@storybook/react-vite": "^9.1.0-alpha.6",
    "storybook": "^9.1.0-alpha.6",
    "vite": "^7.1.6"
  },
  "overrides": {
    "vite": "^7.1.6"  // Force Vite 7 compatibility
  }
}
```

**Testing Required**:
- [ ] `npm run storybook` - Dev server starts
- [ ] `npm run build-storybook` - Build succeeds
- [ ] `npm run test:storybook` - Tests pass
- [ ] Browser testing - No console errors
- [ ] Visual regression tests - Snapshots match

**Rollback**: Revert package.json, run `npm install`

### Option B: Conservative Removal

**Remove Storybook until official Vite 7 support**

**Pros**:
- Zero compatibility issues
- Cleaner dependency tree
- Can wait for official support

**Cons**:
- Lose component documentation
- Lose visual regression testing
- Developer productivity impact
- Community collaboration harder

**Implementation**:
```bash
# Export existing stories first
npm run build-storybook
mv storybook-static docs/archived-storybook

# Remove Storybook
npm uninstall $(npm ls --all --parseable | grep @storybook | awk -F/ '{print $NF}')
```

**Alternatives**:
- Use Playwright component testing instead
- Generate MDX docs from stories
- Wait for Q1 2026 official support

### Option C: Downgrade Vite (Last Resort)

**Downgrade to Vite 6.x temporarily**

**Only if**: Options A & B both rejected

**Risk**: Lose Vite 7 performance/features you may be using

---

## Decision Matrix

| Criterion | Option A (Upgrade) | Option B (Remove) | Option C (Downgrade) |
|-----------|-------------------|------------------|---------------------|
| **Risk** | Medium | Low | Low |
| **Effort** | 2-3 hours | 1 hour | 30 minutes |
| **Modern Tooling** | ✅ Yes | ❌ No | ❌ No |
| **Maintainability** | ⚠️ Experimental | ✅ Clean | ⚠️ Temporary |
| **Developer Experience** | ✅ Best | ❌ Degraded | ✅ Unchanged |
| **Recommended For** | Your project! | Conservative teams | Emergency only |

---

## My Recommendation

### For Part 1 (UV Config)
**No action required** - Your setup is correct. Optional consistency cleanup available if desired.

### For Part 2 (Storybook + Vite 7)
**Proceed with Option A** - Experimental Upgrade

**Reasoning**:
1. Your project already uses cutting-edge tooling (Vite 7, Python 3.12+)
2. Community reports success with this approach
3. You can always rollback if issues arise
4. Aligns with project's modern architecture philosophy
5. Risk is acceptable given thorough testing plan

**Next Steps**:
1. **Approve/Reject** this recommendation
2. If approved, I'll:
   - Create backup of current package.json
   - Upgrade Storybook to 9.x alpha
   - Add Vite 7 override
   - Run all tests
   - Document any workarounds needed
3. If rejected, choose Option B or C

---

## What Do You Want Me To Do?

**Part 1 (UV Consistency)**:
- [ ] Yes, migrate all workflows to `--all-groups` (30 min)
- [ ] No, keep current mixed syntax (works fine)
- [ ] Explain the difference more

**Part 2 (Storybook + Vite 7)**:
- [ ] Proceed with Option A (Experimental Upgrade)
- [ ] Proceed with Option B (Remove Storybook)
- [ ] Proceed with Option C (Downgrade Vite)
- [ ] I need more information first

**Reply with your choice or questions!**
