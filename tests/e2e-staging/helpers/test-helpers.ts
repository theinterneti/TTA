/**
 * Common Test Helper Utilities for Staging E2E Tests
 *
 * This file provides reusable helper functions for common test operations
 * like waiting, authentication, data setup, and validation.
 */

import { Page, expect } from '@playwright/test';
import { STAGING_CONFIG } from './staging-config';

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: Page, timeout: number = 5000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Wait for a specific element to be visible
 */
export async function waitForElement(
  page: Page,
  selector: string,
  timeout: number = STAGING_CONFIG.timeouts.medium
): Promise<void> {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}

/**
 * Perform login with demo credentials
 */
export async function loginWithDemoCredentials(page: Page): Promise<void> {
  const { username, password } = STAGING_CONFIG.testUsers.demo;

  // Navigate to login page
  await page.goto('/login');
  await waitForNetworkIdle(page);

  // Fill in credentials
  const usernameInput = page.locator('input[name="username"], input[id="username"]').first();
  const passwordInput = page.locator('input[name="password"], input[id="password"]').first();

  await expect(usernameInput).toBeVisible({ timeout: STAGING_CONFIG.timeouts.medium });
  await usernameInput.fill(username);
  await passwordInput.fill(password);

  // Submit form
  const submitButton = page.locator('button[type="submit"]').first();
  await submitButton.click();

  // Wait for redirect to dashboard
  await page.waitForURL(/dashboard|home/i, { timeout: STAGING_CONFIG.timeouts.long });
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  try {
    // Check for auth token in storage or session
    const token = await page.evaluate(() => {
      return sessionStorage.getItem('auth_token') || localStorage.getItem('auth_token');
    });
    return !!token;
  } catch {
    return false;
  }
}

/**
 * Logout user
 */
export async function logout(page: Page): Promise<void> {
  // Look for logout button
  const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Sign Out"), a:has-text("Logout")').first();

  if (await logoutButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    await logoutButton.click();
    await page.waitForURL(/login/i, { timeout: STAGING_CONFIG.timeouts.medium });
  } else {
    // Clear session manually
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.clear();
    });
    await page.goto('/login');
  }
}

/**
 * Take a screenshot with a descriptive name
 */
export async function takeScreenshot(
  page: Page,
  name: string,
  fullPage: boolean = false
): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results-staging/screenshots/${name}-${timestamp}.png`,
    fullPage,
  });
}

/**
 * Check for console errors
 */
export async function getConsoleErrors(page: Page): Promise<string[]> {
  const errors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  return errors;
}

/**
 * Wait for API response
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = STAGING_CONFIG.timeouts.medium
): Promise<any> {
  const response = await page.waitForResponse(
    (response) => {
      const url = response.url();
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern);
      }
      return urlPattern.test(url);
    },
    { timeout }
  );

  return response.json();
}

/**
 * Check if element exists (without throwing)
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  try {
    const element = await page.locator(selector).first();
    return await element.isVisible({ timeout: 2000 });
  } catch {
    return false;
  }
}

/**
 * Fill form field safely
 */
export async function fillField(
  page: Page,
  selector: string,
  value: string,
  timeout: number = STAGING_CONFIG.timeouts.short
): Promise<void> {
  const field = page.locator(selector).first();
  await expect(field).toBeVisible({ timeout });
  await field.fill(value);
}

/**
 * Click element safely
 */
export async function clickElement(
  page: Page,
  selector: string,
  timeout: number = STAGING_CONFIG.timeouts.short
): Promise<void> {
  const element = page.locator(selector).first();
  await expect(element).toBeVisible({ timeout });
  await element.click();
}

/**
 * Wait for AI response in chat
 */
export async function waitForAIResponse(
  page: Page,
  timeout: number = STAGING_CONFIG.timeouts.aiResponse
): Promise<void> {
  // Wait for loading indicator to disappear
  const loadingIndicator = page.locator('[data-testid*="loading"], .loading, .spinner').first();

  if (await loadingIndicator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await loadingIndicator.waitFor({ state: 'hidden', timeout });
  } else {
    // Fallback: wait for new message
    await page.waitForTimeout(2000);
  }
}

/**
 * Get current URL path
 */
export async function getCurrentPath(page: Page): Promise<string> {
  const url = new URL(page.url());
  return url.pathname;
}

/**
 * Navigate and wait
 */
export async function navigateTo(page: Page, path: string): Promise<void> {
  await page.goto(path);
  await waitForNetworkIdle(page);
}

/**
 * Check accessibility with axe
 */
export async function checkAccessibility(page: Page): Promise<any> {
  try {
    const { default: AxeBuilder } = await import('@axe-core/playwright');
    const results = await new AxeBuilder({ page }).analyze();
    return results;
  } catch (error) {
    console.warn('Accessibility check failed:', error);
    return null;
  }
}

/**
 * Measure page load time
 */
export async function measurePageLoadTime(page: Page): Promise<number> {
  const timing = await page.evaluate(() => {
    const perfData = window.performance.timing;
    return perfData.loadEventEnd - perfData.navigationStart;
  });
  return timing;
}

/**
 * Clear all test data
 */
export async function clearTestData(page: Page): Promise<void> {
  try {
    await page.evaluate(() => {
      try {
        sessionStorage.clear();
      } catch (e) {
        // SessionStorage might not be accessible
        console.log('Could not clear sessionStorage:', e);
      }
      try {
        localStorage.clear();
      } catch (e) {
        // LocalStorage might not be accessible
        console.log('Could not clear localStorage:', e);
      }
      // Clear cookies
      try {
        document.cookie.split(';').forEach((c) => {
          document.cookie = c
            .replace(/^ +/, '')
            .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
        });
      } catch (e) {
        console.log('Could not clear cookies:', e);
      }
    });
  } catch (error) {
    // If page.evaluate fails entirely, just log and continue
    console.log('Could not clear test data:', error);
  }
}

/**
 * Generate random test data
 */
export function generateRandomString(length: number = 10): string {
  return Math.random().toString(36).substring(2, length + 2);
}

/**
 * Generate random character name
 */
export function generateRandomCharacterName(): string {
  const firstNames = ['Aria', 'Zephyr', 'Luna', 'Phoenix', 'River', 'Storm', 'Sage', 'Raven'];
  const lastNames = ['Stormwind', 'Moonwhisper', 'Firehart', 'Shadowblade', 'Lightbringer', 'Starweaver'];

  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];

  return `${firstName} ${lastName}`;
}
