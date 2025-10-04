import { realTimeTherapeuticMonitor } from '../realTimeTherapeuticMonitor';
import type { 
  EmotionalState, 
  RiskAssessment, 
  MonitoringSession,
  InterventionRecord 
} from '../realTimeTherapeuticMonitor';

describe('RealTimeTherapeuticMonitor', () => {
  const mockSessionId = 'test-session-123';
  const mockUserId = 'test-user-456';
  const mockTherapeuticGoals = ['anxiety_reduction', 'stress_management'];

  beforeEach(() => {
    // Clear any existing sessions
    const activeSessions = realTimeTherapeuticMonitor.getActiveSessions();
    activeSessions.forEach(session => {
      realTimeTherapeuticMonitor.stopMonitoring(session.sessionId);
    });
  });

  describe('Session Management', () => {
    test('should start monitoring session successfully', () => {
      const session = realTimeTherapeuticMonitor.startMonitoring(
        mockSessionId, 
        mockUserId, 
        mockTherapeuticGoals
      );

      expect(session).toBeDefined();
      expect(session.sessionId).toBe(mockSessionId);
      expect(session.userId).toBe(mockUserId);
      expect(session.therapeuticGoals).toEqual(mockTherapeuticGoals);
      expect(session.startTime).toBeGreaterThan(0);
      expect(session.endTime).toBeUndefined();
      expect(session.emotionalStates).toEqual([]);
      expect(session.riskAssessments).toEqual([]);
      expect(session.interventions).toEqual([]);
    });

    test('should stop monitoring session successfully', () => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
      
      const stoppedSession = realTimeTherapeuticMonitor.stopMonitoring(mockSessionId);
      
      expect(stoppedSession).toBeDefined();
      expect(stoppedSession!.endTime).toBeGreaterThan(0);
      expect(realTimeTherapeuticMonitor.getSession(mockSessionId)).toBeNull();
    });

    test('should return null when stopping non-existent session', () => {
      const result = realTimeTherapeuticMonitor.stopMonitoring('non-existent-session');
      expect(result).toBeNull();
    });

    test('should get active sessions', () => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
      realTimeTherapeuticMonitor.startMonitoring('session-2', 'user-2', ['goal-1']);
      
      const activeSessions = realTimeTherapeuticMonitor.getActiveSessions();
      expect(activeSessions).toHaveLength(2);
      expect(activeSessions.map(s => s.sessionId)).toContain(mockSessionId);
      expect(activeSessions.map(s => s.sessionId)).toContain('session-2');
    });
  });

  describe('Emotional State Analysis', () => {
    beforeEach(() => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
    });

    test('should analyze positive emotional state', async () => {
      const userInput = 'I feel happy and excited about my progress today!';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.emotionalState).toBeDefined();
      expect(result.emotionalState.valence).toBeGreaterThan(0);
      expect(result.emotionalState.indicators).toContain('happy');
      expect(result.emotionalState.indicators).toContain('excited');
      expect(result.emotionalState.confidence).toBeGreaterThan(0.5);
    });

    test('should analyze negative emotional state', async () => {
      const userInput = 'I feel sad and hopeless. Everything seems overwhelming.';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.emotionalState).toBeDefined();
      expect(result.emotionalState.valence).toBeLessThan(0);
      expect(result.emotionalState.indicators).toContain('sad');
      expect(result.emotionalState.indicators).toContain('hopeless');
      expect(result.emotionalState.indicators).toContain('overwhelming');
    });

    test('should analyze high arousal emotional state', async () => {
      const userInput = 'I am feeling so anxious and panicked right now!';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.emotionalState).toBeDefined();
      expect(result.emotionalState.arousal).toBeGreaterThan(0.5);
      expect(result.emotionalState.indicators).toContain('anxious');
      expect(result.emotionalState.indicators).toContain('panicked');
    });

    test('should analyze low dominance emotional state', async () => {
      const userInput = 'I feel so helpless and powerless in this situation.';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.emotionalState).toBeDefined();
      expect(result.emotionalState.dominance).toBeLessThan(0.5);
      expect(result.emotionalState.indicators).toContain('helpless');
      expect(result.emotionalState.indicators).toContain('powerless');
    });
  });

  describe('Risk Assessment', () => {
    beforeEach(() => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
    });

    test('should assess low risk for positive input', async () => {
      const userInput = 'I am feeling great today and making good progress!';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.riskAssessment).toBeDefined();
      expect(result.riskAssessment.riskLevel).toBe('low');
      expect(result.riskAssessment.riskScore).toBeLessThan(0.25);
      expect(result.riskAssessment.riskFactors).toHaveLength(0);
    });

    test('should analyze negative emotional input and generate risk assessment', async () => {
      const userInput = 'I feel extremely sad and depressed. I am hopeless and worthless. Everything is terrible and awful and overwhelming.';

      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId,
        userInput,
        {}
      );

      expect(result.riskAssessment).toBeDefined();
      expect(result.riskAssessment.riskLevel).toBeDefined();
      expect(result.riskAssessment.riskScore).toBeGreaterThan(0);
      expect(result.emotionalState.valence).toBeLessThan(0); // Should detect negative emotion
      expect(result.emotionalState.indicators.length).toBeGreaterThan(0);
    });

    test('should assess critical risk for crisis language', async () => {
      const userInput = 'I want to hurt myself. I can\'t see any way out.';

      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId,
        userInput,
        {}
      );



      expect(result.riskAssessment).toBeDefined();
      expect(result.riskAssessment.riskLevel).toBe('critical');
      expect(result.riskAssessment.riskScore).toBeGreaterThan(0.75);
      expect(result.riskAssessment.riskFactors.some(rf => rf.type === 'behavioral')).toBe(true);
      expect(result.riskAssessment.interventionRecommendations.some(ir => ir.priority === 'urgent')).toBe(true);
    });

    test('should generate appropriate intervention recommendations', async () => {
      const userInput = 'I feel overwhelmed and anxious about everything.';
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        userInput, 
        {}
      );

      expect(result.riskAssessment.interventionRecommendations).toBeDefined();
      expect(result.riskAssessment.interventionRecommendations.length).toBeGreaterThan(0);
      
      const recommendation = result.riskAssessment.interventionRecommendations[0];
      expect(recommendation.type).toBeDefined();
      expect(recommendation.priority).toBeDefined();
      expect(recommendation.intervention).toBeDefined();
      expect(recommendation.rationale).toBeDefined();
      expect(recommendation.expectedOutcome).toBeDefined();
      expect(recommendation.timeframe).toBeDefined();
      expect(recommendation.resources).toBeDefined();
    });
  });

  describe('Monitoring Metrics', () => {
    beforeEach(() => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
    });

    test('should return null metrics for session with no data', () => {
      const metrics = realTimeTherapeuticMonitor.getMonitoringMetrics(mockSessionId);
      
      expect(metrics).toBeDefined();
      expect(metrics!.averageRiskScore).toBe(0);
      expect(metrics!.emotionalStability).toBe(0.5);
      expect(metrics!.engagementLevel).toBe(0.5);
      expect(metrics!.therapeuticProgress).toBe(0.5);
      expect(metrics!.interventionEffectiveness).toBe(0.5);
      expect(metrics!.sessionQuality).toBe(0.5);
    });

    test('should calculate metrics after emotional state updates', async () => {
      // Add some emotional states
      await realTimeTherapeuticMonitor.analyzeUserInput(mockSessionId, 'I feel happy today!', {});
      await realTimeTherapeuticMonitor.analyzeUserInput(mockSessionId, 'I am content and peaceful.', {});
      
      const metrics = realTimeTherapeuticMonitor.getMonitoringMetrics(mockSessionId);
      
      expect(metrics).toBeDefined();
      expect(metrics!.averageRiskScore).toBeGreaterThanOrEqual(0);
      expect(metrics!.emotionalStability).toBeGreaterThan(0);
      expect(metrics!.engagementLevel).toBeGreaterThan(0);
    });

    test('should return null for non-existent session', () => {
      const metrics = realTimeTherapeuticMonitor.getMonitoringMetrics('non-existent-session');
      expect(metrics).toBeNull();
    });
  });

  describe('Callback System', () => {
    let callbackData: any = null;
    const mockCallback = jest.fn((data) => {
      callbackData = data;
    });

    beforeEach(() => {
      callbackData = null;
      mockCallback.mockClear();
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
      realTimeTherapeuticMonitor.registerCallback(mockSessionId, mockCallback);
    });

    test('should register and call callback on analysis', async () => {
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId,
        'I feel good today!',
        {}
      );

      expect(mockCallback).toHaveBeenCalled();
      expect(mockCallback).toHaveBeenCalledWith({
        emotionalState: result.emotionalState,
        riskAssessment: result.riskAssessment
      });

      // Check that the callback was called with the right data structure
      const callArgs = mockCallback.mock.calls[0][0];
      expect(callArgs).toBeDefined();
      expect(callArgs.emotionalState).toBeDefined();
      expect(callArgs.riskAssessment).toBeDefined();
    });

    test('should unregister callback', async () => {
      realTimeTherapeuticMonitor.unregisterCallback(mockSessionId);
      
      await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        'I feel good today!', 
        {}
      );

      expect(mockCallback).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    test('should throw error for non-existent session', async () => {
      await expect(
        realTimeTherapeuticMonitor.analyzeUserInput('non-existent-session', 'test input', {})
      ).rejects.toThrow('No active monitoring session found');
    });

    test('should handle empty user input gracefully', async () => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
      
      const result = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        '', 
        {}
      );

      expect(result.emotionalState).toBeDefined();
      expect(result.riskAssessment).toBeDefined();
      expect(result.emotionalState.valence).toBe(0);
      expect(result.emotionalState.arousal).toBe(0);
    });
  });

  describe('Integration with Context', () => {
    beforeEach(() => {
      realTimeTherapeuticMonitor.startMonitoring(mockSessionId, mockUserId, mockTherapeuticGoals);
    });

    test('should consider message length in analysis', async () => {
      const shortMessage = 'ok';
      const longMessage = 'I have been thinking a lot about my progress and I feel like I am making some good strides in managing my anxiety and stress levels.';
      
      const shortResult = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        shortMessage, 
        { messageLength: shortMessage.length }
      );
      
      const longResult = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        longMessage, 
        { messageLength: longMessage.length }
      );

      // Short messages might indicate lower engagement/arousal
      expect(shortResult.emotionalState.arousal).toBeLessThanOrEqual(longResult.emotionalState.arousal);
    });

    test('should consider response time in analysis', async () => {
      const quickResponse = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        'I feel okay', 
        { responseTime: 5000 } // 5 seconds
      );
      
      const slowResponse = await realTimeTherapeuticMonitor.analyzeUserInput(
        mockSessionId, 
        'I feel okay', 
        { responseTime: 45000 } // 45 seconds
      );

      // Slow responses might indicate lower arousal
      expect(slowResponse.emotionalState.arousal).toBeLessThanOrEqual(quickResponse.emotionalState.arousal);
    });
  });
});
