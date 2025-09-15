# TTA Web Interface Architecture

## Overview

The TTA system provides comprehensive web-based user interfaces for different stakeholder types, each optimized for specific use cases and security requirements.

## Interface Portfolio

### 1. Patient/Player Web Interface (Port 3000)
- **Purpose**: Therapeutic gaming experience for patients/users
- **Technology**: React 18 + TypeScript + Tailwind CSS
- **Features**: Character creation, world exploration, therapeutic chat, progress tracking
- **Authentication**: JWT-based patient authentication
- **URL**: `http://localhost:3000`

### 2. Clinical Dashboard Web Interface (Port 3001)
- **Purpose**: Healthcare provider monitoring and oversight
- **Technology**: React 18 + TypeScript + Material-UI
- **Features**: Real-time patient monitoring, analytics, crisis alerts, outcome measurement
- **Authentication**: Healthcare provider JWT with role-based access
- **URL**: `http://localhost:3001`

### 3. System Administrator Web Interface (Port 3002)
- **Purpose**: System management and administration
- **Technology**: React 18 + TypeScript + Ant Design
- **Features**: User management, system monitoring, configuration, database admin
- **Authentication**: Administrator JWT with elevated privileges
- **URL**: `http://localhost:3002`

### 4. Public Information Portal (Port 3003)
- **Purpose**: General information about TTA system and research
- **Technology**: Next.js + TypeScript + Tailwind CSS
- **Features**: Research findings, therapeutic approaches, system information
- **Authentication**: None (public access)
- **URL**: `http://localhost:3003`

### 5. Stakeholder Dashboard (Port 3004)
- **Purpose**: Researchers and oversight bodies data access
- **Technology**: React 18 + TypeScript + Chart.js
- **Features**: Aggregated analytics, system performance, research data
- **Authentication**: Stakeholder JWT with read-only access
- **URL**: `http://localhost:3004`

### 6. Enhanced API Documentation Portal (Port 3005)
- **Purpose**: Interactive API documentation and testing
- **Technology**: React 18 + TypeScript + Swagger UI
- **Features**: Interactive API docs, testing interface, code examples
- **Authentication**: Developer JWT (optional)
- **URL**: `http://localhost:3005`

## Port Assignment Strategy

```
3000: Patient/Player Interface (Primary user interface)
3001: Clinical Dashboard (Healthcare providers)
3002: System Administrator (System management)
3003: Public Portal (No authentication required)
3004: Stakeholder Dashboard (Research/oversight)
3005: API Documentation (Developer tools)

8000: API Gateway (Existing)
8080: Player Experience API (Existing)
8503: Agent Orchestration (Existing)
```

## Technology Stack

### Frontend Framework
- **React 18** with TypeScript for all interfaces
- **Next.js** for Public Portal (SSR/SSG capabilities)
- **Vite** for development build optimization

### UI Libraries
- **Tailwind CSS**: Patient/Player Interface, Public Portal
- **Material-UI (MUI)**: Clinical Dashboard (professional healthcare UI)
- **Ant Design**: System Administrator Interface (comprehensive admin components)

### State Management
- **Redux Toolkit**: Complex state management (Patient, Clinical, Admin)
- **React Query**: API state management and caching
- **Zustand**: Lightweight state for simpler interfaces

### Authentication & Security
- **JWT tokens** with role-based access control
- **React Router** with protected routes
- **Axios interceptors** for token management
- **CORS** configuration per interface

## Integration Architecture

### API Integration
```
Frontend Interfaces → nginx Reverse Proxy → Backend APIs
                                         ├── Player Experience API (8080)
                                         ├── API Gateway (8000)
                                         └── Agent Orchestration (8503)
```

### Authentication Flow
```
1. User login → Interface-specific authentication
2. JWT token issued by appropriate backend
3. Token stored in secure httpOnly cookies
4. API requests include Authorization header
5. Backend validates token and role permissions
```

### Real-time Communication
```
WebSocket Connections:
- Patient Interface → Player Experience API WebSocket
- Clinical Dashboard → Clinical Dashboard WebSocket
- Admin Interface → System Monitoring WebSocket
```

## Deployment Architecture

### Development Environment
```
docker-compose.dev.yml:
├── patient-interface (3000)
├── clinical-dashboard (3001)
├── admin-interface (3002)
├── public-portal (3003)
├── stakeholder-dashboard (3004)
├── api-docs-portal (3005)
└── nginx-proxy (80 → routes to appropriate interface)
```

### Production Environment
```
Kubernetes Deployment:
├── Frontend Services (LoadBalancer)
├── nginx Ingress Controller
├── SSL/TLS Termination
└── Backend API Services
```

## Security Considerations

### Authentication Boundaries
- **Patient Interface**: Patient-only access, therapeutic data protection
- **Clinical Dashboard**: Healthcare provider access, HIPAA compliance
- **Admin Interface**: Administrator access, system-level permissions
- **Public Portal**: No authentication, public information only
- **Stakeholder Dashboard**: Read-only research access
- **API Documentation**: Optional developer authentication

### Data Protection
- **HIPAA Compliance**: Clinical Dashboard with audit logging
- **Data Encryption**: All sensitive data encrypted in transit and at rest
- **Role-Based Access**: Strict permission boundaries between interfaces
- **Session Management**: Secure token handling and expiration

## Accessibility Compliance

All interfaces will comply with **WCAG 2.1 AA** guidelines:
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management
- Semantic HTML structure
- Alternative text for images
- Proper heading hierarchy

## Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Interface-Specific Considerations
- **Patient Interface**: Mobile-first design for accessibility
- **Clinical Dashboard**: Desktop-optimized for professional use
- **Admin Interface**: Desktop-focused with responsive elements
- **Public Portal**: Fully responsive for all devices
