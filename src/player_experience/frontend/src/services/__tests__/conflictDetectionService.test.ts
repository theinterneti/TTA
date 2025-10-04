/**
 * Tests for Enhanced Conflict Detection Service
 */

import {
  detectGoalConflicts,
  getConflictResolutionStrategies,
  applyAutomaticResolution,
  ConflictDetectionResult,
  EnhancedGoalConflict
} from '../conflictDetectionService';
import { GoalProgress } from '../goalProgressService';
import { TherapeuticApproachAnalysis } from '../therapeuticApproachAlignmentService';

describe('Enhanced Conflict Detection Service', () => {
  const mockGoalProgresses: GoalProgress[] = [
    {
      goalId: 'anxiety_reduction',
      progress: 60,
      status: 'in_progress',
      milestones: [],
      lastUpdated: new Date(),
      progressRate: 0.1,
      estimatedCompletion: new Date(),
      notes: 'Making good progress'
    },
    {
      goalId: 'perfectionism_management',
      progress: 30,
      status: 'in_progress',
      milestones: [],
      lastUpdated: new Date(),
      progressRate: 0.05,
      estimatedCompletion: new Date(),
      notes: 'Challenging but improving'
    }
  ];

  const mockApproachAnalysis: TherapeuticApproachAnalysis = {
    selectedGoals: ['anxiety_reduction', 'perfectionism_management'],
    recommendedApproaches: [],
    approachAlignments: [],
    approachCompatibilities: [],
    overallCoherence: 0.8,
    treatmentEffectivenessScore: 0.7,
    integrationRecommendations: []
  };

  describe('detectGoalConflicts', () => {
    it('detects no conflicts for compatible goals', () => {
      const result = detectGoalConflicts(['mindfulness_practice', 'stress_management']);

      expect(result.conflicts).toHaveLength(0);
      expect(result.overallRiskScore).toBe(0);
      expect(result.warningLevel).toBe('none');
      expect(result.safeToProceeed).toBe(true);
      expect(result.summary.totalConflicts).toBe(0);
    });

    it('detects perfectionism-achievement conflict', () => {
      const result = detectGoalConflicts([
        'perfectionism_management',
        'high_achievement',
        'performance_optimization'
      ]);

      expect(result.conflicts).toHaveLength(1);
      expect(result.conflicts[0].conflictType).toBe('approach_incompatibility');
      expect(result.conflicts[0].conflictingGoals).toContain('perfectionism_management');
      expect(result.conflicts[0].conflictingGoals).toContain('high_achievement');
      expect(result.conflicts[0].severityLevel.level).toBeDefined();
      expect(result.conflicts[0].resolutionStrategies).toHaveLength(1);
      expect(result.conflicts[0].userActionRequired).toBe(true);
      expect(result.conflicts[0].autoResolvable).toBe(false);
    });

    it('detects cognitive overload conflict', () => {
      const result = detectGoalConflicts([
        'anxiety_reduction',
        'social_confidence',
        'public_speaking',
        'assertiveness'
      ]);

      expect(result.conflicts).toHaveLength(1);
      expect(result.conflicts[0].conflictType).toBe('cognitive_overload');
      expect(result.conflicts[0].conflictingGoals).toHaveLength(4);
      expect(result.conflicts[0].autoResolvable).toBe(true);
      expect(result.conflicts[0].userActionRequired).toBe(false);
    });

    it('calculates severity based on progress', () => {
      const result = detectGoalConflicts(
        ['perfectionism_management', 'high_achievement'],
        mockGoalProgresses
      );

      expect(result.conflicts).toHaveLength(1);
      const conflict = result.conflicts[0];
      expect(conflict.severityLevel.score).toBeGreaterThan(0);
      expect(['low', 'medium', 'high', 'critical']).toContain(conflict.severityLevel.level);
      expect(['monitor', 'address_soon', 'address_now', 'immediate_action']).toContain(
        conflict.severityLevel.urgency
      );
    });

    it('provides comprehensive conflict analysis', () => {
      const result = detectGoalConflicts(
        ['perfectionism_management', 'high_achievement', 'anxiety_reduction', 'social_confidence'],
        mockGoalProgresses,
        mockApproachAnalysis
      );

      expect(result.overallRiskScore).toBeGreaterThan(0);
      expect(result.recommendedActions).toBeInstanceOf(Array);
      expect(result.recommendedActions.length).toBeGreaterThan(0);
      expect(result.summary.totalConflicts).toBeGreaterThan(0);
      expect(typeof result.safeToProceeed).toBe('boolean');
    });

    it('handles empty goal list', () => {
      const result = detectGoalConflicts([]);

      expect(result.conflicts).toHaveLength(0);
      expect(result.overallRiskScore).toBe(0);
      expect(result.warningLevel).toBe('none');
      expect(result.safeToProceeed).toBe(true);
    });

    it('handles single goal', () => {
      const result = detectGoalConflicts(['anxiety_reduction']);

      expect(result.conflicts).toHaveLength(0);
      expect(result.overallRiskScore).toBe(0);
      expect(result.warningLevel).toBe('none');
      expect(result.safeToProceeed).toBe(true);
    });
  });

  describe('Severity Level Calculation', () => {
    it('assigns higher severity to conflicts with active progress', () => {
      const withProgress = detectGoalConflicts(
        ['perfectionism_management', 'high_achievement'],
        mockGoalProgresses
      );

      const withoutProgress = detectGoalConflicts(
        ['perfectionism_management', 'high_achievement']
      );

      if (withProgress.conflicts.length > 0 && withoutProgress.conflicts.length > 0) {
        expect(withProgress.conflicts[0].severityLevel.score).toBeGreaterThanOrEqual(
          withoutProgress.conflicts[0].severityLevel.score
        );
      }
    });

    it('assigns critical severity appropriately', () => {
      const result = detectGoalConflicts([
        'perfectionism_management',
        'high_achievement',
        'performance_optimization',
        'anxiety_reduction',
        'social_confidence'
      ]);

      const criticalConflicts = result.conflicts.filter(c => c.severityLevel.level === 'critical');
      expect(result.summary.criticalConflicts).toBe(criticalConflicts.length);
    });
  });

  describe('Resolution Strategies', () => {
    it('provides resolution strategies for conflicts', () => {
      const result = detectGoalConflicts(['perfectionism_management', 'high_achievement']);

      if (result.conflicts.length > 0) {
        const conflict = result.conflicts[0];
        expect(conflict.resolutionStrategies).toBeInstanceOf(Array);
        expect(conflict.resolutionStrategies.length).toBeGreaterThan(0);

        const strategy = conflict.resolutionStrategies[0];
        expect(strategy.strategyId).toBeDefined();
        expect(strategy.title).toBeDefined();
        expect(strategy.description).toBeDefined();
        expect(strategy.steps).toBeInstanceOf(Array);
        expect(strategy.expectedOutcome).toBeDefined();
        expect(strategy.timeframe).toBeDefined();
        expect(['easy', 'moderate', 'challenging']).toContain(strategy.difficulty);
        expect(['high', 'medium', 'low']).toContain(strategy.clinicalEvidence);
        expect(strategy.priority).toBeGreaterThan(0);
      }
    });
  });

  describe('getConflictResolutionStrategies', () => {
    it('returns resolution strategies for a conflict ID', () => {
      const strategies = getConflictResolutionStrategies('test-conflict-id');

      expect(strategies).toBeInstanceOf(Array);
      expect(strategies.length).toBeGreaterThan(0);

      const strategy = strategies[0];
      expect(strategy.strategyId).toBeDefined();
      expect(strategy.title).toBeDefined();
      expect(strategy.steps).toBeInstanceOf(Array);
    });
  });

  describe('applyAutomaticResolution', () => {
    it('resolves auto-resolvable conflicts', () => {
      const conflicts: EnhancedGoalConflict[] = [
        {
          conflictId: 'test-conflict',
          conflictingGoals: ['anxiety_reduction', 'social_confidence'],
          conflictType: 'cognitive_overload',
          severity: 'medium',
          description: 'Test conflict',
          resolutionSuggestions: [],
          clinicalGuidance: 'Test guidance',
          detectedAt: new Date(),
          severityLevel: {
            level: 'medium',
            score: 0.5,
            description: 'Medium severity',
            urgency: 'address_soon'
          },
          resolutionStrategies: [],
          impactAnalysis: {
            affectedGoals: [],
            therapeuticRisk: 0.5,
            progressImpact: 0.5,
            userExperienceImpact: 0.5
          },
          contextualFactors: {
            userProgressLevel: 'intermediate',
            goalComplexity: 0.5,
            timeConstraints: false,
            resourceLimitations: false
          },
          autoResolvable: true,
          userActionRequired: false
        }
      ];

      const result = applyAutomaticResolution(conflicts, ['anxiety_reduction', 'social_confidence']);

      expect(result.resolvedConflicts).toContain('test-conflict');
      expect(result.modifiedGoals).toBeInstanceOf(Array);
      expect(result.remainingConflicts.length).toBeLessThan(conflicts.length);
    });

    it('does not resolve critical conflicts automatically', () => {
      const conflicts: EnhancedGoalConflict[] = [
        {
          conflictId: 'critical-conflict',
          conflictingGoals: ['perfectionism_management', 'high_achievement'],
          conflictType: 'approach_incompatibility',
          severity: 'critical',
          description: 'Critical conflict',
          resolutionSuggestions: [],
          clinicalGuidance: 'Critical guidance',
          detectedAt: new Date(),
          severityLevel: {
            level: 'critical',
            score: 0.9,
            description: 'Critical severity',
            urgency: 'immediate_action'
          },
          resolutionStrategies: [],
          impactAnalysis: {
            affectedGoals: [],
            therapeuticRisk: 0.9,
            progressImpact: 0.9,
            userExperienceImpact: 0.9
          },
          contextualFactors: {
            userProgressLevel: 'beginner',
            goalComplexity: 0.9,
            timeConstraints: true,
            resourceLimitations: true
          },
          autoResolvable: true,
          userActionRequired: true
        }
      ];

      const result = applyAutomaticResolution(conflicts, ['perfectionism_management', 'high_achievement']);

      expect(result.resolvedConflicts).toHaveLength(0);
      expect(result.remainingConflicts).toHaveLength(1);
    });
  });

  describe('Warning Levels', () => {
    it('assigns correct warning levels based on risk score', () => {
      // Test different scenarios to verify warning level assignment
      const lowRisk = detectGoalConflicts(['mindfulness_practice']);
      expect(lowRisk.warningLevel).toBe('none');

      const mediumRisk = detectGoalConflicts(['perfectionism_management', 'high_achievement']);
      expect(['low', 'medium', 'high'].includes(mediumRisk.warningLevel)).toBe(true);
    });
  });

  describe('Impact Analysis', () => {
    it('provides comprehensive impact analysis', () => {
      const result = detectGoalConflicts(['perfectionism_management', 'high_achievement']);

      if (result.conflicts.length > 0) {
        const conflict = result.conflicts[0];
        expect(conflict.impactAnalysis.affectedGoals).toBeInstanceOf(Array);
        expect(conflict.impactAnalysis.therapeuticRisk).toBeGreaterThanOrEqual(0);
        expect(conflict.impactAnalysis.therapeuticRisk).toBeLessThanOrEqual(1);
        expect(conflict.impactAnalysis.progressImpact).toBeGreaterThanOrEqual(0);
        expect(conflict.impactAnalysis.progressImpact).toBeLessThanOrEqual(1);
        expect(conflict.impactAnalysis.userExperienceImpact).toBeGreaterThanOrEqual(0);
        expect(conflict.impactAnalysis.userExperienceImpact).toBeLessThanOrEqual(1);
      }
    });
  });

  describe('Contextual Factors', () => {
    it('includes contextual factors in conflict analysis', () => {
      const result = detectGoalConflicts(['perfectionism_management', 'high_achievement']);

      if (result.conflicts.length > 0) {
        const conflict = result.conflicts[0];
        expect(['beginner', 'intermediate', 'advanced']).toContain(
          conflict.contextualFactors.userProgressLevel
        );
        expect(conflict.contextualFactors.goalComplexity).toBeGreaterThanOrEqual(0);
        expect(conflict.contextualFactors.goalComplexity).toBeLessThanOrEqual(1);
        expect(typeof conflict.contextualFactors.timeConstraints).toBe('boolean');
        expect(typeof conflict.contextualFactors.resourceLimitations).toBe('boolean');
      }
    });
  });
});
