import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
}

export class ApiClient {
  private instance: AxiosInstance;

  constructor(config: ApiClientConfig) {
    this.instance = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 10000,
      withCredentials: config.withCredentials || true,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for adding auth token
    this.instance.interceptors.request.use(
      (config) => {
        // Get token from localStorage based on current interface
        const interfaceType = this.getInterfaceType();
        const token = localStorage.getItem(`tta_token_${interfaceType}`);

        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for handling token refresh
    this.instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshToken();
            return this.instance(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.handleAuthError();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private getInterfaceType(): string {
    // Determine interface type from current URL or environment
    const hostname = window.location.hostname;
    const port = window.location.port;

    const portMapping: { [key: string]: string } = {
      '3000': 'patient',
      '3001': 'clinical',
      '3002': 'admin',
      '3003': 'public',
      '3004': 'stakeholder',
      '3005': 'docs',
    };

    return portMapping[port] || 'patient';
  }

  private async refreshToken(): Promise<void> {
    const interfaceType = this.getInterfaceType();
    const token = localStorage.getItem(`tta_token_${interfaceType}`);

    if (!token) {
      throw new Error('No token available for refresh');
    }

    const response = await axios.post(
      '/auth/refresh',
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
        baseURL: this.instance.defaults.baseURL,
      }
    );

    const { access_token } = response.data;
    localStorage.setItem(`tta_token_${interfaceType}`, access_token);
  }

  private handleAuthError(): void {
    const interfaceType = this.getInterfaceType();
    localStorage.removeItem(`tta_token_${interfaceType}`);

    // Redirect to login page
    window.location.href = '/login';
  }

  // HTTP Methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.get<T>(url, config);
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.post<T>(url, data, config);
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.put<T>(url, data, config);
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.patch<T>(url, data, config);
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.delete<T>(url, config);
  }

  // Utility methods
  setBaseURL(baseURL: string): void {
    this.instance.defaults.baseURL = baseURL;
  }

  setAuthToken(token: string): void {
    this.instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  removeAuthToken(): void {
    delete this.instance.defaults.headers.common['Authorization'];
  }
}

// Default API client instance
export const apiClient = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080',
});

// Interface-specific API clients
export const createApiClient = (baseURL: string): ApiClient => {
  return new ApiClient({ baseURL });
};

// API client factory for different backends
export const apiClients = {
  playerExperience: new ApiClient({
    baseURL: process.env.REACT_APP_PLAYER_API_URL || 'http://localhost:8080',
  }),
  apiGateway: new ApiClient({
    baseURL: process.env.REACT_APP_GATEWAY_URL || 'http://localhost:8000',
  }),
  agentOrchestration: new ApiClient({
    baseURL: process.env.REACT_APP_AGENT_URL || 'http://localhost:8503',
  }),
};

export default apiClient;
