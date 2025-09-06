import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { CssBaseline, Box, Typography } from "@mui/material";
import {
  AuthProvider,
  useAuth,
  ErrorBoundary,
  LoadingSpinner,
  ProtectedRoute,
  HIPAAComplianceProvider,
  TherapeuticThemeProvider,
  AccessibilityProvider,
  CrisisSupportProvider,
} from "@tta/shared-components";
import "@tta/shared-components/styles/therapeutic-themes.css";

// Import layout component
import ClinicalLayout from "./components/layout/ClinicalLayout";

// Lazy load pages
const LoginPage = React.lazy(() => import("./pages/auth/LoginPage"));
const Dashboard = React.lazy(() => import("./pages/dashboard/Dashboard"));
// Placeholder components for pages not yet implemented
const PatientMonitoring = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Patient Monitoring</Typography>
        <Typography>
          Real-time patient monitoring interface - Coming Soon
        </Typography>
      </Box>
    ),
  }),
);
const Analytics = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Analytics & Reports</Typography>
        <Typography>Clinical analytics dashboard - Coming Soon</Typography>
      </Box>
    ),
  }),
);
const CrisisManagement = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Crisis Management</Typography>
        <Typography>Crisis intervention interface - Coming Soon</Typography>
      </Box>
    ),
  }),
);
const OutcomeMeasurement = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Outcome Measurements</Typography>
        <Typography>Clinical outcome tracking - Coming Soon</Typography>
      </Box>
    ),
  }),
);
const AuditLogs = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Audit Logs</Typography>
        <Typography>HIPAA compliance audit logs - Coming Soon</Typography>
      </Box>
    ),
  }),
);
const Reports = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Reports</Typography>
        <Typography>Clinical reporting interface - Coming Soon</Typography>
      </Box>
    ),
  }),
);
const Settings = React.lazy(() =>
  Promise.resolve({
    default: () => (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4">Settings</Typography>
        <Typography>Clinical dashboard settings - Coming Soon</Typography>
      </Box>
    ),
  }),
);

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
    mode: "light",
    primary: {
      main: "#1976d2", // Professional blue
      light: "#42a5f5",
      dark: "#1565c0",
    },
    secondary: {
      main: "#388e3c", // Medical green
      light: "#66bb6a",
      dark: "#2e7d32",
    },
    error: {
      main: "#d32f2f", // Critical alert red
      light: "#ef5350",
      dark: "#c62828",
    },
    warning: {
      main: "#f57c00", // Warning orange
      light: "#ff9800",
      dark: "#ef6c00",
    },
    info: {
      main: "#0288d1", // Information blue
      light: "#03a9f4",
      dark: "#0277bd",
    },
    success: {
      main: "#388e3c", // Success green
      light: "#4caf50",
      dark: "#2e7d32",
    },
    background: {
      default: "#fafafa",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 500,
      color: "#1565c0",
    },
    h2: {
      fontSize: "2rem",
      fontWeight: 500,
      color: "#1976d2",
    },
    h3: {
      fontSize: "1.75rem",
      fontWeight: 500,
      color: "#1976d2",
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.6,
    },
    body2: {
      fontSize: "0.875rem",
      lineHeight: 1.5,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: 6,
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: "none",
          "& .MuiDataGrid-cell": {
            borderBottom: "1px solid #e0e0e0",
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
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
        }}
      >
        <LoadingSpinner
          size="large"
          message="Initializing clinical dashboard..."
        />
      </Box>
    );
  }

  // Verify user has clinical access
  if (isAuthenticated && user && !["clinician", "admin"].includes(user.role)) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
        }}
      >
        <div>Access denied. Clinical credentials required.</div>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
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
                  <Route
                    path="/"
                    element={<Navigate to="/dashboard" replace />}
                  />
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
                  <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                  />
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
        <AuthProvider
          apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8080"}
          interfaceType="clinical"
        >
          <TherapeuticThemeProvider
            defaultTheme="clinical"
            persistPreferences={true}
          >
            <AccessibilityProvider
              enableAutoDetection={true}
              therapeuticMode={true}
            >
              <HIPAAComplianceProvider
                interfaceType="clinical"
                clinicalDataAccess={true}
                enableAuditLogging={true}
                sessionTimeoutMinutes={30}
              >
                <CrisisSupportProvider enableRealTimeMonitoring={true}>
                  <ThemeProvider theme={clinicalTheme}>
                    <CssBaseline />
                    <Router basename="/clinical">
                      <AppContent />
                    </Router>
                  </ThemeProvider>
                </CrisisSupportProvider>
              </HIPAAComplianceProvider>
            </AccessibilityProvider>
          </TherapeuticThemeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
