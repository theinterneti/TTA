# Agent Quick Reference

## Reviewing Agent PRs

```bash
# List recent agent PRs
gh pr list --label automated --limit 10

# Review PR
gh pr view <pr-number>

# Checkout and test locally
gh pr checkout <pr-number>
uv run pytest                     # test-agent
uv run mkdocs build --strict      # docs-agent
uv run ruff check src/ tests/     # lint-agent

# Approve or request changes
gh pr review <pr-number> --approve
gh pr review <pr-number> --request-changes --body "Comments..."
```

## Triggering Workflows

```bash
# Trigger quality hygiene
gh workflow run trigger-quality-hygiene.yml

# Trigger documentation sync
gh workflow run trigger-continuous-docs.yml

# With parameters
gh workflow run trigger-quality-hygiene.yml -f target_issue=123
```

## Agent Status

```bash
# Check if agents enabled
grep "enabled:" .github/agents/*.md

# View audit trails
cat docs/kb-exports/test-agent-activity.md
cat docs/kb-exports/docs-agent-activity.md
cat docs/kb-exports/lint-agent-activity.md
```

## Emergency Procedures

```bash
# Disable all agents
for agent in .github/agents/*.md; do
  [ "$(basename $agent)" != "SCHEMA.md" ] && echo "enabled: false" >> $agent
done
git commit -am "emergency: disable all agents" && git push

# Revert agent change
git revert <commit-hash> && git push
```

## Agent Boundaries

| Agent | Writes To | Never Touches | Security |
|-------|-----------|---------------|----------|
| @test-agent | tests/ | src/, failing tests | Medium |
| @docs-agent | docs/, mkdocs.yml | src/, pyproject.toml | Low |
| @lint-agent | src/, tests/ (style) | business logic, assertions | Medium |

## Validation Commands

```bash
# Validate agent configs
python scripts/validate_agent_boundaries.py --all

# Test extraction scripts
python scripts/extract_docstrings.py src/agent_orchestration/
python scripts/validate_code_blocks.py docs/
python scripts/find_undocumented_apis.py src/
```

---

**Full Guides**: See `docs/automation/`
