/**
 * TTA Player Experience API Client
 *
 * Enhanced API client with JWT token management, automatic refresh,
 * and integration with the Nexus Codex backend.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";
const JWT_STORAGE_KEY =
  process.env.REACT_APP_JWT_STORAGE_KEY || "tta_access_token";
const REFRESH_TOKEN_KEY =
  process.env.REACT_APP_REFRESH_TOKEN_KEY || "tta_refresh_token";
const TOKEN_REFRESH_THRESHOLD = parseInt(
  process.env.REACT_APP_TOKEN_REFRESH_THRESHOLD || "300000"
); // 5 minutes

interface TokenData {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
}

class APIClient {
  private baseURL: string;
  private refreshPromise: Promise<void> | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * Get the current access token from storage
   */
  private getAccessToken(): string | null {
    return localStorage.getItem(JWT_STORAGE_KEY);
  }

  /**
   * Get the current refresh token from storage
   */
  private getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Store tokens securely
   */
  private storeTokens(tokenData: TokenData): void {
    localStorage.setItem(JWT_STORAGE_KEY, tokenData.access_token);
    if (tokenData.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refresh_token);
    }
  }

  /**
   * Clear all stored tokens
   */
  private clearTokens(): void {
    localStorage.removeItem(JWT_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Check if token needs refresh based on expiration
   */
  private shouldRefreshToken(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const expirationTime = payload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();

      return expirationTime - currentTime < TOKEN_REFRESH_THRESHOLD;
    } catch (error) {
      console.warn("Failed to parse token expiration:", error);
      return false;
    }
  }

  /**
   * Refresh the access token using the refresh token
   */
  private async refreshAccessToken(): Promise<void> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this._performTokenRefresh();

    try {
      await this.refreshPromise;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async _performTokenRefresh(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }

    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error("Token refresh failed");
      }

      const tokenData: TokenData = await response.json();
      this.storeTokens(tokenData);
    } catch (error) {
      console.error("Token refresh failed:", error);
      this.clearTokens();
      // Redirect to login or emit auth error event
      window.dispatchEvent(new CustomEvent("auth:token-expired"));
      throw error;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Check if token needs refresh before making the request
    if (this.shouldRefreshToken()) {
      try {
        await this.refreshAccessToken();
      } catch (error) {
        // Token refresh failed, proceed without token (will likely get 401)
        console.warn("Token refresh failed, proceeding with request");
      }
    }

    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAccessToken();

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      credentials: "include", // Include cookies for CORS
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized - token might be expired
      if (response.status === 401 && token) {
        try {
          await this.refreshAccessToken();
          // Retry the request with the new token
          const newToken = this.getAccessToken();
          const retryConfig = {
            ...config,
            headers: {
              ...config.headers,
              ...(newToken && { Authorization: `Bearer ${newToken}` }),
            },
          };

          const retryResponse = await fetch(url, retryConfig);
          if (!retryResponse.ok) {
            const errorData = await retryResponse.json().catch(() => ({}));
            throw new Error(
              errorData.detail ||
                errorData.message ||
                `HTTP error! status: ${retryResponse.status}`
            );
          }
          return await retryResponse.json();
        } catch (refreshError) {
          // Refresh failed, clear tokens and throw original error
          this.clearTokens();
          window.dispatchEvent(new CustomEvent("auth:token-expired"));
          throw new Error("Authentication failed");
        }
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            errorData.message ||
            `HTTP error! status: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

const apiClient = new APIClient(API_BASE_URL);

/**
 * Authentication API methods
 */
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    apiClient.post("/api/v1/auth/login", credentials),

  register: (userData: {
    username: string;
    email: string;
    password: string;
    role?: string;
  }) => apiClient.post("/api/v1/auth/register", userData),

  verifyToken: () => apiClient.get("/api/v1/auth/verify"),

  refreshToken: (refreshToken: string) =>
    apiClient.post("/api/v1/auth/refresh", { refresh_token: refreshToken }),

  logout: () => apiClient.post("/api/v1/auth/logout"),

  // Token management utilities
  storeTokens: (tokenData: TokenData) => {
    localStorage.setItem(JWT_STORAGE_KEY, tokenData.access_token);
    if (tokenData.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refresh_token);
    }
  },

  clearTokens: () => {
    localStorage.removeItem(JWT_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  getAccessToken: () => localStorage.getItem(JWT_STORAGE_KEY),

  isAuthenticated: () => !!localStorage.getItem(JWT_STORAGE_KEY),
};

// Player API
export const playerAPI = {
  getProfile: (playerId: string) => apiClient.get(`/players/${playerId}`),

  updateProfile: (playerId: string, updates: any) =>
    apiClient.put(`/players/${playerId}`, updates),

  getDashboard: (playerId: string) =>
    apiClient.get(`/players/${playerId}/dashboard`),
};

// Character API
export const characterAPI = {
  getCharacters: (playerId: string) =>
    apiClient.get(`/players/${playerId}/characters`),

  createCharacter: (playerId: string, characterData: any) =>
    apiClient.post(`/players/${playerId}/characters`, characterData),

  updateCharacter: (characterId: string, updates: any) =>
    apiClient.put(`/characters/${characterId}`, updates),

  deleteCharacter: (characterId: string) =>
    apiClient.delete(`/characters/${characterId}`),

  getCharacterProfile: (characterId: string) =>
    apiClient.get(`/characters/${characterId}/therapeutic-profile`),
};

// World API
export const worldAPI = {
  getAvailableWorlds: (playerId: string) =>
    apiClient.get(`/players/${playerId}/worlds`),

  getWorldDetails: (worldId: string) => apiClient.get(`/worlds/${worldId}`),

  checkCompatibility: (characterId: string, worldId: string) =>
    apiClient.get(`/characters/${characterId}/worlds/${worldId}/compatibility`),

  initializeCharacterInWorld: (
    characterId: string,
    worldId: string,
    parameters: any
  ) =>
    apiClient.post(
      `/characters/${characterId}/worlds/${worldId}/initialize`,
      parameters
    ),

  customizeWorldParameters: (worldId: string, parameters: any) =>
    apiClient.put(`/worlds/${worldId}/parameters`, parameters),
};

// Settings API
export const settingsAPI = {
  getSettings: (playerId: string) =>
    apiClient.get(`/players/${playerId}/settings`),

  updateTherapeuticSettings: (playerId: string, settings: any) =>
    apiClient.put(`/players/${playerId}/settings/therapeutic`, settings),

  updatePrivacySettings: (playerId: string, settings: any) =>
    apiClient.put(`/players/${playerId}/settings/privacy`, settings),

  exportPlayerData: (playerId: string) =>
    apiClient.get(`/players/${playerId}/data/export`),

  deletePlayerData: (playerId: string) =>
    apiClient.delete(`/players/${playerId}/data`),
};

// Chat API
export const chatAPI = {
  getSessions: (playerId: string) =>
    apiClient.get(`/players/${playerId}/sessions`),

  getSession: (sessionId: string) => apiClient.get(`/sessions/${sessionId}`),

  createSession: (characterId: string, worldId: string) =>
    apiClient.post("/sessions", {
      character_id: characterId,
      world_id: worldId,
    }),

  getSessionMessages: (sessionId: string) =>
    apiClient.get(`/sessions/${sessionId}/messages`),
};

/**
 * Nexus Codex API methods
 */
export const nexusAPI = {
  // Get central hub state
  getState: () => apiClient.get("/api/v1/nexus/state"),

  // Get story spheres for 3D visualization
  getSpheres: (filters?: { genre?: string; threat_level?: string }) => {
    const params = new URLSearchParams();
    if (filters?.genre) params.append("genre", filters.genre);
    if (filters?.threat_level)
      params.append("threat_level", filters.threat_level);
    const queryString = params.toString();
    return apiClient.get(
      `/api/v1/nexus/spheres${queryString ? `?${queryString}` : ""}`
    );
  },

  // World management
  getWorld: (worldId: string) =>
    apiClient.get(`/api/v1/nexus/worlds/${worldId}`),

  createWorld: (worldData: any) =>
    apiClient.post("/api/v1/nexus/worlds", worldData),

  searchWorlds: (filters: any) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => params.append(key, v));
        } else {
          params.append(key, value.toString());
        }
      }
    });
    return apiClient.get(`/api/v1/nexus/worlds/search?${params.toString()}`);
  },

  enterWorld: (worldId: string, entryData?: any) =>
    apiClient.post(`/api/v1/nexus/worlds/${worldId}/enter`, entryData || {}),

  // Story Weaver profiles
  getStoryWeavers: () => apiClient.get("/api/v1/nexus/story-weavers"),

  getStoryWeaver: (weaverId: string) =>
    apiClient.get(`/api/v1/nexus/story-weavers/${weaverId}`),

  // World templates
  getTemplates: () => apiClient.get("/api/v1/nexus/templates"),

  getTemplate: (templateId: string) =>
    apiClient.get(`/api/v1/nexus/templates/${templateId}`),
};

export default apiClient;
