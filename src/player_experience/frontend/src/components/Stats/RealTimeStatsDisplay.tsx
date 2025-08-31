import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  useRealTimeUpdates,
  WorldStatistics,
} from "../../hooks/useRealTimeUpdates";

interface RealTimeStatsDisplayProps {
  worldId?: string;
  variant?: "compact" | "detailed" | "widget";
  className?: string;
  showConnectionStatus?: boolean;
  animateChanges?: boolean;
}

const RealTimeStatsDisplay: React.FC<RealTimeStatsDisplayProps> = ({
  worldId,
  variant = "detailed",
  className = "",
  showConnectionStatus = true,
  animateChanges = true,
}) => {
  const {
    isConnected,
    lastUpdate,
    worldStats,
    globalStats,
    connectionType,
    error,
    reconnect,
    clearError,
  } = useRealTimeUpdates({
    enableWebSocket: true,
    enablePolling: true,
    pollingInterval: 20000,
    onUpdate: (update) => {
      console.log("Real-time update received:", update);
    },
    onError: (error) => {
      console.error("Real-time update error:", error);
    },
  });

  const [previousStats, setPreviousStats] = useState<any>(null);
  const [changedFields, setChangedFields] = useState<Set<string>>(new Set());

  // Track changes for animations
  useEffect(() => {
    if (!animateChanges) return;

    const currentStats = worldId ? worldStats.get(worldId) : globalStats;

    if (previousStats && currentStats) {
      const changes = new Set<string>();

      Object.keys(currentStats).forEach((key) => {
        if ((previousStats as any)[key] !== (currentStats as any)[key]) {
          changes.add(key);
        }
      });

      setChangedFields(changes);

      // Clear change indicators after animation
      const timer = setTimeout(() => {
        setChangedFields(new Set());
      }, 2000);

      return () => clearTimeout(timer);
    }

    setPreviousStats(currentStats);
  }, [worldStats, globalStats, worldId, previousStats, animateChanges]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  const formatDuration = (minutes: number) => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}h ${mins}m`;
    }
    return `${minutes}m`;
  };

  const getConnectionStatusColor = () => {
    if (!isConnected) return "text-red-500";
    if (connectionType === "websocket") return "text-green-500";
    if (connectionType === "polling") return "text-yellow-500";
    return "text-gray-500";
  };

  const getConnectionStatusIcon = () => {
    if (!isConnected) return "🔴";
    if (connectionType === "websocket") return "🟢";
    if (connectionType === "polling") return "🟡";
    return "⚪";
  };

  const StatItem: React.FC<{
    label: string;
    value: string | number;
    fieldKey: string;
    icon?: string;
    color?: string;
  }> = ({ label, value, fieldKey, icon, color = "text-gray-900" }) => {
    const isChanged = changedFields.has(fieldKey);

    return (
      <motion.div
        className={`${
          isChanged ? "bg-blue-50 border-blue-200" : "bg-gray-50"
        } rounded-lg p-3 transition-colors duration-500`}
        animate={isChanged ? { scale: [1, 1.05, 1] } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {icon && <span className="text-lg">{icon}</span>}
            <span className="text-sm text-gray-600">{label}</span>
          </div>
          <motion.span
            className={`text-lg font-semibold ${color} ${
              isChanged ? "text-blue-600" : ""
            }`}
            animate={isChanged ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 0.3 }}
          >
            {value}
          </motion.span>
        </div>
      </motion.div>
    );
  };

  const renderWorldStats = (stats: WorldStatistics) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          World Statistics
        </h3>
        {showConnectionStatus && (
          <div className="flex items-center space-x-2 text-sm">
            <span className={getConnectionStatusColor()}>
              {getConnectionStatusIcon()} {connectionType}
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatItem
          label="Active Players"
          value={formatNumber(stats.active_players)}
          fieldKey="active_players"
          icon="👥"
          color="text-blue-600"
        />

        <StatItem
          label="Completion Rate"
          value={formatPercentage(stats.completion_rate)}
          fieldKey="completion_rate"
          icon="✅"
          color="text-green-600"
        />

        <StatItem
          label="Avg Session"
          value={formatDuration(stats.average_session_duration)}
          fieldKey="average_session_duration"
          icon="⏱️"
          color="text-purple-600"
        />

        <StatItem
          label="Narrative Strength"
          value={formatPercentage(stats.narrative_strength)}
          fieldKey="narrative_strength"
          icon="⚡"
          color="text-orange-600"
        />
      </div>

      {stats.last_updated && (
        <div className="text-xs text-gray-500 text-center">
          Last updated: {new Date(stats.last_updated).toLocaleTimeString()}
        </div>
      )}
    </div>
  );

  const renderGlobalStats = () => {
    if (!globalStats) return null;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Global Statistics
          </h3>
          {showConnectionStatus && (
            <div className="flex items-center space-x-2 text-sm">
              <span className={getConnectionStatusColor()}>
                {getConnectionStatusIcon()} {connectionType}
              </span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatItem
            label="Total Players"
            value={formatNumber(globalStats.totalPlayers)}
            fieldKey="totalPlayers"
            icon="👥"
            color="text-blue-600"
          />

          <StatItem
            label="Active Worlds"
            value={formatNumber(globalStats.activeWorlds)}
            fieldKey="activeWorlds"
            icon="🌍"
            color="text-green-600"
          />

          <StatItem
            label="Narrative Strength"
            value={formatPercentage(globalStats.narrativeStrength)}
            fieldKey="narrativeStrength"
            icon="⚡"
            color="text-purple-600"
          />

          <StatItem
            label="System Health"
            value={globalStats.systemHealth}
            fieldKey="systemHealth"
            icon="💚"
            color="text-emerald-600"
          />
        </div>
      </div>
    );
  };

  const renderCompactView = () => {
    const stats = worldId ? worldStats.get(worldId) : null;
    const displayStats = stats || globalStats;

    if (!displayStats) return null;

    return (
      <div className="flex items-center space-x-4">
        {showConnectionStatus && (
          <div className="flex items-center space-x-1 text-xs">
            <span className={getConnectionStatusColor()}>
              {getConnectionStatusIcon()}
            </span>
            <span className="text-gray-600">{connectionType}</span>
          </div>
        )}

        <div className="flex items-center space-x-4 text-sm">
          {stats ? (
            <>
              <span className="flex items-center space-x-1">
                <span>👥</span>
                <span>{formatNumber(stats.active_players)}</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>⚡</span>
                <span>{formatPercentage(stats.narrative_strength)}</span>
              </span>
            </>
          ) : globalStats ? (
            <>
              <span className="flex items-center space-x-1">
                <span>👥</span>
                <span>{formatNumber(globalStats.totalPlayers)}</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>🌍</span>
                <span>{formatNumber(globalStats.activeWorlds)}</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>⚡</span>
                <span>{formatPercentage(globalStats.narrativeStrength)}</span>
              </span>
            </>
          ) : null}
        </div>
      </div>
    );
  };

  const renderWidgetView = () => (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-900">Live Stats</h4>
        {showConnectionStatus && (
          <div className="flex items-center space-x-1">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-green-500" : "bg-red-500"
              }`}
            ></div>
            <span className="text-xs text-gray-600">{connectionType}</span>
          </div>
        )}
      </div>

      {worldId && worldStats.has(worldId) ? (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Players:</span>
            <span className="font-medium">
              {formatNumber(worldStats.get(worldId)!.active_players)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Strength:</span>
            <span className="font-medium">
              {formatPercentage(worldStats.get(worldId)!.narrative_strength)}
            </span>
          </div>
        </div>
      ) : globalStats ? (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total Players:</span>
            <span className="font-medium">
              {formatNumber(globalStats.totalPlayers)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Active Worlds:</span>
            <span className="font-medium">
              {formatNumber(globalStats.activeWorlds)}
            </span>
          </div>
        </div>
      ) : (
        <div className="text-sm text-gray-500">No data available</div>
      )}
    </div>
  );

  if (error && !isConnected) {
    return (
      <div
        className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-red-500">⚠️</span>
            <div>
              <h4 className="text-sm font-medium text-red-800">
                Connection Error
              </h4>
              <p className="text-xs text-red-600">{error}</p>
            </div>
          </div>
          <button
            onClick={() => {
              clearError();
              reconnect();
            }}
            className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm ${className}`}>
      {variant === "compact" && renderCompactView()}
      {variant === "detailed" && (
        <div className="p-6">
          {worldId && worldStats.has(worldId)
            ? renderWorldStats(worldStats.get(worldId)!)
            : renderGlobalStats()}
        </div>
      )}
      {variant === "widget" && renderWidgetView()}

      {lastUpdate && variant === "detailed" && (
        <div className="px-6 pb-4">
          <div className="text-xs text-gray-400 text-center">
            Last update: {new Date(lastUpdate.timestamp).toLocaleTimeString()}{" "}
            via {lastUpdate.source}
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeStatsDisplay;
