/**
 * Unit tests for PersonalizedRecommendationInterface component
 * 
 * Tests comprehensive personalized recommendation display functionality including
 * filtering, interaction, feedback, and accessibility features.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import PersonalizedRecommendationInterface from '../PersonalizedRecommendationInterface';
import {
  RecommendationResult,
  ContextualRecommendation
} from '../../../../services/personalizedRecommendationEngine';

// Mock recommendation data
const mockRecommendations: ContextualRecommendation[] = [
  {
    id: 'rec-1',
    type: 'goal_suggestion',
    category: 'immediate_action',
    title: 'Consider adding: Mindfulness Development',
    description: 'Focus on developing present-moment awareness and mindful living practices. This foundational goal aligns well with your current therapeutic journey.',
    confidence: 0.85,
    priority: 'high',
    clinicalEvidence: 'strong',
    personalizationFactors: [
      {
        factor: 'user_preferences',
        weight: 0.8,
        description: 'Aligns with your preference for mindfulness-based approaches',
        evidenceSource: 'preference_analysis'
      },
      {
        factor: 'progress_readiness',
        weight: 0.7,
        description: 'Your current progress suggests readiness for this goal',
        evidenceSource: 'progress_analysis'
      }
    ],
    expectedOutcome: 'Improved present-moment awareness and stress reduction',
    timeframe: 'this_week',
    actionable: true,
    relatedGoals: ['anxiety_reduction', 'stress_management'],
    therapeuticApproaches: ['mindfulness'],
    contextualFactors: [
      {
        context: 'current_stress_levels',
        relevance: 0.9,
        impact: 'positive',
        description: 'High stress levels indicate strong benefit potential'
      }
    ],
    adaptationReason: 'Recommended based on foundational analysis',
    userRelevanceScore: 0.9,
    timingSensitivity: 'optimal',
    progressAlignment: {
      alignmentScore: 0.8,
      progressStage: 'beginning',
      readinessLevel: 0.8,
      challengeAppropriate: true
    }
  },
  {
    id: 'rec-2',
    type: 'progress_enhancement',
    category: 'progress_optimization',
    title: 'Boost progress on: Anxiety Reduction',
    description: 'Your progress on Anxiety Reduction has slowed. Let\'s explore strategies to reignite momentum.',
    confidence: 0.75,
    priority: 'medium',
    clinicalEvidence: 'moderate',
    personalizationFactors: [
      {
        factor: 'stalled_progress',
        weight: 0.8,
        description: 'Progress has stalled on this goal',
        evidenceSource: 'progress_analysis'
      }
    ],
    expectedOutcome: 'Renewed momentum and clearer progress path',
    timeframe: 'this_month',
    actionable: true,
    relatedGoals: ['anxiety_reduction'],
    contextualFactors: [
      {
        context: 'progress_stagnation',
        relevance: 0.9,
        impact: 'negative',
        description: 'Goal progress has not advanced recently'
      }
    ],
    adaptationReason: 'Progress has stalled, suggesting targeted intervention',
    userRelevanceScore: 0.8,
    timingSensitivity: 'urgent',
    progressAlignment: {
      alignmentScore: 0.7,
      progressStage: 'developing',
      readinessLevel: 0.8,
      challengeAppropriate: true
    }
  },
  {
    id: 'rec-3',
    type: 'approach_optimization',
    category: 'long_term_development',
    title: 'Try a different approach: Somatic Therapy',
    description: 'Consider exploring Somatic Therapy to enhance your therapeutic progress',
    confidence: 0.6,
    priority: 'low',
    clinicalEvidence: 'emerging',
    personalizationFactors: [
      {
        factor: 'approach_effectiveness',
        weight: 0.6,
        description: 'Current approaches showing limited effectiveness',
        evidenceSource: 'effectiveness_analysis'
      }
    ],
    expectedOutcome: 'Enhanced therapeutic effectiveness through Somatic Therapy',
    timeframe: 'next_quarter',
    actionable: true,
    therapeuticApproaches: ['somatic_therapy'],
    contextualFactors: [
      {
        context: 'approach_limitations',
        relevance: 0.7,
        impact: 'neutral',
        description: 'Current approaches may benefit from complementary methods'
      }
    ],
    adaptationReason: 'Alternative approach suggested based on effectiveness patterns',
    userRelevanceScore: 0.6,
    timingSensitivity: 'flexible',
    progressAlignment: {
      alignmentScore: 0.6,
      progressStage: 'developing',
      readinessLevel: 0.6,
      challengeAppropriate: true
    }
  }
];

const mockRecommendationResult: RecommendationResult = {
  recommendations: mockRecommendations,
  totalRecommendations: 3,
  personalizationScore: 0.8,
  confidenceLevel: 'high',
  recommendationSummary: {
    totalRecommendations: 3,
    byPriority: { critical: 0, high: 1, medium: 1, low: 1, optional: 0 },
    byCategory: { 
      immediate_action: 1, 
      short_term_planning: 0, 
      long_term_development: 1, 
      crisis_prevention: 0, 
      progress_optimization: 1, 
      relationship_enhancement: 0, 
      self_care: 0, 
      skill_building: 0 
    },
    byTimeframe: { immediate: 0, this_week: 1, this_month: 1, next_quarter: 1, long_term: 0 },
    averageConfidence: 0.73,
    personalizationStrength: 'high'
  },
  nextReviewDate: new Date('2024-02-01'),
  adaptationHistory: []
};

const mockProps = {
  recommendationResult: mockRecommendationResult,
  onAcceptRecommendation: jest.fn(),
  onDismissRecommendation: jest.fn(),
  onProvideFeedback: jest.fn(),
  onRequestMoreInfo: jest.fn()
};

describe('PersonalizedRecommendationInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render recommendation interface with header', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      expect(screen.getByText('Personalized Recommendations')).toBeInTheDocument();
      expect(screen.getByText('AI-powered suggestions tailored to your therapeutic journey')).toBeInTheDocument();
      expect(screen.getAllByText('High Confidence')).toHaveLength(2); // One in header, one in recommendation
      expect(screen.getByText('80% Personalized')).toBeInTheDocument();
    });

    it('should render all recommendations', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      expect(screen.getByText('Consider adding: Mindfulness Development')).toBeInTheDocument();
      expect(screen.getByText('Boost progress on: Anxiety Reduction')).toBeInTheDocument();
      expect(screen.getByText('Try a different approach: Somatic Therapy')).toBeInTheDocument();
    });

    it('should display priority badges correctly', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      // Use more specific selectors for priority badges
      const highPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('high') &&
               element?.textContent?.includes('⚡') &&
               element?.className?.includes('text-orange-600');
      });
      const mediumPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('medium') &&
               element?.textContent?.includes('💡') &&
               element?.className?.includes('text-blue-600');
      });
      const lowPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('low') &&
               element?.textContent?.includes('💭') &&
               element?.className?.includes('text-gray-600');
      });

      expect(highPriorityElement).toBeInTheDocument();
      expect(mediumPriorityElement).toBeInTheDocument();
      expect(lowPriorityElement).toBeInTheDocument();
    });

    it('should display confidence badges correctly', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      expect(screen.getAllByText('High Confidence')).toHaveLength(2); // Header + recommendation
      expect(screen.getAllByText('Medium Confidence')).toHaveLength(2); // Two recommendations
      expect(screen.queryByText('Lower Confidence')).not.toBeInTheDocument(); // None in mock data
    });

    it('should display timeframes and expected outcomes', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      // Use more specific selectors for timeframes
      expect(screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' && element?.textContent === '⏱️ this week';
      })).toBeInTheDocument();
      expect(screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' && element?.textContent === '⏱️ this month';
      })).toBeInTheDocument();
      expect(screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' && element?.textContent === '⏱️ next quarter';
      })).toBeInTheDocument();
      expect(screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' && element?.textContent === '🎯 Improved present-moment awareness and stress reduction';
      })).toBeInTheDocument();
    });

    it('should render empty state when no recommendations', () => {
      const emptyProps = {
        ...mockProps,
        recommendationResult: {
          ...mockRecommendationResult,
          recommendations: [],
          totalRecommendations: 0
        }
      };
      
      render(<PersonalizedRecommendationInterface {...emptyProps} />);
      
      expect(screen.getByText('You\'re doing great!')).toBeInTheDocument();
      expect(screen.getByText('No specific recommendations at this time. Continue with your current therapeutic journey.')).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    it('should filter recommendations by priority', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const priorityFilter = screen.getByLabelText('Priority:');
      await user.selectOptions(priorityFilter, 'high');
      
      expect(screen.getByText('Consider adding: Mindfulness Development')).toBeInTheDocument();
      expect(screen.queryByText('Boost progress on: Anxiety Reduction')).not.toBeInTheDocument();
      expect(screen.queryByText('Try a different approach: Somatic Therapy')).not.toBeInTheDocument();
    });

    it('should filter recommendations by timeframe', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const timeframeFilter = screen.getByLabelText('Timeframe:');
      await user.selectOptions(timeframeFilter, 'this_week');
      
      expect(screen.getByText('Consider adding: Mindfulness Development')).toBeInTheDocument();
      expect(screen.queryByText('Boost progress on: Anxiety Reduction')).not.toBeInTheDocument();
      expect(screen.queryByText('Try a different approach: Somatic Therapy')).not.toBeInTheDocument();
    });

    it('should show all recommendations when filter is set to "all"', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      // First filter to high priority
      const priorityFilter = screen.getByLabelText('Priority:');
      await user.selectOptions(priorityFilter, 'high');
      
      // Then reset to all
      await user.selectOptions(priorityFilter, 'all');
      
      expect(screen.getByText('Consider adding: Mindfulness Development')).toBeInTheDocument();
      expect(screen.getByText('Boost progress on: Anxiety Reduction')).toBeInTheDocument();
      expect(screen.getByText('Try a different approach: Somatic Therapy')).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('should expand and collapse recommendation details', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const showDetailsButton = screen.getAllByText('Show Details')[0];
      await user.click(showDetailsButton);
      
      expect(screen.getByText('Personalization Factors')).toBeInTheDocument();
      expect(screen.getByText('Clinical Evidence')).toBeInTheDocument();
      expect(screen.getByText('Aligns with your preference for mindfulness-based approaches')).toBeInTheDocument();
      
      const showLessButton = screen.getByText('Show Less');
      await user.click(showLessButton);
      
      expect(screen.queryByText('Personalization Factors')).not.toBeInTheDocument();
    });

    it('should call onAcceptRecommendation when accept button is clicked', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const acceptButtons = screen.getAllByText('Accept');
      await user.click(acceptButtons[0]);
      
      expect(mockProps.onAcceptRecommendation).toHaveBeenCalledWith('rec-1');
    });

    it('should call onDismissRecommendation when dismiss button is clicked', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const dismissButtons = screen.getAllByText('Dismiss');
      await user.click(dismissButtons[0]);
      
      expect(mockProps.onDismissRecommendation).toHaveBeenCalledWith('rec-1');
    });

    it('should call onRequestMoreInfo when more info button is clicked', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const moreInfoButtons = screen.getAllByText('More Info');
      await user.click(moreInfoButtons[0]);
      
      expect(mockProps.onRequestMoreInfo).toHaveBeenCalledWith('rec-1');
    });
  });

  describe('Feedback', () => {
    it('should show feedback form when feedback button is clicked', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const feedbackButtons = screen.getAllByText('Feedback');
      await user.click(feedbackButtons[0]);
      
      expect(screen.getByDisplayValue('3 - Moderately helpful')).toBeInTheDocument();
      expect(screen.getByText('Submit')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('should submit feedback with selected rating', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const feedbackButtons = screen.getAllByText('Feedback');
      await user.click(feedbackButtons[0]);
      
      const ratingSelect = screen.getByDisplayValue('3 - Moderately helpful');
      await user.selectOptions(ratingSelect, '5');
      
      const submitButton = screen.getByText('Submit');
      await user.click(submitButton);
      
      expect(mockProps.onProvideFeedback).toHaveBeenCalledWith('rec-1', 5, '');
    });

    it('should cancel feedback form', async () => {
      const user = userEvent.setup();
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const feedbackButtons = screen.getAllByText('Feedback');
      await user.click(feedbackButtons[0]);
      
      expect(screen.getByText('Submit')).toBeInTheDocument();
      
      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(screen.queryByText('Submit')).not.toBeInTheDocument();
      expect(screen.getAllByText('Feedback')).toHaveLength(3); // All three recommendations show feedback button
    });
  });

  describe('Display Limits', () => {
    it('should respect maxDisplayRecommendations prop', () => {
      render(
        <PersonalizedRecommendationInterface 
          {...mockProps} 
          maxDisplayRecommendations={2}
        />
      );
      
      expect(screen.getByText('Consider adding: Mindfulness Development')).toBeInTheDocument();
      expect(screen.getByText('Boost progress on: Anxiety Reduction')).toBeInTheDocument();
      expect(screen.queryByText('Try a different approach: Somatic Therapy')).not.toBeInTheDocument();
      
      expect(screen.getByText('Showing 2 of 3 recommendations')).toBeInTheDocument();
    });
  });

  describe('Footer Information', () => {
    it('should display recommendation count and next review date', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      expect(screen.getByText('Showing 3 of 3 recommendations')).toBeInTheDocument();
      // Use regex to match date format variations
      expect(screen.getByText(/Next review: \d{1,2}\/\d{1,2}\/\d{4}/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for filters', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      expect(screen.getByLabelText('Priority:')).toBeInTheDocument();
      expect(screen.getByLabelText('Timeframe:')).toBeInTheDocument();
    });

    it('should have proper heading structure', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const mainHeading = screen.getByRole('heading', { level: 3 });
      expect(mainHeading).toHaveTextContent('Personalized Recommendations');
    });

    it('should have keyboard accessible buttons', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      const acceptButtons = screen.getAllByText('Accept');
      acceptButtons.forEach(button => {
        expect(button).toBeEnabled();
        expect(button.tagName).toBe('BUTTON');
      });
    });
  });

  describe('Visual Indicators', () => {
    it('should display appropriate icons for different recommendation types', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);
      
      // Check that emoji icons are present (they would be in the DOM as text)
      const recommendationElements = screen.getAllByText(/🎯|📈|🔄/);
      expect(recommendationElements.length).toBeGreaterThan(0);
    });

    it('should display priority indicators with appropriate styling', () => {
      render(<PersonalizedRecommendationInterface {...mockProps} />);

      // Use more specific selectors for priority badges
      const highPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('high') &&
               element?.textContent?.includes('⚡') &&
               element?.className?.includes('text-orange-600');
      });
      const mediumPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('medium') &&
               element?.textContent?.includes('💡') &&
               element?.className?.includes('text-blue-600');
      });
      const lowPriorityElement = screen.getByText((content, element) => {
        return element?.tagName === 'SPAN' &&
               element?.textContent?.includes('low') &&
               element?.textContent?.includes('💭') &&
               element?.className?.includes('text-gray-600');
      });

      expect(highPriorityElement).toBeInTheDocument();
      expect(mediumPriorityElement).toBeInTheDocument();
      expect(lowPriorityElement).toBeInTheDocument();
    });
  });
});
