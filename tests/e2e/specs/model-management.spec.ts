import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { ModelManagementPage } from '../page-objects/ModelManagementPage';
import { testUsers } from '../fixtures/test-data';
import { mockApiResponse } from '../utils/test-helpers';

test.describe('Model Management', () => {
  let loginPage: LoginPage;
  let modelManagementPage: ModelManagementPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    modelManagementPage = new ModelManagementPage(page);
    
    // Mock API responses for model management
    await mockApiResponse(page, '**/models', [
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo',
        provider: 'openai',
        cost_per_token: 0.002,
        max_tokens: 4096,
        is_free: false,
        performance_score: 8.5,
        description: 'Fast and efficient model for general tasks',
      },
      {
        id: 'llama-2-7b',
        name: 'Llama 2 7B',
        provider: 'meta',
        cost_per_token: 0.0,
        max_tokens: 4096,
        is_free: true,
        performance_score: 7.2,
        description: 'Open source model suitable for basic tasks',
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet',
        provider: 'anthropic',
        cost_per_token: 0.003,
        max_tokens: 200000,
        is_free: false,
        performance_score: 9.1,
        description: 'Advanced model with excellent reasoning capabilities',
      },
    ]);

    await mockApiResponse(page, '**/openrouter/auth/status', {
      authenticated: false,
      api_key_valid: false,
    });

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Page Loading and Navigation', () => {
    test('should load model management page correctly', async () => {
      await modelManagementPage.goto();
      await modelManagementPage.expectPageLoaded();
    });

    test('should display current model status', async () => {
      await modelManagementPage.goto();
      await expect(modelManagementPage.currentModelDisplay).toBeVisible();
      await expect(modelManagementPage.modelStatusIndicator).toBeVisible();
    });
  });

  test.describe('OpenRouter Authentication', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
    });

    test('should connect to OpenRouter with valid API key', async ({ page }) => {
      await mockApiResponse(page, '**/openrouter/auth/connect', {
        success: true,
        authenticated: true,
      }, 200, 'POST');

      await modelManagementPage.connectOpenRouter('test-api-key-123');
      await modelManagementPage.expectAuthenticationSuccess();
    });

    test('should handle invalid API key', async ({ page }) => {
      await mockApiResponse(page, '**/openrouter/auth/connect', {
        success: false,
        error: 'Invalid API key',
      }, 401, 'POST');

      await modelManagementPage.connectOpenRouter('invalid-key');
      await modelManagementPage.expectAuthenticationError();
    });

    test('should disconnect from OpenRouter', async ({ page }) => {
      // First connect
      await mockApiResponse(page, '**/openrouter/auth/connect', {
        success: true,
        authenticated: true,
      }, 200, 'POST');
      
      await modelManagementPage.connectOpenRouter('test-api-key-123');
      await modelManagementPage.expectAuthenticationSuccess();

      // Then disconnect
      await mockApiResponse(page, '**/openrouter/auth/disconnect', {
        success: true,
        authenticated: false,
      }, 200, 'POST');

      await modelManagementPage.disconnectOpenRouter();
      await expect(modelManagementPage.authStatusDisplay).toContainText('Disconnected');
    });

    test('should handle connection errors', async ({ page }) => {
      await page.route('**/openrouter/auth/connect', route => {
        route.fulfill({ status: 500, body: 'Server Error' });
      });

      await modelManagementPage.connectOpenRouter('test-api-key-123');
      await modelManagementPage.expectConnectionError();
    });
  });

  test.describe('Model Selection', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
    });

    test('should select different models', async () => {
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
      await modelManagementPage.expectModelSelected('GPT-3.5 Turbo');
      
      await modelManagementPage.selectModel('Claude 3 Sonnet');
      await modelManagementPage.expectModelSelected('Claude 3 Sonnet');
    });

    test('should search for models', async () => {
      await modelManagementPage.searchModels('GPT');
      
      // Should show only GPT models
      await expect(modelManagementPage.modelOptions.locator('text=GPT')).toBeVisible();
      await expect(modelManagementPage.modelOptions.locator('text=Claude')).not.toBeVisible();
    });

    test('should filter free models', async () => {
      await modelManagementPage.filterFreeModels();
      
      // Should show only free models
      await expect(modelManagementPage.modelOptions.locator('text=Llama 2 7B')).toBeVisible();
      await expect(modelManagementPage.modelOptions.locator('text=GPT-3.5 Turbo')).not.toBeVisible();
    });

    test('should filter paid models', async () => {
      await modelManagementPage.filterPaidModels();
      
      // Should show only paid models
      await expect(modelManagementPage.modelOptions.locator('text=GPT-3.5 Turbo')).toBeVisible();
      await expect(modelManagementPage.modelOptions.locator('text=Llama 2 7B')).not.toBeVisible();
    });

    test('should show all models', async () => {
      await modelManagementPage.filterFreeModels();
      await modelManagementPage.showAllModels();
      
      // Should show all models again
      await expect(modelManagementPage.modelOptions.locator('text=GPT-3.5 Turbo')).toBeVisible();
      await expect(modelManagementPage.modelOptions.locator('text=Llama 2 7B')).toBeVisible();
    });

    test('should display model information', async () => {
      await modelManagementPage.selectModel('Claude 3 Sonnet');
      await modelManagementPage.expectModelInfo('Claude 3 Sonnet');
      
      await expect(modelManagementPage.modelDescription).toContainText('Advanced model');
      await expect(modelManagementPage.modelCostDisplay).toBeVisible();
    });
  });

  test.describe('Model Configuration', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
    });

    test('should configure temperature', async () => {
      await modelManagementPage.setTemperature(0.7);
      await modelManagementPage.expectTemperature(0.7);
    });

    test('should configure max tokens', async () => {
      await modelManagementPage.setMaxTokens(2048);
      await expect(modelManagementPage.maxTokensInput).toHaveValue('2048');
    });

    test('should configure top-p', async () => {
      await modelManagementPage.setTopP(0.9);
      await expect(modelManagementPage.topPSlider).toHaveValue('0.9');
    });

    test('should configure frequency penalty', async () => {
      await modelManagementPage.setFrequencyPenalty(0.5);
      await expect(modelManagementPage.frequencyPenaltySlider).toHaveValue('0.5');
    });

    test('should configure presence penalty', async () => {
      await modelManagementPage.setPresencePenalty(0.3);
      await expect(modelManagementPage.presencePenaltySlider).toHaveValue('0.3');
    });

    test('should validate parameter bounds', async () => {
      // Temperature should be between 0 and 2
      await modelManagementPage.setTemperature(3);
      await modelManagementPage.expectTemperature(2); // Should clamp to max
      
      await modelManagementPage.setTemperature(-1);
      await modelManagementPage.expectTemperature(0); // Should clamp to min
    });
  });

  test.describe('Advanced Settings', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
    });

    test('should toggle advanced settings', async () => {
      await modelManagementPage.toggleAdvancedSettings();
      await expect(modelManagementPage.systemPromptTextarea).toBeVisible();
      await expect(modelManagementPage.stopSequencesInput).toBeVisible();
    });

    test('should configure system prompt', async () => {
      await modelManagementPage.toggleAdvancedSettings();
      await modelManagementPage.setSystemPrompt('You are a helpful therapeutic assistant.');
      await expect(modelManagementPage.systemPromptTextarea).toHaveValue('You are a helpful therapeutic assistant.');
    });

    test('should configure stop sequences', async () => {
      await modelManagementPage.toggleAdvancedSettings();
      await modelManagementPage.setStopSequences('\\n\\n,END');
      await expect(modelManagementPage.stopSequencesInput).toHaveValue('\\n\\n,END');
    });

    test('should configure seed for reproducibility', async () => {
      await modelManagementPage.toggleAdvancedSettings();
      await modelManagementPage.setSeed(12345);
      await expect(modelManagementPage.seedInput).toHaveValue('12345');
    });
  });

  test.describe('Model Testing', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
    });

    test('should test model with prompt', async ({ page }) => {
      await mockApiResponse(page, '**/models/test', {
        response: 'This is a test response from the model.',
        tokens_used: 25,
        response_time: 1.2,
      }, 200, 'POST');

      await modelManagementPage.testModel('Hello, how are you?');
      await modelManagementPage.expectTestResponse();
      
      await expect(modelManagementPage.testResponseDisplay).toContainText('This is a test response');
    });

    test('should handle test errors', async ({ page }) => {
      await mockApiResponse(page, '**/models/test', {
        error: 'Model not available',
      }, 500, 'POST');

      await modelManagementPage.testModel('Hello, how are you?');
      await modelManagementPage.expectTestError();
    });

    test('should measure test response time', async ({ page }) => {
      await mockApiResponse(page, '**/models/test', {
        response: 'Test response',
        tokens_used: 10,
        response_time: 0.8,
      }, 200, 'POST');

      const responseTime = await modelManagementPage.measureTestResponseTime('Test prompt');
      expect(responseTime).toBeLessThan(5000); // 5 seconds
    });
  });

  test.describe('Configuration Management', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
    });

    test('should save configuration', async ({ page }) => {
      await mockApiResponse(page, '**/models/config', {
        success: true,
      }, 200, 'POST');

      await modelManagementPage.setTemperature(0.8);
      await modelManagementPage.setMaxTokens(1024);
      
      await modelManagementPage.saveConfiguration();
      await modelManagementPage.expectConfigurationSaved();
    });

    test('should apply changes', async ({ page }) => {
      await mockApiResponse(page, '**/models/apply', {
        success: true,
      }, 200, 'POST');

      await modelManagementPage.setTemperature(0.6);
      await modelManagementPage.applyChanges();
      
      await expect(modelManagementPage.page.locator('text=Changes applied')).toBeVisible();
    });

    test('should reset to defaults', async () => {
      await modelManagementPage.setTemperature(0.9);
      await modelManagementPage.setMaxTokens(512);
      
      await modelManagementPage.resetToDefaults();
      
      // Should reset to default values
      await modelManagementPage.expectTemperature(0.7); // Assuming default
      await expect(modelManagementPage.maxTokensInput).toHaveValue('4096'); // Assuming default
    });

    test('should show unsaved changes indicator', async () => {
      await modelManagementPage.setTemperature(0.9);
      await modelManagementPage.expectUnsavedChanges();
    });

    test('should handle save errors', async ({ page }) => {
      await mockApiResponse(page, '**/models/config', {
        error: 'Failed to save configuration',
      }, 500, 'POST');

      await modelManagementPage.setTemperature(0.8);
      await modelManagementPage.saveConfiguration();
      
      await modelManagementPage.expectGeneralError('Failed to save configuration');
    });
  });

  test.describe('Performance', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
    });

    test('should switch models quickly', async () => {
      const switchTime = await modelManagementPage.measureModelSwitchTime('Claude 3 Sonnet');
      expect(switchTime).toBeLessThan(2000); // 2 seconds
    });

    test('should load model list efficiently', async ({ page }) => {
      const startTime = Date.now();
      await modelManagementPage.goto();
      await expect(modelManagementPage.modelDropdown).toBeVisible();
      const loadTime = Date.now() - startTime;
      
      expect(loadTime).toBeLessThan(3000); // 3 seconds
    });
  });

  test.describe('Accessibility', () => {
    test.beforeEach(async () => {
      await modelManagementPage.goto();
    });

    test('should support keyboard navigation', async () => {
      await modelManagementPage.testKeyboardNavigation();
    });

    test('should have proper screen reader support', async () => {
      await modelManagementPage.testScreenReaderSupport();
    });

    test('should have proper focus management', async () => {
      await modelManagementPage.modelDropdown.focus();
      await expect(modelManagementPage.modelDropdown).toBeFocused();
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await modelManagementPage.goto();
      await modelManagementPage.expectPageLoaded();
      
      // Test model selection on mobile
      await modelManagementPage.selectModel('GPT-3.5 Turbo');
      await modelManagementPage.expectModelSelected('GPT-3.5 Turbo');
    });

    test('should adapt to tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await modelManagementPage.goto();
      await modelManagementPage.expectPageLoaded();
      
      // Test configuration on tablet
      await modelManagementPage.selectModel('Claude 3 Sonnet');
      await modelManagementPage.setTemperature(0.8);
      await modelManagementPage.expectTemperature(0.8);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/models', route => {
        route.fulfill({ status: 500, body: 'Server Error' });
      });

      await modelManagementPage.goto();
      await modelManagementPage.expectGeneralError('Server Error');
    });

    test('should handle network timeouts', async ({ page }) => {
      await page.route('**/models', route => {
        // Never resolve to simulate timeout
      });

      await modelManagementPage.goto();
      // Should show loading state indefinitely
      await expect(modelManagementPage.page.locator('.loading, .spinner')).toBeVisible();
    });

    test('should handle model unavailability', async ({ page }) => {
      await mockApiResponse(page, '**/models/gpt-3.5-turbo/select', {
        error: 'Model temporarily unavailable',
      }, 503, 'POST');

      await modelManagementPage.selectModel('GPT-3.5 Turbo');
      await modelManagementPage.expectGeneralError('Model temporarily unavailable');
    });
  });
});
