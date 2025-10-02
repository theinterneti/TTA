import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  fetchAvailableModels,
  fetchSystemStatus,
  updateUserPreferences,
  clearError,
} from '../../store/slices/modelManagementSlice';
import ModelSelector from './ModelSelector';
import ModelFilterSettings from './ModelFilterSettings';
import ModelCostDisplay from './ModelCostDisplay';
import OpenRouterAuthModal from './OpenRouterAuthModal';
import OpenRouterAuthStatus from './OpenRouterAuthStatus';

interface ModelManagementSectionProps {
  onModelSelect?: (model: any) => void;
}

const ModelManagementSection: React.FC<ModelManagementSectionProps> = ({
  onModelSelect,
}) => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const {
    selectedModel,
    userPreferences,
    systemStatus,
    selectionHistory,
    filterUsageStats,
    isLoading,
    error,
  } = useSelector((state: RootState) => state.modelManagement);

  const {
    isAuthenticated: isOpenRouterAuthenticated,
    authMethod,
    user: openRouterUser,
  } = useSelector((state: RootState) => state.openRouterAuth);

  const [activeTab, setActiveTab] = useState<'auth' | 'selector' | 'settings' | 'analytics'>('auth');
  const [showCostDetails, setShowCostDetails] = useState(false);

  useEffect(() => {
    dispatch(fetchSystemStatus() as any);
    // Only fetch models if authenticated
    if (isOpenRouterAuthenticated) {
      dispatch(fetchAvailableModels({ provider: 'openrouter' }) as any);
    }
  }, [dispatch, isOpenRouterAuthenticated]);

  // Auto-switch to selector tab when authenticated
  useEffect(() => {
    if (isOpenRouterAuthenticated && activeTab === 'auth') {
      setActiveTab('selector');
    }
  }, [isOpenRouterAuthenticated, activeTab]);

  const handlePreferenceChange = (key: string, value: any) => {
    dispatch(updateUserPreferences({ [key]: value }));
  };

  const getTotalFilterUsage = () => {
    return filterUsageStats.free_filter_usage + 
           filterUsageStats.affordable_filter_usage + 
           filterUsageStats.all_models_usage;
  };

  const getFilterUsagePercentage = (usage: number) => {
    const total = getTotalFilterUsage();
    return total > 0 ? ((usage / total) * 100).toFixed(1) : '0';
  };

  const tabs = [
    { id: 'auth', label: 'Authentication', icon: '🔐' },
    { id: 'selector', label: 'Model Selection', icon: '🤖', requiresAuth: true },
    { id: 'settings', label: 'Filter Settings', icon: '⚙️', requiresAuth: true },
    { id: 'analytics', label: 'Usage Analytics', icon: '📊', requiresAuth: true },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Model Management</h3>
        <p className="text-gray-600 mb-6">
          Configure your AI model preferences, manage costs, and track usage patterns.
        </p>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-blue-900">System Status</h4>
              <p className="text-sm text-blue-800">
                {systemStatus.initialized ? 'Model management system is online' : 'System initializing...'}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-blue-800">
                <strong>{systemStatus.active_models || 0}</strong> active models
              </div>
              <div className="text-xs text-blue-600">
                {Object.keys(systemStatus.providers || {}).length} providers available
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-800">{error}</span>
            </div>
            <button
              onClick={() => dispatch(clearError())}
              className="text-red-600 hover:text-red-800"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Selected Model Summary */}
      {selectedModel && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-green-900">Currently Selected Model</h4>
              <p className="text-sm text-green-800">{selectedModel.name}</p>
              <p className="text-xs text-green-600">{selectedModel.model_id}</p>
            </div>
            <div className="text-right">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                selectedModel.is_free 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {selectedModel.is_free ? 'FREE' : `$${(selectedModel.cost_per_token || 0).toFixed(6)}/token`}
              </div>
              <button
                onClick={() => setShowCostDetails(!showCostDetails)}
                className="text-xs text-green-600 hover:text-green-800 mt-1"
              >
                {showCostDetails ? 'Hide' : 'Show'} Cost Details
              </button>
            </div>
          </div>
          
          {showCostDetails && selectedModel && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <ModelCostDisplay 
                model={selectedModel}
                showEstimatedCost={true}
                className="bg-white rounded-lg p-3"
              />
            </div>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8" aria-label="Model management tabs">
          {tabs.map((tab) => {
            const isDisabled = tab.requiresAuth && !isOpenRouterAuthenticated;
            return (
              <button
                key={tab.id}
                onClick={() => !isDisabled && setActiveTab(tab.id as any)}
                disabled={isDisabled}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : isDisabled
                    ? 'border-transparent text-gray-300 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
                {isDisabled && (
                  <svg className="w-4 h-4 ml-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 0h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'auth' && (
          <div className="space-y-6">
            <OpenRouterAuthStatus
              showFullDetails={true}
              onAuthRequired={() => {
                // Additional logic when auth is required
                console.log('Authentication required for model access');
              }}
            />
          </div>
        )}

        {activeTab === 'selector' && (
          <div className="space-y-6">
            <ModelSelector
              onModelSelect={onModelSelect}
              showPerformanceMetrics={userPreferences.show_performance_metrics}
            />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <ModelFilterSettings />
            
            {/* User Preferences */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-4">User Preferences</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Show Performance Metrics</p>
                    <p className="text-sm text-gray-600">Display performance scores in model cards</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={userPreferences.show_performance_metrics}
                      onChange={(e) => handlePreferenceChange('show_performance_metrics', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Auto-Select Cheapest Model</p>
                    <p className="text-sm text-gray-600">Automatically select the cheapest available model</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={userPreferences.auto_select_cheapest}
                      onChange={(e) => handlePreferenceChange('auto_select_cheapest', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cost Tolerance: ${userPreferences.cost_tolerance.toFixed(6)}/token
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="0.01"
                    step="0.000001"
                    value={userPreferences.cost_tolerance}
                    onChange={(e) => handlePreferenceChange('cost_tolerance', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Filter Usage Statistics */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-4">Filter Usage Statistics</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {filterUsageStats.free_filter_usage}
                  </div>
                  <div className="text-sm text-green-800">Free Filter Uses</div>
                  <div className="text-xs text-green-600">
                    {getFilterUsagePercentage(filterUsageStats.free_filter_usage)}% of total
                  </div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {filterUsageStats.affordable_filter_usage}
                  </div>
                  <div className="text-sm text-blue-800">Affordable Filter Uses</div>
                  <div className="text-xs text-blue-600">
                    {getFilterUsagePercentage(filterUsageStats.affordable_filter_usage)}% of total
                  </div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-600">
                    {filterUsageStats.all_models_usage}
                  </div>
                  <div className="text-sm text-gray-800">All Models Uses</div>
                  <div className="text-xs text-gray-600">
                    {getFilterUsagePercentage(filterUsageStats.all_models_usage)}% of total
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Model Selections */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-4">Recent Model Selections</h4>
              {selectionHistory.length > 0 ? (
                <div className="space-y-3">
                  {selectionHistory.slice(0, 10).map((selection, index) => (
                    <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900">{selection.model_id}</div>
                        <div className="text-sm text-gray-600">
                          {selection.provider} • {selection.is_free ? 'FREE' : `$${(selection.cost_per_token || 0).toFixed(6)}/token`}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(selection.timestamp).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 text-center py-8">No model selections recorded yet</p>
              )}
            </div>

            {/* Usage Insights */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">💡 Usage Insights</h4>
              <div className="text-blue-800 text-sm space-y-1">
                <p>
                  <strong>Most Used Filter:</strong> {
                    filterUsageStats.free_filter_usage >= filterUsageStats.affordable_filter_usage && 
                    filterUsageStats.free_filter_usage >= filterUsageStats.all_models_usage
                      ? 'Free Models'
                      : filterUsageStats.affordable_filter_usage >= filterUsageStats.all_models_usage
                      ? 'Affordable Models'
                      : 'All Models'
                  }
                </p>
                <p><strong>Total Selections:</strong> {selectionHistory.length}</p>
                <p><strong>Cost Preference:</strong> {userPreferences.prefer_free_models ? 'Prefers free models' : 'No cost preference'}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Authentication Modal */}
      <OpenRouterAuthModal
        onAuthSuccess={() => {
          // Refresh models when authentication succeeds
          dispatch(fetchAvailableModels({ provider: 'openrouter' }) as any);
        }}
      />
    </div>
  );
};

export default ModelManagementSection;
