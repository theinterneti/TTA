import pytest
"""

# Logseq: [[TTA.dev/Tests/Test_privacy_api]]
Tests for privacy API endpoints.

This module tests the GDPR compliance features including data encryption,
export, deletion, anonymization, and consent management through direct
service testing rather than API endpoint testing.
"""

import io
import json
import unittest
import zipfile
from datetime import UTC, datetime

from src.player_experience.models.auth import AuthenticatedUser, Permission, UserRole
from src.player_experience.services.privacy_service import (
    ConsentRecord,
    DataCategory,
    DataDeletionRequest,
    DataExportRequest,
    DataPrivacyService,
    DataRetentionPeriod,
    PrivacySettings,
    ProcessingPurpose,
)

pytestmark = pytest.mark.unit


class TestPrivacyCompliance(unittest.TestCase):
    """Test privacy compliance features through service integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.privacy_service = DataPrivacyService()

        self.test_user_id = "test_user_001"
        self.test_user = AuthenticatedUser(
            user_id=self.test_user_id,
            username="testuser",
            email="test@example.com",
            role=UserRole.PLAYER,
            permissions=[
                Permission.MANAGE_OWN_PROFILE,
                Permission.EXPORT_OWN_DATA,
                Permission.DELETE_OWN_DATA,
            ],
        )

        self.admin_user = AuthenticatedUser(
            user_id="admin_user_001",
            username="admin",
            email="admin@example.com",
            role=UserRole.ADMIN,
            permissions=list(Permission),
        )

    def test_privacy_settings_management(self):
        """Test privacy settings management workflow."""
        # Create privacy settings
        settings = PrivacySettings(
            user_id=self.test_user_id,
            data_minimization=True,
            research_consent=False,
            data_retention_preference=DataRetentionPeriod.MEDIUM_TERM,
            marketing_consent=False,
            analytics_consent=True,
        )

        # Update settings
        success = self.privacy_service.update_privacy_settings(settings)
        assert success

        # Retrieve settings
        retrieved_settings = self.privacy_service.get_privacy_settings(
            self.test_user_id
        )
        assert retrieved_settings is not None
        assert retrieved_settings.user_id == self.test_user_id
        assert retrieved_settings.data_minimization
        assert not retrieved_settings.research_consent
        assert (
            retrieved_settings.data_retention_preference
            == DataRetentionPeriod.MEDIUM_TERM
        )
        assert not retrieved_settings.marketing_consent
        assert retrieved_settings.analytics_consent

    def test_consent_management_workflow(self):
        """Test complete consent management workflow."""
        # Record initial consent
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
            consent_evidence="User clicked 'I agree' button",
        )

        consent_id = self.privacy_service.record_consent(consent)
        assert consent_id is not None
        assert consent_id.startswith("consent_")

        # Verify consent is recorded
        consent_records = self.privacy_service.consent_records.get(
            self.test_user_id, []
        )
        assert len(consent_records) == 1
        recorded_consent = consent_records[0]
        assert recorded_consent.consent_id == consent_id
        assert recorded_consent.consent_given
        assert recorded_consent.is_active
        assert recorded_consent.purpose == ProcessingPurpose.CONSENT

        # Withdraw consent
        withdrawal_success = self.privacy_service.withdraw_consent(
            self.test_user_id, consent_id
        )
        assert withdrawal_success

        # Verify consent is withdrawn
        updated_consent = consent_records[0]  # Same object, updated in place
        assert not updated_consent.is_active
        assert updated_consent.withdrawal_date is not None

        # Try to withdraw nonexistent consent
        invalid_withdrawal = self.privacy_service.withdraw_consent(
            self.test_user_id, "nonexistent"
        )
        assert not invalid_withdrawal

    def test_data_export_workflow(self):
        """Test complete data export workflow (GDPR Article 20)."""
        # Set up test data
        therapeutic_content = "User shared personal therapeutic insights during session"
        self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, therapeutic_content
        )

        # Record consent for the data
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

        # Export data in JSON format
        export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="json",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
            anonymize_references=True,
        )

        export_data = self.privacy_service.export_user_data(export_request)
        assert export_data is not None
        assert isinstance(export_data, bytes)

        # Verify it's a valid ZIP file with expected content
        with zipfile.ZipFile(io.BytesIO(export_data), "r") as zip_file:
            file_names = zip_file.namelist()
            assert "user_data_export.json" in file_names
            assert "export_info.txt" in file_names

            # Check export content structure
            export_content = zip_file.read("user_data_export.json").decode("utf-8")
            export_json = json.loads(export_content)

            assert "export_metadata" in export_json
            assert "user_data" in export_json
            assert "processing_records" in export_json
            assert "consent_records" in export_json

            # Verify metadata
            metadata = export_json["export_metadata"]
            assert metadata["user_id"] == self.test_user_id
            assert metadata["format"] == "json"
            assert "gdpr_article" in metadata

        # Test CSV export format
        csv_export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="csv",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
        )

        csv_export_data = self.privacy_service.export_user_data(csv_export_request)
        with zipfile.ZipFile(io.BytesIO(csv_export_data), "r") as zip_file:
            file_names = zip_file.namelist()
            assert "user_data_export.csv" in file_names

            csv_content = zip_file.read("user_data_export.csv").decode("utf-8")
            assert "Category,Key,Value" in csv_content

    def test_data_deletion_workflow(self):
        """Test complete data deletion workflow (GDPR Article 17)."""
        # Set up test data
        therapeutic_content = "Sensitive therapeutic session data"
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, therapeutic_content
        )

        # Verify data exists
        decrypted_content = self.privacy_service.decrypt_therapeutic_content(data_id)
        assert decrypted_content == therapeutic_content

        # Request data deletion
        deletion_request = DataDeletionRequest(
            user_id=self.test_user_id,
            deletion_reason="User requested account deletion",
            categories_to_delete=[DataCategory.THERAPEUTIC_CONTENT],
            preserve_anonymized=True,
            preserve_legal_obligations=True,
        )

        deletion_summary = self.privacy_service.delete_user_data(deletion_request)

        # Verify deletion summary
        assert deletion_summary is not None
        assert deletion_summary["user_id"] == self.test_user_id
        assert deletion_summary["reason"] == "User requested account deletion"
        assert (
            DataCategory.THERAPEUTIC_CONTENT.value
            in deletion_summary["categories_deleted"]
        )
        assert deletion_summary["items_deleted"] > 0

        # Verify data is actually deleted
        deleted_content = self.privacy_service.decrypt_therapeutic_content(data_id)
        assert deleted_content is None

        # Verify deletion is logged
        assert len(self.privacy_service.deletion_log) == 1
        log_entry = self.privacy_service.deletion_log[0]
        assert log_entry["user_id"] == self.test_user_id
        assert "deletion_request" in log_entry
        assert "deletion_summary" in log_entry

    def test_data_anonymization_workflow(self):
        """Test data anonymization for research purposes."""
        # Set up test data
        therapeutic_content = "Patient John Smith discussed anxiety with Dr. Johnson at john.smith@email.com"
        self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, therapeutic_content
        )

        # Anonymize user data
        anonymization_summary = self.privacy_service.anonymize_user_data(
            self.test_user_id
        )

        # Verify anonymization summary
        assert anonymization_summary is not None
        assert anonymization_summary["original_user_id"] == self.test_user_id
        assert anonymization_summary["anonymous_id"] is not None
        assert anonymization_summary["anonymous_id"].startswith("anon_")
        assert anonymization_summary["anonymous_id"] != self.test_user_id
        assert anonymization_summary["items_anonymized"] > 0

        # Verify anonymization is consistent
        second_anonymization = self.privacy_service.anonymize_user_data(
            self.test_user_id
        )
        assert (
            anonymization_summary["anonymous_id"]
            == second_anonymization["anonymous_id"]
        )

    def test_data_processing_records_management(self):
        """Test data processing records management."""
        from src.player_experience.services.privacy_service import DataProcessingRecord

        # Create processing record
        record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent for therapeutic services",
            data_source="therapeutic_session",
            retention_period=DataRetentionPeriod.MEDIUM_TERM,
            is_sensitive=True,
            cross_border_transfer=False,
            automated_decision_making=True,
        )

        # Record the processing activity
        record_id = self.privacy_service.record_data_processing(record)
        assert record_id is not None
        assert record_id.startswith("proc_")

        # Retrieve processing records
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) == 1

        retrieved_record = records[0]
        assert retrieved_record.record_id == record_id
        assert retrieved_record.user_id == self.test_user_id
        assert retrieved_record.data_category == DataCategory.THERAPEUTIC_CONTENT
        assert retrieved_record.processing_purpose == ProcessingPurpose.CONSENT
        assert retrieved_record.is_sensitive
        assert not retrieved_record.cross_border_transfer
        assert retrieved_record.automated_decision_making

    def test_data_retention_compliance_monitoring(self):
        """Test data retention compliance monitoring."""
        from datetime import UTC, timedelta

        from src.player_experience.services.privacy_service import DataProcessingRecord

        # Create old processing record that should trigger compliance issue
        old_record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.THERAPEUTIC_CONTENT,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent",
            data_source="test",
            retention_period=DataRetentionPeriod.SHORT_TERM,  # 30 days
            created_at=datetime.now(UTC) - timedelta(days=45),  # 45 days old
        )

        self.privacy_service.record_data_processing(old_record)

        # Create recent record that should be compliant
        recent_record = DataProcessingRecord(
            record_id="",
            user_id=self.test_user_id,
            data_category=DataCategory.BEHAVIORAL_DATA,
            processing_purpose=ProcessingPurpose.CONSENT,
            legal_basis="User consent",
            data_source="test",
            retention_period=DataRetentionPeriod.MEDIUM_TERM,  # 1 year
            created_at=datetime.now(UTC) - timedelta(days=30),  # 30 days old
        )

        self.privacy_service.record_data_processing(recent_record)

        # Check compliance
        compliance_issues = self.privacy_service.check_data_retention_compliance()

        # Should have one compliance issue (the old record)
        assert len(compliance_issues) == 1
        issue = compliance_issues[0]
        assert issue["user_id"] == self.test_user_id
        assert issue["data_category"] == DataCategory.THERAPEUTIC_CONTENT.value
        assert issue["age_days"] > 30
        assert issue["retention_limit_days"] == 30
        assert issue["action_required"] == "delete_or_anonymize"

    def test_privacy_by_design_principles(self):
        """Test implementation of privacy by design principles."""
        # Test data minimization
        settings = PrivacySettings(
            user_id=self.test_user_id,
            data_minimization=True,
            purpose_limitation=True,
            storage_limitation=True,
            marketing_consent=False,
            analytics_consent=False,
            research_consent=False,
        )

        success = self.privacy_service.update_privacy_settings(settings)
        assert success

        # Verify settings enforce privacy by design
        stored_settings = self.privacy_service.get_privacy_settings(self.test_user_id)
        assert stored_settings.data_minimization
        assert stored_settings.purpose_limitation
        assert stored_settings.storage_limitation
        assert not stored_settings.marketing_consent
        assert not stored_settings.analytics_consent
        assert not stored_settings.research_consent

    def test_gdpr_rights_implementation(self):
        """Test implementation of GDPR rights."""
        # Set up test data
        therapeutic_content = "Test therapeutic content for GDPR rights testing"
        self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, therapeutic_content
        )

        # Test Right to Access (Article 15) - via processing records
        records = self.privacy_service.get_processing_records(self.test_user_id)
        assert len(records) > 0

        # Test Right to Rectification (Article 16) - via privacy settings update
        settings = PrivacySettings(user_id=self.test_user_id, research_consent=True)
        rectification_success = self.privacy_service.update_privacy_settings(settings)
        assert rectification_success

        # Test Right to Erasure (Article 17) - via data deletion
        deletion_request = DataDeletionRequest(
            user_id=self.test_user_id,
            deletion_reason="Testing GDPR right to erasure",
            categories_to_delete=[DataCategory.THERAPEUTIC_CONTENT],
        )
        deletion_summary = self.privacy_service.delete_user_data(deletion_request)
        assert deletion_summary["items_deleted"] > 0

        # Test Right to Data Portability (Article 20) - via data export
        export_request = DataExportRequest(
            user_id=self.test_user_id,
            export_format="json",
            include_categories=[DataCategory.THERAPEUTIC_CONTENT],
        )
        export_data = self.privacy_service.export_user_data(export_request)
        assert export_data is not None

        # Test Right to Object (Article 21) - via consent withdrawal
        consent = ConsentRecord(
            user_id=self.test_user_id,
            consent_id="",
            purpose=ProcessingPurpose.LEGITIMATE_INTERESTS,
            data_categories=[DataCategory.BEHAVIORAL_DATA],
            consent_given=True,
            consent_date=datetime.now(UTC),
            consent_method="explicit",
        )
        consent_id = self.privacy_service.record_consent(consent)
        objection_success = self.privacy_service.withdraw_consent(
            self.test_user_id, consent_id
        )
        assert objection_success

    def test_therapeutic_data_protection_integration(self):
        """Test integration with therapeutic data protection requirements."""
        # Test encryption of sensitive therapeutic content
        sensitive_content = "Patient disclosed trauma history and coping mechanisms"
        data_id = self.privacy_service.encrypt_therapeutic_content(
            self.test_user_id, sensitive_content
        )

        # Verify content is encrypted and stored securely
        assert data_id is not None
        assert data_id in self.privacy_service.encrypted_data_store

        encrypted_data = self.privacy_service.encrypted_data_store[data_id]
        assert encrypted_data.data_category == DataCategory.THERAPEUTIC_CONTENT
        assert encrypted_data.is_sensitive

        # Verify processing record is created for therapeutic data
        records = self.privacy_service.get_processing_records(self.test_user_id)
        therapeutic_records = [
            r for r in records if r.data_category == DataCategory.THERAPEUTIC_CONTENT
        ]
        assert len(therapeutic_records) > 0

        therapeutic_record = therapeutic_records[0]
        assert therapeutic_record.is_sensitive
        assert therapeutic_record.processing_purpose == ProcessingPurpose.CONSENT

        # Test decryption works correctly
        decrypted_content = self.privacy_service.decrypt_therapeutic_content(data_id)
        assert decrypted_content == sensitive_content

        # Test anonymization of therapeutic content with PII
        content_with_pii = "John Smith disclosed trauma history and contacted me at john.smith@email.com"
        anonymized_content = (
            self.privacy_service.anonymization_service.anonymize_therapeutic_content(
                content_with_pii
            )
        )
        assert anonymized_content != content_with_pii
        assert "John Smith" not in anonymized_content  # Should be anonymized
        assert "john.smith@email.com" not in anonymized_content  # Should be anonymized
        assert "[NAME]" in anonymized_content
        assert "[EMAIL]" in anonymized_content


if __name__ == "__main__":
    unittest.main()
