// Logseq: [[TTA.dev/Tests/E2e-staging/Helpers/Load-testing-helpers]]
/**
 * Load Testing Helpers for E2E Tests
 *
 * Provides utilities for simulating concurrent users and load testing
 * the staging environment to validate system resilience and performance.
 */

import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import { STAGING_CONFIG } from './staging-config';

export interface LoadTestConfig {
  concurrentUsers: number;
  rampUpTime: number; // seconds
  testDuration: number; // seconds
  thinkTime: number; // milliseconds between actions
}

export interface LoadTestResult {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  throughput: number; // requests per second
  errorRate: number; // percentage
}

/**
 * Simulate concurrent users accessing the application
 */
export async function simulateConcurrentUsers(
  config: LoadTestConfig,
  userScenario: (page: Page, userId: number) => Promise<void>
): Promise<LoadTestResult> {
  const browser = await chromium.launch();
  const contexts: BrowserContext[] = [];
  const pages: Page[] = [];
  const responseTimes: number[] = [];
  let totalRequests = 0;
  let failedRequests = 0;

  try {
    console.log(`🔄 Starting load test with ${config.concurrentUsers} concurrent users`);

    // Ramp up users gradually
    const usersPerSecond = config.concurrentUsers / config.rampUpTime;
    const rampUpInterval = 1000 / usersPerSecond;

    for (let i = 0; i < config.concurrentUsers; i++) {
      if (i > 0) {
        await new Promise((resolve) => setTimeout(resolve, rampUpInterval));
      }

      const context = await browser.newContext();
      const page = await context.newPage();

      // Track response times
      page.on('response', (response) => {
        const timing = response.request().postDataBuffer?.length || 0;
        responseTimes.push(timing);
        totalRequests++;
      });

      contexts.push(context);
      pages.push(page);

      // Run user scenario in parallel
      userScenario(page, i).catch((error) => {
        console.error(`User ${i} error:`, error);
        failedRequests++;
      });
    }

    // Wait for test duration
    await new Promise((resolve) => setTimeout(resolve, config.testDuration * 1000));

    console.log(`✅ Load test completed`);

    // Calculate metrics
    return calculateLoadTestMetrics(totalRequests, failedRequests, responseTimes);
  } finally {
    // Cleanup
    for (const page of pages) {
      await page.close();
    }
    for (const context of contexts) {
      await context.close();
    }
    await browser.close();
  }
}

/**
 * Calculate load test metrics
 */
export function calculateLoadTestMetrics(
  totalRequests: number,
  failedRequests: number,
  responseTimes: number[]
): LoadTestResult {
  const successfulRequests = totalRequests - failedRequests;
  const sortedTimes = responseTimes.sort((a, b) => a - b);

  return {
    totalRequests,
    successfulRequests,
    failedRequests,
    averageResponseTime: sortedTimes.reduce((a, b) => a + b, 0) / sortedTimes.length,
    minResponseTime: Math.min(...sortedTimes),
    maxResponseTime: Math.max(...sortedTimes),
    p95ResponseTime: sortedTimes[Math.floor(sortedTimes.length * 0.95)],
    p99ResponseTime: sortedTimes[Math.floor(sortedTimes.length * 0.99)],
    throughput: totalRequests / (sortedTimes.length / 1000),
    errorRate: (failedRequests / totalRequests) * 100,
  };
}

/**
 * Standard user journey for load testing
 */
export async function standardUserJourney(page: Page, userId: number): Promise<void> {
  try {
    // Login
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    const usernameInput = page.locator('input[name="username"]').first();
    const passwordInput = page.locator('input[name="password"]').first();

    await usernameInput.fill(`user_${userId}`);
    await passwordInput.fill('password123');

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await page.waitForURL(/dashboard|home/i, { timeout: 10000 });

    // Navigate to gameplay
    await page.goto(`${STAGING_CONFIG.frontend.url}/gameplay`);
    await page.waitForLoadState('networkidle');

    // Send a message
    const chatInput = page.locator('input[name="message"]').first();
    await chatInput.fill(`Test message from user ${userId}`);

    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();

    await page.waitForLoadState('networkidle');
  } catch (error) {
    console.error(`User ${userId} journey failed:`, error);
    throw error;
  }
}

/**
 * Stress test configuration
 */
export const STRESS_TEST_CONFIG: LoadTestConfig = {
  concurrentUsers: 50,
  rampUpTime: 60,
  testDuration: 300,
  thinkTime: 1000,
};

/**
 * Normal load test configuration
 */
export const NORMAL_LOAD_CONFIG: LoadTestConfig = {
  concurrentUsers: 10,
  rampUpTime: 30,
  testDuration: 120,
  thinkTime: 2000,
};

/**
 * Light load test configuration
 */
export const LIGHT_LOAD_CONFIG: LoadTestConfig = {
  concurrentUsers: 5,
  rampUpTime: 15,
  testDuration: 60,
  thinkTime: 3000,
};

/**
 * Generate load test report
 */
export function generateLoadTestReport(result: LoadTestResult): string {
  let report = '=== Load Test Report ===\n\n';
  report += `Total Requests: ${result.totalRequests}\n`;
  report += `Successful: ${result.successfulRequests}\n`;
  report += `Failed: ${result.failedRequests}\n`;
  report += `Error Rate: ${result.errorRate.toFixed(2)}%\n\n`;

  report += '=== Response Times ===\n';
  report += `Average: ${result.averageResponseTime.toFixed(2)}ms\n`;
  report += `Min: ${result.minResponseTime.toFixed(2)}ms\n`;
  report += `Max: ${result.maxResponseTime.toFixed(2)}ms\n`;
  report += `P95: ${result.p95ResponseTime.toFixed(2)}ms\n`;
  report += `P99: ${result.p99ResponseTime.toFixed(2)}ms\n\n`;

  report += `Throughput: ${result.throughput.toFixed(2)} req/s\n`;

  return report;
}

/**
 * Validate load test results against thresholds
 */
export function validateLoadTestResults(
  result: LoadTestResult,
  thresholds: {
    maxErrorRate?: number;
    maxP95ResponseTime?: number;
    maxP99ResponseTime?: number;
    minThroughput?: number;
  }
): { passed: boolean; violations: string[] } {
  const violations: string[] = [];

  if (thresholds.maxErrorRate && result.errorRate > thresholds.maxErrorRate) {
    violations.push(
      `Error rate ${result.errorRate.toFixed(2)}% exceeds threshold ${thresholds.maxErrorRate}%`
    );
  }

  if (thresholds.maxP95ResponseTime && result.p95ResponseTime > thresholds.maxP95ResponseTime) {
    violations.push(
      `P95 response time ${result.p95ResponseTime.toFixed(2)}ms exceeds threshold ${thresholds.maxP95ResponseTime}ms`
    );
  }

  if (thresholds.maxP99ResponseTime && result.p99ResponseTime > thresholds.maxP99ResponseTime) {
    violations.push(
      `P99 response time ${result.p99ResponseTime.toFixed(2)}ms exceeds threshold ${thresholds.maxP99ResponseTime}ms`
    );
  }

  if (thresholds.minThroughput && result.throughput < thresholds.minThroughput) {
    violations.push(
      `Throughput ${result.throughput.toFixed(2)} req/s below threshold ${thresholds.minThroughput} req/s`
    );
  }

  return {
    passed: violations.length === 0,
    violations,
  };
}
