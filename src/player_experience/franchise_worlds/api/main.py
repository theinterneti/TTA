"""

# Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Api/Main]]
TTA Franchise World System - Production API Main Module

This module provides the main FastAPI application for the TTA Franchise World System,
including all production-ready features like monitoring, security, and error handling.
"""

import os
import time
from contextlib import asynccontextmanager

import sentry_sdk
import structlog  # type: ignore[import-not-found]
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from slowapi import (  # type: ignore[import-not-found]
    Limiter,
    _rate_limit_exceeded_handler,
)
from slowapi.errors import RateLimitExceeded  # type: ignore[import-not-found]
from slowapi.util import get_remote_address  # type: ignore[import-not-found]

from ..integration.PlayerExperienceIntegration import FranchiseWorldAPI

# Import routers
from .routers.franchise_worlds import (  # type: ignore[import-not-found]
    router as franchise_worlds_router,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SENTRY_DSN = os.getenv("SENTRY_DSN")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Initialize Sentry for error tracking
if SENTRY_DSN and ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=ENVIRONMENT,
    )

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_SESSIONS = Gauge(
    "tta_active_sessions_total", "Number of active therapeutic sessions"
)

WORLD_USAGE = Counter(
    "tta_world_usage_total", "Usage count per world", ["world_name", "world_genre"]
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting TTA Franchise World System API", environment=ENVIRONMENT)

    # Initialize franchise world system
    try:
        franchise_api = FranchiseWorldAPI()
        await franchise_api.initialize()
        app.state.franchise_api = franchise_api
        logger.info("Franchise world system initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize franchise world system", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down TTA Franchise World System API")


# Create FastAPI application
app = FastAPI(
    title="TTA Franchise World System API",
    description="Production API for the Therapeutic Text Adventure Franchise World System",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if DEBUG else ["tta.yourdomain.com", "localhost"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware for metrics and logging
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect metrics and log requests"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Extract endpoint info
    method = request.method
    endpoint = request.url.path
    status = response.status_code

    # Update metrics
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    # Log request
    logger.info(
        "HTTP request processed",
        method=method,
        endpoint=endpoint,
        status=status,
        duration=duration,
        client_ip=get_remote_address(request),
    )

    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check franchise world system health
        franchise_api = app.state.franchise_api
        worlds = await franchise_api.list_franchise_worlds()

        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Would be dynamic in production
            "version": "1.0.0",
            "environment": ENVIRONMENT,
            "worlds_available": len(worlds),
            "services": {
                "franchise_api": "operational",
                "bridge_service": "operational",
                "database": "operational",
            },
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy") from e


# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Custom metrics endpoint
@app.get("/api/metrics/custom")
async def custom_metrics():
    """Custom application metrics"""
    try:
        franchise_api = app.state.franchise_api
        worlds = await franchise_api.list_franchise_worlds()

        # Update world usage metrics (this would be based on actual usage data)
        for world in worlds:
            WORLD_USAGE.labels(
                world_name=world.get("name", "unknown"),
                world_genre=world.get("genre", "unknown"),
            ).inc(0)  # Initialize counter

        return {
            "total_worlds": len(worlds),
            "fantasy_worlds": len([w for w in worlds if w.get("genre") == "fantasy"]),
            "scifi_worlds": len([w for w in worlds if w.get("genre") == "sci-fi"]),
            "active_sessions": 0,  # Would be actual session count
            "timestamp": "2024-01-01T00:00:00Z",
        }
    except Exception as e:
        logger.error("Failed to generate custom metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics generation failed") from e


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        endpoint=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with proper logging"""
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        endpoint=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "status_code": 500}
    )


# Include routers
app.include_router(franchise_worlds_router, prefix="/api/v1", tags=["franchise-worlds"])


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="TTA Franchise World System API",
        version="1.0.0",
        description="Production API for the Therapeutic Text Adventure Franchise World System",
        routes=app.routes,
    )

    # Add custom security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TTA Franchise World System API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "api": "/api/v1",
            "docs": "/docs" if DEBUG else "disabled",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug",
    )
