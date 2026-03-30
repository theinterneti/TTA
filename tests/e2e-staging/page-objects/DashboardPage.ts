// Logseq: [[TTA.dev/Tests/E2e-staging/Page-objects/Dashboardpage]]
/**
 * Dashboard Page Object for Staging E2E Tests
 *
 * Handles dashboard navigation and user orientation
 */

import { Page, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  // Selectors
  private readonly selectors = {
    pageHeading: 'h1, h2',
    welcomeMessage: '[data-testid="welcome-message"], .welcome',
    createCharacterButton: '[data-testid="dashboard-manage-characters-button"], button:has-text("Create Character"), button:has-text("Manage Characters")',
    selectWorldButton: 'button:has-text("Select World"), button:has-text("Choose World"), a:has-text("Worlds")',
    continueStoryButton: 'button:has-text("Continue"), button:has-text("Resume")',
    recentSessions: '[data-testid="recent-sessions"], .recent-sessions',
    characterList: '[data-testid="character-list"], .character-list',
    navigationMenu: 'nav, [data-testid="navigation"]',
    userProfile: '[data-testid="user-profile"], .user-profile',
    logoutButton: 'button:has-text("Logout"), button:has-text("Sign Out")',
  };

  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to dashboard
   */
  async goto(): Promise<void> {
    await super.goto('/dashboard');
  }

  /**
   * Check if dashboard is loaded
   */
  async isLoaded(): Promise<boolean> {
    return await this.isVisible(this.selectors.pageHeading);
  }

  /**
   * Get welcome message
   */
  async getWelcomeMessage(): Promise<string | null> {
    if (await this.isVisible(this.selectors.welcomeMessage)) {
      return await this.getTextContent(this.selectors.welcomeMessage);
    }
    return null;
  }

  /**
   * Click create character button
   */
  async clickCreateCharacter(): Promise<void> {
    await this.clickElement(this.selectors.createCharacterButton);
  }

  /**
   * Click select world button
   */
  async clickSelectWorld(): Promise<void> {
    await this.clickElement(this.selectors.selectWorldButton);
  }

  /**
   * Click continue story button
   */
  async clickContinueStory(): Promise<void> {
    await this.clickElement(this.selectors.continueStoryButton);
  }

  /**
   * Check if create character button is visible
   */
  async hasCreateCharacterButton(): Promise<boolean> {
    return await this.isVisible(this.selectors.createCharacterButton);
  }

  /**
   * Check if select world button is visible
   */
  async hasSelectWorldButton(): Promise<boolean> {
    return await this.isVisible(this.selectors.selectWorldButton);
  }

  /**
   * Check if continue story button is visible
   */
  async hasContinueStoryButton(): Promise<boolean> {
    return await this.isVisible(this.selectors.continueStoryButton);
  }

  /**
   * Get recent sessions count
   */
  async getRecentSessionsCount(): Promise<number> {
    if (await this.isVisible(this.selectors.recentSessions)) {
      const sessions = this.getElements(`${this.selectors.recentSessions} > *`);
      return await sessions.count();
    }
    return 0;
  }

  /**
   * Get character count
   */
  async getCharacterCount(): Promise<number> {
    if (await this.isVisible(this.selectors.characterList)) {
      const characters = this.getElements(`${this.selectors.characterList} > *`);
      return await characters.count();
    }
    return 0;
  }

  /**
   * Navigate to characters page
   */
  async navigateToCharacters(): Promise<void> {
    const link = this.page.locator('a:has-text("Characters"), nav a[href*="character"]').first();
    await link.click();
    await this.waitForPageLoad();
  }

  /**
   * Navigate to worlds page
   */
  async navigateToWorlds(): Promise<void> {
    const link = this.page.locator('a:has-text("Worlds"), nav a[href*="world"]').first();
    await link.click();
    await this.waitForPageLoad();
  }

  /**
   * Navigate to settings page
   */
  async navigateToSettings(): Promise<void> {
    const link = this.page.locator('a:has-text("Settings"), nav a[href*="setting"]').first();
    await link.click();
    await this.waitForPageLoad();
  }

  /**
   * Navigate to preferences page
   */
  async navigateToPreferences(): Promise<void> {
    const link = this.page.locator('a:has-text("Preferences"), nav a[href*="preference"]').first();
    await link.click();
    await this.waitForPageLoad();
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    if (await this.isVisible(this.selectors.logoutButton)) {
      await this.clickElement(this.selectors.logoutButton);
      await this.waitForUrl(/login/i);
    }
  }

  /**
   * Check if navigation menu is visible
   */
  async hasNavigationMenu(): Promise<boolean> {
    return await this.isVisible(this.selectors.navigationMenu);
  }

  /**
   * Check if user profile is visible
   */
  async hasUserProfile(): Promise<boolean> {
    return await this.isVisible(this.selectors.userProfile);
  }

  /**
   * Expect dashboard to be loaded
   * Accepts "Adventure Platform" (intentional branding) or traditional dashboard headings
   */
  async expectDashboardLoaded(): Promise<void> {
    await this.expectVisible(this.selectors.pageHeading);
    await this.expectText(this.selectors.pageHeading, /adventure platform|dashboard|welcome|home/i);
  }

  /**
   * Expect clear call to action
   */
  async expectClearCallToAction(): Promise<void> {
    const hasCreateButton = await this.hasCreateCharacterButton();
    const hasWorldButton = await this.hasSelectWorldButton();
    const hasContinueButton = await this.hasContinueStoryButton();

    expect(hasCreateButton || hasWorldButton || hasContinueButton).toBeTruthy();
  }

  /**
   * Expect navigation menu
   */
  async expectNavigationMenu(): Promise<void> {
    await this.expectVisible(this.selectors.navigationMenu);
  }

  /**
   * Get page heading text
   */
  async getPageHeading(): Promise<string | null> {
    return await this.getTextContent(this.selectors.pageHeading);
  }
}
