import React, { useState, useEffect, useMemo } from 'react';
import { THERAPEUTIC_GOALS, TherapeuticGoal as TherapeuticGoalString } from '../../types/preferences';
import { TherapeuticGoal } from '../../types/index';
import {
  generateGoalSuggestions,
  generateProgressAwareGoalSuggestions,
  GoalSuggestion,
  SuggestionResult,
  ProgressBasedRecommendation,
  GoalEvolutionSuggestion
} from '../../services/goalSuggestionEngine';
import { initializeGoalProgress, updateGoalProgress, GoalProgress } from '../../services/goalProgressService';
import { analyzeGoalRelationships, GoalRelationshipMap } from '../../services/goalRelationshipService';
import { analyzeTherapeuticApproachAlignment, TherapeuticApproachAnalysis } from '../../services/therapeuticApproachAlignmentService';
import {
  detectGoalConflicts,
  applyAutomaticResolution,
  ConflictDetectionResult,
  EnhancedGoalConflict,
  ConflictResolutionStrategy
} from '../../services/conflictDetectionService';
import {
  generatePersonalizedRecommendations,
  RecommendationResult,
  UserContext
} from '../../services/personalizedRecommendationEngine';
import {
  progressTrackingService,
  ProgressTrackingResult,
  OutcomeMeasurementType
} from '../../services/progressTrackingService';
import {
  therapeuticSessionService,
  TherapeuticSession,
  JourneyAnalysisResult
} from '../../services/therapeuticSessionService';
import {
  THERAPEUTIC_APPROACHES_INFO,
  IntensityLevel,
  ConversationStyle,
  PreferredSetting
} from '../../types/preferences';
import GoalVisualizationDashboard from './GoalVisualization/GoalVisualizationDashboard';
import ConflictWarningBanner from './ConflictResolution/ConflictWarningBanner';
import ConflictResolutionInterface from './ConflictResolution/ConflictResolutionInterface';
import PersonalizedRecommendationInterface from './PersonalizedRecommendations/PersonalizedRecommendationInterface';
import ProgressAnalyticsInterface from './ProgressAnalytics/ProgressAnalyticsInterface';
import SessionManagementInterface from './SessionManagement/SessionManagementInterface';
import RealTimeMonitoringInterface from '../RealTimeMonitoring/RealTimeMonitoringInterface';
import { InterventionRecord, RiskAssessment } from '../../services/realTimeTherapeuticMonitor';

interface TherapeuticGoalsSelectorProps {
  selected: string[];
  primaryConcerns: string[];
  onChange: (goals: string[], concerns: string[]) => void;
  goalProgresses?: GoalProgress[];
  onProgressUpdate?: (goalId: string, progress: number, notes?: string) => void;
  enableProgressTracking?: boolean;
}

const TherapeuticGoalsSelector: React.FC<TherapeuticGoalsSelectorProps> = ({
  selected = [],
  primaryConcerns = [],
  onChange,
  goalProgresses = [],
  onProgressUpdate,
  enableProgressTracking = false,
}) => {
  const [customGoal, setCustomGoal] = useState('');
  const [customConcern, setCustomConcern] = useState('');
  const [activeTab, setActiveTab] = useState<'goals' | 'concerns' | 'visualization' | 'recommendations' | 'analytics' | 'sessions' | 'monitoring'>('goals');
  const [suggestions, setSuggestions] = useState<SuggestionResult>({
    suggestions: [],
    totalConcernsAnalyzed: 0,
    suggestionStrength: 'weak'
  });
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [relationshipMap, setRelationshipMap] = useState<GoalRelationshipMap>({
    goals: [],
    relationships: [],
    conflicts: [],
    complementarySuggestions: [],
    overallCompatibility: 0.7,
    therapeuticCoherence: 1.0
  });
  const [approachAnalysis, setApproachAnalysis] = useState<TherapeuticApproachAnalysis>({
    selectedGoals: [],
    recommendedApproaches: [],
    approachAlignments: [],
    approachCompatibilities: [],
    overallCoherence: 0,
    treatmentEffectivenessScore: 0,
    integrationRecommendations: []
  });
  const [conflictDetectionResult, setConflictDetectionResult] = useState<ConflictDetectionResult>({
    conflicts: [],
    overallRiskScore: 0,
    recommendedActions: [],
    safeToProceeed: true,
    warningLevel: 'none',
    summary: {
      totalConflicts: 0,
      criticalConflicts: 0,
      resolvableConflicts: 0,
      monitoringRequired: 0
    }
  });
  const [showConflictResolution, setShowConflictResolution] = useState(false);

  // Personalized recommendations state
  const [recommendationResult, setRecommendationResult] = useState<RecommendationResult>({
    recommendations: [],
    totalRecommendations: 0,
    personalizationScore: 0,
    confidenceLevel: 'low',
    recommendationSummary: {
      totalRecommendations: 0,
      byPriority: { critical: 0, high: 0, medium: 0, low: 0, optional: 0 },
      byCategory: {
        immediate_action: 0,
        short_term_planning: 0,
        long_term_development: 0,
        crisis_prevention: 0,
        progress_optimization: 0,
        relationship_enhancement: 0,
        self_care: 0,
        skill_building: 0
      },
      byTimeframe: { immediate: 0, this_week: 0, this_month: 0, next_quarter: 0, long_term: 0 },
      averageConfidence: 0,
      personalizationStrength: 'low'
    },
    nextReviewDate: new Date(),
    adaptationHistory: []
  });
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Progress analytics state
  const [progressAnalyticsResult, setProgressAnalyticsResult] = useState<ProgressTrackingResult>({
    currentProgress: [],
    recentEntries: [],
    milestones: [],
    outcomeMeasurements: [],
    therapeuticInsights: [],
    overallEffectiveness: 0,
    riskAssessment: {
      overallRisk: 'minimal' as any,
      riskFactors: [],
      protectiveFactors: [],
      recommendations: []
    },
    recommendations: [],
    nextActions: [],
    generatedAt: new Date(),
    dataQuality: {
      completeness: 0,
      consistency: 0,
      recency: 0,
      reliability: 0,
      overallQuality: 0
    }
  });

  // Session management state
  const [sessions, setSessions] = useState<TherapeuticSession[]>([]);
  const [journeyAnalysis, setJourneyAnalysis] = useState<JourneyAnalysisResult | null>(null);

  // Load user sessions when component mounts
  useEffect(() => {
    try {
      const userSessions = therapeuticSessionService.getUserSessions("current-user");
      setSessions(userSessions);
    } catch (error) {
      console.error('Failed to load user sessions:', error);
    }
  }, []);

  // Memoize arrays to prevent infinite re-renders
  const memoizedPrimaryConcerns = useMemo(() => primaryConcerns, [JSON.stringify(primaryConcerns)]);
  const memoizedSelected = useMemo(() => selected, [JSON.stringify(selected)]);
  const memoizedGoalProgresses = useMemo(() => goalProgresses, [JSON.stringify(goalProgresses)]);

  // Generate suggestions when primary concerns change
  useEffect(() => {
    if (memoizedPrimaryConcerns.length > 0) {
      const newSuggestions = enableProgressTracking && memoizedGoalProgresses.length > 0
        ? generateProgressAwareGoalSuggestions(memoizedPrimaryConcerns, memoizedSelected, memoizedGoalProgresses, 5)
        : generateGoalSuggestions(memoizedPrimaryConcerns, memoizedSelected, 5);

      setSuggestions(newSuggestions);
      setShowSuggestions(newSuggestions.suggestions.length > 0);
    } else {
      setSuggestions({
        suggestions: [],
        totalConcernsAnalyzed: 0,
        suggestionStrength: 'weak'
      });
      setShowSuggestions(false);
    }
  }, [memoizedPrimaryConcerns, memoizedSelected, memoizedGoalProgresses, enableProgressTracking]);

  // Analyze goal relationships when selected goals change
  useEffect(() => {
    if (memoizedSelected.length > 0) {
      const analysis = analyzeGoalRelationships(memoizedSelected);
      setRelationshipMap(analysis);
    } else {
      setRelationshipMap({
        goals: [],
        relationships: [],
        conflicts: [],
        complementarySuggestions: [],
        overallCompatibility: 0.7,
        therapeuticCoherence: 1.0
      });
    }
  }, [memoizedSelected]);

  // Analyze therapeutic approach alignment when selected goals change
  useEffect(() => {
    if (memoizedSelected.length > 0) {
      const analysis = analyzeTherapeuticApproachAlignment(memoizedSelected);
      setApproachAnalysis(analysis);
    } else {
      setApproachAnalysis({
        selectedGoals: [],
        recommendedApproaches: [],
        approachAlignments: [],
        approachCompatibilities: [],
        overallCoherence: 0,
        treatmentEffectivenessScore: 0,
        integrationRecommendations: []
      });
    }
  }, [memoizedSelected]);

  // Enhanced conflict detection when goals or progress change
  useEffect(() => {
    if (memoizedSelected.length > 0) {
      const conflictResult = detectGoalConflicts(memoizedSelected, memoizedGoalProgresses, approachAnalysis);
      setConflictDetectionResult(conflictResult);
    } else {
      setConflictDetectionResult({
        conflicts: [],
        overallRiskScore: 0,
        recommendedActions: [],
        safeToProceeed: true,
        warningLevel: 'none',
        summary: {
          totalConflicts: 0,
          criticalConflicts: 0,
          resolvableConflicts: 0,
          monitoringRequired: 0
        }
      });
    }
  }, [memoizedSelected, memoizedGoalProgresses, approachAnalysis]);

  // Generate personalized recommendations when context changes
  useEffect(() => {
    if (memoizedSelected.length > 0 || memoizedPrimaryConcerns.length > 0) {
      const userContext: UserContext = {
        preferences: {
          player_id: 'current-user', // Would come from actual user context
          intensity_level: 'medium' as any, // Would come from user preferences
          preferred_approaches: ['cognitive_behavioral_therapy', 'mindfulness'] as any,
          conversation_style: 'supportive' as any,
          therapeutic_goals: memoizedSelected,
          primary_concerns: memoizedPrimaryConcerns,
          character_name: 'User',
          preferred_setting: 'peaceful_forest' as any,
          comfort_topics: [],
          trigger_topics: [],
          avoid_topics: [],
          session_duration_preference: 30,
          reminder_frequency: 'weekly',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          version: 1
        },
        goalProgresses: memoizedGoalProgresses,
        approachAnalysis,
        relationshipMap,
        conflictDetection: conflictDetectionResult
      };

      const recommendations = generatePersonalizedRecommendations(userContext, 8);
      setRecommendationResult(recommendations);
      setShowRecommendations(recommendations.recommendations.length > 0);
    } else {
      setRecommendationResult({
        recommendations: [],
        totalRecommendations: 0,
        personalizationScore: 0,
        confidenceLevel: 'low',
        recommendationSummary: {
          totalRecommendations: 0,
          byPriority: { critical: 0, high: 0, medium: 0, low: 0, optional: 0 },
          byCategory: {
            immediate_action: 0,
            short_term_planning: 0,
            long_term_development: 0,
            crisis_prevention: 0,
            progress_optimization: 0,
            relationship_enhancement: 0,
            self_care: 0,
            skill_building: 0
          },
          byTimeframe: { immediate: 0, this_week: 0, this_month: 0, next_quarter: 0, long_term: 0 },
          averageConfidence: 0,
          personalizationStrength: 'low'
        },
        nextReviewDate: new Date(),
        adaptationHistory: []
      });
      setShowRecommendations(false);
    }
  }, [memoizedSelected, memoizedPrimaryConcerns, memoizedGoalProgresses, approachAnalysis, relationshipMap, conflictDetectionResult]);

  // Generate progress analytics when goals or progress data changes
  useEffect(() => {
    if (memoizedSelected.length > 0 && enableProgressTracking) {
      // Create goal objects for analytics (using a simplified structure for the analytics service)
      const selectedGoalObjects = memoizedSelected.map(goalId => {
        const goalLabel = findGoalLabel(goalId);
        const goalProgress = memoizedGoalProgresses.find(gp => gp.goalId === goalId);
        return {
          id: goalId,
          title: goalLabel,
          description: `Working on ${goalLabel.toLowerCase()}`,
          category: 'Therapeutic',
          priority: 'medium' as const,
          targetDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000), // 90 days from now
          approaches: [],
          isActive: true,
          createdAt: new Date(),
          progress: goalProgress?.progress || 0
        };
      });

      const analytics = progressTrackingService.generateProgressAnalytics('current-user', selectedGoalObjects as any, 'month');
      setProgressAnalyticsResult(analytics);
    } else {
      // Reset analytics when no goals selected or progress tracking disabled
      setProgressAnalyticsResult({
        currentProgress: [],
        recentEntries: [],
        milestones: [],
        outcomeMeasurements: [],
        therapeuticInsights: [],
        overallEffectiveness: 0,
        riskAssessment: {
          overallRisk: 'minimal' as any,
          riskFactors: [],
          protectiveFactors: [],
          recommendations: []
        },
        recommendations: [],
        nextActions: [],
        generatedAt: new Date(),
        dataQuality: {
          completeness: 0,
          consistency: 0,
          recency: 0,
          reliability: 0,
          overallQuality: 0
        }
      });
    }
  }, [memoizedSelected, memoizedGoalProgresses, enableProgressTracking]);

  // Helper function to find goal label
  const findGoalLabel = (goalId: string): string => {
    for (const category of Object.values(goalCategories)) {
      const goal = category.find(g => g.id === goalId);
      if (goal) return goal.label;
    }
    return goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const goalCategories = {
    'Emotional Wellbeing': [
      { id: 'anxiety_reduction', label: 'Anxiety Reduction', icon: '😌', description: 'Learn to manage and reduce anxiety symptoms' },
      { id: 'stress_management', label: 'Stress Management', icon: '🧘', description: 'Develop healthy coping strategies for stress' },
      { id: 'emotional_processing', label: 'Emotional Processing', icon: '💭', description: 'Better understand and process emotions' },
      { id: 'anger_management', label: 'Anger Management', icon: '🌊', description: 'Learn healthy ways to express and manage anger' },
      { id: 'grief_processing', label: 'Grief Processing', icon: '🕊️', description: 'Navigate loss and grief in a healthy way' },
    ],
    'Self-Development': [
      { id: 'confidence_building', label: 'Confidence Building', icon: '💪', description: 'Build self-confidence and self-esteem' },
      { id: 'self_compassion', label: 'Self-Compassion', icon: '💝', description: 'Develop kindness and understanding toward yourself' },
      { id: 'personal_growth', label: 'Personal Growth', icon: '🌱', description: 'Explore and develop your potential' },
      { id: 'boundary_setting', label: 'Boundary Setting', icon: '🛡️', description: 'Learn to set and maintain healthy boundaries' },
    ],
    'Relationships & Communication': [
      { id: 'relationship_skills', label: 'Relationship Skills', icon: '🤝', description: 'Improve interpersonal relationships' },
      { id: 'communication_skills', label: 'Communication Skills', icon: '💬', description: 'Enhance communication abilities' },
    ],
    'Mind-Body Connection': [
      { id: 'mindfulness_development', label: 'Mindfulness Development', icon: '🧘‍♀️', description: 'Cultivate present-moment awareness' },
      { id: 'body_awareness', label: 'Body Awareness', icon: '🤸', description: 'Develop connection with physical sensations' },
      { id: 'sleep_improvement', label: 'Sleep Improvement', icon: '😴', description: 'Improve sleep quality and habits' },
    ],
    'Coping & Recovery': [
      { id: 'coping_strategies', label: 'Coping Strategies', icon: '🛠️', description: 'Build a toolkit of healthy coping mechanisms' },
      { id: 'trauma_recovery', label: 'Trauma Recovery', icon: '🌈', description: 'Heal from traumatic experiences' },
    ]
  };

  const handleGoalToggle = (goalId: string) => {
    const updatedGoals = selected.includes(goalId)
      ? selected.filter(g => g !== goalId)
      : [...selected, goalId];
    
    onChange(updatedGoals, primaryConcerns);
  };

  const handleConcernToggle = (concern: string) => {
    const updatedConcerns = primaryConcerns.includes(concern)
      ? primaryConcerns.filter(c => c !== concern)
      : [...primaryConcerns, concern];
    
    onChange(selected, updatedConcerns);
  };

  const addCustomGoal = () => {
    if (customGoal.trim() && !selected.includes(customGoal.trim())) {
      onChange([...selected, customGoal.trim()], primaryConcerns);
      setCustomGoal('');
    }
  };

  const addCustomConcern = () => {
    if (customConcern.trim() && !primaryConcerns.includes(customConcern.trim())) {
      onChange(selected, [...primaryConcerns, customConcern.trim()]);
      setCustomConcern('');
    }
  };

  const applySuggestion = (suggestion: GoalSuggestion) => {
    if (!selected.includes(suggestion.goalId)) {
      onChange([...selected, suggestion.goalId], primaryConcerns);
    }
  };

  const applyAllSuggestions = () => {
    const newGoals = suggestions.suggestions
      .filter(s => !selected.includes(s.goalId))
      .map(s => s.goalId);

    if (newGoals.length > 0) {
      onChange([...selected, ...newGoals], primaryConcerns);
    }
  };

  // Conflict resolution handlers
  const handleViewConflictDetails = () => {
    setShowConflictResolution(true);
  };

  const handleQuickResolveConflicts = () => {
    const resolution = applyAutomaticResolution(conflictDetectionResult.conflicts, selected);
    if (resolution.resolvedConflicts.length > 0) {
      onChange(resolution.modifiedGoals, primaryConcerns);
    }
  };

  const handleResolveConflict = (conflictId: string, strategy: ConflictResolutionStrategy) => {
    // In a real implementation, this would apply the specific strategy
    // For now, we'll just remove the conflicting goals or apply basic resolution
    console.log(`Applying strategy ${strategy.strategyId} for conflict ${conflictId}`);

    // Find the conflict and apply basic resolution
    const conflict = conflictDetectionResult.conflicts.find(c => c.conflictId === conflictId);
    if (conflict && conflict.autoResolvable) {
      const resolution = applyAutomaticResolution([conflict], selected);
      onChange(resolution.modifiedGoals, primaryConcerns);
    }
  };

  const handleModifyGoalsForConflict = (newGoals: string[]) => {
    onChange(newGoals, primaryConcerns);
  };

  // Personalized recommendation handlers
  const handleAcceptRecommendation = (recommendationId: string) => {
    const recommendation = recommendationResult.recommendations.find(rec => rec.id === recommendationId);
    if (recommendation) {
      // Handle different recommendation types
      if (recommendation.type === 'goal_suggestion' && recommendation.relatedGoals) {
        const newGoals = [...selected];
        recommendation.relatedGoals.forEach(goalId => {
          if (!newGoals.includes(goalId)) {
            newGoals.push(goalId);
          }
        });
        onChange(newGoals, primaryConcerns);
      }

      // Remove the accepted recommendation from the list
      const updatedRecommendations = recommendationResult.recommendations.filter(rec => rec.id !== recommendationId);
      setRecommendationResult({
        ...recommendationResult,
        recommendations: updatedRecommendations,
        totalRecommendations: updatedRecommendations.length
      });
    }
  };

  const handleDismissRecommendation = (recommendationId: string) => {
    const updatedRecommendations = recommendationResult.recommendations.filter(rec => rec.id !== recommendationId);
    setRecommendationResult({
      ...recommendationResult,
      recommendations: updatedRecommendations,
      totalRecommendations: updatedRecommendations.length
    });
  };

  const handleProvideFeedback = (recommendationId: string, rating: number, comments?: string) => {
    // In a real implementation, this would send feedback to the backend
    console.log('Recommendation feedback:', { recommendationId, rating, comments });

    // For now, just log the feedback
    // In production, this would update user feedback history and improve future recommendations
  };

  const handleRequestMoreInfo = (recommendationId: string) => {
    const recommendation = recommendationResult.recommendations.find(rec => rec.id === recommendationId);
    if (recommendation) {
      // In a real implementation, this might open a detailed modal or navigate to more information
      console.log('More info requested for:', recommendation.title);
      alert(`More information about: ${recommendation.title}\n\n${recommendation.description}\n\nExpected outcome: ${recommendation.expectedOutcome}`);
    }
  };

  // Progress analytics handlers
  const handleRecordProgress = (goalId: string, progressValue: number, notes?: string) => {
    if (onProgressUpdate) {
      onProgressUpdate(goalId, progressValue, notes);
    }

    // Also record in the progress tracking service
    progressTrackingService.recordProgress({
      goalId,
      userId: 'current-user',
      progressValue,
      progressType: 'self_reported' as any,
      measurementMethod: 'likert_scale' as any,
      notes,
      evidenceLevel: 'observational' as any
    });
  };

  const handleRecordOutcome = (measurementType: string, score: number) => {
    progressTrackingService.recordOutcomeMeasurement({
      userId: 'current-user',
      measurementType: measurementType as any,
      score,
      maxScore: measurementType === 'PHQ9' ? 27 : measurementType === 'GAD7' ? 21 : 100,
      clinicalSignificance: 'not_significant' as any,
      trendDirection: 'stable' as any
    });
  };

  const handleAcceptProgressRecommendation = (recommendationId: string) => {
    console.log(`Accepting progress recommendation ${recommendationId}`);
    // In a real implementation, this would apply the recommendation
  };

  const handleDismissProgressRecommendation = (recommendationId: string) => {
    console.log(`Dismissing progress recommendation ${recommendationId}`);
    // In a real implementation, this would hide the recommendation
  };

  const handleScheduleAction = (actionId: string, dueDate: Date) => {
    console.log(`Scheduling action ${actionId} for ${dueDate.toLocaleDateString()}`);
    // In a real implementation, this would add the action to a calendar or task system
  };

  const handleRequestDetailedInsight = (insightId: string) => {
    console.log(`Requesting detailed insight ${insightId}`);
    // In a real implementation, this would show more detailed information about the insight
  };

  const commonConcerns = [
    'Work stress', 'Relationship issues', 'Family problems', 'Financial worries',
    'Health concerns', 'Life transitions', 'Social anxiety', 'Depression',
    'Perfectionism', 'Procrastination', 'Low self-esteem', 'Loneliness',
    'Career uncertainty', 'Academic pressure', 'Parenting challenges'
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Therapeutic Goals & Primary Concerns
        </h2>
        <p className="text-gray-600 mb-6">
          Select your therapeutic goals and primary concerns to help personalize your experience. 
          This helps the AI understand what you want to work on and what's most important to you.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex overflow-x-auto scrollbar-hide space-x-2 sm:space-x-4 md:space-x-8 pb-2 sm:pb-0" role="tablist" aria-label="Therapeutic goals and concerns">
          <button
            role="tab"
            id="goals-tab"
            aria-controls="goals-panel"
            aria-selected={activeTab === 'goals'}
            tabIndex={activeTab === 'goals' ? 0 : -1}
            onClick={() => setActiveTab('goals')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowRight') {
                setActiveTab('concerns');
                document.getElementById('concerns-tab')?.focus();
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'goals'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            🎯 Therapeutic Goals ({selected.length})
          </button>
          <button
            role="tab"
            id="concerns-tab"
            aria-controls="concerns-panel"
            aria-selected={activeTab === 'concerns'}
            tabIndex={activeTab === 'concerns' ? 0 : -1}
            onClick={() => setActiveTab('concerns')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') {
                setActiveTab('goals');
                document.getElementById('goals-tab')?.focus();
              } else if (e.key === 'ArrowRight') {
                setActiveTab('visualization');
                document.getElementById('visualization-tab')?.focus();
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'concerns'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            📝 Primary Concerns ({primaryConcerns.length})
          </button>
          <button
            role="tab"
            id="visualization-tab"
            aria-controls="visualization-panel"
            aria-selected={activeTab === 'visualization'}
            tabIndex={activeTab === 'visualization' ? 0 : -1}
            onClick={() => setActiveTab('visualization')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') {
                setActiveTab('concerns');
                document.getElementById('concerns-tab')?.focus();
              } else if (e.key === 'ArrowRight') {
                setActiveTab('recommendations');
                document.getElementById('recommendations-tab')?.focus();
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'visualization'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            📊 Visualization {selected.length > 0 ? `(${selected.length} goals)` : ''}
          </button>
          <button
            role="tab"
            id="recommendations-tab"
            aria-controls="recommendations-panel"
            aria-selected={activeTab === 'recommendations'}
            tabIndex={activeTab === 'recommendations' ? 0 : -1}
            onClick={() => setActiveTab('recommendations')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') {
                setActiveTab('visualization');
                document.getElementById('visualization-tab')?.focus();
              } else if (e.key === 'ArrowRight') {
                if (enableProgressTracking) {
                  setActiveTab('analytics');
                  document.getElementById('analytics-tab')?.focus();
                } else {
                  setActiveTab('sessions');
                  document.getElementById('sessions-tab')?.focus();
                }
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'recommendations'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            🤖 AI Recommendations {showRecommendations ? `(${recommendationResult.totalRecommendations})` : ''}
          </button>
          {enableProgressTracking && (
            <button
              role="tab"
              id="analytics-tab"
              aria-controls="analytics-panel"
              aria-selected={activeTab === 'analytics'}
              tabIndex={activeTab === 'analytics' ? 0 : -1}
              onClick={() => setActiveTab('analytics')}
              onKeyDown={(e) => {
                if (e.key === 'ArrowLeft') {
                  setActiveTab('recommendations');
                  document.getElementById('recommendations-tab')?.focus();
                } else if (e.key === 'ArrowRight') {
                  setActiveTab('sessions');
                  document.getElementById('sessions-tab')?.focus();
                }
              }}
              className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
                activeTab === 'analytics'
                  ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              📈 Progress Analytics {progressAnalyticsResult.currentProgress.length > 0 ? `(${Math.round(progressAnalyticsResult.overallEffectiveness)}%)` : ''}
            </button>
          )}
          <button
            role="tab"
            id="sessions-tab"
            aria-controls="sessions-panel"
            aria-selected={activeTab === 'sessions'}
            tabIndex={activeTab === 'sessions' ? 0 : -1}
            onClick={() => setActiveTab('sessions')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') {
                if (enableProgressTracking) {
                  setActiveTab('analytics');
                  document.getElementById('analytics-tab')?.focus();
                } else {
                  setActiveTab('recommendations');
                  document.getElementById('recommendations-tab')?.focus();
                }
              } else if (e.key === 'ArrowRight') {
                setActiveTab('monitoring');
                document.getElementById('monitoring-tab')?.focus();
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'sessions'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            🗓️ Therapeutic Sessions {sessions.length > 0 ? `(${sessions.length})` : ''}
          </button>
          <button
            role="tab"
            id="monitoring-tab"
            aria-controls="monitoring-panel"
            aria-selected={activeTab === 'monitoring'}
            tabIndex={activeTab === 'monitoring' ? 0 : -1}
            onClick={() => setActiveTab('monitoring')}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft') {
                setActiveTab('sessions');
                document.getElementById('sessions-tab')?.focus();
              }
            }}
            className={`py-3 px-3 sm:px-4 md:px-1 border-b-2 font-medium text-sm whitespace-nowrap min-w-[44px] min-h-[44px] flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 ${
              activeTab === 'monitoring'
                ? 'border-primary-500 text-primary-600 bg-primary-50 sm:bg-transparent'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            📊 Real-Time Monitoring
          </button>
        </nav>
      </div>

      {/* Conflict Warning Banner */}
      {conflictDetectionResult.warningLevel !== 'none' && (
        <ConflictWarningBanner
          conflictResult={conflictDetectionResult}
          onViewDetails={handleViewConflictDetails}
          onQuickResolve={handleQuickResolveConflicts}
          onDismiss={() => setConflictDetectionResult(prev => ({ ...prev, warningLevel: 'none' }))}
        />
      )}

      {/* Conflict Resolution Interface */}
      {showConflictResolution && conflictDetectionResult.conflicts.length > 0 && (
        <ConflictResolutionInterface
          conflicts={conflictDetectionResult.conflicts}
          selectedGoals={selected}
          onResolveConflict={handleResolveConflict}
          onApplyAutomaticResolution={handleQuickResolveConflicts}
          onModifyGoals={handleModifyGoalsForConflict}
          className="mb-6"
        />
      )}

      {/* Goals Tab */}
      {activeTab === 'goals' && (
        <div
          role="tabpanel"
          id="goals-panel"
          aria-labelledby="goals-tab"
          className="space-y-6"
        >
          {/* Quick Selection */}
          <div className="bg-gray-50 rounded-lg p-4 sm:p-6">
            <h3 className="font-medium text-gray-900 mb-3 text-base sm:text-lg">Quick Selection:</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-2">
              <button
                onClick={() => onChange(['anxiety_reduction', 'stress_management', 'mindfulness_development'], primaryConcerns)}
                className="btn-outline text-sm sm:text-xs md:text-sm min-h-[44px] px-4 py-3 sm:py-2 text-left sm:text-center"
              >
                <span className="block sm:inline">🧘 Stress & Anxiety</span>
              </button>
              <button
                onClick={() => onChange(['confidence_building', 'self_compassion', 'personal_growth'], primaryConcerns)}
                className="btn-outline text-sm sm:text-xs md:text-sm min-h-[44px] px-4 py-3 sm:py-2 text-left sm:text-center"
              >
                <span className="block sm:inline">💪 Self-Esteem & Growth</span>
              </button>
              <button
                onClick={() => onChange(['relationship_skills', 'communication_skills', 'boundary_setting'], primaryConcerns)}
                className="btn-outline text-sm sm:text-xs md:text-sm min-h-[44px] px-4 py-3 sm:py-2 text-left sm:text-center"
              >
                <span className="block sm:inline">🤝 Relationships</span>
              </button>
              <button
                onClick={() => onChange(['emotional_processing', 'coping_strategies', 'mindfulness_development'], primaryConcerns)}
                className="btn-outline text-sm sm:text-xs md:text-sm min-h-[44px] px-4 py-3 sm:py-2 text-left sm:text-center"
              >
                <span className="block sm:inline">❤️ Emotional Health</span>
              </button>
            </div>
          </div>

          {/* AI-Powered Goal Suggestions */}
          {showSuggestions && suggestions.suggestions.length > 0 && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path fillRule="evenodd" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="font-medium text-blue-900">
                      🤖 AI-Powered Goal Suggestions
                    </h3>
                    <p className="text-sm text-blue-700 mt-1">
                      Based on your selected concerns, here are {suggestions.suggestions.length} evidence-based therapeutic goals that might help:
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    suggestions.suggestionStrength === 'strong' ? 'bg-green-100 text-green-800' :
                    suggestions.suggestionStrength === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {suggestions.suggestionStrength} match
                  </span>
                  {suggestions.suggestions.filter(s => !selected.includes(s.goalId)).length > 1 && (
                    <button
                      onClick={applyAllSuggestions}
                      className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      aria-label="Apply all suggested goals"
                    >
                      Apply All
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:gap-3 md:grid-cols-2">
                {suggestions.suggestions.map((suggestion) => {
                  const isAlreadySelected = selected.includes(suggestion.goalId);
                  const goalInfo = Object.values(goalCategories)
                    .flat()
                    .find(g => g.id === suggestion.goalId);

                  return (
                    <div
                      key={suggestion.goalId}
                      className={`relative p-4 sm:p-3 rounded-lg border-2 transition-all min-h-[80px] sm:min-h-[auto] ${
                        isAlreadySelected
                          ? 'border-green-300 bg-green-50'
                          : 'border-blue-200 bg-white hover:border-blue-300 active:border-blue-400 active:bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2 sm:mb-0">
                            <span className="text-xl sm:text-lg flex-shrink-0" aria-hidden="true">{goalInfo?.icon || '🎯'}</span>
                            <h4 className="font-medium text-gray-900 text-base sm:text-sm leading-tight">
                              {goalInfo?.label || suggestion.goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                            <div className="flex items-center space-x-1">
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                                suggestion.clinicalEvidence === 'high' ? 'bg-green-100 text-green-700' :
                                suggestion.clinicalEvidence === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {suggestion.clinicalEvidence} evidence
                              </span>
                              <span className="text-xs text-gray-500">
                                {Math.round(suggestion.confidence * 100)}% match
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {suggestion.reason}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Category: {suggestion.category}
                          </p>
                        </div>

                        {!isAlreadySelected && (
                          <button
                            onClick={() => applySuggestion(suggestion)}
                            className="ml-3 flex-shrink-0 bg-blue-600 text-white px-3 py-1 rounded-full text-xs hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            aria-label={`Add suggested goal: ${goalInfo?.label || suggestion.goalId}`}
                          >
                            Add
                          </button>
                        )}

                        {isAlreadySelected && (
                          <div className="ml-3 flex-shrink-0 flex items-center text-green-600">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            <span className="text-xs ml-1">Selected</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-3 pt-3 border-t border-blue-200">
                <p className="text-xs text-blue-600">
                  💡 These suggestions are based on evidence-based therapeutic approaches and your selected concerns.
                  You can always add, remove, or customize goals to fit your personal needs.
                </p>
              </div>
            </div>
          )}

          {/* Progress-Based Recommendations */}
          {enableProgressTracking && suggestions.progressBasedRecommendations && suggestions.progressBasedRecommendations.length > 0 && (
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📈</span>
                  <h3 className="font-semibold text-purple-900">Progress-Based Recommendations</h3>
                </div>
              </div>

              <div className="space-y-3">
                {suggestions.progressBasedRecommendations.map((recommendation, index) => {
                  const goalInfo = Object.values(goalCategories)
                    .flat()
                    .find(g => g.id === recommendation.goalId);

                  return (
                    <div
                      key={`${recommendation.goalId}-${index}`}
                      className={`relative p-3 rounded-lg border-2 transition-all ${
                        recommendation.urgency === 'high' ? 'border-red-200 bg-red-50' :
                        recommendation.urgency === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                        'border-purple-200 bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-lg" aria-hidden="true">{goalInfo?.icon || '🎯'}</span>
                            <h4 className="font-medium text-gray-900">
                              {goalInfo?.label || recommendation.goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                            <div className="flex items-center space-x-1">
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                                recommendation.urgency === 'high' ? 'bg-red-100 text-red-700' :
                                recommendation.urgency === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-purple-100 text-purple-700'
                              }`}>
                                {recommendation.urgency} priority
                              </span>
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                                recommendation.clinicalEvidence === 'high' ? 'bg-green-100 text-green-700' :
                                recommendation.clinicalEvidence === 'medium' ? 'bg-blue-100 text-blue-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {recommendation.clinicalEvidence} evidence
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700 mb-1">{recommendation.recommendation}</p>
                          <p className="text-xs text-gray-500">
                            Reason: {recommendation.reason} • Confidence: {Math.round(recommendation.confidence * 100)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-3 pt-3 border-t border-purple-200">
                <p className="text-xs text-purple-600">
                  📊 These recommendations are based on your current goal progress and therapeutic patterns.
                </p>
              </div>
            </div>
          )}

          {/* Goal Evolution Suggestions */}
          {enableProgressTracking && suggestions.evolutionSuggestions && suggestions.evolutionSuggestions.length > 0 && (
            <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">🌱</span>
                  <h3 className="font-semibold text-emerald-900">Goal Evolution Opportunities</h3>
                </div>
              </div>

              <div className="space-y-3">
                {suggestions.evolutionSuggestions.map((evolution, index) => {
                  const goalInfo = Object.values(goalCategories)
                    .flat()
                    .find(g => g.id === evolution.currentGoalId);

                  return (
                    <div
                      key={`${evolution.currentGoalId}-${index}`}
                      className="relative p-3 rounded-lg border-2 border-emerald-200 bg-white transition-all"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-lg" aria-hidden="true">{goalInfo?.icon || '🎯'}</span>
                            <h4 className="font-medium text-gray-900">
                              {goalInfo?.label || evolution.currentGoalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                            <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                              evolution.evolutionType === 'graduate' ? 'bg-emerald-100 text-emerald-700' :
                              evolution.evolutionType === 'split' ? 'bg-blue-100 text-blue-700' :
                              evolution.evolutionType === 'expand' ? 'bg-purple-100 text-purple-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {evolution.evolutionType}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mb-1">
                            <strong>Evolution:</strong> {evolution.suggestedEvolution}
                          </p>
                          <p className="text-xs text-gray-500">
                            {evolution.reason} • Confidence: {Math.round(evolution.confidence * 100)}% •
                            Requires {evolution.requiredProgress}% progress
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-3 pt-3 border-t border-emerald-200">
                <p className="text-xs text-emerald-600">
                  🚀 These evolution opportunities help you advance your therapeutic journey as you make progress.
                </p>
              </div>
            </div>
          )}

          {/* Goal Categories */}
          {Object.entries(goalCategories).map(([category, goals]) => (
            <div key={category} className="space-y-3">
              <h3 className="font-semibold text-gray-900 text-lg">{category}</h3>
              <div className="grid grid-cols-1 gap-4 sm:gap-3 md:grid-cols-2">
                {goals.map((goal) => (
                  <label
                    key={goal.id}
                    className={`flex items-start space-x-3 p-4 sm:p-3 md:p-4 rounded-lg border-2 cursor-pointer transition-all min-h-[80px] sm:min-h-[auto] ${
                      selected.includes(goal.id)
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 active:border-primary-300 active:bg-primary-25'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mt-1 sm:mt-0.5 rounded border-gray-300 text-primary-600 focus:ring-primary-500 w-5 h-5 sm:w-4 sm:h-4 flex-shrink-0"
                      checked={selected.includes(goal.id)}
                      aria-checked={selected.includes(goal.id)}
                      onChange={() => handleGoalToggle(goal.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleGoalToggle(goal.id);
                        }
                      }}
                    />
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <span className="text-xl sm:text-lg mr-2 flex-shrink-0">{goal.icon}</span>
                        <span className="font-medium text-gray-900 text-base sm:text-sm leading-tight">{goal.label}</span>
                        {enableProgressTracking && (() => {
                          const progress = goalProgresses.find(gp => gp.goalId === goal.id);
                          if (progress) {
                            return (
                              <div className="ml-auto flex items-center space-x-2">
                                <div className="flex items-center space-x-1">
                                  <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      className={`h-full transition-all duration-300 ${
                                        progress.status === 'completed' ? 'bg-green-500' :
                                        progress.status === 'in_progress' ? 'bg-blue-500' :
                                        'bg-gray-300'
                                      }`}
                                      style={{ width: `${progress.progress}%` }}
                                    />
                                  </div>
                                  <span className="text-xs text-gray-500 font-medium">
                                    {progress.progress}%
                                  </span>
                                </div>
                                {progress.status === 'completed' && (
                                  <span className="text-green-600 text-sm">✓</span>
                                )}
                              </div>
                            );
                          }
                          return null;
                        })()}
                      </div>
                      <p className="text-sm sm:text-xs md:text-sm text-gray-600 leading-relaxed">{goal.description}</p>
                      {enableProgressTracking && (() => {
                        const progress = goalProgresses.find(gp => gp.goalId === goal.id);
                        if (progress && progress.milestones.length > 0) {
                          const achievedMilestones = progress.milestones.filter(m => m.achieved).length;
                          const totalMilestones = progress.milestones.length;
                          return (
                            <div className="mt-2 text-xs text-gray-500">
                              Milestones: {achievedMilestones}/{totalMilestones} completed
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}

          {/* Custom Goals */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">Custom Goals</h3>
            
            {/* Display custom goals */}
            {selected.filter(goal => !THERAPEUTIC_GOALS.includes(goal as TherapeuticGoalString)).map((customGoal) => (
              <div key={customGoal} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-blue-900">{customGoal}</span>
                <button
                  onClick={() => handleGoalToggle(customGoal)}
                  aria-label={`Remove custom goal: ${customGoal}`}
                  className="text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

            {/* Add custom goal */}
            <div className="flex space-x-2">
              <label htmlFor="custom-goal-input" className="sr-only">
                Add a custom therapeutic goal
              </label>
              <input
                id="custom-goal-input"
                type="text"
                value={customGoal}
                onChange={(e) => setCustomGoal(e.target.value)}
                placeholder="Add a custom therapeutic goal..."
                aria-label="Add a custom therapeutic goal"
                className="input-field flex-1 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                onKeyDown={(e) => e.key === 'Enter' && addCustomGoal()}
              />
              <button
                onClick={addCustomGoal}
                aria-label="Add custom goal"
                className="btn-primary text-sm px-4 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Concerns Tab */}
      {activeTab === 'concerns' && (
        <div
          role="tabpanel"
          id="concerns-panel"
          aria-labelledby="concerns-tab"
          className="space-y-6"
        >
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Common Concerns</h3>
            <p className="text-gray-600 text-sm mb-4">
              Select the areas that are currently causing you the most difficulty or stress.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-2">
              {commonConcerns.map((concern) => (
                <label
                  key={concern}
                  className={`flex items-center space-x-3 sm:space-x-2 p-4 sm:p-3 rounded-lg border cursor-pointer transition-all min-h-[56px] sm:min-h-[auto] ${
                    primaryConcerns.includes(concern)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 active:border-primary-300 active:bg-primary-25'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 w-5 h-5 sm:w-4 sm:h-4 flex-shrink-0"
                    checked={primaryConcerns.includes(concern)}
                    aria-checked={primaryConcerns.includes(concern)}
                    onChange={() => handleConcernToggle(concern)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleConcernToggle(concern);
                      }
                    }}
                  />
                  <span className="text-base sm:text-sm leading-tight">{concern}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Custom Concerns */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">Custom Concerns</h3>
            
            {/* Display custom concerns */}
            {primaryConcerns.filter(concern => !commonConcerns.includes(concern)).map((customConcern) => (
              <div key={customConcern} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                <span className="text-amber-900">{customConcern}</span>
                <button
                  onClick={() => handleConcernToggle(customConcern)}
                  aria-label={`Remove custom concern: ${customConcern}`}
                  className="text-amber-600 hover:text-amber-800 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 rounded"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

            {/* Add custom concern */}
            <div className="flex space-x-2">
              <label htmlFor="custom-concern-input" className="sr-only">
                Add a custom concern
              </label>
              <input
                id="custom-concern-input"
                type="text"
                value={customConcern}
                onChange={(e) => setCustomConcern(e.target.value)}
                placeholder="Add a custom concern..."
                aria-label="Add a custom concern"
                className="input-field flex-1 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                onKeyDown={(e) => e.key === 'Enter' && addCustomConcern()}
              />
              <button
                onClick={addCustomConcern}
                aria-label="Add custom concern"
                className="btn-primary text-sm px-4 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visualization Tab */}
      {activeTab === 'visualization' && (
        <div
          role="tabpanel"
          id="visualization-panel"
          aria-labelledby="visualization-tab"
          className="space-y-6"
        >
          <GoalVisualizationDashboard
            selectedGoals={selected}
            relationshipMap={relationshipMap}
            goalProgresses={goalProgresses}
            approachAnalysis={approachAnalysis}
            onGoalClick={(goalId) => {
              // Toggle goal selection when clicked in visualization
              if (selected.includes(goalId)) {
                onChange(selected.filter(g => g !== goalId), primaryConcerns);
              } else {
                onChange([...selected, goalId], primaryConcerns);
              }
            }}
            onStageClick={(stageId) => {
              // Could implement stage-specific actions here
              console.log('Stage clicked:', stageId);
            }}
          />
        </div>
      )}

      {/* Recommendations Tab */}
      {activeTab === 'recommendations' && (
        <div
          role="tabpanel"
          id="recommendations-panel"
          aria-labelledby="recommendations-tab"
          className="space-y-6"
        >
          {showRecommendations ? (
            <PersonalizedRecommendationInterface
              recommendationResult={recommendationResult}
              onAcceptRecommendation={handleAcceptRecommendation}
              onDismissRecommendation={handleDismissRecommendation}
              onProvideFeedback={handleProvideFeedback}
              onRequestMoreInfo={handleRequestMoreInfo}
              maxDisplayRecommendations={8}
            />
          ) : (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">🌟</div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                No recommendations yet
              </h3>
              <p className="text-blue-700 mb-4">
                Select some therapeutic goals and primary concerns to receive personalized AI recommendations.
              </p>
              <button
                onClick={() => setActiveTab('goals')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Select Goals
              </button>
            </div>
          )}
        </div>
      )}

      {/* Progress Analytics Tab */}
      {activeTab === 'analytics' && enableProgressTracking && (
        <div
          role="tabpanel"
          id="analytics-panel"
          aria-labelledby="analytics-tab"
          className="space-y-6"
        >
          {progressAnalyticsResult.currentProgress.length > 0 ? (
            <ProgressAnalyticsInterface
              progressResult={progressAnalyticsResult}
              onRecordProgress={handleRecordProgress}
              onRecordOutcome={handleRecordOutcome}
              onAcceptRecommendation={handleAcceptProgressRecommendation}
              onDismissRecommendation={handleDismissProgressRecommendation}
              onScheduleAction={handleScheduleAction}
              onRequestDetailedInsight={handleRequestDetailedInsight}
            />
          ) : (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold text-purple-900 mb-2">
                No progress data yet
              </h3>
              <p className="text-purple-700 mb-4">
                Start tracking your progress on therapeutic goals to see detailed analytics and insights.
              </p>
              <button
                onClick={() => setActiveTab('goals')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
              >
                Select Goals to Track
              </button>
            </div>
          )}
        </div>
      )}

      {/* Sessions Tab */}
      {activeTab === 'sessions' && (
        <div
          role="tabpanel"
          id="sessions-panel"
          aria-labelledby="sessions-tab"
          className="space-y-6"
        >
          {selected.length > 0 ? (
            <SessionManagementInterface
              userId="current-user" // TODO: Get actual user ID from props or context
              goals={selected.map(goalId => ({
                id: goalId,
                title: goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                description: `Working on ${goalId.replace(/_/g, ' ')}`,
                category: 'mental-health',
                progress: goalProgresses?.find(gp => gp.goalId === goalId)?.progress || 0
              }))}
              userContext={{
                preferences: {
                  player_id: "current-user",
                  intensity_level: IntensityLevel.MEDIUM,
                  preferred_approaches: [],
                  conversation_style: ConversationStyle.SUPPORTIVE,
                  therapeutic_goals: selected,
                  primary_concerns: primaryConcerns,
                  character_name: "Alex",
                  preferred_setting: PreferredSetting.PEACEFUL_FOREST,
                  comfort_topics: ['nature', 'personal_growth'],
                  trigger_topics: [],
                  avoid_topics: [],
                  session_duration_preference: 60,
                  reminder_frequency: 'weekly' as const,
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  version: 1
                },
                goalProgresses: goalProgresses || []
              }}
              onSessionUpdate={(sessionId, session) => {
                setSessions(prev => {
                  const index = prev.findIndex(s => s.id === sessionId);
                  if (index >= 0) {
                    const updated = [...prev];
                    updated[index] = session;
                    return updated;
                  }
                  return [...prev, session];
                });
              }}
              onJourneyUpdate={(journey) => {
                setJourneyAnalysis(journey);
              }}
            />
          ) : (
            <div className="text-center py-12 bg-blue-50 rounded-lg border-2 border-dashed border-blue-200">
              <div className="text-blue-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 4v10m6-10v10m-6-4h6" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                No Therapeutic Goals Selected
              </h3>
              <p className="text-blue-700 mb-4">
                Select some therapeutic goals to start planning and managing your therapeutic sessions.
              </p>
              <button
                onClick={() => setActiveTab('goals')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Select Goals
              </button>
            </div>
          )}
        </div>
      )}

      {/* Real-Time Monitoring Tab */}
      {activeTab === 'monitoring' && (
        <div
          role="tabpanel"
          id="monitoring-panel"
          aria-labelledby="monitoring-tab"
          className="space-y-6"
        >
          {selected.length > 0 ? (
            <RealTimeMonitoringInterface
              sessionId={`session_${Date.now()}`}
              userId="current-user" // TODO: Get actual user ID from props or context
              therapeuticGoals={selected}
              onInterventionTriggered={(intervention: InterventionRecord) => {
                console.log('Intervention triggered:', intervention);
                // Handle intervention trigger - could show modal, notification, etc.
              }}
              onCrisisDetected={(riskAssessment: RiskAssessment) => {
                console.log('Crisis detected:', riskAssessment);
                // Handle crisis detection - show emergency resources, alert, etc.
              }}
              className="w-full"
            />
          ) : (
            <div className="text-center py-12 bg-red-50 rounded-lg border-2 border-dashed border-red-200">
              <div className="text-red-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-red-900 mb-2">
                No Therapeutic Goals Selected
              </h3>
              <p className="text-red-700 mb-4">
                Select some therapeutic goals to enable real-time monitoring and crisis detection capabilities.
              </p>
              <button
                onClick={() => setActiveTab('goals')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
              >
                Select Goals
              </button>
            </div>
          )}
        </div>
      )}

      {/* Selection Summary */}
      {(selected.length > 0 || primaryConcerns.length > 0) && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h3 className="font-medium text-primary-900 mb-3">Your Selections</h3>
          
          {selected.length > 0 && (
            <div className="mb-3">
              <h4 className="text-sm font-medium text-primary-800 mb-2">
                Therapeutic Goals ({selected.length}):
              </h4>
              <div className="flex flex-wrap gap-1">
                {selected.map((goal) => (
                  <span
                    key={goal}
                    className="inline-block px-2 py-1 text-xs bg-white rounded-full text-primary-700"
                  >
                    {goal.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
          )}

          {primaryConcerns.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-primary-800 mb-2">
                Primary Concerns ({primaryConcerns.length}):
              </h4>
              <div className="flex flex-wrap gap-1">
                {primaryConcerns.map((concern) => (
                  <span
                    key={concern}
                    className="inline-block px-2 py-1 text-xs bg-white rounded-full text-primary-700"
                  >
                    {concern}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Goal Relationship Analysis */}
      {selected.length > 1 && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4 mb-6">
          <div className="flex items-center mb-3">
            <svg className="w-5 h-5 text-indigo-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
            </svg>
            <h3 className="text-lg font-semibold text-indigo-900">🔗 Goal Relationship Analysis</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Compatibility Score */}
            <div className="bg-white rounded-lg p-3 border border-indigo-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-indigo-800">Overall Compatibility</span>
                <span className="text-lg font-bold text-indigo-600">
                  {Math.round(relationshipMap.overallCompatibility * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    relationshipMap.overallCompatibility >= 0.8 ? 'bg-green-500' :
                    relationshipMap.overallCompatibility >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${relationshipMap.overallCompatibility * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Therapeutic Coherence */}
            <div className="bg-white rounded-lg p-3 border border-indigo-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-indigo-800">Therapeutic Coherence</span>
                <span className="text-lg font-bold text-indigo-600">
                  {Math.round(relationshipMap.therapeuticCoherence * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    relationshipMap.therapeuticCoherence >= 0.8 ? 'bg-green-500' :
                    relationshipMap.therapeuticCoherence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${relationshipMap.therapeuticCoherence * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Conflicts */}
          {relationshipMap.conflicts.length > 0 && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-red-800 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Goal Conflicts Detected
              </h4>
              {relationshipMap.conflicts.map((conflict, index) => (
                <div key={index} className="mb-2 last:mb-0">
                  <p className="text-sm text-red-700 font-medium">
                    {conflict.description}
                  </p>
                  <p className="text-xs text-red-600 mt-1">
                    <strong>Resolution:</strong> {conflict.resolutionSuggestions[0]}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Complementary Suggestions */}
          {relationshipMap.complementarySuggestions.length > 0 && (
            <div className="mt-4 bg-emerald-50 border border-emerald-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-emerald-800 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Complementary Goal Suggestions
              </h4>
              {relationshipMap.complementarySuggestions.slice(0, 2).map((suggestion, index) => (
                <div key={index} className="mb-2 last:mb-0">
                  <p className="text-sm text-emerald-700 font-medium">
                    {findGoalLabel(suggestion.suggestedGoal)}
                  </p>
                  <p className="text-xs text-emerald-600 mt-1">
                    {suggestion.therapeuticBenefit}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Therapeutic Approach Alignment */}
      {selected.length > 0 && approachAnalysis.recommendedApproaches.length > 0 && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd" />
            </svg>
            Therapeutic Approach Alignment
          </h3>

          {/* Overall Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-purple-700">Treatment Coherence</span>
                <span className="text-sm text-purple-600">
                  {Math.round(approachAnalysis.overallCoherence * 100)}%
                </span>
              </div>
              <div className="w-full bg-purple-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    approachAnalysis.overallCoherence >= 0.8 ? 'bg-purple-600' :
                    approachAnalysis.overallCoherence >= 0.6 ? 'bg-purple-500' : 'bg-purple-400'
                  }`}
                  style={{ width: `${approachAnalysis.overallCoherence * 100}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-purple-700">Treatment Effectiveness</span>
                <span className="text-sm text-purple-600">
                  {Math.round(approachAnalysis.treatmentEffectivenessScore * 100)}%
                </span>
              </div>
              <div className="w-full bg-purple-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    approachAnalysis.treatmentEffectivenessScore >= 0.8 ? 'bg-purple-600' :
                    approachAnalysis.treatmentEffectivenessScore >= 0.6 ? 'bg-purple-500' : 'bg-purple-400'
                  }`}
                  style={{ width: `${approachAnalysis.treatmentEffectivenessScore * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Recommended Approaches */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-purple-800 mb-2">Recommended Therapeutic Approaches</h4>
            <div className="space-y-2">
              {approachAnalysis.recommendedApproaches.slice(0, 3).map((recommendation, index) => {
                const approachInfo = THERAPEUTIC_APPROACHES_INFO[recommendation.recommendedApproach];
                return (
                  <div key={index} className="bg-white border border-purple-200 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-medium text-purple-900">{approachInfo.name}</h5>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          recommendation.clinicalEvidence === 'high' ? 'bg-green-100 text-green-800' :
                          recommendation.clinicalEvidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {recommendation.clinicalEvidence} evidence
                        </span>
                        <span className="text-sm text-purple-600">
                          {Math.round(recommendation.confidence * 100)}% match
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{approachInfo.description}</p>
                    <p className="text-xs text-purple-700">
                      <strong>Best for:</strong> {approachInfo.bestFor.join(', ')}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Integration Recommendations */}
          {approachAnalysis.integrationRecommendations.length > 0 && (
            <div className="bg-white border border-purple-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-purple-800 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                </svg>
                Integration Guidance
              </h4>
              <div className="space-y-1">
                {approachAnalysis.integrationRecommendations.slice(0, 2).map((recommendation, index) => (
                  <p key={index} className="text-xs text-purple-700">
                    • {recommendation}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Guidance */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-green-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="font-medium text-green-900 mb-1">💡 Setting Therapeutic Goals</h3>
            <div className="text-green-800 text-sm space-y-1">
              <p>• <strong>Start with 3-5 goals</strong> to maintain focus without feeling overwhelmed</p>
              <p>• <strong>Be specific about concerns</strong> to help the AI provide more targeted support</p>
              <p>• <strong>Goals can evolve</strong> as you progress and discover new areas of growth</p>
              <p>• <strong>Balance aspirational and practical</strong> goals for sustainable progress</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TherapeuticGoalsSelector;
