# TTA Component Maturity Criteria

## Overview

Components in the TTA project progress independently through maturity stages based on **objective quality criteria**. This document defines the specific requirements for promoting components between stages.

## Maturity Stages

```
Development → Staging → Production
```

Each stage has increasingly strict requirements to ensure quality and reliability.

## Development Stage

### Entry Criteria

- Component exists in `src/` directory
- Basic functionality implemented
- Initial unit tests written

### Exit Criteria (Promotion to Staging)

Must meet **ALL** of the following:

#### 1. Test Coverage ≥70%

```bash
# Measure coverage
uvx pytest tests/ --cov=src/<component> --cov-report=term

# Example output:
# src/player_experience/     72%    ✓
```

**Breakdown**:
- Critical paths (auth, data persistence): ≥90%
- Business logic: ≥80%
- Utilities: ≥70%
- UI components: ≥60% (focus on integration tests)

**Enforcement**: CI/CD fails if coverage below threshold

#### 2. All Unit Tests Passing

```bash
# Run component-specific unit tests
uvx pytest tests/unit/ -m <component_name> -v

# Must show: 100% passing, 0 failures, 0 errors
```

#### 3. Linting Clean (Ruff)

```bash
# Check linting
uvx ruff check src/<component>/

# Must show: All checks passed
```

**Configuration**: `pyproject.toml`
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
```

#### 4. Type Checking Clean (Pyright)

```bash
# Check types
uvx pyright src/<component>/

# Must show: 0 errors, 0 warnings
```

**Configuration**: `pyrightconfig.json`
```json
{
  "typeCheckingMode": "basic",
  "reportMissingTypeStubs": false
}
```

#### 5. Security Scan Passed

```bash
# Run security scan
uvx bandit -r src/<component>/ -f json -o bandit-report.json

# Check for high/medium severity issues
# Must show: 0 high severity, 0 medium severity
```

**Acceptable**: Low severity issues with documented risk acceptance

#### 6. Integration Tests Written

```bash
# Integration tests must exist
ls tests/integration/test_<component>_*.py

# Must include:
# - Database integration (Redis/Neo4j)
# - API endpoint testing
# - Cross-component interactions
```

**Example**:
```python
# tests/integration/test_player_experience_integration.py

@pytest.mark.integration
@pytest.mark.redis
async def test_player_session_persistence(redis_client):
    """Verify player session persists in Redis."""
    session = await create_player_session(player_id="test-123")

    # Verify Redis storage
    stored = await redis_client.hgetall(f"session:{session.id}")
    assert stored["player_id"] == "test-123"
```

#### 7. Documentation Complete

Must include:
- **README.md**: Component overview, usage examples
- **API Documentation**: Docstrings for all public functions/classes
- **Architecture Diagram**: Component relationships (if complex)

#### 8. No Promotion Blockers

```bash
# Check for blocker issues
gh issue list --label "component:<name>,blocker:*"

# Must show: No open issues
```

## Staging Stage

### Entry Criteria

All Development exit criteria met (above).

### Exit Criteria (Promotion to Production)

Must meet **ALL** of the following:

#### 1. All Integration Tests Passing

```bash
# Run integration tests
uvx pytest tests/integration/ -m <component_name> -v

# Must show: 100% passing, 0 failures, 0 errors
```

**Includes**:
- Real database connections (Redis, Neo4j)
- Multi-component workflows
- API integration tests
- WebSocket communication tests

#### 2. E2E Tests Passing

```bash
# Run E2E tests
uvx playwright test tests/e2e-staging/ --grep <component_name>

# Must show: All tests passed
```

**Validation Areas**:
- Complete user journeys
- UI/UX functionality
- Database persistence
- Error handling
- Browser compatibility (Chromium, Firefox, WebKit)
- Responsive design (desktop, tablet, mobile)

#### 3. Performance Benchmarks Met

**Response Time**:
- API endpoints: p95 < 500ms
- Database queries: p95 < 100ms
- Page loads: p95 < 3s

**Throughput**:
- Concurrent users: ≥100 (staging environment)
- Requests per second: ≥50

**Resource Usage**:
- Memory: < 512MB per container
- CPU: < 50% average utilization

**Measurement**:
```bash
# Load testing
uvx locust -f tests/performance/locustfile.py --host http://staging.tta.local
```

#### 4. Security Audit Completed

**Automated Scans**:
```bash
# Dependency vulnerabilities
uvx safety check

# Secret detection
uvx detect-secrets scan

# SAST (Static Application Security Testing)
uvx bandit -r src/<component>/
```

**Manual Review**:
- Authentication/authorization logic
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- CSRF protection
- Secure session management

**Documentation**: Security findings documented in `SECURITY_FINDINGS_ACCEPTED_RISKS.md`

#### 5. Monitoring Integrated

**Metrics Collection**:
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('component_requests_total', 'Total requests')
request_duration = Histogram('component_request_duration_seconds', 'Request duration')
```

**Logging**:
```python
# Structured logging
import structlog

logger = structlog.get_logger()
logger.info("component_event", event_type="user_action", component="player_experience")
```

**Alerting**:
- Error rate > 1%: Warning
- Error rate > 5%: Critical
- Response time p95 > 1s: Warning
- Response time p95 > 3s: Critical

#### 6. Staging Validation Passed

**Home Lab Deployment**:
```bash
# Deploy to staging
docker-compose -f docker-compose.staging-homelab.yml up -d

# Verify deployment
curl http://staging.tta.local/health
```

**Multi-User Testing**:
- Minimum 3 concurrent users
- Minimum 1 hour session duration
- No critical bugs discovered
- User feedback collected and addressed

#### 7. Rollback Plan Documented

**Must include**:
- Rollback procedure (step-by-step)
- Database migration rollback (if applicable)
- Feature flag configuration (if applicable)
- Estimated rollback time
- Rollback testing verification

**Example**:
```markdown
## Rollback Plan: player-experience v2.0

### Trigger Conditions
- Error rate > 10%
- Critical functionality broken
- Data corruption detected

### Rollback Steps
1. Revert Docker image: `docker pull tta/player-experience:v1.9`
2. Update docker-compose.yml: `image: tta/player-experience:v1.9`
3. Restart containers: `docker-compose restart player-experience`
4. Verify health: `curl http://localhost/health`
5. Monitor metrics for 15 minutes

### Database Rollback
- Run migration: `uv run alembic downgrade -1`
- Verify data integrity: `uv run python scripts/verify_db.py`

### Estimated Time: 10 minutes
```

#### 8. Manual QA Approval

**QA Checklist**:
- [ ] All user flows tested manually
- [ ] UI/UX meets design specifications
- [ ] Accessibility tested (WCAG 2.1 AA)
- [ ] Cross-browser compatibility verified
- [ ] Mobile responsiveness verified
- [ ] Error messages clear and helpful
- [ ] Performance acceptable (subjective feel)
- [ ] No console errors or warnings

**Approval**: QA lead signs off on GitHub issue

## Production Stage

### Entry Criteria

All Staging exit criteria met (above).

### Maintenance Criteria

Once in production, components must maintain:

#### 1. Uptime ≥99.5%

**Measurement**: Monthly uptime percentage
```
Uptime % = (Total Time - Downtime) / Total Time × 100
```

**Acceptable Downtime**: ~3.6 hours per month

#### 2. Error Rate <0.5%

**Measurement**: Errors per total requests
```
Error Rate % = (Error Requests / Total Requests) × 100
```

**Monitoring**: Real-time alerting on error rate spikes

#### 3. Performance SLAs

- API response time p95 < 500ms
- Page load time p95 < 3s
- Database query time p95 < 100ms

#### 4. Security Patching

- Critical vulnerabilities: Patched within 24 hours
- High vulnerabilities: Patched within 7 days
- Medium vulnerabilities: Patched within 30 days

#### 5. Incident Response

**Severity Levels**:
- **P0 (Critical)**: System down, data loss - Response: Immediate
- **P1 (High)**: Major functionality broken - Response: < 1 hour
- **P2 (Medium)**: Minor functionality broken - Response: < 4 hours
- **P3 (Low)**: Cosmetic issues - Response: < 24 hours

## Promotion Blocker Categories

### Blocker: Tests

**Label**: `blocker:tests`

**Criteria**:
- Test coverage below threshold
- Failing unit/integration/E2E tests
- Missing critical test scenarios

**Resolution**: Write/fix tests until criteria met

### Blocker: Security

**Label**: `blocker:security`

**Criteria**:
- High/medium severity vulnerabilities
- Failed security audit
- Missing security controls

**Resolution**: Patch vulnerabilities, implement controls, re-audit

### Blocker: Performance

**Label**: `blocker:performance`

**Criteria**:
- Response times exceed SLAs
- Resource usage too high
- Failed load testing

**Resolution**: Optimize code, add caching, scale resources

### Blocker: Documentation

**Label**: `blocker:documentation`

**Criteria**:
- Missing README or API docs
- Incomplete architecture documentation
- No deployment/rollback procedures

**Resolution**: Write comprehensive documentation

### Blocker: Dependencies

**Label**: `blocker:dependencies`

**Criteria**:
- Outdated dependencies with known vulnerabilities
- Incompatible dependency versions
- Missing dependency declarations

**Resolution**: Update dependencies, resolve conflicts

## Component-Specific Labels

### Format

`component:<name>` where `<name>` is:
- `player-experience`
- `agent-orchestration`
- `narrative-engine`
- `ai-components`
- `infrastructure`
- `api-gateway`

### Target Labels

`target:<stage>` where `<stage>` is:
- `target:staging`
- `target:production`

### Example Issue

```markdown
Title: Promote player-experience to staging

Labels: component:player-experience, target:staging

## Checklist

- [x] Test coverage ≥70% (currently 72%)
- [x] All unit tests passing
- [x] Linting clean (ruff)
- [x] Type checking clean (pyright)
- [x] Security scan passed
- [x] Integration tests written
- [x] Documentation complete
- [x] No promotion blockers

## Next Steps

1. Deploy to staging environment
2. Run integration test suite
3. Run E2E test suite
4. Monitor for 24 hours
5. If stable, create production promotion issue
```

## Automation

### GitHub Actions Workflows

**On Pull Request**:
```yaml
# .github/workflows/component-quality-check.yml
name: Component Quality Check

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests with coverage
        run: uvx pytest --cov=src --cov-fail-under=70
      - name: Run linting
        run: uvx ruff check src/
      - name: Run type checking
        run: uvx pyright src/
      - name: Run security scan
        run: uvx bandit -r src/
```

**On Staging Deployment**:
```yaml
# .github/workflows/staging-validation.yml
name: Staging Validation

on:
  workflow_dispatch:
    inputs:
      component:
        description: 'Component to validate'
        required: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: uvx pytest tests/integration/ -m ${{ inputs.component }}
      - name: Run E2E tests
        run: uvx playwright test --grep ${{ inputs.component }}
      - name: Check performance benchmarks
        run: uvx locust -f tests/performance/locustfile.py --headless
```

## Maturity Dashboard

**Location**: `src/developer_dashboard/`

**Features**:
- Real-time component maturity status
- Test coverage trends
- Promotion blocker tracking
- Quality metrics visualization
- Deployment history

**Access**: `http://localhost:8080/dashboard/maturity`
