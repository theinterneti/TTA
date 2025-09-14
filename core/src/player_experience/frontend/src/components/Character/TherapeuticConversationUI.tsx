import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { 
  addMessage, 
  setTypingStatus, 
  handleWebSocketMessage,
  selectProgress,
  selectMessages,
  selectIsConversationActive
} from '../../store/slices/conversationalCharacterSlice';

interface TherapeuticConversationUIProps {
  onSendMessage: (message: string) => void;
  isConnected: boolean;
  connectionError?: string | null;
}

const TherapeuticConversationUI: React.FC<TherapeuticConversationUIProps> = ({
  onSendMessage,
  isConnected,
  connectionError
}) => {
  const dispatch = useDispatch();
  const progress = useSelector(selectProgress);
  const messages = useSelector(selectMessages);
  const isConversationActive = useSelector(selectIsConversationActive);
  const { isTyping } = useSelector((state: RootState) => state.conversationalCharacter);

  const [inputValue, setInputValue] = useState('');
  const [showTherapeuticContext, setShowTherapeuticContext] = useState(true);

  // Get therapeutic context based on current stage
  const getTherapeuticContext = () => {
    const contextMessages: Record<string, { 
      title: string; 
      message: string; 
      tips: string[];
      encouragement: string;
    }> = {
      welcome: {
        title: "Welcome to Your Safe Space",
        message: "This is a judgment-free environment where you can share as much or as little as feels comfortable.",
        tips: [
          "Take your time with each response",
          "There are no right or wrong answers",
          "You can pause or stop at any time"
        ],
        encouragement: "You've taken a brave first step by being here."
      },
      identity: {
        title: "Exploring Your Identity",
        message: "Understanding how you see yourself is an important part of your therapeutic journey.",
        tips: [
          "Share what feels authentic to you",
          "Your identity is unique and valid",
          "It's okay if you're still figuring things out"
        ],
        encouragement: "Your self-awareness is a strength."
      },
      appearance: {
        title: "Your Self-Image",
        message: "How we see ourselves often reflects our inner world and self-perception.",
        tips: [
          "Focus on what makes you feel like yourself",
          "There's beauty in uniqueness",
          "Self-acceptance is a journey"
        ],
        encouragement: "You are worthy of love and acceptance exactly as you are."
      },
      background: {
        title: "Your Unique Story",
        message: "Every experience has shaped who you are today, and your story matters.",
        tips: [
          "Share what feels significant to you",
          "Both challenges and triumphs are part of growth",
          "Your experiences are valid"
        ],
        encouragement: "Your resilience in sharing your story shows incredible courage."
      },
      values: {
        title: "What Matters Most",
        message: "Understanding your values helps guide decisions and creates meaning in life.",
        tips: [
          "Think about what brings you fulfillment",
          "Values can evolve over time",
          "Living aligned with values promotes wellbeing"
        ],
        encouragement: "Your values are your inner compass guiding you forward."
      },
      therapeutic_transition: {
        title: "Deepening Our Exploration",
        message: "We're now moving into more therapeutic territory. Remember, this is still your safe space.",
        tips: [
          "It's normal to feel vulnerable here",
          "You're in control of what you share",
          "Healing happens at your own pace"
        ],
        encouragement: "Your willingness to explore deeper shows tremendous strength."
      },
      concerns: {
        title: "Acknowledging Your Challenges",
        message: "Recognizing what brings you here takes courage and is the first step toward healing.",
        tips: [
          "Many people share similar struggles",
          "Seeking help is a sign of strength",
          "You don't have to face this alone"
        ],
        encouragement: "By acknowledging your concerns, you're already on the path to positive change."
      },
      goals: {
        title: "Envisioning Your Growth",
        message: "Setting therapeutic goals gives direction and hope to your healing journey.",
        tips: [
          "Goals can be big or small",
          "Progress isn't always linear",
          "Celebrate small victories"
        ],
        encouragement: "Your vision for positive change is the foundation of transformation."
      },
      preferences: {
        title: "Tailoring Your Journey",
        message: "Everyone heals differently. Let's find the approach that works best for you.",
        tips: [
          "Trust your instincts about what feels right",
          "It's okay to have preferences",
          "You can adjust your approach over time"
        ],
        encouragement: "Knowing yourself and your needs is a form of self-care."
      },
      readiness: {
        title: "Assessing Your Readiness",
        message: "Readiness for change varies and can fluctuate - that's completely normal.",
        tips: [
          "Readiness can grow over time",
          "Small steps count as progress",
          "It's okay to start where you are"
        ],
        encouragement: "Your honest self-assessment shows wisdom and self-awareness."
      }
    };

    return contextMessages[progress.current_stage] || {
      title: "Your Therapeutic Journey",
      message: "You're doing great. Keep sharing what feels right for you.",
      tips: ["Take your time", "You're in control", "Every step matters"],
      encouragement: "You're making progress on your healing journey."
    };
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !isConnected || !isConversationActive) return;

    // Add user message to store
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user' as const,
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    dispatch(addMessage(userMessage));
    dispatch(setTypingStatus(true));

    // Send to parent component
    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStageColor = () => {
    const stageIndex = ['welcome', 'identity', 'appearance', 'background', 'values', 
                      'therapeutic_transition', 'concerns', 'goals', 'preferences', 'readiness'].indexOf(progress.current_stage);
    
    if (stageIndex <= 2) return 'bg-blue-50 border-blue-200';
    if (stageIndex <= 5) return 'bg-green-50 border-green-200';
    if (stageIndex <= 8) return 'bg-purple-50 border-purple-200';
    return 'bg-indigo-50 border-indigo-200';
  };

  const getProgressPhase = () => {
    const stageIndex = ['welcome', 'identity', 'appearance', 'background', 'values', 
                      'therapeutic_transition', 'concerns', 'goals', 'preferences', 'readiness'].indexOf(progress.current_stage);
    
    if (stageIndex <= 2) return { phase: 'Getting to Know You', color: 'text-blue-600' };
    if (stageIndex <= 5) return { phase: 'Understanding Your Story', color: 'text-green-600' };
    if (stageIndex <= 8) return { phase: 'Therapeutic Exploration', color: 'text-purple-600' };
    return { phase: 'Setting Your Path', color: 'text-indigo-600' };
  };

  const therapeuticContext = getTherapeuticContext();
  const progressPhase = getProgressPhase();

  return (
    <div className="flex flex-col h-full">
      {/* Therapeutic Context Panel */}
      {showTherapeuticContext && (
        <div className={`p-4 border-b ${getStageColor()} transition-all duration-300`}>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-semibold text-gray-900">{therapeuticContext.title}</h3>
              <p className={`text-sm ${progressPhase.color} font-medium`}>
                {progressPhase.phase}
              </p>
            </div>
            <button
              onClick={() => setShowTherapeuticContext(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Hide therapeutic context"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <p className="text-sm text-gray-700 mb-3">{therapeuticContext.message}</p>
          
          {/* Tips */}
          <div className="mb-3">
            <h4 className="text-xs font-medium text-gray-600 mb-1">Helpful Tips:</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              {therapeuticContext.tips.map((tip, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
          
          {/* Encouragement */}
          <div className="bg-white bg-opacity-50 rounded-lg p-2">
            <p className="text-xs italic text-gray-700">
              💙 {therapeuticContext.encouragement}
            </p>
          </div>
        </div>
      )}

      {/* Show Context Button (when hidden) */}
      {!showTherapeuticContext && (
        <div className="p-2 border-b border-gray-200">
          <button
            onClick={() => setShowTherapeuticContext(true)}
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center transition-colors"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Show therapeutic guidance
          </button>
        </div>
      )}

      {/* Connection Status */}
      {!isConnected && (
        <div className="p-3 bg-red-50 border-b border-red-200">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
            <span className="text-sm text-red-700">
              {connectionError || 'Connection lost. Attempting to reconnect...'}
            </span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex flex-col space-y-3">
          {/* Therapeutic Reminder */}
          <div className="text-xs text-gray-500 text-center">
            This is a safe, confidential space. Share what feels comfortable for you.
          </div>
          
          {/* Input Field */}
          <div className="flex space-x-3">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share your thoughts..."
                className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
                disabled={!isConnected || !isConversationActive}
              />
              
              {/* Character count and guidance */}
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-400">
                  {inputValue.length > 0 && `${inputValue.length} characters`}
                </span>
                <span className="text-xs text-gray-500">
                  Press Enter to send, Shift+Enter for new line
                </span>
              </div>
            </div>
            
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || !isConnected || !isConversationActive}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors self-start"
            >
              Send
            </button>
          </div>
          
          {/* Therapeutic Actions */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => onSendMessage("I need a moment to think about this.")}
              disabled={!isConnected || !isConversationActive}
              className="text-xs text-gray-600 hover:text-gray-800 underline disabled:text-gray-400 disabled:no-underline"
            >
              I need a moment
            </button>
            <button
              onClick={() => onSendMessage("Can you rephrase that question?")}
              disabled={!isConnected || !isConversationActive}
              className="text-xs text-gray-600 hover:text-gray-800 underline disabled:text-gray-400 disabled:no-underline"
            >
              Rephrase question
            </button>
            <button
              onClick={() => onSendMessage("I'd prefer not to answer that right now.")}
              disabled={!isConnected || !isConversationActive}
              className="text-xs text-gray-600 hover:text-gray-800 underline disabled:text-gray-400 disabled:no-underline"
            >
              Skip for now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TherapeuticConversationUI;
