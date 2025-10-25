import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  updateFilterSettings,
  updateOpenRouterFilter,
  fetchOpenRouterFilter,
  fetchFreeModels,
  fetchAffordableModels,
  fetchAvailableModels,
  setActiveFilter,
  setCostThreshold,
  trackFilterUsage,
} from '../../store/slices/modelManagementSlice';

interface ModelFilterSettingsProps {
  onFilterChange?: (filterType: 'all' | 'free' | 'affordable') => void;
  showAdvancedOptions?: boolean;
}

const ModelFilterSettings: React.FC<ModelFilterSettingsProps> = ({
  onFilterChange,
  showAdvancedOptions = true,
}) => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const {
    filterSettings,
    activeFilter,
    costThreshold,
    availableModels,
    freeModels,
    affordableModels,
    isLoadingFilter,
    error,
  } = useSelector((state: RootState) => state.modelManagement);

  const [localCostThreshold, setLocalCostThreshold] = useState(costThreshold);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    dispatch(fetchOpenRouterFilter() as any);
  }, [dispatch]);

  useEffect(() => {
    setLocalCostThreshold(costThreshold);
  }, [costThreshold]);

  const handleFilterChange = async (filterType: 'all' | 'free' | 'affordable') => {
    dispatch(setActiveFilter(filterType));

    // Fetch appropriate models based on filter
    switch (filterType) {
      case 'free':
        dispatch(fetchFreeModels('openrouter') as any);
        break;
      case 'affordable':
        dispatch(fetchAffordableModels({ maxCost: localCostThreshold, provider: 'openrouter' }) as any);
        break;
      default:
        dispatch(fetchAvailableModels({ provider: 'openrouter' }) as any);
    }

    // Track filter usage for analytics
    if (profile?.player_id) {
      const modelsShown = filterType === 'free' ? freeModels.length :
                         filterType === 'affordable' ? affordableModels.length :
                         availableModels.length;

      dispatch(trackFilterUsage({
        filterType: filterType === 'all' ? 'all' : filterType === 'free' ? 'free_only' : 'affordable',
        maxCostThreshold: filterType === 'affordable' ? localCostThreshold : undefined,
        userId: profile.player_id,
        modelsShown,
      }) as any);
    }

    onFilterChange?.(filterType);
  };

  const handleCostThresholdChange = (value: number) => {
    setLocalCostThreshold(value);
    dispatch(setCostThreshold(value));

    // If affordable filter is active, refresh the models
    if (activeFilter === 'affordable') {
      dispatch(fetchAffordableModels({ maxCost: value, provider: 'openrouter' }) as any);
    }
  };

  const handleAdvancedSettingsChange = (setting: string, value: boolean | number) => {
    const updates = { [setting]: value };
    dispatch(updateFilterSettings(updates));
    dispatch(updateOpenRouterFilter(updates) as any);
  };

  const getFilterDescription = (filterType: 'all' | 'free' | 'affordable') => {
    switch (filterType) {
      case 'free':
        return 'Show only models that are completely free to use';
      case 'affordable':
        return `Show models costing up to $${localCostThreshold.toFixed(6)} per token`;
      default:
        return 'Show all available models regardless of cost';
    }
  };

  const getModelCount = (filterType: 'all' | 'free' | 'affordable') => {
    switch (filterType) {
      case 'free':
        return freeModels.length;
      case 'affordable':
        return affordableModels.length;
      default:
        return availableModels.length;
    }
  };

  return (
    <div className="space-y-6">
      {/* Filter Type Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          Model Filter Type
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(['all', 'free', 'affordable'] as const).map((filterType) => (
            <button
              key={filterType}
              onClick={() => handleFilterChange(filterType)}
              disabled={isLoadingFilter}
              className={`p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                activeFilter === filterType
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              } ${isLoadingFilter ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-lg capitalize">
                  {filterType === 'all' ? 'All Models' : filterType === 'free' ? 'Free Only' : 'Affordable'}
                </div>
                <div className="text-sm font-medium px-2 py-1 bg-gray-100 rounded-full">
                  {getModelCount(filterType)}
                </div>
              </div>
              <div className="text-sm text-gray-600">
                {getFilterDescription(filterType)}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Cost Threshold Slider (for affordable filter) */}
      {(activeFilter === 'affordable' || showAdvancedOptions) && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Maximum Cost Per Token: ${localCostThreshold.toFixed(6)}
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="0"
              max="0.01"
              step="0.000001"
              value={localCostThreshold}
              onChange={(e) => handleCostThresholdChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Free ($0.000000)</span>
              <span>Expensive ($0.010000)</span>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Models costing more than ${localCostThreshold.toFixed(6)} per token will be hidden
          </p>
        </div>
      )}

      {/* Quick Cost Presets */}
      {(activeFilter === 'affordable' || showAdvancedOptions) && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Quick Cost Presets
          </label>
          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Free Only', value: 0 },
              { label: 'Very Cheap', value: 0.0001 },
              { label: 'Cheap', value: 0.001 },
              { label: 'Moderate', value: 0.005 },
              { label: 'Expensive', value: 0.01 },
            ].map((preset) => (
              <button
                key={preset.label}
                onClick={() => handleCostThresholdChange(preset.value)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  Math.abs(localCostThreshold - preset.value) < 0.000001
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Advanced Settings */}
      {showAdvancedOptions && (
        <div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900 mb-4"
          >
            <svg
              className={`mr-2 h-4 w-4 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Advanced Filter Settings
          </button>

          {showAdvanced && (
            <div className="space-y-4 pl-6 border-l-2 border-gray-200">
              {/* Prefer Free Models */}
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Prefer Free Models</p>
                  <p className="text-sm text-gray-600">Sort free models first in the list</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={filterSettings.prefer_free_models}
                    onChange={(e) => handleAdvancedSettingsChange('prefer_free_models', e.target.checked)}
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              {/* Show Free Only */}
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Show Free Only (Backend)</p>
                  <p className="text-sm text-gray-600">Apply free filter at the API level</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={filterSettings.show_free_only}
                    onChange={(e) => handleAdvancedSettingsChange('show_free_only', e.target.checked)}
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              {/* Max Cost Per Token (Advanced) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Backend Max Cost Per Token
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.000001"
                  value={filterSettings.max_cost_per_token}
                  onChange={(e) => handleAdvancedSettingsChange('max_cost_per_token', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="0.001000"
                />
                <p className="text-sm text-gray-600 mt-1">
                  Backend-level cost filtering (affects API responses)
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Filter Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💡 Current Filter Summary</h4>
        <div className="text-blue-800 text-sm space-y-1">
          <p><strong>Active Filter:</strong> {activeFilter === 'all' ? 'All Models' : activeFilter === 'free' ? 'Free Only' : 'Affordable Models'}</p>
          <p><strong>Models Shown:</strong> {getModelCount(activeFilter)}</p>
          {activeFilter === 'affordable' && (
            <p><strong>Max Cost:</strong> ${localCostThreshold.toFixed(6)} per token</p>
          )}
          <p><strong>Prefer Free:</strong> {filterSettings.prefer_free_models ? 'Yes' : 'No'}</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelFilterSettings;
