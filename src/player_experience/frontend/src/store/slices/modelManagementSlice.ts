import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { modelAPI, analyticsAPI } from '../../services/api';

// Types
export interface ModelInfo {
  model_id: string;
  name: string;
  provider: string;
  description: string;
  context_length: number;
  cost_per_token: number | null;
  is_free: boolean;
  capabilities: string[];
  therapeutic_safety_score: number | null;
  performance_score: number;
}

export interface FilterSettings {
  show_free_only: boolean;
  prefer_free_models: boolean;
  max_cost_per_token: number;
}

export interface ModelSelectionEvent {
  model_id: string;
  provider: string;
  is_free: boolean;
  cost_per_token?: number;
  selection_reason?: string;
  timestamp: string;
}

export interface UserPreferences {
  preferred_providers: string[];
  cost_tolerance: number;
  prefer_free_models: boolean;
  auto_select_cheapest: boolean;
  show_performance_metrics: boolean;
  model_switching_frequency: 'low' | 'medium' | 'high';
}

interface ModelManagementState {
  // Model data
  availableModels: ModelInfo[];
  freeModels: ModelInfo[];
  affordableModels: ModelInfo[];
  selectedModel: ModelInfo | null;
  
  // Filter settings
  filterSettings: FilterSettings;
  activeFilter: 'all' | 'free' | 'affordable';
  costThreshold: number;
  
  // User preferences
  userPreferences: UserPreferences;
  
  // UI state
  isLoading: boolean;
  isLoadingModels: boolean;
  isLoadingFilter: boolean;
  error: string | null;
  
  // Analytics
  selectionHistory: ModelSelectionEvent[];
  filterUsageStats: {
    free_filter_usage: number;
    affordable_filter_usage: number;
    all_models_usage: number;
  };
  
  // Performance data
  modelPerformance: Record<string, any>;
  systemStatus: any;
}

const initialState: ModelManagementState = {
  availableModels: [],
  freeModels: [],
  affordableModels: [],
  selectedModel: null,
  
  filterSettings: {
    show_free_only: false,
    prefer_free_models: true,
    max_cost_per_token: 0.001,
  },
  activeFilter: 'all',
  costThreshold: 0.001,
  
  userPreferences: {
    preferred_providers: ['openrouter'],
    cost_tolerance: 0.001,
    prefer_free_models: true,
    auto_select_cheapest: false,
    show_performance_metrics: true,
    model_switching_frequency: 'medium',
  },
  
  isLoading: false,
  isLoadingModels: false,
  isLoadingFilter: false,
  error: null,
  
  selectionHistory: [],
  filterUsageStats: {
    free_filter_usage: 0,
    affordable_filter_usage: 0,
    all_models_usage: 0,
  },
  
  modelPerformance: {},
  systemStatus: null,
};

// Async thunks
export const fetchAvailableModels = createAsyncThunk(
  'modelManagement/fetchAvailableModels',
  async ({ provider, freeOnly }: { provider?: string; freeOnly?: boolean } = {}) => {
    const response = await modelAPI.getAvailableModels(provider, freeOnly);
    return response;
  }
);

export const fetchFreeModels = createAsyncThunk(
  'modelManagement/fetchFreeModels',
  async (provider?: string) => {
    const response = await modelAPI.getFreeModels(provider);
    return response;
  }
);

export const fetchAffordableModels = createAsyncThunk(
  'modelManagement/fetchAffordableModels',
  async ({ maxCost, provider }: { maxCost: number; provider?: string }) => {
    const response = await modelAPI.getAffordableModels(maxCost, provider);
    return response;
  }
);

export const fetchOpenRouterFilter = createAsyncThunk(
  'modelManagement/fetchOpenRouterFilter',
  async () => {
    const response = await modelAPI.getOpenRouterFilter();
    return response;
  }
);

export const updateOpenRouterFilter = createAsyncThunk(
  'modelManagement/updateOpenRouterFilter',
  async (settings: Partial<FilterSettings>) => {
    const response = await modelAPI.setOpenRouterFilter(settings);
    return response;
  }
);

export const trackModelSelection = createAsyncThunk(
  'modelManagement/trackModelSelection',
  async (data: {
    model: ModelInfo;
    userId: string;
    selectionReason?: string;
    sessionId?: string;
  }) => {
    const analyticsData = {
      model_id: data.model.model_id,
      provider: data.model.provider,
      is_free: data.model.is_free,
      cost_per_token: data.model.cost_per_token || undefined,
      selection_reason: data.selectionReason,
      user_id: data.userId,
      session_id: data.sessionId,
    };
    
    await analyticsAPI.trackModelSelection(analyticsData);
    return {
      model_id: data.model.model_id,
      provider: data.model.provider,
      is_free: data.model.is_free,
      cost_per_token: data.model.cost_per_token,
      selection_reason: data.selectionReason,
      timestamp: new Date().toISOString(),
    };
  }
);

export const trackFilterUsage = createAsyncThunk(
  'modelManagement/trackFilterUsage',
  async (data: {
    filterType: 'free_only' | 'affordable' | 'all';
    maxCostThreshold?: number;
    userId: string;
    modelsShown: number;
    modelsSelected?: number;
  }) => {
    await analyticsAPI.trackFilterUsage({
      filter_type: data.filterType,
      max_cost_threshold: data.maxCostThreshold,
      user_id: data.userId,
      models_shown: data.modelsShown,
      models_selected: data.modelsSelected,
    });
    return data.filterType;
  }
);

export const fetchSystemStatus = createAsyncThunk(
  'modelManagement/fetchSystemStatus',
  async () => {
    const response = await modelAPI.getSystemStatus();
    return response;
  }
);

const modelManagementSlice = createSlice({
  name: 'modelManagement',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    
    setSelectedModel: (state, action: PayloadAction<ModelInfo>) => {
      state.selectedModel = action.payload;
    },
    
    setActiveFilter: (state, action: PayloadAction<'all' | 'free' | 'affordable'>) => {
      state.activeFilter = action.payload;
    },
    
    setCostThreshold: (state, action: PayloadAction<number>) => {
      state.costThreshold = action.payload;
    },
    
    updateFilterSettings: (state, action: PayloadAction<Partial<FilterSettings>>) => {
      state.filterSettings = { ...state.filterSettings, ...action.payload };
    },
    
    updateUserPreferences: (state, action: PayloadAction<Partial<UserPreferences>>) => {
      state.userPreferences = { ...state.userPreferences, ...action.payload };
    },
    
    addSelectionToHistory: (state, action: PayloadAction<ModelSelectionEvent>) => {
      state.selectionHistory.unshift(action.payload);
      // Keep only last 50 selections
      if (state.selectionHistory.length > 50) {
        state.selectionHistory = state.selectionHistory.slice(0, 50);
      }
    },
    
    incrementFilterUsage: (state, action: PayloadAction<'free_filter_usage' | 'affordable_filter_usage' | 'all_models_usage'>) => {
      state.filterUsageStats[action.payload]++;
    },
    
    resetState: (state) => {
      return { ...initialState, userPreferences: state.userPreferences };
    },
  },
  
  extraReducers: (builder) => {
    // Fetch available models
    builder
      .addCase(fetchAvailableModels.pending, (state) => {
        state.isLoadingModels = true;
        state.error = null;
      })
      .addCase(fetchAvailableModels.fulfilled, (state, action) => {
        state.isLoadingModels = false;
        state.availableModels = action.payload;
      })
      .addCase(fetchAvailableModels.rejected, (state, action) => {
        state.isLoadingModels = false;
        state.error = action.error.message || 'Failed to fetch available models';
      });
    
    // Fetch free models
    builder
      .addCase(fetchFreeModels.pending, (state) => {
        state.isLoadingModels = true;
      })
      .addCase(fetchFreeModels.fulfilled, (state, action) => {
        state.isLoadingModels = false;
        state.freeModels = action.payload;
      })
      .addCase(fetchFreeModels.rejected, (state, action) => {
        state.isLoadingModels = false;
        state.error = action.error.message || 'Failed to fetch free models';
      });
    
    // Fetch affordable models
    builder
      .addCase(fetchAffordableModels.pending, (state) => {
        state.isLoadingModels = true;
      })
      .addCase(fetchAffordableModels.fulfilled, (state, action) => {
        state.isLoadingModels = false;
        state.affordableModels = action.payload;
      })
      .addCase(fetchAffordableModels.rejected, (state, action) => {
        state.isLoadingModels = false;
        state.error = action.error.message || 'Failed to fetch affordable models';
      });
    
    // Fetch OpenRouter filter
    builder
      .addCase(fetchOpenRouterFilter.pending, (state) => {
        state.isLoadingFilter = true;
      })
      .addCase(fetchOpenRouterFilter.fulfilled, (state, action) => {
        state.isLoadingFilter = false;
        if (action.payload.settings) {
          state.filterSettings = { ...state.filterSettings, ...action.payload.settings };
        }
      })
      .addCase(fetchOpenRouterFilter.rejected, (state, action) => {
        state.isLoadingFilter = false;
        state.error = action.error.message || 'Failed to fetch filter settings';
      });
    
    // Update OpenRouter filter
    builder
      .addCase(updateOpenRouterFilter.pending, (state) => {
        state.isLoadingFilter = true;
      })
      .addCase(updateOpenRouterFilter.fulfilled, (state, action) => {
        state.isLoadingFilter = false;
        if (action.payload.settings) {
          state.filterSettings = { ...state.filterSettings, ...action.payload.settings };
        }
      })
      .addCase(updateOpenRouterFilter.rejected, (state, action) => {
        state.isLoadingFilter = false;
        state.error = action.error.message || 'Failed to update filter settings';
      });
    
    // Track model selection
    builder
      .addCase(trackModelSelection.fulfilled, (state, action) => {
        state.selectionHistory.unshift(action.payload);
        if (state.selectionHistory.length > 50) {
          state.selectionHistory = state.selectionHistory.slice(0, 50);
        }
      });
    
    // Track filter usage
    builder
      .addCase(trackFilterUsage.fulfilled, (state, action) => {
        const filterType = action.payload;
        if (filterType === 'free_only') {
          state.filterUsageStats.free_filter_usage++;
        } else if (filterType === 'affordable') {
          state.filterUsageStats.affordable_filter_usage++;
        } else {
          state.filterUsageStats.all_models_usage++;
        }
      });
    
    // Fetch system status
    builder
      .addCase(fetchSystemStatus.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchSystemStatus.fulfilled, (state, action) => {
        state.isLoading = false;
        state.systemStatus = action.payload;
      })
      .addCase(fetchSystemStatus.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch system status';
      });
  },
});

export const {
  clearError,
  setSelectedModel,
  setActiveFilter,
  setCostThreshold,
  updateFilterSettings,
  updateUserPreferences,
  addSelectionToHistory,
  incrementFilterUsage,
  resetState,
} = modelManagementSlice.actions;

export default modelManagementSlice.reducer;
