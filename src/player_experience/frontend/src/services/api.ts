// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Services/Api]]
import { displayError } from '../utils/errorHandling';
import secureStorage from '../utils/secureStorage';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = secureStorage.getToken();

    const config: RequestInit = {
      credentials: 'include', // Include cookies for httpOnly refresh token
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Create structured error object
        const error = {
          response: {
            status: response.status,
            statusText: response.statusText,
            data: errorData,
          },
          message: errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        };

        // Log error with proper serialization
        displayError(error, `API ${options.method || 'GET'} ${endpoint}`);

        throw error;
      }

      return await response.json();
    } catch (error) {
      // If it's not already our structured error, wrap it
      if (!error || !(error as any).response) {
        const wrappedError = {
          message: error instanceof Error ? error.message : 'Network request failed',
          originalError: error,
        };
        displayError(wrappedError, `API ${options.method || 'GET'} ${endpoint}`);
        throw wrappedError;
      }

      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

const apiClient = new APIClient(API_BASE_URL);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    apiClient.post('/api/v1/auth/login', credentials),

  verifyToken: (token: string) =>
    apiClient.get('/api/v1/auth/verify'),

  refreshToken: () =>
    apiClient.post('/api/v1/auth/refresh', {}),

  logout: () =>
    apiClient.post('/api/v1/auth/logout'),
};

// Player API
export const playerAPI = {
  getProfile: (playerId: string) =>
    apiClient.get(`/api/v1/players/${playerId}`),

  updateProfile: (playerId: string, updates: any) =>
    apiClient.put(`/api/v1/players/${playerId}`, updates),

  getDashboard: (playerId: string) =>
    apiClient.get(`/api/v1/players/${playerId}/dashboard`),
};

// Character API
export const characterAPI = {
  getCharacters: (playerId: string) =>
    apiClient.get(`/api/v1/characters/`),

  createCharacter: (playerId: string, characterData: any) =>
    apiClient.post(`/api/v1/characters/`, characterData),

  updateCharacter: (characterId: string, updates: any) =>
    apiClient.put(`/api/v1/characters/${characterId}`, updates),

  deleteCharacter: (characterId: string) =>
    apiClient.delete(`/api/v1/characters/${characterId}`),

  getCharacterProfile: (characterId: string) =>
    apiClient.get(`/api/v1/characters/${characterId}/therapeutic-profile`),
};

// World API
export const worldAPI = {
  getAvailableWorlds: (playerId: string) =>
    apiClient.get(`/api/v1/worlds/`),

  getWorldDetails: (worldId: string) =>
    apiClient.get(`/api/v1/worlds/${worldId}`),

  checkCompatibility: (characterId: string, worldId: string) =>
    apiClient.get(`/api/v1/characters/${characterId}/worlds/${worldId}/compatibility`),

  initializeCharacterInWorld: (characterId: string, worldId: string, parameters: any) =>
    apiClient.post(`/api/v1/characters/${characterId}/worlds/${worldId}/initialize`, parameters),

  customizeWorldParameters: (worldId: string, parameters: any) =>
    apiClient.put(`/api/v1/worlds/${worldId}/parameters`, parameters),
};

// Conversation API
export const conversationAPI = {
  getHistory: (sessionId: string, limit: number = 50) =>
    apiClient.get(`/api/v1/conversation/${sessionId}/history?limit=${limit}`),

  sendMessage: (sessionId: string, message: string, context: any = {}) =>
    apiClient.post('/api/v1/conversation/send', { session_id: sessionId, message, context }),

  clearConversation: (sessionId: string) =>
    apiClient.delete(`/api/v1/conversation/${sessionId}`),
};

// Settings API
export const settingsAPI = {
  getSettings: (playerId: string) =>
    apiClient.get(`/api/v1/players/${playerId}/settings`),

  updateTherapeuticSettings: (playerId: string, settings: any) =>
    apiClient.put(`/api/v1/players/${playerId}/settings/therapeutic`, settings),

  updatePrivacySettings: (playerId: string, settings: any) =>
    apiClient.put(`/api/v1/players/${playerId}/settings/privacy`, settings),

  updateNotificationSettings: (playerId: string, settings: any) =>
    apiClient.put(`/api/v1/players/${playerId}/settings/notifications`, settings),

  updateAccessibilitySettings: (playerId: string, settings: any) =>
    apiClient.put(`/api/v1/players/${playerId}/settings/accessibility`, settings),

  exportPlayerData: (playerId: string) =>
    apiClient.get(`/api/v1/players/${playerId}/data/export`),

  deletePlayerData: (playerId: string) =>
    apiClient.delete(`/api/v1/players/${playerId}/data`),
};

// Chat API
export const chatAPI = {
  getSessions: (playerId: string) =>
    apiClient.get(`/api/v1/sessions/`),

  getSession: (sessionId: string) =>
    apiClient.get(`/api/v1/sessions/${sessionId}`),

  createSession: (characterId: string, worldId: string) =>
    apiClient.post('/api/v1/sessions', { character_id: characterId, world_id: worldId }),

  getSessionMessages: (sessionId: string) =>
    apiClient.get(`/api/v1/sessions/${sessionId}/messages`),
};

// Model Management API
export const modelAPI = {
  // Get available models with optional filtering
  getAvailableModels: (provider?: string, freeOnly?: boolean) => {
    const params = new URLSearchParams();
    if (provider) params.append('provider', provider);
    if (freeOnly) params.append('free_only', 'true');
    const queryString = params.toString();
    return apiClient.get(`/api/v1/models/available${queryString ? `?${queryString}` : ''}`);
  },

  // Get only free models
  getFreeModels: (provider?: string) => {
    const params = new URLSearchParams();
    if (provider) params.append('provider', provider);
    const queryString = params.toString();
    return apiClient.get(`/api/v1/models/free${queryString ? `?${queryString}` : ''}`);
  },

  // Get affordable models within cost threshold
  getAffordableModels: (maxCostPerToken: number, provider?: string) => {
    const params = new URLSearchParams();
    params.append('max_cost_per_token', maxCostPerToken.toString());
    if (provider) params.append('provider', provider);
    return apiClient.get(`/api/v1/models/affordable?${params.toString()}`);
  },

  // Get OpenRouter-specific free models
  getOpenRouterFreeModels: () =>
    apiClient.get('/api/v1/models/openrouter/free'),

  // Set OpenRouter filter settings
  setOpenRouterFilter: (settings: {
    show_free_only?: boolean;
    prefer_free?: boolean;
    max_cost_per_token?: number;
  }) =>
    apiClient.post('/api/v1/models/openrouter/filter', settings),

  // Get current OpenRouter filter settings
  getOpenRouterFilter: () =>
    apiClient.get('/api/v1/models/openrouter/filter'),

  // Generate text using model management system
  generateText: (request: {
    prompt: string;
    task_type?: string;
    max_tokens?: number;
    temperature?: number;
    top_p?: number;
    stream?: boolean;
    max_latency_ms?: number;
    min_quality_score?: number;
  }) =>
    apiClient.post('/api/v1/models/generate', request),

  // Get model recommendations for task type
  getModelRecommendations: (taskType: string) =>
    apiClient.get(`/api/v1/models/recommendations?task_type=${taskType}`),

  // Test model connectivity
  testModel: (modelId: string, providerName: string) =>
    apiClient.post('/api/v1/models/test', { model_id: modelId, provider_name: providerName }),

  // Get system status
  getSystemStatus: () =>
    apiClient.get('/api/v1/models/status'),

  // Get model performance metrics
  getModelPerformance: (modelId: string, timeframeHours: number = 24) =>
    apiClient.get(`/api/v1/models/performance/${modelId}?timeframe_hours=${timeframeHours}`),

  // Get system performance metrics
  getSystemPerformance: () =>
    apiClient.get('/api/v1/models/performance'),
};

// Analytics API for tracking user behavior
export const analyticsAPI = {
  // Track model selection events
  trackModelSelection: (data: {
    model_id: string;
    provider: string;
    is_free: boolean;
    cost_per_token?: number;
    selection_reason?: string;
    user_id: string;
    session_id?: string;
  }) =>
    apiClient.post('/api/v1/analytics/model-selection', data),

  // Track filter usage
  trackFilterUsage: (data: {
    filter_type: 'free_only' | 'affordable' | 'all';
    max_cost_threshold?: number;
    user_id: string;
    models_shown: number;
    models_selected?: number;
  }) =>
    apiClient.post('/api/v1/analytics/filter-usage', data),

  // Track user preferences
  trackUserPreferences: (data: {
    user_id: string;
    preferences: {
      prefer_free_models: boolean;
      max_cost_tolerance: number;
      preferred_providers: string[];
      model_switching_frequency: 'low' | 'medium' | 'high';
    };
  }) =>
    apiClient.post('/api/v1/analytics/user-preferences', data),

  // Track model satisfaction
  trackModelSatisfaction: (data: {
    model_id: string;
    provider: string;
    user_id: string;
    session_id: string;
    satisfaction_score: number; // 1-10
    feedback?: string;
    performance_rating?: number;
    cost_satisfaction?: number;
  }) =>
    apiClient.post('/api/v1/analytics/model-satisfaction', data),
};

// OpenRouter Authentication API
export const openRouterAuthAPI = {
  validateApiKey: async (apiKey: string, validateOnly: boolean = false) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/validate-key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        api_key: apiKey,
        validate_only: validateOnly,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'API key validation failed');
    }

    return response.json();
  },

  initiateOAuth: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/oauth/initiate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'OAuth initiation failed');
    }

    return response.json();
  },

  handleOAuthCallback: async (code: string, state: string, codeVerifier: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/oauth/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        code,
        state,
        code_verifier: codeVerifier,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'OAuth callback failed');
    }

    return response.json();
  },

  getUserInfo: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/user-info`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get user info');
    }

    return response.json();
  },

  logout: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Logout failed');
    }

    return response.json();
  },

  getAuthStatus: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/openrouter/auth/status`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get auth status');
    }

    return response.json();
  },
};

// Player Preferences API
export const preferencesAPI = {
  getPreferences: (playerId: string) =>
    apiClient.get(`/api/preferences/${playerId}`),

  createPreferences: (preferences: any) =>
    apiClient.post('/api/preferences', preferences),

  updatePreferences: (playerId: string, preferences: any) =>
    apiClient.put(`/api/preferences/${playerId}`, preferences),

  deletePreferences: (playerId: string) =>
    apiClient.delete(`/api/preferences/${playerId}`),

  validatePreferences: (preferences: any) =>
    apiClient.post('/api/preferences/validate', preferences),

  generatePreview: (preferences: any, testMessage: string) =>
    apiClient.post('/api/preferences/preview', { preferences, test_message: testMessage }),

  exportPreferences: (playerId: string) =>
    apiClient.get(`/api/preferences/${playerId}/export`),

  importPreferences: (playerId: string, preferencesData: any) =>
    apiClient.post(`/api/preferences/${playerId}/import`, preferencesData),
};

export default apiClient;
