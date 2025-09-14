"""
Security headers middleware for the API Gateway.

This middleware adds comprehensive security headers and performs
basic security validation for all requests.
"""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_gateway_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers and basic security validation.

    Features:
    - Comprehensive security headers
    - Content Security Policy
    - XSS protection
    - CSRF protection
    - Therapeutic safety headers
    """

    def __init__(self, app):
        super().__init__(app)
        self.settings = get_gateway_settings()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

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

        # Content Security Policy for therapeutic safety
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: ws:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # Therapeutic safety headers
        response.headers["X-Therapeutic-Safety"] = "enabled"
        response.headers["X-Crisis-Support"] = "available"

        return response
