import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { nexusAPI } from "../../services/api";
import { useWorldRealTimeUpdates } from "../../hooks/useRealTimeUpdates";

interface WorldData {
  world_id: string;
  world_title: string;
  world_genre: string;
  world_rating: number;
  threat_level?: string;
  narrative_strength?: number;
  description?: string;
  difficulty_level?: string;
  estimated_duration?: number;
  tags?: string[];
  created_by?: string;
  last_updated?: string;
  player_count?: number;
  completion_rate?: number;
}

interface WorldCardProps {
  worldId: string;
  onEnterWorld?: (worldId: string) => void;
  onViewDetails?: (worldId: string) => void;
  className?: string;
  variant?: "default" | "compact" | "detailed";
}

const WorldCard: React.FC<WorldCardProps> = ({
  worldId,
  onEnterWorld,
  onViewDetails,
  className = "",
  variant = "default",
}) => {
  const [worldData, setWorldData] = useState<WorldData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageError, setImageError] = useState(false);

  // Real-time updates for this specific world
  const { worldStats, isConnected: realtimeConnected } =
    useWorldRealTimeUpdates(worldId);

  useEffect(() => {
    const fetchWorldData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await nexusAPI.getWorld(worldId);
        setWorldData(response.world || response);
      } catch (err: any) {
        console.error("Failed to fetch world data:", err);
        setError(err.message || "Failed to load world information");
      } finally {
        setLoading(false);
      }
    };

    if (worldId) {
      fetchWorldData();
    }
  }, [worldId]);

  const handleEnterWorld = () => {
    if (onEnterWorld && worldData) {
      onEnterWorld(worldData.world_id);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails && worldData) {
      onViewDetails(worldData.world_id);
    }
  };

  const getThreatLevelColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case "low":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "critical":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getDifficultyColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case "beginner":
        return "bg-green-100 text-green-800";
      case "intermediate":
        return "bg-yellow-100 text-yellow-800";
      case "advanced":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-2/3 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={`bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500 ${className}`}
      >
        <div className="flex items-center">
          <div className="text-red-500 mr-3">⚠️</div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Error Loading World
            </h3>
            <p className="text-sm text-gray-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!worldData) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <p className="text-gray-500 text-center">World not found</p>
      </div>
    );
  }

  const cardVariants = {
    default:
      "bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200",
    compact:
      "bg-white rounded-md shadow-sm hover:shadow-md transition-shadow duration-200",
    detailed:
      "bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-200",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`${cardVariants[variant]} ${className}`}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {worldData.world_title}
            </h3>
            <div className="flex items-center space-x-2 mb-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {worldData.world_genre}
              </span>
              {worldData.threat_level && (
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getThreatLevelColor(
                    worldData.threat_level
                  )}`}
                >
                  {worldData.threat_level}
                </span>
              )}
              {worldData.difficulty_level && (
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(
                    worldData.difficulty_level
                  )}`}
                >
                  {worldData.difficulty_level}
                </span>
              )}
            </div>
          </div>

          {/* Rating */}
          <div className="flex items-center ml-4">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <span
                  key={i}
                  className={`text-sm ${
                    i < worldData.world_rating
                      ? "text-yellow-400"
                      : "text-gray-300"
                  }`}
                >
                  ★
                </span>
              ))}
            </div>
            <span className="ml-1 text-sm text-gray-600">
              {worldData.world_rating}/5
            </span>
          </div>
        </div>

        {/* Description */}
        {worldData.description && variant !== "compact" && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {worldData.description}
          </p>
        )}

        {/* Stats */}
        {variant === "detailed" && (
          <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
            {worldData.narrative_strength && (
              <div>
                <span className="text-gray-500">Narrative Strength:</span>
                <div className="font-semibold text-blue-600">
                  {worldData.narrative_strength}%
                </div>
              </div>
            )}
            {worldData.estimated_duration && (
              <div>
                <span className="text-gray-500">Duration:</span>
                <div className="font-semibold">
                  {worldData.estimated_duration} min
                </div>
              </div>
            )}
            {worldData.player_count !== undefined && (
              <div>
                <span className="text-gray-500">Active Players:</span>
                <div className="font-semibold">{worldData.player_count}</div>
              </div>
            )}
            {worldData.completion_rate !== undefined && (
              <div>
                <span className="text-gray-500">Completion Rate:</span>
                <div className="font-semibold text-green-600">
                  {Math.round(worldData.completion_rate * 100)}%
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tags */}
        {worldData.tags &&
          worldData.tags.length > 0 &&
          variant !== "compact" && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-1">
                {worldData.tags.slice(0, 4).map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700"
                  >
                    {tag}
                  </span>
                ))}
                {worldData.tags.length > 4 && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700">
                    +{worldData.tags.length - 4} more
                  </span>
                )}
              </div>
            </div>
          )}

        {/* Actions */}
        <div className="flex space-x-3">
          <button
            onClick={handleEnterWorld}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors duration-200 text-sm font-medium"
          >
            Enter World
          </button>
          {variant !== "compact" && (
            <button
              onClick={handleViewDetails}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors duration-200 text-sm font-medium"
            >
              Details
            </button>
          )}
        </div>

        {/* Footer info */}
        {variant === "detailed" && worldData.last_updated && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Last updated:{" "}
              {new Date(worldData.last_updated).toLocaleDateString()}
              {worldData.created_by && ` • Created by ${worldData.created_by}`}
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default WorldCard;
