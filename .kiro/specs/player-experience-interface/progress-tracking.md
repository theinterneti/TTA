# Progress Tracking and Analytics (Task 9)

Status: Completed

## Scope

Implements analytics over session activity and progress markers to produce:

- Progress summaries and effectiveness insights
- Milestone detection and celebration hooks
- Visualization-ready data structures for frontend charts

Aligns with prior WebSocket behaviors where guided exercise completion records a ProgressMarker of type `SKILL_ACQUIRED`.

## Data Sources

- SessionRepository
  - get_session_summaries(player_id, limit)
  - get_player_active_sessions(player_id)
- SessionContext.progress_markers (for active sessions)

## Models (9.1)

Already implemented in codebase:

- ProgressSummary, ProgressHighlight, Milestone, EngagementMetrics, TherapeuticMetric, TherapeuticEffectivenessReport

Added in Task 9:

- ProgressVizSeries (DTO for charting):
  - time_buckets: list[str]
  - series: dict[str, list[float]]
  - meta: dict (e.g., period, units)

## Service (9.2): ProgressTrackingService

Location: src/player_experience/managers/progress_tracking_service.py

Methods (async):

- compute_progress_summary(player_id: str, \*, summaries_limit: int = 30) -> ProgressSummary
  - Aggregates session summaries and active session markers; updates EngagementMetrics and trends; computes overall score
- detect_and_update_milestones(player_id: str) -> tuple[list[Milestone], list[ProgressHighlight]]
  - Rule-based detection (e.g., 7-day streak, N skills acquired) and generates highlights with celebration flags
- generate_progress_insights(player_id: str) -> list[Recommendation]
  - Simple heuristics for recommendations (e.g., maintain momentum, adjust intensity, suggest mindfulness)
- get_visualization_data(player_id: str, \*, days: int = 14) -> ProgressVizSeries
  - Returns daily buckets for recent activity counts and durations

Dependencies:

- Inject SessionRepository on init
- Optionally accept PersonalizationServiceManager for future enrichments (kept optional/mocked for tests)

## Rules (initial, simple)

- Streak Milestone: current_streak_days >= 7 => "One Week Streak" milestone
- Skill Builder Milestone: total SKILL_ACQUIRED markers >= 5 => "Skill Builder Level 1"
- Insights examples:
  - If streak >= 3 and momentum >= 0.6 => "Maintain current pace"
  - If dropout_risk_score > 0.6 => "Shorter, more frequent sessions"
  - If exercises frequent => recommend related world/approach (e.g., mindfulness)

## Outputs

- ProgressSummary updated values (streaks, momentum, readiness, highlights)
- Milestones list; ProgressHighlight entries with celebration_shown=False (UI will set true)
- Recommendations (using Recommendation model)
- ProgressVizSeries for charts

## Testing Strategy

- Unit tests with a MockSessionRepository providing:
  - get_session_summaries: returns dated summaries
  - get_player_active_sessions: returns active sessions with markers
- Validate:
  - Aggregation math (durations, counts)
  - Milestone detection firing as expected
  - Insight generation returns appropriate recommendations
  - Visualization DTO schema and lengths match

## Non-Goals

- Persistent storage of computed summaries (to be handled by Task 10 or DB layer)
- API endpoints/UI (covered in subsequent tasks)
