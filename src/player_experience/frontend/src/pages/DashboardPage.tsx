import React from 'react';
import { useNavigate } from 'react-router-dom';
import PlayerDashboard from '../components/Progress/PlayerDashboard';
import { useDashboardData } from '../hooks/useDashboardData';
import { useAuth } from '../hooks/useAuth';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    data: dashboardData,
    loading,
    error,
    refresh,
    dismissHighlight,
    updateCharacterActivity,
  } = useDashboardData({
    playerId: user?.id || '',
    refreshInterval: 30000,
    autoRefresh: true,
  });

  const handleCharacterSelect = (characterId: string) => {
    updateCharacterActivity(characterId);
    navigate(`/characters/${characterId}`);
  };

  const handleSessionStart = (characterId: string, worldId: string) => {
    updateCharacterActivity(characterId);
    navigate(`/chat?character=${characterId}&world=${worldId}`);
  };

  const handleHighlightDismiss = (highlightId: string) => {
    dismissHighlight(highlightId);
  };

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <h3 className="font-bold">Error Loading Dashboard</h3>
            <p className="text-sm mt-1">{error}</p>
          </div>
          <button
            onClick={refresh}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No dashboard data available.</p>
          <button
            onClick={refresh}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <PlayerDashboard
        dashboardData={dashboardData}
        onCharacterSelect={handleCharacterSelect}
        onSessionStart={handleSessionStart}
        onHighlightDismiss={handleHighlightDismiss}
        refreshInterval={30000}
      />
    </div>
  );
};

export default DashboardPage;
