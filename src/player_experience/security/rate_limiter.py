"""
Advanced rate limiting and DDoS protection system.

This module provides multiple rate limiting algorithms and DDoS protection
mechanisms to secure the Player Experience Interface from abuse.
"""

import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import redis
from redis import Redis

from ..monitoring.logging_config import LogCategory, LogContext, get_logger

logger = get_logger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(str, Enum):
    """Scope for rate limiting."""

    GLOBAL = "global"
    IP_ADDRESS = "ip_address"
    USER = "user"
    ENDPOINT = "endpoint"
    API_KEY = "api_key"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_capacity: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    scope: RateLimitScope = RateLimitScope.IP_ADDRESS
    whitelist: list[str] = field(default_factory=list)
    blacklist: list[str] = field(default_factory=list)
    enable_adaptive: bool = True
    adaptive_threshold: float = 0.8  # Trigger adaptive limiting at 80% capacity


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int, limit_type: str):
        super().__init__(message)
        self.retry_after = retry_after
        self.limit_type = limit_type


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: int | None = None
    limit_type: str | None = None


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.lock = threading.RLock()

    @abstractmethod
    def check_limit(
        self, identifier: str, endpoint: str | None = None
    ) -> RateLimitResult:
        """Check if request is within rate limit."""
        pass

    @abstractmethod
    def reset_limit(self, identifier: str):
        """Reset rate limit for identifier."""
        pass

    def is_whitelisted(self, identifier: str) -> bool:
        """Check if identifier is whitelisted."""
        return identifier in self.config.whitelist

    def is_blacklisted(self, identifier: str) -> bool:
        """Check if identifier is blacklisted."""
        return identifier in self.config.blacklist

    def get_identifier(
        self,
        ip_address: str,
        user_id: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
    ) -> str:
        """Get rate limit identifier based on scope."""
        if self.config.scope == RateLimitScope.GLOBAL:
            return "global"
        elif self.config.scope == RateLimitScope.IP_ADDRESS:
            return ip_address
        elif self.config.scope == RateLimitScope.USER and user_id:
            return f"user:{user_id}"
        elif self.config.scope == RateLimitScope.ENDPOINT and endpoint:
            return f"endpoint:{endpoint}:{ip_address}"
        elif self.config.scope == RateLimitScope.API_KEY and api_key:
            return f"api_key:{api_key}"
        else:
            return ip_address  # Default to IP address


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter implementation."""

    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.buckets: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "tokens": config.burst_capacity,
                "last_refill": time.time(),
                "requests": deque(),
            }
        )

    def check_limit(
        self, identifier: str, endpoint: str | None = None
    ) -> RateLimitResult:
        """Check token bucket rate limit."""
        if self.is_whitelisted(identifier):
            return RateLimitResult(
                allowed=True,
                remaining=self.config.burst_capacity,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

        if self.is_blacklisted(identifier):
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                retry_after=3600,
                limit_type="blacklisted",
            )

        with self.lock:
            bucket = self.buckets[identifier]
            current_time = time.time()

            # Refill tokens based on time elapsed
            time_elapsed = current_time - bucket["last_refill"]
            tokens_to_add = time_elapsed * (self.config.requests_per_minute / 60.0)
            bucket["tokens"] = min(
                self.config.burst_capacity, bucket["tokens"] + tokens_to_add
            )
            bucket["last_refill"] = current_time

            # Check if request can be allowed
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                bucket["requests"].append(current_time)

                # Clean old requests
                cutoff_time = current_time - 3600  # Keep 1 hour of history
                while bucket["requests"] and bucket["requests"][0] < cutoff_time:
                    bucket["requests"].popleft()

                return RateLimitResult(
                    allowed=True,
                    remaining=int(bucket["tokens"]),
                    reset_time=datetime.utcnow()
                    + timedelta(seconds=60 / self.config.requests_per_minute),
                )
            else:
                # Calculate retry after
                retry_after = int(
                    (1 - bucket["tokens"]) * (60.0 / self.config.requests_per_minute)
                )

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(seconds=retry_after),
                    retry_after=retry_after,
                    limit_type="rate_limit",
                )

    def reset_limit(self, identifier: str):
        """Reset token bucket for identifier."""
        with self.lock:
            if identifier in self.buckets:
                self.buckets[identifier]["tokens"] = self.config.burst_capacity
                self.buckets[identifier]["last_refill"] = time.time()


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter implementation."""

    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.windows: dict[str, deque] = defaultdict(lambda: deque())

    def check_limit(
        self, identifier: str, endpoint: str | None = None
    ) -> RateLimitResult:
        """Check sliding window rate limit."""
        if self.is_whitelisted(identifier):
            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

        if self.is_blacklisted(identifier):
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                retry_after=3600,
                limit_type="blacklisted",
            )

        current_time = time.time()

        with self.lock:
            window = self.windows[identifier]

            # Remove requests outside the window
            cutoff_time = current_time - 60  # 1 minute window
            while window and window[0] < cutoff_time:
                window.popleft()

            # Check limits for different time windows
            minute_requests = len(window)
            hour_requests = len([t for t in window if t > current_time - 3600])
            day_requests = len([t for t in window if t > current_time - 86400])

            # Check if any limit is exceeded
            if minute_requests >= self.config.requests_per_minute:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(seconds=60),
                    retry_after=60,
                    limit_type="per_minute",
                )

            if hour_requests >= self.config.requests_per_hour:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(hours=1),
                    retry_after=3600,
                    limit_type="per_hour",
                )

            if day_requests >= self.config.requests_per_day:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(days=1),
                    retry_after=86400,
                    limit_type="per_day",
                )

            # Allow request
            window.append(current_time)

            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute - minute_requests - 1,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

    def reset_limit(self, identifier: str):
        """Reset sliding window for identifier."""
        with self.lock:
            if identifier in self.windows:
                self.windows[identifier].clear()


class RedisRateLimiter(RateLimiter):
    """Redis-based distributed rate limiter."""

    def __init__(self, config: RateLimitConfig, redis_client: Redis):
        super().__init__(config)
        self.redis = redis_client

    def check_limit(
        self, identifier: str, endpoint: str | None = None
    ) -> RateLimitResult:
        """Check rate limit using Redis."""
        if self.is_whitelisted(identifier):
            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

        if self.is_blacklisted(identifier):
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                retry_after=3600,
                limit_type="blacklisted",
            )

        current_time = int(time.time())
        pipe = self.redis.pipeline()

        # Sliding window implementation with Redis
        key = f"rate_limit:{identifier}"
        window_start = current_time - 60  # 1 minute window

        try:
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration
            pipe.expire(key, 3600)  # Keep data for 1 hour

            results = pipe.execute()
            current_requests = results[1]

            if current_requests >= self.config.requests_per_minute:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(minutes=1),
                    retry_after=60,
                    limit_type="per_minute",
                )

            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute - current_requests - 1,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

        except redis.RedisError as e:
            logger.error(f"Redis rate limiter error: {e}", category=LogCategory.ERROR)
            # Fail open - allow request if Redis is unavailable
            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute,
                reset_time=datetime.utcnow() + timedelta(minutes=1),
            )

    def reset_limit(self, identifier: str):
        """Reset rate limit in Redis."""
        key = f"rate_limit:{identifier}"
        try:
            self.redis.delete(key)
        except redis.RedisError as e:
            logger.error(
                f"Redis rate limiter reset error: {e}", category=LogCategory.ERROR
            )


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts limits based on system load."""

    def __init__(self, config: RateLimitConfig, base_limiter: RateLimiter):
        super().__init__(config)
        self.base_limiter = base_limiter
        self.system_load = 0.0
        self.error_rate = 0.0
        self.adaptive_factor = 1.0
        self.last_adjustment = time.time()

    def update_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        error_rate: float,
        response_time: float,
    ):
        """Update system metrics for adaptive limiting."""
        # Calculate system load score (0.0 to 1.0)
        self.system_load = max(cpu_usage / 100.0, memory_usage / 100.0)
        self.error_rate = error_rate / 100.0

        # Adjust adaptive factor based on system health
        current_time = time.time()
        if current_time - self.last_adjustment > 60:  # Adjust every minute
            if self.system_load > 0.8 or self.error_rate > 0.1 or response_time > 2.0:
                # System under stress - reduce limits
                self.adaptive_factor = max(0.1, self.adaptive_factor * 0.8)
            elif (
                self.system_load < 0.5
                and self.error_rate < 0.01
                and response_time < 0.5
            ):
                # System healthy - increase limits
                self.adaptive_factor = min(2.0, self.adaptive_factor * 1.1)

            self.last_adjustment = current_time

            logger.info(
                f"Adaptive rate limiter adjusted: factor={self.adaptive_factor:.2f}, "
                f"load={self.system_load:.2f}, error_rate={self.error_rate:.2f}",
                category=LogCategory.PERFORMANCE,
            )

    def check_limit(
        self, identifier: str, endpoint: str | None = None
    ) -> RateLimitResult:
        """Check adaptive rate limit."""
        # Get base result
        result = self.base_limiter.check_limit(identifier, endpoint)

        if not result.allowed:
            return result

        # Apply adaptive factor
        if self.adaptive_factor < 1.0:
            # Reduce effective limit
            import random

            if random.random() > self.adaptive_factor:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=result.reset_time,
                    retry_after=60,
                    limit_type="adaptive_limit",
                )

        return result

    def reset_limit(self, identifier: str):
        """Reset adaptive rate limit."""
        self.base_limiter.reset_limit(identifier)


class RateLimitMiddleware:
    """Middleware for applying rate limiting to requests."""

    def __init__(
        self, rate_limiter: RateLimiter, get_identifier_func: Callable | None = None
    ):
        self.rate_limiter = rate_limiter
        self.get_identifier = get_identifier_func or self._default_get_identifier

    def _default_get_identifier(self, request) -> str:
        """Default identifier extraction from request."""
        # This would be implemented based on your web framework
        # For FastAPI, you might extract from request.client.host
        return getattr(request.client, "host", "unknown")

    async def __call__(self, request, call_next):
        """Apply rate limiting to request."""
        identifier = self.get_identifier(request)
        endpoint = getattr(request.url, "path", None)

        try:
            result = self.rate_limiter.check_limit(identifier, endpoint)

            if not result.allowed:
                # Provide defaults for optional fields
                retry_after = result.retry_after or 60
                limit_type = result.limit_type or "rate_limit"

                # Log rate limit violation
                logger.warning(
                    f"Rate limit exceeded for {identifier}",
                    category=LogCategory.SECURITY,
                    context=LogContext(ip_address=identifier, endpoint=endpoint),
                    metadata={
                        "limit_type": limit_type,
                        "retry_after": retry_after,
                    },
                )

                raise RateLimitExceeded(
                    f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    retry_after,
                    limit_type,
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Remaining"] = str(result.remaining)
            response.headers["X-RateLimit-Reset"] = str(
                int(result.reset_time.timestamp())
            )

            return response

        except RateLimitExceeded:
            # Return rate limit error response
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(result.retry_after),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(result.reset_time.timestamp())),
                },
            ) from None


def create_rate_limiter(
    config: RateLimitConfig, redis_client: Redis | None = None
) -> RateLimiter:
    """Factory function to create appropriate rate limiter."""
    if redis_client:
        base_limiter = RedisRateLimiter(config, redis_client)
    elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
        base_limiter = TokenBucketRateLimiter(config)
    elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
        base_limiter = SlidingWindowRateLimiter(config)
    else:
        base_limiter = TokenBucketRateLimiter(config)  # Default

    if config.enable_adaptive:
        return AdaptiveRateLimiter(config, base_limiter)
    else:
        return base_limiter


# Backward-compat shim expected by middleware imports
# Provides a simple getter that returns a default validator callable; adjust as needed.
def get_security_validator():
    def _validator(_: Any) -> bool:
        return True

    return _validator
