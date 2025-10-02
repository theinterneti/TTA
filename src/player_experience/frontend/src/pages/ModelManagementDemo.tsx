import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import {
  fetchAvailableModels,
  fetchFreeModels,
  fetchAffordableModels,
  fetchSystemStatus,
  ModelInfo,
} from '../store/slices/modelManagementSlice';
import { ModelSelector, ModelFilterSettings, ModelCostDisplay } from '../components/ModelManagement';

const ModelManagementDemo: React.FC = () => {
  const dispatch = useDispatch();
  const {
    availableModels,
    freeModels,
    affordableModels,
    selectedModel,
    systemStatus,
    isLoading,
    error,
  } = useSelector((state: RootState) => state.modelManagement);

  const [selectedDemoModel, setSelectedDemoModel] = useState<ModelInfo | null>(null);
  const [demoMode, setDemoMode] = useState<'selector' | 'filters' | 'cost'>('selector');

  useEffect(() => {
    // Load initial data
    dispatch(fetchSystemStatus() as any);
    dispatch(fetchAvailableModels({ provider: 'openrouter' }) as any);
    dispatch(fetchFreeModels('openrouter') as any);
    dispatch(fetchAffordableModels({ maxCost: 0.001, provider: 'openrouter' }) as any);
  }, [dispatch]);

  const handleModelSelect = (model: ModelInfo) => {
    setSelectedDemoModel(model);
  };

  const getDemoStats = () => {
    const totalModels = availableModels.length;
    const freeCount = freeModels.length;
    const affordableCount = affordableModels.length;
    const paidCount = totalModels - freeCount;

    return {
      total: totalModels,
      free: freeCount,
      affordable: affordableCount,
      paid: paidCount,
      freePercentage: totalModels > 0 ? ((freeCount / totalModels) * 100).toFixed(1) : '0',
    };
  };

  const stats = getDemoStats();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🤖 Model Management Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Explore the OpenRouter free models filter functionality with an interactive demo
            of the TTA model management system.
          </p>
        </div>

        {/* System Status */}
        {systemStatus && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{stats.total}</div>
                <div className="text-sm text-green-800">Total Models</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{stats.free}</div>
                <div className="text-sm text-blue-800">Free Models</div>
                <div className="text-xs text-blue-600">{stats.freePercentage}% of total</div>
              </div>
              <div className="text-center p-4 bg-indigo-50 rounded-lg">
                <div className="text-2xl font-bold text-indigo-600">{stats.affordable}</div>
                <div className="text-sm text-indigo-800">Affordable Models</div>
                <div className="text-xs text-indigo-600">≤$0.001/token</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">{stats.paid}</div>
                <div className="text-sm text-gray-800">Paid Models</div>
                <div className="text-xs text-gray-600">Premium options</div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Demo Mode Selector */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Demo Modes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: 'selector', title: 'Model Selector', desc: 'Browse and select AI models', icon: '🎯' },
              { id: 'filters', title: 'Filter Settings', desc: 'Configure cost and preference filters', icon: '⚙️' },
              { id: 'cost', title: 'Cost Analysis', desc: 'Analyze model costs and usage', icon: '💰' },
            ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => setDemoMode(mode.id as any)}
                className={`p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                  demoMode === mode.id
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-3">{mode.icon}</span>
                  <div className="font-medium text-lg">{mode.title}</div>
                </div>
                <div className="text-sm text-gray-600">{mode.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Demo Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Demo Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                {demoMode === 'selector' && '🎯 Model Selector Demo'}
                {demoMode === 'filters' && '⚙️ Filter Settings Demo'}
                {demoMode === 'cost' && '💰 Cost Analysis Demo'}
              </h2>

              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="spinner"></div>
                  <span className="ml-2 text-gray-600">Loading demo data...</span>
                </div>
              )}

              {!isLoading && (
                <>
                  {demoMode === 'selector' && (
                    <ModelSelector
                      onModelSelect={handleModelSelect}
                      showPerformanceMetrics={true}
                    />
                  )}

                  {demoMode === 'filters' && (
                    <ModelFilterSettings
                      onFilterChange={(filterType) => {
                        console.log('Filter changed to:', filterType);
                      }}
                      showAdvancedOptions={true}
                    />
                  )}

                  {demoMode === 'cost' && selectedDemoModel && (
                    <ModelCostDisplay
                      model={selectedDemoModel}
                      estimatedTokens={5000}
                      showEstimatedCost={true}
                      showComparison={true}
                      comparisonModels={availableModels.slice(0, 3)}
                    />
                  )}

                  {demoMode === 'cost' && !selectedDemoModel && (
                    <div className="text-center py-12">
                      <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Model First</h3>
                      <p className="text-gray-600 mb-4">
                        Switch to the Model Selector tab and choose a model to see cost analysis.
                      </p>
                      <button
                        onClick={() => setDemoMode('selector')}
                        className="btn-primary"
                      >
                        Go to Model Selector
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Selected Model Info */}
            {(selectedModel || selectedDemoModel) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Selected Model</h3>
                <div className="space-y-3">
                  <div>
                    <div className="font-medium text-gray-900">
                      {(selectedModel || selectedDemoModel)?.name}
                    </div>
                    <div className="text-sm text-gray-600">
                      {(selectedModel || selectedDemoModel)?.model_id}
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium border inline-block ${
                    (selectedModel || selectedDemoModel)?.is_free
                      ? 'text-green-600 bg-green-50 border-green-200'
                      : 'text-yellow-600 bg-yellow-50 border-yellow-200'
                  }`}>
                    {(selectedModel || selectedDemoModel)?.is_free 
                      ? 'FREE' 
                      : `$${((selectedModel || selectedDemoModel)?.cost_per_token || 0).toFixed(6)}/token`
                    }
                  </div>
                </div>
              </div>
            )}

            {/* Demo Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">💡 Demo Instructions</h3>
              <div className="text-blue-800 text-sm space-y-2">
                {demoMode === 'selector' && (
                  <>
                    <p>• Browse available OpenRouter models</p>
                    <p>• Use search to find specific models</p>
                    <p>• Sort by name, cost, or performance</p>
                    <p>• Click on models to select them</p>
                    <p>• View model details and capabilities</p>
                  </>
                )}
                {demoMode === 'filters' && (
                  <>
                    <p>• Toggle between All, Free, and Affordable filters</p>
                    <p>• Adjust cost threshold with the slider</p>
                    <p>• Try quick cost presets</p>
                    <p>• Explore advanced filter settings</p>
                    <p>• See real-time filter summaries</p>
                  </>
                )}
                {demoMode === 'cost' && (
                  <>
                    <p>• Analyze costs for different token amounts</p>
                    <p>• Use the cost calculator</p>
                    <p>• View monthly usage scenarios</p>
                    <p>• Compare costs with other models</p>
                    <p>• Get cost-saving tips</p>
                  </>
                )}
              </div>
            </div>

            {/* Feature Highlights */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4">✨ Key Features</h3>
              <div className="text-green-800 text-sm space-y-2">
                <p>• <strong>Free Model Detection:</strong> Automatically identifies zero-cost models</p>
                <p>• <strong>Cost Filtering:</strong> Filter by maximum cost per token</p>
                <p>• <strong>Smart Sorting:</strong> Prefer free models in listings</p>
                <p>• <strong>Usage Analytics:</strong> Track selection patterns</p>
                <p>• <strong>Cost Estimation:</strong> Calculate usage costs</p>
                <p>• <strong>Real-time Updates:</strong> Dynamic filter application</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-gray-200">
          <p className="text-gray-600">
            This demo showcases the OpenRouter free models filter functionality integrated into the TTA platform.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Built with React, Redux, TypeScript, and Tailwind CSS
          </p>
        </div>
      </div>
    </div>
  );
};

export default ModelManagementDemo;
