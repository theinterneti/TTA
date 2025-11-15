# TTA Documentation

Welcome to the TTA (Therapeutic Text Adventure) documentation!

## Documentation Structure

### 📚 Primary Knowledge Base
Most documentation lives in the **Logseq Knowledge Base** at `.augment/kb/`:
- 306 interconnected documents
- Architecture, components, workflows, testing, and more
- See [docs/reference/logseq-kb.md](reference/logseq-kb.md) for navigation

### 📖 This Directory (`docs/`)
Complementary documentation for active development:

#### [guides/](guides/) - How-To Documentation
- [Testing Guide](guides/testing.md) - Comprehensive testing workflows
- [Docker Quick Start](guides/docker-quick-start.md) - Container setup
- [Database Quick Reference](guides/database-quick-ref.md) - Redis & Neo4j
- [Advanced Testing](guides/advanced-testing.md) - E2E, mutation, load tests
- [Cross-Repo Development](guides/cross-repo-development.md) - Multi-repo workflow
- [Secrets Management](guides/secrets-management.md) - Credential handling
- [NotebookLM with Copilot](guides/notebooklm-copilot.md) - AI integration
- [CodeCov Setup](guides/codecov-setup.md) - Coverage reporting

#### [status/](status/) - Project Dashboards
- [Current Sprint](status/current-sprint.md) - Active work tracking
- [P0 Components](status/p0-components.md) - Critical component status
- [Component Maturity](status/component-maturity.md) - Maturity levels
- [AI Toolkit Submission](status/ai-toolkit-submission.md) - Package status
- [Code Quality](status/code-quality.md) - Linting & workflow health
- [TODO Audit](status/todo-audit.md) - Incomplete work tracking

#### [setup/](setup/) - Environment Setup
- [Dev Environment](setup/dev-environment.md) - Complete setup guide
- [MCP Servers](setup/mcp-servers.md) - Model Context Protocol setup
- [VSCode Database](setup/vscode-database.md) - Database integration
- [Keploy Integration](setup/keploy-integration.md) - Testing framework

#### [development/](development/) - Process Documentation
- [GitHub Issues](development/github-issues.md) - Issue management
- [Workflow Recommendations](development/workflow-recommendations.md) - Best practices
- [Primitives Comparison](development/primitives-comparison.md) - Implementation patterns
- [Primitives Improvements](development/primitives-improvements.md) - Enhancement plans
- [Next Steps](development/next-steps.md) - Upcoming work
- [Test Targets](development/test-targets.md) - Test generation priorities

#### [reference/](reference/) - Quick References
- [Logseq KB Guide](reference/logseq-kb.md) - Navigate the knowledge base

## Getting Started

### New Contributors
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) in the repository root
2. Follow [setup/dev-environment.md](setup/dev-environment.md) for environment setup
3. Review [guides/testing.md](guides/testing.md) for testing workflow
4. Check [status/current-sprint.md](status/current-sprint.md) for active work

### Existing Contributors
- **Daily:** Check [status/current-sprint.md](status/current-sprint.md)
- **New Features:** Review component architecture in `.augment/kb/TTA___Components___`
- **Debugging:** Check [guides/database-quick-ref.md](guides/database-quick-ref.md)
- **Deployment:** Follow [guides/docker-quick-start.md](guides/docker-quick-start.md)

## Documentation Philosophy

### Repository `docs/` (This Directory)
**Purpose:** Active development reference
- Current status and dashboards
- Quick-start guides
- Environment setup
- Common workflows

### Logseq KB (`.augment/kb/`)
**Purpose:** Deep knowledge and context
- System architecture
- Component design decisions
- Historical context and evolution
- Agent behavior and patterns
- Cross-cutting concerns

### When to Add New Docs

**Add to `docs/`:**
- Quick reference guides
- Current project status
- Active work tracking
- Environment setup instructions

**Add to KB:**
- Architectural decisions
- Component specifications
- Long-term design docs
- Agent behavioral patterns
- Cross-project learnings

## Maintenance

- **`docs/`**: Updated frequently with current status
- **`.augment/kb/`**: Updated for significant changes or new components
- **`.archive/`**: Historical reports preserved but not actively maintained

---

**Questions?** Check the [Logseq KB Guide](reference/logseq-kb.md) or ask in team chat!
