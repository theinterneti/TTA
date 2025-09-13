import React, { useEffect, useCallback, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { RootState } from "../../store/store";
import { fetchPlayerDashboard } from "../../store/slices/playerSlice";

const Dashboard: React.FC = () => {
  const renderCount = useRef(0);
  renderCount.current += 1;

  // Debug logging to track re-renders
  console.log(`🔄 Dashboard render #${renderCount.current}`, {
    timestamp: new Date().toISOString(),
  });

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { profile, dashboard, isLoading } = useSelector(
    (state: RootState) => state.player
  );
  const { characters } = useSelector((state: RootState) => state.character);

  // Debug state changes
  useEffect(() => {
    console.log("🔍 Dashboard profile changed:", profile?.player_id);
  }, [profile]);

  useEffect(() => {
    console.log("🔍 Dashboard characters changed:", characters.length);
  }, [characters]);

  useEffect(() => {
    console.log("🔍 Dashboard fetchPlayerDashboard effect triggered");
    if (profile?.player_id) {
      console.log(
        "🚀 Dispatching fetchPlayerDashboard for:",
        profile.player_id
      );
      dispatch(fetchPlayerDashboard(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  const handleNavigateToCharacters = useCallback(() => {
    navigate("/characters");
  }, [navigate]);

  const handleNavigateToWorlds = useCallback(() => {
    navigate("/worlds");
  }, [navigate]);

  const handleNavigateToChat = useCallback(() => {
    navigate("/chat");
  }, [navigate]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {profile?.username || "User"}!
        </h1>
        <p className="text-gray-600">
          Ready to continue your therapeutic journey? Here's what's happening in
          your world.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Characters</p>
              <p className="text-2xl font-bold text-gray-900">
                {characters.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Active Sessions
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.keys(profile?.active_sessions || {}).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Progress Level
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {profile?.therapeutic_preferences.intensity_level || "Medium"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Sessions
          </h3>
          {dashboard?.recent_sessions &&
          dashboard.recent_sessions.length > 0 ? (
            <div className="space-y-3">
              {dashboard.recent_sessions
                .slice(0, 3)
                .map((session: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">
                        {session.character_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {session.world_name}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {session.last_activity}
                    </span>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recent sessions</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recommendations
          </h3>
          {dashboard?.recommendations &&
          dashboard.recommendations.length > 0 ? (
            <div className="space-y-3">
              {dashboard.recommendations
                .slice(0, 3)
                .map((rec: any, index: number) => (
                  <div
                    key={index}
                    className="p-3 bg-therapeutic-calm rounded-lg border border-blue-200"
                  >
                    <p className="font-medium text-gray-900">{rec.title}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {rec.description}
                    </p>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No recommendations available
            </p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            className="btn-primary text-center py-4"
            onClick={handleNavigateToCharacters}
          >
            {characters.length === 0
              ? "Create First Character"
              : "Manage Characters"}
          </button>
          <button
            className="btn-secondary text-center py-4"
            onClick={handleNavigateToWorlds}
          >
            Explore Worlds
          </button>
          <button
            className="btn-secondary text-center py-4"
            onClick={handleNavigateToChat}
            disabled={characters.length === 0}
          >
            {characters.length === 0
              ? "Create Character First"
              : "Continue Last Session"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
