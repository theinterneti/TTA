import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for World Selection Page
 */
export class WorldSelectionPage extends BasePage {
  // Locators
  readonly pageTitle: Locator;
  readonly worldsGrid: Locator;
  readonly searchInput: Locator;
  readonly difficultyFilter: Locator;
  readonly themeFilter: Locator;
  readonly durationFilter: Locator;
  readonly sortFilter: Locator;
  readonly clearFiltersButton: Locator;
  readonly worldCards: Locator;
  readonly noWorldsMessage: Locator;
  readonly characterNoticeMessage: Locator;
  readonly loadingSpinner: Locator;
  readonly worldDetailsModal: Locator;
  readonly worldCustomizationModal: Locator;

  constructor(page: Page) {
    super(page);
    this.pageTitle = page.locator('h1:has-text("World Selection")');
    this.worldsGrid = page.locator('.grid');
    this.searchInput = page.locator('input[placeholder*="Search worlds"]');
    this.difficultyFilter = page.locator('select').nth(0);
    this.themeFilter = page.locator('select').nth(1);
    this.durationFilter = page.locator('select').nth(2);
    this.sortFilter = page.locator('select').nth(3);
    this.clearFiltersButton = page.locator('button:has-text("Clear all filters")');
    this.worldCards = page.locator('.card');
    this.noWorldsMessage = page.locator('text=No worlds');
    this.characterNoticeMessage = page.locator('text=Please select a character first');
    this.loadingSpinner = page.locator('.spinner');
    this.worldDetailsModal = page.locator('[data-testid="world-details-modal"]');
    this.worldCustomizationModal = page.locator('[data-testid="world-customization-modal"]');
  }

  async goto() {
    await this.page.goto('/worlds');
    await this.waitForPageLoad();
  }

  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.page.locator('text=Choose therapeutic environments')).toBeVisible();
  }

  async expectWorldsDisplayed() {
    await expect(this.worldCards.first()).toBeVisible();
  }

  async expectNoWorldsMessage() {
    await expect(this.noWorldsMessage).toBeVisible();
  }

  async expectCharacterNotice() {
    await expect(this.characterNoticeMessage).toBeVisible();
  }

  async expectLoadingState() {
    await expect(this.loadingSpinner).toBeVisible();
  }

  async searchWorlds(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.waitForTimeout(500); // Wait for search debounce
  }

  async filterByDifficulty(difficulty: string) {
    await this.difficultyFilter.selectOption(difficulty);
    await this.page.waitForTimeout(300);
  }

  async filterByTheme(theme: string) {
    await this.themeFilter.selectOption(theme);
    await this.page.waitForTimeout(300);
  }

  async filterByDuration(duration: string) {
    await this.durationFilter.selectOption(duration);
    await this.page.waitForTimeout(300);
  }

  async sortBy(sortOption: string) {
    await this.sortFilter.selectOption(sortOption);
    await this.page.waitForTimeout(300);
  }

  async clearAllFilters() {
    await this.clearFiltersButton.click();
    await this.page.waitForTimeout(300);
  }

  async getWorldCount(): Promise<number> {
    return await this.worldCards.count();
  }

  async getWorldByName(name: string): Promise<Locator> {
    return this.page.locator(`.card:has-text("${name}")`);
  }

  async clickViewDetails(worldName: string) {
    const worldCard = await this.getWorldByName(worldName);
    await worldCard.locator('button:has-text("View Details")').click();
  }

  async clickCustomizeWorld(worldName: string) {
    const worldCard = await this.getWorldByName(worldName);
    await worldCard.locator('button:has-text("Customize")').click();
  }

  async clickSelectWorld(worldName: string) {
    const worldCard = await this.getWorldByName(worldName);
    await worldCard.locator('button:has-text("Select World")').click();
  }

  async expectWorldDetailsModal() {
    await expect(this.worldDetailsModal).toBeVisible();
  }

  async expectWorldCustomizationModal() {
    await expect(this.worldCustomizationModal).toBeVisible();
  }

  async closeModal() {
    await this.page.locator('[data-testid="modal-close"], .modal-close').first().click();
  }

  async expectWorldCompatibilityScore(worldName: string, expectedScore: number) {
    const worldCard = await this.getWorldByName(worldName);
    const scoreText = await worldCard.locator('text=/\\d+% match/').textContent();
    const actualScore = parseInt(scoreText?.match(/(\d+)%/)?.[1] || '0');
    expect(actualScore).toBe(expectedScore);
  }

  async expectWorldThemes(worldName: string, expectedThemes: string[]) {
    const worldCard = await this.getWorldByName(worldName);
    for (const theme of expectedThemes) {
      await expect(worldCard.locator(`text=${theme}`)).toBeVisible();
    }
  }

  async expectWorldDifficulty(worldName: string, expectedDifficulty: string) {
    const worldCard = await this.getWorldByName(worldName);
    await expect(worldCard.locator(`text=${expectedDifficulty}`)).toBeVisible();
  }

  async expectWorldDuration(worldName: string, expectedDuration: string) {
    const worldCard = await this.getWorldByName(worldName);
    await expect(worldCard.locator(`text=${expectedDuration}`)).toBeVisible();
  }

  // Accessibility testing
  async testKeyboardNavigation() {
    await this.searchInput.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.difficultyFilter).toBeFocused();
    
    await this.page.keyboard.press('Tab');
    await expect(this.themeFilter).toBeFocused();
    
    await this.page.keyboard.press('Tab');
    await expect(this.durationFilter).toBeFocused();
  }

  async testScreenReaderSupport() {
    // Check for proper ARIA labels and roles
    await expect(this.searchInput).toHaveAttribute('aria-label');
    await expect(this.difficultyFilter).toHaveAttribute('aria-label');
    await expect(this.worldsGrid).toHaveAttribute('role', 'grid');
  }

  // Performance testing
  async measureSearchPerformance(searchTerm: string): Promise<number> {
    const startTime = Date.now();
    await this.searchWorlds(searchTerm);
    await this.expectWorldsDisplayed();
    return Date.now() - startTime;
  }

  async measureFilterPerformance(filterType: 'difficulty' | 'theme' | 'duration', value: string): Promise<number> {
    const startTime = Date.now();
    
    switch (filterType) {
      case 'difficulty':
        await this.filterByDifficulty(value);
        break;
      case 'theme':
        await this.filterByTheme(value);
        break;
      case 'duration':
        await this.filterByDuration(value);
        break;
    }
    
    await this.page.waitForLoadState('networkidle');
    return Date.now() - startTime;
  }

  // Error handling
  async expectErrorMessage(message: string) {
    await expect(this.page.locator(`text=${message}`)).toBeVisible();
  }

  async expectNetworkError() {
    await expect(this.page.locator('text=Failed to load worlds')).toBeVisible();
  }

  // Mobile responsive testing
  async testMobileLayout() {
    await this.setMobileViewport();
    await this.expectPageLoaded();
    
    // Check that grid becomes single column on mobile
    const gridClasses = await this.worldsGrid.getAttribute('class');
    expect(gridClasses).toContain('grid-cols-1');
  }

  async testTabletLayout() {
    await this.page.setViewportSize({ width: 768, height: 1024 });
    await this.expectPageLoaded();
    
    // Check that grid becomes two columns on tablet
    const gridClasses = await this.worldsGrid.getAttribute('class');
    expect(gridClasses).toContain('md:grid-cols-2');
  }

  // Data validation
  async validateWorldCardData(worldName: string) {
    const worldCard = await this.getWorldByName(worldName);
    
    // Check required elements are present
    await expect(worldCard.locator('h3')).toBeVisible(); // World name
    await expect(worldCard.locator('p')).toBeVisible(); // Description
    await expect(worldCard.locator('button:has-text("View Details")')).toBeVisible();
    await expect(worldCard.locator('button:has-text("Select World")')).toBeVisible();
  }
}
