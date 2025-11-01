# TTA Documentation Index

**Quick reference for all TTA documentation organized by category and purpose.**

---

## 📚 Documentation Categories

### 🚀 Setup & Configuration
Located in `docs/setup/`

- **[Development Setup](setup/DEVELOPMENT_SETUP.md)** - Set up your development environment
- **[Environment Setup](setup/ENVIRONMENT_SETUP.md)** - Configure environment variables
- **[UV Configuration Guide](setup/UV_CONFIGURATION_GUIDE.md)** - UV package manager setup
- **[MCP Setup](setup/MCP_SETUP_README.md)** - Model Context Protocol setup
- **[Testing Database Setup](setup/TESTING_DATABASE_SETUP.md)** - Database configuration for tests

### 🏗️ Development
Located in `docs/development/`

- **[Git Commit Strategy](development/GIT_COMMIT_STRATEGY.md)** - Commit message conventions and workflow
- **[Type Annotation Strategy](development/TYPE_ANNOTATION_STRATEGY_ANALYSIS.md)** - Type checking approach
- **[Type Strategy Executive Summary](development/EXECUTIVE_SUMMARY_TYPE_STRATEGY.md)** - Type checking overview
- **[Proof of Concept: Pyright](development/PROOF_OF_CONCEPT_PYRIGHT.md)** - Pyright type checker POC
- **[Free Models Filter Guide](development/FREE_MODELS_FILTER_GUIDE.md)** - Working with free AI models

### 🧪 Testing
Located in `docs/testing/`

- **[Testing Guide](testing/TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[Testing Directories Analysis](testing/TESTING_DIRECTORIES_ANALYSIS.md)** - Understanding tests/ vs testing/

### 🚢 Deployment
Located in `docs/deployment/`

- **[Production Deployment Guide](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[Staging Deployment Plan](deployment/STAGING_DEPLOYMENT_PLAN.md)** - Staging environment setup
- **[Cloudflare Staging Setup](deployment/CLOUDFLARE_STAGING_SETUP.md)** - Cloudflare configuration
- **[Staging Hosting Analysis](deployment/STAGING_HOSTING_ANALYSIS.md)** - Hosting options analysis

### 🔧 Operations & Maintenance
Located in `docs/operations/`

- **[Operational Excellence Report](operations/OPERATIONAL_EXCELLENCE_REPORT.md)** - Operations best practices
- **[Production Readiness Assessment](operations/PRODUCTION_READINESS_ASSESSMENT.md)** - Production checklist
- **[Database Performance Optimization](operations/DATABASE_PERFORMANCE_OPTIMIZATION.md)** - Database tuning
- **[Filesystem Optimization Report](operations/FILESYSTEM_OPTIMIZATION_REPORT.md)** - WSL2 filesystem optimization

#### Security (`docs/operations/security/`)
- **[Security Hardening Report](operations/security/SECURITY_HARDENING_REPORT.md)** - Security measures
- **[Security Remediation Summary](operations/security/SECURITY_REMEDIATION_SUMMARY.md)** - Security fixes
- **[Security Findings - Accepted Risks](operations/security/SECURITY_FINDINGS_ACCEPTED_RISKS.md)** - Known risks

#### Monitoring (`docs/operations/monitoring/`)
- **[Grafana Access Guide](operations/monitoring/grafana_access_guide.md)** - Grafana dashboard access
- **[Neo4j Browser Troubleshooting](operations/monitoring/neo4j_browser_troubleshooting.md)** - Neo4j issues
- **[TTA Analytics Report](operations/monitoring/tta_analytics_report.md)** - Analytics overview
- **[TTA Analytics Executive Summary](operations/monitoring/tta_analytics_executive_summary.md)** - Analytics summary
- **[TTA Data Visualization Assessment](operations/monitoring/tta_data_visualization_assessment.md)** - Visualization tools

### 🏥 Clinical & Therapeutic
Located in `docs/clinical/`

- **[Evidence-Based Frameworks](clinical/EVIDENCE_BASED_FRAMEWORKS.md)** - Therapeutic approaches (CBT, DBT, ACT, Mindfulness, Trauma-Informed Care)
- **[Clinical Consultation Framework](clinical/CLINICAL_CONSULTATION_FRAMEWORK.md)** - Clinical oversight and validation structure
- **[Therapeutic Content Overview](clinical/THERAPEUTIC_CONTENT_OVERVIEW.md)** - Therapeutic content guidelines and management

### 🔌 Integration
Located in `docs/integration/`

- **[GitHub Secrets Guide](integration/GITHUB_SECRETS_GUIDE.md)** - Managing GitHub secrets
- **[Sentry Integration Guide](integration/SENTRY_INTEGRATION_GUIDE.md)** - Error tracking setup
- **[MCP Verification Report](integration/MCP_VERIFICATION_REPORT.md)** - MCP integration status

### 🌍 Environment Management
Located in `docs/environments/`

- **[Environment Setup Guide](environments/ENVIRONMENT_SETUP_GUIDE.md)** - Complete environment guide
- **[Port Reference](environments/PORT_REFERENCE.md)** - Port allocation reference
- **[Switching Environments](environments/SWITCHING_ENVIRONMENTS.md)** - Environment switching guide

---

## 🗂️ By Role

### New Developer
1. [Development Setup](setup/DEVELOPMENT_SETUP.md)
2. [Environment Setup](setup/ENVIRONMENT_SETUP.md)
3. [Environment Management Guide](environments/ENVIRONMENT_SETUP_GUIDE.md)
4. [Git Commit Strategy](development/GIT_COMMIT_STRATEGY.md)
5. [Testing Guide](testing/TESTING_GUIDE.md)

### DevOps Engineer
1. [Production Deployment Guide](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
2. [Staging Deployment Plan](deployment/STAGING_DEPLOYMENT_PLAN.md)
3. [Operational Excellence Report](operations/OPERATIONAL_EXCELLENCE_REPORT.md)
4. [Security Hardening Report](operations/security/SECURITY_HARDENING_REPORT.md)
5. [Monitoring Guides](operations/monitoring/)

### QA Engineer
1. [Testing Guide](testing/TESTING_GUIDE.md)
2. [Testing Directories Analysis](testing/TESTING_DIRECTORIES_ANALYSIS.md)
3. [Environment Setup Guide](environments/ENVIRONMENT_SETUP_GUIDE.md)
4. [Testing Database Setup](setup/TESTING_DATABASE_SETUP.md)

### Clinical Consultant / Therapist
1. [Evidence-Based Frameworks](clinical/EVIDENCE_BASED_FRAMEWORKS.md)
2. [Clinical Consultation Framework](clinical/CLINICAL_CONSULTATION_FRAMEWORK.md)
3. [Therapeutic Content Overview](clinical/THERAPEUTIC_CONTENT_OVERVIEW.md)

### System Administrator
1. [Environment Setup Guide](environments/ENVIRONMENT_SETUP_GUIDE.md)
2. [Port Reference](environments/PORT_REFERENCE.md)
3. [Database Performance Optimization](operations/DATABASE_PERFORMANCE_OPTIMIZATION.md)
4. [Filesystem Optimization Report](operations/FILESYSTEM_OPTIMIZATION_REPORT.md)
5. [Monitoring Guides](operations/monitoring/)

---

## 📖 Additional Documentation

### Main Documentation Hub
- **[Documentation Hub](README.md)** - Comprehensive documentation organized by audience

### Project Root
- **[Main README](../README.md)** - Project overview and quick start
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute

### Historical Documentation
- **[Archive](../archive/README.md)** - Historical reports and completion summaries
  - Phase completion reports
  - Task completion summaries
  - Fix and resolution reports
  - Validation reports
  - CI/CD reports
  - Integration reports

### Test Artifacts
- **[Artifacts](../artifacts/README.md)** - Test scripts, screenshots, and results
  - Test scripts from development sessions
  - UI screenshots (auth, character, chat)
  - Test execution results

---

## 🔍 Quick Find

### Common Tasks

| Task | Documentation |
|------|---------------|
| Set up development environment | [Development Setup](setup/DEVELOPMENT_SETUP.md) |
| Configure environment variables | [Environment Setup](setup/ENVIRONMENT_SETUP.md) |
| Switch between dev/staging | [Switching Environments](environments/ENVIRONMENT_SETUP_GUIDE.md) |
| Run tests | [Testing Guide](testing/TESTING_GUIDE.md) |
| Deploy to staging | [Staging Deployment Plan](deployment/STAGING_DEPLOYMENT_PLAN.md) |
| Deploy to production | [Production Deployment Guide](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) |
| Check port allocations | [Port Reference](environments/PORT_REFERENCE.md) |
| Access Grafana | [Grafana Access Guide](operations/monitoring/grafana_access_guide.md) |
| Troubleshoot Neo4j | [Neo4j Browser Troubleshooting](operations/monitoring/neo4j_browser_troubleshooting.md) |
| Configure GitHub secrets | [GitHub Secrets Guide](integration/GITHUB_SECRETS_GUIDE.md) |
| Set up error tracking | [Sentry Integration Guide](integration/SENTRY_INTEGRATION_GUIDE.md) |
| Optimize database | [Database Performance Optimization](operations/DATABASE_PERFORMANCE_OPTIMIZATION.md) |
| Review security | [Security Hardening Report](operations/security/SECURITY_HARDENING_REPORT.md) |

### By Topic

| Topic | Documentation |
|-------|---------------|
| **Setup** | [setup/](setup/) |
| **Development** | [development/](development/) |
| **Testing** | [testing/](testing/) |
| **Deployment** | [deployment/](deployment/) |
| **Operations** | [operations/](operations/) |
| **Security** | [operations/security/](operations/security/) |
| **Monitoring** | [operations/monitoring/](operations/monitoring/) |
| **Integration** | [integration/](integration/) |
| **Environments** | [environments/](environments/) |

---

## 📝 Documentation Standards

When creating or updating documentation:

1. **Location:** Place in appropriate category directory
2. **Naming:** Use descriptive names (UPPERCASE for major guides)
3. **Format:** Markdown with clear structure
4. **Examples:** Include practical code examples
5. **Cross-references:** Link to related documentation
6. **Date stamps:** Include last updated date
7. **Update index:** Add to this index and main README

---

**Last Updated:** 2025-10-04
**See Also:** [Documentation Hub](README.md) for audience-specific documentation
