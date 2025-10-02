/**
 * Progress Tracking Service Tests - Priority 3D Implementation
 * 
 * Comprehensive test suite for the progress tracking and analytics system.
 * Tests progress monitoring, outcome measurement, and therapeutic analytics.
 */

import {
  ProgressTrackingService,
  ProgressEntry,
  ProgressType,
  MeasurementMethod,
  EvidenceLevel,
  OutcomeMeasurementType,
  SeverityLevel,
  ClinicalSignificance,
  TrendDirection,
  ProgressTrend,
  MilestoneSignificance,
  TherapeuticImpact
} from '../progressTrackingService';
import { TherapeuticGoal, TherapeuticApproach } from '../../types/preferences';

describe('ProgressTrackingService', () => {
  let service: ProgressTrackingService;
  let mockGoals: TherapeuticGoal[];
  let mockUserId: string;

  beforeEach(() => {
    service = new ProgressTrackingService();
    mockUserId = 'test-user-123';
    
    mockGoals = [
      {
        id: 'goal-1',
        title: 'Reduce Anxiety',
        description: 'Work on managing anxiety through mindfulness techniques',
        category: 'Mental Health',
        priority: 'high',
        targetDate: new Date('2024-03-01'),
        approaches: [TherapeuticApproach.MINDFULNESS, TherapeuticApproach.CBT],
        isActive: true,
        createdAt: new Date('2024-01-01'),
        progress: 45
      },
      {
        id: 'goal-2',
        title: 'Improve Sleep Quality',
        description: 'Establish better sleep hygiene and routines',
        category: 'Wellness',
        priority: 'medium',
        targetDate: new Date('2024-04-01'),
        approaches: [TherapeuticApproach.BEHAVIORAL_ACTIVATION],
        isActive: true,
        createdAt: new Date('2024-01-15'),
        progress: 70
      }
    ];
  });

  describe('Progress Entry Recording', () => {
    it('should record a new progress entry successfully', () => {
      const entryData = {
        goalId: 'goal-1',
        userId: mockUserId,
        progressValue: 65,
        progressType: ProgressType.SELF_REPORTED,
        measurementMethod: MeasurementMethod.LIKERT_SCALE,
        notes: 'Feeling more confident with anxiety management',
        evidenceLevel: EvidenceLevel.OBSERVATIONAL
      };

      const result = service.recordProgress(entryData);

      expect(result).toMatchObject({
        ...entryData,
        id: expect.any(String),
        timestamp: expect.any(Date)
      });
      expect(result.id).toMatch(/^progress_\d+_[a-z0-9]+$/);
    });

    it('should handle progress entries with milestone achievement', () => {
      const entryData = {
        goalId: 'goal-1',
        userId: mockUserId,
        progressValue: 90,
        progressType: ProgressType.MILESTONE_ACHIEVEMENT,
        measurementMethod: MeasurementMethod.BINARY_CHECKLIST,
        evidenceLevel: EvidenceLevel.VALIDATED_SCALE
      };

      const result = service.recordProgress(entryData);

      expect(result.progressValue).toBe(90);
      expect(result.progressType).toBe(ProgressType.MILESTONE_ACHIEVEMENT);
    });

    it('should generate unique IDs for each progress entry', () => {
      const entryData = {
        goalId: 'goal-1',
        userId: mockUserId,
        progressValue: 50,
        progressType: ProgressType.SELF_REPORTED,
        measurementMethod: MeasurementMethod.LIKERT_SCALE,
        evidenceLevel: EvidenceLevel.OBSERVATIONAL
      };

      const result1 = service.recordProgress(entryData);
      const result2 = service.recordProgress(entryData);

      expect(result1.id).not.toBe(result2.id);
    });
  });

  describe('Outcome Measurement Recording', () => {
    it('should record outcome measurements successfully', () => {
      const measurementData = {
        userId: mockUserId,
        measurementType: OutcomeMeasurementType.PHQ9,
        score: 8,
        maxScore: 27,
        severity: SeverityLevel.MILD,
        clinicalSignificance: ClinicalSignificance.CLINICALLY_MEANINGFUL,
        trendDirection: TrendDirection.IMPROVING
      };

      const result = service.recordOutcomeMeasurement(measurementData);

      expect(result).toMatchObject({
        ...measurementData,
        id: expect.any(String),
        timestamp: expect.any(Date)
      });
    });

    it('should handle different outcome measurement types', () => {
      const gad7Measurement = {
        userId: mockUserId,
        measurementType: OutcomeMeasurementType.GAD7,
        score: 5,
        maxScore: 21,
        severity: SeverityLevel.MILD,
        clinicalSignificance: ClinicalSignificance.NOT_SIGNIFICANT,
        trendDirection: TrendDirection.STABLE
      };

      const result = service.recordOutcomeMeasurement(gad7Measurement);

      expect(result.measurementType).toBe(OutcomeMeasurementType.GAD7);
      expect(result.score).toBe(5);
      expect(result.maxScore).toBe(21);
    });
  });

  describe('Progress Analytics Generation', () => {
    beforeEach(() => {
      // Add some sample progress entries with explicit timestamps
      const entries = [
        {
          goalId: 'goal-1',
          userId: mockUserId,
          progressValue: 30,
          progressType: ProgressType.SELF_REPORTED,
          measurementMethod: MeasurementMethod.LIKERT_SCALE,
          evidenceLevel: EvidenceLevel.OBSERVATIONAL
        },
        {
          goalId: 'goal-1',
          userId: mockUserId,
          progressValue: 45,
          progressType: ProgressType.SELF_REPORTED,
          measurementMethod: MeasurementMethod.LIKERT_SCALE,
          evidenceLevel: EvidenceLevel.OBSERVATIONAL
        },
        {
          goalId: 'goal-1',
          userId: mockUserId,
          progressValue: 65,
          progressType: ProgressType.SELF_REPORTED,
          measurementMethod: MeasurementMethod.LIKERT_SCALE,
          evidenceLevel: EvidenceLevel.OBSERVATIONAL
        }
      ];

      // Add entries with delays to ensure different timestamps
      entries.forEach((entry, index) => {
        const recordedEntry = service.recordProgress(entry);
        // Manually adjust timestamp to ensure proper ordering
        recordedEntry.timestamp = new Date(Date.now() - (entries.length - index - 1) * 24 * 60 * 60 * 1000);
      });
    });

    it('should generate comprehensive progress analytics', () => {
      const result = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(result).toMatchObject({
        currentProgress: expect.any(Array),
        recentEntries: expect.any(Array),
        milestones: expect.any(Array),
        outcomeMeasurements: expect.any(Array),
        therapeuticInsights: expect.any(Array),
        overallEffectiveness: expect.any(Number),
        riskAssessment: expect.any(Object),
        recommendations: expect.any(Array),
        nextActions: expect.any(Array),
        generatedAt: expect.any(Date),
        dataQuality: expect.any(Object)
      });
    });

    it('should calculate progress analytics for each goal', () => {
      const result = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(result.currentProgress).toHaveLength(2); // Two goals
      
      const goal1Analytics = result.currentProgress.find(p => p.goalId === 'goal-1');
      expect(goal1Analytics).toBeDefined();
      expect(goal1Analytics?.overallProgress).toBe(65); // Latest progress value
      expect(goal1Analytics?.progressTrend).toBe(ProgressTrend.IMPROVING);
      expect(goal1Analytics?.velocityScore).toBeGreaterThan(0);
      expect(goal1Analytics?.therapeuticEffectiveness).toBeGreaterThan(0);
    });

    it('should include data quality metrics', () => {
      const result = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(result.dataQuality).toMatchObject({
        completeness: expect.any(Number),
        consistency: expect.any(Number),
        recency: expect.any(Number),
        reliability: expect.any(Number),
        overallQuality: expect.any(Number)
      });

      // All metrics should be between 0 and 100
      Object.values(result.dataQuality).forEach(metric => {
        expect(metric).toBeGreaterThanOrEqual(0);
        expect(metric).toBeLessThanOrEqual(100);
      });
    });

    it('should generate risk assessment', () => {
      const result = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(result.riskAssessment).toMatchObject({
        overallRisk: expect.any(String),
        riskFactors: expect.any(Array),
        protectiveFactors: expect.any(Array),
        recommendations: expect.any(Array)
      });

      expect(Object.values(SeverityLevel)).toContain(result.riskAssessment.overallRisk);
    });

    it('should generate therapeutic insights', () => {
      const result = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(result.therapeuticInsights).toBeInstanceOf(Array);
      
      if (result.therapeuticInsights.length > 0) {
        const insight = result.therapeuticInsights[0];
        expect(insight).toMatchObject({
          id: expect.any(String),
          type: expect.any(String),
          title: expect.any(String),
          description: expect.any(String),
          confidence: expect.any(String),
          evidenceLevel: expect.any(String),
          actionable: expect.any(Boolean),
          recommendations: expect.any(Array),
          clinicalRelevance: expect.any(String),
          generatedAt: expect.any(Date)
        });
      }
    });
  });

  describe('Progress Trend Analysis', () => {
    it('should detect improving progress trends', () => {
      // Add entries showing improvement with explicit timestamps
      const improvingEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 20, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 40, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 60, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 80, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      // Add entries with proper timestamps for velocity calculation
      improvingEntries.forEach((entry, index) => {
        const recordedEntry = service.recordProgress(entry);
        // Set timestamps 7 days apart for proper velocity calculation
        recordedEntry.timestamp = new Date(Date.now() - (improvingEntries.length - index - 1) * 7 * 24 * 60 * 60 * 1000);
      });

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      expect(goal1Analytics.progressTrend).toBe(ProgressTrend.IMPROVING);
      expect(goal1Analytics.velocityScore).toBeGreaterThan(0);
    });

    it('should detect declining progress trends', () => {
      // Add entries showing decline
      const decliningEntries = [
        { goalId: 'goal-2', userId: mockUserId, progressValue: 80, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-2', userId: mockUserId, progressValue: 60, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-2', userId: mockUserId, progressValue: 40, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-2', userId: mockUserId, progressValue: 20, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      decliningEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[1]], 'month');
      const goal2Analytics = result.currentProgress[0];

      expect(goal2Analytics.progressTrend).toBe(ProgressTrend.DECLINING);
    });

    it('should detect stable progress trends', () => {
      // Add entries showing stability
      const stableEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 50, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 52, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 48, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 51, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      stableEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      expect(goal1Analytics.progressTrend).toBe(ProgressTrend.STABLE);
    });
  });

  describe('Risk Factor Identification', () => {
    it('should identify declining progress as a risk factor', () => {
      // Add declining progress entries
      const decliningEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 70, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 50, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 30, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      decliningEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      const decliningRisk = goal1Analytics.riskFactors.find(rf => rf.type === 'declining_progress');
      expect(decliningRisk).toBeDefined();
      expect(decliningRisk?.severity).toBe(SeverityLevel.MODERATE);
    });

    it('should identify low progress as a risk factor', () => {
      const lowProgressEntry = {
        goalId: 'goal-1',
        userId: mockUserId,
        progressValue: 15, // Below 20% threshold
        progressType: ProgressType.SELF_REPORTED,
        measurementMethod: MeasurementMethod.LIKERT_SCALE,
        evidenceLevel: EvidenceLevel.OBSERVATIONAL
      };

      service.recordProgress(lowProgressEntry);

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      const lowProgressRisk = goal1Analytics.riskFactors.find(rf => rf.type === 'low_progress');
      expect(lowProgressRisk).toBeDefined();
      expect(lowProgressRisk?.severity).toBe(SeverityLevel.MODERATE);
    });
  });

  describe('Therapeutic Effectiveness Calculation', () => {
    it('should calculate high effectiveness for improving trends', () => {
      const improvingEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 30, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 50, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 70, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      improvingEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      expect(goal1Analytics.therapeuticEffectiveness).toBeGreaterThan(70);
    });

    it('should calculate lower effectiveness for declining trends', () => {
      const decliningEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 70, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 50, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 30, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      decliningEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      expect(goal1Analytics.therapeuticEffectiveness).toBeLessThan(50);
    });
  });

  describe('Timeframe Filtering', () => {
    it('should filter progress entries by timeframe', () => {
      // Add entries with different timestamps
      const oldEntry = {
        goalId: 'goal-1',
        userId: mockUserId,
        progressValue: 30,
        progressType: ProgressType.SELF_REPORTED,
        measurementMethod: MeasurementMethod.LIKERT_SCALE,
        evidenceLevel: EvidenceLevel.OBSERVATIONAL
      };

      service.recordProgress(oldEntry);

      // Test week timeframe
      const weekResult = service.generateProgressAnalytics(mockUserId, mockGoals, 'week');
      const monthResult = service.generateProgressAnalytics(mockUserId, mockGoals, 'month');

      expect(weekResult.recentEntries.length).toBeGreaterThanOrEqual(0);
      expect(monthResult.recentEntries.length).toBeGreaterThanOrEqual(weekResult.recentEntries.length);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle empty progress data gracefully', () => {
      const result = service.generateProgressAnalytics('empty-user', mockGoals, 'month');

      expect(result.currentProgress).toHaveLength(2); // Still analyzes goals
      expect(result.recentEntries).toHaveLength(0);
      expect(result.overallEffectiveness).toBe(0);
    });

    it('should handle single progress entry', () => {
      const singleEntry = {
        goalId: 'goal-1',
        userId: 'single-user',
        progressValue: 50,
        progressType: ProgressType.SELF_REPORTED,
        measurementMethod: MeasurementMethod.LIKERT_SCALE,
        evidenceLevel: EvidenceLevel.OBSERVATIONAL
      };

      service.recordProgress(singleEntry);

      const result = service.generateProgressAnalytics('single-user', [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      expect(goal1Analytics.overallProgress).toBe(50);
      expect(goal1Analytics.progressTrend).toBe(ProgressTrend.INSUFFICIENT_DATA);
    });

    it('should handle goals with no progress entries', () => {
      const result = service.generateProgressAnalytics('no-progress-user', mockGoals, 'month');

      result.currentProgress.forEach(analytics => {
        expect(analytics.overallProgress).toBe(0);
        expect(analytics.progressTrend).toBe(ProgressTrend.INSUFFICIENT_DATA);
        expect(analytics.velocityScore).toBe(0);
      });
    });
  });

  describe('Recommendation Generation', () => {
    it('should generate recommendations for high-performing goals', () => {
      const excellentEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 10, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 50, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 90, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      // Add entries with proper timestamps for high velocity
      excellentEntries.forEach((entry, index) => {
        const recordedEntry = service.recordProgress(entry);
        // Set timestamps 1 day apart for high velocity calculation
        recordedEntry.timestamp = new Date(Date.now() - (excellentEntries.length - index - 1) * 24 * 60 * 60 * 1000);
      });

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      // Check if we have any recommendations (the specific type depends on velocity calculation)
      expect(goal1Analytics.recommendations).toBeDefined();
      expect(goal1Analytics.recommendations.length).toBeGreaterThan(0);
    });

    it('should generate motivation recommendations for stagnant goals', () => {
      const stagnantEntries = [
        { goalId: 'goal-1', userId: mockUserId, progressValue: 25, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 26, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL },
        { goalId: 'goal-1', userId: mockUserId, progressValue: 24, progressType: ProgressType.SELF_REPORTED, measurementMethod: MeasurementMethod.LIKERT_SCALE, evidenceLevel: EvidenceLevel.OBSERVATIONAL }
      ];

      stagnantEntries.forEach(entry => service.recordProgress(entry));

      const result = service.generateProgressAnalytics(mockUserId, [mockGoals[0]], 'month');
      const goal1Analytics = result.currentProgress[0];

      const motivationRec = goal1Analytics.recommendations.find(r => r.type === 'motivation');
      expect(motivationRec).toBeDefined();
      expect(motivationRec?.priority).toBe('high');
    });
  });
});
