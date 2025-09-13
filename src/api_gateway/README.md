# TTA API Gateway & Service Integration

The API Gateway serves as the unified entry point for all TTA (Therapeutic Text Adventure) services, providing centralized routing, authentication, rate limiting, service discovery, and therapeutic safety monitoring.

## Architecture Overview

The API Gateway is built using FastAPI and provides:

- **Centralized Routing**: Single entry point for all TTA services
- **Authentication Integration**: JWT-based authentication with the TTA auth system
- **Service Discovery**: Dynamic service registration and health monitoring
- **Rate Limiting**: Intelligent traffic management with therapeutic prioritization
- **Therapeutic Safety**: Content safety monitoring and crisis detection
- **WebSocket Proxying**: Real-time communication for chat and narrative services
- **Comprehensive Monitoring**: Health checks, metrics, and observability

## Directory Structure

```
src/api_gateway/
├── __init__.py              # Package initialization
├── app.py                   # Main FastAPI application
├── config.py                # Configuration management
├── README.md                # This file
├── core/                    # Core gateway components
│   └── __init__.py
├── middleware/              # Request/response middleware
│   ├── __init__.py
│   ├── auth.py             # Authentication middleware
│   ├── logging.py          # Request/response logging
│   ├── rate_limiting.py    # Rate limiting and traffic management
│   ├── security.py         # Security headers and validation
│   └── therapeutic_safety.py # Therapeutic safety monitoring
├── models/                  # Data models and schemas
│   └── __init__.py
├── monitoring/              # Health and metrics monitoring
│   ├── __init__.py
│   ├── health.py           # Health check endpoints
│   └── metrics.py          # Prometheus metrics collection
├── security/                # Security components
│   └── __init__.py
├── services/                # Business logic services
│   └── __init__.py
└── utils/                   # Utility functions
    └── __init__.py
```

## Configuration

The gateway uses environment-based configuration with the `TTA_GATEWAY_` prefix:

```bash
# Server Configuration
TTA_GATEWAY_HOST=0.0.0.0
TTA_GATEWAY_PORT=8000
TTA_GATEWAY_DEBUG=false

# Security Configuration
TTA_GATEWAY_JWT_SECRET_KEY=your-secret-key
TTA_GATEWAY_CORS_ORIGINS=["http://localhost:3000"]

# Redis Configuration (for service discovery and rate limiting)
TTA_GATEWAY_REDIS_URL=redis://localhost:6379
TTA_GATEWAY_REDIS_DB=0

# Rate Limiting
TTA_GATEWAY_RATE_LIMITING_ENABLED=true
TTA_GATEWAY_DEFAULT_RATE_LIMIT=100/minute
TTA_GATEWAY_THERAPEUTIC_RATE_LIMIT=200/minute

# Therapeutic Safety
TTA_GATEWAY_THERAPEUTIC_SAFETY_ENABLED=true
TTA_GATEWAY_CRISIS_DETECTION_ENABLED=true

# Monitoring
TTA_GATEWAY_METRICS_ENABLED=true
TTA_GATEWAY_HEALTH_CHECK_INTERVAL=30
```

## Running the Gateway

### Development

```bash
# Install dependencies
uv sync

# Run the gateway
python -m src.api_gateway.app

# Or using uvicorn directly
uvicorn src.api_gateway.app:app --host 0.0.0.0 --port 8000 --reload
```

### Production

```bash
# Run with production settings
TTA_ENVIRONMENT=production uvicorn src.api_gateway.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Monitoring

- `GET /health/` - Comprehensive health status
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

### Metrics

- `GET /metrics/` - Metrics summary (JSON)
- `GET /metrics/prometheus` - Prometheus metrics
- `GET /metrics/health-metrics` - Health-related metrics
- `GET /metrics/therapeutic-metrics` - Therapeutic-specific metrics

### Gateway

- `GET /` - Gateway status and information
- `GET /docs` - API documentation (development only)

## Integration with TTA Services

The gateway integrates with:

1. **Authentication & User Management System**
   - JWT token validation
   - User role and permission management
   - MFA support

2. **Player Experience Interface**
   - API endpoint proxying
   - WebSocket chat proxying
   - Session management

3. **Core Gameplay Loop**
   - Therapeutic session routing
   - Progress tracking
   - Safety monitoring

4. **AI Agent Orchestration**
   - Intelligent request routing
   - Load balancing
   - Circuit breaker patterns

## Therapeutic Safety Features

The gateway includes specialized therapeutic safety features:

- **Crisis Detection**: Monitors content for crisis indicators
- **Safety Interventions**: Automatic intervention mechanisms
- **Therapeutic Prioritization**: Priority routing for therapeutic sessions
- **Compliance Logging**: Comprehensive audit trails for clinical review

## Monitoring and Observability

- **Health Checks**: Comprehensive service health monitoring
- **Metrics Collection**: Prometheus-compatible metrics
- **Structured Logging**: Correlation IDs and structured log format
- **Distributed Tracing**: Request tracing across services
- **Performance Monitoring**: Response times and throughput metrics

## Development Status

This is the initial implementation of the API Gateway. Current status:

- ✅ Project structure and configuration
- ✅ Basic FastAPI application setup
- ✅ Middleware framework
- ✅ Health monitoring endpoints
- ✅ Metrics collection framework
- 🚧 Authentication integration (in progress)
- 🚧 Service discovery (in progress)
- 🚧 Rate limiting implementation (in progress)
- 🚧 WebSocket proxying (in progress)
- 🚧 Therapeutic safety monitoring (in progress)

## Next Steps

1. Implement core data models and schemas
2. Build service discovery and registration
3. Complete authentication middleware integration
4. Implement request routing and load balancing
5. Add WebSocket proxying capabilities
6. Complete therapeutic safety monitoring
7. Add comprehensive testing
8. Create deployment configurations
