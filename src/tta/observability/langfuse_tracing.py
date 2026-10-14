"""TTA Langfuse tracing — lightweight wrapper for narrative generation observability.

Wire this into the narrative engine to produce traces in Langfuse project
cmonj12g70006guxy9z6qo25g (TTA).

Usage:
    from tta.observability.langfuse_tracing import trace_narrative

    @trace_narrative(model="deepseek-v4-pro")
    def generate_narrative(prompt: str, game_id: str, turn: int) -> str:
        ...
"""

from __future__ import annotations

import functools
import logging
import os
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

ENABLED = os.environ.get("LANGFUSE_ENABLED", "true").lower() == "true"

_langfuse_client: Any = None


def _get_client() -> Any | None:
    """Lazy-init the Langfuse client."""
    global _langfuse_client
    if not ENABLED:
        return None
    if _langfuse_client is not None:
        return _langfuse_client
    try:
        from langfuse import Langfuse

        _langfuse_client = Langfuse(
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
            base_url=os.environ.get("LANGFUSE_BASE_URL", "http://localhost:3001"),
            flush_at=1,
            flush_interval=1.0,
        )
        logger.info("Langfuse client initialized for TTA")
        return _langfuse_client
    except Exception as e:
        logger.warning(f"Langfuse client init failed (traces disabled): {e}")
        return None


def trace_narrative(
    *,
    model: str = "unknown",
    task_type: str = "narrative_generation",
):
    """Decorator to trace a narrative generation function.

    Creates a Langfuse trace with session_id=game_id. Tracks latency,
    token usage, and prompt/output for each generation call.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            client = _get_client()
            if client is None:
                return func(*args, **kwargs)

            game_id = kwargs.get("game_id") or (args[0] if args else "unknown")
            turn = kwargs.get("turn", 0)
            prompt = str(kwargs.get("prompt", ""))[:500]

            start = time.monotonic()
            trace = client.trace(
                name="narrative-turn",
                session_id=str(game_id),
                input={"prompt": prompt},
                metadata={
                    "turn": turn,
                    "task_type": task_type,
                    "environment": "production",
                },
            )

            try:
                result = func(*args, **kwargs)
                latency_ms = (time.monotonic() - start) * 1000

                output_text = str(result)[:500] if result else ""
                gen = trace.generation(
                    name="narrative-generation",
                    model=model,
                    input={"prompt": prompt},
                    output={"text": output_text},
                    metadata={
                        "latency_ms": round(latency_ms),
                        "output_length": len(str(result)) if result else 0,
                    },
                )
                gen.end()
                return result

            except Exception as e:
                gen = trace.generation(
                    name="narrative-generation",
                    model=model,
                    input={"prompt": prompt},
                    level="ERROR",
                    statusMessage=str(e)[:200],
                    metadata={"error": str(e)[:200]},
                )
                gen.end()
                raise
            finally:
                client.flush()

        return wrapper

    return decorator
