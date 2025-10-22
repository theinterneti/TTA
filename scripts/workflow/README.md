# Integrated Development Workflow

**Version:** 1.0.0
**Status:** Production Ready
**Last Updated:** 2025-10-20

---

## Overview

The Integrated Development Workflow combines all three Phase 1 agentic primitives (AI Context Management, Error Recovery, Development Observability) with TTA's component maturity workflow to create an automated, reliable pipeline from specification to production deployment.

**Key Features:**
- ✅ Zero-manual-intervention automation (happy path)
- ✅ Complete observability via metrics dashboard
- ✅ Resilient error handling with automatic retry
- ✅ AI context maintained across multi-session development
- ✅ Automated quality gates enforcement
- ✅ Compatible with existing TTA workflows

---

## Quick Start

### Basic Usage

```bash
# Run workflow for a component targeting staging
python scripts/workflow/spec_to_production.py \
    --spec specs/my_component.md \
    --component my_component \
    --target staging

# Run workflow targeting production
python scripts/workflow/spec_to_production.py \
    --spec specs/my_component.md \
    --component my_component \
    --target production \
    --output my_component_production_report.json
```

### Python API

```python
from workflow.spec_to_production import run_workflow

result = run_workflow(
    spec_file="specs/my_component.md",
    component_name="my_component",
    target_stage="staging"
)

if result.success:
    print(f"✓ Workflow completed successfully!")
    print(f"Stages: {', '.join(result.stages_completed)}")
    print(f"Dashboard: {result.metrics_dashboard}")
else:
    print(f"✗ Workflow failed")
    print(f"Failed stages: {', '.join(result.stages_failed)}")
```

---

## Workflow Stages

### Stage 1: Specification Parsing

**Purpose:** Parse and validate specification document

**Inputs:**
- Specification file (markdown)
- Component name

**Outputs:**
- Parsed specification
- AI context session created

**Quality Gates:** None

---

### Stage 2: Testing

**Purpose:** Run tests and validate coverage

**Inputs:**
- Component source code
- Test files

**Outputs:**
- Test results
- Coverage report

**Quality Gates:**
- All tests pass
- Coverage ≥70% (for staging)

**Error Recovery:**
- Max retries: 3
- Base delay: 1s
- Exponential backoff: 2.0x

---

### Stage 3: Refactoring

**Purpose:** Validate code quality and auto-fix issues

**Inputs:**
- Component source code

**Outputs:**
- Linting results
- Type checking results
- Security scan results

**Quality Gates:**
- Linting passes (ruff)
- Type checking passes (pyright)
- No security issues (detect-secrets)

**Auto-Fix:**
- Linting issues (ruff check --fix)
- Code formatting (ruff format)

---

### Stage 4: Staging Deployment

**Purpose:** Deploy to staging environment

**Inputs:**
- Validated component code
- Quality gate results

**Outputs:**
- Staging deployment
- Integration test results

**Quality Gates:**
- All dev→staging criteria met
- Coverage ≥70%
- All tests passing
- Linting clean
- Type checking clean
- Security scan passed

**Error Recovery:**
- Max retries: 5
- Base delay: 2s
- Exponential backoff: 2.0x
- Max delay: 30s

---

### Stage 5: Production Deployment

**Purpose:** Deploy to production environment

**Inputs:**
- Staging deployment
- 7-day stability metrics

**Outputs:**
- Production deployment
- E2E test results

**Quality Gates:**
- All staging→production criteria met
- Coverage ≥80% (integration tests)
- Performance meets SLAs
- 7-day uptime ≥99.5%
- Security review complete

**Error Recovery:**
- Max retries: 3
- Base delay: 5s
- Exponential backoff: 1.5x
- Max delay: 60s

---

## Quality Gates

### Testing Gates

| Gate | Threshold | Auto-Fix |
|------|-----------|----------|
| Test Pass Rate | 100% | No |
| Test Coverage (Dev) | ≥50% | No |
| Test Coverage (Staging) | ≥70% | No |
| Test Coverage (Production) | ≥80% | No |

### Code Quality Gates

| Gate | Threshold | Auto-Fix |
|------|-----------|----------|
| Linting (ruff) | 0 issues | Yes |
| Type Checking (pyright) | 0 errors | No |
| Code Complexity | Acceptable | No |

### Security Gates

| Gate | Threshold | Auto-Fix |
|------|-----------|----------|
| Secrets Detection | 0 secrets | No |
| Critical Vulnerabilities | 0 | No |
| High Vulnerabilities | 0 | No |
| Medium Vulnerabilities | ≤5 | No |

### Instruction Validation Gates

| Gate | Threshold | Auto-Fix |
|------|-----------|----------|
| YAML Frontmatter | Valid | No |
| Required Fields | Present | No |
| Content Structure | Recommended | No |

**Validation Rules:**

1. **YAML Frontmatter Validation**
   - Frontmatter must be present between `---` markers
   - Must be valid YAML syntax
   - Required fields: `applyTo`, `description`

2. **Field Type Validation**
   - `applyTo`: Must be string or list of strings (glob patterns)
   - `description`: Must be non-empty string

3. **Content Structure Validation** (warnings only)
   - Markdown headers recommended (`##` sections)
   - Minimum content length: 100 characters

**Example Valid Instruction File:**

```markdown
---
applyTo: "src/player_experience/**/*.py"
description: "Player experience component patterns"
---
# Player Experience Instructions

## Architecture Patterns

Content here...

## Common Patterns

More content...
```

**Common Validation Errors:**

| Error | Fix |
|-------|-----|
| Missing frontmatter | Add `---` delimited YAML at file start |
| Missing `applyTo` | Add `applyTo: "**/*.py"` to frontmatter |
| Missing `description` | Add `description: "..."` to frontmatter |
| Invalid `applyTo` type | Use string or list of strings |
| Empty `description` | Provide meaningful description |

**Running Validation Manually:**

```bash
# Validate all instruction files
python scripts/workflow/quality_gates.py instructions_validation

# Or use Python API
from scripts.workflow.quality_gates import InstructionsValidationGate

gate = InstructionsValidationGate()
result = gate.validate()

if not result.passed:
    for error in result.errors:
        print(f"ERROR: {error}")
```

---

## Primitive Integration

### AI Context Management

**Integration Points:**
- Session created at workflow start
- Decisions tracked with importance scoring
- Session saved after each stage
- Session archived after completion

**Importance Scoring:**
- 1.0: Architectural decisions, requirements, production status
- 0.9: Implementation completion, test results, deployment status
- 0.7: Refactoring decisions, optimization choices
- 0.5: General progress updates

**Session Lifecycle:**
```
Create → Update (per stage) → Save → Archive
```

---

### Error Recovery

**Integration Points:**
- Testing stage (retry flaky tests)
- Staging deployment (retry transient failures)
- Production deployment (retry with rollback)

**Retry Configuration:**
```yaml
testing:
  max_retries: 3
  base_delay: 1.0s
  exponential_base: 2.0

staging_deployment:
  max_retries: 5
  base_delay: 2.0s
  max_delay: 30.0s

production_deployment:
  max_retries: 3
  base_delay: 5.0s
  max_delay: 60.0s
```

**Circuit Breaker:**
- Failure threshold: 5 consecutive failures
- Recovery timeout: 60 seconds
- Half-open test: 1 request

---

### Development Observability

**Integration Points:**
- All stages tracked with `@track_execution`
- Metrics collected per stage
- Dashboard generated after workflow completion

**Metrics Collected:**
- Stage execution time
- Success/failure rate
- Retry count
- Error types
- Quality gate results

**Dashboard Views:**
- Workflow overview
- Quality gate status
- Performance metrics
- Historical trends

---

## Configuration

### Configuration File

Edit `scripts/workflow/workflow_config.yaml` to customize:
- Quality gate thresholds
- Retry policies
- Observability settings
- Context management settings
- Stage timeouts

### Example Configuration

```yaml
quality_gates:
  test_coverage:
    staging_threshold: 70.0
    production_threshold: 80.0

error_recovery:
  testing:
    max_retries: 3
    base_delay: 1.0

observability:
  metrics:
    enabled: true
    retention_days: 30
```

---

## Examples

### Example 1: Run Workflow for Staging

```bash
python scripts/workflow/spec_to_production.py \
    --spec specs/player_experience.md \
    --component player_experience \
    --target staging
```

**Output:**
```
============================================================
WORKFLOW SUMMARY
============================================================
Component: player_experience
Target Stage: staging
Success: ✓ YES
Stages Completed: specification, testing, refactoring, staging_deployment
Total Time: 45230ms
Context Session: player_experience-workflow-2025-10-20
Metrics Dashboard: workflow_dashboard_player_experience.html
Report Saved: workflow_report_player_experience.json
============================================================
```

---

### Example 2: View Workflow Report

```python
import json

with open("workflow_report_player_experience.json") as f:
    report = json.load(f)

print(f"Success: {report['success']}")
print(f"Stages: {report['stages_completed']}")

# View quality gate results
for stage_name, stage_result in report['stage_results'].items():
    print(f"\n{stage_name}:")
    for gate_name, gate_result in stage_result.get('quality_gates', {}).items():
        status = "✓" if gate_result['passed'] else "✗"
        print(f"  {status} {gate_name}")
```

---

### Example 3: View Metrics Dashboard

```bash
# Dashboard is auto-generated after workflow completion
open workflow_dashboard_player_experience.html

# Or generate manually
python scripts/observability/dashboard.py
```

---

## Troubleshooting

### Workflow Fails at Testing Stage

**Problem:** Tests fail or coverage too low

**Solution:**
```bash
# Run tests manually to see failures
uvx pytest tests/my_component/ -v

# Check coverage
uvx pytest tests/my_component/ --cov=src/my_component --cov-report=term

# Fix tests and re-run workflow
```

---

### Workflow Fails at Refactoring Stage

**Problem:** Linting or type checking errors

**Solution:**
```bash
# Auto-fix linting issues
uvx ruff check --fix src/my_component/ tests/my_component/
uvx ruff format src/my_component/ tests/my_component/

# Check type errors
uvx pyright src/my_component/

# Fix type errors manually and re-run workflow
```

---

### Workflow Fails at Staging Deployment

**Problem:** Quality gates not met

**Solution:**
```bash
# Check which gates failed
cat workflow_report_my_component.json | jq '.stage_results.staging_deployment.errors'

# Address each failed gate
# Re-run workflow
```

---

## Best Practices

1. **Write Comprehensive Specs:** Clear specifications lead to better implementations
2. **Test Early, Test Often:** Write tests before running workflow
3. **Monitor Metrics:** Review dashboard after each workflow run
4. **Use Context Sessions:** Load previous sessions for multi-day development
5. **Configure Thresholds:** Adjust quality gate thresholds per component needs
6. **Review Failures:** Analyze failed workflows to improve process

---

## Integration with Existing Workflows

### Pre-commit Hooks

The workflow respects existing pre-commit hooks:
- Ruff linting and formatting
- Secret detection
- Conventional commits

### CI/CD Workflows

The workflow can be integrated into GitHub Actions:

```yaml
name: Component Workflow

on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'

jobs:
  workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run workflow
        run: |
          python scripts/workflow/spec_to_production.py \
            --spec specs/${{ matrix.component }}.md \
            --component ${{ matrix.component }} \
            --target staging
```

---

## Related Documentation

- **Design Document:** `docs/development/integrated-workflow-design.md`
- **Quality Gates:** `scripts/workflow/quality_gates.py`
- **Stage Handlers:** `scripts/workflow/stage_handlers.py`
- **Configuration:** `scripts/workflow/workflow_config.yaml`
- **Component Maturity:** `docs/development/COMPONENT_MATURITY_WORKFLOW.md`

---

**Status:** Production Ready
**Next Steps:** Run workflow for your component!
