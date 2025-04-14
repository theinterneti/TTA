# TTA Project Directory Structure

## Overview

This document provides an overview of the TTA project directory structure, including the main repository and its submodules.

## Root Repository Structure

```
TTA/
├── .github/                    # GitHub specific configurations
│   ├── workflows/             # CI/CD workflows
│   └── ISSUE_TEMPLATE/        # Issue templates
├── .vscode/                   # VS Code configurations
├── Documentation/             # Main documentation
│   ├── architecture/         # Architecture documentation
│   ├── ai-framework/         # AI framework documentation
│   ├── deployment/           # Deployment documentation
│   ├── development/          # Development documentation
│   ├── guides/               # Guides and examples
│   ├── setup/                # Setup documentation
│   └── therapeutic-content/  # Therapeutic content documentation
├── scripts/                   # Utility scripts
│   ├── setup.sh              # Main setup script
│   ├── setup_submodules.sh   # Submodule setup script
│   └── init_dev_environment.sh # Development environment setup
├── templates/                 # Template files for submodules
│   ├── tta.dev/              # Templates for tta.dev
│   └── TTA.prototype/        # Templates for TTA.prototype
├── config/                    # Configuration files
│   ├── docker/               # Docker configurations
│   └── neo4j/                # Neo4j configurations
├── tta.dev/                  # AI development framework (submodule)
├── TTA.prototype/            # Therapeutic content implementation (submodule)
├── .gitmodules               # Submodule configuration
├── .env.example              # Example environment variables
├── docker-compose.yml        # Base Docker Compose configuration
├── docker-compose.dev.yml    # Development Docker Compose configuration
├── docker-compose.prod.yml   # Production Docker Compose configuration
├── Dockerfile                # Multi-stage container definition
├── LICENSE                   # Project license
└── README.md                 # Project README
```

## tta.dev Repository Structure

```
tta.dev/
├── Documentation/           # AI framework documentation
│   ├── Architecture/       # Architecture documentation
│   ├── AI_COMPONENTS/      # AI components documentation
│   ├── Development/        # Development documentation
│   ├── Examples/           # Examples documentation
│   ├── Models/             # Models documentation
│   └── README.md           # Documentation README
├── src/                     # Source code
│   ├── agents/             # AI agents
│   ├── knowledge/          # Knowledge system
│   ├── models/             # AI models
│   └── tools/              # Tools
├── tests/                   # Tests
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── performance/        # Performance tests
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Container definition
└── README.md                # Repository README
```

## TTA.prototype Repository Structure

```
TTA.prototype/
├── Documentation/           # Content implementation documentation
│   ├── architecture/       # Architecture documentation
│   ├── content/            # Content documentation
│   ├── development/        # Development documentation
│   ├── examples/           # Examples documentation
│   ├── guides/             # Guides documentation
│   ├── integration/        # Integration documentation
│   ├── mcp/                # MCP documentation
│   ├── models/             # Models documentation
│   └── ux/                 # UX documentation
├── src/                     # Source code
│   ├── content/            # Content
│   ├── integration/        # Integration
│   ├── mcp/                # MCP
│   └── ux/                 # UX
├── tests/                   # Tests
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── performance/        # Performance tests
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Container definition
└── README.md                # Repository README
```

## Documentation Structure

```
Documentation/
├── architecture/            # Architecture documentation
│   └── README.md           # Architecture README
├── ai-framework/            # AI framework documentation
│   └── README.md           # AI framework README
├── deployment/              # Deployment documentation
│   └── README.md           # Deployment README
├── development/             # Development documentation
│   ├── CONTRIBUTING.md     # Contributing guidelines
│   └── README.md           # Development README
├── guides/                  # Guides and examples
│   └── README.md           # Guides README
├── setup/                   # Setup documentation
│   ├── DIRECTORY_STRUCTURE.md # This file
│   ├── GITHUB_SETUP.md     # GitHub setup
│   ├── INSTALLATION.md     # Installation guide
│   └── README.md           # Setup README
├── therapeutic-content/     # Therapeutic content documentation
│   └── README.md           # Therapeutic content README
└── index.md                 # Documentation index
```