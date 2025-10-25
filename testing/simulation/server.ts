#!/usr/bin/env ts-node

/**
 * TTA Simulation Framework Production Server
 *
 * Provides HTTP API endpoints for running simulations, monitoring status,
 * and retrieving results in a production environment.
 */

import { createServer } from 'http';
import { URL } from 'url';
import { SimulationRunner, SIMULATION_CONFIGS } from './SimulationRunner';
import { SimulationConfig } from './core/SimulationEngine';

const PORT = process.env.PORT || 3002;
const HOST = process.env.HOST || '0.0.0.0';

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
}

class SimulationServer {
  private runner: SimulationRunner;
  private activeSimulations: Map<string, any> = new Map();

  constructor() {
    this.runner = new SimulationRunner();
  }

  private createResponse(success: boolean, data?: any, error?: string): ApiResponse {
    return {
      success,
      data: data || undefined,
      error: error || undefined,
      timestamp: Date.now()
    };
  }

  private async handleHealthCheck(): Promise<ApiResponse> {
    return this.createResponse(true, {
      status: 'healthy',
      version: '1.0.0',
      uptime: process.uptime(),
      activeSimulations: this.activeSimulations.size,
      environment: process.env.NODE_ENV || 'development'
    });
  }

  private async handleGetConfigurations(): Promise<ApiResponse> {
    const configs = Object.keys(SIMULATION_CONFIGS).map(key => ({
      name: key,
      description: this.getConfigDescription(key),
      estimatedDuration: this.getEstimatedDuration(key)
    }));

    return this.createResponse(true, { configurations: configs });
  }

  private getConfigDescription(configName: string): string {
    const descriptions: Record<string, string> = {
      'QUICK_TEST': 'Fast validation test (15 minutes) - ideal for CI/CD',
      'COMPREHENSIVE': 'Full platform validation (2 hours) - thorough testing',
      'PRODUCTION_VALIDATION': 'Pre-deployment validation (4 hours) - complete assessment'
    };
    return descriptions[configName] || 'Custom simulation configuration';
  }

  private getEstimatedDuration(configName: string): string {
    const durations: Record<string, string> = {
      'QUICK_TEST': '15 minutes',
      'COMPREHENSIVE': '2 hours',
      'PRODUCTION_VALIDATION': '4 hours'
    };
    return durations[configName] || 'Variable';
  }

  private async handleRunSimulation(configName: string): Promise<ApiResponse> {
    try {
      const simulationId = `sim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      if (!SIMULATION_CONFIGS[configName as keyof typeof SIMULATION_CONFIGS]) {
        return this.createResponse(false, null, `Unknown configuration: ${configName}`);
      }

      // Start simulation asynchronously
      const simulationPromise = this.runner.runWithConfig(SIMULATION_CONFIGS[configName as keyof typeof SIMULATION_CONFIGS]);
      this.activeSimulations.set(simulationId, {
        configName,
        startTime: Date.now(),
        status: 'running',
        promise: simulationPromise
      });

      // Handle completion
      simulationPromise.then((result: any) => {
        const simulation = this.activeSimulations.get(simulationId);
        if (simulation) {
          simulation.status = 'completed';
          simulation.result = result;
          simulation.endTime = Date.now();
        }
      }).catch((error: any) => {
        const simulation = this.activeSimulations.get(simulationId);
        if (simulation) {
          simulation.status = 'failed';
          simulation.error = error.message;
          simulation.endTime = Date.now();
        }
      });

      return this.createResponse(true, {
        simulationId,
        configName,
        status: 'started',
        message: 'Simulation started successfully'
      });

    } catch (error: any) {
      return this.createResponse(false, null, `Failed to start simulation: ${error.message || error}`);
    }
  }

  private async handleGetSimulationStatus(simulationId: string): Promise<ApiResponse> {
    const simulation = this.activeSimulations.get(simulationId);

    if (!simulation) {
      return this.createResponse(false, null, `Simulation not found: ${simulationId}`);
    }

    const response: any = {
      simulationId,
      configName: simulation.configName,
      status: simulation.status,
      startTime: simulation.startTime
    };

    if (simulation.endTime) {
      response.endTime = simulation.endTime;
      response.duration = simulation.endTime - simulation.startTime;
    }

    if (simulation.result) {
      response.result = simulation.result;
    }

    if (simulation.error) {
      response.error = simulation.error;
    }

    return this.createResponse(true, response);
  }

  private async handleGetActiveSimulations(): Promise<ApiResponse> {
    const simulations = Array.from(this.activeSimulations.entries()).map(([id, sim]) => ({
      simulationId: id,
      configName: sim.configName,
      status: sim.status,
      startTime: sim.startTime,
      duration: sim.endTime ? sim.endTime - sim.startTime : Date.now() - sim.startTime
    }));

    return this.createResponse(true, { simulations });
  }

  private async handleRequest(req: any, res: any): Promise<void> {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const method = req.method;
    const pathname = url.pathname;

    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    let response: ApiResponse;

    try {
      switch (pathname) {
        case '/health':
          response = await this.handleHealthCheck();
          break;

        case '/configurations':
          if (method === 'GET') {
            response = await this.handleGetConfigurations();
          } else {
            response = this.createResponse(false, null, 'Method not allowed');
          }
          break;

        case '/simulations':
          if (method === 'GET') {
            response = await this.handleGetActiveSimulations();
          } else if (method === 'POST') {
            const body = await this.getRequestBody(req);
            const { configName } = JSON.parse(body);
            response = await this.handleRunSimulation(configName);
          } else {
            response = this.createResponse(false, null, 'Method not allowed');
          }
          break;

        default:
          // Check if it's a simulation status request
          const simulationMatch = pathname.match(/^\/simulations\/(.+)$/);
          if (simulationMatch && method === 'GET') {
            response = await this.handleGetSimulationStatus(simulationMatch[1]);
          } else {
            response = this.createResponse(false, null, 'Not found');
          }
          break;
      }
    } catch (error: any) {
      response = this.createResponse(false, null, `Server error: ${error.message || error}`);
    }

    const statusCode = response.success ? 200 : (response.error?.includes('not found') ? 404 : 400);

    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(response, null, 2));
  }

  private getRequestBody(req: any): Promise<string> {
    return new Promise((resolve, reject) => {
      let body = '';
      req.on('data', (chunk: any) => {
        body += chunk.toString();
      });
      req.on('end', () => {
        resolve(body);
      });
      req.on('error', reject);
    });
  }

  public start(): void {
    const server = createServer((req, res) => {
      this.handleRequest(req, res).catch(error => {
        console.error('Request handling error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(this.createResponse(false, null, 'Internal server error')));
      });
    });

    server.listen(Number(PORT), HOST, () => {
      console.log(`🚀 TTA Simulation Framework Server running on http://${HOST}:${PORT}`);
      console.log(`📊 Health check: http://${HOST}:${PORT}/health`);
      console.log(`⚙️  Configurations: http://${HOST}:${PORT}/configurations`);
      console.log(`🎮 Simulations: http://${HOST}:${PORT}/simulations`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
      console.log('Received SIGTERM, shutting down gracefully...');
      server.close(() => {
        console.log('Server closed');
        process.exit(0);
      });
    });
  }
}

// Start server if called directly
if (require.main === module) {
  const server = new SimulationServer();
  server.start();
}

export default SimulationServer;
