"""
Comprehensive input validation and sanitization system.

This module provides robust input validation, sanitization, and security
checks to protect against various attack vectors including XSS, SQL injection,
and other malicious inputs.
"""

import re
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from re import Pattern
from typing import Any

import bleach

from ..monitoring.logging_config import LogCategory, LogContext, get_logger

logger = get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Severity levels for validation violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InputType(str, Enum):
    """Types of input data."""

    TEXT = "text"
    HTML = "html"
    JSON = "json"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    USERNAME = "username"
    PASSWORD = "password"
    THERAPEUTIC_CONTENT = "therapeutic_content"
    USER_MESSAGE = "user_message"
    SEARCH_QUERY = "search_query"
    FILE_PATH = "file_path"
    SQL_QUERY = "sql_query"


class ValidationError(Exception):
    """Exception raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        severity: ValidationSeverity = ValidationSeverity.MEDIUM,
    ):
        super().__init__(message)
        self.field = field
        self.severity = severity


class SanitizationError(Exception):
    """Exception raised when input sanitization fails."""

    def __init__(self, message: str, original_input: str | None = None):
        super().__init__(message)
        self.original_input = original_input


@dataclass
class ValidationRule:
    """Configuration for input validation rule."""

    name: str
    pattern: Pattern | None = None
    min_length: int | None = None
    max_length: int | None = None
    allowed_chars: str | None = None
    forbidden_chars: str | None = None
    custom_validator: Callable[[str], bool] | None = None
    sanitizer: Callable[[str], str] | None = None
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    error_message: str = "Input validation failed"


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    sanitized_input: str | None = None
    violations: list[dict[str, Any]] = field(default_factory=list)
    severity: ValidationSeverity = ValidationSeverity.LOW

    def add_violation(self, rule_name: str, message: str, severity: ValidationSeverity):
        """Add a validation violation."""
        self.violations.append(
            {
                "rule": rule_name,
                "message": message,
                "severity": severity.value,
                "timestamp": str(datetime.utcnow()),
            }
        )

        # Update overall severity
        if severity.value == "critical" or (
            severity.value == "high" and self.severity.value != "critical"
        ):
            self.severity = severity
        elif severity.value == "medium" and self.severity.value == "low":
            self.severity = severity


class SecurityPatterns:
    """Common security patterns for validation."""

    # XSS patterns
    XSS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"<iframe[^>]*>", re.IGNORECASE),
        re.compile(r"<object[^>]*>", re.IGNORECASE),
        re.compile(r"<embed[^>]*>", re.IGNORECASE),
        re.compile(r"<link[^>]*>", re.IGNORECASE),
        re.compile(r"<meta[^>]*>", re.IGNORECASE),
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        re.compile(
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            re.IGNORECASE,
        ),
        re.compile(r"(\b(OR|AND)\s+\d+\s*=\s*\d+)", re.IGNORECASE),
        re.compile(r"'.*?'", re.IGNORECASE),
        re.compile(r"--.*$", re.MULTILINE),
        re.compile(r"/\*.*?\*/", re.DOTALL),
        re.compile(r";\s*(DROP|DELETE|INSERT|UPDATE)", re.IGNORECASE),
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        re.compile(r"[;&|`$(){}[\]<>]"),
        re.compile(
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b", re.IGNORECASE
        ),
        re.compile(r"\.\.\/"),
        re.compile(r"\/etc\/passwd"),
        re.compile(r"\/proc\/"),
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"\.\.\/"),
        re.compile(r"\.\.\\"),
        re.compile(r"%2e%2e%2f", re.IGNORECASE),
        re.compile(r"%2e%2e%5c", re.IGNORECASE),
        re.compile(r"\/etc\/"),
        re.compile(r"\/proc\/"),
        re.compile(r"\/sys\/"),
    ]

    # LDAP injection patterns
    LDAP_INJECTION_PATTERNS = [
        re.compile(r"[()&|!*]"),
        re.compile(r"\\[0-9a-fA-F]{2}"),
    ]


class InputValidator:
    """Main input validation and sanitization class."""

    def __init__(self):
        self.rules: dict[InputType, list[ValidationRule]] = {}
        self.security_patterns = SecurityPatterns()
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Set up default validation rules for different input types."""

        # Text input rules
        self.rules[InputType.TEXT] = [
            ValidationRule(
                name="length_check",
                min_length=1,
                max_length=10000,
                error_message="Text length must be between 1 and 10000 characters",
            ),
            ValidationRule(
                name="xss_check",
                custom_validator=self._check_xss,
                severity=ValidationSeverity.HIGH,
                error_message="Potential XSS attack detected",
            ),
            ValidationRule(
                name="sql_injection_check",
                custom_validator=self._check_sql_injection,
                severity=ValidationSeverity.CRITICAL,
                error_message="Potential SQL injection detected",
            ),
        ]

        # HTML input rules
        self.rules[InputType.HTML] = [
            ValidationRule(
                name="html_sanitization",
                sanitizer=self._sanitize_html,
                error_message="HTML content sanitized",
            ),
            ValidationRule(
                name="malicious_html_check",
                custom_validator=self._check_malicious_html,
                severity=ValidationSeverity.HIGH,
                error_message="Malicious HTML content detected",
            ),
        ]

        # Email validation rules
        self.rules[InputType.EMAIL] = [
            ValidationRule(
                name="email_format",
                pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
                error_message="Invalid email format",
            ),
            ValidationRule(
                name="email_length",
                max_length=254,
                error_message="Email address too long",
            ),
        ]

        # URL validation rules
        self.rules[InputType.URL] = [
            ValidationRule(
                name="url_format",
                pattern=re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE),
                error_message="Invalid URL format",
            ),
            ValidationRule(
                name="url_scheme_check",
                custom_validator=self._check_url_scheme,
                severity=ValidationSeverity.MEDIUM,
                error_message="Unsafe URL scheme detected",
            ),
        ]

        # Username validation rules
        self.rules[InputType.USERNAME] = [
            ValidationRule(
                name="username_format",
                pattern=re.compile(r"^[a-zA-Z0-9_-]{3,30}$"),
                error_message="Username must be 3-30 characters, alphanumeric, underscore, or hyphen only",
            ),
            ValidationRule(
                name="username_reserved_check",
                custom_validator=self._check_reserved_username,
                error_message="Username is reserved",
            ),
        ]

        # Password validation rules
        self.rules[InputType.PASSWORD] = [
            ValidationRule(
                name="password_strength",
                custom_validator=self._check_password_strength,
                error_message="Password does not meet strength requirements",
            ),
            ValidationRule(
                name="password_length",
                min_length=8,
                max_length=128,
                error_message="Password must be 8-128 characters long",
            ),
        ]

        # Therapeutic content rules
        self.rules[InputType.THERAPEUTIC_CONTENT] = [
            ValidationRule(
                name="therapeutic_safety",
                custom_validator=self._check_therapeutic_safety,
                severity=ValidationSeverity.HIGH,
                error_message="Potentially harmful therapeutic content detected",
            ),
            ValidationRule(
                name="content_length",
                max_length=50000,
                error_message="Therapeutic content too long",
            ),
        ]

        # User message rules
        self.rules[InputType.USER_MESSAGE] = [
            ValidationRule(
                name="message_length", max_length=5000, error_message="Message too long"
            ),
            ValidationRule(
                name="spam_check",
                custom_validator=self._check_spam,
                severity=ValidationSeverity.MEDIUM,
                error_message="Potential spam detected",
            ),
            ValidationRule(
                name="profanity_check",
                custom_validator=self._check_profanity,
                sanitizer=self._sanitize_profanity,
                error_message="Inappropriate language detected",
            ),
        ]

        # File path rules
        self.rules[InputType.FILE_PATH] = [
            ValidationRule(
                name="path_traversal_check",
                custom_validator=self._check_path_traversal,
                severity=ValidationSeverity.CRITICAL,
                error_message="Path traversal attack detected",
            ),
            ValidationRule(
                name="allowed_extensions",
                custom_validator=self._check_file_extension,
                error_message="File extension not allowed",
            ),
        ]

    def validate(
        self,
        input_data: str,
        input_type: InputType,
        field_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate input data against rules for the specified type.

        Args:
            input_data: The input data to validate
            input_type: Type of input data
            field_name: Name of the field being validated
            context: Additional context for validation

        Returns:
            ValidationResult with validation status and sanitized input
        """
        result = ValidationResult(is_valid=True, sanitized_input=input_data)

        if input_type not in self.rules:
            logger.warning(f"No validation rules defined for input type: {input_type}")
            return result

        rules = self.rules[input_type]
        current_input = input_data

        for rule in rules:
            try:
                # Apply validation rule
                rule_result = self._apply_rule(current_input, rule, field_name, context)

                if not rule_result["is_valid"]:
                    result.is_valid = False
                    result.add_violation(
                        rule.name, rule_result["message"], rule.severity
                    )

                    # Log security violation
                    if rule.severity in [
                        ValidationSeverity.HIGH,
                        ValidationSeverity.CRITICAL,
                    ]:
                        logger.warning(
                            f"Security validation violation: {rule_result['message']}",
                            category=LogCategory.SECURITY,
                            context=LogContext(),
                            metadata={
                                "field": field_name,
                                "rule": rule.name,
                                "severity": rule.severity.value,
                                "input_type": input_type.value,
                                "input_preview": (
                                    input_data[:100]
                                    if len(input_data) > 100
                                    else input_data
                                ),
                            },
                        )

                # Apply sanitization if available
                if rule.sanitizer and rule_result.get("sanitized"):
                    current_input = rule_result["sanitized"]
                    result.sanitized_input = current_input

            except Exception as e:
                logger.error(
                    f"Error applying validation rule {rule.name}: {e}",
                    category=LogCategory.ERROR,
                    exc_info=True,
                )
                result.is_valid = False
                result.add_violation(
                    rule.name, f"Validation error: {str(e)}", ValidationSeverity.HIGH
                )

        return result

    def _apply_rule(
        self,
        input_data: str,
        rule: ValidationRule,
        field_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply a single validation rule."""
        result = {"is_valid": True, "message": "", "sanitized": None}

        # Length checks
        if rule.min_length is not None and len(input_data) < rule.min_length:
            result["is_valid"] = False
            result["message"] = (
                f"Input too short (minimum {rule.min_length} characters)"
            )
            return result

        if rule.max_length is not None and len(input_data) > rule.max_length:
            result["is_valid"] = False
            result["message"] = f"Input too long (maximum {rule.max_length} characters)"
            return result

        # Pattern matching
        if rule.pattern and not rule.pattern.match(input_data):
            result["is_valid"] = False
            result["message"] = rule.error_message
            return result

        # Character restrictions
        if rule.allowed_chars:
            if not all(c in rule.allowed_chars for c in input_data):
                result["is_valid"] = False
                result["message"] = "Input contains forbidden characters"
                return result

        if rule.forbidden_chars:
            if any(c in rule.forbidden_chars for c in input_data):
                result["is_valid"] = False
                result["message"] = "Input contains forbidden characters"
                return result

        # Custom validation
        if rule.custom_validator:
            try:
                if not rule.custom_validator(input_data):
                    result["is_valid"] = False
                    result["message"] = rule.error_message
                    return result
            except Exception as e:
                result["is_valid"] = False
                result["message"] = f"Custom validation failed: {str(e)}"
                return result

        # Apply sanitization
        if rule.sanitizer:
            try:
                sanitized = rule.sanitizer(input_data)
                result["sanitized"] = sanitized
            except Exception as e:
                logger.error(f"Sanitization failed for rule {rule.name}: {e}")

        return result

    # Security check methods

    def _check_xss(self, input_data: str) -> bool:
        """Check for XSS attack patterns."""
        for pattern in self.security_patterns.XSS_PATTERNS:
            if pattern.search(input_data):
                return False
        return True

    def _check_sql_injection(self, input_data: str) -> bool:
        """Check for SQL injection patterns."""
        for pattern in self.security_patterns.SQL_INJECTION_PATTERNS:
            if pattern.search(input_data):
                return False
        return True

    def _check_malicious_html(self, input_data: str) -> bool:
        """Check for malicious HTML content."""
        # Check for dangerous tags and attributes
        dangerous_tags = [
            "script",
            "iframe",
            "object",
            "embed",
            "link",
            "meta",
            "style",
        ]
        dangerous_attrs = ["onload", "onerror", "onclick", "onmouseover", "onfocus"]

        input_lower = input_data.lower()

        for tag in dangerous_tags:
            if f"<{tag}" in input_lower:
                return False

        for attr in dangerous_attrs:
            if attr in input_lower:
                return False

        return True

    def _check_url_scheme(self, url: str) -> bool:
        """Check URL scheme for safety."""
        safe_schemes = ["http", "https", "ftp", "ftps"]
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.scheme.lower() in safe_schemes
        except Exception:
            return False

    def _check_reserved_username(self, username: str) -> bool:
        """Check if username is reserved."""
        reserved_usernames = [
            "admin",
            "administrator",
            "root",
            "system",
            "api",
            "www",
            "mail",
            "email",
            "support",
            "help",
            "info",
            "contact",
            "test",
            "demo",
            "guest",
            "anonymous",
            "null",
            "undefined",
        ]
        return username.lower() not in reserved_usernames

    def _check_password_strength(self, password: str) -> bool:
        """Check password strength."""
        # At least 8 characters, one uppercase, one lowercase, one digit
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def _check_therapeutic_safety(self, content: str) -> bool:
        """Check therapeutic content for safety concerns."""
        # Check for harmful content patterns
        harmful_patterns = [
            r"\b(kill|die|suicide|hurt|harm|cut|overdose)\b",
            r"\b(worthless|hopeless|useless|failure)\b",
            r"\b(hate myself|want to die|end it all)\b",
        ]

        content_lower = content.lower()
        for pattern in harmful_patterns:
            if re.search(pattern, content_lower):
                return False

        return True

    def _check_spam(self, message: str) -> bool:
        """Check for spam patterns."""
        spam_indicators = [
            r"(buy now|click here|free money|guaranteed)",
            r"(viagra|cialis|pharmacy)",
            r"(lottery|winner|congratulations)",
            r"(\$\d+|\d+\$)",  # Money amounts
        ]

        message_lower = message.lower()
        spam_score = 0

        for pattern in spam_indicators:
            if re.search(pattern, message_lower):
                spam_score += 1

        # Also check for excessive capitalization
        if len(message) > 10:
            caps_ratio = sum(1 for c in message if c.isupper()) / len(message)
            if caps_ratio > 0.7:
                spam_score += 1

        return spam_score < 2

    def _check_profanity(self, text: str) -> bool:
        """Check for profanity (simplified implementation)."""
        # This is a simplified implementation
        # In production, use a comprehensive profanity filter library
        profanity_words = ["damn", "hell", "shit", "fuck", "bitch", "ass", "bastard"]

        text_lower = text.lower()
        for word in profanity_words:
            if word in text_lower:
                return False

        return True

    def _check_path_traversal(self, path: str) -> bool:
        """Check for path traversal attacks."""
        for pattern in self.security_patterns.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(path):
                return False
        return True

    def _check_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        allowed_extensions = [".txt", ".pdf", ".doc", ".docx", ".jpg", ".png", ".gif"]

        import os

        _, ext = os.path.splitext(filename.lower())
        return ext in allowed_extensions

    # Sanitization methods

    def _sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content."""
        allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "ol",
            "ul",
            "li",
            "h1",
            "h2",
            "h3",
        ]
        allowed_attributes = {}

        return bleach.clean(
            html_content, tags=allowed_tags, attributes=allowed_attributes, strip=True
        )

    def _sanitize_profanity(self, text: str) -> str:
        """Sanitize profanity from text."""
        profanity_words = ["damn", "hell", "shit", "fuck", "bitch", "ass", "bastard"]

        sanitized = text
        for word in profanity_words:
            # Replace with asterisks, keeping first letter
            replacement = word[0] + "*" * (len(word) - 1)
            sanitized = re.sub(
                rf"\b{re.escape(word)}\b", replacement, sanitized, flags=re.IGNORECASE
            )

        return sanitized

    def add_custom_rule(self, input_type: InputType, rule: ValidationRule):
        """Add a custom validation rule."""
        if input_type not in self.rules:
            self.rules[input_type] = []

        self.rules[input_type].append(rule)

    def remove_rule(self, input_type: InputType, rule_name: str):
        """Remove a validation rule."""
        if input_type in self.rules:
            self.rules[input_type] = [
                rule for rule in self.rules[input_type] if rule.name != rule_name
            ]


class SecurityValidator:
    """High-level security validator with threat detection."""

    def __init__(self):
        self.input_validator = InputValidator()
        self.threat_patterns = self._load_threat_patterns()

    def _load_threat_patterns(self) -> dict[str, list[Pattern]]:
        """Load threat detection patterns."""
        return {
            "xss": SecurityPatterns.XSS_PATTERNS,
            "sql_injection": SecurityPatterns.SQL_INJECTION_PATTERNS,
            "command_injection": SecurityPatterns.COMMAND_INJECTION_PATTERNS,
            "path_traversal": SecurityPatterns.PATH_TRAVERSAL_PATTERNS,
            "ldap_injection": SecurityPatterns.LDAP_INJECTION_PATTERNS,
        }

    def validate_and_sanitize(
        self, input_data: str, input_type: InputType, field_name: str | None = None
    ) -> ValidationResult:
        """Validate and sanitize input with comprehensive security checks."""
        # First, run standard validation
        result = self.input_validator.validate(input_data, input_type, field_name)

        # Then run additional security checks
        security_result = self._run_security_checks(input_data)

        # Merge results
        if not security_result["is_secure"]:
            result.is_valid = False
            for threat in security_result["threats"]:
                result.add_violation(
                    f"security_{threat['type']}",
                    f"Security threat detected: {threat['description']}",
                    ValidationSeverity.CRITICAL,
                )

        return result

    def _run_security_checks(self, input_data: str) -> dict[str, Any]:
        """Run comprehensive security checks."""
        threats = []

        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if pattern.search(input_data):
                    threats.append(
                        {
                            "type": threat_type,
                            "description": f"Potential {threat_type.replace('_', ' ')} attack",
                            "pattern": pattern.pattern,
                            "severity": "critical",
                        }
                    )

        return {"is_secure": len(threats) == 0, "threats": threats}


# Global validator instance
_global_validator: SecurityValidator | None = None


def get_security_validator() -> SecurityValidator:
    """Get the global security validator instance."""
    global _global_validator
    if _global_validator is None:
        _global_validator = SecurityValidator()
    return _global_validator
