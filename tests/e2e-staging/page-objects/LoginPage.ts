/**
 * Login Page Object for Staging E2E Tests
 *
 * Handles authentication flows including OAuth and demo credentials
 */

import { Page, expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { STAGING_CONFIG } from '../helpers/staging-config';

export class LoginPage extends BasePage {
  // Selectors
  private readonly selectors = {
    usernameInput: 'input[name="username"], input[id="username"]',
    passwordInput: 'input[name="password"], input[id="password"]',
    submitButton: 'button[type="submit"]',
    oauthButton: 'button:has-text("Sign in with OpenRouter"), button:has-text("OAuth")',
    errorMessage: '[data-testid="error-message"], .error-message, .alert-error',
    successMessage: '[data-testid="success-message"], .success-message',
    loginForm: 'form, [data-testid="login-form"]',
    pageTitle: 'h1, h2',
  };

  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to login page
   */
  async goto(): Promise<void> {
    await super.goto('/login');
  }

  /**
   * Check if login page is loaded
   */
  async isLoaded(): Promise<boolean> {
    return await this.isVisible(this.selectors.loginForm);
  }

  /**
   * Login with username and password
   */
  async login(username: string, password: string): Promise<void> {
    await this.expectVisible(this.selectors.usernameInput);

    await this.fillInput(this.selectors.usernameInput, username);
    await this.fillInput(this.selectors.passwordInput, password);
    await this.clickElement(this.selectors.submitButton);
  }

  /**
   * Login with demo credentials
   */
  async loginWithDemo(): Promise<void> {
    const { username, password } = STAGING_CONFIG.testUsers.demo;
    await this.login(username, password);
  }

  /**
   * Login with staging test user
   */
  async loginWithStagingUser(): Promise<void> {
    const { username, password } = STAGING_CONFIG.testUsers.staging;
    await this.login(username, password);
  }

  /**
   * Initiate OAuth flow
   */
  async initiateOAuth(): Promise<void> {
    await this.clickElement(this.selectors.oauthButton);
  }

  /**
   * Wait for successful login (redirect to dashboard)
   */
  async waitForLoginSuccess(): Promise<void> {
    await this.waitForUrl(/dashboard|home/i, STAGING_CONFIG.timeouts.long);
  }

  /**
   * Check if error message is displayed
   */
  async hasError(): Promise<boolean> {
    return await this.isVisible(this.selectors.errorMessage);
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string | null> {
    if (await this.hasError()) {
      return await this.getTextContent(this.selectors.errorMessage);
    }
    return null;
  }

  /**
   * Expect login form to be visible
   */
  async expectLoginFormVisible(): Promise<void> {
    await this.expectVisible(this.selectors.loginForm);
  }

  /**
   * Expect error message
   */
  async expectError(message?: string | RegExp): Promise<void> {
    await this.expectVisible(this.selectors.errorMessage);
    if (message) {
      await this.expectText(this.selectors.errorMessage, message);
    }
  }

  /**
   * Expect successful login
   */
  async expectLoginSuccess(): Promise<void> {
    await this.waitForLoginSuccess();
  }

  /**
   * Check if OAuth button is visible
   */
  async hasOAuthButton(): Promise<boolean> {
    return await this.isVisible(this.selectors.oauthButton);
  }

  /**
   * Clear login form
   */
  async clearForm(): Promise<void> {
    await this.fillInput(this.selectors.usernameInput, '');
    await this.fillInput(this.selectors.passwordInput, '');
  }

  /**
   * Submit empty form (for validation testing)
   */
  async submitEmptyForm(): Promise<void> {
    await this.clickElement(this.selectors.submitButton);
  }

  /**
   * Check if submit button is enabled
   */
  async isSubmitButtonEnabled(): Promise<boolean> {
    const button = this.getElement(this.selectors.submitButton);
    return await button.isEnabled();
  }

  /**
   * Get page title
   */
  async getPageTitle(): Promise<string | null> {
    return await this.getTextContent(this.selectors.pageTitle);
  }

  /**
   * Expect page title
   */
  async expectPageTitle(title: string | RegExp): Promise<void> {
    await this.expectText(this.selectors.pageTitle, title);
  }
}
