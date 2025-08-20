---
inclusion: always
---

# TTA - Therapeutic Text Adventure

## Product Overview

TTA (Therapeutic Text Adventure) is an AI-powered therapeutic platform that combines narrative storytelling with therapeutic interventions. The system uses interactive text-based adventures to deliver personalized therapeutic content and support.

## Architecture Principles

- **Component-based design**: Modular services with clear separation of concerns
- **Multi-repository structure**: Git submodules for different functional areas
- **Configuration-driven**: YAML-based configuration with environment overrides
- **Docker-first deployment**: Containerized services for consistency
- **Therapeutic focus**: All features must align with therapeutic goals and user safety

## Core Components & Responsibilities

### tta.dev (AI Infrastructure)
- Reusable AI components, agents, and RAG systems
- Database integration layers (Neo4j, Redis)
- MCP (Model Context Protocol) tools and materials
- Core therapeutic AI algorithms

### tta.prototype (Narrative Content)
- Worldbuilding and character systems
- Storytelling frameworks and narrative engines
- Therapeutic content templates and scenarios
- Interactive dialogue systems

### tta.prod (Production Systems)
- Deployment configurations and orchestration
- Production-ready service definitions
- Monitoring and logging infrastructure
- Security and compliance configurations

## Development Guidelines

### Therapeutic Safety Requirements
- All content must be reviewed for therapeutic appropriateness
- User privacy and data protection are paramount
- Implement safeguards against harmful or triggering content
- Maintain clear boundaries between AI assistance and professional therapy

### Code Conventions
- Use descriptive variable names that reflect therapeutic context
- Include comprehensive docstrings for all therapeutic functions
- Implement proper error handling with user-friendly messages
- Follow Python PEP 8 standards with therapeutic domain naming

### Component Integration
- Components must declare dependencies explicitly
- Use configuration-driven service discovery
- Implement health checks for all services
- Maintain backward compatibility across component updates

## Key Features & Implementation Notes

- **AI-driven therapeutic content**: Use ethical AI practices with bias monitoring
- **Interactive narratives**: Ensure accessibility and inclusive design
- **Neo4j knowledge graphs**: Model therapeutic relationships and progress
- **Docker orchestration**: Use `./tta.sh` for consistent service management
- **Carbon tracking**: Monitor and optimize AI model energy consumption

## Quality Standards

- All therapeutic content requires clinical review
- Maintain 80%+ test coverage for critical therapeutic paths
- Performance: Response times under 2 seconds for user interactions
- Accessibility: WCAG 2.1 AA compliance for all user interfaces
- Security: Regular vulnerability assessments and updates