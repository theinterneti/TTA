// Logseq: [[TTA.dev/Tests/E2e/Page-objects/Dashboardpage]]
import { Locator, Page, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Dashboard Page
 */
export class DashboardPage extends BasePage {
  // Locators
  readonly pageTitle: Locator;
  readonly welcomeMessage: Locator;
  readonly quickActionsSection: Locator;
  readonly charactersSection: Locator;
  readonly recentSessionsSection: Locator;
  readonly progressSection: Locator;
  readonly createCharacterButton: Locator;
  readonly manageCharactersButton: Locator;
  readonly exploreWorldsButton: Locator;
  readonly continueSessionButton: Locator;
  readonly characterCards: Locator;
  readonly sessionCards: Locator;
  readonly progressChart: Locator;
  readonly notificationsPanel: Locator;
  readonly settingsLink: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);

    // Initialize locators - using test identifiers added in Priority 1
    this.pageTitle = page.locator('[data-testid="dashboard-welcome-title"]');
    this.welcomeMessage = page.locator('[data-testid="dashboard-welcome-message"]');
    this.quickActionsSection = page.locator('[data-testid="dashboard-quick-actions"]');
    this.charactersSection = page.locator('[data-testid="dashboard-stat-characters"]');
    this.recentSessionsSection = page.locator('[data-testid="dashboard-recent-sessions"]');
    this.progressSection = page.locator('[data-testid="dashboard-stat-progress"]');

    // Action buttons - using test identifiers added in Priority 1
    // Note: createCharacterButton and manageCharactersButton use the same element (text changes based on state)
    this.createCharacterButton = page.locator('[data-testid="dashboard-manage-characters-button"]');
    this.manageCharactersButton = page.locator('[data-testid="dashboard-manage-characters-button"]');
    this.exploreWorldsButton = page.locator('[data-testid="dashboard-explore-worlds-button"]');
    this.continueSessionButton = page.locator('[data-testid="dashboard-continue-session-button"]');

    // Content elements
    this.characterCards = page.locator('[data-testid="character-card"], .character-card');
    this.sessionCards = page.locator('[data-testid="session-card"], .session-card');
    this.progressChart = page.locator('[data-testid="progress-chart"], .progress-chart');
    this.notificationsPanel = page.locator('[data-testid="notifications"], .notifications');

    // Navigation elements
    this.settingsLink = page.locator('a[href*="settings"], [data-testid="settings-link"]');
    this.logoutButton = page.locator('button, a').filter({ hasText: /logout|sign out/i });
  }

  // Navigation
  async goto() {
    await super.goto('/dashboard');
    await this.waitForPageLoad();
  }

  // Actions
  async createNewCharacter() {
    await this.createCharacterButton.click();
    await this.page.waitForURL(/characters/);
  }

  async manageCharacters() {
    await this.manageCharactersButton.click();
    await this.page.waitForURL(/characters/);
  }

  async exploreWorlds() {
    await this.exploreWorldsButton.click();
    await this.page.waitForURL(/worlds/);
  }

  async continueLastSession() {
    await this.continueSessionButton.click();
    await this.page.waitForURL(/chat/);
  }

  async selectCharacter(characterName: string) {
    const characterCard = this.characterCards.filter({ hasText: characterName });
    await characterCard.click();
  }

  async selectRecentSession(sessionName: string) {
    const sessionCard = this.sessionCards.filter({ hasText: sessionName });
    await sessionCard.click();
  }

  async goToSettings() {
    await this.settingsLink.click();
    await this.page.waitForURL(/settings/);
  }

  async logout() {
    await this.logoutButton.click();
    await this.page.waitForURL(/login|auth/);
  }

  // Validations
  async expectDashboardLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.quickActionsSection).toBeVisible();
    await this.waitForLoadingToComplete();
  }

  async expectWelcomeMessage(username?: string) {
    await expect(this.welcomeMessage).toBeVisible();
    if (username) {
      await expect(this.welcomeMessage).toContainText(username);
    }
  }

  async expectQuickActionsVisible() {
    await expect(this.quickActionsSection).toBeVisible();
    await expect(this.createCharacterButton).toBeVisible();
    await expect(this.exploreWorldsButton).toBeVisible();
  }

  async expectCharactersSection(hasCharacters: boolean = true) {
    await expect(this.charactersSection).toBeVisible();

    if (hasCharacters) {
      await expect(this.characterCards.first()).toBeVisible();
    } else {
      // Should show empty state or create character prompt
      const emptyState = this.page.locator('[data-testid="no-characters"], .empty-state');
      await expect(emptyState).toBeVisible();
    }
  }

  async expectRecentSessions(hasSessions: boolean = true) {
    await expect(this.recentSessionsSection).toBeVisible();

    if (hasSessions) {
      await expect(this.sessionCards.first()).toBeVisible();
    } else {
      const emptyState = this.page.locator('[data-testid="no-sessions"], .empty-sessions');
      await expect(emptyState).toBeVisible();
    }
  }

  async expectProgressSection() {
    await expect(this.progressSection).toBeVisible();
    // Progress chart might be optional depending on user data
  }

  async expectCharacterCount(count: number) {
    await expect(this.characterCards).toHaveCount(count);
  }

  async expectSessionCount(count: number) {
    await expect(this.sessionCards).toHaveCount(count);
  }

  // New user experience
  async expectNewUserExperience() {
    // Should show onboarding or getting started content
    const gettingStarted = this.page.locator('[data-testid="getting-started"], .getting-started');
    await expect(gettingStarted).toBeVisible();

    // Should emphasize character creation
    await expect(this.createCharacterButton).toBeVisible();
    await expect(this.createCharacterButton).toContainText(/create.*first|get started/i);
  }

  // Returning user experience
  async expectReturningUserExperience() {
    // Should show recent activity
    await this.expectCharactersSection(true);
    await this.expectRecentSessions(true);

    // Continue session button should be enabled
    await expect(this.continueSessionButton).toBeEnabled();
  }

  // Accessibility tests
  async checkAccessibility() {
    await super.checkAccessibility();

    // Check heading hierarchy
    const headings = this.page.locator('h1, h2, h3, h4, h5, h6');
    await expect(headings.first()).toHaveRole('heading');

    // Check button accessibility
    await expect(this.createCharacterButton).toHaveRole('button');
    await expect(this.exploreWorldsButton).toHaveRole('button');

    // Check link accessibility
    await expect(this.settingsLink).toHaveRole('link');
  }

  // Keyboard navigation
  async navigateWithKeyboard() {
    // Test tab navigation through quick actions
    await this.createCharacterButton.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.exploreWorldsButton).toBeFocused();

    await this.page.keyboard.press('Tab');
    await expect(this.continueSessionButton).toBeFocused();

    // Test Enter key activation
    await this.createCharacterButton.focus();
    await this.page.keyboard.press('Enter');
    await this.page.waitForURL(/characters/);
  }

  // Mobile responsiveness
  async checkMobileLayout() {
    await this.setMobileViewport();
    await this.expectDashboardLoaded();

    // Check that sections stack vertically on mobile
    const quickActionsBox = await this.quickActionsSection.boundingBox();
    const charactersBox = await this.charactersSection.boundingBox();

    if (quickActionsBox && charactersBox) {
      expect(charactersBox.y).toBeGreaterThan(quickActionsBox.y + quickActionsBox.height);
    }
  }

  // Performance tests
  async measureDashboardLoadTime() {
    const startTime = Date.now();
    await this.goto();
    await this.expectDashboardLoaded();
    const endTime = Date.now();

    const loadTime = endTime - startTime;
    expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds

    return loadTime;
  }

  // Data refresh
  async refreshDashboard() {
    await this.page.reload();
    await this.expectDashboardLoaded();
  }

  async expectDataRefresh() {
    // Check that data is updated (timestamps, counts, etc.)
    const timestamp = this.page.locator('[data-testid="last-updated"], .last-updated');
    if (await timestamp.count() > 0) {
      await expect(timestamp).toBeVisible();
    }
  }
}
