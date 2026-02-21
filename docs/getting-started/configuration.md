# Configuration

This guide covers all configuration options for the Therapeutic Text Adventure (TTA) platform.

## Environment Files

TTA uses environment files (`.env`) for configuration. Different environments use different files:

| Environment | File | Purpose |
|-------------|------|---------|
| **Development** | `.env` | Local development |
| **Staging** | `.env.staging` | Pre-production testing |
| **Production** | `.env.production` | Production deployment |
| **Testing** | `.env.test` | Automated testing |

### Creating Environment Files

```bash
# Development environment
cp .env.example .env

# Staging environment
cp .env.staging.example .env.staging

# Production environment
cp .env.production.example .env.production
```

!!! warning "Security"
    Never commit actual `.env` files to version control! Only commit `.env.example` templates.

## Core Configuration

### Environment Settings

```bash
# Environment type (development, staging, production)
ENVIRONMENT=development

# Node.js environment
NODE_ENV=development

# Python path (for imports)
PYTHONPATH=/app
```

### Database Configuration

#### PostgreSQL (Optional)

```bash
# Database name
POSTGRES_DB=tta_db

# Database user
POSTGRES_USER=tta_user

# Database password (use strong password in production)
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Full connection URL
DATABASE_URL=postgresql://tta_user:your_secure_postgres_password_here@localhost:5432/tta_db  # pragma: allowlist secret
```

#### Redis (Required)

```bash
# Redis connection URL (simple format)
REDIS_URL=redis://localhost:6379

# Or detailed configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here  # Optional
REDIS_DB=0
```

**Redis Usage:**

- Session management
- Caching
- Real-time data
- Agent coordination

#### Neo4j (Required)

```bash
# Neo4j connection URI
NEO4J_URI=bolt://localhost:7687
NEO4J_URL=bolt://localhost:7687  # Alternative

# Authentication
NEO4J_USER=neo4j
NEO4J_USERNAME=neo4j  # Alternative
NEO4J_PASSWORD=your_neo4j_password_here

# Database name (default: neo4j)
NEO4J_DATABASE=neo4j
```

**Neo4j Usage:**

- Narrative graph structures
- Character relationships
- World state management
- Story progression tracking

### AI Model Configuration

#### OpenRouter (Recommended)

```bash
# API key (get free key at https://openrouter.ai)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Model preferences
OPENROUTER_SHOW_FREE_ONLY=false
OPENROUTER_PREFER_FREE_MODELS=true
OPENROUTER_MAX_COST_PER_TOKEN=0.001

# OAuth configuration (for user authentication)
OPENROUTER_CLIENT_ID=your_openrouter_client_id_here
OPENROUTER_CLIENT_SECRET=your_openrouter_client_secret_here
OPENROUTER_REDIRECT_URI=http://localhost:8080/api/v1/openrouter/auth/oauth/callback
```

**Why OpenRouter?**

- Access to multiple LLM providers
- Free tier available
- Cost optimization
- Automatic fallback
- No vendor lock-in

#### OpenAI (Optional)

```bash
# API key
OPENAI_API_KEY=your_openai_api_key_here

# Model selection
OPENAI_MODEL=gpt-4o-mini

# Generation parameters
OPENAI_MAX_TOKENS=2048
OPENAI_TEMPERATURE=0.7
```

#### Anthropic (Optional)

```bash
# API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### Local Models (Optional)

```bash
# Ollama (local LLM server)
OLLAMA_BASE_URL=http://localhost:11434

# LM Studio (local LLM server)
LM_STUDIO_BASE_URL=http://localhost:1234
```

### Security Configuration

#### JWT (JSON Web Tokens)

```bash
# Secret key (minimum 32 characters)
# Generate with: openssl rand -base64 64
JWT_SECRET_KEY=your_jwt_secret_key_here_minimum_32_characters

# Algorithm
JWT_ALGORITHM=HS256

# Token expiration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Encryption

```bash
# Encryption key (32 bytes, base64 encoded)
# Generate with: openssl rand -base64 32
ENCRYPTION_KEY=your_encryption_key_here_32_bytes_base64_encoded

# Fernet key (for symmetric encryption)
# Generate with: openssl rand -base64 32
FERNET_KEY=your_fernet_key_here_32_bytes_base64_encoded
```

### API Configuration

#### Server Settings

```bash
# Host and port
API_HOST=0.0.0.0
API_PORT=8080

# Development features
API_DEBUG=true
API_RELOAD=true  # Auto-reload on code changes

# Logging
API_LOG_LEVEL=INFO
```

#### CORS (Cross-Origin Resource Sharing)

```bash
# Allowed origins (comma-separated)
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://localhost:3000,https://localhost:8080
```

#### Rate Limiting

```bash
# Maximum calls per period
API_RATE_LIMIT_CALLS=100

# Period in seconds
API_RATE_LIMIT_PERIOD=60
```

### Frontend Configuration

#### React App

```bash
# API endpoints
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=http://localhost:8080

# Development mode
REACT_APP_DEBUG=true

# Token storage keys
REACT_APP_JWT_STORAGE_KEY=tta_access_token
REACT_APP_REFRESH_TOKEN_KEY=tta_refresh_token
```

#### Vite (if using Vite)

```bash
# API base URL
VITE_API_BASE_URL=http://localhost:8080

# Shared components URL
VITE_SHARED_COMPONENTS_URL=http://localhost:3001
```


## Feature Flags

Feature flags allow you to enable/disable functionality without code changes.

### Core Features

```bash
# AI-powered narrative generation
FEATURE_AI_NARRATIVE=true

# Living worlds system
FEATURE_LIVING_WORLDS=true

# Crisis support detection
FEATURE_CRISIS_SUPPORT=true

# Real-time monitoring
FEATURE_REAL_TIME_MONITORING=true
```

### Model Management

```bash
# Model management system
FEATURE_MODEL_MANAGEMENT=true

# Local model support (Ollama, LM Studio)
FEATURE_LOCAL_MODELS=false

# Cloud model support (OpenRouter, OpenAI)
FEATURE_CLOUD_MODELS=true
```

### Advanced Features

```bash
# Predictive analytics (experimental)
FEATURE_PREDICTIVE_ANALYTICS=false

# EHR integration (enterprise)
FEATURE_EHR_INTEGRATION=false

# Mobile apps (coming soon)
FEATURE_MOBILE_APPS=false
```

## Therapeutic Configuration

### Crisis Detection

```bash
# Enable crisis detection
CRISIS_DETECTION_ENABLED=true

# Crisis hotline numbers
CRISIS_HOTLINE_NUMBER=988
CRISIS_TEXT_NUMBER=741741
EMERGENCY_NUMBER=911
```

### Therapeutic Settings

```bash
# Default therapeutic intensity (low, medium, high)
DEFAULT_THERAPEUTIC_INTENSITY=medium

# Safety threshold (0.0-10.0)
THERAPEUTIC_SAFETY_THRESHOLD=7.0

# Session timeout (minutes)
SESSION_TIMEOUT_MINUTES=30

# Maximum concurrent sessions
MAX_CONCURRENT_SESSIONS=100
```

## Monitoring and Logging

### Logging Configuration

```bash
# General log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Database log level
DATABASE_LOG_LEVEL=WARNING

# API log level
API_LOG_LEVEL=INFO
```

### Monitoring Tools

#### Grafana

```bash
# Grafana admin password
GRAFANA_PASSWORD=your_grafana_admin_password_here

# Grafana URL (for MCP integration)
GRAFANA_URL=http://localhost:3000

# Grafana API key (for programmatic access)
GRAFANA_API_KEY=your_grafana_service_account_token_here
```

#### Prometheus

```bash
# Data retention period
PROMETHEUS_RETENTION_TIME=30d
```

#### Sentry (Error Tracking)

```bash
# Sentry DSN (Data Source Name)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Environment name
SENTRY_ENVIRONMENT=development

# Sampling rates (0.0-1.0)
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0

# Privacy settings
SENTRY_SEND_DEFAULT_PII=false

# Enable log integration
SENTRY_ENABLE_LOGS=true
```

### Health Checks

```bash
# Health check interval (seconds)
HEALTH_CHECK_INTERVAL=30

# Health check timeout (seconds)
HEALTH_CHECK_TIMEOUT=10

# Maximum retries before marking unhealthy
HEALTH_CHECK_RETRIES=3
```

## Docker Configuration

### Container Settings

```bash
# Docker Compose project name
COMPOSE_PROJECT_NAME=tta-dev

# Container name prefix
CONTAINER_PREFIX=tta-dev
```

### Container Health Checks

```bash
# Startup wait timeout (seconds)
STARTUP_WAIT_TIMEOUT=120

# Maximum health check retries
MAX_HEALTH_RETRIES=8
```

## Development Tools

### Development Features

```bash
# Enable Grafana dashboard
ENABLE_GRAFANA=true

# Enable Prometheus metrics
ENABLE_PROMETHEUS=true

# Enable Redis Commander (Redis GUI)
ENABLE_REDIS_COMMANDER=true

# Debug container output
DEBUG_CONTAINERS=false
```

### Performance Monitoring

```bash
# Enable performance monitoring
ENABLE_PERFORMANCE_MONITORING=true

# Enable profiling (impacts performance)
PROFILING_ENABLED=false
```

## Testing Configuration

### Test Databases

```bash
# Test PostgreSQL database
TEST_DATABASE_URL=postgresql://tta_user:your_secure_postgres_password_here@localhost:5432/tta_test_db  # pragma: allowlist secret

# Test Redis database (use different DB number)
TEST_REDIS_URL=redis://localhost:6379/1

# Test Neo4j database
TEST_NEO4J_URI=bolt://localhost:7687
```

### Mock Services

```bash
# Mock OpenAI API (for testing without API costs)
MOCK_OPENAI_API=false

# Mock email service
MOCK_EMAIL_SERVICE=true

# Mock SMS service
MOCK_SMS_SERVICE=true
```

## Environment-Specific Configuration

### Development Environment

Recommended settings for local development:

```bash
ENVIRONMENT=development
API_DEBUG=true
API_RELOAD=true
LOG_LEVEL=DEBUG
FEATURE_LOCAL_MODELS=true
MOCK_EMAIL_SERVICE=true
MOCK_SMS_SERVICE=true
```

### Staging Environment

Recommended settings for staging/pre-production:

```bash
ENVIRONMENT=staging
API_DEBUG=false
API_RELOAD=false
LOG_LEVEL=INFO
FEATURE_LOCAL_MODELS=false
MOCK_EMAIL_SERVICE=false
MOCK_SMS_SERVICE=false
SENTRY_ENVIRONMENT=staging
```

### Production Environment

Recommended settings for production:

```bash
ENVIRONMENT=production
API_DEBUG=false
API_RELOAD=false
LOG_LEVEL=WARNING
FEATURE_LOCAL_MODELS=false
MOCK_EMAIL_SERVICE=false
MOCK_SMS_SERVICE=false
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of traces
```

## Security Best Practices

### Password Requirements

- **Minimum length**: 16 characters
- **Complexity**: Mix of uppercase, lowercase, numbers, symbols
- **Uniqueness**: Different password for each service
- **Rotation**: Change passwords every 90 days

### API Key Management

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys regularly** (every 90 days)
4. **Use separate keys** for each environment
5. **Monitor key usage** for anomalies

### Encryption Key Generation

```bash
# Generate JWT secret (64 bytes)
openssl rand -base64 64

# Generate encryption key (32 bytes)
openssl rand -base64 32

# Generate Fernet key (32 bytes)
openssl rand -base64 32
```

### Production Security Checklist

- [ ] All placeholder values replaced with secure values
- [ ] Strong, unique passwords for all services
- [ ] API keys from production accounts (not development)
- [ ] Encryption keys generated and stored securely
- [ ] CORS origins restricted to production domains
- [ ] Debug mode disabled (`API_DEBUG=false`)
- [ ] Appropriate log levels (`LOG_LEVEL=WARNING` or `ERROR`)
- [ ] Sentry configured for error tracking
- [ ] Health checks enabled
- [ ] Rate limiting configured
- [ ] Backup strategy in place

## Troubleshooting

### Configuration Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check file permissions
chmod 600 .env

# Verify no syntax errors
cat .env | grep -v "^#" | grep -v "^$"
```

### Environment Variables Not Set

```bash
# Check if variables are loaded
env | grep TTA

# Manually load .env file
export $(cat .env | grep -v "^#" | xargs)

# Verify specific variable
echo $OPENROUTER_API_KEY
```

### Docker Services Not Connecting

```bash
# Verify environment variables in Docker
docker-compose config

# Check service connectivity
docker-compose exec neo4j cypher-shell -u neo4j -p your_password
docker-compose exec redis redis-cli ping
```

## Next Steps

- **[Quick Start Guide](quickstart.md)**: Run your first TTA session
- **[Development Guide](../development/contributing.md)**: Start contributing
- **[Security Guide](../../SECURITY.md)**: Security best practices

## Additional Resources

- **[Environment Setup Guide](../../ENVIRONMENT_SETUP.md)**: Detailed environment configuration
- **[Docker Setup Guide](../../Documentation/docker/docker_setup_guide.md)**: Advanced Docker configuration
- **[API Documentation](../api/tta-application.md)**: API configuration options


---
**Logseq:** [[TTA.dev/Docs/Getting-started/Configuration]]
