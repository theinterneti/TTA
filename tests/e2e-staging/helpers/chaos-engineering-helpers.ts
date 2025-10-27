/**
 * Chaos Engineering Helpers for E2E Tests
 *
 * Provides utilities for simulating failures and validating system resilience:
 * - Network failures and latency
 * - Database disconnections
 * - Service outages
 * - Partial failures
 */

import { Page, Response } from '@playwright/test';

export interface ChaosScenario {
  name: string;
  description: string;
  execute: (page: Page) => Promise<void>;
  expectedBehavior: string;
}

export interface ChaosTestResult {
  scenario: string;
  passed: boolean;
  errorMessage?: string;
  recoveryTime?: number; // milliseconds
  systemState: 'healthy' | 'degraded' | 'failed';
}

/**
 * Simulate network latency
 */
export async function simulateNetworkLatency(
  page: Page,
  latencyMs: number
): Promise<void> {
  await page.route('**/*', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, latencyMs));
    await route.continue();
  });
}

/**
 * Simulate network failure
 */
export async function simulateNetworkFailure(
  page: Page,
  urlPattern: string = '**/*'
): Promise<void> {
  await page.route(urlPattern, (route) => {
    route.abort('failed');
  });
}

/**
 * Simulate timeout
 */
export async function simulateTimeout(
  page: Page,
  urlPattern: string = '**/*',
  timeoutMs: number = 30000
): Promise<void> {
  await page.route(urlPattern, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, timeoutMs));
    await route.abort('timedout');
  });
}

/**
 * Simulate API error responses
 */
export async function simulateApiErrors(
  page: Page,
  statusCode: number = 500,
  urlPattern: string = '**/api/**'
): Promise<void> {
  await page.route(urlPattern, (route) => {
    route.abort('failed');
  });
}

/**
 * Simulate database disconnection
 */
export async function simulateDatabaseDisconnection(
  page: Page
): Promise<void> {
  // Block database-related API calls
  await page.route('**/api/database/**', (route) => {
    route.abort('failed');
  });

  // Block WebSocket connections
  await page.route('**/ws/**', (route) => {
    route.abort('failed');
  });
}

/**
 * Simulate partial service failure
 */
export async function simulatePartialServiceFailure(
  page: Page,
  failureRate: number = 0.5 // 50% failure rate
): Promise<void> {
  await page.route('**/api/**', (route) => {
    if (Math.random() < failureRate) {
      route.abort('failed');
    } else {
      route.continue();
    }
  });
}

/**
 * Simulate slow API responses
 */
export async function simulateSlowApiResponses(
  page: Page,
  delayMs: number = 5000
): Promise<void> {
  await page.route('**/api/**', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    await route.continue();
  });
}

/**
 * Simulate Redis disconnection
 */
export async function simulateRedisDisconnection(
  page: Page
): Promise<void> {
  await page.route('**/api/cache/**', (route) => {
    route.abort('failed');
  });
}

/**
 * Simulate Neo4j disconnection
 */
export async function simulateNeo4jDisconnection(
  page: Page
): Promise<void> {
  await page.route('**/api/graph/**', (route) => {
    route.abort('failed');
  });
}

/**
 * Test graceful degradation
 */
export async function testGracefulDegradation(
  page: Page,
  action: () => Promise<void>
): Promise<ChaosTestResult> {
  const startTime = Date.now();

  try {
    await action();

    // Check if error message is displayed
    const errorMessage = await page.locator('[role="alert"]').first().textContent();

    if (errorMessage) {
      return {
        scenario: 'Graceful Degradation',
        passed: true,
        systemState: 'degraded',
        recoveryTime: Date.now() - startTime,
      };
    }

    return {
      scenario: 'Graceful Degradation',
      passed: false,
      errorMessage: 'No error message displayed',
      systemState: 'failed',
    };
  } catch (error) {
    return {
      scenario: 'Graceful Degradation',
      passed: false,
      errorMessage: String(error),
      systemState: 'failed',
    };
  }
}

/**
 * Test recovery from failure
 */
export async function testRecoveryFromFailure(
  page: Page,
  failureSimulation: (page: Page) => Promise<void>,
  recoveryAction: (page: Page) => Promise<void>
): Promise<ChaosTestResult> {
  const startTime = Date.now();

  try {
    // Simulate failure
    await failureSimulation(page);

    // Wait for recovery
    await page.waitForTimeout(2000);

    // Attempt recovery
    await recoveryAction(page);

    const recoveryTime = Date.now() - startTime;

    return {
      scenario: 'Recovery from Failure',
      passed: true,
      systemState: 'healthy',
      recoveryTime,
    };
  } catch (error) {
    return {
      scenario: 'Recovery from Failure',
      passed: false,
      errorMessage: String(error),
      systemState: 'failed',
    };
  }
}

/**
 * Test circuit breaker pattern
 */
export async function testCircuitBreaker(
  page: Page,
  failingEndpoint: string,
  maxFailures: number = 3
): Promise<ChaosTestResult> {
  let failures = 0;

  try {
    // Simulate multiple failures
    for (let i = 0; i < maxFailures + 1; i++) {
      try {
        await page.goto(failingEndpoint, { waitUntil: 'networkidle', timeout: 5000 });
      } catch {
        failures++;
      }
    }

    // Check if circuit breaker is active (should show fallback UI)
    const fallbackUI = await page.locator('[data-testid="fallback-ui"]').isVisible();

    return {
      scenario: 'Circuit Breaker',
      passed: fallbackUI,
      systemState: fallbackUI ? 'degraded' : 'failed',
    };
  } catch (error) {
    return {
      scenario: 'Circuit Breaker',
      passed: false,
      errorMessage: String(error),
      systemState: 'failed',
    };
  }
}

/**
 * Test retry logic
 */
export async function testRetryLogic(
  page: Page,
  action: () => Promise<void>,
  maxRetries: number = 3
): Promise<ChaosTestResult> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await action();
      return {
        scenario: `Retry Logic (Attempt ${attempt})`,
        passed: true,
        systemState: 'healthy',
      };
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries) {
        await page.waitForTimeout(1000 * attempt); // Exponential backoff
      }
    }
  }

  return {
    scenario: 'Retry Logic',
    passed: false,
    errorMessage: lastError?.message,
    systemState: 'failed',
  };
}

/**
 * Predefined chaos scenarios
 */
export const CHAOS_SCENARIOS: ChaosScenario[] = [
  {
    name: 'High Latency',
    description: 'Simulate 5 second network latency',
    execute: async (page: Page) => {
      await simulateNetworkLatency(page, 5000);
      await page.goto('http://localhost:3001');
    },
    expectedBehavior: 'Page should load with loading indicators',
  },
  {
    name: 'Network Failure',
    description: 'Simulate complete network failure',
    execute: async (page: Page) => {
      await simulateNetworkFailure(page);
      await page.goto('http://localhost:3001');
    },
    expectedBehavior: 'Should show offline error message',
  },
  {
    name: 'API Timeout',
    description: 'Simulate API timeout',
    execute: async (page: Page) => {
      await simulateTimeout(page, '**/api/**', 30000);
      await page.goto('http://localhost:3001/gameplay');
    },
    expectedBehavior: 'Should show timeout error and retry option',
  },
  {
    name: 'Database Disconnection',
    description: 'Simulate database disconnection',
    execute: async (page: Page) => {
      await simulateDatabaseDisconnection(page);
      await page.goto('http://localhost:3001/gameplay');
    },
    expectedBehavior: 'Should show database error with fallback UI',
  },
  {
    name: 'Partial Service Failure',
    description: 'Simulate 50% API failure rate',
    execute: async (page: Page) => {
      await simulatePartialServiceFailure(page, 0.5);
      await page.goto('http://localhost:3001/gameplay');
    },
    expectedBehavior: 'Should handle intermittent failures gracefully',
  },
];

/**
 * Generate chaos test report
 */
export function generateChaosTestReport(results: ChaosTestResult[]): string {
  let report = '=== Chaos Engineering Test Report ===\n\n';

  const passed = results.filter((r) => r.passed).length;
  const failed = results.filter((r) => !r.passed).length;

  report += `Total Tests: ${results.length}\n`;
  report += `Passed: ${passed}\n`;
  report += `Failed: ${failed}\n`;
  report += `Success Rate: ${((passed / results.length) * 100).toFixed(2)}%\n\n`;

  report += '=== Detailed Results ===\n';
  for (const result of results) {
    report += `\n${result.scenario}: ${result.passed ? '✅ PASS' : '❌ FAIL'}\n`;
    report += `System State: ${result.systemState}\n`;
    if (result.recoveryTime) {
      report += `Recovery Time: ${result.recoveryTime}ms\n`;
    }
    if (result.errorMessage) {
      report += `Error: ${result.errorMessage}\n`;
    }
  }

  return report;
}

