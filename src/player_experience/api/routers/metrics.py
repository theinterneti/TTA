"""
Enhanced metrics router with Prometheus integration for TTA Player Experience API.
Provides both legacy metrics and new Prometheus metrics endpoints.
"""

from __future__ import annotations

import contextlib

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import PlainTextResponse

from ...monitoring.metrics_collector import get_metrics_collector

# Import Prometheus metrics with fallback
try:
    from ...monitoring.prometheus_metrics import (  # type: ignore[import-not-found]
        CONTENT_TYPE_LATEST,
    )
    from ...monitoring.prometheus_metrics import (
        get_metrics_collector as get_prometheus_collector,  # type: ignore[import-not-found]
    )

    prometheus_available = True
except ImportError:
    prometheus_available = False

PROMETHEUS_AVAILABLE = prometheus_available

router = APIRouter()


def _metrics_allowed() -> None:
    # Only allow when debug/testing is enabled; import settings at runtime to honor test overrides
    with contextlib.suppress(Exception):
        from ..config import get_settings

        current_settings = get_settings()
        if not getattr(current_settings, "debug", False):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/metrics", dependencies=[Depends(_metrics_allowed)])
async def get_legacy_metrics() -> dict:
    """Return a minimal snapshot of counters/timers to aid tests and local diagnostics."""
    mc = get_metrics_collector()
    # Provide shallow views to avoid heavy serialization
    return {
        "counters": dict(mc.counters),
        "gauges": dict(mc.gauges),
        "timers": {k: (sum(v) / len(v) if v else 0.0) for k, v in mc.timers.items()},
    }


@router.get(
    "/metrics-prom",
    response_class=PlainTextResponse,
    dependencies=[Depends(_metrics_allowed)],
)
async def get_prometheus_metrics():
    """Return Prometheus-formatted metrics for the Player Experience API."""
    if not PROMETHEUS_AVAILABLE:
        return PlainTextResponse(
            content="# Prometheus metrics not available\n# Install prometheus-client package\n",
            media_type="text/plain",
        )

    try:
        collector = get_prometheus_collector("player-experience")
        metrics_data = collector.get_metrics()
        return PlainTextResponse(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return PlainTextResponse(
            content=f"# Error generating Prometheus metrics: {e}\n",
            status_code=500,
            media_type="text/plain",
        )


@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for monitoring systems."""
    return {
        "status": "healthy",
        "service": "player-experience-api",
        "version": "1.0.0",
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "timestamp": "2025-09-15T12:00:00Z",
    }
