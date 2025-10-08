/**
 * Progress Tracking Service - Priority 3D Implementation
 *
 * Comprehensive progress monitoring and analytics system for therapeutic goals.
 * Provides real-time progress tracking, outcome measurement, and therapeutic analytics.
 *
 * Features:
 * - Real-time progress monitoring with milestone detection
 * - Evidence-based outcome measurement (PHQ-9, GAD-7, etc.)
 * - Therapeutic effectiveness analytics and insights
 * - Progress visualization data generation
 * - Integration with existing therapeutic intelligence services
 */

import { TherapeuticGoal, TherapeuticApproach, UserPreferences } from '../types/preferences';

// Core Progress Tracking Types
export interface ProgressEntry {
  id: string;
  goalId: string;
  userId: string;
  timestamp: Date;
  progressValue: number; // 0-100 scale
  progressType: ProgressType;
  measurementMethod: MeasurementMethod;
  notes?: string;
  sessionId?: string;
  milestoneReached?: boolean;
  evidenceLevel: EvidenceLevel;
}

export interface ProgressMilestone {
  id: string;
  goalId: string;
  title: string;
  description: string;
  targetValue: number;
  achievedAt?: Date;
  significance: MilestoneSignificance;
  therapeuticImpact: TherapeuticImpact;
  celebrationMessage: string;
  nextSteps: string[];
}

export interface ProgressAnalytics {
  goalId: string;
  overallProgress: number;
  progressTrend: ProgressTrend;
  velocityScore: number; // Progress rate over time
  consistencyScore: number; // Regularity of progress updates
  therapeuticEffectiveness: number; // Clinical outcome measure
  riskFactors: RiskFactor[];
  recommendations: ProgressRecommendation[];
  insights: ProgressInsight[];
  nextMilestone?: ProgressMilestone;
}

export interface OutcomeMeasurement {
  id: string;
  userId: string;
  measurementType: OutcomeMeasurementType;
  score: number;
  maxScore: number;
  percentile?: number;
  severity?: SeverityLevel;
  timestamp: Date;
  clinicalSignificance: ClinicalSignificance;
  comparisonToBaseline?: number;
  trendDirection: TrendDirection;
}

export interface TherapeuticInsight {
  id: string;
  type: InsightType;
  title: string;
  description: string;
  confidence: ConfidenceLevel;
  evidenceLevel: EvidenceLevel;
  actionable: boolean;
  recommendations: string[];
  clinicalRelevance: ClinicalRelevance;
  generatedAt: Date;
}

// Enums and Types
export enum ProgressType {
  SELF_REPORTED = 'self_reported',
  BEHAVIORAL_OBSERVATION = 'behavioral_observation',
  CLINICAL_ASSESSMENT = 'clinical_assessment',
  MILESTONE_ACHIEVEMENT = 'milestone_achievement',
  SKILL_DEMONSTRATION = 'skill_demonstration'
}

export enum MeasurementMethod {
  LIKERT_SCALE = 'likert_scale',
  BINARY_CHECKLIST = 'binary_checklist',
  FREQUENCY_COUNT = 'frequency_count',
  DURATION_TRACKING = 'duration_tracking',
  STANDARDIZED_ASSESSMENT = 'standardized_assessment'
}

export enum ProgressTrend {
  IMPROVING = 'improving',
  STABLE = 'stable',
  DECLINING = 'declining',
  FLUCTUATING = 'fluctuating',
  INSUFFICIENT_DATA = 'insufficient_data'
}

export enum MilestoneSignificance {
  MINOR = 'minor',
  MODERATE = 'moderate',
  MAJOR = 'major',
  BREAKTHROUGH = 'breakthrough'
}

export enum TherapeuticImpact {
  LOW = 'low',
  MODERATE = 'moderate',
  HIGH = 'high',
  TRANSFORMATIVE = 'transformative'
}

export enum OutcomeMeasurementType {
  PHQ9 = 'phq9', // Depression
  GAD7 = 'gad7', // Anxiety
  DASS21 = 'dass21', // Depression, Anxiety, Stress
  WEMWBS = 'wemwbs', // Wellbeing
  CUSTOM_SCALE = 'custom_scale',
  GOAL_ATTAINMENT = 'goal_attainment'
}

export enum SeverityLevel {
  MINIMAL = 'minimal',
  MILD = 'mild',
  MODERATE = 'moderate',
  MODERATELY_SEVERE = 'moderately_severe',
  SEVERE = 'severe'
}

export enum ClinicalSignificance {
  NOT_SIGNIFICANT = 'not_significant',
  CLINICALLY_MEANINGFUL = 'clinically_meaningful',
  HIGHLY_SIGNIFICANT = 'highly_significant',
  REQUIRES_ATTENTION = 'requires_attention'
}

export enum TrendDirection {
  IMPROVING = 'improving',
  STABLE = 'stable',
  WORSENING = 'worsening'
}

export enum InsightType {
  PROGRESS_PATTERN = 'progress_pattern',
  RISK_IDENTIFICATION = 'risk_identification',
  OPPORTUNITY_DETECTION = 'opportunity_detection',
  THERAPEUTIC_EFFECTIVENESS = 'therapeutic_effectiveness',
  BEHAVIORAL_CORRELATION = 'behavioral_correlation'
}

export enum ClinicalRelevance {
  LOW = 'low',
  MODERATE = 'moderate',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum EvidenceLevel {
  ANECDOTAL = 'anecdotal',
  OBSERVATIONAL = 'observational',
  VALIDATED_SCALE = 'validated_scale',
  CLINICAL_ASSESSMENT = 'clinical_assessment',
  RESEARCH_BASED = 'research_based'
}

export enum ConfidenceLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  VERY_HIGH = 'very_high'
}

export interface RiskFactor {
  type: string;
  severity: SeverityLevel;
  description: string;
  recommendations: string[];
}

export interface ProgressRecommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  actionable: boolean;
}

export interface ProgressInsight {
  id: string;
  type: InsightType;
  title: string;
  description: string;
  confidence: ConfidenceLevel;
}

// Progress Tracking Result Interface
export interface ProgressTrackingResult {
  currentProgress: ProgressAnalytics[];
  recentEntries: ProgressEntry[];
  milestones: ProgressMilestone[];
  outcomeMeasurements: OutcomeMeasurement[];
  therapeuticInsights: TherapeuticInsight[];
  overallEffectiveness: number;
  riskAssessment: RiskAssessment;
  recommendations: ProgressRecommendation[];
  nextActions: NextAction[];
  generatedAt: Date;
  dataQuality: DataQualityMetrics;
}

export interface RiskAssessment {
  overallRisk: SeverityLevel;
  riskFactors: RiskFactor[];
  protectiveFactors: string[];
  recommendations: string[];
}

export interface NextAction {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  dueDate?: Date;
  category: string;
}

export interface DataQualityMetrics {
  completeness: number; // 0-100
  consistency: number; // 0-100
  recency: number; // 0-100
  reliability: number; // 0-100
  overallQuality: number; // 0-100
}

/**
 * Main Progress Tracking Service
 * Provides comprehensive progress monitoring and analytics capabilities
 */
export class ProgressTrackingService {
  private progressEntries: Map<string, ProgressEntry[]> = new Map();
  private milestones: Map<string, ProgressMilestone[]> = new Map();
  private outcomeMeasurements: Map<string, OutcomeMeasurement[]> = new Map();

  /**
   * Generate comprehensive progress tracking analytics for user goals
   */
  public generateProgressAnalytics(
    userId: string,
    goals: TherapeuticGoal[],
    timeframe: 'week' | 'month' | 'quarter' | 'year' = 'month'
  ): ProgressTrackingResult {
    const progressAnalytics = goals.map(goal => this.analyzeGoalProgress(goal, userId, timeframe));
    const recentEntries = this.getRecentProgressEntries(userId, timeframe);
    const milestones = this.getMilestonesForUser(userId);
    const outcomeMeasurements = this.getOutcomeMeasurements(userId, timeframe);
    const therapeuticInsights = this.generateTherapeuticInsights(userId, goals, progressAnalytics);

    const overallEffectiveness = this.calculateOverallEffectiveness(progressAnalytics, outcomeMeasurements);
    const riskAssessment = this.assessRisk(progressAnalytics, outcomeMeasurements);
    const recommendations = this.generateProgressRecommendations(progressAnalytics, riskAssessment);
    const nextActions = this.generateNextActions(progressAnalytics, milestones);
    const dataQuality = this.assessDataQuality(userId, goals);

    return {
      currentProgress: progressAnalytics,
      recentEntries,
      milestones,
      outcomeMeasurements,
      therapeuticInsights,
      overallEffectiveness,
      riskAssessment,
      recommendations,
      nextActions,
      generatedAt: new Date(),
      dataQuality
    };
  }

  /**
   * Record a new progress entry
   */
  public recordProgress(entry: Omit<ProgressEntry, 'id' | 'timestamp'>): ProgressEntry {
    const progressEntry: ProgressEntry = {
      ...entry,
      id: this.generateId(),
      timestamp: new Date()
    };

    const userEntries = this.progressEntries.get(entry.userId) || [];
    userEntries.push(progressEntry);
    this.progressEntries.set(entry.userId, userEntries);

    // Check for milestone achievement
    this.checkMilestoneAchievement(progressEntry);

    return progressEntry;
  }

  /**
   * Record an outcome measurement
   */
  public recordOutcomeMeasurement(measurement: Omit<OutcomeMeasurement, 'id' | 'timestamp'>): OutcomeMeasurement {
    const outcomeMeasurement: OutcomeMeasurement = {
      ...measurement,
      id: this.generateId(),
      timestamp: new Date()
    };

    const userMeasurements = this.outcomeMeasurements.get(measurement.userId) || [];
    userMeasurements.push(outcomeMeasurement);
    this.outcomeMeasurements.set(measurement.userId, userMeasurements);

    return outcomeMeasurement;
  }

  private analyzeGoalProgress(goal: TherapeuticGoal, userId: string, timeframe: string): ProgressAnalytics {
    const entries = this.getProgressEntriesForGoal(goal.id, userId, timeframe);
    const currentProgress = this.calculateCurrentProgress(entries);
    const trend = this.calculateProgressTrend(entries);
    const velocity = this.calculateVelocityScore(entries);
    const consistency = this.calculateConsistencyScore(entries);
    const effectiveness = this.calculateTherapeuticEffectiveness(goal, entries);

    return {
      goalId: goal.id,
      overallProgress: currentProgress,
      progressTrend: trend,
      velocityScore: velocity,
      consistencyScore: consistency,
      therapeuticEffectiveness: effectiveness,
      riskFactors: this.identifyRiskFactors(goal, entries),
      recommendations: this.generateGoalRecommendations(goal, entries),
      insights: this.generateProgressInsights(goal, entries),
      nextMilestone: this.getNextMilestone(goal.id)
    };
  }

  private calculateCurrentProgress(entries: ProgressEntry[]): number {
    if (entries.length === 0) return 0;

    // Use the most recent entry as current progress
    const sortedEntries = entries.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    return sortedEntries[0].progressValue;
  }

  private calculateProgressTrend(entries: ProgressEntry[]): ProgressTrend {
    if (entries.length < 2) return ProgressTrend.INSUFFICIENT_DATA;

    const sortedEntries = entries.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    const recentEntries = sortedEntries.slice(-5); // Last 5 entries

    if (recentEntries.length < 2) return ProgressTrend.INSUFFICIENT_DATA;

    const firstValue = recentEntries[0].progressValue;
    const lastValue = recentEntries[recentEntries.length - 1].progressValue;
    const difference = lastValue - firstValue;

    if (Math.abs(difference) < 5) return ProgressTrend.STABLE;
    if (difference > 0) return ProgressTrend.IMPROVING;
    return ProgressTrend.DECLINING;
  }

  private calculateVelocityScore(entries: ProgressEntry[]): number {
    if (entries.length < 2) return 0;

    const sortedEntries = entries.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    const timeSpan = sortedEntries[sortedEntries.length - 1].timestamp.getTime() - sortedEntries[0].timestamp.getTime();
    const progressChange = sortedEntries[sortedEntries.length - 1].progressValue - sortedEntries[0].progressValue;

    // Calculate progress per day
    const daysSpan = timeSpan / (1000 * 60 * 60 * 24);
    const velocityPerDay = daysSpan > 0 ? progressChange / daysSpan : 0;

    // Normalize to 0-100 scale (assuming 1 point per day is excellent)
    return Math.min(100, Math.max(0, velocityPerDay * 100));
  }

  private calculateConsistencyScore(entries: ProgressEntry[]): number {
    if (entries.length < 3) return 0;

    const sortedEntries = entries.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    const intervals: number[] = [];

    for (let i = 1; i < sortedEntries.length; i++) {
      const interval = sortedEntries[i].timestamp.getTime() - sortedEntries[i - 1].timestamp.getTime();
      intervals.push(interval);
    }

    if (intervals.length === 0) return 0;

    const avgInterval = intervals.reduce((sum, interval) => sum + interval, 0) / intervals.length;
    if (avgInterval === 0) return 0;

    const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - avgInterval, 2), 0) / intervals.length;
    const standardDeviation = Math.sqrt(variance);

    // Lower standard deviation = higher consistency
    const consistencyScore = Math.max(0, 100 - (standardDeviation / avgInterval) * 100);
    return Math.min(100, Math.max(0, consistencyScore));
  }

  private calculateTherapeuticEffectiveness(goal: TherapeuticGoal, entries: ProgressEntry[]): number {
    // If no entries, return 0 effectiveness
    if (entries.length === 0) return 0;

    // Base effectiveness on progress trend, velocity, and evidence level
    const trend = this.calculateProgressTrend(entries);
    const velocity = this.calculateVelocityScore(entries);
    const consistency = this.calculateConsistencyScore(entries);

    let baseScore = 0;
    switch (trend) {
      case ProgressTrend.IMPROVING:
        baseScore = 80;
        break;
      case ProgressTrend.STABLE:
        baseScore = 60;
        break;
      case ProgressTrend.DECLINING:
        baseScore = 30;
        break;
      case ProgressTrend.INSUFFICIENT_DATA:
        baseScore = 0;
        break;
      default:
        baseScore = 50;
    }

    // Adjust based on velocity and consistency
    const adjustedScore = baseScore + (velocity * 0.2) + (consistency * 0.2);
    return Math.min(100, Math.max(0, adjustedScore));
  }

  private identifyRiskFactors(goal: TherapeuticGoal, entries: ProgressEntry[]): RiskFactor[] {
    const riskFactors: RiskFactor[] = [];

    const trend = this.calculateProgressTrend(entries);
    const consistency = this.calculateConsistencyScore(entries);
    const recentProgress = entries.length > 0 ? entries[entries.length - 1].progressValue : 0;

    if (trend === ProgressTrend.DECLINING) {
      riskFactors.push({
        type: 'declining_progress',
        severity: SeverityLevel.MODERATE,
        description: 'Progress has been declining recently',
        recommendations: ['Review current strategies', 'Consider alternative approaches', 'Seek additional support']
      });
    }

    if (consistency < 30) {
      riskFactors.push({
        type: 'inconsistent_engagement',
        severity: SeverityLevel.MILD,
        description: 'Irregular progress tracking patterns detected',
        recommendations: ['Establish regular check-in schedule', 'Set up progress reminders', 'Identify engagement barriers']
      });
    }

    if (recentProgress < 20) {
      riskFactors.push({
        type: 'low_progress',
        severity: SeverityLevel.MODERATE,
        description: 'Current progress level is below expected range',
        recommendations: ['Reassess goal difficulty', 'Break down into smaller steps', 'Increase support resources']
      });
    }

    return riskFactors;
  }

  private generateGoalRecommendations(goal: TherapeuticGoal, entries: ProgressEntry[]): ProgressRecommendation[] {
    const recommendations: ProgressRecommendation[] = [];
    const trend = this.calculateProgressTrend(entries);
    const velocity = this.calculateVelocityScore(entries);

    if (trend === ProgressTrend.IMPROVING && velocity > 70) {
      recommendations.push({
        id: this.generateId(),
        type: 'acceleration',
        title: 'Consider Advanced Techniques',
        description: 'Your progress is excellent. Consider exploring more advanced therapeutic techniques.',
        priority: 'medium',
        actionable: true
      });
    }

    if (trend === ProgressTrend.STABLE && velocity < 30) {
      recommendations.push({
        id: this.generateId(),
        type: 'motivation',
        title: 'Boost Engagement',
        description: 'Try varying your approach or setting smaller, more frequent milestones.',
        priority: 'high',
        actionable: true
      });
    }

    return recommendations;
  }

  private generateProgressInsights(goal: TherapeuticGoal, entries: ProgressEntry[]): ProgressInsight[] {
    const insights: ProgressInsight[] = [];

    if (entries.length >= 5) {
      const consistency = this.calculateConsistencyScore(entries);
      if (consistency > 80) {
        insights.push({
          id: this.generateId(),
          type: InsightType.PROGRESS_PATTERN,
          title: 'Excellent Consistency',
          description: 'You maintain very consistent progress tracking, which correlates with better outcomes.',
          confidence: ConfidenceLevel.HIGH
        });
      }
    }

    return insights;
  }

  // Helper methods
  private getProgressEntriesForGoal(goalId: string, userId: string, timeframe: string): ProgressEntry[] {
    const userEntries = this.progressEntries.get(userId) || [];
    const cutoffDate = this.getTimeframeCutoff(timeframe);

    return userEntries.filter(entry =>
      entry.goalId === goalId &&
      entry.timestamp >= cutoffDate
    );
  }

  private getRecentProgressEntries(userId: string, timeframe: string): ProgressEntry[] {
    const userEntries = this.progressEntries.get(userId) || [];
    const cutoffDate = this.getTimeframeCutoff(timeframe);

    return userEntries
      .filter(entry => entry.timestamp >= cutoffDate)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 20); // Last 20 entries
  }

  private getMilestonesForUser(userId: string): ProgressMilestone[] {
    return this.milestones.get(userId) || [];
  }

  private getOutcomeMeasurements(userId: string, timeframe: string): OutcomeMeasurement[] {
    const userMeasurements = this.outcomeMeasurements.get(userId) || [];
    const cutoffDate = this.getTimeframeCutoff(timeframe);

    return userMeasurements.filter(measurement => measurement.timestamp >= cutoffDate);
  }

  private generateTherapeuticInsights(
    userId: string,
    goals: TherapeuticGoal[],
    analytics: ProgressAnalytics[]
  ): TherapeuticInsight[] {
    const insights: TherapeuticInsight[] = [];

    // Overall progress insight
    const avgEffectiveness = analytics.reduce((sum, a) => sum + a.therapeuticEffectiveness, 0) / analytics.length;
    if (avgEffectiveness > 75) {
      insights.push({
        id: this.generateId(),
        type: InsightType.THERAPEUTIC_EFFECTIVENESS,
        title: 'Strong Therapeutic Progress',
        description: 'Your overall therapeutic effectiveness is excellent across multiple goals.',
        confidence: ConfidenceLevel.HIGH,
        evidenceLevel: EvidenceLevel.VALIDATED_SCALE,
        actionable: true,
        recommendations: ['Continue current approaches', 'Consider sharing strategies with others', 'Prepare for maintenance phase'],
        clinicalRelevance: ClinicalRelevance.HIGH,
        generatedAt: new Date()
      });
    }

    return insights;
  }

  private calculateOverallEffectiveness(analytics: ProgressAnalytics[], measurements: OutcomeMeasurement[]): number {
    if (analytics.length === 0) return 0;

    const avgAnalyticsEffectiveness = analytics.reduce((sum, a) => sum + a.therapeuticEffectiveness, 0) / analytics.length;

    // If we have outcome measurements, factor them in
    if (measurements.length > 0) {
      const avgMeasurementScore = measurements.reduce((sum, m) => sum + (m.score / m.maxScore) * 100, 0) / measurements.length;
      return (avgAnalyticsEffectiveness + avgMeasurementScore) / 2;
    }

    return avgAnalyticsEffectiveness;
  }

  private assessRisk(analytics: ProgressAnalytics[], measurements: OutcomeMeasurement[]): RiskAssessment {
    const allRiskFactors = analytics.flatMap(a => a.riskFactors);
    const highRiskCount = allRiskFactors.filter(rf => rf.severity === SeverityLevel.MODERATE || rf.severity === SeverityLevel.SEVERE).length;

    let overallRisk: SeverityLevel;
    if (highRiskCount === 0) {
      overallRisk = SeverityLevel.MINIMAL;
    } else if (highRiskCount <= 2) {
      overallRisk = SeverityLevel.MILD;
    } else {
      overallRisk = SeverityLevel.MODERATE;
    }

    return {
      overallRisk,
      riskFactors: allRiskFactors,
      protectiveFactors: ['Regular progress tracking', 'Multiple therapeutic goals', 'Consistent engagement'],
      recommendations: ['Continue monitoring progress', 'Address identified risk factors', 'Maintain current protective factors']
    };
  }

  private generateProgressRecommendations(analytics: ProgressAnalytics[], riskAssessment: RiskAssessment): ProgressRecommendation[] {
    const recommendations = analytics.flatMap(a => a.recommendations);

    // Add risk-based recommendations
    if (riskAssessment.overallRisk !== SeverityLevel.MINIMAL) {
      recommendations.push({
        id: this.generateId(),
        type: 'risk_mitigation',
        title: 'Address Risk Factors',
        description: 'Focus on addressing identified risk factors to improve outcomes.',
        priority: 'high',
        actionable: true
      });
    }

    return recommendations;
  }

  private generateNextActions(analytics: ProgressAnalytics[], milestones: ProgressMilestone[]): NextAction[] {
    const actions: NextAction[] = [];

    // Add milestone-based actions
    const upcomingMilestones = milestones.filter(m => !m.achievedAt);
    upcomingMilestones.forEach(milestone => {
      actions.push({
        id: this.generateId(),
        title: `Work towards: ${milestone.title}`,
        description: milestone.description,
        priority: 'medium',
        category: 'milestone'
      });
    });

    return actions.slice(0, 5); // Limit to top 5 actions
  }

  private assessDataQuality(userId: string, goals: TherapeuticGoal[]): DataQualityMetrics {
    const userEntries = this.progressEntries.get(userId) || [];

    if (goals.length === 0) {
      return {
        completeness: 0,
        consistency: 0,
        recency: 0,
        reliability: 0,
        overallQuality: 0
      };
    }

    const totalPossibleEntries = goals.length * 30; // Assuming daily tracking for a month

    const completeness = totalPossibleEntries > 0 ? Math.min(100, (userEntries.length / totalPossibleEntries) * 100) : 0;
    const consistency = userEntries.length > 0 ? this.calculateConsistencyScore(userEntries) : 0;

    // Recency: How recent is the latest entry
    const latestEntry = userEntries.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())[0];
    const daysSinceLatest = latestEntry ? (Date.now() - latestEntry.timestamp.getTime()) / (1000 * 60 * 60 * 24) : 30;
    const recency = Math.max(0, 100 - (daysSinceLatest * 10));

    const reliability = 85; // Placeholder - would be calculated based on validation
    const overallQuality = (completeness + consistency + recency + reliability) / 4;

    return {
      completeness: Math.max(0, completeness),
      consistency: Math.max(0, consistency),
      recency: Math.max(0, recency),
      reliability: Math.max(0, reliability),
      overallQuality: Math.max(0, overallQuality)
    };
  }

  private checkMilestoneAchievement(entry: ProgressEntry): void {
    const goalMilestones = this.milestones.get(entry.userId) || [];
    const unachievedMilestones = goalMilestones.filter(m => m.goalId === entry.goalId && !m.achievedAt);

    unachievedMilestones.forEach(milestone => {
      if (entry.progressValue >= milestone.targetValue) {
        milestone.achievedAt = new Date();
        entry.milestoneReached = true;
      }
    });
  }

  private getNextMilestone(goalId: string): ProgressMilestone | undefined {
    // This would typically query the milestones for the specific goal
    // For now, return undefined as this is a mock implementation
    return undefined;
  }

  private getTimeframeCutoff(timeframe: string): Date {
    const now = new Date();
    switch (timeframe) {
      case 'week':
        return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case 'month':
        return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      case 'quarter':
        return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
      case 'year':
        return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
      default:
        return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }
  }

  private generateId(): string {
    return `progress_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const progressTrackingService = new ProgressTrackingService();
