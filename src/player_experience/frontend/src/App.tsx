import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from './store/store';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import CharacterManagement from './pages/CharacterManagement/CharacterManagement';
import WorldSelection from './pages/WorldSelection/WorldSelection';
import Settings from './pages/Settings/Settings';
import Chat from './pages/Chat/Chat';
import Login from './pages/Auth/Login';
import './App.css';

function App() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/characters" element={<CharacterManagement />} />
          <Route path="/worlds" element={<WorldSelection />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/chat/:sessionId?" element={<Chat />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App;