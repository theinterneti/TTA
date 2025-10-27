import React, { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  realTimeTherapeuticMonitor,
  MonitoringSession,
  EmotionalState,
  RiskAssessment,
  MonitoringMetrics,
  InterventionRecord
} from '../../services/realTimeTherapeuticMonitor';

interface RealTimeMonitoringInterfaceProps {
  sessionId: string;
  userId: string;
  therapeuticGoals: string[];
  onInterventionTriggered?: (intervention: InterventionRecord) => void;
  onCrisisDetected?: (riskAssessment: RiskAssessment) => void;
  className?: string;
}

interface MonitoringData {
  emotionalState: EmotionalState | null;
  riskAssessment: RiskAssessment | null;
  metrics: MonitoringMetrics | null;
  interventions: InterventionRecord[];
  isActive: boolean;
}

const RealTimeMonitoringInterface: React.FC<RealTimeMonitoringInterfaceProps> = ({
  sessionId,
  userId,
  therapeuticGoals,
  onInterventionTriggered,
  onCrisisDetected,
  className = ''
}) => {
  const dispatch = useDispatch();
  const [monitoringData, setMonitoringData] = useState<MonitoringData>({
    emotionalState: null,
    riskAssessment: null,
    metrics: null,
    interventions: [],
    isActive: false
  });

  const [isMonitoring, setIsMonitoring] = useState(false);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  // Start monitoring when component mounts
  useEffect(() => {
    startMonitoring();
    return () => {
      stopMonitoring();
    };
  }, [sessionId, userId]);

  const startMonitoring = useCallback(() => {
    try {
      const session = realTimeTherapeuticMonitor.startMonitoring(sessionId, userId, therapeuticGoals);

      // Register callback for real-time updates
      realTimeTherapeuticMonitor.registerCallback(sessionId, handleMonitoringUpdate);

      setIsMonitoring(true);
      setMonitoringData(prev => ({ ...prev, isActive: true }));

      console.log('Real-time therapeutic monitoring started for session:', sessionId);
    } catch (error) {
      console.error('Failed to start monitoring:', error);
    }
  }, [sessionId, userId, therapeuticGoals]);

  const stopMonitoring = useCallback(() => {
    try {
      realTimeTherapeuticMonitor.stopMonitoring(sessionId);
      realTimeTherapeuticMonitor.unregisterCallback(sessionId);

      setIsMonitoring(false);
      setMonitoringData(prev => ({ ...prev, isActive: false }));

      console.log('Real-time therapeutic monitoring stopped for session:', sessionId);
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
    }
  }, [sessionId]);

  const handleMonitoringUpdate = useCallback((data: any) => {
    if (data.emotionalState && data.riskAssessment) {
      // Update emotional state and risk assessment
      setMonitoringData(prev => ({
        ...prev,
        emotionalState: data.emotionalState,
        riskAssessment: data.riskAssessment
      }));

      // Check for crisis situations
      if (data.riskAssessment.riskLevel === 'critical' || data.riskAssessment.riskLevel === 'high') {
        if (alertsEnabled && onCrisisDetected) {
          onCrisisDetected(data.riskAssessment);
        }
      }
    }

    if (data.type === 'intervention_triggered' && data.intervention) {
      // Handle intervention trigger
      setMonitoringData(prev => ({
        ...prev,
        interventions: [...prev.interventions, data.intervention]
      }));

      if (onInterventionTriggered) {
        onInterventionTriggered(data.intervention);
      }
    }

    // Update metrics
    const metrics = realTimeTherapeuticMonitor.getMonitoringMetrics(sessionId);
    if (metrics) {
      setMonitoringData(prev => ({ ...prev, metrics }));
    }
  }, [sessionId, alertsEnabled, onCrisisDetected, onInterventionTriggered]);

  const getRiskLevelColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getEmotionalStateDescription = (emotionalState: EmotionalState): string => {
    const { valence, arousal, dominance } = emotionalState;

    if (valence > 0.3 && arousal < 0.6) return 'Calm and positive';
    if (valence > 0.3 && arousal > 0.6) return 'Excited and energetic';
    if (valence < -0.3 && arousal > 0.6) return 'Anxious or agitated';
    if (valence < -0.3 && arousal < 0.6) return 'Sad or withdrawn';
    if (dominance < 0.3) return 'Feeling powerless';
    if (dominance > 0.7) return 'Feeling in control';

    return 'Neutral emotional state';
  };

  const formatMetricValue = (value: number): string => {
    return `${Math.round(value * 100)}%`;
  };

  if (!isMonitoring) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <div className="text-center text-gray-500">
          <div className="w-8 h-8 mx-auto mb-2 bg-gray-300 rounded-full flex items-center justify-center">
            <span className="text-sm">⏸️</span>
          </div>
          <p className="text-sm">Therapeutic monitoring not active</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <h3 className="font-medium text-gray-900">Real-Time Monitoring</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setAlertsEnabled(!alertsEnabled)}
              className={`px-2 py-1 text-xs rounded ${
                alertsEnabled
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-500'
              }`}
              title={alertsEnabled ? 'Alerts enabled' : 'Alerts disabled'}
            >
              🔔
            </button>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              {showDetails ? 'Hide' : 'Details'}
            </button>
          </div>
        </div>
      </div>

      {/* Current Status */}
      <div className="p-4">
        {monitoringData.riskAssessment && (
          <div className={`mb-4 p-3 rounded-lg border ${getRiskLevelColor(monitoringData.riskAssessment.riskLevel)}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Risk Level: {monitoringData.riskAssessment.riskLevel.toUpperCase()}</span>
              <span className="text-sm">
                Score: {Math.round(monitoringData.riskAssessment.riskScore * 100)}%
              </span>
            </div>
            {monitoringData.riskAssessment.riskLevel !== 'low' && (
              <div className="text-sm">
                <p className="mb-1">Risk factors detected:</p>
                <ul className="list-disc list-inside space-y-1">
                  {monitoringData.riskAssessment.riskFactors.slice(0, 3).map((factor, index) => (
                    <li key={index} className="text-xs">
                      {factor.description} ({factor.severity})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {monitoringData.emotionalState && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-blue-900">Emotional State</span>
              <span className="text-sm text-blue-700">
                Confidence: {Math.round(monitoringData.emotionalState.confidence * 100)}%
              </span>
            </div>
            <p className="text-sm text-blue-800 mb-2">
              {getEmotionalStateDescription(monitoringData.emotionalState)}
            </p>
            {showDetails && (
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <div className="font-medium">Valence</div>
                  <div className={monitoringData.emotionalState.valence >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {monitoringData.emotionalState.valence.toFixed(2)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">Arousal</div>
                  <div className="text-blue-600">
                    {monitoringData.emotionalState.arousal.toFixed(2)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">Dominance</div>
                  <div className="text-purple-600">
                    {monitoringData.emotionalState.dominance.toFixed(2)}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Metrics Dashboard */}
        {monitoringData.metrics && (
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="p-2 bg-green-50 rounded border border-green-200">
              <div className="text-xs text-green-700 font-medium">Emotional Stability</div>
              <div className="text-lg font-bold text-green-800">
                {formatMetricValue(monitoringData.metrics.emotionalStability)}
              </div>
            </div>
            <div className="p-2 bg-blue-50 rounded border border-blue-200">
              <div className="text-xs text-blue-700 font-medium">Engagement Level</div>
              <div className="text-lg font-bold text-blue-800">
                {formatMetricValue(monitoringData.metrics.engagementLevel)}
              </div>
            </div>
            <div className="p-2 bg-purple-50 rounded border border-purple-200">
              <div className="text-xs text-purple-700 font-medium">Therapeutic Progress</div>
              <div className="text-lg font-bold text-purple-800">
                {formatMetricValue(monitoringData.metrics.therapeuticProgress)}
              </div>
            </div>
            <div className="p-2 bg-orange-50 rounded border border-orange-200">
              <div className="text-xs text-orange-700 font-medium">Session Quality</div>
              <div className="text-lg font-bold text-orange-800">
                {formatMetricValue(monitoringData.metrics.sessionQuality)}
              </div>
            </div>
          </div>
        )}

        {/* Active Interventions */}
        {monitoringData.interventions.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-gray-900 mb-2">Active Interventions</h4>
            <div className="space-y-2">
              {monitoringData.interventions.slice(-3).map((intervention, index) => (
                <div key={intervention.interventionId} className="p-2 bg-yellow-50 rounded border border-yellow-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-yellow-800">
                      {intervention.intervention}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      intervention.outcome === 'successful' ? 'bg-green-100 text-green-700' :
                      intervention.outcome === 'pending' ? 'bg-gray-100 text-gray-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {intervention.outcome}
                    </span>
                  </div>
                  <div className="text-xs text-yellow-700 mt-1">
                    {new Date(intervention.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Information */}
        {showDetails && monitoringData.emotionalState && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Detailed Analysis</h4>
            <div className="text-sm text-gray-700 space-y-1">
              {monitoringData.emotionalState.indicators.length > 0 && (
                <div>
                  <span className="font-medium">Emotional Indicators: </span>
                  {monitoringData.emotionalState.indicators.join(', ')}
                </div>
              )}
              <div>
                <span className="font-medium">Last Updated: </span>
                {new Date(monitoringData.emotionalState.timestamp).toLocaleString()}
              </div>
              {monitoringData.riskAssessment && monitoringData.riskAssessment.protectiveFactors.length > 0 && (
                <div>
                  <span className="font-medium">Protective Factors: </span>
                  {monitoringData.riskAssessment.protectiveFactors.join(', ')}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 rounded-b-lg border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Session: {sessionId.slice(-8)}</span>
          <span>Monitoring active since {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitoringInterface;
