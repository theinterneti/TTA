"""
Configuration schema validation for Agent Orchestration.

This module provides Pydantic models for validating agent orchestration
configuration, including discovery and auto-registration settings.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class CapabilityMatchingAlgorithm(str, Enum):
    """Available capability matching algorithms."""
    WEIGHTED_SCORE = "weighted_score"
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    PRIORITY_BASED = "priority_based"


class DiscoveryConfig(BaseModel):
    """Configuration for agent discovery system."""
    
    enabled: bool = Field(default=True, description="Enable agent discovery system")
    cache_ttl: int = Field(default=300, ge=60, le=3600, description="Discovery cache TTL in seconds")
    max_search_results: int = Field(default=50, ge=1, le=1000, description="Maximum results for capability searches")
    
    capability_matching: CapabilityMatchingConfig = Field(
        default_factory=lambda: CapabilityMatchingConfig(),
        description="Capability matching configuration"
    )


class CapabilityMatchingConfig(BaseModel):
    """Configuration for capability matching algorithms."""
    
    algorithm: CapabilityMatchingAlgorithm = Field(
        default=CapabilityMatchingAlgorithm.WEIGHTED_SCORE,
        description="Capability matching algorithm"
    )
    score_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Minimum match score threshold"
    )
    prefer_exact_version: bool = Field(
        default=True,
        description="Prefer exact version matches"
    )
    include_deprecated: bool = Field(
        default=False,
        description="Include deprecated capabilities in search results"
    )


class AgentCapabilityConfig(BaseModel):
    """Configuration for agent capability advertisement."""
    
    advertise: bool = Field(default=True, description="Advertise capabilities for discovery")
    version: str = Field(default="1.0.0", description="Capability set version")
    
    @validator('version')
    def validate_version(cls, v):
        """Validate semantic version format."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$', v):
            raise ValueError('Version must follow semantic versioning (e.g., "1.0.0" or "1.0.0-beta.1")')
        return v


class AgentConfig(BaseModel):
    """Configuration for individual agent types."""
    
    enabled: bool = Field(default=True, description="Enable this agent type")
    max_instances: int = Field(default=1, ge=1, le=100, description="Maximum number of instances")
    timeout: int = Field(default=30, ge=1, le=300, description="Agent timeout in seconds")
    
    # Auto-registration settings
    auto_register_enabled: bool = Field(
        default=False,
        description="Enable auto-registration for this agent type"
    )
    instance: Optional[str] = Field(
        default=None,
        description="Explicit instance name (null = auto-generate)"
    )
    
    # Capability settings
    capabilities: AgentCapabilityConfig = Field(
        default_factory=AgentCapabilityConfig,
        description="Capability configuration"
    )
    
    @validator('instance')
    def validate_instance_name(cls, v):
        """Validate instance name format if provided."""
        if v is not None:
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Instance name must contain only alphanumeric characters, underscores, and hyphens')
        return v


class AgentsConfig(BaseModel):
    """Configuration for all agent orchestration settings."""
    
    # Global settings
    auto_register: bool = Field(
        default=False,
        description="Global flag for automatic agent registration (default: false for security)"
    )
    heartbeat_ttl: float = Field(
        default=30.0, ge=5.0, le=300.0,
        description="Agent heartbeat TTL in seconds"
    )
    heartbeat_interval: Optional[float] = Field(
        default=None,
        description="Heartbeat interval (null = auto-calculate as ttl/3)"
    )
    
    # Discovery system
    discovery: DiscoveryConfig = Field(
        default_factory=DiscoveryConfig,
        description="Discovery system configuration"
    )
    
    # Per-agent configurations
    input_processor: AgentConfig = Field(
        default_factory=lambda: AgentConfig(max_instances=3, timeout=10),
        description="Input Processor Agent configuration"
    )
    world_builder: AgentConfig = Field(
        default_factory=lambda: AgentConfig(max_instances=2, timeout=15),
        description="World Builder Agent configuration"
    )
    narrative_generator: AgentConfig = Field(
        default_factory=lambda: AgentConfig(max_instances=3, timeout=20),
        description="Narrative Generator Agent configuration"
    )
    
    @validator('heartbeat_interval')
    def validate_heartbeat_interval(cls, v, values):
        """Validate heartbeat interval against TTL."""
        if v is not None:
            ttl = values.get('heartbeat_ttl', 30.0)
            if v <= 0 or v >= ttl:
                raise ValueError('Heartbeat interval must be positive and less than heartbeat_ttl')
        return v
    
    def get_effective_heartbeat_interval(self) -> float:
        """Get the effective heartbeat interval (calculated if not set)."""
        if self.heartbeat_interval is not None:
            return self.heartbeat_interval
        return max(1.0, self.heartbeat_ttl / 3.0)
    
    def is_auto_registration_enabled(self, agent_type: str) -> bool:
        """Check if auto-registration is enabled for a specific agent type."""
        if not self.auto_register:
            return False
        
        agent_config = getattr(self, agent_type, None)
        if agent_config is None:
            return False
        
        return agent_config.auto_register_enabled
    
    def get_agent_config(self, agent_type: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent type."""
        return getattr(self, agent_type, None)


class AgentOrchestrationConfig(BaseModel):
    """Complete agent orchestration configuration schema."""
    
    enabled: bool = Field(default=True, description="Enable agent orchestration")
    port: int = Field(default=8503, ge=1024, le=65535, description="Service port")
    max_concurrent_workflows: int = Field(
        default=50, ge=1, le=1000,
        description="Maximum concurrent workflows"
    )
    workflow_timeout: int = Field(
        default=30, ge=1, le=3600,
        description="Default workflow timeout in seconds"
    )
    
    # Agent configuration
    agents: AgentsConfig = Field(
        default_factory=AgentsConfig,
        description="Agent configuration"
    )
    
    # Other existing configurations (simplified for now)
    resources: Dict[str, Any] = Field(default_factory=dict, description="Resource management settings")
    messaging: Dict[str, Any] = Field(default_factory=dict, description="Message coordination settings")
    monitoring: Dict[str, Any] = Field(default_factory=dict, description="Performance monitoring settings")
    diagnostics: Dict[str, Any] = Field(default_factory=dict, description="Diagnostics settings")
    realtime: Dict[str, Any] = Field(default_factory=dict, description="Real-time interaction settings")


def validate_agent_orchestration_config(config_dict: Dict[str, Any]) -> AgentOrchestrationConfig:
    """
    Validate agent orchestration configuration from a dictionary.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Validated configuration object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    return AgentOrchestrationConfig(**config_dict)


def get_default_agent_orchestration_config() -> Dict[str, Any]:
    """Get default agent orchestration configuration as a dictionary."""
    return AgentOrchestrationConfig().dict()
