"""
Real User Testing Integration for TTA Quality Evaluation

Provides framework for transitioning from simulated user profiles to actual
human participants with proper consent, privacy protection, and data collection.
"""

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """User consent status for research participation."""

    PENDING = "pending"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ParticipantType(Enum):
    """Type of research participant."""

    VOLUNTEER = "volunteer"
    RECRUITED = "recruited"
    BETA_TESTER = "beta_tester"
    CLINICAL_PARTICIPANT = "clinical_participant"


@dataclass
class ConsentRecord:
    """Record of user consent for research participation."""

    participant_id: str  # Anonymized ID
    consent_timestamp: datetime
    consent_version: str
    consent_status: ConsentStatus

    # Consent details
    data_collection_consent: bool = False
    session_recording_consent: bool = False
    analysis_consent: bool = False
    follow_up_consent: bool = False

    # Privacy settings
    anonymization_level: str = "full"  # "full", "partial", "minimal"
    data_retention_period_days: int = 365

    # Withdrawal information
    withdrawal_timestamp: datetime | None = None
    withdrawal_reason: str | None = None

    # Consent expiration
    expiration_timestamp: datetime | None = None


@dataclass
class AnonymizedParticipant:
    """Anonymized participant profile for research."""

    participant_id: str  # Hash-based anonymous ID
    participant_type: ParticipantType
    recruitment_date: datetime
    consent_record: ConsentRecord

    # Anonymized demographics (optional)
    age_range: str | None = None  # "18-25", "26-35", etc.
    gaming_experience_level: str | None = None  # "novice", "intermediate", "expert"
    tech_comfort_level: str | None = None  # "low", "medium", "high"

    # Research participation history
    sessions_completed: int = 0
    total_participation_time_minutes: int = 0
    last_session_date: datetime | None = None

    # Consent and privacy
    privacy_preferences: dict[str, Any] = field(default_factory=dict)

    # Research group assignment (for A/B testing)
    research_group: str | None = None

    def is_consent_valid(self) -> bool:
        """Check if participant consent is still valid."""
        if self.consent_record.consent_status != ConsentStatus.GRANTED:
            return False

        if self.consent_record.expiration_timestamp:
            return datetime.now() < self.consent_record.expiration_timestamp

        return True


@dataclass
class RealUserSession:
    """Real user testing session data."""

    session_id: str
    participant_id: str  # Anonymized
    start_timestamp: datetime
    scenario_name: str
    model_name: str
    session_type: str  # "individual", "comparative", "a_b_test"
    end_timestamp: datetime | None = None

    # Anonymized interaction data
    turn_count: int = 0
    user_responses: list[str] = field(default_factory=list)  # Anonymized
    system_responses: list[str] = field(default_factory=list)
    response_times: list[float] = field(default_factory=list)

    # Quality metrics (same as simulated)
    narrative_coherence_scores: list[float] = field(default_factory=list)
    world_consistency_scores: list[float] = field(default_factory=list)
    user_engagement_scores: list[float] = field(default_factory=list)

    # Real user specific metrics
    user_satisfaction_scores: list[float] = field(default_factory=list)
    user_feedback_sentiment: list[float] = field(default_factory=list)
    session_completion_rate: float = 0.0

    # Privacy and anonymization
    anonymization_applied: bool = True
    data_retention_expiry: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(days=365)
    )


class RealUserTestingFramework:
    """
    Framework for conducting real user testing with proper ethical guidelines,
    consent management, and privacy protection.
    """

    def __init__(self, config_path: str | None = None):
        """Initialize real user testing framework."""
        self.config_path = (
            config_path or "testing/configs/real_user_testing_config.yaml"
        )
        self.config = self._load_config()

        # Participant management
        self.participants: dict[str, AnonymizedParticipant] = {}
        self.active_sessions: dict[str, RealUserSession] = {}

        # Privacy and security
        self.anonymization_salt = self._generate_anonymization_salt()

        # Research protocols
        self.research_protocols = self._load_research_protocols()

        logger.info("RealUserTestingFramework initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load real user testing configuration."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded real user testing config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for real user testing."""
        return {
            "consent_management": {
                "consent_version": "1.0",
                "consent_expiry_days": 365,
                "minimum_age": 18,
                "require_explicit_consent": True,
            },
            "privacy_protection": {
                "anonymization_level": "full",
                "data_retention_days": 365,
                "automatic_deletion": True,
                "encryption_required": True,
            },
            "research_ethics": {
                "irb_approval_required": True,
                "participant_compensation": True,
                "right_to_withdraw": True,
                "data_sharing_restrictions": True,
            },
        }

    def _generate_anonymization_salt(self) -> str:
        """Generate salt for participant ID anonymization."""
        return str(uuid.uuid4())

    def _anonymize_participant_id(self, original_id: str) -> str:
        """Create anonymized participant ID."""
        combined = f"{original_id}_{self.anonymization_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _load_research_protocols(self) -> dict[str, Any]:
        """Load research protocols and ethical guidelines."""
        return {
            "informed_consent": {
                "required_elements": [
                    "purpose_of_research",
                    "procedures_involved",
                    "risks_and_benefits",
                    "confidentiality_measures",
                    "right_to_withdraw",
                    "contact_information",
                ],
                "consent_process": "explicit_opt_in",
            },
            "data_protection": {
                "anonymization_required": True,
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_controls": "role_based",
            },
            "participant_rights": {
                "right_to_withdraw": True,
                "right_to_data_deletion": True,
                "right_to_data_portability": True,
                "right_to_information": True,
            },
        }

    async def register_participant(
        self,
        original_id: str,
        participant_type: ParticipantType,
        consent_details: dict[str, Any],
    ) -> str:
        """
        Register new participant with proper consent and anonymization.

        Args:
            original_id: Original participant identifier (will be anonymized)
            participant_type: Type of participant
            consent_details: Consent information and preferences

        Returns:
            Anonymized participant ID
        """
        # Create anonymized ID
        participant_id = self._anonymize_participant_id(original_id)

        # Create consent record
        consent_record = ConsentRecord(
            participant_id=participant_id,
            consent_timestamp=datetime.now(),
            consent_version=self.config.get("consent_management", {}).get(
                "consent_version", "1.0"
            ),
            consent_status=ConsentStatus.GRANTED,
            data_collection_consent=consent_details.get("data_collection", False),
            session_recording_consent=consent_details.get("session_recording", False),
            analysis_consent=consent_details.get("analysis", False),
            follow_up_consent=consent_details.get("follow_up", False),
            anonymization_level=consent_details.get("anonymization_level", "full"),
            data_retention_period_days=consent_details.get("retention_days", 365),
            expiration_timestamp=datetime.now()
            + timedelta(
                days=self.config.get("consent_management", {}).get(
                    "consent_expiry_days", 365
                )
            ),
        )

        # Create anonymized participant
        participant = AnonymizedParticipant(
            participant_id=participant_id,
            participant_type=participant_type,
            recruitment_date=datetime.now(),
            age_range=consent_details.get("age_range"),
            gaming_experience_level=consent_details.get("gaming_experience"),
            tech_comfort_level=consent_details.get("tech_comfort"),
            consent_record=consent_record,
            privacy_preferences=consent_details.get("privacy_preferences", {}),
        )

        # Store participant
        self.participants[participant_id] = participant

        logger.info(
            f"Registered participant: {participant_id} (type: {participant_type})"
        )
        return participant_id

    async def start_user_session(
        self,
        participant_id: str,
        scenario_name: str,
        model_name: str,
        session_type: str = "individual",
    ) -> str | None:
        """
        Start real user testing session.

        Args:
            participant_id: Anonymized participant ID
            scenario_name: Name of scenario to test
            model_name: AI model to use
            session_type: Type of session

        Returns:
            Session ID if successful, None if failed
        """
        # Verify participant exists and has valid consent
        if participant_id not in self.participants:
            logger.error(f"Participant not found: {participant_id}")
            return None

        participant = self.participants[participant_id]
        if not participant.is_consent_valid():
            logger.error(f"Invalid consent for participant: {participant_id}")
            return None

        # Create session
        session_id = f"real_user_session_{uuid.uuid4().hex[:8]}"
        session = RealUserSession(
            session_id=session_id,
            participant_id=participant_id,
            start_timestamp=datetime.now(),
            scenario_name=scenario_name,
            model_name=model_name,
            session_type=session_type,
        )

        # Store active session
        self.active_sessions[session_id] = session

        logger.info(
            f"Started real user session: {session_id} for participant: {participant_id}"
        )
        return session_id

    async def record_user_interaction(
        self,
        session_id: str,
        user_input: str,
        system_response: str,
        response_time: float,
        quality_metrics: dict[str, float],
    ):
        """
        Record user interaction with proper anonymization.

        Args:
            session_id: Session identifier
            user_input: User's input (will be anonymized)
            system_response: System's response
            response_time: Response time in seconds
            quality_metrics: Quality assessment metrics
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session not found: {session_id}")
            return

        session = self.active_sessions[session_id]
        participant = self.participants[session.participant_id]

        # Apply anonymization based on consent level
        anonymized_input = self._anonymize_user_input(
            user_input, participant.consent_record.anonymization_level
        )

        # Record interaction
        session.turn_count += 1
        session.user_responses.append(anonymized_input)
        session.system_responses.append(system_response)
        session.response_times.append(response_time)

        # Record quality metrics
        session.narrative_coherence_scores.append(
            quality_metrics.get("narrative_coherence", 0.0)
        )
        session.world_consistency_scores.append(
            quality_metrics.get("world_consistency", 0.0)
        )
        session.user_engagement_scores.append(
            quality_metrics.get("user_engagement", 0.0)
        )

        # Record user-specific metrics if available
        if "user_satisfaction" in quality_metrics:
            session.user_satisfaction_scores.append(
                quality_metrics["user_satisfaction"]
            )
        if "feedback_sentiment" in quality_metrics:
            session.user_feedback_sentiment.append(
                quality_metrics["feedback_sentiment"]
            )

    def _anonymize_user_input(self, user_input: str, anonymization_level: str) -> str:
        """Anonymize user input based on privacy level."""
        if anonymization_level == "full":
            # Full anonymization - remove all potentially identifying information
            # This is a simplified implementation - real implementation would be more sophisticated
            anonymized = user_input.lower()
            # Remove common names, locations, etc. (would use NLP in real implementation)
            return f"[ANONYMIZED_INPUT_{len(anonymized)}_CHARS]"
        elif anonymization_level == "partial":
            # Partial anonymization - keep general content, remove specific identifiers
            return f"[PARTIALLY_ANONYMIZED]: {user_input[:50]}..."
        else:
            # Minimal anonymization - keep most content
            return user_input

    async def end_user_session(
        self, session_id: str, completion_status: str = "completed"
    ):
        """
        End user session and finalize data collection.

        Args:
            session_id: Session identifier
            completion_status: How the session ended
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session not found: {session_id}")
            return

        session = self.active_sessions[session_id]
        session.end_timestamp = datetime.now()

        # Calculate completion rate
        if session.turn_count > 0:
            # This would be calculated based on expected vs actual turns
            session.session_completion_rate = (
                1.0 if completion_status == "completed" else 0.8
            )

        # Update participant statistics
        participant = self.participants[session.participant_id]
        participant.sessions_completed += 1
        participant.last_session_date = datetime.now()

        if session.end_timestamp:
            session_duration = (
                session.end_timestamp - session.start_timestamp
            ).total_seconds() / 60
            participant.total_participation_time_minutes += int(session_duration)

        # Move session to completed sessions (would be stored in database)
        completed_session = self.active_sessions.pop(session_id)

        logger.info(f"Ended user session: {session_id} (status: {completion_status})")

        # Schedule data retention cleanup if needed
        await self._schedule_data_cleanup(completed_session)

    async def _schedule_data_cleanup(self, session: RealUserSession):
        """Schedule automatic data cleanup based on retention policies."""
        if session.data_retention_expiry <= datetime.now():
            # Data should be deleted immediately
            await self._delete_session_data(session.session_id)
        else:
            # Schedule future deletion (would use task scheduler in real implementation)
            logger.info(
                f"Scheduled data cleanup for session {session.session_id} at {session.data_retention_expiry}"
            )

    async def _delete_session_data(self, session_id: str):
        """Permanently delete session data for privacy compliance."""
        logger.info(f"Deleting session data: {session_id}")
        # In real implementation, this would securely delete all associated data

    async def withdraw_participant_consent(
        self, participant_id: str, reason: str | None = None
    ):
        """
        Handle participant consent withdrawal.

        Args:
            participant_id: Anonymized participant ID
            reason: Optional reason for withdrawal
        """
        if participant_id not in self.participants:
            logger.error(f"Participant not found: {participant_id}")
            return

        participant = self.participants[participant_id]
        participant.consent_record.consent_status = ConsentStatus.WITHDRAWN
        participant.consent_record.withdrawal_timestamp = datetime.now()
        participant.consent_record.withdrawal_reason = reason

        # End any active sessions for this participant
        active_participant_sessions = [
            session_id
            for session_id, session in self.active_sessions.items()
            if session.participant_id == participant_id
        ]

        for session_id in active_participant_sessions:
            await self.end_user_session(session_id, "consent_withdrawn")

        # Schedule data deletion if requested
        if participant.consent_record.data_collection_consent:
            await self._schedule_participant_data_deletion(participant_id)

        logger.info(f"Processed consent withdrawal for participant: {participant_id}")

    async def _schedule_participant_data_deletion(self, participant_id: str):
        """Schedule deletion of all data for a participant."""
        logger.info(f"Scheduling data deletion for participant: {participant_id}")
        # In real implementation, this would delete all associated data

    async def generate_anonymized_research_dataset(
        self,
        participants: list[str] | None = None,
        date_range: tuple[datetime, datetime] | None = None,
    ) -> dict[str, Any]:
        """
        Generate anonymized dataset for research analysis.

        Args:
            participants: Specific participants to include (None for all)
            date_range: Date range for sessions to include

        Returns:
            Anonymized research dataset
        """
        dataset = {
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "anonymization_level": "full",
                "participant_count": 0,
                "session_count": 0,
            },
            "participants": [],
            "sessions": [],
            "aggregate_metrics": {},
        }

        # Filter participants
        target_participants = participants or list(self.participants.keys())
        valid_participants = [
            p_id
            for p_id in target_participants
            if p_id in self.participants
            and self.participants[p_id].consent_record.analysis_consent
        ]

        dataset["metadata"]["participant_count"] = len(valid_participants)

        # Add anonymized participant data
        for participant_id in valid_participants:
            participant = self.participants[participant_id]
            dataset["participants"].append(
                {
                    "participant_id": participant_id,  # Already anonymized
                    "participant_type": participant.participant_type.value,
                    "age_range": participant.age_range,
                    "gaming_experience": participant.gaming_experience_level,
                    "tech_comfort": participant.tech_comfort_level,
                    "sessions_completed": participant.sessions_completed,
                    "total_participation_time": participant.total_participation_time_minutes,
                }
            )

        # Add session data (would include completed sessions from database)
        # This is simplified - real implementation would query stored sessions

        logger.info(
            f"Generated anonymized research dataset with {len(valid_participants)} participants"
        )
        return dataset

    async def compare_real_vs_simulated_users(
        self, scenario_name: str, model_name: str
    ) -> dict[str, Any]:
        """
        Compare real user performance vs simulated user performance.

        Args:
            scenario_name: Scenario to compare
            model_name: Model to compare

        Returns:
            Comparison analysis
        """
        # This would compare metrics between real user sessions and simulated sessions
        comparison = {
            "scenario": scenario_name,
            "model": model_name,
            "real_user_metrics": {},
            "simulated_user_metrics": {},
            "differences": {},
            "insights": [],
        }

        # Implementation would analyze actual session data
        logger.info(f"Generated real vs simulated comparison for {scenario_name}")
        return comparison
