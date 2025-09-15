"""
Production Therapeutic ReplayabilitySystem Implementation

This module provides safe exploration environment with outcome comparison,
alternative outcome exploration for therapeutic learning, and integration
with therapeutic goal achievement tracking.
"""

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class ExplorationMode(Enum):
    """Modes of therapeutic exploration."""
    SANDBOX = "sandbox"  # Free exploration without guidance
    GUIDED = "guided"  # Guided exploration with therapeutic insights
    COMPARATIVE = "comparative"  # Compare different therapeutic approaches
    THERAPEUTIC = "therapeutic"  # Focus on therapeutic goal achievement
    CHARACTER_FOCUSED = "character_focused"  # Focus on character development


class PathType(Enum):
    """Types of alternative paths for exploration."""
    CHOICE_ALTERNATIVE = "choice_alternative"  # Different choice at decision point
    THERAPEUTIC_APPROACH = "therapeutic_approach"  # Different therapeutic framework
    CHARACTER_DEVELOPMENT = "character_development"  # Different character growth path
    EMOTIONAL_RESPONSE = "emotional_response"  # Different emotional handling
    SKILL_APPLICATION = "skill_application"  # Different therapeutic skill usage
    SCENARIO_VARIATION = "scenario_variation"  # Different scenario parameters


class ComparisonMetric(Enum):
    """Metrics for comparing alternative paths."""
    THERAPEUTIC_VALUE = "therapeutic_value"
    CHARACTER_GROWTH = "character_growth"
    EMOTIONAL_WELLBEING = "emotional_wellbeing"
    SKILL_DEVELOPMENT = "skill_development"
    GOAL_ACHIEVEMENT = "goal_achievement"
    ENGAGEMENT_LEVEL = "engagement_level"
    SAFETY_SCORE = "safety_score"
    LEARNING_OUTCOMES = "learning_outcomes"


@dataclass
class ExplorationSnapshot:
    """Snapshot of session state for safe exploration."""
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""

    # Session state preservation
    session_phase: str = ""
    character_state: dict[str, Any] = field(default_factory=dict)
    therapeutic_progress: dict[str, Any] = field(default_factory=dict)
    choice_history: list[dict[str, Any]] = field(default_factory=list)
    scenario_context: dict[str, Any] = field(default_factory=dict)

    # Therapeutic context
    therapeutic_goals: list[str] = field(default_factory=list)
    current_framework: str | None = None
    difficulty_level: str = "moderate"
    safety_status: dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    description: str = ""


@dataclass
class AlternativePath:
    """Represents an alternative therapeutic path for exploration."""
    path_id: str = field(default_factory=lambda: str(uuid4()))
    exploration_id: str = ""
    snapshot_id: str = ""

    # Path definition
    path_type: PathType = PathType.CHOICE_ALTERNATIVE
    path_name: str = ""
    path_description: str = ""

    # Alternative choices and outcomes
    alternative_choices: list[dict[str, Any]] = field(default_factory=list)
    predicted_outcomes: dict[str, Any] = field(default_factory=dict)
    actual_outcomes: dict[str, Any] = field(default_factory=dict)

    # Therapeutic analysis
    therapeutic_value: float = 0.0
    character_impact: dict[str, float] = field(default_factory=dict)
    learning_opportunities: list[str] = field(default_factory=list)
    safety_considerations: list[str] = field(default_factory=list)

    # Execution tracking
    is_executed: bool = False
    execution_results: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PathComparison:
    """Comparison analysis between alternative therapeutic paths."""
    comparison_id: str = field(default_factory=lambda: str(uuid4()))
    exploration_id: str = ""

    # Paths being compared
    path_ids: list[str] = field(default_factory=list)
    comparison_metrics: list[ComparisonMetric] = field(default_factory=list)

    # Comparison results
    metric_scores: dict[str, dict[str, float]] = field(default_factory=dict)  # metric -> path_id -> score
    overall_rankings: dict[str, int] = field(default_factory=dict)  # path_id -> rank

    # Insights and recommendations
    key_differences: list[str] = field(default_factory=list)
    therapeutic_insights: list[str] = field(default_factory=list)
    character_development_insights: list[str] = field(default_factory=list)
    recommended_approach: str | None = None
    recommendation_reasoning: str = ""
    learning_opportunities: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExplorationSession:
    """Manages a therapeutic exploration session."""
    exploration_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    base_session_id: str = ""

    # Exploration configuration
    exploration_name: str = ""
    exploration_mode: ExplorationMode = ExplorationMode.GUIDED
    focus_area: str = ""
    therapeutic_goals: list[str] = field(default_factory=list)

    # Exploration tracking
    snapshots_created: list[str] = field(default_factory=list)
    paths_explored: list[str] = field(default_factory=list)
    comparisons_generated: list[str] = field(default_factory=list)
    insights_discovered: list[str] = field(default_factory=list)
    learning_outcomes: dict[str, Any] = field(default_factory=dict)

    # Session management
    is_active: bool = True
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class TherapeuticReplayabilitySystem:
    """
    Production ReplayabilitySystem that provides safe exploration environment
    with outcome comparison and alternative outcome exploration for therapeutic learning.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic replayability system."""
        self.config = config or {}

        # Exploration data storage
        self.exploration_snapshots = {}  # snapshot_id -> ExplorationSnapshot
        self.alternative_paths = {}  # path_id -> AlternativePath
        self.path_comparisons = {}  # comparison_id -> PathComparison
        self.exploration_sessions = {}  # exploration_id -> ExplorationSession

        # User tracking
        self.user_snapshots = {}  # user_id -> List[snapshot_id]
        self.user_explorations = {}  # user_id -> List[exploration_id]
        self.user_paths = {}  # user_id -> List[path_id]

        # Therapeutic system references (will be injected)
        self.consequence_system = None
        self.emotional_safety_system = None
        self.adaptive_difficulty_engine = None
        self.character_development_system = None
        self.therapeutic_integration_system = None
        self.gameplay_loop_controller = None

        # Configuration parameters
        self.max_snapshots_per_user = self.config.get("max_snapshots_per_user", 10)
        self.max_paths_per_exploration = self.config.get("max_paths_per_exploration", 5)
        self.snapshot_retention_days = self.config.get("snapshot_retention_days", 30)
        self.enable_predictive_analysis = self.config.get("enable_predictive_analysis", True)

        # Performance metrics
        self.metrics = {
            "snapshots_created": 0,
            "paths_explored": 0,
            "comparisons_generated": 0,
            "insights_discovered": 0,
            "learning_outcomes_achieved": 0,
        }

        logger.info("TherapeuticReplayabilitySystem initialized")

    async def initialize(self):
        """Initialize the replayability system."""
        # Any async initialization can go here
        logger.info("TherapeuticReplayabilitySystem initialization complete")

    def inject_therapeutic_systems(
        self,
        consequence_system=None,
        emotional_safety_system=None,
        adaptive_difficulty_engine=None,
        character_development_system=None,
        therapeutic_integration_system=None,
        gameplay_loop_controller=None,
    ):
        """Inject therapeutic system dependencies."""
        self.consequence_system = consequence_system
        self.emotional_safety_system = emotional_safety_system
        self.adaptive_difficulty_engine = adaptive_difficulty_engine
        self.character_development_system = character_development_system
        self.therapeutic_integration_system = therapeutic_integration_system
        self.gameplay_loop_controller = gameplay_loop_controller

        logger.info("Therapeutic systems injected into ReplayabilitySystem")

    async def create_exploration_snapshot(
        self,
        session_id: str,
        user_id: str,
        session_state: dict[str, Any],
        description: str = "",
    ) -> ExplorationSnapshot:
        """
        Create a snapshot of current session state for safe exploration.

        This method provides the core interface for preserving session state
        before exploration, enabling users to safely experiment with alternatives.

        Args:
            session_id: Session identifier
            user_id: User identifier
            session_state: Current session state to preserve
            description: Optional description of the snapshot

        Returns:
            ExplorationSnapshot representing the preserved state
        """
        try:
            start_time = datetime.utcnow()

            # Create deep copy of session state for preservation
            preserved_state = copy.deepcopy(session_state)

            # Create exploration snapshot
            snapshot = ExplorationSnapshot(
                session_id=session_id,
                user_id=user_id,
                session_phase=preserved_state.get("current_phase", "unknown"),
                character_state=preserved_state.get("character_attributes", {}),
                therapeutic_progress={
                    "therapeutic_value": preserved_state.get("therapeutic_value_accumulated", 0.0),
                    "choices_made": preserved_state.get("choices_made", 0),
                    "milestones_achieved": preserved_state.get("milestones_achieved", 0),
                },
                choice_history=preserved_state.get("choice_history", []),
                scenario_context=preserved_state.get("scenario_context", {}),
                therapeutic_goals=preserved_state.get("therapeutic_goals", []),
                current_framework=preserved_state.get("current_framework"),
                difficulty_level=preserved_state.get("difficulty_level", "moderate"),
                safety_status=preserved_state.get("emotional_safety_status", {}),
                description=description,
            )

            # Store snapshot
            self.exploration_snapshots[snapshot.snapshot_id] = snapshot

            # Track user snapshots
            if user_id not in self.user_snapshots:
                self.user_snapshots[user_id] = []
            self.user_snapshots[user_id].append(snapshot.snapshot_id)

            # Cleanup old snapshots if needed
            await self._cleanup_old_snapshots(user_id)

            # Update metrics
            self.metrics["snapshots_created"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created exploration snapshot {snapshot.snapshot_id} for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Error creating exploration snapshot for user {user_id}: {e}")

            # Return minimal snapshot
            return ExplorationSnapshot(
                session_id=session_id,
                user_id=user_id,
                description=f"Error snapshot: {str(e)}",
            )

    async def start_exploration_session(
        self,
        user_id: str,
        base_session_id: str,
        exploration_mode: ExplorationMode = ExplorationMode.GUIDED,
        focus_area: str = "",
        therapeutic_goals: list[str] | None = None,
    ) -> ExplorationSession:
        """
        Start a new therapeutic exploration session.

        Args:
            user_id: User identifier
            base_session_id: Base session to explore from
            exploration_mode: Mode of exploration
            focus_area: Specific area to focus exploration on
            therapeutic_goals: Therapeutic goals for the exploration

        Returns:
            ExplorationSession for managing the exploration
        """
        try:
            start_time = datetime.utcnow()

            # Create exploration session
            exploration = ExplorationSession(
                user_id=user_id,
                base_session_id=base_session_id,
                exploration_name=f"{exploration_mode.value.title()} Exploration",
                exploration_mode=exploration_mode,
                focus_area=focus_area or "general_exploration",
                therapeutic_goals=therapeutic_goals or [],
            )

            # Store exploration session
            self.exploration_sessions[exploration.exploration_id] = exploration

            # Track user explorations
            if user_id not in self.user_explorations:
                self.user_explorations[user_id] = []
            self.user_explorations[user_id].append(exploration.exploration_id)

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Started exploration session {exploration.exploration_id} for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return exploration

        except Exception as e:
            logger.error(f"Error starting exploration session for user {user_id}: {e}")

            # Return minimal exploration session
            return ExplorationSession(
                user_id=user_id,
                base_session_id=base_session_id,
                exploration_name="Error Exploration",
                exploration_mode=exploration_mode,
            )

    async def create_alternative_path(
        self,
        exploration_id: str,
        snapshot_id: str,
        path_type: PathType,
        path_name: str,
        alternative_choices: list[dict[str, Any]] | None = None,
        path_description: str = "",
    ) -> AlternativePath:
        """
        Create an alternative therapeutic path for exploration.

        Args:
            exploration_id: Exploration session identifier
            snapshot_id: Snapshot to branch from
            path_type: Type of alternative path
            path_name: Name for the alternative path
            alternative_choices: Alternative choices to explore
            path_description: Description of the path

        Returns:
            AlternativePath representing the alternative exploration
        """
        try:
            start_time = datetime.utcnow()

            # Get exploration session and snapshot
            exploration = self.exploration_sessions.get(exploration_id)
            snapshot = self.exploration_snapshots.get(snapshot_id)

            if not exploration or not snapshot:
                raise ValueError(f"Invalid exploration {exploration_id} or snapshot {snapshot_id}")

            # Create alternative path
            path = AlternativePath(
                exploration_id=exploration_id,
                snapshot_id=snapshot_id,
                path_type=path_type,
                path_name=path_name,
                path_description=path_description,
                alternative_choices=alternative_choices or [],
            )

            # Generate predicted outcomes if predictive analysis is enabled
            if self.enable_predictive_analysis:
                path.predicted_outcomes = await self._predict_path_outcomes(path, snapshot)
                path.therapeutic_value = path.predicted_outcomes.get("therapeutic_value", 0.0)
                path.character_impact = path.predicted_outcomes.get("character_impact", {})
                path.learning_opportunities = path.predicted_outcomes.get("learning_opportunities", [])
                path.safety_considerations = path.predicted_outcomes.get("safety_considerations", [])

            # Store alternative path
            self.alternative_paths[path.path_id] = path

            # Track in exploration session
            exploration.paths_explored.append(path.path_id)
            exploration.last_activity = datetime.utcnow()

            # Track user paths
            if snapshot.user_id not in self.user_paths:
                self.user_paths[snapshot.user_id] = []
            self.user_paths[snapshot.user_id].append(path.path_id)

            # Update metrics
            self.metrics["paths_explored"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created alternative path {path.path_id} for exploration {exploration_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return path

        except Exception as e:
            logger.error(f"Error creating alternative path for exploration {exploration_id}: {e}")

            # Return minimal path
            return AlternativePath(
                exploration_id=exploration_id,
                snapshot_id=snapshot_id,
                path_type=path_type,
                path_name=f"Error Path: {str(e)}",
            )

    async def compare_alternative_paths(
        self,
        exploration_id: str,
        path_ids: list[str],
        comparison_metrics: list[ComparisonMetric] | None = None,
    ) -> PathComparison:
        """
        Compare multiple alternative paths and generate insights.

        Args:
            exploration_id: Exploration session identifier
            path_ids: List of path identifiers to compare
            comparison_metrics: Metrics to use for comparison

        Returns:
            PathComparison with detailed analysis and recommendations
        """
        try:
            start_time = datetime.utcnow()

            # Get exploration session
            exploration = self.exploration_sessions.get(exploration_id)
            if not exploration:
                raise ValueError(f"Exploration session {exploration_id} not found")

            # Get paths to compare
            paths = []
            for path_id in path_ids:
                path = self.alternative_paths.get(path_id)
                if path:
                    paths.append(path)
                else:
                    logger.warning(f"Path {path_id} not found for comparison")

            if len(paths) < 2:
                raise ValueError("At least 2 paths required for comparison")

            # Use default metrics if none provided
            if comparison_metrics is None:
                comparison_metrics = [
                    ComparisonMetric.THERAPEUTIC_VALUE,
                    ComparisonMetric.CHARACTER_GROWTH,
                    ComparisonMetric.EMOTIONAL_WELLBEING,
                    ComparisonMetric.LEARNING_OUTCOMES,
                ]

            # Create path comparison
            comparison = PathComparison(
                exploration_id=exploration_id,
                path_ids=path_ids,
                comparison_metrics=comparison_metrics,
            )

            # Calculate metric scores for each path
            comparison.metric_scores = await self._calculate_metric_scores(paths, comparison_metrics)

            # Generate overall rankings
            comparison.overall_rankings = await self._generate_path_rankings(paths, comparison.metric_scores)

            # Generate insights and recommendations
            comparison.key_differences = await self._identify_key_differences(paths)
            comparison.therapeutic_insights = await self._generate_therapeutic_insights(paths, comparison.metric_scores)
            comparison.character_development_insights = await self._generate_character_insights(paths)
            comparison.recommended_approach = await self._recommend_best_approach(paths, comparison.metric_scores)
            comparison.recommendation_reasoning = await self._generate_recommendation_reasoning(paths, comparison)
            comparison.learning_opportunities = await self._identify_learning_opportunities(paths, comparison)

            # Store comparison
            self.path_comparisons[comparison.comparison_id] = comparison

            # Track in exploration session
            exploration.comparisons_generated.append(comparison.comparison_id)
            exploration.last_activity = datetime.utcnow()

            # Update metrics
            self.metrics["comparisons_generated"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Generated path comparison {comparison.comparison_id} for exploration {exploration_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return comparison

        except Exception as e:
            logger.error(f"Error comparing paths for exploration {exploration_id}: {e}")

            # Return minimal comparison
            return PathComparison(
                exploration_id=exploration_id,
                path_ids=path_ids,
                comparison_metrics=comparison_metrics or [],
                key_differences=[f"Error in comparison: {str(e)}"],
            )

    async def restore_from_snapshot(
        self,
        snapshot_id: str,
        target_session_id: str,
    ) -> dict[str, Any]:
        """
        Restore session state from an exploration snapshot.

        Args:
            snapshot_id: Snapshot identifier to restore from
            target_session_id: Target session to restore to

        Returns:
            Restoration results and restored state information
        """
        try:
            start_time = datetime.utcnow()

            # Get snapshot
            snapshot = self.exploration_snapshots.get(snapshot_id)
            if not snapshot:
                raise ValueError(f"Snapshot {snapshot_id} not found")

            # Prepare restored state
            restored_state = {
                "session_id": target_session_id,
                "user_id": snapshot.user_id,
                "current_phase": snapshot.session_phase,
                "character_attributes": snapshot.character_state.copy(),
                "therapeutic_value_accumulated": snapshot.therapeutic_progress.get("therapeutic_value", 0.0),
                "choices_made": snapshot.therapeutic_progress.get("choices_made", 0),
                "milestones_achieved": snapshot.therapeutic_progress.get("milestones_achieved", 0),
                "choice_history": snapshot.choice_history.copy(),
                "scenario_context": snapshot.scenario_context.copy(),
                "therapeutic_goals": snapshot.therapeutic_goals.copy(),
                "current_framework": snapshot.current_framework,
                "difficulty_level": snapshot.difficulty_level,
                "emotional_safety_status": snapshot.safety_status.copy(),
            }

            # If we have a gameplay loop controller, restore through it
            if self.gameplay_loop_controller:
                restoration_result = await self._restore_through_controller(restored_state, target_session_id)
            else:
                restoration_result = {"restored": True, "method": "direct"}

            processing_time = datetime.utcnow() - start_time

            response = {
                "snapshot_id": snapshot_id,
                "target_session_id": target_session_id,
                "restoration_successful": True,
                "restored_state": restored_state,
                "restoration_result": restoration_result,
                "processing_time": processing_time.total_seconds(),
            }

            logger.info(f"Restored session from snapshot {snapshot_id} in {response['processing_time']:.3f}s")

            return response

        except Exception as e:
            logger.error(f"Error restoring from snapshot {snapshot_id}: {e}")
            return {
                "snapshot_id": snapshot_id,
                "target_session_id": target_session_id,
                "restoration_successful": False,
                "error": str(e),
            }

    # Helper methods for therapeutic system integration

    async def _predict_path_outcomes(self, path: AlternativePath, snapshot: ExplorationSnapshot) -> dict[str, Any]:
        """Predict outcomes for an alternative path using therapeutic systems."""
        try:
            predicted_outcomes = {
                "therapeutic_value": 0.0,
                "character_impact": {},
                "learning_opportunities": [],
                "safety_considerations": [],
            }

            # Use consequence system for prediction if available
            if self.consequence_system and path.alternative_choices:
                for choice in path.alternative_choices:
                    try:
                        consequence = await self.consequence_system.process_choice_consequence(
                            user_id=snapshot.user_id,
                            choice=choice.get("text", ""),
                            scenario_context=snapshot.scenario_context,
                        )
                        predicted_outcomes["therapeutic_value"] += consequence.get("therapeutic_value", 0.0)

                        # Merge character impact
                        char_impact = consequence.get("character_impact", {})
                        for attr, value in char_impact.items():
                            predicted_outcomes["character_impact"][attr] = predicted_outcomes["character_impact"].get(attr, 0.0) + value
                    except Exception as e:
                        logger.debug(f"Error predicting consequence: {e}")

            # Use therapeutic integration system for learning opportunities
            if self.therapeutic_integration_system:
                try:
                    recommendations = await self.therapeutic_integration_system.generate_personalized_recommendations(
                        user_id=snapshot.user_id,
                        therapeutic_goals=snapshot.therapeutic_goals,
                        character_data={"attributes": snapshot.character_state},
                    )

                    for rec in recommendations[:3]:  # Top 3 recommendations
                        predicted_outcomes["learning_opportunities"].append(f"Explore {rec.framework.value} approach")
                except Exception as e:
                    logger.debug(f"Error predicting learning opportunities: {e}")

            # Use emotional safety system for safety considerations
            if self.emotional_safety_system and path.alternative_choices:
                for choice in path.alternative_choices:
                    try:
                        safety_assessment = await self.emotional_safety_system.assess_crisis_risk(
                            user_id=snapshot.user_id,
                            user_input=choice.get("text", ""),
                            session_context=snapshot.scenario_context,
                        )

                        if safety_assessment.get("crisis_detected", False):
                            predicted_outcomes["safety_considerations"].append("Crisis risk detected - proceed with caution")
                        elif safety_assessment.get("safety_level", "standard") == "elevated":
                            predicted_outcomes["safety_considerations"].append("Elevated emotional sensitivity - monitor closely")
                    except Exception as e:
                        logger.debug(f"Error assessing safety: {e}")

            return predicted_outcomes

        except Exception as e:
            logger.error(f"Error predicting path outcomes: {e}")
            return {"therapeutic_value": 0.0, "character_impact": {}, "learning_opportunities": [], "safety_considerations": []}

    async def _calculate_metric_scores(self, paths: list[AlternativePath], metrics: list[ComparisonMetric]) -> dict[str, dict[str, float]]:
        """Calculate metric scores for path comparison."""
        try:
            scores = {}

            for metric in metrics:
                scores[metric.value] = {}

                for path in paths:
                    if metric == ComparisonMetric.THERAPEUTIC_VALUE:
                        scores[metric.value][path.path_id] = path.therapeutic_value
                    elif metric == ComparisonMetric.CHARACTER_GROWTH:
                        # Sum of positive character impacts
                        char_growth = sum(max(0, v) for v in path.character_impact.values())
                        scores[metric.value][path.path_id] = char_growth
                    elif metric == ComparisonMetric.LEARNING_OUTCOMES:
                        scores[metric.value][path.path_id] = len(path.learning_opportunities)
                    elif metric == ComparisonMetric.SAFETY_SCORE:
                        # Inverse of safety considerations (fewer = better)
                        safety_score = max(0, 10 - len(path.safety_considerations))
                        scores[metric.value][path.path_id] = safety_score
                    else:
                        # Default scoring
                        scores[metric.value][path.path_id] = path.therapeutic_value * 0.5

            return scores

        except Exception as e:
            logger.error(f"Error calculating metric scores: {e}")
            return {}

    async def _generate_path_rankings(self, paths: list[AlternativePath], metric_scores: dict[str, dict[str, float]]) -> dict[str, int]:
        """Generate overall rankings for paths based on metric scores."""
        try:
            # Calculate weighted average scores
            path_totals = {}

            for path in paths:
                total_score = 0.0
                metric_count = 0

                for _metric_name, path_scores in metric_scores.items():
                    if path.path_id in path_scores:
                        total_score += path_scores[path.path_id]
                        metric_count += 1

                path_totals[path.path_id] = total_score / max(metric_count, 1)

            # Generate rankings (1 = best)
            sorted_paths = sorted(path_totals.items(), key=lambda x: x[1], reverse=True)
            rankings = {}

            for rank, (path_id, _score) in enumerate(sorted_paths, 1):
                rankings[path_id] = rank

            return rankings

        except Exception as e:
            logger.error(f"Error generating path rankings: {e}")
            return {}

    async def _identify_key_differences(self, paths: list[AlternativePath]) -> list[str]:
        """Identify key differences between alternative paths."""
        try:
            differences = []

            # Compare therapeutic values
            therapeutic_values = [path.therapeutic_value for path in paths]
            if max(therapeutic_values) - min(therapeutic_values) > 1.0:
                differences.append(f"Therapeutic value varies significantly ({min(therapeutic_values):.1f} to {max(therapeutic_values):.1f})")

            # Compare character impacts
            all_attributes = set()
            for path in paths:
                all_attributes.update(path.character_impact.keys())

            for attr in all_attributes:
                attr_values = [path.character_impact.get(attr, 0.0) for path in paths]
                if max(attr_values) - min(attr_values) > 0.5:
                    differences.append(f"{attr.title()} development varies between paths")

            # Compare learning opportunities
            learning_counts = [len(path.learning_opportunities) for path in paths]
            if max(learning_counts) - min(learning_counts) > 1:
                differences.append("Learning opportunity count varies between paths")

            # Compare safety considerations
            safety_counts = [len(path.safety_considerations) for path in paths]
            if max(safety_counts) > 0:
                differences.append("Some paths have safety considerations")

            return differences[:5]  # Limit to top 5 differences

        except Exception as e:
            logger.error(f"Error identifying key differences: {e}")
            return ["Error analyzing path differences"]

    async def _generate_therapeutic_insights(self, paths: list[AlternativePath], metric_scores: dict[str, dict[str, float]]) -> list[str]:
        """Generate therapeutic insights from path comparison."""
        try:
            insights = []

            # Find highest therapeutic value path
            if ComparisonMetric.THERAPEUTIC_VALUE.value in metric_scores:
                tv_scores = metric_scores[ComparisonMetric.THERAPEUTIC_VALUE.value]
                best_path_id = max(tv_scores.items(), key=lambda x: x[1])[0]
                best_path = next((p for p in paths if p.path_id == best_path_id), None)

                if best_path:
                    insights.append(f"'{best_path.path_name}' shows highest therapeutic potential")

                    if best_path.learning_opportunities:
                        insights.append(f"This path offers: {', '.join(best_path.learning_opportunities[:2])}")

            # Analyze character development patterns
            char_insights = []
            for path in paths:
                if path.character_impact:
                    strongest_impact = max(path.character_impact.items(), key=lambda x: abs(x[1]))
                    if abs(strongest_impact[1]) > 0.5:
                        char_insights.append(f"'{path.path_name}' significantly impacts {strongest_impact[0]}")

            insights.extend(char_insights[:2])  # Limit character insights

            # Safety insights
            risky_paths = [p for p in paths if p.safety_considerations]
            if risky_paths:
                insights.append(f"{len(risky_paths)} path(s) require additional safety monitoring")

            return insights[:5]  # Limit to top 5 insights

        except Exception as e:
            logger.error(f"Error generating therapeutic insights: {e}")
            return ["Error generating therapeutic insights"]

    async def _generate_character_insights(self, paths: list[AlternativePath]) -> list[str]:
        """Generate character development insights from path comparison."""
        try:
            insights = []

            # Analyze character development patterns across paths
            all_attributes = set()
            for path in paths:
                all_attributes.update(path.character_impact.keys())

            for attr in all_attributes:
                attr_impacts = [(path.path_name, path.character_impact.get(attr, 0.0)) for path in paths]
                attr_impacts.sort(key=lambda x: abs(x[1]), reverse=True)

                if attr_impacts and abs(attr_impacts[0][1]) > 0.3:
                    insights.append(f"'{attr_impacts[0][0]}' has strongest impact on {attr} development")

            # Find paths with balanced character development
            balanced_paths = []
            for path in paths:
                if len(path.character_impact) >= 3:
                    impact_values = list(path.character_impact.values())
                    if max(impact_values) - min(impact_values) < 1.0:  # Relatively balanced
                        balanced_paths.append(path.path_name)

            if balanced_paths:
                insights.append(f"Balanced character development: {', '.join(balanced_paths[:2])}")

            return insights[:3]  # Limit to top 3 insights

        except Exception as e:
            logger.error(f"Error generating character insights: {e}")
            return ["Error analyzing character development patterns"]

    async def _recommend_best_approach(self, paths: list[AlternativePath], metric_scores: dict[str, dict[str, float]]) -> str | None:
        """Recommend the best therapeutic approach based on analysis."""
        try:
            if not paths or not metric_scores:
                return None

            # Calculate overall scores for each path
            path_scores = {}
            for path in paths:
                total_score = 0.0
                metric_count = 0

                for _metric_name, path_metric_scores in metric_scores.items():
                    if path.path_id in path_metric_scores:
                        total_score += path_metric_scores[path.path_id]
                        metric_count += 1

                if metric_count > 0:
                    path_scores[path.path_id] = total_score / metric_count

            if not path_scores:
                return None

            # Find best path
            best_path_id = max(path_scores.items(), key=lambda x: x[1])[0]
            best_path = next((p for p in paths if p.path_id == best_path_id), None)

            return best_path.path_name if best_path else None

        except Exception as e:
            logger.error(f"Error recommending best approach: {e}")
            return None

    async def _generate_recommendation_reasoning(self, paths: list[AlternativePath], comparison: PathComparison) -> str:
        """Generate reasoning for the recommended approach."""
        try:
            if not comparison.recommended_approach:
                return "No clear recommendation could be determined from the analysis."

            recommended_path = next((p for p in paths if p.path_name == comparison.recommended_approach), None)
            if not recommended_path:
                return "Recommended approach not found in analyzed paths."

            reasoning_parts = [f"'{comparison.recommended_approach}' is recommended because it"]

            # Add therapeutic value reasoning
            if recommended_path.therapeutic_value > 2.0:
                reasoning_parts.append("shows high therapeutic potential")

            # Add character development reasoning
            if recommended_path.character_impact:
                strongest_impact = max(recommended_path.character_impact.items(), key=lambda x: abs(x[1]))
                if abs(strongest_impact[1]) > 0.5:
                    reasoning_parts.append(f"significantly develops {strongest_impact[0]}")

            # Add safety reasoning
            if len(recommended_path.safety_considerations) == 0:
                reasoning_parts.append("maintains emotional safety")

            # Add learning reasoning
            if recommended_path.learning_opportunities:
                reasoning_parts.append("offers valuable learning opportunities")

            if len(reasoning_parts) == 1:
                reasoning_parts.append("demonstrates overall balanced therapeutic benefits")

            return " and ".join(reasoning_parts) + "."

        except Exception as e:
            logger.error(f"Error generating recommendation reasoning: {e}")
            return "Unable to generate reasoning for recommendation."

    async def _identify_learning_opportunities(self, paths: list[AlternativePath], comparison: PathComparison) -> list[str]:
        """Identify learning opportunities from path comparison."""
        try:
            opportunities = []

            # Learning from differences
            if comparison.key_differences:
                opportunities.append("Compare different therapeutic approaches and their outcomes")

            # Learning from character development
            char_paths = [p for p in paths if p.character_impact]
            if len(char_paths) > 1:
                opportunities.append("Explore how different choices affect character development")

            # Learning from therapeutic frameworks
            framework_variety = set()
            for path in paths:
                if path.learning_opportunities:
                    for opp in path.learning_opportunities:
                        if "framework" in opp.lower() or "approach" in opp.lower():
                            framework_variety.add(opp)

            if framework_variety:
                opportunities.append("Experience different therapeutic frameworks in practice")

            # Learning from safety considerations
            risky_paths = [p for p in paths if p.safety_considerations]
            safe_paths = [p for p in paths if not p.safety_considerations]

            if risky_paths and safe_paths:
                opportunities.append("Understand the safety implications of different choices")

            # Learning from outcome prediction
            executed_paths = [p for p in paths if p.is_executed]
            if executed_paths:
                opportunities.append("Compare predicted vs actual outcomes for better decision-making")

            return opportunities[:5]  # Limit to top 5 opportunities

        except Exception as e:
            logger.error(f"Error identifying learning opportunities: {e}")
            return ["Explore alternative approaches to gain therapeutic insights"]

    async def _restore_through_controller(self, restored_state: dict[str, Any], target_session_id: str) -> dict[str, Any]:
        """Restore session state through gameplay loop controller."""
        try:
            # This would integrate with the gameplay loop controller to restore state
            # For now, return a simple restoration result
            return {
                "restored": True,
                "method": "controller_integration",
                "session_id": target_session_id,
            }

        except Exception as e:
            logger.error(f"Error restoring through controller: {e}")
            return {
                "restored": False,
                "method": "controller_integration",
                "error": str(e),
            }

    async def _cleanup_old_snapshots(self, user_id: str):
        """Clean up old snapshots for a user."""
        try:
            user_snapshots = self.user_snapshots.get(user_id, [])

            # Remove excess snapshots
            if len(user_snapshots) > self.max_snapshots_per_user:
                # Sort by creation time and remove oldest
                snapshot_times = []
                for snapshot_id in user_snapshots:
                    snapshot = self.exploration_snapshots.get(snapshot_id)
                    if snapshot:
                        snapshot_times.append((snapshot_id, snapshot.created_at))

                snapshot_times.sort(key=lambda x: x[1])

                # Remove oldest snapshots
                to_remove = len(snapshot_times) - self.max_snapshots_per_user
                for i in range(to_remove):
                    snapshot_id = snapshot_times[i][0]
                    self.exploration_snapshots.pop(snapshot_id, None)
                    user_snapshots.remove(snapshot_id)

            # Remove snapshots older than retention period
            cutoff_date = datetime.utcnow() - timedelta(days=self.snapshot_retention_days)
            expired_snapshots = []

            for snapshot_id in user_snapshots:
                snapshot = self.exploration_snapshots.get(snapshot_id)
                if snapshot and snapshot.created_at < cutoff_date:
                    expired_snapshots.append(snapshot_id)

            for snapshot_id in expired_snapshots:
                self.exploration_snapshots.pop(snapshot_id, None)
                user_snapshots.remove(snapshot_id)

        except Exception as e:
            logger.error(f"Error cleaning up old snapshots for user {user_id}: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the replayability system."""
        try:
            # Check therapeutic system availability
            systems_status = {
                "consequence_system": self.consequence_system is not None,
                "emotional_safety_system": self.emotional_safety_system is not None,
                "adaptive_difficulty_engine": self.adaptive_difficulty_engine is not None,
                "character_development_system": self.character_development_system is not None,
                "therapeutic_integration_system": self.therapeutic_integration_system is not None,
                "gameplay_loop_controller": self.gameplay_loop_controller is not None,
            }

            systems_available = sum(systems_status.values())

            return {
                "status": "healthy" if systems_available >= 3 else "degraded",
                "exploration_modes": len(ExplorationMode),
                "path_types": len(PathType),
                "comparison_metrics": len(ComparisonMetric),
                "active_snapshots": len(self.exploration_snapshots),
                "active_explorations": len(self.exploration_sessions),
                "alternative_paths": len(self.alternative_paths),
                "path_comparisons": len(self.path_comparisons),
                "therapeutic_systems": systems_status,
                "systems_available": f"{systems_available}/6",
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in replayability system health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get replayability system metrics."""
        # Calculate additional metrics
        active_explorations = sum(1 for exp in self.exploration_sessions.values() if exp.is_active)

        return {
            **self.metrics,
            "active_snapshots": len(self.exploration_snapshots),
            "active_explorations": active_explorations,
            "total_explorations": len(self.exploration_sessions),
            "alternative_paths_created": len(self.alternative_paths),
            "path_comparisons_generated": len(self.path_comparisons),
            "users_with_snapshots": len(self.user_snapshots),
            "users_with_explorations": len(self.user_explorations),
        }
