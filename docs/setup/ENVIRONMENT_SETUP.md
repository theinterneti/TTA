# TTA Environment Configuration Guide

## 🔧 Environment File Structure

The TTA project uses a structured approach to environment configuration that supports different deployment scenarios while maintaining security best practices.

### File Structure Overview

```
├── .env.example              # Main template (COMMITTED)
├── .env                      # Local development (IGNORED)
├── .env.local.example        # Personal overrides template (COMMITTED)
├── .env.local                # Personal overrides (IGNORED)
├── .env.production.example   # Production template (COMMITTED)
├── .env.production           # Production config (IGNORED)
└── .env.staging.example      # Staging template (COMMITTED)
```

## 🚀 Quick Setup

### 1. Initial Setup

```bash
# Copy the main template
cp .env.example .env

# Copy personal overrides template (optional)
cp .env.local.example .env.local
```

### 2. Configure Your Environment

Edit `.env` and set your actual values:

```bash
# Required: Get a free OpenRouter API key
OPENROUTER_API_KEY=your_actual_openrouter_key_here

# Optional: Add other API keys as needed
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Personal Customization (Optional)

Use `.env.local` for personal development preferences:

```bash
# Your personal API keys
OPENROUTER_API_KEY=your_personal_key_here

# Your preferred log levels
LOG_LEVEL=DEBUG
API_LOG_LEVEL=DEBUG

# Enable/disable features for your testing
FEATURE_LOCAL_MODELS=true
```

## 📋 Environment File Descriptions

### `.env.example` (Template)
- **Purpose**: Main configuration template
- **Status**: Committed to version control
- **Contains**: All available configuration options with placeholder values
- **Usage**: Copy to `.env` and customize

### `.env` (Local Development)
- **Purpose**: Your local development configuration
- **Status**: Ignored by git (contains secrets)
- **Contains**: Actual values for local development
- **Usage**: Daily development work

### `.env.local.example` (Personal Template)
- **Purpose**: Template for personal development overrides
- **Status**: Committed to version control
- **Contains**: Examples of personal customizations
- **Usage**: Copy to `.env.local` for personal preferences

### `.env.local` (Personal Overrides)
- **Purpose**: Personal development preferences and API keys
- **Status**: Ignored by git
- **Contains**: Your personal API keys and preferences
- **Usage**: Override defaults without affecting team settings

### `.env.production.example` (Production Template)
- **Purpose**: Production deployment template
- **Status**: Committed to version control
- **Contains**: Production-ready configuration template
- **Usage**: Copy to `.env.production` for production deployment

## 🔑 Required API Keys

### OpenRouter (Recommended)
- **Purpose**: Access to 100+ AI models with free tier
- **Get Key**: https://openrouter.ai
- **Free Tier**: Yes, includes many models
- **Variable**: `OPENROUTER_API_KEY`
- **Free Models Filter**: Configure with `OPENROUTER_SHOW_FREE_ONLY`, `OPENROUTER_PREFER_FREE_MODELS`, `OPENROUTER_MAX_COST_PER_TOKEN`

### OpenAI (Optional)
- **Purpose**: Access to GPT models
- **Get Key**: https://platform.openai.com/api-keys
- **Free Tier**: Limited credits for new accounts
- **Variable**: `OPENAI_API_KEY`

### Anthropic (Optional)
- **Purpose**: Access to Claude models
- **Get Key**: https://console.anthropic.com/
- **Free Tier**: Limited credits for new accounts
- **Variable**: `ANTHROPIC_API_KEY`

## 🛡️ Security Best Practices

### ✅ Do's
- ✅ Use `.env.example` files as templates
- ✅ Keep actual secrets in `.env` and `.env.local` (ignored files)
- ✅ Use strong, unique passwords for each service
- ✅ Rotate API keys regularly
- ✅ Use environment-specific configurations
- ✅ Generate secure JWT secrets: `openssl rand -base64 64`
- ✅ Generate encryption keys: `openssl rand -base64 32`

### ❌ Don'ts
- ❌ Never commit `.env`, `.env.local`, or `.env.production` files
- ❌ Don't use default passwords in production
- ❌ Don't share API keys in chat or email
- ❌ Don't use development keys in production
- ❌ Don't store secrets in code or documentation

## 🔧 Configuration Categories

### Database Configuration
```bash
# PostgreSQL
POSTGRES_DB=tta_db
POSTGRES_USER=tta_user
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=your_neo4j_password
```

### AI Model Configuration
```bash
# Model Management
FEATURE_MODEL_MANAGEMENT=true
FEATURE_LOCAL_MODELS=false
FEATURE_CLOUD_MODELS=true

# API Keys
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# OpenRouter Free Models Filter
OPENROUTER_SHOW_FREE_ONLY=false        # Show only free models
OPENROUTER_PREFER_FREE_MODELS=true     # Sort free models first
OPENROUTER_MAX_COST_PER_TOKEN=0.001    # Maximum cost threshold
```

### Security Configuration
```bash
# JWT Settings
JWT_SECRET_KEY=your_secure_jwt_secret_64_chars_minimum
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encryption
ENCRYPTION_KEY=your_32_byte_base64_key
FERNET_KEY=your_32_byte_base64_key
```

### Feature Flags
```bash
# Core Features
FEATURE_AI_NARRATIVE=true
FEATURE_LIVING_WORLDS=true
FEATURE_CRISIS_SUPPORT=true
FEATURE_REAL_TIME_MONITORING=true

# Advanced Features
FEATURE_PREDICTIVE_ANALYTICS=false
FEATURE_EHR_INTEGRATION=false
```

## 🌍 Environment-Specific Setup

### Development Environment
```bash
# Copy and customize
cp .env.example .env
cp .env.local.example .env.local

# Set development-friendly values
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_DEBUG=true
MOCK_EMAIL_SERVICE=true
```

### Staging Environment
```bash
# Use staging template
cp .env.staging.example .env.staging

# Configure for staging
ENVIRONMENT=staging
LOG_LEVEL=INFO
API_DEBUG=false
```

### Production Environment
```bash
# Use production template
cp .env.production.example .env.production

# Configure for production (use secret management!)
ENVIRONMENT=production
LOG_LEVEL=WARNING
API_DEBUG=false
```

## 🔍 Validation and Testing

### Environment Validation Script
```bash
# Check if required variables are set
python scripts/validate_environment.py

# Test database connections
python scripts/test_connections.py

# Validate API keys
python scripts/test_api_keys.py
```

### Common Issues and Solutions

#### Missing API Keys
```bash
# Error: No suitable model found
# Solution: Set OPENROUTER_API_KEY in .env
OPENROUTER_API_KEY=your_actual_key_here
```

#### Database Connection Issues
```bash
# Error: Connection refused
# Solution: Check database configuration and ensure services are running
docker-compose up -d redis neo4j postgres
```

#### CORS Issues
```bash
# Error: CORS policy blocked
# Solution: Update CORS origins in .env
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 📚 Integration with TTA Components

### Model Management System
The environment configuration integrates seamlessly with the new model management system:

```bash
# Enable model management
FEATURE_MODEL_MANAGEMENT=true

# Configure providers
OPENROUTER_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234

# Set preferences
THERAPEUTIC_SAFETY_THRESHOLD=7.0
```

### Docker Integration
Environment variables are automatically loaded by Docker Compose:

```bash
# Docker will use .env file automatically
docker-compose up -d

# For specific environments
docker-compose --env-file .env.staging up -d
```

## 🆘 Troubleshooting

### Environment Not Loading
1. Check file names (no typos)
2. Verify file permissions
3. Ensure no trailing spaces in variable names
4. Check for syntax errors in values

### API Keys Not Working
1. Verify key format and validity
2. Check API key permissions
3. Ensure no extra characters or spaces
4. Test keys with simple API calls

### Database Connection Issues
1. Verify database services are running
2. Check connection strings and credentials
3. Ensure network connectivity
4. Review firewall settings

## 📞 Getting Help

If you encounter issues with environment configuration:

1. Check this documentation first
2. Verify your `.env` file against `.env.example`
3. Test individual components
4. Check the logs for specific error messages
5. Consult the main TTA documentation

## 🔄 Migration from Old Structure

If you're migrating from the old environment structure:

1. **Backup** your current `.env` files
2. **Copy** `.env.example` to `.env`
3. **Migrate** your settings from old files to new structure
4. **Test** the configuration thoroughly
5. **Remove** old environment files once confirmed working

The new structure provides better organization, security, and maintainability for the TTA platform.
