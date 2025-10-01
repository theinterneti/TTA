"""
Enhanced validation schemas for API requests.

This module provides comprehensive Pydantic models with detailed validation,
examples, and documentation for all API endpoints.
"""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ValidationError(Exception):
    """Custom validation error with field information."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


# ============================================================================
# Common Validation Patterns
# ============================================================================

USERNAME_PATTERN = r"^[a-zA-Z0-9_-]+$"
CHARACTER_NAME_PATTERN = r"^[a-zA-Z\s\-']+$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# ============================================================================
# Authentication Schemas
# ============================================================================


class LoginRequestSchema(BaseModel):
    """Login request with username and password."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username for authentication",
        examples=["player123"],
    )
    password: str = Field(
        ..., min_length=8, description="User password", examples=["SecurePass123!"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"username": "player123", "password": "SecurePass123!"}
        }
    )


class TokenResponseSchema(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


# ============================================================================
# Character Validation Schemas
# ============================================================================


class CharacterNameValidator:
    """Validator for character names."""

    @staticmethod
    def validate(name: str) -> str:
        """Validate character name format."""
        if not name or len(name.strip()) < 2:
            raise ValidationError(
                "Character name must be at least 2 characters", "name"
            )
        if len(name) > 50:
            raise ValidationError(
                "Character name must not exceed 50 characters", "name"
            )
        if not re.match(CHARACTER_NAME_PATTERN, name.strip()):
            raise ValidationError(
                "Character name can only contain letters, spaces, hyphens, and apostrophes",
                "name",
            )
        return name.strip()


class AgeRangeValidator:
    """Validator for age ranges."""

    VALID_RANGES = ["child", "teen", "adult", "elder"]

    @staticmethod
    def validate(age_range: str) -> str:
        """Validate age range."""
        if age_range not in AgeRangeValidator.VALID_RANGES:
            raise ValidationError(
                f"Age range must be one of: {', '.join(AgeRangeValidator.VALID_RANGES)}",
                "age_range",
            )
        return age_range


class PersonalityTraitsValidator:
    """Validator for personality traits."""

    @staticmethod
    def validate(traits: list[str]) -> list[str]:
        """Validate personality traits list."""
        if not traits or len(traits) == 0:
            raise ValidationError(
                "At least one personality trait is required", "personality_traits"
            )
        if len(traits) > 10:
            raise ValidationError(
                "Maximum 10 personality traits allowed", "personality_traits"
            )

        validated_traits = []
        for trait in traits:
            trait = trait.strip()
            if len(trait) < 2:
                raise ValidationError(
                    "Each trait must be at least 2 characters", "personality_traits"
                )
            if len(trait) > 50:
                raise ValidationError(
                    "Each trait must not exceed 50 characters", "personality_traits"
                )
            validated_traits.append(trait)

        return validated_traits


# ============================================================================
# Player Validation Schemas
# ============================================================================


class UsernameValidator:
    """Validator for usernames."""

    @staticmethod
    def validate(username: str) -> str:
        """Validate username format."""
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters", "username")
        if len(username) > 50:
            raise ValidationError("Username must not exceed 50 characters", "username")
        if not re.match(USERNAME_PATTERN, username):
            raise ValidationError(
                "Username can only contain letters, numbers, underscores, and hyphens",
                "username",
            )
        return username


class EmailValidator:
    """Validator for email addresses."""

    @staticmethod
    def validate(email: str) -> str:
        """Validate email format."""
        if not email:
            raise ValidationError("Email is required", "email")
        if not re.match(EMAIL_PATTERN, email):
            raise ValidationError("Invalid email format", "email")
        if len(email) > 255:
            raise ValidationError("Email must not exceed 255 characters", "email")
        return email.lower()


class PasswordValidator:
    """Validator for passwords."""

    @staticmethod
    def validate(password: str) -> str:
        """Validate password strength."""
        if not password:
            raise ValidationError("Password is required", "password")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters", "password")
        if len(password) > 128:
            raise ValidationError("Password must not exceed 128 characters", "password")

        # Check for basic password strength
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit",
                "password",
            )

        return password


# ============================================================================
# Therapeutic Profile Validation
# ============================================================================


class TherapeuticGoalValidator:
    """Validator for therapeutic goals."""

    @staticmethod
    def validate_description(description: str) -> str:
        """Validate goal description."""
        if not description or len(description.strip()) < 5:
            raise ValidationError(
                "Goal description must be at least 5 characters", "description"
            )
        if len(description) > 500:
            raise ValidationError(
                "Goal description must not exceed 500 characters", "description"
            )
        return description.strip()

    @staticmethod
    def validate_target_date(target_date: str | None) -> str | None:
        """Validate target date format."""
        if target_date:
            try:
                datetime.fromisoformat(target_date.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError(
                    "Invalid date format. Use ISO 8601 format", "target_date"
                )
        return target_date


class IntensityLevelValidator:
    """Validator for intensity levels."""

    VALID_LEVELS = ["low", "moderate", "high"]

    @staticmethod
    def validate(level: str) -> str:
        """Validate intensity level."""
        if level not in IntensityLevelValidator.VALID_LEVELS:
            raise ValidationError(
                f"Intensity level must be one of: {', '.join(IntensityLevelValidator.VALID_LEVELS)}",
                "preferred_intensity",
            )
        return level


class ReadinessLevelValidator:
    """Validator for readiness levels."""

    VALID_LEVELS = ["not_ready", "considering", "ready", "maintaining"]

    @staticmethod
    def validate(level: str) -> str:
        """Validate readiness level."""
        if level not in ReadinessLevelValidator.VALID_LEVELS:
            raise ValidationError(
                f"Readiness level must be one of: {', '.join(ReadinessLevelValidator.VALID_LEVELS)}",
                "readiness_level",
            )
        return level


# ============================================================================
# Request Validation Helpers
# ============================================================================


class RequestValidator:
    """Helper class for validating API requests."""

    @staticmethod
    def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination parameters."""
        if limit < 1:
            raise ValidationError("Limit must be at least 1", "limit")
        if limit > 100:
            raise ValidationError("Limit must not exceed 100", "limit")
        if offset < 0:
            raise ValidationError("Offset must be non-negative", "offset")
        return limit, offset

    @staticmethod
    def validate_id_format(id_value: str, field_name: str = "id") -> str:
        """Validate ID format."""
        if not id_value or len(id_value.strip()) == 0:
            raise ValidationError(f"{field_name} is required", field_name)
        if len(id_value) > 100:
            raise ValidationError(f"{field_name} is too long", field_name)
        return id_value.strip()


# ============================================================================
# Error Response Schemas
# ============================================================================


class ErrorResponseSchema(BaseModel):
    """Standard error response format."""

    detail: str = Field(..., description="Error message")
    error: str | None = Field(None, description="Error type")
    message: str | None = Field(None, description="User-friendly message")
    field: str | None = Field(None, description="Field that caused the error")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Validation error",
                "error": "ValidationError",
                "message": "Character name must be at least 2 characters",
                "field": "name",
            }
        }
    )


class ValidationErrorResponseSchema(BaseModel):
    """Validation error response with field details."""

    detail: str = Field(..., description="Error message")
    errors: list[dict[str, Any]] = Field(..., description="List of validation errors")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Validation error",
                "errors": [
                    {
                        "field": "name",
                        "message": "Character name must be at least 2 characters",
                        "type": "value_error",
                    }
                ],
            }
        }
    )
