/**
 * World Selection Page Object
 *
 * Handles interactions with the world selection interface where players
 * choose which world/scenario to play in.
 */

import { expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { STAGING_CONFIG } from '../helpers/staging-config';

export class WorldSelectionPage extends BasePage {
  // Selectors
  private readonly worldContainer = '[data-testid="world-selection"], .world-selection';
  private readonly worldCard = '[data-testid="world-card"], .world-card';
  private readonly worldTitle = '[data-testid="world-title"], .world-title';
  private readonly worldDescription = '[data-testid="world-description"], .world-description';
  private readonly selectButton = 'button:has-text("Select"), button:has-text("Play in World")';
  private readonly worldList = '[data-testid="world-list"], .world-list';
  private readonly loadingSpinner = '[data-testid="loading"], .loading, .spinner';
  private readonly errorMessage = '[data-testid="error-message"], .error-message';
  private readonly filterButton = 'button:has-text("Filter"), button[aria-label="Filter"]';
  private readonly searchInput = 'input[type="search"], input[placeholder*="Search"]';
  private readonly backButton = 'button:has-text("Back"), button[aria-label="Back"]';

  /**
   * Navigate to world selection page
   */
  async goto(): Promise<void> {
    await this.page.goto('/worlds');
    await this.waitForPageLoad();
    await this.expectWorldsLoaded();
  }

  /**
   * Expect worlds to be loaded
   */
  async expectWorldsLoaded(): Promise<void> {
    await this.expectVisible(this.worldContainer);
    // Wait for at least one world card to appear
    await this.page.waitForSelector(this.worldCard, { state: 'visible' });
  }

  /**
   * Get number of available worlds
   */
  async getWorldCount(): Promise<number> {
    return await this.getElements(this.worldCard).count();
  }

  /**
   * Get world titles
   */
  async getWorldTitles(): Promise<string[]> {
    return await this.getAllTextContents(`${this.worldCard} ${this.worldTitle}`);
  }

  /**
   * Select world by index
   */
  async selectWorldByIndex(index: number): Promise<void> {
    const cards = this.getElements(this.worldCard);
    const card = cards.nth(index);

    // Scroll into view if needed
    await card.scrollIntoViewIfNeeded();

    // Click select button within the card
    const selectBtn = card.locator(this.selectButton).first();
    await selectBtn.click();

    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Select world by name
   */
  async selectWorldByName(worldName: string): Promise<void> {
    const cards = this.getElements(this.worldCard);
    const count = await cards.count();

    for (let i = 0; i < count; i++) {
      const card = cards.nth(i);
      const title = await card.locator(this.worldTitle).first().textContent();

      if (title?.includes(worldName)) {
        await this.selectWorldByIndex(i);
        return;
      }
    }

    throw new Error(`World "${worldName}" not found`);
  }

  /**
   * Select first available world
   */
  async selectFirstWorld(): Promise<void> {
    await this.selectWorldByIndex(0);
  }

  /**
   * Get world description by index
   */
  async getWorldDescription(index: number): Promise<string | null> {
    const cards = this.getElements(this.worldCard);
    const card = cards.nth(index);
    return await card.locator(this.worldDescription).first().textContent();
  }

  /**
   * Search for world
   */
  async searchWorld(query: string): Promise<void> {
    if (await this.isVisible(this.searchInput)) {
      await this.fillInput(this.searchInput, query);
      await this.page.waitForLoadState('networkidle');
    }
  }

  /**
   * Filter worlds
   */
  async openFilter(): Promise<void> {
    if (await this.isVisible(this.filterButton)) {
      await this.clickElement(this.filterButton);
    }
  }

  /**
   * Go back to previous page
   */
  async goBackToPrevious(): Promise<void> {
    await this.clickElement(this.backButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Expect error message
   */
  async expectErrorMessage(): Promise<void> {
    await this.expectVisible(this.errorMessage);
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string | null> {
    return await this.getTextContent(this.errorMessage);
  }

  /**
   * Verify worlds are displayed
   */
  async expectWorldsDisplayed(): Promise<void> {
    const count = await this.getWorldCount();
    expect(count).toBeGreaterThan(0);
  }

  /**
   * Verify world card has required information
   */
  async expectWorldCardComplete(index: number): Promise<void> {
    const cards = this.getElements(this.worldCard);
    const card = cards.nth(index);

    const title = await card.locator(this.worldTitle).first();
    const description = await card.locator(this.worldDescription).first();
    const selectBtn = await card.locator(this.selectButton).first();

    await expect(title).toBeVisible();
    await expect(description).toBeVisible();
    await expect(selectBtn).toBeVisible();
  }

  /**
   * Wait for worlds to load with timeout
   */
  async waitForWorldsToLoad(timeout: number = STAGING_CONFIG.timeouts.long): Promise<void> {
    await this.page.waitForSelector(this.worldCard, { state: 'visible', timeout });
  }
}
