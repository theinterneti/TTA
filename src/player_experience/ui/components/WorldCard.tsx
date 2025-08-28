/**
 * WorldCard Component
 * 
 * Displays detailed information about a therapeutic world with options
 * to enter, favorite, or get more information.
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  StarIcon, 
  HeartIcon, 
  ClockIcon, 
  UserGroupIcon,
  SparklesIcon,
  XMarkIcon,
  PlayIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { 
  StarIcon as StarIconSolid, 
  HeartIcon as HeartIconSolid 
} from '@heroicons/react/24/solid';

interface WorldCardProps {
  world: {
    world_id: string;
    title: string;
    description?: string;
    genre: string;
    therapeutic_focus?: string[];
    difficulty_level?: string;
    estimated_duration?: number;
    player_count?: number;
    rating: number;
    therapeutic_efficacy?: number;
    strength_level?: number;
    tags?: string[];
    is_featured?: boolean;
    creator_name?: string;
  };
  onEnter: () => void;
  onClose?: () => void;
  compact?: boolean;
}

export const WorldCard: React.FC<WorldCardProps> = ({ 
  world, 
  onEnter, 
  onClose, 
  compact = false 
}) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [showFullDescription, setShowFullDescription] = useState(false);

  const getGenreColor = (genre: string) => {
    const colors = {
      fantasy: 'from-purple-500 to-pink-500',
      'sci-fi': 'from-blue-500 to-cyan-500',
      contemporary: 'from-green-500 to-teal-500',
      historical: 'from-amber-500 to-orange-500',
      hybrid: 'from-indigo-500 to-purple-500',
      'post-apocalyptic': 'from-red-500 to-gray-500',
      mystery: 'from-gray-500 to-slate-500',
      adventure: 'from-emerald-500 to-green-500',
    };
    return colors[genre as keyof typeof colors] || 'from-gray-500 to-gray-600';
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'text-green-600 bg-green-100';
      case 'intermediate':
        return 'text-yellow-600 bg-yellow-100';
      case 'advanced':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDuration = (minutes?: number) => {
    if (!minutes) return 'Unknown';
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <span key={i}>
        {i < Math.floor(rating) ? (
          <StarIconSolid className="w-4 h-4 text-yellow-400" />
        ) : (
          <StarIcon className="w-4 h-4 text-gray-300" />
        )}
      </span>
    ));
  };

  const truncateDescription = (text: string, maxLength: number = 120) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (compact) {
    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="bg-white rounded-lg shadow-md p-4 cursor-pointer"
        onClick={onEnter}
      >
        <div className={`h-2 rounded-t-lg bg-gradient-to-r ${getGenreColor(world.genre)}`} />
        <div className="mt-3">
          <h3 className="font-semibold text-gray-900 line-clamp-1">{world.title}</h3>
          <p className="text-sm text-gray-600 capitalize">{world.genre}</p>
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center space-x-1">
              {renderStars(world.rating)}
              <span className="text-sm text-gray-600 ml-1">{world.rating.toFixed(1)}</span>
            </div>
            {world.player_count !== undefined && (
              <div className="flex items-center text-sm text-gray-500">
                <UserGroupIcon className="w-4 h-4 mr-1" />
                {world.player_count}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white rounded-xl shadow-xl overflow-hidden max-w-md w-full"
    >
      {/* Header */}
      <div className={`h-32 bg-gradient-to-br ${getGenreColor(world.genre)} relative`}>
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-white" />
          </button>
        )}
        
        <div className="absolute bottom-4 left-4 right-4">
          <h2 className="text-xl font-bold text-white mb-1">{world.title}</h2>
          <div className="flex items-center space-x-2">
            <span className="text-white/90 capitalize text-sm">{world.genre}</span>
            {world.is_featured && (
              <div className="flex items-center text-yellow-300">
                <SparklesIcon className="w-4 h-4 mr-1" />
                <span className="text-xs">Featured</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Rating and Stats */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-1">
            {renderStars(world.rating)}
            <span className="text-sm text-gray-600 ml-2">{world.rating.toFixed(1)}</span>
          </div>
          
          <button
            onClick={() => setIsFavorited(!isFavorited)}
            className="p-1 rounded-full hover:bg-gray-100 transition-colors"
          >
            {isFavorited ? (
              <HeartIconSolid className="w-5 h-5 text-red-500" />
            ) : (
              <HeartIcon className="w-5 h-5 text-gray-400" />
            )}
          </button>
        </div>

        {/* Description */}
        {world.description && (
          <div className="mb-4">
            <p className="text-gray-700 text-sm leading-relaxed">
              {showFullDescription 
                ? world.description 
                : truncateDescription(world.description)
              }
              {world.description.length > 120 && (
                <button
                  onClick={() => setShowFullDescription(!showFullDescription)}
                  className="text-blue-600 hover:text-blue-700 ml-1 text-sm font-medium"
                >
                  {showFullDescription ? 'Show less' : 'Show more'}
                </button>
              )}
            </p>
          </div>
        )}

        {/* Therapeutic Focus */}
        {world.therapeutic_focus && world.therapeutic_focus.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Therapeutic Focus</h4>
            <div className="flex flex-wrap gap-2">
              {world.therapeutic_focus.map((focus, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {focus}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {world.difficulty_level && (
            <div className="text-center">
              <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(world.difficulty_level)}`}>
                {world.difficulty_level}
              </div>
              <p className="text-xs text-gray-500 mt-1">Difficulty</p>
            </div>
          )}
          
          {world.estimated_duration && (
            <div className="text-center">
              <div className="flex items-center justify-center text-gray-700">
                <ClockIcon className="w-4 h-4 mr-1" />
                <span className="text-sm font-medium">{formatDuration(world.estimated_duration)}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Duration</p>
            </div>
          )}
          
          {world.player_count !== undefined && (
            <div className="text-center">
              <div className="flex items-center justify-center text-gray-700">
                <UserGroupIcon className="w-4 h-4 mr-1" />
                <span className="text-sm font-medium">{world.player_count}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Players</p>
            </div>
          )}
          
          {world.therapeutic_efficacy !== undefined && (
            <div className="text-center">
              <div className="flex items-center justify-center text-gray-700">
                <SparklesIcon className="w-4 h-4 mr-1" />
                <span className="text-sm font-medium">{(world.therapeutic_efficacy * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Efficacy</p>
            </div>
          )}
        </div>

        {/* Tags */}
        {world.tags && world.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {world.tags.slice(0, 4).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                >
                  #{tag}
                </span>
              ))}
              {world.tags.length > 4 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{world.tags.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Creator */}
        {world.creator_name && (
          <div className="mb-4 text-xs text-gray-500">
            Created by {world.creator_name}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onEnter}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
          >
            <PlayIcon className="w-4 h-4 mr-2" />
            Enter World
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="px-4 py-3 border border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg transition-colors"
          >
            <InformationCircleIcon className="w-4 h-4" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
