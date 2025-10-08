import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { openRouterAuthAPI } from '../../services/api';

// Types for OpenRouter authentication
export interface OpenRouterAuthState {
  // Authentication status
  isAuthenticated: boolean;
  authMethod: 'none' | 'api_key' | 'oauth';

  // User info (from OAuth)
  user: {
    id?: string;
    email?: string;
    name?: string;
    credits?: number;
    usage?: {
      requests: number;
      tokens: number;
    };
  } | null;

  // API key validation
  apiKeyValid: boolean;
  apiKeyValidatedAt: string | null;

  // OAuth state
  oauthState: {
    isLoading: boolean;
    authUrl?: string;
    codeVerifier?: string;
    state?: string;
  };

  // UI state
  isLoading: boolean;
  error: string | null;
  showAuthModal: boolean;

  // Security
  sessionId: string | null;
  lastValidated: string | null;
}

export interface ApiKeyValidationRequest {
  apiKey: string;
  validateOnly?: boolean; // If true, don't store the key
}

export interface ApiKeyValidationResponse {
  valid: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
    credits: number;
    usage: {
      requests: number;
      tokens: number;
    };
  };
  error?: string;
}

export interface OAuthInitiateResponse {
  authUrl: string;
  codeVerifier: string;
  state: string;
}

export interface OAuthCallbackRequest {
  code: string;
  state: string;
  codeVerifier: string;
}

export interface OAuthCallbackResponse {
  success: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
    credits: number;
    usage: {
      requests: number;
      tokens: number;
    };
  };
  sessionId?: string;
  error?: string;
}

const initialState: OpenRouterAuthState = {
  isAuthenticated: false,
  authMethod: 'none',
  user: null,
  apiKeyValid: false,
  apiKeyValidatedAt: null,
  oauthState: {
    isLoading: false,
  },
  isLoading: false,
  error: null,
  showAuthModal: false,
  sessionId: null,
  lastValidated: null,
};

// Async thunks for API calls
export const validateApiKey = createAsyncThunk<
  ApiKeyValidationResponse,
  ApiKeyValidationRequest,
  { rejectValue: string }
>(
  'openRouterAuth/validateApiKey',
  async ({ apiKey, validateOnly = false }, { rejectWithValue }) => {
    try {
      return await openRouterAuthAPI.validateApiKey(apiKey, validateOnly);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Network error');
    }
  }
);

export const initiateOAuth = createAsyncThunk<
  OAuthInitiateResponse,
  void,
  { rejectValue: string }
>(
  'openRouterAuth/initiateOAuth',
  async (_, { rejectWithValue }) => {
    try {
      return await openRouterAuthAPI.initiateOAuth();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Network error');
    }
  }
);

export const handleOAuthCallback = createAsyncThunk<
  OAuthCallbackResponse,
  OAuthCallbackRequest,
  { rejectValue: string }
>(
  'openRouterAuth/handleOAuthCallback',
  async ({ code, state, codeVerifier }, { rejectWithValue }) => {
    try {
      return await openRouterAuthAPI.handleOAuthCallback(code, state, codeVerifier);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Network error');
    }
  }
);

export const refreshUserInfo = createAsyncThunk<
  { user: any },
  void,
  { rejectValue: string }
>(
  'openRouterAuth/refreshUserInfo',
  async (_, { rejectWithValue }) => {
    try {
      return await openRouterAuthAPI.getUserInfo();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Network error');
    }
  }
);

export const logout = createAsyncThunk<
  void,
  void,
  { rejectValue: string }
>(
  'openRouterAuth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await openRouterAuthAPI.logout();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Network error');
    }
  }
);

const openRouterAuthSlice = createSlice({
  name: 'openRouterAuth',
  initialState,
  reducers: {
    // UI actions
    showAuthModal: (state) => {
      state.showAuthModal = true;
    },
    hideAuthModal: (state) => {
      state.showAuthModal = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },

    // OAuth state management
    setOAuthState: (state, action: PayloadAction<{ codeVerifier: string; state: string }>) => {
      state.oauthState.codeVerifier = action.payload.codeVerifier;
      state.oauthState.state = action.payload.state;
    },
    clearOAuthState: (state) => {
      state.oauthState = { isLoading: false };
    },

    // Session management
    setSessionId: (state, action: PayloadAction<string>) => {
      state.sessionId = action.payload;
    },
    clearSession: (state) => {
      state.sessionId = null;
      state.isAuthenticated = false;
      state.authMethod = 'none';
      state.user = null;
      state.apiKeyValid = false;
      state.apiKeyValidatedAt = null;
      state.lastValidated = null;
    },
  },
  extraReducers: (builder) => {
    // API Key Validation
    builder
      .addCase(validateApiKey.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(validateApiKey.fulfilled, (state, action) => {
        state.isLoading = false;
        state.apiKeyValid = action.payload.valid;
        state.apiKeyValidatedAt = new Date().toISOString();

        if (action.payload.valid) {
          state.isAuthenticated = true;
          state.authMethod = 'api_key';
          state.user = action.payload.user || null;
          state.lastValidated = new Date().toISOString();
        }
      })
      .addCase(validateApiKey.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'API key validation failed';
        state.apiKeyValid = false;
        state.isAuthenticated = false;
        state.authMethod = 'none';
      });

    // OAuth Initiation
    builder
      .addCase(initiateOAuth.pending, (state) => {
        state.oauthState.isLoading = true;
        state.error = null;
      })
      .addCase(initiateOAuth.fulfilled, (state, action) => {
        state.oauthState.isLoading = false;
        state.oauthState.authUrl = action.payload.authUrl;
        state.oauthState.codeVerifier = action.payload.codeVerifier;
        state.oauthState.state = action.payload.state;
      })
      .addCase(initiateOAuth.rejected, (state, action) => {
        state.oauthState.isLoading = false;
        state.error = action.payload || 'OAuth initiation failed';
      });

    // OAuth Callback
    builder
      .addCase(handleOAuthCallback.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(handleOAuthCallback.fulfilled, (state, action) => {
        state.isLoading = false;

        if (action.payload.success) {
          state.isAuthenticated = true;
          state.authMethod = 'oauth';
          state.user = action.payload.user || null;
          state.sessionId = action.payload.sessionId || null;
          state.lastValidated = new Date().toISOString();
          state.showAuthModal = false;
        }
      })
      .addCase(handleOAuthCallback.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'OAuth callback failed';
      });

    // User Info Refresh
    builder
      .addCase(refreshUserInfo.fulfilled, (state, action) => {
        state.user = action.payload.user;
        state.lastValidated = new Date().toISOString();
      })
      .addCase(refreshUserInfo.rejected, (state, action) => {
        state.error = action.payload || 'Failed to refresh user info';
      });

    // Logout
    builder
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.authMethod = 'none';
        state.user = null;
        state.apiKeyValid = false;
        state.apiKeyValidatedAt = null;
        state.sessionId = null;
        state.lastValidated = null;
        state.showAuthModal = false;
        state.oauthState = { isLoading: false };
      })
      .addCase(logout.rejected, (state, action) => {
        state.error = action.payload || 'Logout failed';
      });
  },
});

export const {
  showAuthModal,
  hideAuthModal,
  clearError,
  setOAuthState,
  clearOAuthState,
  setSessionId,
  clearSession,
} = openRouterAuthSlice.actions;

export default openRouterAuthSlice.reducer;
