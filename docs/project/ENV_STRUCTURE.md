# TTA Environment Configuration Structure

This document explains the consolidated environment configuration structure used in the TTA project.

## 🔄 **UPDATED STRUCTURE** (2024)

The TTA project has been reorganized to use a unified, security-focused environment configuration structure that follows modern development best practices.

## Overview

The new structure provides:
- **Security**: Sensitive values are never committed to version control
- **Flexibility**: Support for multiple deployment environments
- **Maintainability**: Clear separation between templates and actual configurations
- **Developer Experience**: Easy setup with comprehensive documentation

## File Structure

```
├── .env.example              # Main template (COMMITTED)
├── .env                      # Local development (IGNORED)
├── .env.local.example        # Personal overrides template (COMMITTED)
├── .env.local                # Personal overrides (IGNORED)
├── .env.staging.example      # Staging template (COMMITTED)
├── .env.staging              # Staging config (IGNORED)
├── .env.production.example   # Production template (COMMITTED)
├── .env.production           # Production config (IGNORED)
└── src/player_experience/frontend/
    ├── .env.example          # Frontend template (COMMITTED)
    └── .env                  # Frontend config (IGNORED)
```

## File Purposes

### `.env.example` (Main Template)
- **Status**: Committed to version control
- **Purpose**: Comprehensive template with all available configuration options
- **Contains**: Placeholder values and documentation
- **Usage**: Copy to `.env` and customize for local development

### `.env` (Local Development)
- **Status**: Ignored by git (contains secrets)
- **Purpose**: Your actual local development configuration
- **Contains**: Real API keys, passwords, and local preferences
- **Usage**: Daily development work

### `.env.local.example` (Personal Template)
- **Status**: Committed to version control
- **Purpose**: Template for personal development overrides
- **Contains**: Examples of personal customizations
- **Usage**: Copy to `.env.local` for personal preferences

### `.env.local` (Personal Overrides)
- **Status**: Ignored by git
- **Purpose**: Personal API keys and development preferences
- **Contains**: Your personal settings that override defaults
- **Usage**: Personal customization without affecting team settings

### Environment-Specific Templates
- **`.env.staging.example`**: Template for staging deployment
- **`.env.production.example`**: Template for production deployment
- **Status**: Committed as templates, actual files are ignored

## Quick Setup

```bash
# 1. Copy the main template
cp .env.example .env

# 2. Edit .env and set your actual values
# Required: Get a free OpenRouter API key at https://openrouter.ai
OPENROUTER_API_KEY=your_actual_key_here

# 3. Optional: Set up personal overrides
cp .env.local.example .env.local
```

## Security Features

### ✅ What's Protected
- All actual environment files (`.env`, `.env.local`, etc.) are in `.gitignore`
- API keys and passwords are never committed
- Templates use placeholder values only
- Clear documentation on security best practices

### ✅ What's Committed
- Template files (`.env.example`, `.env.local.example`, etc.)
- Documentation and setup instructions
- Configuration structure and examples

## Environment Loading Order

The system loads environment variables in this order (later values override earlier ones):

1. **System environment variables**
2. **`.env`** (main local configuration)
3. **`.env.local`** (personal overrides)
4. **Application-specific overrides**

## Configuration Categories

### Database Configuration
- PostgreSQL, Redis, Neo4j connection settings
- Connection pooling and performance tuning
- Backup and maintenance settings

### AI Model Configuration
- OpenRouter, OpenAI, Anthropic API keys
- Model selection and performance settings
- Local model hosting configuration (Ollama, LM Studio)

### Security Configuration
- JWT secrets and encryption keys
- CORS settings and rate limiting
- HIPAA compliance settings

### Feature Flags
- Core therapeutic features
- Model management capabilities
- Advanced analytics and integrations

### Monitoring and Logging
- Log levels and retention
- Sentry error tracking
- Grafana and Prometheus configuration

## Migration from Old Structure

If you're migrating from the previous structure:

1. **Backup** your current `.env` files
2. **Run validation**: `python scripts/validate_environment.py`
3. **Copy template**: `cp .env.example .env`
4. **Migrate settings** from your old files to the new structure
5. **Test thoroughly** before removing old files

## Validation and Testing

Use the provided validation script to check your configuration:

```bash
# Validate your environment setup
python scripts/validate_environment.py

# Test database connections
python scripts/test_connections.py
```

## Best Practices

### ✅ Do's
- Use `.env.example` files as templates
- Keep actual secrets in ignored files (`.env`, `.env.local`)
- Use strong, unique passwords for each service
- Rotate API keys regularly
- Generate secure JWT secrets: `openssl rand -base64 64`

### ❌ Don'ts
- Never commit `.env`, `.env.local`, or `.env.production` files
- Don't use default passwords in production
- Don't share API keys in chat or documentation
- Don't use development keys in production

## Integration with TTA Components

The environment configuration integrates seamlessly with:

- **Model Management System**: Automatic provider configuration
- **Docker Compose**: Environment variables loaded automatically
- **Frontend Applications**: React environment variables
- **Monitoring Stack**: Grafana, Prometheus, Sentry integration
- **Database Services**: PostgreSQL, Redis, Neo4j configuration

## Getting Help

For detailed setup instructions, see: [ENVIRONMENT_SETUP.md](../ENVIRONMENT_SETUP.md)

For troubleshooting:
1. Run the validation script: `python scripts/validate_environment.py`
2. Check the setup documentation
3. Verify your `.env` file against `.env.example`
4. Test individual components

## Legacy Structure (Deprecated)

The previous hierarchical structure with TTA.prototype/.env and TTA.dev/.env has been consolidated into this unified approach for better security and maintainability.
