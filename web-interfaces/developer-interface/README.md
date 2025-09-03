# TTA Developer Interface

A unified development dashboard for the TTA (Therapeutic Text Adventure) web interface ecosystem, providing centralized navigation, testing tools, and development utilities.

## Overview

The Developer Interface serves as a comprehensive development hub that streamlines the workflow for developing, testing, and monitoring all TTA web interfaces from a single location.

## Features

### 🎯 Interface Navigation Hub
- **Embedded Previews**: View all interfaces in iframe previews with fullscreen support
- **Direct Links**: Quick access to all seven TTA interfaces
- **Status Monitoring**: Real-time health status indicators for each interface via WebSocket
- **Interface Cards**: Detailed information about each interface including features and technology stack

### 🧪 Testing and Development Tools
- **Authentication Switcher**: Test different user roles (patient, clinician, admin, stakeholder, developer)
- **JWT Token Manager**: Generate, validate, and manage authentication tokens
- **Environment Switcher**: Switch between development, staging, and production environments
- **Quick API Tester**: Pre-configured endpoints for rapid API testing
- **Health Monitor**: Real-time interface health monitoring with WebSocket connections

### 🔧 Development Utilities
- **Live Reload Monitor**: Real-time live reload status tracking via WebSocket events
- **Build Status Dashboard**: Live compilation status and build times from all interfaces
- **Performance Metrics**: Real-time performance tracking with memory usage monitoring
- **Error Reporting**: Centralized error tracking with stack trace analysis
- **Log Viewer**: Real-time console log aggregation from all interfaces with filtering

### 📊 Advanced Debugging Tools
- **Network Request Monitor**: Real-time API call debugging with request/response analysis
- **Component Tree Viewer**: React component hierarchy visualization with performance metrics
- **Redux DevTools Integration**: Time-travel debugging with action replay
- **Why Did You Render**: Component re-render analysis and optimization suggestions
- **Memory Usage Tracking**: Real-time JavaScript heap monitoring with leak detection
- **Performance Profiler**: Detailed performance analysis with optimization recommendations

### 🔌 Real-Time WebSocket Integration
- **Live Health Monitoring**: Real-time interface status updates from backend services
- **Build Event Streaming**: Live build completion notifications and error reporting
- **Hot Module Replacement**: Real-time code change detection and reload events
- **Error Event Broadcasting**: Instant error reporting from all connected interfaces
- **Performance Metric Streaming**: Live performance data collection and analysis

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit with Redux DevTools
- **API Management**: React Query
- **Animations**: Framer Motion
- **Real-time**: WebSocket connections with ReconnectingWebSocket
- **Development**: Vite for fast builds
- **Testing**: Jest + React Testing Library
- **Debugging**: Why Did You Render + React DevTools integration
- **Performance**: Performance Observer API + Memory tracking
- **Network Monitoring**: Fetch interception + Request/Response analysis

## Quick Start

### Development Mode

```bash
# Navigate to developer interface directory
cd web-interfaces/developer-interface

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3006
```

### Production Deployment

```bash
# Build the application
npm run build

# Or use Docker
docker build -t tta-developer-interface .
docker run -p 3006:3006 tta-developer-interface
```

### Using the Deployment Script

```bash
# Deploy all interfaces including developer interface
cd web-interfaces
./deploy.sh development deploy

# Access via nginx proxy at http://localhost/dev
```

## Interface Access

- **Direct URL**: `http://localhost:3006`
- **Proxy URL**: `http://localhost/dev` (via nginx)
- **Development Only**: Automatically disabled in production environments

## Key Components

### Dashboard
- System overview with real-time statistics
- Quick action buttons for common tasks
- Recent activity feed
- Performance overview with visual indicators

### Interface Hub
- Grid view of all TTA interfaces
- Embedded preview mode with fullscreen support
- Interface status monitoring
- Direct navigation to any interface

### Testing Tools
- Role-based authentication testing
- JWT token generation and validation
- Environment configuration management
- API endpoint testing with pre-configured requests

### Development Utils
- Live reload status for all interfaces
- Build monitoring with error reporting
- Performance metrics collection
- Log aggregation and filtering

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

### WebSocket Integration
Real-time monitoring connects to existing TTA backend WebSocket endpoints:

```typescript
// Connects to monitoring endpoints on each service
ws://localhost:8080/ws/monitoring  // Player Experience API
ws://localhost:8000/ws/monitoring  // API Gateway
ws://localhost:8503/ws/monitoring  // Agent Orchestration
```

**Event Types Supported**:
- `interface_health`: Real-time health status updates
- `build_status`: Live build completion notifications
- `live_reload`: Hot module replacement events
- `error_report`: Real-time error broadcasting
- `performance_metric`: Live performance data streaming

### Feature Flags

The interface automatically adjusts features based on the environment:

- **Development**: All features enabled, WebSocket monitoring active, debug tools available
- **Staging**: Limited features, error reporting enabled, WebSocket monitoring only
- **Production**: Automatically disabled for security (returns 404)

## Security Considerations

### Development Only
- Interface is automatically disabled in production environments
- Environment detection prevents accidental production exposure
- Optional authentication with bypass for local development

### Access Control
- Developer JWT authentication (optional)
- Environment-based feature restrictions
- Secure token handling and validation

## Integration

### nginx Configuration
The interface is integrated into the existing nginx reverse proxy:

```nginx
location /dev {
    proxy_pass http://developer-interface:3006;
    # WebSocket support for live features
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
}
```

### Docker Integration
Included in the main docker-compose.yml:

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

## Usage Examples

### Real-Time Debugging with WebSocket
1. Open Debug Tools Panel (bottom-right bug icon)
2. View live network requests in Network tab
3. Monitor real-time errors in Errors tab
4. Watch console logs from all interfaces in Console tab
5. Analyze component performance in Components tab
6. Track memory usage in Performance tab

### Testing Authentication Flows
1. Navigate to Testing Tools → Authentication
2. Select desired user role (patient, clinician, admin)
3. Generate test token with JWT utilities
4. Apply role to target interface via WebSocket
5. Test functionality with different permissions in real-time

### Advanced Performance Profiling
1. Open Debug Tools → Performance tab
2. Enable performance recording
3. Monitor real-time memory usage and heap size
4. Analyze component render times and optimization suggestions
5. Track network request performance with waterfall visualization

### Component Tree Analysis
1. Open Debug Tools → Components tab
2. Browse React component hierarchy
3. View render counts and performance metrics
4. Identify components with high re-render frequency
5. Get optimization suggestions for slow components

### Live Error Tracking
1. Debug Tools automatically captures all errors
2. View errors by severity (critical, high, medium, low)
3. Analyze stack traces and debugging context
4. Filter errors by component or time range
5. Get automated debugging suggestions

## Development Workflow

1. **Start Development**: Launch all interfaces using deployment script
2. **Monitor Status**: Use Developer Interface dashboard to monitor all services
3. **Test Features**: Switch between user roles to test different functionality
4. **Debug Issues**: Use built-in debugging tools and error reporting
5. **Performance Check**: Monitor metrics and optimize as needed

## Troubleshooting

### Interface Not Loading
- Check if target interface is running on expected port
- Verify nginx proxy configuration
- Check browser console for CORS or network errors

### Authentication Issues
- Verify JWT token generation and validation
- Check API endpoint connectivity
- Ensure proper role permissions are set

### Performance Issues
- Monitor build times and error counts
- Check network request performance
- Use performance metrics to identify bottlenecks

## Contributing

1. Follow existing code patterns and TypeScript conventions
2. Add tests for new features
3. Update documentation for any new functionality
4. Ensure accessibility compliance (WCAG 2.1 AA)
5. Test across different browsers and screen sizes

## License

Part of the TTA (Therapeutic Text Adventure) system. See main project license for details.
