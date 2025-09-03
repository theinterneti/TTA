"""
WebSocket monitoring endpoint for the Agent Orchestration service.

Provides real-time monitoring data for agent workflows and system orchestration including:
- Agent status updates and workflow progress events
- System performance metrics and resource utilization
- Workflow execution metrics and completion notifications
- Error reporting and debugging information for agent operations
- Custom application-specific debug events from orchestrated agents
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

import psutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..agents.registry import AgentRegistry
from ..auth.jwt_handler import verify_token
from ..monitoring.agent_monitor import AgentMonitor
from ..orchestration.workflow_manager import WorkflowManager

logger = logging.getLogger(__name__)
router = APIRouter()


class AgentMonitoringEvent(BaseModel):
    """Agent orchestration monitoring event schema."""

    type: str
    timestamp: str
    service_id: str = "agent-orchestration"
    data: dict[str, Any]


class AgentStatusData(BaseModel):
    """Agent status and health data."""

    agent_id: str
    agent_type: str
    status: str  # 'active' | 'idle' | 'error' | 'offline'
    last_activity: str
    performance_metrics: dict[str, float]
    error_count: int
    tasks_completed: int
    current_task: str | None = None


class WorkflowProgressData(BaseModel):
    """Workflow execution progress data."""

    workflow_id: str
    workflow_type: str
    status: str  # 'running' | 'completed' | 'failed' | 'paused'
    progress_percentage: float
    current_step: str
    steps_completed: int
    total_steps: int
    execution_time: float
    timestamp: str


class SystemOrchestrationMetrics(BaseModel):
    """System orchestration performance metrics."""

    active_agents: int
    active_workflows: int
    total_tasks_queued: int
    tasks_per_second: float
    average_task_completion_time: float
    system_load: float
    memory_usage: float
    error_rate: float
    timestamp: str


class AgentOrchestrationMonitoringManager:
    """Manager for Agent Orchestration monitoring WebSocket connections."""

    def __init__(
        self,
        agent_monitor: AgentMonitor,
        workflow_manager: WorkflowManager,
        agent_registry: AgentRegistry,
    ):
        self.connections: dict[str, WebSocket] = {}
        self.authenticated_connections: set[str] = set()
        self.agent_monitor = agent_monitor
        self.workflow_manager = workflow_manager
        self.agent_registry = agent_registry

        # Metrics tracking
        self.orchestration_metrics = {
            "tasks_completed": 0,
            "task_completion_times": [],
            "workflow_executions": 0,
            "error_count": 0,
            "agent_activities": {},
        }

        self._monitoring_task: asyncio.Task | None = None
        self._start_monitoring()

    def _start_monitoring(self):
        """Start background monitoring task."""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background monitoring loop that broadcasts orchestration metrics."""
        consecutive_errors = 0
        max_consecutive_errors = 5

        while True:
            try:
                # Only broadcast if there are active connections
                if not self.connections:
                    await asyncio.sleep(10)  # Longer sleep when no connections
                    continue

                # Broadcast different types of orchestration monitoring data
                await self._broadcast_agent_status()
                await self._broadcast_workflow_progress()
                await self._broadcast_orchestration_metrics()
                await self._broadcast_system_performance()

                # Reset error counter on successful broadcast
                consecutive_errors = 0

                # Wait 5 seconds before next broadcast
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                logger.info("Agent orchestration monitoring loop cancelled")
                break
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in orchestration monitoring loop: {e}")

                # Exponential backoff for consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(
                        f"Too many consecutive errors ({consecutive_errors}), stopping monitoring loop"
                    )
                    break

                backoff_time = min(10 * (2**consecutive_errors), 60)  # Max 60 seconds
                await asyncio.sleep(backoff_time)

    async def _broadcast_agent_status(self):
        """Broadcast agent status and health information."""
        try:
            # Get status of all registered agents
            agents = await self.agent_registry.get_all_agents()
            agent_statuses = []

            for agent_id, agent_info in agents.items():
                try:
                    # Get detailed agent status
                    agent_status = await self._get_agent_status(agent_id, agent_info)
                    agent_statuses.append(agent_status)

                except Exception as e:
                    logger.warning(f"Error getting status for agent {agent_id}: {e}")
                    agent_statuses.append(
                        AgentStatusData(
                            agent_id=agent_id,
                            agent_type=agent_info.get("type", "unknown"),
                            status="error",
                            last_activity=datetime.utcnow().isoformat(),
                            performance_metrics={},
                            error_count=1,
                            tasks_completed=0,
                            current_task=None,
                        )
                    )

            event = AgentMonitoringEvent(
                type="agent_status_update",
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "agents": [agent.dict() for agent in agent_statuses],
                    "total_agents": len(agent_statuses),
                    "active_agents": len(
                        [a for a in agent_statuses if a.status == "active"]
                    ),
                },
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting agent status: {e}")

    async def _get_agent_status(
        self, agent_id: str, agent_info: dict[str, Any]
    ) -> AgentStatusData:
        """Get detailed status for a specific agent."""
        try:
            # This would typically query the agent's actual status
            # For now, we'll simulate based on registry information
            return AgentStatusData(
                agent_id=agent_id,
                agent_type=agent_info.get("type", "unknown"),
                status="active",  # Simulated status
                last_activity=datetime.utcnow().isoformat(),
                performance_metrics={
                    "response_time": 150.0,
                    "success_rate": 0.95,
                    "cpu_usage": 25.0,
                    "memory_usage": 128.0,
                },
                error_count=0,
                tasks_completed=self.orchestration_metrics["agent_activities"]
                .get(agent_id, {})
                .get("tasks_completed", 0),
                current_task=None,  # Would be populated with actual current task
            )
        except Exception as e:
            raise Exception(f"Failed to get agent status: {e}") from e

    async def _broadcast_workflow_progress(self):
        """Broadcast workflow execution progress."""
        try:
            # Get active workflows from workflow manager
            active_workflows = await self.workflow_manager.get_active_workflows()
            workflow_progress = []

            for workflow_id, workflow_info in active_workflows.items():
                try:
                    progress_data = WorkflowProgressData(
                        workflow_id=workflow_id,
                        workflow_type=workflow_info.get("type", "unknown"),
                        status=workflow_info.get("status", "running"),
                        progress_percentage=workflow_info.get("progress", 0.0),
                        current_step=workflow_info.get("current_step", "unknown"),
                        steps_completed=workflow_info.get("steps_completed", 0),
                        total_steps=workflow_info.get("total_steps", 1),
                        execution_time=workflow_info.get("execution_time", 0.0),
                        timestamp=datetime.utcnow().isoformat(),
                    )
                    workflow_progress.append(progress_data)

                except Exception as e:
                    logger.warning(
                        f"Error getting progress for workflow {workflow_id}: {e}"
                    )

            event = AgentMonitoringEvent(
                type="workflow_progress",
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "workflows": [workflow.dict() for workflow in workflow_progress],
                    "total_workflows": len(workflow_progress),
                    "completed_workflows": self.orchestration_metrics[
                        "workflow_executions"
                    ],
                },
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting workflow progress: {e}")

    async def _broadcast_orchestration_metrics(self):
        """Broadcast system orchestration performance metrics."""
        try:
            # Calculate orchestration metrics
            current_time = time.time()
            recent_completions = [
                t
                for t in self.orchestration_metrics["task_completion_times"]
                if current_time - t < 60
            ]

            avg_completion_time = 2.5  # Simulated average completion time
            if self.orchestration_metrics["task_completion_times"]:
                # Would calculate actual average from completion times
                pass

            orchestration_data = SystemOrchestrationMetrics(
                active_agents=len(await self.agent_registry.get_active_agents()),
                active_workflows=len(
                    await self.workflow_manager.get_active_workflows()
                ),
                total_tasks_queued=50,  # Simulated queue size
                tasks_per_second=len(recent_completions) / 60.0,
                average_task_completion_time=avg_completion_time,
                system_load=psutil.cpu_percent(interval=None),
                memory_usage=psutil.virtual_memory().percent,
                error_rate=self.orchestration_metrics["error_count"]
                / max(self.orchestration_metrics["tasks_completed"], 1),
                timestamp=datetime.utcnow().isoformat(),
            )

            event = AgentMonitoringEvent(
                type="orchestration_metrics",
                timestamp=datetime.utcnow().isoformat(),
                data=orchestration_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting orchestration metrics: {e}")

    async def _broadcast_system_performance(self):
        """Broadcast system performance metrics."""
        try:
            # Get system performance metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            performance_data = {
                "interface_id": "agent-orchestration",
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_used": memory.used,
                    "memory_total": memory.total,
                    "active_connections": len(self.connections),
                    "active_agents": len(await self.agent_registry.get_active_agents()),
                    "active_workflows": len(
                        await self.workflow_manager.get_active_workflows()
                    ),
                    "tasks_in_queue": 50,  # Simulated
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            event = AgentMonitoringEvent(
                type="performance_metric",
                timestamp=datetime.utcnow().isoformat(),
                data=performance_data,
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting system performance: {e}")

    async def connect(
        self, websocket: WebSocket, connection_id: str, is_authenticated: bool = False
    ):
        """Add a new monitoring WebSocket connection."""
        await websocket.accept()
        self.connections[connection_id] = websocket

        if is_authenticated:
            self.authenticated_connections.add(connection_id)

        logger.info(
            f"Agent orchestration monitoring WebSocket connected: {connection_id} (authenticated: {is_authenticated})"
        )

        # Send initial status
        await self._send_initial_status(websocket)

    async def disconnect(self, connection_id: str):
        """Remove a monitoring WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        if connection_id in self.authenticated_connections:
            self.authenticated_connections.remove(connection_id)

        logger.info(
            f"Agent orchestration monitoring WebSocket disconnected: {connection_id}"
        )

    async def _send_initial_status(self, websocket: WebSocket):
        """Send initial status to a newly connected client."""
        try:
            welcome_event = AgentMonitoringEvent(
                type="connection_status",
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "status": "connected",
                    "service": "Agent Orchestration",
                    "version": "1.0.0",
                    "capabilities": [
                        "agent_status_updates",
                        "workflow_progress",
                        "orchestration_metrics",
                        "performance_metrics",
                        "error_reporting",
                    ],
                },
            )

            await websocket.send_text(json.dumps(welcome_event.dict()))

        except Exception as e:
            logger.error(f"Error sending initial status: {e}")

    async def _broadcast_to_all(self, message: dict[str, Any]):
        """Broadcast message to all connected monitoring clients."""
        if not self.connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for connection_id, websocket in self.connections.items():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            await self.disconnect(connection_id)

    def track_task_completion(
        self, agent_id: str, task_id: str, completion_time: float
    ):
        """Track task completion for monitoring."""
        self.orchestration_metrics["tasks_completed"] += 1
        self.orchestration_metrics["task_completion_times"].append(time.time())

        # Track per-agent activity
        if agent_id not in self.orchestration_metrics["agent_activities"]:
            self.orchestration_metrics["agent_activities"][agent_id] = {
                "tasks_completed": 0
            }

        self.orchestration_metrics["agent_activities"][agent_id]["tasks_completed"] += 1

        # Keep only recent completion times (last hour)
        current_time = time.time()
        self.orchestration_metrics["task_completion_times"] = [
            t
            for t in self.orchestration_metrics["task_completion_times"]
            if current_time - t < 3600
        ]

    def track_workflow_execution(self, workflow_id: str, status: str):
        """Track workflow execution for monitoring."""
        if status == "completed":
            self.orchestration_metrics["workflow_executions"] += 1
        elif status == "failed":
            self.orchestration_metrics["error_count"] += 1


def create_orchestration_monitoring_manager(
    agent_monitor: AgentMonitor,
    workflow_manager: WorkflowManager,
    agent_registry: AgentRegistry,
) -> AgentOrchestrationMonitoringManager:
    """Create and return an orchestration monitoring manager instance."""
    return AgentOrchestrationMonitoringManager(
        agent_monitor, workflow_manager, agent_registry
    )


def _authenticate_websocket(websocket: WebSocket) -> dict[str, Any] | None:
    """Authenticate WebSocket connection using JWT token."""
    try:
        # Try to get token from query parameters
        token = websocket.query_params.get("token")

        if not token:
            # Try to get token from headers
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return None

        # Verify token
        token_data = verify_token(token)
        return token_data

    except Exception as e:
        logger.warning(f"Orchestration WebSocket authentication failed: {e}")
        return None


async def create_monitoring_websocket_endpoint(
    orchestration_monitoring_manager: AgentOrchestrationMonitoringManager,
):
    """Create the monitoring WebSocket endpoint."""

    @router.websocket("/monitoring")
    async def websocket_monitoring_endpoint(websocket: WebSocket):
        """
        Real-time WebSocket endpoint for Agent Orchestration monitoring data.

        Provides orchestration monitoring information including:
        - Agent status updates and workflow progress events
        - System performance metrics and resource utilization
        - Workflow execution metrics and completion notifications
        - Error reporting and debugging information for agent operations
        """
        connection_id = str(uuid4())

        try:
            # Attempt authentication
            auth_data = _authenticate_websocket(websocket)
            is_authenticated = auth_data is not None

            # Connect to monitoring manager
            await orchestration_monitoring_manager.connect(
                websocket, connection_id, is_authenticated
            )

            # Keep connection alive and handle incoming messages
            while True:
                try:
                    message = await websocket.receive_text()

                    # Parse and handle commands
                    try:
                        command = json.loads(message)
                        await _handle_monitoring_command(
                            command,
                            connection_id,
                            is_authenticated,
                            orchestration_monitoring_manager,
                        )
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Invalid JSON received from {connection_id}: {message}"
                        )

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    break

        except Exception as e:
            logger.error(f"Error in orchestration monitoring WebSocket endpoint: {e}")

        finally:
            await orchestration_monitoring_manager.disconnect(connection_id)

    return router


async def _handle_monitoring_command(
    command: dict[str, Any],
    connection_id: str,
    is_authenticated: bool,
    manager: AgentOrchestrationMonitoringManager,
):
    """Handle incoming monitoring commands."""
    try:
        command_type = command.get("type")

        if command_type == "agent_status_request":
            await manager._broadcast_agent_status()

        elif command_type == "workflow_progress_request":
            await manager._broadcast_workflow_progress()

        elif command_type == "orchestration_metrics_request":
            await manager._broadcast_orchestration_metrics()

        elif command_type == "performance_request":
            await manager._broadcast_system_performance()

        else:
            logger.warning(f"Unknown command: {command_type} from {connection_id}")

    except Exception as e:
        logger.error(f"Error handling orchestration monitoring command: {e}")


__all__ = [
    "router",
    "AgentOrchestrationMonitoringManager",
    "create_orchestration_monitoring_manager",
    "create_monitoring_websocket_endpoint",
]
