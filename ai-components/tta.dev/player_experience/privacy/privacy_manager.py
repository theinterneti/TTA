"""
Privacy Settings Manager

Manages player privacy preferences, consent tracking, and GDPR compliance features.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum

from .data_protection import TherapeuticDataProtection

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Types of consent that can be granted or revoked."""
    DATA_COLLECTION = "data_collection"
    THERAPEUTIC_ANALYSIS = "therapeutic_analysis"
    RESEARCH_PARTICIPATION = "research_participation"
    MARKETING_COMMUNICATIONS = "marketing_communications"
    THIRD_PARTY_SHARING = "third_party_sharing"
    ANALYTICS_TRACKING = "analytics_tracking"


class DataRetentionPeriod(Enum):
    """Data retention period options."""
    ONE_MONTH = 30
    THREE_MONTHS = 90
    SIX_MONTHS = 180
    ONE_YEAR = 365
    INDEFINITE = -1


@dataclass
class ConsentRecord:
    """Records consent given by a player."""
    consent_id: str
    player_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: datetime
    expires_at: datetime | None
    ip_address: str | None
    user_agent: str | None
    consent_version: str


@dataclass
class PrivacySettings:
    """Player's privacy settings and preferences."""
    player_id: str
    data_collection_consent: bool
    research_participation_consent: bool
    marketing_consent: bool
    analytics_consent: bool
    data_retention_period: DataRetentionPeriod
    allow_therapeutic_data_sharing: bool
    crisis_contact_sharing_allowed: bool
    export_format_preference: str  # 'json', 'csv', 'pdf'
    notification_preferences: dict[str, bool]
    created_at: datetime
    updated_at: datetime


@dataclass
class DataProcessingRecord:
    """Records data processing activities for transparency."""
    record_id: str
    player_id: str
    processing_purpose: str
    data_categories: list[str]
    legal_basis: str
    retention_period: int  # days
    third_parties: list[str]
    created_at: datetime


class PrivacyManager:
    """
    Manages player privacy settings, consent tracking, and GDPR compliance.
    """

    def __init__(self, data_protection: TherapeuticDataProtection):
        """Initialize privacy manager with data protection service."""
        self.data_protection = data_protection
        self.consent_records: dict[str, list[ConsentRecord]] = {}
        self.privacy_settings: dict[str, PrivacySettings] = {}
        self.processing_records: dict[str, list[DataProcessingRecord]] = {}

    def create_privacy_settings(self, player_id: str,
                              initial_consents: dict[ConsentType, bool] | None = None) -> PrivacySettings:
        """
        Create initial privacy settings for a new player.

        Args:
            player_id: ID of the player
            initial_consents: Initial consent preferences

        Returns:
            PrivacySettings object
        """
        # Default privacy-first settings
        settings = PrivacySettings(
            player_id=player_id,
            data_collection_consent=initial_consents.get(ConsentType.DATA_COLLECTION, False) if initial_consents else False,
            research_participation_consent=initial_consents.get(ConsentType.RESEARCH_PARTICIPATION, False) if initial_consents else False,
            marketing_consent=initial_consents.get(ConsentType.MARKETING_COMMUNICATIONS, False) if initial_consents else False,
            analytics_consent=initial_consents.get(ConsentType.ANALYTICS_TRACKING, False) if initial_consents else False,
            data_retention_period=DataRetentionPeriod.ONE_YEAR,
            allow_therapeutic_data_sharing=False,
            crisis_contact_sharing_allowed=True,  # Default to true for safety
            export_format_preference='json',
            notification_preferences={
                'privacy_policy_updates': True,
                'data_processing_notifications': True,
                'consent_renewal_reminders': True,
                'security_alerts': True
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.privacy_settings[player_id] = settings

        # Record initial consent decisions
        if initial_consents:
            for consent_type, granted in initial_consents.items():
                self.record_consent(player_id, consent_type, granted)

        # Log privacy settings creation
        self.data_protection.audit_data_access(
            player_id=player_id,
            accessor="system",
            operation="create",
            resource_type="privacy_settings",
            resource_id=player_id
        )

        logger.info(f"Created privacy settings for player {player_id}")
        return settings

    def update_privacy_settings(self, player_id: str, updates: dict[str, any]) -> PrivacySettings:
        """
        Update player's privacy settings.

        Args:
            player_id: ID of the player
            updates: Dictionary of settings to update

        Returns:
            Updated PrivacySettings object
        """
        if player_id not in self.privacy_settings:
            raise ValueError(f"Privacy settings not found for player {player_id}")

        settings = self.privacy_settings[player_id]

        # Update settings
        for key, value in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        settings.updated_at = datetime.utcnow()

        # Log the update
        self.data_protection.audit_data_access(
            player_id=player_id,
            accessor=player_id,
            operation="update",
            resource_type="privacy_settings",
            resource_id=player_id
        )

        logger.info(f"Updated privacy settings for player {player_id}")
        return settings

    def record_consent(self, player_id: str, consent_type: ConsentType, granted: bool,
                      expires_at: datetime | None = None, ip_address: str | None = None,
                      user_agent: str | None = None) -> ConsentRecord:
        """
        Record consent decision by player.

        Args:
            player_id: ID of the player
            consent_type: Type of consent being recorded
            granted: Whether consent was granted or revoked
            expires_at: When consent expires (if applicable)
            ip_address: IP address of the player
            user_agent: User agent string

        Returns:
            ConsentRecord object
        """
        consent_record = ConsentRecord(
            consent_id=f"{player_id}-{consent_type.value}-{datetime.utcnow().timestamp()}",
            player_id=player_id,
            consent_type=consent_type,
            granted=granted,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_version="1.0"
        )

        if player_id not in self.consent_records:
            self.consent_records[player_id] = []

        self.consent_records[player_id].append(consent_record)

        # Log consent recording
        self.data_protection.audit_data_access(
            player_id=player_id,
            accessor=player_id,
            operation="consent_update",
            resource_type="consent_record",
            resource_id=consent_record.consent_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        logger.info(f"Recorded consent for player {player_id}: {consent_type.value} = {granted}")
        return consent_record

    def check_consent(self, player_id: str, consent_type: ConsentType) -> bool:
        """
        Check if player has given valid consent for a specific purpose.

        Args:
            player_id: ID of the player
            consent_type: Type of consent to check

        Returns:
            True if valid consent exists
        """
        if player_id not in self.consent_records:
            return False

        # Get the most recent consent record for this type
        relevant_consents = [
            record for record in self.consent_records[player_id]
            if record.consent_type == consent_type
        ]

        if not relevant_consents:
            return False

        # Get the most recent consent
        latest_consent = max(relevant_consents, key=lambda x: x.granted_at)

        # Check if consent is still valid
        if latest_consent.expires_at and latest_consent.expires_at < datetime.utcnow():
            return False

        return latest_consent.granted

    def get_expiring_consents(self, player_id: str, days_ahead: int = 30) -> list[ConsentRecord]:
        """
        Get consents that will expire within the specified number of days.

        Args:
            player_id: ID of the player
            days_ahead: Number of days to look ahead

        Returns:
            List of expiring consent records
        """
        if player_id not in self.consent_records:
            return []

        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

        expiring_consents = [
            record for record in self.consent_records[player_id]
            if record.expires_at and record.expires_at <= cutoff_date and record.granted
        ]

        return expiring_consents

    def create_processing_record(self, player_id: str, processing_purpose: str,
                               data_categories: list[str], legal_basis: str,
                               retention_period: int, third_parties: list[str] | None = None) -> DataProcessingRecord:
        """
        Create a record of data processing activity for transparency.

        Args:
            player_id: ID of the player
            processing_purpose: Purpose of data processing
            data_categories: Categories of data being processed
            legal_basis: Legal basis for processing (GDPR Article 6)
            retention_period: How long data will be retained (days)
            third_parties: List of third parties data is shared with

        Returns:
            DataProcessingRecord object
        """
        record = DataProcessingRecord(
            record_id=f"{player_id}-processing-{datetime.utcnow().timestamp()}",
            player_id=player_id,
            processing_purpose=processing_purpose,
            data_categories=data_categories,
            legal_basis=legal_basis,
            retention_period=retention_period,
            third_parties=third_parties or [],
            created_at=datetime.utcnow()
        )

        if player_id not in self.processing_records:
            self.processing_records[player_id] = []

        self.processing_records[player_id].append(record)

        logger.info(f"Created processing record for player {player_id}: {processing_purpose}")
        return record

    def generate_privacy_report(self, player_id: str) -> dict[str, any]:
        """
        Generate comprehensive privacy report for a player.

        Args:
            player_id: ID of the player

        Returns:
            Dictionary containing privacy information
        """
        report = {
            "player_id": player_id,
            "report_generated_at": datetime.utcnow().isoformat(),
            "privacy_settings": asdict(self.privacy_settings.get(player_id, {})),
            "consent_history": [
                asdict(record) for record in self.consent_records.get(player_id, [])
            ],
            "processing_activities": [
                asdict(record) for record in self.processing_records.get(player_id, [])
            ],
            "data_retention_info": self._get_retention_info(player_id),
            "third_party_sharing": self._get_third_party_info(player_id),
            "audit_summary": self._get_audit_summary(player_id)
        }

        # Log report generation
        self.data_protection.audit_data_access(
            player_id=player_id,
            accessor=player_id,
            operation="privacy_report",
            resource_type="privacy_data",
            resource_id=player_id
        )

        return report

    def _get_retention_info(self, player_id: str) -> dict[str, any]:
        """Get data retention information for a player."""
        settings = self.privacy_settings.get(player_id)
        if not settings:
            return {}

        retention_days = settings.data_retention_period.value
        if retention_days == -1:
            retention_description = "Data retained indefinitely until deletion requested"
        else:
            deletion_date = settings.created_at + timedelta(days=retention_days)
            retention_description = f"Data will be automatically deleted on {deletion_date.isoformat()}"

        return {
            "retention_period_days": retention_days,
            "retention_description": retention_description,
            "automatic_deletion_enabled": retention_days != -1
        }

    def _get_third_party_info(self, player_id: str) -> dict[str, any]:
        """Get third-party data sharing information."""
        processing_records = self.processing_records.get(player_id, [])

        all_third_parties = set()
        for record in processing_records:
            all_third_parties.update(record.third_parties)

        return {
            "third_parties_with_access": list(all_third_parties),
            "sharing_purposes": [
                {
                    "purpose": record.processing_purpose,
                    "third_parties": record.third_parties,
                    "legal_basis": record.legal_basis
                }
                for record in processing_records if record.third_parties
            ]
        }

    def _get_audit_summary(self, player_id: str) -> dict[str, any]:
        """Get audit log summary for a player."""
        audit_entries = self.data_protection.get_audit_log(player_id=player_id)

        operation_counts = {}
        for entry in audit_entries:
            operation_counts[entry.operation] = operation_counts.get(entry.operation, 0) + 1

        return {
            "total_access_events": len(audit_entries),
            "operation_breakdown": operation_counts,
            "last_access": max([entry.timestamp for entry in audit_entries]).isoformat() if audit_entries else None,
            "unique_accessors": len({entry.accessor for entry in audit_entries})
        }

    def handle_subject_access_request(self, player_id: str) -> dict[str, any]:
        """
        Handle GDPR Subject Access Request (Article 15).

        Args:
            player_id: ID of the player making the request

        Returns:
            Complete data package for the player
        """
        # Generate privacy report
        privacy_report = self.generate_privacy_report(player_id)

        # Export all player data
        player_data = self.data_protection.export_player_data(player_id, include_encrypted=False)

        # Combine into comprehensive response
        sar_response = {
            "subject_access_request": {
                "player_id": player_id,
                "request_processed_at": datetime.utcnow().isoformat(),
                "data_controller": "TTA Therapeutic Platform",
                "contact_info": "privacy@tta-platform.com"
            },
            "privacy_information": privacy_report,
            "personal_data": player_data,
            "rights_information": {
                "right_to_rectification": "You can update your data through your account settings",
                "right_to_erasure": "You can request data deletion through your privacy settings",
                "right_to_restrict_processing": "You can limit data processing through consent settings",
                "right_to_data_portability": "You can export your data in machine-readable format",
                "right_to_object": "You can object to processing through privacy settings"
            }
        }

        logger.info(f"Processed Subject Access Request for player {player_id}")
        return sar_response

    def schedule_data_retention_cleanup(self) -> list[str]:
        """
        Identify players whose data should be deleted based on retention settings.

        Returns:
            List of player IDs whose data should be cleaned up
        """
        cleanup_candidates = []
        current_time = datetime.utcnow()

        for player_id, settings in self.privacy_settings.items():
            if settings.data_retention_period == DataRetentionPeriod.INDEFINITE:
                continue

            retention_days = settings.data_retention_period.value
            deletion_date = settings.created_at + timedelta(days=retention_days)

            if current_time >= deletion_date:
                cleanup_candidates.append(player_id)

        logger.info(f"Identified {len(cleanup_candidates)} players for data retention cleanup")
        return cleanup_candidates
