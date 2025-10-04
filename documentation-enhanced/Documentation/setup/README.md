# TTA Setup Guide

## Overview

This guide covers setup instructions for all components of the TTA project.

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone --recurse-submodules https://github.com/theinterneti/TTA.git
   cd TTA
   ```

2. **Choose Development Focus**
   - [AI Development Setup](ai-dev.md)
   - [Content Development Setup](content-dev.md)
   - [Full Stack Setup](full-stack.md)

## Setup Components

1. **Environment Configuration**
   - [Environment Variables](environment/env-structure.md)
   - [Docker Configuration](docker/README.md)
   - [Development Tools](tools/README.md)

2. **Repository Structure**
   - [GitHub Setup](github/setup.md)
   - [Submodule Management](github/submodules.md)
   - [Branch Configuration](github/branches.md)

3. **Development Environments**
   - [VS Code Setup](ide/vscode.md)
   - [Docker Development](docker/development.md)
   - [GPU Configuration](environment/gpu.md)

## Directory Structure

```
setup/
├── README.md                 # This file
├── ai-dev.md                # AI development setup
├── content-dev.md           # Content development setup
├── full-stack.md            # Full stack setup
├── environment/             # Environment configuration
│   ├── env-structure.md     # Environment variables
│   └── gpu.md              # GPU setup
├── docker/                  # Docker configuration
│   ├── README.md           # Docker overview
│   └── development.md      # Development containers
├── github/                  # GitHub setup
│   ├── setup.md            # Repository setup
│   ├── submodules.md       # Submodule management
│   └── branches.md         # Branch configuration
├── ide/                     # IDE setup
│   └── vscode.md           # VS Code configuration
└── tools/                   # Development tools
    └── README.md           # Tools overview
```

## Port Allocation

| Service          | TTA.prototype | tta.dev | Root TTA |
|------------------|---------------|---------|----------|
| Neo4j Browser    | 7474         | 7475    | 7476     |
| Neo4j Bolt       | 7687         | 7688    | 7689     |
| MCP Server       | 8000         | 8001    | 8002     |

## Volume Strategy

See [docker/volumes.md](docker/volumes.md) for detailed volume configuration.
