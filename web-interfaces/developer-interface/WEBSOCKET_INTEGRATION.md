# WebSocket Integration and Advanced Debugging Tools

## Overview

This document describes the enhanced TTA Developer Interface with real-time WebSocket capabilities and advanced debugging tools that replace simulated data with live monitoring from all TTA backend services.

## WebSocket Architecture

### Connection Management

The `WebSocketManager` service establishes connections to three backend services:

```typescript
// Service endpoints
ws://localhost:8080/ws/monitoring  // Player Experience API
ws://localhost:8000/ws/monitoring  // API Gateway
ws://localhost:8503/ws/monitoring  // Agent Orchestration
```

### Event Types

#### Interface Health Events
```typescript
interface InterfaceHealthData {
  id: string;
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime: number;
  lastCheck: string;
  error?: string;
  buildTime?: number;
  errorCount: number;
}
```

#### Build Status Events
```typescript
interface BuildStatusData {
  interfaceId: string;
  status: 'building' | 'success' | 'error' | 'idle';
  buildTime: number;
  errors: string[];
  warnings: string[];
  timestamp: string;
}
```

#### Live Reload Events
```typescript
interface LiveReloadData {
  interfaceId: string;
  status: 'reloading' | 'completed' | 'failed';
  timestamp: string;
  buildTime?: number;
  changes?: string[];
}
```

## Advanced Debugging Tools

### 1. Network Monitor
- **Real-time request tracking**: Intercepts all fetch requests
- **Request/Response analysis**: Full headers, body, and timing data
- **Filtering capabilities**: By method, status code, URL patterns
- **Performance metrics**: Response times and failure rates
- **WebSocket message monitoring**: Live WebSocket event tracking

### 2. Error Tracker
- **Automatic error capture**: Global error and promise rejection handling
- **Severity classification**: Critical, high, medium, low error levels
- **Stack trace analysis**: Full error context with debugging suggestions
- **Error aggregation**: Group similar errors and track frequency
- **Context-aware debugging**: Component and operation context tracking

### 3. Console Aggregator
- **Multi-interface log collection**: Aggregates logs from all 7 TTA interfaces
- **Real-time streaming**: Live console output with auto-scroll
- **Log level filtering**: Filter by log, info, warn, error, debug levels
- **Search and filtering**: Full-text search across all log messages
- **Source identification**: Track which interface generated each log

### 4. Performance Profiler
- **Memory usage tracking**: Real-time JavaScript heap monitoring
- **Performance metrics**: Navigation timing, resource loading analysis
- **Memory leak detection**: Track memory usage trends and alerts
- **Performance scoring**: Automated performance assessment
- **Optimization suggestions**: Actionable recommendations for improvements

### 5. Component Tree Viewer
- **React component hierarchy**: Visual component tree with performance data
- **Render tracking**: Component render counts and timing analysis
- **Props and state inspection**: Real-time component data viewing
- **Performance optimization**: Identify components with excessive re-renders
- **Why Did You Render integration**: Detailed re-render analysis

## Integration with Existing Systems

### Backend WebSocket Endpoints

The Developer Interface connects to existing TTA WebSocket infrastructure:

1. **Player Experience API** (`/ws/monitoring`)
   - Interface health status
   - Build completion events
   - Error reporting from therapeutic sessions

2. **API Gateway** (`/ws/monitoring`)
   - Request routing metrics
   - Authentication events
   - Service health aggregation

3. **Agent Orchestration** (`/ws/monitoring`)
   - Agent status updates
   - Workflow progress events
   - System performance metrics

### Authentication Integration

WebSocket connections support JWT authentication:

```typescript
// Token priority order
1. tta_token_developer (Developer role)
2. tta_token_admin (Admin role)
3. Anonymous connection (limited features)
```

### Environment Detection

Automatic environment-based feature control:

```typescript
// Development: Full features enabled
- WebSocket monitoring: ✓
- Debug tools: ✓
- Performance profiling: ✓
- Component analysis: ✓

// Staging: Limited features
- WebSocket monitoring: ✓
- Debug tools: ✗
- Performance profiling: ✓
- Component analysis: ✗

// Production: Disabled
- All features: ✗ (Interface returns 404)
```

## Debug Tools Panel

### Panel Architecture

The debug panel is a resizable, tabbed interface that provides:

1. **Network Tab**: Real-time request monitoring and analysis
2. **Errors Tab**: Error tracking with severity classification
3. **Console Tab**: Aggregated console logs from all interfaces
4. **Performance Tab**: Memory usage and performance metrics
5. **Components Tab**: React component tree and render analysis

### Real-Time Features

- **Live data streaming**: All data updates in real-time via WebSocket
- **Automatic reconnection**: Robust connection management with exponential backoff
- **Connection status indicators**: Visual feedback for WebSocket connection health
- **Recording controls**: Start/stop data collection as needed
- **Data persistence**: Maintains debug data across page reloads

## Performance Considerations

### Memory Management
- **Circular buffer implementation**: Limits stored events (50-200 items per type)
- **Automatic cleanup**: Removes old data to prevent memory leaks
- **Connection pooling**: Efficient WebSocket connection management
- **Event debouncing**: Prevents excessive UI updates from high-frequency events

### Network Efficiency
- **Selective subscriptions**: Only subscribe to needed event types
- **Compression support**: WebSocket message compression when available
- **Heartbeat monitoring**: Automatic connection health checks
- **Graceful degradation**: Falls back to polling when WebSocket unavailable

## Security Features

### Development-Only Access
- **Environment detection**: Automatically disabled in production
- **Hostname validation**: Only enabled on localhost/development domains
- **Feature gating**: Progressive feature disabling based on environment

### Data Sanitization
- **Sensitive data masking**: Automatically masks authentication tokens
- **PII protection**: Removes personally identifiable information from logs
- **Error sanitization**: Cleans stack traces of sensitive paths
- **Request filtering**: Excludes sensitive headers and payloads

## Usage Guidelines

### For Developers
1. **Start with Interface Hub**: Monitor overall system health
2. **Use Debug Panel**: Open for detailed real-time analysis
3. **Monitor Performance**: Track memory usage and optimization opportunities
4. **Analyze Components**: Identify performance bottlenecks in React components
5. **Debug Network Issues**: Use real-time request monitoring for API debugging

### For Testing
1. **Authentication Testing**: Use JWT token utilities for role switching
2. **API Testing**: Pre-configured endpoints with real-time monitoring
3. **Performance Testing**: Automated performance scoring and recommendations
4. **Accessibility Testing**: WCAG compliance checking with detailed reports
5. **Integration Testing**: Cross-interface functionality validation

## Troubleshooting

### WebSocket Connection Issues
- Check backend service availability on ports 8080, 8000, 8503
- Verify JWT token validity for authenticated connections
- Monitor browser console for connection errors
- Use connection status indicators in debug panel

### Performance Issues
- Monitor memory usage in Performance tab
- Check for excessive component re-renders in Components tab
- Analyze network request patterns in Network tab
- Review error frequency in Errors tab

### Debug Data Not Appearing
- Ensure recording is enabled (play/pause button in debug panel)
- Check WebSocket connection status indicators
- Verify environment is set to development mode
- Clear browser cache and reload if data seems stale

## Future Enhancements

### Planned Features
- **Multi-user debugging**: Share debug sessions between developers
- **Historical data analysis**: Long-term performance trend analysis
- **Automated testing integration**: Connect with CI/CD pipeline testing
- **Custom event types**: Support for application-specific debug events
- **Export capabilities**: Export debug data for offline analysis

### Integration Opportunities
- **React DevTools**: Deeper integration with React debugging tools
- **Redux DevTools**: Enhanced time-travel debugging capabilities
- **Browser DevTools**: Integration with Chrome/Firefox developer tools
- **Testing frameworks**: Integration with Jest, Cypress, and Playwright
- **Monitoring services**: Export data to external monitoring platforms
