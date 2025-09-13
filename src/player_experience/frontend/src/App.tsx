import React, { useEffect, useRef } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "./store/store";
import { fetchPlayerProfile } from "./store/slices/playerSlice";
import Layout from "./components/Layout/Layout";
import Dashboard from "./pages/Dashboard/Dashboard";
import CharacterManagement from "./pages/CharacterManagement/CharacterManagement";
import WorldSelection from "./pages/WorldSelection/WorldSelection";
import Settings from "./pages/Settings/Settings";
import Chat from "./pages/Chat/Chat";
import Login from "./pages/Auth/Login";
import SearchPage from "./pages/SearchPage";
import NexusPage from "./pages/NexusPage";
import { ErrorBoundary, APIErrorBoundary } from "./components/ErrorBoundary";
import { StatusMonitoringDisplay } from "./components/Status";
import "./App.css";

function App() {
  const renderCount = useRef(0);
  renderCount.current += 1;

  // Debug logging to track re-renders
  console.log(`🔄 App render #${renderCount.current}`, {
    timestamp: new Date().toISOString(),
  });

  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector(
    (state: RootState) => state.auth
  );
  const { profile, isLoading: profileLoading } = useSelector(
    (state: RootState) => state.player
  );

  // Debug state changes
  useEffect(() => {
    console.log("🔍 App auth state changed:", {
      isAuthenticated,
      userId: user?.user_id,
    });
  }, [isAuthenticated, user?.user_id]);

  useEffect(() => {
    console.log("🔍 App profile state changed:", {
      profile: profile?.player_id,
      profileLoading,
    });
  }, [profile, profileLoading]);

  // Load player profile when user is authenticated
  useEffect(() => {
    console.log("🔍 App fetchPlayerProfile effect triggered");
    if (isAuthenticated && user?.user_id && !profile && !profileLoading) {
      console.log("🚀 Dispatching fetchPlayerProfile for:", user.user_id);
      dispatch(fetchPlayerProfile(user.user_id) as any);
    }
  }, [dispatch, isAuthenticated, user?.user_id, profile, profileLoading]);

  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <APIErrorBoundary>
          <Login />
        </APIErrorBoundary>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary
      showDetails={process.env.NODE_ENV === "development"}
      onError={(error, errorInfo) => {
        console.error("App Error:", error, errorInfo);
        // Could send to analytics service
      }}
    >
      <div className="App">
        {/* Global Status Monitoring */}
        <div className="fixed top-0 right-0 z-50 p-4">
          <StatusMonitoringDisplay
            variant="compact"
            className="bg-white shadow-lg border border-gray-200"
            showAlerts={false}
          />
        </div>

        <APIErrorBoundary>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/characters" element={<CharacterManagement />} />
              <Route path="/worlds" element={<WorldSelection />} />
              <Route path="/nexus" element={<NexusPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/chat/:sessionId?" element={<Chat />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        </APIErrorBoundary>
      </div>
    </ErrorBoundary>
  );
}

export default App;
