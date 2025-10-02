"""
Data privacy and protection service for GDPR compliance.

This service provides comprehensive data privacy features including encryption,
data export, deletion, anonymization, and compliance management.
"""

import hashlib
import io
import json
import secrets
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from cryptography.fernet import Fernet
from pydantic import BaseModel, Field


class DataCategory(str, Enum):
    """Categories of data for privacy management."""

    PERSONAL_IDENTIFIABLE = "personal_identifiable"
    THERAPEUTIC_CONTENT = "therapeutic_content"
    BEHAVIORAL_DATA = "behavioral_data"
    TECHNICAL_DATA = "technical_data"
    COMMUNICATION_DATA = "communication_data"
    PREFERENCE_DATA = "preference_data"


class ProcessingPurpose(str, Enum):
    """Legal purposes for data processing under GDPR."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataRetentionPeriod(str, Enum):
    """Standard data retention periods."""

    IMMEDIATE = "immediate"  # Delete immediately
    SHORT_TERM = "30_days"  # 30 days
    MEDIUM_TERM = "1_year"  # 1 year
    LONG_TERM = "7_years"  # 7 years (legal requirement)
    INDEFINITE = "indefinite"  # Keep indefinitely (with consent)


@dataclass
class DataProcessingRecord:
    """Record of data processing activities for GDPR compliance."""

    record_id: str
    user_id: str
    data_category: DataCategory
    processing_purpose: ProcessingPurpose
    legal_basis: str
    data_source: str
    recipients: list[str] = field(default_factory=list)
    retention_period: DataRetentionPeriod = DataRetentionPeriod.MEDIUM_TERM
    created_at: datetime = field(default_factory=datetime.utcnow)
    consent_given: bool = False
    consent_date: datetime | None = None
    is_sensitive: bool = False
    cross_border_transfer: bool = False
    automated_decision_making: bool = False


@dataclass
class EncryptedData:
    """Container for encrypted data with metadata."""

    encrypted_content: bytes
    encryption_method: str
    key_id: str
    created_at: datetime
    data_category: DataCategory
    is_sensitive: bool = True


class DataExportRequest(BaseModel):
    """Request for data export (GDPR Article 20)."""

    user_id: str
    export_format: str = Field(default="json", pattern="^(json|csv|xml)$")
    include_categories: list[DataCategory] = Field(
        default_factory=lambda: list(DataCategory)
    )
    include_deleted: bool = False
    anonymize_references: bool = True


class DataDeletionRequest(BaseModel):
    """Request for data deletion (GDPR Article 17)."""

    user_id: str
    deletion_reason: str
    categories_to_delete: list[DataCategory] = Field(
        default_factory=lambda: list(DataCategory)
    )
    preserve_anonymized: bool = True
    preserve_legal_obligations: bool = True
    immediate_deletion: bool = False


class ConsentRecord(BaseModel):
    """Record of user consent for data processing."""

    user_id: str
    consent_id: str
    purpose: ProcessingPurpose
    data_categories: list[DataCategory]
    consent_given: bool
    consent_date: datetime
    consent_method: str  # "explicit", "implicit", "opt_in", "opt_out"
    consent_evidence: str | None = None
    withdrawal_date: datetime | None = None
    is_active: bool = True


class PrivacySettings(BaseModel):
    """User privacy settings and preferences."""

    user_id: str
    data_minimization: bool = True
    purpose_limitation: bool = True
    storage_limitation: bool = True
    marketing_consent: bool = False
    analytics_consent: bool = True
    research_consent: bool = False
    third_party_sharing: bool = False
    data_retention_preference: DataRetentionPeriod = DataRetentionPeriod.MEDIUM_TERM
    notification_preferences: dict[str, bool] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EncryptionService:
    """Service for data encryption and decryption."""

    def __init__(self, master_key: bytes | None = None):
        """Initialize encryption service with master key."""
        if master_key is None:
            master_key = Fernet.generate_key()
        self.master_key = master_key
        self.fernet = Fernet(master_key)

        # In production, these would be stored securely
        self.encryption_keys: dict[str, bytes] = {}
        self.key_metadata: dict[str, dict[str, Any]] = {}

    def generate_data_key(self, key_id: str, purpose: str) -> bytes:
        """Generate a new data encryption key."""
        key = Fernet.generate_key()
        self.encryption_keys[key_id] = key
        self.key_metadata[key_id] = {
            "purpose": purpose,
            "created_at": datetime.utcnow(),
            "algorithm": "Fernet",
            "key_size": 256,
        }
        return key

    def encrypt_data(
        self, data: str | bytes, key_id: str, data_category: DataCategory
    ) -> EncryptedData:
        """Encrypt data with specified key."""
        if key_id not in self.encryption_keys:
            self.generate_data_key(key_id, f"encryption_{data_category.value}")

        key = self.encryption_keys[key_id]
        fernet = Fernet(key)

        if isinstance(data, str):
            data = data.encode("utf-8")

        encrypted_content = fernet.encrypt(data)

        return EncryptedData(
            encrypted_content=encrypted_content,
            encryption_method="Fernet",
            key_id=key_id,
            created_at=datetime.utcnow(),
            data_category=data_category,
            is_sensitive=data_category
            in [DataCategory.THERAPEUTIC_CONTENT, DataCategory.PERSONAL_IDENTIFIABLE],
        )

    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using stored key."""
        if encrypted_data.key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key {encrypted_data.key_id} not found")

        key = self.encryption_keys[encrypted_data.key_id]
        fernet = Fernet(key)

        return fernet.decrypt(encrypted_data.encrypted_content)

    def rotate_key(self, old_key_id: str, new_key_id: str) -> bool:
        """Rotate encryption key for enhanced security."""
        if old_key_id not in self.encryption_keys:
            return False

        # Generate new key
        self.generate_data_key(new_key_id, f"rotated_from_{old_key_id}")

        # In production, you would re-encrypt all data with the new key
        # For now, just mark the old key as deprecated
        self.key_metadata[old_key_id]["deprecated"] = True
        self.key_metadata[old_key_id]["deprecated_at"] = datetime.utcnow()

        return True


class AnonymizationService:
    """Service for data anonymization and pseudonymization."""

    def __init__(self):
        """Initialize anonymization service."""
        self.anonymization_mappings: dict[str, str] = {}
        self.pseudonym_mappings: dict[str, str] = {}

    def anonymize_user_id(self, user_id: str) -> str:
        """Create anonymous identifier for user."""
        if user_id not in self.anonymization_mappings:
            # Create deterministic but irreversible anonymous ID
            hash_input = f"anonymous_{user_id}_{secrets.token_hex(16)}"
            anonymous_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
            self.anonymization_mappings[user_id] = f"anon_{anonymous_id}"

        return self.anonymization_mappings[user_id]

    def pseudonymize_user_id(self, user_id: str) -> str:
        """Create pseudonymous identifier that can be reversed."""
        if user_id not in self.pseudonym_mappings:
            pseudonym = f"user_{hashlib.md5(user_id.encode()).hexdigest()[:12]}"
            self.pseudonym_mappings[user_id] = pseudonym

        return self.pseudonym_mappings[user_id]

    def anonymize_therapeutic_content(self, content: str) -> str:
        """Anonymize therapeutic content by removing/replacing PII."""
        # Simple anonymization - in production, use NLP techniques
        anonymized = content

        # Replace common PII patterns
        import re

        # Email addresses (do first to avoid conflicts)
        anonymized = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL]",
            anonymized,
        )

        # Phone numbers
        anonymized = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE]", anonymized)
        anonymized = re.sub(r"\(\d{3}\)\s*\d{3}-\d{4}", "[PHONE]", anonymized)

        # Addresses (do before names to avoid conflicts)
        anonymized = re.sub(
            r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b",
            "[ADDRESS]",
            anonymized,
            flags=re.IGNORECASE,
        )

        # Names (do last to avoid conflicts with addresses)
        anonymized = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[NAME]", anonymized)

        return anonymized

    def k_anonymize_dataset(
        self,
        dataset: list[dict[str, Any]],
        k: int = 5,
        quasi_identifiers: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Apply k-anonymity to dataset."""
        if quasi_identifiers is None:
            quasi_identifiers = ["age", "location", "gender"]

        # Simple k-anonymity implementation
        # In production, use more sophisticated algorithms
        anonymized_dataset = []

        for record in dataset:
            anonymized_record = record.copy()

            # Generalize quasi-identifiers
            for qi in quasi_identifiers:
                if qi in anonymized_record:
                    if qi == "age" and isinstance(anonymized_record[qi], int):
                        # Age ranges
                        age = anonymized_record[qi]
                        if age < 18:
                            anonymized_record[qi] = "under_18"
                        elif age < 30:
                            anonymized_record[qi] = "18_29"
                        elif age < 50:
                            anonymized_record[qi] = "30_49"
                        else:
                            anonymized_record[qi] = "50_plus"
                    elif qi == "location":
                        # Generalize to region/state level
                        anonymized_record[qi] = "region_generalized"

            anonymized_dataset.append(anonymized_record)

        return anonymized_dataset


class DataPrivacyService:
    """Comprehensive data privacy and protection service."""

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize privacy service."""
        self.encryption_service = EncryptionService(encryption_key)
        self.anonymization_service = AnonymizationService()

        # In-memory storage (in production, use secure database)
        self.processing_records: list[DataProcessingRecord] = []
        self.consent_records: dict[str, list[ConsentRecord]] = {}
        self.privacy_settings: dict[str, PrivacySettings] = {}
        self.encrypted_data_store: dict[str, EncryptedData] = {}
        self.deletion_log: list[dict[str, Any]] = []

    def record_data_processing(self, record: DataProcessingRecord) -> str:
        """Record data processing activity for GDPR compliance."""
        record.record_id = f"proc_{secrets.token_hex(8)}"
        self.processing_records.append(record)
        return record.record_id

    def get_processing_records(self, user_id: str) -> list[DataProcessingRecord]:
        """Get all processing records for a user."""
        return [
            record for record in self.processing_records if record.user_id == user_id
        ]

    def record_consent(self, consent: ConsentRecord) -> str:
        """Record user consent for data processing."""
        if consent.user_id not in self.consent_records:
            self.consent_records[consent.user_id] = []

        consent.consent_id = f"consent_{secrets.token_hex(8)}"
        self.consent_records[consent.user_id].append(consent)

        return consent.consent_id

    def withdraw_consent(self, user_id: str, consent_id: str) -> bool:
        """Withdraw user consent for data processing."""
        if user_id not in self.consent_records:
            return False

        for consent in self.consent_records[user_id]:
            if consent.consent_id == consent_id and consent.is_active:
                consent.is_active = False
                consent.withdrawal_date = datetime.utcnow()
                return True

        return False

    def update_privacy_settings(self, settings: PrivacySettings) -> bool:
        """Update user privacy settings."""
        settings.updated_at = datetime.utcnow()
        self.privacy_settings[settings.user_id] = settings
        return True

    def get_privacy_settings(self, user_id: str) -> PrivacySettings | None:
        """Get user privacy settings."""
        return self.privacy_settings.get(user_id)

    def encrypt_therapeutic_content(self, user_id: str, content: str) -> str:
        """Encrypt therapeutic content for secure storage."""
        key_id = f"therapeutic_{user_id}"
        encrypted_data = self.encryption_service.encrypt_data(
            content, key_id, DataCategory.THERAPEUTIC_CONTENT
        )

        # Store encrypted data
        data_id = f"encrypted_{secrets.token_hex(8)}"
        self.encrypted_data_store[data_id] = encrypted_data

        # Record processing activity
        processing_record = DataProcessingRecord(
            record_id="",
            user_id=user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent for therapeutic services",
            data_source="therapeutic_session",
            is_sensitive=True,
        )
        self.record_data_processing(processing_record)

        return data_id

    def decrypt_therapeutic_content(self, data_id: str) -> str | None:
        """Decrypt therapeutic content."""
        if data_id not in self.encrypted_data_store:
            return None

        encrypted_data = self.encrypted_data_store[data_id]
        decrypted_bytes = self.encryption_service.decrypt_data(encrypted_data)
        return decrypted_bytes.decode("utf-8")

    def export_user_data(self, request: DataExportRequest) -> bytes:
        """Export user data in requested format (GDPR Article 20)."""
        user_data = self._collect_user_data(request.user_id, request.include_categories)

        if request.anonymize_references:
            user_data = self._anonymize_data_references(user_data)

        # Create export package
        export_data = {
            "export_metadata": {
                "user_id": request.user_id,
                "export_date": datetime.utcnow().isoformat(),
                "format": request.export_format,
                "categories_included": [
                    cat.value for cat in request.include_categories
                ],
                "gdpr_article": "Article 20 - Right to data portability",
            },
            "user_data": user_data,
            "processing_records": [
                {
                    "record_id": record.record_id,
                    "data_category": record.data_category.value,
                    "processing_purpose": record.processing_purpose.value,
                    "legal_basis": record.legal_basis,
                    "created_at": record.created_at.isoformat(),
                    "retention_period": record.retention_period.value,
                }
                for record in self.get_processing_records(request.user_id)
            ],
            "consent_records": [
                {
                    "consent_id": consent.consent_id,
                    "purpose": consent.purpose.value,
                    "data_categories": [cat.value for cat in consent.data_categories],
                    "consent_given": consent.consent_given,
                    "consent_date": consent.consent_date.isoformat(),
                    "is_active": consent.is_active,
                }
                for consent in self.consent_records.get(request.user_id, [])
            ],
        }

        # Convert to requested format
        if request.export_format == "json":
            export_content = json.dumps(export_data, indent=2, default=str)
        elif request.export_format == "csv":
            # Simplified CSV export
            export_content = self._convert_to_csv(export_data)
        else:
            export_content = json.dumps(export_data, indent=2, default=str)

        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                f"user_data_export.{request.export_format}", export_content
            )
            zip_file.writestr(
                "export_info.txt",
                f"GDPR Data Export for User {request.user_id}\nGenerated: {datetime.utcnow()}",
            )

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def delete_user_data(self, request: DataDeletionRequest) -> dict[str, Any]:
        """Delete user data (GDPR Article 17 - Right to erasure)."""
        deletion_summary = {
            "user_id": request.user_id,
            "deletion_date": datetime.utcnow().isoformat(),
            "reason": request.deletion_reason,
            "categories_deleted": [],
            "items_deleted": 0,
            "items_anonymized": 0,
            "items_preserved": 0,
            "legal_obligations_preserved": [],
        }

        # Delete or anonymize data by category
        for category in request.categories_to_delete:
            if category == DataCategory.THERAPEUTIC_CONTENT:
                deleted_count = self._delete_therapeutic_content(
                    request.user_id, request.preserve_anonymized
                )
                deletion_summary["items_deleted"] += deleted_count
            elif category == DataCategory.PERSONAL_IDENTIFIABLE:
                anonymized_count = self._anonymize_personal_data(request.user_id)
                deletion_summary["items_anonymized"] += anonymized_count

            deletion_summary["categories_deleted"].append(category.value)

        # Preserve data required for legal obligations
        if request.preserve_legal_obligations:
            preserved_items = self._preserve_legal_obligation_data(request.user_id)
            deletion_summary["items_preserved"] = len(preserved_items)
            deletion_summary["legal_obligations_preserved"] = preserved_items

        # Log deletion
        deletion_log_entry = {
            "user_id": request.user_id,
            "deletion_request": (
                request.model_dump()
                if hasattr(request, "model_dump")
                else request.dict()
            ),
            "deletion_summary": deletion_summary,
            "timestamp": datetime.utcnow(),
        }
        self.deletion_log.append(deletion_log_entry)

        return deletion_summary

    def anonymize_user_data(self, user_id: str) -> dict[str, Any]:
        """Anonymize user data for research purposes."""
        anonymous_id = self.anonymization_service.anonymize_user_id(user_id)

        anonymization_summary = {
            "original_user_id": user_id,
            "anonymous_id": anonymous_id,
            "anonymization_date": datetime.utcnow().isoformat(),
            "items_anonymized": 0,
        }

        # Anonymize therapeutic content
        therapeutic_items = self._get_user_therapeutic_content(user_id)
        for item_id, content in therapeutic_items.items():
            anonymized_content = (
                self.anonymization_service.anonymize_therapeutic_content(content)
            )
            # Store anonymized version
            self._store_anonymized_content(anonymous_id, item_id, anonymized_content)
            anonymization_summary["items_anonymized"] += 1

        return anonymization_summary

    def check_data_retention_compliance(self) -> list[dict[str, Any]]:
        """Check data retention compliance and identify data for deletion."""
        compliance_issues = []
        current_time = datetime.utcnow()

        for record in self.processing_records:
            retention_period = record.retention_period

            if retention_period == DataRetentionPeriod.IMMEDIATE:
                days_limit = 0
            elif retention_period == DataRetentionPeriod.SHORT_TERM:
                days_limit = 30
            elif retention_period == DataRetentionPeriod.MEDIUM_TERM:
                days_limit = 365
            elif retention_period == DataRetentionPeriod.LONG_TERM:
                days_limit = 365 * 7
            else:
                continue  # Indefinite retention

            age = current_time - record.created_at
            if age.days > days_limit:
                compliance_issues.append(
                    {
                        "record_id": record.record_id,
                        "user_id": record.user_id,
                        "data_category": record.data_category.value,
                        "age_days": age.days,
                        "retention_limit_days": days_limit,
                        "action_required": "delete_or_anonymize",
                    }
                )

        return compliance_issues

    def _collect_user_data(
        self, user_id: str, categories: list[DataCategory]
    ) -> dict[str, Any]:
        """Collect all user data for export."""
        user_data = {}

        # Collect data by category
        for category in categories:
            if category == DataCategory.THERAPEUTIC_CONTENT:
                user_data["therapeutic_content"] = self._get_user_therapeutic_content(
                    user_id
                )
            elif category == DataCategory.PERSONAL_IDENTIFIABLE:
                user_data["personal_data"] = self._get_user_personal_data(user_id)
            elif category == DataCategory.BEHAVIORAL_DATA:
                user_data["behavioral_data"] = self._get_user_behavioral_data(user_id)
            # Add other categories as needed

        return user_data

    def _anonymize_data_references(self, data: dict[str, Any]) -> dict[str, Any]:
        """Anonymize references to other users in exported data."""
        # Simple implementation - in production, use more sophisticated methods
        anonymized_data = json.loads(json.dumps(data, default=str))
        return anonymized_data

    def _convert_to_csv(self, data: dict[str, Any]) -> str:
        """Convert export data to CSV format."""
        # Simplified CSV conversion
        csv_lines = ["Category,Key,Value"]

        def flatten_dict(d, parent_key=""):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, str(v)))
            return dict(items)

        flattened = flatten_dict(data)
        for key, value in flattened.items():
            csv_lines.append(f'"{key}","{value}"')

        return "\n".join(csv_lines)

    def _delete_therapeutic_content(
        self, user_id: str, preserve_anonymized: bool
    ) -> int:
        """Delete therapeutic content for user."""
        # Placeholder implementation
        deleted_count = 0

        # In production, this would delete from database
        items_to_delete = [
            data_id
            for data_id, encrypted_data in self.encrypted_data_store.items()
            if encrypted_data.data_category == DataCategory.THERAPEUTIC_CONTENT
        ]

        for data_id in items_to_delete:
            if preserve_anonymized:
                # Convert to anonymized version before deletion
                content = self.decrypt_therapeutic_content(data_id)
                if content:
                    anonymous_id = self.anonymization_service.anonymize_user_id(user_id)
                    anonymized_content = (
                        self.anonymization_service.anonymize_therapeutic_content(
                            content
                        )
                    )
                    self._store_anonymized_content(
                        anonymous_id, data_id, anonymized_content
                    )

            del self.encrypted_data_store[data_id]
            deleted_count += 1

        return deleted_count

    def _anonymize_personal_data(self, user_id: str) -> int:
        """Anonymize personal identifiable data."""
        # Placeholder implementation
        return 1

    def _preserve_legal_obligation_data(self, user_id: str) -> list[str]:
        """Preserve data required for legal obligations."""
        # Placeholder implementation
        return ["audit_logs", "financial_records"]

    def _get_user_therapeutic_content(self, user_id: str) -> dict[str, str]:
        """Get user's therapeutic content."""
        # Placeholder implementation
        content = {}
        for data_id, encrypted_data in self.encrypted_data_store.items():
            if encrypted_data.data_category == DataCategory.THERAPEUTIC_CONTENT:
                decrypted_content = self.decrypt_therapeutic_content(data_id)
                if decrypted_content:
                    content[data_id] = decrypted_content
        return content

    def _get_user_personal_data(self, user_id: str) -> dict[str, Any]:
        """Get user's personal data."""
        # Placeholder implementation
        return {"user_id": user_id, "profile_data": "placeholder"}

    def _get_user_behavioral_data(self, user_id: str) -> dict[str, Any]:
        """Get user's behavioral data."""
        # Placeholder implementation
        return {"interaction_patterns": "placeholder"}

    def _store_anonymized_content(self, anonymous_id: str, item_id: str, content: str):
        """Store anonymized content."""
        # Placeholder implementation
        pass
