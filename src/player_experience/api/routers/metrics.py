"""
Metrics router to expose lightweight metrics for testing/dev.
Gated by settings.debug flag to avoid accidental exposure in production.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...monitoring.metrics_collector import get_metrics_collector

router = APIRouter()


def _metrics_allowed() -> None:
    # Only allow when debug/testing is enabled; import settings at runtime to honor test overrides
    from .. import config as config_module  # local import to read current settings object
    current_settings = getattr(config_module, "settings", None)
    if not getattr(current_settings, "debug", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/metrics", dependencies=[Depends(_metrics_allowed)])
async def get_metrics() -> dict:
    """Return a minimal snapshot of counters/timers to aid tests and local diagnostics."""
    mc = get_metrics_collector()
    # Provide shallow views to avoid heavy serialization
    return {
        "counters": dict(mc.counters),
        "gauges": dict(mc.gauges),
        "timers": {k: (sum(v) / len(v) if v else 0.0) for k, v in mc.timers.items()},
    }

