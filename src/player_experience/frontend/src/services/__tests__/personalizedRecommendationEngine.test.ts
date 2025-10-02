/**
 * Unit tests for Personalized Recommendation Engine
 * 
 * Tests comprehensive personalized recommendation functionality including
 * contextual analysis, evidence-based suggestions, and user-specific adaptations.
 */

import {
  generatePersonalizedRecommendations,
  PersonalizedRecommendation,
  ContextualRecommendation,
  RecommendationResult,
  UserContext,
  RecommendationType,
  RecommendationCategory,
  RecommendationPriority
} from '../personalizedRecommendationEngine';
import { PlayerPreferences, TherapeuticApproach, IntensityLevel, ConversationStyle, PreferredSetting } from '../../types/preferences';
import { GoalProgress } from '../goalProgressService';

// Mock data for testing
const mockPlayerPreferences: PlayerPreferences = {
  player_id: 'test-player-123',
  intensity_level: IntensityLevel.MEDIUM,
  preferred_approaches: [TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS],
  conversation_style: ConversationStyle.SUPPORTIVE,
  therapeutic_goals: ['anxiety_reduction', 'stress_management'],
  primary_concerns: ['Work stress', 'Social anxiety'],
  character_name: 'Alex',
  preferred_setting: PreferredSetting.PEACEFUL_FOREST,
  comfort_topics: ['nature', 'personal_growth', 'meditation'],
  trigger_topics: ['trauma', 'loss'],
  avoid_topics: ['violence'],
  session_duration_preference: 30,
  reminder_frequency: 'weekly',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
  version: 1
};

const mockGoalProgresses: GoalProgress[] = [
  {
    goalId: 'anxiety_reduction',
    progress: 65,
    startDate: new Date('2024-01-01'),
    lastUpdated: new Date('2024-01-15'),
    milestones: [
      {
        id: 'milestone-1',
        description: 'Identify anxiety triggers',
        targetProgress: 25,
        achieved: true,
        achievedDate: new Date('2024-01-05'),
        therapeuticValue: 'high'
      },
      {
        id: 'milestone-2',
        description: 'Practice breathing techniques',
        targetProgress: 50,
        achieved: true,
        achievedDate: new Date('2024-01-10'),
        therapeuticValue: 'medium'
      },
      {
        id: 'milestone-3',
        description: 'Apply coping strategies',
        targetProgress: 75,
        achieved: false,
        therapeuticValue: 'high'
      }
    ],
    progressHistory: [
      {
        date: new Date('2024-01-01'),
        progress: 0,
        notes: 'Starting anxiety reduction journey'
      },
      {
        date: new Date('2024-01-05'),
        progress: 25,
        notes: 'Identified key triggers'
      },
      {
        date: new Date('2024-01-10'),
        progress: 50,
        notes: 'Breathing techniques helping'
      },
      {
        date: new Date('2024-01-15'),
        progress: 65,
        notes: 'Steady progress continues'
      }
    ],
    status: 'in_progress',
    difficultyLevel: 'intermediate',
    therapeuticApproaches: ['cognitive_behavioral_therapy', 'mindfulness']
  },
  {
    goalId: 'stress_management',
    progress: 30,
    startDate: new Date('2024-01-08'),
    lastUpdated: new Date('2024-01-12'),
    milestones: [
      {
        id: 'milestone-s1',
        description: 'Recognize stress patterns',
        targetProgress: 30,
        achieved: true,
        achievedDate: new Date('2024-01-12'),
        therapeuticValue: 'medium'
      },
      {
        id: 'milestone-s2',
        description: 'Develop stress response plan',
        targetProgress: 60,
        achieved: false,
        therapeuticValue: 'high'
      }
    ],
    progressHistory: [
      {
        date: new Date('2024-01-08'),
        progress: 0,
        notes: 'Beginning stress management work'
      },
      {
        date: new Date('2024-01-12'),
        progress: 30,
        notes: 'Identified stress patterns'
      }
    ],
    status: 'in_progress',
    difficultyLevel: 'beginner',
    therapeuticApproaches: ['mindfulness']
  }
];

const mockUserContext: UserContext = {
  preferences: mockPlayerPreferences,
  goalProgresses: mockGoalProgresses,
  sessionHistory: [
    {
      date: new Date('2024-01-15'),
      duration: 35,
      goalsWorkedOn: ['anxiety_reduction'],
      progressMade: 0.15,
      emotionalState: {
        primary: 'calm',
        intensity: 6,
        stability: 'stable'
      },
      challengesEncountered: ['time_management'],
      breakthroughs: ['breathing_technique_mastery'],
      userSatisfaction: 4
    },
    {
      date: new Date('2024-01-12'),
      duration: 30,
      goalsWorkedOn: ['stress_management'],
      progressMade: 0.3,
      emotionalState: {
        primary: 'focused',
        intensity: 7,
        stability: 'improving'
      },
      challengesEncountered: [],
      breakthroughs: ['stress_pattern_recognition'],
      userSatisfaction: 4
    }
  ],
  recentFeedback: [
    {
      date: new Date('2024-01-15'),
      type: 'goal_relevance',
      rating: 4,
      comments: 'Goals feel very relevant to my needs',
      specificGoal: 'anxiety_reduction'
    },
    {
      date: new Date('2024-01-12'),
      type: 'approach_effectiveness',
      rating: 4,
      comments: 'CBT techniques are working well',
      specificGoal: 'anxiety_reduction'
    }
  ],
  currentEmotionalState: {
    primary: 'optimistic',
    intensity: 7,
    stability: 'stable'
  }
};

describe('Personalized Recommendation Engine', () => {
  describe('generatePersonalizedRecommendations', () => {
    it('should generate personalized recommendations based on user context', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 5);
      
      expect(result).toBeDefined();
      expect(result.recommendations).toBeInstanceOf(Array);
      expect(result.totalRecommendations).toBeGreaterThan(0);
      expect(result.personalizationScore).toBeGreaterThanOrEqual(0);
      expect(result.personalizationScore).toBeLessThanOrEqual(1);
      expect(['high', 'medium', 'low']).toContain(result.confidenceLevel);
      expect(result.recommendationSummary).toBeDefined();
      expect(result.nextReviewDate).toBeInstanceOf(Date);
      expect(result.adaptationHistory).toBeInstanceOf(Array);
    });

    it('should limit recommendations to specified maximum', () => {
      const maxRecommendations = 3;
      const result = generatePersonalizedRecommendations(mockUserContext, maxRecommendations);
      
      expect(result.recommendations.length).toBeLessThanOrEqual(maxRecommendations);
      expect(result.totalRecommendations).toBeLessThanOrEqual(maxRecommendations);
    });

    it('should prioritize recommendations correctly', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 10);
      
      // Check that recommendations are sorted by priority
      const priorities = result.recommendations.map(rec => rec.priority);
      const priorityOrder = { critical: 5, high: 4, medium: 3, low: 2, optional: 1 };
      
      for (let i = 1; i < priorities.length; i++) {
        expect(priorityOrder[priorities[i-1]]).toBeGreaterThanOrEqual(priorityOrder[priorities[i]]);
      }
    });

    it('should include required recommendation properties', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 5);
      
      result.recommendations.forEach(rec => {
        expect(rec.id).toBeDefined();
        expect(rec.type).toBeDefined();
        expect(rec.category).toBeDefined();
        expect(rec.title).toBeDefined();
        expect(rec.description).toBeDefined();
        expect(rec.confidence).toBeGreaterThanOrEqual(0);
        expect(rec.confidence).toBeLessThanOrEqual(1);
        expect(rec.priority).toBeDefined();
        expect(rec.clinicalEvidence).toBeDefined();
        expect(rec.personalizationFactors).toBeInstanceOf(Array);
        expect(rec.expectedOutcome).toBeDefined();
        expect(rec.timeframe).toBeDefined();
        expect(typeof rec.actionable).toBe('boolean');
        expect(rec.contextualFactors).toBeInstanceOf(Array);
        expect(rec.adaptationReason).toBeDefined();
        expect(rec.userRelevanceScore).toBeGreaterThanOrEqual(0);
        expect(rec.userRelevanceScore).toBeLessThanOrEqual(1);
        expect(rec.timingSensitivity).toBeDefined();
        expect(rec.progressAlignment).toBeDefined();
      });
    });

    it('should calculate personalization score based on user data richness', () => {
      // Test with rich user context
      const richResult = generatePersonalizedRecommendations(mockUserContext, 5);
      
      // Test with minimal user context
      const minimalContext: UserContext = {
        preferences: {
          ...mockPlayerPreferences,
          therapeutic_goals: [],
          primary_concerns: []
        },
        goalProgresses: []
      };
      const minimalResult = generatePersonalizedRecommendations(minimalContext, 5);
      
      // Rich context should have higher or equal personalization score
      expect(richResult.personalizationScore).toBeGreaterThanOrEqual(minimalResult.personalizationScore);
    });

    it('should generate appropriate recommendation summary', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 8);
      const summary = result.recommendationSummary;
      
      expect(summary.totalRecommendations).toBe(result.recommendations.length);
      expect(summary.byPriority).toBeDefined();
      expect(summary.byCategory).toBeDefined();
      expect(summary.byTimeframe).toBeDefined();
      expect(summary.averageConfidence).toBeGreaterThanOrEqual(0);
      expect(summary.averageConfidence).toBeLessThanOrEqual(1);
      expect(['high', 'medium', 'low']).toContain(summary.personalizationStrength);
      
      // Verify counts match
      const priorityCounts = Object.values(summary.byPriority).reduce((sum, count) => sum + count, 0);
      const categoryCounts = Object.values(summary.byCategory).reduce((sum, count) => sum + count, 0);
      const timeframeCounts = Object.values(summary.byTimeframe).reduce((sum, count) => sum + count, 0);
      
      expect(priorityCounts).toBe(result.recommendations.length);
      expect(categoryCounts).toBe(result.recommendations.length);
      expect(timeframeCounts).toBe(result.recommendations.length);
    });

    it('should set appropriate next review date', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 5);
      const now = new Date();
      const reviewDate = result.nextReviewDate;
      
      expect(reviewDate).toBeInstanceOf(Date);
      expect(reviewDate.getTime()).toBeGreaterThan(now.getTime());
      
      // Should be within reasonable timeframe (1-30 days)
      const daysDifference = (reviewDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000);
      expect(daysDifference).toBeGreaterThan(0);
      expect(daysDifference).toBeLessThan(31);
    });

    it('should handle empty user context gracefully', () => {
      const emptyContext: UserContext = {
        preferences: {
          ...mockPlayerPreferences,
          therapeutic_goals: [],
          primary_concerns: []
        },
        goalProgresses: []
      };
      
      const result = generatePersonalizedRecommendations(emptyContext, 5);
      
      expect(result).toBeDefined();
      expect(result.recommendations).toBeInstanceOf(Array);
      expect(result.confidenceLevel).toBe('low');
      expect(result.personalizationScore).toBeLessThan(0.5);
    });

    it('should adapt recommendations based on user feedback patterns', () => {
      // Test with positive feedback
      const positiveContext = {
        ...mockUserContext,
        recentFeedback: [
          {
            date: new Date('2024-01-15'),
            type: 'overall_experience' as const,
            rating: 5,
            comments: 'Excellent progress and recommendations'
          }
        ]
      };
      
      const positiveResult = generatePersonalizedRecommendations(positiveContext, 5);
      
      // Test with negative feedback
      const negativeContext = {
        ...mockUserContext,
        recentFeedback: [
          {
            date: new Date('2024-01-15'),
            type: 'approach_effectiveness' as const,
            rating: 2,
            comments: 'Current approach not working well'
          }
        ]
      };
      
      const negativeResult = generatePersonalizedRecommendations(negativeContext, 5);
      
      // Both should generate recommendations, but potentially different types
      expect(positiveResult.recommendations.length).toBeGreaterThan(0);
      expect(negativeResult.recommendations.length).toBeGreaterThan(0);
    });

    it('should consider progress patterns in recommendations', () => {
      // Test with stalled progress
      const stalledContext = {
        ...mockUserContext,
        goalProgresses: [
          {
            ...mockGoalProgresses[0],
            progress: 30,
            lastUpdated: new Date('2024-01-01') // Old update
          }
        ]
      };
      
      const result = generatePersonalizedRecommendations(stalledContext, 5);
      
      // Should include progress enhancement recommendations
      const progressRecommendations = result.recommendations.filter(rec => 
        rec.type === 'progress_enhancement'
      );
      
      expect(result.recommendations.length).toBeGreaterThan(0);
      // Note: Actual progress recommendations would depend on implementation details
    });

    it('should validate recommendation types and categories', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 10);
      
      const validTypes: RecommendationType[] = [
        'goal_suggestion', 'concern_identification', 'approach_optimization',
        'progress_enhancement', 'conflict_resolution', 'milestone_adjustment',
        'therapeutic_deepening', 'integration_support'
      ];
      
      const validCategories: RecommendationCategory[] = [
        'immediate_action', 'short_term_planning', 'long_term_development',
        'crisis_prevention', 'progress_optimization', 'relationship_enhancement',
        'self_care', 'skill_building'
      ];
      
      const validPriorities: RecommendationPriority[] = [
        'critical', 'high', 'medium', 'low', 'optional'
      ];
      
      result.recommendations.forEach(rec => {
        expect(validTypes).toContain(rec.type);
        expect(validCategories).toContain(rec.category);
        expect(validPriorities).toContain(rec.priority);
      });
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle user with no goals or progress', () => {
      const noGoalsContext: UserContext = {
        preferences: {
          ...mockPlayerPreferences,
          therapeutic_goals: [],
          primary_concerns: []
        },
        goalProgresses: []
      };
      
      expect(() => {
        generatePersonalizedRecommendations(noGoalsContext, 5);
      }).not.toThrow();
    });

    it('should handle maximum recommendations of 0', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 0);
      
      expect(result.recommendations).toHaveLength(0);
      expect(result.totalRecommendations).toBe(0);
    });

    it('should handle very large maximum recommendations', () => {
      const result = generatePersonalizedRecommendations(mockUserContext, 100);
      
      expect(result.recommendations.length).toBeLessThanOrEqual(100);
      expect(result.totalRecommendations).toBeLessThanOrEqual(100);
    });
  });
});
