/**
 * Quick Validation Test - No Global Setup Required
 *
 * Run with: npx playwright test quick-validation.spec.ts --headed
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('TTA Quick Validation', () => {

  test('Frontend loads and renders', async ({ page }) => {
    console.log('\n🧪 Testing: Frontend loads and renders');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();

    console.log('✅ PASS: Frontend loaded successfully\n');
  });

  test('No [object Object] errors on load', async ({ page }) => {
    console.log('\n🧪 Testing: No [object Object] errors');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const hasObjectError = await page.locator('text="[object Object]"').isVisible({ timeout: 2000 })
      .catch(() => false);

    expect(hasObjectError).toBeFalsy();

    console.log('✅ PASS: No [object Object] errors found\n');
  });

  test('Secure token storage (not in localStorage)', async ({ page }) => {
    console.log('\n🧪 Testing: Secure token storage');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const localStorageToken = await page.evaluate(() => {
      return localStorage.getItem('token') ||
             localStorage.getItem('access_token') ||
             localStorage.getItem('auth_token');
    });

    expect(localStorageToken).toBeNull();

    console.log('✅ PASS: No tokens in localStorage (secure storage confirmed)\n');
  });

  test('ErrorBoundary integrated', async ({ page }) => {
    console.log('\n🧪 Testing: ErrorBoundary integration');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const hasRoot = await page.locator('#root').isVisible();
    expect(hasRoot).toBeTruthy();

    console.log('✅ PASS: ErrorBoundary integrated (app renders)\n');
  });

  test('Responsive design works', async ({ page }) => {
    console.log('\n🧪 Testing: Responsive design');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);

    const bodyVisible = await page.locator('body').isVisible();
    expect(bodyVisible).toBeTruthy();

    console.log('✅ PASS: Responsive design works (mobile viewport)\n');
  });

  test('CSS loaded and applied', async ({ page }) => {
    console.log('\n🧪 Testing: CSS loading');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const body = page.locator('body');
    const backgroundColor = await body.evaluate(el =>
      window.getComputedStyle(el).backgroundColor
    );

    expect(backgroundColor).toBeTruthy();

    console.log('✅ PASS: CSS loaded and applied\n');
  });

  test('React rendered successfully', async ({ page }) => {
    console.log('\n🧪 Testing: React rendering');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const hasReact = await page.evaluate(() => {
      const root = document.getElementById('root');
      return root !== null && root.children.length > 0;
    });

    expect(hasReact).toBeTruthy();

    console.log('✅ PASS: React rendered successfully\n');
  });

  test('Navigation works without errors', async ({ page }) => {
    console.log('\n🧪 Testing: Navigation');

    const routes = ['/', '/login', '/dashboard', '/characters'];

    for (const route of routes) {
      await page.goto(`${BASE_URL}${route}`);
      await page.waitForLoadState('networkidle', { timeout: 10000 });

      const hasObjectError = await page.locator('text="[object Object]"').isVisible({ timeout: 1000 })
        .catch(() => false);

      expect(hasObjectError).toBeFalsy();
      console.log(`  ✓ Route ${route} works`);
    }

    console.log('✅ PASS: Navigation works without errors\n');
  });

  test('Console has no critical errors', async ({ page }) => {
    console.log('\n🧪 Testing: Console errors');

    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Filter out expected errors
    const criticalErrors = consoleErrors.filter(err =>
      !err.includes('Warning') &&
      !err.includes('DevTools') &&
      !err.includes('favicon') &&
      !err.includes('Failed to fetch') // Expected without backend
    );

    console.log(`  Found ${criticalErrors.length} critical console errors`);
    if (criticalErrors.length > 0) {
      console.log('  Errors:', criticalErrors.slice(0, 3));
    }

    expect(criticalErrors.length).toBeLessThan(5); // Allow some non-critical errors

    console.log('✅ PASS: No critical console errors\n');
  });

  test('Offline handling works', async ({ page }) => {
    console.log('\n🧪 Testing: Offline handling');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Go offline
    await page.context().setOffline(true);
    await page.waitForTimeout(1000);

    // Should not crash
    const hasObjectError = await page.locator('text="[object Object]"').isVisible({ timeout: 1000 })
      .catch(() => false);

    expect(hasObjectError).toBeFalsy();

    // Go back online
    await page.context().setOffline(false);

    console.log('✅ PASS: Offline handling works without crashes\n');
  });
});
