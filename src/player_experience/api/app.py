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

from ..utils.validation import ValidationError
from .auth import AuthenticationError, AuthorizationError
from .middleware import (
    AuthenticationMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    TherapeuticSafetyMiddleware,
)
from .routers import auth, characters, players, worlds, chat, sessions, progress, health, services, nexus
from .routers import metrics as metrics_router
from .services.connection_manager import initialize_services, close_services
from ..database.nexus_schema import NexusSchemaManager, validate_nexus_schema



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    print("Starting Player Experience Interface API...")

    # Initialize service connections
    try:
        success = await initialize_services()
        if success:
            print("✅ All services initialized successfully")

            # Initialize Nexus Codex schema
            from .services.connection_manager import get_service_manager
            service_manager = get_service_manager()

            if service_manager and service_manager.neo4j:
                nexus_manager = NexusSchemaManager(service_manager.neo4j.driver)
                schema_created = await nexus_manager.create_nexus_schema()

                if schema_created:
                    print("✅ Nexus Codex schema initialized successfully")
                else:
                    print("⚠️ Failed to initialize Nexus Codex schema")
        else:
            print("⚠️  Some services failed to initialize - check service health")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")

    yield

    # Shutdown
    print("Shutting down Player Experience Interface API...")

    # Cleanup service connections
    try:
        await close_services()
        print("✅ All services closed successfully")
    except Exception as e:
        print(f"❌ Error closing services: {e}")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    import os

    # Define API tags for organized documentation
    tags_metadata = [
        {
            "name": "health",
            "description": "Health check endpoints for monitoring system status and service availability.",
        },
        {
            "name": "services",
            "description": "Service management endpoints for monitoring and controlling external service connections.",
        },
        {
            "name": "authentication",
            "description": "User authentication and authorization endpoints including login, registration, and token management.",
        },
        {
            "name": "players",
            "description": "Player management endpoints for creating, updating, and retrieving player profiles and data.",
        },
        {
            "name": "characters",
            "description": "Character management endpoints for game character creation, customization, and progression.",
        },
        {
            "name": "worlds",
            "description": "Game world management endpoints for creating and managing virtual environments and scenarios.",
        },
        {
            "name": "sessions",
            "description": "Game session management endpoints for starting, monitoring, and controlling gameplay sessions.",
        },
        {
            "name": "progress",
            "description": "Player progress tracking endpoints for monitoring achievements, milestones, and therapeutic outcomes.",
        },
        {
            "name": "chat",
            "description": "Real-time chat and communication endpoints using WebSocket connections for interactive gameplay.",
        },
        {
            "name": "metrics",
            "description": "System metrics and monitoring endpoints for performance analysis and debugging (development only).",
        },
    ]

    app = FastAPI(
        title="Player Experience Interface API",
        description="API for the TTA (Therapeutic Technology Applications) Player Experience Interface - "
                   "A comprehensive system for AI-driven therapeutic gaming experiences with real-time "
                   "monitoring, personalized content delivery, and integrated health tracking.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=tags_metadata,
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

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(players.router, prefix="/api/v1/players", tags=["players"])
    app.include_router(characters.router, prefix="/api/v1/characters", tags=["characters"])
    app.include_router(worlds.router, prefix="/api/v1/worlds", tags=["worlds"])
    app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
    # Metrics (gated by settings.debug)
    app.include_router(metrics_router.router, tags=["metrics"])
    app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
    # Nexus Codex endpoints
    app.include_router(nexus.router, prefix="/api/v1", tags=["nexus"])

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