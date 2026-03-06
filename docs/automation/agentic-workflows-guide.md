# Agentic Workflows Guide

This guide explains TTA's GitHub Agentic Workflows for continuous quality and documentation automation.

## Overview

TTA uses plain markdown workflows executed by AI agents to maintain code quality and documentation. Unlike traditional GitHub Actions (YAML), these workflows are human-readable and support natural language instructions.

## Available Workflows

### Continuous Quality Hygiene

**Purpose**: Proactively investigate and fix CI failures

**File**: `.github/workflows/continuous-quality-hygiene.md`

**Triggers**:
- Scheduled: Daily at 2 AM UTC
- CI failure in tests.yml or code-quality.yml
- Manual: `workflow_dispatch`

**Agents Used**: @lint-agent, @test-agent

**Flow**:
```
Detect CI Failures → Triage by Type → Route to Agent →
Fix or Investigate → Create Draft PR → Monitor
```

[View full workflow](.github/workflows/continuous-quality-hygiene.md)

---

### Continuous Documentation

**Purpose**: Keep docs synchronized with code changes

**File**: `.github/workflows/continuous-documentation.md`

**Triggers**:
- PR merged to main/staging
- New module added to src/
- Manual: `workflow_dispatch`

**Agents Used**: @docs-agent

**Flow**:
```
Detect Code Changes → Extract Docstrings → Generate Docs →
Validate Build → Create Draft PR
```

[View full workflow](.github/workflows/continuous-documentation.md)

---

## Workflow Architecture

### Execution Model

Agentic workflows are **markdown files** with YAML frontmatter:

```yaml
---
name: Workflow Name
description: Brief description
on:
  schedule:
    - cron: '0 2 * * *'
permissions: read-all
tools:
  - github-cli
  - pytest
agents:
  - test-agent
---

# Workflow steps in natural language markdown...
```

### YAML Frontmatter

**Required Fields**:
- `name`: Workflow name
- `description`: Brief purpose
- `on`: Trigger conditions (GitHub Actions syntax)
- `permissions`: Always `read-all` for safety
- `tools`: List of CLI tools needed
- `agents`: List of custom agents to coordinate

### Markdown Body

Natural language instructions with:
- **Steps**: Numbered sections (## Step 1: ...)
- **Actions**: Bullet points describing what to do
- **Commands**: Bash code blocks showing exact commands
- **Expected Output**: What success looks like

---

## Execution Flow

### 1. Trigger Detection

GitHub Actions YAML triggers execute workflow:
```yaml
# .github/workflows/trigger-quality-hygiene.yml
on:
  workflow_run:
    workflows: ["Tests"]
    types: [completed]

jobs:
  execute:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Executor reads markdown workflow and executes steps
          python .github/scripts/execute-workflow.py continuous-quality-hygiene.md
```

### 2. Workflow Parsing

Executor parses markdown into executable steps:
- Extract step headers (## Step N:)
- Parse actions and commands
- Identify agent assignments
- Build execution graph

### 3. Step Execution

For each step:
- Execute commands in bash
- Capture output
- Validate success criteria
- Record audit trail

### 4. Agent Coordination

When step requires agent:
- Load agent configuration
- Verify boundaries
- Execute agent commands
- Validate outputs
- Update audit trail

### 5. PR Creation

If changes made:
- Create branch
- Commit changes
- Create draft PR with template
- Add labels and request review

---

## Monitoring Workflows

### View Workflow Runs

```bash
# List recent workflow runs
gh run list --workflow=trigger-quality-hygiene.yml --limit 10

# View specific run
gh run view <run-id>

# Download logs
gh run view <run-id> --log > workflow-execution.log
```

### Check Agent Activity

```bash
# View audit trails
cat docs/kb-exports/test-agent-activity.md
cat docs/kb-exports/docs-agent-activity.md
cat docs/kb-exports/lint-agent-activity.md

# Check recent agent PRs
gh pr list --label automated --limit 10
```

### Monitor Metrics

Workflow metrics tracked:
- Failures detected vs auto-fixed
- Time to PR creation
- Auto-merge rate
- PR review time
- Regression rate

---

## Troubleshooting

### Workflow Fails to Execute

```bash
# Check workflow file syntax
cat .github/workflows/continuous-quality-hygiene.md

# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('.github/workflows/continuous-quality-hygiene.md').read().split('---')[1])"

# Check logs
gh run view <run-id> --log-failed
```

### Agent Doesn't Trigger

Possible causes:
1. **Trigger condition not met**: Check workflow `on:` conditions
2. **Agent disabled**: Check `enabled` field in agent config
3. **Rate limit reached**: Max 5 PRs/day per agent
4. **Boundary validation failed**: Check audit trail

### PR Not Created

Check:
1. **Branch creation**: Agent may not have push permissions
2. **GitHub CLI auth**: `gh auth status`
3. **PR template**: Template file exists and is valid
4. **Duplicate check**: PR may already exist for same fix

---

## Customizing Workflows

### Adding a New Step

Edit workflow markdown file:

```markdown
## Step 7: New Custom Step

**Executor**: @custom-agent or github-actions

**Duration**: ~X minutes

### Actions

1. Action description
2. Another action

### Commands

\```bash
# Command to execute
uv run tool --flag
\```

### Expected Output

Description of success criteria
```

### Adding a New Workflow

1. Create `.github/workflows/new-workflow.md` with frontmatter
2. Define steps in natural language
3. Create corresponding YAML trigger in `.github/workflows/trigger-new-workflow.yml`
4. Test with `workflow_dispatch` trigger
5. Enable scheduled or event-based triggers

---

## Best Practices

### Workflow Design

1. **Keep Steps Focused**: Each step should have single responsibility
2. **Provide Commands**: Always include concrete bash commands
3. **Define Success Criteria**: Clear output expectations
4. **Handle Failures**: Specify what to do when step fails
5. **Audit Everything**: Log all actions for compliance

### Safety Guidelines

1. **Read-Only Permissions**: Workflows have `permissions: read-all`
2. **Agent Proposals**: Agents create draft PRs, never auto-merge critical changes
3. **Human Approval**: Production changes always require review
4. **Boundary Enforcement**: Agents cannot access secrets or modify infrastructure
5. **Rollback Ready**: All changes revertible with `git revert`

---

## Reference

- **Workflow Definitions**: `.github/workflows/*.md`
- **Agent Definitions**: `.github/agents/*.md`
- **Execution Engine**: `.github/scripts/execute-workflow.py` (to be implemented)
- **Audit Trails**: `docs/kb-exports/*-activity.md`

---

**Last Updated**: 2026-03-06
**Status**: Active guide
