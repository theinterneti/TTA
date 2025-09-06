# TTA Shared Component Library Specification

## Overview

The TTA Shared Component Library provides a comprehensive set of reusable React components designed specifically for therapeutic applications. All components are WCAG 2.1 AA compliant, HIPAA-ready, and optimized for clinical-grade performance and reliability.

## Architecture

### Component Categories

1. **Authentication & Security**
   - AuthProvider
   - ProtectedRoute
   - HIPAAComplianceProvider

2. **Crisis Support & Safety**
   - CrisisSupportProvider
   - CrisisSupportButton
   - Crisis detection hooks

3. **Therapeutic Theming**
   - TherapeuticThemeProvider
   - ThemeSelector
   - Therapeutic color schemes

4. **Accessibility**
   - AccessibilityProvider
   - Screen reader support
   - Keyboard navigation

5. **Common UI Components**
   - ErrorBoundary
   - LoadingSpinner
   - Form components

## Core Components

### 1. CrisisSupportProvider

**Purpose**: Real-time crisis detection and support with <1s response time requirement.

**Key Features**:
- Integration with SafetyValidationOrchestrator backend
- Real-time WebSocket monitoring
- Professional escalation protocols
- Crisis resource directory
- Performance tracking and monitoring

**API**:
```tsx
interface CrisisSupportContextType {
  assessCrisisRisk: (userInput: string, userHistory?: any[]) => Promise<CrisisAssessment>;
  triggerCrisisProtocol: (assessment: CrisisAssessment) => Promise<void>;
  escalateToProfessional: (userId: string, crisisLevel: CrisisLevel) => Promise<any>;
  showCrisisSupport: boolean;
  setShowCrisisSupport: (show: boolean) => void;
  crisisResources: CrisisResource[];
  isMonitoring: boolean;
  lastAssessment: CrisisAssessment | null;
  averageResponseTime: number;
  totalAssessments: number;
}
```

**Performance Requirements**:
- Crisis assessment response time: <1s
- WebSocket connection: Auto-reconnection with exponential backoff
- Fallback behavior: Graceful degradation if backend unavailable

### 2. TherapeuticThemeProvider

**Purpose**: WCAG 2.1 AA compliant therapeutic themes with accessibility features.

**Available Themes**:
- `calm` - Soothing blues and soft tones
- `warm` - Comforting oranges and yellows
- `nature` - Refreshing greens and earth tones
- `clinical` - Professional grays and neutrals
- `high-contrast` - Maximum accessibility contrast
- `dark` - Dark mode for low-light environments

**Key Features**:
- CSS custom property management
- Preference persistence with localStorage
- Responsive design support
- Accessibility compliance
- Theme switching performance <100ms

**API**:
```tsx
interface TherapeuticThemeContextType {
  theme: TherapeuticTheme;
  colorMode: ColorMode;
  fontSize: FontSize;
  motionPreference: MotionPreference;
  setTheme: (theme: TherapeuticTheme) => void;
  setColorMode: (mode: ColorMode) => void;
  setFontSize: (size: FontSize) => void;
  setMotionPreference: (preference: MotionPreference) => void;
  colors: TherapeuticColorScheme;
  isHighContrast: boolean;
  isDarkMode: boolean;
  isReducedMotion: boolean;
  cssVariables: Record<string, string>;
}
```

### 3. AccessibilityProvider

**Purpose**: Comprehensive accessibility support with WCAG compliance checking.

**Key Features**:
- Screen reader support with live regions
- Keyboard navigation enhancements
- Focus management and trapping
- ARIA label generation
- Accessibility compliance checking
- Auto-detection of user preferences

**API**:
```tsx
interface AccessibilityContextType {
  settings: AccessibilitySettings;
  updateSettings: (updates: Partial<AccessibilitySettings>) => void;
  resetSettings: () => void;
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  announcePageChange: (title: string, description?: string) => void;
  announceError: (error: string, field?: string) => void;
  announceStatus: (status: string, type?: 'success' | 'warning' | 'error' | 'info') => void;
  focusElement: (selector: string) => boolean;
  trapFocus: (container: HTMLElement) => () => void;
  createSkipLink: (target: string, label: string) => void;
  generateAriaLabel: (base: string, context?: string) => string;
  generateAriaDescription: (description: string, verbose?: boolean) => string;
  isScreenReaderActive: boolean;
  isKeyboardUser: boolean;
  isHighContrastMode: boolean;
  isReducedMotionMode: boolean;
  checkWCAGCompliance: (element: HTMLElement) => AccessibilityIssue[];
  validateForm: (form: HTMLFormElement) => FormAccessibilityReport;
}
```

### 4. HIPAAComplianceProvider

**Purpose**: HIPAA-compliant audit logging and data protection for clinical interfaces.

**Key Features**:
- Comprehensive audit logging
- Data access authorization
- Session management with configurable timeouts
- Security event tracking
- Compliance reporting
- Data masking and encryption

**Interface-Specific Configuration**:
- Patient Interface: `clinicalDataAccess: false`, `sessionTimeout: 60min`
- Clinical Dashboard: `clinicalDataAccess: true`, `sessionTimeout: 30min`
- Admin Interface: `clinicalDataAccess: true`, `sessionTimeout: 15min`

**API**:
```tsx
interface HIPAAComplianceContextType {
  logDataAccess: (patientId: string, dataType: string, purpose: string) => void;
  logUserAction: (action: string, resource: string, resourceId?: string, details?: Record<string, any>) => void;
  logSecurityEvent: (type: SecurityEvent['type'], severity: SecurityEvent['severity'], description: string, details?: Record<string, any>) => void;
  isDataAccessAuthorized: (dataType: string, patientId?: string) => boolean;
  maskSensitiveData: (data: string, dataType: string) => string;
  encryptSensitiveData: (data: string) => string;
  decryptSensitiveData: (encryptedData: string) => string;
  sessionTimeout: number;
  lastActivity: Date | null;
  updateActivity: () => void;
  isSessionValid: () => boolean;
  extendSession: () => void;
  complianceStatus: 'compliant' | 'warning' | 'violation';
  auditLogs: AuditLogEntry[];
  dataAccessLogs: DataAccessLog[];
  securityEvents: SecurityEvent[];
  interfaceType: string;
  clinicalDataAccess: boolean;
  requiresAuditTrail: boolean;
  generateComplianceReport: () => ComplianceReport;
  exportAuditLogs: (startDate: Date, endDate: Date) => AuditLogEntry[];
}
```

## Integration Guidelines

### Basic Setup

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

## Performance Standards

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

## Testing Requirements

### Unit Tests
- Component rendering and functionality
- Hook behavior and state management
- Error handling and edge cases
- Performance benchmarks

### Integration Tests
- Cross-component interaction
- Provider context propagation
- Real-time features (WebSocket, crisis detection)
- Accessibility compliance validation

### E2E Tests
- Complete user workflows
- Crisis response scenarios
- Theme switching and persistence
- HIPAA audit trail verification

## Security Considerations

### Data Protection
- All sensitive data encrypted in transit and at rest
- HIPAA-compliant audit logging
- Session management with automatic timeouts
- Data masking for display purposes

### Crisis Support Security
- Secure WebSocket connections (WSS in production)
- Professional escalation protocols
- Crisis resource verification
- Response time monitoring and alerting

### Authentication Integration
- JWT token validation
- Role-based access control
- Session management
- Secure logout procedures

## Deployment Configuration

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

### Production Checklist
- [ ] HTTPS enabled for all communications
- [ ] WebSocket connections use WSS
- [ ] JWT tokens properly validated
- [ ] CORS configured for trusted domains only
- [ ] Audit logs encrypted and backed up
- [ ] Crisis response monitoring active
- [ ] Accessibility compliance validated
- [ ] Performance benchmarks met

## Version Compatibility

- React: ^18.0.0
- TypeScript: ^4.9.0
- Framer Motion: ^10.0.0
- Node.js: ^18.0.0

## Support and Maintenance

### Documentation
- Component API documentation in `/web-interfaces/shared/src/components/`
- Integration guide in `/web-interfaces/shared/INTEGRATION_GUIDE.md`
- Testing examples and patterns

### Monitoring
- Crisis response time tracking
- Theme switching performance
- Accessibility compliance scores
- HIPAA audit log completeness

### Updates and Versioning
- Semantic versioning for breaking changes
- Backward compatibility maintenance
- Migration guides for major updates
- Regular security updates and patches
