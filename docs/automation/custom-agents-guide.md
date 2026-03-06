# Custom Agents Guide

This guide explains TTA's custom agent ecosystem for autonomous quality maintenance and documentation synchronization.

## Overview

TTA uses specialized AI agents to prevent technical debt through continuous automation. Each agent has strict boundaries, audit trails, and human approval gates.

## Available Agents

### @test-agent (Pytest Specialist)

**Purpose**: Autonomous test generation and coverage improvement

**Boundaries**:
- ✅ Write to `tests/` only
- ❌ Never remove failing tests
- ❌ Never modify `src/` application code

**Triggers**:
- Coverage drops below threshold (70/80/85% by maturity)
- Test failures in CI
- Manual invocation

**Usage**:
```bash
# Manually trigger test agent (when implemented)
gh workflow run trigger-quality-hygiene.yml -f target_issue=123
```

[View full agent definition](.github/agents/test-agent.md)

---

### @docs-agent (MkDocs Specialist)

**Purpose**: Autonomous documentation generation and synchronization

**Boundaries**:
- ✅ Write to `docs/` and `mkdocs.yml` only
- ❌ Never modify `src/` application code
- ❌ Never delete docs without archiving

**Triggers**:
- PR merged with docstring changes
- New module added to `src/`
- Documentation drift detected (>7 days)

**Usage**:
```bash
# Manually trigger docs agent
gh workflow run trigger-continuous-docs.yml -f module_path=src/agent_orchestration/circuit_breaker.py
```

[View full agent definition](.github/agents/docs-agent.md)

---

### @lint-agent (Ruff & Pyright Specialist)

**Purpose**: Autonomous code style enforcement

**Boundaries**:
- ✅ Fix style violations only
- ❌ Never change business logic
- ❌ Never modify test assertions

**Triggers**:
- CI lint failures
- PR opened (style check)
- Scheduled daily scan

**Usage**:
```bash
# Manually trigger lint agent
gh workflow run trigger-quality-hygiene.yml
```

[View full agent definition](.github/agents/lint-agent.md)

---

## Agent Architecture

### Execution Model

```
Trigger → Detect → Agent Execution → Validation → Draft PR → Review → Merge
```

### Safety Mechanisms

1. **Dry-Run Mode**: Preview changes without committing
2. **Audit Trails**: All actions logged to `docs/kb-exports/`
3. **Boundary Enforcement**: File-level permissions prevent unauthorized writes
4. **Automated Revert**: If CI breaks after merge, auto-revert
5. **Rate Limiting**: Max 5 PRs/day per agent
6. **Human Approval**: Production changes always require review

### Communication

Agents communicate via:
- **Draft PRs**: Primary output mechanism
- **GitHub Issues**: For investigation reports
- **Audit Logs**: For compliance tracking
- **PR Comments**: For metrics and links

---

## Working with Agents

### Reviewing Agent PRs

When an agent creates a draft PR:

1. **Check the agent label** (e.g., `lint-agent`, `test-agent`, `docs-agent`)
2. **Review the description** for trigger, changes, and verification
3. **Verify boundaries** not violated (check file paths in diff)
4. **Test locally** if needed:
   ```bash
   gh pr checkout <pr-number>
   uv run pytest  # For test-agent PRs
   uv run mkdocs build --strict  # For docs-agent PRs
   ```
5. **Approve or request changes**

### Triggering Agents Manually

```bash
# Trigger quality hygiene (lint + test agents)
gh workflow run trigger-quality-hygiene.yml

# Trigger documentation sync
gh workflow run trigger-continuous-docs.yml

# With parameters
gh workflow run trigger-quality-hygiene.yml -f target_issue=456
gh workflow run trigger-continuous-docs.yml -f module_path=src/new_module.py
```

### Disabling Agents

To temporarily disable an agent:

1. Edit agent configuration file (e.g., `.github/agents/test-agent.md`)
2. Add frontmatter field: `enabled: false`
3. Commit and push
4. Agent will skip execution until re-enabled

### Monitoring Agent Health

```bash
# View recent agent PRs
gh pr list --label automated --limit 10

# Check audit trails
cat docs/kb-exports/test-agent-activity.md
cat docs/kb-exports/docs-agent-activity.md
cat docs/kb-exports/lint-agent-activity.md

# View agent metrics (once Grafana dashboard implemented)
# Visit: http://localhost:3000/d/agent-metrics
```

---

## Troubleshooting

### Agent Creates Bad PR

1. Close the PR: `gh pr close <pr-number>`
2. Create issue documenting the problem
3. Review agent boundaries and configuration
4. Consider disabling agent until fixed

### Agent Violates Boundaries

1. Check security alert in GitHub issues
2. Review audit trail in `docs/kb-exports/`
3. Disable agent immediately
4. Investigate root cause
5. Update boundary validation logic

### Agent Spam (Too Many PRs)

1. Check rate limiting configuration
2. Review PR quality (false positives?)
3. Adjust agent trigger frequency
4. Consider batching multiple fixes into single PR

---

## Best Practices

### For Developers

1. **Trust but Verify**: Agents are reliable, but always review PRs
2. **Provide Feedback**: Comment on agent PRs to improve future behavior
3. **Report Issues**: Create GitHub issues for agent problems
4. **Monitor Metrics**: Check audit trails periodically

### For Agent Maintainers

1. **Test Locally First**: Validate agent changes before deploying
2. **Gradual Rollout**: Enable one agent at a time
3. **Monitor Metrics**: Track auto-fix rate, false positives
4. **Update Documentation**: Keep this guide current with agent changes

---

## Reference

- **Agent Definitions**: `.github/agents/*.md`
- **Workflow Definitions**: `.github/workflows/*.md`
- **PR Templates**: `.github/templates/*-pr-template.md`
- **Audit Trails**: `docs/kb-exports/*-agent-activity.md`
- **Agent Schema**: `.github/agents/SCHEMA.md`

---

**Last Updated**: 2026-03-06
**Status**: Active guide
