/**
 * Notification Provider Component
 * 
 * Provides a context for displaying toast notifications throughout the app.
 * Integrates with error handling utilities to show user-friendly error messages.
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { ErrorSeverity, ErrorNotification, createErrorNotification } from '../../utils/errorHandling';
import './Notifications.css';

interface NotificationContextType {
  showNotification: (notification: Partial<ErrorNotification>) => void;
  showError: (error: any, context?: string) => void;
  showSuccess: (message: string) => void;
  showWarning: (message: string) => void;
  showInfo: (message: string) => void;
  clearNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
  maxNotifications?: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
  maxNotifications = 5,
}) => {
  const [notifications, setNotifications] = useState<ErrorNotification[]>([]);

  const showNotification = useCallback((notification: Partial<ErrorNotification>) => {
    const fullNotification: ErrorNotification = {
      id: notification.id || `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message: notification.message || 'Notification',
      severity: notification.severity || ErrorSeverity.INFO,
      dismissible: notification.dismissible ?? true,
      autoHideDuration: notification.autoHideDuration ?? 5000,
      action: notification.action,
    };

    setNotifications((prev) => {
      const updated = [...prev, fullNotification];
      // Keep only the most recent notifications
      return updated.slice(-maxNotifications);
    });

    // Auto-hide if duration is set
    if (fullNotification.autoHideDuration) {
      setTimeout(() => {
        clearNotification(fullNotification.id);
      }, fullNotification.autoHideDuration);
    }
  }, [maxNotifications]);

  const showError = useCallback((error: any, context?: string) => {
    const notification = createErrorNotification(error, context);
    showNotification(notification);
  }, [showNotification]);

  const showSuccess = useCallback((message: string) => {
    showNotification({
      message,
      severity: ErrorSeverity.INFO,
      autoHideDuration: 3000,
    });
  }, [showNotification]);

  const showWarning = useCallback((message: string) => {
    showNotification({
      message,
      severity: ErrorSeverity.WARNING,
      autoHideDuration: 5000,
    });
  }, [showNotification]);

  const showInfo = useCallback((message: string) => {
    showNotification({
      message,
      severity: ErrorSeverity.INFO,
      autoHideDuration: 4000,
    });
  }, [showNotification]);

  const clearNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const value: NotificationContextType = {
    showNotification,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    clearNotification,
    clearAll,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer
        notifications={notifications}
        onDismiss={clearNotification}
      />
    </NotificationContext.Provider>
  );
};

interface NotificationContainerProps {
  notifications: ErrorNotification[];
  onDismiss: (id: string) => void;
}

const NotificationContainer: React.FC<NotificationContainerProps> = ({
  notifications,
  onDismiss,
}) => {
  if (notifications.length === 0) return null;

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
};

interface NotificationItemProps {
  notification: ErrorNotification;
  onDismiss: (id: string) => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onDismiss,
}) => {
  const getSeverityIcon = () => {
    switch (notification.severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.ERROR:
        return (
          <svg className="notification-icon" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case ErrorSeverity.WARNING:
        return (
          <svg className="notification-icon" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case ErrorSeverity.INFO:
      default:
        return (
          <svg className="notification-icon" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  return (
    <div className={`notification notification-${notification.severity}`}>
      <div className="notification-content">
        <div className="notification-icon-wrapper">
          {getSeverityIcon()}
        </div>
        <div className="notification-message">
          {notification.message}
        </div>
      </div>
      
      <div className="notification-actions">
        {notification.action && (
          <button
            onClick={notification.action.handler}
            className="notification-action-button"
          >
            {notification.action.label}
          </button>
        )}
        
        {notification.dismissible && (
          <button
            onClick={() => onDismiss(notification.id)}
            className="notification-dismiss-button"
            aria-label="Dismiss"
          >
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default NotificationProvider;

