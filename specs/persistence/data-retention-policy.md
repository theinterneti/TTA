# Data Retention Policy

- **Component:** Data retention, export, deletion, and anonymization policy
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

TTA currently exposes strong privacy-oriented building blocks in `src/player_experience/services/privacy_service.py` and multiple storage layers with different lifetimes. This spec records a draft retention policy that aligns current code anchors with the repository’s stated therapeutic/privacy expectations.

Important caveat: the strongest concrete code anchors today are GDPR-oriented (`DataPrivacyService`, consent/export/deletion models), while placeholder text in `specs/persistence/README.md` frames the target as HIPAA-compliant. This document is therefore intentionally marked Draft.

## Scope / Responsibilities

- Classify stored data by category and retention horizon.
- Define deletion, anonymization, and export expectations.
- Distinguish ephemeral caches from durable records.
- Preserve legally required data when deletion requests conflict with obligations.
- Keep therapeutic content handling stricter than routine technical telemetry.

## Requirements

### Functional Requirements
- **FR-1:** Data categories must use the current `DataCategory` enum: personal identifiable, therapeutic content, behavioral data, technical data, communication data, and preference data.
- **FR-2:** Retention periods must map to the current `DataRetentionPeriod` enum: `IMMEDIATE`, `SHORT_TERM`, `MEDIUM_TERM`, `LONG_TERM`, and `INDEFINITE`.
- **FR-3:** `DataExportRequest` and `DataDeletionRequest` must remain the canonical API models for user-directed export/deletion behavior.
- **FR-4:** Deletion flows must support preserving anonymized data and preserving legal obligations when requested.
- **FR-5:** Ephemeral Redis/token/session-cache data should be treated as short-lived operational state, not durable records.
- **FR-6:** Durable session/world/character records must be eligible for anonymization or deletion through privacy-service workflows.

### Draft Retention Guidance
- **Immediate / short-term:** auth token cache, orchestration workflow state, transient Redis coordination keys.
- **Medium-term:** active session metadata and conversation history when retained for gameplay continuity.
- **Long-term:** records subject to legal/compliance requirements.
- **Indefinite:** only when explicit consent and product requirements justify it.

### Non-Functional Requirements
- **NFR-1:** Sensitive data should support encryption through `EncryptionService`.
- **NFR-2:** Anonymization should remove common direct identifiers from therapeutic content.
- **NFR-3:** Policy language must avoid claiming runtime enforcement that the code does not yet implement.

## Interfaces / Dependencies

### Privacy Anchors
- `DataCategory`, `ProcessingPurpose`, `DataRetentionPeriod`
- `DataExportRequest`, `DataDeletionRequest`, `ConsentRecord`, `PrivacySettings`
- `EncryptionService`, `AnonymizationService`, `DataPrivacyService`

### Storage Anchors
- `SessionStore` in `src/player_experience/services/session_store.py`
- `SessionRepository`, `WorldRepository`, `CharacterRepository`
- `TokenCache` and orchestration/circuit-breaker Redis persistence

### TTA.dev Primitive Dependencies
- Generic cache/state primitives may shape operational TTLs.
- Privacy rules, consent, and therapeutic-content handling remain TTA-specific.

## Testing / Validation

Relevant anchors:
- `tests/integration/test_persistence_integration.py` validates concrete persistence and cache lifetimes.
- Privacy-service behavior should be validated by targeted unit tests around export, deletion, and anonymization APIs.

## Acceptance Criteria

- The policy is grounded in current privacy and storage code anchors.
- Short-lived cache data is distinguished from durable player/session data.
- The GDPR-centric implementation versus HIPAA-oriented placeholder gap is called out honestly.
- Future compliance work has a clear baseline contract.
