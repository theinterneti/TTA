/**
 * TTA Therapeutic Gaming Experience - Main Application Component
 *
 * Provides the main application structure with routing, authentication,
 * and therapeutic gaming interface.
 */

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress, Alert, Snackbar } from '@mui/material';
import { Provider } from 'react-redux';

// Import pages and components
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import CharacterStudio from './pages/CharacterStudio';
import WorldExplorer from './pages/WorldExplorer';
import TherapeuticSession from './pages/TherapeuticSession';
import ProfilePage from './pages/ProfilePage';

// Import services and store
import { store } from './store/store';
import ttaApi from './services/api';
import ttaWebSocket from './services/websocket';
import { UserAccount, ServiceHealth } from './types/therapeutic';

// Import components
import NavigationBar from './components/common/NavigationBar';
import CrisisSupport from './components/common/CrisisSupport';
import LoadingScreen from './components/common/LoadingScreen';

// Therapeutic Gaming Theme
const therapeuticTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4A90A4', // Calming teal
      light: '#7BB3C0',
      dark: '#2E5266',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#8FBC8F', // Soft sage green
      light: '#B4D4B4',
      dark: '#5F8A5F',
      contrastText: '#ffffff',
    },
    background: {
      default: '#F8FFFE', // Very light mint
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C3E50', // Soft dark blue-gray
      secondary: '#5D6D7E',
    },
    success: {
      main: '#27AE60', // Encouraging green
    },
    warning: {
      main: '#F39C12', // Gentle orange
    },
    error: {
      main: '#E74C3C', // Supportive red (not harsh)
    },
    info: {
      main: '#3498DB', // Calming blue
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#2C3E50',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#2C3E50',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: '#34495E',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
      color: '#2C3E50',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: '#5D6D7E',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '1rem',
          fontWeight: 500,
        },
        contained: {
          boxShadow: '0 2px 8px rgba(74, 144, 164, 0.2)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(74, 144, 164, 0.3)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
          borderRadius: 16,
          border: '1px solid rgba(74, 144, 164, 0.1)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
});

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = ttaApi.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Main App Component
const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserAccount | null>(null);
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  // Initialize application
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setIsLoading(true);

      // Check service health
      const health = await ttaApi.getServiceHealth();
      setServiceHealth(health);

      // If user is authenticated, load user data
      if (ttaApi.isAuthenticated()) {
        try {
          // In a real app, we'd have a "get current user" endpoint
          // For now, we'll just verify the token is valid
          await ttaApi.getServiceHealth(); // This will fail if token is invalid

          // Initialize WebSocket connection
          await ttaWebSocket.connect();

          // Set up WebSocket event listeners
          setupWebSocketListeners();

        } catch (error) {
          console.error('Failed to load user data:', error);
          ttaApi.clearAuthToken();
        }
      }

    } catch (error) {
      console.error('Failed to initialize app:', error);
      setError('Failed to connect to TTA services. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const setupWebSocketListeners = () => {
    // System notifications
    ttaWebSocket.on('system:notification', (data) => {
      setNotification(data.message);
    });

    // System errors
    ttaWebSocket.on('system:error', (data) => {
      setError(data.error);
    });

    // Crisis detection
    ttaWebSocket.on('therapeutic:crisis_detected', (data) => {
      setError(`Crisis detected (${data.level} level): ${data.context}`);
      // In a real app, this would trigger crisis support protocols
    });

    // Milestone achievements
    ttaWebSocket.on('therapeutic:milestone_achieved', (data) => {
      setNotification(`🎉 Milestone achieved: ${data.description}`);
    });
  };

  const handleLogin = (userData: UserAccount) => {
    setUser(userData);
    initializeApp(); // Reinitialize with authenticated user
  };

  const handleLogout = async () => {
    try {
      await ttaApi.logout();
      ttaWebSocket.disconnect();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  const handleCloseNotification = () => {
    setNotification(null);
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={therapeuticTheme}>
        <CssBaseline />
        <LoadingScreen message="Initializing TTA Therapeutic Gaming Experience..." />
      </ThemeProvider>
    );
  }

  return (
    <Provider store={store}>
      <ThemeProvider theme={therapeuticTheme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            {/* Navigation Bar (only show when authenticated) */}
            {ttaApi.isAuthenticated() && (
              <NavigationBar
                user={user}
                onLogout={handleLogout}
                serviceHealth={serviceHealth}
              />
            )}

            {/* Main Content */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <Routes>
                {/* Public Routes */}
                <Route
                  path="/login"
                  element={<LoginPage onLogin={handleLogin} />}
                />
                <Route
                  path="/register"
                  element={<RegisterPage onRegister={handleLogin} />}
                />

                {/* Protected Routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Dashboard user={user} />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/characters"
                  element={
                    <ProtectedRoute>
                      <CharacterStudio />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/worlds"
                  element={
                    <ProtectedRoute>
                      <WorldExplorer />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/session/:sessionId"
                  element={
                    <ProtectedRoute>
                      <TherapeuticSession />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage user={user} />
                    </ProtectedRoute>
                  }
                />

                {/* Default redirect */}
                <Route
                  path="*"
                  element={<Navigate to="/" replace />}
                />
              </Routes>
            </Box>

            {/* Crisis Support (always available) */}
            <CrisisSupport />

            {/* Error Snackbar */}
            <Snackbar
              open={!!error}
              autoHideDuration={6000}
              onClose={handleCloseError}
              anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
              <Alert
                onClose={handleCloseError}
                severity="error"
                sx={{ width: '100%' }}
              >
                {error}
              </Alert>
            </Snackbar>

            {/* Notification Snackbar */}
            <Snackbar
              open={!!notification}
              autoHideDuration={4000}
              onClose={handleCloseNotification}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
              <Alert
                onClose={handleCloseNotification}
                severity="success"
                sx={{ width: '100%' }}
              >
                {notification}
              </Alert>
            </Snackbar>
          </Box>
        </Router>
      </ThemeProvider>
    </Provider>
  );
};

export default App;
