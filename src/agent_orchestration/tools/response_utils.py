"""
Response wrapper utilities for MCP tools (Phase 3 Tool Optimization).

Provides convenience functions and decorators for creating standardized tool responses:
- success_response(): Wrap successful results
- error_response(): Wrap errors
- paginated_response(): Wrap paginated results
- timed_tool_response(): Decorator for automatic timing and wrapping
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

from .response_models import (
    PaginatedData,
    PaginationMetadata,
    ResponseStatus,
    ToolError,
    ToolMetadata,
    ToolResponse,
    ToolSuggestion,
)

T = TypeVar("T")


def success_response(
    data: T,
    tool_name: str,
    tool_version: str,
    execution_time_ms: float,
    suggestions: list[ToolSuggestion] | None = None,
    request_id: str | None = None,
    schema_version: str = "1.0.0",
) -> ToolResponse[T]:
    """
    Create a successful tool response.

    Args:
        data: Response data
        tool_name: Name of the tool
        tool_version: Version of the tool (semver)
        execution_time_ms: Execution time in milliseconds
        suggestions: Optional suggestions for next actions
        request_id: Optional request ID for tracing
        schema_version: Response schema version (default: "1.0.0")

    Returns:
        ToolResponse with status=SUCCESS

    Example:
        >>> response = success_response(
        ...     data={"player_id": "123", "name": "Alice"},
        ...     tool_name="get_player_profile",
        ...     tool_version="1.0.0",
        ...     execution_time_ms=45.2,
        ... )
        >>> response.status
        <ResponseStatus.SUCCESS: 'success'>
    """
    metadata = ToolMetadata(
        tool_name=tool_name,
        tool_version=tool_version,
        execution_time_ms=execution_time_ms,
        request_id=request_id,
    )

    return ToolResponse(
        status=ResponseStatus.SUCCESS,
        data=data,
        metadata=metadata,
        suggestions=suggestions or [],
        schema_version=schema_version,
    )


def error_response(
    error_code: str,
    error_message: str,
    tool_name: str,
    tool_version: str,
    execution_time_ms: float,
    error_details: dict[str, Any] | None = None,
    retry_after_seconds: int | None = None,
    request_id: str | None = None,
    schema_version: str = "1.0.0",
) -> ToolResponse[None]:
    """
    Create an error tool response.

    Args:
        error_code: Error code (e.g., "VALIDATION_ERROR", "TIMEOUT")
        error_message: Human-readable error message
        tool_name: Name of the tool
        tool_version: Version of the tool (semver)
        execution_time_ms: Execution time in milliseconds
        error_details: Optional additional error details
        retry_after_seconds: Optional seconds to wait before retrying
        request_id: Optional request ID for tracing
        schema_version: Response schema version (default: "1.0.0")

    Returns:
        ToolResponse with status=ERROR

    Example:
        >>> response = error_response(
        ...     error_code="NOT_FOUND",
        ...     error_message="Player not found",
        ...     tool_name="get_player_profile",
        ...     tool_version="1.0.0",
        ...     execution_time_ms=12.5,
        ... )
        >>> response.status
        <ResponseStatus.ERROR: 'error'>
    """
    metadata = ToolMetadata(
        tool_name=tool_name,
        tool_version=tool_version,
        execution_time_ms=execution_time_ms,
        request_id=request_id,
    )

    error = ToolError(
        code=error_code,
        message=error_message,
        details=error_details or {},
        retry_after_seconds=retry_after_seconds,
    )

    return ToolResponse(
        status=ResponseStatus.ERROR,
        data=None,
        metadata=metadata,
        error=error,
        schema_version=schema_version,
    )


def paginated_response(
    items: list[T],
    total_count: int | None,
    has_more: bool,
    next_cursor: str | None,
    prev_cursor: str | None,
    page_size: int,
    tool_name: str,
    tool_version: str,
    execution_time_ms: float,
    suggestions: list[ToolSuggestion] | None = None,
    request_id: str | None = None,
    schema_version: str = "1.0.0",
) -> ToolResponse[PaginatedData[T]]:
    """
    Create a paginated tool response.

    Args:
        items: Items in this page
        total_count: Total number of items (if known)
        has_more: Whether more items are available
        next_cursor: Cursor for next page (if has_more)
        prev_cursor: Cursor for previous page (if applicable)
        page_size: Number of items in this page
        tool_name: Name of the tool
        tool_version: Version of the tool (semver)
        execution_time_ms: Execution time in milliseconds
        suggestions: Optional suggestions for next actions
        request_id: Optional request ID for tracing
        schema_version: Response schema version (default: "1.0.0")

    Returns:
        ToolResponse with PaginatedData

    Example:
        >>> response = paginated_response(
        ...     items=[{"id": "1"}, {"id": "2"}],
        ...     total_count=100,
        ...     has_more=True,
        ...     next_cursor="cursor_abc",
        ...     prev_cursor=None,
        ...     page_size=2,
        ...     tool_name="list_players",
        ...     tool_version="1.0.0",
        ...     execution_time_ms=78.3,
        ... )
        >>> response.data.pagination.has_more
        True
    """
    pagination = PaginationMetadata(
        total_count=total_count,
        has_more=has_more,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
        page_size=page_size,
    )

    paginated_data = PaginatedData(items=items, pagination=pagination)

    metadata = ToolMetadata(
        tool_name=tool_name,
        tool_version=tool_version,
        execution_time_ms=execution_time_ms,
        request_id=request_id,
    )

    return ToolResponse(
        status=ResponseStatus.SUCCESS,
        data=paginated_data,
        metadata=metadata,
        suggestions=suggestions or [],
        schema_version=schema_version,
    )


def timed_tool_response(
    tool_name: str,
    tool_version: str,
    schema_version: str = "1.0.0",
) -> Callable:
    """
    Decorator for automatic timing and response wrapping.

    Automatically times function execution and wraps result in ToolResponse.
    Handles both successful results and exceptions.

    Args:
        tool_name: Name of the tool
        tool_version: Version of the tool (semver)
        schema_version: Response schema version (default: "1.0.0")

    Returns:
        Decorator function

    Example:
        >>> @timed_tool_response("get_player_profile", "1.0.0")
        ... async def get_player_profile(player_id: str):
        ...     return {"player_id": player_id, "name": "Alice"}
        >>> # Returns ToolResponse with automatic timing
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> ToolResponse:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time_ms = (time.time() - start_time) * 1000

                return success_response(
                    data=result,
                    tool_name=tool_name,
                    tool_version=tool_version,
                    execution_time_ms=execution_time_ms,
                    schema_version=schema_version,
                )
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000

                return error_response(
                    error_code=type(e).__name__,
                    error_message=str(e),
                    tool_name=tool_name,
                    tool_version=tool_version,
                    execution_time_ms=execution_time_ms,
                    error_details={"exception_type": type(e).__name__},
                    schema_version=schema_version,
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> ToolResponse:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time_ms = (time.time() - start_time) * 1000

                return success_response(
                    data=result,
                    tool_name=tool_name,
                    tool_version=tool_version,
                    execution_time_ms=execution_time_ms,
                    schema_version=schema_version,
                )
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000

                return error_response(
                    error_code=type(e).__name__,
                    error_message=str(e),
                    tool_name=tool_name,
                    tool_version=tool_version,
                    execution_time_ms=execution_time_ms,
                    error_details={"exception_type": type(e).__name__},
                    schema_version=schema_version,
                )

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
