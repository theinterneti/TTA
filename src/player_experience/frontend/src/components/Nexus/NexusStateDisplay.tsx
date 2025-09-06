import React from "react";
import { motion } from "framer-motion";
import { useNexusState } from "../../hooks/useNexusState";
// import { NexusState } from "../../hooks/useNexusState"; // TODO: Implement NexusState type usage
import { useRealTimeUpdates } from "../../hooks/useRealTimeUpdates";

interface NexusStateDisplayProps {
  variant?: "compact" | "detailed" | "dashboard";
  className?: string;
  showLastUpdated?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const NexusStateDisplay: React.FC<NexusStateDisplayProps> = ({
  variant = "detailed",
  className = "",
  showLastUpdated = true,
  autoRefresh = true,
  refreshInterval = 30000,
}) => {
  const {
    state,
    loading,
    error,
    refetch,
    clearError,
    lastUpdated,
    isConnected,
  } = useNexusState({
    autoRefresh,
    refreshInterval,
    requireAuth: false, // Allow public access to basic state
  });

  // Real-time updates for enhanced statistics
  const {
    isConnected: realtimeConnected,
    globalStats: realtimeStats,
    connectionType,
    error: realtimeError,
  } = useRealTimeUpdates({
    enableWebSocket: true,
    enablePolling: true,
    pollingInterval: refreshInterval,
  });

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case "healthy":
        return "text-green-600 bg-green-100";
      case "degraded":
        return "text-yellow-600 bg-yellow-100";
      case "critical":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getSystemHealthIcon = (health: string) => {
    switch (health) {
      case "healthy":
        return "✅";
      case "degraded":
        return "⚠️";
      case "critical":
        return "🚨";
      default:
        return "❓";
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  if (loading && !state) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
          <div className="space-y-2">
            <div className="h-3 bg-gray-200 rounded w-full"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !state) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <div className="text-center">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <h3 className="text-sm font-medium text-red-800 mb-1">
            Connection Error
          </h3>
          <p className="text-xs text-red-600 mb-3">{error}</p>
          {realtimeError && (
            <p className="text-xs text-orange-600 mb-3">
              Real-time updates unavailable: {realtimeError}
            </p>
          )}
          <button
            onClick={() => {
              clearError();
              refetch();
            }}
            className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!state) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <div className="text-center text-gray-500 text-sm">
          No nexus state available
        </div>
      </div>
    );
  }

  const renderCompactView = () => {
    // Use real-time stats if available, fallback to regular state
    const displayStats = realtimeStats || {
      totalPlayers: state?.total_players || 0,
      activeWorlds: state?.active_worlds || 0,
      narrativeStrength: state?.narrative_strength || 0,
      systemHealth: state?.system_health || "unknown",
    };

    return (
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div
            className={`px-2 py-1 rounded-full text-xs font-medium ${getSystemHealthColor(
              displayStats.systemHealth
            )}`}
          >
            {getSystemHealthIcon(displayStats.systemHealth)}{" "}
            {displayStats.systemHealth.toUpperCase()}
          </div>
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>🌍 {formatNumber(displayStats.activeWorlds)} worlds</span>
          <span>👥 {formatNumber(displayStats.totalPlayers)} players</span>
          <span>
            ⚡ {formatPercentage(displayStats.narrativeStrength)} strength
          </span>
        </div>

        {/* Connection Status Indicators */}
        <div className="flex items-center space-x-2">
          {realtimeConnected && (
            <div className="flex items-center space-x-1 text-xs">
              <div
                className={`w-2 h-2 rounded-full ${
                  connectionType === "websocket"
                    ? "bg-green-500"
                    : "bg-yellow-500"
                }`}
              ></div>
              <span className="text-gray-500">
                {connectionType === "websocket" ? "Live" : "Polling"}
              </span>
            </div>
          )}

          {!isConnected && !realtimeConnected && (
            <div className="text-xs text-red-500 flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
              Disconnected
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderDetailedView = () => (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Nexus Status</h3>
        <div className="flex items-center space-x-2">
          <div
            className={`px-2 py-1 rounded-full text-xs font-medium ${getSystemHealthColor(
              state.system_health
            )}`}
          >
            {getSystemHealthIcon(state.system_health)}{" "}
            {state.system_health.toUpperCase()}
          </div>
          {!isConnected && (
            <div className="text-xs text-red-500 flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
              Disconnected
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-blue-600">
            {formatNumber(state.active_worlds)}
          </div>
          <div className="text-xs text-blue-800">Active Worlds</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-green-50 rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-green-600">
            {formatNumber(state.total_players)}
          </div>
          <div className="text-xs text-green-800">Total Players</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-purple-50 rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-purple-600">
            {formatNumber(state.active_sessions)}
          </div>
          <div className="text-xs text-purple-800">Active Sessions</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-orange-50 rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-orange-600">
            {formatNumber(state.pending_worlds)}
          </div>
          <div className="text-xs text-orange-800">Pending Worlds</div>
        </motion.div>
      </div>

      {/* Progress Bars */}
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700">Narrative Strength</span>
            <span className="text-gray-900 font-medium">
              {formatPercentage(state.narrative_strength)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${state.narrative_strength * 100}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700">Hub Energy</span>
            <span className="text-gray-900 font-medium">
              {formatPercentage(state.hub_energy)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${state.hub_energy * 100}%` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
              className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full"
            />
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {state.maintenance_mode && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center">
            <div className="text-yellow-600 mr-2">🔧</div>
            <div>
              <div className="text-sm font-medium text-yellow-800">
                Maintenance Mode
              </div>
              <div className="text-xs text-yellow-700">
                Some features may be temporarily unavailable
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Last Updated */}
      {showLastUpdated && lastUpdated && (
        <div className="text-xs text-gray-500 text-center">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}
    </div>
  );

  const renderDashboardView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* System Health Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-medium text-gray-900">System Health</h4>
          <div
            className={`px-3 py-1 rounded-full text-sm font-medium ${getSystemHealthColor(
              state.system_health
            )}`}
          >
            {getSystemHealthIcon(state.system_health)}{" "}
            {state.system_health.toUpperCase()}
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Status</span>
            <span className="text-sm font-medium">{state.status}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Connection</span>
            <span
              className={`text-sm font-medium ${
                isConnected ? "text-green-600" : "text-red-600"
              }`}
            >
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>
      </div>

      {/* Activity Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h4 className="text-sm font-medium text-gray-900 mb-4">
          Current Activity
        </h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Active Worlds</span>
            <span className="text-sm font-medium">
              {formatNumber(state.active_worlds)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Total Players</span>
            <span className="text-sm font-medium">
              {formatNumber(state.total_players)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Active Sessions</span>
            <span className="text-sm font-medium">
              {formatNumber(state.active_sessions)}
            </span>
          </div>
        </div>
      </div>

      {/* Performance Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h4 className="text-sm font-medium text-gray-900 mb-4">Performance</h4>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Narrative Strength</span>
              <span className="font-medium">
                {formatPercentage(state.narrative_strength)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all duration-1000"
                style={{ width: `${state.narrative_strength * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Hub Energy</span>
              <span className="font-medium">
                {formatPercentage(state.hub_energy)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-green-600 h-1.5 rounded-full transition-all duration-1000"
                style={{ width: `${state.hub_energy * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`${className}`}>
      {variant === "compact" && renderCompactView()}
      {variant === "detailed" && renderDetailedView()}
      {variant === "dashboard" && renderDashboardView()}
    </div>
  );
};

export default NexusStateDisplay;
