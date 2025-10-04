import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Model Management Page
 */
export class ModelManagementPage extends BasePage {
  // Main page locators
  readonly pageTitle: Locator;
  readonly modelSelector: Locator;
  readonly currentModelDisplay: Locator;
  readonly modelStatusIndicator: Locator;
  readonly refreshModelsButton: Locator;

  // OpenRouter Authentication
  readonly openRouterAuthSection: Locator;
  readonly openRouterAuthButton: Locator;
  readonly openRouterAuthModal: Locator;
  readonly apiKeyInput: Locator;
  readonly authStatusDisplay: Locator;
  readonly connectButton: Locator;
  readonly disconnectButton: Locator;

  // Model Selection
  readonly modelDropdown: Locator;
  readonly modelOptions: Locator;
  readonly modelSearchInput: Locator;
  readonly modelFilterButtons: Locator;
  readonly freeModelsFilter: Locator;
  readonly paidModelsFilter: Locator;
  readonly allModelsFilter: Locator;

  // Model Information
  readonly modelInfoPanel: Locator;
  readonly modelDescription: Locator;
  readonly modelCostDisplay: Locator;
  readonly modelPerformanceMetrics: Locator;
  readonly modelCompatibilityInfo: Locator;

  // Model Configuration
  readonly temperatureSlider: Locator;
  readonly maxTokensInput: Locator;
  readonly topPSlider: Locator;
  readonly frequencyPenaltySlider: Locator;
  readonly presencePenaltySlider: Locator;

  // Advanced Settings
  readonly advancedSettingsToggle: Locator;
  readonly systemPromptTextarea: Locator;
  readonly stopSequencesInput: Locator;
  readonly seedInput: Locator;

  // Testing and Validation
  readonly testModelButton: Locator;
  readonly testPromptInput: Locator;
  readonly testResponseDisplay: Locator;
  readonly testLoadingIndicator: Locator;

  // Save/Apply
  readonly saveConfigButton: Locator;
  readonly applyChangesButton: Locator;
  readonly resetToDefaultsButton: Locator;
  readonly unsavedChangesIndicator: Locator;

  // Error handling
  readonly errorMessage: Locator;
  readonly connectionErrorMessage: Locator;
  readonly authErrorMessage: Locator;

  constructor(page: Page) {
    super(page);
    
    // Main page elements
    this.pageTitle = page.locator('h1:has-text("Model Management")');
    this.modelSelector = page.locator('[data-testid="model-selector"]');
    this.currentModelDisplay = page.locator('[data-testid="current-model"]');
    this.modelStatusIndicator = page.locator('[data-testid="model-status"]');
    this.refreshModelsButton = page.locator('button:has-text("Refresh Models")');

    // OpenRouter Authentication
    this.openRouterAuthSection = page.locator('[data-testid="openrouter-auth-section"]');
    this.openRouterAuthButton = page.locator('button:has-text("Connect OpenRouter")');
    this.openRouterAuthModal = page.locator('[data-testid="openrouter-auth-modal"]');
    this.apiKeyInput = page.locator('input[placeholder*="API Key"]');
    this.authStatusDisplay = page.locator('[data-testid="auth-status"]');
    this.connectButton = page.locator('button:has-text("Connect")');
    this.disconnectButton = page.locator('button:has-text("Disconnect")');

    // Model Selection
    this.modelDropdown = page.locator('select[name="model"], [data-testid="model-dropdown"]');
    this.modelOptions = page.locator('[data-testid="model-option"]');
    this.modelSearchInput = page.locator('input[placeholder*="Search models"]');
    this.modelFilterButtons = page.locator('[data-testid="model-filters"]');
    this.freeModelsFilter = page.locator('button:has-text("Free Models")');
    this.paidModelsFilter = page.locator('button:has-text("Paid Models")');
    this.allModelsFilter = page.locator('button:has-text("All Models")');

    // Model Information
    this.modelInfoPanel = page.locator('[data-testid="model-info-panel"]');
    this.modelDescription = page.locator('[data-testid="model-description"]');
    this.modelCostDisplay = page.locator('[data-testid="model-cost"]');
    this.modelPerformanceMetrics = page.locator('[data-testid="model-performance"]');
    this.modelCompatibilityInfo = page.locator('[data-testid="model-compatibility"]');

    // Model Configuration
    this.temperatureSlider = page.locator('input[name="temperature"]');
    this.maxTokensInput = page.locator('input[name="max_tokens"]');
    this.topPSlider = page.locator('input[name="top_p"]');
    this.frequencyPenaltySlider = page.locator('input[name="frequency_penalty"]');
    this.presencePenaltySlider = page.locator('input[name="presence_penalty"]');

    // Advanced Settings
    this.advancedSettingsToggle = page.locator('button:has-text("Advanced Settings")');
    this.systemPromptTextarea = page.locator('textarea[name="system_prompt"]');
    this.stopSequencesInput = page.locator('input[name="stop_sequences"]');
    this.seedInput = page.locator('input[name="seed"]');

    // Testing and Validation
    this.testModelButton = page.locator('button:has-text("Test Model")');
    this.testPromptInput = page.locator('textarea[placeholder*="test prompt"]');
    this.testResponseDisplay = page.locator('[data-testid="test-response"]');
    this.testLoadingIndicator = page.locator('[data-testid="test-loading"]');

    // Save/Apply
    this.saveConfigButton = page.locator('button:has-text("Save Configuration")');
    this.applyChangesButton = page.locator('button:has-text("Apply Changes")');
    this.resetToDefaultsButton = page.locator('button:has-text("Reset to Defaults")');
    this.unsavedChangesIndicator = page.locator('[data-testid="unsaved-changes"]');

    // Error handling
    this.errorMessage = page.locator('[data-testid="error-message"]');
    this.connectionErrorMessage = page.locator('text=Connection failed');
    this.authErrorMessage = page.locator('text=Authentication failed');
  }

  async goto() {
    await this.page.goto('/settings'); // Assuming model management is part of settings
    await this.waitForPageLoad();
  }

  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
  }

  // OpenRouter Authentication
  async connectOpenRouter(apiKey: string) {
    await this.openRouterAuthButton.click();
    await expect(this.openRouterAuthModal).toBeVisible();
    await this.apiKeyInput.fill(apiKey);
    await this.connectButton.click();
  }

  async disconnectOpenRouter() {
    await this.disconnectButton.click();
  }

  async expectAuthenticationSuccess() {
    await expect(this.authStatusDisplay).toContainText('Connected');
  }

  async expectAuthenticationError() {
    await expect(this.authErrorMessage).toBeVisible();
  }

  // Model Selection
  async selectModel(modelName: string) {
    await this.modelDropdown.click();
    await this.page.locator(`option:has-text("${modelName}")`).click();
    await this.page.waitForTimeout(500);
  }

  async searchModels(searchTerm: string) {
    await this.modelSearchInput.fill(searchTerm);
    await this.page.waitForTimeout(300);
  }

  async filterFreeModels() {
    await this.freeModelsFilter.click();
    await this.page.waitForTimeout(300);
  }

  async filterPaidModels() {
    await this.paidModelsFilter.click();
    await this.page.waitForTimeout(300);
  }

  async showAllModels() {
    await this.allModelsFilter.click();
    await this.page.waitForTimeout(300);
  }

  async expectModelSelected(modelName: string) {
    await expect(this.currentModelDisplay).toContainText(modelName);
  }

  async expectModelInfo(modelName: string) {
    await expect(this.modelInfoPanel).toBeVisible();
    await expect(this.modelDescription).toBeVisible();
  }

  // Model Configuration
  async setTemperature(value: number) {
    await this.temperatureSlider.fill(value.toString());
  }

  async setMaxTokens(value: number) {
    await this.maxTokensInput.fill(value.toString());
  }

  async setTopP(value: number) {
    await this.topPSlider.fill(value.toString());
  }

  async setFrequencyPenalty(value: number) {
    await this.frequencyPenaltySlider.fill(value.toString());
  }

  async setPresencePenalty(value: number) {
    await this.presencePenaltySlider.fill(value.toString());
  }

  async expectTemperature(expectedValue: number) {
    const actualValue = await this.temperatureSlider.inputValue();
    expect(parseFloat(actualValue)).toBe(expectedValue);
  }

  // Advanced Settings
  async toggleAdvancedSettings() {
    await this.advancedSettingsToggle.click();
  }

  async setSystemPrompt(prompt: string) {
    await this.systemPromptTextarea.fill(prompt);
  }

  async setStopSequences(sequences: string) {
    await this.stopSequencesInput.fill(sequences);
  }

  async setSeed(seed: number) {
    await this.seedInput.fill(seed.toString());
  }

  // Testing and Validation
  async testModel(prompt: string) {
    await this.testPromptInput.fill(prompt);
    await this.testModelButton.click();
    await expect(this.testLoadingIndicator).toBeVisible();
  }

  async expectTestResponse() {
    await expect(this.testResponseDisplay).toBeVisible();
    await expect(this.testLoadingIndicator).not.toBeVisible();
  }

  async expectTestError() {
    await expect(this.errorMessage).toBeVisible();
  }

  // Save and Apply
  async saveConfiguration() {
    await this.saveConfigButton.click();
    await this.page.waitForTimeout(1000);
  }

  async applyChanges() {
    await this.applyChangesButton.click();
    await this.page.waitForTimeout(1000);
  }

  async resetToDefaults() {
    await this.resetToDefaultsButton.click();
    await this.page.waitForTimeout(500);
  }

  async expectUnsavedChanges() {
    await expect(this.unsavedChangesIndicator).toBeVisible();
  }

  async expectConfigurationSaved() {
    await expect(this.page.locator('text=Configuration saved')).toBeVisible();
  }

  // Error Handling
  async expectConnectionError() {
    await expect(this.connectionErrorMessage).toBeVisible();
  }

  async expectGeneralError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  // Performance Testing
  async measureModelSwitchTime(modelName: string): Promise<number> {
    const startTime = Date.now();
    await this.selectModel(modelName);
    await this.expectModelSelected(modelName);
    return Date.now() - startTime;
  }

  async measureTestResponseTime(prompt: string): Promise<number> {
    const startTime = Date.now();
    await this.testModel(prompt);
    await this.expectTestResponse();
    return Date.now() - startTime;
  }

  // Accessibility Testing
  async testKeyboardNavigation() {
    await this.modelDropdown.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.temperatureSlider).toBeFocused();
  }

  async testScreenReaderSupport() {
    await expect(this.modelDropdown).toHaveAttribute('aria-label');
    await expect(this.temperatureSlider).toHaveAttribute('aria-describedby');
  }
}
