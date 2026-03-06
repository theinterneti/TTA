# Automation Workflows

This directory contains TTA's GitHub Agentic Workflows for continuous quality and documentation automation.

## Overview

These workflows are written in **plain markdown** with YAML frontmatter and are compiled to GitHub Actions workflows using the `gh-aw` CLI.

## Available Workflows

### [Continuous Quality Hygiene](continuous-quality-hygiene.md)

**Purpose**: Proactively investigate and fix CI failures

**Triggers**:
- Daily at 2 AM UTC
- CI failure in tests.yml or code-quality.yml
- Manual via workflow_dispatch

**Agents**: @lint-agent, @test-agent

**Flow**: Detect failures → Triage → Fix or investigate → Draft PR

---

### [Continuous Documentation](continuous-documentation.md)

**Purpose**: Keep docs synchronized with code changes

**Triggers**:
- PR merged to main/staging
- New module added to src/
- Manual via workflow_dispatch

**Agents**: @docs-agent

**Flow**: Detect changes → Extract docstrings → Update docs → Draft PR

---

## Compiling Workflows

These markdown workflows must be compiled to YAML using `gh-aw` CLI:

```bash
# Install gh-aw (GitHub Agentic Workflows CLI)
# (Installation instructions from gh-aw documentation)

# Compile workflow to executable YAML
gh-aw compile continuous-quality-hygiene.md

# Output: continuous-quality-hygiene.lock.yml
```

The generated `.lock.yml` files are gitignored and compiled locally to save GitHub Actions minutes.

---

## Workflow Format

### YAML Frontmatter
```yaml
---
name: Workflow Name
description: Brief description
on:
  schedule:
    - cron: '0 2 * * *'
permissions: read-all  # Always read-only for safety
tools:
  - github-cli
  - pytest
agents:
  - test-agent
---
```

### Markdown Body

Natural language instructions:
- **Steps**: `## Step 1: Description`
- **Actions**: Bullet points with specific actions
- **Commands**: Bash code blocks with concrete examples
- **Expected Output**: Success criteria

---

## Safety Guidelines

### Permissions

All workflows use `permissions: read-all`:
- **No write access** to repository
- **No secret access** to credentials
- **No workflow modification** rights

Agents propose changes via draft PRs, never commit directly.

### Approval Process

1. Workflow detects issue
2. Agent investigates and proposes fix
3. Draft PR created with detailed description
4. Human reviews and approves
5. Human merges (or agent auto-merges if criteria met)

---

## Monitoring

```bash
# View workflow runs
gh run list --workflow=continuous-quality-hygiene.lock.yml --limit 10

# Check workflow status
gh run watch

# Download workflow logs
gh run view <run-id> --log > workflow.log
```

---

## Reference

- **Custom Agents**: `.github/agents/`
- **PR Templates**: `.github/templates/`
- **Documentation**: `docs/automation/`
- **Phase 3 Plan**: `phase3_automation_plan.md`

---

**Last Updated**: 2026-03-06
