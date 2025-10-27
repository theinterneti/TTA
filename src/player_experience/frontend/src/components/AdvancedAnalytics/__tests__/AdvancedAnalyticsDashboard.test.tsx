/**
 * Advanced Analytics Dashboard Tests - Priority 4B Implementation
 *
 * Comprehensive test suite for the Advanced Analytics Dashboard component including:
 * - Component rendering and state management
 * - Data visualization and chart interactions
 * - Tab navigation and content switching
 * - Error handling and loading states
 * - Integration with predictive analytics services
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import '@testing-library/jest-dom';

import { AdvancedAnalyticsDashboard } from '../AdvancedAnalyticsDashboard';
import { TherapeuticGoal } from '../../../types/index';
import {
  PredictiveAnalyticsResult,
  TrendAnalysis,
  RiskPrediction,
  TherapeuticOutcomePrediction,
  LongitudinalInsight
} from '../../../services/predictiveAnalyticsService';

// Mock the services
jest.mock('../../../services/predictiveAnalyticsService', () => ({
  predictiveAnalyticsService: {
    generatePredictiveAnalytics: jest.fn()
  }
}));

jest.mock('../../../services/progressTrackingService', () => ({
  progressTrackingService: {
    generateProgressAnalytics: jest.fn()
  }
}));

jest.mock('../../../services/realTimeTherapeuticMonitor', () => ({
  realTimeTherapeuticMonitor: {
    getSessionHistory: jest.fn(),
    getEmotionalHistory: jest.fn()
  }
}));

jest.mock('../../../services/personalizedRecommendationEngine', () => ({
  personalizedRecommendationEngine: {
    getRecommendationHistory: jest.fn()
  }
}));

// Mock recharts components
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />
}));

// Mock data
const mockGoals: TherapeuticGoal[] = [
  {
    id: 'goal1',
    title: 'Anxiety Reduction',
    description: 'Reduce anxiety levels through therapeutic interventions',
    category: 'anxiety_reduction',
    progress: 75
  },
  {
    id: 'goal2',
    title: 'Stress Management',
    description: 'Develop effective stress management techniques',
    category: 'stress_management',
    progress: 60
  }
];

const mockTrendAnalysis: TrendAnalysis = {
  trendId: 'trend1',
  goalId: 'goal1',
  trendType: 'improving',
  slope: 0.5,
  correlation: 0.8,
  confidence: 0.85,
  projectedOutcome: 85,
  timeToTarget: 30,
  riskFactors: [],
  recommendations: ['Continue current approach', 'Increase session frequency']
};

const mockRiskPrediction: RiskPrediction = {
  riskId: 'risk1',
  riskType: 'plateau',
  probability: 0.3,
  severity: 'moderate',
  timeframe: 21,
  indicators: [],
  mitigationStrategies: ['Introduce new techniques', 'Adjust goals'],
  confidence: 0.75
};

const mockOutcomePrediction: TherapeuticOutcomePrediction = {
  predictionId: 'prediction1',
  goalId: 'goal1',
  predictedOutcome: 85,
  confidenceInterval: [75, 95],
  timeframe: 30,
  probability: 0.8,
  factors: [],
  alternativeScenarios: []
};

const mockLongitudinalInsight: LongitudinalInsight = {
  insightId: 'insight1',
  insightType: 'pattern',
  description: 'Consistent improvement pattern detected',
  significance: 0.9,
  timespan: 30,
  dataPoints: 15,
  clinicalRelevance: 'high',
  actionable: true,
  recommendations: ['Maintain current approach', 'Consider advanced techniques']
};

const mockAnalyticsResult: PredictiveAnalyticsResult = {
  userId: 'test-user',
  analysisTimestamp: Date.now(),
  trendAnalyses: [mockTrendAnalysis],
  riskPredictions: [mockRiskPrediction],
  outcomePredictions: [mockOutcomePrediction],
  longitudinalInsights: [mockLongitudinalInsight],
  overallPrognosis: {
    score: 78,
    outlook: 'good',
    confidence: 0.82,
    keyFactors: ['Positive progress trends', 'Strong engagement']
  },
  nextAnalysisDate: Date.now() + (24 * 60 * 60 * 1000),
  modelPerformance: {
    accuracy: 0.85,
    precision: 0.82,
    recall: 0.78,
    lastValidated: Date.now() - (7 * 24 * 60 * 60 * 1000)
  }
};

// Create mock store
const createMockStore = () => configureStore({
  reducer: {
    // Add minimal reducers for testing
    test: (state = {}, action) => state
  }
});

describe('AdvancedAnalyticsDashboard', () => {
  let mockStore: ReturnType<typeof createMockStore>;
  let mockPredictiveAnalyticsService: any;
  let mockProgressTrackingService: any;
  let mockRealTimeTherapeuticMonitor: any;
  let mockPersonalizedRecommendationEngine: any;

  beforeEach(() => {
    mockStore = createMockStore();

    // Setup service mocks
    mockPredictiveAnalyticsService = require('../../../services/predictiveAnalyticsService').predictiveAnalyticsService;
    mockProgressTrackingService = require('../../../services/progressTrackingService').progressTrackingService;
    mockRealTimeTherapeuticMonitor = require('../../../services/realTimeTherapeuticMonitor').realTimeTherapeuticMonitor;
    mockPersonalizedRecommendationEngine = require('../../../services/personalizedRecommendationEngine').personalizedRecommendationEngine;

    // Setup default mock implementations
    mockProgressTrackingService.generateProgressAnalytics.mockResolvedValue({
      currentProgress: [],
      recentEntries: [],
      milestones: [],
      outcomeMeasurements: [],
      therapeuticInsights: [],
      overallEffectiveness: 0.8,
      riskAssessment: { overallRisk: 'low', riskFactors: [], protectiveFactors: [], recommendations: [] },
      recommendations: [],
      nextActions: [],
      generatedAt: new Date(),
      dataQuality: { completeness: 0.9, accuracy: 0.85, consistency: 0.8, timeliness: 0.9, issues: [] }
    });

    mockRealTimeTherapeuticMonitor.getSessionHistory.mockReturnValue([]);
    mockRealTimeTherapeuticMonitor.getEmotionalHistory.mockReturnValue([]);
    mockPersonalizedRecommendationEngine.getRecommendationHistory.mockResolvedValue([]);
    mockPredictiveAnalyticsService.generatePredictiveAnalytics.mockResolvedValue(mockAnalyticsResult);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderDashboard = (props = {}) => {
    const defaultProps = {
      userId: 'test-user',
      goals: mockGoals,
      ...props
    };

    return render(
      <Provider store={mockStore}>
        <AdvancedAnalyticsDashboard {...defaultProps} />
      </Provider>
    );
  };

  describe('Component Rendering', () => {
    it('should render loading state initially', () => {
      renderDashboard();
      expect(screen.getByText(/Advanced Analytics Dashboard/)).toBeInTheDocument();
      // Loading state should show animated skeleton
      expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
    });

    it('should render dashboard with analytics data', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Advanced Analytics Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Overall Prognosis')).toBeInTheDocument();
        expect(screen.getByText('GOOD')).toBeInTheDocument();
        expect(screen.getByText('Score: 78/100')).toBeInTheDocument();
      });
    });

    it('should render error state when analytics fail', async () => {
      mockPredictiveAnalyticsService.generatePredictiveAnalytics.mockRejectedValue(
        new Error('Analytics service error')
      );

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Analytics Error')).toBeInTheDocument();
        expect(screen.getByText(/Failed to load analytics data/)).toBeInTheDocument();
        expect(screen.getByText('Retry')).toBeInTheDocument();
      });
    });

    it('should render no data state when no analytics available', async () => {
      mockPredictiveAnalyticsService.generatePredictiveAnalytics.mockResolvedValue(null);

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('No Analytics Data')).toBeInTheDocument();
        expect(screen.getByText(/Complete some therapeutic activities/)).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    it('should render all tab buttons with correct counts', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Trend Analysis')).toBeInTheDocument();
        expect(screen.getByText('Risk Predictions')).toBeInTheDocument();
        expect(screen.getByText('Outcome Predictions')).toBeInTheDocument();
        expect(screen.getByText('Longitudinal Insights')).toBeInTheDocument();

        // Check counts
        expect(screen.getByText('1')).toBeInTheDocument(); // Count badges
      });
    });

    it('should switch between tabs correctly', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Progress Trend Analysis')).toBeInTheDocument();
      });

      // Click on Risk Predictions tab
      fireEvent.click(screen.getByText('Risk Predictions'));
      await waitFor(() => {
        expect(screen.getByText('Risk Assessment Overview')).toBeInTheDocument();
      });

      // Click on Outcome Predictions tab
      fireEvent.click(screen.getByText('Outcome Predictions'));
      await waitFor(() => {
        expect(screen.getByText('Therapeutic Outcome Predictions')).toBeInTheDocument();
      });

      // Click on Longitudinal Insights tab
      fireEvent.click(screen.getByText('Longitudinal Insights'));
      await waitFor(() => {
        expect(screen.getByText('Longitudinal Therapeutic Insights')).toBeInTheDocument();
      });
    });
  });

  describe('Data Visualization', () => {
    it('should render trend analysis charts', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
        expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      });
    });

    it('should render risk prediction charts', async () => {
      renderDashboard();

      // Switch to risk predictions tab
      fireEvent.click(screen.getByText('Risk Predictions'));

      await waitFor(() => {
        expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      });
    });

    it('should render outcome prediction charts', async () => {
      renderDashboard();

      // Switch to outcome predictions tab
      fireEvent.click(screen.getByText('Outcome Predictions'));

      await waitFor(() => {
        expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      });
    });
  });

  describe('Time Range Selection', () => {
    it('should render time range selector', async () => {
      renderDashboard();

      await waitFor(() => {
        const select = screen.getByDisplayValue('Last 30 days');
        expect(select).toBeInTheDocument();
      });
    });

    it('should change time range when selected', async () => {
      renderDashboard();

      await waitFor(() => {
        const select = screen.getByDisplayValue('Last 30 days');
        fireEvent.change(select, { target: { value: '7d' } });
        expect(screen.getByDisplayValue('Last 7 days')).toBeInTheDocument();
      });
    });
  });

  describe('Interactive Features', () => {
    it('should call onInsightClick when insight is clicked', async () => {
      const mockOnInsightClick = jest.fn();
      renderDashboard({ onInsightClick: mockOnInsightClick });

      // Switch to insights tab
      fireEvent.click(screen.getByText('Longitudinal Insights'));

      await waitFor(() => {
        const insightElement = screen.getByText('Consistent improvement pattern detected');
        fireEvent.click(insightElement);
        expect(mockOnInsightClick).toHaveBeenCalledWith(mockLongitudinalInsight);
      });
    });

    it('should call onRiskAlert for critical risks', async () => {
      const mockOnRiskAlert = jest.fn();
      const criticalRiskResult = {
        ...mockAnalyticsResult,
        riskPredictions: [{
          ...mockRiskPrediction,
          severity: 'critical' as const
        }]
      };

      mockPredictiveAnalyticsService.generatePredictiveAnalytics.mockResolvedValue(criticalRiskResult);
      renderDashboard({ onRiskAlert: mockOnRiskAlert });

      await waitFor(() => {
        expect(mockOnRiskAlert).toHaveBeenCalledWith(expect.objectContaining({
          severity: 'critical'
        }));
      });
    });
  });

  describe('Data Integration', () => {
    it('should call all required services to gather data', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(mockProgressTrackingService.generateProgressAnalytics).toHaveBeenCalledWith('test-user', mockGoals);
        expect(mockRealTimeTherapeuticMonitor.getSessionHistory).toHaveBeenCalledWith('test-user');
        expect(mockRealTimeTherapeuticMonitor.getEmotionalHistory).toHaveBeenCalledWith('test-user');
        expect(mockPersonalizedRecommendationEngine.getRecommendationHistory).toHaveBeenCalledWith('test-user');
        expect(mockPredictiveAnalyticsService.generatePredictiveAnalytics).toHaveBeenCalled();
      });
    });

    it('should not load data when userId or goals are missing', () => {
      renderDashboard({ userId: '', goals: [] });

      expect(mockPredictiveAnalyticsService.generatePredictiveAnalytics).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', async () => {
      renderDashboard();

      await waitFor(() => {
        // Check for proper heading structure
        expect(screen.getByRole('heading', { name: /Advanced Analytics Dashboard/ })).toBeInTheDocument();

        // Check for proper button roles
        const tabButtons = screen.getAllByRole('button');
        expect(tabButtons.length).toBeGreaterThan(0);
      });
    });

    it('should support keyboard navigation', async () => {
      renderDashboard();

      await waitFor(() => {
        const firstTab = screen.getByText('Trend Analysis');
        firstTab.focus();
        expect(document.activeElement).toBe(firstTab);
      });
    });
  });
});
