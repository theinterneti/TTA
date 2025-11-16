# TTA Development Workflow

## Solo Developer WSL2 Optimization

### Environment Preferences

- **Platform**: WSL2 (Windows Subsystem for Linux 2)
- **Filesystem**: Strict isolation to WSL filesystem (`/dev/sdf`), **never** Windows drives
- **Philosophy**: Reduce complexity, optimize for daily development efficiency
- **Focus**: Solo developer workflow over enterprise-scale features

### WSL2-Specific Optimizations

**Filesystem Performance**:
```bash
# All TTA operations on WSL filesystem
cd /home/thein/recovered-tta-storytelling

# Avoid Windows mounts (/mnt/c/, /mnt/d/)
# Reason: Significant performance penalty for file I/O
```

**Docker Volume Mounts**:
```yaml
# docker-compose.yml - Correct pattern
volumes:
  - ./src:/app/src  # Relative paths stay in WSL
  - /home/thein/data:/data  # Absolute WSL paths

# ❌ Avoid Windows paths
# - /mnt/c/Users/thein/data:/data
```

**Tool Execution**:
```bash
# Prefer uvx for standalone tools (no installation)
uvx ruff check src/
uvx pyright src/
uvx pytest tests/

# Use uv run only for project-specific scripts
uv run python scripts/migrate_db.py
```

## Multi-Commit Approach

### Philosophy

**Structured commits with logical grouping** rather than monolithic changes.

### Commit Categories

1. **Docker Infrastructure**
   - Dockerfile changes
   - docker-compose.yml updates
   - Container configuration

2. **Deployment Automation**
   - CI/CD workflow changes
   - Deployment scripts
   - Environment configuration

3. **Monitoring**
   - Logging setup
   - Metrics collection
   - Alerting configuration

4. **CI/CD**
   - GitHub Actions workflows
   - Test automation
   - Build pipelines

5. **Documentation**
   - README updates
   - API documentation
   - Architecture diagrams

### Commit Message Format

**Conventional Commits** (enforced by pre-commit hook):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

**Examples**:
```bash
feat(agent-orchestration): add circuit breaker for fault tolerance

Implements circuit breaker pattern to handle agent failures gracefully.
- Configurable failure thresholds
- Automatic recovery after cooldown
- Metrics tracking for monitoring

Closes #123

---

fix(player-experience): resolve session state race condition

Race condition in Redis session updates caused state inconsistency.
Fixed by using Redis transactions (MULTI/EXEC).

Fixes #456

---

docs(testing): add E2E testing guide with Playwright examples

Comprehensive guide for writing and running E2E tests.
Includes setup instructions, common patterns, and troubleshooting.
```

### Commit Workflow

```bash
# 1. Make changes
# 2. Stage files
git add src/agent_orchestration/circuit_breaker.py

# 3. Pre-commit hooks run automatically
#    - Ruff linting
#    - Secret detection
#    - Conventional commit validation
#    - pytest-asyncio fixture validation

# 4. Commit with conventional message
git commit -m "feat(agent-orchestration): add circuit breaker"

# 5. Repeat for each logical grouping
# 6. Push when ready (requires confirmation)
git push origin main
```

### Confirmation Requirements

**User confirmation required before**:
- Committing code
- Pushing to remote
- Merging branches
- Installing dependencies
- Deploying code

**Rationale**: Maintain control over potentially impactful operations.

## Pre-Commit Hooks

### Configuration

**File**: `.pre-commit-config.yaml`

### Enabled Hooks

1. **Ruff Linting**
   ```yaml
   - id: ruff
     args: [--fix]
   - id: ruff-format
   ```
   - Auto-fixes common issues
   - Enforces code style
   - Fast execution (Rust-based)

2. **Secret Detection**
   ```yaml
   - id: detect-secrets
   - id: gitleaks
   ```
   - Prevents committing API keys, passwords, tokens
   - Scans commit diffs and file contents
   - Baseline file: `.secrets.baseline`

3. **Conventional Commit Validation**
   ```yaml
   - id: conventional-commits
   ```
   - Enforces commit message format
   - Validates type, scope, subject
   - Ensures consistent git history

4. **pytest-asyncio Fixture Validation**
   ```yaml
   - id: validate-async-fixtures
   ```
   - Ensures async fixtures use `@pytest_asyncio.fixture`
   - Prevents common async test errors
   - Custom hook specific to TTA

5. **File Size Limits**
   ```yaml
   - id: check-added-large-files
     args: [--maxkb=500]
   ```
   - Prevents accidentally committing large files
   - Keeps repository lean

### Bypass Capability

**Easy bypass for urgent commits**:
```bash
git commit --no-verify -m "hotfix: critical production issue"
```

**Philosophy**: Hooks should help, not hinder. Bypass available but discouraged.

### Execution Optimization

- **Fast execution**: Optimized for solo developer WSL2 workflow
- **Parallel execution**: Multiple hooks run concurrently where possible
- **Incremental**: Only checks changed files, not entire codebase
- **Caching**: Results cached to avoid redundant checks

## Component Maturity Promotion Workflow

### Tracking Mechanism

**GitHub Projects**: Board with columns for each stage

```
┌─────────────┬─────────────┬─────────────┐
│ Development │   Staging   │ Production  │
├─────────────┼─────────────┼─────────────┤
│ Component A │ Component B │ Component C │
│ Component D │             │             │
└─────────────┴─────────────┴─────────────┘
```

**GitHub Issues**: Track promotion blockers

```markdown
## Promotion Blocker: player-experience → staging

**Component**: player-experience
**Target**: staging
**Blockers**:
- [ ] Test coverage below 70% (currently 65%)
- [ ] Integration tests failing for session management
- [ ] Security scan found 2 medium-severity issues

**Action Items**:
1. Add tests for character creation flow (#789)
2. Fix Redis connection timeout in tests (#790)
3. Update dependency with security patch (#791)
```

**TODO Comments**: Reference issues in code

```python
# TODO(#789): Add integration test for character creation
# Blocker for staging promotion - need 70% coverage

async def create_character(player_id: str, character_data: dict):
    """Create new character for player."""
    # Implementation...
```

**Component Labels**:
- `component:player-experience`
- `component:agent-orchestration`
- `component:narrative-engine`
- `target:staging`
- `target:production`
- `blocker:tests`
- `blocker:security`
- `blocker:performance`

### Promotion Criteria

See `component_maturity_criteria` memory for detailed criteria.

### Workflow Example

```bash
# 1. Develop feature in component
git checkout -b feature/player-preferences

# 2. Implement with tests
# 3. Commit changes (multi-commit approach)
git commit -m "feat(player-experience): add preference system"
git commit -m "test(player-experience): add preference integration tests"

# 4. Check maturity criteria
./scripts/check_component_maturity.sh player-experience

# 5. If criteria met, create promotion issue
gh issue create --title "Promote player-experience to staging" \
  --label "component:player-experience,target:staging"

# 6. Move card in GitHub Projects
# 7. Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# 8. Run staging validation
uvx pytest tests/integration/ -m player_experience
uvx playwright test tests/e2e-staging/

# 9. If validation passes, merge and close issue
git checkout main
git merge feature/player-preferences
gh issue close <issue-number>
```

## GitHub Projects Workflow

### Board Structure

**Columns**:
1. **Backlog**: Planned components/features
2. **Development**: Active development
3. **Staging**: Integration testing, pre-production validation
4. **Production**: Live, production-ready components
5. **Blocked**: Components with promotion blockers

### Card Movement

**Development → Staging**:
- All unit tests passing
- Code coverage ≥70%
- Linting and type checking clean
- Security scan passed
- Integration tests written

**Staging → Production**:
- All integration tests passing
- E2E tests passing
- Performance benchmarks met
- Security audit completed
- Manual QA approval

**Any → Blocked**:
- Promotion criteria not met
- Critical bugs discovered
- Security vulnerabilities found
- Performance regressions detected

### Automation

**GitHub Actions** automatically:
- Updates card status based on test results
- Adds labels based on CI/CD outcomes
- Creates promotion blocker issues
- Notifies on status changes

## Git History Philosophy

**Clean, logical progression** from prototype to production:

```
feat(docker): add production-ready Dockerfile with multi-stage build
feat(deployment): add GitHub Actions CI/CD workflow
feat(monitoring): integrate Prometheus metrics collection
test(integration): add comprehensive database integration tests
docs(deployment): add production deployment guide
```

**Not**:
```
WIP
fix stuff
more changes
final fix
actually final fix
```

**Achieved through**:
- Conventional commits (enforced)
- Multi-commit logical grouping
- Pre-commit validation
- Thoughtful commit messages with context
