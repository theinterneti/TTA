import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { authAPI } from "../../services/api";

interface User {
  user_id: string;
  username: string;
  email: string;
  role: string;
  permissions?: string[];
  mfa_verified?: boolean;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  tokenExpiresAt: number | null;
}

const JWT_STORAGE_KEY =
  process.env.REACT_APP_JWT_STORAGE_KEY || "tta_access_token";
const REFRESH_TOKEN_KEY =
  process.env.REACT_APP_REFRESH_TOKEN_KEY || "tta_refresh_token";

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem(JWT_STORAGE_KEY),
  refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
  isAuthenticated: !!localStorage.getItem(JWT_STORAGE_KEY),
  isLoading: false,
  error: null,
  tokenExpiresAt: null,
};

export const login = createAsyncThunk(
  "auth/login",
  async (
    credentials: { username: string; password: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.login(credentials);

      // Store tokens using the authAPI utility functions
      authAPI.storeTokens({
        access_token: (response as any).access_token,
        refresh_token: (response as any).refresh_token,
        expires_in: (response as any).expires_in,
        token_type: (response as any).token_type,
      });

      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || "Login failed");
    }
  }
);

export const register = createAsyncThunk(
  "auth/register",
  async (
    userData: {
      username: string;
      email: string;
      password: string;
      role?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.register(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || "Registration failed");
    }
  }
);

export const logout = createAsyncThunk(
  "auth/logout",
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      authAPI.clearTokens();
      return null;
    } catch (error: any) {
      // Even if logout fails on server, clear local tokens
      authAPI.clearTokens();
      return null;
    }
  }
);

export const verifyToken = createAsyncThunk(
  "auth/verifyToken",
  async (_, { rejectWithValue }) => {
    try {
      const token = authAPI.getAccessToken();
      if (!token) throw new Error("No token found");

      const response = await authAPI.verifyToken();
      return response;
    } catch (error: any) {
      authAPI.clearTokens();
      return rejectWithValue(error.message || "Token verification failed");
    }
  }
);

export const refreshToken = createAsyncThunk(
  "auth/refreshToken",
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) throw new Error("No refresh token found");

      const response = await authAPI.refreshToken(refreshToken);

      authAPI.storeTokens({
        access_token: (response as any).access_token,
        refresh_token: (response as any).refresh_token || refreshToken,
        expires_in: (response as any).expires_in,
        token_type: (response as any).token_type,
      });

      return response;
    } catch (error: any) {
      authAPI.clearTokens();
      return rejectWithValue(error.message || "Token refresh failed");
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    clearAuth: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.tokenExpiresAt = null;
      authAPI.clearTokens();
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
        const payload = action.payload as any;
        state.user = payload.user_info;
        state.accessToken = payload.access_token;
        state.refreshToken = payload.refresh_token;
        if (payload.expires_in) {
          state.tokenExpiresAt = Date.now() + payload.expires_in * 1000;
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = (action.payload as string) || "Login failed";
        state.isAuthenticated = false;
      })
      // Register cases
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = (action.payload as string) || "Registration failed";
      })
      // Logout cases
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.tokenExpiresAt = null;
      })
      // Token verification cases
      .addCase(verifyToken.fulfilled, (state, action) => {
        const payload = action.payload as any;
        state.user = payload.user_info || payload;
        state.isAuthenticated = true;
      })
      .addCase(verifyToken.rejected, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.tokenExpiresAt = null;
      })
      // Token refresh cases
      .addCase(refreshToken.fulfilled, (state, action) => {
        const payload = action.payload as any;
        state.accessToken = payload.access_token;
        if (payload.refresh_token) {
          state.refreshToken = payload.refresh_token;
        }
        if (payload.expires_in) {
          state.tokenExpiresAt = Date.now() + payload.expires_in * 1000;
        }
      })
      .addCase(refreshToken.rejected, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.tokenExpiresAt = null;
      });
  },
});

export const { clearError, setUser, clearAuth } = authSlice.actions;
export default authSlice.reducer;
