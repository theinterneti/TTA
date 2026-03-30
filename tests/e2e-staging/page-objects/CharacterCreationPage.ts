// Logseq: [[TTA.dev/Tests/E2e-staging/Page-objects/Charactercreationpage]]
/**
 * Character Creation Page Object
 *
 * Handles interactions with the character creation form and workflow.
 * Supports creating characters with various attributes and therapeutic profiles.
 */

import { expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { STAGING_CONFIG } from '../helpers/staging-config';

export class CharacterCreationPage extends BasePage {
  // Selectors
  private readonly characterNameInput = 'input[name="character_name"], input[id="characterName"]';
  private readonly appearanceInput = 'textarea[name="appearance"], textarea[id="appearance"]';
  private readonly backgroundInput = 'textarea[name="background"], textarea[id="background"]';
  private readonly personalityTraitsSelect = 'select[name="personality_traits"], select[id="personalityTraits"]';
  private readonly therapeuticGoalsSelect = 'select[name="therapeutic_goals"], select[id="therapeuticGoals"]';
  private readonly intensitySelect = 'select[name="intensity"], select[id="intensity"]';
  private readonly createButton = 'button[type="submit"]:has-text("Create"), button:has-text("Create Character")';
  private readonly cancelButton = 'button:has-text("Cancel")';
  private readonly formContainer = '[data-testid="character-creation-form"], form';
  private readonly successMessage = '[data-testid="success-message"], .success-message';
  private readonly errorMessage = '[data-testid="error-message"], .error-message';

  /**
   * Navigate to character creation page
   */
  async goto(): Promise<void> {
    await this.page.goto('/character/create');
    await this.waitForPageLoad();
    await this.expectFormVisible();
  }

  /**
   * Expect character creation form to be visible
   */
  async expectFormVisible(): Promise<void> {
    await this.expectVisible(this.formContainer);
  }

  /**
   * Fill character name
   */
  async fillCharacterName(name: string): Promise<void> {
    await this.fillInput(this.characterNameInput, name);
  }

  /**
   * Fill appearance description
   */
  async fillAppearance(appearance: string): Promise<void> {
    await this.fillInput(this.appearanceInput, appearance);
  }

  /**
   * Fill background story
   */
  async fillBackground(background: string): Promise<void> {
    await this.fillInput(this.backgroundInput, background);
  }

  /**
   * Select personality traits
   */
  async selectPersonalityTraits(traits: string[]): Promise<void> {
    for (const trait of traits) {
      await this.selectOption(this.personalityTraitsSelect, trait);
    }
  }

  /**
   * Select therapeutic goals
   */
  async selectTherapeuticGoals(goals: string[]): Promise<void> {
    for (const goal of goals) {
      await this.selectOption(this.therapeuticGoalsSelect, goal);
    }
  }

  /**
   * Select intensity level
   */
  async selectIntensity(intensity: string): Promise<void> {
    await this.selectOption(this.intensitySelect, intensity);
  }

  /**
   * Create character with default test data
   */
  async createCharacterWithDefaults(): Promise<void> {
    const character = STAGING_CONFIG.testCharacters.default;

    await this.fillCharacterName(character.name);
    await this.fillAppearance(character.appearance.description);
    await this.fillBackground(character.background.story);

    if (character.background.personality_traits) {
      await this.selectPersonalityTraits(character.background.personality_traits);
    }

    if (character.background.goals) {
      await this.selectTherapeuticGoals(character.background.goals);
    }

    if (character.therapeutic_profile?.preferred_intensity) {
      await this.selectIntensity(character.therapeutic_profile.preferred_intensity);
    }

    await this.submitForm();
  }

  /**
   * Create character with custom data
   */
  async createCharacter(data: {
    name: string;
    appearance?: string;
    background?: string;
    traits?: string[];
    goals?: string[];
    intensity?: string;
  }): Promise<void> {
    await this.fillCharacterName(data.name);

    if (data.appearance) {
      await this.fillAppearance(data.appearance);
    }

    if (data.background) {
      await this.fillBackground(data.background);
    }

    if (data.traits) {
      await this.selectPersonalityTraits(data.traits);
    }

    if (data.goals) {
      await this.selectTherapeuticGoals(data.goals);
    }

    if (data.intensity) {
      await this.selectIntensity(data.intensity);
    }

    await this.submitForm();
  }

  /**
   * Submit character creation form
   */
  async submitForm(): Promise<void> {
    await this.clickElement(this.createButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Cancel character creation
   */
  async cancel(): Promise<void> {
    await this.clickElement(this.cancelButton);
  }

  /**
   * Expect success message
   */
  async expectSuccessMessage(): Promise<void> {
    await this.expectVisible(this.successMessage);
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
   * Verify character name is required
   */
  async verifyCharacterNameRequired(): Promise<void> {
    await this.submitForm();
    await this.expectErrorMessage();
  }

  /**
   * Check if create button is enabled
   */
  async isCreateButtonEnabled(): Promise<boolean> {
    const button = this.getElement(this.createButton);
    return !(await button.isDisabled());
  }
}
