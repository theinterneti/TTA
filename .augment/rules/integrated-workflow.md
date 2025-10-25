# Integrated Development Workflow Rule

**For AI Agent Use Only** - Guidelines for TTA development workflow.

## Quick Start

### Environment Setup
```bash
./uv-manager.sh full      # Complete setup
./uv-manager.sh verify    # Verify environment
uv run pytest             # Run tests
```

### Git Workflow
```bash
./git-workflow.sh         # Interactive menu
./git-workflow.sh commit  # Smart commit
./git-workflow.sh pr      # Create PR
gh pr status              # Check status
```

### Workflow Validation
```bash
./github-workflow-validator.sh all  # All checks
make github-check                   # Via Makefile
gh run list                         # Recent runs
```

## Development Flow

1. **Setup**: Run `./uv-manager.sh full` once
2. **Code**: Edit files, write tests
3. **Commit**: Use `./git-workflow.sh commit` for guided commits
4. **Sync**: Run `./git-workflow.sh sync` to update from remote
5. **PR**: Run `./git-workflow.sh pr` to create pull request
6. **Verify**: Check `gh run watch` for CI status

## Workflow Tools

### Git & GitHub (Root Directory)
- **git-workflow.sh**: Interactive git operations
  - Smart branching with conventions
  - Guided commits (conventional format)
  - PR creation with templates
  - Sync, merge, cleanup
  
- **github-workflow-validator.sh**: Workflow validation
  - YAML syntax checking
  - UV setup validation
  - Recent run monitoring
  
- **uv-manager.sh**: Environment management
  - Setup/verify UV environments
  - VS Code interpreter config
  - Dependency management

### UV Package Manager
```bash
uv sync --all-extras --dev  # Full environment
uv run pytest               # Run with dependencies
uv run ruff check .         # Linting
uv add package-name         # Add dependency
```

### Makefile Targets
```bash
make test           # Unit tests
make github-check   # Validate workflows
make uv-setup       # Setup environment
make uv-verify      # Verify environment
```

## Branch Strategy

**Structure:** main ← staging ← development ← feature/*

**Naming:**
- feature/* - New features
- fix/* - Bug fixes  
- docs/* - Documentation
- test/* - Testing improvements

**Workflow:**
1. Branch from development: `git checkout -b feature/name`
2. Commit with convention: `feat(scope): description`
3. Push: `git push TTA feature/name`
4. PR: `gh pr create --base development`

## Quality Gates

### Pre-Commit
- Test coverage: ≥70%
- All tests passing
- Linting clean (ruff)
- No security issues (detect-secrets)

### Pre-Merge (Development)
- All tests pass
- Code review approved
- CI workflows pass

### Pre-Deploy (Staging/Production)
- Integration tests pass
- Performance acceptable
- Security review complete
- Monitoring configured

## Commit Management

### Use git-workflow.sh
```bash
./git-workflow.sh commit  # Guided conventional commits
```

**Commit format:** `type(scope): description`

**Types:** feat, fix, docs, test, refactor, chore, ci

**Example:** `feat(auth): add JWT token refresh`

### Bypassing Pre-commit Hooks
When needed (existing issues, not new code):
```bash
git commit --no-verify -m "message"
```

## Documentation

**Integration guides in root:**
- GITHUB_INTEGRATION_GUIDE.md - Complete setup
- GITHUB_QUICK_REF.md - Daily commands
- BRANCHING_STRATEGY.md - Git workflow

**Development docs:**
- docs/development/ - Component guides
- .augment/rules/ - AI agent rules

## Best Practices

1. **Environment**: Always use `uv run` for commands
2. **Commits**: Small, focused, conventional format
3. **Testing**: Write tests first, aim for 70%+ coverage
4. **PRs**: Keep under 500 lines, clear descriptions
5. **Branches**: Use naming conventions, delete after merge

## Troubleshooting

### Environment Issues
```bash
./uv-manager.sh verify    # Check setup
./uv-manager.sh clean     # Clean and rebuild
```

### Git Issues
```bash
./git-workflow.sh status  # Current state
git status                # Detailed view
```

### Workflow Issues
```bash
./github-workflow-validator.sh all  # Validate
gh run list --limit 5               # Recent runs
```

## Integration with Other Rules

**Related:**
- `use-github.md` - GitHub operations
- `ai-context-management.md` - Session tracking
- `avoid-long-files.md` - Code quality

---

**Status:** Active
**Last Updated:** 2025-10-25  
**Tools:** git-workflow.sh, github-workflow-validator.sh, uv-manager.sh

