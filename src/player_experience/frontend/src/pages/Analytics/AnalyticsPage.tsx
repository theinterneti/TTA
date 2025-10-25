/**
 * Analytics Page - Phase 2 Implementation
 *
 * Main page for displaying advanced analytics dashboard
 * Integrates AdvancedAnalyticsDashboard with real API data
 */

import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store/store';
import { AdvancedAnalyticsDashboard } from '../../components/AdvancedAnalytics/AdvancedAnalyticsDashboard';
import { TherapeuticGoal } from '../../types/index';
import { RiskPrediction, LongitudinalInsight } from '../../services/predictiveAnalyticsService';

const AnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const { profile } = useSelector((state: RootState) => state.player);
  const [goals, setGoals] = useState<TherapeuticGoal[]>([]);
  const [loading, setLoading] = useState(true);

  // Initialize default therapeutic goals if none exist
  useEffect(() => {
    const initializeGoals = () => {
      if (profile?.player_id) {
        // Create default therapeutic goals based on user preferences
        const defaultGoals: TherapeuticGoal[] = [
          {
            id: 'emotional-regulation',
            title: 'Emotional Regulation',
            description: 'Develop skills to manage and regulate emotions effectively',
            category: 'emotional_wellness',
            targetValue: 100,
            currentValue: 0,
            priority: 'high',
            createdAt: new Date(),
            updatedAt: new Date(),
            isActive: true,
            milestones: [
              {
                id: 'er-milestone-1',
                title: 'Recognize Emotional Triggers',
                description: 'Identify personal emotional triggers and patterns',
                targetValue: 25,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'er-milestone-2',
                title: 'Practice Coping Strategies',
                description: 'Learn and practice healthy coping mechanisms',
                targetValue: 50,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'er-milestone-3',
                title: 'Apply Skills in Daily Life',
                description: 'Successfully apply emotional regulation skills in real situations',
                targetValue: 75,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'er-milestone-4',
                title: 'Maintain Emotional Balance',
                description: 'Consistently maintain emotional balance and well-being',
                targetValue: 100,
                isCompleted: false,
                completedAt: null
              }
            ]
          },
          {
            id: 'social-skills',
            title: 'Social Skills Development',
            description: 'Improve communication and interpersonal relationship skills',
            category: 'social_wellness',
            targetValue: 100,
            currentValue: 0,
            priority: 'medium',
            createdAt: new Date(),
            updatedAt: new Date(),
            isActive: true,
            milestones: [
              {
                id: 'ss-milestone-1',
                title: 'Active Listening',
                description: 'Develop active listening skills in conversations',
                targetValue: 25,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'ss-milestone-2',
                title: 'Assertive Communication',
                description: 'Practice assertive communication techniques',
                targetValue: 50,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'ss-milestone-3',
                title: 'Conflict Resolution',
                description: 'Learn healthy conflict resolution strategies',
                targetValue: 75,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'ss-milestone-4',
                title: 'Build Meaningful Relationships',
                description: 'Establish and maintain healthy relationships',
                targetValue: 100,
                isCompleted: false,
                completedAt: null
              }
            ]
          },
          {
            id: 'stress-management',
            title: 'Stress Management',
            description: 'Develop effective strategies for managing stress and anxiety',
            category: 'mental_wellness',
            targetValue: 100,
            currentValue: 0,
            priority: 'high',
            createdAt: new Date(),
            updatedAt: new Date(),
            isActive: true,
            milestones: [
              {
                id: 'sm-milestone-1',
                title: 'Identify Stress Sources',
                description: 'Recognize personal stress triggers and sources',
                targetValue: 25,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'sm-milestone-2',
                title: 'Relaxation Techniques',
                description: 'Learn and practice relaxation and mindfulness techniques',
                targetValue: 50,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'sm-milestone-3',
                title: 'Stress Prevention',
                description: 'Implement proactive stress prevention strategies',
                targetValue: 75,
                isCompleted: false,
                completedAt: null
              },
              {
                id: 'sm-milestone-4',
                title: 'Maintain Balance',
                description: 'Maintain healthy work-life balance and stress levels',
                targetValue: 100,
                isCompleted: false,
                completedAt: null
              }
            ]
          }
        ];

        setGoals(defaultGoals);
      }
      setLoading(false);
    };

    initializeGoals();
  }, [profile?.player_id]);

  const handleInsightClick = (insight: LongitudinalInsight) => {
    console.log('Insight clicked:', insight);
    // Could navigate to detailed insight view or show modal
  };

  const handleRiskAlert = (risk: RiskPrediction) => {
    console.log('Risk alert:', risk);
    // Could show notification or alert modal
    // For now, just log to console
  };

  if (!profile?.player_id) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view your analytics</p>
          <button
            onClick={() => navigate('/login')}
            className="btn-primary"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Analytics Dashboard
            </h1>
            <p className="text-gray-600">
              Track your therapeutic progress and insights with advanced analytics
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
            >
              Back to Dashboard
            </button>
            <button
              onClick={() => window.open('http://localhost:3003', '_blank')}
              className="btn-primary"
            >
              View Grafana Dashboards
            </button>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard Component */}
      <div className="bg-white rounded-lg shadow-md">
        <AdvancedAnalyticsDashboard
          userId={profile.player_id}
          goals={goals}
          onInsightClick={handleInsightClick}
          onRiskAlert={handleRiskAlert}
          className="w-full"
        />
      </div>

      {/* Additional Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            About Your Analytics
          </h3>
          <div className="space-y-3 text-sm text-gray-600">
            <p>
              <strong>Trend Analysis:</strong> Shows your progress patterns over time
            </p>
            <p>
              <strong>Risk Predictions:</strong> Identifies potential challenges and provides mitigation strategies
            </p>
            <p>
              <strong>Outcome Predictions:</strong> Forecasts your likely therapeutic outcomes
            </p>
            <p>
              <strong>Longitudinal Insights:</strong> Deep insights from your therapeutic journey
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Data Sources
          </h3>
          <div className="space-y-3 text-sm text-gray-600">
            <p>
              <strong>Session Data:</strong> Your conversation sessions and interactions
            </p>
            <p>
              <strong>Progress Tracking:</strong> Milestone achievements and goal progress
            </p>
            <p>
              <strong>Emotional Patterns:</strong> Emotional themes and regulation progress
            </p>
            <p>
              <strong>System Metrics:</strong> Real-time system health and performance data
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
