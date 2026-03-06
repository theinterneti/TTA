# Custom Agents Directory

This directory contains TTA's custom AI agent definitions for autonomous quality maintenance and documentation synchronization.

## Available Agents

| Agent | Purpose | Boundaries | Security Level |
|-------|---------|-----------|----------------|
| [@test-agent](test-agent.md) | Pytest specialist for test generation and coverage | `tests/` only, never remove failing tests | Medium |
| [@docs-agent](docs-agent.md) | MkDocs specialist for documentation sync | `docs/` only, never modify src/ | Low |
| [@lint-agent](lint-agent.md) | Ruff & Pyright specialist for style enforcement | Style only, never change logic | Medium |

## Quick Start

### Reviewing Agent PRs

```bash
# List recent agent PRs
gh pr list --label automated --limit 10

# Review specific agent PR
gh pr view <pr-number>

# Test agent changes locally
gh pr checkout <pr-number>
uv run pytest  # For test-agent
uv run mkdocs build --strict  # For docs-agent
```

### Triggering Agents Manually

```bash
# Trigger quality hygiene workflow (lint + test agents)
gh workflow run trigger-quality-hygiene.yml

# Trigger documentation sync
gh workflow run trigger-continuous-docs.yml -f module_path=src/module.py
```

### Disabling Agents

```bash
# Disable specific agent
echo "enabled: false" >> .github/agents/test-agent.md
git commit -am "chore: disable test-agent"
git push
```

## Agent Architecture

### Execution Flow
```
Trigger (CI/Schedule/Manual) → Workflow Markdown → Agent Execution →
Validation → Draft PR → Human Review → Merge
```

### Safety Mechanisms

1. **Boundary Enforcement**: File-level write permissions
2. **Audit Trails**: All actions logged to `docs/kb-exports/`
3. **Draft PRs Only**: Agents never auto-merge to main
4. **Test Validation**: All changes validated before PR creation
5. **Human Approval**: Production changes require review

### Configuration

Each agent configuration includes:
- YAML frontmatter (metadata, security, boundaries)
- Executable commands (concrete bash examples)
- Code examples from TTA codebase
- Three-tier boundaries (always/ask/never)
- Operational procedures (triggers, workflows, audit)

## Documentation

- **Custom Agents Guide**: `docs/automation/custom-agents-guide.md`
- **Agentic Workflows Guide**: `docs/automation/agentic-workflows-guide.md`
- **Troubleshooting Runbook**: `docs/automation/agent-troubleshooting.md`
- **Agent Schema**: `SCHEMA.md`

## Validation

Validate agent configurations before committing:

```bash
# Validate all agents
python scripts/validate_agent_boundaries.py --all

# Validate specific agent
python scripts/validate_agent_boundaries.py test-agent
```

## Audit Trails

View agent activity:
```bash
cat docs/kb-exports/test-agent-activity.md
cat docs/kb-exports/docs-agent-activity.md
cat docs/kb-exports/lint-agent-activity.md
```

## Adding New Agents

1. Copy `SCHEMA.md` template
2. Define agent metadata in YAML frontmatter
3. Add executable commands section
4. Provide code examples from TTA
5. Define boundaries (allowed/read-only/denied)
6. Specify always/ask/never actions
7. Define operational procedures
8. Validate with `scripts/validate_agent_boundaries.py`
9. Create PR for review

---

**For detailed guidance**, see:
- [Custom Agents Guide](../../docs/automation/custom-agents-guide.md)
- [Agent Schema Definition](SCHEMA.md)

**Last Updated**: 2026-03-06
