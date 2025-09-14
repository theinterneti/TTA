import React from 'react';

interface ConversationProgressProps {
  progress: {
    current_stage: string;
    progress_percentage: number;
    completed_stages: string[];
  };
}

const ConversationProgress: React.FC<ConversationProgressProps> = ({ progress }) => {
  // Stage mapping for display
  const stageDisplayNames: Record<string, string> = {
    welcome: 'Welcome',
    identity: 'Identity',
    appearance: 'Appearance',
    background: 'Background',
    values: 'Values',
    relationships: 'Relationships',
    therapeutic_transition: 'Therapeutic Focus',
    concerns: 'Concerns',
    goals: 'Goals',
    preferences: 'Preferences',
    readiness: 'Readiness',
    summary: 'Summary',
    completion: 'Complete'
  };

  // Stage order for progress visualization
  const stageOrder = [
    'welcome',
    'identity',
    'appearance',
    'background',
    'values',
    'relationships',
    'therapeutic_transition',
    'concerns',
    'goals',
    'preferences',
    'readiness',
    'summary',
    'completion'
  ];

  const getCurrentStageIndex = () => {
    return stageOrder.indexOf(progress.current_stage);
  };

  const getStageStatus = (stage: string) => {
    if (progress.completed_stages.includes(stage)) {
      return 'completed';
    } else if (stage === progress.current_stage) {
      return 'current';
    } else {
      return 'upcoming';
    }
  };

  const getStageIcon = (stage: string, status: string) => {
    switch (status) {
      case 'completed':
        return (
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'current':
        return (
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
          </div>
        );
    }
  };

  const getProgressBarColor = () => {
    if (progress.progress_percentage >= 80) return 'bg-green-500';
    if (progress.progress_percentage >= 50) return 'bg-blue-500';
    if (progress.progress_percentage >= 25) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const getTherapeuticPhaseLabel = () => {
    const currentIndex = getCurrentStageIndex();
    
    if (currentIndex <= 2) {
      return 'Getting to Know You';
    } else if (currentIndex <= 5) {
      return 'Understanding Your Story';
    } else if (currentIndex <= 8) {
      return 'Therapeutic Exploration';
    } else if (currentIndex <= 10) {
      return 'Setting Your Path';
    } else {
      return 'Finalizing Your Companion';
    }
  };

  return (
    <div className="bg-gray-50 border-b border-gray-200 p-4">
      {/* Overall Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            {getTherapeuticPhaseLabel()}
          </span>
          <span className="text-sm text-gray-600">
            {progress.progress_percentage}% Complete
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ease-out ${getProgressBarColor()}`}
            style={{ width: `${progress.progress_percentage}%` }}
          ></div>
        </div>
      </div>

      {/* Stage Indicators - Mobile Responsive */}
      <div className="hidden md:block">
        <div className="flex justify-between items-center">
          {stageOrder.slice(0, 8).map((stage, index) => {
            const status = getStageStatus(stage);
            const displayName = stageDisplayNames[stage] || stage;
            
            return (
              <div key={stage} className="flex flex-col items-center">
                {getStageIcon(stage, status)}
                <span className={`text-xs mt-1 text-center ${
                  status === 'current' 
                    ? 'text-blue-600 font-medium' 
                    : status === 'completed'
                    ? 'text-green-600'
                    : 'text-gray-500'
                }`}>
                  {displayName}
                </span>
                
                {/* Connection line */}
                {index < stageOrder.slice(0, 8).length - 1 && (
                  <div className="absolute mt-4 ml-8 w-16 h-0.5 bg-gray-300"></div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Mobile View - Current Stage Only */}
      <div className="md:hidden">
        <div className="flex items-center justify-center space-x-3">
          {getStageIcon(progress.current_stage, 'current')}
          <div>
            <div className="text-sm font-medium text-gray-900">
              {stageDisplayNames[progress.current_stage] || progress.current_stage}
            </div>
            <div className="text-xs text-gray-600">
              Step {getCurrentStageIndex() + 1} of {stageOrder.length}
            </div>
          </div>
        </div>
      </div>

      {/* Therapeutic Context */}
      {progress.current_stage && (
        <div className="mt-3 text-center">
          <p className="text-xs text-gray-600 italic">
            {getTherapeuticContextMessage(progress.current_stage)}
          </p>
        </div>
      )}
    </div>
  );
};

// Helper function to provide therapeutic context for each stage
const getTherapeuticContextMessage = (stage: string): string => {
  const contextMessages: Record<string, string> = {
    welcome: "Creating a safe space for your journey of self-discovery",
    identity: "Understanding how you see yourself in the world",
    appearance: "Exploring your self-image and personal expression",
    background: "Honoring your unique story and experiences",
    values: "Discovering what matters most to you",
    relationships: "Understanding your connections with others",
    therapeutic_transition: "Gently moving into deeper therapeutic exploration",
    concerns: "Acknowledging what brings you here today",
    goals: "Envisioning the positive changes you seek",
    preferences: "Tailoring the therapeutic approach to your needs",
    readiness: "Assessing your readiness for growth and change",
    summary: "Bringing together your therapeutic companion",
    completion: "Celebrating the creation of your healing partner"
  };

  return contextMessages[stage] || "Continuing your therapeutic journey";
};

export default ConversationProgress;
