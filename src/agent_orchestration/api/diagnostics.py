"""
Enhanced diagnostics API endpoint for agent capability information.

This module provides comprehensive diagnostics endpoints that aggregate
capability information, health status, and performance metrics.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ..registries.redis_agent_registry import RedisAgentRegistry
from ..models import AgentId, AgentType, AgentCapability
from ..capabilities.auto_discovery import AutoDiscoveryManager, get_auto_discovery_manager
from ..performance.response_time_monitor import get_response_time_monitor
from ..performance.optimization import IntelligentAgentCoordinator

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


class AgentHealthStatus(BaseModel):
    """Agent health status information."""
    agent_id: str
    agent_type: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    last_heartbeat: Optional[datetime] = None
    response_time_avg: Optional[float] = None
    success_rate: Optional[float] = None
    current_load: Optional[int] = None
    uptime_seconds: Optional[float] = None


class AgentCapabilityInfo(BaseModel):
    """Agent capability information."""
    capability_type: str
    name: str
    version: str
    description: Optional[str] = None
    enabled: bool = True
    last_used: Optional[datetime] = None
    usage_count: Optional[int] = None


class AgentDiagnosticInfo(BaseModel):
    """Comprehensive agent diagnostic information."""
    agent_id: str
    agent_type: str
    instance: str
    health_status: AgentHealthStatus
    capabilities: List[AgentCapabilityInfo]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    discovery_info: Dict[str, Any] = Field(default_factory=dict)


class SystemDiagnosticSummary(BaseModel):
    """System-wide diagnostic summary."""
    timestamp: datetime
    total_agents: int
    healthy_agents: int
    degraded_agents: int
    unhealthy_agents: int
    unknown_agents: int
    total_capabilities: int
    unique_capability_types: int
    system_load: Optional[float] = None
    average_response_time: Optional[float] = None
    overall_health: str = "unknown"


class DiagnosticsAPI:
    """Enhanced diagnostics API for agent capabilities."""
    
    def __init__(
        self,
        registry: RedisAgentRegistry,
        auto_discovery_manager: Optional[AutoDiscoveryManager] = None,
        require_auth: bool = True
    ):
        self.registry = registry
        self.auto_discovery_manager = auto_discovery_manager
        self.require_auth = require_auth
        
        # Create router
        self.router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
        self._setup_routes()
        
        logger.info("DiagnosticsAPI initialized")
    
    def _setup_routes(self) -> None:
        """Set up API routes."""
        
        @self.router.get("/agents", response_model=List[AgentDiagnosticInfo])
        async def get_agents_diagnostics(
            agent_type: Optional[str] = Query(None, description="Filter by agent type"),
            include_performance: bool = Query(True, description="Include performance metrics"),
            include_discovery: bool = Query(True, description="Include discovery information"),
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
        ):
            """Get comprehensive diagnostics for all agents."""
            if self.require_auth and not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            return await self._get_agents_diagnostics(
                agent_type=agent_type,
                include_performance=include_performance,
                include_discovery=include_discovery
            )
        
        @self.router.get("/agents/{agent_id}", response_model=AgentDiagnosticInfo)
        async def get_agent_diagnostics(
            agent_id: str,
            include_performance: bool = Query(True, description="Include performance metrics"),
            include_discovery: bool = Query(True, description="Include discovery information"),
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
        ):
            """Get diagnostics for a specific agent."""
            if self.require_auth and not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            diagnostic_info = await self._get_agent_diagnostics(
                agent_id=agent_id,
                include_performance=include_performance,
                include_discovery=include_discovery
            )
            
            if not diagnostic_info:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            return diagnostic_info
        
        @self.router.get("/system/summary", response_model=SystemDiagnosticSummary)
        async def get_system_summary(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
        ):
            """Get system-wide diagnostic summary."""
            if self.require_auth and not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            return await self._get_system_summary()
        
        @self.router.get("/system/health")
        async def get_system_health(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
        ):
            """Get simple system health check."""
            if self.require_auth and not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            health_info = await self._get_system_health()
            
            # Return appropriate HTTP status based on health
            if health_info["status"] == "healthy":
                return health_info
            elif health_info["status"] == "degraded":
                raise HTTPException(status_code=503, detail=health_info)
            else:
                raise HTTPException(status_code=500, detail=health_info)
        
        @self.router.get("/discovery/status")
        async def get_discovery_status(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
        ):
            """Get auto-discovery status and statistics."""
            if self.require_auth and not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if not self.auto_discovery_manager:
                raise HTTPException(status_code=404, detail="Auto-discovery not available")
            
            return self.auto_discovery_manager.get_discovery_statistics()
    
    async def _get_agents_diagnostics(
        self,
        agent_type: Optional[str] = None,
        include_performance: bool = True,
        include_discovery: bool = True
    ) -> List[AgentDiagnosticInfo]:
        """Get diagnostics for all agents."""
        try:
            # Get all registered agents
            agents = await self.registry.get_all_agents()
            
            diagnostics = []
            
            for agent_id, agent_info in agents.items():
                # Filter by agent type if specified
                if agent_type and agent_info.get("agent_type") != agent_type:
                    continue
                
                diagnostic_info = await self._build_agent_diagnostic_info(
                    agent_id=agent_id,
                    agent_info=agent_info,
                    include_performance=include_performance,
                    include_discovery=include_discovery
                )
                
                if diagnostic_info:
                    diagnostics.append(diagnostic_info)
            
            return diagnostics
        
        except Exception as e:
            logger.error(f"Failed to get agents diagnostics: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve diagnostics")
    
    async def _get_agent_diagnostics(
        self,
        agent_id: str,
        include_performance: bool = True,
        include_discovery: bool = True
    ) -> Optional[AgentDiagnosticInfo]:
        """Get diagnostics for a specific agent."""
        try:
            # Get agent information
            agent_info = await self.registry.get_agent_info(agent_id)
            
            if not agent_info:
                return None
            
            return await self._build_agent_diagnostic_info(
                agent_id=agent_id,
                agent_info=agent_info,
                include_performance=include_performance,
                include_discovery=include_discovery
            )
        
        except Exception as e:
            logger.error(f"Failed to get agent diagnostics for {agent_id}: {e}")
            return None
    
    async def _build_agent_diagnostic_info(
        self,
        agent_id: str,
        agent_info: Dict[str, Any],
        include_performance: bool = True,
        include_discovery: bool = True
    ) -> Optional[AgentDiagnosticInfo]:
        """Build comprehensive diagnostic information for an agent."""
        try:
            # Parse agent ID
            agent_type = agent_info.get("agent_type", "unknown")
            instance = agent_info.get("instance", agent_id)
            
            # Build health status
            health_status = await self._build_health_status(agent_id, agent_info)
            
            # Build capabilities information
            capabilities = self._build_capabilities_info(agent_info.get("capabilities", []))
            
            # Build performance metrics
            performance_metrics = {}
            if include_performance:
                performance_metrics = await self._get_performance_metrics(agent_id)
            
            # Build discovery information
            discovery_info = {}
            if include_discovery and self.auto_discovery_manager:
                discovery_info = self._get_discovery_info(agent_id)
            
            return AgentDiagnosticInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                instance=instance,
                health_status=health_status,
                capabilities=capabilities,
                metadata=agent_info.get("metadata", {}),
                performance_metrics=performance_metrics,
                discovery_info=discovery_info
            )
        
        except Exception as e:
            logger.error(f"Failed to build diagnostic info for agent {agent_id}: {e}")
            return None
    
    async def _build_health_status(
        self,
        agent_id: str,
        agent_info: Dict[str, Any]
    ) -> AgentHealthStatus:
        """Build health status for an agent."""
        # Get heartbeat information
        last_heartbeat_timestamp = agent_info.get("last_heartbeat")
        last_heartbeat = None
        if last_heartbeat_timestamp:
            last_heartbeat = datetime.fromtimestamp(last_heartbeat_timestamp, tz=timezone.utc)
        
        # Determine health status
        current_time = time.time()
        status = "unknown"
        
        if last_heartbeat_timestamp:
            time_since_heartbeat = current_time - last_heartbeat_timestamp
            if time_since_heartbeat < 60:  # Less than 1 minute
                status = "healthy"
            elif time_since_heartbeat < 300:  # Less than 5 minutes
                status = "degraded"
            else:
                status = "unhealthy"
        
        # Calculate uptime
        registration_time = agent_info.get("registration_time")
        uptime_seconds = None
        if registration_time:
            uptime_seconds = current_time - registration_time
        
        return AgentHealthStatus(
            agent_id=agent_id,
            agent_type=agent_info.get("agent_type", "unknown"),
            status=status,
            last_heartbeat=last_heartbeat,
            uptime_seconds=uptime_seconds
        )
    
    def _build_capabilities_info(
        self,
        capabilities: List[Dict[str, Any]]
    ) -> List[AgentCapabilityInfo]:
        """Build capabilities information."""
        capability_info = []
        
        for cap in capabilities:
            capability_info.append(AgentCapabilityInfo(
                capability_type=cap.get("capability_type", "unknown"),
                name=cap.get("name", "unknown"),
                version=cap.get("version", "1.0.0"),
                description=cap.get("description"),
                enabled=cap.get("enabled", True)
            ))
        
        return capability_info
    
    async def _get_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent."""
        try:
            # Get response time monitor
            monitor = get_response_time_monitor()
            
            # Get recent statistics
            stats = monitor.get_statistics(time_window_minutes=60)
            
            # Find relevant statistics for this agent
            # This is a simplified approach - in practice, you'd need to
            # correlate agent IDs with operation types
            performance_metrics = {
                "monitoring_available": True,
                "statistics_window_minutes": 60
            }
            
            # Add general system performance metrics
            performance_summary = monitor.get_performance_summary()
            performance_metrics.update({
                "system_performance": performance_summary.get("overall_performance", "unknown"),
                "active_operations": performance_summary.get("active_operations", 0)
            })
            
            return performance_metrics
        
        except Exception as e:
            logger.error(f"Failed to get performance metrics for agent {agent_id}: {e}")
            return {"monitoring_available": False, "error": str(e)}
    
    def _get_discovery_info(self, agent_id: str) -> Dict[str, Any]:
        """Get discovery information for an agent."""
        if not self.auto_discovery_manager:
            return {"auto_discovery_available": False}
        
        # Get component status
        status = self.auto_discovery_manager.get_component_status(agent_id)
        
        return {
            "auto_discovery_available": True,
            "discovery_status": status.value if status else "unknown",
            "discovery_enabled": self.auto_discovery_manager.config.enabled
        }
    
    async def _get_system_summary(self) -> SystemDiagnosticSummary:
        """Get system-wide diagnostic summary."""
        try:
            # Get all agents
            agents = await self.registry.get_all_agents()
            
            # Count agents by health status
            health_counts = {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "unknown": 0
            }
            
            total_capabilities = 0
            capability_types = set()
            
            for agent_id, agent_info in agents.items():
                # Build health status
                health_status = await self._build_health_status(agent_id, agent_info)
                health_counts[health_status.status] += 1
                
                # Count capabilities
                capabilities = agent_info.get("capabilities", [])
                total_capabilities += len(capabilities)
                
                for cap in capabilities:
                    capability_types.add(cap.get("capability_type", "unknown"))
            
            # Determine overall health
            total_agents = len(agents)
            if total_agents == 0:
                overall_health = "unknown"
            elif health_counts["unhealthy"] > 0:
                overall_health = "unhealthy"
            elif health_counts["degraded"] > 0:
                overall_health = "degraded"
            elif health_counts["healthy"] == total_agents:
                overall_health = "healthy"
            else:
                overall_health = "degraded"
            
            return SystemDiagnosticSummary(
                timestamp=datetime.now(tz=timezone.utc),
                total_agents=total_agents,
                healthy_agents=health_counts["healthy"],
                degraded_agents=health_counts["degraded"],
                unhealthy_agents=health_counts["unhealthy"],
                unknown_agents=health_counts["unknown"],
                total_capabilities=total_capabilities,
                unique_capability_types=len(capability_types),
                overall_health=overall_health
            )
        
        except Exception as e:
            logger.error(f"Failed to get system summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve system summary")
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get simple system health check."""
        try:
            summary = await self._get_system_summary()
            
            return {
                "status": summary.overall_health,
                "timestamp": summary.timestamp.isoformat(),
                "total_agents": summary.total_agents,
                "healthy_agents": summary.healthy_agents,
                "message": f"System health: {summary.overall_health}"
            }
        
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "message": f"Health check failed: {str(e)}"
            }
