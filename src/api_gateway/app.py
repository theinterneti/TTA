"""
Main API Gateway application.

This module contains the FastAPI application instance and configuration
for the TTA API Gateway & Service Integration system.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .config import GatewaySettings, get_gateway_settings
from .core import GatewayCore, create_gateway_router
from .middleware.auth import AuthenticationMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware
from .middleware.security import SecurityHeadersMiddleware
from .middleware.therapeutic_safety import TherapeuticSafetyMiddleware
from .monitoring.health import health_router
from .monitoring.metrics import metrics_router
from .services import ServiceDiscoveryManager, AutoRegistrationService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the API Gateway.
    """
    # Startup
    settings = get_gateway_settings()

    # Initialize service discovery
    discovery_manager = ServiceDiscoveryManager()
    await discovery_manager.initialize()

    # Initialize gateway core
    gateway_core = GatewayCore(discovery_manager)
    await gateway_core.initialize()

    # Initialize auto-registration service
    auto_registration = AutoRegistrationService(discovery_manager)
    await auto_registration.register_tta_services()

    # Store instances in app state for access in routes
    app.state.discovery_manager = discovery_manager
    app.state.gateway_core = gateway_core
    app.state.auto_registration = auto_registration

    print(f"🚀 TTA API Gateway starting on {settings.host}:{settings.port}")

    yield

    # Shutdown
    print("🛑 TTA API Gateway shutting down")

    # Cleanup resources
    await auto_registration.deregister_all_services()
    await gateway_core.close()
    await discovery_manager.close()


def create_gateway_app() -> FastAPI:
    """
    Create and configure the API Gateway FastAPI application.
    
    Returns:
        FastAPI: Configured API Gateway application
    """
    settings = get_gateway_settings()
    
    app = FastAPI(
        title="TTA API Gateway",
        description="Unified entry point for all TTA services with centralized routing, "
                   "authentication, rate limiting, and therapeutic safety monitoring.",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add security middleware
    if settings.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
    
    # Add CORS middleware
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware (order matters - last added runs first)
    app.add_middleware(TherapeuticSafetyMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    
    return app


# Create the application instance
app = create_gateway_app()


@app.get("/")
async def root():
    """Root endpoint for the API Gateway."""
    return {
        "service": "TTA API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "description": "Unified entry point for all TTA services"
    }


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def gateway_route(request: Request, path: str) -> Response:
    """
    Main gateway route handler for all API requests.

    Args:
        request: FastAPI request
        path: Request path

    Returns:
        Response: Processed response from target service
    """
    if hasattr(request.app.state, 'gateway_core'):
        return await request.app.state.gateway_core.process_request(request)
    else:
        # Fallback if gateway core is not initialized
        return JSONResponse(
            status_code=503,
            content={
                "error": "Gateway not ready",
                "message": "Gateway core is not initialized",
                "code": "GATEWAY_NOT_READY"
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_gateway_settings()
    uvicorn.run(
        "src.api_gateway.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )
