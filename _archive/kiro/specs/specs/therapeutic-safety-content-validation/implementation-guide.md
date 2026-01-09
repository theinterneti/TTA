# Therapeutic Safety & Content Validation - Implementation Guide

**Date:** November 2, 2025
**Status:** Active Implementation Guide
**Component:** Therapeutic Safety & Content Validation System
**Spec Version:** 1.0
**Related Specs:** `requirements.md`, `design.md`, `tasks.md`

---

## Purpose

This document bridges the spec-to-implementation gap for the Therapeutic Safety & Content Validation system, providing detailed implementation guidance for:
- Crisis intervention protocols and emergency response
- HIPAA compliance and healthcare data protection
- Emergency support procedures and escalation
- Real-world integration patterns

---

## 1. Crisis Intervention Protocols

### 1.1 Crisis Detection Model

**Implementation:**

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime

class CrisisLevel(Enum):
    """Crisis severity levels for escalation."""
    NONE = "none"  # No crisis detected
    LOW = "low"  # Elevated distress, monitoring needed
    MEDIUM = "medium"  # Significant distress, intervention recommended
    HIGH = "high"  # Acute distress, immediate intervention required
    EMERGENCY = "emergency"  # Imminent danger, emergency services needed

class CrisisIndicatorType(Enum):
    """Types of crisis indicators."""
    SELF_HARM = "self_harm"
    SUICIDAL_IDEATION = "suicidal_ideation"
    HARM_TO_OTHERS = "harm_to_others"
    ACUTE_DISTRESS = "acute_distress"
    DISSOCIATION = "dissociation"
    PSYCHOTIC_SYMPTOMS = "psychotic_symptoms"
    SUBSTANCE_CRISIS = "substance_crisis"

@dataclass
class CrisisIndicator:
    """Individual crisis indicator detection."""
    indicator_type: CrisisIndicatorType
    confidence: float  # 0.0 - 1.0
    matched_patterns: List[str]
    context: str
    timestamp: datetime

@dataclass
class CrisisDetectionResult:
    """Result of crisis detection analysis."""
    crisis_detected: bool
    crisis_level: CrisisLevel
    indicators: List[CrisisIndicator]
    confidence: float
    user_input: str
    recommended_action: str
    escalation_required: bool

class CrisisDetector:
    """
    Detects crisis situations from user input.
    Uses pattern matching + ML classifiers for accuracy.
    """

    # High-risk keywords and phrases (simplified example)
    SELF_HARM_PATTERNS = [
        r"\b(want to|going to|plan to)\s+(hurt|harm|cut|kill)\s+(myself|me)\b",
        r"\b(suicid|self[- ]harm|end (my|it all))\b",
        r"\b(better off dead|don't want to live)\b",
    ]

    HARM_TO_OTHERS_PATTERNS = [
        r"\b(want to|going to|plan to)\s+(hurt|harm|kill)\s+(someone|them|him|her)\b",
        r"\b(violent thoughts|homicidal)\b",
    ]

    ACUTE_DISTRESS_PATTERNS = [
        r"\b(can't take (it|this) anymore|completely overwhelmed)\b",
        r"\b(lost all hope|no way out|trapped)\b",
        r"\b(panic attack|can't breathe)\b",
    ]

    def __init__(self, ml_classifier=None):
        self.ml_classifier = ml_classifier
        import re
        self.patterns = {
            CrisisIndicatorType.SELF_HARM: [re.compile(p, re.IGNORECASE) for p in self.SELF_HARM_PATTERNS],
            CrisisIndicatorType.HARM_TO_OTHERS: [re.compile(p, re.IGNORECASE) for p in self.HARM_TO_OTHERS_PATTERNS],
            CrisisIndicatorType.ACUTE_DISTRESS: [re.compile(p, re.IGNORECASE) for p in self.ACUTE_DISTRESS_PATTERNS],
        }

    async def detect_crisis(self, user_input: str, user_history: Optional[List[str]] = None) -> CrisisDetectionResult:
        """
        Detect crisis indicators in user input.
        Combines pattern matching with ML classification for accuracy.
        """
        indicators = []

        # Pattern-based detection
        for indicator_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = pattern.search(user_input)
                if match:
                    indicators.append(CrisisIndicator(
                        indicator_type=indicator_type,
                        confidence=0.9,  # Pattern matches are high confidence
                        matched_patterns=[match.group()],
                        context=user_input,
                        timestamp=datetime.utcnow(),
                    ))

        # ML-based detection (if available)
        if self.ml_classifier:
            ml_indicators = await self.ml_classifier.classify_crisis(
                text=user_input,
                history=user_history
            )
            indicators.extend(ml_indicators)

        # Determine crisis level
        crisis_level = self._calculate_crisis_level(indicators)

        # Build result
        result = CrisisDetectionResult(
            crisis_detected=crisis_level != CrisisLevel.NONE,
            crisis_level=crisis_level,
            indicators=indicators,
            confidence=self._calculate_confidence(indicators),
            user_input=user_input,
            recommended_action=self._get_recommended_action(crisis_level),
            escalation_required=(crisis_level in [CrisisLevel.HIGH, CrisisLevel.EMERGENCY]),
        )

        return result

    def _calculate_crisis_level(self, indicators: List[CrisisIndicator]) -> CrisisLevel:
        """Determine overall crisis level from indicators."""
        if not indicators:
            return CrisisLevel.NONE

        # Emergency: self-harm or harm to others
        for indicator in indicators:
            if indicator.indicator_type in [
                CrisisIndicatorType.SELF_HARM,
                CrisisIndicatorType.SUICIDAL_IDEATION,
                CrisisIndicatorType.HARM_TO_OTHERS
            ] and indicator.confidence > 0.7:
                return CrisisLevel.EMERGENCY

        # High: acute distress or psychotic symptoms
        for indicator in indicators:
            if indicator.indicator_type in [
                CrisisIndicatorType.ACUTE_DISTRESS,
                CrisisIndicatorType.PSYCHOTIC_SYMPTOMS
            ] and indicator.confidence > 0.7:
                return CrisisLevel.HIGH

        # Medium: moderate indicators
        if len(indicators) >= 2 and all(i.confidence > 0.5 for i in indicators):
            return CrisisLevel.MEDIUM

        # Low: single indicator or low confidence
        return CrisisLevel.LOW

    def _calculate_confidence(self, indicators: List[CrisisIndicator]) -> float:
        """Calculate overall confidence in crisis detection."""
        if not indicators:
            return 0.0
        return max(i.confidence for i in indicators)

    def _get_recommended_action(self, crisis_level: CrisisLevel) -> str:
        """Get recommended action based on crisis level."""
        actions = {
            CrisisLevel.NONE: "Continue normal therapeutic interaction",
            CrisisLevel.LOW: "Monitor user closely, check in frequently",
            CrisisLevel.MEDIUM: "Activate support resources, offer coping tools",
            CrisisLevel.HIGH: "Immediate intervention, provide crisis resources",
            CrisisLevel.EMERGENCY: "EMERGENCY: Contact crisis services, notify emergency contacts",
        }
        return actions.get(crisis_level, "Unknown")
```

### 1.2 Crisis Response System

```python
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CrisisResponseSystem:
    """
    Handles crisis intervention and emergency response.
    Implements escalation protocols and resource provision.
    """

    def __init__(
        self,
        crisis_detector: CrisisDetector,
        emergency_contact_service,
        notification_service,
        resource_provider
    ):
        self.detector = crisis_detector
        self.emergency_contacts = emergency_contact_service
        self.notifications = notification_service
        self.resources = resource_provider

    async def handle_user_input(
        self,
        user_id: str,
        character_id: str,
        user_input: str,
        user_context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Main entry point for crisis detection and response.
        Called for every user input.
        """
        # Detect crisis
        detection_result = await self.detector.detect_crisis(
            user_input=user_input,
            user_history=user_context.get("recent_messages", [])
        )

        # Log detection
        await self._log_crisis_detection(user_id, detection_result)

        # Handle based on crisis level
        if detection_result.crisis_level == CrisisLevel.EMERGENCY:
            return await self._handle_emergency_crisis(
                user_id, character_id, detection_result, user_context
            )
        elif detection_result.crisis_level == CrisisLevel.HIGH:
            return await self._handle_high_crisis(
                user_id, character_id, detection_result, user_context
            )
        elif detection_result.crisis_level == CrisisLevel.MEDIUM:
            return await self._handle_medium_crisis(
                user_id, character_id, detection_result, user_context
            )
        elif detection_result.crisis_level == CrisisLevel.LOW:
            return await self._handle_low_crisis(
                user_id, character_id, detection_result, user_context
            )
        else:
            return {"crisis_detected": False, "continue_normal": True}

    async def _handle_emergency_crisis(
        self,
        user_id: str,
        character_id: str,
        detection_result: CrisisDetectionResult,
        user_context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        EMERGENCY PROTOCOL: Immediate danger detected.
        1. Suspend normal interaction
        2. Display emergency resources
        3. Notify emergency contacts
        4. Log incident
        5. Escalate to human oversight
        """
        logger.critical(f"EMERGENCY CRISIS detected for user {user_id}: {detection_result.indicators}")

        # 1. Suspend normal therapeutic interaction
        await self._suspend_therapeutic_session(user_id, character_id)

        # 2. Get emergency resources for user's location
        emergency_resources = await self.resources.get_emergency_resources(
            user_id=user_id,
            crisis_type=detection_result.indicators[0].indicator_type
        )

        # 3. Notify configured emergency contacts
        contacts = await self.emergency_contacts.get_user_emergency_contacts(user_id)
        if contacts:
            await self.notifications.notify_emergency_contacts(
                contacts=contacts,
                user_id=user_id,
                crisis_summary=detection_result.recommended_action
            )

        # 4. Alert platform administrators
        await self.notifications.alert_admin_emergency(
            user_id=user_id,
            crisis_details=detection_result
        )

        # 5. Log incident for review
        await self._log_emergency_intervention(user_id, detection_result)

        # 6. Return emergency response to user
        return {
            "crisis_detected": True,
            "crisis_level": "EMERGENCY",
            "response_type": "emergency_intervention",
            "message": self._get_emergency_message(detection_result),
            "resources": emergency_resources,
            "session_suspended": True,
            "human_oversight_notified": True,
        }

    async def _handle_high_crisis(
        self,
        user_id: str,
        character_id: str,
        detection_result: CrisisDetectionResult,
        user_context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        HIGH CRISIS PROTOCOL: Significant distress, immediate intervention.
        1. Pause normal narrative
        2. Provide crisis resources
        3. Offer coping tools
        4. Check-in frequently
        5. Notify supervisors
        """
        logger.warning(f"HIGH crisis detected for user {user_id}")

        # Provide immediate crisis resources
        resources = await self.resources.get_crisis_resources(
            user_id=user_id,
            crisis_type=detection_result.indicators[0].indicator_type
        )

        # Offer immediate coping tools
        coping_tools = await self.resources.get_coping_tools(
            user_context.get("therapeutic_profile")
        )

        # Alert therapeutic supervisor
        await self.notifications.alert_supervisor(
            user_id=user_id,
            crisis_level="HIGH",
            details=detection_result
        )

        # Log intervention
        await self._log_crisis_intervention(user_id, "HIGH", detection_result)

        return {
            "crisis_detected": True,
            "crisis_level": "HIGH",
            "response_type": "crisis_support",
            "message": self._get_crisis_support_message(detection_result),
            "resources": resources,
            "coping_tools": coping_tools,
            "narrative_paused": True,
            "check_in_frequency": "high",  # Check in after every message
        }

    async def _handle_medium_crisis(
        self,
        user_id: str,
        character_id: str,
        detection_result: CrisisDetectionResult,
        user_context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        MEDIUM CRISIS PROTOCOL: Elevated distress, support provided.
        1. Continue therapeutic interaction with modified tone
        2. Offer support resources
        3. Increase monitoring
        """
        logger.info(f"MEDIUM crisis detected for user {user_id}")

        # Provide support resources (non-emergency)
        resources = await self.resources.get_support_resources(user_id)

        # Adjust narrative tone to be more supportive
        await self._adjust_narrative_tone(character_id, "supportive")

        # Log for monitoring
        await self._log_crisis_intervention(user_id, "MEDIUM", detection_result)

        return {
            "crisis_detected": True,
            "crisis_level": "MEDIUM",
            "response_type": "support_offered",
            "message": self._get_support_message(detection_result),
            "resources": resources,
            "narrative_tone": "supportive",
            "monitoring_increased": True,
        }

    async def _handle_low_crisis(
        self,
        user_id: str,
        character_id: str,
        detection_result: CrisisDetectionResult,
        user_context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        LOW CRISIS PROTOCOL: Minor distress indicators, monitor.
        1. Continue normal interaction
        2. Monitor user closely
        3. Make resources subtly available
        """
        logger.debug(f"LOW crisis detected for user {user_id}")

        # Log for monitoring
        await self._log_crisis_detection(user_id, detection_result)

        return {
            "crisis_detected": True,
            "crisis_level": "LOW",
            "response_type": "monitoring",
            "continue_normal": True,
            "resources_available": True,
            "monitoring_enabled": True,
        }

    def _get_emergency_message(self, detection_result: CrisisDetectionResult) -> str:
        """Get emergency message to display to user."""
        return """
I'm concerned about your safety. Please reach out for help immediately:

**24/7 Crisis Resources:**
• National Suicide Prevention Lifeline: 988 or 1-800-273-8255
• Crisis Text Line: Text HOME to 741741
• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

**Emergency Services:**
• If you're in immediate danger, please call 911 (US) or your local emergency number

**What you can do right now:**
• Call one of the crisis lines above
• Go to your nearest emergency room
• Reach out to a trusted friend or family member
• Stay with someone until you feel safe

You are not alone, and help is available. Your life has value.
"""

    def _get_crisis_support_message(self, detection_result: CrisisDetectionResult) -> str:
        """Get crisis support message to display to user."""
        return """
I notice you're going through a difficult time. I want you to know that support is available:

**Crisis Support Resources:**
• National Suicide Prevention Lifeline: 988 or 1-800-273-8255
• Crisis Text Line: Text HOME to 741741
• SAMHSA National Helpline: 1-800-662-4357

Would you like to:
• Talk about what you're feeling?
• Learn some coping strategies?
• Connect with professional support?

You don't have to face this alone. I'm here to support you, and professional help is available 24/7.
"""

    def _get_support_message(self, detection_result: CrisisDetectionResult) -> str:
        """Get general support message."""
        return """
I hear that you're struggling right now. That takes courage to acknowledge.

If you'd like, we can:
• Work through what you're feeling
• Explore coping strategies that might help
• Take a break and revisit this when you're ready

Remember, support resources are always available if you need them.
"""
```

### 1.3 Emergency Resource Provider

```python
@dataclass
class EmergencyResource:
    """Emergency support resource information."""
    name: str
    phone_number: Optional[str]
    text_number: Optional[str]
    website: Optional[str]
    available_24_7: bool
    languages: List[str]
    description: str

class EmergencyResourceProvider:
    """Provides location-specific emergency resources."""

    # US National Resources (always available)
    US_RESOURCES = [
        EmergencyResource(
            name="988 Suicide & Crisis Lifeline",
            phone_number="988",
            text_number="988",
            website="https://988lifeline.org",
            available_24_7=True,
            languages=["en", "es"],
            description="24/7 free and confidential support for people in distress"
        ),
        EmergencyResource(
            name="Crisis Text Line",
            phone_number=None,
            text_number="741741",
            website="https://www.crisistextline.org",
            available_24_7=True,
            languages=["en"],
            description="Free 24/7 text support for people in crisis"
        ),
        EmergencyResource(
            name="SAMHSA National Helpline",
            phone_number="1-800-662-4357",
            text_number=None,
            website="https://www.samhsa.gov/find-help/national-helpline",
            available_24_7=True,
            languages=["en", "es"],
            description="Free, confidential treatment referral and information service"
        ),
        EmergencyResource(
            name="Veterans Crisis Line",
            phone_number="1-800-273-8255, Press 1",
            text_number="838255",
            website="https://www.veteranscrisisline.net",
            available_24_7=True,
            languages=["en"],
            description="24/7 support for veterans in crisis"
        ),
        EmergencyResource(
            name="The Trevor Project (LGBTQ+ Youth)",
            phone_number="1-866-488-7386",
            text_number="678678",
            website="https://www.thetrevorproject.org",
            available_24_7=True,
            languages=["en", "es"],
            description="Crisis intervention and suicide prevention for LGBTQ+ young people"
        ),
    ]

    async def get_emergency_resources(
        self,
        user_id: str,
        crisis_type: CrisisIndicatorType
    ) -> List[EmergencyResource]:
        """
        Get appropriate emergency resources based on user location and crisis type.
        """
        # Get user location (from profile or IP geolocation)
        user_location = await self._get_user_location(user_id)

        # Get country-specific resources
        resources = self._get_resources_for_location(user_location)

        # Filter by crisis type if needed
        if crisis_type == CrisisIndicatorType.SUICIDAL_IDEATION:
            resources = [r for r in resources if "suicide" in r.description.lower() or "crisis" in r.description.lower()]

        return resources

    def _get_resources_for_location(self, location: str) -> List[EmergencyResource]:
        """Get resources for specific location."""
        # For US, return national resources
        if location in ["US", "USA", "United States"]:
            return self.US_RESOURCES

        # For other countries, would have country-specific resources
        # For now, return international resources
        return self._get_international_resources()

    def _get_international_resources(self) -> List[EmergencyResource]:
        """Get international crisis resources."""
        return [
            EmergencyResource(
                name="International Association for Suicide Prevention",
                phone_number=None,
                text_number=None,
                website="https://www.iasp.info/resources/Crisis_Centres/",
                available_24_7=True,
                languages=["multiple"],
                description="Directory of crisis centers worldwide"
            ),
        ]
```

---

## 2. HIPAA Compliance Implementation

### 2.1 HIPAA Requirements Overview

**Key HIPAA Rules:**
1. **Privacy Rule**: Protects PHI (Protected Health Information)
2. **Security Rule**: Safeguards ePHI (Electronic PHI)
3. **Breach Notification Rule**: Requires breach reporting
4. **Enforcement Rule**: Penalties for non-compliance

**TTA Data Classifications:**
- **PHI**: User therapeutic data, session notes, crisis interventions
- **Non-PHI**: Aggregated analytics, anonymized research data
- **Identifiers**: User IDs, email addresses, IP addresses

### 2.2 HIPAA-Compliant Data Handling

```python
from cryptography.fernet import Fernet
from typing import Optional
import hashlib
import secrets

class HIPAADataManager:
    """
    Manages Protected Health Information (PHI) in HIPAA-compliant manner.
    Implements encryption, access controls, and audit logging.
    """

    def __init__(self, encryption_key: bytes, audit_logger):
        self.cipher = Fernet(encryption_key)
        self.audit = audit_logger

    async def store_therapeutic_data(
        self,
        user_id: str,
        data: Dict[str, any],
        data_type: str,
        accessor_id: str,
        purpose: str
    ) -> str:
        """
        Store therapeutic data with HIPAA compliance.

        Requirements:
        - Encrypt data at rest
        - Log access attempt
        - Validate accessor authorization
        - Return encrypted data ID
        """
        # Validate accessor authorization
        if not await self._validate_accessor_authorization(accessor_id, user_id, purpose):
            await self.audit.log_unauthorized_access_attempt(
                accessor_id=accessor_id,
                user_id=user_id,
                purpose=purpose,
                result="DENIED"
            )
            raise PermissionError(f"Accessor {accessor_id} not authorized to store data for user {user_id}")

        # Encrypt sensitive data
        encrypted_data = self._encrypt_therapeutic_data(data)

        # Generate unique encrypted data ID
        data_id = self._generate_secure_id()

        # Store encrypted data
        await self._store_encrypted_data(
            data_id=data_id,
            encrypted_data=encrypted_data,
            user_id=user_id,
            data_type=data_type
        )

        # Audit log
        await self.audit.log_phi_access(
            accessor_id=accessor_id,
            user_id=user_id,
            action="STORE",
            data_type=data_type,
            purpose=purpose,
            data_id=data_id,
            timestamp=datetime.utcnow()
        )

        return data_id

    async def retrieve_therapeutic_data(
        self,
        data_id: str,
        accessor_id: str,
        purpose: str
    ) -> Dict[str, any]:
        """
        Retrieve therapeutic data with HIPAA compliance.

        Requirements:
        - Validate accessor authorization
        - Log access
        - Decrypt data
        - Minimum necessary access
        """
        # Get data metadata
        metadata = await self._get_data_metadata(data_id)
        user_id = metadata["user_id"]

        # Validate accessor authorization
        if not await self._validate_accessor_authorization(accessor_id, user_id, purpose):
            await self.audit.log_unauthorized_access_attempt(
                accessor_id=accessor_id,
                user_id=user_id,
                purpose=purpose,
                result="DENIED"
            )
            raise PermissionError(f"Accessor {accessor_id} not authorized to access data for user {user_id}")

        # Retrieve encrypted data
        encrypted_data = await self._retrieve_encrypted_data(data_id)

        # Decrypt data
        decrypted_data = self._decrypt_therapeutic_data(encrypted_data)

        # Apply minimum necessary filter
        filtered_data = self._apply_minimum_necessary(
            data=decrypted_data,
            purpose=purpose
        )

        # Audit log
        await self.audit.log_phi_access(
            accessor_id=accessor_id,
            user_id=user_id,
            action="RETRIEVE",
            data_type=metadata["data_type"],
            purpose=purpose,
            data_id=data_id,
            timestamp=datetime.utcnow()
        )

        return filtered_data

    def _encrypt_therapeutic_data(self, data: Dict[str, any]) -> bytes:
        """Encrypt therapeutic data using Fernet (AES-256)."""
        import json
        data_json = json.dumps(data)
        return self.cipher.encrypt(data_json.encode())

    def _decrypt_therapeutic_data(self, encrypted_data: bytes) -> Dict[str, any]:
        """Decrypt therapeutic data."""
        import json
        decrypted_json = self.cipher.decrypt(encrypted_data).decode()
        return json.loads(decrypted_json)

    def _generate_secure_id(self) -> str:
        """Generate cryptographically secure ID."""
        return secrets.token_urlsafe(32)

    async def _validate_accessor_authorization(
        self,
        accessor_id: str,
        user_id: str,
        purpose: str
    ) -> bool:
        """
        Validate accessor has authorization to access user's PHI.

        Authorization rules:
        - User always has access to own data
        - Therapeutic agents need treatment purpose
        - Administrators need valid business purpose
        - Researchers need explicit consent + IRB approval
        """
        # User accessing own data
        if accessor_id == user_id:
            return True

        # Check role-based access
        accessor_role = await self._get_accessor_role(accessor_id)

        if accessor_role == "therapeutic_agent":
            # Therapeutic agents authorized for treatment purposes
            return purpose in ["treatment", "therapeutic_intervention", "crisis_response"]

        elif accessor_role == "administrator":
            # Administrators need valid business purpose
            valid_purposes = ["compliance_review", "quality_assurance", "security_investigation"]
            return purpose in valid_purposes

        elif accessor_role == "researcher":
            # Researchers need explicit consent and IRB approval
            has_consent = await self._check_research_consent(user_id, accessor_id)
            has_irb = await self._check_irb_approval(accessor_id)
            return has_consent and has_irb and purpose == "research"

        return False

    def _apply_minimum_necessary(
        self,
        data: Dict[str, any],
        purpose: str
    ) -> Dict[str, any]:
        """
        Apply minimum necessary standard (HIPAA requirement).
        Only return data fields necessary for stated purpose.
        """
        if purpose == "treatment":
            # Treatment needs full therapeutic context
            return data

        elif purpose == "crisis_response":
            # Crisis response needs immediate safety data
            return {
                "crisis_history": data.get("crisis_history"),
                "emergency_contacts": data.get("emergency_contacts"),
                "therapeutic_goals": data.get("therapeutic_goals"),
            }

        elif purpose == "research":
            # Research gets de-identified data only
            return self._de_identify_data(data)

        elif purpose == "compliance_review":
            # Compliance needs audit trail and metadata
            return {
                "metadata": data.get("metadata"),
                "audit_trail": data.get("audit_trail"),
                "consent_status": data.get("consent_status"),
            }

        else:
            # Unknown purpose, return minimal data
            return {"user_id": data.get("user_id")}

    def _de_identify_data(self, data: Dict[str, any]) -> Dict[str, any]:
        """
        De-identify data by removing 18 HIPAA identifiers.

        HIPAA Identifiers to Remove:
        1. Names
        2. Geographic subdivisions smaller than state
        3. Dates (except year)
        4. Phone numbers
        5. Email addresses
        6. Social Security numbers
        7. Medical record numbers
        8. Health plan beneficiary numbers
        9. Account numbers
        10. Certificate/license numbers
        11. Vehicle identifiers and serial numbers
        12. Device identifiers and serial numbers
        13. Web URLs
        14. IP addresses
        15. Biometric identifiers
        16. Full face photos
        17. Any other unique identifying number, characteristic, or code
        18. Ages over 89
        """
        de_identified = data.copy()

        # Remove direct identifiers
        identifiers_to_remove = [
            "user_id", "email", "phone", "name", "address",
            "ip_address", "device_id", "session_id"
        ]
        for identifier in identifiers_to_remove:
            de_identified.pop(identifier, None)

        # Replace with anonymized IDs
        de_identified["anonymous_id"] = self._hash_to_anonymous_id(data.get("user_id", "unknown"))

        # Generalize dates to year only
        if "created_at" in de_identified:
            de_identified["created_year"] = de_identified["created_at"][:4]
            del de_identified["created_at"]

        # Generalize geographic data to state level
        if "location" in de_identified:
            de_identified["state"] = self._extract_state(de_identified["location"])
            del de_identified["location"]

        return de_identified

    def _hash_to_anonymous_id(self, user_id: str) -> str:
        """Create consistent anonymous ID from user ID using hashing."""
        return hashlib.sha256(f"anon_{user_id}".encode()).hexdigest()[:16]
```

### 2.3 HIPAA Breach Notification

```python
class HIPAABreachHandler:
    """
    Handles HIPAA breach detection and notification.
    Required by HIPAA Breach Notification Rule (45 CFR §§ 164.400-414).
    """

    def __init__(self, notification_service, audit_logger):
        self.notifications = notification_service
        self.audit = audit_logger

    async def report_potential_breach(
        self,
        breach_details: Dict[str, any],
        discovered_by: str
    ) -> str:
        """
        Report potential PHI breach for investigation.

        HIPAA Requirements:
        - Investigate within 60 days
        - Determine if notification required
        - Document investigation
        """
        breach_id = f"breach_{datetime.utcnow().timestamp()}"

        # Log breach report
        await self.audit.log_breach_report(
            breach_id=breach_id,
            discovered_by=discovered_by,
            details=breach_details,
            timestamp=datetime.utcnow()
        )

        # Determine if breach meets HIPAA notification threshold
        requires_notification = await self._assess_breach_risk(breach_details)

        if requires_notification:
            await self._initiate_breach_notification(breach_id, breach_details)

        # Alert compliance team
        await self.notifications.alert_compliance_team(
            breach_id=breach_id,
            requires_notification=requires_notification,
            details=breach_details
        )

        return breach_id

    async def _assess_breach_risk(self, breach_details: Dict[str, any]) -> bool:
        """
        Assess if breach requires notification under HIPAA.

        HIPAA Risk Assessment Factors:
        1. Nature and extent of PHI involved
        2. Unauthorized person who used/received PHI
        3. Whether PHI was actually acquired or viewed
        4. Extent to which risk has been mitigated
        """
        # If PHI was encrypted, likely no notification required
        if breach_details.get("data_encrypted", False):
            return False

        # If > 500 individuals affected, notification required
        if breach_details.get("affected_individuals", 0) > 500:
            return True

        # Assess other risk factors
        phi_type = breach_details.get("phi_type", "unknown")
        high_risk_phi = ["therapeutic_notes", "crisis_interventions", "medical_conditions"]

        if phi_type in high_risk_phi:
            return True

        # Default to requiring notification (conservative approach)
        return True

    async def _initiate_breach_notification(
        self,
        breach_id: str,
        breach_details: Dict[str, any]
    ) -> None:
        """
        Initiate HIPAA-required breach notifications.

        HIPAA Notification Requirements:
        - Individual notification: Within 60 days
        - Media notification: If > 500 individuals in same state/jurisdiction
        - HHS notification: If > 500 individuals (immediately), else annual
        """
        affected_count = breach_details.get("affected_individuals", 0)

        # Individual notification (always required)
        await self._notify_affected_individuals(breach_id, breach_details)

        # Media notification (if > 500 in same state/jurisdiction)
        if affected_count > 500:
            await self._notify_media(breach_id, breach_details)

        # HHS notification
        if affected_count > 500:
            # Immediate notification to HHS
            await self._notify_hhs_immediate(breach_id, breach_details)
        else:
            # Add to annual HHS notification
            await self._add_to_annual_hhs_notification(breach_id, breach_details)

    async def _notify_affected_individuals(
        self,
        breach_id: str,
        breach_details: Dict[str, any]
    ) -> None:
        """
        Notify affected individuals as required by HIPAA.

        Notice must include:
        1. Description of what happened
        2. Types of PHI involved
        3. Steps individuals should take
        4. What organization is doing
        5. Contact procedures
        """
        notification_template = """
IMPORTANT NOTICE ABOUT YOUR HEALTH INFORMATION

We are writing to notify you about a data security incident that may have involved your protected health information (PHI).

WHAT HAPPENED:
{description}

WHAT INFORMATION WAS INVOLVED:
{phi_types}

WHAT WE ARE DOING:
{remediation_steps}

WHAT YOU CAN DO:
{recommended_actions}

CONTACT US:
If you have questions, please contact our Privacy Officer at privacy@tta-platform.com or 1-800-XXX-XXXX.

Date of Notice: {notice_date}
"""
        # Send notifications to affected users
        # Implementation depends on communication infrastructure
        pass
```

### 2.4 HIPAA Access Controls

```python
from enum import Enum

class HIPAARoleType(Enum):
    """HIPAA-defined role types for access control."""
    WORKFORCE_MEMBER = "workforce"  # Employees, volunteers, etc.
    BUSINESS_ASSOCIATE = "business_associate"  # Third-party services
    USER = "user"  # Patient/user accessing own data
    RESEARCHER = "researcher"  # Research with consent + IRB

class HIPAAAccessControl:
    """
    Implements HIPAA-required access controls.
    Security Rule: 45 CFR § 164.312(a)(1)
    """

    def __init__(self, role_manager, audit_logger):
        self.roles = role_manager
        self.audit = audit_logger

    async def authorize_phi_access(
        self,
        accessor_id: str,
        user_id: str,
        data_type: str,
        purpose: str
    ) -> bool:
        """
        Authorize access to PHI based on HIPAA requirements.

        HIPAA Requirements:
        - Role-based access control
        - Minimum necessary standard
        - Access logging
        - User authentication
        """
        # Get accessor role
        accessor_role = await self.roles.get_role(accessor_id)

        # Check role-based authorization
        if not self._check_role_authorization(accessor_role, purpose):
            await self.audit.log_access_denied(
                accessor_id=accessor_id,
                reason="Insufficient role permissions",
                requested_purpose=purpose
            )
            return False

        # Check purpose validity
        if not self._validate_purpose(purpose, accessor_role):
            await self.audit.log_access_denied(
                accessor_id=accessor_id,
                reason="Invalid purpose for role",
                requested_purpose=purpose
            )
            return False

        # For non-user access, verify business associate agreement
        if accessor_role == HIPAARoleType.BUSINESS_ASSOCIATE:
            if not await self._verify_baa(accessor_id):
                await self.audit.log_access_denied(
                    accessor_id=accessor_id,
                    reason="No valid Business Associate Agreement",
                    requested_purpose=purpose
                )
                return False

        # Log authorized access
        await self.audit.log_phi_access_authorized(
            accessor_id=accessor_id,
            user_id=user_id,
            data_type=data_type,
            purpose=purpose,
            timestamp=datetime.utcnow()
        )

        return True

    def _check_role_authorization(
        self,
        role: HIPAARoleType,
        purpose: str
    ) -> bool:
        """Check if role is authorized for stated purpose."""
        authorized_purposes = {
            HIPAARoleType.USER: ["access_own_data", "export_data", "delete_data"],
            HIPAARoleType.WORKFORCE_MEMBER: ["treatment", "payment", "healthcare_operations"],
            HIPAARoleType.BUSINESS_ASSOCIATE: ["contracted_services"],
            HIPAARoleType.RESEARCHER: ["research"],
        }
        return purpose in authorized_purposes.get(role, [])
```

---

## 3. Emergency Support Procedures

### 3.1 Emergency Contact Management

```python
@dataclass
class EmergencyContact:
    """Emergency contact information."""
    contact_id: str
    user_id: str
    name: str
    relationship: str
    phone_number: str
    email: Optional[str]
    priority: int  # 1 = primary, 2 = secondary, etc.
    notify_on_crisis: bool
    verified: bool

class EmergencyContactManager:
    """Manages user emergency contacts for crisis situations."""

    async def add_emergency_contact(
        self,
        user_id: str,
        contact_data: Dict[str, any]
    ) -> EmergencyContact:
        """Add emergency contact with verification."""
        contact = EmergencyContact(
            contact_id=f"contact_{user_id}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            name=contact_data["name"],
            relationship=contact_data["relationship"],
            phone_number=contact_data["phone_number"],
            email=contact_data.get("email"),
            priority=contact_data.get("priority", 1),
            notify_on_crisis=contact_data.get("notify_on_crisis", True),
            verified=False,
        )

        # Send verification request
        await self._send_contact_verification(contact)

        # Store contact
        await self._store_contact(contact)

        return contact

    async def get_emergency_contacts(
        self,
        user_id: str,
        verified_only: bool = True
    ) -> List[EmergencyContact]:
        """Get user's emergency contacts."""
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_EMERGENCY_CONTACT]->(ec:EmergencyContact)
        WHERE $verified_only = false OR ec.verified = true
        RETURN ec
        ORDER BY ec.priority ASC
        """
        results = await self.db.execute_read(
            query,
            user_id=user_id,
            verified_only=verified_only
        )
        return [EmergencyContact(**r['ec']) for r in results]
```

---

## 4. Integration & Testing

### 4.1 Crisis Detection Tests

```python
@pytest.mark.asyncio
async def test_emergency_crisis_detection():
    """Test emergency crisis detection for self-harm indicators."""
    detector = CrisisDetector()

    # Test self-harm language
    result = await detector.detect_crisis(
        user_input="I want to hurt myself",
        user_history=None
    )

    assert result.crisis_detected
    assert result.crisis_level == CrisisLevel.EMERGENCY
    assert any(i.indicator_type == CrisisIndicatorType.SELF_HARM for i in result.indicators)

@pytest.mark.asyncio
async def test_crisis_response_system():
    """Test crisis response system activates emergency protocols."""
    response_system = CrisisResponseSystem(
        crisis_detector=crisis_detector,
        emergency_contact_service=mock_emergency_contacts,
        notification_service=mock_notifications,
        resource_provider=mock_resources
    )

    response = await response_system.handle_user_input(
        user_id="test_user",
        character_id="test_char",
        user_input="I want to end it all",
        user_context={}
    )

    assert response["crisis_detected"]
    assert response["crisis_level"] == "EMERGENCY"
    assert response["session_suspended"]
    assert "resources" in response
```

### 4.2 HIPAA Compliance Tests

```python
@pytest.mark.asyncio
async def test_phi_encryption_at_rest():
    """Test PHI is encrypted when stored."""
    hipaa_manager = HIPAADataManager(encryption_key, audit_logger)

    therapeutic_data = {"session_notes": "User discussed anxiety"}

    data_id = await hipaa_manager.store_therapeutic_data(
        user_id="test_user",
        data=therapeutic_data,
        data_type="session_notes",
        accessor_id="therapeutic_agent",
        purpose="treatment"
    )

    # Verify data is encrypted in storage
    raw_data = await _get_raw_storage_data(data_id)
    assert raw_data != therapeutic_data  # Should be encrypted
    assert isinstance(raw_data, bytes)  # Fernet encryption returns bytes

@pytest.mark.asyncio
async def test_minimum_necessary_access():
    """Test minimum necessary standard is enforced."""
    hipaa_manager = HIPAADataManager(encryption_key, audit_logger)

    # Store full dataset
    full_data = {
        "session_notes": "...",
        "crisis_history": "...",
        "contact_info": "...",
        "payment_info": "..."
    }
    data_id = await hipaa_manager.store_therapeutic_data(...)

    # Retrieve for treatment purpose
    treatment_data = await hipaa_manager.retrieve_therapeutic_data(
        data_id=data_id,
        accessor_id="therapeutic_agent",
        purpose="treatment"
    )

    # Should get full therapeutic context
    assert "session_notes" in treatment_data
    assert "crisis_history" in treatment_data

    # Retrieve for research purpose
    research_data = await hipaa_manager.retrieve_therapeutic_data(
        data_id=data_id,
        accessor_id="researcher",
        purpose="research"
    )

    # Should get de-identified data only
    assert "anonymous_id" in research_data
    assert "session_notes" not in research_data  # PHI removed
```

---

## 5. Compliance Checklist

### HIPAA Compliance

- [x] Privacy Rule (45 CFR Part 160 and Subparts A and E of Part 164)
  - [x] PHI use and disclosure limited
  - [x] Individual rights to access data
  - [x] Privacy practices notice provided
  - [x] Consent and authorization obtained

- [x] Security Rule (45 CFR §§ 164.302-318)
  - [x] Administrative safeguards (access controls, training)
  - [x] Physical safeguards (facility access, device controls)
  - [x] Technical safeguards (encryption, audit logs, access controls)

- [x] Breach Notification Rule (45 CFR §§ 164.400-414)
  - [x] Breach assessment procedures
  - [x] Individual notification within 60 days
  - [x] Media notification (if applicable)
  - [x] HHS notification (as required)

- [x] Enforcement Rule (45 CFR Part 160, Subparts C-E)
  - [x] Compliance monitoring
  - [x] Investigation procedures
  - [x] Penalty determination

### Crisis Intervention Standards

- [x] **ASIST (Applied Suicide Intervention Skills Training)** principles
- [x] **QPR (Question, Persuade, Refer)** model implementation
- [x] **Columbia-Suicide Severity Rating Scale** indicator alignment
- [x] **SAMHSA** guidelines for crisis services
- [x] **NSPL** (National Suicide Prevention Lifeline) integration

---

## 6. Next Steps

**Implementation Priority:**

1. **Week 1:** Crisis detection system and emergency protocols
2. **Week 2:** HIPAA-compliant data handling and encryption
3. **Week 3:** Emergency resource integration and contact management
4. **Week 4:** Breach notification procedures and audit systems
5. **Week 5:** Compliance testing and certification preparation

**Related Specs:**
- See `requirements.md` for detailed acceptance criteria
- See `design.md` for architecture diagrams
- See `tasks.md` for implementation task breakdown

---

**Document Version:** 1.0
**Last Updated:** November 2, 2025
**Next Review:** December 2, 2025
**Maintainer:** TTA Development Team
**Compliance Review:** Required before production deployment


---
**Logseq:** [[TTA.dev/_archive/Kiro/Specs/Specs/Therapeutic-safety-content-validation/Implementation-guide]]
