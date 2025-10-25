import { Navigate, Route, Routes } from 'react-router-dom';
import './App.css';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Layout from './components/Layout/Layout';
import { PreferencesOnboarding } from './components/Onboarding';
import AnalyticsPage from './pages/Analytics/AnalyticsPage';
import Login from './pages/Auth/Login';
import CharacterManagement from './pages/CharacterManagement/CharacterManagement';
import Chat from './pages/Chat/Chat';
import Dashboard from './pages/Dashboard/Dashboard';
import Preferences from './pages/Preferences/Preferences';
import Settings from './pages/Settings/Settings';
import WorldSelection from './pages/WorldSelection/WorldSelection';

function App() {
  return (
    <div className="App">
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Navigate to="/dashboard" replace />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Layout>
                <AnalyticsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/characters"
          element={
            <ProtectedRoute>
              <Layout>
                <CharacterManagement />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/worlds"
          element={
            <ProtectedRoute>
              <Layout>
                <WorldSelection />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/preferences"
          element={
            <ProtectedRoute>
              <Layout>
                <Preferences />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/onboarding/preferences"
          element={
            <ProtectedRoute>
              <Layout>
                <PreferencesOnboarding />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat/:sessionId?"
          element={
            <ProtectedRoute>
              <Layout>
                <Chat />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

export default App;
