import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { TestCharacter } from '../fixtures/test-data';

/**
 * Page Object Model for Character Management Page
 */
export class CharacterManagementPage extends BasePage {
  // Locators
  readonly pageTitle: Locator;
  readonly createCharacterButton: Locator;
  readonly characterGrid: Locator;
  readonly characterCards: Locator;
  readonly viewToggleGrid: Locator;
  readonly viewToggleList: Locator;
  readonly searchInput: Locator;
  readonly filterDropdown: Locator;
  readonly sortDropdown: Locator;
  readonly emptyState: Locator;
  readonly loadingSpinner: Locator;

  // Character creation form
  readonly characterForm: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly storyInput: Locator;
  readonly personalityTraitsInput: Locator;
  readonly goalsInput: Locator;
  readonly comfortLevelSlider: Locator;
  readonly intensitySelect: Locator;
  readonly therapeuticGoalsInput: Locator;
  readonly saveCharacterButton: Locator;
  readonly cancelButton: Locator;

  // Character edit form
  readonly editForm: Locator;
  readonly deleteCharacterButton: Locator;
  readonly confirmDeleteButton: Locator;

  constructor(page: Page) {
    super(page);

    // Initialize locators
    this.pageTitle = page.locator('h1').filter({ hasText: /character.*management/i });
    this.createCharacterButton = page.locator('button').filter({ hasText: /create.*character|new character/i });
    this.characterGrid = page.locator('[data-testid="character-grid"], .character-grid');
    this.characterCards = page.locator('[data-testid="character-card"], .character-card');
    this.viewToggleGrid = page.locator('button[data-view="grid"], [data-testid="grid-view"]');
    this.viewToggleList = page.locator('button[data-view="list"], [data-testid="list-view"]');
    this.searchInput = page.locator('input[placeholder*="search"], [data-testid="search-input"]');
    this.filterDropdown = page.locator('select[data-testid="filter"], .filter-dropdown');
    this.sortDropdown = page.locator('select[data-testid="sort"], .sort-dropdown');
    this.emptyState = page.locator('[data-testid="no-characters"], .empty-state');
    this.loadingSpinner = page.locator('.spinner, [data-testid="loading"]');

    // Character creation form
    this.characterForm = page.locator('[data-testid="character-form"], form');
    this.nameInput = page.locator('input[name="name"], [data-testid="character-name"]');
    this.descriptionInput = page.locator('textarea[name="description"], [data-testid="character-description"]');
    this.storyInput = page.locator('textarea[name="story"], [data-testid="character-story"]');
    this.personalityTraitsInput = page.locator('input[name="personality_traits"], [data-testid="personality-traits"]');
    this.goalsInput = page.locator('input[name="goals"], [data-testid="character-goals"]');
    this.comfortLevelSlider = page.locator('input[type="range"], [data-testid="comfort-level"]');
    this.intensitySelect = page.locator('select[name="intensity"], [data-testid="intensity-select"]');
    this.therapeuticGoalsInput = page.locator('input[name="therapeutic_goals"], [data-testid="therapeutic-goals"]');
    this.saveCharacterButton = page.locator('button[type="submit"], [data-testid="save-character"]');
    this.cancelButton = page.locator('button').filter({ hasText: /cancel/i });

    // Character edit form
    this.editForm = page.locator('[data-testid="edit-form"], .edit-form');
    this.deleteCharacterButton = page.locator('button').filter({ hasText: /delete/i });
    this.confirmDeleteButton = page.locator('button').filter({ hasText: /confirm.*delete|yes.*delete/i });
  }

  // Navigation
  async goto() {
    await super.goto('/characters');
    await this.waitForPageLoad();
  }

  // Actions
  async createCharacter(character: TestCharacter) {
    await this.clickCreateCharacter();
    await this.fillCharacterForm(character);
    await this.saveCharacter();
  }

  async clickCreateCharacter() {
    await this.createCharacterButton.click();
    await this.waitForElement('[data-testid="character-form"], form');
  }

  async fillCharacterForm(character: TestCharacter) {
    await this.nameInput.fill(character.name);
    await this.descriptionInput.fill(character.appearance.description);
    await this.storyInput.fill(character.background.story);

    // Handle personality traits (might be comma-separated or individual inputs)
    await this.personalityTraitsInput.fill(character.background.personality_traits.join(', '));

    // Handle goals
    await this.goalsInput.fill(character.background.goals.join(', '));

    // Set comfort level
    await this.comfortLevelSlider.fill(character.therapeutic_profile.comfort_level.toString());

    // Set intensity
    await this.intensitySelect.selectOption(character.therapeutic_profile.preferred_intensity);

    // Handle therapeutic goals
    await this.therapeuticGoalsInput.fill(character.therapeutic_profile.therapeutic_goals.join(', '));
  }

  async saveCharacter() {
    await this.saveCharacterButton.click();
    await this.waitForLoadingToComplete();
  }

  async cancelCharacterCreation() {
    await this.cancelButton.click();
  }

  async editCharacter(characterName: string, updates: Partial<TestCharacter>) {
    await this.selectCharacterForEdit(characterName);
    await this.updateCharacterForm(updates);
    await this.saveCharacter();
  }

  async selectCharacterForEdit(characterName: string) {
    const characterCard = this.characterCards.filter({ hasText: characterName });
    const editButton = characterCard.locator('button').filter({ hasText: /edit/i });
    await editButton.click();
    await this.waitForElement('[data-testid="edit-form"], .edit-form');
  }

  async updateCharacterForm(updates: Partial<TestCharacter>) {
    if (updates.name) {
      await this.nameInput.fill(updates.name);
    }
    if (updates.appearance?.description) {
      await this.descriptionInput.fill(updates.appearance.description);
    }
    if (updates.background?.story) {
      await this.storyInput.fill(updates.background.story);
    }
    // Add more field updates as needed
  }

  async deleteCharacter(characterName: string) {
    await this.selectCharacterForEdit(characterName);
    await this.deleteCharacterButton.click();
    await this.confirmDeleteButton.click();
    await this.waitForLoadingToComplete();
  }

  async searchCharacters(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.waitForTimeout(500); // Wait for search debounce
  }

  async filterCharacters(filterValue: string) {
    await this.filterDropdown.selectOption(filterValue);
    await this.waitForLoadingToComplete();
  }

  async sortCharacters(sortValue: string) {
    await this.sortDropdown.selectOption(sortValue);
    await this.waitForLoadingToComplete();
  }

  async switchToGridView() {
    await this.viewToggleGrid.click();
  }

  async switchToListView() {
    await this.viewToggleList.click();
  }

  // Validations
  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.createCharacterButton).toBeVisible();
    await this.waitForLoadingToComplete();
  }

  async expectCharacterFormVisible() {
    await expect(this.characterForm).toBeVisible();
    await expect(this.nameInput).toBeVisible();
    await expect(this.saveCharacterButton).toBeVisible();
  }

  async expectCharacterCreated(characterName: string) {
    const characterCard = this.characterCards.filter({ hasText: characterName });
    await expect(characterCard).toBeVisible();
  }

  async expectCharacterDeleted(characterName: string) {
    const characterCard = this.characterCards.filter({ hasText: characterName });
    await expect(characterCard).toBeHidden();
  }

  async expectEmptyState() {
    await expect(this.emptyState).toBeVisible();
    await expect(this.characterCards).toHaveCount(0);
  }

  async expectCharacterCount(count: number) {
    await expect(this.characterCards).toHaveCount(count);
  }

  async expectSearchResults(searchTerm: string) {
    const visibleCards = this.characterCards.filter({ hasText: new RegExp(searchTerm, 'i') });
    await expect(visibleCards.first()).toBeVisible();
  }

  // Form validation
  async expectFormValidation() {
    await this.clickCreateCharacter();
    await this.saveCharacterButton.click();

    // Should show validation errors for required fields
    const errorMessages = this.page.locator('.error, [data-testid="error"]');
    await expect(errorMessages.first()).toBeVisible();
  }

  async expectNameRequired() {
    await this.clickCreateCharacter();
    await this.descriptionInput.fill('Test description');
    await this.saveCharacterButton.click();

    const nameError = this.page.locator('.error').filter({ hasText: /name.*required/i });
    await expect(nameError).toBeVisible();
  }

  // Accessibility tests
  async checkAccessibility() {
    await super.checkAccessibility();

    // Check form accessibility
    await this.clickCreateCharacter();
    await expect(this.nameInput).toHaveAttribute('aria-label');
    await expect(this.characterForm).toHaveRole('form');

    // Check button accessibility
    await expect(this.createCharacterButton).toHaveRole('button');
    await expect(this.saveCharacterButton).toHaveRole('button');
  }

  // Keyboard navigation
  async navigateFormWithKeyboard() {
    await this.clickCreateCharacter();

    await this.nameInput.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.descriptionInput).toBeFocused();

    await this.page.keyboard.press('Tab');
    await expect(this.storyInput).toBeFocused();
  }

  // Mobile responsiveness
  async checkMobileLayout() {
    await this.setMobileViewport();
    await this.expectPageLoaded();

    // Should automatically switch to list view on mobile
    const gridContainer = await this.characterGrid.boundingBox();
    expect(gridContainer?.width).toBeLessThan(768);
  }

  // Performance tests
  async measureCharacterCreationTime() {
    const startTime = Date.now();
    await this.createCharacter({
      name: 'Test Character',
      appearance: { description: 'Test description' },
      background: {
        story: 'Test story',
        personality_traits: ['Test trait'],
        goals: ['Test goal'],
      },
      therapeutic_profile: {
        comfort_level: 5,
        preferred_intensity: 'MEDIUM',
        therapeutic_goals: ['Test therapeutic goal'],
      },
    });
    const endTime = Date.now();

    const creationTime = endTime - startTime;
    expect(creationTime).toBeLessThan(10000); // Should complete within 10 seconds

    return creationTime;
  }

  // Bulk operations
  async selectMultipleCharacters(characterNames: string[]) {
    for (const name of characterNames) {
      const characterCard = this.characterCards.filter({ hasText: name });
      const checkbox = characterCard.locator('input[type="checkbox"]');
      await checkbox.check();
    }
  }

  async bulkDeleteCharacters(characterNames: string[]) {
    await this.selectMultipleCharacters(characterNames);
    const bulkDeleteButton = this.page.locator('button').filter({ hasText: /delete selected/i });
    await bulkDeleteButton.click();
    await this.confirmDeleteButton.click();
    await this.waitForLoadingToComplete();
  }
}
