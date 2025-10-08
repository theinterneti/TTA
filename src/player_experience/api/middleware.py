"""
Custom middleware for the Player Experience API.

This module provides various middleware components for security, logging,
rate limiting, and authentication with integrated monitoring and security features.
"""

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..monitoring.logging_config import LogCategory, LogContext, get_logger
from ..monitoring.metrics_collector import record_request_metric
from ..monitoring.performance_monitor import get_performance_monitor
from .auth import AuthenticationError, verify_token

# Configure structured logging
logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to all responses.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response with security headers added
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )

        # Note: CORS headers are handled by CORSMiddleware in app.py
        # Do not add wildcard CORS headers here as they conflict with credentials mode

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware for structured logging and monitoring."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response information with structured logging.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response from the next handler
        """
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract request information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        endpoint = request.url.path
        method = request.method

        # Create logging context
        log_context = LogContext(
            request_id=request_id,
            endpoint=endpoint,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Log request start
        logger.info(
            f"Request started: {method} {endpoint}",
            category=LogCategory.API,
            context=log_context,
            metadata={
                "method": method,
                "endpoint": endpoint,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        # Get performance monitor
        performance_monitor = get_performance_monitor()

        # Track request performance
        # Support both dict-like and Pydantic TokenData stored on request.state.current_player
        cp = getattr(request.state, "current_player", None)
        user_id = None
        has_player_id = False

        if cp is not None:
            try:
                user_id = (
                    cp.get("player_id")
                    if isinstance(cp, dict)
                    else getattr(cp, "player_id", None)
                )
                has_player_id = user_id is not None
            except Exception:
                user_id = getattr(cp, "player_id", None)
                has_player_id = user_id is not None

        # Record player_id presence metrics for authenticated endpoints
        if endpoint not in ["/health", "/metrics", "/docs", "/openapi.json"]:
            try:
                from src.monitoring.prometheus_metrics import get_metrics_collector

                collector = get_metrics_collector("player-experience")
                collector.record_player_id_presence(endpoint, has_player_id)
            except Exception as e:
                logger.debug(f"Failed to record player_id presence metrics: {e}")

        with performance_monitor.request_tracker.track_request(
            request_id, endpoint, method, user_id=user_id
        ):
            try:
                # Process request
                response = await call_next(request)

                # Calculate processing time
                process_time = time.time() - start_time

                # Record metrics
                record_request_metric(
                    endpoint, method, response.status_code, process_time
                )

                # Log response
                logger.info(
                    f"Request completed: {response.status_code}",
                    category=LogCategory.API,
                    context=log_context,
                    metadata={
                        "status_code": response.status_code,
                        "process_time": process_time,
                        "response_size": (
                            len(response.body) if hasattr(response, "body") else 0
                        ),
                    },
                )

                # Add headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(process_time)

                return response

            except Exception as e:
                process_time = time.time() - start_time

                # Record error metrics
                record_request_metric(endpoint, method, 500, process_time)

                # Log error
                logger.error(
                    f"Request failed: {str(e)}",
                    category=LogCategory.ERROR,
                    context=log_context,
                    metadata={
                        "error_type": type(e).__name__,
                        "process_time": process_time,
                    },
                    exc_info=True,
                )

                raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        """
        Initialize rate limiting middleware.

        Args:
            app: The FastAPI application
            calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting to requests.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response or rate limit error
        """
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Get current time
        now = datetime.now()

        # Clean old entries
        client_requests = self.clients[client_ip]
        while client_requests and client_requests[0] < now - timedelta(
            seconds=self.period
        ):
            client_requests.popleft()

        # Check rate limit
        if len(client_requests) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Limit: {self.calls} per {self.period} seconds",
                    "retry_after": self.period,
                },
                headers={"Retry-After": str(self.period)},
            )

        # Add current request
        client_requests.append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, self.calls - len(client_requests))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.period)).timestamp())
        )

        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication for protected routes."""

    # Routes that don't require authentication
    PUBLIC_ROUTES = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",  # gated by settings.debug inside the route
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/register",
        "/api/v1/gameplay/health",  # Gameplay health check endpoint
        "/api/v1/health/",  # System health check
        "/api/v1/health/redis",  # Redis health check
        "/api/v1/health/neo4j",  # Neo4j health check
        "/api/v1/health/agents",  # Agent orchestration health check
        "/api/v1/health/openrouter",  # OpenRouter health check
        "/api/v1/health/liveness",  # Kubernetes liveness probe
        "/api/v1/health/readiness",  # Kubernetes readiness probe
        "/api/v1/health/startup",  # Kubernetes startup probe
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle authentication for protected routes.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response from the next handler or authentication error
        """
        # Check if route is public
        if request.url.path in self.PUBLIC_ROUTES:
            return await call_next(request)

        # Check for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow unauthenticated player creation explicitly (POST /api/v1/players)
        # BUT if an Authorization header is present, verify it and attach current_player to request.state
        if (
            request.method == "POST"
            and request.url.path.rstrip("/") == "/api/v1/players"
        ):
            authorization = request.headers.get("Authorization")
            if authorization:
                try:
                    scheme, token = authorization.split(" ", 1)
                    if scheme.lower() == "bearer" and token:
                        try:
                            token_data = verify_token(token)
                            request.state.current_player = token_data
                        except AuthenticationError:
                            # Ignore invalid token for this public endpoint; proceed unauthenticated
                            pass
                except ValueError:
                    # Malformed Authorization header; ignore for public endpoint
                    pass
            return await call_next(request)

        # Get authorization header
        authorization = request.headers.get("Authorization")

        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Authentication Required",
                    "message": "Authorization header is required",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check Bearer token format
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid Authorization Header",
                    "message": "Authorization header must be in format: Bearer <token>",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token
        try:
            token_data = verify_token(token)

            # Add user info to request state
            request.state.current_player = token_data

        except AuthenticationError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Authentication Failed",
                    "message": str(e),
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Process request
        return await call_next(request)


class CrisisDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect potential crisis situations in requests."""

    # Keywords that might indicate crisis situations
    CRISIS_KEYWORDS = {
        "suicide",
        "kill myself",
        "end it all",
        "can't go on",
        "want to die",
        "self-harm",
        "hurt myself",
        "cutting",
        "overdose",
        "pills",
        "hopeless",
        "worthless",
        "nobody cares",
        "better off dead",
        "emergency",
        "crisis",
        "help me",
        "desperate",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor requests for crisis indicators.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response with potential crisis handling
        """
        # Get request body for analysis (if applicable)
        crisis_detected = False

        # For POST/PUT requests, check body content
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # This is a simplified check - in production, you'd want more sophisticated analysis
                body = await request.body()
                if body:
                    body_text = body.decode("utf-8").lower()

                    # Check for crisis keywords
                    for keyword in self.CRISIS_KEYWORDS:
                        if keyword in body_text:
                            crisis_detected = True
                            break

                # Recreate request with body for next handler
                from starlette.requests import Request as StarletteRequest

                async def receive() -> dict[str, str | bytes]:
                    return {"type": "http.request", "body": body}

                request = StarletteRequest(
                    request.scope,
                    receive=receive,
                )

            except Exception:
                # If we can't read the body, continue normally
                pass

        # Process request
        response = await call_next(request)

        # If crisis detected, add crisis support information to response
        if crisis_detected:
            # Log crisis detection
            logger.warning(
                f"Crisis indicators detected in request from {request.client.host if request.client else 'unknown'}"
            )

            # Add crisis support header
            response.headers["X-Crisis-Support"] = "available"

            # In a real implementation, you might:
            # 1. Trigger immediate crisis support protocols
            # 2. Notify mental health professionals
            # 3. Provide immediate crisis resources
            # 4. Escalate to emergency services if necessary

        return response


class TherapeuticSafetyMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure therapeutic safety and appropriate content delivery."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor and ensure therapeutic safety.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response with safety monitoring
        """
        # Process request
        response = await call_next(request)

        # Add therapeutic safety headers
        response.headers["X-Therapeutic-Safety"] = "monitored"
        response.headers["X-Crisis-Hotline"] = (
            "988"  # National Suicide Prevention Lifeline
        )

        # In a real implementation, this middleware would:
        # 1. Monitor therapeutic content for appropriateness
        # 2. Ensure proper therapeutic boundaries
        # 3. Track therapeutic progress and safety indicators
        # 4. Provide immediate safety resources when needed

        return response
