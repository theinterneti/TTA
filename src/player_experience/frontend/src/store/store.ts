// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Store]]
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import playerReducer from './slices/playerSlice';
import characterReducer from './slices/characterSlice';
import worldReducer from './slices/worldSlice';
import chatReducer from './slices/chatSlice';
import settingsReducer from './slices/settingsSlice';
import modelManagementReducer from './slices/modelManagementSlice';
import openRouterAuthReducer from './slices/openRouterAuthSlice';
import playerPreferencesReducer from './slices/playerPreferencesSlice';
import realTimeMonitoringReducer from './slices/realTimeMonitoringSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    player: playerReducer,
    character: characterReducer,
    world: worldReducer,
    chat: chatReducer,
    settings: settingsReducer,
    modelManagement: modelManagementReducer,
    openRouterAuth: openRouterAuthReducer,
    playerPreferences: playerPreferencesReducer,
    realTimeMonitoring: realTimeMonitoringReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
