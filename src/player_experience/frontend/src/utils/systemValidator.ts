import { nexusAPI } from '../services/api';

export interface ValidationResult {
  endpoint: string;
  status: 'success' | 'error' | 'warning';
  responseTime: number;
  message: string;
  data?: any;
  error?: string;
}

export interface SystemValidationReport {
  overall_status: 'healthy' | 'degraded' | 'critical';
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  warning_tests: number;
  average_response_time: number;
  results: ValidationResult[];
  timestamp: string;
  recommendations: string[];
}

/**
 * Comprehensive system validator for end-to-end functionality testing
 */
export class SystemValidator {
  private results: ValidationResult[] = [];
  private startTime: number = 0;

  /**
   * Run complete system validation
   */
  async validateSystem(): Promise<SystemValidationReport> {
    this.results = [];
    this.startTime = Date.now();

    console.log('🔍 Starting comprehensive system validation...');

    // Test all API endpoints
    await this.validateAuthenticationEndpoints();
    await this.validateNexusEndpoints();
    await this.validateWorldEndpoints();
    await this.validateRealTimeFeatures();
    await this.validatePerformanceMetrics();

    return this.generateReport();
  }

  /**
   * Test authentication endpoints
   */
  private async validateAuthenticationEndpoints(): Promise<void> {
    console.log('🔐 Testing authentication endpoints...');

    // Test login endpoint availability
    await this.testEndpoint(
      'POST /api/v1/auth/login',
      async () => {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: 'test', password: 'test' })
        });
        return { status: response.status, data: await response.text() };
      },
      'Authentication endpoint should be accessible'
    );

    // Test registration endpoint availability
    await this.testEndpoint(
      'POST /api/v1/auth/register',
      async () => {
        const response = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            username: 'test', 
            password: 'test', 
            email: 'test@example.com' 
          })
        });
        return { status: response.status, data: await response.text() };
      },
      'Registration endpoint should be accessible'
    );
  }

  /**
   * Test nexus-related endpoints
   */
  private async validateNexusEndpoints(): Promise<void> {
    console.log('🌌 Testing nexus endpoints...');

    // Test nexus state endpoint
    await this.testEndpoint(
      'GET /api/v1/nexus/state',
      async () => {
        const data = await nexusAPI.getState();
        return { status: 200, data };
      },
      'Nexus state should be retrievable'
    );

    // Test story spheres endpoint
    await this.testEndpoint(
      'GET /api/v1/nexus/spheres',
      async () => {
        const data = await nexusAPI.getStorySpheres();
        return { status: 200, data };
      },
      'Story spheres should be retrievable'
    );
  }

  /**
   * Test world-related endpoints
   */
  private async validateWorldEndpoints(): Promise<void> {
    console.log('🌍 Testing world endpoints...');

    // Test world search endpoint
    await this.testEndpoint(
      'GET /api/v1/nexus/worlds/search',
      async () => {
        const data = await nexusAPI.searchWorlds({ q: 'test', per_page: 5 });
        return { status: 200, data };
      },
      'World search should return results'
    );

    // Test world creation endpoint availability
    await this.testEndpoint(
      'POST /api/v1/nexus/worlds',
      async () => {
        const response = await fetch('/api/v1/nexus/worlds', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'test'}`
          },
          body: JSON.stringify({ 
            world_title: 'Test World',
            world_genre: 'Fantasy',
            description: 'Test world for validation'
          })
        });
        return { status: response.status, data: await response.text() };
      },
      'World creation endpoint should be accessible'
    );

    // Test world details endpoint (using a sample world ID)
    await this.testEndpoint(
      'GET /api/v1/nexus/worlds/{world_id}',
      async () => {
        try {
          const searchResults = await nexusAPI.searchWorlds({ per_page: 1 });
          if (searchResults.results && searchResults.results.length > 0) {
            const worldId = searchResults.results[0].world_id;
            const data = await nexusAPI.getWorld(worldId);
            return { status: 200, data };
          } else {
            return { status: 404, data: 'No worlds available for testing' };
          }
        } catch (error: any) {
          return { status: 500, data: error.message };
        }
      },
      'World details should be retrievable'
    );

    // Test world entry endpoint availability
    await this.testEndpoint(
      'POST /api/v1/nexus/worlds/{world_id}/enter',
      async () => {
        const response = await fetch('/api/v1/nexus/worlds/test-world-id/enter', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'test'}`
          },
          body: JSON.stringify({ entry_preferences: {} })
        });
        return { status: response.status, data: await response.text() };
      },
      'World entry endpoint should be accessible'
    );
  }

  /**
   * Test real-time features
   */
  private async validateRealTimeFeatures(): Promise<void> {
    console.log('⚡ Testing real-time features...');

    // Test WebSocket connection capability
    await this.testEndpoint(
      'WebSocket /api/v1/ws/updates',
      async () => {
        return new Promise((resolve) => {
          try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/updates`;
            const ws = new WebSocket(wsUrl);
            
            const timeout = setTimeout(() => {
              ws.close();
              resolve({ status: 408, data: 'WebSocket connection timeout' });
            }, 5000);

            ws.onopen = () => {
              clearTimeout(timeout);
              ws.close();
              resolve({ status: 200, data: 'WebSocket connection successful' });
            };

            ws.onerror = () => {
              clearTimeout(timeout);
              resolve({ status: 500, data: 'WebSocket connection failed' });
            };
          } catch (error: any) {
            resolve({ status: 500, data: error.message });
          }
        });
      },
      'WebSocket connection should be available'
    );

    // Test real-time stats endpoint
    await this.testEndpoint(
      'GET /api/v1/nexus/stats/realtime',
      async () => {
        const response = await fetch('/api/v1/nexus/stats/realtime', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'test'}`,
          },
        });
        return { status: response.status, data: await response.text() };
      },
      'Real-time statistics should be available'
    );
  }

  /**
   * Test performance metrics
   */
  private async validatePerformanceMetrics(): Promise<void> {
    console.log('📊 Testing performance metrics...');

    // Test 3D rendering capability
    await this.testEndpoint(
      '3D Rendering Support',
      async () => {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) {
          return { status: 500, data: 'WebGL not supported' };
        }

        const renderer = gl.getParameter(gl.RENDERER);
        const vendor = gl.getParameter(gl.VENDOR);
        
        return { 
          status: 200, 
          data: { 
            webgl_supported: true,
            renderer,
            vendor,
            max_texture_size: gl.getParameter(gl.MAX_TEXTURE_SIZE)
          }
        };
      },
      '3D rendering should be supported'
    );

    // Test local storage capability
    await this.testEndpoint(
      'Local Storage Support',
      async () => {
        try {
          const testKey = 'tta_validation_test';
          const testValue = 'test_value_' + Date.now();
          
          localStorage.setItem(testKey, testValue);
          const retrieved = localStorage.getItem(testKey);
          localStorage.removeItem(testKey);
          
          if (retrieved === testValue) {
            return { status: 200, data: 'Local storage working correctly' };
          } else {
            return { status: 500, data: 'Local storage not functioning properly' };
          }
        } catch (error: any) {
          return { status: 500, data: error.message };
        }
      },
      'Local storage should be functional'
    );
  }

  /**
   * Test individual endpoint
   */
  private async testEndpoint(
    endpoint: string,
    testFunction: () => Promise<{ status: number; data: any }>,
    description: string
  ): Promise<void> {
    const startTime = Date.now();
    
    try {
      const result = await testFunction();
      const responseTime = Date.now() - startTime;
      
      let status: ValidationResult['status'] = 'success';
      let message = description + ' ✅';
      
      // Determine status based on response
      if (result.status >= 500) {
        status = 'error';
        message = description + ' ❌ - Server error';
      } else if (result.status >= 400) {
        status = 'warning';
        message = description + ' ⚠️ - Client error (expected for some tests)';
      } else if (responseTime > 5000) {
        status = 'warning';
        message = description + ' ⚠️ - Slow response time';
      }

      this.results.push({
        endpoint,
        status,
        responseTime,
        message,
        data: result.data,
      });

    } catch (error: any) {
      const responseTime = Date.now() - startTime;
      
      this.results.push({
        endpoint,
        status: 'error',
        responseTime,
        message: description + ' ❌ - Exception occurred',
        error: error.message,
      });
    }
  }

  /**
   * Generate comprehensive validation report
   */
  private generateReport(): SystemValidationReport {
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.status === 'success').length;
    const failedTests = this.results.filter(r => r.status === 'error').length;
    const warningTests = this.results.filter(r => r.status === 'warning').length;
    
    const averageResponseTime = this.results.reduce((sum, r) => sum + r.responseTime, 0) / totalTests;
    
    let overallStatus: SystemValidationReport['overall_status'] = 'healthy';
    if (failedTests > totalTests * 0.3) {
      overallStatus = 'critical';
    } else if (failedTests > 0 || warningTests > totalTests * 0.5) {
      overallStatus = 'degraded';
    }

    const recommendations: string[] = [];
    
    // Generate recommendations based on results
    if (averageResponseTime > 2000) {
      recommendations.push('Consider optimizing API response times - average is above 2 seconds');
    }
    
    if (failedTests > 0) {
      recommendations.push('Address failed endpoint tests to ensure full functionality');
    }
    
    if (warningTests > totalTests * 0.3) {
      recommendations.push('Review warning-level issues for potential improvements');
    }

    const webglTest = this.results.find(r => r.endpoint === '3D Rendering Support');
    if (webglTest?.status === 'error') {
      recommendations.push('WebGL support is required for 3D features - check browser compatibility');
    }

    if (recommendations.length === 0) {
      recommendations.push('System validation completed successfully - all systems operational');
    }

    return {
      overall_status: overallStatus,
      total_tests: totalTests,
      passed_tests: passedTests,
      failed_tests: failedTests,
      warning_tests: warningTests,
      average_response_time: Math.round(averageResponseTime),
      results: this.results,
      timestamp: new Date().toISOString(),
      recommendations,
    };
  }
}

/**
 * Convenience function to run system validation
 */
export const validateSystem = async (): Promise<SystemValidationReport> => {
  const validator = new SystemValidator();
  return await validator.validateSystem();
};

export default SystemValidator;
