import React, { useState, useEffect } from 'react';
import { ModelInfo } from '../../store/slices/modelManagementSlice';

interface ModelCostDisplayProps {
  model: ModelInfo;
  estimatedTokens?: number;
  showEstimatedCost?: boolean;
  showComparison?: boolean;
  comparisonModels?: ModelInfo[];
  className?: string;
}

const ModelCostDisplay: React.FC<ModelCostDisplayProps> = ({
  model,
  estimatedTokens = 1000,
  showEstimatedCost = true,
  showComparison = false,
  comparisonModels = [],
  className = '',
}) => {
  const [tokenInput, setTokenInput] = useState(estimatedTokens);
  const [showCalculator, setShowCalculator] = useState(false);

  const formatCost = (costPerToken: number | null, tokens: number = 1) => {
    if (costPerToken === null || costPerToken === 0) return 'FREE';
    const totalCost = costPerToken * tokens;
    if (totalCost < 0.000001) return '<$0.000001';
    if (totalCost < 0.01) return `$${totalCost.toFixed(6)}`;
    return `$${totalCost.toFixed(4)}`;
  };

  const getCostCategory = (costPerToken: number | null) => {
    if (costPerToken === null || costPerToken === 0) return 'free';
    if (costPerToken <= 0.0001) return 'very-cheap';
    if (costPerToken <= 0.001) return 'cheap';
    if (costPerToken <= 0.01) return 'moderate';
    return 'expensive';
  };

  const getCostCategoryColor = (category: string) => {
    switch (category) {
      case 'free':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'very-cheap':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'cheap':
        return 'text-indigo-600 bg-indigo-50 border-indigo-200';
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'expensive':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getCostCategoryLabel = (category: string) => {
    switch (category) {
      case 'free':
        return 'FREE';
      case 'very-cheap':
        return 'Very Cheap';
      case 'cheap':
        return 'Cheap';
      case 'moderate':
        return 'Moderate';
      case 'expensive':
        return 'Expensive';
      default:
        return 'Unknown';
    }
  };

  const calculateMonthlyCost = (costPerToken: number | null, tokensPerDay: number) => {
    if (costPerToken === null || costPerToken === 0) return 0;
    return costPerToken * tokensPerDay * 30;
  };

  const getUsageScenarios = () => [
    { label: 'Light Usage', tokensPerDay: 1000, description: '~10 short conversations/day' },
    { label: 'Moderate Usage', tokensPerDay: 5000, description: '~50 conversations/day' },
    { label: 'Heavy Usage', tokensPerDay: 20000, description: '~200 conversations/day' },
    { label: 'Enterprise Usage', tokensPerDay: 100000, description: '~1000 conversations/day' },
  ];

  const category = getCostCategory(model.cost_per_token);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Main Cost Display */}
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium text-gray-900">{model.name}</h4>
          <p className="text-sm text-gray-500">{model.model_id}</p>
        </div>
        <div className={`px-3 py-2 rounded-lg border font-medium ${getCostCategoryColor(category)}`}>
          {getCostCategoryLabel(category)}
        </div>
      </div>

      {/* Cost Details */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm font-medium text-gray-700">Per Token</div>
          <div className="text-lg font-bold text-gray-900">
            {formatCost(model.cost_per_token, 1)}
          </div>
        </div>
        
        {showEstimatedCost && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-700">
              {tokenInput.toLocaleString()} Tokens
            </div>
            <div className="text-lg font-bold text-gray-900">
              {formatCost(model.cost_per_token, tokenInput)}
            </div>
          </div>
        )}
      </div>

      {/* Cost Calculator */}
      {showEstimatedCost && (
        <div>
          <button
            onClick={() => setShowCalculator(!showCalculator)}
            className="flex items-center text-sm text-primary-600 hover:text-primary-700"
          >
            <svg 
              className={`mr-1 h-4 w-4 transition-transform ${showCalculator ? 'rotate-90' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7-7" />
            </svg>
            Cost Calculator
          </button>

          {showCalculator && (
            <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estimated Tokens
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000000"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[100, 500, 1000, 5000, 10000, 50000].map((tokens) => (
                  <button
                    key={tokens}
                    onClick={() => setTokenInput(tokens)}
                    className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                      tokenInput === tokens
                        ? 'bg-primary-500 text-white'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {tokens.toLocaleString()} tokens
                  </button>
                ))}
              </div>

              <div className="pt-3 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-2">Estimated Cost</div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatCost(model.cost_per_token, tokenInput)}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Usage Scenarios */}
      {model.cost_per_token && model.cost_per_token > 0 && (
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-3">Monthly Cost Estimates</h5>
          <div className="space-y-2">
            {getUsageScenarios().map((scenario) => {
              const monthlyCost = calculateMonthlyCost(model.cost_per_token, scenario.tokensPerDay);
              return (
                <div key={scenario.label} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{scenario.label}</div>
                    <div className="text-xs text-gray-600">{scenario.description}</div>
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {monthlyCost < 0.01 ? '<$0.01' : `$${monthlyCost.toFixed(2)}`}/month
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Cost Comparison */}
      {showComparison && comparisonModels.length > 0 && (
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-3">Cost Comparison</h5>
          <div className="space-y-2">
            {[model, ...comparisonModels].map((compareModel) => {
              const cost = compareModel.cost_per_token || 0;
              const estimatedCost = cost * tokenInput;
              const isCurrentModel = compareModel.model_id === model.model_id;
              
              return (
                <div 
                  key={compareModel.model_id}
                  className={`flex items-center justify-between py-2 px-3 rounded-lg ${
                    isCurrentModel ? 'bg-primary-50 border border-primary-200' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className={`text-sm font-medium truncate ${
                      isCurrentModel ? 'text-primary-900' : 'text-gray-900'
                    }`}>
                      {compareModel.name}
                      {isCurrentModel && <span className="ml-2 text-xs">(Current)</span>}
                    </div>
                    <div className="text-xs text-gray-600 truncate">{compareModel.model_id}</div>
                  </div>
                  <div className="text-right ml-3">
                    <div className={`text-sm font-medium ${
                      isCurrentModel ? 'text-primary-900' : 'text-gray-900'
                    }`}>
                      {formatCost(compareModel.cost_per_token, tokenInput)}
                    </div>
                    <div className="text-xs text-gray-600">
                      {formatCost(compareModel.cost_per_token, 1)}/token
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Cost Savings Tip */}
      {model.cost_per_token && model.cost_per_token > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h6 className="text-sm font-medium text-green-900">💡 Cost Saving Tip</h6>
              <p className="text-sm text-green-800 mt-1">
                Consider using free models for development and testing, then switch to paid models only for production use.
                You can also optimize your prompts to use fewer tokens.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelCostDisplay;
