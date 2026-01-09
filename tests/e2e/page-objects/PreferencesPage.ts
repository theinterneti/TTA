// Logseq: [[TTA.dev/Tests/E2e/Page-objects/Preferencespage]]
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Preferences Page
 */
export class PreferencesPage extends BasePage {
  // Main page locators
  readonly pageTitle: Locator;
  readonly pageDescription: Locator;
  readonly exportButton: Locator;
  readonly importButton: Locator;
  readonly resetButton: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;

  // Configuration tabs
  readonly intensityTab: Locator;
  readonly approachTab: Locator;
  readonly conversationTab: Locator;
  readonly goalsTab: Locator;
  readonly characterTab: Locator;
  readonly topicsTab: Locator;

  // Intensity Level Selector
  readonly intensitySlider: Locator;
  readonly intensityLabels: Locator;
  readonly intensityValue: Locator;

  // Therapeutic Approach Selector
  readonly approachCheckboxes: Locator;
  readonly cbtCheckbox: Locator;
  readonly mindfulnessCheckbox: Locator;
  readonly dbtCheckbox: Locator;

  // Conversation Style Selector
  readonly conversationStyleRadios: Locator;
  readonly supportiveRadio: Locator;
  readonly challengingRadio: Locator;
  readonly neutralRadio: Locator;

  // Therapeutic Goals
  readonly goalsInput: Locator;
  readonly goalsSuggestions: Locator;
  readonly selectedGoals: Locator;

  // Character Customization
  readonly characterNameInput: Locator;
  readonly preferredSettingSelect: Locator;

  // Topic Preferences
  readonly comfortTopicsInput: Locator;
  readonly triggerTopicsInput: Locator;
  readonly avoidTopicsInput: Locator;

  // Modals
  readonly importModal: Locator;
  readonly resetModal: Locator;
  readonly fileInput: Locator;
  readonly importConfirmButton: Locator;
  readonly resetConfirmButton: Locator;
  readonly cancelButton: Locator;

  // Save/validation
  readonly saveButton: Locator;
  readonly unsavedChangesWarning: Locator;
  readonly validationErrors: Locator;

  constructor(page: Page) {
    super(page);

    // Main page elements
    this.pageTitle = page.locator('h1:has-text("Therapeutic Preferences")');
    this.pageDescription = page.locator('text=Customize your therapeutic experience');
    this.exportButton = page.locator('button:has-text("Export")');
    this.importButton = page.locator('button:has-text("Import")');
    this.resetButton = page.locator('button:has-text("Reset")');
    this.loadingSpinner = page.locator('.animate-spin');
    this.errorMessage = page.locator('.bg-red-50');

    // Configuration tabs
    this.intensityTab = page.locator('[data-tab="intensity"]');
    this.approachTab = page.locator('[data-tab="approach"]');
    this.conversationTab = page.locator('[data-tab="conversation"]');
    this.goalsTab = page.locator('[data-tab="goals"]');
    this.characterTab = page.locator('[data-tab="character"]');
    this.topicsTab = page.locator('[data-tab="topics"]');

    // Form elements
    this.intensitySlider = page.locator('input[type="range"]');
    this.intensityLabels = page.locator('[data-testid="intensity-labels"]');
    this.intensityValue = page.locator('[data-testid="intensity-value"]');

    this.approachCheckboxes = page.locator('input[type="checkbox"][name="therapeutic_approach"]');
    this.cbtCheckbox = page.locator('input[value="CBT"]');
    this.mindfulnessCheckbox = page.locator('input[value="MINDFULNESS"]');
    this.dbtCheckbox = page.locator('input[value="DBT"]');

    this.conversationStyleRadios = page.locator('input[type="radio"][name="conversation_style"]');
    this.supportiveRadio = page.locator('input[value="SUPPORTIVE"]');
    this.challengingRadio = page.locator('input[value="CHALLENGING"]');
    this.neutralRadio = page.locator('input[value="NEUTRAL"]');

    this.goalsInput = page.locator('input[placeholder*="therapeutic goals"]');
    this.goalsSuggestions = page.locator('[data-testid="goals-suggestions"]');
    this.selectedGoals = page.locator('[data-testid="selected-goals"]');

    this.characterNameInput = page.locator('input[name="character_name"]');
    this.preferredSettingSelect = page.locator('select[name="preferred_setting"]');

    this.comfortTopicsInput = page.locator('input[name="comfort_topics"]');
    this.triggerTopicsInput = page.locator('input[name="trigger_topics"]');
    this.avoidTopicsInput = page.locator('input[name="avoid_topics"]');

    // Modals
    this.importModal = page.locator('[data-testid="import-modal"]');
    this.resetModal = page.locator('[data-testid="reset-modal"]');
    this.fileInput = page.locator('input[type="file"]');
    this.importConfirmButton = page.locator('button:has-text("Import")').last();
    this.resetConfirmButton = page.locator('button:has-text("Reset All")');
    this.cancelButton = page.locator('button:has-text("Cancel")');

    this.saveButton = page.locator('button:has-text("Save")');
    this.unsavedChangesWarning = page.locator('[data-testid="unsaved-changes"]');
    this.validationErrors = page.locator('[data-testid="validation-errors"]');
  }

  async goto() {
    await this.page.goto('/preferences');
    await this.waitForPageLoad();
  }

  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.pageDescription).toBeVisible();
  }

  async expectLoadingState() {
    await expect(this.loadingSpinner).toBeVisible();
  }

  async expectErrorMessage(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  // Tab navigation
  async clickTab(tabName: string) {
    const tabMap: { [key: string]: Locator } = {
      'intensity': this.intensityTab,
      'approach': this.approachTab,
      'conversation': this.conversationTab,
      'goals': this.goalsTab,
      'character': this.characterTab,
      'topics': this.topicsTab,
    };

    await tabMap[tabName].click();
    await this.page.waitForTimeout(300);
  }

  // Intensity Level Configuration
  async setIntensityLevel(level: number) {
    await this.intensitySlider.fill(level.toString());
    await this.page.waitForTimeout(200);
  }

  async expectIntensityLevel(expectedLevel: number) {
    const actualValue = await this.intensitySlider.inputValue();
    expect(parseInt(actualValue)).toBe(expectedLevel);
  }

  // Therapeutic Approach Configuration
  async selectTherapeuticApproach(approach: string) {
    const approachMap: { [key: string]: Locator } = {
      'CBT': this.cbtCheckbox,
      'MINDFULNESS': this.mindfulnessCheckbox,
      'DBT': this.dbtCheckbox,
    };

    await approachMap[approach].check();
  }

  async unselectTherapeuticApproach(approach: string) {
    const approachMap: { [key: string]: Locator } = {
      'CBT': this.cbtCheckbox,
      'MINDFULNESS': this.mindfulnessCheckbox,
      'DBT': this.dbtCheckbox,
    };

    await approachMap[approach].uncheck();
  }

  async expectApproachSelected(approach: string) {
    const approachMap: { [key: string]: Locator } = {
      'CBT': this.cbtCheckbox,
      'MINDFULNESS': this.mindfulnessCheckbox,
      'DBT': this.dbtCheckbox,
    };

    await expect(approachMap[approach]).toBeChecked();
  }

  // Conversation Style Configuration
  async selectConversationStyle(style: string) {
    const styleMap: { [key: string]: Locator } = {
      'SUPPORTIVE': this.supportiveRadio,
      'CHALLENGING': this.challengingRadio,
      'NEUTRAL': this.neutralRadio,
    };

    await styleMap[style].check();
  }

  async expectConversationStyle(expectedStyle: string) {
    const styleMap: { [key: string]: Locator } = {
      'SUPPORTIVE': this.supportiveRadio,
      'CHALLENGING': this.challengingRadio,
      'NEUTRAL': this.neutralRadio,
    };

    await expect(styleMap[expectedStyle]).toBeChecked();
  }

  // Therapeutic Goals Configuration
  async addTherapeuticGoal(goal: string) {
    await this.goalsInput.fill(goal);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(200);
  }

  async removeTherapeuticGoal(goal: string) {
    const goalTag = this.page.locator(`[data-testid="goal-tag"]:has-text("${goal}")`);
    await goalTag.locator('button').click();
  }

  async expectGoalSelected(goal: string) {
    await expect(this.selectedGoals.locator(`text=${goal}`)).toBeVisible();
  }

  // Character Customization
  async setCharacterName(name: string) {
    await this.characterNameInput.fill(name);
  }

  async setPreferredSetting(setting: string) {
    await this.preferredSettingSelect.selectOption(setting);
  }

  async expectCharacterName(expectedName: string) {
    await expect(this.characterNameInput).toHaveValue(expectedName);
  }

  // Topic Preferences
  async setComfortTopics(topics: string[]) {
    await this.comfortTopicsInput.fill(topics.join(', '));
  }

  async setTriggerTopics(topics: string[]) {
    await this.triggerTopicsInput.fill(topics.join(', '));
  }

  async setAvoidTopics(topics: string[]) {
    await this.avoidTopicsInput.fill(topics.join(', '));
  }

  // Save and validation
  async savePreferences() {
    await this.saveButton.click();
    await this.page.waitForTimeout(1000);
  }

  async expectUnsavedChangesWarning() {
    await expect(this.unsavedChangesWarning).toBeVisible();
  }

  async expectValidationErrors() {
    await expect(this.validationErrors).toBeVisible();
  }

  // Import/Export functionality
  async clickExport() {
    await this.exportButton.click();
  }

  async clickImport() {
    await this.importButton.click();
    await expect(this.importModal).toBeVisible();
  }

  async importPreferences(filePath: string) {
    await this.clickImport();
    await this.fileInput.setInputFiles(filePath);
    await this.importConfirmButton.click();
  }

  async clickReset() {
    await this.resetButton.click();
    await expect(this.resetModal).toBeVisible();
  }

  async confirmReset() {
    await this.resetConfirmButton.click();
  }

  async cancelModal() {
    await this.cancelButton.click();
  }

  // Accessibility testing
  async testKeyboardNavigation() {
    await this.intensitySlider.focus();
    await this.page.keyboard.press('ArrowRight');
    await this.page.keyboard.press('Tab');
    await expect(this.cbtCheckbox).toBeFocused();
  }

  async testScreenReaderSupport() {
    await expect(this.intensitySlider).toHaveAttribute('aria-label');
    await expect(this.cbtCheckbox).toHaveAttribute('aria-describedby');
  }

  // Performance testing
  async measureSavePerformance(): Promise<number> {
    const startTime = Date.now();
    await this.savePreferences();
    return Date.now() - startTime;
  }
}
