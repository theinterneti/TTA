const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
    const token = localStorage.getItem('token');

    const config: RequestInit = {
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
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
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
    apiClient.post('/auth/login', credentials),
  
  verifyToken: (token: string) =>
    apiClient.get('/auth/verify'),
  
  logout: () =>
    apiClient.post('/auth/logout'),
};

// Player API
export const playerAPI = {
  getProfile: (playerId: string) =>
    apiClient.get(`/players/${playerId}`),
  
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
  
  getWorldDetails: (worldId: string) =>
    apiClient.get(`/worlds/${worldId}`),
  
  checkCompatibility: (characterId: string, worldId: string) =>
    apiClient.get(`/characters/${characterId}/worlds/${worldId}/compatibility`),
  
  initializeCharacterInWorld: (characterId: string, worldId: string, parameters: any) =>
    apiClient.post(`/characters/${characterId}/worlds/${worldId}/initialize`, parameters),
  
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
  
  getSession: (sessionId: string) =>
    apiClient.get(`/sessions/${sessionId}`),
  
  createSession: (characterId: string, worldId: string) =>
    apiClient.post('/sessions', { character_id: characterId, world_id: worldId }),
  
  getSessionMessages: (sessionId: string) =>
    apiClient.get(`/sessions/${sessionId}/messages`),
};

export default apiClient;