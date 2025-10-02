/**
 * Unit Tests for Goal Suggestion Engine
 * 
 * Tests the intelligent therapeutic goal recommendation system
 * based on evidence-based clinical mappings.
 */

import {
  generateGoalSuggestions,
  generateProgressAwareGoalSuggestions,
  GoalProgress
} from '../goalSuggestionEngine';

describe('Goal Suggestion Engine', () => {
  describe('generateGoalSuggestions', () => {
    it('should return empty suggestions when no concerns are provided', () => {
      const result = generateGoalSuggestions([]);
      
      expect(result.suggestions).toHaveLength(0);
      expect(result.totalConcernsAnalyzed).toBe(0);
      expect(result.suggestionStrength).toBe('weak');
    });

    it('should generate suggestions for single concern', () => {
      const result = generateGoalSuggestions(['Work stress']);
      
      expect(result.suggestions.length).toBeGreaterThan(0);
      expect(result.totalConcernsAnalyzed).toBe(1);
      expect(result.suggestions[0].goalId).toBe('stress_management');
      expect(result.suggestions[0].confidence).toBeGreaterThan(0.9);
      expect(result.suggestions[0].clinicalEvidence).toBe('high');
    });

    it('should generate suggestions for multiple concerns', () => {
      const result = generateGoalSuggestions(['Work stress', 'Social anxiety']);
      
      expect(result.suggestions.length).toBeGreaterThan(0);
      expect(result.totalConcernsAnalyzed).toBe(2);
      
      // Should include stress_management and anxiety_reduction
      const goalIds = result.suggestions.map(s => s.goalId);
      expect(goalIds).toContain('stress_management');
      expect(goalIds).toContain('anxiety_reduction');
    });

    it('should boost confidence for goals suggested by multiple concerns', () => {
      const singleConcernResult = generateGoalSuggestions(['Work stress']);
      const multipleConcernResult = generateGoalSuggestions(['Work stress', 'Academic pressure']);
      
      const stressManagementSingle = singleConcernResult.suggestions.find(s => s.goalId === 'stress_management');
      const stressManagementMultiple = multipleConcernResult.suggestions.find(s => s.goalId === 'stress_management');
      
      expect(stressManagementMultiple?.confidence).toBeGreaterThan(stressManagementSingle?.confidence || 0);
    });

    it('should exclude already selected goals from suggestions', () => {
      const result = generateGoalSuggestions(['Work stress'], ['stress_management']);
      
      const goalIds = result.suggestions.map(s => s.goalId);
      expect(goalIds).not.toContain('stress_management');
    });

    it('should limit suggestions to maxSuggestions parameter', () => {
      const result = generateGoalSuggestions(['Work stress', 'Social anxiety', 'Depression'], [], 3);
      
      expect(result.suggestions.length).toBeLessThanOrEqual(3);
    });

    it('should prioritize high clinical evidence suggestions', () => {
      const result = generateGoalSuggestions(['Social anxiety']);
      
      // anxiety_reduction should be first (high evidence, high confidence)
      expect(result.suggestions[0].goalId).toBe('anxiety_reduction');
      expect(result.suggestions[0].clinicalEvidence).toBe('high');
    });

    it('should determine suggestion strength correctly', () => {
      const strongResult = generateGoalSuggestions(['Social anxiety']); // High confidence mappings
      const weakResult = generateGoalSuggestions(['Career uncertainty']); // Lower confidence mappings
      
      expect(strongResult.suggestionStrength).toBe('strong');
      expect(weakResult.suggestionStrength).toBe('moderate');
    });

    it('should handle unknown concerns gracefully', () => {
      const result = generateGoalSuggestions(['Unknown concern']);
      
      expect(result.suggestions).toHaveLength(0);
      expect(result.totalConcernsAnalyzed).toBe(1);
      expect(result.suggestionStrength).toBe('weak');
    });

    it('should provide meaningful reasons for suggestions', () => {
      const result = generateGoalSuggestions(['Work stress']);
      
      result.suggestions.forEach(suggestion => {
        expect(suggestion.reason).toBeTruthy();
        expect(typeof suggestion.reason).toBe('string');
        expect(suggestion.reason.length).toBeGreaterThan(10);
      });
    });

    it('should categorize goals correctly', () => {
      const result = generateGoalSuggestions(['Work stress']);
      
      result.suggestions.forEach(suggestion => {
        expect(suggestion.category).toBeTruthy();
        expect(typeof suggestion.category).toBe('string');
      });
    });

    describe('Clinical Evidence-Based Mappings', () => {
      it('should suggest anxiety_reduction for social anxiety with high confidence', () => {
        const result = generateGoalSuggestions(['Social anxiety']);
        const anxietyReduction = result.suggestions.find(s => s.goalId === 'anxiety_reduction');
        
        expect(anxietyReduction).toBeTruthy();
        expect(anxietyReduction?.confidence).toBeGreaterThan(0.9);
        expect(anxietyReduction?.clinicalEvidence).toBe('high');
      });

      it('should suggest relationship_skills for relationship issues', () => {
        const result = generateGoalSuggestions(['Relationship issues']);
        const relationshipSkills = result.suggestions.find(s => s.goalId === 'relationship_skills');
        
        expect(relationshipSkills).toBeTruthy();
        expect(relationshipSkills?.confidence).toBeGreaterThan(0.9);
        expect(relationshipSkills?.clinicalEvidence).toBe('high');
      });

      it('should suggest confidence_building for low self-esteem', () => {
        const result = generateGoalSuggestions(['Low self-esteem']);
        const confidenceBuilding = result.suggestions.find(s => s.goalId === 'confidence_building');
        
        expect(confidenceBuilding).toBeTruthy();
        expect(confidenceBuilding?.confidence).toBeGreaterThan(0.9);
        expect(confidenceBuilding?.clinicalEvidence).toBe('high');
      });

      it('should suggest emotional_processing for depression', () => {
        const result = generateGoalSuggestions(['Depression']);
        const emotionalProcessing = result.suggestions.find(s => s.goalId === 'emotional_processing');
        
        expect(emotionalProcessing).toBeTruthy();
        expect(emotionalProcessing?.confidence).toBeGreaterThan(0.85);
        expect(emotionalProcessing?.clinicalEvidence).toBe('high');
      });

      it('should suggest self_compassion for perfectionism', () => {
        const result = generateGoalSuggestions(['Perfectionism']);
        const selfCompassion = result.suggestions.find(s => s.goalId === 'self_compassion');
        
        expect(selfCompassion).toBeTruthy();
        expect(selfCompassion?.confidence).toBeGreaterThan(0.85);
        expect(selfCompassion?.clinicalEvidence).toBe('high');
      });
    });

    describe('Complex Scenarios', () => {
      it('should handle multiple overlapping concerns effectively', () => {
        const result = generateGoalSuggestions([
          'Work stress', 
          'Social anxiety', 
          'Perfectionism'
        ]);
        
        expect(result.suggestions.length).toBeGreaterThan(0);
        expect(result.totalConcernsAnalyzed).toBe(3);
        
        // Should include goals that address multiple concerns
        const goalIds = result.suggestions.map(s => s.goalId);
        expect(goalIds).toContain('stress_management'); // Work stress
        expect(goalIds).toContain('anxiety_reduction'); // Social anxiety + perfectionism
      });

      it('should maintain reasonable suggestion counts for many concerns', () => {
        const manyConcerns = [
          'Work stress', 'Social anxiety', 'Depression', 'Perfectionism',
          'Relationship issues', 'Low self-esteem', 'Financial worries'
        ];
        
        const result = generateGoalSuggestions(manyConcerns, [], 5);
        
        expect(result.suggestions.length).toBeLessThanOrEqual(5);
        expect(result.totalConcernsAnalyzed).toBe(7);
        expect(result.suggestionStrength).toBe('strong');
      });

      it('should provide diverse suggestions across categories', () => {
        const result = generateGoalSuggestions([
          'Work stress', 'Relationship issues', 'Low self-esteem'
        ]);
        
        const categories = new Set(result.suggestions.map(s => s.category));
        expect(categories.size).toBeGreaterThan(1); // Multiple categories represented
      });
    });
  });

  describe('generateProgressAwareGoalSuggestions', () => {
    const mockDate = new Date('2024-01-15T10:00:00Z');

    it('should return base suggestions when no progress data is provided', () => {
      const result = generateProgressAwareGoalSuggestions(['Work stress'], [], []);

      expect(result.suggestions.length).toBeGreaterThan(0);
      expect(result.progressBasedRecommendations).toEqual([]);
      expect(result.evolutionSuggestions).toEqual([]);
    });

    it('should adjust confidence for completed goals', () => {
      const completedProgress: GoalProgress = {
        goalId: 'stress_management',
        progress: 100,
        status: 'completed',
        milestones: [],
        progressHistory: [
          { date: mockDate, progress: 100 }
        ]
      };

      const result = generateProgressAwareGoalSuggestions(
        ['Work stress'],
        [],
        [completedProgress]
      );

      const stressGoalSuggestion = result.suggestions.find(s => s.goalId === 'stress_management');
      if (stressGoalSuggestion) {
        expect(stressGoalSuggestion.reason).toContain('previously completed');
        expect(stressGoalSuggestion.confidence).toBeLessThan(0.5); // Reduced confidence
      }
    });

    it('should boost confidence for goals in progress', () => {
      const inProgressGoal: GoalProgress = {
        goalId: 'anxiety_reduction',
        progress: 45,
        status: 'in_progress',
        milestones: [],
        progressHistory: [
          { date: mockDate, progress: 45 }
        ]
      };

      const result = generateProgressAwareGoalSuggestions(
        ['Social anxiety'],
        [],
        [inProgressGoal]
      );

      const anxietyGoalSuggestion = result.suggestions.find(s => s.goalId === 'anxiety_reduction');
      if (anxietyGoalSuggestion) {
        expect(anxietyGoalSuggestion.reason).toContain('Current progress: 45%');
      }
    });

    it('should include progress-based recommendations for stalled goals', () => {
      const stalledProgress: GoalProgress = {
        goalId: 'confidence_building',
        progress: 25,
        status: 'in_progress',
        milestones: [],
        progressHistory: [
          { date: new Date('2024-01-01'), progress: 25 },
          { date: new Date('2024-01-05'), progress: 25 },
          { date: new Date('2024-01-10'), progress: 25 } // No progress over 9 days, meets stalled criteria
        ]
      };

      const result = generateProgressAwareGoalSuggestions(
        ['Low self-esteem'],
        [],
        [stalledProgress]
      );

      expect(result.progressBasedRecommendations).toHaveLength(1);
      expect(result.progressBasedRecommendations![0]).toEqual(
        expect.objectContaining({
          type: 'goal_adjustment',
          goalId: 'confidence_building',
          urgency: 'medium'
        })
      );
    });

    it('should include evolution suggestions for high-progress goals', () => {
      const highProgressGoal: GoalProgress = {
        goalId: 'emotional_processing',
        progress: 80,
        status: 'in_progress',
        milestones: [],
        progressHistory: [
          { date: mockDate, progress: 80 }
        ]
      };

      const result = generateProgressAwareGoalSuggestions(
        ['Depression'],
        [],
        [highProgressGoal]
      );

      expect(result.evolutionSuggestions).toHaveLength(1);
      expect(result.evolutionSuggestions![0]).toEqual(
        expect.objectContaining({
          currentGoalId: 'emotional_processing',
          evolutionType: 'graduate',
          confidence: 0.8
        })
      );
    });

    it('should handle multiple progress states simultaneously', () => {
      const progresses: GoalProgress[] = [
        {
          goalId: 'anxiety_reduction',
          progress: 100,
          status: 'completed',
          milestones: [],
          progressHistory: [{ date: mockDate, progress: 100 }]
        },
        {
          goalId: 'stress_management',
          progress: 25,
          status: 'in_progress',
          milestones: [],
          progressHistory: [
            { date: new Date('2024-01-01'), progress: 25 },
            { date: new Date('2024-01-05'), progress: 25 },
            { date: new Date('2024-01-10'), progress: 25 } // No progress over 9 days, meets stalled criteria
          ]
        },
        {
          goalId: 'confidence_building',
          progress: 85,
          status: 'in_progress',
          milestones: [],
          progressHistory: [{ date: mockDate, progress: 85 }]
        }
      ];

      const result = generateProgressAwareGoalSuggestions(
        ['Work stress', 'Social anxiety', 'Low self-esteem'],
        [],
        progresses
      );

      expect(result.progressBasedRecommendations!.length).toBeGreaterThan(0);
      expect(result.evolutionSuggestions!.length).toBeGreaterThan(0);

      // Should have recommendations for completed, stalled, and high-progress goals
      const recommendationTypes = result.progressBasedRecommendations!.map(r => r.type);
      expect(recommendationTypes).toContain('new_goal'); // For completed
      expect(recommendationTypes).toContain('goal_adjustment'); // For stalled
    });

    it('should maintain original suggestion quality while adding progress insights', () => {
      const progresses: GoalProgress[] = [
        {
          goalId: 'mindfulness_development',
          progress: 50,
          status: 'in_progress',
          milestones: [],
          progressHistory: [{ date: mockDate, progress: 50 }]
        }
      ];

      const baseResult = generateGoalSuggestions(['Depression'], [], 5);
      const progressAwareResult = generateProgressAwareGoalSuggestions(
        ['Depression'],
        [],
        progresses,
        5
      );

      // Should have same number of base suggestions
      expect(progressAwareResult.suggestions.length).toBe(baseResult.suggestions.length);
      expect(progressAwareResult.totalConcernsAnalyzed).toBe(baseResult.totalConcernsAnalyzed);

      // But should have additional progress-aware features
      expect(progressAwareResult.progressBasedRecommendations).toBeDefined();
      expect(progressAwareResult.evolutionSuggestions).toBeDefined();
    });
  });
});
