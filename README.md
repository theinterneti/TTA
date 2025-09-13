# TTA Interactive Storytelling Platform

> **Interactive AI-Powered Storytelling Platform** - A focused recovery of the TTA project emphasizing narrative generation, player interaction, and AI integration.

## 🎯 Project Overview

This repository contains the recovered and refined TTA (Therapeutic Text Adventure) project, specifically focused on **interactive storytelling and AI integration** capabilities. The clinical/therapeutic components have been intentionally excluded to create a clean, focused platform for AI-powered narrative experiences.

### 🌟 Key Features

- **🤖 AI Integration**: Support for OpenRouter API, BYOK (Bring Your Own Key), and local model integration
- **📖 Dynamic Storytelling**: Advanced narrative generation and orchestration systems
- **�� Real-time Chat Interface**: WebSocket-based player interaction with AI characters
- **🌍 Living Worlds**: Persistent, evolving game worlds that respond to player choices
- **🎮 Player Experience**: Comprehensive player management and progress tracking
- **🔧 Modular Architecture**: Clean, maintainable codebase with clear separation of concerns

## 🏗️ Architecture

### Core Components

```
src/
├── living_worlds/          # Dynamic world state management
├── agent_orchestration/    # AI agent coordination and workflow
├── api_gateway/           # Main API routing and middleware
├── player_experience/     # Player interaction and management
├── components/
│   ├── narrative_arc_orchestrator/  # Story orchestration
│   ├── narrative_coherence/         # Story consistency validation
│   ├── adventure_experience/        # Adventure enhancement
│   └── gameplay_loop/              # Core gameplay mechanics
└── infrastructure/        # Scalability and deployment tools
```

### AI Integration

```
tta/
└── prod/
    ├── agents/           # AI agent implementations
    ├── models/          # Model configuration and providers
    └── knowledge/       # Knowledge graph management
```

### Specifications

```
kiro-specs/
├── narrative-arc-orchestration/    # Story system specs
├── player-experience-interface/    # Chat and interaction specs
├── ai-agent-orchestration/        # AI integration specs
└── tta-living-worlds/             # World management specs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend components)
- Redis (for caching and real-time features)
- Neo4j (for knowledge graphs and world state)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theinterneti/tta-storytelling-platform.git
   cd tta-storytelling-platform
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r config/pyproject.toml
   ```

3. **Set up environment variables:**
   ```bash
   cp config/.env.example .env
   # Edit .env with your configuration
   ```

4. **Install frontend dependencies:**
   ```bash
   cd src/player_experience/frontend
   npm install
   ```

### Configuration

Key environment variables to configure:

```env
# AI Model Configuration
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_API_BASE=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3-sonnet

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

REDIS_URL=redis://localhost:6379

# Application Settings
TTA_USE_MOCKS=false
TTA_DEVELOPMENT_MODE=true
```

### Running the Application

1. **Start the backend services:**
   ```bash
   python src/main.py
   ```

2. **Start the frontend (in another terminal):**
   ```bash
   cd src/player_experience/frontend
   npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 Documentation

- **[Recovery Summary](RECOVERY_SUMMARY.md)** - Details about the recovery process and what was preserved
- **[Kiro Specifications](kiro-specs/)** - Comprehensive system specifications
- **[API Documentation](src/player_experience/api/README.md)** - Backend API reference
- **[Frontend Guide](src/player_experience/frontend/README.md)** - Frontend development guide

## 🔧 Development

### Project Structure

This project follows a modular architecture with clear separation between:

- **Storytelling Engine** (`src/living_worlds/`, `src/components/narrative_*`)
- **AI Integration** (`tta/`, `src/agent_orchestration/`)
- **Player Interface** (`src/player_experience/`)
- **API Layer** (`src/api_gateway/`)
- **Infrastructure** (`src/infrastructure/`)

### Key Technologies

- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI/ML**: LangChain, OpenRouter API, Local model support
- **Databases**: Neo4j (graph), Redis (cache)
- **Infrastructure**: Docker, Kubernetes ready

### Testing

```bash
# Run backend tests
python -m pytest tests/

# Run frontend tests
cd src/player_experience/frontend
npm test
```

## 🎮 Features

### Interactive Storytelling
- Dynamic narrative generation based on player choices
- Character arc development and management
- Story coherence validation and consistency checking
- Multi-branching storylines with consequence tracking

### AI Integration
- **OpenRouter API** support for cloud-based models
- **BYOK (Bring Your Own Key)** functionality
- **Local model** integration for privacy-focused deployments
- Agent orchestration for complex narrative workflows

### Player Experience
- Real-time chat interface with AI characters
- WebSocket-based communication for instant responses
- Player progress tracking and achievement system
- Cross-story character persistence

### Living Worlds
- Persistent world state that evolves over time
- Player choice impact tracking
- Dynamic world events and consequences
- Redis-based caching for performance

## 🔄 Recovery Information

This project was recovered from a larger TTA system on **September 13, 2025**. The recovery process:

- **Selective Recovery**: Focused on storytelling and AI integration components
- **Excluded Components**: Clinical, therapeutic, and medical modules
- **Size Reduction**: From ~180GB original to ~1.6GB focused platform
- **Clean Architecture**: Reorganized for clarity and maintainability

See [RECOVERY_SUMMARY.md](RECOVERY_SUMMARY.md) for complete details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original TTA development team
- Recovery and refactoring completed September 2025
- Focus shifted from clinical applications to general interactive storytelling

---

**Built with ❤️ for interactive storytelling and AI-powered narratives**
