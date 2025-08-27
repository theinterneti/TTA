"""
Rate limiting data models for the API Gateway.

This module contains models for rate limiting configuration,
traffic management, and therapeutic session prioritization.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RateLimitType(str, Enum):
    """Rate limit type enumeration."""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_SECOND = "bandwidth_per_second"
    CONCURRENT_CONNECTIONS = "concurrent_connections"


class RateLimitScope(str, Enum):
    """Rate limit scope enumeration."""
    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_SERVICE = "per_service"
    PER_ENDPOINT = "per_endpoint"


class TrafficPriority(str, Enum):
    """Traffic priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    THERAPEUTIC = "therapeutic"
    CRISIS = "crisis"


class RateLimitRule(BaseModel):
    """Rate limiting rule configuration."""
    
    # Rule identification
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(default=None, description="Rule description")
    enabled: bool = Field(default=True, description="Rule enabled status")
    
    # Rate limit configuration
    limit_type: RateLimitType = Field(..., description="Type of rate limit")
    limit_value: int = Field(..., ge=1, description="Rate limit value")
    window_size: int = Field(..., ge=1, description="Time window in seconds")
    scope: RateLimitScope = Field(..., description="Rate limit scope")
    
    # Matching criteria
    path_patterns: List[str] = Field(default_factory=list, description="Path patterns to match")
    methods: List[str] = Field(default_factory=list, description="HTTP methods to match")
    user_roles: List[str] = Field(default_factory=list, description="User roles to match")
    service_names: List[str] = Field(default_factory=list, description="Service names to match")
    
    # Priority and exceptions
    priority: TrafficPriority = Field(default=TrafficPriority.NORMAL, description="Traffic priority")
    bypass_therapeutic: bool = Field(default=False, description="Bypass for therapeutic sessions")
    bypass_crisis: bool = Field(default=True, description="Bypass for crisis situations")
    
    # Actions
    block_on_exceed: bool = Field(default=True, description="Block requests when limit exceeded")
    delay_on_exceed: Optional[float] = Field(default=None, description="Delay in seconds when limit exceeded")
    custom_response: Optional[Dict[str, Any]] = Field(default=None, description="Custom response when limit exceeded")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Rule update timestamp")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('path_patterns')
    def validate_path_patterns(cls, v):
        """Validate path patterns."""
        if not v:
            return ["*"]  # Default to match all paths
        return v
    
    @validator('methods')
    def validate_methods(cls, v):
        """Validate HTTP methods."""
        if not v:
            return ["*"]  # Default to match all methods
        return [method.upper() for method in v]
    
    def matches_request(self, path: str, method: str, user_role: Optional[str] = None, 
                       service_name: Optional[str] = None) -> bool:
        """Check if rule matches a request."""
        # Check path patterns
        if self.path_patterns and "*" not in self.path_patterns:
            import fnmatch
            if not any(fnmatch.fnmatch(path, pattern) for pattern in self.path_patterns):
                return False
        
        # Check methods
        if self.methods and "*" not in self.methods:
            if method.upper() not in self.methods:
                return False
        
        # Check user roles
        if self.user_roles and user_role:
            if user_role not in self.user_roles:
                return False
        
        # Check service names
        if self.service_names and service_name:
            if service_name not in self.service_names:
                return False
        
        return True


class RateLimitConfig(BaseModel):
    """Complete rate limiting configuration."""
    
    # Global configuration
    enabled: bool = Field(default=True, description="Rate limiting enabled")
    default_limit: int = Field(default=100, ge=1, description="Default requests per minute")
    burst_limit: int = Field(default=200, ge=1, description="Burst limit for short periods")
    
    # Therapeutic-specific configuration
    therapeutic_multiplier: float = Field(default=2.0, ge=1.0, description="Rate limit multiplier for therapeutic sessions")
    crisis_bypass: bool = Field(default=True, description="Bypass rate limits for crisis situations")
    
    # Rules and policies
    rules: List[RateLimitRule] = Field(default_factory=list, description="Rate limiting rules")
    
    # Storage configuration
    storage_backend: str = Field(default="redis", description="Storage backend for rate limit data")
    key_prefix: str = Field(default="tta:gateway:ratelimit", description="Key prefix for storage")
    
    # Monitoring
    log_violations: bool = Field(default=True, description="Log rate limit violations")
    alert_on_violations: bool = Field(default=True, description="Alert on rate limit violations")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_applicable_rules(self, path: str, method: str, user_role: Optional[str] = None,
                           service_name: Optional[str] = None) -> List[RateLimitRule]:
        """Get applicable rate limiting rules for a request."""
        return [
            rule for rule in self.rules
            if rule.enabled and rule.matches_request(path, method, user_role, service_name)
        ]


class RateLimitStatus(BaseModel):
    """Current rate limit status for a client."""
    
    # Identification
    client_id: str = Field(..., description="Client identifier (IP, user ID, etc.)")
    scope: RateLimitScope = Field(..., description="Rate limit scope")
    rule_name: str = Field(..., description="Applied rule name")
    
    # Current status
    current_count: int = Field(default=0, description="Current request count in window")
    limit_value: int = Field(..., description="Rate limit value")
    window_start: datetime = Field(..., description="Current window start time")
    window_end: datetime = Field(..., description="Current window end time")
    
    # Status flags
    is_exceeded: bool = Field(default=False, description="Rate limit exceeded")
    is_blocked: bool = Field(default=False, description="Client is blocked")
    
    # Timestamps
    first_request: datetime = Field(default_factory=datetime.utcnow, description="First request in window")
    last_request: datetime = Field(default_factory=datetime.utcnow, description="Last request timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @property
    def remaining_requests(self) -> int:
        """Get remaining requests in current window."""
        return max(0, self.limit_value - self.current_count)
    
    @property
    def reset_time(self) -> datetime:
        """Get time when rate limit resets."""
        return self.window_end
    
    def increment(self) -> None:
        """Increment request count."""
        self.current_count += 1
        self.last_request = datetime.utcnow()
        self.is_exceeded = self.current_count > self.limit_value


class TherapeuticEvent(BaseModel):
    """Therapeutic event for priority handling."""
    
    # Event identification
    event_id: UUID = Field(..., description="Unique event identifier")
    user_id: UUID = Field(..., description="User identifier")
    session_id: Optional[UUID] = Field(default=None, description="Therapeutic session identifier")
    
    # Event details
    event_type: str = Field(..., description="Type of therapeutic event")
    priority: TrafficPriority = Field(..., description="Event priority level")
    description: Optional[str] = Field(default=None, description="Event description")
    
    # Crisis information
    is_crisis: bool = Field(default=False, description="Crisis event flag")
    crisis_level: Optional[int] = Field(default=None, ge=1, le=5, description="Crisis severity level (1-5)")
    intervention_required: bool = Field(default=False, description="Requires immediate intervention")
    
    # Timestamps
    occurred_at: datetime = Field(default_factory=datetime.utcnow, description="Event occurrence timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Event expiration timestamp")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def is_active(self) -> bool:
        """Check if event is still active."""
        if self.expires_at:
            return datetime.utcnow() < self.expires_at
        return True
    
    def get_priority_multiplier(self) -> float:
        """Get rate limit multiplier based on event priority."""
        multipliers = {
            TrafficPriority.LOW: 0.5,
            TrafficPriority.NORMAL: 1.0,
            TrafficPriority.HIGH: 2.0,
            TrafficPriority.THERAPEUTIC: 3.0,
            TrafficPriority.CRISIS: 10.0,
        }
        return multipliers.get(self.priority, 1.0)
