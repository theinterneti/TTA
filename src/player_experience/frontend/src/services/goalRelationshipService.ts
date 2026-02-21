// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Services/Goalrelationshipservice]]
/**
 * Goal Relationship Service
 *
 * Provides goal relationship analysis, conflict detection, and complementary goal suggestions
 * for therapeutic goal management. Implements evidence-based therapeutic principles for
 * goal compatibility and synergy analysis.
 */

export interface GoalRelationship {
  sourceGoal: string;
  targetGoal: string;
  relationshipType: 'synergistic' | 'conflicting' | 'neutral' | 'complementary' | 'prerequisite';
  strength: number; // 0-1 scale
  clinicalEvidence: 'high' | 'medium' | 'low';
  description: string;
  therapeuticRationale: string;
}

export interface GoalConflict {
  conflictingGoals: string[];
  conflictType: 'resource_competition' | 'approach_incompatibility' | 'timeline_conflict' | 'cognitive_overload';
  severity: 'low' | 'medium' | 'high';
  description: string;
  resolutionSuggestions: string[];
  clinicalGuidance: string;
}

export interface ComplementaryGoalSuggestion {
  suggestedGoal: string;
  compatibleWith: string[];
  synergy: number; // 0-1 scale
  therapeuticBenefit: string;
  implementationOrder: 'concurrent' | 'sequential' | 'flexible';
  clinicalEvidence: 'high' | 'medium' | 'low';
}

export interface GoalRelationshipMap {
  goals: string[];
  relationships: GoalRelationship[];
  conflicts: GoalConflict[];
  complementarySuggestions: ComplementaryGoalSuggestion[];
  overallCompatibility: number; // 0-1 scale
  therapeuticCoherence: number; // 0-1 scale
}

// Evidence-based goal relationship mappings
const GOAL_RELATIONSHIPS: Record<string, GoalRelationship[]> = {
  'anxiety_reduction': [
    {
      sourceGoal: 'anxiety_reduction',
      targetGoal: 'mindfulness_practice',
      relationshipType: 'synergistic',
      strength: 0.9,
      clinicalEvidence: 'high',
      description: 'Mindfulness practice directly supports anxiety reduction through present-moment awareness',
      therapeuticRationale: 'MBSR and MBCT show strong evidence for anxiety reduction through mindfulness'
    },
    {
      sourceGoal: 'anxiety_reduction',
      targetGoal: 'perfectionism_management',
      relationshipType: 'conflicting',
      strength: 0.7,
      clinicalEvidence: 'high',
      description: 'Perfectionism often maintains and exacerbates anxiety symptoms',
      therapeuticRationale: 'Perfectionism creates unrealistic standards that fuel anxiety and avoidance'
    },
    {
      sourceGoal: 'anxiety_reduction',
      targetGoal: 'confidence_building',
      relationshipType: 'complementary',
      strength: 0.8,
      clinicalEvidence: 'high',
      description: 'Reduced anxiety enables confidence building, while confidence reduces anxiety',
      therapeuticRationale: 'Bidirectional relationship where each goal supports the other\'s achievement'
    }
  ],
  'stress_management': [
    {
      sourceGoal: 'stress_management',
      targetGoal: 'work_life_balance',
      relationshipType: 'synergistic',
      strength: 0.85,
      clinicalEvidence: 'high',
      description: 'Work-life balance is essential for effective stress management',
      therapeuticRationale: 'Boundary setting and time management directly reduce stress sources'
    },
    {
      sourceGoal: 'stress_management',
      targetGoal: 'emotional_processing',
      relationshipType: 'complementary',
      strength: 0.75,
      clinicalEvidence: 'medium',
      description: 'Processing emotions reduces stress accumulation and improves coping',
      therapeuticRationale: 'Emotional awareness and processing prevent stress from becoming chronic'
    }
  ],
  'confidence_building': [
    {
      sourceGoal: 'confidence_building',
      targetGoal: 'social_skills',
      relationshipType: 'synergistic',
      strength: 0.8,
      clinicalEvidence: 'high',
      description: 'Social skills development builds confidence through successful interactions',
      therapeuticRationale: 'Social competence and self-efficacy are mutually reinforcing'
    },
    {
      sourceGoal: 'confidence_building',
      targetGoal: 'perfectionism_management',
      relationshipType: 'prerequisite',
      strength: 0.7,
      clinicalEvidence: 'medium',
      description: 'Managing perfectionism is often necessary before building genuine confidence',
      therapeuticRationale: 'Perfectionism undermines confidence by setting unrealistic standards'
    }
  ]
};

// Goal conflict patterns
const CONFLICT_PATTERNS: GoalConflict[] = [
  {
    conflictingGoals: ['perfectionism_management', 'high_achievement'],
    conflictType: 'approach_incompatibility',
    severity: 'high',
    description: 'Perfectionism and high achievement goals can create internal tension',
    resolutionSuggestions: [
      'Reframe high achievement as "excellence" rather than "perfection"',
      'Set realistic, measurable achievement goals',
      'Focus on progress over perfection'
    ],
    clinicalGuidance: 'Address perfectionism first to enable healthy achievement motivation'
  },
  {
    conflictingGoals: ['anxiety_reduction', 'social_confidence', 'public_speaking'],
    conflictType: 'cognitive_overload',
    severity: 'medium',
    description: 'Too many anxiety-related goals may overwhelm cognitive resources',
    resolutionSuggestions: [
      'Prioritize anxiety reduction as foundation goal',
      'Sequence social confidence before public speaking',
      'Consider combining related goals into broader objective'
    ],
    clinicalGuidance: 'Start with foundational anxiety work before specific social challenges'
  }
];

// Complementary goal suggestions
const COMPLEMENTARY_SUGGESTIONS: Record<string, ComplementaryGoalSuggestion[]> = {
  'anxiety_reduction': [
    {
      suggestedGoal: 'mindfulness_practice',
      compatibleWith: ['anxiety_reduction', 'stress_management'],
      synergy: 0.9,
      therapeuticBenefit: 'Provides foundational skills for anxiety management and stress reduction',
      implementationOrder: 'concurrent',
      clinicalEvidence: 'high'
    },
    {
      suggestedGoal: 'breathing_techniques',
      compatibleWith: ['anxiety_reduction'],
      synergy: 0.85,
      therapeuticBenefit: 'Immediate anxiety relief tool that supports long-term anxiety management',
      implementationOrder: 'concurrent',
      clinicalEvidence: 'high'
    }
  ],
  'confidence_building': [
    {
      suggestedGoal: 'self_compassion',
      compatibleWith: ['confidence_building', 'emotional_processing'],
      synergy: 0.8,
      therapeuticBenefit: 'Self-compassion provides stable foundation for genuine confidence',
      implementationOrder: 'sequential',
      clinicalEvidence: 'high'
    }
  ]
};

/**
 * Analyzes relationships between selected therapeutic goals
 */
export function analyzeGoalRelationships(selectedGoals: string[]): GoalRelationshipMap {
  const relationships: GoalRelationship[] = [];
  const conflicts: GoalConflict[] = [];
  const complementarySuggestions: ComplementaryGoalSuggestion[] = [];

  // Find relationships between selected goals
  selectedGoals.forEach(goal => {
    const goalRelationships = GOAL_RELATIONSHIPS[goal] || [];
    goalRelationships.forEach(relationship => {
      if (selectedGoals.includes(relationship.targetGoal)) {
        relationships.push(relationship);
      }
    });
  });

  // Detect conflicts
  CONFLICT_PATTERNS.forEach(conflict => {
    const conflictingGoalsInSelection = conflict.conflictingGoals.filter(goal =>
      selectedGoals.includes(goal)
    );
    if (conflictingGoalsInSelection.length >= 2) {
      conflicts.push({
        ...conflict,
        conflictingGoals: conflictingGoalsInSelection
      });
    }
  });

  // Generate complementary suggestions
  selectedGoals.forEach(goal => {
    const suggestions = COMPLEMENTARY_SUGGESTIONS[goal] || [];
    suggestions.forEach(suggestion => {
      if (!selectedGoals.includes(suggestion.suggestedGoal)) {
        const isCompatible = suggestion.compatibleWith.some(compatibleGoal =>
          selectedGoals.includes(compatibleGoal)
        );
        if (isCompatible) {
          complementarySuggestions.push(suggestion);
        }
      }
    });
  });

  // Calculate overall compatibility and therapeutic coherence
  const overallCompatibility = calculateOverallCompatibility(relationships, conflicts);
  const therapeuticCoherence = calculateTherapeuticCoherence(selectedGoals, relationships);

  return {
    goals: selectedGoals,
    relationships,
    conflicts,
    complementarySuggestions,
    overallCompatibility,
    therapeuticCoherence
  };
}

/**
 * Calculates overall compatibility score for goal set
 */
function calculateOverallCompatibility(
  relationships: GoalRelationship[],
  conflicts: GoalConflict[]
): number {
  if (relationships.length === 0 && conflicts.length === 0) return 0.7; // Neutral

  const positiveScore = relationships.reduce((sum, rel) => {
    const multiplier = rel.relationshipType === 'synergistic' ? 1.0 :
                     rel.relationshipType === 'complementary' ? 0.8 :
                     rel.relationshipType === 'prerequisite' ? 0.6 : 0.3;
    return sum + (rel.strength * multiplier);
  }, 0);

  const negativeScore = conflicts.reduce((sum, conflict) => {
    const multiplier = conflict.severity === 'high' ? 1.0 :
                      conflict.severity === 'medium' ? 0.6 : 0.3;
    return sum + multiplier;
  }, 0);

  const totalRelationships = relationships.length + conflicts.length;
  if (totalRelationships === 0) return 0.7;

  const rawScore = (positiveScore - negativeScore) / totalRelationships;
  return Math.max(0, Math.min(1, (rawScore + 1) / 2)); // Normalize to 0-1
}

/**
 * Calculates therapeutic coherence score
 */
function calculateTherapeuticCoherence(
  goals: string[],
  relationships: GoalRelationship[]
): number {
  if (goals.length <= 1) return 1.0;

  const synergisticRelationships = relationships.filter(rel =>
    rel.relationshipType === 'synergistic' || rel.relationshipType === 'complementary'
  );

  const maxPossibleRelationships = (goals.length * (goals.length - 1)) / 2;
  const coherenceRatio = synergisticRelationships.length / maxPossibleRelationships;

  // Weight by relationship strength and clinical evidence
  const weightedCoherence = synergisticRelationships.reduce((sum, rel) => {
    const evidenceWeight = rel.clinicalEvidence === 'high' ? 1.0 :
                          rel.clinicalEvidence === 'medium' ? 0.7 : 0.4;
    return sum + (rel.strength * evidenceWeight);
  }, 0) / synergisticRelationships.length;

  return Math.min(1, coherenceRatio * 2 + (weightedCoherence || 0) * 0.5);
}

/**
 * Gets detailed conflict analysis for specific goals
 */
export function getConflictAnalysis(goals: string[]): GoalConflict[] {
  return CONFLICT_PATTERNS.filter(conflict => {
    const conflictingGoalsInSelection = conflict.conflictingGoals.filter(goal =>
      goals.includes(goal)
    );
    return conflictingGoalsInSelection.length >= 2;
  }).map(conflict => ({
    ...conflict,
    conflictingGoals: conflict.conflictingGoals.filter(goal => goals.includes(goal))
  }));
}

/**
 * Gets complementary goal suggestions for current selection
 */
export function getComplementaryGoalSuggestions(
  selectedGoals: string[],
  maxSuggestions: number = 3
): ComplementaryGoalSuggestion[] {
  const allSuggestions: ComplementaryGoalSuggestion[] = [];

  selectedGoals.forEach(goal => {
    const suggestions = COMPLEMENTARY_SUGGESTIONS[goal] || [];
    suggestions.forEach(suggestion => {
      if (!selectedGoals.includes(suggestion.suggestedGoal)) {
        const isCompatible = suggestion.compatibleWith.some(compatibleGoal =>
          selectedGoals.includes(compatibleGoal)
        );
        if (isCompatible) {
          allSuggestions.push(suggestion);
        }
      }
    });
  });

  // Remove duplicates and sort by synergy score
  const uniqueSuggestions = allSuggestions.filter((suggestion, index, array) =>
    array.findIndex(s => s.suggestedGoal === suggestion.suggestedGoal) === index
  );

  return uniqueSuggestions
    .sort((a, b) => b.synergy - a.synergy)
    .slice(0, maxSuggestions);
}
