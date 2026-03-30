# TTA Security and Best Practices

## Filesystem Isolation Requirements

### WSL2 Filesystem Isolation

**CRITICAL RULE**: All TTA project components must write **ONLY** to WSL filesystem (`/dev/sdf`), **NEVER** to Windows drives.

**Rationale**:
- Performance: WSL filesystem is 10-100x faster than Windows mounts
- Permissions: Avoid Windows/Linux permission conflicts
- Reliability: Prevent file corruption from cross-filesystem operations
- Docker: Volume mounts from Windows paths cause significant overhead

### Allowed Paths

✅ **Correct**:
```bash
/home/thein/recovered-tta-storytelling/     # Project root
/home/thein/.cache/                         # Cache directory
/tmp/                                       # Temporary files
/var/log/tta/                              # Log files
```

❌ **Forbidden**:
```bash
/mnt/c/Users/thein/                        # Windows C: drive
/mnt/d/Projects/                           # Windows D: drive
/mnt/*/                                    # Any Windows mount
```

### Docker Volume Mounts

**Correct Pattern**:
```yaml
# docker-compose.yml
services:
  app:
    volumes:
      # Relative paths (stay in WSL)
      - ./src:/app/src
      - ./config:/app/config

      # Absolute WSL paths
      - /home/thein/data:/data
      - /tmp/tta-cache:/cache
```

**Incorrect Pattern**:
```yaml
# ❌ DO NOT USE
services:
  app:
    volumes:
      # Windows paths cause performance issues
      - /mnt/c/Users/thein/data:/data
      - C:\Users\thein\data:/data  # Invalid in WSL
```

### Validation

**Pre-commit Hook**:
```bash
# Check for Windows path references
if grep -r "/mnt/[a-z]/" src/ config/ docker-compose*.yml; then
  echo "ERROR: Windows filesystem paths detected"
  echo "Use WSL paths only (/home/thein/...)"
  exit 1
fi
```

**Runtime Check**:
```python
# src/infrastructure/filesystem_validator.py
import os
from pathlib import Path

def validate_path(path: str) -> None:
    """Ensure path is on WSL filesystem, not Windows mount."""
    resolved = Path(path).resolve()

    if str(resolved).startswith('/mnt/'):
        raise ValueError(
            f"Path {path} is on Windows filesystem. "
            f"Use WSL paths only (/home/thein/...)"
        )
```

## Secret Management Practices

### Secret Detection Tools

**detect-secrets** (Yelp):
```bash
# Scan for secrets
uvx detect-secrets scan

# Create baseline (first time)
uvx detect-secrets scan > .secrets.baseline

# Audit baseline
uvx detect-secrets audit .secrets.baseline
```

**gitleaks** (Gitleaks):
```bash
# Scan repository
uvx gitleaks detect --source . --verbose

# Scan commits
uvx gitleaks protect --staged
```

**Configuration**: `.gitleaksignore`
```
# Ignore false positives
test/fixtures/fake_api_key.txt
docs/examples/sample_config.yml
```

### Pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

### Secret Storage

**Environment Variables** (Preferred):
```bash
# .env (NEVER commit to git)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
REDIS_PASSWORD=xxxxx
NEO4J_PASSWORD=xxxxx
SUPABASE_KEY=xxxxx

# .gitignore
.env
.env.*
!.env.example
```

**Example File**:
```bash
# .env.example (safe to commit)
OPENROUTER_API_KEY=your_api_key_here
REDIS_PASSWORD=your_redis_password
NEO4J_PASSWORD=your_neo4j_password
SUPABASE_KEY=your_supabase_key
```

**Loading Secrets**:
```python
# src/infrastructure/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    redis_password: str
    neo4j_password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**Docker Secrets**:
```yaml
# docker-compose.yml
services:
  app:
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    # OR use secrets (production)
    secrets:
      - openrouter_api_key

secrets:
  openrouter_api_key:
    file: ./secrets/openrouter_api_key.txt
```

### Secret Rotation

**Policy**:
- API keys: Rotate every 90 days
- Database passwords: Rotate every 180 days
- OAuth secrets: Rotate on security incidents

**Procedure**:
1. Generate new secret
2. Update in secret store (environment variables, vault)
3. Deploy with new secret
4. Verify functionality
5. Revoke old secret
6. Document rotation in changelog

## Authentication Patterns

### OAuth Integration

**Supported Providers**:
- GitHub OAuth
- Google OAuth
- Custom OAuth providers

**Flow**:
```python
# src/api_gateway/auth/oauth.py
from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth

router = APIRouter()
oauth = OAuth()

# Register OAuth provider
oauth.register(
    name='github',
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email'},
)

@router.get('/login/github')
async def github_login(request: Request):
    """Initiate GitHub OAuth flow."""
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get('/callback/github')
async def github_callback(request: Request):
    """Handle GitHub OAuth callback."""
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get('user', token=token)

    # Create session
    session_id = await create_session(user_info)

    # Set secure cookie
    response = RedirectResponse(url='/dashboard')
    response.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # HTTPS only
        samesite='lax', # CSRF protection
        max_age=86400,  # 24 hours
    )
    return response
```

### Secure API Key Handling

**NEVER** store API keys in:
- ❌ localStorage (accessible to JavaScript, XSS vulnerable)
- ❌ sessionStorage (same issues as localStorage)
- ❌ Cookies without httponly flag
- ❌ Client-side code (visible in browser)

**Correct Pattern**:
```python
# Server-side API key storage
# src/api_gateway/auth/api_keys.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class APIKeyRequest(BaseModel):
    provider: str  # 'openrouter', 'anthropic', etc.
    api_key: str

@router.post('/api-keys')
async def store_api_key(
    request: APIKeyRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Store API key securely on server."""
    # Encrypt API key
    encrypted_key = encrypt_api_key(request.api_key)

    # Store in Redis with user association
    await redis_client.hset(
        f"user:{user_id}:api_keys",
        request.provider,
        encrypted_key
    )

    return {"status": "success"}

@router.get('/api-keys/{provider}')
async def get_api_key(
    provider: str,
    user_id: str = Depends(get_current_user_id)
):
    """Retrieve API key for use (server-side only)."""
    encrypted_key = await redis_client.hget(
        f"user:{user_id}:api_keys",
        provider
    )

    if not encrypted_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Decrypt and use (never send to client)
    api_key = decrypt_api_key(encrypted_key)
    return {"has_key": True}  # Don't send actual key to client
```

**Client-Side Form**:
```typescript
// web-interfaces/src/components/APIKeyForm.tsx
async function submitAPIKey(provider: string, apiKey: string) {
  // Send to server via HTTPS
  const response = await fetch('/api/api-keys', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // Include session cookie
    body: JSON.stringify({ provider, api_key: apiKey }),
  });

  if (response.ok) {
    // Clear form (don't store in state)
    setApiKey('');
    alert('API key stored securely');
  }
}
```

### Session Management

**Server-Side Sessions** (Redis-backed):
```python
# src/api_gateway/auth/sessions.py
import secrets
from datetime import datetime, timedelta

async def create_session(user_info: dict) -> str:
    """Create secure server-side session."""
    session_id = secrets.token_urlsafe(32)

    session_data = {
        'user_id': user_info['id'],
        'email': user_info['email'],
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
    }

    # Store in Redis
    await redis_client.setex(
        f"session:{session_id}",
        86400,  # 24 hours
        json.dumps(session_data)
    )

    return session_id

async def get_session(session_id: str) -> dict | None:
    """Retrieve session data."""
    data = await redis_client.get(f"session:{session_id}")
    if not data:
        return None

    session = json.loads(data)

    # Check expiration
    if datetime.fromisoformat(session['expires_at']) < datetime.utcnow():
        await redis_client.delete(f"session:{session_id}")
        return None

    return session
```

**Security Properties**:
- ✅ httponly cookies (prevent XSS)
- ✅ secure flag (HTTPS only)
- ✅ samesite=lax (CSRF protection)
- ✅ Server-side storage (can't be tampered with)
- ✅ Automatic expiration (Redis TTL)

## Docker Optimization Patterns

### Standardized Dockerfile Pattern

**Multi-Stage Build**:
```dockerfile
# Dockerfile (standardized pattern)

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy UV and virtual environment from builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Layer Caching Optimization

**Order of Operations** (most stable to most volatile):
```dockerfile
# 1. Base image (rarely changes)
FROM python:3.11-slim

# 2. System dependencies (rarely changes)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Python dependencies (changes occasionally)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 4. Application code (changes frequently)
COPY src/ ./src/

# 5. Runtime configuration (changes frequently)
CMD ["uvicorn", "src.main:app"]
```

**Benefits**:
- Faster builds (reuse cached layers)
- Smaller images (fewer layers)
- Consistent builds (locked dependencies)

### Validated Volume Mounts

**Pattern**:
```yaml
# docker-compose.yml
services:
  app:
    volumes:
      # Source code (development)
      - ./src:/app/src:ro  # Read-only for safety

      # Configuration
      - ./config:/app/config:ro

      # Data persistence
      - tta-data:/app/data

      # Logs
      - ./logs:/app/logs

volumes:
  tta-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/thein/tta-data  # WSL path
```

**Validation**:
```python
# src/infrastructure/volume_validator.py
import os
from pathlib import Path

def validate_volume_mounts():
    """Ensure all volume mounts are on WSL filesystem."""
    required_paths = [
        '/app/src',
        '/app/config',
        '/app/data',
    ]

    for path in required_paths:
        if not Path(path).exists():
            raise RuntimeError(f"Required volume mount missing: {path}")

        # Check not on Windows mount
        resolved = Path(path).resolve()
        if str(resolved).startswith('/mnt/'):
            raise RuntimeError(
                f"Volume mount {path} is on Windows filesystem. "
                f"Use WSL paths only."
            )
```

### .dockerignore

**Comprehensive Exclusions**:
```
# .dockerignore

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Documentation
docs/
*.md
!README.md

# Tests
tests/
playwright-report/

# CI/CD
.github/

# Logs
*.log
logs/

# Environment
.env
.env.*
!.env.example

# Build artifacts
dist/
build/
*.egg-info/

# OS
.DS_Store
Thumbs.db
```

## Additional Security Best Practices

### Input Validation

**Pydantic Models**:
```python
from pydantic import BaseModel, Field, validator

class StoryRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=5000)
    player_id: str = Field(..., regex=r'^[a-zA-Z0-9-]+$')

    @validator('title')
    def sanitize_title(cls, v):
        """Remove potentially dangerous characters."""
        return v.strip().replace('<', '').replace('>', '')
```

### SQL Injection Prevention

**Parameterized Queries** (always):
```python
# ✅ Correct (parameterized)
query = "SELECT * FROM stories WHERE player_id = $1"
result = await db.fetch(query, player_id)

# ❌ Incorrect (vulnerable to SQL injection)
query = f"SELECT * FROM stories WHERE player_id = '{player_id}'"
result = await db.fetch(query)
```

### XSS Prevention

**Output Encoding**:
```python
from markupsafe import escape

def render_story_text(text: str) -> str:
    """Safely render user-generated story text."""
    return escape(text)
```

**Content Security Policy**:
```python
# src/api_gateway/middleware/security.py
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### CSRF Protection

**Token-Based**:
```python
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware
import secrets

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

@app.post('/api/story')
async def create_story(request: Request, story: StoryRequest):
    """Create story with CSRF protection."""
    # Verify CSRF token
    csrf_token = request.headers.get('X-CSRF-Token')
    session_token = request.session.get('csrf_token')

    if not csrf_token or csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token invalid")

    # Process request
    return await create_story_internal(story)
```

### Rate Limiting

**Per-User Limits**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post('/api/story')
@limiter.limit("10/minute")
async def create_story(request: Request, story: StoryRequest):
    """Create story with rate limiting."""
    return await create_story_internal(story)
```

## Monitoring and Alerting

### Security Event Logging

```python
import structlog

security_logger = structlog.get_logger("security")

# Log authentication events
security_logger.info(
    "authentication_success",
    user_id=user_id,
    method="oauth",
    provider="github"
)

# Log authorization failures
security_logger.warning(
    "authorization_failure",
    user_id=user_id,
    resource="story",
    action="delete",
    reason="insufficient_permissions"
)

# Log suspicious activity
security_logger.error(
    "suspicious_activity",
    user_id=user_id,
    event="multiple_failed_logins",
    count=5,
    timeframe="5_minutes"
)
```

### Security Metrics

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram

auth_attempts = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

auth_failures = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['method', 'reason']
)

api_key_usage = Counter(
    'api_key_usage_total',
    'Total API key usage',
    ['provider', 'user_id']
)
```
