# TTA Developer Interface Specification

## Overview

The TTA Developer Interface is a unified development dashboard that provides centralized navigation, testing tools, and development utilities for the entire TTA web interface ecosystem. It serves as a comprehensive development hub for streamlining workflows across all seven TTA interfaces.

## System Architecture

### Technology Stack
- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit with Redux DevTools
- **API Management**: React Query
- **Animations**: Framer Motion
- **Real-time**: WebSocket connections with ReconnectingWebSocket
- **Build Tool**: Vite for fast builds
- **Testing**: Jest + React Testing Library
- **Debugging**: Why Did You Render + React DevTools integration
- **Performance**: Performance Observer API + Memory tracking
- **Network Monitoring**: Fetch interception + Request/Response analysis

### Deployment Configuration
- **URL**: `http://localhost:3006`
- **Proxy URL**: `http://localhost/dev` (via nginx)
- **Environment**: Development only (automatically disabled in production)
- **Port**: 3006

## Core Features

### 1. Interface Navigation Hub

**Purpose**: Centralized access point for all TTA interfaces with real-time monitoring.

**Features**:
- Embedded iframe previews with fullscreen support
- Direct navigation links to all seven interfaces
- Real-time health status indicators via WebSocket
- Interface cards with detailed information
- Technology stack overview for each interface

**Supported Interfaces**:
- Patient Interface (localhost:5173)
- Clinical Dashboard (localhost:3001)
- Admin Interface (localhost:3002)
- Public Portal (localhost:3003)
- Stakeholder Dashboard (localhost:3004)
- API Documentation (localhost:3005)
- Developer Interface (localhost:3006)

### 2. Testing and Development Tools

**Authentication Switcher**:
- Test different user roles (patient, clinician, admin, stakeholder, developer)
- JWT token generation and validation
- Role-based permission testing
- Real-time authentication state management

**Environment Management**:
- Switch between development, staging, and production environments
- Environment-specific configuration management
- Feature flag control based on environment

**API Testing Suite**:
- Pre-configured endpoint testing
- Request/response analysis
- Authentication header management
- Quick API validation tools

### 3. Real-Time Monitoring System

**WebSocket Integration**:
```typescript
// Monitoring endpoints
ws://localhost:8080/ws/monitoring  // Player Experience API
ws://localhost:8000/ws/monitoring  // API Gateway
ws://localhost:8503/ws/monitoring  // Agent Orchestration
```

**Event Types**:
- `interface_health`: Real-time health status updates
- `build_status`: Live build completion notifications
- `live_reload`: Hot module replacement events
- `error_report`: Real-time error broadcasting
- `performance_metric`: Live performance data streaming

**Health Monitoring**:
- Real-time interface status tracking
- Build completion notifications
- Error event broadcasting
- Performance metric collection

### 4. Advanced Debugging Tools

**Network Request Monitor**:
- Real-time API call debugging
- Request/response analysis with timing
- Network waterfall visualization
- Error tracking and analysis

**Component Tree Viewer**:
- React component hierarchy visualization
- Performance metrics per component
- Render count tracking
- Re-render analysis with optimization suggestions

**Performance Profiler**:
- Real-time JavaScript heap monitoring
- Memory leak detection
- Component performance analysis
- Optimization recommendations

**Error Reporting System**:
- Centralized error tracking
- Stack trace analysis
- Error severity classification
- Automated debugging suggestions

### 5. Development Utilities

**Live Reload Monitor**:
- Real-time live reload status tracking
- Hot module replacement event monitoring
- Build status dashboard with timing
- Compilation error reporting

**Log Viewer**:
- Real-time console log aggregation
- Multi-interface log filtering
- Error level classification
- Search and filtering capabilities

**Performance Metrics**:
- Memory usage tracking
- Build time monitoring
- API response time analysis
- Component render performance

## User Interface Design

### Dashboard Layout
- System overview with real-time statistics
- Quick action buttons for common development tasks
- Recent activity feed with filtering
- Performance overview with visual indicators

### Interface Hub
- Grid view of all TTA interfaces
- Embedded preview mode with fullscreen capability
- Status indicators (online/offline/error)
- Direct navigation buttons

### Debug Tools Panel
- Collapsible bottom panel with tabbed interface
- Network tab for API monitoring
- Errors tab for error tracking
- Console tab for log aggregation
- Components tab for React analysis
- Performance tab for metrics

## Security and Access Control

### Development-Only Access
- Automatically disabled in production environments
- Environment detection prevents accidental exposure
- Returns 404 in production for security

### Authentication
- Optional developer JWT authentication
- Bypass available for local development
- Secure token handling and validation
- Role-based access control testing

### Feature Restrictions
- Environment-based feature availability
- Development: All features enabled
- Staging: Limited features, error reporting only
- Production: Completely disabled

## Configuration

### Environment Variables
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8080
REACT_APP_GATEWAY_URL=http://localhost:8000
REACT_APP_AGENT_URL=http://localhost:8503

# Development Features
REACT_APP_DEV_MODE=true
REACT_APP_DEBUG_MODE=true

# WebSocket Configuration
REACT_APP_WS_URL=ws://localhost:8080
```

### Docker Integration
```yaml
developer-interface:
  build: ./developer-interface
  container_name: tta-developer-interface
  ports:
    - "3006:3006"
  environment:
    - NODE_ENV=development
    - REACT_APP_DEV_MODE=true
```

### nginx Proxy Configuration
```nginx
location /dev {
    proxy_pass http://developer-interface:3006;
    # WebSocket support for live features
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
}
```

## Development Workflow Integration

### Startup Process
1. Launch all interfaces using deployment script
2. Access Developer Interface at localhost:3006
3. Monitor interface health status
4. Use embedded previews for development

### Testing Workflow
1. Switch user roles via Authentication Switcher
2. Generate test JWT tokens
3. Apply roles to target interfaces
4. Test functionality with different permissions
5. Monitor API calls and responses

### Debugging Workflow
1. Open Debug Tools panel
2. Monitor real-time network requests
3. Track errors across all interfaces
4. Analyze component performance
5. Review console logs with filtering

### Performance Analysis
1. Enable performance recording
2. Monitor memory usage and heap size
3. Analyze component render times
4. Track network request performance
5. Get optimization recommendations

## API Integration

### Backend Endpoints
- Health monitoring: `GET /api/v1/health`
- Interface status: `GET /api/v1/interfaces/status`
- Authentication testing: `POST /api/v1/auth/test`
- Performance metrics: `GET /api/v1/metrics`

### WebSocket Events
- Connection management with automatic reconnection
- Event filtering and routing
- Real-time data streaming
- Error handling and recovery

## Testing Strategy

### Unit Tests
- Component rendering and functionality
- WebSocket connection handling
- Authentication flow testing
- Error handling scenarios

### Integration Tests
- Multi-interface communication
- Real-time monitoring accuracy
- Authentication switcher functionality
- Performance metric collection

### E2E Tests
- Complete development workflow
- Interface navigation and embedding
- Debug tool functionality
- Error reporting accuracy

## Performance Requirements

### Load Time Standards
- Initial load: <2s
- Interface switching: <500ms
- Debug panel opening: <300ms
- WebSocket connection: <3s

### Real-time Features
- Health status updates: <1s latency
- Error reporting: <500ms from occurrence
- Performance metrics: Real-time streaming
- Log aggregation: <200ms delay

### Resource Usage
- Memory footprint: <100MB baseline
- CPU usage: <5% during normal operation
- Network bandwidth: Minimal overhead
- Storage: <50MB for logs and cache

## Maintenance and Support

### Monitoring
- Interface health tracking
- Error rate monitoring
- Performance metric collection
- User activity analytics

### Updates and Versioning
- Synchronized with main TTA releases
- Independent feature updates
- Bug fix deployments
- Development tool enhancements

### Documentation
- Developer workflow guides
- API integration documentation
- Debugging best practices
- Performance optimization guides

## Troubleshooting

### Common Issues
- Interface not loading: Check port availability and nginx config
- Authentication issues: Verify JWT token generation
- Performance problems: Monitor build times and network requests
- WebSocket connection failures: Check backend service status

### Debug Procedures
1. Check interface health status
2. Review error logs and stack traces
3. Analyze network request patterns
4. Monitor performance metrics
5. Verify authentication state

## Future Enhancements

### Planned Features
- Advanced performance profiling
- Automated testing integration
- Code quality metrics
- Deployment pipeline integration

### Integration Roadmap
- CI/CD pipeline integration
- Advanced error tracking
- Performance benchmarking
- Automated testing workflows
