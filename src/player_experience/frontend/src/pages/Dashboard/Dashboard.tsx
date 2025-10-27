import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchCharacters } from '../../store/slices/characterSlice';
import { fetchPlayerDashboard } from '../../store/slices/playerSlice';
import { RootState } from '../../store/store';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { profile, dashboard, isLoading } = useSelector((state: RootState) => state.player);
  const { characters, isLoading: charactersLoading } = useSelector((state: RootState) => state.character);

  useEffect(() => {
    if (profile?.player_id) {
      dispatch(fetchPlayerDashboard(profile.player_id) as any);
      dispatch(fetchCharacters(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  if (isLoading || charactersLoading) {
    return (
      <div data-testid="dashboard-loading" className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">
          {isLoading ? 'Loading dashboard...' : 'Loading characters...'}
        </span>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-container" className="space-y-6">
      {/* Welcome Section */}
      <div data-testid="dashboard-welcome-section" className="bg-white rounded-lg shadow-md p-6">
        <h1 data-testid="dashboard-welcome-title" className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {profile?.username}!
        </h1>
        <p data-testid="dashboard-welcome-message" className="text-gray-600">
          Ready to continue your therapeutic journey? Here's what's happening in your world.
        </p>
      </div>

      {/* Quick Stats */}
      <div data-testid="dashboard-stats-section" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div data-testid="dashboard-stat-characters" className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Characters</p>
              <p data-testid="dashboard-stat-characters-count" className="text-2xl font-bold text-gray-900">{characters.length}</p>
            </div>
          </div>
        </div>

        <div data-testid="dashboard-stat-sessions" className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p data-testid="dashboard-stat-sessions-count" className="text-2xl font-bold text-gray-900">
                {Object.keys(profile?.active_sessions || {}).length}
              </p>
            </div>
          </div>
        </div>

        <div data-testid="dashboard-stat-progress" className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Progress Level</p>
              <p data-testid="dashboard-stat-progress-level" className="text-2xl font-bold text-gray-900">
                {profile?.therapeutic_preferences.intensity_level || 'Medium'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div data-testid="dashboard-activity-section" className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div data-testid="dashboard-recent-sessions" className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions</h3>
          {dashboard?.recent_sessions && dashboard.recent_sessions.length > 0 ? (
            <div data-testid="dashboard-sessions-list" className="space-y-3">
              {dashboard.recent_sessions.slice(0, 3).map((session: any, index: number) => (
                <div key={index} data-testid={`dashboard-session-item-${index}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{session.character_name}</p>
                    <p className="text-sm text-gray-600">{session.world_name}</p>
                  </div>
                  <span className="text-xs text-gray-500">{session.last_activity}</span>
                </div>
              ))}
            </div>
          ) : (
            <p data-testid="dashboard-sessions-empty" className="text-gray-500 text-center py-8">No recent sessions</p>
          )}
        </div>

        <div data-testid="dashboard-recommendations" className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          {dashboard?.recommendations && dashboard.recommendations.length > 0 ? (
            <div data-testid="dashboard-recommendations-list" className="space-y-3">
              {dashboard.recommendations.slice(0, 3).map((rec: any, index: number) => (
                <div key={index} data-testid={`dashboard-recommendation-item-${index}`} className="p-3 bg-therapeutic-calm rounded-lg border border-blue-200">
                  <p className="font-medium text-gray-900">{rec.title}</p>
                  <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p data-testid="dashboard-recommendations-empty" className="text-gray-500 text-center py-8">No recommendations available</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div data-testid="dashboard-quick-actions" className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button
            data-testid="dashboard-manage-characters-button"
            className="btn-primary text-center py-4"
            onClick={() => navigate('/characters')}
          >
            {characters.length === 0 ? 'Create First Character' : 'Manage Characters'}
          </button>
          <button
            data-testid="dashboard-explore-worlds-button"
            className="btn-secondary text-center py-4"
            onClick={() => navigate('/worlds')}
          >
            Explore Worlds
          </button>
          <button
            data-testid="dashboard-continue-session-button"
            className="btn-secondary text-center py-4"
            onClick={() => navigate('/chat')}
            disabled={characters.length === 0}
            title={characters.length === 0 ? 'Create a character first to start a session' : 'Continue your last session'}
          >
            Continue Last Session
          </button>
          <button
            data-testid="dashboard-view-analytics-button"
            className="btn-secondary text-center py-4 bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100"
            onClick={() => navigate('/analytics')}
          >
            View Analytics
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
