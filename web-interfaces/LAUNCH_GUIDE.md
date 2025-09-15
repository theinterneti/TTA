# TTA Web Interfaces - Complete Launch Guide

## Overview

This guide provides comprehensive instructions for launching all TTA web interfaces, including the enhanced patient interface, clinical dashboard, admin panel, and specialized interfaces.

## Interface Portfolio

### 1. Patient/Player Web Interface (Port 3000)

- **URL**: `http://localhost:3000` or `http://localhost/`
- **Purpose**: Enhanced therapeutic gaming experience
- **Technology**: React 18 + TypeScript + Tailwind CSS + Framer Motion
- **Authentication**: JWT-based patient authentication

### 2. Clinical Dashboard Web Interface (Port 3001)

- **URL**: `http://localhost:3001` or `http://localhost/clinical`
- **Purpose**: Healthcare provider monitoring and oversight
- **Technology**: React 18 + TypeScript + Material-UI + Chart.js
- **Authentication**: Healthcare provider JWT with HIPAA compliance

### 3. System Administrator Web Interface (Port 3002)

- **URL**: `http://localhost:3002` or `http://localhost/admin`
- **Purpose**: System management and administration
- **Technology**: React 18 + TypeScript + Ant Design + Monaco Editor
- **Authentication**: Administrator JWT with elevated privileges

### 4. Public Information Portal (Port 3003)

- **URL**: `http://localhost:3003` or `http://localhost/public`
- **Purpose**: General information and research findings
- **Technology**: Next.js + TypeScript + Tailwind CSS
- **Authentication**: None (public access)

### 5. Stakeholder Dashboard (Port 3004)

- **URL**: `http://localhost:3004` or `http://localhost/stakeholder`
- **Purpose**: Research and oversight data access
- **Technology**: React 18 + TypeScript + Chart.js + D3.js
- **Authentication**: Stakeholder JWT with read-only access

### 6. Enhanced API Documentation Portal (Port 3005)

- **URL**: `http://localhost:3005` or `http://localhost/docs`
- **Purpose**: Interactive API documentation and testing
- **Technology**: React 18 + TypeScript + Swagger UI + Monaco Editor
- **Authentication**: Developer JWT (optional)

### 7. Developer Interface (Port 3006)

- **URL**: `http://localhost:3006` or `http://localhost/dev`
- **Purpose**: Unified development dashboard for TTA interface ecosystem
- **Technology**: React 18 + TypeScript + Tailwind CSS + Framer Motion
- **Authentication**: Developer JWT (optional, with bypass for local development)

## Prerequisites

### System Requirements

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Node.js**: 18+ (for development)
- **Memory**: 8GB RAM recommended for all interfaces
- **Storage**: 20GB free space

### Backend Services

Ensure the following TTA backend services are running:

- **Player Experience API**: Port 8080
- **API Gateway**: Port 8000
- **Agent Orchestration**: Port 8503
- **Neo4j Database**: Port 7687
- **Redis Cache**: Port 6379

## Quick Launch (All Interfaces)

### Option 1: Docker Deployment (Recommended)

```bash
# Navigate to web interfaces directory
cd web-interfaces

# Deploy all interfaces with one command
./deploy.sh production deploy

# Check deployment status
./deploy.sh production status

# Access interfaces via nginx proxy
# Patient Interface:      http://localhost/
# Clinical Dashboard:     http://localhost/clinical
# Admin Interface:        http://localhost/admin
# Public Portal:          http://localhost/public
# Stakeholder Dashboard:  http://localhost/stakeholder
# API Documentation:      http://localhost/docs
# Developer Interface:    http://localhost/dev
```

### Option 2: Development Mode

```bash
# Set up development environment
./deploy.sh development setup

# Start all interfaces in development mode
./deploy.sh development deploy

# Access interfaces directly on their ports
# Patient Interface:      http://localhost:3000
# Clinical Dashboard:     http://localhost:3001
# Admin Interface:        http://localhost:3002
# Public Portal:          http://localhost:3003
# Stakeholder Dashboard:  http://localhost:3004
# API Documentation:      http://localhost:3005
# Developer Interface:    http://localhost:3006
```

## Individual Interface Launch

### Patient/Player Interface

```bash
# Development
cd web-interfaces/patient-interface
npm install
npm run dev
# Access: http://localhost:3000

# Production
docker build -t tta-patient-interface .
docker run -p 3000:3000 tta-patient-interface
```

### Clinical Dashboard

```bash
# Development
cd web-interfaces/clinical-dashboard
npm install
npm run dev
# Access: http://localhost:3001

# Production
docker build -t tta-clinical-dashboard .
docker run -p 3001:3001 tta-clinical-dashboard
```

### System Administrator Interface

```bash
# Development
cd web-interfaces/admin-interface
npm install
npm run dev
# Access: http://localhost:3002

# Production
docker build -t tta-admin-interface .
docker run -p 3002:3002 tta-admin-interface
```

### Public Information Portal

```bash
# Development
cd web-interfaces/public-portal
npm install
npm run dev
# Access: http://localhost:3003

# Production
docker build -t tta-public-portal .
docker run -p 3003:3003 tta-public-portal
```

### Stakeholder Dashboard

```bash
# Development
cd web-interfaces/stakeholder-dashboard
npm install
npm run dev
# Access: http://localhost:3004

# Production
docker build -t tta-stakeholder-dashboard .
docker run -p 3004:3004 tta-stakeholder-dashboard
```

### API Documentation Portal

```bash
# Development
cd web-interfaces/api-docs-portal
npm install
npm run dev
# Access: http://localhost:3005

# Production
docker build -t tta-api-docs-portal .
docker run -p 3005:3005 tta-api-docs-portal
```

### Developer Interface

```bash
# Development
cd web-interfaces/developer-interface
npm install
npm run dev
# Access: http://localhost:3006

# Production
docker build -t tta-developer-interface .
docker run -p 3006:3006 tta-developer-interface
```

## Environment Configuration

### Required Environment Variables

Create `.env` files for each interface or set globally:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=ws://localhost:8080
REACT_APP_GATEWAY_URL=http://localhost:8000
REACT_APP_AGENT_URL=http://localhost:8503

# Security
REACT_APP_JWT_SECRET_KEY=your-very-secure-secret-key-here

# Feature Flags
REACT_APP_HIPAA_MODE=true          # Clinical Dashboard
REACT_APP_READ_ONLY_MODE=true      # Stakeholder Dashboard
REACT_APP_DEBUG_MODE=false         # All interfaces

# CORS Configuration
REACT_APP_CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
```

## Authentication Setup

### User Roles and Access

- **Patient**: Access to Patient Interface only
- **Clinician**: Access to Clinical Dashboard and Patient Interface
- **Admin**: Access to all interfaces
- **Stakeholder**: Access to Stakeholder Dashboard (read-only)
- **Developer**: Access to API Documentation Portal
- **Public**: Access to Public Portal (no authentication)

### JWT Configuration

Ensure backend APIs are configured with matching JWT settings:

```bash
# Backend API Configuration
API_JWT_SECRET_KEY=your-very-secure-secret-key-here
API_ACCESS_TOKEN_EXPIRE_MINUTES=30
API_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Health Checks and Monitoring

### Verify All Services

```bash
# Check all interface health
./deploy.sh production health

# Individual health checks
curl http://localhost:3000/health  # Patient Interface
curl http://localhost:3001/health  # Clinical Dashboard
curl http://localhost:3002/health  # Admin Interface
curl http://localhost:3003/health  # Public Portal
curl http://localhost:3004/health  # Stakeholder Dashboard
curl http://localhost:3005/health  # API Documentation
curl http://localhost:3006/health  # Developer Interface

# nginx proxy health
curl http://localhost/health
```

### Monitoring Commands

```bash
# View logs for all services
./deploy.sh production logs

# View logs for specific service
docker-compose logs -f patient-interface

# Check resource usage
docker stats

# Monitor nginx access logs
docker-compose logs -f nginx-proxy
```

## Security Considerations

### HTTPS Configuration (Production)

```bash
# Generate SSL certificates
mkdir -p web-interfaces/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout web-interfaces/nginx/ssl/nginx.key \
  -out web-interfaces/nginx/ssl/nginx.crt

# Update nginx configuration for HTTPS
# Edit web-interfaces/nginx/nginx.conf to include SSL settings
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 3000:3005/tcp  # Block direct access to interfaces
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**

   ```bash
   # Check port usage
   netstat -tulpn | grep :3000

   # Kill processes using ports
   sudo fuser -k 3000/tcp
   ```

2. **Authentication Errors**

   ```bash
   # Check JWT configuration
   echo $REACT_APP_JWT_SECRET_KEY

   # Verify API connectivity
   curl http://localhost:8080/health
   ```

3. **CORS Issues**

   ```bash
   # Check CORS configuration in backend
   curl -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS http://localhost:8080/api/v1/health
   ```

4. **Build Failures**

   ```bash
   # Clear npm cache
   npm cache clean --force

   # Remove node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Log Analysis

```bash
# Search for errors in logs
./deploy.sh production logs | grep -i error

# Monitor real-time logs
./deploy.sh production logs -f

# Check specific service logs
docker-compose logs -f clinical-dashboard
```

## Performance Optimization

### Production Optimizations

```bash
# Enable gzip compression in nginx
# Configure caching headers
# Optimize Docker images with multi-stage builds
# Use CDN for static assets
```

### Resource Limits

```bash
# Set Docker resource limits
docker-compose up -d --scale patient-interface=2
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration files
tar -czf tta-web-config-$(date +%Y%m%d).tar.gz \
  web-interfaces/nginx/ \
  web-interfaces/config/ \
  web-interfaces/.env*
```

### Service Recovery

```bash
# Restart failed services
./deploy.sh production restart

# Rebuild and redeploy
./deploy.sh production build
./deploy.sh production deploy
```

This comprehensive launch guide provides all necessary information to successfully deploy and manage the TTA web interfaces in both development and production environments.
