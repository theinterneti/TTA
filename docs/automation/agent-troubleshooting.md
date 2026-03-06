# Agent Troubleshooting Runbook

This runbook provides step-by-step procedures for troubleshooting and recovering from agent issues.

## Common Issues

### Issue 1: Agent Creates Breaking Changes

**Symptoms**: CI fails after agent PR is merged

**Detection**:
```bash
# Check recent agent PR merges
gh pr list --label automated --state merged --limit 5

# Check CI status
gh run list --workflow=tests.yml --limit 5
```

**Recovery**:
```bash
# 1. Identify breaking commit
git log --oneline -10

# 2. Revert immediately
git revert <commit-hash>
git push origin main

# 3. Disable agent
echo "enabled: false" >> .github/agents/<agent-name>.md
git add .github/agents/<agent-name>.md
git commit -m "chore: disable <agent-name> due to breaking change"
git push

# 4. Create incident report
gh issue create \
  --title "Incident: Agent <agent-name> caused breaking change" \
  --body "See commit <commit-hash> and reverted in <revert-commit>" \
  --label "incident,agent-failure"
```

---

### Issue 2: Agent Violates Boundaries

**Symptoms**: Agent attempts to write to unauthorized directories

**Detection**:
```bash
# Check audit trail for violations
grep "boundary_violation" docs/kb-exports/*-agent-activity.md

# Check recent PRs for unexpected file changes
gh pr view <pr-number> --json files | jq -r '.files[].path' | grep -v "^tests/\|^docs/"
```

**Recovery**:
```bash
# 1. Close the PR immediately
gh pr close <pr-number>

# 2. Disable agent
echo "enabled: false" >> .github/agents/<agent-name>.md
git add .github/agents/<agent-name>.md
git commit -m "security: disable <agent-name> due to boundary violation"
git push

# 3. Alert security team
gh issue create \
  --title "SECURITY: Agent boundary violation by <agent-name>" \
  --body "PR #<pr-number> attempted unauthorized file access" \
  --label "security,agent-violation,critical"

# 4. Review agent configuration
cat .github/agents/<agent-name>.md

# 5. Audit recent activity
cat docs/kb-exports/<agent-name>-activity.md
```

---

### Issue 3: Agent Spam (Too Many PRs)

**Symptoms**: >5 PRs from single agent in 24 hours

**Detection**:
```bash
# Count agent PRs in last 24 hours
gh pr list --label automated,<agent-name> --created ">$(date -d '24 hours ago' +%Y-%m-%d)" | wc -l
```

**Recovery**:
```bash
# 1. Pause agent execution temporarily
echo "enabled: false" >> .github/agents/<agent-name>.md
git add .github/agents/<agent-name>.md
git commit -m "chore: pause <agent-name> due to high PR volume"
git push

# 2. Review all agent PRs
gh pr list --label automated,<agent-name> --limit 20

# 3. Close duplicates or batch merge
for pr in $(gh pr list --label automated,<agent-name> --json number --jq '.[].number'); do
  gh pr view $pr
  # Decide: merge, close, or keep
done

# 4. Adjust rate limiting in workflow
# Edit .github/workflows/continuous-quality-hygiene.md
# Add check: "if [ $(gh pr list --label <agent-name> | wc -l) -ge 5 ]; then exit 0; fi"
```

---

### Issue 4: Workflow Execution Timeout

**Symptoms**: Workflow runs >30 minutes and times out

**Detection**:
```bash
# Check workflow duration
gh run list --workflow=trigger-quality-hygiene.yml --limit 5 --json conclusion,startedAt,completedAt
```

**Recovery**:
```bash
# 1. Cancel hung workflow
gh run cancel <run-id>

# 2. Review logs to identify bottleneck
gh run view <run-id> --log > timeout-investigation.log

# 3. Optimize slow step
# - Add timeout to long-running commands
# - Break large operations into smaller chunks
# - Skip expensive operations if not needed

# 4. Update workflow with timeout
# Edit workflow markdown to add:
# timeout 600 <command>  # 10 minute timeout
```

---

### Issue 5: MkDocs Build Fails

**Symptoms**: @docs-agent PR fails validation, MkDocs build errors

**Detection**:
```bash
# Check docs-agent PR for build errors
gh pr view <pr-number> | grep "MkDocs build"

# Build locally to reproduce
uv run mkdocs build --strict 2>&1 | tee mkdocs-errors.log
```

**Recovery**:
```bash
# 1. Identify error type
cat mkdocs-errors.log

# Common errors:
# - Broken links: Fix with scripts/validate_internal_links.py
# - Invalid navigation: Check mkdocs.yml syntax
# - Missing files: Verify all referenced files exist

# 2. Fix locally
# If broken link:
grep -r "\](" docs/ --include="*.md" | python scripts/validate_internal_links.py

# If navigation error:
cat mkdocs.yml  # Check YAML syntax

# 3. Update agent PR
gh pr checkout <pr-number>
# Make fixes
git add docs/ mkdocs.yml
git commit --amend --no-edit
git push --force

# 4. Rebuild to verify
uv run mkdocs build --strict
```

---

### Issue 6: Test Coverage Drops After Agent PR

**Symptoms**: @test-agent adds tests but coverage decreases

**Detection**:
```bash
# Check coverage before/after in PR description
gh pr view <pr-number> | grep "coverage"

# Run coverage locally
uv run pytest --cov=src --cov-report=term-missing tests/
```

**Recovery**:
```bash
# 1. Identify cause
# - Agent may have added tests for already-tested code
# - New tests may mock out previously-covered code paths

# 2. Review test quality
gh pr diff <pr-number> | grep "def test_"

# 3. Request revision or close PR
gh pr comment <pr-number> --body "@test-agent: Coverage decreased. Please review and adjust tests."
gh pr close <pr-number>

# 4. Create manual issue for proper fix
gh issue create \
  --title "Coverage drop in module X after test addition" \
  --body "Agent PR #<pr-number> caused coverage drop. Manual review needed." \
  --label "coverage,manual-review"
```

---

## Incident Response

### Agent Incident Response Procedure

1. **Detect** → Alert triggered (CI break, boundary violation, spam)
2. **Contain** → Disable agent, close problematic PRs
3. **Investigate** → Review audit trail, check logs, identify root cause
4. **Remediate** → Fix agent configuration, update boundaries
5. **Document** → Create incident report in `docs/kb-exports/`
6. **Re-enable** → Test agent locally before re-enabling in production

### Creating Incident Reports

```bash
# Create incident report
cat > docs/kb-exports/incident-$(date +%Y%m%d-%H%M%S).md << 'EOF'
# Agent Incident Report

**Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Agent**: <agent-name>
**Severity**: Critical | High | Medium | Low

## Summary
Brief description of incident

## Timeline
- **Detection**: When incident was detected
- **Containment**: When agent was disabled
- **Resolution**: When incident was resolved

## Root Cause
What caused the incident

## Impact
- PRs affected: #X, #Y
- Files affected: src/...
- Tests broken: X tests failed

## Remediation
Steps taken to fix

## Prevention
How to prevent recurrence
EOF

git add docs/kb-exports/incident-*.md
git commit -m "docs: incident report for <agent-name>"
git push
```

---

## Maintenance

### Weekly Health Check

```bash
# 1. Review agent activity
cat docs/kb-exports/test-agent-activity.md | grep "timestamp" | tail -7
cat docs/kb-exports/docs-agent-activity.md | grep "timestamp" | tail -7
cat docs/kb-exports/lint-agent-activity.md | grep "timestamp" | tail -7

# 2. Check agent PR success rate
TOTAL=$(gh pr list --label automated --state all --limit 100 | wc -l)
MERGED=$(gh pr list --label automated --state merged --limit 100 | wc -l)
echo "Agent PR success rate: $MERGED / $TOTAL"

# 3. Verify no boundary violations
grep "boundary_violation" docs/kb-exports/*-activity.md

# 4. Check for stale agent PRs (>7 days)
gh pr list --label automated --state open --json number,createdAt | \
  jq -r '.[] | select((now - (.createdAt | fromdateiso8601)) > 604800) | .number'
```

### Monthly Review

- Review agent performance metrics
- Analyze false positive rate
- Survey team satisfaction
- Adjust agent boundaries if needed
- Update agent configurations
- Archive old incident reports

---

## Emergency Procedures

### Disable All Agents

```bash
# Quick disable all agents
for agent in .github/agents/*.md; do
  if [ "$(basename $agent)" != "SCHEMA.md" ]; then
    echo "enabled: false" >> $agent
  fi
done

git add .github/agents/
git commit -m "emergency: disable all agents"
git push
```

### Revert All Agent Changes

```bash
# Find all agent commits in last 7 days
git log --since="7 days ago" --grep="@test-agent\|@docs-agent\|@lint-agent" --oneline

# Revert range
git revert <oldest-commit>^..<newest-commit>
git push
```

---

## Contact

**Agent Maintainer**: @theinterneti
**Incident Reports**: Create GitHub issue with `incident` label
**Questions**: See `docs/automation/custom-agents-guide.md`

---

**Last Updated**: 2026-03-06
**Status**: Active runbook
