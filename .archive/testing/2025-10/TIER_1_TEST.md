# Tier 1 Workflow Test

**Branch**: feat/test-tier-1-workflows
**Target**: development
**Expected Tier**: 1 (Experimental)

## Expected Behavior

### Quality Checks
- ✅ Format check runs (failures allowed)
- ⏭️ Lint skipped
- ⏭️ Type check skipped
- ⏭️ Security scan skipped

### Testing
- ✅ Unit tests run (failures allowed)
- ⏭️ Integration tests skipped
- ⏭️ Monitoring validation skipped

### Coverage
- 📊 Coverage measured (no threshold)
- 📊 Report generated (informational only)

### Mutation Testing
- ⏭️ Skipped (tier 1-2 don't require mutation testing)

## Validation Checklist

- [ ] Workflow detects tier = 1
- [ ] GitHub Step Summary shows "Tier 1 - Experimental"
- [ ] Format check runs
- [ ] Lint job skipped
- [ ] Unit tests run (continue-on-error)
- [ ] Integration tests skipped
- [ ] Coverage report generated
- [ ] No coverage threshold enforced
- [ ] Mutation testing skipped
- [ ] PR can merge despite test failures

## Test Date

2025-10-29
