import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { useAuth } from '../auth/AuthProvider';

/**
 * HIPAA Compliance Provider for All TTA Interfaces
 *
 * Provides HIPAA-compliant audit logging, data protection, and access controls
 * for all interfaces that handle clinical data. Ensures all clinical data access
 * is properly logged and monitored for compliance with healthcare regulations.
 */

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceId?: string;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
  outcome: 'success' | 'failure' | 'warning';
  interfaceType: 'patient' | 'clinical' | 'admin' | 'public' | 'stakeholder' | 'docs';
  details?: Record<string, any>;
}

export interface DataAccessLog {
  patientId: string;
  dataType: string;
  accessTime: string;
  purpose: string;
  userId: string;
  interfaceType: string;
  authorized: boolean;
}

export interface SecurityEvent {
  type: 'login_attempt' | 'unauthorized_access' | 'data_breach' | 'session_timeout' | 'suspicious_activity';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  userId?: string;
  ipAddress: string;
  timestamp: string;
  interfaceType: string;
}

export interface HIPAAComplianceContextType {
  // Audit logging
  logDataAccess: (patientId: string, dataType: string, purpose: string) => void;
  logUserAction: (
    action: string,
    resource: string,
    resourceId?: string,
    details?: Record<string, any>
  ) => void;
  logSecurityEvent: (
    type: SecurityEvent['type'],
    severity: SecurityEvent['severity'],
    description: string,
    details?: Record<string, any>
  ) => void;

  // Data protection
  isDataAccessAuthorized: (dataType: string, patientId?: string) => boolean;
  maskSensitiveData: (data: string, dataType: string) => string;
  encryptSensitiveData: (data: string) => string;
  decryptSensitiveData: (encryptedData: string) => string;

  // Session management
  sessionTimeout: number;
  lastActivity: Date | null;
  updateActivity: () => void;
  isSessionValid: () => boolean;
  extendSession: () => void;

  // Compliance status
  complianceStatus: 'compliant' | 'warning' | 'violation';
  auditLogs: AuditLogEntry[];
  dataAccessLogs: DataAccessLog[];
  securityEvents: SecurityEvent[];

  // Interface-specific compliance
  interfaceType: string;
  clinicalDataAccess: boolean;
  requiresAuditTrail: boolean;

  // Compliance reporting
  generateComplianceReport: () => ComplianceReport;
  exportAuditLogs: (startDate: Date, endDate: Date) => AuditLogEntry[];
}

export interface ComplianceReport {
  reportId: string;
  generatedAt: string;
  interfaceType: string;
  complianceScore: number;
  totalAuditEntries: number;
  securityIncidents: number;
  dataAccessViolations: number;
  recommendations: string[];
}

const HIPAAComplianceContext = createContext<HIPAAComplianceContextType | undefined>(undefined);

export const useHIPAACompliance = () => {
  const context = useContext(HIPAAComplianceContext);
  if (context === undefined) {
    throw new Error('useHIPAACompliance must be used within a HIPAAComplianceProvider');
  }
  return context;
};

interface HIPAAComplianceProviderProps {
  children: ReactNode;
  interfaceType: 'patient' | 'clinical' | 'admin' | 'public' | 'stakeholder' | 'docs';
  sessionTimeoutMinutes?: number;
  enableAuditLogging?: boolean;
  clinicalDataAccess?: boolean;
  apiBaseUrl?: string;
}

export const HIPAAComplianceProvider: React.FC<HIPAAComplianceProviderProps> = ({
  children,
  interfaceType,
  sessionTimeoutMinutes = 30, // Default 30-minute timeout for clinical sessions
  enableAuditLogging = true,
  clinicalDataAccess = false,
  apiBaseUrl = 'http://localhost:8080',
}) => {
  const { user, token, isAuthenticated } = useAuth();
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [dataAccessLogs, setDataAccessLogs] = useState<DataAccessLog[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [lastActivity, setLastActivity] = useState<Date | null>(null);
  const [complianceStatus, setComplianceStatus] = useState<'compliant' | 'warning' | 'violation'>('compliant');

  const sessionTimeout = sessionTimeoutMinutes * 60 * 1000; // Convert to milliseconds
  const requiresAuditTrail = clinicalDataAccess || interfaceType === 'clinical' || interfaceType === 'admin';

  // Initialize activity tracking
  useEffect(() => {
    if (isAuthenticated) {
      setLastActivity(new Date());
    }
  }, [isAuthenticated]);

  // Session timeout monitoring
  useEffect(() => {
    if (!isAuthenticated || !lastActivity) return;

    const checkSessionTimeout = () => {
      const now = new Date();
      const timeSinceLastActivity = now.getTime() - lastActivity.getTime();

      if (timeSinceLastActivity > sessionTimeout) {
        logSecurityEvent('session_timeout', 'medium', 'User session timed out due to inactivity');
        // In a real implementation, this would trigger logout
        console.warn('Session timeout detected');
      }
    };

    const interval = setInterval(checkSessionTimeout, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [lastActivity, sessionTimeout, isAuthenticated]);

  // Activity tracking
  const updateActivity = useCallback(() => {
    setLastActivity(new Date());
  }, []);

  // Session validation
  const isSessionValid = useCallback(() => {
    if (!lastActivity) return false;
    const now = new Date();
    const timeSinceLastActivity = now.getTime() - lastActivity.getTime();
    return timeSinceLastActivity < sessionTimeout;
  }, [lastActivity, sessionTimeout]);

  // Extend session
  const extendSession = useCallback(() => {
    updateActivity();
    logUserAction('session_extended', 'session', user?.id);
  }, [updateActivity, user?.id]);

  // Generate unique ID for logs
  const generateLogId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // Get client IP (simplified for demo)
  const getClientIP = () => '127.0.0.1'; // In production, this would be properly detected

  // Log data access
  const logDataAccess = useCallback((patientId: string, dataType: string, purpose: string) => {
    if (!enableAuditLogging) return;

    const authorized = isDataAccessAuthorized(dataType, patientId);

    const accessLog: DataAccessLog = {
      patientId,
      dataType,
      accessTime: new Date().toISOString(),
      purpose,
      userId: user?.id || 'anonymous',
      interfaceType,
      authorized,
    };

    setDataAccessLogs(prev => [...prev, accessLog]);

    // Also create audit log entry
    logUserAction('data_access', dataType, patientId, {
      purpose,
      authorized,
      patientId,
    });

    if (!authorized) {
      setComplianceStatus('violation');
      logSecurityEvent('unauthorized_access', 'high', `Unauthorized access to ${dataType} for patient ${patientId}`);
    }
  }, [enableAuditLogging, user?.id, interfaceType]);

  // Log user action
  const logUserAction = useCallback((
    action: string,
    resource: string,
    resourceId?: string,
    details?: Record<string, any>
  ) => {
    if (!enableAuditLogging) return;

    const auditEntry: AuditLogEntry = {
      id: generateLogId(),
      timestamp: new Date().toISOString(),
      userId: user?.id || 'anonymous',
      username: user?.username || 'anonymous',
      action,
      resource,
      resourceId,
      ipAddress: getClientIP(),
      userAgent: navigator.userAgent,
      sessionId: token?.substring(0, 8) || 'no-session',
      outcome: 'success',
      interfaceType,
      details,
    };

    setAuditLogs(prev => [...prev, auditEntry]);
    updateActivity();
  }, [enableAuditLogging, user, token, interfaceType, updateActivity]);

  // Log security event
  const logSecurityEvent = useCallback((
    type: SecurityEvent['type'],
    severity: SecurityEvent['severity'],
    description: string,
    details?: Record<string, any>
  ) => {
    const securityEvent: SecurityEvent = {
      type,
      severity,
      description,
      userId: user?.id,
      ipAddress: getClientIP(),
      timestamp: new Date().toISOString(),
      interfaceType,
    };

    setSecurityEvents(prev => [...prev, securityEvent]);

    // Also create audit log entry for security events
    logUserAction('security_event', type, undefined, {
      severity,
      description,
      ...details,
    });

    // Update compliance status based on severity
    if (severity === 'critical' || severity === 'high') {
      setComplianceStatus('violation');
    } else if (severity === 'medium' && complianceStatus === 'compliant') {
      setComplianceStatus('warning');
    }
  }, [user?.id, interfaceType, logUserAction, complianceStatus]);

  // Data access authorization
  const isDataAccessAuthorized = useCallback((dataType: string, patientId?: string): boolean => {
    if (!user || !isAuthenticated) return false;

    // Interface-specific authorization rules
    switch (interfaceType) {
      case 'clinical':
        // Clinical users can access all patient data
        return user.role === 'clinician' || user.role === 'admin';

      case 'patient':
        // Patients can only access their own data
        return patientId === user.id;

      case 'admin':
        // Admins can access all data
        return user.role === 'admin';

      case 'public':
        // Public interface has no access to patient data
        return false;

      case 'stakeholder':
        // Stakeholders can access aggregated/anonymized data only
        return dataType.includes('aggregated') || dataType.includes('anonymous');

      case 'docs':
        // Documentation interface has no access to patient data
        return false;

      default:
        return false;
    }
  }, [user, isAuthenticated, interfaceType]);

  // Mask sensitive data
  const maskSensitiveData = useCallback((data: string, dataType: string): string => {
    if (!data) return data;

    switch (dataType) {
      case 'ssn':
        return data.replace(/\d(?=\d{4})/g, '*');
      case 'phone':
        return data.replace(/\d(?=\d{4})/g, '*');
      case 'email':
        const [local, domain] = data.split('@');
        return `${local.charAt(0)}***@${domain}`;
      case 'name':
        return data.split(' ').map(part => part.charAt(0) + '*'.repeat(part.length - 1)).join(' ');
      default:
        return data.length > 4 ? data.substring(0, 2) + '*'.repeat(data.length - 4) + data.substring(data.length - 2) : data;
    }
  }, []);

  // Simple encryption/decryption (in production, use proper encryption)
  const encryptSensitiveData = useCallback((data: string): string => {
    // This is a placeholder - use proper encryption in production
    return btoa(data);
  }, []);

  const decryptSensitiveData = useCallback((encryptedData: string): string => {
    // This is a placeholder - use proper decryption in production
    try {
      return atob(encryptedData);
    } catch {
      return encryptedData;
    }
  }, []);

  // Generate compliance report
  const generateComplianceReport = useCallback((): ComplianceReport => {
    const now = new Date();
    const securityIncidents = securityEvents.filter(event =>
      event.severity === 'high' || event.severity === 'critical'
    ).length;

    const dataAccessViolations = dataAccessLogs.filter(log => !log.authorized).length;

    // Calculate compliance score (0-100)
    let score = 100;
    score -= securityIncidents * 10;
    score -= dataAccessViolations * 15;
    score = Math.max(0, score);

    const recommendations: string[] = [];
    if (securityIncidents > 0) {
      recommendations.push('Review and address security incidents');
    }
    if (dataAccessViolations > 0) {
      recommendations.push('Investigate unauthorized data access attempts');
    }
    if (score < 80) {
      recommendations.push('Implement additional security measures');
    }

    return {
      reportId: generateLogId(),
      generatedAt: now.toISOString(),
      interfaceType,
      complianceScore: score,
      totalAuditEntries: auditLogs.length,
      securityIncidents,
      dataAccessViolations,
      recommendations,
    };
  }, [securityEvents, dataAccessLogs, auditLogs, interfaceType]);

  // Export audit logs
  const exportAuditLogs = useCallback((startDate: Date, endDate: Date): AuditLogEntry[] => {
    return auditLogs.filter(log => {
      const logDate = new Date(log.timestamp);
      return logDate >= startDate && logDate <= endDate;
    });
  }, [auditLogs]);

  const value: HIPAAComplianceContextType = {
    logDataAccess,
    logUserAction,
    logSecurityEvent,
    isDataAccessAuthorized,
    maskSensitiveData,
    encryptSensitiveData,
    decryptSensitiveData,
    sessionTimeout,
    lastActivity,
    updateActivity,
    isSessionValid,
    extendSession,
    complianceStatus,
    auditLogs,
    dataAccessLogs,
    securityEvents,
    interfaceType,
    clinicalDataAccess,
    requiresAuditTrail,
    generateComplianceReport,
    exportAuditLogs,
  };

  return (
    <HIPAAComplianceContext.Provider value={value}>
      {children}
    </HIPAAComplianceContext.Provider>
  );
};

export default HIPAAComplianceProvider;
