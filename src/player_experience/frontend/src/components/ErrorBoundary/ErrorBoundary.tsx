/**
 * Error Boundary Component
 * 
 * Catches React component errors and displays user-friendly fallback UI
 * instead of crashing the entire application.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { serializeError, ErrorSeverity } from '../../utils/errorHandling';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    const serialized = serializeError(error, 'React Component Error');
    
    console.error('Error Boundary caught an error:', {
      error: serialized,
      componentStack: errorInfo.componentStack,
    });

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      const serialized = serializeError(this.state.error, 'Application Error');

      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <div style={styles.iconContainer}>
              <svg
                style={styles.icon}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            
            <h1 style={styles.title}>Something went wrong</h1>
            
            <p style={styles.message}>{serialized.userMessage}</p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={styles.details}>
                <summary style={styles.summary}>Technical Details (Development Only)</summary>
                <pre style={styles.pre}>
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
            
            <div style={styles.actions}>
              <button
                onClick={this.handleReset}
                style={styles.button}
              >
                Try Again
              </button>
              
              <button
                onClick={() => window.location.href = '/'}
                style={{ ...styles.button, ...styles.secondaryButton }}
              >
                Go to Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Inline styles for error boundary (to avoid dependency on external CSS)
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
    padding: '1rem',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    padding: '2rem',
    maxWidth: '32rem',
    width: '100%',
    textAlign: 'center',
  },
  iconContainer: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '1rem',
  },
  icon: {
    width: '4rem',
    height: '4rem',
    color: '#ef4444',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: '0.5rem',
  },
  message: {
    color: '#6b7280',
    marginBottom: '1.5rem',
    lineHeight: '1.5',
  },
  details: {
    textAlign: 'left',
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: '#f9fafb',
    borderRadius: '0.375rem',
    border: '1px solid #e5e7eb',
  },
  summary: {
    cursor: 'pointer',
    fontWeight: '500',
    color: '#374151',
    marginBottom: '0.5rem',
  },
  pre: {
    fontSize: '0.75rem',
    color: '#6b7280',
    overflow: 'auto',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  actions: {
    display: 'flex',
    gap: '0.75rem',
    justifyContent: 'center',
  },
  button: {
    padding: '0.5rem 1rem',
    borderRadius: '0.375rem',
    fontWeight: '500',
    cursor: 'pointer',
    border: 'none',
    backgroundColor: '#3b82f6',
    color: 'white',
    transition: 'background-color 0.2s',
  },
  secondaryButton: {
    backgroundColor: '#6b7280',
  },
};

export default ErrorBoundary;

