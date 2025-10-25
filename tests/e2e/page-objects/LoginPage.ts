import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { TestUser } from '../fixtures/test-data';

/**
 * Page Object Model for Login Page
 */
export class LoginPage extends BasePage {
  // Locators
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  readonly loadingSpinner: Locator;
  readonly forgotPasswordLink: Locator;
  readonly signUpLink: Locator;
  readonly loginForm: Locator;
  readonly welcomeTitle: Locator;
  readonly logoIcon: Locator;

  constructor(page: Page) {
    super(page);

    // Initialize locators
    this.loginForm = page.locator('[data-testid="login-form"], form');
    this.usernameInput = page.locator('input[name="username"], input[id="username"]');
    this.passwordInput = page.locator('input[name="password"], input[id="password"]');
    this.loginButton = page.locator('button[type="submit"], [data-testid="login-button"]');
    this.errorMessage = page.locator('.error, [data-testid="error"], .text-red-600');
    this.loadingSpinner = page.locator('.spinner, [data-testid="loading"]');
    this.forgotPasswordLink = page.locator('a[href*="forgot"], [data-testid="forgot-password"]');
    this.signUpLink = page.locator('a[href*="signup"], [data-testid="signup-link"]');
    this.welcomeTitle = page.locator('h1, h2').filter({ hasText: /welcome|login|sign in/i });
    this.logoIcon = page.locator('svg, img').first();
  }

  // Navigation
  async goto() {
    await super.goto('/');
    await this.waitForPageLoad();
  }

  // Actions
  async login(user: TestUser) {
    await this.fillUsername(user.username);
    await this.fillPassword(user.password);
    await this.clickLogin();
  }

  async fillUsername(username: string) {
    await this.usernameInput.fill(username);
  }

  async fillPassword(password: string) {
    await this.passwordInput.fill(password);
  }

  async clickLogin() {
    await this.loginButton.click();
  }

  async clickForgotPassword() {
    await this.forgotPasswordLink.click();
  }

  async clickSignUp() {
    await this.signUpLink.click();
  }

  // Validations
  async expectLoginFormVisible() {
    await expect(this.loginForm).toBeVisible();
    await expect(this.usernameInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
    await expect(this.loginButton).toBeVisible();
  }

  async expectWelcomeMessage() {
    await expect(this.welcomeTitle).toBeVisible();
    await expect(this.welcomeTitle).toContainText(/welcome|TTA/i);
  }

  async expectErrorMessage(message?: string) {
    await expect(this.errorMessage).toBeVisible();
    if (message) {
      await expect(this.errorMessage).toContainText(message);
    }
  }

  async expectNoErrorMessage() {
    await expect(this.errorMessage).toBeHidden();
  }

  async expectLoadingState() {
    await expect(this.loadingSpinner).toBeVisible();
    await expect(this.loginButton).toBeDisabled();
  }

  async expectLoginSuccess() {
    // Should redirect away from login page
    await this.page.waitForURL(/dashboard|home/);
  }

  // Form validation tests
  async expectUsernameRequired() {
    await this.fillPassword('password');
    await this.clickLogin();
    await this.expectErrorMessage();
  }

  async expectPasswordRequired() {
    await this.fillUsername('username');
    await this.clickLogin();
    await this.expectErrorMessage();
  }

  async expectInvalidCredentials() {
    await this.login({ username: 'invalid', password: 'invalid', email: '' });
    await this.expectErrorMessage();
  }

  // Accessibility tests
  async checkAccessibility() {
    await super.checkAccessibility();

    // Check form labels
    await expect(this.usernameInput).toHaveAttribute('aria-label');
    await expect(this.passwordInput).toHaveAttribute('aria-label');

    // Check form structure
    await expect(this.loginForm).toHaveRole('form');

    // Check button accessibility
    await expect(this.loginButton).toHaveAttribute('type', 'submit');
  }

  // Keyboard navigation
  async navigateWithKeyboard() {
    await this.usernameInput.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.passwordInput).toBeFocused();

    await this.page.keyboard.press('Tab');
    await expect(this.loginButton).toBeFocused();

    // Test Enter key submission
    await this.usernameInput.focus();
    await this.fillUsername('testuser');
    await this.page.keyboard.press('Tab');
    await this.fillPassword('testpass');
    await this.page.keyboard.press('Enter');
  }

  // Mobile responsiveness
  async checkMobileLayout() {
    await this.setMobileViewport();
    await this.expectLoginFormVisible();

    // Check that form is properly sized for mobile
    const formBox = await this.loginForm.boundingBox();
    expect(formBox?.width).toBeLessThan(400);
  }

  // Security tests
  async checkPasswordMasking() {
    await this.fillPassword('secretpassword');
    await expect(this.passwordInput).toHaveAttribute('type', 'password');
  }

  async checkNoPasswordInUrl() {
    await this.login({ username: 'test', password: 'secret', email: '' });
    const url = this.page.url();
    expect(url).not.toContain('secret');
    expect(url).not.toContain('password');
  }

  // Performance tests
  async measureLoginTime() {
    const startTime = Date.now();
    await this.login({ username: 'testuser', password: 'testpass', email: '' });
    await this.expectLoginSuccess();
    const endTime = Date.now();

    const loginTime = endTime - startTime;
    expect(loginTime).toBeLessThan(5000); // Should complete within 5 seconds

    return loginTime;
  }

  // Visual tests
  async expectCorrectStyling() {
    // Check that the login form has proper styling
    await expect(this.loginForm).toHaveCSS('display', /flex|block/);

    // Check button styling
    await expect(this.loginButton).toHaveCSS('cursor', 'pointer');

    // Check input styling
    await expect(this.usernameInput).toHaveCSS('border-width', /1px|2px/);
  }
}
