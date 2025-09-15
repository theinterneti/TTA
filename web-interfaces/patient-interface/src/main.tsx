import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Enhanced error boundary for therapeutic applications
class TherapeuticErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('TTA Patient Interface Error:', error, errorInfo)

    // In production, this would send error reports to monitoring service
    if (process.env.NODE_ENV === 'production') {
      // Send error to monitoring service
      console.log('Error would be reported to monitoring service')
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          padding: '20px',
          textAlign: 'center',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }}>
          <h1 style={{ color: '#dc2626', marginBottom: '20px' }}>
            Therapeutic Interface Temporarily Unavailable
          </h1>
          <p style={{ color: '#6b7280', marginBottom: '30px', maxWidth: '500px' }}>
            We're experiencing a technical issue with the therapeutic interface.
            Your safety and progress are our priority. Please try refreshing the page
            or contact your healthcare provider if the issue persists.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500'
            }}
          >
            Refresh Interface
          </button>
          <p style={{
            color: '#9ca3af',
            fontSize: '14px',
            marginTop: '20px',
            maxWidth: '400px'
          }}>
            If you're experiencing a crisis, please contact emergency services
            or your healthcare provider immediately.
          </p>
        </div>
      )
    }

    return this.props.children
  }
}

// Initialize React app with therapeutic error handling
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TherapeuticErrorBoundary>
      <App />
    </TherapeuticErrorBoundary>
  </React.StrictMode>,
)
