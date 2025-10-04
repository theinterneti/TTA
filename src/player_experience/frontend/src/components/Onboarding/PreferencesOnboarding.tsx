import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store/store';
import { PlayerPreferencesConfiguration } from '../PlayerPreferences';
import { PlayerPreferences } from '../../types/preferences';

interface PreferencesOnboardingProps {
  onComplete?: (preferences: PlayerPreferences) => void;
  onSkip?: () => void;
}

const PreferencesOnboarding: React.FC<PreferencesOnboardingProps> = ({
  onComplete,
  onSkip,
}) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const [currentStep, setCurrentStep] = useState<'welcome' | 'configure' | 'complete'>('welcome');

  const handleGetStarted = () => {
    setCurrentStep('configure');
  };

  const handleSkipOnboarding = () => {
    if (onSkip) {
      onSkip();
    } else {
      navigate('/dashboard');
    }
  };

  const handlePreferencesComplete = (preferences: PlayerPreferences) => {
    setCurrentStep('complete');
    
    // Auto-redirect after showing completion
    setTimeout(() => {
      if (onComplete) {
        onComplete(preferences);
      } else {
        navigate('/dashboard');
      }
    }, 3000);
  };

  if (!profile?.player_id) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Profile Required
          </h2>
          <p className="text-gray-600 mb-6">
            You need to have a player profile to set up preferences.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (currentStep === 'welcome') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">🌟</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to Your Adventure Journey
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Let's personalize your experience to create the most engaging and meaningful
              interactive storytelling adventure for you.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              What We'll Set Up Together
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600">⚡</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Story Intensity</h3>
                  <p className="text-gray-600 text-sm">Choose how gentle or intensive you'd like your adventure experience to be</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-600">🧠</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Story Styles</h3>
                  <p className="text-gray-600 text-sm">Select story approaches that resonate with you like problem-solving, mindfulness, or personal narrative</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-600">💬</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Conversation Style</h3>
                  <p className="text-gray-600 text-sm">Choose how you'd like to communicate - gentle, direct, exploratory, or supportive</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-amber-600">🎯</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Your Goals</h3>
                  <p className="text-gray-600 text-sm">Set therapeutic goals and identify areas you'd like to focus on</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-pink-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-pink-600">🎭</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Character & Setting</h3>
                  <p className="text-gray-600 text-sm">Customize your therapeutic companion and choose your preferred environment</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-indigo-600">📝</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Topic Preferences</h3>
                  <p className="text-gray-600 text-sm">Specify topics that comfort you and any you'd prefer to avoid</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGetStarted}
              className="btn-primary text-lg px-8 py-3"
            >
              Let's Get Started
            </button>
            <button
              onClick={handleSkipOnboarding}
              className="btn-outline text-lg px-8 py-3"
            >
              Skip for Now
            </button>
          </div>

          <p className="text-gray-500 text-sm mt-6">
            Don't worry - you can change these preferences anytime from your settings.
          </p>
        </div>
      </div>
    );
  }

  if (currentStep === 'configure') {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <PlayerPreferencesConfiguration
          playerId={profile.player_id}
          isOnboarding={true}
          onComplete={handlePreferencesComplete}
          onCancel={handleSkipOnboarding}
        />
      </div>
    );
  }

  if (currentStep === 'complete') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
        <div className="max-w-md mx-auto text-center">
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">✅</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            All Set!
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Your therapeutic preferences have been saved. Your personalized experience 
            is now ready to begin.
          </p>
          <div className="bg-white rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">What's Next?</h3>
            <p className="text-gray-600 text-sm">
              You'll be redirected to your dashboard where you can start your first 
              therapeutic storytelling session with your personalized settings.
            </p>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 text-sm mt-4">
            Redirecting you to the dashboard...
          </p>
        </div>
      </div>
    );
  }

  return null;
};

export default PreferencesOnboarding;
