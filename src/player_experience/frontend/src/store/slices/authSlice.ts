// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Slices/Authslice]]
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';
import secureStorage, { sessionManager } from '../../utils/secureStorage';
import { getErrorMessage } from '../../utils/errorHandling';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}

// Initialize from secure storage
const getInitialState = (): AuthState => {
  const token = secureStorage.getToken();
  const session = sessionManager.getSession();

  return {
    user: session ? { id: session.userId, username: '', email: '' } : null,
    token: token,
    isAuthenticated: !!token && !!session,
    isLoading: false,
    error: null,
    sessionId: session?.sessionId || null,
  };
};

const initialState: AuthState = getInitialState();

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { username: string; password: string }) => {
    const response = await authAPI.login(credentials);
    // API returns access_token, but we store it as token
    const token = response.access_token || response.token;
    const expiresIn = response.expires_in || 3600; // Default 1 hour

    // Store token securely in memory
    secureStorage.setToken(token, expiresIn);

    // Store session data
    const user = response.user_info || response.user;
    const sessionId = response.session_id || `session_${Date.now()}`;

    sessionManager.setSession({
      sessionId,
      userId: user.user_id || user.id,
      lastActivity: Date.now(),
    });

    // Transform response to match expected format
    return {
      token: token,
      user: user,
      sessionId: sessionId,
    };
  }
);

export const logout = createAsyncThunk('auth/logout', async (_, { dispatch }) => {
  try {
    // Call the backend logout API to invalidate the session
    await authAPI.logout();
  } catch (error) {
    // Even if the API call fails, we should still clear storage
    console.warn('Logout API call failed, but clearing storage anyway:', error);
  }

  // Clear secure storage
  secureStorage.clearToken();
  sessionManager.clearSession();

  // Clear any remaining localStorage data (for migration purposes)
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('selectedCharacter');
  localStorage.removeItem('chatSession');
  localStorage.removeItem('playerProfile');
  localStorage.removeItem('userSettings');

  // Clear session storage
  sessionStorage.clear();

  return null;
});

export const verifyToken = createAsyncThunk('auth/verifyToken', async () => {
  const token = secureStorage.getToken();
  if (!token) throw new Error('No token found');

  const response = await authAPI.verifyToken(token);
  return response;
});

export const refreshToken = createAsyncThunk('auth/refreshToken', async () => {
  // Refresh token is handled via httpOnly cookie on the server
  // This action triggers the refresh endpoint
  const response = await authAPI.refreshToken();
  const token = response.access_token || response.token;
  const expiresIn = response.expires_in || 3600;

  // Store new token securely
  secureStorage.setToken(token, expiresIn);

  return {
    token: token,
    user: response.user_info || response.user,
  };
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    setAuthenticated: (state, action: PayloadAction<{ user: User; isAuthenticated: boolean }>) => {
      state.user = action.payload.user;
      state.isAuthenticated = action.payload.isAuthenticated;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.sessionId = action.payload.sessionId;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = getErrorMessage(action.error, 'Login');
      })
      .addCase(logout.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(logout.rejected, (state, action) => {
        // Even if logout fails, clear the authentication state
        state.user = null;
        state.token = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        state.isLoading = false;
        state.error = getErrorMessage(action.error, 'Logout') + ' (session cleared locally)';
      })
      .addCase(verifyToken.fulfilled, (state, action) => {
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(verifyToken.rejected, (state) => {
        state.user = null;
        state.token = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        secureStorage.clearToken();
      })
      .addCase(refreshToken.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(refreshToken.rejected, (state) => {
        state.isLoading = false;
        state.user = null;
        state.token = null;
        state.sessionId = null;
        state.isAuthenticated = false;
        secureStorage.clearToken();
        sessionManager.clearSession();
      });
  },
});

export const { clearError, setUser, setAuthenticated, setLoading } = authSlice.actions;
export default authSlice.reducer;
