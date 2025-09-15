# TTA Shared Components Integration Guide

## Overview

This guide provides comprehensive instructions for integrating the TTA shared component library across all web interfaces. The shared components provide clinical-grade reliability, WCAG 2.1 AA accessibility compliance, and therapeutic user experience patterns.

## Quick Start

### 1. Installation

```bash
# Install shared components package
npm install @tta/shared-components

# Install required peer dependencies
npm install react react-dom framer-motion
```

### 2. Basic Setup

```tsx
import React from 'react';
import {
  AuthProvider,
  TherapeuticThemeProvider,
  AccessibilityProvider,
  HIPAAComplianceProvider,
  CrisisSupportProvider
} from '@tta/shared-components';
import '@tta/shared-components/styles/therapeutic-themes.css';

function App() {
  return (
    <AuthProvider
      apiBaseUrl="http://localhost:8080"
      interfaceType="patient" // or 'clinical', 'admin', etc.
    >
      <TherapeuticThemeProvider
        defaultTheme="calm"
        persistPreferences={true}
      >
        <AccessibilityProvider
          enableAutoDetection={true}
          therapeuticMode={true}
        >
          <HIPAAComplianceProvider
            interfaceType="patient"
            clinicalDataAccess={false}
            enableAuditLogging={true}
          >
            <CrisisSupportProvider
              enableRealTimeMonitoring={true}
            >
              {/* Your app content */}
            </CrisisSupportProvider>
          </HIPAAComplianceProvider>
        </AccessibilityProvider>
      </TherapeuticThemeProvider>
    </AuthProvider>
  );
}
```

## Component Documentation

### 1. CrisisSupportProvider

Provides real-time crisis detection and support resources with <1s response time.

**Features:**
- Integration with SafetyValidationOrchestrator backend
- Real-time WebSocket monitoring
- Professional escalation protocols
- Crisis resource directory
- Performance tracking

**Usage:**
```tsx
import { useCrisisSupport, CrisisSupportButton } from '@tta/shared-components';

function MyComponent() {
  const { assessCrisisRisk, showCrisisSupport } = useCrisisSupport();

  const handleUserInput = async (input: string) => {
    const assessment = await assessCrisisRisk(input);
    if (assessment.crisis_level >= CrisisLevel.HIGH) {
      // Crisis support modal will auto-show
    }
  };

  return (
    <div>
      <CrisisSupportButton variant="emergency" />
      {/* Your content */}
    </div>
  );
}
```

### 2. TherapeuticThemeProvider

WCAG 2.1 AA compliant therapeutic themes with accessibility features.

**Available Themes:**
- `calm` - Soothing blues and soft tones
- `warm` - Comforting oranges and yellows
- `nature` - Refreshing greens and earth tones
- `clinical` - Professional grays and neutrals
- `high-contrast` - Maximum accessibility contrast
- `dark` - Dark mode for low-light environments

**Usage:**
```tsx
import { useTherapeuticTheme, ThemeSelector } from '@tta/shared-components';

function ThemeSettings() {
  const { theme, setTheme, colors } = useTherapeuticTheme();

  return (
    <div>
      <ThemeSelector showLabels={true} />
      <div style={{ backgroundColor: colors.primary[100] }}>
        Themed content
      </div>
    </div>
  );
}
```

### 3. AccessibilityProvider

Comprehensive accessibility support with WCAG compliance checking.

**Features:**
- Screen reader support with live regions
- Keyboard navigation enhancements
- Focus management and trapping
- ARIA label generation
- Accessibility compliance checking

**Usage:**
```tsx
import { useAccessibility } from '@tta/shared-components';

function AccessibleForm() {
  const {
    announce,
    generateAriaLabel,
    validateForm,
    trapFocus
  } = useAccessibility();

  const handleSubmit = (e) => {
    const form = e.target;
    const report = validateForm(form);

    if (!report.isAccessible) {
      announce('Form has accessibility issues', 'assertive');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="name">
        {generateAriaLabel('Name', 'Required field')}
      </label>
      <input id="name" required />
    </form>
  );
}
```

### 4. HIPAAComplianceProvider

HIPAA-compliant audit logging and data protection for clinical interfaces.

**Features:**
- Comprehensive audit logging
- Data access authorization
- Session management with timeouts
- Security event tracking
- Compliance reporting

**Usage:**
```tsx
import { useHIPAACompliance } from '@tta/shared-components';

function ClinicalDataComponent() {
  const {
    logDataAccess,
    isDataAccessAuthorized,
    maskSensitiveData
  } = useHIPAACompliance();

  const accessPatientData = (patientId: string) => {
    if (isDataAccessAuthorized('patient_record', patientId)) {
      logDataAccess(patientId, 'patient_record', 'clinical_review');
      // Access data
    }
  };

  return (
    <div>
      {/* Clinical interface content */}
    </div>
  );
}
```

## Interface-Specific Configuration

### Patient Interface (localhost:5173)
```tsx
<HIPAAComplianceProvider
  interfaceType="patient"
  clinicalDataAccess={false}
  sessionTimeoutMinutes={60}
/>
```

### Clinical Dashboard (localhost:3001)
```tsx
<HIPAAComplianceProvider
  interfaceType="clinical"
  clinicalDataAccess={true}
  sessionTimeoutMinutes={30}
/>
```

### Admin Interface (localhost:3002)
```tsx
<HIPAAComplianceProvider
  interfaceType="admin"
  clinicalDataAccess={true}
  sessionTimeoutMinutes={15}
/>
```

## Performance Requirements

### Crisis Support
- **Response Time**: <1s for crisis assessment
- **WebSocket**: Real-time monitoring with automatic reconnection
- **Fallback**: Graceful degradation if backend unavailable

### Theme Provider
- **Load Time**: <100ms for theme switching
- **CSS Variables**: Automatic application to document root
- **Persistence**: LocalStorage with error handling

### Accessibility
- **Screen Reader**: Live region announcements
- **Keyboard**: Tab order and focus management
- **Compliance**: WCAG 2.1 AA validation

### HIPAA Compliance
- **Audit Logging**: All data access events
- **Session Timeout**: Configurable per interface
- **Data Protection**: Encryption and masking

## Testing Integration

### Unit Tests
```tsx
import { render, screen } from '@testing-library/react';
import { CrisisSupportProvider } from '@tta/shared-components';

test('crisis support integration', () => {
  render(
    <CrisisSupportProvider>
      <MyComponent />
    </CrisisSupportProvider>
  );

  // Test crisis support functionality
});
```

### E2E Tests
```tsx
// Test crisis response time
const startTime = performance.now();
await assessCrisisRisk('test input');
const responseTime = performance.now() - startTime;
expect(responseTime).toBeLessThan(1000);
```

## Troubleshooting

### Common Issues

1. **Crisis Support WebSocket Connection Failed**
   - Check backend is running on localhost:8080
   - Verify WebSocket endpoint `/ws/crisis-monitoring`
   - Ensure authentication token is valid

2. **Theme Not Applying**
   - Import CSS file: `@tta/shared-components/styles/therapeutic-themes.css`
   - Check CSS custom properties in browser dev tools
   - Verify TherapeuticThemeProvider wraps your app

3. **Accessibility Announcements Not Working**
   - Check if screen reader is detected
   - Verify live region is created in DOM
   - Test with actual screen reader software

4. **HIPAA Audit Logs Not Saving**
   - Verify `enableAuditLogging={true}`
   - Check localStorage permissions
   - Ensure user is authenticated

### Performance Monitoring

```tsx
import { useCrisisSupport } from '@tta/shared-components';

function PerformanceMonitor() {
  const { averageResponseTime, totalAssessments } = useCrisisSupport();

  return (
    <div>
      <p>Average Response Time: {averageResponseTime}ms</p>
      <p>Total Assessments: {totalAssessments}</p>
    </div>
  );
}
```

## Production Deployment

### Environment Variables
```bash
# Crisis Support
TTA_CRISIS_WEBSOCKET_URL=wss://api.tta.dev/ws/crisis-monitoring
TTA_CRISIS_RESPONSE_TIMEOUT=1000

# HIPAA Compliance
TTA_AUDIT_LOG_ENDPOINT=https://api.tta.dev/audit-logs
TTA_SESSION_TIMEOUT_MINUTES=30

# Accessibility
TTA_ENABLE_ACCESSIBILITY_VALIDATION=true
TTA_THERAPEUTIC_MODE=true
```

### Security Considerations
- Use HTTPS for all API communications
- Implement proper JWT token validation
- Enable CORS only for trusted domains
- Use secure WebSocket connections (WSS)
- Encrypt sensitive data in audit logs

## Support

For technical support or questions about shared component integration:

1. Check the component documentation in `/web-interfaces/shared/src/components/`
2. Review the `.kiro/specs/shared-component-library/` specifications
3. Test with the Developer Interface at localhost:3006
4. Refer to existing implementations in Patient Interface (localhost:5173)

## Version Compatibility

- React: ^18.0.0
- TypeScript: ^4.9.0
- Framer Motion: ^10.0.0
- Node.js: ^18.0.0

## Contributing

When adding new shared components:

1. Follow the established patterns in existing components
2. Ensure WCAG 2.1 AA compliance
3. Add comprehensive TypeScript types
4. Include unit tests and documentation
5. Update this integration guide
