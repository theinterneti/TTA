# TTA Authentication System Documentation

## Overview

The Therapeutic Text Adventure (TTA) platform features a comprehensive authentication system that provides secure user management, multi-factor authentication, role-based access control, and session management. The system is built with security best practices and integrates seamlessly with the Neo4j graph database for persistent storage.

## Architecture

### Core Components

1. **UserRepository** - Database operations for user authentication data
2. **EnhancedAuthService** - Main authentication service with MFA and security features
3. **UserManagementService** - Coordinates User and PlayerProfile creation
4. **UserAuthSchemaManager** - Manages Neo4j schema for authentication data
5. **Authentication Middleware** - Request authentication and authorization
6. **Health Check Endpoints** - Monitoring and diagnostics

### Database Schema

The authentication system uses Neo4j with the following node types:

- **User** - Core authentication data (credentials, roles, security settings)
- **UserSession** - Active user sessions with expiration tracking
- **MFASecret** - Multi-factor authentication secrets and backup codes
- **SecurityEvent** - Audit log of security-related events

### Security Features

- **Password Security**: bcrypt hashing with configurable complexity
- **Account Lockout**: Configurable failed login attempt tracking
- **Multi-Factor Authentication**: TOTP support with QR code generation
- **JWT Tokens**: Secure access and refresh token management
- **Role-Based Access Control**: Granular permission system
- **Security Event Logging**: Comprehensive audit trail
- **Rate Limiting**: Protection against brute force attacks

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "player|admin|therapist",
  "therapeutic_preferences": {
    "goals": ["anxiety", "depression"],
    "intensity": "medium",
    "frequency": "weekly"
  },
  "privacy_settings": {
    "data_sharing": true,
    "analytics": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "uuid"
}
```

#### POST /api/v1/auth/login
Authenticate a user and create a session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "role": "player",
    "permissions": ["read", "write"],
    "mfa_enabled": false
  }
}
```

#### POST /api/v1/auth/logout
Logout and invalidate the current session.

#### POST /api/v1/auth/refresh
Refresh an access token using a refresh token.

#### POST /api/v1/auth/mfa/setup
Set up multi-factor authentication.

#### POST /api/v1/auth/mfa/verify
Verify an MFA challenge.

### Health Check Endpoints

#### GET /api/v1/health
Basic health check.

#### GET /api/v1/health/detailed
Detailed health check with component status.

#### GET /api/v1/health/ready
Kubernetes readiness probe.

#### GET /api/v1/health/live
Kubernetes liveness probe.

## Configuration

### Environment Variables

The system supports configuration through environment variables:

#### Required Settings
- `JWT_SECRET_KEY` - Secret key for JWT token signing (min 32 chars in production)
- `NEO4J_URL` - Neo4j database connection URL
- `NEO4J_USERNAME` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password

#### Security Settings
- `MAX_LOGIN_ATTEMPTS` - Maximum failed login attempts (default: 5)
- `LOCKOUT_DURATION_MINUTES` - Account lockout duration (default: 15)
- `PASSWORD_MIN_LENGTH` - Minimum password length (default: 8)
- `MFA_ENABLED` - Enable multi-factor authentication (default: false)

#### Server Settings
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Environment (development|production|test)

### Configuration Files

Use the provided `.env.production.template` as a starting point for production configuration.

## Deployment

### Database Setup

1. **Install Neo4j** (version 5.8.0 or later)
2. **Run the setup script**:
   ```bash
   python scripts/setup_auth_database.py --uri bolt://localhost:7687 --username neo4j --password your-password
   ```
3. **Verify the setup**:
   ```bash
   python scripts/setup_auth_database.py --verify-only
   ```

### Application Deployment

1. **Set environment variables** (see Configuration section)
2. **Install dependencies**:
   ```bash
   uv sync
   ```
3. **Run database migrations**:
   ```bash
   python scripts/setup_auth_database.py
   ```
4. **Start the application**:
   ```bash
   uv run python -m src.player_experience.api.main
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "src.player_experience.api.main"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tta-auth-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tta-auth-api
  template:
    metadata:
      labels:
        app: tta-auth-api
    spec:
      containers:
      - name: api
        image: tta-auth-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: tta-secrets
              key: jwt-secret
        - name: NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: tta-secrets
              key: neo4j-password
        livenessProbe:
          httpGet:
            path: /api/v1/health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Security Considerations

### Production Security Checklist

- [ ] Change default JWT secret key to a strong, random value (min 32 characters)
- [ ] Change default Neo4j password to a strong value
- [ ] Configure CORS origins for your domain (remove localhost)
- [ ] Enable HTTPS/TLS in production
- [ ] Set up proper firewall rules for database access
- [ ] Enable MFA for admin accounts
- [ ] Configure rate limiting appropriately
- [ ] Set up monitoring and alerting
- [ ] Regular security updates and patches
- [ ] Backup and disaster recovery procedures

### Password Policy

The system enforces configurable password requirements:
- Minimum length (default: 8 characters)
- Uppercase letters (configurable)
- Lowercase letters (configurable)
- Numbers (configurable)
- Special characters (configurable)

### Session Management

- JWT tokens with configurable expiration
- Refresh token rotation
- Session invalidation on logout
- Concurrent session limits (configurable)

## Monitoring and Observability

### Health Checks

The system provides multiple health check endpoints:
- Basic health check for load balancer
- Detailed health check with component status
- Kubernetes-compatible readiness and liveness probes

### Metrics

Key metrics to monitor:
- Authentication success/failure rates
- Account lockout events
- Session creation/expiration
- Database connection health
- Response times

### Logging

The system logs security events including:
- User registration attempts
- Login successes and failures
- Account lockout events
- MFA challenges and verifications
- Permission denied events

## Testing

### Unit Tests

Run unit tests for authentication components:
```bash
uv run pytest tests/test_user_repository.py -v
uv run pytest tests/test_enhanced_authentication.py -v
```

### Integration Tests

Run integration tests with Neo4j:
```bash
uv run pytest tests/test_user_authentication_integration.py -v --neo4j
```

### Load Testing

Use tools like Apache Bench or Artillery to test authentication endpoints under load.

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check Neo4j service status
   - Verify connection credentials
   - Check network connectivity

2. **JWT Token Issues**
   - Verify secret key configuration
   - Check token expiration settings
   - Validate token format

3. **Account Lockout Issues**
   - Check failed login attempt configuration
   - Verify lockout duration settings
   - Review security event logs

### Debug Mode

Enable debug mode for development:
```bash
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Support

For issues and questions:
- Check the health check endpoints for system status
- Review application logs for error details
- Consult the troubleshooting section above
- Contact the development team with specific error messages and logs
