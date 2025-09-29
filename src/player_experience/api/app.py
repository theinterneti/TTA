"""
Main FastAPI application for the Player Experience Interface.

This module sets up the FastAPI application with middleware, error handling,
authentication, and CORS configuration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import PlainTextResponse

# Try relative import first, fall back to absolute import
try:
    from ..utils.validation import ValidationError
except ImportError:
    from src.player_experience.utils.validation import ValidationError

try:
    from .auth import AuthenticationError, AuthorizationError
except ImportError:
    from src.player_experience.api.auth import AuthenticationError, AuthorizationError

try:
    from .middleware import (
        AuthenticationMiddleware,
        LoggingMiddleware,
        RateLimitMiddleware,
        SecurityHeadersMiddleware,
        TherapeuticSafetyMiddleware,
    )
except ImportError:
    from src.player_experience.api.middleware import (
        AuthenticationMiddleware,
        LoggingMiddleware,
        RateLimitMiddleware,
        SecurityHeadersMiddleware,
        TherapeuticSafetyMiddleware,
    )

try:
    from .routers import auth, characters, players, worlds, chat, sessions, progress, settings, conversation
    from .routers import metrics as metrics_router
    from .routers import openrouter_auth, gameplay
except ImportError:
    from src.player_experience.api.routers import auth, characters, players, worlds, chat, sessions, progress, settings, conversation
    from src.player_experience.api.routers import metrics as metrics_router
    from src.player_experience.api.routers import openrouter_auth, gameplay

try:
    from .config import get_settings
    from .sentry_config import init_sentry
except ImportError:
    from src.player_experience.api.config import get_settings
    from src.player_experience.api.sentry_config import init_sentry



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    print("Starting Player Experience Interface API...")

    # Initialize Sentry for error monitoring and performance tracking
    settings = get_settings()
    init_sentry(settings)

    # Initialize any required services here
    # e.g., database connections, cache connections, etc.

    yield

    # Shutdown
    print("Shutting down Player Experience Interface API...")

    # Cleanup any resources here
    # e.g., close database connections, cache connections, etc.


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    import os

    app = FastAPI(
        title="Player Experience Interface API",
        description="API for the TTA Player Experience Interface",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React development server
            "http://localhost:8080",  # Alternative frontend port
            "https://localhost:3000",  # HTTPS development
            "https://localhost:8080",  # HTTPS alternative
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TherapeuticSafetyMiddleware)

    # Rate limiting (configurable via env for tests): PEI_RATE_LIMIT_CALLS/PEI_RATE_LIMIT_PERIOD
    rl_calls = int(os.getenv("PEI_RATE_LIMIT_CALLS", "100"))
    rl_period = int(os.getenv("PEI_RATE_LIMIT_PERIOD", "60"))
    app.add_middleware(RateLimitMiddleware, calls=rl_calls, period=rl_period)

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthenticationMiddleware)

    # Add Prometheus metrics middleware
    try:
        from monitoring.metrics_middleware import setup_monitoring_middleware
        setup_monitoring_middleware(app, service_name="player-experience")
    except ImportError:
        # Fallback if monitoring module not available
        pass

    # Include routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(openrouter_auth.router, prefix="/api/v1", tags=["openrouter-auth"])
    app.include_router(players.router, prefix="/api/v1/players", tags=["players"])
    app.include_router(characters.router, prefix="/api/v1/characters", tags=["characters"])
    app.include_router(worlds.router, prefix="/api/v1/worlds", tags=["worlds"])
    app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
    app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["conversation"])
    app.include_router(settings.router, prefix="/api/v1/players", tags=["settings"])
    # Add Prometheus metrics endpoint (no authentication required) - BEFORE routers
    @app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
    async def prometheus_metrics():
        """Prometheus metrics endpoint for monitoring (no auth required)."""
        try:
            import prometheus_client
            from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

            # Generate basic metrics for the TTA Player API
            metrics_output = generate_latest()
            return PlainTextResponse(
                content=metrics_output.decode('utf-8'),
                media_type=CONTENT_TYPE_LATEST
            )
        except ImportError:
            # Fallback to basic metrics if prometheus_client not available
            return PlainTextResponse(
                content="# Prometheus metrics not available\n# Install prometheus-client package\n",
                media_type="text/plain"
            )
        except Exception as e:
            return PlainTextResponse(
                content=f"# Error generating Prometheus metrics: {e}\n",
                status_code=500,
                media_type="text/plain"
            )

    app.include_router(gameplay.router, prefix="/api/v1/gameplay", tags=["gameplay"])
    # Metrics (gated by settings.debug) - now includes /metrics-prom endpoint
    app.include_router(metrics_router.router, tags=["metrics"])
    app.include_router(progress.router, prefix="/api/v1", tags=["progress"])

    # WebSocket endpoints (mounted under /ws)
    app.include_router(chat.router, prefix="/ws", tags=["chat"])

    # Register exception handlers
    register_exception_handlers(app)

    # Add root endpoints
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint for health check."""
        return {"message": "Player Experience Interface API is running"}

    @app.options("/")
    async def root_options() -> dict[str, str]:
        """OPTIONS handler for root endpoint."""
        return {"message": "OK"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "player-experience-api"}

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for the application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        from fastapi.encoders import jsonable_encoder
        errs = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": errs,
                "detail": errs,
            },
        )

    @app.exception_handler(ValidationError)
    async def custom_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle custom validation errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation Error",
                "message": str(exc),
            },
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """Handle authentication errors."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Authentication Error",
                "message": str(exc),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        """Handle authorization errors."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Authorization Error",
                "message": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Log and include a minimal detail for easier test debugging
        try:
            import logging
            logging.getLogger(__name__).error("Unhandled exception", exc_info=exc)

            # Capture exception in Sentry with therapeutic context
            from sentry_config import capture_therapeutic_error
            capture_therapeutic_error(
                exc,
                context={
                    "request_method": request.method,
                    "request_url": str(request.url),
                    "request_headers": dict(request.headers),
                },
            )
        except Exception:
            pass
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "detail": str(exc.__class__.__name__),
            },
        )


# Create the application instance
app = create_app()