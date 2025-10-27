import { Page, expect } from '@playwright/test';

/**
 * Utility functions for E2E tests
 */

// Authentication helpers
export async function loginAsUser(page: Page, username: string = 'testuser', password: string = 'testpass') {
  await page.goto('/');
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard/);
}

export async function logout(page: Page) {
  const logoutButton = page.locator('button, a').filter({ hasText: /logout|sign out/i });
  await logoutButton.click();
  await page.waitForURL(/login|auth/);
}

// Mock API responses
export async function mockApiResponse(page: Page, urlPattern: string | RegExp, response: any, status: number = 200) {
  await page.route(urlPattern, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(response),
    });
  });
}

export async function mockApiError(page: Page, urlPattern: string | RegExp, status: number = 500, error: string = 'Internal server error') {
  await page.route(urlPattern, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify({ error }),
    });
  });
}

export async function mockNetworkFailure(page: Page, urlPattern: string | RegExp) {
  await page.route(urlPattern, route => {
    route.abort('failed');
  });
}

// WebSocket mocking
export async function mockWebSocketMessage(page: Page, message: any) {
  await page.evaluate((msg) => {
    window.dispatchEvent(new CustomEvent('websocket-message', {
      detail: msg
    }));
  }, message);
}

export async function mockWebSocketConnectionStatus(page: Page, connected: boolean = true) {
  await page.evaluate((isConnected) => {
    window.dispatchEvent(new CustomEvent(isConnected ? 'websocket-connect' : 'websocket-disconnect'));
  }, connected);
}

// Form helpers
export async function fillForm(page: Page, formData: Record<string, string>) {
  for (const [field, value] of Object.entries(formData)) {
    const input = page.locator(`input[name="${field}"], textarea[name="${field}"], select[name="${field}"]`);
    await input.fill(value);
  }
}

export async function submitForm(page: Page, formSelector: string = 'form') {
  await page.locator(formSelector).press('Enter');
}

// Wait helpers
export async function waitForLoadingToComplete(page: Page, timeout: number = 10000) {
  await page.waitForSelector('.spinner', { state: 'hidden', timeout }).catch(() => {});
  await page.waitForSelector('[data-testid="loading"]', { state: 'hidden', timeout }).catch(() => {});
  await page.waitForLoadState('networkidle');
}

export async function waitForApiCall(page: Page, urlPattern: string | RegExp, timeout: number = 10000) {
  await page.waitForResponse(urlPattern, { timeout });
}

// Accessibility helpers
export async function checkBasicAccessibility(page: Page) {
  // Check for main landmark
  await expect(page.locator('main, [role="main"]')).toBeVisible();

  // Check for skip links
  const skipLinks = await page.locator('a[href^="#"]').count();
  expect(skipLinks).toBeGreaterThan(0);

  // Check for heading hierarchy
  const headings = page.locator('h1, h2, h3, h4, h5, h6');
  await expect(headings.first()).toBeVisible();
}

export async function testKeyboardNavigation(page: Page, elements: string[]) {
  for (let i = 0; i < elements.length - 1; i++) {
    await page.locator(elements[i]).focus();
    await page.keyboard.press('Tab');
    await expect(page.locator(elements[i + 1])).toBeFocused();
  }
}

// Visual testing helpers
export async function takeScreenshot(page: Page, name: string, fullPage: boolean = false) {
  await page.screenshot({
    path: `test-results/screenshots/${name}.png`,
    fullPage,
  });
}

export async function compareScreenshot(page: Page, name: string) {
  await expect(page).toHaveScreenshot(`${name}.png`);
}

// Performance helpers
export async function measurePageLoadTime(page: Page, url: string): Promise<number> {
  const startTime = Date.now();
  await page.goto(url);
  await waitForLoadingToComplete(page);
  return Date.now() - startTime;
}

export async function measureActionTime(action: () => Promise<void>): Promise<number> {
  const startTime = Date.now();
  await action();
  return Date.now() - startTime;
}

// Data generation helpers
export function generateRandomString(length: number = 10): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export function generateRandomEmail(): string {
  return `test_${generateRandomString(8)}@example.com`;
}

export function generateTimestamp(): string {
  return new Date().toISOString();
}

// Local storage helpers
export async function setLocalStorage(page: Page, key: string, value: string) {
  await page.evaluate(([k, v]) => {
    localStorage.setItem(k, v);
  }, [key, value]);
}

export async function getLocalStorage(page: Page, key: string): Promise<string | null> {
  return await page.evaluate((k) => {
    return localStorage.getItem(k);
  }, key);
}

export async function clearLocalStorage(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
  });
}

// Session storage helpers
export async function setSessionStorage(page: Page, key: string, value: string) {
  await page.evaluate(([k, v]) => {
    sessionStorage.setItem(k, v);
  }, [key, value]);
}

export async function clearSessionStorage(page: Page) {
  await page.evaluate(() => {
    sessionStorage.clear();
  });
}

// Cookie helpers
export async function setCookie(page: Page, name: string, value: string, domain?: string) {
  await page.context().addCookies([{
    name,
    value,
    domain: domain || 'localhost',
    path: '/',
  }]);
}

export async function clearCookies(page: Page) {
  await page.context().clearCookies();
}

// Viewport helpers
export async function setMobileViewport(page: Page) {
  await page.setViewportSize({ width: 375, height: 667 });
}

export async function setTabletViewport(page: Page) {
  await page.setViewportSize({ width: 768, height: 1024 });
}

export async function setDesktopViewport(page: Page) {
  await page.setViewportSize({ width: 1280, height: 720 });
}

// Error handling helpers
export async function expectNoConsoleErrors(page: Page) {
  const errors: string[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  // Wait a bit for any console errors to appear
  await page.waitForTimeout(1000);

  expect(errors).toHaveLength(0);
}

export async function expectNoNetworkErrors(page: Page) {
  const failedRequests: string[] = [];

  page.on('response', response => {
    if (response.status() >= 400) {
      failedRequests.push(`${response.status()} ${response.url()}`);
    }
  });

  // Wait for any pending requests
  await page.waitForLoadState('networkidle');

  expect(failedRequests).toHaveLength(0);
}

// Retry helpers
export async function retryAction(action: () => Promise<void>, maxRetries: number = 3, delay: number = 1000) {
  let lastError: Error | null = null;

  for (let i = 0; i < maxRetries; i++) {
    try {
      await action();
      return;
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

// Test data cleanup
export async function cleanupTestData(page: Page, userId?: string) {
  if (userId) {
    // Clean up user-specific test data
    await mockApiResponse(page, `**/players/${userId}/characters`, []);
    await mockApiResponse(page, `**/players/${userId}/sessions`, []);
  }

  // Clear browser storage
  await clearLocalStorage(page);
  await clearSessionStorage(page);
  await clearCookies(page);
}

// Debug helpers
export async function debugPageState(page: Page) {
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());
  console.log('Local storage:', await page.evaluate(() => ({ ...localStorage })));
  console.log('Session storage:', await page.evaluate(() => ({ ...sessionStorage })));
}

// WebSocket testing helpers
export async function mockWebSocketConnection(page: Page, responses: any[] = []) {
  await page.addInitScript((mockResponses) => {
    const originalWebSocket = window.WebSocket;
    let mockSocket: any = null;

    window.WebSocket = class extends EventTarget {
      readyState = WebSocket.CONNECTING;
      url: string;

      constructor(url: string | URL, protocols?: string | string[]) {
        super();
        this.url = url.toString();
        mockSocket = this;

        setTimeout(() => {
          this.readyState = WebSocket.OPEN;
          this.dispatchEvent(new Event('open'));
        }, 100);
      }

      send(data: string) {
        const message = JSON.parse(data);
        const response = mockResponses.find((r: any) => r.type === message.type) ||
                        { type: 'response', data: 'Mock response' };

        setTimeout(() => {
          this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify(response) }));
        }, 200);
      }

      close() {
        this.readyState = WebSocket.CLOSED;
        this.dispatchEvent(new Event('close'));
      }
    } as any;

    // Expose mock socket for testing
    (window as any).mockWebSocket = mockSocket;
  }, responses);
}

export async function simulateWebSocketError(page: Page, errorType: 'connection' | 'message' | 'close' = 'connection') {
  await page.evaluate((type) => {
    const mockSocket = (window as any).mockWebSocket;
    if (mockSocket) {
      switch (type) {
        case 'connection':
          mockSocket.dispatchEvent(new Event('error'));
          break;
        case 'message':
          mockSocket.dispatchEvent(new MessageEvent('error', { data: 'Message error' }));
          break;
        case 'close':
          mockSocket.readyState = WebSocket.CLOSED;
          mockSocket.dispatchEvent(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }));
          break;
      }
    }
  }, errorType);
}

// File handling helpers
export async function createTempFile(content: string, filename: string): Promise<string> {
  const fs = require('fs');
  const path = require('path');
  const os = require('os');

  const tempDir = os.tmpdir();
  const filePath = path.join(tempDir, filename);

  fs.writeFileSync(filePath, content);
  return filePath;
}

export async function deleteTempFile(filePath: string): Promise<void> {
  const fs = require('fs');
  try {
    fs.unlinkSync(filePath);
  } catch (error) {
    // Ignore errors if file doesn't exist
  }
}

// Performance measurement helpers
export async function measureRenderTime(page: Page, action: () => Promise<void>): Promise<number> {
  const startTime = await page.evaluate(() => performance.now());
  await action();
  const endTime = await page.evaluate(() => performance.now());
  return endTime - startTime;
}

export async function measureMemoryUsage(page: Page): Promise<{ used: number; total: number }> {
  return await page.evaluate(() => {
    const memory = (performance as any).memory;
    return {
      used: memory?.usedJSHeapSize || 0,
      total: memory?.totalJSHeapSize || 0,
    };
  });
}

export async function measureNetworkRequests(page: Page, action: () => Promise<void>): Promise<number> {
  const requests: string[] = [];

  page.on('request', request => {
    requests.push(request.url());
  });

  await action();

  return requests.length;
}

// Accessibility testing helpers
export async function checkBasicAccessibility(page: Page): Promise<void> {
  // Check for basic accessibility requirements
  await expect(page.locator('main, [role="main"]')).toBeVisible();

  // Check for skip links
  const skipLinks = await page.locator('a[href^="#"]').count();
  expect(skipLinks).toBeGreaterThan(0);

  // Check for proper heading hierarchy
  const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
  expect(headings.length).toBeGreaterThan(0);
}

export async function testKeyboardNavigation(page: Page, elements: string[]): Promise<void> {
  for (let i = 0; i < elements.length; i++) {
    const element = page.locator(elements[i]);
    await element.focus();
    await expect(element).toBeFocused();

    if (i < elements.length - 1) {
      await page.keyboard.press('Tab');
    }
  }
}

// Data validation helpers
export async function validateFormData(page: Page, expectedData: Record<string, any>): Promise<void> {
  for (const [field, expectedValue] of Object.entries(expectedData)) {
    const input = page.locator(`input[name="${field}"], select[name="${field}"], textarea[name="${field}"]`);
    await expect(input).toHaveValue(expectedValue.toString());
  }
}

export async function validateApiResponse(page: Page, urlPattern: string, expectedFields: string[]): Promise<void> {
  const response = await page.waitForResponse(urlPattern);
  const data = await response.json();

  for (const field of expectedFields) {
    expect(data).toHaveProperty(field);
  }
}

// Browser storage helpers
export async function setLocalStorageItem(page: Page, key: string, value: any): Promise<void> {
  await page.evaluate(({ key, value }) => {
    localStorage.setItem(key, JSON.stringify(value));
  }, { key, value });
}

export async function getLocalStorageItem(page: Page, key: string): Promise<any> {
  return await page.evaluate((key) => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  }, key);
}

export async function clearBrowserStorage(page: Page): Promise<void> {
  await clearLocalStorage(page);
  await clearSessionStorage(page);
  await clearCookies(page);
}

// Test environment helpers
export async function setupTestEnvironment(page: Page): Promise<void> {
  // Set up common test environment
  await page.addInitScript(() => {
    // Disable animations for faster testing
    const style = document.createElement('style');
    style.textContent = `
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-delay: 0.01ms !important;
        transition-duration: 0.01ms !important;
        transition-delay: 0.01ms !important;
      }
    `;
    document.head.appendChild(style);

    // Mock console methods to reduce noise
    console.debug = () => {};
    console.info = () => {};
  });
}

export async function teardownTestEnvironment(page: Page): Promise<void> {
  // Clean up test environment
  await clearBrowserStorage(page);
  await page.unrouteAll();
}

export async function logNetworkActivity(page: Page) {
  page.on('request', request => {
    console.log('Request:', request.method(), request.url());
  });

  page.on('response', response => {
    console.log('Response:', response.status(), response.url());
  });
}
