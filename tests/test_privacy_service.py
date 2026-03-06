"""

# Logseq: [[TTA.dev/Tests/Test_privacy_service]]
Tests for data privacy and protection service.

This module tests GDPR compliance features including data encryption,
export, deletion, anonymization, and consent management.
"""

import io
import json
import unittest
import zipfile
from datetime import UTC, datetime, timedelta

import pytest

from src.player_experience.services.privacy_service import (
    AnonymizationService,
    ConsentRecord,
    DataCategory,
    DataDeletionRequest,
    DataExportRequest,
    DataPrivacyService,
    DataProcessingRecord,
    DataRetentionPeriod,
    EncryptedData,
    EncryptionService,
    PrivacySettings,
    ProcessingPurpose,
)


class TestEncryptionService(unittest.TestCase):
    """Test encryption service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.encryption_service = EncryptionService()
        self.test_data = "Sensitive therapeutic content for user session"
        self.test_key_id = "test_key_001"

    def test_generate_data_key(self):
        """Test data key generation."""
        key = self.encryption_service.generate_data_key(
            self.test_key_id, "test_purpose"
        )

        assert key is not None
        assert self.test_key_id in self.encryption_service.encryption_keys
        assert self.test_key_id in self.encryption_service.key_metadata

        metadata = self.encryption_service.key_metadata[self.test_key_id]
        assert metadata["purpose"] == "test_purpose"
        assert metadata["algorithm"] == "Fernet"
        assert metadata["key_size"] == 256

    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption."""
        # Encrypt data
        encrypted_data = self.encryption_service.encrypt_data(
            self.test_data, self.test_key_id, DataCategory.THERAPEUTIC_CONTENT
        )

        assert isinstance(encrypted_data, EncryptedData)
        assert encrypted_data.encryption_method == "Fernet"
        assert encrypted_data.key_id == self.test_key_id
        assert encrypted_data.data_category == DataCategory.THERAPEUTIC_CONTENT
        assert encrypted_data.is_sensitive

        # Decrypt data
        decrypted_data = self.encryption_service.decrypt_data(encrypted_data)
        assert decrypted_data.decode("utf-8") == self.test_data

    def test_encrypt_bytes_data(self):
        """Test encryption of bytes data."""
        test_bytes = b"Binary therapeutic data"

        encrypted_data = self.encryption_service.encrypt_data(
            test_bytes, self.test_key_id, DataCategory.THERAPEUTIC_CONTENT
        )

        decrypted_data = self.encryption_service.decrypt_data(encrypted_data)
        assert decrypted_data == test_bytes

    def test_decrypt_with_missing_key(self):
        """Test decryption with missing key raises error."""
        encrypted_data = EncryptedData(
            encrypted_content=b"fake_encrypted_data",
            encryption_method="Fernet",
            key_id="nonexistent_key",
            created_at=datetime.now(UTC),
            data_category=DataCategory.THERAPEUTIC_CONTENT,
        )

        with pytest.raises(ValueError) as context:
            self.encryption_service.decrypt_data(encrypted_data)

        assert "Encryption key nonexistent_key not found" in str(context.value)

    def test_key_rotation(self):
        """Test encryption key rotation."""
        old_key_id = "old_key"
        new_key_id = "new_key"

        # Generate old key
        self.encryption_service.generate_data_key(old_key_id, "test_purpose")

        # Rotate key
        success = self.encryption_service.rotate_key(old_key_id, new_key_id)

        assert success
        assert new_key_id in self.encryption_service.encryption_keys
        assert self.encryption_service.key_metadata[old_key_id]["deprecated"]
        assert self.encryption_service.key_metadata[old_key_id]["deprecated_at"] is not None

    def test_key_rotation_nonexistent_key(self):
        """Test key rotation with nonexistent key."""
        success = self.encryption_service.rotate_key("nonexistent", "new_key")
        assert not success


class TestAnonymizationService(unittest.TestCase):
    """Test anonymization service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.anonymization_service = AnonymizationService()
        self.test_user_id = "user_12345"
        self.test_content = """
        Hi, my name is John Smith and my email is john.smith@example.com.
        I live at 123 Main Street and my phone number is (555) 123-4567.
        I've been working with Dr. Sarah Johnson on my anxiety issues.
        """

    def test_anonymize_user_id(self):
        """Test user ID anonymization."""
        anonymous_id = self.anonymization_service.anonymize_user_id(self.test_user_id)

        assert anonymous_id is not None
        assert anonymous_id.startswith("anon_")
        assert anonymous_id != self.test_user_id

        # Should be consistent for same user
        anonymous_id2 = self.anonymization_service.anonymize_user_id(self.test_user_id)
        assert anonymous_id == anonymous_id2

    def test_pseudonymize_user_id(self):
        """Test user ID pseudonymization."""
        pseudonym = self.anonymization_service.pseudonymize_user_id(self.test_user_id)

        assert pseudonym is not None
        assert pseudonym.startswith("user_")
        assert pseudonym != self.test_user_id

        # Should be consistent for same user
        pseudonym2 = self.anonymization_service.pseudonymize_user_id(self.test_user_id)
        assert pseudonym == pseudonym2

    def test_anonymize_therapeutic_content(self):
        """Test therapeutic content anonymization."""
        anonymized = self.anonymization_service.anonymize_therapeutic_content(
            self.test_content
        )

        # Check that PII has been replaced
        assert "John Smith" not in anonymized
        assert "john.smith@example.com" not in anonymized
        assert "123 Main Street" not in anonymized
        assert "(555) 123-4567" not in anonymized

        # Check that placeholders are present
        assert "[NAME]" in anonymized
        assert "[EMAIL]" in anonymized
        assert "[ADDRESS]" in anonymized
        assert "[PHONE]" in anonymized

    def test_k_anonymize_dataset(self):
        """Test k-anonymity application to dataset."""
        dataset = [
            {"age": 25, "location": "New York", "gender": "M", "condition": "anxiety"},
            {
                "age": 30,
                "location": "California",
                "gender": "F",
                "condition": "depression",
            },
            {"age": 45, "location": "Texas", "gender": "M", "condition": "ptsd"},
            {"age": 16, "location": "Florida", "gender": "F", "condition": "anxiety"},
        ]

        anonymized = self.anonymization_service.k_anonymize_dataset(
            dataset, k=2, quasi_identifiers=["age", "location"]
        )

        assert len(anonymized) == len(dataset)

        # Check age generalization
        for record in anonymized:
            assert record["age"] in ["under_18", "18_29", "30_49", "50_plus"]
            assert record["location"] == "region_generalized"

    def test_k_anonymize_empty_dataset(self):
        """Test k-anonymity with empty dataset."""
        anonymized = self.anonymization_service.k_anonymize_dataset([])
        assert anonymized == []


class TestDataPrivacyService(unittest.TestCase):
    """Test comprehensive data privacy service."""

    def setUp(self):
        """Set up test fixtures."""
        self.privacy_service = DataPrivacyService()
        self.test_user_id = "user_test_001"
        self.test_content = "Therapeutic session content with sensitive information"

    def test_record_data_processing(self):
        """Test recording data processing activities."""
        record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent for therapeutic services",
            data_source="therapeutic_session",
            is_sensitive=True,
        )

        record_id = self.privacy_service.record_data_processing(record)

        assert record_id is not None
        assert record_id.startswith("proc_")

        # Verify record is stored
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1
        assert records[0].record_id == record_id

    def test_record_consent(self):
        """Test recording user consent."""
        consent = ConsentRecord(
            user_id=self.test_user_id,
            consent_id="",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.THERAPEUTIC_CONTENT],
            consent_given=True,
            consent_date=datetime.now(UTC),
            consent_method="explicit",
        )

        consent_id = self.privacy_service.record_consent(consent)

        assert consent_id is not None
        assert consent_id.startswith("consent_")

        # Verify consent is stored
        consents = self.privacy_service.consent_records.get(self.test_user_id, [])
        assert len(consents) == 1
        assert consents[0].consent_id == consent_id
        assert consents[0].is_active

    def test_withdraw_consent(self):
        """Test withdrawing user consent."""
        # First record consent
        consent = ConsentRecord(
            user_id=self.test_user_id,
            consent_id="",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.THERAPEUTIC_CONTENT],
            consent_given=True,
            consent_date=datetime.now(UTC),
            consent_method="explicit",
        )

        consent_id = self.privacy_service.record_consent(consent)

        # Then withdraw it
        success = self.privacy_service.withdraw_consent(self.test_user_id, consent_id)

        assert success

        # Verify consent is withdrawn
        consents = self.privacy_service.consent_records.get(self.test_user_id, [])
        assert len(consents) == 1
        assert not consents[0].is_active
        assert consents[0].withdrawal_date is not None

    def test_withdraw_nonexistent_consent(self):
        """Test withdrawing nonexistent consent."""
        success = self.privacy_service.withdraw_consent(
            self.test_user_id, "nonexistent_consent"
        )
        assert not success

    def test_update_privacy_settings(self):
        """Test updating privacy settings."""
        settings = PrivacySettings(
            user_id=self.test_user_id,
            data_minimization=True,
            research_consent=False,
            data_retention_preference=DataRetentionPeriod.SHORT_TERM,
        )

        success = self.privacy_service.update_privacy_settings(settings)
        assert success

        # Verify settings are stored
        stored_settings = self.privacy_service.get_privacy_settings(self.test_user_id)
        assert stored_settings is not None
        assert stored_settings.user_id == self.test_user_id
        assert stored_settings.data_minimization
        assert not stored_settings.research_consent
        assert stored_settings.data_retention_preference == DataRetentionPeriod.SHORT_TERM

    def test_encrypt_therapeutic_content(self):
        """Test encrypting therapeutic content."""
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, self.test_content
        )

        assert data_id is not None
        assert data_id.startswith("encrypted_")

        # Verify data is encrypted and stored
        assert data_id in self.privacy_service.encrypted_data_store

        # Verify processing record is created
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1
        assert records[0].data_category == DataCategory.THERAPEUTIC_CONTENT

    def test_decrypt_therapeutic_content(self):
        """Test decrypting therapeutic content."""
        # First encrypt content
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, self.test_content
        )

        # Then decrypt it
        decrypted_content = self.privacy_service.decrypt_therapeutic_content(data_id)

        assert decrypted_content == self.test_content

    def test_decrypt_nonexistent_content(self):
        """Test decrypting nonexistent content."""
        decrypted_content = self.privacy_service.decrypt_therapeutic_content(
            "nonexistent_id"
        )
        assert decrypted_content is None

    def test_export_user_data(self):
        """Test exporting user data."""
        # Set up test data
        self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, self.test_content
        )

        consent = ConsentRecord(
            user_id=self.test_user_id,
            consent_id="",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.THERAPEUTIC_CONTENT],
            consent_given=True,
            consent_date=datetime.now(UTC),
            consent_method="explicit",
        )
        self.privacy_service.record_consent(consent)

        # Export data
        export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="json",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
        )

        export_data = self.privacy_service.export_user_data(export_request)

        assert export_data is not None
        assert isinstance(export_data, bytes)

        # Verify it's a valid ZIP file
        with zipfile.ZipFile(io.BytesIO(export_data), "r") as zip_file:
            file_names = zip_file.namelist()
            assert "user_data_export.json" in file_names
            assert "export_info.txt" in file_names

            # Check export content
            export_content = zip_file.read("user_data_export.json").decode("utf-8")
            export_json = json.loads(export_content)

            assert "export_metadata" in export_json
            assert "user_data" in export_json
            assert "processing_records" in export_json
            assert "consent_records" in export_json

            assert export_json["export_metadata"]["user_id"] == self.test_user_id

    def test_export_user_data_csv_format(self):
        """Test exporting user data in CSV format."""
        export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="csv",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
        )

        export_data = self.privacy_service.export_user_data(export_request)

        # Verify it's a valid ZIP file with CSV content
        with zipfile.ZipFile(io.BytesIO(export_data), "r") as zip_file:
            file_names = zip_file.namelist()
            assert "user_data_export.csv" in file_names

            csv_content = zip_file.read("user_data_export.csv").decode("utf-8")
            assert "Category,Key,Value" in csv_content

    def test_delete_user_data(self):
        """Test deleting user data."""
        # Set up test data
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, self.test_content
        )

        # Delete data
        deletion_request = DataDeletionRequest(
            user_id=self.test_user_id,
            deletion_reason="User requested account deletion",
            categories_to_delete=[DataCategory.THERAPEUTIC_CONTENT],
            preserve_anonymized=True,
        )

        deletion_summary = self.privacy_service.delete_user_data(deletion_request)

        assert deletion_summary is not None
        assert deletion_summary["user_id"] == self.test_user_id
        assert DataCategory.THERAPEUTIC_CONTENT.value in deletion_summary["categories_deleted"]
        assert deletion_summary["items_deleted"] > 0

        # Verify data is deleted
        assert data_id not in self.privacy_service.encrypted_data_store

        # Verify deletion is logged
        assert len(self.privacy_service.deletion_log) == 1
        log_entry = self.privacy_service.deletion_log[0]
        assert log_entry["user_id"] == self.test_user_id

    def test_anonymize_user_data(self):
        """Test anonymizing user data."""
        # Set up test data
        self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, self.test_content
        )

        # Anonymize data
        anonymization_summary = self.privacy_service.anonymize_user_data(
            self.test_user_id
        )

        assert anonymization_summary is not None
        assert anonymization_summary["original_user_id"] == self.test_user_id
        assert anonymization_summary["anonymous_id"] is not None
        assert anonymization_summary["anonymous_id"].startswith("anon_")
        assert anonymization_summary["items_anonymized"] > 0

    def test_check_data_retention_compliance(self):
        """Test checking data retention compliance."""
        # Create old processing record
        old_record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent",
            data_source="test",
            retention_period=DataRetentionPeriod.SHORT_TERM,
            created_at=datetime.now(UTC) - timedelta(days=45),  # Older than 30 days
        )

        self.privacy_service.record_data_processing(old_record)

        # Check compliance
        compliance_issues = self.privacy_service.check_data_retention_compliance()

        assert len(compliance_issues) == 1
        issue = compliance_issues[0]
        assert issue["user_id"] == self.test_user_id
        assert issue["data_category"] == DataCategory.THERAPEUTIC_CONTENT.value
        assert issue["age_days"] > 30
        assert issue["retention_limit_days"] == 30
        assert issue["action_required"] == "delete_or_anonymize"

    def test_check_data_retention_compliance_no_issues(self):
        """Test data retention compliance with no issues."""
        # Create recent processing record
        recent_record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent",
            data_source="test",
            retention_period=DataRetentionPeriod.MEDIUM_TERM,
            created_at=datetime.now(UTC) - timedelta(days=30),  # Within 1 year limit
        )

        self.privacy_service.record_data_processing(recent_record)

        # Check compliance
        compliance_issues = self.privacy_service.check_data_retention_compliance()

        assert len(compliance_issues) == 0


class TestPrivacyServiceIntegration(unittest.TestCase):
    """Test privacy service integration scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.privacy_service = DataPrivacyService()
        self.test_user_id = "integration_user_001"

    def test_complete_gdpr_workflow(self):
        """Test complete GDPR compliance workflow."""
        # 1. Record consent
        consent = ConsentRecord(
            user_id=self.test_user_id,
            consent_id="",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[
                DataCategory.THERAPEUTIC_CONTENT,
                DataCategory.BEHAVIORAL_DATA,
            ],
            consent_given=True,
            consent_date=datetime.now(UTC),
            consent_method="explicit",
        )

        consent_id = self.privacy_service.record_consent(consent)
        assert consent_id is not None

        # 2. Process and encrypt data
        therapeutic_content = "User shared personal therapeutic insights"
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, therapeutic_content
        )
        assert data_id is not None

        # 3. Update privacy settings
        settings = PrivacySettings(
            user_id=self.test_user_id,
            research_consent=True,
            data_retention_preference=DataRetentionPeriod.MEDIUM_TERM,
        )

        success = self.privacy_service.update_privacy_settings(settings)
        assert success

        # 4. Export data (Article 20)
        export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="json",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
        )

        export_data = self.privacy_service.export_user_data(export_request)
        assert export_data is not None

        # 5. Withdraw consent
        withdraw_success = self.privacy_service.withdraw_consent(
            self.test_user_id, consent_id
        )
        assert withdraw_success

        # 6. Delete data (Article 17)
        deletion_request = DataDeletionRequest(
            user_id=self.test_user_id,
            deletion_reason="User requested data deletion after consent withdrawal",
            categories_to_delete=[DataCategory.THERAPEUTIC_CONTENT],
            preserve_anonymized=True,
        )

        deletion_summary = self.privacy_service.delete_user_data(deletion_request)
        assert deletion_summary is not None
        assert deletion_summary["items_deleted"] > 0

        # 7. Verify data is deleted
        decrypted_content = self.privacy_service.decrypt_therapeutic_content(data_id)
        assert decrypted_content is None

    def test_privacy_by_design_principles(self):
        """Test privacy by design principles implementation."""
        # Data minimization
        settings = PrivacySettings(
            user_id=self.test_user_id,
            data_minimization=True,
            purpose_limitation=True,
            storage_limitation=True,
        )

        success = self.privacy_service.update_privacy_settings(settings)
        assert success

        stored_settings = self.privacy_service.get_privacy_settings(self.test_user_id)
        assert stored_settings.data_minimization
        assert stored_settings.purpose_limitation
        assert stored_settings.storage_limitation

        # Purpose limitation - record processing with specific purpose
        record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="Explicit user consent for therapeutic services only",
            data_source="therapeutic_session",
        )

        record_id = self.privacy_service.record_data_processing(record)
        assert record_id is not None

        # Storage limitation - verify retention period is set
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1
        assert records[0].retention_period is not None

    def test_cross_border_data_transfer_compliance(self):
        """Test cross-border data transfer compliance."""
        # Record processing with cross-border transfer
        record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent with adequacy decision",
            data_source="therapeutic_session",
            cross_border_transfer=True,
            recipients=["EU-based therapeutic AI service"],
        )

        record_id = self.privacy_service.record_data_processing(record)
        assert record_id is not None

        # Verify cross-border transfer is recorded
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1
        assert records[0].cross_border_transfer
        assert "EU-based therapeutic AI service" in records[0].recipients

    def test_automated_decision_making_transparency(self):
        """Test automated decision making transparency."""
        # Record processing with automated decision making
        record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.BEHAVIORAL_DATA,
            processing_purpose=ProcessingPurpose.LEGITIMATE_INTERESTS,
            legal_basis="Legitimate interest for therapeutic effectiveness",
            data_source="ai_recommendation_system",
            automated_decision_making=True,
        )

        record_id = self.privacy_service.record_data_processing(record)
        assert record_id is not None

        # Verify automated decision making is recorded
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1
        assert records[0].automated_decision_making


if __name__ == "__main__":
    unittest.main()
