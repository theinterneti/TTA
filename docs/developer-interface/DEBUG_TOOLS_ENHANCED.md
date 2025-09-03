# Enhanced Debug Tools Documentation

## Overview

The TTA Developer Interface now includes comprehensive debugging capabilities that provide real-time monitoring, performance analysis, collaborative debugging, and CI/CD integration across all TTA interfaces.

## Features

### 1. Real-Time WebSocket Monitoring

**Purpose**: Monitor all backend services in real-time through WebSocket connections.

**Capabilities**:
- Connects to Player Experience API (`ws://localhost:8080/ws/monitoring`)
- Connects to API Gateway (`ws://localhost:8000/ws/monitoring`)
- Connects to Agent Orchestration (`ws://localhost:8503/ws/monitoring`)
- Real-time health status updates
- Performance metrics streaming
- Error reporting and debugging information

**Usage**:
```typescript
import { webSocketManager } from '../services/WebSocketManager';

// Monitor connection status
webSocketManager.on('connection_established', (connection) => {
  console.log(`Connected to ${connection.url}`);
});

// Listen for monitoring data
webSocketManager.on('dev_event', (event) => {
  if (event.type === 'interface_health') {
    // Handle health status update
  }
});
```

### 2. Performance Baseline Recording

**Purpose**: Automatically capture and track performance metrics with regression detection.

**Capabilities**:
- Automatic baseline creation for all 7 TTA interfaces
- Real-time performance monitoring
- Regression detection with configurable thresholds
- Historical trend analysis
- Performance alerting system

**Configuration**:
```typescript
// Regression thresholds (percentage increase)
const thresholds = {
  load_time: { medium: 20, high: 40, critical: 60 },
  render_time: { medium: 25, high: 50, critical: 75 },
  memory_usage: { medium: 30, high: 60, critical: 100 },
  network: { medium: 15, high: 30, critical: 50 }
};
```

**Usage**:
```typescript
import { performanceBaselineManager } from '../services/PerformanceBaselineManager';

// Record a performance metric
performanceBaselineManager.recordMetric({
  name: 'load_time',
  value: 150.5,
  unit: 'ms',
  timestamp: new Date().toISOString(),
  interfaceId: 'patient',
  category: 'load_time'
});

// Listen for regressions
performanceBaselineManager.on('regression_detected', (regression) => {
  console.warn(`Performance regression: ${regression.description}`);
});
```

### 3. Custom Event System

**Purpose**: Support application-specific debug events from all TTA interfaces.

**Predefined Events**:
- **Patient Interface**: `patient_session_start`, `patient_choice_made`
- **Clinical Dashboard**: `clinician_patient_review`, `clinical_alert_triggered`
- **Admin Interface**: `admin_user_management`, `admin_system_config_change`
- **Public Portal**: `public_resource_access`
- **Stakeholder Dashboard**: `stakeholder_report_generated`
- **API Documentation**: `api_docs_endpoint_tested`
- **Developer Interface**: `dev_debug_session_start`

**Usage**:
```typescript
import { customEventManager } from '../services/CustomEventManager';

// Register a custom event definition
customEventManager.registerEventDefinition({
  eventType: 'custom_user_action',
  interfaceId: 'patient',
  name: 'Custom User Action',
  description: 'User performed a custom action',
  schema: {
    actionType: { type: 'string', required: true, description: 'Type of action' },
    duration: { type: 'number', required: false, description: 'Action duration in ms' }
  },
  category: 'user_interaction',
  severity: 'info',
  createdAt: new Date().toISOString(),
  version: '1.0.0'
});

// Create an event instance
customEventManager.createEventInstance(
  'custom_user_action',
  'patient',
  { actionType: 'button_click', duration: 250 },
  { userId: 'user_123' },
  'info',
  ['ui', 'interaction']
);
```

### 4. React DevTools Integration

**Purpose**: Seamless integration with React DevTools browser extension.

**Capabilities**:
- Component tree visualization
- Render tracking and performance profiling
- Fiber inspection
- Props and state inspection
- Performance metrics correlation

**Usage**:
```typescript
import { reactDevToolsBridge } from '../services/ReactDevToolsBridge';

// Check DevTools availability
if (reactDevToolsBridge.isDevToolsConnected()) {
  // Get component tree
  const componentTree = reactDevToolsBridge.getComponentTree();

  // Select a component
  reactDevToolsBridge.selectComponent('MyComponent_0_key');

  // Get profiler data
  const profilerData = reactDevToolsBridge.getComponentProfilerData('MyComponent_0_key');
}
```

### 5. Collaborative Debugging

**Purpose**: Enable multiple developers to share debug sessions in real-time.

**Capabilities**:
- Real-time session sharing
- Synchronized debug panel states
- Shared annotations and notes
- Participant management
- Session bookmarking

**Usage**:
```typescript
import { collaborativeDebugManager } from '../services/CollaborativeDebugManager';

// Create a debug session
const session = await collaborativeDebugManager.createSession(
  'Bug Investigation',
  'Investigating login issues'
);

// Invite a collaborator
const invitation = collaborativeDebugManager.inviteUser(
  'colleague@example.com',
  'collaborator'
);

// Add a shared note
collaborativeDebugManager.addNote({
  content: 'Found the issue in authentication middleware',
  type: 'issue',
  priority: 'high'
});

// Add an annotation
collaborativeDebugManager.addAnnotation({
  type: 'highlight',
  target: { component: 'LoginForm', selector: '.error-message' },
  content: 'Error message appears here when authentication fails'
});
```

### 6. CI/CD Pipeline Integration

**Purpose**: Automatically capture debug data during test runs and detect regressions.

**Capabilities**:
- Automated test run recording
- Performance regression detection
- Debug artifact collection
- Comprehensive reporting
- GitHub Actions integration

**GitHub Actions Setup**:
```yaml
# .github/workflows/debug-integration.yml
- name: Run Debug Integration Tests
  run: |
    cd web-interfaces/developer-interface
    npm run test:debug-tools -- --ci --coverage
  env:
    TTA_DEBUG_MODE: 'true'
    TTA_PERFORMANCE_BASELINE: 'true'
    TTA_CI_INTEGRATION: 'true'
```

**Usage**:
```typescript
import { ciPipelineIntegration } from '../services/CIPipelineIntegration';

// Start a test run
const testRun = ciPipelineIntegration.startTestRun(
  process.env.GITHUB_RUN_ID,
  process.env.GITHUB_REF_NAME,
  process.env.GITHUB_SHA,
  process.env.GITHUB_ACTOR
);

// Record test results
ciPipelineIntegration.recordTestResult({
  testId: 'test_123',
  testName: 'should render correctly',
  testFile: 'Component.test.tsx',
  status: 'passed',
  duration: 1250
});

// Finish test run
const finishedRun = ciPipelineIntegration.finishTestRun('passed');
```

## Debug Panel Interface

### Navigation Tabs

1. **Network**: Monitor network requests and WebSocket connections
2. **Errors**: Track and analyze error events
3. **Console**: Aggregate console logs from all interfaces
4. **Performance**: View performance metrics and profiling data
5. **Components**: Inspect React component tree and DevTools integration
6. **Events**: Browse and filter custom application events
7. **Baselines**: Monitor performance baselines and regressions
8. **Collaborate**: Manage collaborative debugging sessions

### Controls

- **Recording Toggle**: Start/stop debug data recording
- **Clear Data**: Clear all collected debug information
- **WebSocket Status**: View connection status to all backend services
- **Export**: Export debug data for analysis

## Configuration

### Environment Variables

```bash
# Enable debug mode
TTA_DEBUG_MODE=true

# Enable performance baseline recording
TTA_PERFORMANCE_BASELINE=true

# Enable CI/CD integration
TTA_CI_INTEGRATION=true

# WebSocket endpoints
TTA_WEBSOCKET_ENDPOINTS=ws://localhost:8080/ws/monitoring,ws://localhost:8000/ws/monitoring,ws://localhost:8503/ws/monitoring

# Performance thresholds
TTA_PERFORMANCE_THRESHOLDS='{"load_time":{"medium":20,"high":40,"critical":60}}'
```

### Local Storage Configuration

The debug tools store configuration and data in browser local storage:

- `tta_debug_user`: User profile for collaborative debugging
- `tta_performance_baselines`: Performance baseline data
- `tta_performance_historical`: Historical performance metrics
- `tta_performance_regressions`: Detected performance regressions

## Testing

### Running Tests

```bash
# Run all debug tools integration tests
npm run test:debug-tools

# Run WebSocket integration tests
npm run test:websocket

# Run performance baseline tests
npm run test:performance

# Run custom event system tests
npm run test:events

# Run collaborative debugging tests
npm run test:collaborative

# Run full integration test suite
npm run test:integration
```

### Test Coverage

The test suite covers:
- WebSocket connection management
- Performance baseline recording and regression detection
- Custom event system functionality
- Collaborative debugging features
- React DevTools integration
- CI/CD pipeline integration
- End-to-end debug workflows

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failures**
   - Verify backend services are running
   - Check firewall and network settings
   - Ensure WebSocket endpoints are accessible

2. **Performance Baseline Not Recording**
   - Verify `TTA_PERFORMANCE_BASELINE=true` is set
   - Check browser permissions for performance API
   - Ensure sufficient data points for baseline creation

3. **React DevTools Not Detected**
   - Install React DevTools browser extension
   - Refresh the page after installing extension
   - Check browser console for DevTools hook availability

4. **Collaborative Sessions Not Working**
   - Verify WebSocket connections are established
   - Check user authentication status
   - Ensure session permissions are correctly configured

### Debug Logging

Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'tta:*');
```

This will enable detailed logging for all TTA debug components.

## Performance Considerations

- WebSocket connections are automatically managed and reconnected on failure
- Performance metrics are sampled and stored with configurable limits
- Debug data is automatically cleaned up to prevent memory leaks
- Collaborative sessions use efficient delta synchronization

## Security

- All WebSocket connections use secure protocols in production
- Collaborative sessions require authentication
- Debug data is sanitized before storage
- CI/CD integration uses secure environment variables

## Future Enhancements

- Visual debugging with screenshot capture
- Advanced performance profiling with flame graphs
- Integration with external monitoring services
- Mobile debugging capabilities
- Advanced collaboration features (voice/video chat)
