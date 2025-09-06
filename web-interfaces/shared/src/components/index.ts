export { default as ErrorBoundary, withErrorBoundary, useErrorHandler, APIErrorBoundary, ThreeDErrorBoundary } from './ErrorBoundary';
export { LoadingSpinner } from './LoadingSpinner';
export { ProtectedRoute } from './ProtectedRoute';

// Crisis Support Components
export {
  default as CrisisSupportProvider,
  CrisisSupportProvider,
  useCrisisSupport,
  useCrisisDetection,
  CrisisSupportButton,
  CrisisLevel
} from './CrisisSupport';
export type { CrisisAssessment, CrisisIndicator } from './CrisisSupport';

// Therapeutic Theme Components
export {
  default as TherapeuticThemeProvider,
  TherapeuticThemeProvider,
  useTherapeuticTheme,
  ThemeSelector
} from './TherapeuticThemeProvider';
export type {
  TherapeuticTheme,
  ColorMode,
  FontSize,
  MotionPreference,
  TherapeuticColorScheme
} from './TherapeuticThemeProvider';

// Accessibility Components
export {
  default as AccessibilityProvider,
  AccessibilityProvider,
  useAccessibility
} from './AccessibilityProvider';
export type {
  ScreenReaderMode,
  KeyboardNavigationMode,
  FocusIndicatorStyle,
  AnnouncementLevel,
  AccessibilitySettings,
  AccessibilityIssue,
  FormAccessibilityReport
} from './AccessibilityProvider';

// HIPAA Compliance Components
export {
  default as HIPAAComplianceProvider,
  HIPAAComplianceProvider,
  useHIPAACompliance
} from './HIPAAComplianceProvider';
export type {
  AuditLogEntry,
  DataAccessLog,
  SecurityEvent,
  HIPAAComplianceContextType,
  ComplianceReport
} from './HIPAAComplianceProvider';

// Re-export auth components
export { AuthProvider, useAuth } from '../auth/AuthProvider';
export { default as OAuthLogin } from '../auth/OAuthLogin';
export { default as OAuthCallback } from '../auth/OAuthCallback';
export type { User, AuthContextType } from '../auth/AuthProvider';
export type { OAuthProvider, OAuthLoginProps } from '../auth/OAuthLogin';
export type { OAuthCallbackProps } from '../auth/OAuthCallback';
