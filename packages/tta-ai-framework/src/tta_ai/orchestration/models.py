"""
Core data models for Agent Orchestration.

These minimal pydantic models define the contract for agent communication and
orchestration requests/responses. They intentionally avoid implementation
specifics; richer models can be added in follow-up tasks.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class AgentType(str, Enum):
    IPA = "input_processor"
    WBA = "world_builder"
    NGA = "narrative_generator"


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class MessagePriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 9


class RoutingKey(BaseModel):
    topic: str | None = None
    tags: list[str] = Field(default_factory=list)


class AgentId(BaseModel):
    type: AgentType = Field(..., description="Logical agent type")
    instance: str | None = Field(
        default=None,
        description="Optional instance identifier (for sharded/pooled agents)",
    )


class AgentMessage(BaseModel):
    message_id: str = Field(..., min_length=6)
    sender: AgentId
    recipient: AgentId
    message_type: MessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    routing: RoutingKey = Field(default_factory=RoutingKey)
    timestamp: str | None = Field(
        default=None, description="ISO-8601 timestamp; may be set by coordinator"
    )


class OrchestrationRequest(BaseModel):
    session_id: str | None = None
    entrypoint: AgentType = AgentType.IPA
    input: dict[str, Any] = Field(default_factory=dict)


class OrchestrationResponse(BaseModel):
    response_text: str
    updated_context: dict[str, Any] = Field(default_factory=dict)
    workflow_metadata: dict[str, Any] = Field(default_factory=dict)


# Agent Capability System Models


class CapabilityType(str, Enum):
    """Types of capabilities that agents can advertise."""

    PROCESSING = "processing"  # Input/output processing capabilities
    GENERATION = "generation"  # Content generation capabilities
    ANALYSIS = "analysis"  # Analysis and validation capabilities
    COORDINATION = "coordination"  # Workflow coordination capabilities
    STORAGE = "storage"  # Data storage and retrieval capabilities
    COMMUNICATION = "communication"  # Inter-agent communication capabilities


class CapabilityScope(str, Enum):
    """Scope of capability operation."""

    SESSION = "session"  # Session-scoped operations
    GLOBAL = "global"  # Global operations across sessions
    INSTANCE = "instance"  # Instance-specific operations


class CapabilityStatus(str, Enum):
    """Status of a capability."""

    ACTIVE = "active"  # Capability is active and available
    DEPRECATED = "deprecated"  # Capability is deprecated but still functional
    DISABLED = "disabled"  # Capability is temporarily disabled
    EXPERIMENTAL = "experimental"  # Capability is experimental/beta


class AgentCapability(BaseModel):
    """Represents a single capability that an agent can provide."""

    name: str = Field(..., description="Unique name of the capability")
    type: CapabilityType = Field(..., description="Type of capability")
    version: str = Field(
        ..., description="Semantic version of the capability (e.g., '1.0.0')"
    )
    description: str | None = Field(None, description="Human-readable description")

    # Operational metadata
    scope: CapabilityScope = Field(
        default=CapabilityScope.SESSION, description="Scope of operation"
    )
    status: CapabilityStatus = Field(
        default=CapabilityStatus.ACTIVE, description="Current status"
    )

    # Capability requirements and constraints
    required_inputs: set[str] = Field(
        default_factory=set, description="Required input fields"
    )
    optional_inputs: set[str] = Field(
        default_factory=set, description="Optional input fields"
    )
    output_schema: dict[str, Any] | None = Field(
        None, description="JSON schema for outputs"
    )

    # Performance and resource metadata
    estimated_duration_ms: int | None = Field(
        None, description="Estimated execution time in milliseconds"
    )
    resource_requirements: dict[str, Any] = Field(
        default_factory=dict, description="Resource requirements (CPU, memory, etc.)"
    )

    # Compatibility and dependencies
    compatible_versions: set[str] = Field(
        default_factory=set, description="Compatible capability versions"
    )
    dependencies: set[str] = Field(
        default_factory=set, description="Required dependencies"
    )

    # Metadata
    tags: set[str] = Field(default_factory=set, description="Searchable tags")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("version")
    def validate_version(cls, v):
        """Validate semantic version format."""
        import re

        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$", v):
            raise ValueError(
                'Version must follow semantic versioning (e.g., "1.0.0" or "1.0.0-beta.1")'
            )
        return v

    @validator("name")
    def validate_name(cls, v):
        """Validate capability name format."""
        import re

        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "Capability name must start with lowercase letter and contain only lowercase letters, numbers, and underscores"
            )
        return v


class AgentCapabilitySet(BaseModel):
    """Collection of capabilities for an agent."""

    agent_id: AgentId = Field(..., description="Agent identifier")
    capabilities: list[AgentCapability] = Field(
        default_factory=list, description="List of capabilities"
    )

    # Capability set metadata
    version: str = Field(default="1.0.0", description="Version of the capability set")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    # Discovery and routing metadata
    priority: int = Field(
        default=5,
        description="Priority for capability matching (1-10, higher is better)",
    )
    load_factor: float = Field(default=1.0, description="Current load factor (0.0-1.0)")
    availability: bool = Field(
        default=True, description="Whether agent is available for new requests"
    )

    def get_capability(
        self, name: str, version: str | None = None
    ) -> AgentCapability | None:
        """Get a specific capability by name and optionally version."""
        for cap in self.capabilities:
            if cap.name == name:
                if version is None or cap.version == version:
                    return cap
        return None

    def has_capability(self, name: str, version: str | None = None) -> bool:
        """Check if agent has a specific capability."""
        return self.get_capability(name, version) is not None

    def get_capabilities_by_type(
        self, capability_type: CapabilityType
    ) -> list[AgentCapability]:
        """Get all capabilities of a specific type."""
        return [cap for cap in self.capabilities if cap.type == capability_type]

    def get_active_capabilities(self) -> list[AgentCapability]:
        """Get all active capabilities."""
        return [
            cap for cap in self.capabilities if cap.status == CapabilityStatus.ACTIVE
        ]


class CapabilityMatchCriteria(BaseModel):
    """Criteria for matching agent capabilities."""

    # Basic matching criteria
    capability_name: str | None = Field(
        None, description="Specific capability name to match"
    )
    capability_type: CapabilityType | None = Field(
        None, description="Type of capability required"
    )
    required_inputs: set[str] = Field(
        default_factory=set, description="Required input fields"
    )

    # Version constraints
    min_version: str | None = Field(None, description="Minimum capability version")
    max_version: str | None = Field(None, description="Maximum capability version")
    preferred_version: str | None = Field(
        None, description="Preferred capability version"
    )

    # Performance constraints
    max_duration_ms: int | None = Field(None, description="Maximum acceptable duration")
    resource_constraints: dict[str, Any] = Field(
        default_factory=dict, description="Resource constraints"
    )

    # Availability constraints
    require_available: bool = Field(
        default=True, description="Require agent to be available"
    )
    max_load_factor: float = Field(
        default=0.8, description="Maximum acceptable load factor"
    )

    # Tags and metadata
    required_tags: set[str] = Field(
        default_factory=set, description="Required capability tags"
    )
    metadata_filters: dict[str, Any] = Field(
        default_factory=dict, description="Metadata filters"
    )


class CapabilityMatchResult(BaseModel):
    """Result of capability matching."""

    agent_id: AgentId = Field(..., description="Matched agent identifier")
    capability: AgentCapability = Field(..., description="Matched capability")
    match_score: float = Field(..., description="Match score (0.0-1.0)")

    # Match details
    exact_match: bool = Field(
        default=False, description="Whether this is an exact match"
    )
    version_match: bool = Field(
        default=False, description="Whether version requirements are met"
    )
    performance_match: bool = Field(
        default=False, description="Whether performance requirements are met"
    )

    # Agent status at match time
    agent_load_factor: float = Field(
        default=0.0, description="Agent load factor at match time"
    )
    agent_availability: bool = Field(
        default=True, description="Agent availability at match time"
    )
    estimated_wait_time_ms: int | None = Field(
        None, description="Estimated wait time for agent"
    )


class CapabilityDiscoveryRequest(BaseModel):
    """Request for discovering agents with specific capabilities."""

    criteria: CapabilityMatchCriteria = Field(..., description="Matching criteria")
    max_results: int = Field(
        default=10, description="Maximum number of results to return"
    )
    include_degraded: bool = Field(
        default=False, description="Include agents with degraded performance"
    )
    sort_by: str = Field(default="match_score", description="Sort results by field")
    sort_descending: bool = Field(default=True, description="Sort in descending order")


class CapabilityDiscoveryResponse(BaseModel):
    """Response from capability discovery."""

    matches: list[CapabilityMatchResult] = Field(
        default_factory=list, description="Matched capabilities"
    )
    total_agents_searched: int = Field(
        default=0, description="Total number of agents searched"
    )
    search_duration_ms: int = Field(
        default=0, description="Search duration in milliseconds"
    )

    # Discovery metadata
    discovery_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Discovery timestamp"
    )
    cache_hit: bool = Field(
        default=False, description="Whether results came from cache"
    )
