import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { ChatPage } from '../page-objects/ChatPage';
import { testUsers, testMessages } from '../fixtures/test-data';

test.describe('Chat/Storytelling Interface', () => {
  let loginPage: LoginPage;
  let chatPage: ChatPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    chatPage = new ChatPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
    await chatPage.goto();
    await chatPage.expectChatLoaded();
  });

  test.describe('Chat Interface', () => {
    test('should display chat interface correctly', async () => {
      await chatPage.expectChatLoaded();
      await expect(chatPage.messageInput).toBeVisible();
      await expect(chatPage.sendButton).toBeVisible();
      await expect(chatPage.messageHistory).toBeVisible();
    });

    test('should show connection status', async () => {
      await chatPage.expectConnected();
    });

    test('should display session information', async () => {
      await chatPage.expectSessionInfo('Test Character', 'Test World');
    });
  });

  test.describe('Message Sending', () => {
    test('should send message with send button', async () => {
      const message = 'Hello, I would like to start my journey.';
      await chatPage.sendMessage(message);
      await chatPage.expectMessageSent(message);
    });

    test('should send message with Enter key', async () => {
      const message = 'Testing Enter key functionality.';
      await chatPage.sendMessageWithEnter(message);
      await chatPage.expectMessageSent(message);
    });

    test('should clear input after sending', async () => {
      await chatPage.sendMessage('Test message');
      await expect(chatPage.messageInput).toHaveValue('');
    });

    test('should disable send button for empty messages', async () => {
      await chatPage.messageInput.fill('');
      await expect(chatPage.sendButton).toBeDisabled();
    });

    test('should handle long messages', async () => {
      const longMessage = 'This is a very long message that tests how the chat interface handles extended text input. '.repeat(10);
      await chatPage.sendMessage(longMessage);
      await chatPage.expectMessageSent(longMessage);
    });
  });

  test.describe('Message Reception', () => {
    test('should receive assistant responses', async ({ page }) => {
      // Mock WebSocket response
      await page.evaluate(() => {
        // Simulate WebSocket message
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'Welcome to your therapeutic journey!',
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectAssistantResponse();
    });

    test('should show typing indicator', async () => {
      await chatPage.sendMessage('Test message');
      await expect(chatPage.typingIndicator).toBeVisible();
    });

    test('should hide typing indicator after response', async () => {
      await chatPage.sendMessage('Test message');
      await chatPage.waitForAssistantResponse();
      await expect(chatPage.typingIndicator).toBeHidden();
    });

    test('should display different message types', async ({ page }) => {
      // Mock different message types
      const messageTypes = [
        { type: 'user', content: 'User message' },
        { type: 'assistant', content: 'Assistant response' },
        { type: 'system', content: 'System notification' },
      ];
      
      for (const msg of messageTypes) {
        await page.evaluate((message) => {
          window.dispatchEvent(new CustomEvent('websocket-message', {
            detail: {
              ...message,
              timestamp: new Date().toISOString(),
            }
          }));
        }, msg);
      }
      
      await expect(chatPage.userMessages).toHaveCount(1);
      await expect(chatPage.assistantMessages).toHaveCount(1);
      await expect(chatPage.systemMessages).toHaveCount(1);
    });
  });

  test.describe('Interactive Elements', () => {
    test('should display choice buttons', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'What would you like to do?',
            metadata: {
              interactive_elements: {
                choices: [
                  { id: 'choice1', text: 'Explore the forest' },
                  { id: 'choice2', text: 'Visit the village' },
                ]
              }
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectChoicesAvailable();
    });

    test('should handle choice selection', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'Choose your path:',
            metadata: {
              interactive_elements: {
                choices: [
                  { id: 'choice1', text: 'Path of courage' },
                  { id: 'choice2', text: 'Path of wisdom' },
                ]
              }
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.selectChoice('Path of courage');
      await chatPage.expectAssistantResponse();
    });

    test('should display guided exercises', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'Let\'s try a breathing exercise.',
            metadata: {
              interactive_elements: {
                guided_exercise: {
                  type: 'breathing',
                  steps: ['Breathe in', 'Hold', 'Breathe out'],
                }
              }
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectGuidedExercise();
    });

    test('should handle interactive button clicks', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'Click to continue.',
            metadata: {
              interactive_elements: {
                buttons: [
                  { id: 'continue', text: 'Continue Journey' },
                ]
              }
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.clickInteractiveElement('Continue Journey');
    });
  });

  test.describe('Therapeutic Features', () => {
    test('should detect therapeutic content', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'Let\'s practice some mindfulness techniques to help you cope with these feelings.',
            metadata: {
              therapeutic_technique: 'mindfulness',
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectTherapeuticContent();
    });

    test('should show safety indicators', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'I understand you\'re going through a difficult time.',
            metadata: {
              safety_level: 'caution',
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectSafetyLevel('caution');
    });

    test('should trigger crisis support when needed', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'system',
            content: 'Crisis support resources are available.',
            metadata: {
              safety_level: 'crisis',
              safety: { crisis: true },
            },
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.expectCrisisSupport();
    });

    test('should provide feedback options', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'How are you feeling about this approach?',
            id: 'feedback-msg-1',
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      await chatPage.provideFeedback(0, 'helpful');
    });
  });

  test.describe('Conversation Flow', () => {
    test('should maintain conversation context', async () => {
      const conversation = [
        'Hello, I\'m feeling anxious today.',
        'I\'ve been having trouble sleeping.',
        'What techniques can help me relax?',
      ];
      
      await chatPage.continueConversation(conversation);
      await chatPage.expectMessageCount(conversation.length * 2); // User + assistant messages
    });

    test('should handle conversation branching', async () => {
      await chatPage.startConversation();
      await chatPage.selectChoice('Explore feelings');
      await chatPage.expectAssistantResponse();
    });

    test('should save conversation progress', async () => {
      await chatPage.startConversation();
      await chatPage.saveSession();
      
      // Should show save confirmation
      const saveConfirmation = chatPage.page.locator('[data-testid="save-confirmation"]');
      await expect(saveConfirmation).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should be accessible with keyboard navigation', async () => {
      await chatPage.navigateWithKeyboard();
    });

    test('should meet accessibility standards', async () => {
      await chatPage.checkAccessibility();
    });

    test('should support screen reader navigation', async () => {
      await expect(chatPage.skipLinks.first()).toBeVisible();
      await expect(chatPage.screenReaderAnnouncements.first()).toHaveAttribute('aria-live');
    });

    test('should navigate messages with arrow keys', async () => {
      await chatPage.sendMessage('First message');
      await chatPage.sendMessage('Second message');
      await chatPage.navigateMessages();
    });

    test('should announce new messages to screen readers', async ({ page }) => {
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-message', {
          detail: {
            type: 'assistant',
            content: 'New message for screen reader test',
            timestamp: new Date().toISOString(),
          }
        }));
      });
      
      const announcement = chatPage.page.locator('[aria-live="polite"]');
      await expect(announcement).toContainText('New message');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async () => {
      await chatPage.checkMobileLayout();
    });

    test('should adapt input area for mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await chatPage.expectChatLoaded();
      
      const inputBox = await chatPage.messageInput.boundingBox();
      expect(inputBox?.width).toBeLessThan(350);
    });

    test('should handle virtual keyboard on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await chatPage.messageInput.focus();
      
      // Should adjust layout for virtual keyboard
      await expect(chatPage.messageInput).toBeFocused();
    });
  });

  test.describe('Performance', () => {
    test('should respond within acceptable time', async () => {
      const responseTime = await chatPage.measureResponseTime();
      expect(responseTime).toBeLessThan(10000);
    });

    test('should handle real-time updates efficiently', async () => {
      await chatPage.expectRealTimeUpdates();
    });

    test('should handle long conversation history', async ({ page }) => {
      // Simulate long conversation
      const messages = Array.from({ length: 100 }, (_, i) => ({
        type: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}`,
        timestamp: new Date().toISOString(),
      }));
      
      for (const msg of messages) {
        await page.evaluate((message) => {
          window.dispatchEvent(new CustomEvent('websocket-message', {
            detail: message
          }));
        }, msg);
      }
      
      // Should still be responsive
      await chatPage.sendMessage('Performance test message');
      await chatPage.expectMessageSent('Performance test message');
    });
  });

  test.describe('Error Handling', () => {
    test('should handle connection errors', async ({ page }) => {
      // Simulate connection loss
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-disconnect'));
      });
      
      await chatPage.expectConnectionError();
      await chatPage.expectDisconnected();
    });

    test('should handle message send failures', async ({ page }) => {
      // Mock send failure
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('websocket-error', {
          detail: { error: 'Failed to send message' }
        }));
      });
      
      await chatPage.sendMessage('Test message');
      await chatPage.expectMessageError();
    });

    test('should retry failed messages', async ({ page }) => {
      let attemptCount = 0;
      await page.route('**/chat/send', route => {
        attemptCount++;
        if (attemptCount === 1) {
          route.fulfill({ status: 500 });
        } else {
          route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
        }
      });
      
      await chatPage.sendMessage('Retry test message');
      // Should eventually succeed
      await chatPage.expectMessageSent('Retry test message');
    });

    test('should handle session timeout', async ({ page }) => {
      // Simulate session timeout
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('session-timeout'));
      });
      
      const timeoutMessage = chatPage.page.locator('[data-testid="session-timeout"]');
      await expect(timeoutMessage).toBeVisible();
    });
  });

  test.describe('Session Management', () => {
    test('should load existing session', async () => {
      await chatPage.loadSession('existing-session-id');
      await chatPage.expectChatLoaded();
      await chatPage.expectSessionInfo();
    });

    test('should create new session', async () => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      
      // Should show new session indicator
      const newSessionIndicator = chatPage.page.locator('[data-testid="new-session"]');
      await expect(newSessionIndicator).toBeVisible();
    });

    test('should exit chat session', async () => {
      await chatPage.exitChat();
      await expect(chatPage.page).toHaveURL(/dashboard|characters/);
    });
  });
});
