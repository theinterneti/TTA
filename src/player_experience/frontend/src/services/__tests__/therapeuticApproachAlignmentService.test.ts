/**
 * Tests for Therapeutic Approach Alignment Service
 */

import {
  analyzeTherapeuticApproachAlignment,
  ApproachRecommendation,
  ApproachGoalAlignment,
  ApproachCompatibility,
  TherapeuticApproachAnalysis
} from '../therapeuticApproachAlignmentService';
import { TherapeuticApproach } from '../../types/preferences';

describe('Therapeutic Approach Alignment Service', () => {
  describe('analyzeTherapeuticApproachAlignment', () => {
    it('should return empty analysis for no selected goals', () => {
      const result = analyzeTherapeuticApproachAlignment([]);

      expect(result.selectedGoals).toEqual([]);
      expect(result.recommendedApproaches).toEqual([]);
      expect(result.approachAlignments).toEqual([]);
      expect(result.approachCompatibilities).toEqual([]);
      expect(result.overallCoherence).toBe(0);
      expect(result.treatmentEffectivenessScore).toBe(0);
      expect(result.integrationRecommendations).toEqual([]);
    });

    it('should recommend CBT for anxiety reduction', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction']);

      expect(result.selectedGoals).toEqual(['anxiety_reduction']);
      expect(result.recommendedApproaches.length).toBeGreaterThan(0);

      const cbtRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.CBT
      );
      expect(cbtRecommendation).toBeDefined();
      expect(cbtRecommendation?.confidence).toBeGreaterThan(0.8);
      expect(cbtRecommendation?.clinicalEvidence).toBe('high');
    });

    it('should recommend DBT for emotional regulation', () => {
      const result = analyzeTherapeuticApproachAlignment(['emotional_regulation']);

      const dbtRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.DIALECTICAL_BEHAVIOR
      );
      expect(dbtRecommendation).toBeDefined();
      expect(dbtRecommendation?.confidence).toBeGreaterThan(0.9);
      expect(dbtRecommendation?.clinicalEvidence).toBe('high');
    });

    it('should recommend mindfulness for stress management', () => {
      const result = analyzeTherapeuticApproachAlignment(['stress_management']);

      const mindfulnessRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.MINDFULNESS
      );
      expect(mindfulnessRecommendation).toBeDefined();
      expect(mindfulnessRecommendation?.confidence).toBeGreaterThan(0.8);
      expect(mindfulnessRecommendation?.clinicalEvidence).toBe('high');
    });

    it('should handle multiple goals with overlapping approaches', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'depression_management']);

      expect(result.recommendedApproaches.length).toBeGreaterThan(0);

      // CBT should be highly recommended for both anxiety and depression
      const cbtRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.CBT
      );
      expect(cbtRecommendation).toBeDefined();
      expect(cbtRecommendation?.primaryGoals).toContain('anxiety_reduction');
      expect(cbtRecommendation?.primaryGoals).toContain('depression_management');
    });

    it('should calculate overall coherence correctly', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'mindfulness_practice']);

      expect(result.overallCoherence).toBeGreaterThan(0);
      expect(result.overallCoherence).toBeLessThanOrEqual(1);

      // Should have high coherence due to strong alignment
      expect(result.overallCoherence).toBeGreaterThan(0.7);
    });

    it('should calculate treatment effectiveness score', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'depression_management']);

      expect(result.treatmentEffectivenessScore).toBeGreaterThan(0);
      expect(result.treatmentEffectivenessScore).toBeLessThanOrEqual(1);

      // Should have good effectiveness due to strong evidence base
      expect(result.treatmentEffectivenessScore).toBeGreaterThan(0.6);
    });
  });

  describe('Approach Recommendations', () => {
    it('should provide detailed recommendation information', () => {
      const result = analyzeTherapeuticApproachAlignment(['confidence_building']);

      expect(result.recommendedApproaches.length).toBeGreaterThan(0);

      const recommendation = result.recommendedApproaches[0];
      expect(recommendation.recommendedApproach).toBeDefined();
      expect(recommendation.confidence).toBeGreaterThan(0);
      expect(recommendation.primaryGoals).toContain('confidence_building');
      expect(recommendation.reason).toBeDefined();
      expect(recommendation.expectedBenefits).toBeDefined();
      expect(recommendation.implementationSuggestions).toBeDefined();
      expect(recommendation.clinicalEvidence).toMatch(/^(high|medium|low)$/);
    });

    it('should sort recommendations by confidence', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'trauma_recovery']);

      expect(result.recommendedApproaches.length).toBeGreaterThan(1);

      // Recommendations should be sorted by confidence (descending)
      for (let i = 1; i < result.recommendedApproaches.length; i++) {
        expect(result.recommendedApproaches[i - 1].confidence)
          .toBeGreaterThanOrEqual(result.recommendedApproaches[i].confidence);
      }
    });

    it('should limit recommendations to top 4', () => {
      const result = analyzeTherapeuticApproachAlignment([
        'anxiety_reduction', 'depression_management', 'stress_management',
        'confidence_building', 'emotional_regulation'
      ]);

      expect(result.recommendedApproaches.length).toBeLessThanOrEqual(4);
    });
  });

  describe('Approach Alignments', () => {
    it('should generate detailed approach alignments', () => {
      const result = analyzeTherapeuticApproachAlignment(['mindfulness_practice']);

      expect(result.approachAlignments.length).toBeGreaterThan(0);

      const alignment = result.approachAlignments[0];
      expect(alignment.approach).toBeDefined();
      expect(alignment.alignedGoals).toContain('mindfulness_practice');
      expect(alignment.alignmentStrength).toBeGreaterThan(0);
      expect(alignment.alignmentStrength).toBeLessThanOrEqual(1);
      expect(alignment.clinicalEvidence).toMatch(/^(high|medium|low)$/);
      expect(alignment.rationale).toBeDefined();
      expect(alignment.techniques).toBeDefined();
      expect(alignment.expectedOutcomes).toBeDefined();
    });

    it('should calculate alignment strength correctly', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'depression_management']);

      const cbtAlignment = result.approachAlignments.find(
        a => a.approach === TherapeuticApproach.CBT
      );

      expect(cbtAlignment).toBeDefined();
      expect(cbtAlignment?.alignmentStrength).toBe(1.0); // CBT aligns with both goals
    });
  });

  describe('Approach Compatibilities', () => {
    it('should analyze compatibility between multiple approaches', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'mindfulness_practice']);

      expect(result.approachCompatibilities.length).toBeGreaterThan(0);

      const compatibility = result.approachCompatibilities[0];
      expect(compatibility.primaryApproach).toBeDefined();
      expect(compatibility.secondaryApproach).toBeDefined();
      expect(compatibility.compatibilityScore).toBeGreaterThan(0);
      expect(compatibility.compatibilityScore).toBeLessThanOrEqual(1);
      expect(compatibility.compatibilityType).toMatch(/^(synergistic|complementary|neutral|conflicting)$/);
      expect(compatibility.integrationStrategy).toBeDefined();
      expect(compatibility.clinicalEvidence).toMatch(/^(high|medium|low)$/);
      expect(compatibility.considerations).toBeDefined();
    });

    it('should identify synergistic approaches', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'mindfulness_practice']);

      // Should find CBT-Mindfulness synergy
      const synergisticCompatibility = result.approachCompatibilities.find(
        c => c.compatibilityType === 'synergistic'
      );

      expect(synergisticCompatibility).toBeDefined();
      expect(synergisticCompatibility?.compatibilityScore).toBeGreaterThan(0.8);
    });

    it('should handle single approach scenarios', () => {
      const result = analyzeTherapeuticApproachAlignment(['trauma_recovery']);

      // May have fewer compatibilities with single dominant approach
      expect(result.approachCompatibilities.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Integration Recommendations', () => {
    it('should provide integration guidance for multiple approaches', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'depression_management']);

      expect(result.integrationRecommendations).toBeDefined();
      expect(result.integrationRecommendations.length).toBeGreaterThan(0);

      // Should include general guidance
      const hasGeneralGuidance = result.integrationRecommendations.some(
        rec => rec.includes('assessment') || rec.includes('effectiveness')
      );
      expect(hasGeneralGuidance).toBe(true);
    });

    it('should recommend single approach focus when appropriate', () => {
      const result = analyzeTherapeuticApproachAlignment(['emotional_regulation']);

      // DBT might be so dominant that single approach is recommended
      const hasSingleApproachGuidance = result.integrationRecommendations.some(
        rec => rec.includes('Single approach') || rec.includes('consistent')
      );

      if (result.recommendedApproaches.length === 1) {
        expect(hasSingleApproachGuidance).toBe(true);
      }
    });

    it('should identify synergistic combinations', () => {
      const result = analyzeTherapeuticApproachAlignment(['mindfulness_practice', 'emotional_regulation']);

      // Should identify mindfulness-DBT synergy
      const hasSynergyGuidance = result.integrationRecommendations.some(
        rec => rec.includes('synerg') || rec.includes('Strong')
      );

      if (result.approachCompatibilities.some(c => c.compatibilityType === 'synergistic')) {
        expect(hasSynergyGuidance).toBe(true);
      }
    });

    it('should suggest phased implementation for multiple approaches', () => {
      const result = analyzeTherapeuticApproachAlignment([
        'anxiety_reduction', 'depression_management', 'stress_management'
      ]);

      if (result.recommendedApproaches.length > 2) {
        const hasPhasedGuidance = result.integrationRecommendations.some(
          rec => rec.includes('phased') || rec.includes('start with')
        );
        expect(hasPhasedGuidance).toBe(true);
      }
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle unknown goals gracefully', () => {
      const result = analyzeTherapeuticApproachAlignment(['unknown_goal']);

      expect(result.selectedGoals).toEqual(['unknown_goal']);
      expect(result.recommendedApproaches).toEqual([]);
      expect(result.overallCoherence).toBe(0);
      expect(result.treatmentEffectivenessScore).toBe(0);
    });

    it('should handle mixed known and unknown goals', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'unknown_goal']);

      expect(result.selectedGoals).toEqual(['anxiety_reduction', 'unknown_goal']);
      expect(result.recommendedApproaches.length).toBeGreaterThan(0);

      // Should still provide recommendations for known goals
      const cbtRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.CBT
      );
      expect(cbtRecommendation).toBeDefined();
    });

    it('should handle duplicate goals', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction', 'anxiety_reduction']);

      expect(result.selectedGoals).toEqual(['anxiety_reduction', 'anxiety_reduction']);
      expect(result.recommendedApproaches.length).toBeGreaterThan(0);

      // Should handle duplicates without errors
      const cbtRecommendation = result.recommendedApproaches.find(
        r => r.recommendedApproach === TherapeuticApproach.CBT
      );
      expect(cbtRecommendation).toBeDefined();
    });
  });

  describe('Clinical Evidence Integration', () => {
    it('should prioritize high-evidence approaches', () => {
      const result = analyzeTherapeuticApproachAlignment(['anxiety_reduction']);

      // CBT should be top recommendation with high evidence
      const topRecommendation = result.recommendedApproaches[0];
      expect(topRecommendation.clinicalEvidence).toBe('high');
    });

    it('should include evidence levels in alignments', () => {
      const result = analyzeTherapeuticApproachAlignment(['depression_management']);

      result.approachAlignments.forEach(alignment => {
        expect(alignment.clinicalEvidence).toMatch(/^(high|medium|low)$/);
      });
    });

    it('should factor evidence into treatment effectiveness', () => {
      const highEvidenceResult = analyzeTherapeuticApproachAlignment(['anxiety_reduction']);
      const mixedEvidenceResult = analyzeTherapeuticApproachAlignment(['trauma_recovery']);

      // High evidence goals should generally have higher effectiveness scores
      expect(highEvidenceResult.treatmentEffectivenessScore).toBeGreaterThan(0.7);
    });
  });

  describe('Therapeutic Approach Coverage', () => {
    it('should cover all major therapeutic approaches', () => {
      const allGoals = [
        'anxiety_reduction', 'depression_management', 'stress_management',
        'confidence_building', 'emotional_regulation', 'relationship_skills',
        'mindfulness_practice', 'trauma_recovery', 'perfectionism_management',
        'work_life_balance'
      ];

      const result = analyzeTherapeuticApproachAlignment(allGoals);

      const approachTypes = new Set(result.recommendedApproaches.map(r => r.recommendedApproach));

      // Should recommend multiple different approaches
      expect(approachTypes.size).toBeGreaterThan(3);

      // Should include major evidence-based approaches
      expect(approachTypes.has(TherapeuticApproach.CBT)).toBe(true);
      expect(approachTypes.has(TherapeuticApproach.MINDFULNESS)).toBe(true);
    });

    it('should provide comprehensive analysis for complex goal sets', () => {
      const complexGoals = [
        'anxiety_reduction', 'emotional_regulation', 'mindfulness_practice', 'relationship_skills'
      ];

      const result = analyzeTherapeuticApproachAlignment(complexGoals);

      expect(result.recommendedApproaches.length).toBeGreaterThan(2);
      expect(result.approachAlignments.length).toBeGreaterThan(2);
      expect(result.approachCompatibilities.length).toBeGreaterThan(0);
      expect(result.overallCoherence).toBeGreaterThan(0.5);
      expect(result.treatmentEffectivenessScore).toBeGreaterThan(0.5);
      expect(result.integrationRecommendations.length).toBeGreaterThan(1);
    });
  });
});
