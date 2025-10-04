import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store/store';
import { PlayerPreferencesConfiguration } from '../../components/PlayerPreferences';
import { 
  fetchPlayerPreferences, 
  exportPreferences, 
  importPreferences,
  resetPreferences 
} from '../../store/slices/playerPreferencesSlice';
import { PlayerPreferences } from '../../types/preferences';

const Preferences: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { preferences, isLoading, error } = useSelector(
    (state: RootState) => state.playerPreferences
  );

  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [showResetModal, setShowResetModal] = useState(false);

  useEffect(() => {
    if (profile?.player_id) {
      dispatch(fetchPlayerPreferences(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  const handlePreferencesComplete = (updatedPreferences: PlayerPreferences) => {
    // Preferences saved successfully
    console.log('Preferences updated:', updatedPreferences);
  };

  const handleExportPreferences = () => {
    if (profile?.player_id) {
      dispatch(exportPreferences(profile.player_id) as any);
    }
  };

  const handleImportFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/json') {
      setImportFile(file);
    } else {
      alert('Please select a valid JSON file.');
    }
  };

  const handleImportPreferences = async () => {
    if (!importFile || !profile?.player_id) return;

    try {
      const fileContent = await importFile.text();
      const preferencesData = JSON.parse(fileContent);
      
      await dispatch(importPreferences({ 
        playerId: profile.player_id, 
        preferencesData 
      }) as any);
      
      setShowImportModal(false);
      setImportFile(null);
    } catch (error) {
      console.error('Failed to import preferences:', error);
      alert('Failed to import preferences. Please check the file format.');
    }
  };

  const handleResetPreferences = () => {
    dispatch(resetPreferences());
    setShowResetModal(false);
    
    // Reload preferences to get defaults
    if (profile?.player_id) {
      dispatch(fetchPlayerPreferences(profile.player_id) as any);
    }
  };

  if (!profile?.player_id) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Player Profile Required
          </h2>
          <p className="text-gray-600 mb-6">
            You need to have a player profile to manage preferences.
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

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Therapeutic Preferences
            </h1>
            <p className="text-gray-600 mt-2">
              Customize your therapeutic experience to match your needs and comfort level.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={handleExportPreferences}
              className="btn-outline flex items-center"
              disabled={!preferences}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export
            </button>
            
            <button
              onClick={() => setShowImportModal(true)}
              className="btn-outline flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              Import
            </button>
            
            <button
              onClick={() => setShowResetModal(true)}
              className="btn-outline text-red-600 border-red-300 hover:bg-red-50 flex items-center"
              disabled={!preferences}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Main Configuration */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600">Loading preferences...</span>
        </div>
      ) : (
        <PlayerPreferencesConfiguration
          playerId={profile.player_id}
          isOnboarding={false}
          onComplete={handlePreferencesComplete}
        />
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4 w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Import Preferences
            </h3>
            <p className="text-gray-600 mb-4">
              Select a JSON file containing your exported preferences to import them.
            </p>
            
            <div className="mb-4">
              <input
                type="file"
                accept=".json"
                onChange={handleImportFile}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
            </div>

            {importFile && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 text-sm">
                  Selected: {importFile.name}
                </p>
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowImportModal(false);
                  setImportFile(null);
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleImportPreferences}
                disabled={!importFile}
                className="btn-primary"
              >
                Import
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reset Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4 w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Reset Preferences
            </h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to reset all preferences to their default values? 
              This action cannot be undone.
            </p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowResetModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleResetPreferences}
                className="btn-primary bg-red-600 hover:bg-red-700"
              >
                Reset All
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Preferences;
