import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  Avatar,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  LocalHospital,
  Security,
} from '@mui/icons-material';
import { useAuth, LoadingSpinner, useHIPAACompliance } from '@tta/shared-components';

const LoginPage: React.FC = () => {
  const { login, isAuthenticated, isLoading } = useAuth();
  const { logUserAction } = useHIPAACompliance();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Log login attempt
      logUserAction('login_attempt', 'authentication', undefined, {
        username: formData.username,
        interface: 'clinical_dashboard',
      });

      await login(formData.username, formData.password);

      // Successful login will be handled by the auth provider
      logUserAction('login_success', 'authentication', undefined, {
        username: formData.username,
        interface: 'clinical_dashboard',
      });
    } catch (err: any) {
      console.error('Login error:', err);
      setError(
        err.message || 'Invalid credentials. Please check your username and password.'
      );

      // Log failed login attempt
      logUserAction('login_failure', 'authentication', undefined, {
        username: formData.username,
        interface: 'clinical_dashboard',
        error: err.message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

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

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        backgroundImage: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card
          elevation={8}
          sx={{
            borderRadius: 3,
            overflow: 'hidden',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          }}
        >
          <Box
            sx={{
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              p: 3,
              textAlign: 'center',
            }}
          >
            <Avatar
              sx={{
                bgcolor: 'primary.light',
                width: 64,
                height: 64,
                mx: 'auto',
                mb: 2,
              }}
            >
              <LocalHospital fontSize="large" />
            </Avatar>
            <Typography variant="h4" component="h1" gutterBottom>
              TTA Clinical Dashboard
            </Typography>
            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
              Healthcare Provider Portal
            </Typography>
          </Box>

          <CardContent sx={{ p: 4 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                mb: 3,
                p: 2,
                bgcolor: 'info.light',
                borderRadius: 1,
                color: 'info.contrastText',
              }}
            >
              <Security sx={{ mr: 1 }} />
              <Typography variant="body2">
                HIPAA-compliant secure authentication
              </Typography>
            </Box>

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                margin="normal"
                required
                autoComplete="username"
                autoFocus
                placeholder="Enter your clinical username"
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleInputChange}
                margin="normal"
                required
                autoComplete="current-password"
                placeholder="Enter your password"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleTogglePasswordVisibility}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isSubmitting || !formData.username || !formData.password}
                sx={{
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                }}
              >
                {isSubmitting ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LoadingSpinner size="small" />
                    Authenticating...
                  </Box>
                ) : (
                  'Sign In to Clinical Dashboard'
                )}
              </Button>
            </form>

            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Test Credentials: dr_smith / clinician123
              </Typography>
            </Box>

            <Box
              sx={{
                mt: 4,
                pt: 3,
                borderTop: 1,
                borderColor: 'divider',
                textAlign: 'center',
              }}
            >
              <Typography variant="caption" color="text.secondary">
                This system maintains HIPAA compliance and audit logging.
                <br />
                All access is monitored and recorded for security purposes.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default LoginPage;
