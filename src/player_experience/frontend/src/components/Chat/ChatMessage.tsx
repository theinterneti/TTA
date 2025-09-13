import React from 'react';
import InteractiveButton from './InteractiveButton';
import GuidedExercise from './GuidedExercise';
import ProgressFeedback from './ProgressFeedback';

interface ChatMessageProps {
  message: {
    id: string;
    type: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
    metadata?: {
      therapeutic_technique?: string;
      safety_level?: 'safe' | 'caution' | 'crisis';
      safety?: {
        crisis?: boolean;
      };
      interactive_elements?: {
        buttons?: Array<{
          id: string;
          text: string;
          action: string;
          variant?: 'primary' | 'secondary' | 'therapeutic' | 'crisis' | 'success';
          metadata?: {
            therapeutic_technique?: string;
            safety_level?: 'safe' | 'caution' | 'crisis';
            expected_outcome?: string;
            confidence_level?: number;
          };
        }>;
        guided_exercise?: {
          type: string;
          instructions: string;
          steps: string[];
          duration?: number;
          interactive?: boolean;
        };
        progress_feedback?: {
          type: 'milestone' | 'achievement' | 'progress' | 'encouragement';
          title: string;
          description: string;
          progress?: {
            current: number;
            total: number;
            unit?: string;
          };
          milestone?: {
            name: string;
            icon?: string;
            level?: number;
          };
        };
      };
    };
  };
  onInteractionClick: (messageId: string, action: string) => void;
  onFeedback: (messageId: string, feedback: 'helpful' | 'not_helpful') => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onInteractionClick, onFeedback }) => {
  const formatMessageContent = (content: string) => {
    // Simple formatting for therapeutic content
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const getMessageStatusIcon = () => {
    if (message.type === 'user') {
      return (
        <svg className="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      );
    }
    return null;
  };

  const getSafetyIndicator = () => {
    if (message.metadata?.safety?.crisis) {
      return (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>Crisis support resources available</span>
          </div>
        </div>
      );
    }
    return null;
  };

  const getTherapeuticTechniqueBadge = () => {
    if (message.metadata?.therapeutic_technique) {
      return (
        <div className="mt-2 inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          {message.metadata.therapeutic_technique}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md ${message.type === 'user' ? 'ml-12' : 'mr-12'} ${
        message.type === 'user' ? 'sm:ml-8 md:ml-12' : 'sm:mr-8 md:mr-12'
      }`}>
        <div
          className={`px-4 py-3 rounded-lg shadow-sm focus-within:ring-2 focus-within:ring-blue-500 ${
            message.type === 'user'
              ? 'bg-blue-600 text-white rounded-br-sm'
              : message.type === 'system'
              ? 'bg-yellow-50 text-yellow-800 border border-yellow-200 rounded-bl-sm'
              : 'bg-white text-gray-900 border border-gray-200 rounded-bl-sm'
          }`}
          role="group"
          aria-label={`${message.type} message`}
        >
          <div
            className="text-sm leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
          />

          {/* Therapeutic technique badge */}
          {getTherapeuticTechniqueBadge()}

          {/* Safety indicator for crisis content */}
          {getSafetyIndicator()}

          {/* Interactive Elements - Buttons */}
          {message.metadata?.interactive_elements?.buttons && (
            <div className="mt-3 space-y-2">
              {message.metadata.interactive_elements.buttons.map((button) => (
                <InteractiveButton
                  key={button.id}
                  id={button.id}
                  text={button.text}
                  action={button.action}
                  variant={button.variant || 'secondary'}
                  onClick={(id, action) => onInteractionClick(message.id, action)}
                  metadata={button.metadata}
                />
              ))}
            </div>
          )}

          {/* Interactive Elements - Progress Feedback */}
          {message.metadata?.interactive_elements?.progress_feedback && (
            <div className="mt-3">
              <ProgressFeedback
                type={message.metadata.interactive_elements.progress_feedback.type}
                title={message.metadata.interactive_elements.progress_feedback.title}
                description={message.metadata.interactive_elements.progress_feedback.description}
                progress={message.metadata.interactive_elements.progress_feedback.progress}
                milestone={message.metadata.interactive_elements.progress_feedback.milestone}
              />
            </div>
          )}
        </div>

        {/* Interactive Elements - Guided Exercise (outside message bubble for better UX) */}
        {message.metadata?.interactive_elements?.guided_exercise && (
          <div className="mt-3">
            <GuidedExercise
              exercise={message.metadata.interactive_elements.guided_exercise}
              onComplete={() => onInteractionClick(message.id, 'exercise_completed')}
              onProgress={(step, completed) =>
                onInteractionClick(message.id, `exercise_progress:${step}:${completed}`)
              }
            />
          </div>
        )}

        {/* Message metadata */}
        <div className={`flex items-center justify-between mt-1 px-1 ${
          message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
        }`}>
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
          <div className="flex items-center space-x-1">
            {getMessageStatusIcon()}
            {message.type === 'assistant' && (
              <div className="flex space-x-1">
                <button
                  onClick={() => onFeedback(message.id, 'helpful')}
                  className="text-gray-400 hover:text-green-600 transition-colors p-1 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
                  aria-label="Mark as helpful"
                  title="This was helpful"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                  </svg>
                </button>
                <button
                  onClick={() => onFeedback(message.id, 'not_helpful')}
                  className="text-gray-400 hover:text-red-600 transition-colors p-1 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
                  aria-label="Mark as not helpful"
                  title="This was not helpful"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v2a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
