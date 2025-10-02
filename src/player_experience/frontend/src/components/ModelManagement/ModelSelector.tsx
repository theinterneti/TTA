import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  ModelInfo,
  fetchAvailableModels,
  setSelectedModel,
  trackModelSelection,
  setActiveFilter,
} from '../../store/slices/modelManagementSlice';

interface ModelSelectorProps {
  onModelSelect?: (model: ModelInfo) => void;
  showPerformanceMetrics?: boolean;
  compact?: boolean;
  filterType?: 'all' | 'free' | 'affordable';
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  onModelSelect,
  showPerformanceMetrics = true,
  compact = false,
  filterType = 'all',
}) => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const {
    availableModels,
    freeModels,
    affordableModels,
    selectedModel,
    isLoadingModels,
    activeFilter,
    error,
  } = useSelector((state: RootState) => state.modelManagement);

  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'cost' | 'performance'>('name');
  const [showDetails, setShowDetails] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchAvailableModels({ provider: 'openrouter' }) as any);
  }, [dispatch]);

  const getModelsToShow = () => {
    let models: ModelInfo[] = [];
    
    switch (filterType || activeFilter) {
      case 'free':
        models = freeModels;
        break;
      case 'affordable':
        models = affordableModels;
        break;
      default:
        models = availableModels;
    }

    // Apply search filter
    if (searchTerm) {
      models = models.filter(model =>
        model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        model.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        model.model_id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sorting
    return models.sort((a, b) => {
      switch (sortBy) {
        case 'cost':
          const aCost = a.cost_per_token || 0;
          const bCost = b.cost_per_token || 0;
          return aCost - bCost;
        case 'performance':
          return (b.performance_score || 0) - (a.performance_score || 0);
        default:
          return a.name.localeCompare(b.name);
      }
    });
  };

  const handleModelSelect = (model: ModelInfo) => {
    dispatch(setSelectedModel(model));
    
    // Track the selection for analytics
    if (profile?.player_id) {
      dispatch(trackModelSelection({
        model,
        userId: profile.player_id,
        selectionReason: 'manual_selection',
      }) as any);
    }

    onModelSelect?.(model);
  };

  const formatCost = (costPerToken: number | null) => {
    if (costPerToken === null || costPerToken === 0) return 'FREE';
    if (costPerToken < 0.000001) return '<$0.000001/token';
    return `$${costPerToken.toFixed(6)}/token`;
  };

  const getModelStatusColor = (model: ModelInfo) => {
    if (model.is_free) return 'text-green-600 bg-green-50 border-green-200';
    if ((model.cost_per_token || 0) <= 0.001) return 'text-blue-600 bg-blue-50 border-blue-200';
    if ((model.cost_per_token || 0) <= 0.01) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const modelsToShow = getModelsToShow();

  if (isLoadingModels) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading models...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Sort Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search models..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <div className="sm:w-48">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'name' | 'cost' | 'performance')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="name">Sort by Name</option>
            <option value="cost">Sort by Cost</option>
            <option value="performance">Sort by Performance</option>
          </select>
        </div>
      </div>

      {/* Model Count */}
      <div className="text-sm text-gray-600">
        Showing {modelsToShow.length} model{modelsToShow.length !== 1 ? 's' : ''}
        {searchTerm && ` matching "${searchTerm}"`}
      </div>

      {/* Models Grid */}
      <div className={`grid gap-4 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}>
        {modelsToShow.map((model) => (
          <div
            key={model.model_id}
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedModel?.model_id === model.model_id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleModelSelect(model)}
          >
            {/* Model Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate" title={model.name}>
                  {model.name}
                </h3>
                <p className="text-sm text-gray-500 truncate" title={model.model_id}>
                  {model.model_id}
                </p>
              </div>
              
              {/* Cost Badge */}
              <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getModelStatusColor(model)}`}>
                {formatCost(model.cost_per_token)}
              </div>
            </div>

            {/* Model Description */}
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {model.description}
            </p>

            {/* Model Details */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Context Length</span>
                <span>{model.context_length?.toLocaleString() || 'N/A'}</span>
              </div>
              
              {showPerformanceMetrics && model.performance_score && (
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Performance Score</span>
                  <span>{model.performance_score}/10</span>
                </div>
              )}
              
              {model.therapeutic_safety_score && (
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Safety Score</span>
                  <span>{model.therapeutic_safety_score}/10</span>
                </div>
              )}
            </div>

            {/* Capabilities */}
            {model.capabilities && model.capabilities.length > 0 && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-1">
                  {model.capabilities.slice(0, 3).map((capability) => (
                    <span
                      key={capability}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                    >
                      {capability}
                    </span>
                  ))}
                  {model.capabilities.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      +{model.capabilities.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Expand Details Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowDetails(showDetails === model.model_id ? null : model.model_id);
              }}
              className="mt-3 text-xs text-primary-600 hover:text-primary-700 flex items-center"
            >
              {showDetails === model.model_id ? 'Hide Details' : 'Show Details'}
              <svg 
                className={`ml-1 h-3 w-3 transition-transform ${showDetails === model.model_id ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Expanded Details */}
            {showDetails === model.model_id && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                <div className="text-xs">
                  <span className="font-medium text-gray-700">Provider:</span>
                  <span className="ml-2 text-gray-600">{model.provider}</span>
                </div>
                
                {model.capabilities && (
                  <div className="text-xs">
                    <span className="font-medium text-gray-700">All Capabilities:</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {model.capabilities.map((capability) => (
                        <span
                          key={capability}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                        >
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {modelsToShow.length === 0 && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No models found</h3>
          <p className="text-gray-600">
            {searchTerm 
              ? `No models match your search "${searchTerm}"`
              : 'No models available with current filters'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
