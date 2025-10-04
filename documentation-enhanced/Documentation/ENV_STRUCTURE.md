# TTA Environment Variable Structure

This document explains the hierarchical .env file structure used in the TTA project.

## Overview

The TTA project uses a hierarchical .env file structure that aligns with the development workflow:

1. **TTA.prototype/.env**: Development environment variables (active development)
2. **TTA.dev/.env**: Stable environment variables (validated implementations)
3. **TTA/.env**: Root-level connection variables (infrastructure)

## Workflow

- New changes and experiments start in TTA.prototype
- After validation and testing, changes bubble up to TTA.dev
- The root TTA level provides the infrastructure to connect both repositories

## File Purposes

### TTA.prototype/.env
- Contains all development variables
- Most actively modified
- Used for experimentation and new features
- Referenced by TTA.prototype/docker-compose.yml

### TTA.dev/.env
- Contains stable, validated variables
- Updated only after changes in TTA.prototype are tested and approved
- More stable, less frequently changed
- Referenced by TTA.dev/docker-compose.yml

### TTA/.env (root level)
- Contains only essential connection variables needed for the meta-repository
- Primarily focused on Docker and devcontainer configuration
- Rarely changed
- Used by the root docker-compose.yml

## Variable Precedence

When multiple .env files are specified in docker-compose.yml, variables are loaded in the order they appear. Later variables override earlier ones. The current precedence order is:

1. Repository-specific .env file (e.g., TTA.prototype/.env)
2. Root .env file (TTA/.env)
3. Environment variables defined directly in docker-compose.yml

This allows for repository-specific overrides while maintaining common infrastructure variables.

## Updating Environment Variables

### For Development (TTA.prototype)
1. Make changes to TTA.prototype/.env
2. Test thoroughly
3. Document changes

### For Stable Implementation (TTA.dev)
1. Only after validation in TTA.prototype
2. Copy validated variables from TTA.prototype/.env to TTA.dev/.env
3. Document the migration

### For Infrastructure (TTA/.env)
1. Only update when changing core infrastructure
2. Keep this file minimal
3. Document any changes that might affect both repositories

## Best Practices

1. Keep sensitive information (tokens, passwords) consistent across environments
2. Document all non-obvious environment variables
3. When adding new variables, consider which level they belong to
4. Use comments to explain the purpose of variables
5. Regularly review and clean up unused variables
