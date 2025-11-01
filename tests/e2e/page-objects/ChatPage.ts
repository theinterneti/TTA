import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Chat/Storytelling Page
 */
export class ChatPage extends BasePage {
  // Locators
  readonly chatContainer: Locator;
  readonly messageHistory: Locator;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly messageList: Locator;
  readonly userMessages: Locator;
  readonly assistantMessages: Locator;
  readonly systemMessages: Locator;
  readonly typingIndicator: Locator;
  readonly connectionStatus: Locator;
  readonly sessionInfo: Locator;
  readonly characterInfo: Locator;
  readonly worldInfo: Locator;
  readonly exitChatButton: Locator;
  readonly settingsButton: Locator;
  readonly helpButton: Locator;

  // Interactive elements
  readonly interactiveButtons: Locator;
  readonly choiceButtons: Locator;
  readonly guidedExercises: Locator;
  readonly progressFeedback: Locator;
  readonly feedbackButtons: Locator;
  readonly crisisAlert: Locator;
  readonly safetyIndicator: Locator;

  // Accessibility elements
  readonly skipLinks: Locator;
  readonly screenReaderAnnouncements: Locator;
  readonly messageNavigation: Locator;

  constructor(page: Page) {
    super(page);

    // Initialize locators
    this.chatContainer = page.locator('[data-testid="chat-container"], .chat-container');
    this.messageHistory = page.locator('[data-testid="message-history"], .message-history');
    this.messageInput = page.locator('input[data-testid="message-input"], textarea[placeholder*="message"]');
    this.sendButton = page.locator('button[data-testid="send-button"], button').filter({ hasText: /send/i });
    this.messageList = page.locator('[data-testid="message-list"], .message-list');
    this.userMessages = page.locator('[data-testid="user-message"], .user-message');
    this.assistantMessages = page.locator('[data-testid="assistant-message"], .assistant-message');
    this.systemMessages = page.locator('[data-testid="system-message"], .system-message');
    this.typingIndicator = page.locator('[data-testid="typing-indicator"], .typing-indicator');
    this.connectionStatus = page.locator('[data-testid="connection-status"], .connection-status');

    // Session info
    this.sessionInfo = page.locator('[data-testid="session-info"], .session-info');
    this.characterInfo = page.locator('[data-testid="character-info"], .character-info');
    this.worldInfo = page.locator('[data-testid="world-info"], .world-info');

    // Navigation
    this.exitChatButton = page.locator('button').filter({ hasText: /exit|leave|back/i });
    this.settingsButton = page.locator('button[data-testid="chat-settings"], .settings-button');
    this.helpButton = page.locator('button[data-testid="help"], .help-button');

    // Interactive elements
    this.interactiveButtons = page.locator('[data-testid="interactive-button"], .interactive-button');
    this.choiceButtons = page.locator('[data-testid="choice-button"], .choice-button');
    this.guidedExercises = page.locator('[data-testid="guided-exercise"], .guided-exercise');
    this.progressFeedback = page.locator('[data-testid="progress-feedback"], .progress-feedback');
    this.feedbackButtons = page.locator('[data-testid="feedback-button"], .feedback-button');
    this.crisisAlert = page.locator('[data-testid="crisis-alert"], .crisis-alert');
    this.safetyIndicator = page.locator('[data-testid="safety-indicator"], .safety-indicator');

    // Accessibility
    this.skipLinks = page.locator('a[href^="#"]');
    this.screenReaderAnnouncements = page.locator('[aria-live], [data-testid="sr-announcement"]');
    this.messageNavigation = page.locator('[data-testid="message-navigation"]');
  }

  // Navigation
  async goto(sessionId?: string) {
    const path = sessionId ? `/chat/${sessionId}` : '/chat';
    await super.goto(path);
    await this.waitForPageLoad();
  }

  // Actions
  async sendMessage(message: string) {
    await this.messageInput.fill(message);
    await this.sendButton.click();
    await this.waitForMessageSent();
  }

  async sendMessageWithEnter(message: string) {
    await this.messageInput.fill(message);
    await this.messageInput.press('Enter');
    await this.waitForMessageSent();
  }

  async waitForMessageSent() {
    // Wait for message to appear in history
    await this.page.waitForTimeout(500);
    await this.waitForLoadingToComplete();
  }

  async waitForAssistantResponse() {
    await expect(this.typingIndicator).toBeVisible();
    await expect(this.typingIndicator).toBeHidden({ timeout: 30000 });
  }

  async selectChoice(choiceText: string) {
    const choiceButton = this.choiceButtons.filter({ hasText: choiceText });
    await choiceButton.click();
    await this.waitForAssistantResponse();
  }

  async clickInteractiveElement(elementText: string) {
    const interactiveElement = this.interactiveButtons.filter({ hasText: elementText });
    await interactiveElement.click();
  }

  async provideFeedback(messageIndex: number, feedback: 'helpful' | 'not_helpful') {
    const message = this.assistantMessages.nth(messageIndex);
    const feedbackButton = message.locator(`[data-feedback="${feedback}"]`);
    await feedbackButton.click();
  }

  async exitChat() {
    await this.exitChatButton.click();
    await this.page.waitForURL(/dashboard|characters/);
  }

  // Validations
  async expectChatLoaded() {
    await expect(this.chatContainer).toBeVisible();
    await expect(this.messageInput).toBeVisible();
    await expect(this.sendButton).toBeVisible();
    await this.waitForLoadingToComplete();
  }

  async expectConnected() {
    await expect(this.connectionStatus).toContainText(/connected|online/i);
  }

  async expectDisconnected() {
    await expect(this.connectionStatus).toContainText(/disconnected|offline/i);
  }

  async expectMessageSent(messageText: string) {
    const userMessage = this.userMessages.filter({ hasText: messageText });
    await expect(userMessage).toBeVisible();
  }

  async expectAssistantResponse() {
    await this.waitForAssistantResponse();
    await expect(this.assistantMessages.last()).toBeVisible();
  }

  async expectMessageCount(count: number) {
    const allMessages = this.page.locator('[data-testid*="message"]');
    await expect(allMessages).toHaveCount(count);
  }

  async expectChoicesAvailable() {
    await expect(this.choiceButtons.first()).toBeVisible();
  }

  async expectGuidedExercise() {
    await expect(this.guidedExercises.first()).toBeVisible();
  }

  async expectCrisisSupport() {
    await expect(this.crisisAlert).toBeVisible();
    // Should show crisis support resources
    const crisisResources = this.page.locator('[data-testid="crisis-resources"]');
    await expect(crisisResources).toBeVisible();
  }

  async expectSafetyLevel(level: 'safe' | 'caution' | 'crisis') {
    await expect(this.safetyIndicator).toHaveAttribute('data-safety-level', level);
  }

  // Conversation flow tests
  async startConversation() {
    await this.sendMessage('Hello, I\'d like to start my therapeutic journey.');
    await this.expectAssistantResponse();
  }

  async continueConversation(messages: string[]) {
    for (const message of messages) {
      await this.sendMessage(message);
      await this.expectAssistantResponse();
    }
  }

  async expectTherapeuticContent() {
    // Check for therapeutic techniques in responses
    const therapeuticKeywords = /mindfulness|coping|breathing|reflection|feelings|emotions/i;
    const lastResponse = this.assistantMessages.last();
    await expect(lastResponse).toContainText(therapeuticKeywords);
  }

  // Accessibility tests
  async checkAccessibility() {
    await super.checkAccessibility();

    // Check skip links
    await expect(this.skipLinks.first()).toBeVisible();

    // Check ARIA live regions
    await expect(this.screenReaderAnnouncements.first()).toHaveAttribute('aria-live');

    // Check message accessibility
    const messages = this.page.locator('[role="article"]');
    await expect(messages.first()).toHaveRole('article');

    // Check input accessibility
    await expect(this.messageInput).toHaveAttribute('aria-label');
  }

  // Keyboard navigation
  async navigateWithKeyboard() {
    // Test message input focus
    await this.messageInput.focus();
    await expect(this.messageInput).toBeFocused();

    // Test Enter key for sending
    await this.messageInput.fill('Test message');
    await this.messageInput.press('Enter');
    await this.expectMessageSent('Test message');

    // Test Escape key for clearing input
    await this.messageInput.fill('Test');
    await this.messageInput.press('Escape');
    await expect(this.messageInput).toHaveValue('');
  }

  async navigateMessages() {
    // Test arrow key navigation through messages
    await this.page.keyboard.press('ArrowUp');
    await this.page.keyboard.press('ArrowDown');
  }

  // Mobile responsiveness
  async checkMobileLayout() {
    await this.setMobileViewport();
    await this.expectChatLoaded();

    // Check that chat takes full screen on mobile
    const chatBox = await this.chatContainer.boundingBox();
    expect(chatBox?.width).toBeLessThan(400);

    // Check that input is properly sized
    const inputBox = await this.messageInput.boundingBox();
    expect(inputBox?.width).toBeLessThan(350);
  }

  // Real-time functionality
  async expectRealTimeUpdates() {
    // Send message and expect immediate UI update
    const initialMessageCount = await this.userMessages.count();
    await this.sendMessage('Real-time test');

    const newMessageCount = await this.userMessages.count();
    expect(newMessageCount).toBe(initialMessageCount + 1);
  }

  // Performance tests
  async measureResponseTime() {
    const startTime = Date.now();
    await this.sendMessage('Performance test message');
    await this.expectAssistantResponse();
    const endTime = Date.now();

    const responseTime = endTime - startTime;
    expect(responseTime).toBeLessThan(10000); // Should respond within 10 seconds

    return responseTime;
  }

  // Error handling
  async expectConnectionError() {
    const errorMessage = this.page.locator('[data-testid="connection-error"], .error');
    await expect(errorMessage).toBeVisible();
  }

  async expectMessageError() {
    const errorMessage = this.page.locator('[data-testid="message-error"], .message-error');
    await expect(errorMessage).toBeVisible();
  }

  // Session management
  async expectSessionInfo(characterName?: string, worldName?: string) {
    await expect(this.sessionInfo).toBeVisible();

    if (characterName) {
      await expect(this.characterInfo).toContainText(characterName);
    }

    if (worldName) {
      await expect(this.worldInfo).toContainText(worldName);
    }
  }

  async saveSession() {
    const saveButton = this.page.locator('button').filter({ hasText: /save/i });
    await saveButton.click();
  }

  async loadSession(sessionId: string) {
    await this.goto(sessionId);
    await this.expectChatLoaded();
  }
}
