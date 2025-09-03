import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { AuthProvider, useAuth } from '@tta/shared-components';
import { store } from './store/store';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { CrisisSupport } from './components/safety/CrisisSupport';
import { AccessibilityProvider } from './components/accessibility/AccessibilityProvider';
import { TherapeuticThemeProvider } from './components/theme/TherapeuticThemeProvider';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Lazy load pages for better performance
const LoginPage = React.lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = React.lazy(() => import('./pages/auth/RegisterPage'));
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'));
const CharacterCreation = React.lazy(() => import('./pages/character/CharacterCreation'));
const CharacterManagement = React.lazy(() => import('./pages/character/CharacterManagement'));
const WorldExploration = React.lazy(() => import('./pages/world/WorldExploration'));
const TherapeuticChat = React.lazy(() => import('./pages/chat/TherapeuticChat'));
const ProgressTracking = React.lazy(() => import('./pages/progress/ProgressTracking'));
const Settings = React.lazy(() => import('./pages/settings/Settings'));
const Achievements = React.lazy(() => import('./pages/achievements/Achievements'));
const SafetyCenter = React.lazy(() => import('./pages/safety/SafetyCenter'));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Set up global error handling
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      // Log to monitoring service
    };

    const handleError = (event: ErrorEvent) => {
      console.error('Global error:', event.error);
      // Log to monitoring service
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <LoadingSpinner size="large" message="Initializing therapeutic environment..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <AnimatePresence mode="wait">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              !isAuthenticated ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Suspense fallback={<LoadingSpinner />}>
                    <LoginPage />
                  </Suspense>
                </motion.div>
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route
            path="/register"
            element={
              !isAuthenticated ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Suspense fallback={<LoadingSpinner />}>
                    <RegisterPage />
                  </Suspense>
                </motion.div>
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Navigate to="/dashboard" replace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <Dashboard />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/character/create"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <CharacterCreation />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/characters"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <CharacterManagement />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/worlds"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <WorldExploration />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:sessionId?"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <TherapeuticChat />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/progress"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <ProgressTracking />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/achievements"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <Achievements />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/safety"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <SafetyCenter />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <Settings />
                </Suspense>
              </ProtectedRoute>
            }
          />

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AnimatePresence>

      {/* Global Crisis Support Component */}
      <CrisisSupport />
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
            interfaceType="patient"
          >
            <AccessibilityProvider>
              <TherapeuticThemeProvider>
                <Router>
                  <AppContent />
                </Router>
              </TherapeuticThemeProvider>
            </AccessibilityProvider>
          </AuthProvider>
        </Provider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
