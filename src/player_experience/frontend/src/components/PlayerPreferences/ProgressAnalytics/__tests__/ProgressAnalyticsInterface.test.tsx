/**
 * Progress Analytics Interface Tests - Priority 3D Implementation
 *
 * Comprehensive test suite for the progress analytics interface component.
 * Tests progress visualization, outcome display, and therapeutic insights.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ProgressAnalyticsInterface from '../ProgressAnalyticsInterface';
import {
  ProgressTrackingResult,
  ProgressAnalytics,
  OutcomeMeasurement,
  TherapeuticInsight,
  RiskAssessment,
  ProgressRecommendation,
  NextAction,
  DataQualityMetrics,
  ProgressTrend,
  SeverityLevel,
  ClinicalSignificance,
  TrendDirection,
  InsightType,
  ClinicalRelevance,
  ConfidenceLevel,
  OutcomeMeasurementType,
  EvidenceLevel
} from '../../../../services/progressTrackingService';

describe('ProgressAnalyticsInterface', () => {
  let mockProgressResult: ProgressTrackingResult;
  let mockProps: any;

  beforeEach(() => {
    // Create comprehensive mock data
    const mockProgressAnalytics: ProgressAnalytics[] = [
      {
        goalId: 'goal-1',
        overallProgress: 75,
        progressTrend: ProgressTrend.IMPROVING,
        velocityScore: 85,
        consistencyScore: 90,
        therapeuticEffectiveness: 82,
        riskFactors: [],
        recommendations: [
          {
            id: 'rec-1',
            type: 'acceleration',
            title: 'Consider Advanced Techniques',
            description: 'Your progress is excellent. Consider exploring more advanced therapeutic techniques.',
            priority: 'medium',
            actionable: true
          }
        ],
        insights: [
          {
            id: 'insight-1',
            type: InsightType.PROGRESS_PATTERN,
            title: 'Excellent Consistency',
            description: 'You maintain very consistent progress tracking.',
            confidence: ConfidenceLevel.HIGH
          }
        ]
      },
      {
        goalId: 'goal-2',
        overallProgress: 45,
        progressTrend: ProgressTrend.STABLE,
        velocityScore: 40,
        consistencyScore: 60,
        therapeuticEffectiveness: 55,
        riskFactors: [
          {
            type: 'low_progress',
            severity: SeverityLevel.MILD,
            description: 'Progress has been slower than expected',
            recommendations: ['Consider adjusting approach', 'Increase support']
          }
        ],
        recommendations: [],
        insights: []
      }
    ];

    const mockOutcomeMeasurements: OutcomeMeasurement[] = [
      {
        id: 'outcome-1',
        userId: 'user-1',
        measurementType: OutcomeMeasurementType.PHQ9,
        score: 8,
        maxScore: 27,
        severity: SeverityLevel.MILD,
        timestamp: new Date('2024-01-15'),
        clinicalSignificance: ClinicalSignificance.CLINICALLY_MEANINGFUL,
        trendDirection: TrendDirection.IMPROVING
      },
      {
        id: 'outcome-2',
        userId: 'user-1',
        measurementType: OutcomeMeasurementType.GAD7,
        score: 5,
        maxScore: 21,
        severity: SeverityLevel.MINIMAL,
        timestamp: new Date('2024-01-10'),
        clinicalSignificance: ClinicalSignificance.NOT_SIGNIFICANT,
        trendDirection: TrendDirection.STABLE
      }
    ];

    const mockTherapeuticInsights: TherapeuticInsight[] = [
      {
        id: 'insight-1',
        type: InsightType.THERAPEUTIC_EFFECTIVENESS,
        title: 'Strong Therapeutic Progress',
        description: 'Your overall therapeutic effectiveness is excellent across multiple goals.',
        confidence: ConfidenceLevel.HIGH,
        evidenceLevel: EvidenceLevel.VALIDATED_SCALE,
        actionable: true,
        recommendations: ['Continue current approaches', 'Consider sharing strategies'],
        clinicalRelevance: ClinicalRelevance.HIGH,
        generatedAt: new Date('2024-01-15')
      }
    ];

    const mockRiskAssessment: RiskAssessment = {
      overallRisk: SeverityLevel.MINIMAL,
      riskFactors: [
        {
          type: 'inconsistent_engagement',
          severity: SeverityLevel.MILD,
          description: 'Irregular progress tracking patterns detected',
          recommendations: ['Establish regular check-in schedule']
        }
      ],
      protectiveFactors: ['Regular progress tracking', 'Multiple therapeutic goals'],
      recommendations: ['Continue monitoring progress', 'Maintain current protective factors']
    };

    const mockDataQuality: DataQualityMetrics = {
      completeness: 85,
      consistency: 78,
      recency: 92,
      reliability: 88,
      overallQuality: 86
    };

    mockProgressResult = {
      currentProgress: mockProgressAnalytics,
      recentEntries: [
        {
          id: 'entry-1',
          goalId: 'goal-1',
          userId: 'user-1',
          timestamp: new Date('2024-01-15'),
          progressValue: 75,
          progressType: 'self_reported' as any,
          measurementMethod: 'likert_scale' as any,
          notes: 'Feeling more confident',
          evidenceLevel: EvidenceLevel.OBSERVATIONAL
        }
      ],
      milestones: [
        {
          id: 'milestone-1',
          goalId: 'goal-1',
          title: 'First Major Milestone',
          description: 'Achieved significant progress in anxiety management',
          targetValue: 50,
          achievedAt: new Date('2024-01-10'),
          significance: 'major' as any,
          therapeuticImpact: 'high' as any,
          celebrationMessage: 'Congratulations on this achievement!',
          nextSteps: ['Continue current approach', 'Set next milestone']
        }
      ],
      outcomeMeasurements: mockOutcomeMeasurements,
      therapeuticInsights: mockTherapeuticInsights,
      overallEffectiveness: 78,
      riskAssessment: mockRiskAssessment,
      recommendations: [
        {
          id: 'rec-1',
          type: 'motivation',
          title: 'Boost Engagement',
          description: 'Try varying your approach or setting smaller milestones.',
          priority: 'high',
          actionable: true
        }
      ],
      nextActions: [
        {
          id: 'action-1',
          title: 'Review Progress Patterns',
          description: 'Analyze recent progress trends and adjust strategies',
          priority: 'medium',
          category: 'analysis'
        }
      ],
      generatedAt: new Date('2024-01-15T10:00:00Z'),
      dataQuality: mockDataQuality
    };

    mockProps = {
      progressResult: mockProgressResult,
      onRecordProgress: jest.fn(),
      onRecordOutcome: jest.fn(),
      onAcceptRecommendation: jest.fn(),
      onDismissRecommendation: jest.fn(),
      onScheduleAction: jest.fn(),
      onRequestDetailedInsight: jest.fn()
    };
  });

  describe('Component Rendering', () => {
    it('should render the progress analytics interface', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByText('Progress Analytics')).toBeInTheDocument();
      expect(screen.getByText('Data Quality:')).toBeInTheDocument();
      expect(screen.getByText('86%')).toBeInTheDocument(); // Data quality score
    });

    it('should render navigation tabs', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /detailed analysis/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /therapeutic insights/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /recommendations/i })).toBeInTheDocument();
    });

    it('should show overview panel by default', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByText('Overall Effectiveness')).toBeInTheDocument();
      expect(screen.getByText('78%')).toBeInTheDocument(); // Overall effectiveness score
      expect(screen.getByText('Risk Level')).toBeInTheDocument();
      expect(screen.getByText('Active Goals')).toBeInTheDocument();
    });
  });

  describe('Overview Panel', () => {
    it('should display key metrics cards', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      // Overall Effectiveness Card
      expect(screen.getByText('Overall Effectiveness')).toBeInTheDocument();
      expect(screen.getByText('78%')).toBeInTheDocument();
      expect(screen.getByText('Good therapeutic progress')).toBeInTheDocument();

      // Risk Level Card
      expect(screen.getByText('Risk Level')).toBeInTheDocument();
      expect(screen.getByText('minimal')).toBeInTheDocument();

      // Active Goals Card
      expect(screen.getByText('Active Goals')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument(); // Number of goals
    });

    it('should display goal progress summary', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByText('Goal Progress Summary')).toBeInTheDocument();
      expect(screen.getByText('Goal goal-1')).toBeInTheDocument();
      expect(screen.getByText('Goal goal-2')).toBeInTheDocument();
      expect(screen.getByText('75% complete • improving trend')).toBeInTheDocument();
      expect(screen.getByText('45% complete • stable trend')).toBeInTheDocument();
    });

    it('should expand goal details when clicked', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const goalCard = screen.getByText('Goal goal-1').closest('div');
      expect(goalCard).toBeInTheDocument();

      await user.click(goalCard!);

      expect(screen.getByText('Velocity:')).toBeInTheDocument();
      expect(screen.getByText('Consistency:')).toBeInTheDocument();
      expect(screen.getByText('Risk Factors:')).toBeInTheDocument();
      expect(screen.getByText('Recommendations:')).toBeInTheDocument();
    });

    it('should show/hide risk details when clicked', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const viewRiskButton = screen.getByText('View risk factors');
      await user.click(viewRiskButton);

      expect(screen.getByText('Risk Assessment Details')).toBeInTheDocument();
      expect(screen.getByText('Irregular progress tracking patterns detected')).toBeInTheDocument();

      const hideRiskButton = screen.getByText('Hide details');
      await user.click(hideRiskButton);

      expect(screen.queryByText('Risk Assessment Details')).not.toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch to detailed analysis tab', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const detailedTab = screen.getByRole('tab', { name: /detailed analysis/i });
      await user.click(detailedTab);

      expect(screen.getByText('Clinical Outcome Measurements')).toBeInTheDocument();
      expect(screen.getByText('Data Quality Metrics')).toBeInTheDocument();
      expect(screen.getByText('Recent Progress Entries')).toBeInTheDocument();
    });

    it('should switch to insights tab', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const insightsTab = screen.getByRole('tab', { name: /therapeutic insights/i });
      await user.click(insightsTab);

      expect(screen.getByText('Strong Therapeutic Progress')).toBeInTheDocument();
    });

    it('should switch to recommendations tab', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const recommendationsTab = screen.getByRole('tab', { name: /recommendations/i });
      await user.click(recommendationsTab);

      expect(screen.getByText('Progress Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Suggested Next Actions')).toBeInTheDocument();
    });
  });

  describe('Detailed Analysis Panel', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const detailedTab = screen.getByRole('tab', { name: /detailed analysis/i });
      await user.click(detailedTab);
    });

    it('should display outcome measurements', () => {
      expect(screen.getByText('Clinical Outcome Measurements')).toBeInTheDocument();
      expect(screen.getByText('PHQ9')).toBeInTheDocument();
      expect(screen.getByText('GAD7')).toBeInTheDocument();
      expect(screen.getByText('8/27 • mild')).toBeInTheDocument();
      expect(screen.getByText('5/21 • minimal')).toBeInTheDocument();
    });

    it('should display data quality metrics', () => {
      expect(screen.getByText('Data Quality Metrics')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument(); // Completeness
      expect(screen.getByText('78%')).toBeInTheDocument(); // Consistency
      expect(screen.getByText('92%')).toBeInTheDocument(); // Recency
      expect(screen.getByText('88%')).toBeInTheDocument(); // Reliability
    });

    it('should display recent progress entries', () => {
      expect(screen.getByText('Recent Progress Entries')).toBeInTheDocument();
      expect(screen.getByText('Goal goal-1')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
      expect(screen.getByText('Feeling more confident')).toBeInTheDocument();
    });

    it('should handle empty outcome measurements', async () => {
      const emptyProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          outcomeMeasurements: []
        }
      };

      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...emptyProps} />);

      const detailedTabs = screen.getAllByRole('tab', { name: /detailed analysis/i });
      await user.click(detailedTabs[0]);

      expect(screen.getByText('No outcome measurements recorded yet.')).toBeInTheDocument();
      expect(screen.getByText('Record your first measurement')).toBeInTheDocument();
    });
  });

  describe('Therapeutic Insights Panel', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const insightsTab = screen.getByRole('tab', { name: /therapeutic insights/i });
      await user.click(insightsTab);
    });

    it('should display therapeutic insights', () => {
      expect(screen.getByText('Strong Therapeutic Progress')).toBeInTheDocument();
      expect(screen.getByText('high confidence')).toBeInTheDocument();
    });

    it('should expand/collapse insight details', async () => {
      const user = userEvent.setup();

      const moreButton = screen.getByText('More');
      await user.click(moreButton);

      expect(screen.getByText('Clinical Relevance:')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
      expect(screen.getByText('Recommendations:')).toBeInTheDocument();

      const lessButton = screen.getByText('Less');
      await user.click(lessButton);

      expect(screen.queryByText('Clinical Relevance:')).not.toBeInTheDocument();
    });

    it('should handle actionable insights', async () => {
      const user = userEvent.setup();

      const actButton = screen.getByText('Act on This');
      await user.click(actButton);

      expect(mockProps.onRequestDetailedInsight).toHaveBeenCalledWith('insight-1');
    });

    it('should handle empty insights', async () => {
      const emptyProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          therapeuticInsights: []
        }
      };

      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...emptyProps} />);

      const insightsTabs = screen.getAllByRole('tab', { name: /therapeutic insights/i });
      await user.click(insightsTabs[0]);

      expect(screen.getByText('No insights available yet')).toBeInTheDocument();
      expect(screen.getByText('Continue tracking your progress to generate therapeutic insights.')).toBeInTheDocument();
    });
  });

  describe('Recommendations Panel', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const recommendationsTab = screen.getByRole('tab', { name: /recommendations/i });
      await user.click(recommendationsTab);
    });

    it('should display progress recommendations', () => {
      expect(screen.getByText('Progress Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Boost Engagement')).toBeInTheDocument();
      expect(screen.getByText('high priority')).toBeInTheDocument();
    });

    it('should handle recommendation actions', async () => {
      const user = userEvent.setup();

      const acceptButton = screen.getByText('Accept');
      await user.click(acceptButton);

      expect(mockProps.onAcceptRecommendation).toHaveBeenCalledWith('rec-1');

      const dismissButton = screen.getByText('Dismiss');
      await user.click(dismissButton);

      expect(mockProps.onDismissRecommendation).toHaveBeenCalledWith('rec-1');
    });

    it('should display next actions', () => {
      expect(screen.getByText('Suggested Next Actions')).toBeInTheDocument();
      expect(screen.getByText('Review Progress Patterns')).toBeInTheDocument();
      expect(screen.getByText('medium')).toBeInTheDocument();
    });

    it('should handle action scheduling', async () => {
      const user = userEvent.setup();

      const scheduleButton = screen.getByText('Schedule');
      await user.click(scheduleButton);

      expect(mockProps.onScheduleAction).toHaveBeenCalledWith('action-1', expect.any(Date));
    });
  });

  describe('Data Quality Indicators', () => {
    it('should show high quality indicator for good data', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const dataQualityBadge = screen.getByText('86%');
      expect(dataQualityBadge).toHaveClass('bg-green-100', 'text-green-800');
    });

    it('should show medium quality indicator for moderate data', () => {
      const moderateQualityProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          dataQuality: {
            ...mockProgressResult.dataQuality,
            overallQuality: 65
          }
        }
      };

      render(<ProgressAnalyticsInterface {...moderateQualityProps} />);

      const dataQualityBadge = screen.getByText('65%');
      expect(dataQualityBadge).toHaveClass('bg-yellow-100', 'text-yellow-800');
    });

    it('should show low quality indicator for poor data', () => {
      const lowQualityProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          dataQuality: {
            ...mockProgressResult.dataQuality,
            overallQuality: 45
          }
        }
      };

      render(<ProgressAnalyticsInterface {...lowQualityProps} />);

      const dataQualityBadge = screen.getByText('45%');
      expect(dataQualityBadge).toHaveClass('bg-red-100', 'text-red-800');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getAllByRole('tab')).toHaveLength(4);
      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
    });

    it('should have proper tab navigation', async () => {
      const user = userEvent.setup();
      render(<ProgressAnalyticsInterface {...mockProps} />);

      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      const detailedTab = screen.getByRole('tab', { name: /detailed analysis/i });

      expect(overviewTab).toHaveAttribute('aria-selected', 'true');
      expect(detailedTab).toHaveAttribute('aria-selected', 'false');

      await user.click(detailedTab);

      expect(overviewTab).toHaveAttribute('aria-selected', 'false');
      expect(detailedTab).toHaveAttribute('aria-selected', 'true');
    });

    it('should have descriptive button labels', () => {
      render(<ProgressAnalyticsInterface {...mockProps} />);

      expect(screen.getByText('View risk factors')).toBeInTheDocument();

      // Switch to recommendations tab to test action buttons
      const recommendationsTab = screen.getByRole('tab', { name: /recommendations/i });
      fireEvent.click(recommendationsTab);

      expect(screen.getByText('Accept')).toBeInTheDocument();
      expect(screen.getByText('Dismiss')).toBeInTheDocument();
      expect(screen.getByText('Schedule')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty progress data gracefully', () => {
      const emptyProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          currentProgress: [],
          recentEntries: [],
          recommendations: [],
          nextActions: [],
          therapeuticInsights: []
        }
      };

      render(<ProgressAnalyticsInterface {...emptyProps} />);

      expect(screen.getByText('0')).toBeInTheDocument(); // Active goals count
    });

    it('should handle missing optional data', () => {
      const minimalProps = {
        ...mockProps,
        progressResult: {
          ...mockProgressResult,
          milestones: [],
          outcomeMeasurements: [],
          therapeuticInsights: []
        }
      };

      render(<ProgressAnalyticsInterface {...minimalProps} />);

      expect(screen.getByText('Progress Analytics')).toBeInTheDocument();
    });
  });
});
