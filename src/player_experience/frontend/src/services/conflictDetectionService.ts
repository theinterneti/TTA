// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Services/Conflictdetectionservice]]
/**
 * Enhanced Conflict Detection Service
 *
 * Provides real-time conflict detection for therapeutic goal combinations with
 * intelligent analysis, user-friendly warnings, and resolution guidance.
 * Implements evidence-based therapeutic principles for optimal goal planning.
 */

import { GoalConflict, GoalRelationship } from './goalRelationshipService';
import { GoalProgress } from './goalProgressService';
import { TherapeuticApproachAnalysis } from './therapeuticApproachAlignmentService';

export interface ConflictSeverityLevel {
  level: 'low' | 'medium' | 'high' | 'critical';
  score: number; // 0-1 scale
  description: string;
  urgency: 'monitor' | 'address_soon' | 'address_now' | 'immediate_action';
}

export interface ConflictResolutionStrategy {
  strategyId: string;
  title: string;
  description: string;
  steps: string[];
  expectedOutcome: string;
  timeframe: string;
  difficulty: 'easy' | 'moderate' | 'challenging';
  clinicalEvidence: 'high' | 'medium' | 'low';
  priority: number; // 1-5, 1 being highest priority
}

export interface EnhancedGoalConflict extends GoalConflict {
  conflictId: string;
  detectedAt: Date;
  severityLevel: ConflictSeverityLevel;
  resolutionStrategies: ConflictResolutionStrategy[];
  impactAnalysis: {
    affectedGoals: string[];
    therapeuticRisk: number; // 0-1 scale
    progressImpact: number; // 0-1 scale
    userExperienceImpact: number; // 0-1 scale
  };
  contextualFactors: {
    userProgressLevel: 'beginner' | 'intermediate' | 'advanced';
    goalComplexity: number; // 0-1 scale
    timeConstraints: boolean;
    resourceLimitations: boolean;
  };
  autoResolvable: boolean;
  userActionRequired: boolean;
}

export interface ConflictDetectionResult {
  conflicts: EnhancedGoalConflict[];
  overallRiskScore: number; // 0-1 scale
  recommendedActions: string[];
  safeToProceeed: boolean;
  warningLevel: 'none' | 'low' | 'medium' | 'high' | 'critical';
  summary: {
    totalConflicts: number;
    criticalConflicts: number;
    resolvableConflicts: number;
    monitoringRequired: number;
  };
}

// Enhanced conflict patterns with more sophisticated detection
const ENHANCED_CONFLICT_PATTERNS: Array<{
  pattern: string[];
  detector: (goals: string[], progress?: GoalProgress[], approaches?: TherapeuticApproachAnalysis) => EnhancedGoalConflict | null;
}> = [
  {
    pattern: ['perfectionism_management', 'high_achievement', 'performance_optimization'],
    detector: (goals, progress, approaches) => {
      const conflictingGoals = goals.filter(g =>
        ['perfectionism_management', 'high_achievement', 'performance_optimization'].includes(g)
      );

      if (conflictingGoals.length >= 2) {
        const severity = calculateSeverityLevel(conflictingGoals, progress);

        return {
          conflictId: `perfectionism-achievement-${Date.now()}`,
          conflictingGoals,
          conflictType: 'approach_incompatibility',
          severity: severity.level as 'low' | 'medium' | 'high',
          description: 'Perfectionism management conflicts with high achievement goals, potentially creating internal tension and self-sabotage patterns',
          resolutionSuggestions: [
            'Reframe achievement goals as "excellence" rather than "perfection"',
            'Set realistic, measurable achievement milestones',
            'Practice self-compassion during goal pursuit'
          ],
          clinicalGuidance: 'Address perfectionism patterns first to enable healthy achievement motivation',
          detectedAt: new Date(),
          severityLevel: severity,
          resolutionStrategies: [
            {
              strategyId: 'reframe-excellence',
              title: 'Reframe Achievement as Excellence',
              description: 'Transform perfectionist achievement goals into excellence-focused objectives',
              steps: [
                'Identify specific perfectionist thoughts and behaviors',
                'Rewrite achievement goals with realistic standards',
                'Practice "good enough" mindset for non-critical tasks',
                'Celebrate progress over perfection'
              ],
              expectedOutcome: 'Reduced anxiety and increased sustainable achievement',
              timeframe: '4-6 weeks',
              difficulty: 'moderate',
              clinicalEvidence: 'high',
              priority: 1
            }
          ],
          impactAnalysis: {
            affectedGoals: conflictingGoals,
            therapeuticRisk: 0.7,
            progressImpact: 0.6,
            userExperienceImpact: 0.5
          },
          contextualFactors: {
            userProgressLevel: 'intermediate',
            goalComplexity: 0.8,
            timeConstraints: false,
            resourceLimitations: false
          },
          autoResolvable: false,
          userActionRequired: true
        };
      }
      return null;
    }
  },
  {
    pattern: ['anxiety_reduction', 'social_confidence', 'public_speaking', 'assertiveness'],
    detector: (goals, progress, approaches) => {
      const anxietyRelatedGoals = goals.filter(g =>
        ['anxiety_reduction', 'social_confidence', 'public_speaking', 'assertiveness'].includes(g)
      );

      if (anxietyRelatedGoals.length >= 3) {
        const severity = calculateSeverityLevel(anxietyRelatedGoals, progress);

        return {
          conflictId: `cognitive-overload-${Date.now()}`,
          conflictingGoals: anxietyRelatedGoals,
          conflictType: 'cognitive_overload',
          severity: severity.level as 'low' | 'medium' | 'high',
          description: 'Multiple anxiety-related goals may overwhelm cognitive resources and create performance pressure',
          resolutionSuggestions: [
            'Prioritize foundational anxiety reduction first',
            'Sequence social goals in order of difficulty',
            'Consider combining related goals into broader objectives'
          ],
          clinicalGuidance: 'Start with core anxiety management before specific social challenges',
          detectedAt: new Date(),
          severityLevel: severity,
          resolutionStrategies: [
            {
              strategyId: 'sequential-approach',
              title: 'Sequential Goal Approach',
              description: 'Address anxiety-related goals in therapeutic sequence',
              steps: [
                'Focus on general anxiety reduction techniques first',
                'Build foundational coping skills',
                'Gradually introduce social confidence work',
                'Add specific challenges like public speaking last'
              ],
              expectedOutcome: 'Reduced overwhelm and more sustainable progress',
              timeframe: '8-12 weeks',
              difficulty: 'easy',
              clinicalEvidence: 'high',
              priority: 1
            }
          ],
          impactAnalysis: {
            affectedGoals: anxietyRelatedGoals,
            therapeuticRisk: 0.6,
            progressImpact: 0.8,
            userExperienceImpact: 0.7
          },
          contextualFactors: {
            userProgressLevel: 'beginner',
            goalComplexity: 0.7,
            timeConstraints: true,
            resourceLimitations: false
          },
          autoResolvable: true,
          userActionRequired: false
        };
      }
      return null;
    }
  }
];

/**
 * Calculates severity level based on goals and progress
 */
function calculateSeverityLevel(
  conflictingGoals: string[],
  progress?: GoalProgress[]
): ConflictSeverityLevel {
  const goalCount = conflictingGoals.length;
  const hasProgress = progress && progress.length > 0;

  // Base severity on number of conflicting goals
  let score = Math.min(goalCount / 5, 1); // Normalize to 0-1

  // Adjust based on progress - conflicts are more severe with active progress
  if (hasProgress) {
    const avgProgress = progress
      .filter(p => conflictingGoals.includes(p.goalId))
      .reduce((sum, p) => sum + p.progress, 0) / conflictingGoals.length;

    if (avgProgress > 0.5) {
      score += 0.2; // Higher severity if goals are actively being worked on
    }
  }

  score = Math.min(score, 1);

  if (score >= 0.8) {
    return {
      level: 'critical',
      score,
      description: 'Critical conflict requiring immediate attention',
      urgency: 'immediate_action'
    };
  } else if (score >= 0.6) {
    return {
      level: 'high',
      score,
      description: 'High-priority conflict that should be addressed soon',
      urgency: 'address_now'
    };
  } else if (score >= 0.4) {
    return {
      level: 'medium',
      score,
      description: 'Moderate conflict that may impact progress',
      urgency: 'address_soon'
    };
  } else {
    return {
      level: 'low',
      score,
      description: 'Low-level conflict to monitor',
      urgency: 'monitor'
    };
  }
}

/**
 * Enhanced conflict detection with real-time analysis
 */
export function detectGoalConflicts(
  selectedGoals: string[],
  goalProgresses?: GoalProgress[],
  approachAnalysis?: TherapeuticApproachAnalysis
): ConflictDetectionResult {
  const conflicts: EnhancedGoalConflict[] = [];

  // Run enhanced pattern detection
  ENHANCED_CONFLICT_PATTERNS.forEach(({ pattern, detector }) => {
    const conflict = detector(selectedGoals, goalProgresses, approachAnalysis);
    if (conflict) {
      conflicts.push(conflict);
    }
  });

  // Calculate overall risk score
  const overallRiskScore = conflicts.length > 0
    ? conflicts.reduce((sum, c) => sum + c.severityLevel.score, 0) / conflicts.length
    : 0;

  // Determine warning level
  const warningLevel = overallRiskScore >= 0.8 ? 'critical' :
                      overallRiskScore >= 0.6 ? 'high' :
                      overallRiskScore >= 0.4 ? 'medium' :
                      overallRiskScore > 0 ? 'low' : 'none';

  // Generate recommended actions
  const recommendedActions = generateRecommendedActions(conflicts);

  // Determine if safe to proceed
  const safeToProceeed = conflicts.filter(c => c.severityLevel.level === 'critical').length === 0;

  return {
    conflicts,
    overallRiskScore,
    recommendedActions,
    safeToProceeed,
    warningLevel,
    summary: {
      totalConflicts: conflicts.length,
      criticalConflicts: conflicts.filter(c => c.severityLevel.level === 'critical').length,
      resolvableConflicts: conflicts.filter(c => c.autoResolvable).length,
      monitoringRequired: conflicts.filter(c => c.severityLevel.urgency === 'monitor').length
    }
  };
}

/**
 * Generates recommended actions based on detected conflicts
 */
function generateRecommendedActions(conflicts: EnhancedGoalConflict[]): string[] {
  const actions: string[] = [];

  const criticalConflicts = conflicts.filter(c => c.severityLevel.level === 'critical');
  const highConflicts = conflicts.filter(c => c.severityLevel.level === 'high');
  const autoResolvable = conflicts.filter(c => c.autoResolvable);

  if (criticalConflicts.length > 0) {
    actions.push('🚨 Address critical conflicts immediately before proceeding');
    actions.push('Consider removing or modifying conflicting goals');
  }

  if (highConflicts.length > 0) {
    actions.push('⚠️ Review high-priority conflicts and apply suggested resolutions');
  }

  if (autoResolvable.length > 0) {
    actions.push('✨ Apply automatic conflict resolution for compatible goals');
  }

  if (conflicts.length > 3) {
    actions.push('📊 Consider reducing the total number of active goals');
  }

  return actions;
}

/**
 * Gets resolution strategies for a specific conflict
 */
export function getConflictResolutionStrategies(conflictId: string): ConflictResolutionStrategy[] {
  // This would typically fetch from a database or more sophisticated matching
  // For now, return default strategies based on conflict type
  return [
    {
      strategyId: 'prioritize-foundation',
      title: 'Prioritize Foundation Goals',
      description: 'Focus on foundational therapeutic goals before advanced objectives',
      steps: [
        'Identify which goals are prerequisites for others',
        'Temporarily pause advanced goals',
        'Focus resources on foundation building',
        'Gradually reintroduce advanced goals'
      ],
      expectedOutcome: 'More stable progress and reduced conflict',
      timeframe: '2-4 weeks',
      difficulty: 'easy',
      clinicalEvidence: 'high',
      priority: 1
    }
  ];
}

/**
 * Applies automatic conflict resolution where possible
 */
export function applyAutomaticResolution(
  conflicts: EnhancedGoalConflict[],
  selectedGoals: string[]
): {
  resolvedConflicts: string[];
  modifiedGoals: string[];
  remainingConflicts: EnhancedGoalConflict[];
} {
  const resolvedConflicts: string[] = [];
  const modifiedGoals = [...selectedGoals];
  const remainingConflicts: EnhancedGoalConflict[] = [];

  conflicts.forEach(conflict => {
    if (conflict.autoResolvable && conflict.severityLevel.level !== 'critical') {
      // Apply automatic resolution logic
      if (conflict.conflictType === 'cognitive_overload') {
        // Remove least important goals or suggest sequencing
        resolvedConflicts.push(conflict.conflictId);
      } else {
        remainingConflicts.push(conflict);
      }
    } else {
      remainingConflicts.push(conflict);
    }
  });

  return {
    resolvedConflicts,
    modifiedGoals,
    remainingConflicts
  };
}
