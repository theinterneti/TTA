import {
  initializeGoalProgress,
  updateGoalProgress,
  generateProgressBasedRecommendations,
  generateGoalEvolutionSuggestions,
  GoalProgress,
  GoalMilestone,
  ProgressEntry,
  EmotionalState
} from '../goalProgressService';

describe('Goal Progress Service', () => {
  const mockDate = new Date('2024-01-15T10:00:00Z');
  
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(mockDate);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('initializeGoalProgress', () => {
    it('should initialize progress for anxiety_reduction goal with default milestones', () => {
      const progress = initializeGoalProgress('anxiety_reduction');

      expect(progress).toEqual({
        goalId: 'anxiety_reduction',
        progress: 0,
        startDate: mockDate,
        lastUpdated: mockDate,
        milestones: expect.arrayContaining([
          expect.objectContaining({
            id: 'anxiety_awareness',
            description: 'Recognize anxiety triggers and physical symptoms',
            targetProgress: 25,
            achieved: false,
            therapeuticValue: 'high'
          }),
          expect.objectContaining({
            id: 'coping_techniques',
            description: 'Learn and practice 3+ anxiety management techniques',
            targetProgress: 50,
            achieved: false,
            therapeuticValue: 'high'
          })
        ]),
        progressHistory: [{
          date: mockDate,
          progress: 0,
          notes: 'Goal initiated'
        }],
        status: 'not_started',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      });
    });

    it('should initialize progress for unknown goal with empty milestones', () => {
      const progress = initializeGoalProgress('unknown_goal');

      expect(progress.goalId).toBe('unknown_goal');
      expect(progress.milestones).toEqual([]);
      expect(progress.progress).toBe(0);
      expect(progress.status).toBe('not_started');
    });

    it('should initialize progress for stress_management goal with specific milestones', () => {
      const progress = initializeGoalProgress('stress_management');

      expect(progress.milestones).toHaveLength(4);
      expect(progress.milestones[0]).toEqual(
        expect.objectContaining({
          id: 'stress_identification',
          targetProgress: 30,
          therapeuticValue: 'high'
        })
      );
    });
  });

  describe('updateGoalProgress', () => {
    let initialProgress: GoalProgress;

    beforeEach(() => {
      initialProgress = initializeGoalProgress('anxiety_reduction');
    });

    it('should update progress and add history entry', () => {
      const updatedProgress = updateGoalProgress(initialProgress, 25, 'Made good progress');

      expect(updatedProgress.progress).toBe(25);
      expect(updatedProgress.status).toBe('in_progress');
      expect(updatedProgress.progressHistory).toHaveLength(2);
      expect(updatedProgress.progressHistory[1]).toEqual({
        date: mockDate,
        progress: 25,
        notes: 'Made good progress'
      });
    });

    it('should achieve milestones when progress reaches target', () => {
      const updatedProgress = updateGoalProgress(initialProgress, 30);

      const anxietyAwarenessMilestone = updatedProgress.milestones.find(m => m.id === 'anxiety_awareness');
      expect(anxietyAwarenessMilestone?.achieved).toBe(true);
      expect(anxietyAwarenessMilestone?.achievedDate).toEqual(mockDate);

      const copingTechniquesMilestone = updatedProgress.milestones.find(m => m.id === 'coping_techniques');
      expect(copingTechniquesMilestone?.achieved).toBe(false);
    });

    it('should set status to completed when progress reaches 100', () => {
      const updatedProgress = updateGoalProgress(initialProgress, 100);

      expect(updatedProgress.status).toBe('completed');
      expect(updatedProgress.progress).toBe(100);
    });

    it('should clamp progress values between 0 and 100', () => {
      const negativeProgress = updateGoalProgress(initialProgress, -10);
      expect(negativeProgress.progress).toBe(0);

      const excessiveProgress = updateGoalProgress(initialProgress, 150);
      expect(excessiveProgress.progress).toBe(100);
    });

    it('should include emotional state in progress entry', () => {
      const emotionalState: EmotionalState = {
        valence: 20,
        arousal: 60,
        confidence: 75
      };

      const updatedProgress = updateGoalProgress(initialProgress, 25, 'Feeling better', emotionalState);

      expect(updatedProgress.progressHistory[1].emotionalState).toEqual(emotionalState);
    });

    it('should estimate completion date based on progress trend', () => {
      // Add some progress history to establish a trend
      let progress = updateGoalProgress(initialProgress, 10);
      
      // Advance time and add more progress
      jest.setSystemTime(new Date('2024-01-16T10:00:00Z'));
      progress = updateGoalProgress(progress, 20);
      
      jest.setSystemTime(new Date('2024-01-17T10:00:00Z'));
      progress = updateGoalProgress(progress, 30);

      expect(progress.estimatedCompletion).toBeDefined();
      expect(progress.estimatedCompletion!.getTime()).toBeGreaterThan(mockDate.getTime());
    });
  });

  describe('generateProgressBasedRecommendations', () => {
    it('should recommend goal adjustment for stalled progress', () => {
      const stalledProgress: GoalProgress = {
        goalId: 'anxiety_reduction',
        progress: 25,
        startDate: new Date('2024-01-01'),
        lastUpdated: new Date('2024-01-05'), // 10 days ago
        milestones: [],
        progressHistory: [
          { date: new Date('2024-01-01'), progress: 25 },
          { date: new Date('2024-01-05'), progress: 25 } // No progress for days
        ],
        status: 'in_progress',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      };

      const recommendations = generateProgressBasedRecommendations([stalledProgress], ['Work stress']);

      expect(recommendations).toHaveLength(1);
      expect(recommendations[0]).toEqual(
        expect.objectContaining({
          type: 'goal_adjustment',
          goalId: 'anxiety_reduction',
          urgency: 'medium',
          confidence: 0.8
        })
      );
    });

    it('should recommend milestone focus for rapid progress', () => {
      const rapidProgress: GoalProgress = {
        goalId: 'confidence_building',
        progress: 60,
        startDate: new Date('2024-01-14'),
        lastUpdated: mockDate,
        milestones: [],
        progressHistory: [
          { date: new Date('2024-01-14'), progress: 20 },
          { date: mockDate, progress: 60 } // 40% progress in 1 day
        ],
        status: 'in_progress',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      };

      const recommendations = generateProgressBasedRecommendations([rapidProgress], []);

      expect(recommendations).toHaveLength(1);
      expect(recommendations[0]).toEqual(
        expect.objectContaining({
          type: 'milestone_focus',
          goalId: 'confidence_building',
          urgency: 'low',
          confidence: 0.9
        })
      );
    });

    it('should recommend new goals for completed goals', () => {
      const completedProgress: GoalProgress = {
        goalId: 'stress_management',
        progress: 100,
        startDate: new Date('2024-01-01'),
        lastUpdated: mockDate,
        milestones: [],
        progressHistory: [
          { date: new Date('2024-01-01'), progress: 0 },
          { date: mockDate, progress: 100 }
        ],
        status: 'completed',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      };

      const recommendations = generateProgressBasedRecommendations([completedProgress], []);

      expect(recommendations.length).toBeGreaterThanOrEqual(1);
      const newGoalRecommendation = recommendations.find(r => r.type === 'new_goal');
      expect(newGoalRecommendation).toEqual(
        expect.objectContaining({
          type: 'new_goal',
          goalId: 'stress_management',
          urgency: 'low',
          confidence: 0.85
        })
      );
    });

    it('should sort recommendations by urgency and confidence', () => {
      const progresses: GoalProgress[] = [
        {
          goalId: 'goal1',
          progress: 25,
          startDate: new Date('2024-01-01'),
          lastUpdated: new Date('2024-01-05'),
          milestones: [],
          progressHistory: [
            { date: new Date('2024-01-01'), progress: 25 },
            { date: new Date('2024-01-05'), progress: 25 }
          ],
          status: 'in_progress',
          difficultyLevel: 'beginner',
          therapeuticApproaches: []
        },
        {
          goalId: 'goal2',
          progress: 100,
          startDate: new Date('2024-01-01'),
          lastUpdated: mockDate,
          milestones: [],
          progressHistory: [
            { date: new Date('2024-01-01'), progress: 0 },
            { date: mockDate, progress: 100 }
          ],
          status: 'completed',
          difficultyLevel: 'beginner',
          therapeuticApproaches: []
        }
      ];

      const recommendations = generateProgressBasedRecommendations(progresses, []);

      expect(recommendations.length).toBeGreaterThanOrEqual(2);
      // Medium urgency should come before low urgency
      expect(recommendations[0].urgency).toBe('medium');

      // Find the first low urgency recommendation
      const lowUrgencyRecommendation = recommendations.find(r => r.urgency === 'low');
      expect(lowUrgencyRecommendation).toBeDefined();
    });
  });

  describe('generateGoalEvolutionSuggestions', () => {
    it('should suggest graduation for high-progress goals', () => {
      const highProgressGoal: GoalProgress = {
        goalId: 'anxiety_reduction',
        progress: 80,
        startDate: new Date('2024-01-01'),
        lastUpdated: mockDate,
        milestones: [],
        progressHistory: [
          { date: new Date('2024-01-01'), progress: 0 },
          { date: mockDate, progress: 80 }
        ],
        status: 'in_progress',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      };

      const suggestions = generateGoalEvolutionSuggestions([highProgressGoal]);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0]).toEqual(
        expect.objectContaining({
          currentGoalId: 'anxiety_reduction',
          evolutionType: 'graduate',
          suggestedEvolution: 'Advanced anxiety management and helping others',
          confidence: 0.8,
          requiredProgress: 75
        })
      );
    });

    it('should suggest splitting for complex goals with struggling areas', () => {
      const complexGoal: GoalProgress = {
        goalId: 'emotional_processing',
        progress: 60,
        startDate: new Date('2024-01-01'),
        lastUpdated: mockDate,
        milestones: [
          { id: 'milestone1', description: 'Test 1', targetProgress: 50, achieved: false },
          { id: 'milestone2', description: 'Test 2', targetProgress: 55, achieved: false }
        ],
        progressHistory: [
          { date: new Date('2024-01-01'), progress: 0 },
          { date: mockDate, progress: 60 }
        ],
        status: 'in_progress',
        difficultyLevel: 'beginner',
        therapeuticApproaches: []
      };

      const suggestions = generateGoalEvolutionSuggestions([complexGoal]);

      expect(suggestions.length).toBeGreaterThanOrEqual(1);
      const splitSuggestion = suggestions.find(s => s.evolutionType === 'split');
      expect(splitSuggestion).toEqual(
        expect.objectContaining({
          currentGoalId: 'emotional_processing',
          evolutionType: 'split',
          suggestedEvolution: 'Separate emotional awareness from emotional expression',
          confidence: 0.7,
          requiredProgress: 50
        })
      );
    });

    it('should sort suggestions by confidence', () => {
      const progresses: GoalProgress[] = [
        {
          goalId: 'goal1',
          progress: 80,
          startDate: new Date('2024-01-01'),
          lastUpdated: mockDate,
          milestones: [],
          progressHistory: [{ date: mockDate, progress: 80 }],
          status: 'in_progress',
          difficultyLevel: 'beginner',
          therapeuticApproaches: []
        },
        {
          goalId: 'goal2',
          progress: 60,
          startDate: new Date('2024-01-01'),
          lastUpdated: mockDate,
          milestones: [
            { id: 'm1', description: 'Test', targetProgress: 50, achieved: false },
            { id: 'm2', description: 'Test', targetProgress: 55, achieved: false }
          ],
          progressHistory: [{ date: mockDate, progress: 60 }],
          status: 'in_progress',
          difficultyLevel: 'beginner',
          therapeuticApproaches: []
        }
      ];

      const suggestions = generateGoalEvolutionSuggestions(progresses);

      expect(suggestions.length).toBeGreaterThan(0);
      // Should be sorted by confidence (descending)
      for (let i = 1; i < suggestions.length; i++) {
        expect(suggestions[i - 1].confidence).toBeGreaterThanOrEqual(suggestions[i].confidence);
      }
    });
  });
});
