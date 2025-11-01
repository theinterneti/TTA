import React, { useState } from 'react';
import { GoalProgress } from '../../../services/goalProgressService';
import { TherapeuticApproachAnalysis } from '../../../services/therapeuticApproachAlignmentService';

interface JourneyStage {
  id: string;
  title: string;
  description: string;
  goals: string[];
  approaches: string[];
  progress: number;
  status: 'completed' | 'current' | 'upcoming' | 'blocked';
  estimatedDuration: string;
  milestones: string[];
  icon: string;
}

interface TherapeuticJourneyMapProps {
  selectedGoals: string[];
  goalProgresses: GoalProgress[];
  approachAnalysis: TherapeuticApproachAnalysis;
  className?: string;
  onStageClick?: (stageId: string) => void;
}

const TherapeuticJourneyMap: React.FC<TherapeuticJourneyMapProps> = ({
  selectedGoals,
  goalProgresses,
  approachAnalysis,
  className = '',
  onStageClick
}) => {
  const [selectedStage, setSelectedStage] = useState<string | null>(null);

  // Helper function to get goal label
  const getGoalLabel = (goalId: string): string => {
    return goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Generate journey stages based on selected goals and progress
  const generateJourneyStages = (): JourneyStage[] => {
    if (!selectedGoals.length) return [];

    const stages: JourneyStage[] = [];

    // Stage 1: Foundation Building
    const foundationGoals = selectedGoals.filter(goal =>
      ['mindfulness_practice', 'self_esteem_building', 'emotional_regulation'].includes(goal)
    );

    if (foundationGoals.length > 0) {
      const avgProgress = foundationGoals.reduce((sum, goalId) => {
        const progress = goalProgresses.find(gp => gp.goalId === goalId)?.progress || 0;
        return sum + progress;
      }, 0) / foundationGoals.length;

      stages.push({
        id: 'foundation',
        title: 'Foundation Building',
        description: 'Establishing core therapeutic skills and self-awareness',
        goals: foundationGoals,
        approaches: ['Mindfulness-Based Therapy', 'CBT', 'Humanistic Therapy'],
        progress: avgProgress,
        status: avgProgress >= 75 ? 'completed' : avgProgress >= 25 ? 'current' : 'upcoming',
        estimatedDuration: '4-8 weeks',
        milestones: [
          'Daily mindfulness practice established',
          'Basic emotional awareness developed',
          'Self-compassion skills learned'
        ],
        icon: '🌱'
      });
    }

    // Stage 2: Skill Development
    const skillGoals = selectedGoals.filter(goal =>
      ['anxiety_reduction', 'stress_management', 'communication_improvement', 'relationship_skills'].includes(goal)
    );

    if (skillGoals.length > 0) {
      const avgProgress = skillGoals.reduce((sum, goalId) => {
        const progress = goalProgresses.find(gp => gp.goalId === goalId)?.progress || 0;
        return sum + progress;
      }, 0) / skillGoals.length;

      const foundationComplete = stages.find(s => s.id === 'foundation')?.status === 'completed';

      stages.push({
        id: 'skill_development',
        title: 'Skill Development',
        description: 'Building specific therapeutic skills and coping strategies',
        goals: skillGoals,
        approaches: ['CBT', 'DBT', 'ACT'],
        progress: avgProgress,
        status: !foundationComplete ? 'blocked' : avgProgress >= 75 ? 'completed' : avgProgress >= 25 ? 'current' : 'upcoming',
        estimatedDuration: '6-12 weeks',
        milestones: [
          'Coping strategies mastered',
          'Communication skills improved',
          'Anxiety management techniques learned'
        ],
        icon: '🛠️'
      });
    }

    // Stage 3: Integration & Application
    const integrationGoals = selectedGoals.filter(goal =>
      ['work_life_balance', 'perfectionism_reduction', 'anger_management'].includes(goal)
    );

    if (integrationGoals.length > 0) {
      const avgProgress = integrationGoals.reduce((sum, goalId) => {
        const progress = goalProgresses.find(gp => gp.goalId === goalId)?.progress || 0;
        return sum + progress;
      }, 0) / integrationGoals.length;

      const skillsComplete = stages.find(s => s.id === 'skill_development')?.status === 'completed';

      stages.push({
        id: 'integration',
        title: 'Integration & Application',
        description: 'Applying skills to real-world situations and relationships',
        goals: integrationGoals,
        approaches: ['ACT', 'Humanistic Therapy', 'Psychodynamic Therapy'],
        progress: avgProgress,
        status: !skillsComplete ? 'blocked' : avgProgress >= 75 ? 'completed' : avgProgress >= 25 ? 'current' : 'upcoming',
        estimatedDuration: '8-16 weeks',
        milestones: [
          'Skills applied in daily life',
          'Relationship patterns improved',
          'Work-life balance achieved'
        ],
        icon: '🌟'
      });
    }

    // Stage 4: Healing & Recovery
    const healingGoals = selectedGoals.filter(goal =>
      ['trauma_recovery', 'grief_processing', 'addiction_recovery'].includes(goal)
    );

    if (healingGoals.length > 0) {
      const avgProgress = healingGoals.reduce((sum, goalId) => {
        const progress = goalProgresses.find(gp => gp.goalId === goalId)?.progress || 0;
        return sum + progress;
      }, 0) / healingGoals.length;

      stages.push({
        id: 'healing',
        title: 'Healing & Recovery',
        description: 'Deep healing work and trauma processing',
        goals: healingGoals,
        approaches: ['Somatic Therapy', 'EMDR', 'Narrative Therapy'],
        progress: avgProgress,
        status: avgProgress >= 75 ? 'completed' : avgProgress >= 25 ? 'current' : 'upcoming',
        estimatedDuration: '12-24 weeks',
        milestones: [
          'Trauma symptoms reduced',
          'Grief processed healthily',
          'Recovery milestones achieved'
        ],
        icon: '🕊️'
      });
    }

    // Stage 5: Maintenance & Growth
    if (stages.some(s => s.status === 'completed')) {
      stages.push({
        id: 'maintenance',
        title: 'Maintenance & Growth',
        description: 'Maintaining progress and continued personal growth',
        goals: selectedGoals,
        approaches: ['Ongoing Support', 'Peer Groups', 'Self-Directed Practice'],
        progress: 0,
        status: 'upcoming',
        estimatedDuration: 'Ongoing',
        milestones: [
          'Regular self-assessment',
          'Continued skill practice',
          'Support network maintained'
        ],
        icon: '🌳'
      });
    }

    return stages;
  };

  const journeyStages = generateJourneyStages();

  // Get status color
  const getStatusColor = (status: JourneyStage['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-100 border-green-300 text-green-800';
      case 'current': return 'bg-blue-100 border-blue-300 text-blue-800';
      case 'upcoming': return 'bg-gray-100 border-gray-300 text-gray-600';
      case 'blocked': return 'bg-red-100 border-red-300 text-red-600';
      default: return 'bg-gray-100 border-gray-300 text-gray-600';
    }
  };

  // Get progress bar color
  const getProgressColor = (progress: number) => {
    if (progress >= 75) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  if (!selectedGoals.length) {
    return (
      <div className={`bg-gray-50 rounded-lg p-8 text-center ${className}`}>
        <div className="text-4xl mb-4">🗺️</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Therapeutic Journey</h3>
        <p className="text-gray-600">Select therapeutic goals to see your personalized journey map</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Therapeutic Journey Map</h3>
          <p className="text-gray-600">Your personalized path to therapeutic goals</p>
        </div>
        <div className="text-sm text-gray-500">
          {journeyStages.filter(s => s.status === 'completed').length} of {journeyStages.length} stages completed
        </div>
      </div>

      {/* Journey Timeline */}
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Stages */}
        <div className="space-y-8">
          {journeyStages.map((stage, index) => (
            <div key={stage.id} className="relative flex items-start">
              {/* Stage icon */}
              <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full border-4 ${getStatusColor(stage.status)} cursor-pointer transition-all hover:scale-105`}
                   onClick={() => {
                     setSelectedStage(selectedStage === stage.id ? null : stage.id);
                     onStageClick?.(stage.id);
                   }}>
                <span className="text-2xl">{stage.icon}</span>
              </div>

              {/* Stage content */}
              <div className="ml-6 flex-1">
                <div className={`rounded-lg border-2 p-4 transition-all ${
                  selectedStage === stage.id ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-lg font-semibold text-gray-900">{stage.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(stage.status)}`}>
                      {stage.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gray-600 mb-3">{stage.description}</p>

                  {/* Progress bar */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium">{Math.round(stage.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${getProgressColor(stage.progress)}`}
                        style={{ width: `${stage.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Stage details (expanded) */}
                  {selectedStage === stage.id && (
                    <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                      <div>
                        <h5 className="font-medium text-gray-900 mb-1">Goals</h5>
                        <div className="flex flex-wrap gap-1">
                          {stage.goals.map(goalId => (
                            <span key={goalId} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                              {getGoalLabel(goalId)}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-900 mb-1">Therapeutic Approaches</h5>
                        <div className="flex flex-wrap gap-1">
                          {stage.approaches.map(approach => (
                            <span key={approach} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm">
                              {approach}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-900 mb-1">Key Milestones</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {stage.milestones.map((milestone, idx) => (
                            <li key={idx} className="flex items-center">
                              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></span>
                              {milestone}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>Estimated Duration: {stage.estimatedDuration}</span>
                        {stage.status === 'blocked' && (
                          <span className="text-red-600">⚠️ Complete previous stage first</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Journey insights */}
      <div className="mt-8 pt-6 border-t border-gray-100">
        <h4 className="font-semibold text-gray-900 mb-3">Journey Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="font-medium text-blue-900">Current Focus</div>
            <div className="text-blue-700">
              {journeyStages.find(s => s.status === 'current')?.title || 'Getting Started'}
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="font-medium text-green-900">Overall Progress</div>
            <div className="text-green-700">
              {Math.round(journeyStages.reduce((sum, s) => sum + s.progress, 0) / journeyStages.length)}% Complete
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="font-medium text-purple-900">Estimated Timeline</div>
            <div className="text-purple-700">
              {journeyStages.length * 8}-{journeyStages.length * 16} weeks
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TherapeuticJourneyMap;
