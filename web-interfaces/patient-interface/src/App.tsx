import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import {
  AuthProvider,
  useAuth,
  LoadingSpinner,
  ProtectedRoute,
  ErrorBoundary,
} from "@tta/shared-components";

// Lazy load pages for better performance
const LoginPage = React.lazy(() => import("./pages/auth/LoginPage"));
const Dashboard = React.lazy(() => import("./pages/dashboard/Dashboard"));
const OAuthCallback = React.lazy(() =>
  import("@tta/shared-components").then((module) => ({
    default: module.OAuthCallback,
  })),
);

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <LoadingSpinner
          size="large"
          message="Initializing therapeutic environment..."
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
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

        {/* OAuth Callback Route */}
        <Route
          path="/auth/callback/:provider"
          element={
            <Suspense fallback={<LoadingSpinner />}>
              <OAuthCallback />
            </Suspense>
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

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider
        apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
        interfaceType="patient"
      >
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
