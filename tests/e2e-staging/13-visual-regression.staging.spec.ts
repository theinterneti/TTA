/**
 * Visual Regression Testing Suite for TTA Staging Environment
 *
 * Tests visual consistency:
 * - Critical UI components
 * - Cross-browser visual validation
 * - Responsive design across viewports
 * - Visual regression detection
 */

import { test, expect, chromium, firefox, webkit } from '@playwright/test';
import {
  compareScreenshot,
  compareComponentAcrossBrowsers,
  compareMultipleViewports,
  CRITICAL_COMPONENTS,
  STANDARD_VIEWPORTS,
  generateVisualRegressionReport,
  cleanupVisualRegressionFiles,
} from './helpers/visual-regression-helpers';
import { STAGING_CONFIG } from './helpers/staging-config';

test.describe('Visual Regression Testing', () => {
  test.setTimeout(120000); // 2 minutes for visual tests

  test('should match login page baseline', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'login-page');

    expect(result.passed).toBeTruthy();
  });

  test('should match dashboard baseline', async ({ page }) => {
    // Login first
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const usernameInput = page.locator('input[name="username"]').first();
    const passwordInput = page.locator('input[name="password"]').first();

    await usernameInput.fill('testuser');
    await passwordInput.fill('password123');

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await page.waitForURL(/dashboard|home/i, { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'dashboard');

    expect(result.passed).toBeTruthy();
  });

  test('should match character creation baseline', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/character-creation`);
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'character-creation');

    expect(result.passed).toBeTruthy();
  });

  test('should match gameplay interface baseline', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/gameplay`);
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'gameplay-interface');

    expect(result.passed).toBeTruthy();
  });

  test('should be consistent across browsers', async () => {
    const browsers = {
      chromium: await chromium.launch(),
      firefox: await firefox.launch(),
      webkit: await webkit.launch(),
    };

    const pages: Record<string, any> = {};

    try {
      for (const [browserName, browser] of Object.entries(browsers)) {
        const page = await browser.newPage();
        pages[browserName] = page;

        await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
        await page.waitForLoadState('networkidle');
      }

      const results = await compareComponentAcrossBrowsers(
        pages,
        '[data-testid="login-page"]',
        'login-page-cross-browser'
      );

      // All browsers should have screenshots
      expect(Object.keys(results).length).toBeGreaterThan(0);

      for (const result of Object.values(results)) {
        expect(result.passed).toBeTruthy();
      }
    } finally {
      for (const page of Object.values(pages)) {
        await page.close();
      }
      for (const browser of Object.values(browsers)) {
        await browser.close();
      }
    }
  });

  test('should be responsive across viewports', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);

    const results = await compareMultipleViewports(page, 'login-page', STANDARD_VIEWPORTS);

    console.log(generateVisualRegressionReport(results));

    // All viewports should render without errors
    for (const result of results) {
      expect(result.passed).toBeTruthy();
    }
  });

  test('should maintain layout on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    // Check that elements are visible and not overlapping
    const inputs = page.locator('input');
    const inputCount = await inputs.count();

    expect(inputCount).toBeGreaterThan(0);

    // All inputs should be visible
    for (let i = 0; i < inputCount; i++) {
      const isVisible = await inputs.nth(i).isVisible();
      expect(isVisible).toBeTruthy();
    }
  });

  test('should maintain layout on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'login-page-tablet');

    expect(result.passed).toBeTruthy();
  });

  test('should maintain layout on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    const result = await compareScreenshot(page, 'login-page-desktop');

    expect(result.passed).toBeTruthy();
  });

  test('should detect visual regressions', async ({ page }) => {
    await page.goto(`${STAGING_CONFIG.frontend.url}/login`);
    await page.waitForLoadState('networkidle');

    // Take initial screenshot
    const result1 = await compareScreenshot(page, 'regression-test', {
      baselineDir: 'tests/e2e-staging/visual-baselines',
      diffDir: 'tests/e2e-staging/visual-diffs',
      threshold: 0.01,
      updateBaseline: true,
    });

    expect(result1.passed).toBeTruthy();

    // Modify page (simulate regression)
    await page.evaluate(() => {
      const button = document.querySelector('button');
      if (button) {
        button.style.backgroundColor = 'red';
      }
    });

    // Take second screenshot
    const result2 = await compareScreenshot(page, 'regression-test', {
      baselineDir: 'tests/e2e-staging/visual-baselines',
      diffDir: 'tests/e2e-staging/visual-diffs',
      threshold: 0.01,
      updateBaseline: false,
    });

    // Should detect the change
    expect(result2.passed).toBeFalsy();
  });

  test('should cleanup old visual regression files', () => {
    cleanupVisualRegressionFiles(
      {
        baselineDir: 'tests/e2e-staging/visual-baselines',
        diffDir: 'tests/e2e-staging/visual-diffs',
        threshold: 0.01,
        updateBaseline: false,
      },
      7
    );

    // Should complete without errors
    expect(true).toBeTruthy();
  });
});

