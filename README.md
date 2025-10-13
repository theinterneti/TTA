# TTA - Therapeutic Text Adventure

<div align="center">

[![Tests](https://github.com/theinterneti/TTA/workflows/Tests/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/tests.yml)
[![Code Quality](https://github.com/theinterneti/TTA/workflows/Code%20Quality/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/code-quality.yml)
[![Security Scan](https://github.com/theinterneti/TTA/workflows/Security%20Scan/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/security-scan.yml)
[![E2E Tests](https://github.com/theinterneti/TTA/workflows/E2E%20Tests/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/e2e-tests.yml)
[![Mutation Testing](https://github.com/theinterneti/TTA/workflows/Mutation%20Testing/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/mutation-testing.yml)

**AI-powered therapeutic text adventure platform combining evidence-based mental health support with engaging interactive storytelling**

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Repository Structure](#-repository-structure)
- [Development](#-development)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

---

## 🎯 Overview

The Therapeutic Text Adventure (TTA) is an innovative platform that merges the engaging nature of interactive storytelling with evidence-based therapeutic techniques. By leveraging advanced AI models and graph-based narrative systems, TTA creates personalized, adaptive therapeutic experiences that help users explore mental health concepts in a safe, engaging environment.

**What makes TTA unique:**

- **Evidence-Based Approach**: Integrates CBT, DBT, and other therapeutic frameworks
- **Adaptive Narratives**: Stories that respond to user choices and emotional states
- **Safe Exploration**: Therapeutic safety systems ensure appropriate content
- **Engaging Experience**: Entertainment-first design that doesn't feel clinical
- **Privacy-Focused**: HIPAA-compliant data handling and user privacy protection

**Target Users:**
- Individuals seeking mental health support through interactive experiences
- Therapists looking for supplementary tools for client engagement
- Researchers studying AI-assisted therapeutic interventions
- Developers building therapeutic AI applications

---

## ✨ Key Features

### 🎭 **Interactive Storytelling**
- **Dynamic Narratives**: AI-generated stories that adapt to user choices
- **Character Development**: Deep, evolving characters with therapeutic arcs
- **Multiple Worlds**: Diverse therapeutic scenarios and settings
- **Branching Paths**: Meaningful choices that impact story progression

### 🧠 **Therapeutic Integration**
- **Evidence-Based Frameworks**: CBT, DBT, ACT, and mindfulness techniques
- **Emotional Safety**: Real-time content validation and safety checks
- **Progress Tracking**: Monitor therapeutic goals and achievements
- **Personalization**: Adaptive difficulty and content based on user needs

### 🤖 **AI-Powered Systems**
- **Multi-Agent Orchestration**: Coordinated AI agents for narrative, therapy, and safety
- **LangGraph Integration**: Advanced workflow management for complex interactions
- **Model Flexibility**: Support for multiple LLM providers (OpenRouter, local models)
- **RAG System**: Context-aware responses using knowledge management

### 🔒 **Security & Privacy**
- **HIPAA Compliance**: Secure handling of therapeutic data
- **Data Encryption**: At-rest and in-transit encryption
- **Access Control**: Role-based permissions and authentication
- **Audit Logging**: Comprehensive activity tracking

### 📊 **Monitoring & Analytics**
- **Real-Time Dashboards**: Grafana-based monitoring and visualization
- **Performance Metrics**: System health and response time tracking
- **Therapeutic Metrics**: User engagement and progress analytics
- **Developer Tools**: Comprehensive debugging and diagnostic interfaces

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** for frontend development
- **Docker** and Docker Compose for services
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/theinterneti/TTA.git
   cd TTA
   ```

2. **Set up environment**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Get a free OpenRouter API key at https://openrouter.ai
   # Edit .env and add your API key
   nano .env  # or use your preferred editor
   ```

3. **Install dependencies**
   ```bash
   # Python dependencies
   uv sync --all-extras --dev

   # Pre-commit hooks
   pre-commit install
   ```

4. **Start services**
   ```bash
   # Start Neo4j and Redis
   docker-compose up -d neo4j redis

   # Verify services are running
   docker-compose ps
   ```

5. **Run the application**
   ```bash
   # Start the API server
   uv run python src/player_experience/api/main.py

   # In another terminal, start the frontend
   cd src/player_experience/frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

### Verify Installation

```bash
# Run validation script
python scripts/validate_environment.py

# Run quick tests
uv run pytest -q

# Check system health
curl http://localhost:8000/health
```

---

## 🏗️ Architecture

TTA uses a microservices architecture with the following key components:

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              User Interface & Experience Layer               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  API Gateway (FastAPI)                       │
│         Authentication, Rate Limiting, Routing              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼─────────────┐
│   Player     │ │ Agent   │ │  Therapeutic   │
│  Experience  │ │Orchestr.│ │     Safety     │
│   Service    │ │ Service │ │    Service     │
└───────┬──────┘ └──┬──────┘ └──┬─────────────┘
        │           │            │
        └───────────┼────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼──────┐ ┌─▼────────┐ ┌▼──────────┐
│   Neo4j      │ │  Redis   │ │ OpenRouter│
│  (Graph DB)  │ │ (Cache)  │ │   (LLM)   │
└──────────────┘ └──────────┘ └───────────┘
```

**Core Services:**

- **Player Experience**: User management, session handling, progress tracking
- **Agent Orchestration**: Multi-agent coordination using LangGraph
- **Therapeutic Safety**: Content validation, emotional safety checks
- **Narrative Engine**: Story generation, character development, world management
- **Gameplay Loop**: Turn-based interaction, choice processing, consequence system

**Data Layer:**

- **Neo4j**: Graph database for narrative structures, relationships, and world state
- **Redis**: Session management, caching, real-time data
- **PostgreSQL** (optional): User data, analytics, audit logs

**External Services:**

- **OpenRouter**: LLM API gateway for multiple model providers
- **Prometheus + Grafana**: Monitoring and observability
- **GitHub Actions**: CI/CD pipeline

---

## 📁 Repository Structure

```
TTA/
├── .github/                    # GitHub configuration
│   ├── workflows/             # CI/CD workflows
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── dependabot.yml         # Dependency updates
├── src/                       # Source code
│   ├── agent_orchestration/   # Multi-agent coordination
│   ├── api_gateway/           # API gateway service
│   ├── components/            # Shared components
│   │   ├── gameplay_loop/     # Core gameplay mechanics
│   │   ├── narrative_coherence/ # Story consistency
│   │   └── therapeutic_safety/ # Safety systems
│   └── player_experience/     # Player-facing services
│       ├── api/               # FastAPI backend
│       ├── frontend/          # React frontend
│       ├── database/          # Database schemas
│       └── services/          # Business logic
├── tests/                     # Test suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   └── comprehensive_battery/ # Comprehensive test battery
├── Documentation/             # Project documentation
│   ├── architecture/          # Architecture docs
│   ├── api/                   # API documentation
│   ├── development/           # Development guides
│   └── therapeutic-content/   # Therapeutic frameworks
├── config/                    # Configuration files
├── scripts/                   # Utility scripts
├── monitoring/                # Monitoring configuration
│   ├── grafana/              # Grafana dashboards
│   └── prometheus/           # Prometheus config
├── docker-compose.yml         # Docker services
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

---

## 💻 Development

### Development Workflow

TTA uses a **three-tier branching strategy**: `development` → `staging` → `main`

See [Branching Strategy Documentation](docs/development/BRANCHING_STRATEGY.md) for complete details.

1. **Create a feature branch from development**
   ```bash
   # Ensure you're on development and up to date
   git checkout development
   git pull origin development

   # Use the helper script (recommended)
   ./scripts/create-feature-branch.sh <domain> <description>
   # Example: ./scripts/create-feature-branch.sh game player-inventory

   # Or create manually
   git checkout -b feature/<domain>-<description>
   ```

2. **Make changes and test**
   ```bash
   # Run code quality checks
   uv run ruff check src/ tests/
   uv run black --check src/ tests/
   uv run mypy src/

   # Run tests
   uv run pytest -q

   # Validate quality gates before pushing
   ./scripts/validate-quality-gates.sh development
   ```

3. **Commit with conventional commits**
   ```bash
   git commit -m "feat(component): add new feature"
   # Types: feat, fix, docs, test, refactor, perf, ci, chore
   ```

4. **Push and create PR targeting development**
   ```bash
   git push origin feature/<domain>-<description>
   gh pr create --base development --fill
   ```

**Branch Flow:**
- Feature branches → `development` (auto-merge when tests pass)
- `development` → `staging` (auto-merge when tests pass)
- `staging` → `main` (manual approval required)

### Code Quality Standards

- **Formatting**: Black (line length: 88)
- **Linting**: Ruff (replaces flake8, pylint)
- **Type Checking**: mypy with strict mode
- **Security**: Bandit, safety, pip-audit
- **Pre-commit Hooks**: Automatic checks before commit

### Environment Configuration

```bash
# Development environment
cp .env.example .env

# Staging environment
cp .env.staging.example .env.staging

# Production environment
cp .env.production.example .env.production
```

**Required Environment Variables:**
- `OPENROUTER_API_KEY`: OpenRouter API key for LLM access
- `NEO4J_URI`: Neo4j connection string
- `NEO4J_AUTH`: Neo4j authentication (user/password)
- `REDIS_URL`: Redis connection string

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for complete configuration guide.

### Docker Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d neo4j redis

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Orchestration Commands

```bash
# Start all components
./tta.sh start

# Start specific components
./tta.sh start agent_orchestration player_experience

# Stop all components
./tta.sh stop

# Get status
./tta.sh status

# View logs
./tta.sh logs agent_orchestration
```

---

## 🧪 Testing

TTA includes comprehensive testing infrastructure with multiple layers of validation.

### Quick Testing

```bash
# Run all tests
uv run pytest

# Run specific test types
uv run pytest tests/unit/              # Unit tests
uv run pytest tests/integration/       # Integration tests
uv run pytest tests/e2e/              # End-to-end tests

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run tests with specific markers
uv run pytest -m "not slow"           # Skip slow tests
uv run pytest -m "redis or neo4j"     # Only database tests
```

### Comprehensive Test Battery

The TTA Comprehensive Test Battery provides robust, multi-dimensional testing:

```bash
# Quick validation (standard tests)
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --categories standard

# Full test battery (all categories)
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --all --detailed-report --metrics

# Force mock mode (no external dependencies)
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --all --force-mock

# Specific categories
python tests/comprehensive_battery/run_comprehensive_tests.py \
  --categories standard,adversarial,load_stress
```

**Test Categories:**

| Category | Description | Duration |
|----------|-------------|----------|
| **Standard** | Normal user interactions and story flows | ~5 min |
| **Adversarial** | Security vulnerabilities and edge cases | ~10 min |
| **Load/Stress** | Performance under concurrent load | ~15 min |
| **Data Pipeline** | End-to-end data flow validation | ~20 min |
| **Dashboard** | Real-time monitoring functionality | ~10 min |

**Features:**
- ✅ Automatic mock fallback when services unavailable
- ✅ CI/CD integration with GitHub Actions
- ✅ Real-time monitoring dashboard
- ✅ Comprehensive reporting (JSON, HTML, CSV, TXT)
- ✅ Parallel execution support

### Mutation Testing

TTA uses mutation testing to ensure test quality for critical Model Management services:

```bash
# Run mutation tests for all services
./scripts/run-mutation-tests.sh

# Run for specific service
./scripts/run-mutation-tests.sh model-selector
./scripts/run-mutation-tests.sh fallback-handler
./scripts/run-mutation-tests.sh performance-monitor

# Set custom threshold
./scripts/run-mutation-tests.sh -t 90 --all
```

**Current Mutation Scores:**
- **ModelSelector**: 100% (534/534 mutations killed) 🏆
- **FallbackHandler**: 100% (352/352 mutations killed) 🏆
- **PerformanceMonitor**: 100% (519/519 mutations killed) 🏆

**Automated Testing:**
- Runs weekly (Sunday 2 AM UTC)
- Fails if mutation score drops below 85%
- Reports available as GitHub Actions artifacts

📖 See [Mutation Testing CI/CD Guide](docs/testing/MUTATION_TESTING_CICD_GUIDE.md) for details

### CI/CD Testing

Tests run automatically on:
- **Pull Requests**: Unit, integration, code quality, security scans
- **Main Branch**: Full test battery, E2E tests, performance tests
- **Scheduled**: Daily comprehensive test battery at 2 AM UTC

View test results: [GitHub Actions](https://github.com/theinterneti/TTA/actions)

---

## 📚 Documentation

📖 **Full documentation is available at [theinterneti.github.io/TTA](https://theinterneti.github.io/TTA)**

### Core Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines and development workflow
- **[SECURITY.md](SECURITY.md)**: Security policy and vulnerability reporting
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**: Community guidelines

### Technical Documentation

- **[Architecture Documentation](Documentation/architecture/)**: System design and components
  - [System Architecture Diagram](Documentation/architecture/system-architecture-diagram.md)
  - [Component Interactions](Documentation/architecture/component-interaction-diagram.md)
  - [Data Flow](Documentation/architecture/data-flow-diagram.md)
  - [CI/CD & Deployment](Documentation/architecture/cicd-deployment-diagram.md)
- **[API Documentation](Documentation/api/)**: API reference and examples
- **[Development Guides](Documentation/development/)**: Setup and development guides
- **[Testing Framework](docs/testing-framework.md)**: Testing strategies and tools

### Therapeutic Content

- **[Therapeutic Frameworks](Documentation/therapeutic-content/)**: CBT, DBT, ACT integration
- **[Content Guidelines](Documentation/therapeutic-content/guidelines.md)**: Content creation standards
- **[Safety Protocols](Documentation/therapeutic-content/safety.md)**: Therapeutic safety measures

### Additional Resources

- **[Environment Setup](ENVIRONMENT_SETUP.md)**: Detailed environment configuration
- **[Docker Setup](Documentation/docker/docker_setup_guide.md)**: Docker and DevContainer setup
- **[Troubleshooting](Documentation/docker/devcontainer_troubleshooting_guide.md)**: Common issues and solutions

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: [Create an issue](https://github.com/theinterneti/TTA/issues/new?template=bug_report.yml)
- ✨ **Suggest Features**: [Request a feature](https://github.com/theinterneti/TTA/issues/new?template=feature_request.yml)
- 📝 **Improve Documentation**: Fix typos, clarify instructions, add examples
- 🔧 **Submit Code**: Fix bugs, implement features, improve performance
- 🧪 **Write Tests**: Increase test coverage, add edge cases
- 🎨 **Design**: Improve UI/UX, create graphics, design workflows

### Getting Started

1. **Read the guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Find an issue**: Look for issues labeled `good first issue`
3. **Fork and clone**: Create your own fork of the repository
4. **Create a branch**: `git checkout -b feat/your-feature`
5. **Make changes**: Follow code standards and write tests
6. **Submit PR**: Create a pull request with clear description

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## 🔒 Security

Security is a top priority for TTA, especially given the therapeutic nature of the application.

### Security Features

- ✅ **Secret Scanning**: Automatic detection of committed secrets
- ✅ **Dependabot**: Automated dependency vulnerability updates
- ✅ **Branch Protection**: Required reviews and status checks
- ✅ **Security Scanning**: Semgrep, CodeQL, Trivy, Bandit
- ✅ **SBOM Generation**: Software Bill of Materials for transparency

### Reporting Vulnerabilities

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **theinternetisbig@gmail.com**

Include:
- Type of vulnerability
- Affected components
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

See [SECURITY.md](SECURITY.md) for complete security policy.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenRouter**: For providing access to multiple LLM providers
- **Neo4j**: For the powerful graph database platform
- **LangGraph**: For the agent orchestration framework
- **FastAPI**: For the high-performance API framework
- **React**: For the frontend framework
- **All Contributors**: Thank you for your contributions!

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/theinterneti/TTA/issues)
- **Discussions**: [GitHub Discussions](https://github.com/theinterneti/TTA/discussions) (coming soon)
- **Email**: theinternetisbig@gmail.com

---

<div align="center">

**Made with ❤️ for mental health and well-being**

[⬆ Back to Top](#tta---therapeutic-text-adventure)

</div>
