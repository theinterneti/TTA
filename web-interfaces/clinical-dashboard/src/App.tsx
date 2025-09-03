import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { AuthProvider, useAuth } from '@tta/shared-components';
import { store } from './store/store';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { ClinicalLayout } from './components/layout/ClinicalLayout';
import { HIPAAComplianceProvider } from './components/compliance/HIPAAComplianceProvider';

// Lazy load pages
const LoginPage = React.lazy(() => import('./pages/auth/LoginPage'));
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'));
const PatientMonitoring = React.lazy(() => import('./pages/monitoring/PatientMonitoring'));
const Analytics = React.lazy(() => import('./pages/analytics/Analytics'));
const CrisisManagement = React.lazy(() => import('./pages/crisis/CrisisManagement'));
const OutcomeMeasurement = React.lazy(() => import('./pages/outcomes/OutcomeMeasurement'));
const AuditLogs = React.lazy(() => import('./pages/audit/AuditLogs'));
const Reports = React.lazy(() => import('./pages/reports/Reports'));
const Settings = React.lazy(() => import('./pages/settings/Settings'));

// Create React Query client with clinical-specific settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 2 * 60 * 1000, // 2 minutes for real-time clinical data
      cacheTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: true, // Important for clinical monitoring
    },
  },
});

// Clinical theme with professional healthcare colors
const clinicalTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Professional blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#388e3c', // Medical green
      light: '#66bb6a',
      dark: '#2e7d32',
    },
    error: {
      main: '#d32f2f', // Critical alert red
      light: '#ef5350',
      dark: '#c62828',
    },
    warning: {
      main: '#f57c00', // Warning orange
      light: '#ff9800',
      dark: '#ef6c00',
    },
    info: {
      main: '#0288d1', // Information blue
      light: '#03a9f4',
      dark: '#0277bd',
    },
    success: {
      main: '#388e3c', // Success green
      light: '#4caf50',
      dark: '#2e7d32',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      color: '#1565c0',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#1976d2',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      color: '#1976d2',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 6,
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: 'none',
          '& .MuiDataGrid-cell': {
            borderBottom: '1px solid #e0e0e0',
          },
        },
      },
    },
  },
});

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <LoadingSpinner size="large" message="Initializing clinical dashboard..." />
      </Box>
    );
  }

  // Verify user has clinical access
  if (isAuthenticated && user && !['clinician', 'admin'].includes(user.role)) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <div>Access denied. Clinical credentials required.</div>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            !isAuthenticated ? (
              <Suspense fallback={<LoadingSpinner />}>
                <LoginPage />
              </Suspense>
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Protected Routes with Clinical Layout */}
        <Route
          path="/*"
          element={
            <ProtectedRoute requiredRole="clinician">
              <ClinicalLayout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route
                    path="/dashboard"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <Dashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/monitoring"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <PatientMonitoring />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/analytics"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <Analytics />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/crisis"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <CrisisManagement />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/outcomes"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <OutcomeMeasurement />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/audit"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <AuditLogs />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/reports"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <Reports />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <Settings />
                      </Suspense>
                    }
                  />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </ClinicalLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Provider store={store}>
          <AuthProvider
            apiBaseUrl={process.env.REACT_APP_API_URL || 'http://localhost:8080'}
            interfaceType="clinical"
          >
            <ThemeProvider theme={clinicalTheme}>
              <CssBaseline />
              <HIPAAComplianceProvider>
                <Router basename="/clinical">
                  <AppContent />
                </Router>
              </HIPAAComplianceProvider>
            </ThemeProvider>
          </AuthProvider>
        </Provider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
