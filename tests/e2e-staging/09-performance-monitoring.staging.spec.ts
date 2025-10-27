/**
 * Performance Monitoring E2E Tests
 *
 * Validates that the application meets performance budgets and
 * provides acceptable user experience across different scenarios.
 */

import { expect, test } from '@playwright/test';
import { STAGING_CONFIG } from './helpers/staging-config';
import {
  measurePageLoadPerformance,
  measureApiResponseTime,
  validatePerformanceBudgets,
  PerformanceMonitor,
} from './helpers/performance-helpers';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { GameplayPage } from './page-objects/GameplayPage';

test.describe('Performance Monitoring', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let gameplayPage: GameplayPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    gameplayPage = new GameplayPage(page);
  });

  test('should load login page within performance budget', async ({ page }) => {
    console.log('⏱️ Measuring login page load performance');

    await loginPage.goto();

    const metrics = await measurePageLoadPerformance(page);

    console.log(`  → Page Load Time: ${metrics.pageLoadTime.toFixed(2)}ms`);
    console.log(`  → First Contentful Paint: ${metrics.firstContentfulPaint.toFixed(2)}ms`);
    console.log(`  → Time to Interactive: ${metrics.timeToInteractive.toFixed(2)}ms`);

    const validation = validatePerformanceBudgets(metrics);
    expect(validation.passed).toBeTruthy();

    console.log('  ✓ Login page meets performance budget');
  });

  test('should load dashboard within performance budget', async ({ page }) => {
    console.log('⏱️ Measuring dashboard load performance');

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await dashboardPage.goto();

    const metrics = await measurePageLoadPerformance(page);

    console.log(`  → Page Load Time: ${metrics.pageLoadTime.toFixed(2)}ms`);
    console.log(`  → First Contentful Paint: ${metrics.firstContentfulPaint.toFixed(2)}ms`);

    const validation = validatePerformanceBudgets(metrics);
    expect(validation.passed).toBeTruthy();

    console.log('  ✓ Dashboard meets performance budget');
  });

  test('should respond to API calls within budget', async ({ page }) => {
    console.log('⏱️ Measuring API response times');

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    const responseTime = await measureApiResponseTime(page, '/api/v1/dashboard', async () => {
      await dashboardPage.goto();
    });

    console.log(`  → API Response Time: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(STAGING_CONFIG.performance.apiResponse * 2);

    console.log('  ✓ API response time acceptable');
  });

  test('should handle AI responses within acceptable time', async ({ page }) => {
    console.log('⏱️ Measuring AI response time');

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    const startTime = Date.now();
    await gameplayPage.sendMessage('What do I see around me?');
    const responseTime = Date.now() - startTime;

    console.log(`  → AI Response Time: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(STAGING_CONFIG.timeouts.aiResponse);

    console.log('  ✓ AI response time acceptable');
  });

  test('should maintain performance during extended gameplay', async ({ page }) => {
    console.log('⏱️ Measuring performance during extended session');

    const monitor = new PerformanceMonitor(page);

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Simulate extended gameplay
    const messages = [
      'I look around carefully.',
      'I approach the nearest object.',
      'I examine it closely.',
      'I make a decision.',
      'I take action.',
    ];

    for (const message of messages) {
      await monitor.recordPageLoadMetrics();
      await gameplayPage.sendMessage(message);
    }

    const avgMetrics = monitor.getAverageMetrics();
    console.log(`  → Average Page Load Time: ${avgMetrics.pageLoadTime.toFixed(2)}ms`);
    console.log(`  → Average API Response Time: ${avgMetrics.averageApiResponseTime.toFixed(2)}ms`);

    const validation = validatePerformanceBudgets(avgMetrics);
    expect(validation.passed).toBeTruthy();

    console.log('  ✓ Performance maintained during extended session');
  });

  test('should not have layout shifts during interaction', async ({ page }) => {
    console.log('⏱️ Measuring layout stability');

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();

    const metrics = await measurePageLoadPerformance(page);

    console.log(`  → Cumulative Layout Shift: ${metrics.cumulativeLayoutShift.toFixed(3)}`);
    expect(metrics.cumulativeLayoutShift).toBeLessThan(0.1);

    console.log('  ✓ Layout is stable');
  });

  test('should generate performance report', async ({ page }) => {
    console.log('📊 Generating performance report');

    const monitor = new PerformanceMonitor(page);

    await loginPage.goto();
    await monitor.recordPageLoadMetrics();

    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await monitor.recordPageLoadMetrics();

    await gameplayPage.sendMessage('Test message');
    await monitor.recordPageLoadMetrics();

    const report = monitor.generateReport();
    console.log(report);

    expect(report).toContain('Performance Report');
    expect(report).toContain('Page Load Time');

    console.log('  ✓ Performance report generated');
  });

  test('should handle rapid interactions without degradation', async ({ page }) => {
    console.log('⚡ Testing rapid interactions');

    const monitor = new PerformanceMonitor(page);

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Send multiple messages rapidly
    const messages = ['Message 1', 'Message 2', 'Message 3'];

    for (const message of messages) {
      await monitor.recordPageLoadMetrics();
      await gameplayPage.sendMessage(message);
    }

    const avgMetrics = monitor.getAverageMetrics();
    const apiStats = monitor.getApiStats();

    console.log(`  → Average Response Time: ${avgMetrics.averageApiResponseTime.toFixed(2)}ms`);
    console.log(`  → API Endpoints: ${Object.keys(apiStats).length}`);

    // Performance should not degrade significantly
    expect(avgMetrics.pageLoadTime).toBeLessThan(STAGING_CONFIG.performance.pageLoad * 3);

    console.log('  ✓ Rapid interactions handled without degradation');
  });
});

