---
name: Continuous Quality Hygiene
description: Proactively investigate CI failures and propose targeted fixes
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_run:
    workflows: ["Tests", "Code Quality"]
    types: [completed]
  workflow_dispatch:
    inputs:
      target_issue:
        description: 'GitHub issue number to investigate'
        required: false
permissions: read-all
tools:
  - github-cli
  - ruff
  - pytest
  - git
agents:
  - lint-agent
  - test-agent
---

# Continuous Quality Hygiene Workflow

This workflow proactively investigates CI failures and proposes targeted fixes via draft PRs. It coordinates @lint-agent and @test-agent to handle different failure types automatically.

## Objective

Reduce manual intervention for CI failures by automatically detecting, triaging, and fixing quality issues. Target: 80% of lint/format issues auto-fixed within 1 hour.

---

## Step 1: Detect Quality Issues

**Executor**: GitHub Actions runner + lint-agent

**Duration**: ~5 minutes

### Actions

1. Fetch the latest CI run results for the `main` branch
2. Parse failure logs from `tests.yml` and `code-quality.yml` workflows
3. Categorize failures into types:
   - **Lint Failures**: Ruff violations (E501, F401, I001, etc.)
   - **Type Failures**: Pyright type checking errors
   - **Test Failures**: Pytest failures with stack traces
   - **Coverage Drops**: Coverage below maturity threshold

4. Create structured failure manifest for routing

### Commands

```bash
# Get latest workflow run status
gh run list --workflow=tests.yml --branch=main --limit=1 --json conclusion,databaseId,status

# If latest run failed, download logs
RUN_ID=$(gh run list --workflow=tests.yml --branch=main --limit=1 --json databaseId --jq '.[0].databaseId')
gh run view $RUN_ID --log-failed > ci-failures.log

# Parse Ruff violations
uv run ruff check src/ tests/ --output-format=json > ruff-violations.json

# Get coverage report
uv run pytest --cov=src --cov-report=json tests/ 2>/dev/null || true
```

### Expected Output

Create `failure-manifest.json`:
```json
{
  "timestamp": "2026-03-06T02:00:00Z",
  "ci_run_id": 12345,
  "workflow": "tests.yml",
  "failures": [
    {
      "type": "lint",
      "file": "src/agent_orchestration/agents.py",
      "line": 145,
      "rule": "E501",
      "message": "Line too long (92 > 88 characters)",
      "auto_fixable": true
    },
    {
      "type": "test",
      "file": "tests/unit/test_circuit_breaker.py",
      "test": "test_circuit_breaker_recovery",
      "error": "AssertionError: expected CLOSED, got HALF_OPEN",
      "auto_fixable": false
    }
  ]
}
```

---

## Step 2: Triage and Route

**Executor**: GitHub Actions runner (decision logic)

**Duration**: ~2 minutes

### Actions

1. Route failures to appropriate agent based on type:
   - **Lint failures** (auto-fixable rules) → @lint-agent
   - **Type failures** → @lint-agent (analysis) + human review
   - **Test failures** → @test-agent (investigation)
   - **Coverage drops** (>5%) → @test-agent (add tests)

2. For non-auto-fixable issues, create GitHub issue with:
   - Failure details and stack trace
   - Labels: `ci-failure`, `auto-triage`, type-specific label
   - Link to CI run

### Decision Logic

```python
# Pseudo-code for routing
for failure in failures:
    if failure.type == "lint" and failure.rule in AUTO_FIXABLE_RULES:
        route_to_agent("lint-agent", failure)
    elif failure.type == "test" and is_flaky(failure):
        route_to_agent("test-agent", {"action": "investigate_flaky", "failure": failure})
    elif failure.type == "coverage" and coverage_delta < -5:
        route_to_agent("test-agent", {"action": "add_tests", "module": failure.module})
    else:
        create_github_issue(failure)
```

### Commands

```bash
# Create GitHub issue for manual review
gh issue create \
  --title "CI Failure: ${FAILURE_TYPE} in ${FILE}" \
  --body "$(cat failure-details.md)" \
  --label "ci-failure,auto-triage,${FAILURE_TYPE}"
```

---

## Step 3: Execute Remediation (Lint Failures)

**Executor**: @lint-agent

**Duration**: ~5 minutes

### Actions (for auto-fixable lint violations)

1. Create new branch: `chore/auto-fix-lint-{timestamp}`
2. Run `uv run ruff check src/ tests/ --fix`
3. Run `uv run ruff format src/ tests/`
4. Verify no test failures: `uv run pytest -q -m "not integration" tests/`
5. Verify diff shows only style changes (no logic modifications)
6. Commit with conventional commit message
7. Create draft PR linking to CI failure

### Commands

```bash
# Create branch
BRANCH="chore/auto-fix-lint-$(date +%s)"
git checkout -b $BRANCH

# Fix violations
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/

# Verify no breakage
uv run pytest -q -m "not integration and not neo4j and not redis" tests/

# Commit if tests pass
if [ $? -eq 0 ]; then
  git add src/ tests/
  git commit -m "style: auto-fix lint violations from CI run #${CI_RUN_ID}"
  git push origin $BRANCH

  # Create draft PR
  gh pr create \
    --draft \
    --title "style: auto-fix lint violations from CI run #${CI_RUN_ID}" \
    --body-file .github/templates/lint-agent-pr-template.md \
    --label "automated,ci-fix,lint-agent"
fi
```

### Expected Output

Draft PR created with:
- Detailed violation summary
- Before/after diff
- Test verification results
- Link to original CI failure

---

## Step 4: Execute Investigation (Test Failures)

**Executor**: @test-agent

**Duration**: ~10 minutes

### Actions (for test failures)

1. Analyze failing test stack trace and error message
2. Check if failure is flaky by rerunning test 3 times
3. If flaky: Add `@pytest.mark.flaky(reruns=3)` decorator
4. If consistent failure:
   - Check recent commits that touched tested code (`git log --oneline -10 -- src/path/to/module.py`)
   - Analyze test assumptions and mocked dependencies
   - Review circuit breaker state or timing issues
5. Create detailed investigation report
6. Create GitHub issue with evidence and proposed fix

### Commands

```bash
# Rerun test 3 times to check for flakiness
TEST_NAME="tests/unit/test_circuit_breaker.py::test_circuit_breaker_recovery"
FAILURES=0
for i in {1..3}; do
  uv run pytest $TEST_NAME -v || ((FAILURES++))
done

if [ $FAILURES -eq 3 ]; then
  echo "Consistent failure - needs investigation"
elif [ $FAILURES -gt 0 ]; then
  echo "Flaky test detected - add @pytest.mark.flaky"
fi

# Get recent changes to tested code
MODULE=$(grep -r "from src\." $TEST_NAME | head -1 | sed 's/.*from src\.\(.*\) import.*/src\/\1.py/')
git log --oneline -10 -- $MODULE

# Create investigation report
cat > investigation-report.md << 'EOF'
## Test Failure Investigation

**Test**: ${TEST_NAME}
**Failure Type**: ${FAILURE_TYPE}
**Flaky**: ${IS_FLAKY}

### Root Cause Analysis
${ANALYSIS}

### Proposed Fix
${PROPOSED_FIX}
EOF

# Create GitHub issue
gh issue create \
  --title "Test Failure: ${TEST_NAME}" \
  --body-file investigation-report.md \
  --label "test-failure,auto-triage,test-agent"
```

### Expected Output

GitHub issue created with:
- Root cause analysis
- Evidence from git history and code inspection
- Proposed fix options
- Request for human review

---

## Step 5: Create Draft PR

**Executor**: GitHub CLI (gh)

**Duration**: ~2 minutes

### Actions

1. Push branch to remote
2. Create draft PR with detailed description
3. Link to original CI failure run
4. Add appropriate labels (automated, ci-fix, agent-specific)
5. Request review from codeowners
6. Post summary comment with metrics

### Commands

```bash
# Push branch
git push origin $BRANCH

# Create draft PR
gh pr create \
  --draft \
  --title "${COMMIT_MESSAGE}" \
  --body "$(cat .github/templates/auto-fix-pr-body.md)" \
  --label "automated,ci-fix,${AGENT_NAME}" \
  --assignee "@me"

# Get PR number
PR_NUMBER=$(gh pr list --head $BRANCH --json number --jq '.[0].number')

# Link to CI failure
gh pr comment $PR_NUMBER --body "🔗 Original CI failure: https://github.com/theinterneti/TTA/actions/runs/${CI_RUN_ID}"

# Add metrics comment
gh pr comment $PR_NUMBER --body "📊 Metrics: ${VIOLATIONS_FIXED} violations fixed in ${FILES_CHANGED} files"
```

---

## Step 6: Continuous Monitoring

**Executor**: GitHub Actions (scheduled check every 6 hours)

**Duration**: Ongoing

### Actions

1. Monitor draft PR status (approved, changes requested, stale)
2. If approved: Merge and close
3. If changes requested: Notify agent for revision (create follow-up issue)
4. If stale (>7 days): Close and create issue for manual handling
5. Track metrics: time-to-merge, auto-fix success rate, regression rate

### Commands

```bash
# Check PR status
PR_STATUS=$(gh pr view $PR_NUMBER --json state,reviews --jq '.state')

if [ "$PR_STATUS" = "APPROVED" ]; then
  # Merge PR
  gh pr merge $PR_NUMBER --squash --auto

elif [ "$PR_STATUS" = "CHANGES_REQUESTED" ]; then
  # Create follow-up issue
  gh issue create \
    --title "Follow-up: PR #${PR_NUMBER} needs revision" \
    --body "Agent PR requires changes. Review comments and update." \
    --label "agent-follow-up"

else
  # Check if stale (>7 days old)
  CREATED_AT=$(gh pr view $PR_NUMBER --json createdAt --jq -r '.createdAt')
  AGE_DAYS=$(( ($(date +%s) - $(date -d "$CREATED_AT" +%s)) / 86400 ))

  if [ $AGE_DAYS -gt 7 ]; then
    gh pr close $PR_NUMBER
    gh issue create \
      --title "Stale agent PR closed: #${PR_NUMBER}" \
      --body "PR was open for >7 days without review. Manual handling required." \
      --label "stale-agent-pr"
  fi
fi
```

### Metrics Collection

Track and report to `docs/kb-exports/workflow-metrics.json`:
```json
{
  "workflow": "continuous-quality-hygiene",
  "execution_date": "2026-03-06",
  "failures_detected": 15,
  "auto_fixed": 12,
  "human_review_required": 3,
  "avg_time_to_pr_minutes": 8,
  "auto_merge_rate": 0.80,
  "prs_created": [123, 124, 125]
}
```

---

## Success Criteria

✅ Draft PR created within 1 hour of CI failure
✅ 80% of lint failures auto-fixed without human intervention
✅ Test failures investigated with root cause analysis
✅ Coverage maintained at 70-85% thresholds
✅ Zero breaking changes introduced by agents

---

## Failure Handling

- **Agent Fails**: Create GitHub issue with failure logs, do not retry
- **Tests Fail After Fix**: Revert changes immediately, escalate to human
- **Multiple PRs Conflict**: Merge sequentially by priority (lint → test → docs)
- **Boundary Violation**: Halt execution, alert security team via issue

---

## Safety Mechanisms

1. **Dry-Run Support**: Agents support `--dry-run` to preview changes
2. **Audit Trails**: Every action logged with timestamp and reasoning
3. **Automated Revert**: If CI breaks after merge, auto-revert and disable agent
4. **Rate Limiting**: Max 5 PRs per day per agent to prevent spam
5. **Human Approval Gates**: Production changes always require explicit review

---

**Last Updated**: 2026-03-06
**Status**: Active agentic workflow
