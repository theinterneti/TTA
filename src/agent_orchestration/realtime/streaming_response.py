"""

# Logseq: [[TTA.dev/Agent_orchestration/Realtime/Streaming_response]]
Streaming response system for long-running agent orchestration workflows.

This module provides streaming capabilities for workflows that need to provide
real-time updates and intermediate results to clients during execution.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

from fastapi.responses import StreamingResponse

from .progressive_feedback import OperationProgress, ProgressiveFeedbackManager

logger = logging.getLogger(__name__)


class StreamingWorkflowResponse:
    """Manages streaming responses for long-running workflows."""

    def __init__(
        self,
        workflow_id: str,
        workflow_type: str,
        user_id: str | None = None,
        feedback_manager: ProgressiveFeedbackManager | None = None,
        chunk_size: int = 1024,
        heartbeat_interval: float = 30.0,
    ):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.user_id = user_id
        self.feedback_manager = feedback_manager
        self.chunk_size = chunk_size
        self.heartbeat_interval = heartbeat_interval

        # Streaming state
        self.is_streaming = False
        self.stream_queue: asyncio.Queue = asyncio.Queue()
        self.completion_event = asyncio.Event()
        self.error_event = asyncio.Event()
        self.error_message: str | None = None

        # Progress tracking
        self.operation_id: str | None = None
        self.last_heartbeat = 0.0

        logger.debug(f"StreamingWorkflowResponse created: {workflow_id}")

    async def start_streaming(self) -> None:
        """Start the streaming response."""
        if self.is_streaming:
            return

        self.is_streaming = True

        # Start operation tracking if feedback manager is available
        if self.feedback_manager:
            self.operation_id = await self.feedback_manager.start_operation(
                operation_type=f"streaming_{self.workflow_type}",
                user_id=self.user_id,
            )

            # Add callback for progress updates
            if self.operation_id:
                self.feedback_manager.add_operation_callback(
                    self.operation_id, self._handle_progress_update
                )

        logger.info(f"Started streaming for workflow: {self.workflow_id}")

    async def send_chunk(
        self, data: str | dict[str, Any], chunk_type: str = "data"
    ) -> None:
        """Send a data chunk to the stream."""
        if not self.is_streaming:
            return

        try:
            # Format chunk
            chunk = self._format_chunk(data, chunk_type)

            # Add to queue
            await self.stream_queue.put(chunk)

        except Exception as e:
            logger.error(f"Error sending chunk: {e}")
            await self.send_error(f"Error sending chunk: {str(e)}")

    async def send_progress(
        self,
        stage: str,
        progress_percentage: float,
        message: str | None = None,
        intermediate_result: dict[str, Any] | None = None,
    ) -> None:
        """Send progress update to the stream."""
        if not self.is_streaming:
            return

        # Update operation progress if available
        if self.feedback_manager and self.operation_id:
            await self.feedback_manager.update_operation_progress(
                self.operation_id,
                stage=stage,
                message=message,
                progress_percentage=progress_percentage,
                intermediate_result=intermediate_result,
            )

        # Send progress chunk
        progress_data = {
            "stage": stage,
            "progress_percentage": progress_percentage,
            "message": message,
            "intermediate_result": intermediate_result,
            "timestamp": asyncio.get_event_loop().time(),
        }

        await self.send_chunk(progress_data, "progress")

    async def send_result(self, result: dict[str, Any]) -> None:
        """Send intermediate or final result to the stream."""
        await self.send_chunk(result, "result")

    async def send_error(
        self, error_message: str, error_details: dict[str, Any] | None = None
    ) -> None:
        """Send error to the stream and mark as failed."""
        self.error_message = error_message

        error_data = {
            "error": error_message,
            "details": error_details,
            "timestamp": asyncio.get_event_loop().time(),
        }

        await self.send_chunk(error_data, "error")

        # Mark operation as failed
        if self.feedback_manager and self.operation_id:
            await self.feedback_manager.fail_operation(
                self.operation_id,
                error_message,
                error_details,
            )

        self.error_event.set()

    async def complete(self, final_result: dict[str, Any] | None = None) -> None:
        """Complete the streaming response."""
        if not self.is_streaming:
            return

        # Send final result if provided
        if final_result:
            await self.send_result(final_result)

        # Send completion chunk
        completion_data = {
            "status": "completed",
            "timestamp": asyncio.get_event_loop().time(),
        }

        await self.send_chunk(completion_data, "completion")

        # Complete operation tracking
        if self.feedback_manager and self.operation_id:
            await self.feedback_manager.complete_operation(
                self.operation_id,
                "Streaming workflow completed",
                final_result,
            )

        self.completion_event.set()
        self.is_streaming = False

        logger.info(f"Completed streaming for workflow: {self.workflow_id}")

    async def generate_stream(self) -> AsyncGenerator[str, None]:
        """Generate the streaming response."""
        try:
            await self.start_streaming()

            # Send initial chunk
            initial_data = {
                "workflow_id": self.workflow_id,
                "workflow_type": self.workflow_type,
                "user_id": self.user_id,
                "started_at": asyncio.get_event_loop().time(),
            }

            yield self._format_chunk(initial_data, "start")

            # Stream chunks until completion or error
            while self.is_streaming:
                try:
                    # Wait for next chunk or timeout for heartbeat
                    chunk = await asyncio.wait_for(
                        self.stream_queue.get(), timeout=self.heartbeat_interval
                    )

                    yield chunk

                    # Check for completion or error
                    if self.completion_event.is_set() or self.error_event.is_set():
                        break

                except TimeoutError:
                    # Send heartbeat
                    heartbeat_data = {
                        "type": "heartbeat",
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                    yield self._format_chunk(heartbeat_data, "heartbeat")

        except Exception as e:
            logger.error(f"Error in stream generation: {e}")
            error_chunk = self._format_chunk(
                {"error": f"Stream generation error: {str(e)}"}, "error"
            )
            yield error_chunk

        finally:
            self.is_streaming = False

    def _format_chunk(self, data: str | dict[str, Any], chunk_type: str) -> str:
        """Format a chunk for streaming."""
        if isinstance(data, str):
            chunk_data = {"content": data}
        else:
            chunk_data = data

        chunk = {
            "type": chunk_type,
            "workflow_id": self.workflow_id,
            "data": chunk_data,
            "timestamp": asyncio.get_event_loop().time(),
        }

        # Format as Server-Sent Events (SSE)
        return f"data: {json.dumps(chunk)}\n\n"

    async def _handle_progress_update(self, operation: OperationProgress) -> None:
        """Handle progress updates from the feedback manager."""
        if not self.is_streaming:
            return

        try:
            progress_data = {
                "operation_id": operation.operation_id,
                "stage": operation.current_stage,
                "progress_percentage": operation.progress_percentage,
                "completed_steps": operation.completed_steps,
                "total_steps": operation.total_steps,
                "estimated_remaining": operation.get_estimated_remaining(),
                "intermediate_results": operation.intermediate_results,
            }

            await self.stream_queue.put(
                self._format_chunk(progress_data, "progress_update")
            )

        except Exception as e:
            logger.error(f"Error handling progress update: {e}")


class StreamingResponseManager:
    """Manages multiple streaming responses."""

    def __init__(self, feedback_manager: ProgressiveFeedbackManager | None = None):
        self.feedback_manager = feedback_manager
        self.active_streams: dict[str, StreamingWorkflowResponse] = {}

        logger.info("StreamingResponseManager initialized")

    def create_streaming_response(
        self,
        workflow_type: str,
        user_id: str | None = None,
        workflow_id: str | None = None,
        **kwargs,
    ) -> StreamingWorkflowResponse:
        """Create a new streaming response."""
        if workflow_id is None:
            workflow_id = uuid4().hex

        stream_response = StreamingWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            user_id=user_id,
            feedback_manager=self.feedback_manager,
            **kwargs,
        )

        self.active_streams[workflow_id] = stream_response

        logger.info(f"Created streaming response: {workflow_id}")
        return stream_response

    def get_streaming_response(
        self, workflow_id: str
    ) -> StreamingWorkflowResponse | None:
        """Get an existing streaming response."""
        return self.active_streams.get(workflow_id)

    async def create_fastapi_streaming_response(
        self,
        workflow_type: str,
        user_id: str | None = None,
        workflow_id: str | None = None,
        media_type: str = "text/plain",
        **kwargs,
    ) -> StreamingResponse:
        """Create a FastAPI StreamingResponse."""
        stream_response = self.create_streaming_response(
            workflow_type=workflow_type,
            user_id=user_id,
            workflow_id=workflow_id,
            **kwargs,
        )

        return StreamingResponse(
            stream_response.generate_stream(),
            media_type=media_type,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Workflow-ID": stream_response.workflow_id,
            },
        )

    async def complete_stream(
        self, workflow_id: str, final_result: dict[str, Any] | None = None
    ) -> bool:
        """Complete a streaming response."""
        stream_response = self.active_streams.get(workflow_id)
        if not stream_response:
            return False

        await stream_response.complete(final_result)
        self.active_streams.pop(workflow_id, None)

        return True

    async def fail_stream(
        self,
        workflow_id: str,
        error_message: str,
        error_details: dict[str, Any] | None = None,
    ) -> bool:
        """Fail a streaming response."""
        stream_response = self.active_streams.get(workflow_id)
        if not stream_response:
            return False

        await stream_response.send_error(error_message, error_details)
        self.active_streams.pop(workflow_id, None)

        return True

    def get_active_streams(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Get information about active streams."""
        streams = []

        for stream in self.active_streams.values():
            if user_id is None or stream.user_id == user_id:
                streams.append(
                    {
                        "workflow_id": stream.workflow_id,
                        "workflow_type": stream.workflow_type,
                        "user_id": stream.user_id,
                        "is_streaming": stream.is_streaming,
                        "operation_id": stream.operation_id,
                    }
                )

        return streams

    def get_statistics(self) -> dict[str, Any]:
        """Get streaming response manager statistics."""
        return {
            "active_streams": len(self.active_streams),
            "streams_by_type": self._get_streams_by_type(),
            "streams_by_user": self._get_streams_by_user(),
        }

    def _get_streams_by_type(self) -> dict[str, int]:
        """Get count of streams by type."""
        counts = {}
        for stream in self.active_streams.values():
            counts[stream.workflow_type] = counts.get(stream.workflow_type, 0) + 1
        return counts

    def _get_streams_by_user(self) -> dict[str, int]:
        """Get count of streams by user."""
        counts = {}
        for stream in self.active_streams.values():
            user_id = stream.user_id or "anonymous"
            counts[user_id] = counts.get(user_id, 0) + 1
        return counts
