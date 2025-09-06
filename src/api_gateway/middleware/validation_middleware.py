"""
Enhanced validation middleware for the API Gateway.

This module provides comprehensive input validation, schema validation,
and data integrity checking with therapeutic safety considerations.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import HTTPException, status
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate
from pydantic import ValidationError

from ..config import get_gateway_settings
from ..models import GatewayRequest

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Types of validation to perform."""

    SCHEMA = "schema"
    FORMAT = "format"
    CONTENT = "content"
    SIZE = "size"
    THERAPEUTIC = "therapeutic"
    SECURITY = "security"


class ValidationSeverity(Enum):
    """Validation error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Individual validation rule configuration."""

    name: str
    description: str
    validation_type: ValidationType
    severity: ValidationSeverity
    enabled: bool = True
    path_patterns: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=lambda: ["*"])

    # Schema validation
    json_schema: dict[str, Any] | None = None

    # Format validation
    format_patterns: dict[str, str] = field(default_factory=dict)

    # Content validation
    required_fields: list[str] = field(default_factory=list)
    forbidden_fields: list[str] = field(default_factory=list)
    max_field_length: dict[str, int] = field(default_factory=dict)

    # Size validation
    max_body_size: int | None = None
    max_array_length: int | None = None
    max_object_depth: int | None = None

    # Therapeutic validation
    therapeutic_required_fields: list[str] = field(default_factory=list)
    crisis_detection_fields: list[str] = field(default_factory=list)

    # Security validation
    sql_injection_check: bool = False
    xss_check: bool = False
    path_traversal_check: bool = False


@dataclass
class ValidationConfig:
    """Configuration for validation middleware."""

    enabled: bool = True
    fail_fast: bool = False  # Stop on first validation error
    log_validation_errors: bool = True
    return_detailed_errors: bool = False  # Return detailed errors to client
    therapeutic_validation_required: bool = True

    # Default validation rules
    default_rules: list[ValidationRule] = field(default_factory=list)

    # Validation limits
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_json_depth: int = 10
    max_array_length: int = 1000
    max_string_length: int = 10000

    # Therapeutic validation settings
    require_user_context: bool = True
    validate_therapeutic_sessions: bool = True
    crisis_content_validation: bool = True


class ValidationMiddleware:
    """
    Enhanced validation middleware for comprehensive input validation.

    Provides schema validation, format checking, content validation,
    size limits, and therapeutic safety validation.
    """

    def __init__(self, config: ValidationConfig | None = None):
        """
        Initialize validation middleware.

        Args:
            config: Validation configuration
        """
        self.config = config or ValidationConfig()
        self.settings = get_gateway_settings()

        # Validation rules
        self.validation_rules: list[ValidationRule] = []
        self._load_default_rules()

        # Security patterns
        self.sql_injection_patterns = self._load_sql_injection_patterns()
        self.xss_patterns = self._load_xss_patterns()
        self.path_traversal_patterns = self._load_path_traversal_patterns()

        # Therapeutic validation patterns
        self.crisis_keywords = self._load_crisis_keywords()
        self.therapeutic_field_patterns = self._load_therapeutic_patterns()

    def _load_default_rules(self) -> None:
        """Load default validation rules."""
        # Basic JSON schema validation
        self.validation_rules.append(
            ValidationRule(
                name="basic_json_validation",
                description="Basic JSON structure validation",
                validation_type=ValidationType.SCHEMA,
                severity=ValidationSeverity.ERROR,
                path_patterns=["*"],
                methods=["POST", "PUT", "PATCH"],
                max_body_size=self.config.max_request_size,
                max_object_depth=self.config.max_json_depth,
            )
        )

        # Security validation
        self.validation_rules.append(
            ValidationRule(
                name="security_validation",
                description="Security threat detection",
                validation_type=ValidationType.SECURITY,
                severity=ValidationSeverity.CRITICAL,
                path_patterns=["*"],
                sql_injection_check=True,
                xss_check=True,
                path_traversal_check=True,
            )
        )

        # Therapeutic content validation
        self.validation_rules.append(
            ValidationRule(
                name="therapeutic_validation",
                description="Therapeutic content and safety validation",
                validation_type=ValidationType.THERAPEUTIC,
                severity=ValidationSeverity.WARNING,
                path_patterns=["/api/therapeutic/*", "/api/sessions/*", "/api/chat/*"],
                crisis_detection_fields=["message", "content", "description", "notes"],
            )
        )

        # Size validation
        self.validation_rules.append(
            ValidationRule(
                name="size_validation",
                description="Request and content size validation",
                validation_type=ValidationType.SIZE,
                severity=ValidationSeverity.ERROR,
                path_patterns=["*"],
                max_body_size=self.config.max_request_size,
                max_array_length=self.config.max_array_length,
                max_field_length={
                    "message": self.config.max_string_length,
                    "content": self.config.max_string_length,
                    "description": self.config.max_string_length,
                },
            )
        )

    def _load_sql_injection_patterns(self) -> list[re.Pattern]:
        """Load SQL injection detection patterns."""
        patterns = [
            re.compile(
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                re.IGNORECASE,
            ),
            re.compile(r"(\b(OR|AND)\s+\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"('|\"|;|--|\*|\/\*|\*\/)", re.IGNORECASE),
            re.compile(r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)", re.IGNORECASE),
        ]
        return patterns

    def _load_xss_patterns(self) -> list[re.Pattern]:
        """Load XSS detection patterns."""
        patterns = [
            re.compile(
                r"<\s*script[^>]*>.*?</\s*script\s*>", re.IGNORECASE | re.DOTALL
            ),
            re.compile(
                r"<\s*iframe[^>]*>.*?</\s*iframe\s*>", re.IGNORECASE | re.DOTALL
            ),
            re.compile(r"javascript\s*:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"<\s*img[^>]*src\s*=\s*[\"']?javascript:", re.IGNORECASE),
        ]
        return patterns

    def _load_path_traversal_patterns(self) -> list[re.Pattern]:
        """Load path traversal detection patterns."""
        patterns = [
            re.compile(r"\.\.\/"),
            re.compile(r"\.\.\\"),
            re.compile(r"%2e%2e%2f", re.IGNORECASE),
            re.compile(r"%2e%2e%5c", re.IGNORECASE),
        ]
        return patterns

    def _load_crisis_keywords(self) -> list[str]:
        """Load crisis detection keywords."""
        return [
            # Self-harm indicators
            "suicide",
            "kill myself",
            "end it all",
            "hurt myself",
            "self-harm",
            "cutting",
            "overdose",
            "jump off",
            "hang myself",
            "want to die",
            # Crisis emotional states
            "hopeless",
            "worthless",
            "can't go on",
            "no point",
            "give up",
            "desperate",
            "trapped",
            "unbearable pain",
            "can't take it",
            # Immediate danger
            "right now",
            "tonight",
            "today",
            "this moment",
            "immediately",
            "planning to",
            "going to",
            "about to",
            # Substance abuse crisis
            "overdosed",
            "too many pills",
            "drinking too much",
            "can't stop using",
            "relapsed",
            "using again",
            "high right now",
        ]

    def _load_therapeutic_patterns(self) -> dict[str, re.Pattern]:
        """Load therapeutic field validation patterns."""
        return {
            "session_id": re.compile(r"^[a-zA-Z0-9\-_]{8,64}$"),
            "user_id": re.compile(r"^[a-zA-Z0-9\-_]{8,64}$"),
            "mood_score": re.compile(r"^([1-9]|10)$"),  # 1-10 scale
            "anxiety_level": re.compile(r"^(low|medium|high|severe)$", re.IGNORECASE),
            "crisis_level": re.compile(
                r"^(none|low|medium|high|critical)$", re.IGNORECASE
            ),
        }

    async def validate_request(self, gateway_request: GatewayRequest) -> GatewayRequest:
        """
        Validate incoming request against configured rules.

        Args:
            gateway_request: Request to validate

        Returns:
            GatewayRequest: Validated request

        Raises:
            HTTPException: If validation fails
        """
        validation_errors = []

        try:
            # Find applicable validation rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path, gateway_request.method.value
            )

            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                try:
                    # Perform validation based on rule type
                    if rule.validation_type == ValidationType.SCHEMA:
                        await self._validate_schema(gateway_request, rule)
                    elif rule.validation_type == ValidationType.FORMAT:
                        await self._validate_format(gateway_request, rule)
                    elif rule.validation_type == ValidationType.CONTENT:
                        await self._validate_content(gateway_request, rule)
                    elif rule.validation_type == ValidationType.SIZE:
                        await self._validate_size(gateway_request, rule)
                    elif rule.validation_type == ValidationType.THERAPEUTIC:
                        await self._validate_therapeutic(gateway_request, rule)
                    elif rule.validation_type == ValidationType.SECURITY:
                        await self._validate_security(gateway_request, rule)

                except ValidationError as e:
                    error_info = {
                        "rule": rule.name,
                        "type": rule.validation_type.value,
                        "severity": rule.severity.value,
                        "message": str(e),
                        "path": gateway_request.path,
                    }
                    validation_errors.append(error_info)

                    if self.config.log_validation_errors:
                        logger.warning(f"Validation error: {error_info}")

                    # Stop on first error if fail_fast is enabled
                    if self.config.fail_fast and rule.severity in [
                        ValidationSeverity.ERROR,
                        ValidationSeverity.CRITICAL,
                    ]:
                        break

            # Handle validation errors
            if validation_errors:
                await self._handle_validation_errors(validation_errors, gateway_request)

            return gateway_request

        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            if self.config.fail_fast:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Validation processing error",
                ) from e
            return gateway_request

    def _find_applicable_rules(self, path: str, method: str) -> list[ValidationRule]:
        """Find validation rules applicable to the request."""
        applicable_rules = []

        for rule in self.validation_rules:
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

    async def _validate_schema(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate request against JSON schema."""
        if not rule.json_schema or not request.body:
            return

        try:
            if isinstance(request.body, str):
                body_data = json.loads(request.body)
            else:
                body_data = request.body

            validate(instance=body_data, schema=rule.json_schema)

        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}") from e
        except JsonSchemaValidationError as e:
            raise ValidationError(f"Schema validation failed: {e.message}") from e

    async def _validate_format(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate request format patterns."""
        if not rule.format_patterns or not request.body:
            return

        try:
            if isinstance(request.body, str):
                body_data = json.loads(request.body)
            else:
                body_data = request.body

            for field, pattern in rule.format_patterns.items():
                if field in body_data:
                    value = str(body_data[field])
                    if not re.match(pattern, value):
                        raise ValidationError(
                            f"Field '{field}' format validation failed"
                        )

        except json.JSONDecodeError:
            pass  # Skip format validation for non-JSON content

    async def _validate_content(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate request content requirements."""
        if not request.body:
            return

        try:
            if isinstance(request.body, str):
                body_data = json.loads(request.body)
            else:
                body_data = request.body

            # Check required fields
            for field in rule.required_fields:
                if field not in body_data:
                    raise ValidationError(f"Required field '{field}' is missing")

            # Check forbidden fields
            for field in rule.forbidden_fields:
                if field in body_data:
                    raise ValidationError(f"Forbidden field '{field}' is present")

            # Check field length limits
            for field, max_length in rule.max_field_length.items():
                if field in body_data:
                    value = str(body_data[field])
                    if len(value) > max_length:
                        raise ValidationError(
                            f"Field '{field}' exceeds maximum length of {max_length}"
                        )

        except json.JSONDecodeError:
            pass  # Skip content validation for non-JSON content

    async def _validate_size(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate request size limits."""
        # Check body size
        if rule.max_body_size and request.body:
            body_size = len(str(request.body).encode("utf-8"))
            if body_size > rule.max_body_size:
                raise ValidationError(
                    f"Request body size {body_size} exceeds limit of {rule.max_body_size}"
                )

        # Check JSON structure limits
        if request.body:
            try:
                if isinstance(request.body, str):
                    body_data = json.loads(request.body)
                else:
                    body_data = request.body

                # Check object depth
                if rule.max_object_depth:
                    depth = self._calculate_json_depth(body_data)
                    if depth > rule.max_object_depth:
                        raise ValidationError(
                            f"JSON depth {depth} exceeds limit of {rule.max_object_depth}"
                        )

                # Check array lengths
                if rule.max_array_length:
                    self._check_array_lengths(body_data, rule.max_array_length)

            except json.JSONDecodeError:
                pass  # Skip size validation for non-JSON content

    async def _validate_therapeutic(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate therapeutic content and safety requirements."""
        if not request.body:
            return

        try:
            if isinstance(request.body, str):
                body_data = json.loads(request.body)
            else:
                body_data = request.body

            # Check therapeutic required fields
            for field in rule.therapeutic_required_fields:
                if field not in body_data:
                    raise ValidationError(f"Therapeutic field '{field}' is required")

            # Crisis detection in specified fields
            crisis_detected = False
            crisis_content = []

            for field in rule.crisis_detection_fields:
                if field in body_data:
                    content = str(body_data[field]).lower()
                    for keyword in self.crisis_keywords:
                        if keyword in content:
                            crisis_detected = True
                            crisis_content.append(
                                f"Field '{field}' contains crisis indicator: '{keyword}'"
                            )

            if crisis_detected:
                # Log crisis detection
                logger.critical(
                    "Crisis content detected in request",
                    extra={
                        "path": request.path,
                        "user_id": (
                            request.auth_context.get("user_id")
                            if request.auth_context
                            else None
                        ),
                        "crisis_indicators": crisis_content,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # Mark request as crisis mode
                if request.auth_context:
                    request.auth_context["crisis_mode"] = True

                # Don't fail validation, but ensure proper handling
                logger.warning(
                    "Crisis content detected - request marked for priority handling"
                )

            # Validate therapeutic field patterns
            for field, pattern in self.therapeutic_field_patterns.items():
                if field in body_data:
                    value = str(body_data[field])
                    if not pattern.match(value):
                        raise ValidationError(
                            f"Therapeutic field '{field}' has invalid format"
                        )

        except json.JSONDecodeError:
            pass  # Skip therapeutic validation for non-JSON content

    async def _validate_security(
        self, request: GatewayRequest, rule: ValidationRule
    ) -> None:
        """Validate request for security threats."""
        content_to_check = []

        # Collect content to check
        if request.body:
            if isinstance(request.body, str):
                content_to_check.append(request.body)
            else:
                content_to_check.append(json.dumps(request.body))

        # Check query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                content_to_check.append(f"{key}={value}")

        # Check headers (selected ones)
        security_relevant_headers = ["user-agent", "referer", "x-forwarded-for"]
        if request.headers:
            for header, value in request.headers.items():
                if header.lower() in security_relevant_headers:
                    content_to_check.append(value)

        # Perform security checks
        for content in content_to_check:
            if rule.sql_injection_check:
                await self._check_sql_injection(content)

            if rule.xss_check:
                await self._check_xss(content)

            if rule.path_traversal_check:
                await self._check_path_traversal(content)

    async def _check_sql_injection(self, content: str) -> None:
        """Check for SQL injection patterns."""
        for pattern in self.sql_injection_patterns:
            if pattern.search(content):
                raise ValidationError(
                    f"Potential SQL injection detected: {pattern.pattern}"
                )

    async def _check_xss(self, content: str) -> None:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if pattern.search(content):
                raise ValidationError(
                    f"Potential XSS attack detected: {pattern.pattern}"
                )

    async def _check_path_traversal(self, content: str) -> None:
        """Check for path traversal patterns."""
        for pattern in self.path_traversal_patterns:
            if pattern.search(content):
                raise ValidationError(
                    f"Potential path traversal attack detected: {pattern.pattern}"
                )

    def _calculate_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of a JSON object."""
        if not isinstance(obj, dict | list):
            return current_depth

        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._calculate_json_depth(value, current_depth + 1)
                for value in obj.values()
            )

        if isinstance(obj, list):
            if not obj:
                return current_depth
            return max(
                self._calculate_json_depth(item, current_depth + 1) for item in obj
            )

        return current_depth

    def _check_array_lengths(self, obj: Any, max_length: int) -> None:
        """Recursively check array lengths in JSON object."""
        if isinstance(obj, list):
            if len(obj) > max_length:
                raise ValidationError(
                    f"Array length {len(obj)} exceeds limit of {max_length}"
                )
            for item in obj:
                self._check_array_lengths(item, max_length)
        elif isinstance(obj, dict):
            for value in obj.values():
                self._check_array_lengths(value, max_length)

    async def _handle_validation_errors(
        self, errors: list[dict[str, Any]], request: GatewayRequest
    ) -> None:
        """Handle validation errors based on severity and configuration."""
        critical_errors = [e for e in errors if e["severity"] == "critical"]
        error_level_errors = [e for e in errors if e["severity"] == "error"]

        if critical_errors:
            # Critical errors always result in request rejection
            error_detail = "Critical validation errors detected"
            if self.config.return_detailed_errors:
                error_detail = {"errors": critical_errors}

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
            )

        if error_level_errors and self.config.fail_fast:
            # Error level errors result in rejection if fail_fast is enabled
            error_detail = "Validation errors detected"
            if self.config.return_detailed_errors:
                error_detail = {"errors": error_level_errors}

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
            )

        # Log all errors for monitoring
        if errors:
            logger.warning(
                f"Validation issues detected for request {request.path}",
                extra={
                    "validation_errors": errors,
                    "user_id": (
                        request.auth_context.get("user_id")
                        if request.auth_context
                        else None
                    ),
                    "path": request.path,
                    "method": request.method.value,
                },
            )

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.validation_rules.append(rule)

    def remove_validation_rule(self, rule_name: str) -> bool:
        """Remove a validation rule by name."""
        for i, rule in enumerate(self.validation_rules):
            if rule.name == rule_name:
                del self.validation_rules[i]
                return True
        return False

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics."""
        return {
            "total_rules": len(self.validation_rules),
            "enabled_rules": len([r for r in self.validation_rules if r.enabled]),
            "rules_by_type": {
                vtype.value: len(
                    [r for r in self.validation_rules if r.validation_type == vtype]
                )
                for vtype in ValidationType
            },
            "rules_by_severity": {
                severity.value: len(
                    [r for r in self.validation_rules if r.severity == severity]
                )
                for severity in ValidationSeverity
            },
            "config": {
                "fail_fast": self.config.fail_fast,
                "max_request_size": self.config.max_request_size,
                "therapeutic_validation": self.config.therapeutic_validation_required,
            },
        }
