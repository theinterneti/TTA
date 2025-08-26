"""
Auto-discovery mechanisms for agent capability registration during startup.

This module provides intelligent auto-discovery that automatically registers
agent capabilities during component startup with configurable discovery strategies.
"""
from __future__ import annotations

import asyncio
import logging
import time
import socket
import os
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..registries.redis_agent_registry import RedisAgentRegistry
from ..models import AgentId, AgentType, AgentCapability, AgentCapabilitySet, CapabilityType

logger = logging.getLogger(__name__)


class DiscoveryStrategy(str, Enum):
    """Auto-discovery strategies."""
    IMMEDIATE = "immediate"  # Register immediately on startup
    DELAYED = "delayed"     # Register after delay/validation
    HEARTBEAT = "heartbeat" # Register on first heartbeat
    MANUAL = "manual"       # Manual registration only


class DiscoveryStatus(str, Enum):
    """Discovery status for components."""
    PENDING = "pending"
    DISCOVERING = "discovering"
    REGISTERED = "registered"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class DiscoveryConfig:
    """Configuration for auto-discovery."""
    enabled: bool = True
    strategy: DiscoveryStrategy = DiscoveryStrategy.IMMEDIATE
    discovery_timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 5.0
    heartbeat_interval: float = 30.0
    capability_validation: bool = True
    auto_register_on_startup: bool = True
    discovery_delay: float = 0.0  # Delay before discovery starts
    
    # Environment-specific settings
    development_enabled: bool = True
    testing_enabled: bool = False
    staging_enabled: bool = True
    production_enabled: bool = True


@dataclass
class ComponentInfo:
    """Information about a discoverable component."""
    component_id: str
    component_type: str
    agent_type: Optional[AgentType] = None
    capabilities: List[AgentCapability] = field(default_factory=list)
    host: Optional[str] = None
    port: Optional[int] = None
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovery_status: DiscoveryStatus = DiscoveryStatus.PENDING
    last_discovery_attempt: Optional[float] = None
    discovery_attempts: int = 0


class AutoDiscoveryManager:
    """Manages auto-discovery of agent capabilities during startup."""
    
    def __init__(
        self,
        registry: RedisAgentRegistry,
        config: Optional[DiscoveryConfig] = None
    ):
        self.registry = registry
        self.config = config or DiscoveryConfig()
        
        # Discovery state
        self.components: Dict[str, ComponentInfo] = {}
        self.discovery_callbacks: List[Callable] = []
        self.is_running = False
        
        # Background tasks
        self.discovery_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Environment detection
        self.environment = self._detect_environment()
        
        # Validate environment-specific enablement
        if not self._is_enabled_for_environment():
            self.config.enabled = False
            logger.info(f"Auto-discovery disabled for environment: {self.environment}")
        
        logger.info(f"AutoDiscoveryManager initialized (enabled: {self.config.enabled})")
    
    def _detect_environment(self) -> str:
        """Detect current environment."""
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env in ["dev", "develop", "development"]:
            return "development"
        elif env in ["test", "testing"]:
            return "testing"
        elif env in ["stage", "staging"]:
            return "staging"
        elif env in ["prod", "production"]:
            return "production"
        else:
            return "development"  # Default
    
    def _is_enabled_for_environment(self) -> bool:
        """Check if auto-discovery is enabled for current environment."""
        env_settings = {
            "development": self.config.development_enabled,
            "testing": self.config.testing_enabled,
            "staging": self.config.staging_enabled,
            "production": self.config.production_enabled
        }
        return env_settings.get(self.environment, True)
    
    async def start(self) -> None:
        """Start the auto-discovery manager."""
        if not self.config.enabled:
            logger.info("Auto-discovery is disabled")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start background tasks
        if self.config.strategy in [DiscoveryStrategy.DELAYED, DiscoveryStrategy.HEARTBEAT]:
            self.discovery_task = asyncio.create_task(self._discovery_loop())
        
        if self.config.heartbeat_interval > 0:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("AutoDiscoveryManager started")
    
    async def stop(self) -> None:
        """Stop the auto-discovery manager."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in [self.discovery_task, self.heartbeat_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("AutoDiscoveryManager stopped")
    
    def register_component(
        self,
        component_id: str,
        component_type: str,
        agent_type: Optional[AgentType] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a component for auto-discovery."""
        if not self.config.enabled:
            return
        
        # Get host information
        host = self._get_local_host()
        
        component_info = ComponentInfo(
            component_id=component_id,
            component_type=component_type,
            agent_type=agent_type,
            capabilities=capabilities or [],
            host=host,
            metadata=metadata or {},
            discovery_status=DiscoveryStatus.PENDING
        )
        
        self.components[component_id] = component_info
        
        # Immediate discovery if configured
        if self.config.strategy == DiscoveryStrategy.IMMEDIATE and self.config.auto_register_on_startup:
            asyncio.create_task(self._discover_component(component_id))
        
        logger.info(f"Component registered for auto-discovery: {component_id}")
    
    async def discover_component(self, component_id: str) -> bool:
        """Manually trigger discovery for a specific component."""
        if component_id not in self.components:
            logger.warning(f"Component not found for discovery: {component_id}")
            return False
        
        return await self._discover_component(component_id)
    
    async def _discover_component(self, component_id: str) -> bool:
        """Discover and register a component."""
        if not self.config.enabled:
            return False
        
        component = self.components.get(component_id)
        if not component:
            return False
        
        component.discovery_status = DiscoveryStatus.DISCOVERING
        component.last_discovery_attempt = time.time()
        component.discovery_attempts += 1
        
        try:
            # Apply discovery delay if configured
            if self.config.discovery_delay > 0:
                await asyncio.sleep(self.config.discovery_delay)
            
            # Validate capabilities if enabled
            if self.config.capability_validation:
                if not await self._validate_component_capabilities(component):
                    component.discovery_status = DiscoveryStatus.FAILED
                    logger.warning(f"Component capability validation failed: {component_id}")
                    return False
            
            # Register with registry
            success = await self._register_with_registry(component)
            
            if success:
                component.discovery_status = DiscoveryStatus.REGISTERED
                logger.info(f"Component successfully discovered and registered: {component_id}")
                
                # Notify callbacks
                await self._notify_discovery_callbacks(component, "registered")
                return True
            else:
                component.discovery_status = DiscoveryStatus.FAILED
                logger.error(f"Failed to register component with registry: {component_id}")
                return False
        
        except Exception as e:
            component.discovery_status = DiscoveryStatus.FAILED
            logger.error(f"Discovery failed for component {component_id}: {e}")
            return False
    
    async def _validate_component_capabilities(self, component: ComponentInfo) -> bool:
        """Validate component capabilities."""
        if not component.capabilities:
            # If no capabilities specified, try to infer from agent type
            if component.agent_type:
                component.capabilities = self._infer_capabilities_from_agent_type(component.agent_type)
        
        # Basic validation - ensure capabilities are properly formed
        for capability in component.capabilities:
            if not isinstance(capability, AgentCapability):
                logger.warning(f"Invalid capability type for component {component.component_id}")
                return False
            
            if not capability.capability_type or not capability.name:
                logger.warning(f"Incomplete capability for component {component.component_id}")
                return False
        
        return True
    
    def _infer_capabilities_from_agent_type(self, agent_type: AgentType) -> List[AgentCapability]:
        """Infer capabilities from agent type."""
        capability_mappings = {
            AgentType.INPUT_PROCESSOR: [
                AgentCapability(
                    capability_type=CapabilityType.INPUT_PROCESSING,
                    name="text_analysis",
                    version="1.0.0",
                    description="Text input processing and analysis"
                ),
                AgentCapability(
                    capability_type=CapabilityType.SAFETY_VALIDATION,
                    name="content_safety",
                    version="1.0.0",
                    description="Content safety validation"
                )
            ],
            AgentType.WORLD_BUILDER: [
                AgentCapability(
                    capability_type=CapabilityType.WORLD_MANAGEMENT,
                    name="world_state_management",
                    version="1.0.0",
                    description="World state management and persistence"
                ),
                AgentCapability(
                    capability_type=CapabilityType.CONTEXT_MANAGEMENT,
                    name="context_integration",
                    version="1.0.0",
                    description="Context integration and management"
                )
            ],
            AgentType.NARRATIVE_GENERATOR: [
                AgentCapability(
                    capability_type=CapabilityType.CONTENT_GENERATION,
                    name="narrative_generation",
                    version="1.0.0",
                    description="Narrative content generation"
                ),
                AgentCapability(
                    capability_type=CapabilityType.THERAPEUTIC_CONTENT,
                    name="therapeutic_narrative",
                    version="1.0.0",
                    description="Therapeutic narrative generation"
                )
            ]
        }
        
        return capability_mappings.get(agent_type, [])
    
    async def _register_with_registry(self, component: ComponentInfo) -> bool:
        """Register component with the agent registry."""
        try:
            agent_id = AgentId(
                agent_type=component.agent_type or AgentType.INPUT_PROCESSOR,
                instance=component.component_id
            )
            
            # Register agent with capabilities
            await self.registry.register_agent(
                agent_id=agent_id,
                capabilities=component.capabilities,
                metadata={
                    **component.metadata,
                    "auto_discovered": True,
                    "discovery_timestamp": time.time(),
                    "host": component.host,
                    "port": component.port,
                    "version": component.version
                }
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to register component {component.component_id} with registry: {e}")
            return False
    
    def _get_local_host(self) -> str:
        """Get local host information."""
        try:
            # Try to get the actual IP address
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            # Fallback to localhost
            return "127.0.0.1"
    
    async def _discovery_loop(self) -> None:
        """Background discovery loop for delayed/heartbeat strategies."""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Find components that need discovery
                for component_id, component in self.components.items():
                    if component.discovery_status == DiscoveryStatus.PENDING:
                        if self.config.strategy == DiscoveryStrategy.DELAYED:
                            # Discover after delay
                            await self._discover_component(component_id)
                        elif self.config.strategy == DiscoveryStrategy.HEARTBEAT:
                            # Will be discovered on heartbeat
                            pass
                    elif component.discovery_status == DiscoveryStatus.FAILED:
                        # Retry failed discoveries
                        if (component.discovery_attempts < self.config.retry_attempts and
                            current_time - (component.last_discovery_attempt or 0) > self.config.retry_delay):
                            await self._discover_component(component_id)
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _heartbeat_loop(self) -> None:
        """Background heartbeat loop."""
        while self.is_running:
            try:
                # Send heartbeats for registered components
                for component_id, component in self.components.items():
                    if component.discovery_status == DiscoveryStatus.REGISTERED:
                        await self._send_heartbeat(component)
                    elif (component.discovery_status == DiscoveryStatus.PENDING and 
                          self.config.strategy == DiscoveryStrategy.HEARTBEAT):
                        # Discover on first heartbeat
                        await self._discover_component(component_id)
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(self.config.heartbeat_interval)
    
    async def _send_heartbeat(self, component: ComponentInfo) -> None:
        """Send heartbeat for a component."""
        try:
            if component.agent_type:
                agent_id = AgentId(
                    agent_type=component.agent_type,
                    instance=component.component_id
                )
                
                await self.registry.update_heartbeat(agent_id)
        
        except Exception as e:
            logger.error(f"Failed to send heartbeat for component {component.component_id}: {e}")
    
    async def _notify_discovery_callbacks(self, component: ComponentInfo, event: str) -> None:
        """Notify discovery callbacks."""
        for callback in self.discovery_callbacks:
            try:
                await callback(component, event)
            except Exception as e:
                logger.error(f"Discovery callback failed: {e}")
    
    def add_discovery_callback(self, callback: Callable) -> None:
        """Add discovery event callback."""
        self.discovery_callbacks.append(callback)
    
    def get_component_status(self, component_id: str) -> Optional[DiscoveryStatus]:
        """Get discovery status for a component."""
        component = self.components.get(component_id)
        return component.discovery_status if component else None
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get auto-discovery statistics."""
        status_counts = {}
        for status in DiscoveryStatus:
            status_counts[status.value] = sum(
                1 for c in self.components.values() 
                if c.discovery_status == status
            )
        
        return {
            "enabled": self.config.enabled,
            "environment": self.environment,
            "strategy": self.config.strategy.value,
            "total_components": len(self.components),
            "status_counts": status_counts,
            "discovery_attempts": sum(c.discovery_attempts for c in self.components.values()),
            "is_running": self.is_running
        }


# Global auto-discovery manager instance
_auto_discovery_manager: Optional[AutoDiscoveryManager] = None


def get_auto_discovery_manager(
    registry: Optional[RedisAgentRegistry] = None,
    config: Optional[DiscoveryConfig] = None
) -> AutoDiscoveryManager:
    """Get the global auto-discovery manager."""
    global _auto_discovery_manager
    if _auto_discovery_manager is None:
        if registry is None:
            raise ValueError("Registry required for first initialization")
        _auto_discovery_manager = AutoDiscoveryManager(registry, config)
    return _auto_discovery_manager
