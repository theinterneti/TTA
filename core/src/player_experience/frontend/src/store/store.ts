import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import playerReducer from "./slices/playerSlice";
import characterReducer from "./slices/characterSlice";
import conversationalCharacterReducer from "./slices/conversationalCharacterSlice";
import worldReducer from "./slices/worldSlice";
import chatReducer from "./slices/chatSlice";
import settingsReducer from "./slices/settingsSlice";
import { enhancedActionLogger } from "../utils/debugUtils";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    player: playerReducer,
    character: characterReducer,
    conversationalCharacter: conversationalCharacterReducer,
    world: worldReducer,
    chat: chatReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ["persist/PERSIST", "persist/REHYDRATE"],
      },
    }).concat(enhancedActionLogger),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
