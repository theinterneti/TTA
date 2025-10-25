"""
Standardized response models for MCP tools (Phase 3 Tool Optimization).

Provides consistent, versioned response schemas for all tools including:
- Generic response wrapper with metadata
- Error handling models
- Pagination support
- Tool suggestions
- Schema versioning and compatibility
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

# Generic type for response data
T = TypeVar("T")


class ResponseStatus(str, Enum):
    """Status of tool execution."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  # Partial success (e.g., some items failed)


class ToolMetadata(BaseModel):
    """Metadata about tool execution."""

    tool_name: str = Field(..., description="Name of the tool that generated this response")
    tool_version: str = Field(..., description="Version of the tool (semver)")
    execution_time_ms: float = Field(..., ge=0.0, description="Execution time in milliseconds")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of response")
    request_id: str | None = Field(default=None, description="Optional request ID for tracing")

    @field_validator("tool_version")
    @classmethod
    def _validate_version(cls, v: str) -> str:
        """Validate semver format."""
        parts = v.split(".")
        if not (2 <= len(parts) <= 3):
            raise ValueError("tool_version must be in semver format (e.g., 1.0.0)")
        for p in parts:
            if not p.isdigit():
                raise ValueError("tool_version segments must be numeric")
        return v


class ToolError(BaseModel):
    """Error information for failed tool execution."""

    code: str = Field(..., description="Error code (e.g., 'VALIDATION_ERROR', 'TIMEOUT')")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    retry_after_seconds: int | None = Field(
        default=None, ge=0, description="Seconds to wait before retrying (for rate limits)"
    )


class SuggestionType(str, Enum):
    """Type of tool suggestion."""

    RELATED_TOOL = "related_tool"  # Suggest a related tool
    NEXT_ACTION = "next_action"  # Suggest next logical action
    ALTERNATIVE = "alternative"  # Suggest alternative approach
    OPTIMIZATION = "optimization"  # Suggest optimization


class ToolSuggestion(BaseModel):
    """Suggestion for next action or related tool."""

    type: SuggestionType = Field(..., description="Type of suggestion")
    description: str = Field(
        ..., min_length=1, max_length=512, description="Description of suggestion"
    )
    tool_name: str | None = Field(
        default=None, description="Name of suggested tool (if applicable)"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Suggested parameters for the tool"
    )


class PaginationMetadata(BaseModel):
    """Metadata for paginated responses."""

    total_count: int | None = Field(
        default=None, ge=0, description="Total number of items (if known)"
    )
    has_more: bool = Field(..., description="Whether more items are available")
    next_cursor: str | None = Field(default=None, description="Cursor for next page (if has_more)")
    prev_cursor: str | None = Field(
        default=None, description="Cursor for previous page (if applicable)"
    )
    page_size: int = Field(..., ge=1, le=100, description="Number of items in this page")

    @field_validator("next_cursor", "prev_cursor")
    @classmethod
    def _validate_cursor(cls, v: str | None) -> str | None:
        """Validate cursor format (base64.signature)."""
        if v is None:
            return v
        if "." not in v:
            raise ValueError("cursor must be in format 'base64_data.signature'")
        parts = v.split(".")
        if len(parts) != 2:
            raise ValueError("cursor must have exactly one '.' separator")
        return v


class PaginatedData(BaseModel, Generic[T]):
    """Generic paginated data container."""

    items: list[T] = Field(..., description="Items in this page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class ToolResponse(BaseModel, Generic[T]):
    """
    Generic standardized response wrapper for all MCP tools.

    Provides consistent structure with:
    - Status (success/error/partial)
    - Data (generic type T)
    - Metadata (execution info)
    - Suggestions (next actions)
    - Error (if applicable)
    - Schema version (for compatibility)
    """

    status: ResponseStatus = Field(..., description="Execution status")
    data: T | None = Field(default=None, description="Response data (type varies by tool)")
    metadata: ToolMetadata = Field(..., description="Execution metadata")
    suggestions: list[ToolSuggestion] = Field(
        default_factory=list, description="Suggestions for next actions"
    )
    error: ToolError | None = Field(default=None, description="Error information (if status=error)")
    schema_version: str = Field(default="1.0.0", description="Response schema version (semver)")

    @field_validator("schema_version")
    @classmethod
    def _validate_schema_version(cls, v: str) -> str:
        """Validate semver format."""
        parts = v.split(".")
        if not (2 <= len(parts) <= 3):
            raise ValueError("schema_version must be in semver format (e.g., 1.0.0)")
        for p in parts:
            if not p.isdigit():
                raise ValueError("schema_version segments must be numeric")
        return v

    def model_post_init(self, __context: Any) -> None:
        """Validate response consistency after initialization."""
        # Error must be present if status is ERROR
        if self.status == ResponseStatus.ERROR and self.error is None:
            raise ValueError("error field is required when status=ERROR")
        # Data should be None if status is ERROR
        if self.status == ResponseStatus.ERROR and self.data is not None:
            raise ValueError("data should be None when status=ERROR")


def check_schema_compatibility(response_version: str, expected_version: str) -> bool:
    """
    Check if response schema version is compatible with expected version.

    Uses semver compatibility rules:
    - Major version must match (breaking changes)
    - Minor version can be >= (backward compatible additions)
    - Patch version ignored (bug fixes)

    Args:
        response_version: Schema version from response (e.g., "1.2.3")
        expected_version: Expected schema version (e.g., "1.0.0")

    Returns:
        True if compatible, False otherwise

    Examples:
        >>> check_schema_compatibility("1.2.3", "1.0.0")  # Compatible (same major, newer minor)
        True
        >>> check_schema_compatibility("2.0.0", "1.0.0")  # Incompatible (different major)
        False
        >>> check_schema_compatibility("1.0.5", "1.2.0")  # Incompatible (older minor)
        False
    """
    try:
        resp_parts = [int(p) for p in response_version.split(".")]
        exp_parts = [int(p) for p in expected_version.split(".")]

        # Pad to 3 parts if needed
        while len(resp_parts) < 3:
            resp_parts.append(0)
        while len(exp_parts) < 3:
            exp_parts.append(0)

        resp_major, resp_minor, _ = resp_parts[:3]
        exp_major, exp_minor, _ = exp_parts[:3]

        # Major version must match
        if resp_major != exp_major:
            return False

        # Minor version must be >= (backward compatible)
        if resp_minor < exp_minor:
            return False

        return True

    except (ValueError, IndexError):
        # Invalid version format
        return False


def get_json_schema(model_class: type[BaseModel]) -> dict[str, Any]:
    """
    Get JSON Schema for a Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        JSON Schema dictionary

    Example:
        >>> schema = get_json_schema(ToolMetadata)
        >>> schema["type"]
        'object'
    """
    return model_class.model_json_schema()
