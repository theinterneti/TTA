import React, { useState, useEffect } from 'react';
import {
  therapeuticSessionService,
  TherapeuticSession,
  SessionPlanningResult,
  SessionExecutionResult,
  SessionAnalysisResult,
  JourneyAnalysisResult,
  UserFeedback
} from '../../../services/therapeuticSessionService';
import { TherapeuticGoal } from '../../../types/index';
import { UserContext } from '../../../services/personalizedRecommendationEngine';

interface SessionManagementInterfaceProps {
  userId: string;
  goals: TherapeuticGoal[];
  userContext: UserContext;
  onSessionUpdate?: (sessionId: string, session: TherapeuticSession) => void;
  onJourneyUpdate?: (journey: JourneyAnalysisResult) => void;
}

type SessionManagementTab = 'planning' | 'active' | 'history' | 'journey';

const SessionManagementInterface: React.FC<SessionManagementInterfaceProps> = ({
  userId,
  goals,
  userContext,
  onSessionUpdate,
  onJourneyUpdate
}) => {
  const [activeTab, setActiveTab] = useState<SessionManagementTab>('planning');
  const [sessions, setSessions] = useState<TherapeuticSession[]>([]);
  const [currentSession, setCurrentSession] = useState<TherapeuticSession | null>(null);
  const [sessionPlan, setSessionPlan] = useState<SessionPlanningResult | null>(null);
  const [journeyAnalysis, setJourneyAnalysis] = useState<JourneyAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load user sessions on component mount
  useEffect(() => {
    loadUserSessions();
    loadJourneyAnalysis();
  }, [userId]);

  const loadUserSessions = () => {
    try {
      const userSessions = therapeuticSessionService.getUserSessions(userId);
      setSessions(userSessions);
    } catch (err) {
      setError('Failed to load sessions');
      console.error('Error loading sessions:', err);
    }
  };

  const loadJourneyAnalysis = async () => {
    try {
      const journey = await therapeuticSessionService.analyzeTherapeuticJourney(userId);
      setJourneyAnalysis(journey);
      onJourneyUpdate?.(journey);
    } catch (err) {
      // Journey analysis might fail if no sessions exist yet
      console.log('Journey analysis not available:', err);
    }
  };

  const handlePlanSession = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const planResult = await therapeuticSessionService.planSession(
        userId,
        goals,
        userContext,
        'individual',
        60
      );
      setSessionPlan(planResult);
    } catch (err) {
      setError('Failed to plan session');
      console.error('Error planning session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSession = () => {
    if (!sessionPlan) return;

    try {
      const sessionId = therapeuticSessionService.createSession(
        userId,
        sessionPlan.sessionPlan,
        new Date(),
        'individual'
      );

      const newSession = therapeuticSessionService.getSession(sessionId);
      if (newSession) {
        setSessions(prev => [newSession, ...prev]);
        setCurrentSession(newSession);
        onSessionUpdate?.(sessionId, newSession);
        setActiveTab('active');
      }
    } catch (err) {
      setError('Failed to create session');
      console.error('Error creating session:', err);
    }
  };

  const handleStartSession = async (sessionId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      await therapeuticSessionService.executeSession(sessionId);
      const updatedSession = therapeuticSessionService.getSession(sessionId);
      if (updatedSession) {
        setCurrentSession(updatedSession);
        setSessions(prev => prev.map(s => s.id === sessionId ? updatedSession : s));
        onSessionUpdate?.(sessionId, updatedSession);
      }
    } catch (err) {
      setError('Failed to start session');
      console.error('Error starting session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteSession = async (sessionId: string, feedback: UserFeedback) => {
    setIsLoading(true);
    setError(null);

    try {
      const completionResult = await therapeuticSessionService.completeSession(
        sessionId,
        feedback,
        'Session completed successfully'
      );

      const updatedSession = therapeuticSessionService.getSession(sessionId);
      if (updatedSession) {
        setSessions(prev => prev.map(s => s.id === sessionId ? updatedSession : s));
        setCurrentSession(null);
        onSessionUpdate?.(sessionId, updatedSession);

        // Refresh journey analysis
        await loadJourneyAnalysis();
      }
    } catch (err) {
      setError('Failed to complete session');
      console.error('Error completing session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTabNavigation = () => (
    <nav className="flex overflow-x-auto scrollbar-hide space-x-2 sm:space-x-1 mb-6 pb-2 sm:pb-0" role="tablist" aria-label="Session management tabs">
      {[
        { id: 'planning', label: 'Session Planning', shortLabel: 'Planning', icon: '📋' },
        { id: 'active', label: 'Active Sessions', shortLabel: 'Active', icon: '▶️' },
        { id: 'history', label: 'Session History', shortLabel: 'History', icon: '📚' },
        { id: 'journey', label: 'Therapeutic Journey', shortLabel: 'Journey', icon: '🗺️' }
      ].map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`${tab.id}-panel`}
          id={`${tab.id}-tab`}
          className={`px-4 py-3 sm:py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center ${
            activeTab === tab.id
              ? 'bg-blue-100 text-blue-700 border border-blue-200'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50 active:bg-gray-100'
          }`}
          onClick={() => setActiveTab(tab.id as SessionManagementTab)}
        >
          <span aria-hidden="true" className="mr-2 text-base sm:text-sm">{tab.icon}</span>
          <span className="hidden sm:inline">{tab.label}</span>
          <span className="sm:hidden text-xs">{tab.shortLabel}</span>
        </button>
      ))}
    </nav>
  );

  const renderSessionPlanningPanel = () => (
    <div
      role="tabpanel"
      id="planning-panel"
      aria-labelledby="planning-tab"
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Session Planning</h3>
        <button
          onClick={handlePlanSession}
          disabled={isLoading || goals.length === 0}
          className="px-4 py-3 sm:py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[44px] text-sm sm:text-base"
        >
          {isLoading ? 'Planning...' : 'Plan New Session'}
        </button>
      </div>

      {goals.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <p className="text-yellow-800">
            Please select therapeutic goals before planning a session.
          </p>
        </div>
      )}

      {sessionPlan && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-gray-900">Session Plan</h4>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Confidence:</span>
              <div className={`px-2 py-1 rounded text-sm font-medium ${
                sessionPlan.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                sessionPlan.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {Math.round(sessionPlan.confidence * 100)}%
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h5 className="font-medium text-gray-900 mb-2">Objectives ({sessionPlan.sessionPlan.objectives.length})</h5>
              <ul className="space-y-2">
                {sessionPlan.sessionPlan.objectives.map((objective) => (
                  <li key={objective.id} className="flex items-start space-x-3">
                    <span className={`inline-block w-2 h-2 rounded-full mt-2 ${
                      objective.priority === 'high' ? 'bg-red-500' :
                      objective.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`} />
                    <div>
                      <p className="text-gray-900">{objective.description}</p>
                      <p className="text-sm text-gray-600">{objective.targetOutcome}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h5 className="font-medium text-gray-900 mb-2">Activities ({sessionPlan.sessionPlan.activities.length})</h5>
              <div className="space-y-2">
                {sessionPlan.sessionPlan.activities.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p className="font-medium text-gray-900">{activity.name}</p>
                      <p className="text-sm text-gray-600">{activity.description}</p>
                    </div>
                    <span className="text-sm text-gray-500">{activity.duration}min</span>
                  </div>
                ))}
              </div>
            </div>

            {sessionPlan.warnings.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <h5 className="font-medium text-yellow-800 mb-2">Warnings</h5>
                <ul className="list-disc list-inside space-y-1">
                  {sessionPlan.warnings.map((warning, index) => (
                    <li key={index} className="text-yellow-700">{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex justify-end">
              <button
                onClick={handleCreateSession}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Create Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderActiveSessionsPanel = () => (
    <div
      role="tabpanel"
      id="active-panel"
      aria-labelledby="active-tab"
      className="space-y-6"
    >
      <h3 className="text-lg font-semibold text-gray-900">Active Sessions</h3>

      {currentSession ? (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-gray-900">Current Session</h4>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              currentSession.status === 'in-progress' ? 'bg-green-100 text-green-800' :
              currentSession.status === 'planned' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {currentSession.status}
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Focus Areas:</p>
              <p className="text-gray-900">{currentSession.focusAreas.join(', ')}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Duration:</p>
              <p className="text-gray-900">{currentSession.duration} minutes</p>
            </div>

            <div className="flex space-x-3">
              {currentSession.status === 'planned' && (
                <button
                  onClick={() => handleStartSession(currentSession.id)}
                  disabled={isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? 'Starting...' : 'Start Session'}
                </button>
              )}

              {currentSession.status === 'in-progress' && (
                <button
                  onClick={() => {
                    const feedback: UserFeedback = {
                      sessionRating: 8,
                      helpfulness: 8,
                      engagement: 7,
                      comfort: 8,
                      comments: 'Session completed',
                      improvements: []
                    };
                    handleCompleteSession(currentSession.id, feedback);
                  }}
                  disabled={isLoading}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? 'Completing...' : 'Complete Session'}
                </button>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500">No active sessions</p>
          <p className="text-sm text-gray-400 mt-2">Plan a new session to get started</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="session-management-interface bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900">Session Management</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Total Sessions:</span>
            <div className="px-2 py-1 rounded text-sm font-medium bg-blue-100 text-blue-800">
              {sessions.length}
            </div>
          </div>
        </div>
        {renderTabNavigation()}
      </div>

      <div className="p-6">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {activeTab === 'planning' && renderSessionPlanningPanel()}
        {activeTab === 'active' && renderActiveSessionsPanel()}
        {activeTab === 'history' && (
          <div role="tabpanel" id="history-panel" aria-labelledby="history-tab">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Session History</h3>
            <p className="text-gray-500">Session history panel - Coming soon</p>
          </div>
        )}
        {activeTab === 'journey' && (
          <div role="tabpanel" id="journey-panel" aria-labelledby="journey-tab">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Journey</h3>
            <p className="text-gray-500">Therapeutic journey panel - Coming soon</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionManagementInterface;
