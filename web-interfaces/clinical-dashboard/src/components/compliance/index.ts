/**
 * HIPAA Compliance Components for Clinical Dashboard
 *
 * This module provides comprehensive HIPAA compliance features including:
 * - Audit logging for all clinical data access
 * - Data protection and access controls
 * - Session management and timeout monitoring
 * - Security event logging and monitoring
 */

export { HIPAAComplianceProvider, useHIPAACompliance } from './HIPAAComplianceProvider';

// Re-export types for external use
export type {
  AuditLogEntry,
  DataAccessLog,
  HIPAAComplianceContextType,
} from './HIPAAComplianceProvider';
