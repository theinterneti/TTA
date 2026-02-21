// Logseq: [[TTA.dev/Tests/E2e-staging/Page-objects/Basepage]]
/**
 * Base Page Object for Staging E2E Tests
 *
 * Provides common functionality for all page objects including
 * navigation, waiting, and element interaction helpers.
 */

import { Page, Locator, expect } from '@playwright/test';
import { STAGING_CONFIG } from '../helpers/staging-config';
import { waitForNetworkIdle } from '../helpers/test-helpers';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to a specific path
   */
  async goto(path: string = '/'): Promise<void> {
    await this.page.goto(path);
    await waitForNetworkIdle(this.page);
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get element by selector
   */
  getElement(selector: string): Locator {
    return this.page.locator(selector).first();
  }

  /**
   * Get elements by selector
   */
  getElements(selector: string): Locator {
    return this.page.locator(selector);
  }

  /**
   * Click element
   */
  async clickElement(selector: string, timeout?: number): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toBeVisible({ timeout: timeout || STAGING_CONFIG.timeouts.medium });
    await element.click();
  }

  /**
   * Fill input field
   */
  async fillInput(selector: string, value: string, timeout?: number): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toBeVisible({ timeout: timeout || STAGING_CONFIG.timeouts.medium });
    await element.fill(value);
  }

  /**
   * Select option from dropdown
   */
  async selectOption(selector: string, value: string): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toBeVisible();
    await element.selectOption(value);
  }

  /**
   * Check if element is visible
   */
  async isVisible(selector: string, timeout: number = 2000): Promise<boolean> {
    try {
      const element = this.getElement(selector);
      return await element.isVisible({ timeout });
    } catch {
      return false;
    }
  }

  /**
   * Wait for element to be visible
   */
  async waitForElement(selector: string, timeout?: number): Promise<void> {
    await this.page.waitForSelector(selector, {
      state: 'visible',
      timeout: timeout || STAGING_CONFIG.timeouts.medium,
    });
  }

  /**
   * Wait for element to be hidden
   */
  async waitForElementHidden(selector: string, timeout?: number): Promise<void> {
    await this.page.waitForSelector(selector, {
      state: 'hidden',
      timeout: timeout || STAGING_CONFIG.timeouts.medium,
    });
  }

  /**
   * Get text content of element
   */
  async getTextContent(selector: string): Promise<string | null> {
    const element = this.getElement(selector);
    return await element.textContent();
  }

  /**
   * Get all text contents
   */
  async getAllTextContents(selector: string): Promise<string[]> {
    const elements = this.getElements(selector);
    return await elements.allTextContents();
  }

  /**
   * Check if element exists
   */
  async elementExists(selector: string): Promise<boolean> {
    const count = await this.getElements(selector).count();
    return count > 0;
  }

  /**
   * Wait for URL to match pattern
   */
  async waitForUrl(pattern: string | RegExp, timeout?: number): Promise<void> {
    await this.page.waitForURL(pattern, {
      timeout: timeout || STAGING_CONFIG.timeouts.long,
    });
  }

  /**
   * Get current URL
   */
  getCurrentUrl(): string {
    return this.page.url();
  }

  /**
   * Get current path
   */
  getCurrentPath(): string {
    const url = new URL(this.page.url());
    return url.pathname;
  }

  /**
   * Reload page
   */
  async reload(): Promise<void> {
    await this.page.reload();
    await waitForNetworkIdle(this.page);
  }

  /**
   * Go back
   */
  async goBack(): Promise<void> {
    await this.page.goBack();
    await waitForNetworkIdle(this.page);
  }

  /**
   * Take screenshot
   */
  async takeScreenshot(name: string, fullPage: boolean = false): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({
      path: `test-results-staging/screenshots/${name}-${timestamp}.png`,
      fullPage,
    });
  }

  /**
   * Wait for API response
   */
  async waitForApiResponse(urlPattern: string | RegExp, timeout?: number): Promise<any> {
    const response = await this.page.waitForResponse(
      (response) => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout: timeout || STAGING_CONFIG.timeouts.medium }
    );

    return response.json();
  }

  /**
   * Check for console errors
   */
  async getConsoleErrors(): Promise<string[]> {
    const errors: string[] = [];

    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    return errors;
  }

  /**
   * Clear browser storage
   */
  async clearStorage(): Promise<void> {
    await this.page.evaluate(() => {
      sessionStorage.clear();
      localStorage.clear();
    });
  }

  /**
   * Expect element to be visible
   */
  async expectVisible(selector: string, timeout?: number): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toBeVisible({ timeout: timeout || STAGING_CONFIG.timeouts.medium });
  }

  /**
   * Expect element to be hidden
   */
  async expectHidden(selector: string): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toBeHidden();
  }

  /**
   * Expect element to have text
   */
  async expectText(selector: string, text: string | RegExp): Promise<void> {
    const element = this.getElement(selector);
    await expect(element).toContainText(text);
  }

  /**
   * Expect page title
   */
  async expectTitle(title: string | RegExp): Promise<void> {
    await expect(this.page).toHaveTitle(title);
  }

  /**
   * Expect URL to match
   */
  async expectUrl(pattern: string | RegExp): Promise<void> {
    await expect(this.page).toHaveURL(pattern);
  }
}
