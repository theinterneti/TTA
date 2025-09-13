/**
 * Redux Store Configuration for TTA Therapeutic Gaming Experience
 *
 * Manages application state including user authentication, characters,
 * sessions, and therapeutic progress.
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import charactersReducer from './slices/charactersSlice';
import worldsReducer from './slices/worldsSlice';
import sessionsReducer from './slices/sessionsSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    characters: charactersReducer,
    worlds: worldsReducer,
    sessions: sessionsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
