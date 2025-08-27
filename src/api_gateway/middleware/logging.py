"""
Logging middleware for the API Gateway.

This middleware provides comprehensive request/response logging with
correlation IDs, structured logging, and integration with TTA's
existing logging infrastructure.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_gateway_settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging.
    
    Features:
    - Request/response logging with correlation IDs
    - Performance timing
    - Structured logging format
    - Integration with therapeutic safety monitoring
    """
    
    def __init__(self, app, logger=None):
        super().__init__(app)
        self.settings = get_gateway_settings()
        self.logger = logger or self._get_logger()
    
    def _get_logger(self):
        """Get or create logger instance."""
        import logging
        
        logger = logging.getLogger("api_gateway")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            
            if self.settings.structured_logging:
                # Use structured logging format
                formatter = logging.Formatter(
                    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                    '"logger": "%(name)s", "message": "%(message)s"}'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.settings.log_level.upper()))
        
        return logger
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with comprehensive logging.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The response from the next handler
        """
        # Generate correlation ID for request tracing
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Extract request information
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        # Log incoming request
        self.logger.info(
            f"Request started - {method} {path}",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "event_type": "request_start"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful response
            self.logger.info(
                f"Request completed - {method} {path} - {response.status_code}",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": client_ip,
                    "event_type": "request_complete"
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate processing time for error case
            process_time = time.time() - start_time
            
            # Log error
            self.logger.error(
                f"Request failed - {method} {path} - {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": process_time,
                    "client_ip": client_ip,
                    "event_type": "request_error"
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.
        
        Handles various proxy headers and forwarded IPs.
        
        Args:
            request: The incoming request
            
        Returns:
            str: Client IP address
        """
        # Check for forwarded headers (common in load balancer setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
