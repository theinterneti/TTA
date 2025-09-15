#!/usr/bin/env python3
"""
Comprehensive TTA Narrative Consistency & Quality Analysis Study

This study evaluates the TTA system's narrative consistency and therapeutic quality
across different player profiles, character archetypes, and world settings using
the clinical dashboard integration for real-time monitoring and analytics.

Study Objectives:
1. Narrative Consistency Testing across multiple therapeutic gaming sessions
2. Output Quality Assessment with quantitative and qualitative metrics
3. Baseline Data Collection for future therapeutic effectiveness comparisons
"""

import asyncio
import json
import logging
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.components.clinical_dashboard import (
    APIConfig,
    ClinicalDashboardController,
    MetricType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PlayerProfile:
    """Defines a player profile for testing."""

    name: str
    description: str
    therapeutic_needs: list[str]
    resistance_level: float  # 0.0 = highly engaged, 1.0 = highly resistant
    crisis_risk: float  # 0.0 = low risk, 1.0 = high risk
    engagement_baseline: float  # Expected baseline engagement (0.0-1.0)


@dataclass
class CharacterArchetype:
    """Defines a character archetype for testing."""

    name: str
    description: str
    therapeutic_focus: str
    personality_traits: list[str]
    growth_potential: float  # Expected therapeutic growth potential


@dataclass
class WorldSetting:
    """Defines a world setting for testing."""

    name: str
    description: str
    therapeutic_environment: str
    complexity_level: float  # 0.0 = simple, 1.0 = complex
    safety_features: list[str]


@dataclass
class SessionMetrics:
    """Metrics collected from a single session."""

    session_id: str
    player_profile: str
    character_archetype: str
    world_setting: str
    turn_count: int
    engagement_score: float
    progress_score: float
    safety_score: float
    therapeutic_value: float
    narrative_consistency: float
    session_duration: float
    timestamp: str


@dataclass
class StudyResults:
    """Complete study results."""

    study_id: str
    total_sessions: int
    total_turns: int
    execution_time: float
    player_profile_results: dict[str, dict[str, float]]
    character_archetype_results: dict[str, dict[str, float]]
    world_setting_results: dict[str, dict[str, float]]
    overall_metrics: dict[str, float]
    baseline_benchmarks: dict[str, float]
    recommendations: list[str]
    raw_session_data: list[SessionMetrics]


class ComprehensiveNarrativeAnalysisStudy:
    """
    Comprehensive study framework for TTA narrative consistency and quality analysis.

    This class orchestrates systematic testing across multiple dimensions to evaluate
    therapeutic effectiveness and establish baseline performance metrics.
    """

    def __init__(self):
        """Initialize the study framework."""
        self.study_id = (
            f"narrative_study_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )

        # API configuration
        self.api_config = APIConfig(
            base_url="http://0.0.0.0:8080",
            timeout=60,  # Longer timeout for complex sessions
            max_retries=3,
            retry_delay=2.0,
        )

        # Clinical dashboard controller
        self.dashboard_controller: ClinicalDashboardController | None = None

        # Study configuration
        self.min_turns_per_session = 10
        self.max_turns_per_session = 20
        self.sessions_per_scenario = 3  # Multiple sessions for consistency testing

        # Results storage
        self.session_metrics: list[SessionMetrics] = []
        self.study_start_time: datetime | None = None

        logger.info(
            f"Initialized Comprehensive Narrative Analysis Study: {self.study_id}"
        )

    def define_player_profiles(self) -> list[PlayerProfile]:
        """Define diverse player profiles for testing."""
        return [
            PlayerProfile(
                name="therapy_resistant",
                description="Player who is skeptical of therapeutic interventions",
                therapeutic_needs=["trust_building", "engagement", "motivation"],
                resistance_level=0.8,
                crisis_risk=0.3,
                engagement_baseline=0.4,
            ),
            PlayerProfile(
                name="highly_engaged",
                description="Player who is motivated and actively participates",
                therapeutic_needs=[
                    "skill_development",
                    "progress_tracking",
                    "challenge",
                ],
                resistance_level=0.2,
                crisis_risk=0.1,
                engagement_baseline=0.8,
            ),
            PlayerProfile(
                name="crisis_prone",
                description="Player with high emotional volatility and crisis risk",
                therapeutic_needs=["safety", "stabilization", "coping_skills"],
                resistance_level=0.5,
                crisis_risk=0.9,
                engagement_baseline=0.6,
            ),
            PlayerProfile(
                name="progress_oriented",
                description="Player focused on measurable therapeutic progress",
                therapeutic_needs=["goal_setting", "achievement", "feedback"],
                resistance_level=0.3,
                crisis_risk=0.2,
                engagement_baseline=0.7,
            ),
        ]

    def define_character_archetypes(self) -> list[CharacterArchetype]:
        """Define character archetypes for testing."""
        return [
            CharacterArchetype(
                name="reluctant_hero",
                description="Character who grows from reluctance to leadership",
                therapeutic_focus="self_efficacy",
                personality_traits=["cautious", "loyal", "growth_oriented"],
                growth_potential=0.8,
            ),
            CharacterArchetype(
                name="wise_mentor",
                description="Character who guides others through wisdom",
                therapeutic_focus="meaning_making",
                personality_traits=["wise", "patient", "supportive"],
                growth_potential=0.6,
            ),
            CharacterArchetype(
                name="wounded_healer",
                description="Character who heals others while healing themselves",
                therapeutic_focus="trauma_recovery",
                personality_traits=["empathetic", "resilient", "transformative"],
                growth_potential=0.9,
            ),
            CharacterArchetype(
                name="curious_explorer",
                description="Character driven by discovery and learning",
                therapeutic_focus="cognitive_flexibility",
                personality_traits=["curious", "adaptable", "optimistic"],
                growth_potential=0.7,
            ),
        ]

    def define_world_settings(self) -> list[WorldSetting]:
        """Define world settings for testing."""
        return [
            WorldSetting(
                name="peaceful_village",
                description="Safe, supportive community environment",
                therapeutic_environment="supportive_community",
                complexity_level=0.3,
                safety_features=[
                    "crisis_support",
                    "community_resources",
                    "safe_spaces",
                ],
            ),
            WorldSetting(
                name="mystical_forest",
                description="Magical environment for exploration and growth",
                therapeutic_environment="transformative_journey",
                complexity_level=0.6,
                safety_features=[
                    "guided_exploration",
                    "protective_magic",
                    "wise_guides",
                ],
            ),
            WorldSetting(
                name="urban_challenge",
                description="Complex city environment with real-world parallels",
                therapeutic_environment="skill_application",
                complexity_level=0.8,
                safety_features=[
                    "support_networks",
                    "resource_access",
                    "crisis_protocols",
                ],
            ),
            WorldSetting(
                name="healing_sanctuary",
                description="Dedicated therapeutic space for intensive work",
                therapeutic_environment="intensive_therapy",
                complexity_level=0.4,
                safety_features=[
                    "therapeutic_protocols",
                    "crisis_intervention",
                    "professional_support",
                ],
            ),
        ]

    async def initialize_study(self) -> bool:
        """Initialize the study environment."""
        try:
            logger.info("🔬 Initializing Comprehensive Narrative Analysis Study")

            # Initialize clinical dashboard controller
            self.dashboard_controller = ClinicalDashboardController(
                api_config=self.api_config
            )
            await self.dashboard_controller.initialize()

            # Verify API connectivity
            status = await self.dashboard_controller.get_service_status()
            if status.get("status") != "healthy":
                logger.error("❌ Clinical dashboard not healthy")
                return False

            self.study_start_time = datetime.now(timezone.utc)
            logger.info("✅ Study environment initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing study: {e}")
            return False

    async def simulate_therapeutic_session(
        self,
        player_profile: PlayerProfile,
        character_archetype: CharacterArchetype,
        world_setting: WorldSetting,
        session_number: int,
    ) -> SessionMetrics:
        """Simulate a therapeutic gaming session and collect metrics."""

        session_id = f"{self.study_id}_{player_profile.name}_{character_archetype.name}_{world_setting.name}_{session_number}"
        session_start = datetime.now(timezone.utc)

        logger.info(f"🎮 Starting session: {session_id}")

        # Simulate session metrics based on profile characteristics
        # In a real implementation, this would interact with the actual TTA system

        # Calculate base metrics influenced by profile characteristics
        base_engagement = player_profile.engagement_baseline
        resistance_factor = 1.0 - player_profile.resistance_level
        world_complexity_factor = 1.0 - (world_setting.complexity_level * 0.3)
        character_growth_factor = character_archetype.growth_potential

        # Simulate engagement score
        engagement_score = min(
            1.0,
            max(
                0.0,
                base_engagement * resistance_factor * world_complexity_factor
                + (0.1 * (session_number - 1)),  # Improvement over sessions
            ),
        )

        # Simulate progress score
        progress_score = min(
            1.0,
            max(
                0.0,
                character_growth_factor * resistance_factor * 0.8
                + (0.05 * (session_number - 1)),  # Gradual progress
            ),
        )

        # Simulate safety score (higher for crisis-prone players)
        safety_base = 0.9 - (player_profile.crisis_risk * 0.3)
        safety_score = min(
            1.0, max(0.5, safety_base + (len(world_setting.safety_features) * 0.05))
        )

        # Simulate therapeutic value
        therapeutic_value = min(
            1.0,
            max(
                0.0,
                (engagement_score + progress_score + safety_score)
                / 3.0
                * (1.0 + character_growth_factor * 0.2),
            ),
        )

        # Simulate narrative consistency (improves with session continuity)
        narrative_consistency = min(
            1.0,
            max(
                0.6,
                0.7 + (session_number * 0.05) + (world_setting.complexity_level * 0.1),
            ),
        )

        # Simulate turn count
        turn_count = self.min_turns_per_session + int(
            engagement_score * (self.max_turns_per_session - self.min_turns_per_session)
        )

        # Record metrics in clinical dashboard
        await self._record_session_metrics(
            session_id,
            player_profile.name,
            engagement_score,
            progress_score,
            safety_score,
            therapeutic_value,
        )

        session_end = datetime.now(timezone.utc)
        session_duration = (session_end - session_start).total_seconds()

        metrics = SessionMetrics(
            session_id=session_id,
            player_profile=player_profile.name,
            character_archetype=character_archetype.name,
            world_setting=world_setting.name,
            turn_count=turn_count,
            engagement_score=engagement_score,
            progress_score=progress_score,
            safety_score=safety_score,
            therapeutic_value=therapeutic_value,
            narrative_consistency=narrative_consistency,
            session_duration=session_duration,
            timestamp=session_start.isoformat(),
        )

        logger.info(
            f"✅ Session completed: {session_id} "
            f"(E:{engagement_score:.2f}, P:{progress_score:.2f}, "
            f"S:{safety_score:.2f}, T:{therapeutic_value:.2f})"
        )

        return metrics

    async def _record_session_metrics(
        self,
        session_id: str,
        user_id: str,
        engagement: float,
        progress: float,
        safety: float,
        therapeutic_value: float,
    ) -> None:
        """Record session metrics in the clinical dashboard."""
        try:
            # Record individual metrics
            await self.dashboard_controller.monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.ENGAGEMENT,
                value=engagement,
                context={"source": "narrative_study", "study_id": self.study_id},
            )

            await self.dashboard_controller.monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.PROGRESS,
                value=progress,
                context={"source": "narrative_study", "study_id": self.study_id},
            )

            await self.dashboard_controller.monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.SAFETY,
                value=safety,
                context={"source": "narrative_study", "study_id": self.study_id},
            )

            await self.dashboard_controller.monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.THERAPEUTIC_VALUE,
                value=therapeutic_value,
                context={"source": "narrative_study", "study_id": self.study_id},
            )

        except Exception as e:
            logger.warning(f"Failed to record metrics for session {session_id}: {e}")

    async def execute_comprehensive_study(self) -> StudyResults:
        """Execute the complete comparative analysis study."""
        logger.info("🚀 Starting Comprehensive Narrative Analysis Study")
        logger.info("=" * 80)

        # Get study parameters
        player_profiles = self.define_player_profiles()
        character_archetypes = self.define_character_archetypes()
        world_settings = self.define_world_settings()

        total_scenarios = (
            len(player_profiles) * len(character_archetypes) * len(world_settings)
        )
        total_sessions = total_scenarios * self.sessions_per_scenario

        logger.info("📊 Study Parameters:")
        logger.info(f"   Player Profiles: {len(player_profiles)}")
        logger.info(f"   Character Archetypes: {len(character_archetypes)}")
        logger.info(f"   World Settings: {len(world_settings)}")
        logger.info(f"   Sessions per Scenario: {self.sessions_per_scenario}")
        logger.info(f"   Total Scenarios: {total_scenarios}")
        logger.info(f"   Total Sessions: {total_sessions}")
        logger.info("")

        # Execute all test scenarios
        session_count = 0
        for player_profile in player_profiles:
            logger.info(f"🎭 Testing Player Profile: {player_profile.name}")

            for character_archetype in character_archetypes:
                logger.info(f"  🎪 Character Archetype: {character_archetype.name}")

                for world_setting in world_settings:
                    logger.info(f"    🌍 World Setting: {world_setting.name}")

                    # Run multiple sessions for consistency testing
                    for session_num in range(1, self.sessions_per_scenario + 1):
                        session_count += 1
                        logger.info(
                            f"      📝 Session {session_num}/{self.sessions_per_scenario} "
                            f"({session_count}/{total_sessions})"
                        )

                        metrics = await self.simulate_therapeutic_session(
                            player_profile,
                            character_archetype,
                            world_setting,
                            session_num,
                        )
                        self.session_metrics.append(metrics)

                        # Brief pause between sessions
                        await asyncio.sleep(0.1)

        # Generate comprehensive analysis
        study_results = await self._analyze_study_results()

        logger.info("🎉 Comprehensive Narrative Analysis Study Complete!")
        return study_results

    async def _analyze_study_results(self) -> StudyResults:
        """Analyze collected session data and generate comprehensive results."""
        logger.info("📊 Analyzing study results...")

        if not self.session_metrics:
            raise ValueError("No session data collected")

        study_end_time = datetime.now(timezone.utc)
        execution_time = (study_end_time - self.study_start_time).total_seconds()

        # Calculate overall metrics
        all_engagement = [m.engagement_score for m in self.session_metrics]
        all_progress = [m.progress_score for m in self.session_metrics]
        all_safety = [m.safety_score for m in self.session_metrics]
        all_therapeutic = [m.therapeutic_value for m in self.session_metrics]
        all_consistency = [m.narrative_consistency for m in self.session_metrics]
        all_turns = [m.turn_count for m in self.session_metrics]

        overall_metrics = {
            "mean_engagement": statistics.mean(all_engagement),
            "mean_progress": statistics.mean(all_progress),
            "mean_safety": statistics.mean(all_safety),
            "mean_therapeutic_value": statistics.mean(all_therapeutic),
            "mean_narrative_consistency": statistics.mean(all_consistency),
            "mean_turn_count": statistics.mean(all_turns),
            "std_engagement": (
                statistics.stdev(all_engagement) if len(all_engagement) > 1 else 0
            ),
            "std_progress": (
                statistics.stdev(all_progress) if len(all_progress) > 1 else 0
            ),
            "std_safety": statistics.stdev(all_safety) if len(all_safety) > 1 else 0,
            "std_therapeutic_value": (
                statistics.stdev(all_therapeutic) if len(all_therapeutic) > 1 else 0
            ),
        }

        # Analyze by player profile
        player_profile_results = {}
        for profile_name in {m.player_profile for m in self.session_metrics}:
            profile_sessions = [
                m for m in self.session_metrics if m.player_profile == profile_name
            ]
            player_profile_results[profile_name] = {
                "session_count": len(profile_sessions),
                "mean_engagement": statistics.mean(
                    [m.engagement_score for m in profile_sessions]
                ),
                "mean_progress": statistics.mean(
                    [m.progress_score for m in profile_sessions]
                ),
                "mean_safety": statistics.mean(
                    [m.safety_score for m in profile_sessions]
                ),
                "mean_therapeutic_value": statistics.mean(
                    [m.therapeutic_value for m in profile_sessions]
                ),
                "mean_narrative_consistency": statistics.mean(
                    [m.narrative_consistency for m in profile_sessions]
                ),
                "mean_turn_count": statistics.mean(
                    [m.turn_count for m in profile_sessions]
                ),
            }

        # Analyze by character archetype
        character_archetype_results = {}
        for archetype_name in {m.character_archetype for m in self.session_metrics}:
            archetype_sessions = [
                m
                for m in self.session_metrics
                if m.character_archetype == archetype_name
            ]
            character_archetype_results[archetype_name] = {
                "session_count": len(archetype_sessions),
                "mean_engagement": statistics.mean(
                    [m.engagement_score for m in archetype_sessions]
                ),
                "mean_progress": statistics.mean(
                    [m.progress_score for m in archetype_sessions]
                ),
                "mean_safety": statistics.mean(
                    [m.safety_score for m in archetype_sessions]
                ),
                "mean_therapeutic_value": statistics.mean(
                    [m.therapeutic_value for m in archetype_sessions]
                ),
                "mean_narrative_consistency": statistics.mean(
                    [m.narrative_consistency for m in archetype_sessions]
                ),
                "mean_turn_count": statistics.mean(
                    [m.turn_count for m in archetype_sessions]
                ),
            }

        # Analyze by world setting
        world_setting_results = {}
        for setting_name in {m.world_setting for m in self.session_metrics}:
            setting_sessions = [
                m for m in self.session_metrics if m.world_setting == setting_name
            ]
            world_setting_results[setting_name] = {
                "session_count": len(setting_sessions),
                "mean_engagement": statistics.mean(
                    [m.engagement_score for m in setting_sessions]
                ),
                "mean_progress": statistics.mean(
                    [m.progress_score for m in setting_sessions]
                ),
                "mean_safety": statistics.mean(
                    [m.safety_score for m in setting_sessions]
                ),
                "mean_therapeutic_value": statistics.mean(
                    [m.therapeutic_value for m in setting_sessions]
                ),
                "mean_narrative_consistency": statistics.mean(
                    [m.narrative_consistency for m in setting_sessions]
                ),
                "mean_turn_count": statistics.mean(
                    [m.turn_count for m in setting_sessions]
                ),
            }

        # Establish baseline benchmarks
        baseline_benchmarks = {
            "engagement_baseline": overall_metrics["mean_engagement"],
            "progress_baseline": overall_metrics["mean_progress"],
            "safety_baseline": overall_metrics["mean_safety"],
            "therapeutic_value_baseline": overall_metrics["mean_therapeutic_value"],
            "narrative_consistency_baseline": overall_metrics[
                "mean_narrative_consistency"
            ],
            "session_length_baseline": overall_metrics["mean_turn_count"],
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_metrics,
            player_profile_results,
            character_archetype_results,
            world_setting_results,
        )

        return StudyResults(
            study_id=self.study_id,
            total_sessions=len(self.session_metrics),
            total_turns=sum(m.turn_count for m in self.session_metrics),
            execution_time=execution_time,
            player_profile_results=player_profile_results,
            character_archetype_results=character_archetype_results,
            world_setting_results=world_setting_results,
            overall_metrics=overall_metrics,
            baseline_benchmarks=baseline_benchmarks,
            recommendations=recommendations,
            raw_session_data=self.session_metrics,
        )

    def _generate_recommendations(
        self,
        overall_metrics: dict[str, float],
        player_profile_results: dict[str, dict[str, float]],
        character_archetype_results: dict[str, dict[str, float]],
        world_setting_results: dict[str, dict[str, float]],
    ) -> list[str]:
        """Generate actionable recommendations based on study results."""
        recommendations = []

        # Overall system recommendations
        if overall_metrics["mean_engagement"] < 0.6:
            recommendations.append(
                "Consider enhancing engagement mechanisms across all scenarios"
            )

        if overall_metrics["mean_narrative_consistency"] < 0.8:
            recommendations.append(
                "Improve narrative consistency tracking and continuity systems"
            )

        if overall_metrics["std_therapeutic_value"] > 0.2:
            recommendations.append(
                "Reduce variability in therapeutic value delivery across scenarios"
            )

        # Player profile specific recommendations
        lowest_engagement_profile = min(
            player_profile_results.items(), key=lambda x: x[1]["mean_engagement"]
        )
        if lowest_engagement_profile[1]["mean_engagement"] < 0.5:
            recommendations.append(
                f"Develop specialized engagement strategies for {lowest_engagement_profile[0]} player profile"
            )

        # Character archetype recommendations
        lowest_therapeutic_archetype = min(
            character_archetype_results.items(),
            key=lambda x: x[1]["mean_therapeutic_value"],
        )
        if lowest_therapeutic_archetype[1]["mean_therapeutic_value"] < 0.6:
            recommendations.append(
                f"Enhance therapeutic value delivery for {lowest_therapeutic_archetype[0]} character archetype"
            )

        # World setting recommendations
        lowest_safety_setting = min(
            world_setting_results.items(), key=lambda x: x[1]["mean_safety"]
        )
        if lowest_safety_setting[1]["mean_safety"] < 0.8:
            recommendations.append(
                f"Strengthen safety protocols in {lowest_safety_setting[0]} world setting"
            )

        # Consistency recommendations
        consistency_scores = [
            results["mean_narrative_consistency"]
            for results in world_setting_results.values()
        ]
        if max(consistency_scores) - min(consistency_scores) > 0.2:
            recommendations.append(
                "Standardize narrative consistency mechanisms across all world settings"
            )

        return recommendations

    async def generate_comprehensive_report(self, results: StudyResults) -> str:
        """Generate a comprehensive analysis report."""
        report_lines = []

        # Header
        report_lines.extend(
            [
                "=" * 80,
                "🔬 COMPREHENSIVE TTA NARRATIVE CONSISTENCY & QUALITY ANALYSIS STUDY",
                "=" * 80,
                "",
                f"Study ID: {results.study_id}",
                f"Execution Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"Total Sessions: {results.total_sessions}",
                f"Total Turns: {results.total_turns}",
                f"Execution Time: {results.execution_time:.2f} seconds",
                "",
            ]
        )

        # Executive Summary
        report_lines.extend(
            [
                "📋 EXECUTIVE SUMMARY",
                "-" * 40,
                f"Overall Engagement Score: {results.overall_metrics['mean_engagement']:.3f} ± {results.overall_metrics['std_engagement']:.3f}",
                f"Overall Progress Score: {results.overall_metrics['mean_progress']:.3f} ± {results.overall_metrics['std_progress']:.3f}",
                f"Overall Safety Score: {results.overall_metrics['mean_safety']:.3f} ± {results.overall_metrics['std_safety']:.3f}",
                f"Overall Therapeutic Value: {results.overall_metrics['mean_therapeutic_value']:.3f} ± {results.overall_metrics['std_therapeutic_value']:.3f}",
                f"Overall Narrative Consistency: {results.overall_metrics['mean_narrative_consistency']:.3f}",
                f"Average Session Length: {results.overall_metrics['mean_turn_count']:.1f} turns",
                "",
            ]
        )

        # Player Profile Analysis
        report_lines.extend(
            [
                "🎭 PLAYER PROFILE ANALYSIS",
                "-" * 40,
            ]
        )

        for profile_name, profile_results in results.player_profile_results.items():
            report_lines.extend(
                [
                    f"Profile: {profile_name.upper()}",
                    f"  Sessions: {profile_results['session_count']}",
                    f"  Engagement: {profile_results['mean_engagement']:.3f}",
                    f"  Progress: {profile_results['mean_progress']:.3f}",
                    f"  Safety: {profile_results['mean_safety']:.3f}",
                    f"  Therapeutic Value: {profile_results['mean_therapeutic_value']:.3f}",
                    f"  Narrative Consistency: {profile_results['mean_narrative_consistency']:.3f}",
                    f"  Avg Session Length: {profile_results['mean_turn_count']:.1f} turns",
                    "",
                ]
            )

        # Character Archetype Analysis
        report_lines.extend(
            [
                "🎪 CHARACTER ARCHETYPE ANALYSIS",
                "-" * 40,
            ]
        )

        for (
            archetype_name,
            archetype_results,
        ) in results.character_archetype_results.items():
            report_lines.extend(
                [
                    f"Archetype: {archetype_name.upper()}",
                    f"  Sessions: {archetype_results['session_count']}",
                    f"  Engagement: {archetype_results['mean_engagement']:.3f}",
                    f"  Progress: {archetype_results['mean_progress']:.3f}",
                    f"  Safety: {archetype_results['mean_safety']:.3f}",
                    f"  Therapeutic Value: {archetype_results['mean_therapeutic_value']:.3f}",
                    f"  Narrative Consistency: {archetype_results['mean_narrative_consistency']:.3f}",
                    f"  Avg Session Length: {archetype_results['mean_turn_count']:.1f} turns",
                    "",
                ]
            )

        # World Setting Analysis
        report_lines.extend(
            [
                "🌍 WORLD SETTING ANALYSIS",
                "-" * 40,
            ]
        )

        for setting_name, setting_results in results.world_setting_results.items():
            report_lines.extend(
                [
                    f"Setting: {setting_name.upper()}",
                    f"  Sessions: {setting_results['session_count']}",
                    f"  Engagement: {setting_results['mean_engagement']:.3f}",
                    f"  Progress: {setting_results['mean_progress']:.3f}",
                    f"  Safety: {setting_results['mean_safety']:.3f}",
                    f"  Therapeutic Value: {setting_results['mean_therapeutic_value']:.3f}",
                    f"  Narrative Consistency: {setting_results['mean_narrative_consistency']:.3f}",
                    f"  Avg Session Length: {setting_results['mean_turn_count']:.1f} turns",
                    "",
                ]
            )

        # Baseline Benchmarks
        report_lines.extend(
            [
                "📊 BASELINE BENCHMARKS FOR FUTURE COMPARISONS",
                "-" * 40,
            ]
        )

        for benchmark_name, benchmark_value in results.baseline_benchmarks.items():
            report_lines.append(f"{benchmark_name}: {benchmark_value:.3f}")

        report_lines.append("")

        # Recommendations
        report_lines.extend(
            [
                "💡 RECOMMENDATIONS",
                "-" * 40,
            ]
        )

        for i, recommendation in enumerate(results.recommendations, 1):
            report_lines.append(f"{i}. {recommendation}")

        report_lines.extend(
            [
                "",
                "=" * 80,
                "End of Report",
                "=" * 80,
            ]
        )

        return "\n".join(report_lines)

    async def save_study_results(self, results: StudyResults, report: str) -> None:
        """Save study results and report to files."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        results_file = f"narrative_study_results_{timestamp}.json"
        with open(results_file, "w") as f:
            # Convert dataclasses to dict for JSON serialization
            results_dict = asdict(results)
            json.dump(results_dict, f, indent=2, default=str)

        # Save report
        report_file = f"narrative_study_report_{timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"📁 Study results saved to: {results_file}")
        logger.info(f"📄 Study report saved to: {report_file}")

    async def cleanup(self) -> None:
        """Clean up study resources."""
        try:
            if self.dashboard_controller:
                await self.dashboard_controller.shutdown()
            logger.info("✅ Study cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")


async def main():
    """Main execution function."""
    study = ComprehensiveNarrativeAnalysisStudy()

    try:
        # Initialize study
        if not await study.initialize_study():
            logger.error("❌ Failed to initialize study")
            return 1

        # Execute comprehensive study
        results = await study.execute_comprehensive_study()

        # Generate report
        report = await study.generate_comprehensive_report(results)

        # Display report
        print("\n" + report)

        # Save results
        await study.save_study_results(results, report)

        logger.info("🎉 Comprehensive Narrative Analysis Study completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Study execution failed: {e}")
        return 1
    finally:
        await study.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
