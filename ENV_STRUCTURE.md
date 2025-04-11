# TTA Environment Variable Structure

## Overview

The TTA project uses a hierarchical .env file structure that aligns with the separation of concerns:

TTA/.env: Infrastructure-level variables
├── NEO4J_ROOT_PASSWORD
├── DOCKER_HOST
└── COMPOSE_PROJECT_NAME=tta-root

tta.dev/.env: AI Development variables
├── NEO4J_PASSWORD
├── AI_MODEL_SETTINGS
├── DEVELOPMENT_TOOLS_CONFIG
└── COMPOSE_PROJECT_NAME=tta-dev

TTA.prototype/.env: Application variables
├── NEO4J_PASSWORD
├── TTA_CONTENT_SETTINGS
├── USER_EXPERIENCE_CONFIG
└── COMPOSE_PROJECT_NAME=tta-prototype

## Purpose and Scope

### tta.dev/.env
- AI development configuration
- Model integration settings
- Development tool configurations
- Testing and validation parameters
- Referenced by tta.dev/docker-compose.yml

### tta.dev/.env
- AI model configurations
- Machine learning parameters
- Development tool settings
- Technical integration variables
- Model deployment settings

### TTA.prototype/.env
- Narrative content settings
- Therapeutic parameters
- User experience variables
- Content management settings
- AI tool integration variables

### TTA/.env (root)
- Infrastructure configuration
- Cross-repository settings
- Development environment setup
- Resource allocation
## Variable Precedence

1. Repository-specific .env file
2. Root .env file
3. docker-compose.yml environment variables

## Best Practices

1. Keep AI development variables in tta.dev
2. Keep TTA-specific variables in TTA.prototype
3. Use root .env only for integration
4. Document all variables and their purpose
5. Consider cross-repository impacts when changing shared variables
