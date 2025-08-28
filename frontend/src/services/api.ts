/**
 * TTA API Client Service
 * 
 * Provides a comprehensive client for all 46 TTA API endpoints
 * with proper TypeScript typing and error handling.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  UserAccount,
  Character,
  WorldSummary,
  WorldDetails,
  TherapeuticSession,
  LoginResponse,
  ApiResponse,
  ServiceHealth,
  WorldCustomization,
  SessionSettings,
  CharacterExport,
  WorldExport,
  SessionExport,
  CompatibilityAnalysis
} from '../types/therapeutic';

class TTAApiClient {
  private api: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8080') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('tta_access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('tta_access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication Endpoints
  async register(userData: {
    username: string;
    email: string;
    password: string;
    therapeuticPreferences?: any;
    privacySettings?: any;
  }): Promise<ApiResponse<UserAccount>> {
    const response = await this.api.post('/api/v1/auth/register', userData);
    return response.data;
  }

  async login(credentials: {
    username: string;
    password: string;
  }): Promise<LoginResponse> {
    const response = await this.api.post('/api/v1/auth/login', credentials);
    if (response.data.accessToken) {
      localStorage.setItem('tta_access_token', response.data.accessToken);
    }
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout');
    } finally {
      localStorage.removeItem('tta_access_token');
    }
  }

  async refreshToken(): Promise<LoginResponse> {
    const response = await this.api.post('/api/v1/auth/refresh');
    if (response.data.accessToken) {
      localStorage.setItem('tta_access_token', response.data.accessToken);
    }
    return response.data;
  }

  // Player Management Endpoints
  async createPlayer(playerData: {
    username: string;
    email: string;
    therapeuticPreferences: any;
    privacySettings: any;
  }): Promise<ApiResponse<UserAccount>> {
    const response = await this.api.post('/api/v1/players/', playerData);
    return response.data;
  }

  async getPlayer(playerId: string): Promise<ApiResponse<UserAccount>> {
    const response = await this.api.get(`/api/v1/players/${playerId}`);
    return response.data;
  }

  async updatePlayer(playerId: string, updates: Partial<UserAccount>): Promise<ApiResponse<UserAccount>> {
    const response = await this.api.put(`/api/v1/players/${playerId}`, updates);
    return response.data;
  }

  async deletePlayer(playerId: string): Promise<ApiResponse<void>> {
    const response = await this.api.delete(`/api/v1/players/${playerId}`);
    return response.data;
  }

  async getPlayerProgress(playerId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/api/v1/players/${playerId}/progress`);
    return response.data;
  }

  // Character Management Endpoints
  async createCharacter(characterData: Omit<Character, 'characterId' | 'createdAt' | 'lastActive'>): Promise<ApiResponse<Character>> {
    const response = await this.api.post('/api/v1/characters/', characterData);
    return response.data;
  }

  async getCharacter(characterId: string): Promise<ApiResponse<Character>> {
    const response = await this.api.get(`/api/v1/characters/${characterId}`);
    return response.data;
  }

  async updateCharacter(characterId: string, updates: Partial<Character>): Promise<ApiResponse<Character>> {
    const response = await this.api.put(`/api/v1/characters/${characterId}`, updates);
    return response.data;
  }

  async deleteCharacter(characterId: string): Promise<ApiResponse<void>> {
    const response = await this.api.delete(`/api/v1/characters/${characterId}`);
    return response.data;
  }

  async getPlayerCharacters(playerId: string): Promise<ApiResponse<Character[]>> {
    const response = await this.api.get(`/api/v1/players/${playerId}/characters`);
    return response.data;
  }

  async getCharacterProgress(characterId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/api/v1/characters/${characterId}/progress`);
    return response.data;
  }

  // World Management Endpoints
  async getWorlds(): Promise<ApiResponse<WorldSummary[]>> {
    const response = await this.api.get('/api/v1/worlds/');
    return response.data;
  }

  async getWorld(worldId: string): Promise<ApiResponse<WorldDetails>> {
    const response = await this.api.get(`/api/v1/worlds/${worldId}`);
    return response.data;
  }

  async getWorldCompatibility(worldId: string, characterId: string): Promise<ApiResponse<CompatibilityAnalysis>> {
    const response = await this.api.get(`/api/v1/worlds/${worldId}/compatibility/${characterId}`);
    return response.data;
  }

  async customizeWorld(worldId: string, customization: WorldCustomization): Promise<ApiResponse<WorldDetails>> {
    const response = await this.api.post(`/api/v1/worlds/${worldId}/customize`, customization);
    return response.data;
  }

  async getFeaturedWorlds(): Promise<ApiResponse<WorldSummary[]>> {
    const response = await this.api.get('/api/v1/worlds/featured');
    return response.data;
  }

  async searchWorlds(query: string, filters?: any): Promise<ApiResponse<WorldSummary[]>> {
    const response = await this.api.get('/api/v1/worlds/search', {
      params: { q: query, ...filters }
    });
    return response.data;
  }

  // Session Management Endpoints
  async createSession(sessionData: {
    characterId: string;
    worldId: string;
    therapeuticSettings: SessionSettings;
  }): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.post('/api/v1/sessions/', sessionData);
    return response.data;
  }

  async getSession(sessionId: string): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.get(`/api/v1/sessions/${sessionId}`);
    return response.data;
  }

  async updateSession(sessionId: string, updates: Partial<TherapeuticSession>): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.put(`/api/v1/sessions/${sessionId}`, updates);
    return response.data;
  }

  async pauseSession(sessionId: string): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.post(`/api/v1/sessions/${sessionId}/pause`);
    return response.data;
  }

  async resumeSession(sessionId: string): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.post(`/api/v1/sessions/${sessionId}/resume`);
    return response.data;
  }

  async endSession(sessionId: string): Promise<ApiResponse<TherapeuticSession>> {
    const response = await this.api.post(`/api/v1/sessions/${sessionId}/end`);
    return response.data;
  }

  async getPlayerSessions(playerId: string): Promise<ApiResponse<TherapeuticSession[]>> {
    const response = await this.api.get(`/api/v1/players/${playerId}/sessions`);
    return response.data;
  }

  async getCharacterSessions(characterId: string): Promise<ApiResponse<TherapeuticSession[]>> {
    const response = await this.api.get(`/api/v1/characters/${characterId}/sessions`);
    return response.data;
  }

  // Progress Tracking Endpoints
  async getSessionProgress(sessionId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/api/v1/sessions/${sessionId}/progress`);
    return response.data;
  }

  async updateSessionProgress(sessionId: string, progress: any): Promise<ApiResponse<any>> {
    const response = await this.api.put(`/api/v1/sessions/${sessionId}/progress`, progress);
    return response.data;
  }

  // Export Endpoints
  async exportCharacter(characterId: string, format: 'json' | 'pdf' | 'csv' = 'json'): Promise<CharacterExport> {
    const response = await this.api.get(`/api/v1/characters/${characterId}/export`, {
      params: { format }
    });
    return response.data;
  }

  async exportWorld(worldId: string, format: 'json' | 'pdf' | 'csv' = 'json'): Promise<WorldExport> {
    const response = await this.api.get(`/api/v1/worlds/${worldId}/export`, {
      params: { format }
    });
    return response.data;
  }

  async exportSession(sessionId: string, format: 'json' | 'pdf' | 'csv' = 'json'): Promise<SessionExport> {
    const response = await this.api.get(`/api/v1/sessions/${sessionId}/export`, {
      params: { format }
    });
    return response.data;
  }

  // Service Health Endpoints
  async getServiceHealth(): Promise<ServiceHealth> {
    const response = await this.api.get('/api/v1/services/health');
    return response.data;
  }

  async getServiceConfig(): Promise<ApiResponse<any>> {
    const response = await this.api.get('/api/v1/services/config');
    return response.data;
  }

  async reconnectServices(): Promise<ApiResponse<any>> {
    const response = await this.api.post('/api/v1/services/reconnect');
    return response.data;
  }

  // Health Check Endpoints
  async getHealthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return !!localStorage.getItem('tta_access_token');
  }

  getAuthToken(): string | null {
    return localStorage.getItem('tta_access_token');
  }

  setAuthToken(token: string): void {
    localStorage.setItem('tta_access_token', token);
  }

  clearAuthToken(): void {
    localStorage.removeItem('tta_access_token');
  }
}

// Create and export a singleton instance
export const ttaApi = new TTAApiClient();
export default ttaApi;
