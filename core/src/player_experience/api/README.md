# Player Experience Interface API

This is the FastAPI-based web API for the TTA Player Experience Interface. It provides REST endpoints for player management, character management, world management, and authentication.

## Features

- **FastAPI Application**: Modern, fast web API framework
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-origin resource sharing for web frontends
- **Comprehensive Middleware**: Security, logging, rate limiting, and therapeutic safety
- **OpenAPI Documentation**: Automatic API documentation generation
- **Error Handling**: Comprehensive error handling and validation
- **Therapeutic Safety**: Built-in crisis detection and safety monitoring

## Quick Start

### Running the Server

```bash
# Using the main entry point
uv run python src/player_experience/api/main.py

# Or using uvicorn directly
uv run uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080 --reload

# Or using the TTA orchestration system (when integrated)
./tta.sh start player-experience-api
```

### Environment Configuration

Set environment variables to configure the API:

```bash
# Basic configuration
export API_HOST=0.0.0.0
export API_PORT=8080
export API_DEBUG=true

# Security configuration
export API_JWT_SECRET_KEY=your-very-secure-secret-key-here
export API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS configuration
export API_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Database configuration
export API_REDIS_URL=redis://localhost:6379
export API_NEO4J_URL=bolt://localhost:7687
export API_NEO4J_USERNAME=neo4j
export API_NEO4J_PASSWORD=your-password
```

## API Endpoints

### Authentication Endpoints

- `POST /api/v1/auth/login` - Login with username/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (client-side token disposal)
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/verify-token` - Verify token validity

### Player Management Endpoints

- `GET /api/v1/players/` - List players (placeholder)
- `GET /api/v1/players/{player_id}` - Get player profile (placeholder)
- `POST /api/v1/players/` - Create player profile (placeholder)
- `PUT /api/v1/players/{player_id}` - Update player profile (placeholder)
- `DELETE /api/v1/players/{player_id}` - Delete player profile (placeholder)

### Character Management Endpoints

- `GET /api/v1/characters/` - List characters (placeholder)
- `GET /api/v1/characters/{character_id}` - Get character (placeholder)
- `POST /api/v1/characters/` - Create character (placeholder)
- `PUT /api/v1/characters/{character_id}` - Update character (placeholder)
- `DELETE /api/v1/characters/{character_id}` - Delete character (placeholder)

### World Management Endpoints

- `GET /api/v1/worlds/` - List available worlds (placeholder)
- `GET /api/v1/worlds/{world_id}` - Get world details (placeholder)
- `GET /api/v1/worlds/{world_id}/compatibility/{character_id}` - Check compatibility (placeholder)
- `POST /api/v1/worlds/{world_id}/customize` - Customize world parameters (placeholder)

### System Endpoints

- `GET /` - Root endpoint (health check)
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /metrics` - Lightweight metrics (testing/dev only, returns 404 when not in debug)
- `GET /api/v1/players/{player_id}/progress/viz?days=14` - Progress visualization data (protected)

- `GET /openapi.json` - OpenAPI specification

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Login**: Send credentials to `/api/v1/auth/login`
2. **Get Token**: Receive access and refresh tokens
3. **Use Token**: Include in Authorization header: `Bearer <access_token>`
4. **Refresh**: Use refresh token to get new access token when expired

### Example Authentication Flow

```python
import requests

# Login
response = requests.post("http://localhost:8080/api/v1/auth/login", json={
    "username": "your_username",
    "password": "your_password"
})

tokens = response.json()
access_token = tokens["access_token"]

# Use token for protected endpoints
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8080/api/v1/players/", headers=headers)
```

## Middleware

The API includes several middleware components:

### Security Middleware

- **SecurityHeadersMiddleware**: Adds security headers (HSTS, CSP, etc.)
- **AuthenticationMiddleware**: Handles JWT token validation
- **TrustedHostMiddleware**: Validates allowed hosts

### Operational Middleware

- **LoggingMiddleware**: Logs requests and responses
- **RateLimitMiddleware**: Implements rate limiting (100 requests/minute by default)
- **CORSMiddleware**: Handles cross-origin requests

### Therapeutic Safety Middleware

- **TherapeuticSafetyMiddleware**: Monitors for therapeutic safety
- **CrisisDetectionMiddleware**: Detects potential crisis situations

## Configuration

The API uses Pydantic Settings for configuration management. Configuration can be provided via:

1. Environment variables (prefixed with `API_`)
2. `.env` file
3. Direct instantiation

### Configuration Classes

- `APISettings`: Base configuration
- `DevelopmentSettings`: Development environment settings
- `ProductionSettings`: Production environment settings
- `TestingSettings`: Test environment settings

## Error Handling

The API provides comprehensive error handling:

- **HTTP Exceptions**: Standard HTTP error responses
- **Validation Errors**: Detailed validation error messages
- **Authentication Errors**: Clear authentication failure messages
- **Authorization Errors**: Access denied messages
- **General Exceptions**: Graceful handling of unexpected errors

## Testing

Run the test suite:

```bash
# Run all API tests
uv run python -m pytest tests/test_api_structure.py tests/test_api_integration.py -v

# Test server startup
uv run python scripts/test_api_server.py
```

## Development

### Project Structure

```
src/player_experience/api/
├── __init__.py          # Package exports
├── app.py              # Main FastAPI application
├── auth.py             # Authentication utilities
├── config.py           # Configuration management
├── main.py             # Server entry point
├── middleware.py       # Custom middleware
└── routers/            # API route handlers
    ├── __init__.py
    ├── auth.py         # Authentication routes
    ├── players.py      # Player management routes
    ├── characters.py   # Character management routes
    └── worlds.py       # World management routes
```

### Adding New Endpoints

1. Create or modify router files in `routers/`
2. Include router in `app.py`
3. Add authentication dependencies as needed
4. Write tests for new endpoints

### Middleware Development

1. Create middleware class in `middleware.py`
2. Add middleware to app in `app.py`
3. Consider middleware order (authentication should be last)

## Security Considerations

- **JWT Secret**: Use a strong, unique secret key in production
- **Rate Limiting**: Defaults to 100 req/minute; override via `PEI_RATE_LIMIT_CALLS` and `PEI_RATE_LIMIT_PERIOD` env vars.
- **WebSocket Validation**: User chat messages are validated and sanitized; unsafe messages receive a friendly system response.
- **Metrics Gating**: `/metrics` is available only when `settings.debug` is True (hidden with 404 otherwise).

- **HTTPS**: Always use HTTPS in production
- **CORS**: Configure CORS origins appropriately
- **Rate Limiting**: Adjust rate limits based on usage patterns
- **Input Validation**: All inputs are validated using Pydantic models
- **Crisis Detection**: Built-in monitoring for therapeutic safety

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.player_experience.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Environment Variables for Production

```bash
export ENVIRONMENT=production
export API_JWT_SECRET_KEY=your-very-secure-production-secret-key
export API_DEBUG=false
export API_CORS_ORIGINS=https://yourdomain.com
export API_DATABASE_URL=postgresql://user:pass@host:port/db
export API_REDIS_URL=redis://redis-host:6379
```

## Next Steps

The current implementation provides the basic FastAPI application structure. The following tasks will implement the actual functionality:

- **Task 7.2**: Implement Player Management API endpoints
- **Task 7.3**: Implement Character Management API endpoints
- **Task 7.4**: Implement World Management API endpoints
- **Task 8**: Build WebSocket Chat Interface Backend

## Support

For issues or questions about the API:

1. Check the OpenAPI documentation at `/docs`
2. Review the test files for usage examples
3. Check the middleware logs for debugging information
4. Ensure all required environment variables are set
