import React, { useState, useEffect } from 'react';
import { 
  UserIcon, 
  PlayIcon, 
  ChartBarIcon, 
  LightBulbIcon,
  ArrowRightIcon,
  CalendarIcon,
  ClockIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';
import ProgressChart from './ProgressChart';
import MilestoneTracker from './MilestoneTracker';
import AchievementCelebration from './AchievementCelebration';
import InsightDisplay from './InsightDisplay';

interface Character {
  character_id: string;
  name: string;
  appearance: {
    avatar_url?: string;
    description: string;
  };
  last_active: string;
  active_worlds: string[];
}

interface SessionSummary {
  session_id: string;
  character_id: string;
  world_id: string;
  world_name: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  key_achievements: string[];
  therapeutic_interventions_count: number;
}

interface ProgressHighlight {
  highlight_id: string;
  title: string;
  description: string;
  highlight_type: string;
  achieved_at: string;
  therapeutic_value: number;
  celebration_shown: boolean;
}

interface Milestone {
  milestone_id: string;
  title: string;
  description: string;
  progress_percentage: number;
  is_achieved: boolean;
  achieved_date?: string;
  target_date?: string;
  required_actions: string[];
  completed_actions: string[];
  therapeutic_approaches_involved: string[];
  reward_description: string;
}

interface Recommendation {
  recommendation_id: string;
  title: string;
  description: string;
  recommendation_type: string;
  priority: number;
}

interface ProgressVizSeries {
  time_buckets: string[];
  series: {
    sessions: number[];
    duration_minutes: number[];
  };
  meta: {
    period_days: number;
    units: {
      duration_minutes: string;
    };
  };
}

interface ProgressSummary {
  player_id: string;
  therapeutic_momentum: number;
  readiness_for_advancement: number;
  progress_trend: string;
  engagement_trend: string;
  challenge_areas: string[];
  strength_areas: string[];
  next_recommended_goals: string[];
  suggested_therapeutic_adjustments: string[];
  favorite_therapeutic_approach?: string;
  last_updated: string;
}

interface PlayerDashboardData {
  player_id: string;
  active_characters: Character[];
  recent_sessions: SessionSummary[];
  progress_highlights: ProgressHighlight[];
  recommendations: Recommendation[];
  upcoming_milestones: Milestone[];
  achieved_milestones: Milestone[];
  progress_summary: ProgressSummary;
  visualization_data: ProgressVizSeries;
}

interface PlayerDashboardProps {
  dashboardData: PlayerDashboardData;
  onCharacterSelect: (characterId: string) => void;
  onSessionStart: (characterId: string, worldId: string) => void;
  onHighlightDismiss: (highlightId: string) => void;
  className?: string;
  refreshInterval?: number;
}

const PlayerDashboard: React.FC<PlayerDashboardProps> = ({
  dashboardData,
  onCharacterSelect,
  onSessionStart,
  onHighlightDismiss,
  className = '',
  refreshInterval = 30000, // 30 seconds
}) => {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'progress' | 'insights'>('overview');
  const [lastRefresh, setLastRefresh] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setLastRefresh(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getCharacterAvatar = (character: Character) => {
    if (character.appearance.avatar_url) {
      return (
        <img
          src={character.appearance.avatar_url}
          alt={character.name}
          className="w-10 h-10 rounded-full object-cover"
        />
      );
    }
    return (
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium">
        {character.name.charAt(0).toUpperCase()}
      </div>
    );
  };

  const QuickStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Active Characters</p>
            <p className="text-2xl font-bold text-gray-900">{dashboardData.active_characters.length}</p>
          </div>
          <UserIcon className="h-8 w-8 text-blue-500" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Recent Sessions</p>
            <p className="text-2xl font-bold text-gray-900">{dashboardData.recent_sessions.length}</p>
          </div>
          <PlayIcon className="h-8 w-8 text-green-500" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Achievements</p>
            <p className="text-2xl font-bold text-gray-900">{dashboardData.achieved_milestones.length}</p>
          </div>
          <TrophyIcon className="h-8 w-8 text-yellow-500" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Momentum</p>
            <p className="text-2xl font-bold text-gray-900">
              {(dashboardData.progress_summary.therapeutic_momentum * 100).toFixed(0)}%
            </p>
          </div>
          <ChartBarIcon className="h-8 w-8 text-purple-500" />
        </div>
      </div>
    </div>
  );

  const CharacterOverview = () => (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Characters</h3>
      <div className="space-y-4">
        {dashboardData.active_characters.map((character) => (
          <div
            key={character.character_id}
            className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => onCharacterSelect(character.character_id)}
          >
            <div className="flex items-center space-x-4">
              {getCharacterAvatar(character)}
              <div>
                <h4 className="font-medium text-gray-900">{character.name}</h4>
                <p className="text-sm text-gray-600">
                  {character.active_worlds.length} active world{character.active_worlds.length !== 1 ? 's' : ''}
                </p>
                <p className="text-xs text-gray-500">
                  Last active: {formatTimeAgo(character.last_active)}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {character.active_worlds.length > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSessionStart(character.character_id, character.active_worlds[0]);
                  }}
                  className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                >
                  Continue
                </button>
              )}
              <ArrowRightIcon className="h-5 w-5 text-gray-400" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const RecentActivity = () => (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {dashboardData.recent_sessions.slice(0, 5).map((session) => (
          <div key={session.session_id} className="flex items-start space-x-4 p-3 border-l-4 border-blue-200 bg-blue-50 rounded-r">
            <div className="flex-shrink-0">
              <ClockIcon className="h-5 w-5 text-blue-500 mt-0.5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                Session in {session.world_name}
              </p>
              <p className="text-sm text-gray-600">
                {session.duration_minutes} minutes • {session.therapeutic_interventions_count} interventions
              </p>
              {session.key_achievements.length > 0 && (
                <div className="mt-1">
                  <p className="text-xs text-green-600 font-medium">
                    🎯 {session.key_achievements[0]}
                    {session.key_achievements.length > 1 && ` +${session.key_achievements.length - 1} more`}
                  </p>
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">
                {formatTimeAgo(session.start_time)}
              </p>
            </div>
          </div>
        ))}
        {dashboardData.recent_sessions.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <CalendarIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No recent sessions. Start your therapeutic journey!</p>
          </div>
        )}
      </div>
    </div>
  );

  const QuickRecommendations = () => (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Recommendations</h3>
      <div className="space-y-3">
        {dashboardData.recommendations.slice(0, 3).map((rec) => (
          <div
            key={rec.recommendation_id}
            className={`p-3 rounded-lg border-l-4 ${
              rec.priority === 1
                ? 'border-red-400 bg-red-50'
                : rec.priority === 2
                ? 'border-yellow-400 bg-yellow-50'
                : 'border-blue-400 bg-blue-50'
            }`}
          >
            <h4 className="font-medium text-gray-900 text-sm">{rec.title}</h4>
            <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
          </div>
        ))}
        {dashboardData.recommendations.length === 0 && (
          <div className="text-center text-gray-500 py-4">
            <LightBulbIcon className="h-6 w-6 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No specific recommendations at this time.</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className={`max-w-7xl mx-auto p-6 ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Therapeutic Journey</h1>
        <p className="text-gray-600">
          Welcome back! Here's your progress overview and next steps.
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Last updated: {lastRefresh.toLocaleTimeString()}
        </p>
      </div>

      {/* Achievement Celebrations */}
      <AchievementCelebration
        highlights={dashboardData.progress_highlights}
        onDismiss={onHighlightDismiss}
        className="mb-6"
      />

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: UserIcon },
            { id: 'progress', label: 'Progress', icon: ChartBarIcon },
            { id: 'insights', label: 'Insights', icon: LightBulbIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {selectedTab === 'overview' && (
        <div>
          <QuickStats />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <CharacterOverview />
              <RecentActivity />
            </div>
            <div>
              <QuickRecommendations />
              <MilestoneTracker
                milestones={dashboardData.achieved_milestones}
                activeMilestones={dashboardData.upcoming_milestones}
                maxDisplay={3}
                className="mt-6"
              />
            </div>
          </div>
        </div>
      )}

      {selectedTab === 'progress' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProgressChart
              data={dashboardData.visualization_data}
              chartType="line"
              metric="both"
              height={300}
            />
            <ProgressChart
              data={dashboardData.visualization_data}
              chartType="bar"
              metric="sessions"
              height={300}
            />
          </div>
          <MilestoneTracker
            milestones={dashboardData.achieved_milestones}
            activeMilestones={dashboardData.upcoming_milestones}
            showAll={true}
          />
        </div>
      )}

      {selectedTab === 'insights' && (
        <div>
          <InsightDisplay
            progressSummary={dashboardData.progress_summary}
            recommendations={dashboardData.recommendations}
            expandable={true}
          />
        </div>
      )}
    </div>
  );
};

export default PlayerDashboard;