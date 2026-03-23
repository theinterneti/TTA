# PR Automation - Quick Reference

## 🚀 Quick Commands

### List & View PRs
```bash
# List all open PRs
./scripts/pr-manager.sh list

# Show PR details
./scripts/pr-manager.sh details 73
```

### Review PRs
```bash
# Approve
./scripts/pr-manager.sh approve 73 "LGTM!"

# Request changes
./scripts/pr-manager.sh changes 73 "Please fix X"

# Check Copilot review
./scripts/pr-manager.sh copilot 73

# Auto-resolve Copilot comments on modified files
./scripts/pr-manager.sh resolve 73
```

### Merge PRs
```bash
# Enable auto-merge
./scripts/pr-manager.sh automerge 73

# Merge immediately
./scripts/pr-manager.sh merge 73 squash
```

### Monitor
```bash
# Watch PR status (real-time)
./scripts/pr-manager.sh watch 73 30

# Check workflows
./scripts/pr-manager.sh workflow 73
```

## 📋 Auto-Merge Criteria

- ✅ At least 1 approval
- ✅ No change requests
- ✅ All Copilot comments resolved
- ✅ All CI checks passing

## 🎯 PR Lifecycle

1. **Create PR** → Auto-assign reviewers
2. **Copilot Review** → Address comments
3. **Quality Checks** → Fix any failures
4. **Human Review** → Get approval
5. **Auto-Merge** → Automatic when ready

## 🔧 Addressing PR #73

Your current PR needs:

1. **Fix Copilot comments**:
   - `test_router_primitive.py:16` - `__class__.__name__` issue
   - `test_cache_primitive.py:19` - Same `__class__.__name__` issue
   - `openhands_stage.py` - `asyncio.run()` pattern
   - `main.py:75` - Incomplete install command

2. **Push fixes**:
   ```bash
   git add .
   git commit -m "fix: address Copilot review feedback"
   git push
   ```

3. **Wait for CI** → Then auto-merge enabled!

## 📞 Get Help

```bash
./scripts/pr-manager.sh help
```

See: `docs/development/PR_AUTOMATION_GUIDE.md` for full documentation


---