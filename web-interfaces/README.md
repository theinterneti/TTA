# TTA Web Interfaces

Comprehensive web-based user interfaces for the TTA (Therapeutic Text Adventure) system, providing specialized interfaces for different stakeholder types.

## Overview

The TTA Web Interfaces consist of seven specialized applications:

1. **Patient/Player Interface** (Port 3000) - Therapeutic gaming experience
2. **Clinical Dashboard** (Port 3001) - Healthcare provider monitoring
3. **System Administrator Interface** (Port 3002) - System management
4. **Public Information Portal** (Port 3003) - General information and research
5. **Stakeholder Dashboard** (Port 3004) - Research and oversight data
6. **Enhanced API Documentation** (Port 3005) - Interactive API documentation
7. **Developer Interface** (Port 3006) - Unified development dashboard

## Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Node.js 18+ (for development)
- nginx (included in Docker setup)

### Development Setup

```bash
# Clone and navigate to the web interfaces directory
cd web-interfaces

# Set up development environment
./deploy.sh development setup

# Start all interfaces in development mode
./deploy.sh development deploy
```

### Production Deployment

```bash
# Deploy to production
./deploy.sh production deploy

# Check deployment status
./deploy.sh production status

# View logs
./deploy.sh production logs
```

## Architecture

### Port Assignment

```
Port 80:   nginx Reverse Proxy (Production)
Port 3000: Patient/Player Interface
Port 3001: Clinical Dashboard
Port 3002: System Administrator Interface
Port 3003: Public Information Portal
Port 3004: Stakeholder Dashboard
Port 3005: API Documentation Portal
Port 3006: Developer Interface
```

### URL Structure

```
http://localhost/           → Patient Interface
http://localhost/clinical   → Clinical Dashboard
http://localhost/admin      → Admin Interface
http://localhost/public     → Public Portal
http://localhost/stakeholder → Stakeholder Dashboard
http://localhost/docs       → API Documentation
http://localhost/dev        → Developer Interface
```

### Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit + React Query
- **UI Libraries**:
  - Tailwind CSS (Patient, Public)
  - Material-UI (Clinical)
  - Ant Design (Admin)
- **Build Tools**: Vite (development), Docker (production)
- **Reverse Proxy**: nginx

## Interface Details

### 1. Patient/Player Interface

**Purpose**: Therapeutic gaming experience for patients/users

**Features**:

- Character creation and management
- World exploration and navigation
- Real-time therapeutic chat interface
- Progress tracking and achievements
- Settings and privacy controls
- Crisis support integration

**Technology**: React + TypeScript + Tailwind CSS + Framer Motion

**Authentication**: JWT-based patient authentication

### 2. Clinical Dashboard

**Purpose**: Healthcare provider monitoring and oversight

**Features**:

- Real-time patient monitoring displays
- Therapeutic progress analytics and visualizations
- Crisis alert management system
- Clinical outcome measurement tools
- HIPAA-compliant audit logs and reporting
- Professional healthcare UI design

**Technology**: React + TypeScript + Material-UI + Chart.js

**Authentication**: Healthcare provider JWT with role-based access

### 3. System Administrator Interface

**Purpose**: System management and administration

**Features**:

- Service status monitoring and control
- User and role management
- System configuration interface
- Performance metrics and diagnostics
- Database administration tools
- Security audit and monitoring

**Technology**: React + TypeScript + Ant Design + Monaco Editor

**Authentication**: Administrator JWT with elevated privileges

### 4. Public Information Portal

**Purpose**: General information about TTA system and research

**Features**:

- Research findings and publications
- Therapeutic approaches documentation
- System information and capabilities
- Contact and support information
- Accessibility-focused design

**Technology**: Next.js + TypeScript + Tailwind CSS

**Authentication**: None (public access)

### 5. Stakeholder Dashboard

**Purpose**: Researchers and oversight bodies data access

**Features**:

- Aggregated, anonymized analytics
- System performance metrics
- Research data visualization
- Export capabilities for reports
- Read-only access to system insights

**Technology**: React + TypeScript + Chart.js + D3.js

**Authentication**: Stakeholder JWT with read-only access

### 6. Enhanced API Documentation Portal

**Purpose**: Interactive API documentation and testing

**Features**:

- Interactive API documentation
- API testing interface with live examples
- Code generation for multiple languages
- Authentication flow testing
- WebSocket endpoint documentation

**Technology**: React + TypeScript + Swagger UI + Monaco Editor

**Authentication**: Developer JWT (optional)

### 7. Developer Interface

**Purpose**: Unified development dashboard for TTA interface ecosystem

**Features**:

- Interface navigation hub with embedded previews
- Authentication switcher for testing different user roles
- Real-time health monitoring and status indicators
- API testing panel with pre-configured endpoints
- Environment switcher and JWT token utilities
- Live reload monitoring and build status reporting
- Performance metrics and accessibility testing
- Network request monitoring and debugging tools

**Technology**: React + TypeScript + Tailwind CSS + Framer Motion

**Authentication**: Developer JWT (optional, with bypass for local development)

## Security Features

### Authentication & Authorization

- **JWT-based authentication** with role-based access control
- **Interface-specific authentication** boundaries
- **Secure token handling** with httpOnly cookies
- **Session management** with automatic token refresh

### HIPAA Compliance (Clinical Dashboard)

- **Audit logging** for all clinical data access
- **Data encryption** in transit and at rest
- **Access controls** with healthcare provider verification
- **Privacy protection** with data anonymization

### Security Headers

- **Content Security Policy** (CSP)
- **X-Frame-Options** for clickjacking protection
- **X-Content-Type-Options** for MIME type sniffing protection
- **Referrer Policy** for privacy protection

## Accessibility

All interfaces comply with **WCAG 2.1 AA** guidelines:

- **Keyboard navigation** support
- **Screen reader** compatibility
- **High contrast mode** support
- **Focus management** and visual indicators
- **Semantic HTML** structure
- **Alternative text** for images
- **Proper heading hierarchy**

## Responsive Design

### Breakpoints

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Interface-Specific Design

- **Patient Interface**: Mobile-first for accessibility
- **Clinical Dashboard**: Desktop-optimized for professional use
- **Admin Interface**: Desktop-focused with responsive elements
- **Public Portal**: Fully responsive for all devices

## Development

### Local Development

```bash
# Start individual interface in development mode
cd patient-interface
npm run dev

# Or start all interfaces
./deploy.sh development deploy
```

### Testing

```bash
# Run tests for all interfaces
./deploy.sh development test

# Run tests for specific interface
cd clinical-dashboard
npm test
```

### Building

```bash
# Build all interfaces
./deploy.sh production build

# Build specific interface
cd admin-interface
npm run build
```

## Deployment

### Docker Deployment

```bash
# Deploy all interfaces with Docker
./deploy.sh production deploy

# Check deployment health
./deploy.sh production health
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n tta-web-interfaces
```

## Monitoring

### Health Checks

Each interface includes health check endpoints:

- `GET /health` - Basic health status
- Docker health checks with automatic restart
- nginx upstream health monitoring

### Logging

- **Structured logging** with JSON format
- **Centralized log aggregation** via Docker
- **Error tracking** with stack traces
- **Performance monitoring** with metrics

## Configuration

### Environment Variables

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=ws://localhost:8080

# Security
REACT_APP_JWT_SECRET_KEY=your-secret-key

# Feature Flags
REACT_APP_HIPAA_MODE=true
REACT_APP_READ_ONLY_MODE=false
```

### nginx Configuration

Custom nginx configuration in `nginx/nginx.conf`:

- **Reverse proxy** routing
- **SSL/TLS termination**
- **Static file serving**
- **Compression** and caching
- **Security headers**

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000-3005 are available
2. **Authentication errors**: Check JWT configuration and API connectivity
3. **CORS issues**: Verify CORS origins in backend configuration
4. **Build failures**: Check Node.js version and dependency compatibility

### Debugging

```bash
# View logs for all services
./deploy.sh production logs

# Check service health
./deploy.sh production health

# Restart specific service
docker-compose restart patient-interface
```

## Contributing

1. Follow the established code style and linting rules
2. Write tests for new features
3. Ensure accessibility compliance
4. Update documentation for changes
5. Test across different browsers and devices

## License

This project is part of the TTA (Therapeutic Text Adventure) system and follows the same licensing terms.
