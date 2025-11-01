import { Page, Locator, expect } from '@playwright/test';

/**
 * Base Page Object Model for common functionality
 */
export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Common navigation methods
  async goto(path: string = '/') {
    await this.page.goto(path);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  // Common element interactions
  async clickElement(selector: string) {
    await this.page.click(selector);
  }

  async fillInput(selector: string, value: string) {
    await this.page.fill(selector, value);
  }

  async selectOption(selector: string, value: string) {
    await this.page.selectOption(selector, value);
  }

  // Common assertions
  async expectElementVisible(selector: string) {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  async expectElementHidden(selector: string) {
    await expect(this.page.locator(selector)).toBeHidden();
  }

  async expectElementText(selector: string, text: string) {
    await expect(this.page.locator(selector)).toHaveText(text);
  }

  async expectElementContainsText(selector: string, text: string) {
    await expect(this.page.locator(selector)).toContainText(text);
  }

  // Common wait methods
  async waitForElement(selector: string, timeout: number = 5000) {
    await this.page.waitForSelector(selector, { timeout });
  }

  async waitForElementToDisappear(selector: string, timeout: number = 5000) {
    await this.page.waitForSelector(selector, { state: 'hidden', timeout });
  }

  // Form helpers
  async submitForm(formSelector: string = 'form') {
    await this.page.locator(formSelector).press('Enter');
  }

  async clearAndFill(selector: string, value: string) {
    await this.page.locator(selector).clear();
    await this.page.locator(selector).fill(value);
  }

  // Loading states
  async waitForLoadingToComplete() {
    // Wait for any loading spinners to disappear
    await this.page.waitForSelector('.spinner', { state: 'hidden', timeout: 10000 }).catch(() => {});
    await this.page.waitForSelector('[data-testid="loading"]', { state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  // Error handling
  async expectNoErrors() {
    const errorElements = await this.page.locator('.error, [data-testid="error"]').count();
    expect(errorElements).toBe(0);
  }

  async getErrorMessage(): Promise<string | null> {
    const errorElement = this.page.locator('.error, [data-testid="error"]').first();
    if (await errorElement.count() > 0) {
      return await errorElement.textContent();
    }
    return null;
  }

  // Accessibility helpers
  async checkAccessibility() {
    // Check for basic accessibility requirements
    await this.expectElementVisible('main, [role="main"]');

    // Check for skip links
    const skipLinks = await this.page.locator('a[href^="#"]').count();
    expect(skipLinks).toBeGreaterThan(0);
  }

  async navigateWithKeyboard(key: string) {
    await this.page.keyboard.press(key);
  }

  // Screenshot helpers
  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png` });
  }

  // Mobile helpers
  async setMobileViewport() {
    await this.page.setViewportSize({ width: 375, height: 667 });
  }

  async setDesktopViewport() {
    await this.page.setViewportSize({ width: 1280, height: 720 });
  }

  // Common UI patterns
  async openModal(triggerSelector: string, modalSelector: string) {
    await this.clickElement(triggerSelector);
    await this.waitForElement(modalSelector);
  }

  async closeModal(closeSelector: string = '[data-testid="modal-close"], .modal-close') {
    await this.clickElement(closeSelector);
  }

  async selectTab(tabSelector: string) {
    await this.clickElement(tabSelector);
    await this.page.waitForTimeout(100); // Brief wait for tab content to load
  }

  // Network helpers
  async waitForApiCall(urlPattern: string | RegExp) {
    await this.page.waitForResponse(urlPattern);
  }

  async mockApiResponse(urlPattern: string | RegExp, response: any) {
    await this.page.route(urlPattern, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }

  // Local storage helpers
  async setLocalStorage(key: string, value: string) {
    await this.page.evaluate(([key, value]) => {
      localStorage.setItem(key, value);
    }, [key, value]);
  }

  async getLocalStorage(key: string): Promise<string | null> {
    return await this.page.evaluate((key) => {
      return localStorage.getItem(key);
    }, key);
  }

  async clearLocalStorage() {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
  }
}
