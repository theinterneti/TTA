import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStatusMonitoring, StatusAlert } from '../../hooks/useStatusMonitoring';

interface StatusMonitoringDisplayProps {
  variant?: 'full' | 'compact' | 'alerts-only';
  className?: string;
  showAlerts?: boolean;
  showHealthCheck?: boolean;
  autoHideAlerts?: boolean;
}

const StatusMonitoringDisplay: React.FC<StatusMonitoringDisplayProps> = ({
  variant = 'full',
  className = '',
  showAlerts = true,
  showHealthCheck = true,
  autoHideAlerts = true,
}) => {
  const {
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
  } = useStatusMonitoring({
    enableHealthChecks: true,
    healthCheckInterval: 60000,
    enableAlerts: showAlerts,
    maxRetries: 3,
    retryDelay: 2000,
  });

  const [showDetails, setShowDetails] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'degraded':
      case 'maintenance':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'offline':
      case 'disconnected':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
        return '✅';
      case 'degraded':
      case 'maintenance':
        return '⚠️';
      case 'critical':
      case 'error':
        return '🚨';
      case 'offline':
      case 'disconnected':
        return '🔴';
      default:
        return '❓';
    }
  };

  const getAlertIcon = (type: StatusAlert['type']) => {
    switch (type) {
      case 'success': return '✅';
      case 'info': return 'ℹ️';
      case 'warning': return '⚠️';
      case 'error': return '🚨';
      default: return 'ℹ️';
    }
  };

  const getAlertColor = (type: StatusAlert['type']) => {
    switch (type) {
      case 'success': return 'border-green-200 bg-green-50 text-green-800';
      case 'info': return 'border-blue-200 bg-blue-50 text-blue-800';
      case 'warning': return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'error': return 'border-red-200 bg-red-50 text-red-800';
      default: return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const formatResponseTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const AlertItem: React.FC<{ alert: StatusAlert }> = ({ alert }) => (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      className={`border rounded-lg p-3 ${getAlertColor(alert.type)}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-2">
          <span className="text-lg">{getAlertIcon(alert.type)}</span>
          <div className="flex-1">
            <h4 className="font-medium text-sm">{alert.title}</h4>
            <p className="text-xs mt-1 opacity-90">{alert.message}</p>
            <p className="text-xs mt-1 opacity-75">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>
        {alert.dismissible && (
          <button
            onClick={() => dismissAlert(alert.id)}
            className="text-current opacity-60 hover:opacity-100 transition-opacity"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </motion.div>
  );

  const renderCompactView = () => (
    <div className="flex items-center space-x-3">
      {systemStatus && (
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(systemStatus.api_status)}`}>
          {getStatusIcon(systemStatus.api_status)} System {systemStatus.api_status}
        </div>
      )}
      
      {isMonitoring && (
        <div className="flex items-center space-x-1 text-xs text-gray-600">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Monitoring</span>
        </div>
      )}
      
      {error && (
        <div className="text-xs text-red-600 flex items-center space-x-1">
          <span>🚨</span>
          <span>Error</span>
        </div>
      )}
    </div>
  );

  const renderFullView = () => (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
        <div className="flex items-center space-x-2">
          {isMonitoring ? (
            <button
              onClick={stopMonitoring}
              className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
            >
              Stop Monitoring
            </button>
          ) : (
            <button
              onClick={startMonitoring}
              className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
            >
              Start Monitoring
            </button>
          )}
          
          {showHealthCheck && (
            <button
              onClick={performHealthCheck}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
            >
              Check Now
            </button>
          )}
        </div>
      </div>

      {/* Overall Status */}
      <div className={`p-4 rounded-lg border-2 ${isHealthy ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">
              {isHealthy ? '✅' : '🚨'}
            </div>
            <div>
              <h4 className={`font-semibold ${isHealthy ? 'text-green-800' : 'text-red-800'}`}>
                System {isHealthy ? 'Healthy' : 'Issues Detected'}
              </h4>
              <p className={`text-sm ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
                {isHealthy 
                  ? 'All systems operational' 
                  : 'Some services may be experiencing issues'
                }
              </p>
            </div>
          </div>
          
          {lastHealthCheck && (
            <div className="text-right">
              <p className="text-xs text-gray-600">Last checked</p>
              <p className="text-sm font-medium text-gray-900">
                {lastHealthCheck.toLocaleTimeString()}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Status */}
      {systemStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Service Status</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">API Server</span>
                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(systemStatus.api_status)}`}>
                  {getStatusIcon(systemStatus.api_status)} {systemStatus.api_status}
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">Database</span>
                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(systemStatus.database_status)}`}>
                  {getStatusIcon(systemStatus.database_status)} {systemStatus.database_status}
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">Nexus Hub</span>
                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(systemStatus.nexus_hub_status)}`}>
                  {getStatusIcon(systemStatus.nexus_hub_status)} {systemStatus.nexus_hub_status}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Performance</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">Response Time</span>
                <span className="text-sm font-medium">
                  {formatResponseTime(systemStatus.response_time)}
                </span>
              </div>
              
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">Error Count</span>
                <span className="text-sm font-medium">
                  {systemStatus.error_count}
                </span>
              </div>
              
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">Monitoring</span>
                <span className={`text-sm font-medium ${isMonitoring ? 'text-green-600' : 'text-gray-600'}`}>
                  {isMonitoring ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-red-500">🚨</span>
              <div>
                <h4 className="text-sm font-medium text-red-800">System Error</h4>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
            <button
              onClick={clearError}
              className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderAlertsOnly = () => (
    <div className="space-y-2">
      {alerts.length > 0 && (
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900">System Alerts ({alerts.length})</h4>
          <button
            onClick={clearAllAlerts}
            className="text-xs text-gray-600 hover:text-gray-800 underline"
          >
            Clear All
          </button>
        </div>
      )}
      
      <AnimatePresence>
        {alerts.map((alert) => (
          <AlertItem key={alert.id} alert={alert} />
        ))}
      </AnimatePresence>
      
      {alerts.length === 0 && (
        <div className="text-center py-4 text-gray-500 text-sm">
          No system alerts
        </div>
      )}
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-sm ${className}`}>
      {variant === 'compact' && renderCompactView()}
      {variant === 'full' && (
        <div className="p-6">
          {renderFullView()}
          
          {/* Alerts Section */}
          {showAlerts && alerts.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">Recent Alerts</h4>
                <button
                  onClick={clearAllAlerts}
                  className="text-xs text-gray-600 hover:text-gray-800 underline"
                >
                  Clear All
                </button>
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                <AnimatePresence>
                  {alerts.slice(0, 5).map((alert) => (
                    <AlertItem key={alert.id} alert={alert} />
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>
      )}
      {variant === 'alerts-only' && (
        <div className="p-4">
          {renderAlertsOnly()}
        </div>
      )}
    </div>
  );
};

export default StatusMonitoringDisplay;
