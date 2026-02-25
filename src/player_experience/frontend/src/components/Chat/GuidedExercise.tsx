import React, { useState, useEffect } from 'react';

interface GuidedExerciseProps {
  exercise: {
    type: string;
    instructions: string;
    steps: string[];
    duration?: number; // in seconds
    interactive?: boolean;
  };
  onComplete?: () => void;
  onProgress?: (step: number, completed: boolean) => void;
}

const GuidedExercise: React.FC<GuidedExerciseProps> = ({
  exercise,
  onComplete,
  onProgress
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<boolean[]>(
    new Array(exercise.steps.length).fill(false)
  );
  const [timer, setTimer] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);

  // Timer effect for timed exercises
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isTimerRunning && timer > 0) {
      interval = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            setIsTimerRunning(false);
            handleStepComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isTimerRunning, timer]);

  const startExercise = () => {
    setIsActive(true);
    setCurrentStep(0);
    if (exercise.duration) {
      setTimer(exercise.duration);
      setIsTimerRunning(true);
    }
  };

  const handleStepComplete = () => {
    const newCompletedSteps = [...completedSteps];
    newCompletedSteps[currentStep] = true;
    setCompletedSteps(newCompletedSteps);

    onProgress?.(currentStep, true);

    if (currentStep < exercise.steps.length - 1) {
      setCurrentStep(currentStep + 1);
      if (exercise.duration) {
        setTimer(exercise.duration);
        setIsTimerRunning(true);
      }
    } else {
      // Exercise completed
      setIsActive(false);
      setIsTimerRunning(false);
      onComplete?.();
    }
  };

  const handleStepSkip = () => {
    if (currentStep < exercise.steps.length - 1) {
      setCurrentStep(currentStep + 1);
      if (exercise.duration) {
        setTimer(exercise.duration);
        setIsTimerRunning(true);
      }
    } else {
      setIsActive(false);
      setIsTimerRunning(false);
    }
  };

  const resetExercise = () => {
    setIsActive(false);
    setCurrentStep(0);
    setCompletedSteps(new Array(exercise.steps.length).fill(false));
    setTimer(0);
    setIsTimerRunning(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getExerciseIcon = () => {
    switch (exercise.type.toLowerCase()) {
      case 'breathing':
      case 'breathing exercise':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      case 'mindfulness':
      case 'meditation':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'grounding':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        );
    }
  };

  return (
    <div data-testid="guided-exercise" className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 my-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="text-blue-600">
            {getExerciseIcon()}
          </div>
          <h4 className="text-lg font-semibold text-blue-900">
            {exercise.type}
          </h4>
        </div>

        {/* Timer display */}
        {exercise.duration && isActive && (
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isTimerRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            <span className="text-sm font-mono text-blue-800">
              {formatTime(timer)}
            </span>
          </div>
        )}
      </div>

      {/* Instructions */}
      <p className="text-sm text-blue-800 mb-4">
        {exercise.instructions}
      </p>

      {/* Exercise Steps */}
      {!isActive ? (
        <div className="space-y-2 mb-4">
          {exercise.steps.map((step, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-blue-600">{index + 1}</span>
              </div>
              <span className="text-sm text-blue-800">{step}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="mb-4">
          {/* Progress bar */}
          <div className="w-full bg-blue-100 rounded-full h-2 mb-4">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${((currentStep + 1) / exercise.steps.length) * 100}%` }}
            />
          </div>

          {/* Current step */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500 shadow-sm">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">{currentStep + 1}</span>
              </div>
              <div className="flex-1">
                <p className="text-blue-900 font-medium">
                  {exercise.steps[currentStep]}
                </p>
                {exercise.duration && (
                  <div className="mt-2 flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-blue-500 h-1 rounded-full transition-all duration-1000 ease-linear"
                        style={{
                          width: exercise.duration ? `${((exercise.duration - timer) / exercise.duration) * 100}%` : '0%'
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {formatTime(timer)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Step indicators */}
          <div className="flex justify-center space-x-2 mt-4">
            {exercise.steps.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                  index < currentStep
                    ? 'bg-green-500'
                    : index === currentStep
                    ? 'bg-blue-500'
                    : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex justify-between items-center">
        {!isActive ? (
          <button
            onClick={startExercise}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.5a1.5 1.5 0 011.5 1.5v1a1.5 1.5 0 01-1.5 1.5H9m0-5a1.5 1.5 0 011.5-1.5H12m-3 5h3m-3 0h.375a1.125 1.125 0 011.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125H9m0 0H5.625c-.621 0-1.125-.504-1.125-1.125v-1.5c0-.621.504-1.125 1.125-1.125H9z" />
            </svg>
            <span>Start Exercise</span>
          </button>
        ) : (
          <div className="flex space-x-2">
            {exercise.interactive && (
              <button
                onClick={handleStepComplete}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Complete Step</span>
              </button>
            )}

            <button
              onClick={handleStepSkip}
              className="flex items-center space-x-2 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3-3 3m-4-6l3 3-3 3" />
              </svg>
              <span>Skip</span>
            </button>
          </div>
        )}

        {/* Reset button (always available) */}
        <button
          onClick={resetExercise}
          className="text-gray-500 hover:text-gray-700 p-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          title="Reset exercise"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* Completion celebration */}
      {completedSteps.every(step => step) && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="text-green-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-sm font-medium text-green-800">
              Great job! You've completed the exercise.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default GuidedExercise;
