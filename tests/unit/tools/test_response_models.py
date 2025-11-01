"""
Unit tests for response models (Phase 3 Tool Optimization).

Tests all response models with >90% coverage target.
"""

import pytest
from pydantic import ValidationError

from src.agent_orchestration.tools.response_models import (
    PaginatedData,
    PaginationMetadata,
    ResponseStatus,
    SuggestionType,
    ToolError,
    ToolMetadata,
    ToolResponse,
    ToolSuggestion,
    check_schema_compatibility,
    get_json_schema,
)


class TestToolMetadata:
    """Tests for ToolMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = ToolMetadata(
            tool_name="get_player_profile",
            tool_version="1.0.0",
            execution_time_ms=45.2,
        )
        assert metadata.tool_name == "get_player_profile"
        assert metadata.tool_version == "1.0.0"
        assert metadata.execution_time_ms == 45.2
        assert metadata.request_id is None

    def test_invalid_version(self):
        """Test invalid semver version."""
        with pytest.raises(ValidationError):
            ToolMetadata(
                tool_name="test",
                tool_version="invalid",
                execution_time_ms=10.0,
            )

    def test_negative_execution_time(self):
        """Test negative execution time is rejected."""
        with pytest.raises(ValidationError):
            ToolMetadata(
                tool_name="test",
                tool_version="1.0.0",
                execution_time_ms=-10.0,
            )


class TestToolError:
    """Tests for ToolError model."""

    def test_valid_error(self):
        """Test creating valid error."""
        error = ToolError(
            code="NOT_FOUND",
            message="Player not found",
            details={"player_id": "123"},
        )
        assert error.code == "NOT_FOUND"
        assert error.message == "Player not found"
        assert error.details == {"player_id": "123"}
        assert error.retry_after_seconds is None

    def test_with_retry_after(self):
        """Test error with retry_after_seconds."""
        error = ToolError(
            code="RATE_LIMIT",
            message="Too many requests",
            retry_after_seconds=60,
        )
        assert error.retry_after_seconds == 60


class TestToolSuggestion:
    """Tests for ToolSuggestion model."""

    def test_valid_suggestion(self):
        """Test creating valid suggestion."""
        suggestion = ToolSuggestion(
            type=SuggestionType.RELATED_TOOL,
            description="Use list_player_sessions to see all sessions",
            tool_name="list_player_sessions",
            parameters={"player_id": "123"},
        )
        assert suggestion.type == SuggestionType.RELATED_TOOL
        assert suggestion.tool_name == "list_player_sessions"


class TestPaginationMetadata:
    """Tests for PaginationMetadata model."""

    def test_valid_pagination(self):
        """Test creating valid pagination metadata."""
        pagination = PaginationMetadata(
            total_count=100,
            has_more=True,
            next_cursor="abc.def",
            page_size=50,
        )
        assert pagination.total_count == 100
        assert pagination.has_more is True
        assert pagination.next_cursor == "abc.def"

    def test_invalid_cursor_format(self):
        """Test invalid cursor format is rejected."""
        with pytest.raises(ValidationError):
            PaginationMetadata(
                has_more=True,
                next_cursor="invalid_no_dot",
                page_size=50,
            )

    def test_page_size_limits(self):
        """Test page_size limits."""
        with pytest.raises(ValidationError):
            PaginationMetadata(has_more=False, page_size=0)

        with pytest.raises(ValidationError):
            PaginationMetadata(has_more=False, page_size=101)


class TestPaginatedData:
    """Tests for PaginatedData model."""

    def test_valid_paginated_data(self):
        """Test creating valid paginated data."""
        pagination = PaginationMetadata(
            has_more=True, next_cursor="abc.def", page_size=2
        )
        data = PaginatedData(
            items=[{"id": "1"}, {"id": "2"}], pagination=pagination
        )
        assert len(data.items) == 2
        assert data.pagination.has_more is True


class TestToolResponse:
    """Tests for ToolResponse model."""

    def test_success_response(self):
        """Test creating successful response."""
        metadata = ToolMetadata(
            tool_name="test", tool_version="1.0.0", execution_time_ms=10.0
        )
        response = ToolResponse(
            status=ResponseStatus.SUCCESS,
            data={"result": "ok"},
            metadata=metadata,
        )
        assert response.status == ResponseStatus.SUCCESS
        assert response.data == {"result": "ok"}
        assert response.error is None

    def test_error_response(self):
        """Test creating error response."""
        metadata = ToolMetadata(
            tool_name="test", tool_version="1.0.0", execution_time_ms=10.0
        )
        error = ToolError(code="ERROR", message="Failed")
        response = ToolResponse(
            status=ResponseStatus.ERROR,
            data=None,
            metadata=metadata,
            error=error,
        )
        assert response.status == ResponseStatus.ERROR
        assert response.data is None
        assert response.error is not None

    def test_error_without_error_field_fails(self):
        """Test error status requires error field."""
        metadata = ToolMetadata(
            tool_name="test", tool_version="1.0.0", execution_time_ms=10.0
        )
        with pytest.raises(ValidationError):
            ToolResponse(
                status=ResponseStatus.ERROR,
                data=None,
                metadata=metadata,
                error=None,
            )

    def test_error_with_data_fails(self):
        """Test error status should not have data."""
        metadata = ToolMetadata(
            tool_name="test", tool_version="1.0.0", execution_time_ms=10.0
        )
        error = ToolError(code="ERROR", message="Failed")
        with pytest.raises(ValidationError):
            ToolResponse(
                status=ResponseStatus.ERROR,
                data={"should": "not_be_here"},
                metadata=metadata,
                error=error,
            )


class TestSchemaCompatibility:
    """Tests for schema version compatibility checking."""

    def test_compatible_versions(self):
        """Test compatible version combinations."""
        assert check_schema_compatibility("1.2.3", "1.0.0") is True
        assert check_schema_compatibility("1.0.5", "1.0.0") is True
        assert check_schema_compatibility("1.1.0", "1.0.0") is True

    def test_incompatible_major_version(self):
        """Test incompatible major versions."""
        assert check_schema_compatibility("2.0.0", "1.0.0") is False
        assert check_schema_compatibility("1.0.0", "2.0.0") is False

    def test_incompatible_minor_version(self):
        """Test incompatible minor versions (older)."""
        assert check_schema_compatibility("1.0.0", "1.2.0") is False

    def test_invalid_version_format(self):
        """Test invalid version formats."""
        assert check_schema_compatibility("invalid", "1.0.0") is False
        assert check_schema_compatibility("1.0.0", "invalid") is False


class TestJSONSchema:
    """Tests for JSON Schema generation."""

    def test_get_json_schema(self):
        """Test JSON Schema generation."""
        schema = get_json_schema(ToolMetadata)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "tool_name" in schema["properties"]

