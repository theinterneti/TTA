/**
 * Goal Progress Service for TherapeuticGoalsSelector
 *
 * This service provides progress tracking, dynamic goal evolution, and
 * progress-based recommendations for therapeutic goals.
 */

export interface GoalProgress {
  goalId: string;
  progress: number; // 0-100 percentage
  startDate: Date;
  lastUpdated: Date;
  milestones: GoalMilestone[];
  progressHistory: ProgressEntry[];
  status: GoalStatus;
  estimatedCompletion?: Date;
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  therapeuticApproaches: string[];
}

export interface GoalMilestone {
  id: string;
  description: string;
  targetProgress: number; // 0-100
  achieved: boolean;
  achievedDate?: Date;
  evidence?: string[];
  therapeuticValue: 'low' | 'medium' | 'high';
}

export interface ProgressEntry {
  date: Date;
  progress: number;
  notes?: string;
  sessionId?: string;
  therapeuticInsight?: string;
  emotionalState?: EmotionalState;
}

export interface EmotionalState {
  valence: number; // -100 to 100 (negative to positive)
  arousal: number; // 0-100 (calm to excited)
  confidence: number; // 0-100
}

export type GoalStatus = 'not_started' | 'in_progress' | 'completed' | 'paused' | 'archived';

export interface ProgressBasedRecommendation {
  type: 'goal_adjustment' | 'new_goal' | 'milestone_focus' | 'approach_change';
  goalId: string;
  recommendation: string;
  reason: string;
  confidence: number; // 0-1 scale
  urgency: 'low' | 'medium' | 'high';
  clinicalEvidence: 'high' | 'medium' | 'low';
}

export interface GoalEvolutionSuggestion {
  currentGoalId: string;
  suggestedEvolution: string;
  evolutionType: 'expand' | 'refine' | 'split' | 'merge' | 'graduate';
  reason: string;
  confidence: number;
  requiredProgress: number; // minimum progress needed for evolution
}

export interface ProgressAnalytics {
  overallProgress: number; // 0-100 average across all goals
  progressTrend: 'improving' | 'stable' | 'declining';
  completionRate: number; // percentage of goals completed
  averageTimeToCompletion: number; // days
  mostEffectiveApproaches: string[];
  strugglingAreas: string[];
  readinessForAdvancement: number; // 0-1 scale
  recommendedNextSteps: string[];
}

/**
 * Default milestones for common therapeutic goals
 */
const DEFAULT_GOAL_MILESTONES: Record<string, GoalMilestone[]> = {
  'anxiety_reduction': [
    {
      id: 'anxiety_awareness',
      description: 'Recognize anxiety triggers and physical symptoms',
      targetProgress: 25,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'coping_techniques',
      description: 'Learn and practice 3+ anxiety management techniques',
      targetProgress: 50,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'daily_application',
      description: 'Apply anxiety management techniques in daily situations',
      targetProgress: 75,
      achieved: false,
      therapeuticValue: 'medium'
    },
    {
      id: 'anxiety_mastery',
      description: 'Consistently manage anxiety with minimal impact on daily life',
      targetProgress: 100,
      achieved: false,
      therapeuticValue: 'high'
    }
  ],
  'stress_management': [
    {
      id: 'stress_identification',
      description: 'Identify personal stress patterns and triggers',
      targetProgress: 30,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'stress_toolkit',
      description: 'Develop personalized stress management toolkit',
      targetProgress: 60,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'preventive_strategies',
      description: 'Implement preventive stress management strategies',
      targetProgress: 85,
      achieved: false,
      therapeuticValue: 'medium'
    },
    {
      id: 'stress_resilience',
      description: 'Maintain resilience under high-stress situations',
      targetProgress: 100,
      achieved: false,
      therapeuticValue: 'high'
    }
  ],
  'confidence_building': [
    {
      id: 'self_awareness',
      description: 'Identify strengths and areas for growth',
      targetProgress: 25,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'positive_self_talk',
      description: 'Replace negative self-talk with supportive inner dialogue',
      targetProgress: 50,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'achievement_recognition',
      description: 'Acknowledge and celebrate personal achievements',
      targetProgress: 75,
      achieved: false,
      therapeuticValue: 'medium'
    },
    {
      id: 'confident_action',
      description: 'Take confident action in challenging situations',
      targetProgress: 100,
      achieved: false,
      therapeuticValue: 'high'
    }
  ],
  'emotional_processing': [
    {
      id: 'emotion_identification',
      description: 'Accurately identify and name emotions',
      targetProgress: 30,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'emotion_acceptance',
      description: 'Accept emotions without judgment',
      targetProgress: 60,
      achieved: false,
      therapeuticValue: 'high'
    },
    {
      id: 'healthy_expression',
      description: 'Express emotions in healthy, constructive ways',
      targetProgress: 85,
      achieved: false,
      therapeuticValue: 'medium'
    },
    {
      id: 'emotional_wisdom',
      description: 'Use emotional insights for personal growth',
      targetProgress: 100,
      achieved: false,
      therapeuticValue: 'high'
    }
  ]
};

/**
 * Create initial progress tracking for a new goal
 */
export function initializeGoalProgress(goalId: string): GoalProgress {
  const now = new Date();

  return {
    goalId,
    progress: 0,
    startDate: now,
    lastUpdated: now,
    milestones: DEFAULT_GOAL_MILESTONES[goalId]?.map(m => ({ ...m })) || [],
    progressHistory: [{
      date: now,
      progress: 0,
      notes: 'Goal initiated'
    }],
    status: 'not_started',
    difficultyLevel: 'beginner',
    therapeuticApproaches: []
  };
}

/**
 * Update goal progress and check for milestone achievements
 */
export function updateGoalProgress(
  goalProgress: GoalProgress,
  newProgress: number,
  notes?: string,
  emotionalState?: EmotionalState
): GoalProgress {
  const now = new Date();
  const updatedProgress = { ...goalProgress };

  // Update progress
  updatedProgress.progress = Math.max(0, Math.min(100, newProgress));
  updatedProgress.lastUpdated = now;

  // Add progress entry
  updatedProgress.progressHistory.push({
    date: now,
    progress: newProgress,
    notes,
    emotionalState
  });

  // Check for milestone achievements
  updatedProgress.milestones = updatedProgress.milestones.map(milestone => {
    if (!milestone.achieved && updatedProgress.progress >= milestone.targetProgress) {
      return {
        ...milestone,
        achieved: true,
        achievedDate: now
      };
    }
    return milestone;
  });

  // Update status based on progress
  if (updatedProgress.progress === 0) {
    updatedProgress.status = 'not_started';
  } else if (updatedProgress.progress === 100) {
    updatedProgress.status = 'completed';
  } else {
    updatedProgress.status = 'in_progress';
  }

  // Estimate completion date based on progress trend
  if (updatedProgress.progressHistory.length >= 2) {
    const recentEntries = updatedProgress.progressHistory.slice(-5);
    const progressRate = calculateProgressRate(recentEntries);

    if (progressRate > 0 && updatedProgress.progress < 100) {
      const remainingProgress = 100 - updatedProgress.progress;
      const estimatedDays = remainingProgress / progressRate;
      updatedProgress.estimatedCompletion = new Date(now.getTime() + estimatedDays * 24 * 60 * 60 * 1000);
    }
  }

  return updatedProgress;
}

/**
 * Calculate progress rate from recent entries
 */
function calculateProgressRate(entries: ProgressEntry[]): number {
  if (entries.length < 2) return 0;

  const first = entries[0];
  const last = entries[entries.length - 1];
  const timeDiff = (last.date.getTime() - first.date.getTime()) / (24 * 60 * 60 * 1000); // days
  const progressDiff = last.progress - first.progress;

  return timeDiff > 0 ? progressDiff / timeDiff : 0;
}

/**
 * Generate progress-based recommendations for goal management
 */
export function generateProgressBasedRecommendations(
  goalProgresses: GoalProgress[],
  primaryConcerns: string[]
): ProgressBasedRecommendation[] {
  const recommendations: ProgressBasedRecommendation[] = [];

  goalProgresses.forEach(goalProgress => {
    // Check for stalled progress
    if (goalProgress.status === 'in_progress' && isProgressStalled(goalProgress)) {
      recommendations.push({
        type: 'goal_adjustment',
        goalId: goalProgress.goalId,
        recommendation: 'Consider adjusting approach or breaking goal into smaller steps',
        reason: 'Progress has stalled for an extended period',
        confidence: 0.8,
        urgency: 'medium',
        clinicalEvidence: 'high'
      });
    }

    // Check for rapid progress
    if (isProgressRapid(goalProgress)) {
      recommendations.push({
        type: 'milestone_focus',
        goalId: goalProgress.goalId,
        recommendation: 'Focus on consolidating gains and preparing for next milestone',
        reason: 'Rapid progress indicates readiness for advancement',
        confidence: 0.9,
        urgency: 'low',
        clinicalEvidence: 'medium'
      });
    }

    // Check for completed goals
    if (goalProgress.status === 'completed') {
      recommendations.push({
        type: 'new_goal',
        goalId: goalProgress.goalId,
        recommendation: 'Consider setting advanced goals in this area or exploring related areas',
        reason: 'Goal completed successfully, ready for progression',
        confidence: 0.85,
        urgency: 'low',
        clinicalEvidence: 'high'
      });
    }
  });

  return recommendations.sort((a, b) => {
    // Sort by urgency first, then confidence
    const urgencyWeight = { high: 3, medium: 2, low: 1 };
    const urgencyDiff = urgencyWeight[b.urgency] - urgencyWeight[a.urgency];
    if (urgencyDiff !== 0) return urgencyDiff;

    return b.confidence - a.confidence;
  });
}

/**
 * Check if progress has stalled
 */
function isProgressStalled(goalProgress: GoalProgress): boolean {
  const recentEntries = goalProgress.progressHistory.slice(-3);
  if (recentEntries.length < 2) return false;

  const progressRate = calculateProgressRate(recentEntries);
  const daysSinceLastUpdate = (new Date().getTime() - goalProgress.lastUpdated.getTime()) / (24 * 60 * 60 * 1000);

  return progressRate <= 0.5 && daysSinceLastUpdate > 7; // Less than 0.5% progress per day and no update in 7 days
}

/**
 * Check if progress is rapid
 */
function isProgressRapid(goalProgress: GoalProgress): boolean {
  const recentEntries = goalProgress.progressHistory.slice(-3);
  if (recentEntries.length < 2) return false;

  const progressRate = calculateProgressRate(recentEntries);
  return progressRate > 5; // More than 5% progress per day
}

/**
 * Generate goal evolution suggestions based on progress
 */
export function generateGoalEvolutionSuggestions(
  goalProgresses: GoalProgress[]
): GoalEvolutionSuggestion[] {
  const suggestions: GoalEvolutionSuggestion[] = [];

  goalProgresses.forEach(goalProgress => {
    if (goalProgress.progress >= 75) {
      // Suggest graduation to advanced goals
      suggestions.push({
        currentGoalId: goalProgress.goalId,
        suggestedEvolution: getAdvancedGoalSuggestion(goalProgress.goalId),
        evolutionType: 'graduate',
        reason: 'High progress indicates readiness for advanced challenges',
        confidence: 0.8,
        requiredProgress: 75
      });
    }

    if (goalProgress.progress >= 50 && hasMultipleStrugglingAreas(goalProgress)) {
      // Suggest splitting complex goals
      suggestions.push({
        currentGoalId: goalProgress.goalId,
        suggestedEvolution: getSplitGoalSuggestion(goalProgress.goalId),
        evolutionType: 'split',
        reason: 'Goal complexity suggests benefit from focused sub-goals',
        confidence: 0.7,
        requiredProgress: 50
      });
    }
  });

  return suggestions.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Get advanced goal suggestion for graduation
 */
function getAdvancedGoalSuggestion(goalId: string): string {
  const advancedGoals: Record<string, string> = {
    'anxiety_reduction': 'Advanced anxiety management and helping others',
    'stress_management': 'Stress resilience coaching and leadership under pressure',
    'confidence_building': 'Public speaking and mentoring others',
    'emotional_processing': 'Emotional intelligence and empathetic leadership'
  };

  return advancedGoals[goalId] || `Advanced ${goalId.replace(/_/g, ' ')} mastery`;
}

/**
 * Get split goal suggestion for complex goals
 */
function getSplitGoalSuggestion(goalId: string): string {
  const splitSuggestions: Record<string, string> = {
    'anxiety_reduction': 'Separate social anxiety and performance anxiety goals',
    'stress_management': 'Focus on work stress vs. personal stress separately',
    'confidence_building': 'Split into self-confidence and social confidence',
    'emotional_processing': 'Separate emotional awareness from emotional expression'
  };

  return splitSuggestions[goalId] || `Break ${goalId.replace(/_/g, ' ')} into focused sub-goals`;
}

/**
 * Check if goal has multiple struggling areas
 */
function hasMultipleStrugglingAreas(goalProgress: GoalProgress): boolean {
  const unachievedMilestones = goalProgress.milestones.filter(m => !m.achieved);
  const overdueMilestones = unachievedMilestones.filter(m =>
    goalProgress.progress >= m.targetProgress - 10 // Within 10% of target but not achieved
  );

  return overdueMilestones.length >= 2;
}
