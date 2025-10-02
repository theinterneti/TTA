/**
 * Goal Relationship Service Tests
 * 
 * Comprehensive test suite for goal relationship analysis, conflict detection,
 * and complementary goal suggestions functionality.
 */

import {
  analyzeGoalRelationships,
  getConflictAnalysis,
  getComplementaryGoalSuggestions,
  GoalRelationshipMap,
  GoalConflict,
  ComplementaryGoalSuggestion
} from '../goalRelationshipService';

describe('Goal Relationship Service', () => {
  describe('analyzeGoalRelationships', () => {
    it('should return empty analysis for no goals', () => {
      const result = analyzeGoalRelationships([]);
      
      expect(result.goals).toEqual([]);
      expect(result.relationships).toEqual([]);
      expect(result.conflicts).toEqual([]);
      expect(result.complementarySuggestions).toEqual([]);
      expect(result.overallCompatibility).toBe(0.7); // Neutral
      expect(result.therapeuticCoherence).toBe(1.0); // Perfect for empty set
    });

    it('should identify synergistic relationships', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.relationships).toHaveLength(1);
      expect(result.relationships[0]).toMatchObject({
        sourceGoal: 'anxiety_reduction',
        targetGoal: 'mindfulness_practice',
        relationshipType: 'synergistic',
        strength: 0.9,
        clinicalEvidence: 'high'
      });
      expect(result.overallCompatibility).toBeGreaterThan(0.7);
    });

    it('should detect conflicting goals', () => {
      const goals = ['perfectionism_management', 'high_achievement'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.conflicts).toHaveLength(1);
      expect(result.conflicts[0]).toMatchObject({
        conflictingGoals: ['perfectionism_management', 'high_achievement'],
        conflictType: 'approach_incompatibility',
        severity: 'high'
      });
      expect(result.overallCompatibility).toBeLessThan(0.7);
    });

    it('should generate complementary suggestions', () => {
      const goals = ['anxiety_reduction'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.complementarySuggestions.length).toBeGreaterThan(0);
      const mindfulnessSuggestion = result.complementarySuggestions.find(
        s => s.suggestedGoal === 'mindfulness_practice'
      );
      expect(mindfulnessSuggestion).toBeDefined();
      expect(mindfulnessSuggestion?.synergy).toBe(0.9);
    });

    it('should calculate compatibility for mixed relationships', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice', 'perfectionism_management'];
      const result = analyzeGoalRelationships(goals);
      
      // Should have both positive and negative relationships
      expect(result.relationships.length).toBeGreaterThan(0);
      expect(result.overallCompatibility).toBeGreaterThan(0);
      expect(result.overallCompatibility).toBeLessThan(1);
    });

    it('should handle single goal selection', () => {
      const goals = ['anxiety_reduction'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.goals).toEqual(['anxiety_reduction']);
      expect(result.relationships).toEqual([]); // No internal relationships
      expect(result.therapeuticCoherence).toBe(1.0); // Perfect for single goal
    });

    it('should prioritize high clinical evidence relationships', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice', 'confidence_building'];
      const result = analyzeGoalRelationships(goals);
      
      const highEvidenceRelationships = result.relationships.filter(
        rel => rel.clinicalEvidence === 'high'
      );
      expect(highEvidenceRelationships.length).toBeGreaterThan(0);
    });
  });

  describe('getConflictAnalysis', () => {
    it('should return empty array for non-conflicting goals', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice'];
      const conflicts = getConflictAnalysis(goals);
      
      expect(conflicts).toEqual([]);
    });

    it('should detect perfectionism-achievement conflict', () => {
      const goals = ['perfectionism_management', 'high_achievement'];
      const conflicts = getConflictAnalysis(goals);
      
      expect(conflicts).toHaveLength(1);
      expect(conflicts[0]).toMatchObject({
        conflictingGoals: ['perfectionism_management', 'high_achievement'],
        conflictType: 'approach_incompatibility',
        severity: 'high'
      });
      expect(conflicts[0].resolutionSuggestions.length).toBeGreaterThan(0);
    });

    it('should detect cognitive overload conflicts', () => {
      const goals = ['anxiety_reduction', 'social_confidence', 'public_speaking'];
      const conflicts = getConflictAnalysis(goals);
      
      expect(conflicts).toHaveLength(1);
      expect(conflicts[0]).toMatchObject({
        conflictType: 'cognitive_overload',
        severity: 'medium'
      });
    });

    it('should provide clinical guidance for conflicts', () => {
      const goals = ['perfectionism_management', 'high_achievement'];
      const conflicts = getConflictAnalysis(goals);
      
      expect(conflicts[0].clinicalGuidance).toBeDefined();
      expect(conflicts[0].clinicalGuidance.length).toBeGreaterThan(0);
    });

    it('should filter conflicts to only include selected goals', () => {
      const goals = ['perfectionism_management']; // Only one of the conflicting pair
      const conflicts = getConflictAnalysis(goals);
      
      expect(conflicts).toEqual([]); // No conflict with single goal
    });
  });

  describe('getComplementaryGoalSuggestions', () => {
    it('should return empty array for goals with no suggestions', () => {
      const goals = ['unknown_goal'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      expect(suggestions).toEqual([]);
    });

    it('should suggest mindfulness for anxiety reduction', () => {
      const goals = ['anxiety_reduction'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      expect(suggestions.length).toBeGreaterThan(0);
      const mindfulnessSuggestion = suggestions.find(
        s => s.suggestedGoal === 'mindfulness_practice'
      );
      expect(mindfulnessSuggestion).toBeDefined();
      expect(mindfulnessSuggestion?.synergy).toBe(0.9);
      expect(mindfulnessSuggestion?.clinicalEvidence).toBe('high');
    });

    it('should suggest self-compassion for confidence building', () => {
      const goals = ['confidence_building'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      const selfCompassionSuggestion = suggestions.find(
        s => s.suggestedGoal === 'self_compassion'
      );
      expect(selfCompassionSuggestion).toBeDefined();
      expect(selfCompassionSuggestion?.implementationOrder).toBe('sequential');
    });

    it('should respect maxSuggestions parameter', () => {
      const goals = ['anxiety_reduction'];
      const suggestions = getComplementaryGoalSuggestions(goals, 1);
      
      expect(suggestions).toHaveLength(1);
    });

    it('should not suggest already selected goals', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      const mindfulnessSuggestion = suggestions.find(
        s => s.suggestedGoal === 'mindfulness_practice'
      );
      expect(mindfulnessSuggestion).toBeUndefined();
    });

    it('should sort suggestions by synergy score', () => {
      const goals = ['anxiety_reduction'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      if (suggestions.length > 1) {
        for (let i = 0; i < suggestions.length - 1; i++) {
          expect(suggestions[i].synergy).toBeGreaterThanOrEqual(suggestions[i + 1].synergy);
        }
      }
    });

    it('should provide therapeutic benefits for suggestions', () => {
      const goals = ['anxiety_reduction'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      suggestions.forEach(suggestion => {
        expect(suggestion.therapeuticBenefit).toBeDefined();
        expect(suggestion.therapeuticBenefit.length).toBeGreaterThan(0);
      });
    });

    it('should handle multiple compatible goals', () => {
      const goals = ['anxiety_reduction', 'stress_management'];
      const suggestions = getComplementaryGoalSuggestions(goals);
      
      const mindfulnessSuggestion = suggestions.find(
        s => s.suggestedGoal === 'mindfulness_practice'
      );
      expect(mindfulnessSuggestion).toBeDefined();
      expect(mindfulnessSuggestion?.compatibleWith).toContain('anxiety_reduction');
      expect(mindfulnessSuggestion?.compatibleWith).toContain('stress_management');
    });
  });

  describe('Compatibility Scoring', () => {
    it('should give high compatibility for synergistic goals', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.overallCompatibility).toBeGreaterThan(0.8);
    });

    it('should give low compatibility for conflicting goals', () => {
      const goals = ['perfectionism_management', 'high_achievement'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.overallCompatibility).toBeLessThan(0.5);
    });

    it('should calculate therapeutic coherence correctly', () => {
      const goals = ['anxiety_reduction', 'mindfulness_practice', 'confidence_building'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.therapeuticCoherence).toBeGreaterThan(0);
      expect(result.therapeuticCoherence).toBeLessThanOrEqual(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle duplicate goals gracefully', () => {
      const goals = ['anxiety_reduction', 'anxiety_reduction'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.goals).toEqual(['anxiety_reduction', 'anxiety_reduction']);
      expect(result.relationships).toEqual([]); // No self-relationships
    });

    it('should handle unknown goals without errors', () => {
      const goals = ['unknown_goal_1', 'unknown_goal_2'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.goals).toEqual(goals);
      expect(result.relationships).toEqual([]);
      expect(result.conflicts).toEqual([]);
      expect(result.complementarySuggestions).toEqual([]);
    });

    it('should handle mixed known and unknown goals', () => {
      const goals = ['anxiety_reduction', 'unknown_goal'];
      const result = analyzeGoalRelationships(goals);
      
      expect(result.goals).toEqual(goals);
      expect(result.complementarySuggestions.length).toBeGreaterThan(0);
    });
  });
});
