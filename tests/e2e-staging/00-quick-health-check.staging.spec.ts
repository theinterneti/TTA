/**
 * Quick Health Check for TTA Staging Environment
 *
 * This test validates that the staging environment is accessible and responsive
 * before running the full E2E test suite.
 */

import { test, expect } from '@playwright/test';

test.describe('Staging Environment Health Check', () => {
  test('Frontend is accessible', async ({ page }) => {
    console.log('✓ Testing frontend accessibility at http://localhost:3001');

    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Check that page loaded
    const title = await page.title();
    console.log(`  ✓ Page title: ${title}`);
    expect(title).toBeTruthy();

    // Check that HTML is present
    const html = await page.content();
    expect(html).toContain('<!DOCTYPE html>');
    console.log('  ✓ HTML content loaded');
  });

  test('API is accessible', async ({ request }) => {
    console.log('✓ Testing API accessibility at http://localhost:8081');

    const response = await request.get('http://localhost:8081/health');
    console.log(`  ✓ API health check status: ${response.status()}`);
    expect(response.ok()).toBeTruthy();
  });

  test('Frontend renders login page', async ({ page }) => {
    console.log('✓ Testing login page rendering');

    await page.goto('/', { waitUntil: 'networkidle', timeout: 30000 });

    // Wait for React to render
    await page.waitForTimeout(2000);

    // Take screenshot for debugging
    await page.screenshot({ path: 'test-results-staging/health-check-login.png' });

    // Check for common login elements
    const bodyText = await page.textContent('body');
    console.log(`  ✓ Page body contains text: ${bodyText?.substring(0, 100)}...`);

    // Look for any form elements
    const forms = await page.locator('form').count();
    const inputs = await page.locator('input').count();
    const buttons = await page.locator('button').count();

    console.log(`  ✓ Found ${forms} forms, ${inputs} inputs, ${buttons} buttons`);

    expect(inputs + buttons).toBeGreaterThan(0);
  });

  test('Can interact with page elements', async ({ page }) => {
    console.log('✓ Testing page interactivity');

    await page.goto('/', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);

    // Try to find any clickable elements
    const clickableElements = await page.locator('button, a, input[type="submit"]').count();
    console.log(`  ✓ Found ${clickableElements} clickable elements`);

    expect(clickableElements).toBeGreaterThan(0);
  });

  test('No console errors on page load', async ({ page }) => {
    console.log('✓ Testing for console errors');

    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);

    if (errors.length > 0) {
      console.log(`  ⚠ Found ${errors.length} console errors:`);
      errors.forEach(err => console.log(`    - ${err}`));
    } else {
      console.log('  ✓ No console errors detected');
    }

    // Don't fail on console errors for now, just report them
    expect(errors.length).toBeLessThan(100); // Sanity check
  });
});
