import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import RealTimeMonitoringInterface from '../RealTimeMonitoringInterface';
import { realTimeTherapeuticMonitor } from '../../../services/realTimeTherapeuticMonitor';
import realTimeMonitoringReducer from '../../../store/slices/realTimeMonitoringSlice';

// Mock the real-time therapeutic monitor
jest.mock('../../../services/realTimeTherapeuticMonitor', () => ({
  realTimeTherapeuticMonitor: {
    startMonitoring: jest.fn(),
    stopMonitoring: jest.fn(),
    registerCallback: jest.fn(),
    unregisterCallback: jest.fn(),
    getMonitoringMetrics: jest.fn(),
  }
}));

const mockRealTimeMonitor = realTimeTherapeuticMonitor as jest.Mocked<typeof realTimeTherapeuticMonitor>;

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      realTimeMonitoring: realTimeMonitoringReducer,
    },
  });
};

const renderWithProvider = (component: React.ReactElement, store = createTestStore()) => {
  return render(
    <Provider store={store}>
      {component}
    </Provider>
  );
};

describe('RealTimeMonitoringInterface', () => {
  const defaultProps = {
    sessionId: 'test-session-123',
    userId: 'test-user-456',
    therapeuticGoals: ['anxiety_reduction', 'stress_management'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockRealTimeMonitor.startMonitoring.mockReturnValue({
      sessionId: defaultProps.sessionId,
      userId: defaultProps.userId,
      startTime: Date.now(),
      emotionalStates: [],
      riskAssessments: [],
      interventions: [],
      therapeuticGoals: defaultProps.therapeuticGoals,
      sessionContext: {}
    });
  });

  describe('Component Initialization', () => {
    test('should render monitoring interface when active', () => {
      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      
      expect(screen.getByText('Real-Time Monitoring')).toBeInTheDocument();
      expect(screen.getByText(/Monitoring active since/)).toBeInTheDocument();
    });

    test('should start monitoring on mount', () => {
      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      
      expect(mockRealTimeMonitor.startMonitoring).toHaveBeenCalledWith(
        defaultProps.sessionId,
        defaultProps.userId,
        defaultProps.therapeuticGoals
      );
      expect(mockRealTimeMonitor.registerCallback).toHaveBeenCalledWith(
        defaultProps.sessionId,
        expect.any(Function)
      );
    });

    test('should stop monitoring on unmount', () => {
      const { unmount } = renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      
      unmount();
      
      expect(mockRealTimeMonitor.stopMonitoring).toHaveBeenCalledWith(defaultProps.sessionId);
      expect(mockRealTimeMonitor.unregisterCallback).toHaveBeenCalledWith(defaultProps.sessionId);
    });
  });

  describe('Risk Assessment Display', () => {
    test('should display low risk assessment', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      // Simulate risk assessment update
      const mockRiskAssessment = {
        riskLevel: 'low' as const,
        riskScore: 0.1,
        riskFactors: [],
        protectiveFactors: ['Positive emotional state'],
        interventionRecommendations: [],
        timestamp: Date.now(),
        confidence: 0.8
      };

      const mockEmotionalState = {
        valence: 0.5,
        arousal: 0.3,
        dominance: 0.6,
        confidence: 0.8,
        timestamp: Date.now(),
        indicators: ['happy', 'content']
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: mockEmotionalState,
          riskAssessment: mockRiskAssessment
        });
      });

      expect(screen.getByText(/Risk Level: LOW/)).toBeInTheDocument();
      expect(screen.getByText(/Score: 10%/)).toBeInTheDocument();
    });

    test('should display high risk assessment with factors', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      const mockRiskAssessment = {
        riskLevel: 'high' as const,
        riskScore: 0.8,
        riskFactors: [
          {
            type: 'emotional' as const,
            severity: 'high' as const,
            description: 'Severe negative emotional state detected',
            indicators: ['sad', 'hopeless'],
            duration: 10,
            trend: 'worsening' as const
          }
        ],
        protectiveFactors: [],
        interventionRecommendations: [],
        timestamp: Date.now(),
        confidence: 0.9
      };

      const mockEmotionalState = {
        valence: -0.8,
        arousal: 0.7,
        dominance: 0.2,
        confidence: 0.9,
        timestamp: Date.now(),
        indicators: ['sad', 'hopeless', 'anxious']
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: mockEmotionalState,
          riskAssessment: mockRiskAssessment
        });
      });

      expect(screen.getByText(/Risk Level: HIGH/)).toBeInTheDocument();
      expect(screen.getByText(/Score: 80%/)).toBeInTheDocument();
      expect(screen.getByText(/Risk factors detected:/)).toBeInTheDocument();
      expect(screen.getByText(/Severe negative emotional state detected/)).toBeInTheDocument();
    });

    test('should display critical risk assessment', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      const mockRiskAssessment = {
        riskLevel: 'critical' as const,
        riskScore: 0.95,
        riskFactors: [
          {
            type: 'behavioral' as const,
            severity: 'critical' as const,
            description: 'Crisis language or self-harm indicators detected',
            indicators: ['hurt myself', 'want to die'],
            duration: 0,
            trend: 'worsening' as const
          }
        ],
        protectiveFactors: [],
        interventionRecommendations: [
          {
            type: 'immediate' as const,
            priority: 'urgent' as const,
            intervention: 'Crisis intervention protocol activation',
            rationale: 'Critical risk level detected',
            expectedOutcome: 'Immediate safety',
            timeframe: 'Immediate',
            resources: ['Crisis hotline', 'Emergency services']
          }
        ],
        timestamp: Date.now(),
        confidence: 0.95
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: {
            valence: -0.9,
            arousal: 0.8,
            dominance: 0.1,
            confidence: 0.95,
            timestamp: Date.now(),
            indicators: ['hopeless', 'desperate']
          },
          riskAssessment: mockRiskAssessment
        });
      });

      expect(screen.getByText(/Risk Level: CRITICAL/)).toBeInTheDocument();
      expect(screen.getByText(/Score: 95%/)).toBeInTheDocument();
    });
  });

  describe('Emotional State Display', () => {
    test('should display emotional state information', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      const mockEmotionalState = {
        valence: 0.6,
        arousal: 0.4,
        dominance: 0.7,
        confidence: 0.85,
        timestamp: Date.now(),
        indicators: ['happy', 'content', 'confident']
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: mockEmotionalState,
          riskAssessment: {
            riskLevel: 'low' as const,
            riskScore: 0.1,
            riskFactors: [],
            protectiveFactors: [],
            interventionRecommendations: [],
            timestamp: Date.now(),
            confidence: 0.8
          }
        });
      });

      expect(screen.getByText('Emotional State')).toBeInTheDocument();
      expect(screen.getByText(/Confidence: 85%/)).toBeInTheDocument();
      expect(screen.getByText(/Calm and positive/)).toBeInTheDocument();
    });

    test('should show detailed emotional metrics when details are enabled', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      // Click details button
      const detailsButton = screen.getByText('Details');
      fireEvent.click(detailsButton);

      const mockEmotionalState = {
        valence: 0.3,
        arousal: 0.6,
        dominance: 0.5,
        confidence: 0.75,
        timestamp: Date.now(),
        indicators: ['excited', 'energetic']
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: mockEmotionalState,
          riskAssessment: {
            riskLevel: 'low' as const,
            riskScore: 0.2,
            riskFactors: [],
            protectiveFactors: [],
            interventionRecommendations: [],
            timestamp: Date.now(),
            confidence: 0.75
          }
        });
      });

      expect(screen.getByText('Valence')).toBeInTheDocument();
      expect(screen.getByText('Arousal')).toBeInTheDocument();
      expect(screen.getByText('Dominance')).toBeInTheDocument();
      expect(screen.getByText('0.30')).toBeInTheDocument();
      expect(screen.getByText('0.60')).toBeInTheDocument();
      expect(screen.getByText('0.50')).toBeInTheDocument();
    });
  });

  describe('Monitoring Metrics Display', () => {
    test('should display monitoring metrics', async () => {
      const mockMetrics = {
        averageRiskScore: 0.2,
        emotionalStability: 0.8,
        engagementLevel: 0.75,
        therapeuticProgress: 0.65,
        interventionEffectiveness: 0.9,
        sessionQuality: 0.78
      };

      mockRealTimeMonitor.getMonitoringMetrics.mockReturnValue(mockMetrics);

      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      await waitFor(() => {
        mockCallback({
          emotionalState: {
            valence: 0.5,
            arousal: 0.3,
            dominance: 0.6,
            confidence: 0.8,
            timestamp: Date.now(),
            indicators: []
          },
          riskAssessment: {
            riskLevel: 'low' as const,
            riskScore: 0.2,
            riskFactors: [],
            protectiveFactors: [],
            interventionRecommendations: [],
            timestamp: Date.now(),
            confidence: 0.8
          }
        });
      });

      expect(screen.getByText('Emotional Stability')).toBeInTheDocument();
      expect(screen.getByText('80%')).toBeInTheDocument();
      expect(screen.getByText('Engagement Level')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
      expect(screen.getByText('Therapeutic Progress')).toBeInTheDocument();
      expect(screen.getByText('65%')).toBeInTheDocument();
      expect(screen.getByText('Session Quality')).toBeInTheDocument();
      expect(screen.getByText('78%')).toBeInTheDocument();
    });
  });

  describe('Intervention Display', () => {
    test('should display active interventions', async () => {
      const mockCallback = jest.fn();
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      const mockIntervention = {
        interventionId: 'int-123',
        type: 'immediate' as const,
        intervention: 'Grounding and stabilization techniques',
        timestamp: Date.now(),
        outcome: 'pending' as const,
        userResponse: '',
        followUpRequired: true
      };

      await waitFor(() => {
        mockCallback({
          type: 'intervention_triggered',
          intervention: mockIntervention,
          riskAssessment: {
            riskLevel: 'high' as const,
            riskScore: 0.8,
            riskFactors: [],
            protectiveFactors: [],
            interventionRecommendations: [],
            timestamp: Date.now(),
            confidence: 0.9
          }
        });
      });

      expect(screen.getByText('Active Interventions')).toBeInTheDocument();
      expect(screen.getByText('Grounding and stabilization techniques')).toBeInTheDocument();
      expect(screen.getByText('pending')).toBeInTheDocument();
    });
  });

  describe('Alert Controls', () => {
    test('should toggle alerts when alert button is clicked', () => {
      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      
      const alertButton = screen.getByTitle('Alerts enabled');
      fireEvent.click(alertButton);
      
      expect(screen.getByTitle('Alerts disabled')).toBeInTheDocument();
    });

    test('should toggle details view when details button is clicked', () => {
      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      
      const detailsButton = screen.getByText('Details');
      fireEvent.click(detailsButton);
      
      expect(screen.getByText('Hide')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Hide'));
      expect(screen.getByText('Details')).toBeInTheDocument();
    });
  });

  describe('Crisis Detection Callbacks', () => {
    test('should call onCrisisDetected when high risk is detected', async () => {
      const mockOnCrisisDetected = jest.fn();
      const mockCallback = jest.fn();
      
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(
        <RealTimeMonitoringInterface 
          {...defaultProps} 
          onCrisisDetected={mockOnCrisisDetected}
        />
      );

      const mockRiskAssessment = {
        riskLevel: 'critical' as const,
        riskScore: 0.95,
        riskFactors: [],
        protectiveFactors: [],
        interventionRecommendations: [],
        timestamp: Date.now(),
        confidence: 0.95
      };

      await waitFor(() => {
        mockCallback({
          emotionalState: {
            valence: -0.9,
            arousal: 0.8,
            dominance: 0.1,
            confidence: 0.95,
            timestamp: Date.now(),
            indicators: []
          },
          riskAssessment: mockRiskAssessment
        });
      });

      expect(mockOnCrisisDetected).toHaveBeenCalledWith(mockRiskAssessment);
    });

    test('should call onInterventionTriggered when intervention is triggered', async () => {
      const mockOnInterventionTriggered = jest.fn();
      const mockCallback = jest.fn();
      
      mockRealTimeMonitor.registerCallback.mockImplementation((sessionId, callback) => {
        mockCallback.mockImplementation(callback);
      });

      renderWithProvider(
        <RealTimeMonitoringInterface 
          {...defaultProps} 
          onInterventionTriggered={mockOnInterventionTriggered}
        />
      );

      const mockIntervention = {
        interventionId: 'int-123',
        type: 'immediate' as const,
        intervention: 'Crisis intervention',
        timestamp: Date.now(),
        outcome: 'pending' as const,
        userResponse: '',
        followUpRequired: true
      };

      await waitFor(() => {
        mockCallback({
          type: 'intervention_triggered',
          intervention: mockIntervention
        });
      });

      expect(mockOnInterventionTriggered).toHaveBeenCalledWith(mockIntervention);
    });
  });

  describe('Error Handling', () => {
    test('should handle monitoring start failure gracefully', () => {
      mockRealTimeMonitor.startMonitoring.mockImplementation(() => {
        throw new Error('Failed to start monitoring');
      });

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);

      expect(consoleSpy).toHaveBeenCalledWith('Failed to start monitoring:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });

    test('should handle monitoring stop failure gracefully', () => {
      mockRealTimeMonitor.stopMonitoring.mockImplementation(() => {
        throw new Error('Failed to stop monitoring');
      });

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const { unmount } = renderWithProvider(<RealTimeMonitoringInterface {...defaultProps} />);
      unmount();

      expect(consoleSpy).toHaveBeenCalledWith('Failed to stop monitoring:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });
});
