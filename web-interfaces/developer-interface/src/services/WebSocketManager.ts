import ReconnectingWebSocket from 'reconnecting-websocket';
import { EventEmitter } from 'events';

export interface DevMonitoringEvent {
  type: 'interface_health' | 'build_status' | 'live_reload' | 'error_report' | 'performance_metric';
  timestamp: string;
  interfaceId: string;
  data: any;
}

export interface InterfaceHealthData {
  id: string;
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime: number;
  lastCheck: string;
  error?: string;
  buildTime?: number;
  errorCount: number;
}

export interface BuildStatusData {
  interfaceId: string;
  status: 'building' | 'success' | 'error' | 'idle';
  buildTime: number;
  errors: string[];
  warnings: string[];
  timestamp: string;
}

export interface LiveReloadData {
  interfaceId: string;
  status: 'reloading' | 'completed' | 'failed';
  timestamp: string;
  buildTime?: number;
  changes?: string[];
}

export interface PerformanceMetricData {
  interfaceId: string;
  metrics: {
    loadTime: number;
    renderTime: number;
    memoryUsage: number;
    networkRequests: number;
  };
  timestamp: string;
}

export class WebSocketManager extends EventEmitter {
  private connections: Map<string, ReconnectingWebSocket> = new Map();
  private isEnabled: boolean = false;
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts: number = 10;
  private baseUrls: { [key: string]: string } = {
    player: 'ws://localhost:8080',
    gateway: 'ws://localhost:8000',
    agent: 'ws://localhost:8503',
  };

  constructor() {
    super();
    this.isEnabled = process.env.NODE_ENV === 'development';

    if (this.isEnabled) {
      this.initializeConnections();
    }
  }

  private initializeConnections(): void {
    // Connect to monitoring endpoints on each backend service
    this.connectToService('player', '/ws/monitoring');
    this.connectToService('gateway', '/ws/monitoring');
    this.connectToService('agent', '/ws/monitoring');
  }

  private connectToService(serviceId: string, endpoint: string): void {
    if (!this.isEnabled) return;

    const url = `${this.baseUrls[serviceId]}${endpoint}`;
    const token = this.getAuthToken();

    const wsUrl = token ? `${url}?token=${token}` : url;

    const ws = new ReconnectingWebSocket(wsUrl, [], {
      maxReconnectionDelay: 10000,
      minReconnectionDelay: 1000,
      reconnectionDelayGrowFactor: 1.3,
      connectionTimeout: 4000,
      maxRetries: this.maxReconnectAttempts,
      debug: process.env.NODE_ENV === 'development',
    });

    ws.addEventListener('open', () => {
      console.log(`✅ Connected to ${serviceId} monitoring WebSocket`);
      this.reconnectAttempts.set(serviceId, 0);
      this.emit('connection_status', { serviceId, status: 'connected' });

      // Request initial status
      this.sendMessage(serviceId, {
        type: 'request_status',
        timestamp: new Date().toISOString(),
      });
    });

    ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(serviceId, data);
      } catch (error) {
        console.error(`Failed to parse WebSocket message from ${serviceId}:`, error);
      }
    });

    ws.addEventListener('close', (event) => {
      console.log(`🔌 Disconnected from ${serviceId} monitoring WebSocket:`, event.code, event.reason);
      this.emit('connection_status', { serviceId, status: 'disconnected', code: event.code, reason: event.reason });
    });

    ws.addEventListener('error', (event) => {
      console.error(`❌ WebSocket error for ${serviceId}:`, event);
      const attempts = this.reconnectAttempts.get(serviceId) || 0;
      this.reconnectAttempts.set(serviceId, attempts + 1);
      this.emit('connection_error', { serviceId, error: event, attempts });
    });

    this.connections.set(serviceId, ws);
  }

  private handleMessage(serviceId: string, data: any): void {
    const event: DevMonitoringEvent = {
      type: data.type || 'unknown',
      timestamp: data.timestamp || new Date().toISOString(),
      interfaceId: data.interfaceId || serviceId,
      data: data.data || data,
    };

    // Emit specific event types
    switch (event.type) {
      case 'interface_health':
        this.emit('health_update', event.data as InterfaceHealthData);
        break;
      case 'build_status':
        this.emit('build_status', event.data as BuildStatusData);
        break;
      case 'live_reload':
        this.emit('live_reload', event.data as LiveReloadData);
        break;
      case 'error_report':
        this.emit('error_report', event.data);
        break;
      case 'performance_metric':
        this.emit('performance_metric', event.data as PerformanceMetricData);
        break;
      default:
        this.emit('message', event);
    }

    // Emit general event
    this.emit('dev_event', event);
  }

  private sendMessage(serviceId: string, message: any): void {
    const ws = this.connections.get(serviceId);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  private getAuthToken(): string | null {
    // Try to get developer token from localStorage
    return localStorage.getItem('tta_token_developer') ||
           localStorage.getItem('tta_token_admin') ||
           null;
  }

  public requestHealthCheck(): void {
    this.connections.forEach((ws, serviceId) => {
      this.sendMessage(serviceId, {
        type: 'health_check_request',
        timestamp: new Date().toISOString(),
      });
    });
  }

  public requestBuildStatus(): void {
    this.connections.forEach((ws, serviceId) => {
      this.sendMessage(serviceId, {
        type: 'build_status_request',
        timestamp: new Date().toISOString(),
      });
    });
  }

  public getConnectionStatus(): { [serviceId: string]: string } {
    const status: { [serviceId: string]: string } = {};
    this.connections.forEach((ws, serviceId) => {
      switch (ws.readyState) {
        case WebSocket.CONNECTING:
          status[serviceId] = 'connecting';
          break;
        case WebSocket.OPEN:
          status[serviceId] = 'connected';
          break;
        case WebSocket.CLOSING:
          status[serviceId] = 'closing';
          break;
        case WebSocket.CLOSED:
          status[serviceId] = 'disconnected';
          break;
        default:
          status[serviceId] = 'unknown';
      }
    });
    return status;
  }

  public disconnect(): void {
    this.connections.forEach((ws, serviceId) => {
      console.log(`Disconnecting from ${serviceId} WebSocket`);
      ws.close();
    });
    this.connections.clear();
    this.removeAllListeners();
  }

  public reconnect(): void {
    this.disconnect();
    if (this.isEnabled) {
      setTimeout(() => {
        this.initializeConnections();
      }, 1000);
    }
  }

  public isConnected(): boolean {
    return Array.from(this.connections.values()).some(ws => ws.readyState === WebSocket.OPEN);
  }

  public getConnectedServices(): string[] {
    const connected: string[] = [];
    this.connections.forEach((ws, serviceId) => {
      if (ws.readyState === WebSocket.OPEN) {
        connected.push(serviceId);
      }
    });
    return connected;
  }
}

// Singleton instance
export const webSocketManager = new WebSocketManager();
