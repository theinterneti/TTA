/**
 * Gameplay Page Object
 *
 * Handles interactions with the main gameplay interface including
 * chat, story display, character actions, and game state management.
 */

import { expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { STAGING_CONFIG } from '../helpers/staging-config';

export class GameplayPage extends BasePage {
  // Selectors
  private readonly gameContainer = '[data-testid="gameplay-container"], .gameplay-container';
  private readonly storyDisplay = '[data-testid="story-display"], .story-display';
  private readonly chatInput = 'input[name="message"], textarea[name="message"], input[id="chatInput"]';
  private readonly sendButton = 'button[type="submit"]:has-text("Send"), button:has-text("Send Message")';
  private readonly characterInfo = '[data-testid="character-info"], .character-info';
  private readonly worldInfo = '[data-testid="world-info"], .world-info';
  private readonly chatHistory = '[data-testid="chat-history"], .chat-history';
  private readonly aiResponse = '[data-testid="ai-response"], .ai-response';
  private readonly loadingIndicator = '[data-testid="loading"], .loading, .spinner';
  private readonly errorAlert = '[data-testid="error-alert"], .error-alert';
  private readonly actionButtons = '[data-testid="action-button"], .action-button';
  private readonly menuButton = 'button:has-text("Menu"), button[aria-label="Menu"]';
  private readonly settingsButton = 'button:has-text("Settings"), button[aria-label="Settings"]';
  private readonly exitButton = 'button:has-text("Exit"), button:has-text("Leave Game")';

  /**
   * Navigate to gameplay page
   */
  async goto(): Promise<void> {
    await this.page.goto('/gameplay');
    await this.waitForPageLoad();
    await this.expectGameplayLoaded();
  }

  /**
   * Expect gameplay interface to be loaded
   */
  async expectGameplayLoaded(): Promise<void> {
    await this.expectVisible(this.gameContainer);
    await this.expectVisible(this.storyDisplay);
    await this.expectVisible(this.chatInput);
  }

  /**
   * Send a message to the AI
   */
  async sendMessage(message: string): Promise<void> {
    await this.fillInput(this.chatInput, message);
    await this.clickElement(this.sendButton);
    
    // Wait for AI response
    await this.waitForAiResponse();
  }

  /**
   * Wait for AI response to appear
   */
  async waitForAiResponse(timeout: number = STAGING_CONFIG.timeouts.aiResponse): Promise<void> {
    // Wait for loading to appear and disappear
    try {
      await this.page.waitForSelector(this.loadingIndicator, { state: 'visible', timeout: 2000 });
      await this.page.waitForSelector(this.loadingIndicator, { state: 'hidden', timeout });
    } catch {
      // Loading indicator might not appear, just wait for response
      await this.page.waitForSelector(this.aiResponse, { state: 'visible', timeout });
    }
  }

  /**
   * Get the latest AI response text
   */
  async getLatestAiResponse(): Promise<string | null> {
    const responses = this.getElements(this.aiResponse);
    const count = await responses.count();
    
    if (count === 0) {
      return null;
    }
    
    return await responses.nth(count - 1).textContent();
  }

  /**
   * Get all chat messages
   */
  async getAllChatMessages(): Promise<string[]> {
    return await this.getAllTextContents(`${this.chatHistory} [data-testid="message"], ${this.chatHistory} .message`);
  }

  /**
   * Get character name from display
   */
  async getCharacterName(): Promise<string | null> {
    return await this.getTextContent(`${this.characterInfo} [data-testid="name"], ${this.characterInfo} .name`);
  }

  /**
   * Get world name from display
   */
  async getWorldName(): Promise<string | null> {
    return await this.getTextContent(`${this.worldInfo} [data-testid="name"], ${this.worldInfo} .name`);
  }

  /**
   * Get story text
   */
  async getStoryText(): Promise<string | null> {
    return await this.getTextContent(this.storyDisplay);
  }

  /**
   * Verify story content is not empty
   */
  async expectStoryContent(): Promise<void> {
    const storyText = await this.getStoryText();
    expect(storyText).toBeTruthy();
    expect(storyText?.length).toBeGreaterThan(0);
  }

  /**
   * Verify chat history is populated
   */
  async expectChatHistory(): Promise<void> {
    const messages = await this.getAllChatMessages();
    expect(messages.length).toBeGreaterThan(0);
  }

  /**
   * Click action button
   */
  async clickActionButton(index: number = 0): Promise<void> {
    const buttons = this.getElements(this.actionButtons);
    await buttons.nth(index).click();
    await this.waitForPageLoad();
  }

  /**
   * Get available action buttons
   */
  async getActionButtonCount(): Promise<number> {
    return await this.getElements(this.actionButtons).count();
  }

  /**
   * Open menu
   */
  async openMenu(): Promise<void> {
    await this.clickElement(this.menuButton);
  }

  /**
   * Open settings
   */
  async openSettings(): Promise<void> {
    await this.clickElement(this.settingsButton);
  }

  /**
   * Exit game
   */
  async exitGame(): Promise<void> {
    await this.clickElement(this.exitButton);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Expect error alert
   */
  async expectErrorAlert(): Promise<void> {
    await this.expectVisible(this.errorAlert);
  }

  /**
   * Get error message
   */
  async getErrorMessage(): Promise<string | null> {
    return await this.getTextContent(this.errorAlert);
  }

  /**
   * Verify chat input is enabled
   */
  async expectChatInputEnabled(): Promise<void> {
    const input = this.getElement(this.chatInput);
    await expect(input).toBeEnabled();
  }

  /**
   * Verify send button is enabled
   */
  async expectSendButtonEnabled(): Promise<void> {
    const button = this.getElement(this.sendButton);
    await expect(button).toBeEnabled();
  }

  /**
   * Measure message response time
   */
  async measureResponseTime(): Promise<number> {
    const startTime = Date.now();
    await this.waitForAiResponse();
    return Date.now() - startTime;
  }
}

