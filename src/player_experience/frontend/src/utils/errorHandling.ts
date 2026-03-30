// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Utils/Errorhandling]]
/**
 * Error Handling Utilities
 *
 * Provides comprehensive error serialization, formatting, and user-friendly
 * message generation to replace '[object Object]' displays.
 */

export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export interface SerializedError {
  message: string;
  severity: ErrorSeverity;
  code?: string;
  details?: string;
  timestamp: string;
  userMessage: string;
  technicalDetails?: any;
}

/**
 * Serialize any error object into a user-friendly format
 */
export function serializeError(error: any, context?: string): SerializedError {
  const timestamp = new Date().toISOString();

  // Handle null/undefined
  if (!error) {
    return {
      message: 'An unknown error occurred',
      severity: ErrorSeverity.ERROR,
      timestamp,
      userMessage: 'Something went wrong. Please try again.',
    };
  }

  // Handle Error objects
  if (error instanceof Error) {
    return {
      message: error.message,
      severity: ErrorSeverity.ERROR,
      timestamp,
      userMessage: formatUserMessage(error.message, context),
      technicalDetails: {
        name: error.name,
        stack: error.stack,
      },
    };
  }

  // Handle API error responses
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    return {
      message: data?.detail || data?.message || `HTTP ${status} error`,
      severity: getSeverityFromStatus(status),
      code: status.toString(),
      timestamp,
      userMessage: formatAPIErrorMessage(status, data, context),
      technicalDetails: data,
    };
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      message: error,
      severity: ErrorSeverity.ERROR,
      timestamp,
      userMessage: formatUserMessage(error, context),
    };
  }

  // Handle objects with message property
  if (error.message) {
    return {
      message: error.message,
      severity: error.severity || ErrorSeverity.ERROR,
      code: error.code,
      timestamp,
      userMessage: formatUserMessage(error.message, context),
      technicalDetails: error,
    };
  }

  // Handle generic objects
  try {
    const message = JSON.stringify(error);
    return {
      message,
      severity: ErrorSeverity.ERROR,
      timestamp,
      userMessage: 'An unexpected error occurred. Please try again.',
      technicalDetails: error,
    };
  } catch {
    return {
      message: 'Unserializable error object',
      severity: ErrorSeverity.ERROR,
      timestamp,
      userMessage: 'An unexpected error occurred. Please try again.',
    };
  }
}

/**
 * Get severity level from HTTP status code
 */
function getSeverityFromStatus(status: number): ErrorSeverity {
  if (status >= 500) return ErrorSeverity.CRITICAL;
  if (status >= 400) return ErrorSeverity.ERROR;
  if (status >= 300) return ErrorSeverity.WARNING;
  return ErrorSeverity.INFO;
}

/**
 * Format API error into user-friendly message
 */
function formatAPIErrorMessage(status: number, data: any, context?: string): string {
  const contextPrefix = context ? `${context}: ` : '';

  switch (status) {
    case 400:
      return `${contextPrefix}Invalid request. Please check your input and try again.`;
    case 401:
      return `${contextPrefix}You need to log in to continue.`;
    case 403:
      return `${contextPrefix}You don't have permission to perform this action.`;
    case 404:
      return `${contextPrefix}The requested resource was not found.`;
    case 422:
      if (data?.detail) {
        if (Array.isArray(data.detail)) {
          const errors = data.detail.map((err: any) =>
            `${err.loc?.join('.') || 'Field'}: ${err.msg}`
          ).join(', ');
          return `${contextPrefix}Validation error: ${errors}`;
        }
        return `${contextPrefix}Validation error: ${data.detail}`;
      }
      return `${contextPrefix}The data provided is invalid. Please check and try again.`;
    case 429:
      return `${contextPrefix}Too many requests. Please wait a moment and try again.`;
    case 500:
      return `${contextPrefix}Server error. Our team has been notified. Please try again later.`;
    case 503:
      return `${contextPrefix}Service temporarily unavailable. Please try again in a few moments.`;
    default:
      if (data?.detail) {
        return `${contextPrefix}${data.detail}`;
      }
      if (data?.message) {
        return `${contextPrefix}${data.message}`;
      }
      return `${contextPrefix}An error occurred. Please try again.`;
  }
}

/**
 * Format generic error message into user-friendly text
 */
function formatUserMessage(message: string, context?: string): string {
  const contextPrefix = context ? `${context}: ` : '';

  // Common error patterns
  if (message.toLowerCase().includes('network')) {
    return `${contextPrefix}Network error. Please check your connection and try again.`;
  }

  if (message.toLowerCase().includes('timeout')) {
    return `${contextPrefix}Request timed out. Please try again.`;
  }

  if (message.toLowerCase().includes('unauthorized') || message.toLowerCase().includes('authentication')) {
    return `${contextPrefix}Authentication failed. Please log in again.`;
  }

  if (message.toLowerCase().includes('forbidden') || message.toLowerCase().includes('permission')) {
    return `${contextPrefix}You don't have permission to perform this action.`;
  }

  // Return original message if it's already user-friendly (short and clear)
  if (message.length < 100 && !message.includes('Error:') && !message.includes('Exception')) {
    return `${contextPrefix}${message}`;
  }

  // Default fallback
  return `${contextPrefix}An error occurred. Please try again.`;
}

/**
 * Display error to user (console + optional UI notification)
 */
export function displayError(error: any, context?: string): SerializedError {
  const serialized = serializeError(error, context);

  // Log to console with appropriate level
  switch (serialized.severity) {
    case ErrorSeverity.CRITICAL:
      console.error('[CRITICAL]', serialized.message, serialized.technicalDetails);
      break;
    case ErrorSeverity.ERROR:
      console.error('[ERROR]', serialized.message, serialized.technicalDetails);
      break;
    case ErrorSeverity.WARNING:
      console.warn('[WARNING]', serialized.message, serialized.technicalDetails);
      break;
    case ErrorSeverity.INFO:
      console.info('[INFO]', serialized.message);
      break;
  }

  return serialized;
}

/**
 * Extract user-friendly message from any error
 */
export function getErrorMessage(error: any, context?: string): string {
  return serializeError(error, context).userMessage;
}

/**
 * Check if error is a specific type
 */
export function isNetworkError(error: any): boolean {
  const serialized = serializeError(error);
  return serialized.message.toLowerCase().includes('network') ||
         serialized.message.toLowerCase().includes('connection');
}

export function isAuthError(error: any): boolean {
  const serialized = serializeError(error);
  return serialized.code === '401' ||
         serialized.code === '403' ||
         serialized.message.toLowerCase().includes('unauthorized') ||
         serialized.message.toLowerCase().includes('authentication');
}

export function isValidationError(error: any): boolean {
  const serialized = serializeError(error);
  return serialized.code === '422' || serialized.code === '400';
}

/**
 * Create error notification object for UI display
 */
export interface ErrorNotification {
  id: string;
  message: string;
  severity: ErrorSeverity;
  dismissible: boolean;
  autoHideDuration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
}

export function createErrorNotification(
  error: any,
  context?: string,
  options?: {
    dismissible?: boolean;
    autoHideDuration?: number;
    action?: { label: string; handler: () => void };
  }
): ErrorNotification {
  const serialized = serializeError(error, context);

  return {
    id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    message: serialized.userMessage,
    severity: serialized.severity,
    dismissible: options?.dismissible ?? true,
    autoHideDuration: options?.autoHideDuration ?? (
      serialized.severity === ErrorSeverity.CRITICAL ? undefined : 5000
    ),
    action: options?.action,
  };
}
