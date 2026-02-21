// Logseq: [[TTA.dev/Tests/E2e/Specs/Progress-tracking.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { ProgressPage } from '../page-objects/ProgressPage';
import { testUsers } from '../fixtures/test-data';
import { mockApiResponse } from '../utils/test-helpers';

test.describe('Progress Tracking', () => {
  let loginPage: LoginPage;
  let progressPage: ProgressPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    progressPage = new ProgressPage(page);

    // Mock API responses for progress data
    await mockApiResponse(page, '**/players/*/progress', {
      total_sessions: 15,
      current_streak: 7,
      completed_goals: 3,
      progress_percentage: 68,
      weekly_progress: [
        { date: '2024-01-01', sessions: 2, mood_score: 7 },
        { date: '2024-01-02', sessions: 1, mood_score: 8 },
        { date: '2024-01-03', sessions: 3, mood_score: 6 },
      ],
      milestones: [
        {
          id: 'milestone-1',
          name: 'First Week Complete',
          description: 'Complete 7 consecutive days',
          completed: true,
          completion_date: '2024-01-07',
        },
        {
          id: 'milestone-2',
          name: 'Anxiety Management',
          description: 'Complete anxiety-focused sessions',
          completed: false,
          progress: 0.6,
        },
      ],
      achievements: [
        {
          id: 'achievement-1',
          name: 'Consistent Learner',
          description: 'Maintained a 7-day streak',
          earned_date: '2024-01-07',
          badge_icon: 'streak',
        },
      ],
      insights: [
        {
          category: 'mood',
          title: 'Mood Improvement',
          description: 'Your mood scores have improved by 15% this week',
          trend: 'improving',
        },
      ],
    });

    await mockApiResponse(page, '**/players/*/sessions', [
      {
        session_id: 'session-1',
        date: '2024-01-07',
        duration: 45,
        rating: 4,
        notes: 'Great session on mindfulness',
        therapeutic_goals: ['anxiety_reduction'],
      },
      {
        session_id: 'session-2',
        date: '2024-01-06',
        duration: 30,
        rating: 5,
        notes: 'Breakthrough moment with CBT techniques',
        therapeutic_goals: ['stress_management'],
      },
    ]);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Dashboard Overview', () => {
    test('should load progress dashboard correctly', async () => {
      await progressPage.goto();
      await progressPage.expectPageLoaded();
      await progressPage.expectProgressMetrics();
    });

    test('should display correct progress metrics', async () => {
      await progressPage.goto();

      const sessionCount = await progressPage.getSessionCount();
      const streakCount = await progressPage.getStreakCount();
      const goalsCount = await progressPage.getCompletedGoalsCount();

      expect(sessionCount).toBe(15);
      expect(streakCount).toBe(7);
      expect(goalsCount).toBe(3);
    });

    test('should show progress chart', async () => {
      await progressPage.goto();
      await progressPage.expectProgressChart();
    });

    test('should validate progress data consistency', async () => {
      await progressPage.goto();
      await progressPage.validateProgressData();
    });
  });

  test.describe('Time Period Filtering', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should filter by weekly view', async () => {
      await progressPage.filterByWeekly();
      await expect(progressPage.weeklyProgressChart).toBeVisible();
    });

    test('should filter by monthly view', async () => {
      await progressPage.filterByMonthly();
      await expect(progressPage.monthlyProgressChart).toBeVisible();
    });

    test('should filter by quarterly view', async () => {
      await progressPage.filterByQuarterly();
      await expect(progressPage.progressChart).toBeVisible();
    });

    test('should filter by yearly view', async () => {
      await progressPage.filterByYearly();
      await expect(progressPage.progressChart).toBeVisible();
    });

    test('should update chart data when changing time periods', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/progress?period=monthly', {
        monthly_progress: [
          { month: '2024-01', sessions: 20, mood_average: 7.5 },
          { month: '2024-02', sessions: 18, mood_average: 8.0 },
        ],
      });

      await progressPage.filterByMonthly();
      await expect(progressPage.monthlyProgressChart).toBeVisible();
    });
  });

  test.describe('Milestone Tracking', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display milestones', async () => {
      await progressPage.expectMilestones();
    });

    test('should show completed milestones', async () => {
      await progressPage.expectMilestoneCompleted('First Week Complete');
    });

    test('should display milestone details', async () => {
      await progressPage.clickMilestone('First Week Complete');
      await progressPage.expectMilestoneDetails('First Week Complete');
    });

    test('should show milestone progress for incomplete milestones', async () => {
      await progressPage.clickMilestone('Anxiety Management');
      await progressPage.expectMilestoneDetails('Anxiety Management');

      // Should show 60% progress
      const progressBar = progressPage.page.locator('[data-testid="milestone-progress-bar"]');
      await expect(progressBar).toHaveAttribute('aria-valuenow', '60');
    });
  });

  test.describe('Achievement System', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display achievements', async () => {
      await progressPage.expectAchievements();
    });

    test('should show achievement details in modal', async () => {
      await progressPage.clickAchievement('Consistent Learner');
      await progressPage.expectAchievementModal('Consistent Learner');
    });

    test('should allow sharing achievements', async ({ page }) => {
      await mockApiResponse(page, '**/achievements/*/share', { success: true }, 200, 'POST');

      await progressPage.clickAchievement('Consistent Learner');
      await progressPage.shareAchievement();

      await expect(page.locator('text=Achievement shared')).toBeVisible();
    });

    test('should display achievement badges', async () => {
      await expect(progressPage.achievementBadges).toBeVisible();
      await expect(progressPage.page.locator('[data-badge="streak"]')).toBeVisible();
    });
  });

  test.describe('Goal Management', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display current goals', async () => {
      await progressPage.expectCurrentGoals();
    });

    test('should add new goal', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/goals', {
        goal_id: 'new-goal-1',
        title: 'Improve Sleep Quality',
        target_date: '2024-02-01',
        progress: 0,
      }, 201, 'POST');

      await progressPage.addNewGoal('Improve Sleep Quality', '2024-02-01');

      await expect(page.locator('text=Goal added successfully')).toBeVisible();
    });

    test('should edit existing goal', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/goals/*', {
        success: true,
      }, 200, 'PUT');

      await progressPage.editGoal('Old Goal Title', 'Updated Goal Title');

      await expect(page.locator('text=Goal updated successfully')).toBeVisible();
    });

    test('should show goal progress', async () => {
      await progressPage.expectGoalProgress('Anxiety Management', 60);
    });

    test('should validate goal input', async () => {
      await progressPage.addNewGoal('', ''); // Empty inputs

      await expect(progressPage.page.locator('text=Goal title is required')).toBeVisible();
    });
  });

  test.describe('Session History', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display session history', async () => {
      await progressPage.expectSessionHistory();
    });

    test('should show session details', async () => {
      await progressPage.clickSessionDetails('session-1');
      await expect(progressPage.sessionDetails).toBeVisible();
    });

    test('should display session ratings', async () => {
      await progressPage.expectSessionRating('session-1', 4);
      await progressPage.expectSessionRating('session-2', 5);
    });

    test('should show session notes', async () => {
      await progressPage.clickSessionDetails('session-1');
      await expect(progressPage.sessionNotes).toContainText('Great session on mindfulness');
    });
  });

  test.describe('Insights and Recommendations', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display personal insights', async () => {
      await progressPage.expectInsights();
    });

    test('should show trend analysis', async () => {
      await progressPage.expectTrendAnalysis();
    });

    test('should display mood trends', async () => {
      await progressPage.expectMoodTrend('improving');
    });

    test('should show recommendation cards', async () => {
      await expect(progressPage.recommendationCards).toBeVisible();
    });
  });

  test.describe('Therapeutic Progress', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should display therapeutic metrics', async () => {
      await progressPage.expectTherapeuticMetrics();
    });

    test('should show mood tracker', async () => {
      await expect(progressPage.moodTracker).toBeVisible();
    });

    test('should display anxiety level trends', async () => {
      await expect(progressPage.anxietyLevels).toBeVisible();
    });

    test('should show coping skills progress', async () => {
      await expect(progressPage.copingSkillsProgress).toBeVisible();
    });

    test('should display therapeutic goals progress', async () => {
      await expect(progressPage.therapeuticGoalsProgress).toBeVisible();
    });
  });

  test.describe('Export and Sharing', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should export progress report as PDF', async ({ page }) => {
      const downloadPromise = page.waitForEvent('download');
      await progressPage.exportProgress('pdf');
      const download = await downloadPromise;

      expect(download.suggestedFilename()).toContain('progress-report');
      expect(download.suggestedFilename()).toContain('.pdf');
    });

    test('should export progress report as CSV', async ({ page }) => {
      const downloadPromise = page.waitForEvent('download');
      await progressPage.exportProgress('csv');
      const download = await downloadPromise;

      expect(download.suggestedFilename()).toContain('progress-data');
      expect(download.suggestedFilename()).toContain('.csv');
    });

    test('should print progress report', async ({ page }) => {
      // Mock print dialog
      await page.evaluate(() => {
        window.print = () => console.log('Print dialog opened');
      });

      await progressPage.printReport();

      // Verify print was triggered (in real test, you'd check for print dialog)
      const printLogs = await page.evaluate(() => console.log);
    });
  });

  test.describe('Performance', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should load charts within performance budget', async () => {
      const chartLoadTime = await progressPage.measureChartLoadTime();
      expect(chartLoadTime).toBeLessThan(3000); // 3 seconds
    });

    test('should refresh data efficiently', async () => {
      const refreshTime = await progressPage.measureDataRefreshTime();
      expect(refreshTime).toBeLessThan(5000); // 5 seconds
    });

    test('should handle large datasets', async ({ page }) => {
      // Mock large dataset
      const largeProgressData = {
        total_sessions: 500,
        weekly_progress: Array.from({ length: 52 }, (_, i) => ({
          date: `2024-01-${i + 1}`,
          sessions: Math.floor(Math.random() * 10),
          mood_score: Math.floor(Math.random() * 10) + 1,
        })),
      };

      await mockApiResponse(page, '**/players/*/progress', largeProgressData);

      const startTime = Date.now();
      await page.reload();
      await progressPage.expectPageLoaded();
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(10000); // 10 seconds for large dataset
    });
  });

  test.describe('Accessibility', () => {
    test.beforeEach(async () => {
      await progressPage.goto();
    });

    test('should support keyboard navigation', async () => {
      await progressPage.testKeyboardNavigation();
    });

    test('should have proper screen reader support', async () => {
      await progressPage.testScreenReaderSupport();
    });

    test('should have proper ARIA labels for charts', async () => {
      await expect(progressPage.progressChart).toHaveAttribute('role', 'img');
      await expect(progressPage.progressChart).toHaveAttribute('aria-label');
    });

    test('should support high contrast mode', async ({ page }) => {
      // Simulate high contrast mode
      await page.addStyleTag({
        content: `
          @media (prefers-contrast: high) {
            * { border: 1px solid black !important; }
          }
        `,
      });

      await progressPage.expectPageLoaded();
      // Charts and elements should still be visible and functional
      await progressPage.expectProgressChart();
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await progressPage.goto();
      await progressPage.expectPageLoaded();

      // Test mobile-specific functionality
      await progressPage.filterByWeekly();
      await progressPage.expectProgressChart();
    });

    test('should adapt to tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await progressPage.goto();
      await progressPage.expectPageLoaded();

      // Test tablet-specific functionality
      await progressPage.clickMilestone('First Week Complete');
      await progressPage.expectMilestoneDetails('First Week Complete');
    });

    test('should maintain chart readability across viewports', async ({ page }) => {
      const viewports = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1280, height: 720 }, // Desktop
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await progressPage.expectProgressChart();

        // Chart should be visible and properly sized
        const chartBounds = await progressPage.progressChart.boundingBox();
        expect(chartBounds?.width).toBeGreaterThan(200);
        expect(chartBounds?.height).toBeGreaterThan(150);
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/players/*/progress', route => {
        route.fulfill({ status: 500, body: 'Server Error' });
      });

      await progressPage.goto();
      await expect(page.locator('text=Failed to load progress data')).toBeVisible();
    });

    test('should handle missing data gracefully', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/progress', {
        total_sessions: 0,
        current_streak: 0,
        completed_goals: 0,
        milestones: [],
        achievements: [],
      });

      await progressPage.goto();
      await progressPage.expectPageLoaded();

      // Should show empty states
      await expect(page.locator('text=No progress data yet')).toBeVisible();
    });

    test('should handle network timeouts', async ({ page }) => {
      await page.route('**/players/*/progress', route => {
        // Never resolve to simulate timeout
      });

      await progressPage.goto();
      // Should show loading state
      await expect(page.locator('.loading, .spinner')).toBeVisible();
    });
  });
});
