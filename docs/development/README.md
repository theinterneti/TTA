# TTA Development Documentation

Welcome to the TTA development documentation. This directory contains comprehensive guides for the TTA Component Maturity Promotion Workflow and related development processes.

---

## Quick Start

### For Developers

**Want to promote a component?**
1. Read: [Component Promotion Guide](COMPONENT_PROMOTION_GUIDE.md)
2. Check: Component's `MATURITY.md` file
3. Create: Promotion request using the issue template

**Want to understand the workflow?**
1. Read: [Component Maturity Workflow](COMPONENT_MATURITY_WORKFLOW.md)
2. Review: [Component Inventory](COMPONENT_INVENTORY.md)

**Want to track component status?**
1. View: GitHub Project "TTA Component Maturity Tracker"
2. Check: Daily component status report (automated issue)

---

## Documentation Index

### Core Workflow Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [Component Maturity Workflow](COMPONENT_MATURITY_WORKFLOW.md) | Overview of maturity stages, criteria, and process | All developers |
| [Component Promotion Guide](COMPONENT_PROMOTION_GUIDE.md) | Step-by-step promotion instructions | Developers promoting components |
| [Component Labels Guide](COMPONENT_LABELS_GUIDE.md) | Label taxonomy and usage | All developers |
| [Component Inventory](COMPONENT_INVENTORY.md) | Catalog of all components | All developers |

### Setup and Configuration

| Document | Purpose | Audience |
|----------|---------|----------|
| [GitHub Project Setup](GITHUB_PROJECT_SETUP.md) | Project board configuration | Project administrators |

### Implementation Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| [Phase 5: Pilot Promotion](PHASE5_PILOT_PROMOTION_GUIDE.md) | Pilot promotion execution | Developers executing pilot |
| [Phase 6: Rollout Guide](PHASE6_ROLLOUT_GUIDE.md) | Systematic rollout strategy | Project managers |

### Implementation Reports

| Document | Purpose | Audience |
|----------|---------|----------|
| [Implementation Complete](COMPONENT_MATURITY_WORKFLOW_IMPLEMENTATION_COMPLETE.md) | Overall implementation summary | All stakeholders |
| [Phase 1: Foundation](PHASE1_FOUNDATION_COMPLETE.md) | Foundation phase report | Project administrators |
| [Phase 2: Templates & Documentation](PHASE2_TEMPLATES_DOCUMENTATION_COMPLETE.md) | Templates phase report | Developers |
| [Phase 3: Component Inventory](PHASE3_COMPONENT_INVENTORY_COMPLETE.md) | Inventory phase report | Developers |
| [Phase 4: CI/CD Integration](PHASE4_CICD_INTEGRATION_COMPLETE.md) | CI/CD phase report | DevOps engineers |

---

## Component Maturity Stages

### 🔨 Development
- Active development
- Incomplete features
- Frequent breaking changes
- Local development only

**Exit Criteria**: 70% test coverage, API documented, code quality checks passing

### 🧪 Staging
- Feature-complete
- Integration testing
- API stable
- Multi-user testing

**Exit Criteria**: 80% integration test coverage, 99.5% uptime (7 days), performance validated

### 🚀 Production
- Production-deployed
- Monitored 24/7
- SLA-backed
- Incident response

**Maintenance Criteria**: 99.9% uptime, meets SLAs, regular security scans

---

## Functional Groups

### 🏗️ Core Infrastructure (3 components)
- Neo4j, Docker, Carbon
- Foundational services
- No dependencies
- Must be production-ready first

### 🤖 AI/Agent Systems (4 components)
- Model Management, LLM, Agent Orchestration, Narrative Arc Orchestrator
- AI orchestration and model management
- Depends on Core Infrastructure
- Performance-critical

### 🎮 Player Experience (3 components)
- Gameplay Loop, Character Arc Manager, Player Experience
- Player-facing services
- Depends on Core Infrastructure and AI/Agent Systems
- UX-critical

### 🧠 Therapeutic Content (2 components)
- Narrative Coherence, Therapeutic Systems
- Therapeutic frameworks and safety
- Depends on AI/Agent Systems and Player Experience
- Safety-critical

---

## Promotion Process Overview

```
1. Prepare Component
   ├─ Increase test coverage
   ├─ Complete documentation
   ├─ Fix code quality issues
   └─ Update MATURITY.md

2. Create Promotion Request
   ├─ Use issue template
   ├─ Fill out criteria checklist
   └─ Add appropriate labels

3. Automated Validation
   ├─ Run tests
   ├─ Check coverage
   ├─ Validate criteria
   └─ Post results

4. Manual Review
   ├─ Review validation results
   ├─ Verify criteria
   └─ Approve promotion

5. Execute Promotion
   ├─ Deploy to target environment
   ├─ Update MATURITY.md
   ├─ Update GitHub Project
   └─ Close promotion issue

6. Monitor
   ├─ Track health metrics
   ├─ Monitor for 7 days (staging→production)
   └─ Address any issues
```

---

## Automation

### Automated Workflows

**Component Promotion Validation**
- Trigger: Issue labeled `promotion:requested`
- Actions: Run tests, validate criteria, post results, update labels
- File: `.github/workflows/component-promotion-validation.yml`

**Component Status Report**
- Trigger: Daily at 00:00 UTC, manual, or code changes
- Actions: Run all tests, generate status report, create/update status issue
- File: `.github/workflows/component-status-report.yml`

### Automated Checks

- ✅ Unit test execution
- ✅ Test coverage (≥70% for staging, ≥80% for production)
- ✅ Linting (ruff)
- ✅ Type checking (pyright)
- ✅ Security scanning (bandit)
- ✅ Promotion criteria validation

---

## Scripts

### Label Management
```bash
# Create all component maturity labels
./scripts/setup-component-maturity-labels.sh
```

### Component Setup
```bash
# Create MATURITY.md files for all components
./scripts/create-component-maturity-files.sh
```

### Project Population
```bash
# Guide for adding components to GitHub Project
./scripts/add-components-to-project.sh
```

---

## Issue Templates

### Component Promotion Request
- Template: `.github/ISSUE_TEMPLATE/component_promotion.yml`
- Use: Request promotion to next stage
- Auto-labels: `promotion:requested`

### Promotion Blocker
- Template: `.github/ISSUE_TEMPLATE/promotion_blocker.yml`
- Use: Track blockers preventing promotion
- Auto-labels: `promotion:blocked`

---

## Labels

### Component Labels (24)
- `component:neo4j`, `component:docker`, `component:llm`, etc.
- Purpose: Identify which component

### Target Labels (2)
- `target:staging`, `target:production`
- Purpose: Identify promotion target

### Promotion Workflow Labels (5)
- `promotion:requested`, `promotion:in-review`, `promotion:approved`, `promotion:blocked`, `promotion:completed`
- Purpose: Track promotion status

### Blocker Type Labels (6)
- `blocker:tests`, `blocker:documentation`, `blocker:performance`, `blocker:security`, `blocker:dependencies`, `blocker:integration`
- Purpose: Categorize blockers

**Total Labels**: 37

---

## Current Status

### Implementation
- ✅ All 6 phases complete
- ✅ 25+ files created
- ✅ 37 labels created
- ✅ 12 components inventoried
- ✅ 2 automated workflows implemented

### Components
- **Development**: 12 components
- **Staging**: 0 components
- **Production**: 0 components

### Next Steps
1. Create GitHub Project board (manual)
2. Add components to project (manual)
3. Execute pilot promotion (Neo4j)
4. Begin systematic rollout

---

## Getting Help

### Documentation
- Start with [Component Maturity Workflow](COMPONENT_MATURITY_WORKFLOW.md)
- For promotion: [Component Promotion Guide](COMPONENT_PROMOTION_GUIDE.md)
- For labels: [Component Labels Guide](COMPONENT_LABELS_GUIDE.md)

### Issues
- Create a discussion in GitHub Discussions
- Tag with `question` or `help-wanted`

### Contact
- Repository maintainer: @theinterneti

---

## Contributing

### Improving the Workflow
1. Document issues or suggestions
2. Create a discussion or issue
3. Propose changes via PR
4. Update documentation

### Updating Documentation
1. Make changes to relevant markdown files
2. Update this README if adding new documents
3. Submit PR with clear description

---

## Related Documentation

### Project-Wide Documentation
- [Project Reorganization Plan](../../PROJECT_REORGANIZATION_PLAN.md)
- [Environment Setup Guide](../environments/ENVIRONMENT_SETUP_GUIDE.md)

### Component Documentation
- Component READMEs: `src/components/<component>/README.md`
- Component MATURITY files: `src/components/<component>/MATURITY.md`

---

**Last Updated**: 2025-10-07

**Status**: ✅ Implementation Complete, Ready for Pilot Promotion
