// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Services/Therapeuticapproachalignmentservice]]
/**
 * Therapeutic Approach Alignment Service
 *
 * Provides intelligent matching between therapeutic goals and appropriate therapeutic approaches,
 * validates compatibility, and offers evidence-based recommendations for enhanced treatment effectiveness.
 */

import { TherapeuticApproach, THERAPEUTIC_APPROACHES_INFO } from '../types/preferences';

export interface ApproachGoalAlignment {
  approach: TherapeuticApproach;
  alignedGoals: string[];
  alignmentStrength: number; // 0-1 scale
  clinicalEvidence: 'high' | 'medium' | 'low';
  rationale: string;
  techniques: string[];
  expectedOutcomes: string[];
}

export interface ApproachCompatibility {
  primaryApproach: TherapeuticApproach;
  secondaryApproach: TherapeuticApproach;
  compatibilityScore: number; // 0-1 scale
  compatibilityType: 'synergistic' | 'complementary' | 'neutral' | 'conflicting';
  integrationStrategy: string;
  clinicalEvidence: 'high' | 'medium' | 'low';
  considerations: string[];
}

export interface ApproachRecommendation {
  recommendedApproach: TherapeuticApproach;
  confidence: number; // 0-1 scale
  primaryGoals: string[];
  reason: string;
  expectedBenefits: string[];
  implementationSuggestions: string[];
  clinicalEvidence: 'high' | 'medium' | 'low';
}

export interface TherapeuticApproachAnalysis {
  selectedGoals: string[];
  recommendedApproaches: ApproachRecommendation[];
  approachAlignments: ApproachGoalAlignment[];
  approachCompatibilities: ApproachCompatibility[];
  overallCoherence: number; // 0-1 scale
  treatmentEffectivenessScore: number; // 0-1 scale
  integrationRecommendations: string[];
}

// Evidence-based goal-to-approach mappings
const GOAL_APPROACH_MAPPINGS: Record<string, { approach: TherapeuticApproach; strength: number; evidence: 'high' | 'medium' | 'low'; rationale: string }[]> = {
  'anxiety_reduction': [
    { approach: TherapeuticApproach.CBT, strength: 0.95, evidence: 'high', rationale: 'CBT is gold standard for anxiety disorders with extensive RCT evidence' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.85, evidence: 'high', rationale: 'MBSR and MBCT show strong efficacy for anxiety reduction' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.8, evidence: 'medium', rationale: 'ACT effective for anxiety through acceptance and values-based action' },
    { approach: TherapeuticApproach.SOMATIC, strength: 0.7, evidence: 'medium', rationale: 'Body-based approaches help with physical anxiety symptoms' }
  ],
  'depression_management': [
    { approach: TherapeuticApproach.CBT, strength: 0.9, evidence: 'high', rationale: 'CBT has strongest evidence base for depression treatment' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.8, evidence: 'high', rationale: 'MBCT prevents depression relapse and reduces rumination' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.75, evidence: 'medium', rationale: 'ACT addresses depression through behavioral activation and values work' },
    { approach: TherapeuticApproach.PSYCHODYNAMIC, strength: 0.7, evidence: 'medium', rationale: 'Psychodynamic therapy effective for depression with interpersonal focus' }
  ],
  'stress_management': [
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.9, evidence: 'high', rationale: 'Mindfulness-based stress reduction is evidence-based standard' },
    { approach: TherapeuticApproach.CBT, strength: 0.8, evidence: 'high', rationale: 'CBT provides practical stress management tools and cognitive restructuring' },
    { approach: TherapeuticApproach.SOMATIC, strength: 0.75, evidence: 'medium', rationale: 'Body-based approaches address physical stress responses' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.7, evidence: 'medium', rationale: 'ACT helps with stress through acceptance and psychological flexibility' }
  ],
  'confidence_building': [
    { approach: TherapeuticApproach.CBT, strength: 0.85, evidence: 'high', rationale: 'CBT addresses negative self-talk and builds self-efficacy' },
    { approach: TherapeuticApproach.HUMANISTIC, strength: 0.8, evidence: 'medium', rationale: 'Person-centered approach builds self-worth through unconditional positive regard' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.7, evidence: 'medium', rationale: 'ACT builds confidence through values-based action and self-compassion' },
    { approach: TherapeuticApproach.NARRATIVE, strength: 0.65, evidence: 'medium', rationale: 'Narrative therapy helps reframe identity and build preferred self-story' }
  ],
  'emotional_regulation': [
    { approach: TherapeuticApproach.DIALECTICAL_BEHAVIOR, strength: 0.95, evidence: 'high', rationale: 'DBT specifically designed for emotional dysregulation with strong evidence' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.8, evidence: 'high', rationale: 'Mindfulness core component of emotion regulation skills' },
    { approach: TherapeuticApproach.CBT, strength: 0.75, evidence: 'high', rationale: 'CBT provides cognitive strategies for emotion regulation' },
    { approach: TherapeuticApproach.SOMATIC, strength: 0.7, evidence: 'medium', rationale: 'Body-based approaches help regulate emotional responses' }
  ],
  'relationship_skills': [
    { approach: TherapeuticApproach.DIALECTICAL_BEHAVIOR, strength: 0.85, evidence: 'high', rationale: 'DBT interpersonal effectiveness module specifically targets relationship skills' },
    { approach: TherapeuticApproach.HUMANISTIC, strength: 0.8, evidence: 'medium', rationale: 'Person-centered approach improves empathy and communication skills' },
    { approach: TherapeuticApproach.CBT, strength: 0.7, evidence: 'medium', rationale: 'CBT addresses relationship-related cognitive distortions' },
    { approach: TherapeuticApproach.PSYCHODYNAMIC, strength: 0.75, evidence: 'medium', rationale: 'Explores relationship patterns and attachment styles' }
  ],
  'mindfulness_practice': [
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.95, evidence: 'high', rationale: 'Direct alignment with mindfulness-based interventions' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.8, evidence: 'high', rationale: 'ACT incorporates mindfulness as core therapeutic process' },
    { approach: TherapeuticApproach.DIALECTICAL_BEHAVIOR, strength: 0.75, evidence: 'high', rationale: 'DBT includes mindfulness as foundational skill module' },
    { approach: TherapeuticApproach.SOMATIC, strength: 0.7, evidence: 'medium', rationale: 'Body awareness practices complement mindfulness development' }
  ],
  'trauma_recovery': [
    { approach: TherapeuticApproach.SOMATIC, strength: 0.9, evidence: 'high', rationale: 'Trauma-informed somatic approaches address body-stored trauma' },
    { approach: TherapeuticApproach.NARRATIVE, strength: 0.8, evidence: 'medium', rationale: 'Narrative therapy helps reconstruct trauma stories and identity' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.75, evidence: 'medium', rationale: 'Mindfulness supports trauma recovery through present-moment grounding' },
    { approach: TherapeuticApproach.PSYCHODYNAMIC, strength: 0.7, evidence: 'medium', rationale: 'Explores unconscious trauma impacts and defense mechanisms' }
  ],
  'perfectionism_management': [
    { approach: TherapeuticApproach.CBT, strength: 0.9, evidence: 'high', rationale: 'CBT directly addresses perfectionist thinking patterns and behaviors' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.8, evidence: 'medium', rationale: 'ACT helps with perfectionism through self-compassion and psychological flexibility' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.7, evidence: 'medium', rationale: 'Mindfulness reduces perfectionist rumination and self-criticism' },
    { approach: TherapeuticApproach.HUMANISTIC, strength: 0.65, evidence: 'medium', rationale: 'Unconditional positive regard counters perfectionist self-criticism' }
  ],
  'work_life_balance': [
    { approach: TherapeuticApproach.CBT, strength: 0.8, evidence: 'medium', rationale: 'CBT provides practical strategies for boundary setting and time management' },
    { approach: TherapeuticApproach.ACCEPTANCE_COMMITMENT, strength: 0.85, evidence: 'medium', rationale: 'ACT helps clarify values and align actions with work-life priorities' },
    { approach: TherapeuticApproach.MINDFULNESS, strength: 0.75, evidence: 'medium', rationale: 'Mindfulness supports present-moment awareness and stress reduction' },
    { approach: TherapeuticApproach.HUMANISTIC, strength: 0.7, evidence: 'medium', rationale: 'Person-centered approach supports authentic self-expression and needs' }
  ]
};

// Approach compatibility matrix
const APPROACH_COMPATIBILITY: Record<string, ApproachCompatibility> = {
  'cognitive_behavioral_therapy_mindfulness': {
    primaryApproach: TherapeuticApproach.CBT,
    secondaryApproach: TherapeuticApproach.MINDFULNESS,
    compatibilityScore: 0.9,
    compatibilityType: 'synergistic',
    integrationStrategy: 'Mindfulness-Based CBT combines cognitive restructuring with present-moment awareness',
    clinicalEvidence: 'high',
    considerations: ['MBCT is established integration', 'Mindfulness enhances cognitive flexibility', 'Reduces rumination in CBT']
  },
  'dialectical_behavior_therapy_mindfulness': {
    primaryApproach: TherapeuticApproach.DIALECTICAL_BEHAVIOR,
    secondaryApproach: TherapeuticApproach.MINDFULNESS,
    compatibilityScore: 0.95,
    compatibilityType: 'synergistic',
    integrationStrategy: 'DBT inherently incorporates mindfulness as core foundational skill',
    clinicalEvidence: 'high',
    considerations: ['Mindfulness is DBT foundation', 'Natural integration', 'Enhances distress tolerance']
  },
  'acceptance_commitment_therapy_mindfulness': {
    primaryApproach: TherapeuticApproach.ACCEPTANCE_COMMITMENT,
    secondaryApproach: TherapeuticApproach.MINDFULNESS,
    compatibilityScore: 0.9,
    compatibilityType: 'synergistic',
    integrationStrategy: 'ACT uses mindfulness for psychological flexibility and values-based living',
    clinicalEvidence: 'high',
    considerations: ['Mindfulness central to ACT', 'Supports acceptance processes', 'Enhances values clarity']
  },
  'cognitive_behavioral_therapy_psychodynamic': {
    primaryApproach: TherapeuticApproach.CBT,
    secondaryApproach: TherapeuticApproach.PSYCHODYNAMIC,
    compatibilityScore: 0.6,
    compatibilityType: 'complementary',
    integrationStrategy: 'Sequential or integrated approach addressing both symptoms and underlying patterns',
    clinicalEvidence: 'medium',
    considerations: ['Different time orientations', 'CBT for symptoms, psychodynamic for patterns', 'Requires skilled integration']
  },
  'somatic_therapy_mindfulness': {
    primaryApproach: TherapeuticApproach.SOMATIC,
    secondaryApproach: TherapeuticApproach.MINDFULNESS,
    compatibilityScore: 0.85,
    compatibilityType: 'synergistic',
    integrationStrategy: 'Body awareness and mindfulness naturally complement for embodied presence',
    clinicalEvidence: 'medium',
    considerations: ['Both emphasize present-moment awareness', 'Body-mind integration', 'Trauma-informed approaches']
  }
};

/**
 * Analyzes therapeutic approach alignment for selected goals
 */
export function analyzeTherapeuticApproachAlignment(selectedGoals: string[]): TherapeuticApproachAnalysis {
  if (selectedGoals.length === 0) {
    return {
      selectedGoals: [],
      recommendedApproaches: [],
      approachAlignments: [],
      approachCompatibilities: [],
      overallCoherence: 0,
      treatmentEffectivenessScore: 0,
      integrationRecommendations: []
    };
  }

  // Generate approach recommendations
  const recommendedApproaches = generateApproachRecommendations(selectedGoals);

  // Generate approach alignments
  const approachAlignments = generateApproachAlignments(selectedGoals, recommendedApproaches);

  // Analyze approach compatibilities
  const approachCompatibilities = analyzeApproachCompatibilities(recommendedApproaches);

  // Calculate overall coherence and effectiveness
  const overallCoherence = calculateOverallCoherence(approachAlignments, approachCompatibilities);
  const treatmentEffectivenessScore = calculateTreatmentEffectiveness(selectedGoals, recommendedApproaches);

  // Generate integration recommendations
  const integrationRecommendations = generateIntegrationRecommendations(recommendedApproaches, approachCompatibilities);

  return {
    selectedGoals,
    recommendedApproaches,
    approachAlignments,
    approachCompatibilities,
    overallCoherence,
    treatmentEffectivenessScore,
    integrationRecommendations
  };
}

/**
 * Generates therapeutic approach recommendations based on selected goals
 */
function generateApproachRecommendations(selectedGoals: string[]): ApproachRecommendation[] {
  const approachScores = new Map<TherapeuticApproach, { score: number; goals: string[]; evidenceLevel: 'high' | 'medium' | 'low'; rationales: string[] }>();

  // Collect scores for each approach across all goals
  selectedGoals.forEach(goal => {
    const mappings = GOAL_APPROACH_MAPPINGS[goal] || [];
    mappings.forEach(mapping => {
      const current = approachScores.get(mapping.approach) || {
        score: 0,
        goals: [],
        evidenceLevel: 'low' as const,
        rationales: []
      };

      current.score += mapping.strength;
      current.goals.push(goal);
      current.rationales.push(mapping.rationale);

      // Update evidence level to highest available
      if (mapping.evidence === 'high' || (mapping.evidence === 'medium' && current.evidenceLevel === 'low')) {
        current.evidenceLevel = mapping.evidence;
      }

      approachScores.set(mapping.approach, current);
    });
  });

  // Convert to recommendations and sort by score
  const recommendations: ApproachRecommendation[] = Array.from(approachScores.entries())
    .map(([approach, data]) => {
      const approachInfo = THERAPEUTIC_APPROACHES_INFO[approach];
      const confidence = Math.min(1, data.score / selectedGoals.length);

      return {
        recommendedApproach: approach,
        confidence,
        primaryGoals: [...new Set(data.goals)],
        reason: `Strong alignment with ${data.goals.length} selected goals`,
        expectedBenefits: approachInfo.bestFor,
        implementationSuggestions: approachInfo.techniques,
        clinicalEvidence: data.evidenceLevel
      };
    })
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 4); // Top 4 recommendations

  return recommendations;
}

/**
 * Generates detailed approach-goal alignments
 */
function generateApproachAlignments(selectedGoals: string[], recommendations: ApproachRecommendation[]): ApproachGoalAlignment[] {
  return recommendations.map(rec => {
    const approachInfo = THERAPEUTIC_APPROACHES_INFO[rec.recommendedApproach];
    const alignedGoals = selectedGoals.filter(goal => {
      const mappings = GOAL_APPROACH_MAPPINGS[goal] || [];
      return mappings.some(m => m.approach === rec.recommendedApproach);
    });

    const alignmentStrength = alignedGoals.length / selectedGoals.length;

    // Get clinical evidence and rationale
    const goalMappings = alignedGoals.flatMap(goal =>
      (GOAL_APPROACH_MAPPINGS[goal] || []).filter(m => m.approach === rec.recommendedApproach)
    );

    const clinicalEvidence = goalMappings.some(m => m.evidence === 'high') ? 'high' :
                           goalMappings.some(m => m.evidence === 'medium') ? 'medium' : 'low';

    const rationale = goalMappings.length > 0 ? goalMappings[0].rationale :
                     `${approachInfo.name} provides structured approach for selected therapeutic goals`;

    return {
      approach: rec.recommendedApproach,
      alignedGoals,
      alignmentStrength,
      clinicalEvidence,
      rationale,
      techniques: approachInfo.techniques,
      expectedOutcomes: approachInfo.bestFor
    };
  });
}

/**
 * Analyzes compatibility between recommended approaches
 */
function analyzeApproachCompatibilities(recommendations: ApproachRecommendation[]): ApproachCompatibility[] {
  const compatibilities: ApproachCompatibility[] = [];

  for (let i = 0; i < recommendations.length; i++) {
    for (let j = i + 1; j < recommendations.length; j++) {
      const approach1 = recommendations[i].recommendedApproach;
      const approach2 = recommendations[j].recommendedApproach;

      const key1 = `${approach1}_${approach2}`;
      const key2 = `${approach2}_${approach1}`;

      const compatibility = APPROACH_COMPATIBILITY[key1] || APPROACH_COMPATIBILITY[key2];

      if (compatibility) {
        compatibilities.push(compatibility);
      } else {
        // Generate default compatibility assessment
        compatibilities.push(generateDefaultCompatibility(approach1, approach2));
      }
    }
  }

  return compatibilities;
}

/**
 * Generates default compatibility for approach pairs not explicitly defined
 */
function generateDefaultCompatibility(approach1: TherapeuticApproach, approach2: TherapeuticApproach): ApproachCompatibility {
  const info1 = THERAPEUTIC_APPROACHES_INFO[approach1];
  const info2 = THERAPEUTIC_APPROACHES_INFO[approach2];

  // Simple heuristic based on approach characteristics
  const compatibilityScore = 0.7; // Default neutral-positive compatibility

  return {
    primaryApproach: approach1,
    secondaryApproach: approach2,
    compatibilityScore,
    compatibilityType: 'complementary',
    integrationStrategy: `${info1.name} and ${info2.name} can be integrated through careful sequencing and coordination`,
    clinicalEvidence: 'low',
    considerations: ['Requires skilled integration', 'Monitor for approach conflicts', 'Consider sequential implementation']
  };
}

/**
 * Calculates overall therapeutic coherence
 */
function calculateOverallCoherence(alignments: ApproachGoalAlignment[], compatibilities: ApproachCompatibility[]): number {
  if (alignments.length === 0) return 0;

  // Average alignment strength
  const avgAlignment = alignments.reduce((sum, a) => sum + a.alignmentStrength, 0) / alignments.length;

  // Average compatibility score
  const avgCompatibility = compatibilities.length > 0
    ? compatibilities.reduce((sum, c) => sum + c.compatibilityScore, 0) / compatibilities.length
    : 0.7; // Default if no compatibilities

  // Weight alignment more heavily than compatibility
  return (avgAlignment * 0.7) + (avgCompatibility * 0.3);
}

/**
 * Calculates treatment effectiveness score
 */
function calculateTreatmentEffectiveness(selectedGoals: string[], recommendations: ApproachRecommendation[]): number {
  if (recommendations.length === 0) return 0;

  // Factor in evidence levels and confidence scores
  const effectivenessScore = recommendations.reduce((sum, rec) => {
    const evidenceWeight = rec.clinicalEvidence === 'high' ? 1.0 :
                          rec.clinicalEvidence === 'medium' ? 0.8 : 0.6;
    return sum + (rec.confidence * evidenceWeight);
  }, 0) / recommendations.length;

  return Math.min(1, effectivenessScore);
}

/**
 * Generates integration recommendations for multiple approaches
 */
function generateIntegrationRecommendations(recommendations: ApproachRecommendation[], compatibilities: ApproachCompatibility[]): string[] {
  const integrationRecs: string[] = [];

  if (recommendations.length <= 1) {
    integrationRecs.push('Single approach focus allows for deep, consistent therapeutic work');
    return integrationRecs;
  }

  // Analyze compatibility patterns
  const synergisticPairs = compatibilities.filter(c => c.compatibilityType === 'synergistic');
  const conflictingPairs = compatibilities.filter(c => c.compatibilityType === 'conflicting');

  if (synergisticPairs.length > 0) {
    integrationRecs.push(`Strong synergies identified: ${synergisticPairs.map(p => `${THERAPEUTIC_APPROACHES_INFO[p.primaryApproach].name} + ${THERAPEUTIC_APPROACHES_INFO[p.secondaryApproach].name}`).join(', ')}`);
  }

  if (conflictingPairs.length > 0) {
    integrationRecs.push(`Approach conflicts require careful management: ${conflictingPairs.map(p => p.integrationStrategy).join('; ')}`);
  }

  // General integration guidance
  if (recommendations.length > 2) {
    integrationRecs.push('Consider phased implementation: start with highest-confidence approach, then integrate complementary methods');
  }

  integrationRecs.push('Regular assessment of approach effectiveness and client preference is essential for successful integration');

  return integrationRecs;
}
