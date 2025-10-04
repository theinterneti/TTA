import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SessionManagementInterface from '../SessionManagementInterface';
import { therapeuticSessionService } from '../../../../services/therapeuticSessionService';
import { TherapeuticGoal } from '../../../../types/preferences';
import { UserContext } from '../../../../services/personalizedRecommendationEngine';

// Mock the therapeutic session service
jest.mock('../../../../services/therapeuticSessionService', () => ({
  therapeuticSessionService: {
    planSession: jest.fn(),
    createSession: jest.fn(),
    getSession: jest.fn(),
    getUserSessions: jest.fn(),
    executeSession: jest.fn(),
    completeSession: jest.fn(),
    analyzeTherapeuticJourney: jest.fn(),
  },
}));

const mockTherapeuticSessionService = therapeuticSessionService as jest.Mocked<typeof therapeuticSessionService>;

describe('SessionManagementInterface', () => {
  const mockUserId = 'test-user-123';
  const mockGoals: TherapeuticGoal[] = [
    {
      id: 'goal1',
      title: 'Manage Anxiety',
      description: 'Learn techniques to manage anxiety',
      category: 'mental-health',
      priority: 'high',
      targetDate: '2024-12-31',
      isActive: true,
      progress: 0.3,
      milestones: [],
      therapeuticApproaches: ['CBT'],
      measurableOutcomes: ['Reduced anxiety episodes'],
      personalRelevance: 0.9,
      difficultyLevel: 'moderate',
      timeCommitment: 'medium',
      supportLevel: 'high'
    }
  ];

  const mockUserContext: UserContext = {
    userId: mockUserId,
    preferences: {
      therapeuticApproaches: ['CBT'],
      sessionDuration: 60,
      communicationStyle: 'direct',
      triggerWarnings: [],
      accessibilityNeeds: []
    },
    progressHistory: [],
    feedbackHistory: [],
    sessionHistory: []
  };

  const mockSessionPlan = {
    sessionPlan: {
      objectives: [
        {
          id: 'obj1',
          description: 'Work on anxiety management',
          priority: 'high' as const,
          measurable: true,
          targetOutcome: 'Reduced anxiety symptoms',
          relatedGoals: ['goal1']
        }
      ],
      activities: [
        {
          id: 'activity1',
          name: 'Breathing Exercise',
          description: 'Practice deep breathing',
          duration: 15,
          therapeuticTechnique: 'mindfulness',
          materials: [],
          adaptations: []
        }
      ],
      techniques: [],
      expectedDuration: 60,
      preparationNotes: 'Test preparation notes',
      riskAssessment: {
        overallRisk: 'low' as const,
        riskFactors: [],
        mitigationStrategies: [],
        emergencyProtocols: []
      },
      intelligenceInsights: {
        goalSuggestions: [],
        conflictWarnings: { conflicts: [], hasConflicts: false, severity: 'low', autoResolvable: false },
        personalizedRecommendations: [],
        progressInsights: [],
        relationshipInsights: []
      }
    },
    confidence: 0.85,
    warnings: [],
    recommendations: []
  };

  const mockSession = {
    id: 'session-123',
    userId: mockUserId,
    status: 'planned' as const,
    sessionType: 'individual' as const,
    plannedDate: new Date(),
    duration: 60,
    focusAreas: ['Anxiety management'],
    plannedGoals: ['goal1'],
    therapeuticApproaches: ['CBT'],
    sessionPlan: mockSessionPlan.sessionPlan,
    createdAt: new Date(),
    updatedAt: new Date()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockTherapeuticSessionService.getUserSessions.mockReturnValue([]);
    mockTherapeuticSessionService.analyzeTherapeuticJourney.mockRejectedValue(new Error('No sessions'));
  });

  describe('Component Rendering', () => {
    it('should render session management interface with all tabs', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      expect(screen.getByText('Session Management')).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /session planning/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /active sessions/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /session history/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /therapeutic journey/i })).toBeInTheDocument();
    });

    it('should display total sessions count', () => {
      mockTherapeuticSessionService.getUserSessions.mockReturnValue([mockSession]);
      
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      expect(screen.getByText('Total Sessions:')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('should show planning tab by default', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      expect(screen.getByRole('tab', { name: /session planning/i })).toHaveAttribute('aria-selected', 'true');
      expect(screen.getAllByText('Session Planning')).toHaveLength(2); // Tab button and panel heading
      expect(screen.getByText('Plan New Session')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      // Click on Active Sessions tab
      fireEvent.click(screen.getByRole('tab', { name: /active sessions/i }));
      expect(screen.getByRole('tab', { name: /active sessions/i })).toHaveAttribute('aria-selected', 'true');
      expect(screen.getAllByText('Active Sessions')).toHaveLength(2); // Tab button and panel heading

      // Click on Session History tab
      fireEvent.click(screen.getByRole('tab', { name: /session history/i }));
      expect(screen.getByRole('tab', { name: /session history/i })).toHaveAttribute('aria-selected', 'true');
      expect(screen.getAllByText('Session History')).toHaveLength(2); // Tab button and panel heading

      // Click on Therapeutic Journey tab
      fireEvent.click(screen.getByRole('tab', { name: /therapeutic journey/i }));
      expect(screen.getByRole('tab', { name: /therapeutic journey/i })).toHaveAttribute('aria-selected', 'true');
      expect(screen.getAllByText('Therapeutic Journey')).toHaveLength(2); // Tab button and panel heading
    });
  });

  describe('Session Planning', () => {
    it('should disable plan button when no goals are provided', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={[]}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      expect(planButton).toBeDisabled();
      expect(screen.getByText('Please select therapeutic goals before planning a session.')).toBeInTheDocument();
    });

    it('should enable plan button when goals are provided', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      expect(planButton).not.toBeDisabled();
    });

    it('should call planSession when plan button is clicked', async () => {
      mockTherapeuticSessionService.planSession.mockResolvedValue(mockSessionPlan);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        expect(mockTherapeuticSessionService.planSession).toHaveBeenCalledWith(
          mockUserId,
          mockGoals,
          mockUserContext,
          'individual',
          60
        );
      });
    });

    it('should display session plan after planning', async () => {
      mockTherapeuticSessionService.planSession.mockResolvedValue(mockSessionPlan);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        expect(screen.getByText('Session Plan')).toBeInTheDocument();
        expect(screen.getByText('85%')).toBeInTheDocument(); // Confidence
        expect(screen.getByText('Work on anxiety management')).toBeInTheDocument();
        expect(screen.getByText('Breathing Exercise')).toBeInTheDocument();
        expect(screen.getByText('Create Session')).toBeInTheDocument();
      });
    });

    it('should handle planning errors gracefully', async () => {
      mockTherapeuticSessionService.planSession.mockRejectedValue(new Error('Planning failed'));

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to plan session')).toBeInTheDocument();
      });
    });
  });

  describe('Session Creation', () => {
    it('should create session when create button is clicked', async () => {
      mockTherapeuticSessionService.planSession.mockResolvedValue(mockSessionPlan);
      mockTherapeuticSessionService.createSession.mockReturnValue('session-123');
      mockTherapeuticSessionService.getSession.mockReturnValue(mockSession);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      // First plan a session
      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        expect(screen.getByText('Create Session')).toBeInTheDocument();
      });

      // Then create the session
      const createButton = screen.getByText('Create Session');
      fireEvent.click(createButton);

      expect(mockTherapeuticSessionService.createSession).toHaveBeenCalledWith(
        mockUserId,
        mockSessionPlan.sessionPlan,
        expect.any(Date),
        'individual'
      );
    });

    it('should call onSessionUpdate callback when session is created', async () => {
      const mockOnSessionUpdate = jest.fn();
      mockTherapeuticSessionService.planSession.mockResolvedValue(mockSessionPlan);
      mockTherapeuticSessionService.createSession.mockReturnValue('session-123');
      mockTherapeuticSessionService.getSession.mockReturnValue(mockSession);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
          onSessionUpdate={mockOnSessionUpdate}
        />
      );

      // Plan and create session
      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        const createButton = screen.getByText('Create Session');
        fireEvent.click(createButton);
      });

      expect(mockOnSessionUpdate).toHaveBeenCalledWith('session-123', mockSession);
    });
  });

  describe('Active Sessions', () => {
    it('should show no active sessions message when no current session', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      // Switch to active sessions tab
      fireEvent.click(screen.getByRole('tab', { name: /active sessions/i }));

      expect(screen.getByText('No active sessions')).toBeInTheDocument();
      expect(screen.getByText('Plan a new session to get started')).toBeInTheDocument();
    });

    it('should display current session when available', async () => {
      mockTherapeuticSessionService.planSession.mockResolvedValue(mockSessionPlan);
      mockTherapeuticSessionService.createSession.mockReturnValue('session-123');
      mockTherapeuticSessionService.getSession.mockReturnValue(mockSession);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      // Create a session first
      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        const createButton = screen.getByText('Create Session');
        fireEvent.click(createButton);
      });

      // Should automatically switch to active sessions tab
      await waitFor(() => {
        expect(screen.getByText('Current Session')).toBeInTheDocument();
        expect(screen.getByText('planned')).toBeInTheDocument();
        expect(screen.getByText('Anxiety management')).toBeInTheDocument();
        expect(screen.getByText('60 minutes')).toBeInTheDocument();
        expect(screen.getByText('Start Session')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes for tabs', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const tabList = screen.getByRole('tablist');
      expect(tabList).toHaveAttribute('aria-label', 'Session management tabs');

      const planningTab = screen.getByRole('tab', { name: /session planning/i });
      expect(planningTab).toHaveAttribute('aria-selected', 'true');
      expect(planningTab).toHaveAttribute('aria-controls', 'planning-panel');
      expect(planningTab).toHaveAttribute('id', 'planning-tab');

      const planningPanel = screen.getByRole('tabpanel');
      expect(planningPanel).toHaveAttribute('aria-labelledby', 'planning-tab');
      expect(planningPanel).toHaveAttribute('id', 'planning-panel');
    });

    it('should have proper button states and labels', () => {
      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={[]}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      expect(planButton).toBeDisabled();
      expect(planButton).toHaveClass('disabled:opacity-50', 'disabled:cursor-not-allowed');
    });
  });

  describe('Error Handling', () => {
    it('should display error messages when operations fail', async () => {
      mockTherapeuticSessionService.planSession.mockRejectedValue(new Error('Network error'));

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      fireEvent.click(planButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to plan session')).toBeInTheDocument();
      });
    });

    it('should clear error messages when new operations succeed', async () => {
      mockTherapeuticSessionService.planSession
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockSessionPlan);

      render(
        <SessionManagementInterface
          userId={mockUserId}
          goals={mockGoals}
          userContext={mockUserContext}
        />
      );

      const planButton = screen.getByText('Plan New Session');
      
      // First attempt fails
      fireEvent.click(planButton);
      await waitFor(() => {
        expect(screen.getByText('Failed to plan session')).toBeInTheDocument();
      });

      // Second attempt succeeds
      fireEvent.click(planButton);
      await waitFor(() => {
        expect(screen.queryByText('Failed to plan session')).not.toBeInTheDocument();
        expect(screen.getByText('Session Plan')).toBeInTheDocument();
      });
    });
  });
});
