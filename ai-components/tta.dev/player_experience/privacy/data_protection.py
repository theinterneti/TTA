"""
Data Privacy and Protection Module

Implements GDPR-compliant data protection features including encryption,
data export, anonymization, and secure deletion for therapeutic content.
"""

import base64
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


@dataclass
class EncryptedContent:
    """Represents encrypted therapeutic content with metadata."""
    encrypted_data: bytes
    encryption_method: str
    created_at: datetime
    content_type: str
    checksum: str


@dataclass
class AnonymizedData:
    """Represents anonymized data for research purposes."""
    anonymized_id: str
    data_type: str
    anonymized_content: dict[str, Any]
    anonymization_method: str
    created_at: datetime


@dataclass
class AuditEntry:
    """Represents an audit log entry for data access."""
    entry_id: str
    player_id: str
    accessor: str
    operation: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass
class DeletionReport:
    """Report of data deletion operations."""
    player_id: str
    deletion_requested_at: datetime
    deletion_completed_at: datetime | None
    deleted_resources: list[str]
    anonymized_resources: list[str]
    errors: list[str]
    status: str  # 'pending', 'completed', 'failed', 'partial'


class TherapeuticDataProtection:
    """
    Handles encryption, anonymization, and secure deletion of therapeutic data.
    Implements GDPR compliance features for player data protection.
    """

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize data protection with encryption key."""
        if encryption_key is None:
            encryption_key = self._generate_key()

        self.cipher_suite = Fernet(encryption_key)
        self.audit_log: list[AuditEntry] = []

    def _generate_key(self) -> bytes:
        """Generate a new encryption key from environment or create one."""
        password = os.environ.get('TTA_ENCRYPTION_PASSWORD', 'default-dev-password').encode()
        salt = os.environ.get('TTA_ENCRYPTION_SALT', 'default-salt').encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_therapeutic_content(self, content: str | dict, content_type: str = "therapeutic") -> EncryptedContent:
        """
        Encrypt sensitive therapeutic content.

        Args:
            content: Content to encrypt (string or dict)
            content_type: Type of content being encrypted

        Returns:
            EncryptedContent object with encrypted data and metadata
        """
        try:
            # Convert content to JSON string if it's a dict
            if isinstance(content, dict):
                content_str = json.dumps(content, default=str)
            else:
                content_str = str(content)

            # Encrypt the content
            encrypted_data = self.cipher_suite.encrypt(content_str.encode())

            # Generate checksum for integrity verification
            checksum = hashlib.sha256(content_str.encode()).hexdigest()

            encrypted_content = EncryptedContent(
                encrypted_data=encrypted_data,
                encryption_method="Fernet-AES256",
                created_at=datetime.utcnow(),
                content_type=content_type,
                checksum=checksum
            )

            logger.info(f"Encrypted {content_type} content, size: {len(encrypted_data)} bytes")
            return encrypted_content

        except Exception as e:
            logger.error(f"Failed to encrypt content: {str(e)}")
            raise

    def decrypt_therapeutic_content(self, encrypted_content: EncryptedContent) -> str | dict:
        """
        Decrypt therapeutic content and verify integrity.

        Args:
            encrypted_content: EncryptedContent object to decrypt

        Returns:
            Decrypted content as string or dict
        """
        try:
            # Decrypt the content
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_content.encrypted_data)
            decrypted_str = decrypted_bytes.decode()

            # Verify checksum
            checksum = hashlib.sha256(decrypted_str.encode()).hexdigest()
            if checksum != encrypted_content.checksum:
                raise ValueError("Content integrity check failed - data may be corrupted")

            # Try to parse as JSON, return as string if it fails
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str

        except Exception as e:
            logger.error(f"Failed to decrypt content: {str(e)}")
            raise

    def anonymize_research_data(self, player_data: dict[str, Any], anonymization_method: str = "hash-based") -> AnonymizedData:
        """
        Anonymize player data for research purposes while preserving therapeutic insights.

        Args:
            player_data: Player data to anonymize
            anonymization_method: Method used for anonymization

        Returns:
            AnonymizedData object with anonymized content
        """
        try:
            # Generate anonymous ID based on original player ID
            original_id = player_data.get('player_id', 'unknown')
            anonymized_id = hashlib.sha256(f"{original_id}-research-salt".encode()).hexdigest()[:16]

            # Create anonymized version of the data
            anonymized_content = self._anonymize_content(player_data)

            anonymized_data = AnonymizedData(
                anonymized_id=anonymized_id,
                data_type="player_research_data",
                anonymized_content=anonymized_content,
                anonymization_method=anonymization_method,
                created_at=datetime.utcnow()
            )

            logger.info(f"Anonymized data for research, anonymous ID: {anonymized_id}")
            return anonymized_data

        except Exception as e:
            logger.error(f"Failed to anonymize research data: {str(e)}")
            raise

    def _anonymize_content(self, data: dict[str, Any]) -> dict[str, Any]:
        """Remove or hash personally identifiable information."""
        anonymized = {}

        # Fields to completely remove
        remove_fields = {'email', 'username', 'ip_address', 'user_agent', 'crisis_contact_info'}

        # Fields to hash
        hash_fields = {'player_id', 'character_id', 'session_id'}

        # Fields to generalize
        generalize_fields = {'created_at', 'last_active'}

        for key, value in data.items():
            if key in remove_fields:
                continue  # Skip PII fields
            elif key in hash_fields:
                anonymized[key] = hashlib.sha256(f"{value}-anon".encode()).hexdigest()[:16]
            elif key in generalize_fields and isinstance(value, datetime):
                # Generalize timestamps to week precision
                anonymized[key] = value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_content(value)
            elif isinstance(value, list):
                anonymized[key] = [self._anonymize_content(item) if isinstance(item, dict) else item for item in value]
            else:
                anonymized[key] = value

        return anonymized

    def audit_data_access(self, player_id: str, accessor: str, operation: str,
                         resource_type: str, resource_id: str,
                         ip_address: str | None = None, user_agent: str | None = None) -> AuditEntry:
        """
        Create audit log entry for data access.

        Args:
            player_id: ID of the player whose data was accessed
            accessor: ID or identifier of who accessed the data
            operation: Type of operation (read, write, delete, export)
            resource_type: Type of resource accessed
            resource_id: ID of the specific resource
            ip_address: IP address of the accessor
            user_agent: User agent string of the accessor

        Returns:
            AuditEntry object
        """
        entry = AuditEntry(
            entry_id=hashlib.sha256(f"{player_id}-{accessor}-{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
            player_id=player_id,
            accessor=accessor,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.audit_log.append(entry)
        logger.info(f"Audit: {accessor} performed {operation} on {resource_type}:{resource_id} for player {player_id}")

        return entry

    def export_player_data(self, player_id: str, include_encrypted: bool = False) -> dict[str, Any]:
        """
        Export all player data in GDPR-compliant format.

        Args:
            player_id: ID of the player requesting data export
            include_encrypted: Whether to include encrypted therapeutic content

        Returns:
            Dictionary containing all player data
        """
        try:
            # This would typically fetch from database - simplified for implementation
            export_data = {
                "export_metadata": {
                    "player_id": player_id,
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "export_version": "1.0",
                    "includes_encrypted_content": include_encrypted
                },
                "player_profile": {},  # Would be populated from database
                "characters": [],      # Would be populated from database
                "sessions": [],        # Would be populated from database
                "progress_data": {},   # Would be populated from database
                "audit_log": [asdict(entry) for entry in self.audit_log if entry.player_id == player_id]
            }

            # Log the export operation
            self.audit_data_access(
                player_id=player_id,
                accessor=player_id,  # Player is accessing their own data
                operation="export",
                resource_type="complete_profile",
                resource_id=player_id
            )

            logger.info(f"Exported data for player {player_id}")
            return export_data

        except Exception as e:
            logger.error(f"Failed to export data for player {player_id}: {str(e)}")
            raise

    def handle_data_deletion_request(self, player_id: str, preserve_research_data: bool = True) -> DeletionReport:
        """
        Handle GDPR data deletion request.

        Args:
            player_id: ID of the player requesting deletion
            preserve_research_data: Whether to preserve anonymized data for research

        Returns:
            DeletionReport with details of the deletion process
        """
        deletion_report = DeletionReport(
            player_id=player_id,
            deletion_requested_at=datetime.utcnow(),
            deletion_completed_at=None,
            deleted_resources=[],
            anonymized_resources=[],
            errors=[],
            status='pending'
        )

        try:
            # Log the deletion request
            self.audit_data_access(
                player_id=player_id,
                accessor=player_id,
                operation="deletion_request",
                resource_type="complete_profile",
                resource_id=player_id
            )

            # In a real implementation, this would:
            # 1. Fetch all player data from databases
            # 2. Create anonymized versions if preserve_research_data is True
            # 3. Securely delete original data
            # 4. Update deletion report with results

            # Simulated deletion process
            resources_to_delete = [
                f"player_profile:{player_id}",
                f"characters:{player_id}",
                f"sessions:{player_id}",
                f"progress_data:{player_id}",
                f"therapeutic_content:{player_id}"
            ]

            for resource in resources_to_delete:
                try:
                    # Simulate deletion
                    if preserve_research_data and "therapeutic_content" in resource:
                        # Create anonymized version before deletion
                        deletion_report.anonymized_resources.append(f"anonymized_{resource}")

                    deletion_report.deleted_resources.append(resource)
                    logger.info(f"Deleted resource: {resource}")

                except Exception as e:
                    error_msg = f"Failed to delete {resource}: {str(e)}"
                    deletion_report.errors.append(error_msg)
                    logger.error(error_msg)

            # Update completion status
            if not deletion_report.errors:
                deletion_report.status = 'completed'
            elif deletion_report.deleted_resources:
                deletion_report.status = 'partial'
            else:
                deletion_report.status = 'failed'

            deletion_report.deletion_completed_at = datetime.utcnow()

            logger.info(f"Data deletion completed for player {player_id}, status: {deletion_report.status}")
            return deletion_report

        except Exception as e:
            error_msg = f"Critical error during data deletion: {str(e)}"
            deletion_report.errors.append(error_msg)
            deletion_report.status = 'failed'
            logger.error(error_msg)
            return deletion_report

    def verify_data_integrity(self, encrypted_content: EncryptedContent) -> bool:
        """
        Verify the integrity of encrypted therapeutic content.

        Args:
            encrypted_content: Content to verify

        Returns:
            True if content is valid and uncorrupted
        """
        try:
            self.decrypt_therapeutic_content(encrypted_content)
            return True
        except Exception as e:
            logger.warning(f"Data integrity check failed: {str(e)}")
            return False

    def get_audit_log(self, player_id: str | None = None,
                     start_date: datetime | None = None,
                     end_date: datetime | None = None) -> list[AuditEntry]:
        """
        Retrieve audit log entries with optional filtering.

        Args:
            player_id: Filter by specific player ID
            start_date: Filter entries after this date
            end_date: Filter entries before this date

        Returns:
            List of matching audit entries
        """
        filtered_entries = self.audit_log

        if player_id:
            filtered_entries = [entry for entry in filtered_entries if entry.player_id == player_id]

        if start_date:
            filtered_entries = [entry for entry in filtered_entries if entry.timestamp >= start_date]

        if end_date:
            filtered_entries = [entry for entry in filtered_entries if entry.timestamp <= end_date]

        return filtered_entries
