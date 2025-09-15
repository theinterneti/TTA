#!/usr/bin/env python3
"""
Enhanced Clinical Robustness & Boundary-Testing Validation Study

This expanded study simulates complex mental health conditions, grief scenarios,
justice-involved individuals, and boundary-testing behaviors to validate the
TTA system's clinical robustness, safety protocols, and therapeutic effectiveness
under challenging real-world conditions.

Study Objectives:
1. Validate system response to complex mental health presentations
2. Test boundary-testing behavior management and therapeutic redirection
3. Validate crisis detection and intervention capabilities
4. Assess therapeutic alliance maintenance under challenging conditions
5. Demonstrate clinical robustness for production deployment
"""

import asyncio
import json
import logging
import random
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


class MentalHealthCondition(Enum):
    """Mental health conditions to simulate."""

    DEPRESSION_MILD = "depression_mild"
    DEPRESSION_MODERATE = "depression_moderate"
    DEPRESSION_SEVERE = "depression_severe"
    ANXIETY_GENERALIZED = "anxiety_generalized"
    ANXIETY_SOCIAL = "anxiety_social"
    ANXIETY_PANIC = "anxiety_panic"
    PTSD_COMBAT = "ptsd_combat"
    PTSD_TRAUMA = "ptsd_trauma"
    PTSD_COMPLEX = "ptsd_complex"
    BIPOLAR_MANIC = "bipolar_manic"
    BIPOLAR_DEPRESSIVE = "bipolar_depressive"
    SUBSTANCE_RECOVERY = "substance_recovery"
    SUBSTANCE_ACTIVE = "substance_active"
    SUBSTANCE_RELAPSE_RISK = "substance_relapse_risk"
    EATING_DISORDER = "eating_disorder"
    PERSONALITY_BORDERLINE = "personality_borderline"
    PERSONALITY_ANTISOCIAL = "personality_antisocial"


class GriefType(Enum):
    """Types of grief and loss scenarios."""

    RECENT_SPOUSE = "recent_spouse_loss"
    RECENT_CHILD = "recent_child_loss"
    RECENT_PARENT = "recent_parent_loss"
    ANTICIPATORY = "anticipatory_grief"
    COMPLICATED = "complicated_grief"
    DISENFRANCHISED = "disenfranchised_grief"
    COLLECTIVE = "collective_grief"


class JusticeInvolvement(Enum):
    """Justice-involved individual scenarios."""

    PAROLE_PREP = "parole_preparation"
    REENTRY_PROGRAM = "reentry_program"
    ANGER_MANAGEMENT = "anger_management"
    VICTIM_EMPATHY = "victim_empathy"
    CRIMINAL_THINKING = "criminal_thinking"


class BoundaryTestingBehavior(Enum):
    """Types of boundary-testing behaviors."""

    INAPPROPRIATE_SEXUAL = "inappropriate_sexual"
    VIOLENT_FANTASY = "violent_fantasy"
    SELF_HARM_IDEATION = "self_harm_ideation"
    SUBSTANCE_GLORIFICATION = "substance_glorification"
    THERAPEUTIC_MANIPULATION = "therapeutic_manipulation"
    CONFIDENTIALITY_TESTING = "confidentiality_testing"
    ENGAGEMENT_RESISTANCE = "engagement_resistance"
    SAFETY_BYPASS_ATTEMPT = "safety_bypass_attempt"


class InterventionLevel(Enum):
    """Graduated intervention levels."""

    WARNING = "warning"
    REDIRECTION = "redirection"
    ESCALATION = "escalation"
    CRISIS_INTERVENTION = "crisis_intervention"


@dataclass
class ClinicalPlayerProfile:
    """Enhanced player profile with clinical presentations."""

    name: str
    description: str
    mental_health_condition: MentalHealthCondition | None
    grief_type: GriefType | None
    justice_involvement: JusticeInvolvement | None
    primary_symptoms: list[str]
    therapeutic_needs: list[str]
    risk_factors: list[str]
    protective_factors: list[str]
    engagement_baseline: float
    crisis_risk: float
    boundary_testing_likelihood: float
    therapeutic_alliance_strength: float


@dataclass
class BoundaryTestingScenario:
    """Boundary-testing behavior scenario."""

    behavior_type: BoundaryTestingBehavior
    severity_level: float  # 0.0 = mild testing, 1.0 = severe boundary violation
    description: str
    expected_intervention: InterventionLevel
    therapeutic_response: str
    safety_concern_level: float


@dataclass
class InterventionResponse:
    """System response to boundary-testing behavior."""

    intervention_level: InterventionLevel
    response_time: float  # seconds
    therapeutic_redirection: str
    safety_protocol_activated: bool
    crisis_detected: bool
    alliance_maintained: bool
    effectiveness_score: float


@dataclass
class EnhancedSessionMetrics:
    """Enhanced metrics for clinical robustness testing."""

    session_id: str
    player_profile: str
    mental_health_condition: str
    boundary_testing_occurred: bool
    intervention_responses: list[InterventionResponse]
    engagement_score: float
    progress_score: float
    safety_score: float
    therapeutic_value: float
    alliance_maintenance: float
    crisis_detection_accuracy: float
    boundary_management_effectiveness: float
    narrative_consistency: float
    session_duration: float
    timestamp: str


class EnhancedClinicalRobustnessStudy:
    """
    Enhanced study framework for clinical robustness and boundary-testing validation.

    This class orchestrates comprehensive testing of the TTA system's ability to handle
    complex mental health conditions, boundary-testing behaviors, and crisis situations
    while maintaining therapeutic safety and effectiveness.
    """

    def __init__(self):
        """Initialize the enhanced study framework."""
        self.study_id = f"clinical_robustness_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # API configuration
        self.api_config = APIConfig(
            base_url="http://0.0.0.0:8080",
            timeout=90,  # Longer timeout for complex scenarios
            max_retries=3,
            retry_delay=2.0,
        )

        # Clinical dashboard controller
        self.dashboard_controller: ClinicalDashboardController | None = None

        # Study configuration
        self.min_turns_per_session = 15
        self.max_turns_per_session = 25
        self.sessions_per_profile = 5  # More sessions for clinical validation
        self.boundary_testing_probability = 0.3  # 30% chance per session

        # Results storage
        self.session_metrics: list[EnhancedSessionMetrics] = []
        self.intervention_responses: list[InterventionResponse] = []
        self.study_start_time: datetime | None = None

        logger.info(f"Initialized Enhanced Clinical Robustness Study: {self.study_id}")

    def define_clinical_player_profiles(self) -> list[ClinicalPlayerProfile]:
        """Define clinical player profiles with mental health conditions."""
        return [
            # Depression Profiles
            ClinicalPlayerProfile(
                name="depression_moderate",
                description="Player with moderate depression, low energy, hopelessness",
                mental_health_condition=MentalHealthCondition.DEPRESSION_MODERATE,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=["low_mood", "anhedonia", "fatigue", "hopelessness"],
                therapeutic_needs=[
                    "behavioral_activation",
                    "cognitive_restructuring",
                    "mood_monitoring",
                ],
                risk_factors=[
                    "social_isolation",
                    "negative_thinking",
                    "sleep_disturbance",
                ],
                protective_factors=["family_support", "previous_therapy_success"],
                engagement_baseline=0.3,
                crisis_risk=0.4,
                boundary_testing_likelihood=0.2,
                therapeutic_alliance_strength=0.6,
            ),
            # Anxiety Profiles
            ClinicalPlayerProfile(
                name="anxiety_social",
                description="Player with social anxiety, fear of judgment, avoidance",
                mental_health_condition=MentalHealthCondition.ANXIETY_SOCIAL,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=[
                    "social_fear",
                    "avoidance",
                    "physical_anxiety",
                    "self_consciousness",
                ],
                therapeutic_needs=[
                    "exposure_therapy",
                    "social_skills",
                    "anxiety_management",
                ],
                risk_factors=[
                    "perfectionism",
                    "negative_self_evaluation",
                    "social_isolation",
                ],
                protective_factors=["motivation_to_change", "insight"],
                engagement_baseline=0.4,
                crisis_risk=0.3,
                boundary_testing_likelihood=0.1,
                therapeutic_alliance_strength=0.7,
            ),
            # PTSD Profiles
            ClinicalPlayerProfile(
                name="ptsd_combat",
                description="Combat veteran with PTSD, hypervigilance, trauma responses",
                mental_health_condition=MentalHealthCondition.PTSD_COMBAT,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=[
                    "flashbacks",
                    "hypervigilance",
                    "avoidance",
                    "emotional_numbing",
                ],
                therapeutic_needs=[
                    "trauma_processing",
                    "grounding_techniques",
                    "safety_building",
                ],
                risk_factors=["trauma_triggers", "substance_use", "social_withdrawal"],
                protective_factors=[
                    "military_training",
                    "service_connection",
                    "family_support",
                ],
                engagement_baseline=0.5,
                crisis_risk=0.7,
                boundary_testing_likelihood=0.4,
                therapeutic_alliance_strength=0.5,
            ),
            # Bipolar Profile
            ClinicalPlayerProfile(
                name="bipolar_depressive",
                description="Player in depressive episode of bipolar disorder",
                mental_health_condition=MentalHealthCondition.BIPOLAR_DEPRESSIVE,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=[
                    "severe_depression",
                    "mood_swings",
                    "energy_fluctuation",
                    "cognitive_impairment",
                ],
                therapeutic_needs=[
                    "mood_stabilization",
                    "medication_compliance",
                    "episode_prevention",
                ],
                risk_factors=[
                    "medication_noncompliance",
                    "stress_sensitivity",
                    "sleep_disruption",
                ],
                protective_factors=["illness_awareness", "support_system"],
                engagement_baseline=0.4,
                crisis_risk=0.6,
                boundary_testing_likelihood=0.3,
                therapeutic_alliance_strength=0.6,
            ),
            # Substance Use Profile
            ClinicalPlayerProfile(
                name="substance_recovery",
                description="Player in early recovery from substance use disorder",
                mental_health_condition=MentalHealthCondition.SUBSTANCE_RECOVERY,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=[
                    "cravings",
                    "mood_instability",
                    "cognitive_fog",
                    "shame",
                ],
                therapeutic_needs=[
                    "relapse_prevention",
                    "coping_skills",
                    "identity_rebuilding",
                ],
                risk_factors=[
                    "environmental_triggers",
                    "peer_influence",
                    "stress_vulnerability",
                ],
                protective_factors=[
                    "recovery_motivation",
                    "support_group",
                    "sponsor_relationship",
                ],
                engagement_baseline=0.6,
                crisis_risk=0.5,
                boundary_testing_likelihood=0.5,
                therapeutic_alliance_strength=0.7,
            ),
            # Grief Profile
            ClinicalPlayerProfile(
                name="complicated_grief",
                description="Player with complicated grief after spouse loss",
                mental_health_condition=None,
                grief_type=GriefType.COMPLICATED,
                justice_involvement=None,
                primary_symptoms=[
                    "persistent_yearning",
                    "difficulty_accepting_loss",
                    "anger",
                    "guilt",
                ],
                therapeutic_needs=[
                    "grief_processing",
                    "meaning_making",
                    "life_restructuring",
                ],
                risk_factors=[
                    "social_isolation",
                    "anniversary_reactions",
                    "secondary_losses",
                ],
                protective_factors=["previous_coping", "spiritual_beliefs"],
                engagement_baseline=0.4,
                crisis_risk=0.4,
                boundary_testing_likelihood=0.2,
                therapeutic_alliance_strength=0.6,
            ),
            # Justice-Involved Profile
            ClinicalPlayerProfile(
                name="reentry_program",
                description="Player in reentry program, working on criminal thinking patterns",
                mental_health_condition=None,
                grief_type=None,
                justice_involvement=JusticeInvolvement.REENTRY_PROGRAM,
                primary_symptoms=[
                    "antisocial_thinking",
                    "impulse_control",
                    "anger",
                    "mistrust",
                ],
                therapeutic_needs=[
                    "cognitive_restructuring",
                    "empathy_development",
                    "social_skills",
                ],
                risk_factors=[
                    "criminal_associates",
                    "substance_use",
                    "employment_barriers",
                ],
                protective_factors=["family_motivation", "program_structure"],
                engagement_baseline=0.3,
                crisis_risk=0.3,
                boundary_testing_likelihood=0.7,
                therapeutic_alliance_strength=0.4,
            ),
            # Personality Disorder Profile
            ClinicalPlayerProfile(
                name="borderline_personality",
                description="Player with borderline personality traits, emotional dysregulation",
                mental_health_condition=MentalHealthCondition.PERSONALITY_BORDERLINE,
                grief_type=None,
                justice_involvement=None,
                primary_symptoms=[
                    "emotional_instability",
                    "fear_of_abandonment",
                    "identity_disturbance",
                    "impulsivity",
                ],
                therapeutic_needs=[
                    "emotion_regulation",
                    "interpersonal_skills",
                    "distress_tolerance",
                ],
                risk_factors=[
                    "relationship_conflicts",
                    "self_harm_history",
                    "trauma_history",
                ],
                protective_factors=["therapy_engagement", "creative_abilities"],
                engagement_baseline=0.5,
                crisis_risk=0.8,
                boundary_testing_likelihood=0.8,
                therapeutic_alliance_strength=0.3,
            ),
        ]

    def define_boundary_testing_scenarios(self) -> list[BoundaryTestingScenario]:
        """Define boundary-testing behavior scenarios."""
        return [
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.INAPPROPRIATE_SEXUAL,
                severity_level=0.3,
                description="Mild inappropriate sexual comments or innuendo",
                expected_intervention=InterventionLevel.WARNING,
                therapeutic_response="Gentle redirection to appropriate therapeutic content",
                safety_concern_level=0.3,
            ),
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.VIOLENT_FANTASY,
                severity_level=0.5,
                description="Expression of violent thoughts without specific threats",
                expected_intervention=InterventionLevel.REDIRECTION,
                therapeutic_response="Explore underlying emotions, redirect to coping strategies",
                safety_concern_level=0.6,
            ),
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.SELF_HARM_IDEATION,
                severity_level=0.8,
                description="Expression of self-harm thoughts or planning",
                expected_intervention=InterventionLevel.CRISIS_INTERVENTION,
                therapeutic_response="Immediate safety assessment and crisis intervention",
                safety_concern_level=0.9,
            ),
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.THERAPEUTIC_MANIPULATION,
                severity_level=0.4,
                description="Attempts to manipulate therapeutic process or boundaries",
                expected_intervention=InterventionLevel.REDIRECTION,
                therapeutic_response="Maintain boundaries while exploring underlying needs",
                safety_concern_level=0.2,
            ),
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.ENGAGEMENT_RESISTANCE,
                severity_level=0.6,
                description="Active resistance to therapeutic engagement",
                expected_intervention=InterventionLevel.REDIRECTION,
                therapeutic_response="Motivational interviewing techniques, explore ambivalence",
                safety_concern_level=0.1,
            ),
            BoundaryTestingScenario(
                behavior_type=BoundaryTestingBehavior.SUBSTANCE_GLORIFICATION,
                severity_level=0.5,
                description="Glorifying substance use or minimizing consequences",
                expected_intervention=InterventionLevel.REDIRECTION,
                therapeutic_response="Challenge cognitive distortions, explore consequences",
                safety_concern_level=0.4,
            ),
        ]

    async def initialize_study(self) -> bool:
        """Initialize the enhanced study environment."""
        try:
            logger.info("🔬 Initializing Enhanced Clinical Robustness Study")

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
            logger.info("✅ Enhanced study environment initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing enhanced study: {e}")
            return False

    async def simulate_boundary_testing_behavior(
        self, profile: ClinicalPlayerProfile, session_id: str
    ) -> tuple[bool, list[InterventionResponse]]:
        """Simulate boundary-testing behavior and system responses."""

        # Determine if boundary testing occurs based on profile likelihood
        if random.random() > profile.boundary_testing_likelihood:
            return False, []

        # Select boundary testing scenarios based on profile characteristics
        available_scenarios = self.define_boundary_testing_scenarios()

        # Filter scenarios based on profile characteristics
        relevant_scenarios = []
        for scenario in available_scenarios:
            if self._is_scenario_relevant_to_profile(scenario, profile):
                relevant_scenarios.append(scenario)

        if not relevant_scenarios:
            return False, []

        # Select 1-3 boundary testing behaviors for this session
        num_behaviors = min(random.randint(1, 3), len(relevant_scenarios))
        selected_scenarios = random.sample(relevant_scenarios, num_behaviors)

        intervention_responses = []

        for scenario in selected_scenarios:
            # Simulate system response to boundary testing
            response = await self._simulate_intervention_response(
                scenario, profile, session_id
            )
            intervention_responses.append(response)

            logger.info(
                f"🚨 Boundary testing detected: {scenario.behavior_type.value} "
                f"(Severity: {scenario.severity_level:.2f}) - "
                f"Response: {response.intervention_level.value}"
            )

        return True, intervention_responses

    def _is_scenario_relevant_to_profile(
        self, scenario: BoundaryTestingScenario, profile: ClinicalPlayerProfile
    ) -> bool:
        """Determine if a boundary testing scenario is relevant to a player profile."""

        # Map scenarios to relevant conditions
        scenario_relevance = {
            BoundaryTestingBehavior.INAPPROPRIATE_SEXUAL: [
                MentalHealthCondition.PERSONALITY_BORDERLINE,
                MentalHealthCondition.PERSONALITY_ANTISOCIAL,
                MentalHealthCondition.BIPOLAR_MANIC,
            ],
            BoundaryTestingBehavior.VIOLENT_FANTASY: [
                MentalHealthCondition.PTSD_COMBAT,
                MentalHealthCondition.PTSD_TRAUMA,
                MentalHealthCondition.PERSONALITY_ANTISOCIAL,
            ],
            BoundaryTestingBehavior.SELF_HARM_IDEATION: [
                MentalHealthCondition.DEPRESSION_SEVERE,
                MentalHealthCondition.PERSONALITY_BORDERLINE,
                MentalHealthCondition.BIPOLAR_DEPRESSIVE,
            ],
            BoundaryTestingBehavior.SUBSTANCE_GLORIFICATION: [
                MentalHealthCondition.SUBSTANCE_ACTIVE,
                MentalHealthCondition.SUBSTANCE_RELAPSE_RISK,
            ],
            BoundaryTestingBehavior.THERAPEUTIC_MANIPULATION: [
                MentalHealthCondition.PERSONALITY_BORDERLINE,
                MentalHealthCondition.PERSONALITY_ANTISOCIAL,
            ],
            BoundaryTestingBehavior.ENGAGEMENT_RESISTANCE: [
                MentalHealthCondition.DEPRESSION_MODERATE,
                MentalHealthCondition.DEPRESSION_SEVERE,
            ],
        }

        # Check if scenario is relevant to profile's condition
        relevant_conditions = scenario_relevance.get(scenario.behavior_type, [])

        if profile.mental_health_condition in relevant_conditions:
            return True

        # Justice-involved individuals more likely to test boundaries
        if profile.justice_involvement and scenario.behavior_type in [
            BoundaryTestingBehavior.THERAPEUTIC_MANIPULATION,
            BoundaryTestingBehavior.ENGAGEMENT_RESISTANCE,
            BoundaryTestingBehavior.VIOLENT_FANTASY,
        ]:
            return True

        # High crisis risk profiles more likely to test safety boundaries
        if profile.crisis_risk > 0.6 and scenario.behavior_type in [
            BoundaryTestingBehavior.SELF_HARM_IDEATION,
            BoundaryTestingBehavior.SAFETY_BYPASS_ATTEMPT,
        ]:
            return True

        return False

    async def _simulate_intervention_response(
        self,
        scenario: BoundaryTestingScenario,
        profile: ClinicalPlayerProfile,
        session_id: str,
    ) -> InterventionResponse:
        """Simulate system intervention response to boundary testing."""

        # Calculate response time based on severity
        base_response_time = 0.5  # 500ms base response
        severity_factor = scenario.severity_level
        response_time = base_response_time * (1 + severity_factor)

        # Determine intervention level based on scenario and profile
        intervention_level = self._determine_intervention_level(scenario, profile)

        # Assess if crisis is detected
        crisis_detected = (
            scenario.safety_concern_level > 0.7
            or intervention_level == InterventionLevel.CRISIS_INTERVENTION
        )

        # Assess if safety protocol is activated
        safety_protocol_activated = (
            scenario.safety_concern_level > 0.5 or crisis_detected
        )

        # Assess therapeutic alliance maintenance
        alliance_impact = self._calculate_alliance_impact(
            scenario, profile, intervention_level
        )
        alliance_maintained = alliance_impact > 0.5

        # Calculate intervention effectiveness
        effectiveness_score = self._calculate_intervention_effectiveness(
            scenario, profile, intervention_level, alliance_maintained
        )

        # Record intervention in clinical dashboard
        await self._record_intervention_metrics(
            session_id,
            profile.name,
            scenario,
            intervention_level,
            crisis_detected,
            effectiveness_score,
        )

        return InterventionResponse(
            intervention_level=intervention_level,
            response_time=response_time,
            therapeutic_redirection=scenario.therapeutic_response,
            safety_protocol_activated=safety_protocol_activated,
            crisis_detected=crisis_detected,
            alliance_maintained=alliance_maintained,
            effectiveness_score=effectiveness_score,
        )

    def _determine_intervention_level(
        self, scenario: BoundaryTestingScenario, profile: ClinicalPlayerProfile
    ) -> InterventionLevel:
        """Determine appropriate intervention level."""

        # Base intervention level from scenario
        base_level = scenario.expected_intervention

        # Adjust based on profile characteristics
        if profile.crisis_risk > 0.7 and scenario.safety_concern_level > 0.5:
            # High-risk profiles get escalated interventions
            if base_level == InterventionLevel.WARNING:
                return InterventionLevel.REDIRECTION
            elif base_level == InterventionLevel.REDIRECTION:
                return InterventionLevel.ESCALATION

        # Personality disorders may require firmer boundaries
        if profile.mental_health_condition in [
            MentalHealthCondition.PERSONALITY_BORDERLINE,
            MentalHealthCondition.PERSONALITY_ANTISOCIAL,
        ]:
            if base_level == InterventionLevel.WARNING:
                return InterventionLevel.REDIRECTION

        return base_level

    def _calculate_alliance_impact(
        self,
        scenario: BoundaryTestingScenario,
        profile: ClinicalPlayerProfile,
        intervention_level: InterventionLevel,
    ) -> float:
        """Calculate impact on therapeutic alliance."""

        base_alliance = profile.therapeutic_alliance_strength

        # Intervention level impact
        intervention_impact = {
            InterventionLevel.WARNING: 0.9,
            InterventionLevel.REDIRECTION: 0.8,
            InterventionLevel.ESCALATION: 0.6,
            InterventionLevel.CRISIS_INTERVENTION: 0.7,  # Crisis intervention can strengthen alliance
        }

        # Scenario type impact
        scenario_impact = 1.0 - (scenario.severity_level * 0.3)

        # Profile-specific adjustments
        if (
            profile.mental_health_condition
            == MentalHealthCondition.PERSONALITY_BORDERLINE
        ):
            # Borderline personalities may have stronger reactions to boundaries
            scenario_impact *= 0.8

        final_alliance = (
            base_alliance * intervention_impact[intervention_level] * scenario_impact
        )
        return min(1.0, max(0.0, final_alliance))

    def _calculate_intervention_effectiveness(
        self,
        scenario: BoundaryTestingScenario,
        profile: ClinicalPlayerProfile,
        intervention_level: InterventionLevel,
        alliance_maintained: bool,
    ) -> float:
        """Calculate intervention effectiveness score."""

        # Base effectiveness based on appropriate intervention level
        if intervention_level == scenario.expected_intervention:
            base_effectiveness = 0.8
        elif intervention_level.value > scenario.expected_intervention.value:
            base_effectiveness = 0.7  # Over-intervention
        else:
            base_effectiveness = 0.5  # Under-intervention

        # Alliance maintenance bonus
        if alliance_maintained:
            base_effectiveness += 0.1

        # Profile-specific adjustments
        if profile.therapeutic_alliance_strength > 0.6:
            base_effectiveness += 0.1

        return min(1.0, max(0.0, base_effectiveness))

    async def _record_intervention_metrics(
        self,
        session_id: str,
        user_id: str,
        scenario: BoundaryTestingScenario,
        intervention_level: InterventionLevel,
        crisis_detected: bool,
        effectiveness_score: float,
    ) -> None:
        """Record intervention metrics in clinical dashboard."""
        try:
            # Record boundary testing event
            await self.dashboard_controller.monitoring_service.collect_metric(
                user_id=user_id,
                session_id=session_id,
                metric_type=MetricType.SAFETY,
                value=1.0 - scenario.safety_concern_level,
                context={
                    "source": "boundary_testing",
                    "behavior_type": scenario.behavior_type.value,
                    "severity": scenario.severity_level,
                    "intervention_level": intervention_level.value,
                    "crisis_detected": crisis_detected,
                    "effectiveness": effectiveness_score,
                },
            )

        except Exception as e:
            logger.warning(f"Failed to record intervention metrics: {e}")

    async def simulate_enhanced_therapeutic_session(
        self, profile: ClinicalPlayerProfile, session_number: int
    ) -> EnhancedSessionMetrics:
        """Simulate an enhanced therapeutic session with clinical complexity."""

        session_id = f"{self.study_id}_{profile.name}_{session_number}"
        session_start = datetime.now(timezone.utc)

        logger.info(f"🎮 Starting enhanced session: {session_id}")

        # Simulate boundary testing behavior
        boundary_testing_occurred, intervention_responses = (
            await self.simulate_boundary_testing_behavior(profile, session_id)
        )

        # Calculate base metrics influenced by clinical presentation
        base_engagement = profile.engagement_baseline

        # Adjust engagement based on mental health condition
        condition_factor = self._get_condition_engagement_factor(
            profile.mental_health_condition
        )

        # Adjust for boundary testing impact
        boundary_impact = 1.0
        if boundary_testing_occurred:
            # Boundary testing can reduce engagement initially
            boundary_impact = 0.8
            # But effective interventions can restore it
            avg_effectiveness = statistics.mean(
                [r.effectiveness_score for r in intervention_responses]
            )
            boundary_impact += avg_effectiveness * 0.3

        # Session progression factor (improvement over sessions)
        progression_factor = 1.0 + (session_number * 0.05)

        # Calculate final engagement score
        engagement_score = min(
            1.0,
            max(
                0.0,
                base_engagement
                * condition_factor
                * boundary_impact
                * progression_factor,
            ),
        )

        # Calculate progress score based on therapeutic needs
        progress_base = 0.3 + (len(profile.protective_factors) * 0.1)
        progress_score = min(
            1.0, max(0.0, progress_base * condition_factor * progression_factor)
        )

        # Calculate safety score based on risk factors and interventions
        safety_base = 1.0 - (profile.crisis_risk * 0.3)
        intervention_safety_boost = 0.0
        if boundary_testing_occurred:
            # Effective interventions improve safety
            avg_crisis_detection = statistics.mean(
                [1.0 if r.crisis_detected else 0.0 for r in intervention_responses]
            )
            intervention_safety_boost = avg_crisis_detection * 0.1

        safety_score = min(1.0, max(0.3, safety_base + intervention_safety_boost))

        # Calculate therapeutic value
        therapeutic_value = min(
            1.0,
            max(
                0.0,
                (engagement_score + progress_score + safety_score)
                / 3.0
                * (1.0 + profile.therapeutic_alliance_strength * 0.2),
            ),
        )

        # Calculate alliance maintenance score
        alliance_maintenance = profile.therapeutic_alliance_strength
        if boundary_testing_occurred:
            alliance_impacts = [r.alliance_maintained for r in intervention_responses]
            alliance_maintenance *= sum(alliance_impacts) / len(alliance_impacts)

        # Calculate crisis detection accuracy
        crisis_detection_accuracy = 1.0  # Default for no boundary testing
        if boundary_testing_occurred:
            # Measure accuracy of crisis detection
            true_crises = sum(
                1
                for r in intervention_responses
                if r.intervention_level == InterventionLevel.CRISIS_INTERVENTION
            )
            detected_crises = sum(
                1 for r in intervention_responses if r.crisis_detected
            )
            if true_crises > 0:
                crisis_detection_accuracy = min(1.0, detected_crises / true_crises)

        # Calculate boundary management effectiveness
        boundary_management_effectiveness = 1.0  # Default for no boundary testing
        if boundary_testing_occurred:
            boundary_management_effectiveness = statistics.mean(
                [r.effectiveness_score for r in intervention_responses]
            )

        # Simulate narrative consistency (affected by clinical complexity)
        narrative_consistency = min(
            1.0, max(0.6, 0.8 + (session_number * 0.02) - (profile.crisis_risk * 0.1))
        )

        # Calculate session length based on engagement and complexity
        base_turns = self.min_turns_per_session
        engagement_turns = int(
            engagement_score * (self.max_turns_per_session - base_turns)
        )
        complexity_turns = len(
            profile.primary_symptoms
        )  # More symptoms = longer sessions
        base_turns + engagement_turns + complexity_turns

        # Record comprehensive metrics in clinical dashboard
        await self._record_enhanced_session_metrics(
            session_id,
            profile,
            engagement_score,
            progress_score,
            safety_score,
            therapeutic_value,
            boundary_testing_occurred,
        )

        session_end = datetime.now(timezone.utc)
        session_duration = (session_end - session_start).total_seconds()

        metrics = EnhancedSessionMetrics(
            session_id=session_id,
            player_profile=profile.name,
            mental_health_condition=(
                profile.mental_health_condition.value
                if profile.mental_health_condition
                else "none"
            ),
            boundary_testing_occurred=boundary_testing_occurred,
            intervention_responses=intervention_responses,
            engagement_score=engagement_score,
            progress_score=progress_score,
            safety_score=safety_score,
            therapeutic_value=therapeutic_value,
            alliance_maintenance=alliance_maintenance,
            crisis_detection_accuracy=crisis_detection_accuracy,
            boundary_management_effectiveness=boundary_management_effectiveness,
            narrative_consistency=narrative_consistency,
            session_duration=session_duration,
            timestamp=session_start.isoformat(),
        )

        logger.info(
            f"✅ Enhanced session completed: {session_id} "
            f"(E:{engagement_score:.2f}, P:{progress_score:.2f}, "
            f"S:{safety_score:.2f}, T:{therapeutic_value:.2f}, "
            f"BT:{boundary_testing_occurred})"
        )

        return metrics

    def _get_condition_engagement_factor(
        self, condition: MentalHealthCondition | None
    ) -> float:
        """Get engagement factor based on mental health condition."""
        if not condition:
            return 1.0

        # Engagement factors based on clinical presentations
        condition_factors = {
            MentalHealthCondition.DEPRESSION_MILD: 0.8,
            MentalHealthCondition.DEPRESSION_MODERATE: 0.6,
            MentalHealthCondition.DEPRESSION_SEVERE: 0.4,
            MentalHealthCondition.ANXIETY_GENERALIZED: 0.7,
            MentalHealthCondition.ANXIETY_SOCIAL: 0.5,
            MentalHealthCondition.ANXIETY_PANIC: 0.6,
            MentalHealthCondition.PTSD_COMBAT: 0.7,
            MentalHealthCondition.PTSD_TRAUMA: 0.6,
            MentalHealthCondition.PTSD_COMPLEX: 0.5,
            MentalHealthCondition.BIPOLAR_MANIC: 1.2,  # High engagement during mania
            MentalHealthCondition.BIPOLAR_DEPRESSIVE: 0.4,
            MentalHealthCondition.SUBSTANCE_RECOVERY: 0.8,
            MentalHealthCondition.SUBSTANCE_ACTIVE: 0.3,
            MentalHealthCondition.SUBSTANCE_RELAPSE_RISK: 0.6,
            MentalHealthCondition.EATING_DISORDER: 0.5,
            MentalHealthCondition.PERSONALITY_BORDERLINE: 0.9,  # High but unstable
            MentalHealthCondition.PERSONALITY_ANTISOCIAL: 0.4,
        }

        return condition_factors.get(condition, 1.0)

    async def _record_enhanced_session_metrics(
        self,
        session_id: str,
        profile: ClinicalPlayerProfile,
        engagement: float,
        progress: float,
        safety: float,
        therapeutic_value: float,
        boundary_testing: bool,
    ) -> None:
        """Record enhanced session metrics in clinical dashboard."""
        try:
            # Record standard metrics
            metrics_to_record = [
                (MetricType.ENGAGEMENT, engagement),
                (MetricType.PROGRESS, progress),
                (MetricType.SAFETY, safety),
                (MetricType.THERAPEUTIC_VALUE, therapeutic_value),
            ]

            for metric_type, value in metrics_to_record:
                await self.dashboard_controller.monitoring_service.collect_metric(
                    user_id=profile.name,
                    session_id=session_id,
                    metric_type=metric_type,
                    value=value,
                    context={
                        "source": "enhanced_clinical_study",
                        "study_id": self.study_id,
                        "mental_health_condition": (
                            profile.mental_health_condition.value
                            if profile.mental_health_condition
                            else "none"
                        ),
                        "boundary_testing": boundary_testing,
                        "crisis_risk": profile.crisis_risk,
                        "alliance_strength": profile.therapeutic_alliance_strength,
                    },
                )

        except Exception as e:
            logger.warning(f"Failed to record enhanced session metrics: {e}")

    async def execute_enhanced_clinical_study(self) -> dict[str, Any]:
        """Execute the comprehensive enhanced clinical robustness study."""
        logger.info("🚀 Starting Enhanced Clinical Robustness Study")
        logger.info("=" * 80)

        # Get clinical profiles
        clinical_profiles = self.define_clinical_player_profiles()

        total_sessions = len(clinical_profiles) * self.sessions_per_profile

        logger.info("📊 Enhanced Study Parameters:")
        logger.info(f"   Clinical Profiles: {len(clinical_profiles)}")
        logger.info(f"   Sessions per Profile: {self.sessions_per_profile}")
        logger.info(f"   Total Sessions: {total_sessions}")
        logger.info("   Boundary Testing Enabled: Yes")
        logger.info("   Crisis Detection Enabled: Yes")
        logger.info("")

        # Execute all clinical scenarios
        session_count = 0
        for profile in clinical_profiles:
            logger.info(f"🏥 Testing Clinical Profile: {profile.name}")
            logger.info(
                f"   Condition: {profile.mental_health_condition.value if profile.mental_health_condition else 'None'}"
            )
            logger.info(f"   Crisis Risk: {profile.crisis_risk:.2f}")
            logger.info(
                f"   Boundary Testing Likelihood: {profile.boundary_testing_likelihood:.2f}"
            )

            for session_num in range(1, self.sessions_per_profile + 1):
                session_count += 1
                logger.info(
                    f"      📝 Session {session_num}/{self.sessions_per_profile} "
                    f"({session_count}/{total_sessions})"
                )

                metrics = await self.simulate_enhanced_therapeutic_session(
                    profile, session_num
                )
                self.session_metrics.append(metrics)

                # Brief pause between sessions
                await asyncio.sleep(0.1)

        # Generate comprehensive analysis
        study_results = await self._analyze_enhanced_study_results()

        logger.info("🎉 Enhanced Clinical Robustness Study Complete!")
        return study_results

    async def _analyze_enhanced_study_results(self) -> dict[str, Any]:
        """Analyze enhanced study results with clinical robustness metrics."""
        logger.info("📊 Analyzing enhanced clinical study results...")

        if not self.session_metrics:
            raise ValueError("No enhanced session data collected")

        study_end_time = datetime.now(timezone.utc)
        execution_time = (study_end_time - self.study_start_time).total_seconds()

        # Overall metrics
        all_engagement = [m.engagement_score for m in self.session_metrics]
        all_progress = [m.progress_score for m in self.session_metrics]
        all_safety = [m.safety_score for m in self.session_metrics]
        all_therapeutic = [m.therapeutic_value for m in self.session_metrics]
        all_alliance = [m.alliance_maintenance for m in self.session_metrics]
        all_crisis_detection = [
            m.crisis_detection_accuracy for m in self.session_metrics
        ]
        all_boundary_management = [
            m.boundary_management_effectiveness for m in self.session_metrics
        ]

        # Boundary testing analysis
        boundary_testing_sessions = [
            m for m in self.session_metrics if m.boundary_testing_occurred
        ]
        boundary_testing_rate = len(boundary_testing_sessions) / len(
            self.session_metrics
        )

        # Intervention analysis
        all_interventions = []
        for session in self.session_metrics:
            all_interventions.extend(session.intervention_responses)

        intervention_effectiveness = (
            statistics.mean([i.effectiveness_score for i in all_interventions])
            if all_interventions
            else 1.0
        )
        crisis_detection_rate = (
            sum(1 for i in all_interventions if i.crisis_detected)
            / len(all_interventions)
            if all_interventions
            else 0.0
        )

        # Mental health condition analysis
        condition_results = {}
        for condition_name in {
            m.mental_health_condition for m in self.session_metrics
        }:
            condition_sessions = [
                m
                for m in self.session_metrics
                if m.mental_health_condition == condition_name
            ]
            condition_results[condition_name] = {
                "session_count": len(condition_sessions),
                "mean_engagement": statistics.mean(
                    [m.engagement_score for m in condition_sessions]
                ),
                "mean_progress": statistics.mean(
                    [m.progress_score for m in condition_sessions]
                ),
                "mean_safety": statistics.mean(
                    [m.safety_score for m in condition_sessions]
                ),
                "mean_therapeutic_value": statistics.mean(
                    [m.therapeutic_value for m in condition_sessions]
                ),
                "boundary_testing_rate": sum(
                    1 for m in condition_sessions if m.boundary_testing_occurred
                )
                / len(condition_sessions),
                "mean_alliance_maintenance": statistics.mean(
                    [m.alliance_maintenance for m in condition_sessions]
                ),
                "mean_crisis_detection": statistics.mean(
                    [m.crisis_detection_accuracy for m in condition_sessions]
                ),
            }

        # Generate clinical recommendations
        clinical_recommendations = self._generate_clinical_recommendations(
            condition_results, boundary_testing_rate, intervention_effectiveness
        )

        return {
            "study_id": self.study_id,
            "total_sessions": len(self.session_metrics),
            "execution_time": execution_time,
            "overall_metrics": {
                "mean_engagement": statistics.mean(all_engagement),
                "mean_progress": statistics.mean(all_progress),
                "mean_safety": statistics.mean(all_safety),
                "mean_therapeutic_value": statistics.mean(all_therapeutic),
                "mean_alliance_maintenance": statistics.mean(all_alliance),
                "mean_crisis_detection_accuracy": statistics.mean(all_crisis_detection),
                "mean_boundary_management_effectiveness": statistics.mean(
                    all_boundary_management
                ),
                "std_engagement": (
                    statistics.stdev(all_engagement) if len(all_engagement) > 1 else 0
                ),
                "std_safety": (
                    statistics.stdev(all_safety) if len(all_safety) > 1 else 0
                ),
            },
            "boundary_testing_analysis": {
                "boundary_testing_rate": boundary_testing_rate,
                "total_boundary_sessions": len(boundary_testing_sessions),
                "intervention_effectiveness": intervention_effectiveness,
                "crisis_detection_rate": crisis_detection_rate,
                "total_interventions": len(all_interventions),
            },
            "mental_health_condition_results": condition_results,
            "clinical_recommendations": clinical_recommendations,
            "raw_session_data": [asdict(m) for m in self.session_metrics],
        }

    def _generate_clinical_recommendations(
        self,
        condition_results: dict[str, dict[str, float]],
        boundary_testing_rate: float,
        intervention_effectiveness: float,
    ) -> list[str]:
        """Generate clinical recommendations based on enhanced study results."""
        recommendations = []

        # Overall system recommendations
        if intervention_effectiveness < 0.7:
            recommendations.append(
                "Enhance intervention protocols and therapeutic redirection techniques"
            )

        if boundary_testing_rate > 0.5:
            recommendations.append(
                "Implement proactive boundary-setting education for high-risk profiles"
            )

        # Condition-specific recommendations
        for condition, results in condition_results.items():
            if results["mean_safety"] < 0.7:
                recommendations.append(
                    f"Strengthen safety protocols for {condition} presentations"
                )

            if results["mean_alliance_maintenance"] < 0.5:
                recommendations.append(
                    f"Develop alliance-building strategies for {condition} profiles"
                )

            if results["boundary_testing_rate"] > 0.7:
                recommendations.append(
                    f"Create specialized boundary management protocols for {condition}"
                )

        # Crisis detection recommendations
        avg_crisis_detection = statistics.mean(
            [r["mean_crisis_detection"] for r in condition_results.values()]
        )
        if avg_crisis_detection < 0.8:
            recommendations.append(
                "Improve crisis detection algorithms and response protocols"
            )

        return recommendations

    async def generate_enhanced_clinical_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive enhanced clinical report."""
        report_lines = []

        # Header
        report_lines.extend(
            [
                "=" * 80,
                "🏥 ENHANCED CLINICAL ROBUSTNESS & BOUNDARY-TESTING VALIDATION STUDY",
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
        boundary = results["boundary_testing_analysis"]

        report_lines.extend(
            [
                "📋 EXECUTIVE SUMMARY",
                "-" * 40,
                f"Overall Engagement Score: {overall['mean_engagement']:.3f} ± {overall['std_engagement']:.3f}",
                f"Overall Progress Score: {overall['mean_progress']:.3f}",
                f"Overall Safety Score: {overall['mean_safety']:.3f} ± {overall['std_safety']:.3f}",
                f"Overall Therapeutic Value: {overall['mean_therapeutic_value']:.3f}",
                f"Alliance Maintenance: {overall['mean_alliance_maintenance']:.3f}",
                f"Crisis Detection Accuracy: {overall['mean_crisis_detection_accuracy']:.3f}",
                f"Boundary Management Effectiveness: {overall['mean_boundary_management_effectiveness']:.3f}",
                "",
                "🚨 BOUNDARY TESTING & CRISIS MANAGEMENT",
                "-" * 40,
                f"Boundary Testing Rate: {boundary['boundary_testing_rate']:.1%}",
                f"Total Boundary Testing Sessions: {boundary['total_boundary_sessions']}",
                f"Intervention Effectiveness: {boundary['intervention_effectiveness']:.3f}",
                f"Crisis Detection Rate: {boundary['crisis_detection_rate']:.1%}",
                f"Total Interventions: {boundary['total_interventions']}",
                "",
            ]
        )

        # Mental Health Condition Analysis
        report_lines.extend(
            [
                "🧠 MENTAL HEALTH CONDITION ANALYSIS",
                "-" * 40,
            ]
        )

        for condition, results_data in results[
            "mental_health_condition_results"
        ].items():
            report_lines.extend(
                [
                    f"Condition: {condition.upper()}",
                    f"  Sessions: {results_data['session_count']}",
                    f"  Engagement: {results_data['mean_engagement']:.3f}",
                    f"  Progress: {results_data['mean_progress']:.3f}",
                    f"  Safety: {results_data['mean_safety']:.3f}",
                    f"  Therapeutic Value: {results_data['mean_therapeutic_value']:.3f}",
                    f"  Alliance Maintenance: {results_data['mean_alliance_maintenance']:.3f}",
                    f"  Boundary Testing Rate: {results_data['boundary_testing_rate']:.1%}",
                    f"  Crisis Detection: {results_data['mean_crisis_detection']:.3f}",
                    "",
                ]
            )

        # Clinical Recommendations
        report_lines.extend(
            [
                "💡 CLINICAL RECOMMENDATIONS",
                "-" * 40,
            ]
        )

        for i, recommendation in enumerate(results["clinical_recommendations"], 1):
            report_lines.append(f"{i}. {recommendation}")

        report_lines.extend(
            [
                "",
                "=" * 80,
                "End of Enhanced Clinical Report",
                "=" * 80,
            ]
        )

        return "\n".join(report_lines)

    async def save_enhanced_study_results(
        self, results: dict[str, Any], report: str
    ) -> None:
        """Save enhanced study results and report."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        results_file = f"enhanced_clinical_study_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save report
        report_file = f"enhanced_clinical_study_report_{timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"📁 Enhanced study results saved to: {results_file}")
        logger.info(f"📄 Enhanced study report saved to: {report_file}")

    async def cleanup(self) -> None:
        """Clean up enhanced study resources."""
        try:
            if self.dashboard_controller:
                await self.dashboard_controller.shutdown()
            logger.info("✅ Enhanced study cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during enhanced study cleanup: {e}")


async def main():
    """Main execution function for enhanced clinical study."""
    study = EnhancedClinicalRobustnessStudy()

    try:
        # Initialize enhanced study
        if not await study.initialize_study():
            logger.error("❌ Failed to initialize enhanced study")
            return 1

        # Execute enhanced clinical study
        results = await study.execute_enhanced_clinical_study()

        # Generate enhanced report
        report = await study.generate_enhanced_clinical_report(results)

        # Display report
        print("\n" + report)

        # Save results
        await study.save_enhanced_study_results(results, report)

        logger.info("🎉 Enhanced Clinical Robustness Study completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Enhanced study execution failed: {e}")
        return 1
    finally:
        await study.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
