import { useState, useEffect, useCallback, useRef } from "react";
import { nexusAPI } from "../services/api";

export interface SystemStatus {
  api_status: "healthy" | "degraded" | "critical" | "offline";
  database_status: "connected" | "disconnected" | "error";
  nexus_hub_status: "active" | "maintenance" | "offline";
  websocket_status: "connected" | "disconnected" | "error";
  last_health_check: string;
  response_time: number;
  error_count: number;
  uptime: number;
}

export interface StatusAlert {
  id: string;
  type: "error" | "warning" | "info" | "success";
  title: string;
  message: string;
  timestamp: string;
  dismissible: boolean;
  autoHide?: number; // milliseconds
}

export interface UseStatusMonitoringOptions {
  enableHealthChecks?: boolean;
  healthCheckInterval?: number;
  enableAlerts?: boolean;
  maxRetries?: number;
  retryDelay?: number;
  onStatusChange?: (status: SystemStatus) => void;
  onAlert?: (alert: StatusAlert) => void;
}

export interface UseStatusMonitoringResult {
  systemStatus: SystemStatus | null;
  isHealthy: boolean;
  alerts: StatusAlert[];
  lastHealthCheck: Date | null;
  isMonitoring: boolean;
  error: string | null;

  // Actions
  performHealthCheck: () => Promise<void>;
  dismissAlert: (alertId: string) => void;
  clearAllAlerts: () => void;
  startMonitoring: () => void;
  stopMonitoring: () => void;
  clearError: () => void;
}

/**
 * Custom hook for comprehensive system status monitoring
 *
 * Features:
 * - Automated health checks
 * - System status tracking
 * - Alert management
 * - Error recovery
 * - Performance monitoring
 */
export const useStatusMonitoring = (
  options: UseStatusMonitoringOptions = {}
): UseStatusMonitoringResult => {
  const {
    enableHealthChecks = true,
    healthCheckInterval = 60000, // 1 minute
    enableAlerts = true,
    maxRetries = 3,
    retryDelay = 2000,
    onStatusChange,
    onAlert,
  } = options;

  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [alerts, setAlerts] = useState<StatusAlert[]>([]);
  const [lastHealthCheck, setLastHealthCheck] = useState<Date | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const healthCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);
  const mountedRef = useRef(true);

  /**
   * Create and dispatch an alert
   */
  const createAlert = useCallback(
    (
      type: StatusAlert["type"],
      title: string,
      message: string,
      options: { dismissible?: boolean; autoHide?: number } = {}
    ) => {
      if (!enableAlerts || !mountedRef.current) return;

      const alert: StatusAlert = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        type,
        title,
        message,
        timestamp: new Date().toISOString(),
        dismissible: options.dismissible ?? true,
        autoHide: options.autoHide,
      };

      setAlerts((prev) => [alert, ...prev.slice(0, 9)]); // Keep last 10 alerts
      onAlert?.(alert);

      // Auto-hide alert if specified
      if (alert.autoHide) {
        setTimeout(() => {
          setAlerts((prev) => prev.filter((a) => a.id !== alert.id));
        }, alert.autoHide);
      }
    },
    [enableAlerts, onAlert]
  );

  /**
   * Dismiss a specific alert
   */
  const dismissAlert = useCallback((alertId: string) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
  }, []);

  /**
   * Clear all alerts
   */
  const clearAllAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Perform a comprehensive health check
   */
  const performHealthCheck = useCallback(async () => {
    if (!mountedRef.current) return;

    const startTime = Date.now();

    try {
      setError(null);

      // Test API connectivity
      const healthResponse = await Promise.race([
        nexusAPI.getState(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Health check timeout")), 10000)
        ),
      ]);

      const responseTime = Date.now() - startTime;
      const currentTime = new Date().toISOString();

      // Determine system status based on response
      let apiStatus: SystemStatus["api_status"] = "healthy";
      let nexusHubStatus: SystemStatus["nexus_hub_status"] = "active";

      if (responseTime > 5000) {
        apiStatus = "degraded";
        createAlert(
          "warning",
          "Slow Response",
          `API response time is ${responseTime}ms (>5s)`,
          { autoHide: 10000 }
        );
      } else if (responseTime > 2000) {
        apiStatus = "degraded";
      }

      // Check if maintenance mode is active
      if (
        healthResponse &&
        typeof healthResponse === "object" &&
        "maintenance_mode" in healthResponse &&
        healthResponse.maintenance_mode
      ) {
        nexusHubStatus = "maintenance";
        createAlert(
          "info",
          "Maintenance Mode",
          "The system is currently in maintenance mode",
          { dismissible: false }
        );
      }

      const newStatus: SystemStatus = {
        api_status: apiStatus,
        database_status: "connected", // Assume connected if API responds
        nexus_hub_status: nexusHubStatus,
        websocket_status: "connected", // This would be updated by WebSocket hooks
        last_health_check: currentTime,
        response_time: responseTime,
        error_count: 0,
        uptime: Date.now(), // This would be calculated from server start time
      };

      setSystemStatus(newStatus);
      setLastHealthCheck(new Date());
      retryCountRef.current = 0;
      onStatusChange?.(newStatus);

      // Success alert for recovery
      if (
        systemStatus?.api_status === "critical" ||
        systemStatus?.api_status === "offline"
      ) {
        createAlert(
          "success",
          "System Recovered",
          "Connection to the system has been restored",
          { autoHide: 5000 }
        );
      }
    } catch (err: any) {
      console.error("Health check failed:", err);

      const errorMessage = err.message || "Health check failed";
      setError(errorMessage);

      // Determine severity based on error type
      let apiStatus: SystemStatus["api_status"] = "critical";
      let alertType: StatusAlert["type"] = "error";
      let alertTitle = "System Error";

      if (
        err.message?.includes("timeout") ||
        err.message?.includes("Network Error")
      ) {
        apiStatus = "offline";
        alertTitle = "Connection Lost";
      } else if (err.status >= 500) {
        apiStatus = "critical";
        alertTitle = "Server Error";
      } else if (err.status >= 400) {
        apiStatus = "degraded";
        alertType = "warning";
        alertTitle = "Service Issue";
      }

      const newStatus: SystemStatus = {
        api_status: apiStatus,
        database_status: "error",
        nexus_hub_status: "offline",
        websocket_status: "disconnected",
        last_health_check: new Date().toISOString(),
        response_time: Date.now() - startTime,
        error_count: (systemStatus?.error_count || 0) + 1,
        uptime: 0,
      };

      setSystemStatus(newStatus);
      setLastHealthCheck(new Date());
      onStatusChange?.(newStatus);

      // Create alert for the error
      createAlert(alertType, alertTitle, errorMessage, { dismissible: true });

      // Attempt retry if within limits
      if (retryCountRef.current < maxRetries) {
        retryCountRef.current++;

        createAlert(
          "info",
          "Retrying Connection",
          `Attempting to reconnect... (${retryCountRef.current}/${maxRetries})`,
          { autoHide: 3000 }
        );

        retryTimeoutRef.current = setTimeout(() => {
          if (mountedRef.current) {
            performHealthCheck();
          }
        }, retryDelay * retryCountRef.current);
      } else {
        createAlert(
          "error",
          "Connection Failed",
          "Unable to connect to the system after multiple attempts",
          { dismissible: true }
        );
      }
    }
  }, [systemStatus, maxRetries, retryDelay, createAlert, onStatusChange]);

  /**
   * Start monitoring
   */
  const startMonitoring = useCallback(() => {
    if (!enableHealthChecks || isMonitoring) return;

    setIsMonitoring(true);

    // Perform initial health check
    performHealthCheck();

    // Set up periodic health checks
    healthCheckIntervalRef.current = setInterval(() => {
      if (mountedRef.current) {
        performHealthCheck();
      }
    }, healthCheckInterval);

    createAlert(
      "info",
      "Monitoring Started",
      "System health monitoring is now active",
      { autoHide: 3000 }
    );
  }, [
    enableHealthChecks,
    isMonitoring,
    performHealthCheck,
    healthCheckInterval,
    createAlert,
  ]);

  /**
   * Stop monitoring
   */
  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);

    if (healthCheckIntervalRef.current) {
      clearInterval(healthCheckIntervalRef.current);
      healthCheckIntervalRef.current = null;
    }

    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    createAlert(
      "info",
      "Monitoring Stopped",
      "System health monitoring has been disabled",
      { autoHide: 3000 }
    );
  }, [createAlert]);

  /**
   * Initialize monitoring on mount
   * Fixed: Removed startMonitoring and stopMonitoring from dependencies to prevent infinite loop
   */
  const monitoringInitializedRef = useRef(false);

  useEffect(() => {
    if (enableHealthChecks && !monitoringInitializedRef.current) {
      monitoringInitializedRef.current = true;
      startMonitoring();
    }

    return () => {
      mountedRef.current = false;
      if (monitoringInitializedRef.current) {
        stopMonitoring();
      }
    };
  }, [enableHealthChecks]); // Only depend on enableHealthChecks

  // Computed values
  const isHealthy =
    systemStatus?.api_status === "healthy" &&
    systemStatus?.database_status === "connected" &&
    systemStatus?.nexus_hub_status === "active";

  return {
    systemStatus,
    isHealthy,
    alerts,
    lastHealthCheck,
    isMonitoring,
    error,
    performHealthCheck,
    dismissAlert,
    clearAllAlerts,
    startMonitoring,
    stopMonitoring,
    clearError,
  };
};

/**
 * Simplified hook for basic health monitoring
 */
export const useBasicHealthCheck = () => {
  const { systemStatus, isHealthy, performHealthCheck } = useStatusMonitoring({
    enableHealthChecks: true,
    healthCheckInterval: 120000, // 2 minutes
    enableAlerts: false,
  });

  return {
    isHealthy,
    apiStatus: systemStatus?.api_status || "offline",
    responseTime: systemStatus?.response_time || 0,
    lastCheck: systemStatus?.last_health_check,
    checkHealth: performHealthCheck,
  };
};

export default useStatusMonitoring;
