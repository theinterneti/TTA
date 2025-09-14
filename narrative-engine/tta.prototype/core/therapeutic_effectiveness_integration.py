"""
Therapeutic Effectiveness Integration Module

This module integrates all therapeutic effectiveness enhancements into the existing TTA system,
providing a unified interface for enhanced therapeutic content delivery, professional oversight,
and effectiveness optimization.

Classes:
    TherapeuticEffectivenessManager: Main integration manager
    EnhancedTherapeuticSession: Enhanced session management with effectiveness tracking
    TherapeuticQualityAssurance: Quality assurance and monitoring system
"""

import logging
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Import enhanced therapeutic components
from .enhanced_therapeutic_effectiveness import (
    EvidenceBasedIntervention,
    EvidenceBasedInterventionEngine,
    TherapeuticContentReviewSystem,
)
from .enhanced_therapeutic_effectiveness_part2 import (
    ClinicalSupervisionIntegration,
    EnhancedTherapeuticDialogueEngine,
    TherapeuticEffectivenessOptimizer,
)

# Import existing TTA components
try:
    from ..models.data_models import NarrativeContext, SessionState, TherapeuticProgress
    from .therapeutic_content_integration import TherapeuticContentIntegration
    from .therapeutic_dialogue_system import CharacterManagementAgent
    from .therapeutic_guidance_agent import TherapeuticGuidanceAgent
except ImportError:
    # Fallback for testing
    logging.warning(
        "Could not import existing TTA components, using mock implementations"
    )

    class MockTherapeuticContentIntegration:
        def detect_therapeutic_opportunities(self, context):
            return []

    class MockTherapeuticGuidanceAgent:
        def generate_therapeutic_response(self, context):
            return {"content": "Mock therapeutic response"}

    class MockCharacterManagementAgent:
        def generate_character_dialogue(self, context):
            return {"dialogue": "Mock character dialogue"}

    TherapeuticContentIntegration = MockTherapeuticContentIntegration
    TherapeuticGuidanceAgent = MockTherapeuticGuidanceAgent
    CharacterManagementAgent = MockCharacterManagementAgent

logger = logging.getLogger(__name__)


@dataclass
class EnhancedTherapeuticMetrics:
    """Enhanced metrics for therapeutic effectiveness tracking."""

    session_id: str = ""
    overall_effectiveness_score: float = 0.0
    clinical_accuracy_score: float = 0.0
    evidence_base_score: float = 0.0
    dialogue_quality_score: float = 0.0
    intervention_success_score: float = 0.0
    safety_protocol_score: float = 0.0
    professional_oversight_score: float = 0.0
    client_progress_indicators: dict[str, float] = field(default_factory=dict)
    therapeutic_goals_achieved: int = 0
    total_therapeutic_goals: int = 0
    interventions_completed: int = 0
    total_interventions_attempted: int = 0
    crisis_interventions_handled: int = 0
    professional_consultations: int = 0
    content_reviews_completed: int = 0
    measurement_timestamp: datetime = field(default_factory=datetime.now)

    def calculate_goal_achievement_rate(self) -> float:
        """Calculate therapeutic goal achievement rate."""
        if self.total_therapeutic_goals == 0:
            return 0.0
        return self.therapeutic_goals_achieved / self.total_therapeutic_goals

    def calculate_intervention_success_rate(self) -> float:
        """Calculate intervention success rate."""
        if self.total_interventions_attempted == 0:
            return 0.0
        return self.interventions_completed / self.total_interventions_attempted


@dataclass
class EnhancedTherapeuticSession:
    """Enhanced therapeutic session with effectiveness tracking and professional oversight."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    session_start_time: datetime = field(default_factory=datetime.now)
    session_end_time: datetime | None = None
    therapeutic_goals: list[str] = field(default_factory=list)
    interventions_used: list[dict[str, Any]] = field(default_factory=list)
    dialogue_exchanges: list[dict[str, Any]] = field(default_factory=list)
    crisis_assessments: list[dict[str, Any]] = field(default_factory=list)
    professional_consultations: list[str] = field(default_factory=list)
    content_reviews: list[str] = field(default_factory=list)
    effectiveness_metrics: EnhancedTherapeuticMetrics | None = None
    session_notes: str = ""
    clinical_supervision_required: bool = False
    quality_assurance_completed: bool = False

    def add_intervention(self, intervention_data: dict[str, Any]) -> None:
        """Add intervention to session tracking."""
        intervention_record = {
            "timestamp": datetime.now().isoformat(),
            "intervention_id": intervention_data.get("intervention_id"),
            "intervention_name": intervention_data.get("intervention_name"),
            "evidence_level": intervention_data.get("evidence_level"),
            "effectiveness_prediction": intervention_data.get(
                "effectiveness_prediction", 0.0
            ),
            "implementation_status": "initiated",
        }
        self.interventions_used.append(intervention_record)

    def add_dialogue_exchange(self, dialogue_data: dict[str, Any]) -> None:
        """Add dialogue exchange to session tracking."""
        dialogue_record = {
            "timestamp": datetime.now().isoformat(),
            "dialogue_type": dialogue_data.get("dialogue_type"),
            "therapeutic_value": dialogue_data.get("therapeutic_value", 0.0),
            "clinical_validation": dialogue_data.get("clinical_validation"),
            "character_consistency": dialogue_data.get(
                "character_consistency_score", 1.0
            ),
        }
        self.dialogue_exchanges.append(dialogue_record)

    def complete_session(self) -> None:
        """Mark session as completed and calculate final metrics."""
        self.session_end_time = datetime.now()
        self.effectiveness_metrics = self._calculate_session_effectiveness()

    def _calculate_session_effectiveness(self) -> EnhancedTherapeuticMetrics:
        """Calculate effectiveness metrics for the session."""
        metrics = EnhancedTherapeuticMetrics(session_id=self.session_id)

        # Calculate intervention metrics
        if self.interventions_used:
            effectiveness_scores = [
                intervention.get("effectiveness_prediction", 0.0)
                for intervention in self.interventions_used
            ]
            metrics.intervention_success_score = (
                statistics.mean(effectiveness_scores) if effectiveness_scores else 0.0
            )
            metrics.total_interventions_attempted = len(self.interventions_used)
            metrics.interventions_completed = len(
                [
                    i
                    for i in self.interventions_used
                    if i.get("implementation_status") == "completed"
                ]
            )

        # Calculate dialogue quality metrics
        if self.dialogue_exchanges:
            dialogue_scores = [
                exchange.get("therapeutic_value", 0.0)
                for exchange in self.dialogue_exchanges
            ]
            metrics.dialogue_quality_score = (
                statistics.mean(dialogue_scores) if dialogue_scores else 0.0
            )

        # Calculate evidence base score
        evidence_levels = [
            intervention.get("evidence_level", "level_7")
            for intervention in self.interventions_used
        ]
        evidence_weights = {
            "level_1": 1.0,
            "level_2": 0.9,
            "level_3": 0.8,
            "level_4": 0.7,
            "level_5": 0.6,
            "level_6": 0.5,
            "level_7": 0.4,
        }
        if evidence_levels:
            evidence_scores = [
                evidence_weights.get(level, 0.4) for level in evidence_levels
            ]
            metrics.evidence_base_score = statistics.mean(evidence_scores)

        # Calculate professional oversight score
        metrics.professional_consultations = len(self.professional_consultations)
        metrics.content_reviews_completed = len(self.content_reviews)
        metrics.professional_oversight_score = min(
            1.0,
            0.7
            + (metrics.professional_consultations * 0.1)
            + (metrics.content_reviews_completed * 0.1),
        )

        # Calculate overall effectiveness
        component_scores = [
            metrics.intervention_success_score,
            metrics.dialogue_quality_score,
            metrics.evidence_base_score,
            metrics.professional_oversight_score,
        ]
        metrics.overall_effectiveness_score = statistics.mean(
            [s for s in component_scores if s > 0]
        )

        return metrics


class TherapeuticEffectivenessManager:
    """Main manager for enhanced therapeutic effectiveness system."""

    def __init__(self):
        """Initialize the therapeutic effectiveness manager."""
        # Initialize enhanced components
        self.intervention_engine = EvidenceBasedInterventionEngine()
        self.content_review_system = TherapeuticContentReviewSystem()
        self.dialogue_engine = EnhancedTherapeuticDialogueEngine(
            self.content_review_system, self.intervention_engine
        )
        self.supervision_integration = ClinicalSupervisionIntegration()
        self.effectiveness_optimizer = TherapeuticEffectivenessOptimizer()

        # Initialize existing TTA components
        self.content_integration = TherapeuticContentIntegration()
        self.guidance_agent = TherapeuticGuidanceAgent()
        self.character_agent = CharacterManagementAgent()

        # Session tracking
        self.active_sessions = {}
        self.session_history = {}
        self.effectiveness_tracking = {}

        logger.info("TherapeuticEffectivenessManager initialized")

    def create_enhanced_session(
        self,
        client_id: str,
        therapeutic_goals: list[str],
        session_context: dict[str, Any],
    ) -> EnhancedTherapeuticSession:
        """
        Create an enhanced therapeutic session with effectiveness tracking.

        Args:
            client_id: Unique identifier for the client
            therapeutic_goals: List of therapeutic goals for the session
            session_context: Context information for the session

        Returns:
            EnhancedTherapeuticSession: Created session with tracking enabled
        """
        try:
            session = EnhancedTherapeuticSession(
                client_id=client_id, therapeutic_goals=therapeutic_goals
            )

            # Store active session
            self.active_sessions[session.session_id] = session

            # Initialize session tracking
            self.effectiveness_tracking[session.session_id] = {
                "start_time": datetime.now(),
                "context": session_context,
                "interventions_planned": [],
                "quality_checkpoints": [],
            }

            logger.info(f"Enhanced therapeutic session created: {session.session_id}")
            return session

        except Exception as e:
            logger.error(f"Error creating enhanced session: {e}")
            raise

    def process_therapeutic_interaction(
        self,
        session_id: str,
        user_input: str,
        narrative_context: NarrativeContext,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """
        Process a therapeutic interaction with enhanced effectiveness tracking.

        Args:
            session_id: ID of the therapeutic session
            user_input: User's input text
            narrative_context: Current narrative context
            session_state: Current session state

        Returns:
            Dict containing enhanced therapeutic response and effectiveness data
        """
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session not found: {session_id}")

            session = self.active_sessions[session_id]

            # Step 1: Detect therapeutic opportunities with enhanced analysis
            opportunities = self._detect_enhanced_opportunities(
                user_input, narrative_context, session_state
            )

            # Step 2: Select optimal evidence-based intervention
            selected_intervention = self._select_optimal_intervention(
                opportunities, session_state, session.therapeutic_goals
            )

            # Step 3: Generate clinically validated dialogue
            dialogue_response = self._generate_enhanced_dialogue(
                selected_intervention, narrative_context, session_state
            )

            # Step 4: Apply professional oversight if needed
            oversight_result = self._apply_professional_oversight(
                dialogue_response, selected_intervention, session_state
            )

            # Step 5: Track effectiveness metrics
            effectiveness_data = self._track_interaction_effectiveness(
                session, selected_intervention, dialogue_response, oversight_result
            )

            # Step 6: Update session tracking
            self._update_session_tracking(
                session, selected_intervention, dialogue_response
            )

            # Compile comprehensive response
            enhanced_response = {
                "therapeutic_content": dialogue_response["dialogue_content"],
                "intervention_used": selected_intervention,
                "dialogue_metadata": dialogue_response,
                "professional_oversight": oversight_result,
                "effectiveness_prediction": effectiveness_data[
                    "predicted_effectiveness"
                ],
                "therapeutic_value": effectiveness_data["therapeutic_value"],
                "clinical_validation": dialogue_response.get(
                    "clinical_validation", "pending"
                ),
                "evidence_level": (
                    selected_intervention.evidence_level.value
                    if selected_intervention
                    else "unknown"
                ),
                "session_progress": self._calculate_session_progress(session),
                "recommendations": effectiveness_data.get("recommendations", []),
                "monitoring_points": dialogue_response.get("monitoring_points", []),
                "next_steps": effectiveness_data.get("next_steps", []),
            }

            return enhanced_response

        except Exception as e:
            logger.error(f"Error processing therapeutic interaction: {e}")
            return self._generate_error_response(str(e))

    def _detect_enhanced_opportunities(
        self,
        user_input: str,
        narrative_context: NarrativeContext,
        session_state: SessionState,
    ) -> list[dict[str, Any]]:
        """Detect therapeutic opportunities using enhanced analysis."""
        # Use existing content integration for opportunity detection
        basic_opportunities = self.content_integration.detect_therapeutic_opportunities(
            {
                "user_input": user_input,
                "narrative_context": narrative_context,
                "session_state": session_state,
            }
        )

        # Enhance opportunities with evidence-based analysis
        enhanced_opportunities = []
        for opportunity in basic_opportunities:
            enhanced_opportunity = {
                "basic_opportunity": opportunity,
                "evidence_based_interventions": self._map_to_evidence_based_interventions(
                    opportunity
                ),
                "clinical_priority": self._assess_clinical_priority(
                    opportunity, session_state
                ),
                "safety_considerations": self._assess_safety_considerations(
                    opportunity, session_state
                ),
            }
            enhanced_opportunities.append(enhanced_opportunity)

        return enhanced_opportunities

    def _select_optimal_intervention(
        self,
        opportunities: list[dict[str, Any]],
        session_state: SessionState,
        therapeutic_goals: list[str],
    ) -> EvidenceBasedIntervention | None:
        """Select the optimal evidence-based intervention."""
        if not opportunities:
            return None

        # Extract presenting concerns from opportunities
        presenting_concerns = []
        for opp in opportunities:
            basic_opp = opp.get("basic_opportunity", {})
            if "presenting_concern" in basic_opp:
                presenting_concerns.append(basic_opp["presenting_concern"])

        # Get emotional state
        emotional_state = "neutral"
        if session_state.emotional_state:
            emotional_state = session_state.emotional_state.primary_emotion.value

        # Create session context
        session_context = {
            "therapeutic_goals": therapeutic_goals,
            "emotional_intensity": (
                getattr(session_state.emotional_state, "intensity", 0.5)
                if session_state.emotional_state
                else 0.5
            ),
        }

        # Select intervention using evidence-based engine
        selected_intervention = self.intervention_engine.get_appropriate_intervention(
            presenting_concerns=presenting_concerns,
            emotional_state=emotional_state,
            session_context=session_context,
        )

        return selected_intervention

    def _generate_enhanced_dialogue(
        self,
        intervention: EvidenceBasedIntervention | None,
        narrative_context: NarrativeContext,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """Generate enhanced therapeutic dialogue."""
        if not intervention:
            # Fallback to basic supportive dialogue
            return {
                "dialogue_content": "I'm here to support you. Can you tell me more about what you're experiencing?",
                "therapeutic_value": 0.6,
                "clinical_validation": "basic_approved",
                "evidence_level": "clinical_consensus",
            }

        # Prepare client context for dialogue generation
        client_context = {
            "presenting_concerns": [intervention.name],
            "emotional_state": (
                session_state.emotional_state.primary_emotion.value
                if session_state.emotional_state
                else "neutral"
            ),
            "emotional_intensity": (
                getattr(session_state.emotional_state, "intensity", 0.5)
                if session_state.emotional_state
                else 0.5
            ),
            "narrative_context": (
                " ".join(narrative_context.recent_events)
                if narrative_context.recent_events
                else ""
            ),
        }

        # Generate dialogue using enhanced dialogue engine
        dialogue_response = self.dialogue_engine.generate_clinically_validated_dialogue(
            dialogue_type=intervention.therapeutic_approach.value,
            client_context=client_context,
            therapeutic_goals=[intervention.name],
            safety_level="safe",
        )

        return dialogue_response

    def _apply_professional_oversight(
        self,
        dialogue_response: dict[str, Any],
        intervention: EvidenceBasedIntervention | None,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """Apply professional oversight to therapeutic content."""
        oversight_result = {
            "oversight_applied": False,
            "supervision_required": False,
            "content_review_required": False,
            "safety_assessment": "safe",
            "professional_recommendations": [],
        }

        # Check if professional oversight is needed
        if self._requires_professional_oversight(
            dialogue_response, intervention, session_state
        ):
            oversight_result["oversight_applied"] = True

            # Determine type of oversight needed
            if self._requires_crisis_consultation(session_state):
                oversight_result["supervision_required"] = True
                oversight_result["supervision_type"] = "crisis_consultation"
                oversight_result["urgency_level"] = "crisis"
            elif self._requires_case_consultation(intervention, session_state):
                oversight_result["supervision_required"] = True
                oversight_result["supervision_type"] = "case_consultation"
                oversight_result["urgency_level"] = "normal"

            # Check if content review is needed
            if self._requires_content_review(dialogue_response, intervention):
                oversight_result["content_review_required"] = True
                oversight_result["review_priority"] = "normal"

        return oversight_result

    def _track_interaction_effectiveness(
        self,
        session: EnhancedTherapeuticSession,
        intervention: EvidenceBasedIntervention | None,
        dialogue_response: dict[str, Any],
        oversight_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Track effectiveness metrics for the interaction."""
        effectiveness_data = {
            "predicted_effectiveness": 0.7,  # Default
            "therapeutic_value": 0.7,
            "evidence_strength": 0.5,
            "clinical_validation_score": 0.8,
            "professional_oversight_score": 0.7,
            "recommendations": [],
            "next_steps": [],
        }

        # Calculate predicted effectiveness
        if intervention:
            effectiveness_data["predicted_effectiveness"] = (
                intervention.effectiveness_rating
            )
            effectiveness_data["evidence_strength"] = self._map_evidence_level_to_score(
                intervention.evidence_level
            )

        # Get therapeutic value from dialogue
        effectiveness_data["therapeutic_value"] = dialogue_response.get(
            "therapeutic_value", 0.7
        )

        # Calculate clinical validation score
        validation_result = dialogue_response.get("validation_result", {})
        effectiveness_data["clinical_validation_score"] = validation_result.get(
            "clinical_appropriateness", 0.8
        )

        # Calculate professional oversight score
        if oversight_result["oversight_applied"]:
            effectiveness_data["professional_oversight_score"] = 0.9

        # Generate recommendations
        effectiveness_data["recommendations"] = (
            self._generate_effectiveness_recommendations(
                effectiveness_data, intervention, dialogue_response
            )
        )

        return effectiveness_data

    def _update_session_tracking(
        self,
        session: EnhancedTherapeuticSession,
        intervention: EvidenceBasedIntervention | None,
        dialogue_response: dict[str, Any],
    ) -> None:
        """Update session tracking with interaction data."""
        # Add intervention to session
        if intervention:
            intervention_data = {
                "intervention_id": intervention.intervention_id,
                "intervention_name": intervention.name,
                "evidence_level": intervention.evidence_level.value,
                "effectiveness_prediction": intervention.effectiveness_rating,
            }
            session.add_intervention(intervention_data)

        # Add dialogue exchange to session
        dialogue_data = {
            "dialogue_type": dialogue_response.get("template_used", "general"),
            "therapeutic_value": dialogue_response.get("therapeutic_value", 0.0),
            "clinical_validation": dialogue_response.get(
                "clinical_validation", "pending"
            ),
        }
        session.add_dialogue_exchange(dialogue_data)

    def _calculate_session_progress(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Calculate current session progress metrics."""
        progress = {
            "interventions_attempted": len(session.interventions_used),
            "dialogue_exchanges": len(session.dialogue_exchanges),
            "average_therapeutic_value": 0.0,
            "session_duration_minutes": 0,
            "goals_addressed": 0,
            "total_goals": len(session.therapeutic_goals),
        }

        # Calculate average therapeutic value
        if session.dialogue_exchanges:
            therapeutic_values = [
                exchange.get("therapeutic_value", 0.0)
                for exchange in session.dialogue_exchanges
            ]
            progress["average_therapeutic_value"] = statistics.mean(therapeutic_values)

        # Calculate session duration
        if session.session_start_time:
            duration = datetime.now() - session.session_start_time
            progress["session_duration_minutes"] = duration.total_seconds() / 60

        return progress

    def complete_session_with_effectiveness_analysis(
        self, session_id: str
    ) -> dict[str, Any]:
        """Complete session and provide comprehensive effectiveness analysis."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session not found: {session_id}")

            session = self.active_sessions[session_id]
            session.complete_session()

            # Move to session history
            self.session_history[session_id] = session
            del self.active_sessions[session_id]

            # Generate comprehensive effectiveness analysis
            effectiveness_analysis = self._generate_effectiveness_analysis(session)

            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                session
            )

            # Compile final session report
            session_report = {
                "session_id": session_id,
                "session_duration": (
                    session.session_end_time - session.session_start_time
                ).total_seconds()
                / 60,
                "effectiveness_metrics": (
                    session.effectiveness_metrics.__dict__
                    if session.effectiveness_metrics
                    else {}
                ),
                "effectiveness_analysis": effectiveness_analysis,
                "optimization_recommendations": optimization_recommendations,
                "interventions_summary": self._summarize_interventions(session),
                "dialogue_quality_summary": self._summarize_dialogue_quality(session),
                "professional_oversight_summary": self._summarize_professional_oversight(
                    session
                ),
                "next_session_recommendations": self._generate_next_session_recommendations(
                    session
                ),
            }

            logger.info(f"Session completed with effectiveness analysis: {session_id}")
            return session_report

        except Exception as e:
            logger.error(f"Error completing session with effectiveness analysis: {e}")
            return {"error": str(e), "session_id": session_id}

    def get_system_effectiveness_metrics(self) -> dict[str, Any]:
        """Get overall system effectiveness metrics."""
        try:
            # Collect metrics from all completed sessions
            all_sessions = list(self.session_history.values())

            if not all_sessions:
                return {
                    "overall_effectiveness_score": 0.0,
                    "total_sessions": 0,
                    "message": "No completed sessions available for analysis",
                }

            # Calculate aggregate metrics
            effectiveness_scores = []
            intervention_success_rates = []
            dialogue_quality_scores = []
            professional_oversight_scores = []

            for session in all_sessions:
                if session.effectiveness_metrics:
                    metrics = session.effectiveness_metrics
                    effectiveness_scores.append(metrics.overall_effectiveness_score)
                    intervention_success_rates.append(
                        metrics.calculate_intervention_success_rate()
                    )
                    dialogue_quality_scores.append(metrics.dialogue_quality_score)
                    professional_oversight_scores.append(
                        metrics.professional_oversight_score
                    )

            # Calculate system-wide metrics
            system_metrics = {
                "overall_effectiveness_score": (
                    statistics.mean(effectiveness_scores)
                    if effectiveness_scores
                    else 0.0
                ),
                "intervention_success_rate": (
                    statistics.mean(intervention_success_rates)
                    if intervention_success_rates
                    else 0.0
                ),
                "dialogue_quality_score": (
                    statistics.mean(dialogue_quality_scores)
                    if dialogue_quality_scores
                    else 0.0
                ),
                "professional_oversight_score": (
                    statistics.mean(professional_oversight_scores)
                    if professional_oversight_scores
                    else 0.0
                ),
                "total_sessions_analyzed": len(all_sessions),
                "total_interventions": sum(
                    len(s.interventions_used) for s in all_sessions
                ),
                "total_dialogue_exchanges": sum(
                    len(s.dialogue_exchanges) for s in all_sessions
                ),
                "average_session_duration": (
                    statistics.mean(
                        [
                            (s.session_end_time - s.session_start_time).total_seconds()
                            / 60
                            for s in all_sessions
                            if s.session_end_time
                        ]
                    )
                    if all_sessions
                    else 0.0
                ),
                "effectiveness_trend": self._calculate_effectiveness_trend(
                    all_sessions
                ),
            }

            # Add improvement recommendations based on the calculated metrics
            system_metrics["improvement_recommendations"] = (
                self._generate_system_improvement_recommendations(system_metrics)
            )

            return system_metrics

        except Exception as e:
            logger.error(f"Error calculating system effectiveness metrics: {e}")
            return {"error": str(e), "overall_effectiveness_score": 0.0}

    # Helper methods for internal processing
    def _map_to_evidence_based_interventions(
        self, opportunity: dict[str, Any]
    ) -> list[str]:
        """Map therapeutic opportunity to evidence-based interventions."""
        # Simplified mapping - in production, this would be more sophisticated
        opportunity_type = opportunity.get("type", "general")

        mapping = {
            "anxiety": [
                "mindfulness_based_intervention",
                "cognitive_restructuring_cbt",
            ],
            "depression": ["behavioral_activation", "cognitive_restructuring_cbt"],
            "trauma": ["grounding_technique_trauma"],
            "general": ["cognitive_restructuring_cbt"],
        }

        return mapping.get(opportunity_type, ["cognitive_restructuring_cbt"])

    def _assess_clinical_priority(
        self, opportunity: dict[str, Any], session_state: SessionState
    ) -> str:
        """Assess clinical priority of therapeutic opportunity."""
        # Check for crisis indicators
        if (
            "crisis" in str(opportunity).lower()
            or "suicide" in str(opportunity).lower()
        ):
            return "crisis"

        # Check emotional intensity
        if (
            session_state.emotional_state
            and session_state.emotional_state.intensity > 0.8
        ):
            return "high"

        return "normal"

    def _assess_safety_considerations(
        self, opportunity: dict[str, Any], session_state: SessionState
    ) -> list[str]:
        """Assess safety considerations for therapeutic opportunity."""
        safety_considerations = []

        # Check for crisis indicators
        if "crisis" in str(opportunity).lower():
            safety_considerations.append("Crisis intervention protocols required")

        # Check for trauma indicators
        if "trauma" in str(opportunity).lower():
            safety_considerations.append("Trauma-informed approach required")

        return safety_considerations

    def _requires_professional_oversight(
        self,
        dialogue_response: dict[str, Any],
        intervention: EvidenceBasedIntervention | None,
        session_state: SessionState,
    ) -> bool:
        """Determine if professional oversight is required."""
        # Always require oversight for crisis situations
        if self._requires_crisis_consultation(session_state):
            return True

        # Require oversight for complex interventions
        if intervention and intervention.evidence_level.value in ["level_1", "level_2"]:
            return True

        # Require oversight for low therapeutic value
        if dialogue_response.get("therapeutic_value", 1.0) < 0.6:
            return True

        return False

    def _requires_crisis_consultation(self, session_state: SessionState) -> bool:
        """Determine if crisis consultation is required."""
        # Check for crisis indicators in session state
        # This is a simplified check - in production, this would be more comprehensive
        return False  # Placeholder

    def _requires_case_consultation(
        self,
        intervention: EvidenceBasedIntervention | None,
        session_state: SessionState,
    ) -> bool:
        """Determine if case consultation is required."""
        # Require consultation for complex cases
        if intervention and len(intervention.contraindications) > 2:
            return True

        return False

    def _requires_content_review(
        self,
        dialogue_response: dict[str, Any],
        intervention: EvidenceBasedIntervention | None,
    ) -> bool:
        """Determine if content review is required."""
        # Require review for new or unvalidated content
        if dialogue_response.get("clinical_validation") == "pending":
            return True

        return False

    def _map_evidence_level_to_score(self, evidence_level) -> float:
        """Map evidence level to numerical score."""
        evidence_scores = {
            "level_1": 1.0,
            "level_2": 0.9,
            "level_3": 0.8,
            "level_4": 0.7,
            "level_5": 0.6,
            "level_6": 0.5,
            "level_7": 0.4,
        }
        return evidence_scores.get(
            (
                evidence_level.value
                if hasattr(evidence_level, "value")
                else str(evidence_level)
            ),
            0.4,
        )

    def _generate_effectiveness_recommendations(
        self,
        effectiveness_data: dict[str, Any],
        intervention: EvidenceBasedIntervention | None,
        dialogue_response: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations for improving effectiveness."""
        recommendations = []

        if effectiveness_data["predicted_effectiveness"] < 0.7:
            recommendations.append("Consider using higher evidence-level interventions")

        if effectiveness_data["therapeutic_value"] < 0.6:
            recommendations.append("Enhance dialogue quality and therapeutic content")

        if effectiveness_data["professional_oversight_score"] < 0.8:
            recommendations.append("Increase professional supervision and oversight")

        return recommendations

    def _generate_effectiveness_analysis(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Generate comprehensive effectiveness analysis for session."""
        if not session.effectiveness_metrics:
            return {"error": "No effectiveness metrics available"}

        metrics = session.effectiveness_metrics

        analysis = {
            "overall_assessment": self._assess_overall_effectiveness(
                metrics.overall_effectiveness_score
            ),
            "strengths": self._identify_session_strengths(session),
            "areas_for_improvement": self._identify_improvement_areas(session),
            "evidence_base_quality": self._assess_evidence_base_quality(session),
            "therapeutic_relationship_quality": self._assess_therapeutic_relationship(
                session
            ),
            "intervention_effectiveness": self._assess_intervention_effectiveness(
                session
            ),
            "professional_standards_compliance": self._assess_professional_compliance(
                session
            ),
        }

        return analysis

    def _generate_optimization_recommendations(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Generate optimization recommendations based on session analysis."""
        if not session.effectiveness_metrics:
            return {"recommendations": ["Complete effectiveness metrics collection"]}

        current_scores = {
            "overall_effectiveness": session.effectiveness_metrics.overall_effectiveness_score,
            "intervention_success": session.effectiveness_metrics.intervention_success_score,
            "dialogue_quality": session.effectiveness_metrics.dialogue_quality_score,
            "professional_oversight": session.effectiveness_metrics.professional_oversight_score,
        }

        # Use effectiveness optimizer to generate recommendations
        optimization_plan = (
            self.effectiveness_optimizer.optimize_therapeutic_effectiveness(
                current_scores, target_score=0.80
            )
        )

        return optimization_plan

    def _generate_error_response(self, error_message: str) -> dict[str, Any]:
        """Generate error response for therapeutic interactions."""
        return {
            "therapeutic_content": "I'm here to support you. If you're having thoughts of hurting yourself, please call 988 for the National Suicide Prevention Lifeline.",
            "error": error_message,
            "therapeutic_value": 0.5,
            "clinical_validation": "emergency_fallback",
            "evidence_level": "crisis_protocol",
            "recommendations": [
                "Manual review required",
                "Professional consultation recommended",
            ],
            "monitoring_points": [
                "Assess client safety",
                "Ensure professional support available",
            ],
        }

    # Additional helper methods for analysis and reporting
    def _assess_overall_effectiveness(self, score: float) -> str:
        """Assess overall effectiveness level."""
        if score >= 0.9:
            return "Excellent - Exceeds clinical standards"
        elif score >= 0.8:
            return "Good - Meets clinical standards"
        elif score >= 0.7:
            return "Satisfactory - Approaching clinical standards"
        elif score >= 0.6:
            return "Needs Improvement - Below clinical standards"
        else:
            return "Poor - Significant improvement required"

    def _identify_session_strengths(
        self, session: EnhancedTherapeuticSession
    ) -> list[str]:
        """Identify strengths in the therapeutic session."""
        strengths = []

        if session.effectiveness_metrics:
            metrics = session.effectiveness_metrics

            if metrics.evidence_base_score >= 0.8:
                strengths.append("Strong evidence-based intervention usage")

            if metrics.dialogue_quality_score >= 0.8:
                strengths.append("High-quality therapeutic dialogue")

            if metrics.professional_oversight_score >= 0.8:
                strengths.append("Appropriate professional oversight")

            if metrics.calculate_intervention_success_rate() >= 0.8:
                strengths.append("High intervention success rate")

        return strengths if strengths else ["Session completed successfully"]

    def _identify_improvement_areas(
        self, session: EnhancedTherapeuticSession
    ) -> list[str]:
        """Identify areas for improvement in the therapeutic session."""
        improvements = []

        if session.effectiveness_metrics:
            metrics = session.effectiveness_metrics

            if metrics.evidence_base_score < 0.7:
                improvements.append("Increase use of evidence-based interventions")

            if metrics.dialogue_quality_score < 0.7:
                improvements.append("Enhance therapeutic dialogue quality")

            if metrics.professional_oversight_score < 0.7:
                improvements.append("Increase professional supervision and oversight")

            if metrics.calculate_intervention_success_rate() < 0.7:
                improvements.append(
                    "Improve intervention implementation and follow-through"
                )

        return improvements if improvements else ["Continue current high standards"]

    def _assess_evidence_base_quality(self, session: EnhancedTherapeuticSession) -> str:
        """Assess quality of evidence base for interventions used."""
        if not session.interventions_used:
            return "No interventions to assess"

        evidence_levels = [
            intervention.get("evidence_level", "level_7")
            for intervention in session.interventions_used
        ]

        level_1_count = evidence_levels.count("level_1")
        level_2_count = evidence_levels.count("level_2")

        if level_1_count > len(evidence_levels) * 0.5:
            return (
                "Excellent - Primarily systematic review/meta-analysis level evidence"
            )
        elif (level_1_count + level_2_count) > len(evidence_levels) * 0.5:
            return "Good - Primarily RCT and systematic review level evidence"
        else:
            return "Needs improvement - Consider higher evidence-level interventions"

    def _assess_therapeutic_relationship(
        self, session: EnhancedTherapeuticSession
    ) -> str:
        """Assess quality of therapeutic relationship."""
        if not session.dialogue_exchanges:
            return "Insufficient data for assessment"

        avg_therapeutic_value = statistics.mean(
            [
                exchange.get("therapeutic_value", 0.0)
                for exchange in session.dialogue_exchanges
            ]
        )

        if avg_therapeutic_value >= 0.8:
            return "Strong therapeutic relationship evident"
        elif avg_therapeutic_value >= 0.6:
            return "Good therapeutic relationship developing"
        else:
            return "Therapeutic relationship needs strengthening"

    def _assess_intervention_effectiveness(
        self, session: EnhancedTherapeuticSession
    ) -> str:
        """Assess effectiveness of interventions used."""
        if not session.effectiveness_metrics:
            return "Effectiveness metrics not available"

        success_rate = (
            session.effectiveness_metrics.calculate_intervention_success_rate()
        )

        if success_rate >= 0.8:
            return "High intervention effectiveness"
        elif success_rate >= 0.6:
            return "Moderate intervention effectiveness"
        else:
            return "Intervention effectiveness needs improvement"

    def _assess_professional_compliance(
        self, session: EnhancedTherapeuticSession
    ) -> str:
        """Assess compliance with professional standards."""
        compliance_score = 0.7  # Base compliance

        if session.professional_consultations:
            compliance_score += 0.1

        if session.content_reviews:
            compliance_score += 0.1

        if (
            session.clinical_supervision_required
            and len(session.professional_consultations) > 0
        ):
            compliance_score += 0.1

        if compliance_score >= 0.9:
            return "Excellent professional standards compliance"
        elif compliance_score >= 0.8:
            return "Good professional standards compliance"
        else:
            return "Professional standards compliance needs improvement"

    def _summarize_interventions(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Summarize interventions used in the session."""
        return {
            "total_interventions": len(session.interventions_used),
            "evidence_levels": [
                i.get("evidence_level") for i in session.interventions_used
            ],
            "average_effectiveness_prediction": (
                statistics.mean(
                    [
                        i.get("effectiveness_prediction", 0.0)
                        for i in session.interventions_used
                    ]
                )
                if session.interventions_used
                else 0.0
            ),
        }

    def _summarize_dialogue_quality(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Summarize dialogue quality metrics."""
        return {
            "total_exchanges": len(session.dialogue_exchanges),
            "average_therapeutic_value": (
                statistics.mean(
                    [
                        e.get("therapeutic_value", 0.0)
                        for e in session.dialogue_exchanges
                    ]
                )
                if session.dialogue_exchanges
                else 0.0
            ),
            "clinical_validations": [
                e.get("clinical_validation") for e in session.dialogue_exchanges
            ],
        }

    def _summarize_professional_oversight(
        self, session: EnhancedTherapeuticSession
    ) -> dict[str, Any]:
        """Summarize professional oversight activities."""
        return {
            "consultations_requested": len(session.professional_consultations),
            "content_reviews_completed": len(session.content_reviews),
            "supervision_required": session.clinical_supervision_required,
            "quality_assurance_completed": session.quality_assurance_completed,
        }

    def _generate_next_session_recommendations(
        self, session: EnhancedTherapeuticSession
    ) -> list[str]:
        """Generate recommendations for next therapeutic session."""
        recommendations = []

        if session.effectiveness_metrics:
            if session.effectiveness_metrics.overall_effectiveness_score < 0.7:
                recommendations.append(
                    "Focus on evidence-based interventions in next session"
                )

            if session.effectiveness_metrics.dialogue_quality_score < 0.7:
                recommendations.append("Enhance therapeutic dialogue techniques")

            if (
                len(session.therapeutic_goals)
                > session.effectiveness_metrics.therapeutic_goals_achieved
            ):
                recommendations.append(
                    "Continue working on unachieved therapeutic goals"
                )

        recommendations.append(
            "Monitor client progress and adjust interventions as needed"
        )

        return recommendations

    def _calculate_effectiveness_trend(
        self, sessions: list[EnhancedTherapeuticSession]
    ) -> str:
        """Calculate effectiveness trend across sessions."""
        if len(sessions) < 2:
            return "Insufficient data for trend analysis"

        # Sort sessions by start time
        sorted_sessions = sorted(sessions, key=lambda s: s.session_start_time)

        # Get effectiveness scores
        scores = [
            s.effectiveness_metrics.overall_effectiveness_score
            for s in sorted_sessions
            if s.effectiveness_metrics
        ]

        if len(scores) < 2:
            return "Insufficient effectiveness data for trend analysis"

        # Simple trend calculation
        recent_avg = statistics.mean(scores[-3:])  # Last 3 sessions
        earlier_avg = statistics.mean(scores[:-3]) if len(scores) > 3 else scores[0]

        if recent_avg > earlier_avg + 0.05:
            return "Improving effectiveness trend"
        elif recent_avg < earlier_avg - 0.05:
            return "Declining effectiveness trend"
        else:
            return "Stable effectiveness trend"

    def _generate_system_improvement_recommendations(
        self, system_metrics: dict[str, Any]
    ) -> list[str]:
        """Generate system-wide improvement recommendations."""
        recommendations = []

        if system_metrics["overall_effectiveness_score"] < 0.8:
            recommendations.append(
                "Implement system-wide effectiveness improvement program"
            )

        if system_metrics["intervention_success_rate"] < 0.7:
            recommendations.append(
                "Enhance intervention selection and implementation protocols"
            )

        if system_metrics["dialogue_quality_score"] < 0.7:
            recommendations.append(
                "Improve therapeutic dialogue training and templates"
            )

        if system_metrics["professional_oversight_score"] < 0.8:
            recommendations.append(
                "Increase professional supervision and oversight frequency"
            )

        return (
            recommendations if recommendations else ["Maintain current high standards"]
        )
