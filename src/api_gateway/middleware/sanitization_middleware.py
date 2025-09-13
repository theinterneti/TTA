"""
Sanitization middleware for the API Gateway.

This module provides comprehensive data sanitization, PII masking,
content filtering, and data privacy protection.
"""

import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..config import get_gateway_settings
from ..models import GatewayRequest, GatewayResponse

logger = logging.getLogger(__name__)


class SanitizationType(Enum):
    """Types of sanitization to perform."""

    PII_MASKING = "pii_masking"
    CONTENT_FILTERING = "content_filtering"
    DATA_REDACTION = "data_redaction"
    FORMAT_NORMALIZATION = "format_normalization"
    THERAPEUTIC_PRIVACY = "therapeutic_privacy"


class PrivacyLevel(Enum):
    """Privacy protection levels."""

    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class SanitizationRule:
    """Individual sanitization rule configuration."""

    name: str
    description: str
    sanitization_type: SanitizationType
    enabled: bool = True
    priority: int = 100  # Lower numbers execute first
    path_patterns: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=lambda: ["*"])

    # PII masking configuration
    mask_email: bool = False
    mask_phone: bool = False
    mask_ssn: bool = False
    mask_credit_card: bool = False
    mask_medical_id: bool = False
    mask_custom_patterns: dict[str, str] = field(default_factory=dict)

    # Content filtering
    filter_profanity: bool = False
    filter_sensitive_terms: bool = False
    blocked_terms: list[str] = field(default_factory=list)
    replacement_text: str = "[FILTERED]"

    # Data redaction
    redact_fields: list[str] = field(default_factory=list)
    redact_patterns: list[str] = field(default_factory=list)
    redaction_replacement: str = "[REDACTED]"

    # Format normalization
    normalize_whitespace: bool = False
    normalize_case: bool = False
    normalize_unicode: bool = False

    # Therapeutic privacy
    therapeutic_content_masking: bool = False
    session_data_protection: bool = False
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD


@dataclass
class SanitizationConfig:
    """Configuration for sanitization middleware."""

    enabled: bool = True
    preserve_data_structure: bool = True
    log_sanitization_actions: bool = True

    # Default privacy settings
    default_privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    therapeutic_privacy_level: PrivacyLevel = PrivacyLevel.HIGH

    # PII detection patterns
    enable_pii_detection: bool = True
    pii_confidence_threshold: float = 0.8

    # Content filtering
    enable_content_filtering: bool = True
    profanity_filtering: bool = False  # Disabled by default for therapeutic content

    # Compliance settings
    hipaa_compliance: bool = True
    gdpr_compliance: bool = True
    coppa_compliance: bool = False


class SanitizationMiddleware:
    """
    Sanitization middleware for comprehensive data privacy protection.

    Provides PII masking, content filtering, data redaction,
    and therapeutic privacy protection.
    """

    def __init__(self, config: SanitizationConfig | None = None):
        """
        Initialize sanitization middleware.

        Args:
            config: Sanitization configuration
        """
        self.config = config or SanitizationConfig()
        self.settings = get_gateway_settings()

        # Sanitization rules
        self.sanitization_rules: list[SanitizationRule] = []
        self._load_default_rules()

        # PII detection patterns
        self.pii_patterns = self._load_pii_patterns()

        # Content filtering patterns
        self.profanity_patterns = self._load_profanity_patterns()
        self.sensitive_terms = self._load_sensitive_terms()

        # Custom sanitization functions
        self.custom_sanitizers: dict[str, Callable] = {}
        self._register_default_sanitizers()

        # Sanitization statistics
        self.sanitization_stats = {
            "total_requests_processed": 0,
            "pii_instances_masked": 0,
            "content_filtered": 0,
            "data_redacted": 0,
        }

    def _load_default_rules(self) -> None:
        """Load default sanitization rules."""
        # PII masking rule
        self.sanitization_rules.append(
            SanitizationRule(
                name="pii_masking",
                description="Mask personally identifiable information",
                sanitization_type=SanitizationType.PII_MASKING,
                priority=10,
                path_patterns=["*"],
                mask_email=True,
                mask_phone=True,
                mask_ssn=True,
                mask_credit_card=True,
                mask_medical_id=True,
            )
        )

        # Therapeutic privacy rule
        self.sanitization_rules.append(
            SanitizationRule(
                name="therapeutic_privacy",
                description="Enhanced privacy protection for therapeutic content",
                sanitization_type=SanitizationType.THERAPEUTIC_PRIVACY,
                priority=5,
                path_patterns=["/api/therapeutic/*", "/api/sessions/*", "/api/chat/*"],
                therapeutic_content_masking=True,
                session_data_protection=True,
                privacy_level=PrivacyLevel.HIGH,
            )
        )

        # Content filtering rule (disabled by default for therapeutic content)
        self.sanitization_rules.append(
            SanitizationRule(
                name="content_filtering",
                description="Filter inappropriate content",
                sanitization_type=SanitizationType.CONTENT_FILTERING,
                priority=20,
                path_patterns=["*"],
                enabled=False,  # Disabled by default
                filter_profanity=True,
                filter_sensitive_terms=True,
            )
        )

        # Data redaction rule
        self.sanitization_rules.append(
            SanitizationRule(
                name="sensitive_data_redaction",
                description="Redact sensitive data fields",
                sanitization_type=SanitizationType.DATA_REDACTION,
                priority=15,
                path_patterns=["*"],
                redact_fields=["password", "secret", "token", "api_key", "private_key"],
            )
        )

    def _load_pii_patterns(self) -> dict[str, re.Pattern]:
        """Load PII detection patterns."""
        return {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
            ),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"),
            "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
            "medical_id": re.compile(
                r"\b(MRN|MR|MEDICAL|PATIENT)[-:\s]?\d+\b", re.IGNORECASE
            ),
            "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            "mac_address": re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b"),
        }

    def _load_profanity_patterns(self) -> list[re.Pattern]:
        """Load profanity detection patterns."""
        # Basic profanity patterns - in a real implementation, this would be more comprehensive
        profanity_words = [
            # This is a minimal set for demonstration
            # In production, use a comprehensive profanity filter library
        ]
        return [re.compile(rf"\b{word}\b", re.IGNORECASE) for word in profanity_words]

    def _load_sensitive_terms(self) -> list[str]:
        """Load sensitive terms that should be filtered."""
        return [
            # Sensitive terms that might need filtering in certain contexts
            # This would be customizable based on therapeutic requirements
        ]

    def _register_default_sanitizers(self) -> None:
        """Register default sanitization functions."""
        self.custom_sanitizers.update(
            {
                "mask_email": self._mask_email,
                "mask_phone": self._mask_phone,
                "mask_ssn": self._mask_ssn,
                "mask_credit_card": self._mask_credit_card,
                "redact_field": self._redact_field,
                "normalize_whitespace": self._normalize_whitespace,
                "therapeutic_content_mask": self._therapeutic_content_mask,
            }
        )

    async def sanitize_request(self, gateway_request: GatewayRequest) -> GatewayRequest:
        """
        Sanitize incoming request data.

        Args:
            gateway_request: Request to sanitize

        Returns:
            GatewayRequest: Sanitized request
        """
        try:
            self.sanitization_stats["total_requests_processed"] += 1

            # Find applicable sanitization rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path, gateway_request.method.value
            )

            # Sort rules by priority
            applicable_rules.sort(key=lambda r: r.priority)

            # Apply sanitization rules
            sanitized_request = gateway_request.copy()

            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                try:
                    sanitized_request = await self._apply_sanitization_rule(
                        sanitized_request, rule
                    )
                except Exception as e:
                    logger.error(f"Error applying sanitization rule '{rule.name}': {e}")
                    # Continue with other rules

            return sanitized_request

        except Exception as e:
            logger.error(f"Error during request sanitization: {e}")
            return gateway_request

    async def sanitize_response(
        self, gateway_response: GatewayResponse, gateway_request: GatewayRequest
    ) -> GatewayResponse:
        """
        Sanitize outgoing response data.

        Args:
            gateway_response: Response to sanitize
            gateway_request: Original request for context

        Returns:
            GatewayResponse: Sanitized response
        """
        try:
            # Find applicable sanitization rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path, gateway_request.method.value
            )

            # Sort rules by priority
            applicable_rules.sort(key=lambda r: r.priority)

            # Apply sanitization rules to response
            sanitized_response = gateway_response.copy()

            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                try:
                    sanitized_response = await self._apply_sanitization_rule(
                        sanitized_response, rule, is_response=True
                    )
                except Exception as e:
                    logger.error(
                        f"Error applying sanitization rule '{rule.name}' to response: {e}"
                    )
                    # Continue with other rules

            return sanitized_response

        except Exception as e:
            logger.error(f"Error during response sanitization: {e}")
            return gateway_response

    def _find_applicable_rules(self, path: str, method: str) -> list[SanitizationRule]:
        """Find sanitization rules applicable to the request."""
        applicable_rules = []

        for rule in self.sanitization_rules:
            # Check method match
            if rule.methods != ["*"] and method not in rule.methods:
                continue

            # Check path pattern match
            if rule.path_patterns:
                path_match = False
                for pattern in rule.path_patterns:
                    if pattern == "*" or re.match(pattern.replace("*", ".*"), path):
                        path_match = True
                        break
                if not path_match:
                    continue

            applicable_rules.append(rule)

        return applicable_rules

    async def _apply_sanitization_rule(
        self, target: Any, rule: SanitizationRule, is_response: bool = False
    ) -> Any:
        """Apply a single sanitization rule to request or response."""

        if rule.sanitization_type == SanitizationType.PII_MASKING:
            target = await self._apply_pii_masking(target, rule)

        elif rule.sanitization_type == SanitizationType.CONTENT_FILTERING:
            target = await self._apply_content_filtering(target, rule)

        elif rule.sanitization_type == SanitizationType.DATA_REDACTION:
            target = await self._apply_data_redaction(target, rule)

        elif rule.sanitization_type == SanitizationType.FORMAT_NORMALIZATION:
            target = await self._apply_format_normalization(target, rule)

        elif rule.sanitization_type == SanitizationType.THERAPEUTIC_PRIVACY:
            target = await self._apply_therapeutic_privacy(target, rule)

        return target

    async def _apply_pii_masking(self, target: Any, rule: SanitizationRule) -> Any:
        """Apply PII masking to target data."""
        if not hasattr(target, "body") or not target.body:
            return target

        try:
            # Parse body data
            if isinstance(target.body, str):
                body_data = json.loads(target.body)
                body_is_string = True
            else:
                body_data = (
                    target.body.copy() if isinstance(target.body, dict) else target.body
                )
                body_is_string = False

            # Apply PII masking
            if isinstance(body_data, dict):
                body_data = self._mask_pii_in_dict(body_data, rule)
            elif isinstance(body_data, str):
                body_data = self._mask_pii_in_text(body_data, rule)

            # Update target body
            target.body = json.dumps(body_data) if body_is_string else body_data

        except json.JSONDecodeError:
            # Handle non-JSON content
            if isinstance(target.body, str):
                target.body = self._mask_pii_in_text(target.body, rule)
        except Exception as e:
            logger.error(f"Error applying PII masking: {e}")

        return target

    def _mask_pii_in_dict(
        self, data: dict[str, Any], rule: SanitizationRule
    ) -> dict[str, Any]:
        """Recursively mask PII in dictionary data."""
        masked_data = {}

        for key, value in data.items():
            if isinstance(value, dict):
                masked_data[key] = self._mask_pii_in_dict(value, rule)
            elif isinstance(value, list):
                masked_data[key] = [
                    (
                        self._mask_pii_in_dict(item, rule)
                        if isinstance(item, dict)
                        else (
                            self._mask_pii_in_text(str(item), rule)
                            if isinstance(item, str)
                            else item
                        )
                    )
                    for item in value
                ]
            elif isinstance(value, str):
                masked_data[key] = self._mask_pii_in_text(value, rule)
            else:
                masked_data[key] = value

        return masked_data

    def _mask_pii_in_text(self, text: str, rule: SanitizationRule) -> str:
        """Mask PII patterns in text content."""
        masked_text = text

        # Apply PII masking based on rule configuration
        if rule.mask_email and "email" in self.pii_patterns:
            masked_text = self.pii_patterns["email"].sub(self._mask_email, masked_text)
            self.sanitization_stats["pii_instances_masked"] += len(
                self.pii_patterns["email"].findall(text)
            )

        if rule.mask_phone and "phone" in self.pii_patterns:
            masked_text = self.pii_patterns["phone"].sub(
                self._mask_phone_match, masked_text
            )
            self.sanitization_stats["pii_instances_masked"] += len(
                self.pii_patterns["phone"].findall(text)
            )

        if rule.mask_ssn and "ssn" in self.pii_patterns:
            masked_text = self.pii_patterns["ssn"].sub("***-**-****", masked_text)
            self.sanitization_stats["pii_instances_masked"] += len(
                self.pii_patterns["ssn"].findall(text)
            )

        if rule.mask_credit_card and "credit_card" in self.pii_patterns:
            masked_text = self.pii_patterns["credit_card"].sub(
                "****-****-****-****", masked_text
            )
            self.sanitization_stats["pii_instances_masked"] += len(
                self.pii_patterns["credit_card"].findall(text)
            )

        if rule.mask_medical_id and "medical_id" in self.pii_patterns:
            masked_text = self.pii_patterns["medical_id"].sub("MRN: ****", masked_text)
            self.sanitization_stats["pii_instances_masked"] += len(
                self.pii_patterns["medical_id"].findall(text)
            )

        # Apply custom pattern masking
        for pattern_name, replacement in rule.mask_custom_patterns.items():
            if pattern_name in self.pii_patterns:
                masked_text = self.pii_patterns[pattern_name].sub(
                    replacement, masked_text
                )

        return masked_text

    async def _apply_content_filtering(
        self, target: Any, rule: SanitizationRule
    ) -> Any:
        """Apply content filtering to target data."""
        if not hasattr(target, "body") or not target.body:
            return target

        try:
            # Parse body data
            if isinstance(target.body, str):
                body_data = json.loads(target.body)
                body_is_string = True
            else:
                body_data = (
                    target.body.copy() if isinstance(target.body, dict) else target.body
                )
                body_is_string = False

            # Apply content filtering
            if isinstance(body_data, dict):
                body_data = self._filter_content_in_dict(body_data, rule)
            elif isinstance(body_data, str):
                body_data = self._filter_content_in_text(body_data, rule)

            # Update target body
            target.body = json.dumps(body_data) if body_is_string else body_data

        except json.JSONDecodeError:
            # Handle non-JSON content
            if isinstance(target.body, str):
                target.body = self._filter_content_in_text(target.body, rule)
        except Exception as e:
            logger.error(f"Error applying content filtering: {e}")

        return target

    def _filter_content_in_dict(
        self, data: dict[str, Any], rule: SanitizationRule
    ) -> dict[str, Any]:
        """Recursively filter content in dictionary data."""
        filtered_data = {}

        for key, value in data.items():
            if isinstance(value, dict):
                filtered_data[key] = self._filter_content_in_dict(value, rule)
            elif isinstance(value, list):
                filtered_data[key] = [
                    (
                        self._filter_content_in_dict(item, rule)
                        if isinstance(item, dict)
                        else (
                            self._filter_content_in_text(str(item), rule)
                            if isinstance(item, str)
                            else item
                        )
                    )
                    for item in value
                ]
            elif isinstance(value, str):
                filtered_data[key] = self._filter_content_in_text(value, rule)
            else:
                filtered_data[key] = value

        return filtered_data

    def _filter_content_in_text(self, text: str, rule: SanitizationRule) -> str:
        """Filter inappropriate content in text."""
        filtered_text = text

        # Filter profanity
        if rule.filter_profanity:
            for pattern in self.profanity_patterns:
                if pattern.search(filtered_text):
                    filtered_text = pattern.sub(rule.replacement_text, filtered_text)
                    self.sanitization_stats["content_filtered"] += 1

        # Filter blocked terms
        for term in rule.blocked_terms:
            if term.lower() in filtered_text.lower():
                filtered_text = re.sub(
                    re.escape(term),
                    rule.replacement_text,
                    filtered_text,
                    flags=re.IGNORECASE,
                )
                self.sanitization_stats["content_filtered"] += 1

        # Filter sensitive terms
        if rule.filter_sensitive_terms:
            for term in self.sensitive_terms:
                if term.lower() in filtered_text.lower():
                    filtered_text = re.sub(
                        re.escape(term),
                        rule.replacement_text,
                        filtered_text,
                        flags=re.IGNORECASE,
                    )
                    self.sanitization_stats["content_filtered"] += 1

        return filtered_text

    async def _apply_data_redaction(self, target: Any, rule: SanitizationRule) -> Any:
        """Apply data redaction to target data."""
        if not hasattr(target, "body") or not target.body:
            return target

        try:
            # Parse body data
            if isinstance(target.body, str):
                body_data = json.loads(target.body)
                body_is_string = True
            else:
                body_data = (
                    target.body.copy() if isinstance(target.body, dict) else target.body
                )
                body_is_string = False

            # Apply data redaction
            if isinstance(body_data, dict):
                body_data = self._redact_data_in_dict(body_data, rule)

            # Update target body
            target.body = json.dumps(body_data) if body_is_string else body_data

        except json.JSONDecodeError:
            pass  # Skip redaction for non-JSON content
        except Exception as e:
            logger.error(f"Error applying data redaction: {e}")

        return target

    def _redact_data_in_dict(
        self, data: dict[str, Any], rule: SanitizationRule
    ) -> dict[str, Any]:
        """Recursively redact sensitive data in dictionary."""
        redacted_data = {}

        for key, value in data.items():
            # Check if field should be redacted
            if key.lower() in [field.lower() for field in rule.redact_fields]:
                redacted_data[key] = rule.redaction_replacement
                self.sanitization_stats["data_redacted"] += 1
            elif isinstance(value, dict):
                redacted_data[key] = self._redact_data_in_dict(value, rule)
            elif isinstance(value, list):
                redacted_data[key] = [
                    (
                        self._redact_data_in_dict(item, rule)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                # Check redaction patterns
                redacted_value = value
                if isinstance(value, str):
                    for pattern in rule.redact_patterns:
                        if re.search(pattern, value, re.IGNORECASE):
                            redacted_value = rule.redaction_replacement
                            self.sanitization_stats["data_redacted"] += 1
                            break

                redacted_data[key] = redacted_value

        return redacted_data

    async def _apply_format_normalization(
        self, target: Any, rule: SanitizationRule
    ) -> Any:
        """Apply format normalization to target data."""
        # Implementation for format normalization
        return target

    async def _apply_therapeutic_privacy(
        self, target: Any, rule: SanitizationRule
    ) -> Any:
        """Apply therapeutic privacy protection."""
        # Enhanced privacy protection for therapeutic content
        if rule.therapeutic_content_masking:
            target = await self._apply_pii_masking(target, rule)

        return target

    def _mask_email(self, match) -> str:
        """Mask email address."""
        email = match.group(0)
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    def _mask_phone_match(self, match) -> str:
        """Mask phone number from regex match."""
        return "***-***-****"

    def _mask_phone(self, phone: str) -> str:
        """Mask phone number."""
        return "***-***-****"

    def _mask_ssn(self, ssn: str) -> str:
        """Mask Social Security Number."""
        return "***-**-****"

    def _mask_credit_card(self, cc: str) -> str:
        """Mask credit card number."""
        return "****-****-****-****"

    def _redact_field(self, value: Any) -> str:
        """Redact sensitive field value."""
        return "[REDACTED]"

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        return re.sub(r"\s+", " ", text.strip())

    def _therapeutic_content_mask(self, content: str) -> str:
        """Apply therapeutic-specific content masking."""
        # Apply enhanced masking for therapeutic content
        masked_content = content

        # Mask potential therapeutic identifiers
        therapeutic_patterns = {
            r"\bsession[-_]?\d+\b": "SESSION-***",
            r"\btherapist[-_]?\w+\b": "THERAPIST-***",
            r"\bcounselor[-_]?\w+\b": "COUNSELOR-***",
        }

        for pattern, replacement in therapeutic_patterns.items():
            masked_content = re.sub(
                pattern, replacement, masked_content, flags=re.IGNORECASE
            )

        return masked_content

    def add_sanitization_rule(self, rule: SanitizationRule) -> None:
        """Add a custom sanitization rule."""
        self.sanitization_rules.append(rule)

    def remove_sanitization_rule(self, rule_name: str) -> bool:
        """Remove a sanitization rule by name."""
        for i, rule in enumerate(self.sanitization_rules):
            if rule.name == rule_name:
                del self.sanitization_rules[i]
                return True
        return False

    def register_custom_sanitizer(self, name: str, function: Callable) -> None:
        """Register a custom sanitization function."""
        self.custom_sanitizers[name] = function

    def get_sanitization_stats(self) -> dict[str, Any]:
        """Get sanitization statistics."""
        return {
            "total_rules": len(self.sanitization_rules),
            "enabled_rules": len([r for r in self.sanitization_rules if r.enabled]),
            "rules_by_type": {
                stype.value: len(
                    [r for r in self.sanitization_rules if r.sanitization_type == stype]
                )
                for stype in SanitizationType
            },
            "processing_stats": self.sanitization_stats.copy(),
            "custom_sanitizers": len(self.custom_sanitizers),
            "config": {
                "default_privacy_level": self.config.default_privacy_level.value,
                "therapeutic_privacy_level": self.config.therapeutic_privacy_level.value,
                "pii_detection_enabled": self.config.enable_pii_detection,
                "content_filtering_enabled": self.config.enable_content_filtering,
                "hipaa_compliance": self.config.hipaa_compliance,
                "gdpr_compliance": self.config.gdpr_compliance,
            },
        }
