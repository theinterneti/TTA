/**
 * Goal Suggestion Engine for TherapeuticGoalsSelector
 *
 * This service provides intelligent therapeutic goal recommendations based on
 * user-selected primary concerns using evidence-based clinical mappings.
 */

export interface GoalSuggestion {
  goalId: string;
  confidence: number; // 0-1 scale
  reason: string;
  category: string;
  clinicalEvidence: 'high' | 'medium' | 'low';
}

export interface SuggestionResult {
  suggestions: GoalSuggestion[];
  totalConcernsAnalyzed: number;
  suggestionStrength: 'strong' | 'moderate' | 'weak';
  progressBasedRecommendations?: ProgressBasedRecommendation[];
  evolutionSuggestions?: GoalEvolutionSuggestion[];
}

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

export interface GoalProgress {
  goalId: string;
  progress: number; // 0-100 percentage
  status: 'not_started' | 'in_progress' | 'completed' | 'paused' | 'archived';
  milestones: Array<{
    id: string;
    description: string;
    achieved: boolean;
    targetProgress: number;
  }>;
  progressHistory: Array<{
    date: Date;
    progress: number;
    notes?: string;
  }>;
}

/**
 * Clinical evidence-based mappings between primary concerns and therapeutic goals
 * Based on CBT, DBT, ACT, and other evidence-based therapeutic approaches
 */
const CONCERN_TO_GOAL_MAPPINGS: Record<string, Array<{
  goalId: string;
  confidence: number;
  reason: string;
  clinicalEvidence: 'high' | 'medium' | 'low';
}>> = {
  'Work stress': [
    { goalId: 'stress_management', confidence: 0.95, reason: 'Direct correlation with workplace stress reduction techniques', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.85, reason: 'Mindfulness-based stress reduction (MBSR) proven effective for work stress', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.80, reason: 'Building healthy coping mechanisms for workplace challenges', clinicalEvidence: 'high' },
    { goalId: 'boundary_setting', confidence: 0.75, reason: 'Work-life balance and professional boundary management', clinicalEvidence: 'medium' },
  ],

  'Relationship issues': [
    { goalId: 'relationship_skills', confidence: 0.95, reason: 'Direct focus on improving interpersonal relationships', clinicalEvidence: 'high' },
    { goalId: 'communication_skills', confidence: 0.90, reason: 'Communication is fundamental to healthy relationships', clinicalEvidence: 'high' },
    { goalId: 'boundary_setting', confidence: 0.80, reason: 'Healthy boundaries essential for relationship wellbeing', clinicalEvidence: 'high' },
    { goalId: 'emotional_processing', confidence: 0.75, reason: 'Understanding emotions improves relationship dynamics', clinicalEvidence: 'medium' },
  ],

  'Family problems': [
    { goalId: 'communication_skills', confidence: 0.90, reason: 'Family therapy emphasizes communication improvement', clinicalEvidence: 'high' },
    { goalId: 'boundary_setting', confidence: 0.85, reason: 'Healthy family boundaries reduce conflict and stress', clinicalEvidence: 'high' },
    { goalId: 'relationship_skills', confidence: 0.80, reason: 'Family relationships benefit from interpersonal skills', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.75, reason: 'Managing family stress requires effective coping tools', clinicalEvidence: 'medium' },
  ],

  'Financial worries': [
    { goalId: 'stress_management', confidence: 0.90, reason: 'Financial stress is a major stressor requiring management techniques', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.85, reason: 'Healthy coping mechanisms for financial uncertainty', clinicalEvidence: 'high' },
    { goalId: 'anxiety_reduction', confidence: 0.80, reason: 'Financial worries often manifest as anxiety symptoms', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.70, reason: 'Mindfulness helps with financial anxiety and decision-making', clinicalEvidence: 'medium' },
  ],

  'Health concerns': [
    { goalId: 'anxiety_reduction', confidence: 0.90, reason: 'Health anxiety is common and treatable with CBT techniques', clinicalEvidence: 'high' },
    { goalId: 'stress_management', confidence: 0.85, reason: 'Health concerns create significant stress requiring management', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.80, reason: 'Mindfulness-based interventions effective for health anxiety', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.75, reason: 'Adaptive coping strategies for health-related challenges', clinicalEvidence: 'medium' },
  ],

  'Life transitions': [
    { goalId: 'coping_strategies', confidence: 0.90, reason: 'Transitions require adaptive coping mechanisms', clinicalEvidence: 'high' },
    { goalId: 'personal_growth', confidence: 0.85, reason: 'Life transitions offer opportunities for personal development', clinicalEvidence: 'high' },
    { goalId: 'confidence_building', confidence: 0.80, reason: 'Building confidence helps navigate life changes', clinicalEvidence: 'medium' },
    { goalId: 'stress_management', confidence: 0.75, reason: 'Transitions often involve stress that needs management', clinicalEvidence: 'medium' },
  ],

  'Social anxiety': [
    { goalId: 'anxiety_reduction', confidence: 0.95, reason: 'Social anxiety disorder directly addressed through anxiety reduction techniques', clinicalEvidence: 'high' },
    { goalId: 'confidence_building', confidence: 0.85, reason: 'Building self-confidence reduces social anxiety symptoms', clinicalEvidence: 'high' },
    { goalId: 'communication_skills', confidence: 0.80, reason: 'Improved communication skills reduce social anxiety', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.75, reason: 'Mindfulness techniques help manage social anxiety in the moment', clinicalEvidence: 'medium' },
  ],

  'Depression': [
    { goalId: 'emotional_processing', confidence: 0.90, reason: 'Processing emotions is central to depression treatment', clinicalEvidence: 'high' },
    { goalId: 'self_compassion', confidence: 0.85, reason: 'Self-compassion therapy effective for depression', clinicalEvidence: 'high' },
    { goalId: 'personal_growth', confidence: 0.80, reason: 'Personal growth activities counter depressive symptoms', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.75, reason: 'Mindfulness-based cognitive therapy for depression', clinicalEvidence: 'high' },
  ],

  'Perfectionism': [
    { goalId: 'self_compassion', confidence: 0.90, reason: 'Self-compassion directly counters perfectionist self-criticism', clinicalEvidence: 'high' },
    { goalId: 'anxiety_reduction', confidence: 0.85, reason: 'Perfectionism often involves anxiety about performance', clinicalEvidence: 'high' },
    { goalId: 'stress_management', confidence: 0.80, reason: 'Perfectionist tendencies create chronic stress', clinicalEvidence: 'medium' },
    { goalId: 'boundary_setting', confidence: 0.75, reason: 'Setting realistic boundaries and expectations', clinicalEvidence: 'medium' },
  ],

  'Procrastination': [
    { goalId: 'confidence_building', confidence: 0.85, reason: 'Low confidence often underlies procrastination behaviors', clinicalEvidence: 'medium' },
    { goalId: 'stress_management', confidence: 0.80, reason: 'Procrastination often stems from stress avoidance', clinicalEvidence: 'medium' },
    { goalId: 'personal_growth', confidence: 0.75, reason: 'Personal development addresses procrastination patterns', clinicalEvidence: 'medium' },
    { goalId: 'coping_strategies', confidence: 0.70, reason: 'Healthy coping strategies replace procrastination behaviors', clinicalEvidence: 'medium' },
  ],

  'Low self-esteem': [
    { goalId: 'confidence_building', confidence: 0.95, reason: 'Direct correlation between confidence building and self-esteem improvement', clinicalEvidence: 'high' },
    { goalId: 'self_compassion', confidence: 0.90, reason: 'Self-compassion therapy highly effective for low self-esteem', clinicalEvidence: 'high' },
    { goalId: 'personal_growth', confidence: 0.80, reason: 'Personal growth activities build self-worth and esteem', clinicalEvidence: 'high' },
  ],

  'Loneliness': [
    { goalId: 'relationship_skills', confidence: 0.90, reason: 'Building relationship skills addresses loneliness directly', clinicalEvidence: 'high' },
    { goalId: 'communication_skills', confidence: 0.85, reason: 'Better communication helps form meaningful connections', clinicalEvidence: 'high' },
    { goalId: 'confidence_building', confidence: 0.80, reason: 'Confidence helps in social situations and forming relationships', clinicalEvidence: 'medium' },
    { goalId: 'self_compassion', confidence: 0.75, reason: 'Self-compassion reduces self-criticism that can worsen loneliness', clinicalEvidence: 'medium' },
  ],

  'Career uncertainty': [
    { goalId: 'confidence_building', confidence: 0.85, reason: 'Career confidence helps with decision-making and job searching', clinicalEvidence: 'medium' },
    { goalId: 'personal_growth', confidence: 0.80, reason: 'Personal development clarifies career goals and values', clinicalEvidence: 'medium' },
    { goalId: 'stress_management', confidence: 0.75, reason: 'Career uncertainty creates stress requiring management', clinicalEvidence: 'medium' },
    { goalId: 'coping_strategies', confidence: 0.70, reason: 'Coping with career transitions and uncertainty', clinicalEvidence: 'medium' },
  ],

  'Academic pressure': [
    { goalId: 'stress_management', confidence: 0.90, reason: 'Academic stress management is well-researched and effective', clinicalEvidence: 'high' },
    { goalId: 'anxiety_reduction', confidence: 0.85, reason: 'Academic pressure often manifests as performance anxiety', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.80, reason: 'Healthy coping mechanisms for academic challenges', clinicalEvidence: 'high' },
    { goalId: 'mindfulness_development', confidence: 0.75, reason: 'Mindfulness helps with academic focus and stress', clinicalEvidence: 'medium' },
  ],

  'Parenting challenges': [
    { goalId: 'stress_management', confidence: 0.90, reason: 'Parenting stress management is crucial for family wellbeing', clinicalEvidence: 'high' },
    { goalId: 'boundary_setting', confidence: 0.85, reason: 'Healthy boundaries essential in parent-child relationships', clinicalEvidence: 'high' },
    { goalId: 'communication_skills', confidence: 0.80, reason: 'Effective parent-child communication reduces family conflict', clinicalEvidence: 'high' },
    { goalId: 'coping_strategies', confidence: 0.75, reason: 'Parenting requires diverse coping strategies for various challenges', clinicalEvidence: 'medium' },
  ],
};

/**
 * Goal categories for organizing suggestions
 */
const GOAL_CATEGORIES: Record<string, string> = {
  'anxiety_reduction': 'Emotional Wellbeing',
  'stress_management': 'Emotional Wellbeing',
  'emotional_processing': 'Emotional Wellbeing',
  'anger_management': 'Emotional Wellbeing',
  'grief_processing': 'Emotional Wellbeing',
  'confidence_building': 'Self-Development',
  'self_compassion': 'Self-Development',
  'personal_growth': 'Self-Development',
  'boundary_setting': 'Self-Development',
  'relationship_skills': 'Relationships & Communication',
  'communication_skills': 'Relationships & Communication',
  'mindfulness_development': 'Mind-Body Connection',
  'body_awareness': 'Mind-Body Connection',
  'sleep_improvement': 'Mind-Body Connection',
  'coping_strategies': 'Coping & Recovery',
  'trauma_recovery': 'Coping & Recovery',
};

/**
 * Generate therapeutic goal suggestions based on selected primary concerns
 */
export function generateGoalSuggestions(
  primaryConcerns: string[],
  currentlySelected: string[] = [],
  maxSuggestions: number = 5
): SuggestionResult {
  if (primaryConcerns.length === 0) {
    return {
      suggestions: [],
      totalConcernsAnalyzed: 0,
      suggestionStrength: 'weak'
    };
  }

  // Collect all potential suggestions with their scores
  const suggestionMap = new Map<string, GoalSuggestion>();

  primaryConcerns.forEach(concern => {
    const mappings = CONCERN_TO_GOAL_MAPPINGS[concern];
    if (mappings) {
      mappings.forEach(mapping => {
        // Skip if already selected
        if (currentlySelected.includes(mapping.goalId)) {
          return;
        }

        const existingSuggestion = suggestionMap.get(mapping.goalId);
        if (existingSuggestion) {
          // Boost confidence if multiple concerns suggest the same goal
          existingSuggestion.confidence = Math.min(1.0, existingSuggestion.confidence + (mapping.confidence * 0.3));
          existingSuggestion.reason += ` Also helps with ${concern.toLowerCase()}.`;
        } else {
          suggestionMap.set(mapping.goalId, {
            goalId: mapping.goalId,
            confidence: mapping.confidence,
            reason: mapping.reason,
            category: GOAL_CATEGORIES[mapping.goalId] || 'Other',
            clinicalEvidence: mapping.clinicalEvidence
          });
        }
      });
    }
  });

  // Sort suggestions by confidence and clinical evidence
  const sortedSuggestions = Array.from(suggestionMap.values())
    .sort((a, b) => {
      // First sort by clinical evidence (high > medium > low)
      const evidenceWeight = { high: 3, medium: 2, low: 1 };
      const evidenceDiff = evidenceWeight[b.clinicalEvidence] - evidenceWeight[a.clinicalEvidence];
      if (evidenceDiff !== 0) return evidenceDiff;

      // Then by confidence
      return b.confidence - a.confidence;
    })
    .slice(0, maxSuggestions);

  // Determine suggestion strength
  const avgConfidence = sortedSuggestions.reduce((sum, s) => sum + s.confidence, 0) / sortedSuggestions.length;
  const suggestionStrength: 'strong' | 'moderate' | 'weak' =
    avgConfidence >= 0.8 ? 'strong' :
    avgConfidence >= 0.6 ? 'moderate' : 'weak';

  return {
    suggestions: sortedSuggestions,
    totalConcernsAnalyzed: primaryConcerns.length,
    suggestionStrength
  };
}

/**
 * Generate progress-aware goal suggestions that consider current goal progress
 */
export function generateProgressAwareGoalSuggestions(
  primaryConcerns: string[],
  currentlySelected: string[] = [],
  goalProgresses: GoalProgress[] = [],
  maxSuggestions: number = 5
): SuggestionResult {
  // Get base suggestions
  const baseSuggestions = generateGoalSuggestions(primaryConcerns, currentlySelected, maxSuggestions);

  // Generate progress-based recommendations
  const progressRecommendations = generateProgressBasedRecommendations(goalProgresses, primaryConcerns);

  // Generate evolution suggestions
  const evolutionSuggestions = generateGoalEvolutionSuggestions(goalProgresses);

  // Enhance base suggestions with progress insights
  const enhancedSuggestions = baseSuggestions.suggestions.map(suggestion => {
    const relatedProgress = goalProgresses.find(gp => gp.goalId === suggestion.goalId);

    if (relatedProgress) {
      // Adjust confidence based on progress
      let adjustedConfidence = suggestion.confidence;

      if (relatedProgress.status === 'completed') {
        // Lower confidence for completed goals unless it's for advanced work
        adjustedConfidence *= 0.3;
        suggestion.reason += ' Note: This goal was previously completed - consider advanced variations.';
      } else if (relatedProgress.status === 'in_progress') {
        // Boost confidence for goals already in progress
        adjustedConfidence *= 1.2;
        suggestion.reason += ` Current progress: ${relatedProgress.progress}%.`;
      }

      return {
        ...suggestion,
        confidence: Math.min(1.0, adjustedConfidence)
      };
    }

    return suggestion;
  });

  return {
    ...baseSuggestions,
    suggestions: enhancedSuggestions,
    progressBasedRecommendations: progressRecommendations,
    evolutionSuggestions: evolutionSuggestions
  };
}

/**
 * Generate progress-based recommendations for goal management
 */
function generateProgressBasedRecommendations(
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
 * Generate goal evolution suggestions based on progress
 */
function generateGoalEvolutionSuggestions(
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
 * Check if progress has stalled
 */
function isProgressStalled(goalProgress: GoalProgress): boolean {
  if (goalProgress.progressHistory.length < 2) return false;

  const recentEntries = goalProgress.progressHistory.slice(-3);
  const first = recentEntries[0];
  const last = recentEntries[recentEntries.length - 1];

  const timeDiff = (last.date.getTime() - first.date.getTime()) / (24 * 60 * 60 * 1000); // days
  const progressDiff = last.progress - first.progress;
  const progressRate = timeDiff > 0 ? progressDiff / timeDiff : 0;

  return progressRate <= 0.5 && timeDiff > 7; // Less than 0.5% progress per day over 7+ days
}

/**
 * Check if progress is rapid
 */
function isProgressRapid(goalProgress: GoalProgress): boolean {
  if (goalProgress.progressHistory.length < 2) return false;

  const recentEntries = goalProgress.progressHistory.slice(-3);
  const first = recentEntries[0];
  const last = recentEntries[recentEntries.length - 1];

  const timeDiff = (last.date.getTime() - first.date.getTime()) / (24 * 60 * 60 * 1000); // days
  const progressDiff = last.progress - first.progress;
  const progressRate = timeDiff > 0 ? progressDiff / timeDiff : 0;

  return progressRate > 5; // More than 5% progress per day
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
