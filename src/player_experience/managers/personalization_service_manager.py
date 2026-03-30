"""

# Logseq: [[TTA.dev/Player_experience/Managers/Personalization_service_manager]]
Therapeutic personalization and adaptation management.

This module provides comprehensive therapeutic personalization services,
extending the existing PersonalizationEngine with player-specific features,
real-time adaptation, and crisis detection capabilities.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..models.enums import CrisisType
from ..models.session import Recommendation
from ..models.therapeutic_settings import (
    EnhancedTherapeuticSettings,
    SettingsConflict,
    TherapeuticPreferencesValidator,
)

logger = logging.getLogger(__name__)

# Import from TTA prototype (with fallback for testing)
try:
    import os
    import sys

    prototype_path = os.path.join(  # noqa: PTH118
        os.path.dirname(__file__),  # noqa: PTH120
        "..",
        "..",
        "..",
        "tta.prototype",
        "core",  # noqa: PTH120
    )
    if prototype_path not in sys.path:
        sys.path.append(prototype_path)
    from personalization_engine import (  # type: ignore[import-not-found]
        PersonalizationEngine,
    )
    from progress_based_therapeutic_adaptation import (  # type: ignore[import-not-found]
        ProgressBasedTherapeuticAdaptation,
    )
except (ImportError, NameError, ModuleNotFoundError) as e:
    # Fallback for testing - create mock classes
    logger.warning(
        f"Could not import TTA prototype components: {e}. Using mock implementations."
    )

    class PersonalizationEngine:
        def __init__(self, llm_client=None):
            self.llm_client = llm_client

        def personalize_content(
            self, user_id, content, session_state, profile, progress=None
        ):
            return {
                "adapted_content": content,
                "recommendations": [],
                "adaptation_info": {
                    "type": "mock",
                    "rationale": "Mock adaptation for testing",
                    "confidence": 0.5,
                },
            }

    class ProgressBasedTherapeuticAdaptation:
        def __init__(self, llm_client=None):
            self.llm_client = llm_client

        def adapt_therapeutic_content(self, user_id, content, progress_data):
            return {"adapted_content": content, "adaptations": []}


@dataclass
class PlayerFeedback:
    """Represents feedback from a player about their therapeutic experience."""

    feedback_id: str
    player_id: str
    session_id: str
    feedback_type: str  # "rating", "text", "preference_change", "crisis_indicator"
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False

    def __post_init__(self):
        """Validate feedback after initialization."""
        if not self.feedback_id:
            self.feedback_id = str(uuid.uuid4())


@dataclass
class AdaptationResult:
    """Result of therapeutic adaptation based on player feedback."""

    adaptation_id: str
    player_id: str
    changes_made: list[str]
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    requires_player_approval: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate adaptation result after initialization."""
        if not self.adaptation_id:
            self.adaptation_id = str(uuid.uuid4())

        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")


@dataclass
class CrisisSupportResource:
    """Represents a crisis support resource."""

    resource_id: str
    name: str
    description: str
    contact_method: str  # "phone", "text", "chat", "website"
    contact_info: str
    availability: str  # "24/7", "business_hours", "specific_times"
    crisis_types: list[CrisisType]
    priority: int = 1  # 1 (highest) to 5 (lowest)
    is_emergency: bool = False

    def __post_init__(self):
        """Validate crisis support resource after initialization."""
        if not 1 <= self.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")


class CrisisDetectionSystem:
    """Handles crisis detection and emergency response."""

    def __init__(self):
        """Initialize the crisis detection system."""
        self.crisis_keywords = {
            CrisisType.SUICIDAL_IDEATION: [
                "suicide",
                "kill myself",
                "end it all",
                "not worth living",
                "better off dead",
                "want to die",
                "end my life",
            ],
            CrisisType.SELF_HARM: [
                "hurt myself",
                "cut myself",
                "self harm",
                "self-harm",
                "cutting",
                "burning myself",
                "punish myself",
            ],
            CrisisType.PANIC_ATTACK: [
                "can't breathe",
                "heart racing",
                "panic attack",
                "losing control",
                "going crazy",
                "chest pain",
                "dizzy",
                "hyperventilating",
            ],
            CrisisType.SEVERE_DEPRESSION: [
                "hopeless",
                "worthless",
                "nothing matters",
                "can't go on",
                "empty inside",
                "numb",
                "no point",
                "give up",
            ],
            CrisisType.TRAUMA_RESPONSE: [
                "flashback",
                "nightmare",
                "triggered",
                "reliving",
                "can't stop thinking",
                "haunted",
                "traumatized",
            ],
        }

        self.crisis_resources = self._initialize_crisis_resources()

    def _initialize_crisis_resources(self) -> list[CrisisSupportResource]:
        """Initialize default crisis support resources."""
        return [
            CrisisSupportResource(
                resource_id="988_lifeline",
                name="988 Suicide & Crisis Lifeline",
                description="Free and confidential emotional support 24/7",
                contact_method="phone",
                contact_info="988",
                availability="24/7",
                crisis_types=[
                    CrisisType.SUICIDAL_IDEATION,
                    CrisisType.SEVERE_DEPRESSION,
                ],
                priority=1,
                is_emergency=True,
            ),
            CrisisSupportResource(
                resource_id="crisis_text_line",
                name="Crisis Text Line",
                description="Free, 24/7 support via text message",
                contact_method="text",
                contact_info="Text HOME to 741741",
                availability="24/7",
                crisis_types=[
                    CrisisType.SUICIDAL_IDEATION,
                    CrisisType.SELF_HARM,
                    CrisisType.PANIC_ATTACK,
                ],
                priority=1,
                is_emergency=True,
            ),
            CrisisSupportResource(
                resource_id="emergency_services",
                name="Emergency Services",
                description="Immediate emergency response",
                contact_method="phone",
                contact_info="911",
                availability="24/7",
                crisis_types=[CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM],
                priority=1,
                is_emergency=True,
            ),
            CrisisSupportResource(
                resource_id="nami_helpline",
                name="NAMI HelpLine",
                description="Information, referrals and support for mental health",
                contact_method="phone",
                contact_info="1-800-950-NAMI (6264)",
                availability="Monday-Friday 10am-10pm ET",
                crisis_types=[
                    CrisisType.SEVERE_DEPRESSION,
                    CrisisType.GENERAL_DISTRESS,
                ],
                priority=2,
            ),
            CrisisSupportResource(
                resource_id="samhsa_helpline",
                name="SAMHSA National Helpline",
                description="Treatment referral and information service",
                contact_method="phone",
                contact_info="1-800-662-HELP (4357)",
                availability="24/7",
                crisis_types=[CrisisType.SUBSTANCE_ABUSE, CrisisType.GENERAL_DISTRESS],
                priority=2,
            ),
        ]

    def detect_crisis_indicators(
        self, text: str, context: dict[str, Any]
    ) -> tuple[bool, list[CrisisType], float]:
        """
        Detect crisis indicators in text and context.

        Returns:
            Tuple of (crisis_detected, crisis_types, confidence_score)
        """
        text_lower = text.lower()
        detected_types = []
        confidence_scores = []

        # Keyword-based detection
        for crisis_type, keywords in self.crisis_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                detected_types.append(crisis_type)
                # Calculate confidence based on number of matches and keyword specificity
                confidence = min(0.9, matches * 0.3 + 0.1)
                confidence_scores.append(confidence)

        # Context-based detection
        if context:
            # Check for emotional state indicators
            emotional_state = context.get("emotional_state", {})
            if emotional_state:
                distress_level = emotional_state.get("distress_level", 0.0)
                if distress_level > 0.8:
                    detected_types.append(CrisisType.GENERAL_DISTRESS)
                    confidence_scores.append(distress_level)

            # Check for behavioral indicators
            behavioral_indicators = context.get("behavioral_indicators", [])
            crisis_behaviors = [
                "withdrawal",
                "agitation",
                "sleep_disruption",
                "appetite_changes",
            ]
            if any(behavior in behavioral_indicators for behavior in crisis_behaviors):
                detected_types.append(CrisisType.SEVERE_DEPRESSION)
                confidence_scores.append(0.6)

        # Calculate overall confidence
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        crisis_detected = len(detected_types) > 0 and overall_confidence > 0.3

        return crisis_detected, list(set(detected_types)), overall_confidence

    def get_crisis_resources(
        self, crisis_types: list[CrisisType], emergency_only: bool = False
    ) -> list[CrisisSupportResource]:
        """Get appropriate crisis support resources for given crisis types."""
        relevant_resources = []

        for resource in self.crisis_resources:
            # Filter by emergency status if requested
            if emergency_only and not resource.is_emergency:
                continue

            # Check if resource handles any of the crisis types
            if any(
                crisis_type in resource.crisis_types for crisis_type in crisis_types
            ):
                relevant_resources.append(resource)

        # Sort by priority (1 = highest priority)
        relevant_resources.sort(key=lambda r: r.priority)

        return relevant_resources


class PersonalizationServiceManager:
    """
    Manages therapeutic personalization and adaptation.

    Extends the existing PersonalizationEngine with player-specific features,
    real-time adaptation based on feedback, and crisis detection capabilities.
    """

    def __init__(self, llm_client=None):
        """Initialize the Personalization Service Manager."""
        self.personalization_engine = PersonalizationEngine(llm_client)
        self.progress_adapter = ProgressBasedTherapeuticAdaptation(llm_client)
        self.settings_validator = TherapeuticPreferencesValidator()
        self.crisis_detector = CrisisDetectionSystem()

        # Storage for adaptation history (in production, this would be database-backed)
        self.adaptation_history: dict[str, list[AdaptationResult]] = {}
        self.feedback_history: dict[str, list[PlayerFeedback]] = {}

        logger.info("PersonalizationServiceManager initialized")

    def update_therapeutic_settings(
        self, player_id: str, settings: EnhancedTherapeuticSettings
    ) -> tuple[bool, list[SettingsConflict]]:
        """
        Update therapeutic settings for a player with validation.

        Args:
            player_id: The player's unique identifier
            settings: The new therapeutic settings

        Returns:
            Tuple of (success, conflicts_list)
        """
        try:
            # Validate settings
            is_valid, conflicts = self.settings_validator.validate_settings(settings)

            if not is_valid:
                # Try to auto-resolve all conflicts (including critical ones)
                resolved_settings = settings
                resolved_any = False

                for conflict in conflicts:
                    if conflict.auto_resolvable and conflict.resolution_options:
                        try:
                            resolved_settings = (
                                self.settings_validator.resolve_conflict(
                                    resolved_settings,
                                    conflict,
                                    conflict.resolution_options[0],
                                )
                            )
                            logger.info(
                                f"Auto-resolved conflict {conflict.conflict_id} for player {player_id}"
                            )
                            resolved_any = True
                        except Exception as e:
                            logger.error(
                                f"Failed to auto-resolve conflict {conflict.conflict_id}: {e}"
                            )

                # Re-validate after resolution
                if resolved_any:
                    is_valid, remaining_conflicts = (
                        self.settings_validator.validate_settings(resolved_settings)
                    )
                    if is_valid:
                        settings = resolved_settings
                        conflicts = remaining_conflicts
                    else:
                        # Check if there are still critical unresolvable conflicts
                        critical_unresolvable = [
                            c
                            for c in remaining_conflicts
                            if c.severity == "critical" and not c.auto_resolvable
                        ]
                        if critical_unresolvable:
                            logger.warning(
                                f"Critical unresolvable conflicts found in settings for player {player_id}"
                            )
                            return False, remaining_conflicts
                        # Non-critical conflicts remaining, but settings are usable
                        settings = resolved_settings
                        conflicts = remaining_conflicts
                else:
                    # No conflicts were resolvable, check if any are critical
                    critical_conflicts = [
                        c for c in conflicts if c.severity == "critical"
                    ]
                    if critical_conflicts:
                        logger.warning(
                            f"Critical conflicts found in settings for player {player_id}"
                        )
                        return False, conflicts

            # Store settings (in production, this would save to database)
            logger.info(f"Therapeutic settings updated for player {player_id}")
            return True, conflicts

        except Exception as e:
            logger.error(
                f"Error updating therapeutic settings for player {player_id}: {e}"
            )
            return False, []

    def get_adaptive_recommendations(
        self, player_id: str, context: dict[str, Any] | None = None
    ) -> list[Recommendation]:
        """
        Generate adaptive recommendations based on player behavior and progress.

        Args:
            player_id: The player's unique identifier
            context: Optional context information

        Returns:
            List of personalized recommendations
        """
        try:
            recommendations = []

            # Get adaptation history for this player
            player_adaptations = self.adaptation_history.get(player_id, [])
            player_feedback = self.feedback_history.get(player_id, [])

            # Generate recommendations based on recent feedback
            if player_feedback:
                recent_feedback = [
                    f
                    for f in player_feedback
                    if f.timestamp > datetime.now() - timedelta(days=7)
                ]

                # Analyze feedback patterns
                if recent_feedback:
                    recommendations.extend(
                        self._generate_feedback_based_recommendations(
                            player_id, recent_feedback
                        )
                    )

            # Generate recommendations based on adaptation patterns
            if player_adaptations:
                recent_adaptations = [
                    a
                    for a in player_adaptations
                    if a.timestamp > datetime.now() - timedelta(days=14)
                ]

                if recent_adaptations:
                    recommendations.extend(
                        self._generate_adaptation_based_recommendations(
                            player_id, recent_adaptations
                        )
                    )

            # Generate contextual recommendations
            if context:
                recommendations.extend(
                    self._generate_contextual_recommendations(player_id, context)
                )

            # Sort by priority and limit results
            recommendations.sort(key=lambda r: r.priority)
            return recommendations[:5]  # Return top 5 recommendations

        except Exception as e:
            logger.error(
                f"Error generating adaptive recommendations for player {player_id}: {e}"
            )
            return []

    def process_feedback(
        self, player_id: str, feedback: PlayerFeedback
    ) -> AdaptationResult:
        """
        Process player feedback and adapt therapeutic experience accordingly.

        Args:
            player_id: The player's unique identifier
            feedback: The feedback to process

        Returns:
            Result of the adaptation process
        """
        try:
            # Store feedback
            if player_id not in self.feedback_history:
                self.feedback_history[player_id] = []
            self.feedback_history[player_id].append(feedback)

            # Process different types of feedback
            changes_made = []
            confidence_score = 0.5
            reasoning = ""
            requires_approval = False

            if feedback.feedback_type == "rating":
                changes_made, confidence_score, reasoning = (
                    self._process_rating_feedback(feedback)
                )
            elif feedback.feedback_type == "text":
                changes_made, confidence_score, reasoning = self._process_text_feedback(
                    feedback
                )
            elif feedback.feedback_type == "preference_change":
                changes_made, confidence_score, reasoning = (
                    self._process_preference_feedback(feedback)
                )
                requires_approval = True
            elif feedback.feedback_type == "crisis_indicator":
                changes_made, confidence_score, reasoning = (
                    self._process_crisis_feedback(feedback)
                )
                requires_approval = False  # Crisis adaptations are automatic

            # Create adaptation result
            adaptation_result = AdaptationResult(
                adaptation_id=str(uuid.uuid4()),
                player_id=player_id,
                changes_made=changes_made,
                confidence_score=confidence_score,
                reasoning=reasoning,
                requires_player_approval=requires_approval,
            )

            # Store adaptation result
            if player_id not in self.adaptation_history:
                self.adaptation_history[player_id] = []
            self.adaptation_history[player_id].append(adaptation_result)

            # Mark feedback as processed
            feedback.processed = True

            logger.info(
                f"Processed feedback {feedback.feedback_id} for player {player_id}"
            )
            return adaptation_result

        except Exception as e:
            logger.error(f"Error processing feedback for player {player_id}: {e}")
            return AdaptationResult(
                adaptation_id=str(uuid.uuid4()),
                player_id=player_id,
                changes_made=[],
                confidence_score=0.0,
                reasoning=f"Error processing feedback: {e}",
                requires_player_approval=True,
            )

    def get_crisis_support_resources(
        self,
        player_id: str,
        crisis_types: list[CrisisType] | None = None,
        emergency_only: bool = False,
    ) -> list[CrisisSupportResource]:
        """
        Get crisis support resources for a player.

        Args:
            player_id: The player's unique identifier
            crisis_types: Specific crisis types to get resources for
            emergency_only: Whether to return only emergency resources

        Returns:
            List of relevant crisis support resources
        """
        try:
            if crisis_types is None:
                # If no specific crisis types, return general resources
                crisis_types = [CrisisType.GENERAL_DISTRESS]

            resources = self.crisis_detector.get_crisis_resources(
                crisis_types, emergency_only
            )

            logger.info(
                f"Retrieved {len(resources)} crisis support resources for player {player_id}"
            )
            return resources

        except Exception as e:
            logger.error(
                f"Error getting crisis support resources for player {player_id}: {e}"
            )
            return []

    def detect_crisis_situation(
        self, player_id: str, text: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, list[CrisisType], list[CrisisSupportResource]]:
        """
        Detect crisis situation and provide immediate resources.

        Args:
            player_id: The player's unique identifier
            text: Text to analyze for crisis indicators
            context: Optional context information

        Returns:
            Tuple of (crisis_detected, crisis_types, emergency_resources)
        """
        try:
            # Detect crisis indicators
            crisis_detected, crisis_types, confidence = (
                self.crisis_detector.detect_crisis_indicators(text, context or {})
            )

            emergency_resources = []

            if crisis_detected:
                logger.warning(
                    f"Crisis detected for player {player_id}: {crisis_types} (confidence: {confidence:.2f})"
                )

                # Get emergency resources
                emergency_resources = self.crisis_detector.get_crisis_resources(
                    crisis_types, emergency_only=True
                )

                # Create crisis feedback for adaptation
                crisis_feedback = PlayerFeedback(
                    feedback_id=str(uuid.uuid4()),
                    player_id=player_id,
                    session_id="",  # May not have session context
                    feedback_type="crisis_indicator",
                    content={
                        "crisis_types": [ct.value for ct in crisis_types],
                        "confidence": confidence,
                        "text_analyzed": text,
                        "context": context,
                    },
                )

                # Process crisis feedback for immediate adaptation
                self.process_feedback(player_id, crisis_feedback)

            return crisis_detected, crisis_types, emergency_resources

        except Exception as e:
            logger.error(
                f"Error detecting crisis situation for player {player_id}: {e}"
            )
            return False, [], []

    def _generate_feedback_based_recommendations(
        self, player_id: str, feedback_list: list[PlayerFeedback]
    ) -> list[Recommendation]:
        """Generate recommendations based on recent feedback patterns."""
        recommendations = []

        # Analyze feedback patterns
        rating_feedback = [f for f in feedback_list if f.feedback_type == "rating"]
        text_feedback = [f for f in feedback_list if f.feedback_type == "text"]

        # Low ratings suggest need for adjustment
        if rating_feedback:
            avg_rating = sum(f.content.get("rating", 3) for f in rating_feedback) / len(
                rating_feedback
            )
            if avg_rating < 3:
                recommendations.append(
                    Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title="Adjust Therapeutic Intensity",
                        description="Recent ratings suggest the current approach may be too intense. Consider reducing intensity or trying a gentler approach.",
                        recommendation_type="therapeutic_adjustment",
                        priority=2,
                        reasoning="Low average rating in recent sessions",
                    )
                )

        # Analyze text feedback for common themes
        if text_feedback:
            # Simple keyword analysis (in production, this would use NLP)
            all_text = " ".join(
                f.content.get("text", "") for f in text_feedback
            ).lower()

            if "too fast" in all_text or "overwhelming" in all_text:
                recommendations.append(
                    Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title="Slow Down Pacing",
                        description="Feedback indicates the pacing may be too fast. Consider extending session duration or reducing content density.",
                        recommendation_type="pacing_adjustment",
                        priority=2,
                        reasoning="Player feedback indicates pacing issues",
                    )
                )

            if "boring" in all_text or "not engaging" in all_text:
                recommendations.append(
                    Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title="Increase Engagement",
                        description="Consider adding more interactive elements or trying different therapeutic approaches to increase engagement.",
                        recommendation_type="engagement_improvement",
                        priority=3,
                        reasoning="Player feedback indicates low engagement",
                    )
                )

        return recommendations

    def _generate_adaptation_based_recommendations(
        self, player_id: str, adaptations: list[AdaptationResult]
    ) -> list[Recommendation]:
        """Generate recommendations based on adaptation patterns."""
        recommendations = []

        # Look for patterns in adaptations
        successful_adaptations = [a for a in adaptations if a.confidence_score > 0.7]
        failed_adaptations = [a for a in adaptations if a.confidence_score < 0.3]

        if len(failed_adaptations) > len(successful_adaptations):
            recommendations.append(
                Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    title="Review Therapeutic Approach",
                    description="Recent adaptations have had mixed results. Consider consulting with a therapeutic professional to review the current approach.",
                    recommendation_type="professional_consultation",
                    priority=1,
                    reasoning="Pattern of low-confidence adaptations detected",
                )
            )

        return recommendations

    def _generate_contextual_recommendations(
        self, player_id: str, context: dict[str, Any]
    ) -> list[Recommendation]:
        """Generate recommendations based on current context."""
        recommendations = []

        # Check for time-based recommendations
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            recommendations.append(
                Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    title="Consider Session Timing",
                    description="Late night or early morning sessions may affect therapeutic effectiveness. Consider scheduling during regular hours.",
                    recommendation_type="scheduling_suggestion",
                    priority=4,
                    reasoning="Session occurring outside optimal hours",
                )
            )

        # Check for emotional state recommendations
        emotional_state = context.get("emotional_state", {})
        if emotional_state:
            stress_level = emotional_state.get("stress_level", 0.0)
            if stress_level > 0.8:
                recommendations.append(
                    Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title="Stress Management Focus",
                        description="High stress levels detected. Consider focusing on stress reduction techniques in upcoming sessions.",
                        recommendation_type="therapeutic_focus",
                        priority=2,
                        reasoning="High stress level detected in current context",
                    )
                )

        return recommendations

    def _process_rating_feedback(
        self, feedback: PlayerFeedback
    ) -> tuple[list[str], float, str]:
        """Process rating-based feedback."""
        rating = feedback.content.get("rating", 3)
        changes_made = []
        confidence_score = 0.6
        reasoning = f"Based on rating of {rating}/5"

        if rating <= 2:
            changes_made = ["reduce_intensity", "increase_support"]
            confidence_score = 0.8
            reasoning += " - Low rating suggests need for gentler approach"
        elif rating >= 4:
            changes_made = ["maintain_current_approach"]
            confidence_score = 0.9
            reasoning += " - High rating suggests current approach is effective"

        return changes_made, confidence_score, reasoning

    def _process_text_feedback(
        self, feedback: PlayerFeedback
    ) -> tuple[list[str], float, str]:
        """Process text-based feedback."""
        text = feedback.content.get("text", "").lower()
        changes_made = []
        confidence_score = 0.5
        reasoning = "Based on text feedback analysis"

        # Simple keyword-based analysis
        if "helpful" in text or "good" in text:
            changes_made = ["maintain_current_approach"]
            confidence_score = 0.7
        elif "difficult" in text or "hard" in text:
            changes_made = ["reduce_difficulty", "increase_support"]
            confidence_score = 0.6
        elif "boring" in text:
            changes_made = ["increase_engagement", "vary_approaches"]
            confidence_score = 0.7

        return changes_made, confidence_score, reasoning

    def _process_preference_feedback(
        self, feedback: PlayerFeedback
    ) -> tuple[list[str], float, str]:
        """Process preference change feedback."""
        changes = feedback.content.get("preference_changes", {})
        changes_made = [f"update_{key}" for key in changes]
        confidence_score = 0.9  # High confidence for explicit preference changes
        reasoning = "Direct preference change request from player"

        return changes_made, confidence_score, reasoning

    def _process_crisis_feedback(
        self, feedback: PlayerFeedback
    ) -> tuple[list[str], float, str]:
        """Process crisis indicator feedback."""
        crisis_types = feedback.content.get("crisis_types", [])
        changes_made = [
            "enable_crisis_monitoring",
            "reduce_intensity",
            "provide_support_resources",
        ]
        confidence_score = 1.0  # Maximum confidence for crisis situations
        reasoning = f"Crisis indicators detected: {', '.join(crisis_types)}"

        return changes_made, confidence_score, reasoning
