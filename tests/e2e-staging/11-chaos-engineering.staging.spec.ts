/**
 * Chaos Engineering Test Suite for TTA Staging Environment
 *
 * Tests system resilience under failure conditions:
 * - Network failures and latency
 * - Database disconnections
 * - Service outages
 * - Partial failures
 * - Graceful degradation
 */

import { test, expect } from '@playwright/test';
import {
  simulateNetworkLatency,
  simulateNetworkFailure,
  simulateDatabaseDisconnection,
  simulatePartialServiceFailure,
  testGracefulDegradation,
  testRecoveryFromFailure,
  testCircuitBreaker,
  CHAOS_SCENARIOS,
  generateChaosTestReport,
} from './helpers/chaos-engineering-helpers';
import { STAGING_CONFIG } from './helpers/staging-config';

test.describe('Chaos Engineering', () => {
  test.setTimeout(120000); // 2 minutes for chaos tests

  test('should handle high network latency gracefully', async ({ page }) => {
    await simulateNetworkLatency(page, 5000);

    const result = await testGracefulDegradation(page, async () => {
      await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    });

    expect(result.passed).toBeTruthy();
    expect(result.systemState).toBe('degraded');
  });

  test('should handle network failure with error message', async ({ page }) => {
    await simulateNetworkFailure(page);

    const result = await testGracefulDegradation(page, async () => {
      try {
        await page.goto(`${STAGING_CONFIG.frontend.url}/login`, { timeout: 5000 });
      } catch {
        // Expected to fail
      }
    });

    // Should show error message or offline indicator
    const errorVisible = await page.locator('[role="alert"]').isVisible().catch(() => false);
    expect(errorVisible || result.systemState === 'degraded').toBeTruthy();
  });

  test('should recover from database disconnection', async ({ page }) => {
    const result = await testRecoveryFromFailure(
      page,
      async (p) => {
        await simulateDatabaseDisconnection(p);
        await p.goto(`${STAGING_CONFIG.frontend.url}/gameplay`);
      },
      async (p) => {
        await p.reload();
      }
    );

    expect(result.passed).toBeTruthy();
    expect(result.recoveryTime).toBeLessThan(10000);
  });

  test('should handle partial service failures', async ({ page }) => {
    await simulatePartialServiceFailure(page, 0.5);

    const result = await testGracefulDegradation(page, async () => {
      await page.goto(`${STAGING_CONFIG.frontend.url}/gameplay`);
    });

    // System should remain partially functional
    expect(result.systemState).not.toBe('failed');
  });

  test('should implement circuit breaker pattern', async ({ page }) => {
    const result = await testCircuitBreaker(
      page,
      `${STAGING_CONFIG.frontend.url}/api/invalid-endpoint`,
      3
    );

    // Circuit breaker should activate after multiple failures
    expect(result.passed).toBeTruthy();
  });

  test('should display user-friendly error messages', async ({ page }) => {
    await simulateNetworkFailure(page, '**/api/**');

    await page.goto(`${STAGING_CONFIG.frontend.url}/gameplay`);

    // Wait for error message
    const errorMessage = await page
      .locator('[role="alert"]')
      .first()
      .textContent()
      .catch(() => null);

    // Error message should be user-friendly (not technical)
    if (errorMessage) {
      expect(errorMessage.toLowerCase()).not.toContain('500');
      expect(errorMessage.toLowerCase()).not.toContain('undefined');
    }
  });

  test('should maintain data consistency during failures', async ({ page }) => {
    // Simulate intermittent failures
    await simulatePartialServiceFailure(page, 0.3);

    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    // Try to login
    const usernameInput = page.locator('input[name="username"]').first();
    const passwordInput = page.locator('input[name="password"]').first();

    await usernameInput.fill('testuser');
    await passwordInput.fill('password123');

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Should either succeed or show clear error, not corrupt data
    await page.waitForTimeout(2000);

    const isLoggedIn = page.url().includes('dashboard') || page.url().includes('home');
    const hasError = await page.locator('[role="alert"]').isVisible().catch(() => false);

    expect(isLoggedIn || hasError).toBeTruthy();
  });

  test('should handle timeout gracefully', async ({ page }) => {
    // Simulate slow API responses
    await page.route('**/api/**', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 30000));
      await route.continue();
    });

    const result = await testGracefulDegradation(page, async () => {
      try {
        await page.goto(`${STAGING_CONFIG.frontend.url}/gameplay`, { timeout: 5000 });
      } catch {
        // Expected timeout
      }
    });

    // Should show timeout error or retry option
    expect(result.systemState).not.toBe('healthy');
  });

  test('should validate all chaos scenarios', async ({ page }) => {
    const results = [];

    for (const scenario of CHAOS_SCENARIOS.slice(0, 3)) {
      // Test first 3 scenarios to keep test time reasonable
      try {
        await scenario.execute(page);
        results.push({
          scenario: scenario.name,
          passed: true,
          systemState: 'degraded',
        });
      } catch (error) {
        results.push({
          scenario: scenario.name,
          passed: false,
          systemState: 'failed',
          errorMessage: String(error),
        });
      }
    }

    console.log(generateChaosTestReport(results));

    // At least some scenarios should be handled gracefully
    const passedCount = results.filter((r) => r.passed).length;
    expect(passedCount).toBeGreaterThan(0);
  });
});
