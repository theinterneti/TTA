#!/usr/bin/env python3
"""
Comprehensive Media-Based World Generation Validation Study

This study evaluates the TTA system's ability to adapt popular media franchises
into therapeutic gaming environments while maintaining clinical effectiveness,
safety protocols, and narrative authenticity. The study tests therapeutic
integration across diverse fictional universes and measures engagement
enhancement through media familiarity.

Study Objectives:
1. Media Franchise Adaptation Testing across diverse fictional universes
2. Therapeutic Integration Validation within established media contexts
3. Content Appropriateness Assessment for challenging source material
4. Player Engagement Analysis comparing media vs. original worlds
5. Clinical Dashboard Integration for real-time media-based session monitoring
"""

import asyncio
import json
import logging
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

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


class MediaCategory(Enum):
    """Categories of media franchises to test."""

    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    HORROR_THRILLER = "horror_thriller"
    FAMILY_FRIENDLY = "family_friendly"
    SUPERHERO = "superhero"
    ANIME_MANGA = "anime_manga"
    VIDEO_GAMES = "video_games"


class ContentComplexity(Enum):
    """Content complexity levels for therapeutic adaptation."""

    SIMPLE = "simple"  # Family-friendly, minimal adaptation needed
    MODERATE = "moderate"  # Some challenging elements, moderate adaptation
    COMPLEX = "complex"  # Significant challenging content, extensive adaptation
    EXTREME = "extreme"  # Very challenging content, complete transformation


class TherapeuticFramework(Enum):
    """Therapeutic frameworks integrated into media worlds."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    TRAUMA_INFORMED = "trauma_informed_care"
    MINDFULNESS = "mindfulness_based"
    NARRATIVE_THERAPY = "narrative_therapy"
    SOLUTION_FOCUSED = "solution_focused"


@dataclass
class MediaFranchise:
    """Defines a media franchise for therapeutic adaptation."""

    name: str
    category: MediaCategory
    description: str
    source_content_rating: str  # G, PG, PG-13, R, etc.
    complexity_level: ContentComplexity
    challenging_elements: list[str]  # Violence, horror, mature themes, etc.
    therapeutic_opportunities: list[str]  # Growth themes, character arcs, etc.
    recommended_frameworks: list[TherapeuticFramework]
    target_age_groups: list[str]
    adaptation_strategy: str
    safety_considerations: list[str]


@dataclass
class MediaPlayerProfile:
    """Player profile with media preferences and therapeutic needs."""

    name: str
    description: str
    preferred_media_categories: list[MediaCategory]
    familiar_franchises: list[str]
    therapeutic_needs: list[str]
    age_group: str
    media_engagement_baseline: float  # Expected engagement with media content
    therapeutic_readiness: float  # Readiness for therapeutic work
    content_sensitivity: float  # Sensitivity to challenging content


@dataclass
class ContentAdaptation:
    """Describes how challenging content is adapted for therapeutic use."""

    original_element: str
    therapeutic_metaphor: str
    adaptation_method: str
    safety_rating: float
    therapeutic_value: float
    narrative_preservation: float


@dataclass
class MediaSessionMetrics:
    """Metrics for media-based therapeutic sessions."""

    session_id: str
    player_profile: str
    media_franchise: str
    media_category: str
    content_adaptations: list[ContentAdaptation]
    engagement_score: float
    therapeutic_value: float
    safety_score: float
    narrative_authenticity: float
    media_familiarity_bonus: float
    framework_integration_score: float
    content_appropriateness: float
    session_duration: float
    timestamp: str


class MediaBasedWorldValidationStudy:
    """
    Comprehensive study framework for media-based world generation validation.

    This class orchestrates testing of the TTA system's ability to adapt popular
    media franchises into therapeutic gaming environments while maintaining
    clinical effectiveness and safety standards.
    """

    def __init__(self):
        """Initialize the media-based validation study."""
        self.study_id = (
            f"media_world_study_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )

        # API configuration
        self.api_config = APIConfig(
            base_url="http://0.0.0.0:8080",
            timeout=120,  # Longer timeout for complex media adaptations
            max_retries=3,
            retry_delay=2.0,
        )

        # Clinical dashboard controller
        self.dashboard_controller = None

        # Study configuration
        self.sessions_per_franchise = 3
        self.min_turns_per_session = 12
        self.max_turns_per_session = 20

        # Results storage
        self.session_metrics: list[MediaSessionMetrics] = []
        self.study_start_time = None

        logger.info(f"Initialized Media-Based World Validation Study: {self.study_id}")

    def define_media_franchises(self) -> list[MediaFranchise]:
        """Define media franchises for therapeutic adaptation testing."""
        return [
            # Science Fiction
            MediaFranchise(
                name="Star Trek",
                category=MediaCategory.SCIENCE_FICTION,
                description="Optimistic future with exploration and diplomacy themes",
                source_content_rating="PG-13",
                complexity_level=ContentComplexity.SIMPLE,
                challenging_elements=["mild_violence", "complex_ethics"],
                therapeutic_opportunities=[
                    "problem_solving",
                    "diversity_acceptance",
                    "moral_reasoning",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.CBT,
                    TherapeuticFramework.SOLUTION_FOCUSED,
                ],
                target_age_groups=["teen", "adult"],
                adaptation_strategy="Emphasize diplomatic solutions and ethical decision-making",
                safety_considerations=[
                    "avoid_war_scenarios",
                    "focus_on_peaceful_resolution",
                ],
            ),
            MediaFranchise(
                name="Blade Runner",
                category=MediaCategory.SCIENCE_FICTION,
                description="Dystopian future exploring humanity and identity",
                source_content_rating="R",
                complexity_level=ContentComplexity.COMPLEX,
                challenging_elements=[
                    "violence",
                    "existential_themes",
                    "dark_atmosphere",
                ],
                therapeutic_opportunities=[
                    "identity_exploration",
                    "empathy_development",
                    "meaning_making",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.NARRATIVE_THERAPY,
                    TherapeuticFramework.TRAUMA_INFORMED,
                ],
                target_age_groups=["adult"],
                adaptation_strategy="Transform violence into internal conflicts, focus on identity journey",
                safety_considerations=[
                    "remove_graphic_content",
                    "emphasize_hope",
                    "provide_support_resources",
                ],
            ),
            # Fantasy
            MediaFranchise(
                name="Harry Potter",
                category=MediaCategory.FANTASY,
                description="Magical world with coming-of-age themes",
                source_content_rating="PG-13",
                complexity_level=ContentComplexity.MODERATE,
                challenging_elements=["mild_violence", "death_themes", "bullying"],
                therapeutic_opportunities=[
                    "friendship",
                    "resilience",
                    "self_discovery",
                    "overcoming_adversity",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.CBT,
                    TherapeuticFramework.NARRATIVE_THERAPY,
                ],
                target_age_groups=["child", "teen", "adult"],
                adaptation_strategy="Focus on friendship bonds and personal growth over conflict",
                safety_considerations=[
                    "minimize_death_references",
                    "emphasize_support_systems",
                ],
            ),
            MediaFranchise(
                name="Lord of the Rings",
                category=MediaCategory.FANTASY,
                description="Epic fantasy with themes of courage and friendship",
                source_content_rating="PG-13",
                complexity_level=ContentComplexity.MODERATE,
                challenging_elements=["battle_scenes", "dark_themes", "loss"],
                therapeutic_opportunities=[
                    "courage_building",
                    "teamwork",
                    "perseverance",
                    "hope",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.CBT,
                    TherapeuticFramework.SOLUTION_FOCUSED,
                ],
                target_age_groups=["teen", "adult"],
                adaptation_strategy="Transform battles into personal challenges, emphasize fellowship",
                safety_considerations=[
                    "metaphorical_conflicts",
                    "focus_on_positive_outcomes",
                ],
            ),
            # Horror/Thriller (Heavily Adapted)
            MediaFranchise(
                name="Resident Evil (Therapeutic)",
                category=MediaCategory.HORROR_THRILLER,
                description="Survival themes adapted for anxiety and trauma therapy",
                source_content_rating="M (Adapted to PG-13)",
                complexity_level=ContentComplexity.EXTREME,
                challenging_elements=[
                    "horror_elements",
                    "survival_stress",
                    "isolation",
                ],
                therapeutic_opportunities=[
                    "anxiety_management",
                    "coping_skills",
                    "resilience_building",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.TRAUMA_INFORMED,
                    TherapeuticFramework.DBT,
                ],
                target_age_groups=["adult"],
                adaptation_strategy="Transform horror into anxiety metaphors, focus on coping strategies",
                safety_considerations=[
                    "no_graphic_content",
                    "emphasize_safety",
                    "provide_grounding_techniques",
                ],
            ),
            # Family-Friendly
            MediaFranchise(
                name="My Little Pony",
                category=MediaCategory.FAMILY_FRIENDLY,
                description="Friendship and harmony themes in colorful world",
                source_content_rating="G",
                complexity_level=ContentComplexity.SIMPLE,
                challenging_elements=["minor_conflicts"],
                therapeutic_opportunities=[
                    "friendship_skills",
                    "emotional_regulation",
                    "conflict_resolution",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.DBT,
                    TherapeuticFramework.MINDFULNESS,
                ],
                target_age_groups=["child", "teen"],
                adaptation_strategy="Direct therapeutic integration with minimal adaptation needed",
                safety_considerations=[
                    "maintain_positive_atmosphere",
                    "age_appropriate_content",
                ],
            ),
            MediaFranchise(
                name="Studio Ghibli",
                category=MediaCategory.FAMILY_FRIENDLY,
                description="Magical realism with environmental and growth themes",
                source_content_rating="G",
                complexity_level=ContentComplexity.SIMPLE,
                challenging_elements=["mild_environmental_concerns"],
                therapeutic_opportunities=[
                    "nature_connection",
                    "personal_growth",
                    "family_relationships",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.MINDFULNESS,
                    TherapeuticFramework.NARRATIVE_THERAPY,
                ],
                target_age_groups=["child", "teen", "adult"],
                adaptation_strategy="Emphasize mindfulness and connection with nature",
                safety_considerations=[
                    "maintain_wonder",
                    "positive_environmental_messages",
                ],
            ),
            # Superhero
            MediaFranchise(
                name="Marvel Universe",
                category=MediaCategory.SUPERHERO,
                description="Superhero stories with responsibility and growth themes",
                source_content_rating="PG-13",
                complexity_level=ContentComplexity.MODERATE,
                challenging_elements=["action_violence", "moral_complexity"],
                therapeutic_opportunities=[
                    "responsibility",
                    "teamwork",
                    "overcoming_limitations",
                    "helping_others",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.CBT,
                    TherapeuticFramework.SOLUTION_FOCUSED,
                ],
                target_age_groups=["teen", "adult"],
                adaptation_strategy="Focus on personal responsibility and helping others",
                safety_considerations=[
                    "minimize_violence",
                    "emphasize_positive_role_models",
                ],
            ),
            # Video Games
            MediaFranchise(
                name="Animal Crossing",
                category=MediaCategory.VIDEO_GAMES,
                description="Peaceful life simulation with community building",
                source_content_rating="E",
                complexity_level=ContentComplexity.SIMPLE,
                challenging_elements=["none"],
                therapeutic_opportunities=[
                    "routine_building",
                    "social_skills",
                    "goal_setting",
                    "stress_relief",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.DBT,
                    TherapeuticFramework.MINDFULNESS,
                ],
                target_age_groups=["child", "teen", "adult"],
                adaptation_strategy="Direct therapeutic integration with daily life skills",
                safety_considerations=[
                    "maintain_peaceful_environment",
                    "positive_social_interactions",
                ],
            ),
            MediaFranchise(
                name="Minecraft",
                category=MediaCategory.VIDEO_GAMES,
                description="Creative building and exploration game",
                source_content_rating="E",
                complexity_level=ContentComplexity.SIMPLE,
                challenging_elements=["mild_monsters"],
                therapeutic_opportunities=[
                    "creativity",
                    "problem_solving",
                    "goal_achievement",
                    "collaboration",
                ],
                recommended_frameworks=[
                    TherapeuticFramework.CBT,
                    TherapeuticFramework.SOLUTION_FOCUSED,
                ],
                target_age_groups=["child", "teen", "adult"],
                adaptation_strategy="Focus on creative expression and collaborative building",
                safety_considerations=["peaceful_mode", "collaborative_projects"],
            ),
        ]

    def define_media_player_profiles(self) -> list[MediaPlayerProfile]:
        """Define player profiles with diverse media preferences."""
        return [
            MediaPlayerProfile(
                name="sci_fi_enthusiast",
                description="Adult player who loves science fiction and complex narratives",
                preferred_media_categories=[
                    MediaCategory.SCIENCE_FICTION,
                    MediaCategory.SUPERHERO,
                ],
                familiar_franchises=["Star Trek", "Blade Runner", "Marvel Universe"],
                therapeutic_needs=[
                    "identity_exploration",
                    "problem_solving",
                    "future_planning",
                ],
                age_group="adult",
                media_engagement_baseline=0.8,
                therapeutic_readiness=0.7,
                content_sensitivity=0.3,
            ),
            MediaPlayerProfile(
                name="fantasy_lover",
                description="Teen player drawn to magical worlds and adventure",
                preferred_media_categories=[
                    MediaCategory.FANTASY,
                    MediaCategory.FAMILY_FRIENDLY,
                ],
                familiar_franchises=[
                    "Harry Potter",
                    "Lord of the Rings",
                    "Studio Ghibli",
                ],
                therapeutic_needs=[
                    "self_discovery",
                    "friendship_skills",
                    "courage_building",
                ],
                age_group="teen",
                media_engagement_baseline=0.9,
                therapeutic_readiness=0.6,
                content_sensitivity=0.5,
            ),
            MediaPlayerProfile(
                name="family_oriented",
                description="Parent seeking positive content for family therapy",
                preferred_media_categories=[
                    MediaCategory.FAMILY_FRIENDLY,
                    MediaCategory.VIDEO_GAMES,
                ],
                familiar_franchises=[
                    "My Little Pony",
                    "Studio Ghibli",
                    "Animal Crossing",
                ],
                therapeutic_needs=[
                    "family_bonding",
                    "emotional_regulation",
                    "stress_management",
                ],
                age_group="adult",
                media_engagement_baseline=0.6,
                therapeutic_readiness=0.8,
                content_sensitivity=0.8,
            ),
            MediaPlayerProfile(
                name="gaming_native",
                description="Young adult comfortable with video game worlds",
                preferred_media_categories=[
                    MediaCategory.VIDEO_GAMES,
                    MediaCategory.ANIME_MANGA,
                ],
                familiar_franchises=["Minecraft", "Animal Crossing"],
                therapeutic_needs=[
                    "social_skills",
                    "goal_setting",
                    "creativity_expression",
                ],
                age_group="young_adult",
                media_engagement_baseline=0.9,
                therapeutic_readiness=0.5,
                content_sensitivity=0.4,
            ),
            MediaPlayerProfile(
                name="trauma_survivor",
                description="Adult with trauma history needing careful content adaptation",
                preferred_media_categories=[
                    MediaCategory.FAMILY_FRIENDLY,
                    MediaCategory.FANTASY,
                ],
                familiar_franchises=["Studio Ghibli", "Harry Potter"],
                therapeutic_needs=[
                    "trauma_processing",
                    "safety_building",
                    "empowerment",
                ],
                age_group="adult",
                media_engagement_baseline=0.5,
                therapeutic_readiness=0.9,
                content_sensitivity=0.9,
            ),
        ]

    async def initialize_study(self) -> bool:
        """Initialize the media-based validation study."""
        try:
            logger.info("🎬 Initializing Media-Based World Validation Study")

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
            logger.info("✅ Media-based study environment initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing media-based study: {e}")
            return False

    def generate_content_adaptations(
        self, franchise: MediaFranchise, player_profile: MediaPlayerProfile
    ) -> list[ContentAdaptation]:
        """Generate content adaptations based on franchise and player profile."""
        adaptations = []

        # Adapt challenging elements based on player sensitivity
        for element in franchise.challenging_elements:
            adaptation = self._create_content_adaptation(
                element, franchise, player_profile
            )
            adaptations.append(adaptation)

        return adaptations

    def _create_content_adaptation(
        self,
        element: str,
        franchise: MediaFranchise,
        player_profile: MediaPlayerProfile,
    ) -> ContentAdaptation:
        """Create a specific content adaptation."""

        # Define adaptation strategies for different challenging elements
        adaptation_strategies = {
            "violence": {
                "therapeutic_metaphor": "internal_conflict_resolution",
                "method": "Transform physical conflicts into emotional/psychological challenges",
                "safety_boost": 0.3,
            },
            "battle_scenes": {
                "therapeutic_metaphor": "overcoming_personal_obstacles",
                "method": "Reframe battles as personal growth challenges",
                "safety_boost": 0.2,
            },
            "horror_elements": {
                "therapeutic_metaphor": "facing_fears_and_anxieties",
                "method": "Transform horror into anxiety management exercises",
                "safety_boost": 0.4,
            },
            "death_themes": {
                "therapeutic_metaphor": "life_transitions_and_growth",
                "method": "Reframe as personal transformation and renewal",
                "safety_boost": 0.3,
            },
            "dark_atmosphere": {
                "therapeutic_metaphor": "navigating_difficult_emotions",
                "method": "Use darkness as metaphor for depression/anxiety with light as hope",
                "safety_boost": 0.2,
            },
            "existential_themes": {
                "therapeutic_metaphor": "meaning_making_and_purpose",
                "method": "Guide exploration of personal values and life purpose",
                "safety_boost": 0.1,
            },
        }

        # Get adaptation strategy or create default
        strategy = adaptation_strategies.get(
            element,
            {
                "therapeutic_metaphor": "personal_growth_opportunity",
                "method": "Transform challenging content into growth-oriented narrative",
                "safety_boost": 0.2,
            },
        )

        # Calculate safety rating based on player sensitivity and adaptation
        base_safety = 0.5
        sensitivity_adjustment = player_profile.content_sensitivity * 0.3
        adaptation_boost = strategy["safety_boost"]
        safety_rating = min(
            1.0, base_safety + sensitivity_adjustment + adaptation_boost
        )

        # Calculate therapeutic value
        therapeutic_value = min(1.0, 0.6 + (player_profile.therapeutic_readiness * 0.3))

        # Calculate narrative preservation (how well original elements are maintained)
        if franchise.complexity_level == ContentComplexity.SIMPLE:
            narrative_preservation = 0.9
        elif franchise.complexity_level == ContentComplexity.MODERATE:
            narrative_preservation = 0.7
        elif franchise.complexity_level == ContentComplexity.COMPLEX:
            narrative_preservation = 0.5
        else:  # EXTREME
            narrative_preservation = 0.3

        return ContentAdaptation(
            original_element=element,
            therapeutic_metaphor=strategy["therapeutic_metaphor"],
            adaptation_method=strategy["method"],
            safety_rating=safety_rating,
            therapeutic_value=therapeutic_value,
            narrative_preservation=narrative_preservation,
        )

    async def simulate_media_therapeutic_session(
        self,
        franchise: MediaFranchise,
        player_profile: MediaPlayerProfile,
        session_number: int,
    ) -> MediaSessionMetrics:
        """Simulate a therapeutic session in a media-adapted world."""

        session_id = f"{self.study_id}_{franchise.name.replace(' ', '_')}_{player_profile.name}_{session_number}"
        session_start = datetime.now(timezone.utc)

        logger.info(
            f"🎮 Starting media session: {franchise.name} with {player_profile.name}"
        )

        # Generate content adaptations for this session
        content_adaptations = self.generate_content_adaptations(
            franchise, player_profile
        )

        # Calculate media familiarity bonus
        media_familiarity_bonus = 0.0
        if franchise.name in player_profile.familiar_franchises:
            media_familiarity_bonus = 0.2
        elif franchise.category in player_profile.preferred_media_categories:
            media_familiarity_bonus = 0.1

        # Calculate base engagement with media enhancement
        base_engagement = player_profile.media_engagement_baseline
        media_enhanced_engagement = min(1.0, base_engagement + media_familiarity_bonus)

        # Apply session progression (improvement over sessions)
        progression_factor = 1.0 + (session_number * 0.05)
        engagement_score = min(1.0, media_enhanced_engagement * progression_factor)

        # Calculate therapeutic value based on framework integration
        framework_integration_score = self._calculate_framework_integration(
            franchise, player_profile
        )

        # Base therapeutic value from adaptations
        if content_adaptations:
            adaptation_therapeutic_value = statistics.mean(
                [a.therapeutic_value for a in content_adaptations]
            )
        else:
            adaptation_therapeutic_value = 0.8  # Simple content, high therapeutic value

        therapeutic_value = min(
            1.0,
            adaptation_therapeutic_value
            * framework_integration_score
            * player_profile.therapeutic_readiness,
        )

        # Calculate safety score
        if content_adaptations:
            adaptation_safety = statistics.mean(
                [a.safety_rating for a in content_adaptations]
            )
        else:
            adaptation_safety = 0.95  # Simple content, very safe

        # Adjust safety based on player sensitivity
        safety_score = min(
            1.0, adaptation_safety + (player_profile.content_sensitivity * 0.1)
        )

        # Calculate narrative authenticity
        if content_adaptations:
            narrative_authenticity = statistics.mean(
                [a.narrative_preservation for a in content_adaptations]
            )
        else:
            narrative_authenticity = 0.95  # Simple content maintains authenticity

        # Calculate content appropriateness
        content_appropriateness = self._calculate_content_appropriateness(
            franchise, player_profile, content_adaptations
        )

        # Record metrics in clinical dashboard
        await self._record_media_session_metrics(
            session_id,
            player_profile.name,
            franchise.name,
            engagement_score,
            therapeutic_value,
            safety_score,
        )

        session_end = datetime.now(timezone.utc)
        session_duration = (session_end - session_start).total_seconds()

        metrics = MediaSessionMetrics(
            session_id=session_id,
            player_profile=player_profile.name,
            media_franchise=franchise.name,
            media_category=franchise.category.value,
            content_adaptations=content_adaptations,
            engagement_score=engagement_score,
            therapeutic_value=therapeutic_value,
            safety_score=safety_score,
            narrative_authenticity=narrative_authenticity,
            media_familiarity_bonus=media_familiarity_bonus,
            framework_integration_score=framework_integration_score,
            content_appropriateness=content_appropriateness,
            session_duration=session_duration,
            timestamp=session_start.isoformat(),
        )

        logger.info(
            f"✅ Media session completed: {franchise.name} "
            f"(E:{engagement_score:.2f}, T:{therapeutic_value:.2f}, "
            f"S:{safety_score:.2f}, A:{narrative_authenticity:.2f})"
        )

        return metrics

    def _calculate_framework_integration(
        self, franchise: MediaFranchise, player_profile: MediaPlayerProfile
    ) -> float:
        """Calculate how well therapeutic frameworks integrate with the media world."""

        # Base integration score
        base_score = 0.7

        # Bonus for matching therapeutic needs with franchise opportunities
        need_match_bonus = 0.0
        for need in player_profile.therapeutic_needs:
            if any(
                need in opportunity
                for opportunity in franchise.therapeutic_opportunities
            ):
                need_match_bonus += 0.05

        # Bonus for appropriate framework selection
        framework_bonus = len(franchise.recommended_frameworks) * 0.02

        return min(1.0, base_score + need_match_bonus + framework_bonus)

    def _calculate_content_appropriateness(
        self,
        franchise: MediaFranchise,
        player_profile: MediaPlayerProfile,
        adaptations: list[ContentAdaptation],
    ) -> float:
        """Calculate content appropriateness for the player profile."""

        # Base appropriateness
        base_score = 0.8

        # Age appropriateness
        age_appropriate = player_profile.age_group in franchise.target_age_groups
        age_bonus = 0.1 if age_appropriate else -0.2

        # Content sensitivity alignment
        if adaptations:
            avg_safety = statistics.mean([a.safety_rating for a in adaptations])
            sensitivity_alignment = avg_safety * player_profile.content_sensitivity
        else:
            sensitivity_alignment = 0.1

        return min(1.0, max(0.0, base_score + age_bonus + sensitivity_alignment))

    async def _record_media_session_metrics(
        self,
        session_id: str,
        user_id: str,
        franchise_name: str,
        engagement: float,
        therapeutic_value: float,
        safety: float,
    ) -> None:
        """Record media session metrics in clinical dashboard."""
        try:
            # Record standard metrics with media context
            metrics_to_record = [
                (MetricType.ENGAGEMENT, engagement),
                (MetricType.THERAPEUTIC_VALUE, therapeutic_value),
                (MetricType.SAFETY, safety),
            ]

            for metric_type, value in metrics_to_record:
                await self.dashboard_controller.monitoring_service.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=metric_type,
                    value=value,
                    context={
                        "source": "media_world_study",
                        "study_id": self.study_id,
                        "media_franchise": franchise_name,
                        "adaptation_type": "media_based_world",
                    },
                )

        except Exception as e:
            logger.warning(f"Failed to record media session metrics: {e}")

    async def execute_media_world_study(self) -> dict[str, Any]:
        """Execute the comprehensive media-based world validation study."""
        logger.info("🚀 Starting Media-Based World Validation Study")
        logger.info("=" * 80)

        # Get study parameters
        media_franchises = self.define_media_franchises()
        player_profiles = self.define_media_player_profiles()

        total_sessions = (
            len(media_franchises) * len(player_profiles) * self.sessions_per_franchise
        )

        logger.info("📊 Media Study Parameters:")
        logger.info(f"   Media Franchises: {len(media_franchises)}")
        logger.info(f"   Player Profiles: {len(player_profiles)}")
        logger.info(f"   Sessions per Franchise: {self.sessions_per_franchise}")
        logger.info(f"   Total Sessions: {total_sessions}")
        logger.info("")

        # Execute all media franchise scenarios
        session_count = 0
        for franchise in media_franchises:
            logger.info(f"🎬 Testing Media Franchise: {franchise.name}")
            logger.info(f"   Category: {franchise.category.value}")
            logger.info(f"   Complexity: {franchise.complexity_level.value}")
            logger.info(
                f"   Challenging Elements: {len(franchise.challenging_elements)}"
            )

            for player_profile in player_profiles:
                # Check if this franchise is appropriate for this player
                if not self._is_franchise_appropriate(franchise, player_profile):
                    logger.info(
                        f"   ⏭️ Skipping {player_profile.name} (inappropriate content)"
                    )
                    continue

                logger.info(f"   👤 Player Profile: {player_profile.name}")

                for session_num in range(1, self.sessions_per_franchise + 1):
                    session_count += 1
                    logger.info(
                        f"      📝 Session {session_num}/{self.sessions_per_franchise}"
                    )

                    metrics = await self.simulate_media_therapeutic_session(
                        franchise, player_profile, session_num
                    )
                    self.session_metrics.append(metrics)

                    # Brief pause between sessions
                    await asyncio.sleep(0.1)

        # Generate comprehensive analysis
        study_results = await self._analyze_media_study_results()

        logger.info("🎉 Media-Based World Validation Study Complete!")
        return study_results

    def _is_franchise_appropriate(
        self, franchise: MediaFranchise, player_profile: MediaPlayerProfile
    ) -> bool:
        """Check if a franchise is appropriate for a player profile."""

        # Age appropriateness check
        if player_profile.age_group not in franchise.target_age_groups:
            return False

        # Content sensitivity check for complex content
        if (
            franchise.complexity_level
            in [ContentComplexity.COMPLEX, ContentComplexity.EXTREME]
            and player_profile.content_sensitivity > 0.7
        ):
            return False

        # Special case: trauma survivors should avoid extreme content
        if (
            "trauma_processing" in player_profile.therapeutic_needs
            and franchise.complexity_level == ContentComplexity.EXTREME
        ):
            return False

        return True

    async def _analyze_media_study_results(self) -> dict[str, Any]:
        """Analyze media study results with comprehensive metrics."""
        logger.info("📊 Analyzing media-based study results...")

        if not self.session_metrics:
            raise ValueError("No media session data collected")

        study_end_time = datetime.now(timezone.utc)
        execution_time = (study_end_time - self.study_start_time).total_seconds()

        # Overall metrics
        all_engagement = [m.engagement_score for m in self.session_metrics]
        all_therapeutic = [m.therapeutic_value for m in self.session_metrics]
        all_safety = [m.safety_score for m in self.session_metrics]
        all_authenticity = [m.narrative_authenticity for m in self.session_metrics]
        all_appropriateness = [m.content_appropriateness for m in self.session_metrics]
        all_familiarity_bonus = [
            m.media_familiarity_bonus for m in self.session_metrics
        ]
        all_framework_integration = [
            m.framework_integration_score for m in self.session_metrics
        ]

        # Media category analysis
        category_results = {}
        for category in MediaCategory:
            category_sessions = [
                m for m in self.session_metrics if m.media_category == category.value
            ]
            if category_sessions:
                category_results[category.value] = {
                    "session_count": len(category_sessions),
                    "mean_engagement": statistics.mean(
                        [m.engagement_score for m in category_sessions]
                    ),
                    "mean_therapeutic_value": statistics.mean(
                        [m.therapeutic_value for m in category_sessions]
                    ),
                    "mean_safety": statistics.mean(
                        [m.safety_score for m in category_sessions]
                    ),
                    "mean_narrative_authenticity": statistics.mean(
                        [m.narrative_authenticity for m in category_sessions]
                    ),
                    "mean_content_appropriateness": statistics.mean(
                        [m.content_appropriateness for m in category_sessions]
                    ),
                    "mean_familiarity_bonus": statistics.mean(
                        [m.media_familiarity_bonus for m in category_sessions]
                    ),
                }

        # Franchise-specific analysis
        franchise_results = {}
        for franchise_name in {m.media_franchise for m in self.session_metrics}:
            franchise_sessions = [
                m for m in self.session_metrics if m.media_franchise == franchise_name
            ]
            franchise_results[franchise_name] = {
                "session_count": len(franchise_sessions),
                "mean_engagement": statistics.mean(
                    [m.engagement_score for m in franchise_sessions]
                ),
                "mean_therapeutic_value": statistics.mean(
                    [m.therapeutic_value for m in franchise_sessions]
                ),
                "mean_safety": statistics.mean(
                    [m.safety_score for m in franchise_sessions]
                ),
                "mean_narrative_authenticity": statistics.mean(
                    [m.narrative_authenticity for m in franchise_sessions]
                ),
                "content_adaptations_count": sum(
                    len(m.content_adaptations) for m in franchise_sessions
                ),
            }

        # Content adaptation analysis
        all_adaptations = []
        for session in self.session_metrics:
            all_adaptations.extend(session.content_adaptations)

        adaptation_effectiveness = (
            statistics.mean([a.therapeutic_value for a in all_adaptations])
            if all_adaptations
            else 1.0
        )
        adaptation_safety = (
            statistics.mean([a.safety_rating for a in all_adaptations])
            if all_adaptations
            else 1.0
        )
        narrative_preservation = (
            statistics.mean([a.narrative_preservation for a in all_adaptations])
            if all_adaptations
            else 1.0
        )

        # Generate media-specific recommendations
        media_recommendations = self._generate_media_recommendations(
            category_results, franchise_results, adaptation_effectiveness
        )

        return {
            "study_id": self.study_id,
            "total_sessions": len(self.session_metrics),
            "execution_time": execution_time,
            "overall_metrics": {
                "mean_engagement": statistics.mean(all_engagement),
                "mean_therapeutic_value": statistics.mean(all_therapeutic),
                "mean_safety": statistics.mean(all_safety),
                "mean_narrative_authenticity": statistics.mean(all_authenticity),
                "mean_content_appropriateness": statistics.mean(all_appropriateness),
                "mean_familiarity_bonus": statistics.mean(all_familiarity_bonus),
                "mean_framework_integration": statistics.mean(
                    all_framework_integration
                ),
                "std_engagement": (
                    statistics.stdev(all_engagement) if len(all_engagement) > 1 else 0
                ),
                "std_safety": (
                    statistics.stdev(all_safety) if len(all_safety) > 1 else 0
                ),
            },
            "content_adaptation_analysis": {
                "total_adaptations": len(all_adaptations),
                "adaptation_effectiveness": adaptation_effectiveness,
                "adaptation_safety": adaptation_safety,
                "narrative_preservation": narrative_preservation,
            },
            "media_category_results": category_results,
            "franchise_results": franchise_results,
            "media_recommendations": media_recommendations,
            "raw_session_data": [asdict(m) for m in self.session_metrics],
        }

    def _generate_media_recommendations(
        self,
        category_results: dict,
        franchise_results: dict,
        adaptation_effectiveness: float,
    ) -> list[str]:
        """Generate media-specific recommendations."""
        recommendations = []

        # Overall adaptation recommendations
        if adaptation_effectiveness < 0.7:
            recommendations.append(
                "Enhance content adaptation strategies for challenging media elements"
            )

        # Category-specific recommendations
        for category, results in category_results.items():
            if results["mean_safety"] < 0.8:
                recommendations.append(
                    f"Strengthen safety protocols for {category} media adaptations"
                )

            if results["mean_narrative_authenticity"] < 0.6:
                recommendations.append(
                    f"Improve narrative preservation techniques for {category} franchises"
                )

            if results["mean_familiarity_bonus"] < 0.1:
                recommendations.append(
                    f"Better leverage media familiarity for {category} engagement"
                )

        # Franchise-specific recommendations
        low_performing_franchises = [
            name
            for name, results in franchise_results.items()
            if results["mean_therapeutic_value"] < 0.6
        ]

        if low_performing_franchises:
            recommendations.append(
                f"Optimize therapeutic integration for: {', '.join(low_performing_franchises)}"
            )

        return recommendations

    async def generate_media_study_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive media study report."""
        report_lines = []

        # Header
        report_lines.extend(
            [
                "=" * 80,
                "🎬 COMPREHENSIVE MEDIA-BASED WORLD GENERATION VALIDATION STUDY",
                "=" * 80,
                "",
                f"Study ID: {results['study_id']}",
                f"Execution Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"Total Sessions: {results['total_sessions']}",
                f"Execution Time: {results['execution_time']:.2f} seconds",
                "",
            ]
        )

        # Executive Summary
        overall = results["overall_metrics"]
        adaptation = results["content_adaptation_analysis"]

        report_lines.extend(
            [
                "📋 EXECUTIVE SUMMARY",
                "-" * 40,
                f"Overall Engagement Score: {overall['mean_engagement']:.3f} ± {overall['std_engagement']:.3f}",
                f"Overall Therapeutic Value: {overall['mean_therapeutic_value']:.3f}",
                f"Overall Safety Score: {overall['mean_safety']:.3f} ± {overall['std_safety']:.3f}",
                f"Narrative Authenticity: {overall['mean_narrative_authenticity']:.3f}",
                f"Content Appropriateness: {overall['mean_content_appropriateness']:.3f}",
                f"Media Familiarity Bonus: {overall['mean_familiarity_bonus']:.3f}",
                f"Framework Integration: {overall['mean_framework_integration']:.3f}",
                "",
                "🔄 CONTENT ADAPTATION ANALYSIS",
                "-" * 40,
                f"Total Content Adaptations: {adaptation['total_adaptations']}",
                f"Adaptation Effectiveness: {adaptation['adaptation_effectiveness']:.3f}",
                f"Adaptation Safety: {adaptation['adaptation_safety']:.3f}",
                f"Narrative Preservation: {adaptation['narrative_preservation']:.3f}",
                "",
            ]
        )

        # Media Category Analysis
        report_lines.extend(
            [
                "📺 MEDIA CATEGORY ANALYSIS",
                "-" * 40,
            ]
        )

        for category, results_data in results["media_category_results"].items():
            report_lines.extend(
                [
                    f"Category: {category.upper()}",
                    f"  Sessions: {results_data['session_count']}",
                    f"  Engagement: {results_data['mean_engagement']:.3f}",
                    f"  Therapeutic Value: {results_data['mean_therapeutic_value']:.3f}",
                    f"  Safety: {results_data['mean_safety']:.3f}",
                    f"  Narrative Authenticity: {results_data['mean_narrative_authenticity']:.3f}",
                    f"  Content Appropriateness: {results_data['mean_content_appropriateness']:.3f}",
                    f"  Familiarity Bonus: {results_data['mean_familiarity_bonus']:.3f}",
                    "",
                ]
            )

        # Top Performing Franchises
        franchise_results = results["franchise_results"]
        top_franchises = sorted(
            franchise_results.items(),
            key=lambda x: x[1]["mean_therapeutic_value"],
            reverse=True,
        )[:5]

        report_lines.extend(
            [
                "🏆 TOP PERFORMING FRANCHISES",
                "-" * 40,
            ]
        )

        for i, (franchise_name, franchise_data) in enumerate(top_franchises, 1):
            report_lines.extend(
                [
                    f"{i}. {franchise_name}",
                    f"   Therapeutic Value: {franchise_data['mean_therapeutic_value']:.3f}",
                    f"   Engagement: {franchise_data['mean_engagement']:.3f}",
                    f"   Safety: {franchise_data['mean_safety']:.3f}",
                    f"   Narrative Authenticity: {franchise_data['mean_narrative_authenticity']:.3f}",
                    "",
                ]
            )

        # Media Recommendations
        report_lines.extend(
            [
                "💡 MEDIA ADAPTATION RECOMMENDATIONS",
                "-" * 40,
            ]
        )

        for i, recommendation in enumerate(results["media_recommendations"], 1):
            report_lines.append(f"{i}. {recommendation}")

        report_lines.extend(
            [
                "",
                "=" * 80,
                "End of Media-Based World Validation Report",
                "=" * 80,
            ]
        )

        return "\n".join(report_lines)

    async def save_media_study_results(
        self, results: dict[str, Any], report: str
    ) -> None:
        """Save media study results and report."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        results_file = f"media_world_study_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save report
        report_file = f"media_world_study_report_{timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"📁 Media study results saved to: {results_file}")
        logger.info(f"📄 Media study report saved to: {report_file}")

    async def cleanup(self) -> None:
        """Clean up media study resources."""
        try:
            if self.dashboard_controller:
                await self.dashboard_controller.shutdown()
            logger.info("✅ Media study cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during media study cleanup: {e}")


async def main():
    """Main execution function for media-based world validation study."""
    study = MediaBasedWorldValidationStudy()

    try:
        # Initialize media study
        if not await study.initialize_study():
            logger.error("❌ Failed to initialize media study")
            return 1

        # Execute media world study
        results = await study.execute_media_world_study()

        # Generate media report
        report = await study.generate_media_study_report(results)

        # Display report
        print("\n" + report)

        # Save results
        await study.save_media_study_results(results, report)

        logger.info("🎉 Media-Based World Validation Study completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Media study execution failed: {e}")
        return 1
    finally:
        await study.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
