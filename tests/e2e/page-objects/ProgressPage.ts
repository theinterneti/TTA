// Logseq: [[TTA.dev/Tests/E2e/Page-objects/Progresspage]]
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object Model for Progress Tracking Page
 */
export class ProgressPage extends BasePage {
  // Main dashboard elements
  readonly pageTitle: Locator;
  readonly progressOverview: Locator;
  readonly progressChart: Locator;
  readonly milestoneTracker: Locator;
  readonly achievementCelebration: Locator;
  readonly insightDisplay: Locator;

  // Progress metrics
  readonly totalSessionsCount: Locator;
  readonly streakCounter: Locator;
  readonly completedGoalsCount: Locator;
  readonly progressPercentage: Locator;
  readonly weeklyProgressChart: Locator;
  readonly monthlyProgressChart: Locator;

  // Milestone tracking
  readonly milestoneList: Locator;
  readonly completedMilestones: Locator;
  readonly upcomingMilestones: Locator;
  readonly milestoneProgress: Locator;
  readonly milestoneDetails: Locator;

  // Achievement system
  readonly achievementBadges: Locator;
  readonly recentAchievements: Locator;
  readonly achievementModal: Locator;
  readonly achievementDescription: Locator;
  readonly shareAchievementButton: Locator;

  // Insights and recommendations
  readonly personalInsights: Locator;
  readonly recommendationCards: Locator;
  readonly insightCategories: Locator;
  readonly trendAnalysis: Locator;

  // Time period filters
  readonly timeFilterButtons: Locator;
  readonly weeklyFilter: Locator;
  readonly monthlyFilter: Locator;
  readonly quarterlyFilter: Locator;
  readonly yearlyFilter: Locator;

  // Export and sharing
  readonly exportProgressButton: Locator;
  readonly shareProgressButton: Locator;
  readonly printReportButton: Locator;
  readonly exportModal: Locator;
  readonly exportFormatSelect: Locator;

  // Goal management
  readonly currentGoals: Locator;
  readonly goalProgressBars: Locator;
  readonly addGoalButton: Locator;
  readonly editGoalButton: Locator;
  readonly goalModal: Locator;
  readonly goalInput: Locator;
  readonly goalTargetDate: Locator;

  // Session history
  readonly sessionHistory: Locator;
  readonly sessionCards: Locator;
  readonly sessionDetails: Locator;
  readonly sessionRatings: Locator;
  readonly sessionNotes: Locator;

  // Therapeutic progress
  readonly therapeuticMetrics: Locator;
  readonly moodTracker: Locator;
  readonly anxietyLevels: Locator;
  readonly copingSkillsProgress: Locator;
  readonly therapeuticGoalsProgress: Locator;

  constructor(page: Page) {
    super(page);

    // Main dashboard elements
    this.pageTitle = page.locator('h1:has-text("Progress Dashboard"), h1:has-text("Your Progress")');
    this.progressOverview = page.locator('[data-testid="progress-overview"]');
    this.progressChart = page.locator('[data-testid="progress-chart"]');
    this.milestoneTracker = page.locator('[data-testid="milestone-tracker"]');
    this.achievementCelebration = page.locator('[data-testid="achievement-celebration"]');
    this.insightDisplay = page.locator('[data-testid="insight-display"]');

    // Progress metrics
    this.totalSessionsCount = page.locator('[data-testid="total-sessions"]');
    this.streakCounter = page.locator('[data-testid="streak-counter"]');
    this.completedGoalsCount = page.locator('[data-testid="completed-goals"]');
    this.progressPercentage = page.locator('[data-testid="progress-percentage"]');
    this.weeklyProgressChart = page.locator('[data-testid="weekly-progress"]');
    this.monthlyProgressChart = page.locator('[data-testid="monthly-progress"]');

    // Milestone tracking
    this.milestoneList = page.locator('[data-testid="milestone-list"]');
    this.completedMilestones = page.locator('[data-testid="completed-milestones"]');
    this.upcomingMilestones = page.locator('[data-testid="upcoming-milestones"]');
    this.milestoneProgress = page.locator('[data-testid="milestone-progress"]');
    this.milestoneDetails = page.locator('[data-testid="milestone-details"]');

    // Achievement system
    this.achievementBadges = page.locator('[data-testid="achievement-badges"]');
    this.recentAchievements = page.locator('[data-testid="recent-achievements"]');
    this.achievementModal = page.locator('[data-testid="achievement-modal"]');
    this.achievementDescription = page.locator('[data-testid="achievement-description"]');
    this.shareAchievementButton = page.locator('button:has-text("Share Achievement")');

    // Insights and recommendations
    this.personalInsights = page.locator('[data-testid="personal-insights"]');
    this.recommendationCards = page.locator('[data-testid="recommendation-cards"]');
    this.insightCategories = page.locator('[data-testid="insight-categories"]');
    this.trendAnalysis = page.locator('[data-testid="trend-analysis"]');

    // Time period filters
    this.timeFilterButtons = page.locator('[data-testid="time-filters"]');
    this.weeklyFilter = page.locator('button:has-text("Weekly")');
    this.monthlyFilter = page.locator('button:has-text("Monthly")');
    this.quarterlyFilter = page.locator('button:has-text("Quarterly")');
    this.yearlyFilter = page.locator('button:has-text("Yearly")');

    // Export and sharing
    this.exportProgressButton = page.locator('button:has-text("Export Progress")');
    this.shareProgressButton = page.locator('button:has-text("Share Progress")');
    this.printReportButton = page.locator('button:has-text("Print Report")');
    this.exportModal = page.locator('[data-testid="export-modal"]');
    this.exportFormatSelect = page.locator('select[name="export_format"]');

    // Goal management
    this.currentGoals = page.locator('[data-testid="current-goals"]');
    this.goalProgressBars = page.locator('[data-testid="goal-progress-bar"]');
    this.addGoalButton = page.locator('button:has-text("Add Goal")');
    this.editGoalButton = page.locator('button:has-text("Edit Goal")');
    this.goalModal = page.locator('[data-testid="goal-modal"]');
    this.goalInput = page.locator('input[name="goal_title"]');
    this.goalTargetDate = page.locator('input[name="target_date"]');

    // Session history
    this.sessionHistory = page.locator('[data-testid="session-history"]');
    this.sessionCards = page.locator('[data-testid="session-card"]');
    this.sessionDetails = page.locator('[data-testid="session-details"]');
    this.sessionRatings = page.locator('[data-testid="session-rating"]');
    this.sessionNotes = page.locator('[data-testid="session-notes"]');

    // Therapeutic progress
    this.therapeuticMetrics = page.locator('[data-testid="therapeutic-metrics"]');
    this.moodTracker = page.locator('[data-testid="mood-tracker"]');
    this.anxietyLevels = page.locator('[data-testid="anxiety-levels"]');
    this.copingSkillsProgress = page.locator('[data-testid="coping-skills"]');
    this.therapeuticGoalsProgress = page.locator('[data-testid="therapeutic-goals-progress"]');
  }

  async goto() {
    await this.page.goto('/dashboard'); // Progress is typically part of dashboard
    await this.waitForPageLoad();
  }

  async expectPageLoaded() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.progressOverview).toBeVisible();
  }

  // Progress metrics validation
  async expectProgressMetrics() {
    await expect(this.totalSessionsCount).toBeVisible();
    await expect(this.streakCounter).toBeVisible();
    await expect(this.completedGoalsCount).toBeVisible();
  }

  async expectProgressChart() {
    await expect(this.progressChart).toBeVisible();
  }

  async getSessionCount(): Promise<number> {
    const text = await this.totalSessionsCount.textContent();
    return parseInt(text?.match(/\d+/)?.[0] || '0');
  }

  async getStreakCount(): Promise<number> {
    const text = await this.streakCounter.textContent();
    return parseInt(text?.match(/\d+/)?.[0] || '0');
  }

  async getCompletedGoalsCount(): Promise<number> {
    const text = await this.completedGoalsCount.textContent();
    return parseInt(text?.match(/\d+/)?.[0] || '0');
  }

  // Time period filtering
  async filterByWeekly() {
    await this.weeklyFilter.click();
    await this.page.waitForTimeout(500);
  }

  async filterByMonthly() {
    await this.monthlyFilter.click();
    await this.page.waitForTimeout(500);
  }

  async filterByQuarterly() {
    await this.quarterlyFilter.click();
    await this.page.waitForTimeout(500);
  }

  async filterByYearly() {
    await this.yearlyFilter.click();
    await this.page.waitForTimeout(500);
  }

  // Milestone tracking
  async expectMilestones() {
    await expect(this.milestoneTracker).toBeVisible();
    await expect(this.milestoneList).toBeVisible();
  }

  async clickMilestone(milestoneName: string) {
    const milestone = this.page.locator(`[data-testid="milestone"]:has-text("${milestoneName}")`);
    await milestone.click();
  }

  async expectMilestoneDetails(milestoneName: string) {
    await expect(this.milestoneDetails).toContainText(milestoneName);
  }

  async expectMilestoneCompleted(milestoneName: string) {
    const milestone = this.page.locator(`[data-testid="milestone"]:has-text("${milestoneName}")`);
    await expect(milestone).toHaveClass(/completed/);
  }

  // Achievement system
  async expectAchievements() {
    await expect(this.achievementBadges).toBeVisible();
  }

  async clickAchievement(achievementName: string) {
    const achievement = this.page.locator(`[data-testid="achievement"]:has-text("${achievementName}")`);
    await achievement.click();
  }

  async expectAchievementModal(achievementName: string) {
    await expect(this.achievementModal).toBeVisible();
    await expect(this.achievementDescription).toContainText(achievementName);
  }

  async shareAchievement() {
    await this.shareAchievementButton.click();
  }

  // Goal management
  async expectCurrentGoals() {
    await expect(this.currentGoals).toBeVisible();
  }

  async addNewGoal(goalTitle: string, targetDate: string) {
    await this.addGoalButton.click();
    await expect(this.goalModal).toBeVisible();
    await this.goalInput.fill(goalTitle);
    await this.goalTargetDate.fill(targetDate);
    await this.page.locator('button:has-text("Save Goal")').click();
  }

  async editGoal(oldGoalTitle: string, newGoalTitle: string) {
    const goalCard = this.page.locator(`[data-testid="goal-card"]:has-text("${oldGoalTitle}")`);
    await goalCard.locator('button:has-text("Edit")').click();
    await expect(this.goalModal).toBeVisible();
    await this.goalInput.fill(newGoalTitle);
    await this.page.locator('button:has-text("Save Goal")').click();
  }

  async expectGoalProgress(goalTitle: string, expectedProgress: number) {
    const goalCard = this.page.locator(`[data-testid="goal-card"]:has-text("${goalTitle}")`);
    const progressBar = goalCard.locator('[data-testid="goal-progress-bar"]');
    const progressValue = await progressBar.getAttribute('aria-valuenow');
    expect(parseInt(progressValue || '0')).toBe(expectedProgress);
  }

  // Session history
  async expectSessionHistory() {
    await expect(this.sessionHistory).toBeVisible();
    await expect(this.sessionCards.first()).toBeVisible();
  }

  async clickSessionDetails(sessionId: string) {
    const sessionCard = this.page.locator(`[data-testid="session-card"][data-session-id="${sessionId}"]`);
    await sessionCard.click();
  }

  async expectSessionRating(sessionId: string, expectedRating: number) {
    const sessionCard = this.page.locator(`[data-testid="session-card"][data-session-id="${sessionId}"]`);
    const ratingStars = sessionCard.locator('[data-testid="rating-star"].filled');
    const actualRating = await ratingStars.count();
    expect(actualRating).toBe(expectedRating);
  }

  // Insights and recommendations
  async expectInsights() {
    await expect(this.personalInsights).toBeVisible();
    await expect(this.recommendationCards).toBeVisible();
  }

  async expectTrendAnalysis() {
    await expect(this.trendAnalysis).toBeVisible();
  }

  // Export functionality
  async exportProgress(format: string) {
    await this.exportProgressButton.click();
    await expect(this.exportModal).toBeVisible();
    await this.exportFormatSelect.selectOption(format);
    await this.page.locator('button:has-text("Export")').click();
  }

  async printReport() {
    await this.printReportButton.click();
  }

  // Therapeutic progress
  async expectTherapeuticMetrics() {
    await expect(this.therapeuticMetrics).toBeVisible();
    await expect(this.moodTracker).toBeVisible();
  }

  async expectMoodTrend(expectedTrend: 'improving' | 'stable' | 'declining') {
    const trendIndicator = this.moodTracker.locator('[data-testid="mood-trend"]');
    await expect(trendIndicator).toHaveClass(new RegExp(expectedTrend));
  }

  // Performance testing
  async measureChartLoadTime(): Promise<number> {
    const startTime = Date.now();
    await this.expectProgressChart();
    return Date.now() - startTime;
  }

  async measureDataRefreshTime(): Promise<number> {
    const startTime = Date.now();
    await this.page.reload();
    await this.expectPageLoaded();
    return Date.now() - startTime;
  }

  // Accessibility testing
  async testKeyboardNavigation() {
    await this.weeklyFilter.focus();
    await this.page.keyboard.press('Tab');
    await expect(this.monthlyFilter).toBeFocused();
  }

  async testScreenReaderSupport() {
    await expect(this.progressChart).toHaveAttribute('aria-label');
    await expect(this.milestoneTracker).toHaveAttribute('role', 'region');
  }

  // Data validation
  async validateProgressData() {
    const sessionCount = await this.getSessionCount();
    const streakCount = await this.getStreakCount();
    const goalsCount = await this.getCompletedGoalsCount();

    expect(sessionCount).toBeGreaterThanOrEqual(0);
    expect(streakCount).toBeGreaterThanOrEqual(0);
    expect(goalsCount).toBeGreaterThanOrEqual(0);
  }
}
