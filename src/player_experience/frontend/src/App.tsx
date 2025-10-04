import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from './store/store';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import CharacterManagement from './pages/CharacterManagement/CharacterManagement';
import WorldSelection from './pages/WorldSelection/WorldSelection';
import Settings from './pages/Settings/Settings';
import Preferences from './pages/Preferences/Preferences';
import Chat from './pages/Chat/Chat';
import Login from './pages/Auth/Login';
import { PreferencesOnboarding } from './components/Onboarding';
import { useEntertainmentMode } from './hooks/useUIMode';
import AnalyticsPage from './pages/Analytics/AnalyticsPage';
import './App.css';

function App() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  const { isReady, isLoading } = useEntertainmentMode();

  if (!isAuthenticated) {
    return <Login />;
  }

  // Show loading while initializing entertainment mode
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Preparing Your Adventure</h2>
          <p className="text-gray-600">Setting up your personalized experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/characters" element={<CharacterManagement />} />
          <Route path="/worlds" element={<WorldSelection />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/preferences" element={<Preferences />} />
          <Route path="/onboarding/preferences" element={<PreferencesOnboarding />} />
          <Route path="/chat/:sessionId?" element={<Chat />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App;