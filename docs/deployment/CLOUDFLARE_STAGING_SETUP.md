# 🌐 Cloudflare Staging Setup for TTA Storytelling Platform

## 📋 Overview

This guide configures Cloudflare-managed staging URLs for your TTA (Therapeutic Text Adventure) storytelling platform using your domain `theinterneti.com`.

## 🎯 Staging URL Structure

### **Recommended Subdomain Strategy**

```
Production:
├── tta.theinterneti.com              # Main patient interface
├── api.tta.theinterneti.com          # API endpoints
├── clinical.tta.theinterneti.com     # Clinical dashboard
└── admin.tta.theinterneti.com        # Admin interface

Staging:
├── staging-tta.theinterneti.com      # Staging patient interface
├── api-staging.tta.theinterneti.com  # Staging API endpoints
├── clinical-staging.tta.theinterneti.com  # Staging clinical dashboard
└── admin-staging.tta.theinterneti.com     # Staging admin interface
```

### **Alternative Subdomain Strategy (Shorter)**

```
Production:
├── tta.theinterneti.com              # Main patient interface
├── api.theinterneti.com/tta          # API endpoints
├── clinical.theinterneti.com         # Clinical dashboard
└── admin.theinterneti.com            # Admin interface

Staging:
├── staging.theinterneti.com          # Staging patient interface
├── api-staging.theinterneti.com      # Staging API endpoints
├── clinical-staging.theinterneti.com # Staging clinical dashboard
└── admin-staging.theinterneti.com    # Staging admin interface
```

## 🔧 Cloudflare DNS Configuration

### **Step 1: DNS Records Setup**

Add these DNS records in your Cloudflare dashboard:

```dns
# Staging Environment
CNAME  staging-tta              your-staging-server.com
CNAME  api-staging              your-staging-server.com
CNAME  clinical-staging         your-staging-server.com
CNAME  admin-staging            your-staging-server.com

# Production Environment (for reference)
CNAME  tta                      your-production-server.com
CNAME  api                      your-production-server.com
CNAME  clinical                 your-production-server.com
CNAME  admin                    your-production-server.com
```

### **Step 2: SSL/TLS Configuration**

1. **SSL/TLS Mode**: Full (strict)
2. **Edge Certificates**: Universal SSL enabled
3. **Always Use HTTPS**: Enabled
4. **HSTS**: Enabled with 6 months max-age
5. **Minimum TLS Version**: 1.2

### **Step 3: Security Settings**

```yaml
Security Level: Medium
Bot Fight Mode: Enabled
Browser Integrity Check: Enabled
Challenge Passage: 30 minutes
Security Level: Medium
```

## 🚀 GitHub Secrets and Variables Configuration

### **Required GitHub Secrets**

```bash
# Set staging-specific secrets
gh secret set STAGING_API_URL --body "https://api-staging.tta.theinterneti.com"
gh secret set STAGING_WEB_URL --body "https://staging-tta.theinterneti.com"
gh secret set STAGING_CLINICAL_URL --body "https://clinical-staging.tta.theinterneti.com"
gh secret set STAGING_ADMIN_URL --body "https://admin-staging.tta.theinterneti.com"

# Database and infrastructure secrets (staging-specific)
gh secret set STAGING_DATABASE_URL --body "postgresql://user:pass@staging-db.com:5432/tta_staging"
gh secret set STAGING_REDIS_URL --body "redis://staging-redis.com:6379"
gh secret set STAGING_NEO4J_URL --body "bolt://staging-neo4j.com:7687"
gh secret set STAGING_NEO4J_PASSWORD --body "your-staging-neo4j-password"

# Sentry configuration for staging
gh secret set STAGING_SENTRY_DSN --body "https://your-staging-sentry-dsn@sentry.io/project-id"
```

### **Required GitHub Variables**

```bash
# Set staging environment variables
gh variable set STAGING_ENVIRONMENT --body "staging"
gh variable set STAGING_DEBUG --body "false"
gh variable set STAGING_LOG_LEVEL --body "INFO"

# Performance and scaling settings
gh variable set STAGING_MAX_CONCURRENT_SESSIONS --body "500"
gh variable set STAGING_RATE_LIMIT_CALLS --body "1000"
gh variable set STAGING_RATE_LIMIT_PERIOD --body "60"

# Feature flags for staging
gh variable set STAGING_FEATURE_REAL_TIME_MONITORING --body "true"
gh variable set STAGING_FEATURE_ADVANCED_ANALYTICS --body "true"
gh variable set STAGING_FEATURE_BETA_FEATURES --body "true"
```

## 📦 Docker Compose Configuration Update

Update your `docker-compose.staging.yml` with the new URLs:

```yaml
version: '3.8'

services:
  # Player Experience API - Staging
  player-experience-api:
    build:
      context: .
      dockerfile: src/player_experience/Dockerfile
    container_name: tta-player-experience-api-staging
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=staging
      - API_HOST=0.0.0.0
      - API_PORT=8080
      - API_DEBUG=false
      - API_LOG_LEVEL=INFO

      # Staging URLs
      - STAGING_API_URL=https://api-staging.tta.theinterneti.com
      - STAGING_WEB_URL=https://staging-tta.theinterneti.com
      - STAGING_CLINICAL_URL=https://clinical-staging.tta.theinterneti.com

      # CORS Configuration for staging
      - API_CORS_ORIGINS=https://staging-tta.theinterneti.com,https://clinical-staging.tta.theinterneti.com,https://admin-staging.tta.theinterneti.com

      # Database connections
      - DATABASE_URL=${STAGING_DATABASE_URL}
      - REDIS_URL=${STAGING_REDIS_URL}
      - NEO4J_URL=${STAGING_NEO4J_URL}
      - NEO4J_PASSWORD=${STAGING_NEO4J_PASSWORD}

      # Monitoring
      - SENTRY_DSN=${STAGING_SENTRY_DSN}
      - SENTRY_ENVIRONMENT=staging
      - SENTRY_TRACES_SAMPLE_RATE=0.2

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api-staging.rule=Host(`api-staging.tta.theinterneti.com`)"
      - "traefik.http.routers.api-staging.tls=true"
      - "traefik.http.routers.api-staging.tls.certresolver=letsencrypt"

  # Web Interface - Staging
  web-interface:
    build:
      context: ./web-interfaces/patient
      dockerfile: Dockerfile.staging
    container_name: tta-web-interface-staging
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=staging
      - REACT_APP_API_URL=https://api-staging.tta.theinterneti.com
      - REACT_APP_WS_URL=wss://api-staging.tta.theinterneti.com
      - REACT_APP_SENTRY_DSN=${STAGING_SENTRY_DSN}
      - REACT_APP_ENVIRONMENT=staging

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web-staging.rule=Host(`staging-tta.theinterneti.com`)"
      - "traefik.http.routers.web-staging.tls=true"
      - "traefik.http.routers.web-staging.tls.certresolver=letsencrypt"

networks:
  default:
    name: tta-staging-network
```

## 🔄 Nginx Configuration for Staging

Create `nginx/staging.conf`:

```nginx
# Staging configuration for TTA
server {
    listen 80;
    server_name staging-tta.theinterneti.com api-staging.tta.theinterneti.com clinical-staging.tta.theinterneti.com admin-staging.tta.theinterneti.com;
    return 301 https://$server_name$request_uri;
}

# Main staging interface
server {
    listen 443 ssl http2;
    server_name staging-tta.theinterneti.com;

    ssl_certificate /etc/ssl/certs/staging.crt;
    ssl_certificate_key /etc/ssl/private/staging.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://web-interface:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API staging interface
server {
    listen 443 ssl http2;
    server_name api-staging.tta.theinterneti.com;

    ssl_certificate /etc/ssl/certs/staging.crt;
    ssl_certificate_key /etc/ssl/private/staging.key;

    location / {
        proxy_pass http://player-experience-api:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🧪 Testing and Validation

### **Step 1: DNS Propagation Check**

```bash
# Check DNS propagation
dig staging-tta.theinterneti.com
dig api-staging.tta.theinterneti.com
dig clinical-staging.tta.theinterneti.com

# Test SSL certificates
curl -I https://staging-tta.theinterneti.com
curl -I https://api-staging.tta.theinterneti.com
```

### **Step 2: Application Health Checks**

```bash
# Test API endpoints
curl https://api-staging.tta.theinterneti.com/health
curl https://api-staging.tta.theinterneti.com/api/v1/health

# Test web interface
curl -I https://staging-tta.theinterneti.com
```

### **Step 3: End-to-End Testing**

```bash
# Run staging deployment test
python src/player_experience/test_deployment.py \
  --host staging-tta.theinterneti.com \
  --port 443 \
  --environment staging \
  --output staging-test-results.json
```

## 📊 Monitoring and Alerting

### **Cloudflare Analytics**

1. **Enable Analytics**: Turn on detailed analytics for all staging subdomains
2. **Set up Alerts**: Configure alerts for:
   - High error rates (>5%)
   - Slow response times (>2s)
   - SSL certificate expiration
   - DDoS attacks

### **Application Monitoring**

```yaml
# Add to your monitoring configuration
staging_endpoints:
  - name: "Staging Web Interface"
    url: "https://staging-tta.theinterneti.com"
    expected_status: 200
    check_interval: 60s

  - name: "Staging API Health"
    url: "https://api-staging.tta.theinterneti.com/health"
    expected_status: 200
    check_interval: 30s

  - name: "Staging API Docs"
    url: "https://api-staging.tta.theinterneti.com/docs"
    expected_status: 200
    check_interval: 300s
```

## 🚀 Deployment Script Update

Update your `scripts/deploy-staging.sh` to use the new URLs:

```bash
#!/bin/bash

# Staging deployment configuration
STAGING_DOMAIN="theinterneti.com"
STAGING_WEB_URL="https://staging-tta.${STAGING_DOMAIN}"
STAGING_API_URL="https://api-staging.tta.${STAGING_DOMAIN}"
STAGING_CLINICAL_URL="https://clinical-staging.tta.${STAGING_DOMAIN}"

# Export environment variables
export STAGING_API_URL
export STAGING_WEB_URL
export STAGING_CLINICAL_URL

echo "🚀 Deploying TTA Staging Environment"
echo "Web Interface: $STAGING_WEB_URL"
echo "API Endpoint: $STAGING_API_URL"
echo "Clinical Dashboard: $STAGING_CLINICAL_URL"

# Deploy with docker-compose
docker-compose -f docker-compose.staging.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🔍 Running health checks..."
curl -f "$STAGING_API_URL/health" || exit 1
curl -f "$STAGING_WEB_URL" || exit 1

echo "✅ Staging deployment completed successfully!"
echo "🌐 Access your staging environment at: $STAGING_WEB_URL"
```

## ✅ Next Steps

1. **Configure Cloudflare DNS** with the recommended subdomains
2. **Set GitHub Secrets and Variables** using the provided commands
3. **Update Docker Compose** configuration with new URLs
4. **Deploy Staging Environment** using the updated deployment script
5. **Test All Endpoints** to ensure proper functionality
6. **Set up Monitoring** for the staging environment

Your TTA staging environment will be accessible at:
- **Main Interface**: https://staging-tta.theinterneti.com
- **API Documentation**: https://api-staging.tta.theinterneti.com/docs
- **Health Check**: https://api-staging.tta.theinterneti.com/health

This setup provides a production-like staging environment with proper SSL, monitoring, and Cloudflare protection! 🎉
