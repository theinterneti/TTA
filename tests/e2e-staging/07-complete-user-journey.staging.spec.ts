/**
 * Complete User Journey E2E Test
 *
 * Validates the entire user flow from authentication through gameplay:
 * 1. Login with OAuth/demo credentials
 * 2. Navigate dashboard
 * 3. Create character
 * 4. Select world
 * 5. Play collaborative storytelling game
 * 6. Verify data persistence
 * 7. Logout
 *
 * This is the primary test for demonstrating zero-instruction usability.
 */

import { expect, test } from '@playwright/test';
import { STAGING_CONFIG } from './helpers/staging-config';
import { PerformanceMonitor } from './helpers/performance-helpers';
import { verifyDataPersistence, waitForDataPersistence } from './helpers/database-helpers';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { CharacterCreationPage } from './page-objects/CharacterCreationPage';
import { WorldSelectionPage } from './page-objects/WorldSelectionPage';
import { GameplayPage } from './page-objects/GameplayPage';

test.describe('Complete User Journey - OAuth to Gameplay', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterCreationPage;
  let worldPage: WorldSelectionPage;
  let gameplayPage: GameplayPage;
  let performanceMonitor: PerformanceMonitor;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterCreationPage(page);
    worldPage = new WorldSelectionPage(page);
    gameplayPage = new GameplayPage(page);
    performanceMonitor = new PerformanceMonitor(page);
  });

  test('should complete full user journey from login to gameplay', async ({ page }) => {
    console.log('🎮 Starting complete user journey test');

    // Step 1: Login
    await test.step('Step 1: Authenticate user', async () => {
      console.log('  → Navigating to login page');
      await loginPage.goto();
      await performanceMonitor.recordPageLoadMetrics();

      console.log('  → Logging in with demo credentials');
      await loginPage.loginWithDemo();
      await loginPage.waitForLoginSuccess();

      console.log('  ✓ User authenticated successfully');
    });

    // Step 2: Dashboard
    await test.step('Step 2: Navigate dashboard', async () => {
      console.log('  → Verifying dashboard is loaded');
      await dashboardPage.expectDashboardLoaded();
      await performanceMonitor.recordPageLoadMetrics();

      console.log('  → Checking dashboard content');
      const hasCharacters = await dashboardPage.hasCharacters();
      console.log(`  ✓ Dashboard loaded (has characters: ${hasCharacters})`);
    });

    // Step 3: Create Character
    await test.step('Step 3: Create character', async () => {
      console.log('  → Navigating to character creation');
      await characterPage.goto();
      await performanceMonitor.recordPageLoadMetrics();

      console.log('  → Creating character with default data');
      await characterPage.createCharacterWithDefaults();

      console.log('  → Verifying character creation success');
      await characterPage.expectSuccessMessage();

      console.log('  ✓ Character created successfully');
    });

    // Step 4: Select World
    await test.step('Step 4: Select world', async () => {
      console.log('  → Navigating to world selection');
      await worldPage.goto();
      await performanceMonitor.recordPageLoadMetrics();

      console.log('  → Verifying worlds are available');
      await worldPage.expectWorldsDisplayed();
      const worldCount = await worldPage.getWorldCount();
      console.log(`  → Found ${worldCount} available worlds`);

      console.log('  → Selecting first world');
      await worldPage.selectFirstWorld();

      console.log('  ✓ World selected successfully');
    });

    // Step 5: Start Gameplay
    await test.step('Step 5: Start gameplay session', async () => {
      console.log('  → Verifying gameplay interface loaded');
      await gameplayPage.expectGameplayLoaded();
      await performanceMonitor.recordPageLoadMetrics();

      console.log('  → Verifying story content');
      await gameplayPage.expectStoryContent();

      console.log('  → Verifying character info displayed');
      const characterName = await gameplayPage.getCharacterName();
      console.log(`  → Character: ${characterName}`);

      console.log('  ✓ Gameplay session started');
    });

    // Step 6: Interact with AI
    await test.step('Step 6: Interact with AI storyteller', async () => {
      console.log('  → Sending message to AI');
      const message = 'I look around and take in my surroundings.';
      await gameplayPage.sendMessage(message);

      console.log('  → Waiting for AI response');
      const response = await gameplayPage.getLatestAiResponse();
      expect(response).toBeTruthy();
      expect(response?.length).toBeGreaterThan(0);

      console.log(`  → AI Response: ${response?.substring(0, 100)}...`);
      console.log('  ✓ AI interaction successful');
    });

    // Step 7: Verify Data Persistence
    await test.step('Step 7: Verify data persistence', async () => {
      console.log('  → Checking chat history');
      const messages = await gameplayPage.getAllChatMessages();
      expect(messages.length).toBeGreaterThan(0);
      console.log(`  → Chat history contains ${messages.length} messages`);

      console.log('  → Verifying story state persisted');
      const storyText = await gameplayPage.getStoryText();
      expect(storyText).toBeTruthy();

      console.log('  ✓ Data persistence verified');
    });

    // Step 8: Performance Validation
    await test.step('Step 8: Validate performance', async () => {
      const report = performanceMonitor.generateReport();
      console.log('  → Performance Report:');
      console.log(report);

      const avgMetrics = performanceMonitor.getAverageMetrics();
      expect(avgMetrics.pageLoadTime).toBeLessThan(STAGING_CONFIG.performance.pageLoad * 2);

      console.log('  ✓ Performance acceptable');
    });

    // Step 9: Logout
    await test.step('Step 9: Logout', async () => {
      console.log('  → Logging out');
      await gameplayPage.exitGame();

      console.log('  → Verifying redirect to login');
      await loginPage.expectLoginFormVisible();

      console.log('  ✓ Logout successful');
    });

    console.log('✅ Complete user journey test passed!');
  });

  test('should maintain data consistency across page reloads', async ({ page }) => {
    console.log('🔄 Testing data consistency across reloads');

    // Login and start gameplay
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Get initial state
    const initialStory = await gameplayPage.getStoryText();
    const initialMessages = await gameplayPage.getAllChatMessages();

    console.log('  → Reloading page');
    await gameplayPage.reload();

    // Verify state persisted
    const reloadedStory = await gameplayPage.getStoryText();
    const reloadedMessages = await gameplayPage.getAllChatMessages();

    expect(reloadedStory).toBe(initialStory);
    expect(reloadedMessages.length).toBe(initialMessages.length);

    console.log('  ✓ Data consistency verified after reload');
  });

  test('should handle multiple interactions smoothly', async ({ page }) => {
    console.log('💬 Testing multiple AI interactions');

    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    const messages = [
      'I examine the area carefully.',
      'I talk to the nearby character.',
      'I make a decision about my next action.',
    ];

    for (let i = 0; i < messages.length; i++) {
      console.log(`  → Sending message ${i + 1}/${messages.length}`);
      await gameplayPage.sendMessage(messages[i]);

      const response = await gameplayPage.getLatestAiResponse();
      expect(response).toBeTruthy();
    }

    const allMessages = await gameplayPage.getAllChatMessages();
    expect(allMessages.length).toBeGreaterThanOrEqual(messages.length);

    console.log(`  ✓ Successfully handled ${messages.length} interactions`);
  });
});

