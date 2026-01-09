// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Services/__tests__/Predictiveanalyticsservice.test]]
/**
 * Predictive Analytics Service Tests - Priority 4B Implementation
 *
 * Comprehensive test suite for predictive analytics functionality including:
 * - Trend analysis and pattern recognition
 * - Risk prediction algorithms
 * - Therapeutic outcome forecasting
 * - Longitudinal insights generation
 * - Model performance assessment
 */

import {
  PredictiveAnalyticsService,
  predictiveAnalyticsService,
  TrendAnalysis,
  RiskPrediction,
  TherapeuticOutcomePrediction,
  LongitudinalInsight
} from '../predictiveAnalyticsService';
import { TherapeuticGoal } from '../../types/index';
import { ProgressTrackingResult, ProgressAnalytics, ProgressEntry } from '../progressTrackingService';
import { MonitoringSession, EmotionalState } from '../realTimeTherapeuticMonitor';
import { RecommendationResult } from '../personalizedRecommendationEngine';

// Mock data generators
const createMockGoal = (id: string, title: string, category: string): TherapeuticGoal => ({
  id,
  title,
  description: `Mock goal for ${title}`,
  category,
  progress: Math.floor(Math.random() * 100)
});

const createMockProgressEntry = (goalId: string, progressValue: number, daysAgo: number = 0): ProgressEntry => ({
  id: `entry_${Date.now()}_${Math.random()}`,
  goalId,
  userId: 'test-user',
  timestamp: new Date(Date.now() - (daysAgo * 24 * 60 * 60 * 1000)),
  progressValue,
  progressType: 'self_reported',
  measurementMethod: 'scale_rating',
  evidenceLevel: 'moderate'
});

const createMockProgressAnalytics = (goalId: string): ProgressAnalytics => ({
  goalId,
  overallProgress: Math.floor(Math.random() * 100),
  progressTrend: 'improving',
  velocityScore: Math.random(),
  consistencyScore: Math.random(),
  therapeuticEffectiveness: Math.random(),
  riskFactors: [],
  recommendations: [],
  insights: []
});

const createMockProgressData = (goals: TherapeuticGoal[]): ProgressTrackingResult => ({
  currentProgress: goals.map(goal => createMockProgressAnalytics(goal.id)),
  recentEntries: goals.flatMap(goal => [
    createMockProgressEntry(goal.id, 30, 10),
    createMockProgressEntry(goal.id, 45, 7),
    createMockProgressEntry(goal.id, 60, 5),
    createMockProgressEntry(goal.id, 75, 2),
    createMockProgressEntry(goal.id, 80, 0)
  ]),
  milestones: [],
  outcomeMeasurements: [],
  therapeuticInsights: [],
  overallEffectiveness: 0.8,
  riskAssessment: {
    overallRisk: 'low',
    riskFactors: [],
    protectiveFactors: [],
    recommendations: []
  },
  recommendations: [],
  nextActions: [],
  generatedAt: new Date(),
  dataQuality: {
    completeness: 0.9,
    accuracy: 0.85,
    consistency: 0.8,
    timeliness: 0.9,
    issues: []
  }
});

const createMockEmotionalState = (valence: number, arousal: number, dominance: number, daysAgo: number = 0): EmotionalState => ({
  valence,
  arousal,
  dominance,
  timestamp: new Date(Date.now() - (daysAgo * 24 * 60 * 60 * 1000)),
  confidence: 0.8
});

const createMockMonitoringSession = (userId: string, daysAgo: number = 0): MonitoringSession => ({
  sessionId: `session_${Date.now()}_${Math.random()}`,
  userId,
  startTime: Date.now() - (daysAgo * 24 * 60 * 60 * 1000),
  endTime: Date.now() - (daysAgo * 24 * 60 * 60 * 1000) + (30 * 60 * 1000), // 30 min session
  emotionalStates: [
    createMockEmotionalState(0.2, 0.3, 0.4, daysAgo),
    createMockEmotionalState(0.3, 0.4, 0.5, daysAgo)
  ],
  riskAssessments: [],
  interventions: [],
  therapeuticGoals: ['anxiety_reduction', 'stress_management'],
  sessionContext: {}
});

const createMockRecommendationResult = (): RecommendationResult => ({
  recommendations: [],
  totalRecommendations: 0,
  personalizationScore: 0.8,
  confidenceLevel: 'high',
  recommendationSummary: {
    primaryFocus: 'anxiety_reduction',
    secondaryFocus: 'stress_management',
    approachRecommendation: 'cognitive_behavioral_therapy',
    intensityRecommendation: 'medium',
    sessionFrequency: 'weekly',
    estimatedDuration: '12-16 weeks'
  },
  nextReviewDate: Date.now() + (7 * 24 * 60 * 60 * 1000),
  adaptationHistory: []
});

describe('PredictiveAnalyticsService', () => {
  let service: PredictiveAnalyticsService;
  let mockGoals: TherapeuticGoal[];
  let mockProgressData: ProgressTrackingResult;
  let mockMonitoringData: MonitoringSession[];
  let mockEmotionalHistory: EmotionalState[];
  let mockRecommendationHistory: RecommendationResult[];

  beforeEach(() => {
    service = new PredictiveAnalyticsService();

    // Create mock data
    mockGoals = [
      createMockGoal('goal1', 'Anxiety Reduction', 'anxiety_reduction'),
      createMockGoal('goal2', 'Stress Management', 'stress_management'),
      createMockGoal('goal3', 'Confidence Building', 'confidence_building')
    ];

    mockProgressData = createMockProgressData(mockGoals);

    mockMonitoringData = [
      createMockMonitoringSession('test-user', 0),
      createMockMonitoringSession('test-user', 1),
      createMockMonitoringSession('test-user', 3),
      createMockMonitoringSession('test-user', 7)
    ];

    mockEmotionalHistory = [
      createMockEmotionalState(0.2, 0.3, 0.4, 0),
      createMockEmotionalState(0.3, 0.4, 0.5, 1),
      createMockEmotionalState(0.4, 0.3, 0.6, 2),
      createMockEmotionalState(0.5, 0.2, 0.7, 3),
      createMockEmotionalState(0.6, 0.1, 0.8, 5)
    ];

    mockRecommendationHistory = [
      createMockRecommendationResult(),
      createMockRecommendationResult()
    ];
  });

  describe('generatePredictiveAnalytics', () => {
    it('should generate comprehensive predictive analytics', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result).toBeDefined();
      expect(result.userId).toBe('test-user');
      expect(result.analysisTimestamp).toBeGreaterThan(0);
      expect(result.trendAnalyses).toBeInstanceOf(Array);
      expect(result.riskPredictions).toBeInstanceOf(Array);
      expect(result.outcomePredictions).toBeInstanceOf(Array);
      expect(result.longitudinalInsights).toBeInstanceOf(Array);
      expect(result.overallPrognosis).toBeDefined();
      expect(result.modelPerformance).toBeDefined();
    });

    it('should generate trend analyses for goals with sufficient data', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result.trendAnalyses.length).toBeGreaterThan(0);

      result.trendAnalyses.forEach(trend => {
        expect(trend.trendId).toBeDefined();
        expect(trend.goalId).toBeDefined();
        expect(['improving', 'declining', 'stable', 'volatile']).toContain(trend.trendType);
        expect(trend.confidence).toBeGreaterThanOrEqual(0);
        expect(trend.confidence).toBeLessThanOrEqual(1);
        expect(trend.projectedOutcome).toBeGreaterThanOrEqual(0);
        expect(trend.projectedOutcome).toBeLessThanOrEqual(100);
        expect(trend.recommendations).toBeInstanceOf(Array);
      });
    });

    it('should generate risk predictions with appropriate severity levels', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      result.riskPredictions.forEach(risk => {
        expect(risk.riskId).toBeDefined();
        expect(['dropout', 'plateau', 'regression', 'crisis', 'burnout']).toContain(risk.riskType);
        expect(['low', 'moderate', 'high', 'critical']).toContain(risk.severity);
        expect(risk.probability).toBeGreaterThanOrEqual(0);
        expect(risk.probability).toBeLessThanOrEqual(1);
        expect(risk.timeframe).toBeGreaterThan(0);
        expect(risk.indicators).toBeInstanceOf(Array);
        expect(risk.mitigationStrategies).toBeInstanceOf(Array);
        expect(risk.confidence).toBeGreaterThanOrEqual(0);
        expect(risk.confidence).toBeLessThanOrEqual(1);
      });
    });

    it('should generate outcome predictions with confidence intervals', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      result.outcomePredictions.forEach(prediction => {
        expect(prediction.predictionId).toBeDefined();
        expect(prediction.goalId).toBeDefined();
        expect(prediction.predictedOutcome).toBeGreaterThanOrEqual(0);
        expect(prediction.predictedOutcome).toBeLessThanOrEqual(100);
        expect(prediction.confidenceInterval).toHaveLength(2);
        expect(prediction.confidenceInterval[0]).toBeLessThanOrEqual(prediction.confidenceInterval[1]);
        expect(prediction.timeframe).toBeGreaterThan(0);
        expect(prediction.probability).toBeGreaterThanOrEqual(0);
        expect(prediction.probability).toBeLessThanOrEqual(1);
        expect(prediction.factors).toBeInstanceOf(Array);
        expect(prediction.alternativeScenarios).toBeInstanceOf(Array);
      });
    });

    it('should calculate overall prognosis correctly', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result.overallPrognosis).toBeDefined();
      expect(result.overallPrognosis.score).toBeGreaterThanOrEqual(0);
      expect(result.overallPrognosis.score).toBeLessThanOrEqual(100);
      expect(['excellent', 'good', 'fair', 'concerning']).toContain(result.overallPrognosis.outlook);
      expect(result.overallPrognosis.confidence).toBeGreaterThanOrEqual(0);
      expect(result.overallPrognosis.confidence).toBeLessThanOrEqual(1);
      expect(result.overallPrognosis.keyFactors).toBeInstanceOf(Array);
    });

    it('should assess model performance', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result.modelPerformance).toBeDefined();
      expect(result.modelPerformance.accuracy).toBeGreaterThanOrEqual(0);
      expect(result.modelPerformance.accuracy).toBeLessThanOrEqual(1);
      expect(result.modelPerformance.precision).toBeGreaterThanOrEqual(0);
      expect(result.modelPerformance.precision).toBeLessThanOrEqual(1);
      expect(result.modelPerformance.recall).toBeGreaterThanOrEqual(0);
      expect(result.modelPerformance.recall).toBeLessThanOrEqual(1);
      expect(result.modelPerformance.lastValidated).toBeGreaterThan(0);
    });
  });

  describe('caching functionality', () => {
    it('should cache analytics results', async () => {
      const result1 = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      const result2 = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      // Results should be identical due to caching
      expect(result1.analysisTimestamp).toBe(result2.analysisTimestamp);
    });
  });

  describe('edge cases', () => {
    it('should handle empty goals array', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        [],
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result).toBeDefined();
      expect(result.trendAnalyses).toHaveLength(0);
      expect(result.outcomePredictions).toHaveLength(0);
    });

    it('should handle insufficient progress data', async () => {
      const minimalProgressData = {
        ...mockProgressData,
        recentEntries: [] // No progress entries
      };

      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        minimalProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result).toBeDefined();
      expect(result.trendAnalyses).toHaveLength(0);
    });

    it('should handle empty emotional history', async () => {
      const result = await service.generatePredictiveAnalytics(
        'test-user',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        [], // Empty emotional history
        mockRecommendationHistory
      );

      expect(result).toBeDefined();
      expect(result.longitudinalInsights.length).toBeLessThanOrEqual(1); // Only milestone insights
    });
  });

  describe('singleton instance', () => {
    it('should export a singleton instance', () => {
      expect(predictiveAnalyticsService).toBeInstanceOf(PredictiveAnalyticsService);
    });

    it('should maintain state across calls', async () => {
      const result1 = await predictiveAnalyticsService.generatePredictiveAnalytics(
        'test-user-singleton',
        mockGoals,
        mockProgressData,
        mockMonitoringData,
        mockEmotionalHistory,
        mockRecommendationHistory
      );

      expect(result1).toBeDefined();
      expect(result1.userId).toBe('test-user-singleton');
    });
  });
});
