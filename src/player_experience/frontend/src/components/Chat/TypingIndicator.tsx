import React from 'react';

interface TypingIndicatorProps {
  isVisible: boolean;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="flex justify-start mb-4">
      <div className="mr-12 max-w-xs lg:max-w-md">
        <div className="bg-white text-gray-900 shadow-sm px-4 py-3 rounded-lg rounded-bl-sm border border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div 
                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" 
                style={{ animationDelay: '0.1s' }}
              ></div>
              <div 
                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" 
                style={{ animationDelay: '0.2s' }}
              ></div>
            </div>
            <span className="text-xs text-gray-500">Assistant is typing...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;