import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Settings Page
 */
export class SettingsPage extends BasePage {
  // Locators
  readonly pageTitle: Locator;
  readonly tabNavigation: Locator;
  readonly therapeuticTab: Locator;
  readonly modelsTab: Locator;
  readonly privacyTab: Locator;
  readonly notificationsTab: Locator;
  readonly accessibilityTab: Locator;
  readonly crisisTab: Locator;
  readonly saveButton: Locator;
  readonly unsavedWarning: Locator;
  readonly errorMessage: Locator;

  // Therapeutic settings
  readonly intensitySelect: Locator;
  readonly approachesCheckboxes: Locator;
  readonly triggerWarningsInput: Locator;
  readonly comfortTopicsInput: Locator;
  readonly avoidTopicsInput: Locator;
  readonly crisisContactInput: Locator;

  // Privacy settings
  readonly dataSharingToggle: Locator;
  readonly researchParticipationToggle: Locator;
  readonly contactPreferencesCheckboxes: Locator;
  readonly dataRetentionSelect: Locator;
  readonly exportDataButton: Locator;
  readonly deleteDataButton: Locator;

  // Notification settings
  readonly sessionRemindersToggle: Locator;
  readonly progressUpdatesToggle: Locator;
  readonly milestoneToggle: Locator;
  readonly crisisAlertsToggle: Locator;
  readonly emailNotificationsToggle: Locator;
  readonly pushNotificationsToggle: Locator;

  // Accessibility settings
  readonly highContrastToggle: Locator;
  readonly largeTextToggle: Locator;
  readonly screenReaderToggle: Locator;
  readonly reducedMotionToggle: Locator;
  readonly keyboardNavigationToggle: Locator;

  // AI Models settings
  readonly modelSelector: Locator;
  readonly freeModelsFilter: Locator;
  readonly costThresholdSlider: Locator;
  readonly modelPreferences: Locator;
  readonly modelAnalytics: Locator;

  constructor(page: Page) {
    super(page);
    
    // Initialize locators
    this.pageTitle = page.locator('h1').filter({ hasText: /settings/i });
    this.tabNavigation = page.locator('[data-testid="settings-tabs"], nav');
    this.therapeuticTab = page.locator('button').filter({ hasText: /therapeutic/i });
    this.modelsTab = page.locator('button').filter({ hasText: /ai models/i });
    this.privacyTab = page.locator('button').filter({ hasText: /privacy/i });
    this.notificationsTab = page.locator('button').filter({ hasText: /notifications/i });
    this.accessibilityTab = page.locator('button').filter({ hasText: /accessibility/i });
    this.crisisTab = page.locator('button').filter({ hasText: /crisis/i });
    this.saveButton = page.locator('button').filter({ hasText: /save changes/i });
    this.unsavedWarning = page.locator('[data-testid="unsaved-warning"], .unsaved-warning');
    this.errorMessage = page.locator('[data-testid="error"], .error');

    // Therapeutic settings
    this.intensitySelect = page.locator('select[name="intensity_level"]');
    this.approachesCheckboxes = page.locator('input[name="preferred_approaches"]');
    this.triggerWarningsInput = page.locator('input[name="trigger_warnings"]');
    this.comfortTopicsInput = page.locator('input[name="comfort_topics"]');
    this.avoidTopicsInput = page.locator('input[name="avoid_topics"]');
    this.crisisContactInput = page.locator('textarea[name="crisis_contact_info"]');

    // Privacy settings
    this.dataSharingToggle = page.locator('input[name="data_sharing_consent"]');
    this.researchParticipationToggle = page.locator('input[name="research_participation"]');
    this.contactPreferencesCheckboxes = page.locator('input[name="contact_preferences"]');
    this.dataRetentionSelect = page.locator('select[name="data_retention_period"]');
    this.exportDataButton = page.locator('button').filter({ hasText: /export.*data/i });
    this.deleteDataButton = page.locator('button').filter({ hasText: /delete.*data/i });

    // Notification settings
    this.sessionRemindersToggle = page.locator('input[name="session_reminders"]');
    this.progressUpdatesToggle = page.locator('input[name="progress_updates"]');
    this.milestoneToggle = page.locator('input[name="milestone_celebrations"]');
    this.crisisAlertsToggle = page.locator('input[name="crisis_alerts"]');
    this.emailNotificationsToggle = page.locator('input[name="email_notifications"]');
    this.pushNotificationsToggle = page.locator('input[name="push_notifications"]');

    // Accessibility settings
    this.highContrastToggle = page.locator('input[name="high_contrast"]');
    this.largeTextToggle = page.locator('input[name="large_text"]');
    this.screenReaderToggle = page.locator('input[name="screen_reader_optimized"]');
    this.reducedMotionToggle = page.locator('input[name="reduced_motion"]');
    this.keyboardNavigationToggle = page.locator('input[name="keyboard_navigation"]');

    // AI Models settings
    this.modelSelector = page.locator('[data-testid="model-selector"]');
    this.freeModelsFilter = page.locator('input[name="show_free_only"]');
    this.costThresholdSlider = page.locator('input[name="max_cost_per_token"]');
    this.modelPreferences = page.locator('[data-testid="model-preferences"]');
    this.modelAnalytics = page.locator('[data-testid="model-analytics"]');
  }

  // Navigation
  async goto() {
    await super.goto('/settings');
    await this.waitForPageLoad();
  }

  // Tab navigation
  async goToTherapeuticTab() {
    await this.therapeuticTab.click();
    await this.page.waitForTimeout(200);
  }

  async goToModelsTab() {
    await this.modelsTab.click();
    await this.page.waitForTimeout(200);
  }

  async goToPrivacyTab() {
    await this.privacyTab.click();
    await this.page.waitForTimeout(200);
  }

  async goToNotificationsTab() {
    await this.notificationsTab.click();
    await this.page.waitForTimeout(200);
  }

  async goToAccessibilityTab() {
    await this.accessibilityTab.click();
    await this.page.waitForTimeout(200);
  }

  async goToCrisisTab() {
    await this.crisisTab.click();
    await this.page.waitForTimeout(200);
  }

  // Actions
  async saveSettings() {
    await this.saveButton.click();
    await this.waitForLoadingToComplete();
  }

  async updateTherapeuticSettings(settings: {
    intensity?: 'LOW' | 'MEDIUM' | 'HIGH';
    approaches?: string[];
    triggerWarnings?: string[];
    comfortTopics?: string[];
    avoidTopics?: string[];
    crisisContact?: string;
  }) {
    await this.goToTherapeuticTab();
    
    if (settings.intensity) {
      await this.intensitySelect.selectOption(settings.intensity);
    }
    
    if (settings.approaches) {
      // Handle checkbox selection for approaches
      for (const approach of settings.approaches) {
        const checkbox = this.approachesCheckboxes.filter({ hasText: approach });
        await checkbox.check();
      }
    }
    
    if (settings.triggerWarnings) {
      await this.triggerWarningsInput.fill(settings.triggerWarnings.join(', '));
    }
    
    if (settings.comfortTopics) {
      await this.comfortTopicsInput.fill(settings.comfortTopics.join(', '));
    }
    
    if (settings.avoidTopics) {
      await this.avoidTopicsInput.fill(settings.avoidTopics.join(', '));
    }
    
    if (settings.crisisContact) {
      await this.crisisContactInput.fill(settings.crisisContact);
    }
  }

  async updatePrivacySettings(settings: {
    dataSharing?: boolean;
    researchParticipation?: boolean;
    contactPreferences?: string[];
    dataRetention?: number;
  }) {
    await this.goToPrivacyTab();
    
    if (settings.dataSharing !== undefined) {
      if (settings.dataSharing) {
        await this.dataSharingToggle.check();
      } else {
        await this.dataSharingToggle.uncheck();
      }
    }
    
    if (settings.researchParticipation !== undefined) {
      if (settings.researchParticipation) {
        await this.researchParticipationToggle.check();
      } else {
        await this.researchParticipationToggle.uncheck();
      }
    }
    
    if (settings.contactPreferences) {
      for (const preference of settings.contactPreferences) {
        const checkbox = this.contactPreferencesCheckboxes.filter({ hasText: preference });
        await checkbox.check();
      }
    }
    
    if (settings.dataRetention) {
      await this.dataRetentionSelect.selectOption(settings.dataRetention.toString());
    }
  }

  async updateNotificationSettings(settings: {
    sessionReminders?: boolean;
    progressUpdates?: boolean;
    milestones?: boolean;
    crisisAlerts?: boolean;
    email?: boolean;
    push?: boolean;
  }) {
    await this.goToNotificationsTab();
    
    const toggles = [
      { setting: settings.sessionReminders, toggle: this.sessionRemindersToggle },
      { setting: settings.progressUpdates, toggle: this.progressUpdatesToggle },
      { setting: settings.milestones, toggle: this.milestoneToggle },
      { setting: settings.crisisAlerts, toggle: this.crisisAlertsToggle },
      { setting: settings.email, toggle: this.emailNotificationsToggle },
      { setting: settings.push, toggle: this.pushNotificationsToggle },
    ];
    
    for (const { setting, toggle } of toggles) {
      if (setting !== undefined) {
        if (setting) {
          await toggle.check();
        } else {
          await toggle.uncheck();
        }
      }
    }
  }

  async updateAccessibilitySettings(settings: {
    highContrast?: boolean;
    largeText?: boolean;
    screenReader?: boolean;
    reducedMotion?: boolean;
    keyboardNavigation?: boolean;
  }) {
    await this.goToAccessibilityTab();
    
    const toggles = [
      { setting: settings.highContrast, toggle: this.highContrastToggle },
      { setting: settings.largeText, toggle: this.largeTextToggle },
      { setting: settings.screenReader, toggle: this.screenReaderToggle },
      { setting: settings.reducedMotion, toggle: this.reducedMotionToggle },
      { setting: settings.keyboardNavigation, toggle: this.keyboardNavigationToggle },
    ];
    
    for (const { setting, toggle } of toggles) {
      if (setting !== undefined) {
        if (setting) {
          await toggle.check();
        } else {
          await toggle.uncheck();
        }
      }
    }
  }

  async exportData() {
    await this.goToPrivacyTab();
    await this.exportDataButton.click();
    
    // Wait for download to start
    const downloadPromise = this.page.waitForEvent('download');
    const download = await downloadPromise;
    
    return download;
  }

  async deleteAllData() {
    await this.goToPrivacyTab();
    await this.deleteDataButton.click();
    
    // Confirm deletion
    const confirmButton = this.page.locator('button').filter({ hasText: /confirm.*delete/i });
    await confirmButton.click();
    
    await this.waitForLoadingToComplete();
  }

  // Validations
  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.tabNavigation).toBeVisible();
    await this.waitForLoadingToComplete();
  }

  async expectTabActive(tabName: string) {
    const activeTab = this.page.locator(`button[aria-selected="true"]`).filter({ hasText: new RegExp(tabName, 'i') });
    await expect(activeTab).toBeVisible();
  }

  async expectUnsavedChanges() {
    await expect(this.unsavedWarning).toBeVisible();
    await expect(this.saveButton).toBeVisible();
  }

  async expectSettingsSaved() {
    await expect(this.unsavedWarning).toBeHidden();
    // Should show success message
    const successMessage = this.page.locator('[data-testid="success"], .success');
    await expect(successMessage).toBeVisible();
  }

  async expectErrorMessage(message?: string) {
    await expect(this.errorMessage).toBeVisible();
    if (message) {
      await expect(this.errorMessage).toContainText(message);
    }
  }

  // Accessibility tests
  async checkAccessibility() {
    await super.checkAccessibility();
    
    // Check tab accessibility
    await expect(this.tabNavigation).toHaveRole('tablist');
    await expect(this.therapeuticTab).toHaveRole('tab');
    
    // Check form accessibility
    await this.goToTherapeuticTab();
    await expect(this.intensitySelect).toHaveAttribute('aria-label');
    
    // Check toggle accessibility
    await this.goToNotificationsTab();
    await expect(this.sessionRemindersToggle).toHaveRole('switch');
  }

  // Keyboard navigation
  async navigateTabsWithKeyboard() {
    await this.therapeuticTab.focus();
    await this.page.keyboard.press('ArrowRight');
    await expect(this.modelsTab).toBeFocused();
    
    await this.page.keyboard.press('ArrowRight');
    await expect(this.privacyTab).toBeFocused();
    
    // Test Enter key activation
    await this.page.keyboard.press('Enter');
    await this.expectTabActive('privacy');
  }
}
