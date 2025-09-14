# Security Configuration Guide

## Overview

This document outlines the security configuration requirements for the TTA Player Experience API, including proper secret management and environment variable setup.

## Critical Security Requirements

### 1. JWT Secret Key

**Environment Variable:** `JWT_SECRET_KEY`

- **REQUIRED** in all environments
- Minimum 32 characters long
- Must be cryptographically random
- **NEVER** use default values in production

**Generate a secure key:**
```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Database Credentials

**Neo4j Configuration:**
- `NEO4J_URL`: Connection URL (default: bolt://localhost:7687)
- `NEO4J_USERNAME`: Username (default: neo4j)
- `NEO4J_PASSWORD`: **REQUIRED** - Strong password, minimum 8 characters

**Redis Configuration:**
- `REDIS_URL`: Connection URL (default: redis://localhost:6379)
- `REDIS_PASSWORD`: Optional, but recommended for production

### 3. Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in all required values in `.env`

3. **NEVER** commit `.env` files to version control

## Production Security Checklist

- [ ] JWT_SECRET_KEY is set and at least 32 characters
- [ ] NEO4J_PASSWORD is changed from default
- [ ] REDIS_PASSWORD is set if Redis requires authentication
- [ ] CORS origins are properly configured (no localhost in production)
- [ ] Environment is set to "production"
- [ ] All default passwords have been changed

## Security Validation

The application includes automatic validation:

- **JWT Secret Key**: Validates minimum length and non-empty values
- **Neo4j Password**: Ensures production passwords are not defaults
- **CORS Origins**: Prevents localhost origins in production

## Secret Management Best Practices

1. **Use Environment Variables**: Never hardcode secrets in source code
2. **Rotate Secrets Regularly**: Change passwords and keys periodically
3. **Use Secret Management Services**: Consider HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
4. **Principle of Least Privilege**: Grant minimal necessary permissions
5. **Monitor Access**: Log and monitor secret access patterns

## Development vs Production

### Development
- Can use weaker secrets for convenience
- Default values provided for quick setup
- Validation is more lenient

### Production
- **MUST** use strong, unique secrets
- Strict validation enforced
- No default values allowed
- CORS restrictions enforced

## Troubleshooting

### Common Issues

1. **"JWT_SECRET_KEY environment variable must be set"**
   - Ensure JWT_SECRET_KEY is set in your .env file
   - Check the key is at least 16 characters long

2. **"Must set a strong Neo4j password in production"**
   - Change NEO4J_PASSWORD from the default "password"
   - Use a password at least 8 characters long

3. **"Remove localhost from CORS origins in production"**
   - Update API_CORS_ORIGINS to use your actual domain
   - Remove any localhost entries

## Contact

For security concerns or questions, please contact the development team.
