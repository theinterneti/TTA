"""
Agent Orchestration Component

Provides a lightweight entrypoint component that will host workflow management,
message coordination, and agent proxy registration in subsequent tasks.
"""
from __future__ import annotations

import logging
from typing import Any

from src.orchestration.component import Component
from src.orchestration.decorators import log_entry_exit, timing_decorator

# For now we only rely on configuration and the base component lifecycle.

logger = logging.getLogger(__name__)


class AgentOrchestrationComponent(Component):
    """
    Component that initializes the Agent Orchestration Service.

    Dependencies are kept minimal for Task 1. Downstream tasks will introduce
    Redis, Neo4j, and LLM dependencies as concrete backends are implemented.
    """

    def __init__(self, config: Any):
        super().__init__(config, name="agent_orchestration", dependencies=["redis"])  # expect redis availability
        self.port = self.config.get("agent_orchestration.port", 8503)
        logger.info(f"Initialized Agent Orchestration component on port {self.port}")
        self._redis_client = None
        self._message_coordinator = None

    @log_entry_exit
    @timing_decorator
    def _start_impl(self) -> bool:
        """Start the orchestration service and perform message auto-recovery."""
        try:
            # Initialize Redis client (async) and coordinator lazily when needed
            import redis.asyncio as aioredis
            redis_url = self.config.get("player_experience.api.redis_url", "redis://localhost:6379/0")
            self._redis_client = aioredis.from_url(redis_url)

            # Defer import to avoid circulars
            from src.agent_orchestration.coordinators import RedisMessageCoordinator
            self._message_coordinator = RedisMessageCoordinator(self._redis_client, key_prefix="ao")

            # Auto-recovery: reclaim expired reservations across agents and log per-agent counts (inside coordinator)
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._message_coordinator.recover_pending(None))
                logger.info("Auto-recovery scheduled asynchronously")
            else:
                recovered = loop.run_until_complete(self._message_coordinator.recover_pending(None))
                logger.info("Auto-recovery reclaimed %s messages in total", recovered)

            # Start background polling task for queue lengths and DLQ gauges
            self._metrics_task = loop.create_task(self._poll_queue_metrics())

            # Start diagnostics HTTP endpoint if enabled
            if bool(self.config.get("agent_orchestration.diagnostics.enabled", False)):
                self._start_diagnostics_server(loop)
            else:
                logger.info("Diagnostics server disabled via config (agent_orchestration.diagnostics.enabled=false)")

            logger.info("Agent Orchestration component started; auto-recovery executed")
            return True
        except Exception as e:
            logger.error(f"Agent Orchestration startup failed: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """Stop the orchestration service."""
        try:
            import asyncio
            # Cancel metrics task if running
            mt = getattr(self, "_metrics_task", None)
            if mt:
                try:
                    mt.cancel()
                except Exception:
                    pass
            # Stop diagnostics server if started
            server = getattr(self, "_diag_server", None)
            if server:
                try:
                    server.should_exit = True  # type: ignore[attr-defined]
                except Exception:
                    pass
            # Close Redis client
            if self._redis_client:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self._redis_client.aclose())
        except Exception:
            pass
        logger.info("Agent Orchestration component stopped")
        return True

    async def _poll_queue_metrics(self) -> None:
        """Run periodic polling loop (5s) to update gauges and perform threshold checks."""
        import asyncio
        try:
            while True:
                await asyncio.sleep(5)
                await self._poll_queue_metrics_once()
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.warning(f"Queue metrics polling encountered an error: {e}")

    async def _poll_queue_metrics_once(self) -> None:
        """Single-cycle polling to update metrics and run threshold checks."""
        from src.agent_orchestration.models import AgentType
        coord = self._message_coordinator
        if not coord:
            return
        # Thresholds (basic foundation)
        dlq_warn_threshold = int(self.config.get("agent_orchestration.metrics.dlq_warn_threshold", 10))
        retry_spike_warn_threshold = int(self.config.get("agent_orchestration.metrics.retry_spike_warn_threshold", 20))
        prev_snapshot = getattr(self, "_prev_metrics_snapshot", None)

        # Scan instances and update gauges
        for at in (AgentType.IPA, AgentType.WBA, AgentType.NGA):
            # 1) Queue audit lists pattern
            async for key in self._redis_client.scan_iter(match=f"ao:queue:{at.value}:*"):
                k = key.decode() if isinstance(key, (bytes, bytearray)) else key
                inst = k.split(":")[-1]
                agent_key = f"{at.name.lower()}:{inst}"
                # Audit list overall length (priority 0)
                try:
                    qlen = await self._redis_client.llen(k)
                    coord.metrics.set_queue_length(agent_key, priority=0, length=int(qlen or 0))
                except Exception:
                    pass
                # DLQ gauge
                dlq_key = f"ao:dlq:{at.value}:{inst}"
                try:
                    dlq_len = await self._redis_client.llen(dlq_key)
                    coord.metrics.set_dlq_length(agent_key, int(dlq_len or 0))
                    if dlq_len and dlq_len >= dlq_warn_threshold:
                        logger.warning("DLQ length threshold exceeded for %s: %s >= %s", agent_key, dlq_len, dlq_warn_threshold)
                except Exception:
                    pass

            # 2) Per-priority ready queue sizes (zsets) — independent scan in case audit list absent
            async for skey_b in self._redis_client.scan_iter(match=f"ao:sched:{at.value}:*:prio:*"):
                skey = skey_b.decode() if isinstance(skey_b, (bytes, bytearray)) else skey_b
                # skey format: ao:sched:{type}:{inst}:prio:{prio}
                parts = skey.split(":")
                if len(parts) >= 6:
                    inst = parts[3]
                    try:
                        prio = int(parts[5])
                    except Exception:
                        continue
                    agent_key = f"{at.name.lower()}:{inst}"
                    try:
                        plen = await self._redis_client.zcard(skey)
                        coord.metrics.set_queue_length(agent_key, priority=prio, length=int(plen or 0))
                    except Exception:
                        pass

        # Retry spike detection based on total retries scheduled delta
        snap = coord.metrics.snapshot()
        if prev_snapshot is not None:
            prev_retries = prev_snapshot.get("retry", {}).get("total_retries_scheduled", 0)
            cur_retries = snap.get("retry", {}).get("total_retries_scheduled", 0)
            if (cur_retries - prev_retries) >= retry_spike_warn_threshold:
                logger.warning(
                    "Retry spike detected: +%s >= %s in last interval",
                    (cur_retries - prev_retries), retry_spike_warn_threshold,
                )
        self._prev_metrics_snapshot = snap

    def _create_diagnostics_app(self):
        """Create a simple FastAPI app for diagnostics and metrics."""
        try:
            from fastapi import FastAPI
        except Exception:
            return None
        app = FastAPI(title="Agent Orchestration Diagnostics", version="0.1.0")

        @app.get("/health")
        async def health() -> dict:
            ready = self._message_coordinator is not None
            return {"status": "healthy" if ready else "initializing", "component": "agent_orchestration"}

        @app.get("/metrics")
        async def metrics() -> dict:
            coord = self._message_coordinator
            if not coord:
                return {"error": "coordinator not initialized"}
            return coord.metrics.snapshot()

        @app.get("/metrics-prom")
        async def metrics_prometheus() -> str:
            """Export Prometheus metrics."""
            coord = self._message_coordinator
            if not coord:
                return "# coordinator not initialized\n"
            try:
                from prometheus_client import CollectorRegistry, Counter, Gauge, Summary, generate_latest
            except Exception:
                return "# prometheus_client not available\n"
            # Create a registry and map our metrics
            reg = CollectorRegistry()
            # Counters
            c_ok = Counter("agent_orchestration_messages_delivered_total", "Total successful deliveries", registry=reg)
            c_err = Counter("agent_orchestration_messages_delivery_errors_total", "Total delivery errors", registry=reg)
            c_retry = Counter("agent_orchestration_message_retries_total", "Total retries scheduled", registry=reg)
            c_perm = Counter("agent_orchestration_message_permanent_failures_total", "Total permanent failures", registry=reg)
            # Gauges
            g_queue = Gauge("agent_orchestration_queue_length", "Queue length", ["agent", "priority"], registry=reg)
            g_dlq = Gauge("agent_orchestration_dlq_length", "DLQ length", ["agent"], registry=reg)
            # Summary for backoff delays
            s_backoff = Summary("agent_orchestration_backoff_seconds", "Backoff delay seconds", registry=reg)

            snap = coord.metrics.snapshot()
            # Set counters (note: prometheus_client counters can only inc; we inc to target absolute on first pass)
            # To avoid ever-decreasing, we store last exported snapshot delta on the component
            last = getattr(self, "_prom_last", None) or {"delivery": {"delivered_ok": 0, "delivered_error": 0}, "retry": {"total_retries_scheduled": 0, "total_permanent_failures": 0}}
            inc_ok = max(0, snap["delivery"]["delivered_ok"] - last["delivery"]["delivered_ok"])
            inc_err = max(0, snap["delivery"]["delivered_error"] - last["delivery"]["delivered_error"])
            inc_retry = max(0, snap["retry"]["total_retries_scheduled"] - last["retry"]["total_retries_scheduled"])
            inc_perm = max(0, snap["retry"]["total_permanent_failures"] - last["retry"]["total_permanent_failures"])
            # Increment counters by deltas
            if inc_ok: c_ok.inc(inc_ok)
            if inc_err: c_err.inc(inc_err)
            if inc_retry: c_retry.inc(inc_retry)
            if inc_perm: c_perm.inc(inc_perm)
            self._prom_last = {
                "delivery": {"delivered_ok": snap["delivery"]["delivered_ok"], "delivered_error": snap["delivery"]["delivered_error"]},
                "retry": {"total_retries_scheduled": snap["retry"]["total_retries_scheduled"], "total_permanent_failures": snap["retry"]["total_permanent_failures"]},
            }
            # Gauges: set absolute values
            for k, v in snap.get("gauges", {}).get("queue_lengths", {}).items():
                agent, prio = k.split("|")
                g_queue.labels(agent=agent, priority=prio).set(v)
            for agent, v in snap.get("gauges", {}).get("dlq_lengths", {}).items():
                g_dlq.labels(agent=agent).set(v)
            # Summary: observe last backoff
            try:
                s_backoff.observe(float(snap["retry"]["last_backoff_seconds"]))
            except Exception:
                pass

            return generate_latest(reg).decode()

        return app

    def _start_diagnostics_server(self, loop) -> None:
        """Try to start a lightweight diagnostics server on self.port."""
        try:
            import uvicorn
        except Exception:
            logger.info("uvicorn not available; skipping diagnostics HTTP server startup")
            return
        app = self._create_diagnostics_app()
        if not app:
            logger.info("FastAPI unavailable; skipping diagnostics server")
            return
        config = uvicorn.Config(app, host="127.0.0.1", port=int(self.port), log_level="info")
        server = uvicorn.Server(config)
        self._diag_server = server
        import threading
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
