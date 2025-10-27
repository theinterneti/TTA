import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { ChatPage } from '../page-objects/ChatPage';
import { WorldSelectionPage } from '../page-objects/WorldSelectionPage';
import { PreferencesPage } from '../page-objects/PreferencesPage';
import { testUsers, generateRandomCharacter } from '../fixtures/test-data';
import { measurePageLoadTime, measureActionTime, mockApiResponse } from '../utils/test-helpers';

test.describe('Performance Testing', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterManagementPage;
  let chatPage: ChatPage;
  let worldSelectionPage: WorldSelectionPage;
  let preferencesPage: PreferencesPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterManagementPage(page);
    chatPage = new ChatPage(page);
    worldSelectionPage = new WorldSelectionPage(page);
    preferencesPage = new PreferencesPage(page);

    // Mock API responses for consistent performance testing
    await mockApiResponse(page, '**/players/*/characters', []);
    await mockApiResponse(page, '**/worlds', []);
    await mockApiResponse(page, '**/players/*/preferences', {});

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Page Load Performance', () => {
    test('should load dashboard within performance budget', async ({ page }) => {
      const loadTime = await measurePageLoadTime(page, '/dashboard');
      expect(loadTime).toBeLessThan(3000); // 3 seconds
    });

    test('should load character management within performance budget', async ({ page }) => {
      const loadTime = await measurePageLoadTime(page, '/characters');
      expect(loadTime).toBeLessThan(2500); // 2.5 seconds
    });

    test('should load world selection within performance budget', async ({ page }) => {
      const loadTime = await measurePageLoadTime(page, '/worlds');
      expect(loadTime).toBeLessThan(2500); // 2.5 seconds
    });

    test('should load preferences within performance budget', async ({ page }) => {
      const loadTime = await measurePageLoadTime(page, '/preferences');
      expect(loadTime).toBeLessThan(2000); // 2 seconds
    });

    test('should load chat interface within performance budget', async ({ page }) => {
      const loadTime = await measurePageLoadTime(page, '/chat');
      expect(loadTime).toBeLessThan(3000); // 3 seconds (includes WebSocket setup)
    });

    test('should handle concurrent page loads efficiently', async ({ page, context }) => {
      const pages = await Promise.all([
        context.newPage(),
        context.newPage(),
        context.newPage(),
      ]);

      const loadPromises = pages.map(async (p, index) => {
        const routes = ['/dashboard', '/characters', '/worlds'];
        return measurePageLoadTime(p, routes[index]);
      });

      const loadTimes = await Promise.all(loadPromises);

      // All pages should load within reasonable time even when concurrent
      loadTimes.forEach(time => {
        expect(time).toBeLessThan(5000); // 5 seconds for concurrent loads
      });

      // Clean up
      await Promise.all(pages.map(p => p.close()));
    });
  });

  test.describe('User Interaction Performance', () => {
    test('should handle character creation quickly', async ({ page }) => {
      await characterPage.goto();

      const creationTime = await measureActionTime(async () => {
        await mockApiResponse(page, '**/players/*/characters', {
          character_id: 'new-char-1',
          name: 'Test Character',
        }, 201, 'POST');

        const testCharacter = generateRandomCharacter();
        await characterPage.createCharacter(testCharacter);
      });

      expect(creationTime).toBeLessThan(2000); // 2 seconds
    });

    test('should handle world filtering quickly', async ({ page }) => {
      await worldSelectionPage.goto();

      const filterTime = await measureActionTime(async () => {
        await worldSelectionPage.filterByDifficulty('BEGINNER');
      });

      expect(filterTime).toBeLessThan(500); // 500ms
    });

    test('should handle preferences saving quickly', async ({ page }) => {
      await preferencesPage.goto();

      const saveTime = await measureActionTime(async () => {
        await mockApiResponse(page, '**/players/*/preferences', { success: true }, 200, 'PUT');
        await preferencesPage.setIntensityLevel(7);
        await preferencesPage.savePreferences();
      });

      expect(saveTime).toBeLessThan(1500); // 1.5 seconds
    });

    test('should handle chat message sending quickly', async ({ page }) => {
      await chatPage.goto();

      const messageTime = await measureActionTime(async () => {
        await mockApiResponse(page, '**/chat/send', {
          message_id: 'msg-1',
          response: 'Test response',
        }, 200, 'POST');

        await chatPage.sendMessage('Hello, how are you?');
      });

      expect(messageTime).toBeLessThan(1000); // 1 second
    });

    test('should handle rapid user interactions', async ({ page }) => {
      await dashboardPage.goto();

      // Simulate rapid navigation
      const rapidNavigationTime = await measureActionTime(async () => {
        await dashboardPage.navigateToCharacters();
        await characterPage.expectPageLoaded();
        await characterPage.navigateToWorlds();
        await worldSelectionPage.expectPageLoaded();
        await worldSelectionPage.navigateToSettings();
      });

      expect(rapidNavigationTime).toBeLessThan(3000); // 3 seconds for multiple navigations
    });
  });

  test.describe('API Response Performance', () => {
    test('should handle API responses within SLA', async ({ page }) => {
      const apiEndpoints = [
        { url: '**/players/*/characters', expectedTime: 1000 },
        { url: '**/worlds', expectedTime: 1500 },
        { url: '**/players/*/preferences', expectedTime: 800 },
        { url: '**/players/*/progress', expectedTime: 1200 },
      ];

      for (const endpoint of apiEndpoints) {
        const responseTime = await measureActionTime(async () => {
          await page.request.get(endpoint.url.replace('**', 'http://localhost:8000/api/v1'));
        });

        expect(responseTime).toBeLessThan(endpoint.expectedTime);
      }
    });

    test('should handle large dataset responses efficiently', async ({ page }) => {
      // Mock large character list
      const largeCharacterList = Array.from({ length: 100 }, (_, i) => ({
        character_id: `char-${i}`,
        name: `Character ${i}`,
        description: `Description for character ${i}`,
      }));

      await mockApiResponse(page, '**/players/*/characters', largeCharacterList);

      const loadTime = await measureActionTime(async () => {
        await characterPage.goto();
        await characterPage.expectCharacterListLoaded();
      });

      expect(loadTime).toBeLessThan(3000); // 3 seconds for large dataset
    });

    test('should handle concurrent API requests efficiently', async ({ page }) => {
      const concurrentRequests = [
        page.request.get('/api/v1/players/test/characters'),
        page.request.get('/api/v1/worlds'),
        page.request.get('/api/v1/players/test/preferences'),
        page.request.get('/api/v1/players/test/progress'),
      ];

      const startTime = Date.now();
      await Promise.all(concurrentRequests);
      const totalTime = Date.now() - startTime;

      // Concurrent requests should not take much longer than the slowest individual request
      expect(totalTime).toBeLessThan(2000); // 2 seconds
    });
  });

  test.describe('Memory and Resource Usage', () => {
    test('should not have memory leaks during navigation', async ({ page }) => {
      // Get initial memory usage
      const initialMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });

      // Navigate through multiple pages
      const pages = ['/dashboard', '/characters', '/worlds', '/preferences', '/settings'];

      for (const pagePath of pages) {
        await page.goto(pagePath);
        await page.waitForLoadState('networkidle');

        // Force garbage collection if available
        await page.evaluate(() => {
          if ((window as any).gc) {
            (window as any).gc();
          }
        });
      }

      // Check final memory usage
      const finalMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });

      // Memory should not increase dramatically (allowing for some normal growth)
      const memoryIncrease = finalMemory - initialMemory;
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // 50MB threshold
    });

    test('should handle large DOM efficiently', async ({ page }) => {
      // Create a page with many elements
      await page.goto('/characters');

      // Mock large character list to create large DOM
      const largeCharacterList = Array.from({ length: 200 }, (_, i) => ({
        character_id: `char-${i}`,
        name: `Character ${i}`,
        description: `Long description for character ${i} `.repeat(10),
      }));

      await mockApiResponse(page, '**/players/*/characters', largeCharacterList);
      await page.reload();

      // Measure DOM interaction performance
      const scrollTime = await measureActionTime(async () => {
        await page.evaluate(() => {
          window.scrollTo(0, document.body.scrollHeight);
        });
        await page.waitForTimeout(100);
      });

      expect(scrollTime).toBeLessThan(500); // 500ms for scrolling large DOM
    });

    test('should handle WebSocket connections efficiently', async ({ page }) => {
      await chatPage.goto();

      // Measure WebSocket connection time
      const connectionTime = await measureActionTime(async () => {
        await chatPage.expectChatLoaded();
        await chatPage.expectWebSocketConnected();
      });

      expect(connectionTime).toBeLessThan(2000); // 2 seconds for WebSocket connection
    });
  });

  test.describe('Network Performance', () => {
    test('should handle slow network conditions', async ({ page }) => {
      // Simulate slow 3G network
      await page.route('**/*', route => {
        setTimeout(() => route.continue(), 500); // 500ms delay
      });

      const loadTime = await measurePageLoadTime(page, '/dashboard');

      // Should still be usable on slow networks
      expect(loadTime).toBeLessThan(8000); // 8 seconds on slow network
    });

    test('should optimize image loading', async ({ page }) => {
      await dashboardPage.goto();

      // Check that images are loaded efficiently
      const images = await page.locator('img').all();

      for (const img of images) {
        const src = await img.getAttribute('src');
        if (src && !src.startsWith('data:')) {
          // Images should have proper loading attributes
          const loading = await img.getAttribute('loading');
          expect(loading).toBe('lazy');
        }
      }
    });

    test('should handle offline scenarios gracefully', async ({ page }) => {
      await dashboardPage.goto();

      // Simulate offline
      await page.context().setOffline(true);

      // Try to navigate
      await page.click('a[href="/characters"]');

      // Should show offline message or cached content
      await expect(page.locator('text=offline, text=cached, text=unavailable')).toBeVisible();

      // Restore online
      await page.context().setOffline(false);
    });
  });

  test.describe('Rendering Performance', () => {
    test('should achieve good Core Web Vitals', async ({ page }) => {
      await page.goto('/dashboard');

      // Measure Core Web Vitals
      const vitals = await page.evaluate(() => {
        return new Promise((resolve) => {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const vitals: any = {};

            entries.forEach((entry) => {
              if (entry.name === 'first-contentful-paint') {
                vitals.fcp = entry.startTime;
              }
              if (entry.entryType === 'largest-contentful-paint') {
                vitals.lcp = entry.startTime;
              }
              if (entry.entryType === 'layout-shift') {
                vitals.cls = (vitals.cls || 0) + (entry as any).value;
              }
            });

            setTimeout(() => resolve(vitals), 3000);
          });

          observer.observe({ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] });
        });
      });

      // Core Web Vitals thresholds
      expect((vitals as any).fcp).toBeLessThan(1800); // First Contentful Paint < 1.8s
      expect((vitals as any).lcp).toBeLessThan(2500); // Largest Contentful Paint < 2.5s
      expect((vitals as any).cls || 0).toBeLessThan(0.1); // Cumulative Layout Shift < 0.1
    });

    test('should render animations smoothly', async ({ page }) => {
      await dashboardPage.goto();

      // Trigger animations (e.g., modal opening)
      await dashboardPage.openUserMenu();

      // Measure frame rate during animation
      const frameRate = await page.evaluate(() => {
        return new Promise((resolve) => {
          let frames = 0;
          const startTime = performance.now();

          function countFrames() {
            frames++;
            if (performance.now() - startTime < 1000) {
              requestAnimationFrame(countFrames);
            } else {
              resolve(frames);
            }
          }

          requestAnimationFrame(countFrames);
        });
      });

      // Should maintain at least 30 FPS
      expect(frameRate as number).toBeGreaterThan(30);
    });

    test('should handle responsive design efficiently', async ({ page }) => {
      const viewports = [
        { width: 375, height: 667 },   // Mobile
        { width: 768, height: 1024 },  // Tablet
        { width: 1280, height: 720 },  // Desktop
      ];

      for (const viewport of viewports) {
        const resizeTime = await measureActionTime(async () => {
          await page.setViewportSize(viewport);
          await page.waitForLoadState('networkidle');
        });

        expect(resizeTime).toBeLessThan(500); // 500ms for viewport changes
      }
    });
  });

  test.describe('Stress Testing', () => {
    test('should handle rapid user interactions', async ({ page }) => {
      await characterPage.goto();

      // Simulate rapid clicking
      const rapidClickTime = await measureActionTime(async () => {
        for (let i = 0; i < 10; i++) {
          await characterPage.clickCreateCharacter();
          await characterPage.closeModal();
          await page.waitForTimeout(50);
        }
      });

      expect(rapidClickTime).toBeLessThan(3000); // 3 seconds for 10 rapid interactions
    });

    test('should handle multiple simultaneous users', async ({ context }) => {
      // Simulate multiple users by creating multiple pages
      const userPages = await Promise.all([
        context.newPage(),
        context.newPage(),
        context.newPage(),
      ]);

      const userActions = userPages.map(async (userPage, index) => {
        const userLoginPage = new LoginPage(userPage);
        const userDashboardPage = new DashboardPage(userPage);

        await userLoginPage.goto();
        await userLoginPage.login({ ...testUsers.default, username: `user${index}` });
        await userDashboardPage.goto();

        return measureActionTime(async () => {
          await userDashboardPage.expectDashboardLoaded();
        });
      });

      const loadTimes = await Promise.all(userActions);

      // All users should be able to use the system simultaneously
      loadTimes.forEach(time => {
        expect(time).toBeLessThan(5000); // 5 seconds per user
      });

      // Clean up
      await Promise.all(userPages.map(p => p.close()));
    });

    test('should handle long-running sessions', async ({ page }) => {
      await chatPage.goto();

      // Simulate a long chat session
      const longSessionTime = await measureActionTime(async () => {
        for (let i = 0; i < 20; i++) {
          await mockApiResponse(page, '**/chat/send', {
            message_id: `msg-${i}`,
            response: `Response ${i}`,
          }, 200, 'POST');

          await chatPage.sendMessage(`Message ${i}`);
          await page.waitForTimeout(100);
        }
      });

      expect(longSessionTime).toBeLessThan(15000); // 15 seconds for 20 messages
    });
  });
});
