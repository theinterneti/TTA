# Recovered TTA (Therapeutic Text Adventure) Project

## 🎯 Project Overview
This is the recovered and reorganized TTA (Therapeutic Text Adventure) project - a sophisticated AI-powered therapeutic platform that combines narrative storytelling with therapeutic interventions through an interactive text-based adventure system.

## 📁 Project Structure

```
recovered-tta-storytelling/
├── core/                           # Main orchestration system
│   ├── src/                       # Core source code (15 modules)
│   │   ├── agent_orchestration/   # AI agent coordination
│   │   ├── api_gateway/          # API routing and management
│   │   ├── components/           # Core system components
│   │   ├── living_worlds/        # Dynamic world simulation
│   │   ├── player_experience/    # Player interaction systems
│   │   └── main.py              # Application entry point
│   ├── tta/                      # TTA orchestration components
│   └── README.md                 # Core documentation
├── ai-components/                  # AI infrastructure
│   └── tta.dev/                  # Reusable AI components
│       ├── core/                 # AI core systems
│       ├── neo4j/               # Graph database integration
│       ├── src/                 # AI component source
│       └── docs/                # AI documentation
├── narrative-engine/               # Storytelling system
│   └── tta.prototype/            # Narrative components
│       ├── components/           # Story components
│       ├── core/                # Narrative core
│       ├── database/            # Story persistence
│       └── src/                 # Narrative engine source
├── web-interfaces/                 # Web UI components
│   ├── patient-interface/        # Patient-facing UI
│   ├── clinical-dashboard/       # Clinical staff interface
│   ├── developer-interface/      # Developer tools
│   ├── public-portal/           # Public website
│   ├── admin-interface/         # Administrative UI
│   └── shared/                  # Shared UI components
├── documentation/                  # All documentation
│   ├── Documentation/           # Setup and installation guides
│   ├── specifications/          # Technical specifications (.kiro)
│   ├── api/                    # API documentation
│   └── progress/               # Development progress reports
├── configuration/                  # Configuration files
│   ├── environment/            # Environment templates
│   ├── docker/                 # Docker configurations
│   ├── database/               # Database setup
│   └── config/                 # Application configs
├── testing/                       # Test suites
│   ├── tests/                  # Original test suite
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── validation/             # Validation scripts
├── tools/                         # Utilities and scripts
│   ├── scripts/                # Utility scripts
│   └── tta.sh                  # Main orchestration script
└── pyproject.toml                 # Python project configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js (for web interfaces)
- Docker (optional, for containerized deployment)
- Neo4j database (for AI components)

### 1. Environment Setup
```bash
cd /home/thein/recovered-tta-storytelling

# Copy environment template
cp configuration/environment/.env.development.example .env

# Edit .env with your configuration
nano .env
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -e .

# Install frontend dependencies (optional)
cd frontend && npm install && cd ..

# Install web interface dependencies (as needed)
cd web-interfaces/patient-interface && npm install && cd ../..
```

### 3. Database Setup
```bash
# Review database configuration
ls configuration/database/

# Set up databases as needed (Neo4j, etc.)
# Follow instructions in documentation/Documentation/setup/
```

### 4. Run Tests (Verify Migration)
```bash
cd testing
pytest tests/ -v
```

### 5. Start the System
```bash
# Check system status
./tools/tta.sh status

# Start all components
./tools/tta.sh start

# Or start specific components
./tools/tta.sh start tta.dev_neo4j tta.dev_llm
```

## 🏗️ Architecture Overview

### Core Components

1. **Orchestration System** (`core/`)
   - Main application entry point
   - Agent coordination and management
   - API gateway for service communication
   - Player experience management

2. **AI Infrastructure** (`ai-components/`)
   - Reusable AI components and agents
   - RAG (Retrieval-Augmented Generation) systems
   - Database integration (Neo4j)
   - MCP (Model Context Protocol) materials

3. **Narrative Engine** (`narrative-engine/`)
   - Story generation and management
   - Character development systems
   - World-building components
   - Therapeutic effectiveness tracking

4. **Web Interfaces** (`web-interfaces/`)
   - Patient-facing interface for therapy sessions
   - Clinical dashboard for healthcare providers
   - Developer interface for system management
   - Public portal for information and access

### Key Technologies
- **Backend:** Python 3.10+, FastAPI/Flask
- **Frontend:** React/Next.js (multiple interfaces)
- **Database:** Neo4j (graph), PostgreSQL (relational)
- **AI/ML:** LangChain, OpenAI API, custom AI agents
- **Containerization:** Docker, Docker Compose
- **Testing:** Pytest, comprehensive test suites

## 📚 Documentation

### Essential Reading
1. **Setup Guide:** `documentation/Documentation/setup/INSTALLATION.md`
2. **API Documentation:** `documentation/api/`
3. **Technical Specifications:** `documentation/specifications/`
4. **Migration Summary:** `MIGRATION_SUMMARY.md`

### Development Documentation
- **Core System:** `core/README.md`
- **AI Components:** `ai-components/tta.dev/README.md`
- **Narrative Engine:** `narrative-engine/tta.prototype/README.md`
- **Web Interfaces:** `web-interfaces/README.md`

## 🧪 Testing

The project includes comprehensive testing infrastructure:

```bash
# Run all tests
cd testing && pytest

# Run specific test categories
pytest tests/                    # Original test suite
pytest integration/             # Integration tests
pytest e2e/                     # End-to-end tests
pytest validation/              # Validation scripts
```

## 🔧 Development Workflow

### Starting Development
1. Set up your development environment (see Quick Start)
2. Review the technical specifications in `documentation/specifications/`
3. Examine the existing code structure in `core/src/`
4. Run tests to ensure everything is working
5. Start with small changes and test frequently

### Key Development Commands
```bash
# System orchestration
./tools/tta.sh status           # Check component status
./tools/tta.sh start            # Start all components
./tools/tta.sh stop             # Stop all components

# Development server (if applicable)
python core/main.py             # Start main application

# Testing
cd testing && pytest -v        # Run tests with verbose output
```

## 🏥 Therapeutic Focus

This system is designed for therapeutic applications:
- **Evidence-based:** Built on therapeutic frameworks
- **Safe:** Includes crisis detection and safety mechanisms
- **Effective:** Tracks therapeutic progress and outcomes
- **Accessible:** Multiple interfaces for different user types

## 🔒 Security & Privacy

- Environment variables for sensitive configuration
- Secure database connections
- Privacy protection mechanisms
- Clinical data handling compliance

## 📈 Project Status

This is a recovered project with significant prior development:
- ✅ Core orchestration system implemented
- ✅ AI infrastructure components developed
- ✅ Narrative engine with therapeutic focus
- ✅ Multiple web interfaces created
- ✅ Comprehensive testing infrastructure
- ✅ Documentation and specifications

## 🤝 Contributing

1. Review the existing codebase and documentation
2. Set up your development environment
3. Run tests to ensure everything works
4. Make changes in small, testable increments
5. Add tests for new functionality
6. Update documentation as needed

## 📞 Support

For questions about:
- **Setup:** Check `documentation/Documentation/setup/`
- **API Usage:** See `documentation/api/`
- **Architecture:** Review `documentation/specifications/`
- **Migration:** See `MIGRATION_SUMMARY.md`

## 📄 License

[License information would be found in the original project files]

---

**Note:** This project was recovered and reorganized from archived sources. All essential components have been preserved and organized for optimal development workflow. The migration preserved file timestamps, permissions, and internal structure while providing a clean, logical organization for continued development.
