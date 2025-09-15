import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useAuth } from "@tta/shared-components";

/**
 * HIPAA Compliance Provider for Clinical Dashboard
 *
 * Provides HIPAA-compliant audit logging, data protection, and access controls
 * for clinical interfaces. Ensures all clinical data access is properly logged
 * and monitored for compliance with healthcare regulations.
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
  outcome: "success" | "failure" | "warning";
  details?: Record<string, any>;
}

export interface DataAccessLog {
  patientId: string;
  dataType: string;
  accessTime: string;
  purpose: string;
  userId: string;
}

export interface HIPAAComplianceContextType {
  // Audit logging
  logDataAccess: (patientId: string, dataType: string, purpose: string) => void;
  logUserAction: (
    action: string,
    resource: string,
    resourceId?: string,
    details?: Record<string, any>,
  ) => void;
  logSecurityEvent: (
    event: string,
    severity: "low" | "medium" | "high",
    details?: Record<string, any>,
  ) => void;

  // Data protection
  isDataAccessAuthorized: (dataType: string, patientId?: string) => boolean;
  maskSensitiveData: (data: string, dataType: string) => string;

  // Session management
  sessionTimeout: number;
  lastActivity: Date | null;
  updateActivity: () => void;

  // Compliance status
  complianceStatus: "compliant" | "warning" | "violation";
  auditLogs: AuditLogEntry[];
  dataAccessLogs: DataAccessLog[];
}

const HIPAAComplianceContext = createContext<
  HIPAAComplianceContextType | undefined
>(undefined);

export const useHIPAACompliance = () => {
  const context = useContext(HIPAAComplianceContext);
  if (context === undefined) {
    throw new Error(
      "useHIPAACompliance must be used within a HIPAAComplianceProvider",
    );
  }
  return context;
};

interface HIPAAComplianceProviderProps {
  children: ReactNode;
  sessionTimeoutMinutes?: number;
}

export const HIPAAComplianceProvider: React.FC<
  HIPAAComplianceProviderProps
> = ({
  children,
  sessionTimeoutMinutes = 30, // Default 30-minute timeout for clinical sessions
}) => {
  const { user, token, isAuthenticated } = useAuth();
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [dataAccessLogs, setDataAccessLogs] = useState<DataAccessLog[]>([]);
  const [lastActivity, setLastActivity] = useState<Date | null>(null);
  const [complianceStatus, setComplianceStatus] = useState<
    "compliant" | "warning" | "violation"
  >("compliant");

  const sessionTimeout = sessionTimeoutMinutes * 60 * 1000; // Convert to milliseconds

  // Generate unique audit log ID
  const generateAuditId = (): string => {
    return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Get client information for audit logging
  const getClientInfo = () => {
    return {
      ipAddress: "client_ip", // In production, this would be obtained from the request
      userAgent: navigator.userAgent,
      sessionId: token ? "session_from_token" : "no_session",
    };
  };

  // Log data access for HIPAA compliance
  const logDataAccess = (
    patientId: string,
    dataType: string,
    purpose: string,
  ) => {
    if (!user || !isAuthenticated) {
      console.warn("Attempted data access without authentication");
      return;
    }

    const accessLog: DataAccessLog = {
      patientId,
      dataType,
      accessTime: new Date().toISOString(),
      purpose,
      userId: user.id || user.user_id,
    };

    setDataAccessLogs((prev) => [...prev, accessLog]);

    // Also create audit log entry
    logUserAction("data_access", dataType, patientId, {
      purpose,
      dataType,
      patientId,
    });

    console.log("🔒 HIPAA Data Access Logged:", accessLog);
  };

  // Log user actions for audit trail
  const logUserAction = (
    action: string,
    resource: string,
    resourceId?: string,
    details?: Record<string, any>,
  ) => {
    if (!user || !isAuthenticated) {
      console.warn("Attempted action logging without authentication");
      return;
    }

    const clientInfo = getClientInfo();
    const auditEntry: AuditLogEntry = {
      id: generateAuditId(),
      timestamp: new Date().toISOString(),
      userId: user.id || user.user_id,
      username: user.username,
      action,
      resource,
      resourceId,
      ...clientInfo,
      outcome: "success",
      details,
    };

    setAuditLogs((prev) => [...prev, auditEntry]);
    console.log("📋 Audit Log Entry:", auditEntry);
  };

  // Log security events
  const logSecurityEvent = (
    event: string,
    severity: "low" | "medium" | "high",
    details?: Record<string, any>,
  ) => {
    const clientInfo = getClientInfo();
    const auditEntry: AuditLogEntry = {
      id: generateAuditId(),
      timestamp: new Date().toISOString(),
      userId: user?.id || user?.user_id || "anonymous",
      username: user?.username || "anonymous",
      action: "security_event",
      resource: "system",
      ...clientInfo,
      outcome: severity === "high" ? "failure" : "warning",
      details: { event, severity, ...details },
    };

    setAuditLogs((prev) => [...prev, auditEntry]);

    // Update compliance status based on severity
    if (severity === "high") {
      setComplianceStatus("violation");
    } else if (severity === "medium" && complianceStatus === "compliant") {
      setComplianceStatus("warning");
    }

    console.log(`🚨 Security Event [${severity.toUpperCase()}]:`, auditEntry);
  };

  // Check if data access is authorized
  const isDataAccessAuthorized = (
    dataType: string,
    patientId?: string,
  ): boolean => {
    if (!user || !isAuthenticated) {
      return false;
    }

    // Check user permissions for data type
    const userPermissions = user.permissions || [];

    switch (dataType) {
      case "patient_progress":
        return userPermissions.includes("view_patient_progress");
      case "therapeutic_content":
        return userPermissions.includes("manage_therapeutic_content");
      case "crisis_protocols":
        return userPermissions.includes("access_crisis_protocols");
      case "anonymized_data":
        return userPermissions.includes("view_anonymized_data");
      default:
        return false;
    }
  };

  // Mask sensitive data based on type
  const maskSensitiveData = (data: string, dataType: string): string => {
    switch (dataType) {
      case "patient_id":
        return data.replace(/(.{3}).*(.{3})/, "$1***$2");
      case "email":
        return data.replace(/(.{2}).*(@.*)/, "$1***$2");
      case "phone":
        return data.replace(/(\d{3}).*(\d{4})/, "$1-***-$2");
      case "ssn":
        return "***-**-" + data.slice(-4);
      default:
        return data;
    }
  };

  // Update last activity timestamp
  const updateActivity = () => {
    setLastActivity(new Date());
  };

  // Session timeout monitoring
  useEffect(() => {
    if (!isAuthenticated) return;

    const checkSessionTimeout = () => {
      if (lastActivity) {
        const timeSinceActivity = Date.now() - lastActivity.getTime();
        if (timeSinceActivity > sessionTimeout) {
          logSecurityEvent("session_timeout", "medium", {
            timeSinceActivity,
            sessionTimeout,
          });
          // In production, this would trigger logout
          console.warn("🕐 Session timeout detected");
        }
      }
    };

    const timeoutInterval = setInterval(checkSessionTimeout, 60000); // Check every minute
    return () => clearInterval(timeoutInterval);
  }, [lastActivity, sessionTimeout, isAuthenticated]);

  // Initialize activity tracking
  useEffect(() => {
    if (isAuthenticated) {
      updateActivity();
      logUserAction("session_start", "clinical_dashboard");
    }
  }, [isAuthenticated]);

  // Activity tracking for user interactions
  useEffect(() => {
    const handleUserActivity = () => {
      updateActivity();
    };

    // Track various user activities
    const events = [
      "mousedown",
      "mousemove",
      "keypress",
      "scroll",
      "touchstart",
    ];
    events.forEach((event) => {
      document.addEventListener(event, handleUserActivity, true);
    });

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleUserActivity, true);
      });
    };
  }, []);

  const value: HIPAAComplianceContextType = {
    logDataAccess,
    logUserAction,
    logSecurityEvent,
    isDataAccessAuthorized,
    maskSensitiveData,
    sessionTimeout,
    lastActivity,
    updateActivity,
    complianceStatus,
    auditLogs,
    dataAccessLogs,
  };

  return (
    <HIPAAComplianceContext.Provider value={value}>
      {children}
    </HIPAAComplianceContext.Provider>
  );
};

export default HIPAAComplianceProvider;
