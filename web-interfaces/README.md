# TTA Web Interfaces

Comprehensive web-based user interfaces for the TTA (Therapeutic Text Adventure) system, providing specialized interfaces for different stakeholder types with clinical-grade reliability and enhanced therapeutic backend integration.

## 🎯 **Current Status - December 2024**

**✅ OPERATIONAL INTERFACES:**

- **Patient/Player Interface** (Port 5173) - ✅ **FULLY FUNCTIONAL** with authentication
- **Developer Interface** (Port 3006) - ✅ **FULLY OPERATIONAL** with comprehensive testing tools
- **Clinical Dashboard** (Port 3001) - ✅ **INFRASTRUCTURE READY** (authentication pending)

**🚧 IN DEVELOPMENT:**

- **System Administrator Interface** (Port 3002) - Infrastructure ready
- **Public Information Portal** (Port 3003) - Infrastructure ready
- **Stakeholder Dashboard** (Port 3004) - Infrastructure ready
- **Enhanced API Documentation** (Port 3005) - Infrastructure ready

## Overview

The TTA Web Interfaces consist of seven specialized applications with **enhanced therapeutic backend integration** following recent 60% code quality improvements:

1. **Patient/Player Interface** (Port 5173) - ✅ **FUNCTIONAL** - Therapeutic gaming experience
2. **Clinical Dashboard** (Port 3001) - 🚧 **READY** - Healthcare provider monitoring
3. **System Administrator Interface** (Port 3002) - 📋 **PLANNED** - System management
4. **Public Information Portal** (Port 3003) - 📋 **PLANNED** - General information and research
5. **Stakeholder Dashboard** (Port 3004) - 📋 **PLANNED** - Research and oversight data
6. **Enhanced API Documentation** (Port 3005) - 📋 **PLANNED** - Interactive API documentation
7. **Developer Interface** (Port 3006) - ✅ **OPERATIONAL** - Unified development dashboard

## 🔑 **Test Credentials - Ready for Use**

The system includes comprehensive test credentials for all user roles:

| **Role**           | **Username**   | **Password**   | **Interface Access**         | **Permissions**                       |
| ------------------ | -------------- | -------------- | ---------------------------- | ------------------------------------- |
| **Patient/Player** | `test_patient` | `patient123`   | Patient Interface (5173)     | Therapeutic gaming, progress tracking |
| **Clinician**      | `dr_smith`     | `clinician123` | Clinical Dashboard (3001)    | Patient monitoring, clinical notes    |
| **Administrator**  | `admin`        | `admin123`     | All Interfaces               | Full system access                    |
| **Researcher**     | `researcher`   | `research123`  | Stakeholder Dashboard (3004) | Read-only analytics                   |
| **Developer**      | `developer`    | `dev123`       | Developer Interface (3006)   | API access, debugging                 |

## 🏗️ **Enhanced Architecture - Recent Improvements**

### **Shared Component Library**

- ✅ **ErrorBoundary**: Clinical-grade error handling with therapeutic messaging
- ✅ **LoadingSpinner**: Therapeutic-themed loading indicators
- ✅ **ProtectedRoute**: Role-based access control with detailed permission checking
- ✅ **AuthProvider**: Integrated authentication with backend API (localhost:8080)

### **Code Quality Improvements (60% Enhancement)**

- ✅ **B904 Exception Chaining**: Therapeutic debugging vs user-facing error handling
- ✅ **F811 Symbol Cleanup**: Eliminated duplicate class definitions
- ✅ **E402 Import Organization**: PEP 8 compliant import structure
- ✅ **F821 Undefined Names**: Enhanced component integration

### **Backend Integration**

- ✅ **CharacterArcManagerComponent**: Ready for frontend integration
- ✅ **NarrativeArcOrchestratorComponent**: Enhanced with recent improvements
- ✅ **SafetyValidationOrchestrator**: Enhanced with ValidationTimeoutEvent
- ✅ **DynamicStoryGenerationService**: Import issues resolved

## Quick Start

### Prerequisites

- Node.js 18+ (for development)
- Enhanced TTA Backend Systems (operational)
- Docker 20.10+ and Docker Compose 2.0+ (optional)

### Development Setup - Current Working State

```bash
# Navigate to TTA project root
cd /path/to/TTA

# Start the enhanced backend systems (if not already running)
# The therapeutic systems are operational and ready for integration

# Start Patient Interface (FUNCTIONAL)
cd web-interfaces/patient-interface
npm install
npm run dev
# Access at: http://localhost:5173
# Login with: test_patient / patient123

# Start Developer Interface (OPERATIONAL)
cd ../developer-interface
npm install
npm run dev
# Access at: http://localhost:3006
# No authentication required for development

# Start Clinical Dashboard (INFRASTRUCTURE READY)
cd ../clinical-dashboard
npm install
npm run dev
# Access at: http://localhost:3001
# Login with: dr_smith / clinician123 (authentication pending)
```

### Quick Access URLs

| **Interface**       | **URL**                 | **Status**         | **Test Login**            |
| ------------------- | ----------------------- | ------------------ | ------------------------- |
| Patient Interface   | `http://localhost:5173` | ✅ **FUNCTIONAL**  | test_patient / patient123 |
| Developer Interface | `http://localhost:3006` | ✅ **OPERATIONAL** | No auth required          |
| Clinical Dashboard  | `http://localhost:3001` | 🚧 **READY**       | dr_smith / clinician123   |

### Production Deployment

```bash
# Traditional deployment (when Docker permissions resolved)
./deploy.sh production deploy

# Alternative: Node.js direct deployment
cd web-interfaces/patient-interface && npm run build && npm run preview
cd ../clinical-dashboard && npm run build && npm run preview
cd ../developer-interface && npm run build && npm run preview

# Check deployment status
./deploy.sh production status

# View logs
./deploy.sh production logs
```

## 🚀 **Development Roadmap - Sprint-Based Structure**

### **Current Sprint Status**

**✅ Phase 1: Critical Infrastructure Components - COMPLETE**

- Shared component library structure (ErrorBoundary, LoadingSpinner, ProtectedRoute)
- Basic authentication integration with backend API
- Patient Interface fully functional with test credentials

**🔥 Phase 2: Therapeutic-Specific Components - IN PROGRESS**

- CrisisSupport component (integrating with SafetyValidationOrchestrator)
- TherapeuticThemeProvider (WCAG-compliant therapeutic themes)
- HIPAAComplianceProvider (clinical dashboard compliance)
- AccessibilityProvider (screen reader, keyboard navigation)

**📋 Phase 3: Authentication Pages - PLANNED**

- Clinical Dashboard authentication (HIPAA-compliant)
- Admin Interface authentication (enhanced security)
- Stakeholder Dashboard authentication (read-only access)

**📈 Phase 4-6: Advanced Features - PLANNED**

- Core dashboard components for all interfaces
- Therapeutic gaming components (CharacterCreation, TherapeuticChat)
- Clinical monitoring and analytics components

### **Sprint Timeline**

| **Sprint**   | **Duration** | **Focus**           | **Deliverables**                        |
| ------------ | ------------ | ------------------- | --------------------------------------- |
| **Sprint 1** | Week 1       | Foundation & Safety | CrisisSupport, TherapeuticThemeProvider |
| **Sprint 2** | Week 2       | Authentication      | All interface login pages               |
| **Sprint 3** | Week 3       | Core Dashboards     | Clinical and admin dashboards           |
| **Sprint 4** | Week 4       | Therapeutic Gaming  | CharacterCreation, TherapeuticChat      |
| **Sprint 5** | Week 5       | Clinical Monitoring | Advanced analytics and monitoring       |

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
