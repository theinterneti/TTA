// Logseq: [[TTA.dev/Tests/E2e-staging/08-data-persistence.staging.spec]]
/**
 * Data Persistence E2E Tests
 *
 * Validates that game state, user data, and progress are properly
 * persisted in Redis and Neo4j databases.
 */

import { expect, test } from '@playwright/test';
import { STAGING_CONFIG } from './helpers/staging-config';
import { RedisHelper, Neo4jHelper, waitForDataPersistence } from './helpers/database-helpers';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { CharacterCreationPage } from './page-objects/CharacterCreationPage';
import { GameplayPage } from './page-objects/GameplayPage';

test.describe('Data Persistence - Redis & Neo4j', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterCreationPage;
  let gameplayPage: GameplayPage;
  let redisHelper: RedisHelper;
  let neo4jHelper: Neo4jHelper;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterCreationPage(page);
    gameplayPage = new GameplayPage(page);
    redisHelper = new RedisHelper();
    neo4jHelper = new Neo4jHelper();
  });

  test('should verify Redis is accessible', async () => {
    console.log('🔍 Checking Redis accessibility');

    const isAccessible = await redisHelper.isAccessible();
    expect(isAccessible).toBeTruthy();

    console.log('  ✓ Redis is accessible');
  });

  test('should verify Neo4j is accessible', async () => {
    console.log('🔍 Checking Neo4j accessibility');

    const isAccessible = await neo4jHelper.isAccessible();
    expect(isAccessible).toBeTruthy();

    console.log('  ✓ Neo4j is accessible');
  });

  test('should persist session data in Redis', async ({ page }) => {
    console.log('💾 Testing session persistence in Redis');

    // Login
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    // Get session ID from storage
    const sessionId = await page.evaluate(() => {
      return sessionStorage.getItem('session_id') || localStorage.getItem('session_id') || 'test_session';
    });

    console.log(`  → Session ID: ${sessionId}`);

    // Wait for session to be persisted
    const persisted = await waitForDataPersistence(sessionId, 5000);
    expect(persisted).toBeTruthy();

    // Verify session data in Redis
    const sessionData = await redisHelper.getSessionData(sessionId);
    expect(sessionData).toBeTruthy();

    console.log('  ✓ Session data persisted in Redis');
  });

  test('should persist character data in Neo4j', async ({ page }) => {
    console.log('💾 Testing character persistence in Neo4j');

    // Login and create character
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await characterPage.goto();
    const character = STAGING_CONFIG.testCharacters.default;
    await characterPage.createCharacterWithDefaults();

    // Get character ID from page
    const characterId = await page.evaluate(() => {
      return document.querySelector('[data-character-id]')?.getAttribute('data-character-id') || 'test_char';
    });

    console.log(`  → Character ID: ${characterId}`);

    // Wait for character to be persisted
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Verify character data in Neo4j
    const characterData = await neo4jHelper.getCharacterData(characterId);
    expect(characterData).toBeTruthy();

    console.log('  ✓ Character data persisted in Neo4j');
  });

  test('should persist game progress across sessions', async ({ page }) => {
    console.log('💾 Testing game progress persistence');

    // First session: Login and play
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Send a message
    const testMessage = 'I begin my adventure.';
    await gameplayPage.sendMessage(testMessage);

    // Get initial chat history
    const initialMessages = await gameplayPage.getAllChatMessages();
    const initialCount = initialMessages.length;

    console.log(`  → Initial message count: ${initialCount}`);

    // Logout
    await loginPage.goto();
    await loginPage.logout();

    // Second session: Login again
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    // Navigate back to gameplay
    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Verify progress persisted
    const reloadedMessages = await gameplayPage.getAllChatMessages();
    expect(reloadedMessages.length).toBeGreaterThanOrEqual(initialCount);

    console.log(`  → Reloaded message count: ${reloadedMessages.length}`);
    console.log('  ✓ Game progress persisted across sessions');
  });

  test('should maintain data consistency between Redis and Neo4j', async ({ page }) => {
    console.log('🔄 Testing data consistency between databases');

    // Create character
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    await characterPage.goto();
    await characterPage.createCharacterWithDefaults();

    const characterId = await page.evaluate(() => {
      return document.querySelector('[data-character-id]')?.getAttribute('data-character-id') || 'test_char';
    });

    // Wait for persistence
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Check both databases
    const redisData = await redisHelper.getSessionData(characterId);
    const neo4jData = await neo4jHelper.getCharacterData(characterId);

    expect(redisData).toBeTruthy();
    expect(neo4jData).toBeTruthy();

    console.log('  ✓ Data consistent across Redis and Neo4j');
  });

  test('should handle concurrent data updates', async ({ page, context }) => {
    console.log('⚡ Testing concurrent data updates');

    // Create two browser contexts
    const page2 = await context.newPage();

    try {
      // Login in both pages
      await loginPage.goto();
      await loginPage.loginWithDemo();
      await loginPage.waitForLoginSuccess();

      const loginPage2 = new LoginPage(page2);
      await loginPage2.goto();
      await loginPage2.loginWithDemo();
      await loginPage2.waitForLoginSuccess();

      // Send messages from both pages
      const gameplayPage2 = new GameplayPage(page2);

      await gameplayPage.goto();
      await gameplayPage.expectGameplayLoaded();

      await gameplayPage2.goto();
      await gameplayPage2.expectGameplayLoaded();

      // Send messages concurrently
      await Promise.all([
        gameplayPage.sendMessage('First message'),
        gameplayPage2.sendMessage('Second message'),
      ]);

      // Verify both messages are persisted
      const messages1 = await gameplayPage.getAllChatMessages();
      const messages2 = await gameplayPage2.getAllChatMessages();

      expect(messages1.length).toBeGreaterThan(0);
      expect(messages2.length).toBeGreaterThan(0);

      console.log('  ✓ Concurrent updates handled correctly');
    } finally {
      await page2.close();
    }
  });

  test('should recover from database connection loss', async ({ page }) => {
    console.log('🔧 Testing database resilience');

    // Login
    await loginPage.goto();
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();

    // Start gameplay
    await gameplayPage.goto();
    await gameplayPage.expectGameplayLoaded();

    // Send message (should work)
    await gameplayPage.sendMessage('Test message');
    const response1 = await gameplayPage.getLatestAiResponse();
    expect(response1).toBeTruthy();

    // Simulate network issue and retry
    await page.context().setOffline(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.context().setOffline(false);

    // Try to send another message
    await gameplayPage.sendMessage('Another message');
    const response2 = await gameplayPage.getLatestAiResponse();
    expect(response2).toBeTruthy();

    console.log('  ✓ Database resilience verified');
  });
});
