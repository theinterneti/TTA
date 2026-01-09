# TTA Secrets Management Guide

**Last Updated**: 2025-10-27
**Status**: ✅ Active

---

## Overview

TTA uses a multi-layered approach to secrets management:
1. **Development**: `.env` files + `secrets/` directory (gitignored)
2. **Test/Staging**: Docker secrets from `secrets/` directory
3. **Production**: External secrets manager (AWS Secrets Manager, etc.)

---

## Current Configuration

### Development Environment

**Neo4j**:
- URI: `bolt://localhost:7687`
- Username: `neo4j`
- Password: `tta_dev_password_2024`
- Browser: http://localhost:7474
- Docker Container: `tta-dev-neo4j`

**Redis**:
- URI: `redis://localhost:6379`
- Password: *(none for dev)*
- Docker Container: `tta-dev-redis`

**Location**:
- `.env` file (root directory)
- `secrets/dev/neo4j_auth.txt` → `neo4j/tta_dev_password_2024`
- `secrets/dev/redis_password.txt` → *(empty for dev)*

### Test Environment

**Neo4j**:
- URI: `bolt://localhost:7688`
- Username: `neo4j`
- Password: `tta_test_password_2024`
- Docker Container: `tta-test-neo4j`

**Redis**:
- URI: `redis://localhost:7379`
- Password: *(none for test)*
- Docker Container: `tta-test-redis`

**Location**:
- `secrets/test/neo4j_auth.txt` → `neo4j/tta_test_password_2024`
- `secrets/test/redis_password.txt` → *(empty for test)*

### Staging Environment

**Neo4j**:
- URI: `bolt://localhost:7689`
- Username: `neo4j`
- Password: `staging_neo4j_secure_pass_2024`
- Docker Container: `tta-staging-neo4j`

**Redis**:
- URI: `redis://localhost:8379`
- Password: `staging_redis_secure_pass_2024`
- Docker Container: `tta-staging-redis`

**Location**:
- `secrets/staging/neo4j_auth.txt` → `neo4j/staging_neo4j_secure_pass_2024`
- `secrets/staging/redis_password.txt` → `staging_redis_secure_pass_2024`

---

## VS Code Configuration

The `.vscode/settings.json` file is configured with connections for all environments:

```json
{
  "neo4j.connections": [
    {
      "name": "🟢 TTA Dev Neo4j",
      "protocol": "bolt",
      "host": "localhost",
      "port": 7687,
      "username": "neo4j",
      "password": "tta_dev_password_2024",
      "database": "neo4j"
    },
    {
      "name": "🟡 TTA Test Neo4j",
      "protocol": "bolt",
      "host": "localhost",
      "port": 7688,
      "username": "neo4j",
      "password": "tta_test_password_2024",
      "database": "neo4j"
    },
    {
      "name": "🟠 TTA Staging Neo4j",
      "protocol": "bolt",
      "host": "localhost",
      "port": 7689,
      "username": "neo4j",
      "password": "staging_neo4j_secure_pass_2024",
      "database": "neo4j"
    }
  ]
}
```

**Redis connections** are also configured in the same file.

---

## Testing Connections

### Neo4j CLI Tests

```bash
# Development
docker exec tta-dev-neo4j cypher-shell -u neo4j -p 'tta_dev_password_2024' \
  'RETURN "Dev connection successful!" AS message'

# Test
docker exec tta-test-neo4j cypher-shell -u neo4j -p 'tta_test_password_2024' \
  'RETURN "Test connection successful!" AS message'

# Staging
docker exec tta-staging-neo4j cypher-shell -u neo4j -p 'staging_neo4j_secure_pass_2024' \
  'RETURN "Staging connection successful!" AS message'
```

### Python Connection Test

```bash
# Uses .env file automatically
python scripts/test_database_connections.py
```

### VS Code Extension

1. Open Command Palette (`Ctrl+Shift+P`)
2. Search: "Neo4j: Connect"
3. Select environment: `🟢 TTA Dev Neo4j`
4. Connection should succeed automatically

---

## Password Rotation

### Development/Test

1. Update password in `secrets/{env}/neo4j_auth.txt`
2. Update `.env` file (for dev only)
3. Update `.vscode/settings.json`
4. Restart Docker containers:
   ```bash
   docker compose -f docker-compose.{env}.yml down
   docker compose -f docker-compose.{env}.yml up -d
   ```

### Staging

1. Generate new secure password:
   ```bash
   openssl rand -base64 32
   ```
2. Update `secrets/staging/neo4j_auth.txt`
3. Update `.vscode/settings.json`
4. Restart staging services:
   ```bash
   bash docker/scripts/tta-docker.sh staging restart
   ```

### Production

Use the external secrets manager rotation process. See `secrets/production/README.md`.

---

## Security Best Practices

### ✅ DO:
- Keep `secrets/` directory gitignored
- Use strong passwords for staging/production (32+ characters)
- Rotate passwords regularly (quarterly minimum)
- Use environment-specific passwords
- Document password requirements in this file

### ❌ DON'T:
- Commit `.env` files to version control
- Use production passwords in development
- Share passwords in chat/email
- Use default passwords (like "password" or "neo4j")
- Hard-code passwords in source code

---

## Troubleshooting

### "Authentication failed" in VS Code

1. Check the running container's password:
   ```bash
   docker exec tta-dev-neo4j env | grep NEO4J_AUTH
   ```

2. Verify the password matches:
   - `secrets/dev/neo4j_auth.txt`
   - `.vscode/settings.json`
   - `.env` file

3. If mismatch, update all locations and restart:
   ```bash
   docker compose -f docker-compose.dev.yml restart neo4j
   ```

### "Connection refused"

1. Check if container is running:
   ```bash
   docker ps | grep neo4j
   ```

2. Check if port is correct:
   - Dev: 7687
   - Test: 7688
   - Staging: 7689

3. Verify firewall/network:
   ```bash
   telnet localhost 7687
   ```

### "Database not found"

Neo4j 5.x uses `neo4j` as the default database name. Make sure:
- `.vscode/settings.json` → `"database": "neo4j"`
- `.env` → `NEO4J_DATABASE=neo4j`

---

## File Reference

### Secrets Files
```
secrets/
├── dev/
│   ├── neo4j_auth.txt           # neo4j/tta_dev_password_2024
│   ├── redis_password.txt       # (empty)
│   └── grafana_admin_password.txt
├── test/
│   ├── neo4j_auth.txt           # neo4j/tta_test_password_2024
│   └── redis_password.txt       # (empty)
└── staging/
    ├── neo4j_auth.txt           # neo4j/staging_neo4j_secure_pass_2024
    └── redis_password.txt       # staging_redis_secure_pass_2024
```

### Configuration Files
- `.env` - Development environment variables
- `.env.example` - Template with placeholders
- `.vscode/settings.json` - VS Code extension connections
- `docker-compose.dev.yml` - Dev services with fallback passwords
- `docker-compose.test.yml` - Test services with fallback passwords
- `docker-compose.staging.yml` - Staging services (uses secrets)

---

## Environment Variable Reference

### Neo4j
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_URL=bolt://localhost:7687          # Alias for URI
NEO4J_USER=neo4j
NEO4J_USERNAME=neo4j                      # Alias for USER
NEO4J_PASSWORD=tta_dev_password_2024
NEO4J_DATABASE=neo4j
```

### Redis
```bash
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=                           # Empty for dev/test
REDIS_DB=0
```

### Test Environment (Overrides)
```bash
TEST_NEO4J_URI=bolt://localhost:7688
TEST_REDIS_URL=redis://localhost:7379
```

---

## Docker Compose Patterns

### Using Environment Variables (Development)
```yaml
services:
  neo4j:
    environment:
      - NEO4J_AUTH=${NEO4J_AUTH:-neo4j/tta_dev_password_2024}
```

### Using Docker Secrets (Test/Staging/Production)
```yaml
services:
  neo4j:
    secrets:
      - neo4j_auth
    environment:
      - NEO4J_AUTH_FILE=/run/secrets/neo4j_auth

secrets:
  neo4j_auth:
    file: ./secrets/test/neo4j_auth.txt
```

---

## Migration Notes

### From Old Password System (Pre-2025-10-27)

**Old system** had inconsistent passwords:
- Secrets files: Random generated passwords
- Docker compose: Fallback default passwords
- .env files: Placeholder strings

**New system** (current):
- **Standardized**: All sources use same password per environment
- **Documented**: Passwords listed in this file
- **Discoverable**: Easy to find actual password
- **Consistent**: VS Code, Docker, and Python all use same credentials

**Migration steps**:
1. ✅ Updated `secrets/dev/neo4j_auth.txt` → `neo4j/tta_dev_password_2024`
2. ✅ Updated `secrets/test/neo4j_auth.txt` → `neo4j/tta_test_password_2024`
3. ✅ Updated `secrets/staging/neo4j_auth.txt` → `neo4j/staging_neo4j_secure_pass_2024`
4. ✅ Added Neo4j connections to `.vscode/settings.json`
5. ✅ Created this documentation

---

## Quick Reference

| Environment | Neo4j Port | Neo4j Password | Redis Port | Redis Password |
|-------------|------------|----------------|------------|----------------|
| Development | 7687       | `tta_dev_password_2024` | 6379 | *(none)* |
| Test        | 7688       | `tta_test_password_2024` | 7379 | *(none)* |
| Staging     | 7689       | `staging_neo4j_secure_pass_2024` | 8379 | `staging_redis_secure_pass_2024` |

**VS Code Neo4j Extension**: Command Palette → "Neo4j: Connect" → Select environment

**Browser Access**:
- Dev: http://localhost:7474
- Test: http://localhost:7475
- Staging: http://localhost:7476

---

**For production secrets management**, see: `secrets/production/README.md`


---
**Logseq:** [[TTA.dev/Docs/Guides/Secrets-management]]
