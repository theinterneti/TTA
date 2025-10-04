"""
Validation utilities for player experience data models.
"""

import re
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format and length."""
    if not username or len(username) < 3 or len(username) > 30:
        return False

    # Allow letters, numbers, underscores, and hyphens
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, username))


def validate_character_name(name: str) -> bool:
    """Validate character name format and length."""
    if not name or len(name.strip()) < 2 or len(name) > 50:
        return False

    # Allow letters, spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-Z\s\-']+$"
    return bool(re.match(pattern, name.strip()))


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Returns:
        tuple: (is_valid, list_of_issues)
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        issues.append("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")

    return len(issues) == 0, issues


def validate_therapeutic_intensity(intensity: float) -> bool:
    """Validate therapeutic intensity value."""
    return 0.0 <= intensity <= 1.0


def validate_session_duration(duration_minutes: int) -> bool:
    """Validate session duration."""
    return 10 <= duration_minutes <= 120


def validate_progress_percentage(percentage: float) -> bool:
    """Validate progress percentage value."""
    return 0.0 <= percentage <= 100.0


def validate_rating(rating: float) -> bool:
    """Validate rating value (0.0 to 5.0)."""
    return 0.0 <= rating <= 5.0


def validate_model(model: Any) -> None:
    """
    Validate a data model by calling its __post_init__ method.

    Args:
        model: The data model instance to validate

    Raises:
        ValidationError: If validation fails
    """
    try:
        if hasattr(model, "__post_init__"):
            model.__post_init__()
    except ValueError as e:
        raise ValidationError(str(e)) from e
    except Exception as e:
        raise ValidationError(f"Validation failed: {str(e)}") from e


def sanitize_text_input(text: str, max_length: int | None = None) -> str:
    """
    Sanitize text input by removing potentially harmful content.

    Args:
        text: The text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Remove leading/trailing whitespace
    sanitized = text.strip()

    # Remove null bytes and control characters (except newlines and tabs)
    sanitized = "".join(char for char in sanitized if ord(char) >= 32 or char in "\n\t")

    # Truncate if max_length is specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_therapeutic_topics(topics: list[str]) -> bool:
    """Validate therapeutic topics list."""
    if not isinstance(topics, list):
        return False

    for topic in topics:
        if not isinstance(topic, str) or len(topic.strip()) == 0:
            return False

        if len(topic) > 100:  # Reasonable limit for topic length
            return False

    return True


def validate_crisis_contact_info(contact_info: dict) -> list[str]:
    """
    Validate crisis contact information.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if "primary_contact_phone" in contact_info:
        phone = contact_info["primary_contact_phone"]
        if phone and not re.match(r"^\+?[\d\s\-\(\)]{10,}$", phone):
            errors.append("Invalid primary contact phone format")

    if "therapist_phone" in contact_info:
        phone = contact_info["therapist_phone"]
        if phone and not re.match(r"^\+?[\d\s\-\(\)]{10,}$", phone):
            errors.append("Invalid therapist phone format")

    return errors
