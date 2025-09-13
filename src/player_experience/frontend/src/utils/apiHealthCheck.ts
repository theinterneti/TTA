/**
 * API Health Check Utility
 *
 * Provides functions to verify backend connectivity and API health
 * for the TTA Player Experience Interface.
 */

interface HealthCheckResult {
  healthy: boolean;
  service?: string;
  error?: string;
  responseTime?: number;
}

interface ConnectivityTestResult {
  apiHealth: HealthCheckResult;
  corsEnabled: boolean;
  authEndpointAccessible: boolean;
  nexusEndpointAccessible: boolean;
  overallStatus: 'healthy' | 'degraded' | 'unhealthy';
}

/**
 * Check if the API health endpoint is responding
 */
export async function checkApiHealth(): Promise<HealthCheckResult> {
  const startTime = Date.now();

  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    const responseTime = Date.now() - startTime;

    if (response.ok) {
      const data = await response.json();
      return {
        healthy: true,
        service: data.service,
        responseTime,
      };
    } else {
      return {
        healthy: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
        responseTime,
      };
    }
  } catch (error) {
    return {
      healthy: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      responseTime: Date.now() - startTime,
    };
  }
}

/**
 * Test CORS configuration by checking response headers
 */
export async function testCorsConfiguration(): Promise<boolean> {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/health`, {
      method: 'GET',
      headers: {
        'Origin': window.location.origin,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    // Check if CORS headers are present
    const corsOrigin = response.headers.get('access-control-allow-origin');
    const corsCredentials = response.headers.get('access-control-allow-credentials');

    return corsOrigin !== null && corsCredentials === 'true';
  } catch (error) {
    console.error('CORS test failed:', error);
    return false;
  }
}

/**
 * Test authentication endpoint accessibility
 */
export async function testAuthEndpoint(): Promise<boolean> {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username: 'test', password: 'test' }),
    });

    // We expect a 401 response for invalid credentials, which means the endpoint is accessible
    return response.status === 401;
  } catch (error) {
    console.error('Auth endpoint test failed:', error);
    return false;
  }
}

/**
 * Test Nexus API endpoint accessibility (should require auth)
 */
export async function testNexusEndpoint(): Promise<boolean> {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/nexus/state`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    // We expect a 401 or similar auth error, which means the endpoint is accessible
    return response.status === 401 || response.status === 403;
  } catch (error) {
    console.error('Nexus endpoint test failed:', error);
    return false;
  }
}

/**
 * Run comprehensive connectivity tests
 */
export async function runConnectivityTests(): Promise<ConnectivityTestResult> {
  console.log('🔍 Running API connectivity tests...');

  const [apiHealth, corsEnabled, authEndpointAccessible, nexusEndpointAccessible] = await Promise.all([
    checkApiHealth(),
    testCorsConfiguration(),
    testAuthEndpoint(),
    testNexusEndpoint(),
  ]);

  let overallStatus: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

  if (!apiHealth.healthy) {
    overallStatus = 'unhealthy';
  } else if (!corsEnabled || !authEndpointAccessible || !nexusEndpointAccessible) {
    overallStatus = 'degraded';
  }

  const result: ConnectivityTestResult = {
    apiHealth,
    corsEnabled,
    authEndpointAccessible,
    nexusEndpointAccessible,
    overallStatus,
  };

  console.log('📊 Connectivity test results:', result);
  return result;
}

/**
 * Display connectivity test results in a user-friendly format
 */
export function displayConnectivityResults(results: ConnectivityTestResult): void {
  console.group('🌐 API Connectivity Test Results');

  console.log(`Overall Status: ${results.overallStatus.toUpperCase()}`);
  console.log(`API Health: ${results.apiHealth.healthy ? '✅' : '❌'} ${results.apiHealth.service || ''}`);
  console.log(`CORS Enabled: ${results.corsEnabled ? '✅' : '❌'}`);
  console.log(`Auth Endpoint: ${results.authEndpointAccessible ? '✅' : '❌'}`);
  console.log(`Nexus Endpoint: ${results.nexusEndpointAccessible ? '✅' : '❌'}`);

  if (results.apiHealth.responseTime) {
    console.log(`Response Time: ${results.apiHealth.responseTime}ms`);
  }

  if (results.apiHealth.error) {
    console.error(`API Error: ${results.apiHealth.error}`);
  }

  console.groupEnd();
}
