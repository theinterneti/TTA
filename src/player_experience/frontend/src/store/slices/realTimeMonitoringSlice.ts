// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Slices/Realtimemonitoringslice]]
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import {
  EmotionalState,
  RiskAssessment,
  MonitoringMetrics,
  InterventionRecord,
  MonitoringSession
} from '../../services/realTimeTherapeuticMonitor';

export interface RealTimeMonitoringState {
  // Current monitoring session
  currentSession: MonitoringSession | null;
  isMonitoring: boolean;

  // Real-time data
  currentEmotionalState: EmotionalState | null;
  currentRiskAssessment: RiskAssessment | null;
  currentMetrics: MonitoringMetrics | null;

  // Historical data
  emotionalStateHistory: EmotionalState[];
  riskAssessmentHistory: RiskAssessment[];
  interventionHistory: InterventionRecord[];

  // Alerts and notifications
  activeAlerts: Alert[];
  alertsEnabled: boolean;

  // Settings
  monitoringSettings: MonitoringSettings;

  // UI state
  showMonitoringInterface: boolean;
  showDetailedView: boolean;

  // Error handling
  error: string | null;
  lastUpdated: number | null;
}

export interface Alert {
  id: string;
  type: 'crisis' | 'intervention' | 'warning' | 'info';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  timestamp: number;
  acknowledged: boolean;
  actionRequired: boolean;
  relatedData?: any;
}

export interface MonitoringSettings {
  enableRealTimeAnalysis: boolean;
  enableCrisisDetection: boolean;
  enableInterventionTriggers: boolean;
  riskThresholds: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  alertSettings: {
    enableAudioAlerts: boolean;
    enableVisualAlerts: boolean;
    enablePushNotifications: boolean;
  };
  dataRetention: {
    emotionalStateHistoryLimit: number;
    riskAssessmentHistoryLimit: number;
    interventionHistoryLimit: number;
  };
}

const initialState: RealTimeMonitoringState = {
  currentSession: null,
  isMonitoring: false,

  currentEmotionalState: null,
  currentRiskAssessment: null,
  currentMetrics: null,

  emotionalStateHistory: [],
  riskAssessmentHistory: [],
  interventionHistory: [],

  activeAlerts: [],
  alertsEnabled: true,

  monitoringSettings: {
    enableRealTimeAnalysis: true,
    enableCrisisDetection: true,
    enableInterventionTriggers: true,
    riskThresholds: {
      low: 0.25,
      moderate: 0.5,
      high: 0.75,
      critical: 0.9
    },
    alertSettings: {
      enableAudioAlerts: true,
      enableVisualAlerts: true,
      enablePushNotifications: false
    },
    dataRetention: {
      emotionalStateHistoryLimit: 100,
      riskAssessmentHistoryLimit: 50,
      interventionHistoryLimit: 25
    }
  },

  showMonitoringInterface: false,
  showDetailedView: false,

  error: null,
  lastUpdated: null
};

const realTimeMonitoringSlice = createSlice({
  name: 'realTimeMonitoring',
  initialState,
  reducers: {
    // Session management
    startMonitoringSession: (state, action: PayloadAction<MonitoringSession>) => {
      state.currentSession = action.payload;
      state.isMonitoring = true;
      state.error = null;
      state.lastUpdated = Date.now();
    },

    stopMonitoringSession: (state) => {
      state.currentSession = null;
      state.isMonitoring = false;
      state.currentEmotionalState = null;
      state.currentRiskAssessment = null;
      state.currentMetrics = null;
      state.lastUpdated = Date.now();
    },

    // Real-time data updates
    updateEmotionalState: (state, action: PayloadAction<EmotionalState>) => {
      state.currentEmotionalState = action.payload;

      // Add to history with limit
      state.emotionalStateHistory.push(action.payload);
      if (state.emotionalStateHistory.length > state.monitoringSettings.dataRetention.emotionalStateHistoryLimit) {
        state.emotionalStateHistory.shift();
      }

      state.lastUpdated = Date.now();
    },

    updateRiskAssessment: (state, action: PayloadAction<RiskAssessment>) => {
      state.currentRiskAssessment = action.payload;

      // Add to history with limit
      state.riskAssessmentHistory.push(action.payload);
      if (state.riskAssessmentHistory.length > state.monitoringSettings.dataRetention.riskAssessmentHistoryLimit) {
        state.riskAssessmentHistory.shift();
      }

      // Generate alerts for high-risk situations
      if (action.payload.riskLevel === 'high' || action.payload.riskLevel === 'critical') {
        const alert: Alert = {
          id: `risk_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: action.payload.riskLevel === 'critical' ? 'crisis' : 'warning',
          severity: action.payload.riskLevel as Alert['severity'],
          title: `${action.payload.riskLevel.toUpperCase()} Risk Detected`,
          message: `Risk score: ${Math.round(action.payload.riskScore * 100)}%. ${action.payload.riskFactors.length} risk factors identified.`,
          timestamp: Date.now(),
          acknowledged: false,
          actionRequired: action.payload.riskLevel === 'critical',
          relatedData: action.payload
        };
        state.activeAlerts.push(alert);
      }

      state.lastUpdated = Date.now();
    },

    updateMetrics: (state, action: PayloadAction<MonitoringMetrics>) => {
      state.currentMetrics = action.payload;
      state.lastUpdated = Date.now();
    },

    // Intervention management
    addIntervention: (state, action: PayloadAction<InterventionRecord>) => {
      state.interventionHistory.push(action.payload);

      // Limit history size
      if (state.interventionHistory.length > state.monitoringSettings.dataRetention.interventionHistoryLimit) {
        state.interventionHistory.shift();
      }

      // Generate intervention alert
      const alert: Alert = {
        id: `intervention_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'intervention',
        severity: action.payload.type === 'immediate' ? 'high' : 'medium',
        title: 'Intervention Triggered',
        message: action.payload.intervention,
        timestamp: Date.now(),
        acknowledged: false,
        actionRequired: action.payload.followUpRequired,
        relatedData: action.payload
      };
      state.activeAlerts.push(alert);

      state.lastUpdated = Date.now();
    },

    updateInterventionOutcome: (state, action: PayloadAction<{ interventionId: string; outcome: InterventionRecord['outcome']; userResponse?: string }>) => {
      const intervention = state.interventionHistory.find(i => i.interventionId === action.payload.interventionId);
      if (intervention) {
        intervention.outcome = action.payload.outcome;
        if (action.payload.userResponse) {
          intervention.userResponse = action.payload.userResponse;
        }
        intervention.followUpRequired = action.payload.outcome !== 'successful';
      }
      state.lastUpdated = Date.now();
    },

    // Alert management
    acknowledgeAlert: (state, action: PayloadAction<string>) => {
      const alert = state.activeAlerts.find(a => a.id === action.payload);
      if (alert) {
        alert.acknowledged = true;
      }
    },

    dismissAlert: (state, action: PayloadAction<string>) => {
      state.activeAlerts = state.activeAlerts.filter(a => a.id !== action.payload);
    },

    clearAllAlerts: (state) => {
      state.activeAlerts = [];
    },

    toggleAlerts: (state) => {
      state.alertsEnabled = !state.alertsEnabled;
    },

    // Settings management
    updateMonitoringSettings: (state, action: PayloadAction<Partial<MonitoringSettings>>) => {
      state.monitoringSettings = { ...state.monitoringSettings, ...action.payload };
    },

    updateRiskThresholds: (state, action: PayloadAction<MonitoringSettings['riskThresholds']>) => {
      state.monitoringSettings.riskThresholds = action.payload;
    },

    updateAlertSettings: (state, action: PayloadAction<MonitoringSettings['alertSettings']>) => {
      state.monitoringSettings.alertSettings = action.payload;
    },

    // UI state management
    toggleMonitoringInterface: (state) => {
      state.showMonitoringInterface = !state.showMonitoringInterface;
    },

    setShowMonitoringInterface: (state, action: PayloadAction<boolean>) => {
      state.showMonitoringInterface = action.payload;
    },

    toggleDetailedView: (state) => {
      state.showDetailedView = !state.showDetailedView;
    },

    setShowDetailedView: (state, action: PayloadAction<boolean>) => {
      state.showDetailedView = action.payload;
    },

    // Error handling
    setMonitoringError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.lastUpdated = Date.now();
    },

    clearMonitoringError: (state) => {
      state.error = null;
    },

    // Data management
    clearHistoricalData: (state) => {
      state.emotionalStateHistory = [];
      state.riskAssessmentHistory = [];
      state.interventionHistory = [];
      state.activeAlerts = [];
    },

    // Bulk data update (for initialization or sync)
    updateMonitoringData: (state, action: PayloadAction<{
      emotionalState?: EmotionalState;
      riskAssessment?: RiskAssessment;
      metrics?: MonitoringMetrics;
      interventions?: InterventionRecord[];
    }>) => {
      const { emotionalState, riskAssessment, metrics, interventions } = action.payload;

      if (emotionalState) {
        state.currentEmotionalState = emotionalState;
        state.emotionalStateHistory.push(emotionalState);
      }

      if (riskAssessment) {
        state.currentRiskAssessment = riskAssessment;
        state.riskAssessmentHistory.push(riskAssessment);
      }

      if (metrics) {
        state.currentMetrics = metrics;
      }

      if (interventions) {
        state.interventionHistory.push(...interventions);
      }

      state.lastUpdated = Date.now();
    }
  }
});

export const {
  startMonitoringSession,
  stopMonitoringSession,
  updateEmotionalState,
  updateRiskAssessment,
  updateMetrics,
  addIntervention,
  updateInterventionOutcome,
  acknowledgeAlert,
  dismissAlert,
  clearAllAlerts,
  toggleAlerts,
  updateMonitoringSettings,
  updateRiskThresholds,
  updateAlertSettings,
  toggleMonitoringInterface,
  setShowMonitoringInterface,
  toggleDetailedView,
  setShowDetailedView,
  setMonitoringError,
  clearMonitoringError,
  clearHistoricalData,
  updateMonitoringData
} = realTimeMonitoringSlice.actions;

export default realTimeMonitoringSlice.reducer;
