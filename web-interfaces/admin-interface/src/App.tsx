import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { ConfigProvider, theme, App as AntApp } from 'antd';
import { AuthProvider, useAuth } from '@tta/shared-components';
import { store } from './store/store';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AdminLayout } from './components/layout/AdminLayout';
import { SecurityProvider } from './components/security/SecurityProvider';

// Lazy load pages
const LoginPage = React.lazy(() => import('./pages/auth/LoginPage'));
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'));
const SystemMonitoring = React.lazy(() => import('./pages/monitoring/SystemMonitoring'));
const UserManagement = React.lazy(() => import('./pages/users/UserManagement'));
const RoleManagement = React.lazy(() => import('./pages/roles/RoleManagement'));
const SystemConfiguration = React.lazy(() => import('./pages/config/SystemConfiguration'));
const DatabaseAdmin = React.lazy(() => import('./pages/database/DatabaseAdmin'));
const LogViewer = React.lazy(() => import('./pages/logs/LogViewer'));
const PerformanceMetrics = React.lazy(() => import('./pages/performance/PerformanceMetrics'));
const SecurityAudit = React.lazy(() => import('./pages/security/SecurityAudit'));
const BackupRestore = React.lazy(() => import('./pages/backup/BackupRestore'));
const SystemHealth = React.lazy(() => import('./pages/health/SystemHealth'));
const Settings = React.lazy(() => import('./pages/settings/Settings'));

// Create React Query client with admin-specific settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 30 * 1000, // 30 seconds for admin data
      cacheTime: 2 * 60 * 1000, // 2 minutes
      refetchOnWindowFocus: true,
    },
  },
});

// Admin theme configuration
const adminTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    borderRadius: 6,
    wireframe: false,
  },
  components: {
    Layout: {
      siderBg: '#001529',
      triggerBg: '#002140',
    },
    Menu: {
      darkItemBg: '#001529',
      darkSubMenuItemBg: '#000c17',
      darkItemSelectedBg: '#1890ff',
    },
    Card: {
      borderRadiusLG: 8,
    },
    Table: {
      borderRadiusLG: 6,
    },
    Button: {
      borderRadiusLG: 6,
    },
  },
};

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f2f5',
        }}
      >
        <LoadingSpinner size="large" message="Initializing admin interface..." />
      </div>
    );
  }

  // Verify user has admin access
  if (isAuthenticated && user && user.role !== 'admin') {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f2f5',
        }}
      >
        <div>Access denied. Administrator credentials required.</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
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

        {/* Protected Routes with Admin Layout */}
        <Route
          path="/*"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminLayout>
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
                        <SystemMonitoring />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/users"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <UserManagement />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/roles"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <RoleManagement />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/config"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <SystemConfiguration />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/database"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <DatabaseAdmin />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/logs"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <LogViewer />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/performance"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <PerformanceMetrics />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/security"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <SecurityAudit />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/backup"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <BackupRestore />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/health"
                    element={
                      <Suspense fallback={<LoadingSpinner />}>
                        <SystemHealth />
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
              </AdminLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Provider store={store}>
          <AuthProvider
            apiBaseUrl={process.env.REACT_APP_API_URL || 'http://localhost:8080'}
            interfaceType="admin"
          >
            <ConfigProvider theme={adminTheme}>
              <AntApp>
                <SecurityProvider>
                  <Router basename="/admin">
                    <AppContent />
                  </Router>
                </SecurityProvider>
              </AntApp>
            </ConfigProvider>
          </AuthProvider>
        </Provider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
