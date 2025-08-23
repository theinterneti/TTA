"""
Agent Orchestration Component

Provides a lightweight entrypoint component that will host workflow management,
message coordination, and agent proxy registration in subsequent tasks.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from src.orchestration.component import Component
from src.orchestration.decorators import log_entry_exit, timing_decorator


# Utility to parse memory-size strings like "4GB" into bytes
_DEF_UNITS = {
    "kb": 1024,
    "mb": 1024**2,
    "gb": 1024**3,
    "tb": 1024**4,
}

def _parse_bytes(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            return int(v)
        s = str(v).strip().lower()
        for suf, mul in _DEF_UNITS.items():
            if s.endswith(suf):
                num = float(s.replace(suf, "").strip())
                return int(num * mul)
        return int(float(s))
    except Exception:
        return None

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
        self._resource_manager = None
        self._agent_registry = None  # optional registry for discovery/health

        self._callable_registry = None

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

            # Initialize agent registry and start health checks if configured
            try:
                from src.agent_orchestration.agents import AgentRegistry
                self._agent_registry = AgentRegistry()
                health_iv = float(self.config.get("agent_orchestration.monitoring.health_check_interval", 15))
                self._agent_registry.start_periodic_health_checks(health_iv)
            except Exception:
                self._agent_registry = None

            # Initialize ResourceManager and start background monitoring
            from src.agent_orchestration.resources import ResourceManager
            rm = ResourceManager(
                gpu_memory_limit_fraction=float(self.config.get("agent_orchestration.resources.gpu_memory_limit", 0.8)),
                cpu_thread_limit=self.config.get("agent_orchestration.resources.cpu_thread_limit", None),
                memory_limit_bytes=_parse_bytes(self.config.get("agent_orchestration.resources.memory_limit", None)),
                warn_cpu_percent=float(self.config.get("agent_orchestration.monitoring.cpu_warn", 85)),
                warn_mem_percent=float(self.config.get("agent_orchestration.monitoring.mem_warn", 85)),
                crit_cpu_percent=float(self.config.get("agent_orchestration.monitoring.cpu_crit", 95)),
                crit_mem_percent=float(self.config.get("agent_orchestration.monitoring.mem_crit", 95)),
                redis_client=self._redis_client,
                redis_prefix="ao",
            )
            self._resource_manager = rm
            try:
                rm.start_background_monitoring(int(self.config.get("agent_orchestration.monitoring.metrics_interval", 30)))
            except Exception:
                pass

            # Initialize agent registry and start health checks if configured
            try:
                from src.agent_orchestration.registries import RedisAgentRegistry
                from src.agent_orchestration.agents import AgentRegistry
                ttl = float(self.config.get("agent_orchestration.agents.heartbeat_ttl", 30.0))
                hb = self.config.get("agent_orchestration.agents.heartbeat_interval", None)
                hb = float(hb) if hb is not None else None
                self._agent_registry = RedisAgentRegistry(self._redis_client, key_prefix="ao", heartbeat_ttl_s=ttl, heartbeat_interval_s=hb)
                health_iv = float(self.config.get("agent_orchestration.monitoring.health_check_interval", 15))
                self._agent_registry.start_periodic_health_checks(health_iv)
                self._agent_registry.start_heartbeats()
            except Exception:
                # Fallback to in-memory registry if Redis registry fails
                try:
                    from src.agent_orchestration.agents import AgentRegistry
                    self._agent_registry = AgentRegistry()
                    health_iv = float(self.config.get("agent_orchestration.monitoring.health_check_interval", 15))
                    self._agent_registry.start_periodic_health_checks(health_iv)
                except Exception:
                    self._agent_registry = None

            # Auto-register built-in proxies if enabled
            try:
                if bool(self.config.get("agent_orchestration.agents.auto_register", False)):
                    from src.agent_orchestration.proxies import (
                        InputProcessorAgentProxy, WorldBuilderAgentProxy, NarrativeGeneratorAgentProxy,
                    )
                    import socket, os, uuid

                    def _inst(name_key: str) -> str:
                        explicit = self.config.get(name_key)
                        if explicit:
                            return str(explicit)
                        host = socket.gethostname()
                        pid = os.getpid()
                        sid = uuid.uuid4().hex[:6]
                        return f"{host}-{pid}-{sid}"

                    # Per-agent enable flags (default false)
                    if bool(self.config.get("agent_orchestration.agents.ipa.enabled", False)):
                        ipa = InputProcessorAgentProxy(coordinator=self._message_coordinator, instance=_inst("agent_orchestration.agents.ipa.instance"))
                        if loop.is_running():
                            loop.create_task(ipa.start()); self._agent_registry.register(ipa)
                        else:
                            loop.run_until_complete(ipa.start()); self._agent_registry.register(ipa)
                    if bool(self.config.get("agent_orchestration.agents.wba.enabled", False)):
                        wba = WorldBuilderAgentProxy(coordinator=self._message_coordinator, instance=_inst("agent_orchestration.agents.wba.instance"))
                        if loop.is_running():
                            loop.create_task(wba.start()); self._agent_registry.register(wba)
                        else:
                            loop.run_until_complete(wba.start()); self._agent_registry.register(wba)
                    if bool(self.config.get("agent_orchestration.agents.nga.enabled", False)):
                        nga = NarrativeGeneratorAgentProxy(coordinator=self._message_coordinator, instance=_inst("agent_orchestration.agents.nga.instance"))
                        if loop.is_running():
                            loop.create_task(nga.start()); self._agent_registry.register(nga)
                        else:
                            loop.run_until_complete(nga.start()); self._agent_registry.register(nga)
            except Exception as e:
                logger.warning("Auto-registration of agents failed: %s", e)

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
            # Stop resource monitoring
            try:
                if getattr(self, "_resource_manager", None):
                    self._resource_manager.stop_background_monitoring()
            except Exception:
                pass
            # Deregister locally registered agents and stop health/heartbeats
            try:
                reg = getattr(self, "_agent_registry", None)
                if reg:
                    # Attempt to deregister each known local agent
                    try:
                        from src.agent_orchestration.agents import Agent
                        for agent in list(reg.all()):
                            try:
                                reg.deregister(agent.agent_id)
                            except Exception:
                                pass
                    except Exception:
                        pass
                    # Stop health checks and heartbeats (Redis)
                    try:
                        reg.stop_periodic_health_checks()
                    except Exception:
                        pass
                    try:
                        from src.agent_orchestration.registries import RedisAgentRegistry  # type: ignore
                        if isinstance(reg, RedisAgentRegistry):  # type: ignore
                            reg.stop_heartbeats()
                    except Exception:
                        pass
            except Exception:
                pass
            # Close Redis client
            if self._redis_client:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Schedule close and wait briefly
                        fut = asyncio.run_coroutine_threadsafe(self._redis_client.aclose(), loop)
                        try:
                            fut.result(timeout=1.0)
                        except Exception:
                            pass
                    else:
                        loop.run_until_complete(self._redis_client.aclose())
                except Exception:
                    pass
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

        # Initialize tools configuration; lazily create Redis clients per-request to avoid cross-loop issues
        try:
            self._tools_cfg = self.config.get("agent_orchestration.tools", {}) or {}
            # Provide a registry for programmatic use (same loop as caller)
            import redis.asyncio as aioredis
            redis_url = self.config.get("player_experience.api.redis_url", "redis://localhost:6379/0")
            rclient = aioredis.from_url(redis_url)
            from src.agent_orchestration.tools.redis_tool_registry import RedisToolRegistry
            from src.agent_orchestration.tools.coordinator import ToolCoordinator
            from src.agent_orchestration.tools.models import ToolPolicy
            self._tool_registry = RedisToolRegistry(
                rclient,
                key_prefix=str(self._tools_cfg.get("redis_key_prefix", "ao")),
                cache_ttl_s=float(self._tools_cfg.get("cache_ttl_s", 300.0)),
                cache_max_items=int(self._tools_cfg.get("cache_max_items", 512)),
            )
            self._tool_policy = ToolPolicy(
                allow_network_tools=bool(self._tools_cfg.get("allow_network_tools", False)),
                allow_filesystem_tools=bool(self._tools_cfg.get("allow_filesystem_tools", False)),
                allow_process_tools=bool(self._tools_cfg.get("allow_process_tools", False)),
                allow_subprocess_tools=bool(self._tools_cfg.get("allow_subprocess_tools", False)),
                allow_shell_exec=bool(self._tools_cfg.get("allow_shell_exec", False)),
                allowed_callables=list(self._tools_cfg.get("allowed_callables", [])),
                max_schema_depth=int(self._tools_cfg.get("max_schema_depth", 5)),
            )
            self._tool_coordinator = ToolCoordinator(self._tool_registry, self._tool_policy)
        except Exception:
            self._tool_registry = None
            self._tool_coordinator = None
            self._tool_policy = None

        def _make_request_local_registry():
            try:
                import redis.asyncio as aioredis
                redis_url = self.config.get("player_experience.api.redis_url", "redis://localhost:6379/0")
                rclient = aioredis.from_url(redis_url)
                from src.agent_orchestration.tools.redis_tool_registry import RedisToolRegistry
                return RedisToolRegistry(
                    rclient,
                    key_prefix=str(self._tools_cfg.get("redis_key_prefix", "ao")),
                    cache_ttl_s=float(self._tools_cfg.get("cache_ttl_s", 300.0)),
                    cache_max_items=int(self._tools_cfg.get("cache_max_items", 512)),
                )
            except Exception:
                return None
        # Create a shared invocation service for app usage
        try:
            from src.agent_orchestration.tools.callable_registry import CallableRegistry
            from src.agent_orchestration.tools.invocation_service import ToolInvocationService
            _call_registry = CallableRegistry()
            self._callable_registry = _call_registry
            def default_resolver(spec):
                return _call_registry.resolve_callable(spec)
            self._tool_invocation = ToolInvocationService(
                registry=self._tool_registry,
                coordinator=self._tool_coordinator,
                policy=self._tool_policy,
                callable_resolver=default_resolver,
            )
        except Exception:
            self._tool_invocation = None


        @app.get("/health")
        async def health() -> dict:
            ready = self._message_coordinator is not None
            return {"status": "healthy" if ready else "initializing", "component": "agent_orchestration"}

        @app.get("/metrics")
        async def metrics() -> dict:
            coord = self._message_coordinator
            if not coord:
                return {"error": "coordinator not initialized"}
            snap = coord.metrics.snapshot()
            data = {"messages": snap}
            # Back-compat: expose top-level delivery/retry/gauges keys for simple checks
            try:
                data.update({
                    "delivery": snap.get("delivery", {}),
                    "retry": snap.get("retry", {}),
                    "gauges": snap.get("gauges", {}),
                })
            except Exception:
                pass
            # Aggregate performance metrics (per-agent step stats)
            try:
                from src.agent_orchestration.performance import get_step_aggregator
                perf_snap = get_step_aggregator().snapshot()
                data["performance"] = perf_snap
            except Exception:
                pass
            # Tools summary and metrics
            try:
                reg = _make_request_local_registry() or getattr(self, "_tool_registry", None)
                if reg:
                    tool_ids = await reg.list_tool_ids()
                    cache_stats = await reg.cache_stats()
                    # summarize status counts
                    active = 0; deprecated = 0
                    for tid in tool_ids:
                        nm, ver = tid.split(":", 1)
                        st = await reg.get_status(nm, ver)
                        if st == "active": active += 1
                        else: deprecated += 1
                    data["tools"] = {
                        "total": len(tool_ids),
                        "active": active,
                        "deprecated": deprecated,
                        "cache": cache_stats,
                    }
                    # attach per-tool execution stats
                    try:
                        from src.agent_orchestration.tools.metrics import get_tool_metrics
                        data["tool_exec"] = get_tool_metrics().snapshot()
                    except Exception:
                        pass
            except Exception:
                pass
            # Resource usage snapshot
            try:
                if getattr(self, "_resource_manager", None):
                    rep = await self._resource_manager.monitor_usage()
                    data["resources"] = {
                        "timestamp": rep.timestamp,
                        "usage": rep.usage.__dict__,
                        "thresholds": rep.thresholds_exceeded,
                    }
            except Exception:
                pass
            # Agent registry snapshot if available (sync)
            try:
                from src.agent_orchestration.agents import AgentRegistry  # type: ignore
                reg = getattr(self, "_agent_registry", None)
                if reg and isinstance(reg, AgentRegistry):  # type: ignore
                    data["agents"] = reg.snapshot()
            except Exception:
                pass
            return data

        @app.get("/agents")
        async def agents() -> dict:
            """Agent registry snapshot with derived performance and heartbeat age.
            Returns merged local and Redis-discovered agents when RedisAgentRegistry is used.
            """
            reg = getattr(self, "_agent_registry", None)
            if not reg:
                return {"error": "agent registry not initialized"}
            # Gather base snapshot
            local_snap = reg.snapshot()
            redis_index: list = []
            try:
                from src.agent_orchestration.registries import RedisAgentRegistry  # type: ignore
                if isinstance(reg, RedisAgentRegistry):  # type: ignore
                    redis_index = await reg.list_registered()
            except Exception:
                pass
            # Derived perf metrics from aggregator keyed by type:instance
            perf = {}
            try:
                from src.agent_orchestration.performance import get_step_aggregator
                perf = get_step_aggregator().snapshot()  # { "ipa:worker-1": {p50,p95,avg,error_rate}, ... }
            except Exception:
                pass
            # Attach perf metrics to local agents
            for name, data in local_snap.items():
                try:
                    agent_key = f"{data['agent_id']['type']}:{data['agent_id'].get('instance') or 'default'}"
                except Exception:
                    agent_key = name
                if agent_key in perf:
                    data.setdefault("performance", {}).update(perf[agent_key])
            # Add last_heartbeat_age to redis_index entries
            now = time.time()
            for entry in redis_index:
                try:
                    hb = float(entry.get("last_heartbeat", 0.0))
                    entry["last_heartbeat_age"] = max(0.0, now - hb)
                    # merge perf if available
                    try:
                        aid = entry.get("agent_id", {})
                        ak = f"{aid.get('type')}:{aid.get('instance') or 'default'}"
                        if ak in perf:
                            entry.setdefault("performance", {}).update(perf[ak])
                    except Exception:
                        pass
                except Exception:
                    entry["last_heartbeat_age"] = None
            return {"local": local_snap, "redis_index": redis_index}


        @app.get("/metrics-prom")
        async def metrics_prometheus() -> str:
            """Export Prometheus metrics."""
            coord = self._message_coordinator
            if not coord:
                return "# coordinator not initialized\n"
            try:
                from prometheus_client import CollectorRegistry, Counter, Gauge, Summary, Histogram, generate_latest
            except Exception:
                return "# prometheus_client not available\n"
            # Create a registry and map our metrics
            prom_reg = CollectorRegistry()
            # Counters
            c_ok = Counter("agent_orchestration_messages_delivered_total", "Total successful deliveries", registry=prom_reg)
            c_err = Counter("agent_orchestration_messages_delivery_errors_total", "Total delivery errors", registry=prom_reg)
            c_retry = Counter("agent_orchestration_message_retries_total", "Total retries scheduled", registry=prom_reg)
            c_perm = Counter("agent_orchestration_message_permanent_failures_total", "Total permanent failures", registry=prom_reg)
            # Gauges
            g_queue = Gauge("agent_orchestration_queue_length", "Queue length", ["agent", "priority"], registry=prom_reg)
            g_dlq = Gauge("agent_orchestration_dlq_length", "DLQ length", ["agent"], registry=prom_reg)
            # Summary for backoff delays
            s_backoff = Summary("agent_orchestration_backoff_seconds", "Backoff delay seconds", registry=prom_reg)
            # Performance metrics: histogram for durations, gauge for error rate
            h_step_duration = Histogram(
                "agent_orchestration_step_duration_ms",
                "Workflow step duration in ms",
                ["agent"],
                registry=prom_reg,
                buckets=(5, 10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400),
            )
            g_step_error_rate = Gauge(
                "agent_orchestration_step_error_rate",
                "Workflow step error rate (0..1)",
                ["agent"],
                registry=prom_reg,
            )

            # Message metrics
            snap = coord.metrics.snapshot()

            # Tool metrics
            tool_exec = {}
            tool_cache = {"hits": 0, "misses": 0}
            try:
                from src.agent_orchestration.tools.metrics import get_tool_metrics
                tool_exec = get_tool_metrics().snapshot()
            except Exception:
                pass
            try:
                reg = _make_request_local_registry() or getattr(self, "_tool_registry", None)
                if reg:
                    tool_cache = await reg.cache_stats()
            except Exception:
                pass
            # Set counters (note: prometheus_client counters can only inc; we inc to target absolute on first pass)
            last = getattr(self, "_prom_last", None) or {"delivery": {"delivered_ok": 0, "delivered_error": 0}, "retry": {"total_retries_scheduled": 0, "total_permanent_failures": 0}}
            inc_ok = max(0, snap["delivery"]["delivered_ok"] - last["delivery"]["delivered_ok"])
            inc_err = max(0, snap["delivery"]["delivered_error"] - last["delivery"]["delivered_error"])
            inc_retry = max(0, snap["retry"]["total_retries_scheduled"] - last["retry"]["total_retries_scheduled"])
            inc_perm = max(0, snap["retry"]["total_permanent_failures"] - last["retry"]["total_permanent_failures"])
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

            # Performance metrics from aggregator
            try:
                from src.agent_orchestration.performance import get_step_aggregator
                perf = get_step_aggregator().snapshot()
                for agent, stats in perf.items():
                    # Observe p95 (approx) and p50 (approx) into histogram; prometheus client will bucket
                    # Also set error rate gauge per agent
                    g_step_error_rate.labels(agent=agent).set(float(stats.get("error_rate", 0.0)))
                    # Observing avg is ok to represent load
                    h_step_duration.labels(agent=agent).observe(float(stats.get("avg", 0.0)))
                    h_step_duration.labels(agent=agent).observe(float(stats.get("p50", 0.0)))
                    h_step_duration.labels(agent=agent).observe(float(stats.get("p95", 0.0)))
            except Exception:
                pass

            # Export tool metrics as well (per-tool labels)
            try:
                from prometheus_client import Counter, Histogram
                tool_inv = Counter("agent_orchestration_tool_invocations_total", "Tool invocations", ["tool", "version"], registry=prom_reg)
                tool_ok = Counter("agent_orchestration_tool_success_total", "Tool successes", ["tool", "version"], registry=prom_reg)
                tool_err = Counter("agent_orchestration_tool_failure_total", "Tool failures", ["tool", "version"], registry=prom_reg)
                tool_dur = Histogram(
                    "agent_orchestration_tool_duration_seconds",
                    "Tool execution duration in seconds",
                    ["tool", "version"],
                    registry=prom_reg,
                    buckets=(0.01, 0.05, 0.2, 1.0, 5.0),
                )
                # Limit cardinality if configured
                max_tools = int(self._tools_cfg.get("max_prometheus_tools", 200)) if hasattr(self, "_tools_cfg") else 200
                count = 0
                for key, stats in tool_exec.items():
                    if count >= max_tools: break
                    name, version = key.split(":", 1)
                    ok = int(stats.get("successes", 0)); err = int(stats.get("failures", 0))
                    total = ok + err
                    # increment counters
                    if total: tool_inv.labels(name, version).inc(total)
                    if ok: tool_ok.labels(name, version).inc(ok)
                    if err: tool_err.labels(name, version).inc(err)
                    # approximate duration via buckets distribution
                    buckets = stats.get("buckets", {})
                    midpoint = {"<10": 0.005, "10-50": 0.03, "50-200": 0.125, "200-1000": 0.6, ">=1000": 1.5}
                    for b, c in buckets.items():
                        for _ in range(int(c)):
                            tool_dur.labels(name, version).observe(midpoint.get(b, 0.1))
                    count += 1
            except Exception:
                pass

            return generate_latest(prom_reg).decode()

        @app.get("/tools")
        async def tools_endpoint() -> dict:
            reg = _make_request_local_registry() or getattr(self, "_tool_registry", None)
            if not reg:
                return {"error": "tool registry not initialized"}
            tool_ids = await reg.list_tool_ids()
            items = []
            for tid in tool_ids:
                nm, ver = tid.split(":", 1)
                st = await reg.get_status(nm, ver)
                spec = await reg.get_tool(nm, ver)
                items.append({
                    "name": nm,
                    "version": ver,
                    "status": st,
                    "last_used_at": getattr(spec, "last_used_at", 0.0) if spec else None,
                })
            cache_stats = await reg.cache_stats()
            usage = {}
            try:
                from src.agent_orchestration.tools.metrics import get_tool_metrics
                usage = get_tool_metrics().snapshot()
            except Exception:
                pass
            return {"tools": items, "cache": cache_stats, "usage": usage}

        @app.get("/tools/summary")
        async def tools_summary(page: int = 1, limit: int = 50, status: str | None = None,
                                name_prefix: str | None = None, sort_by: str = "last_used_at",
                                order: str = "desc") -> dict:
            reg = _make_request_local_registry() or getattr(self, "_tool_registry", None)
            if not reg:
                return {"error": "tool registry not initialized"}
            # paging
            limit = max(1, min(500, int(limit)))
            page = max(1, int(page))
            tool_ids = await reg.list_tool_ids()
            tools = []
            for tid in tool_ids:
                nm, ver = tid.split(":", 1)
                if name_prefix and not nm.startswith(name_prefix):
                    continue
                st = await reg.get_status(nm, ver)
                if status and st != status:
                    continue
                spec = await reg.get_tool(nm, ver)
                tools.append({
                    "name": nm,
                    "version": ver,
                    "status": st,
                    "last_used_at": getattr(spec, "last_used_at", 0.0) if spec else 0.0,
                })
            reverse = (order.lower() != "asc")
            if sort_by in ("last_used_at", "name", "version", "status"):
                tools.sort(key=lambda x: x.get(sort_by) or 0, reverse=reverse)
            total = len(tools)
            start = (page - 1) * limit
            end = start + limit
            items = tools[start:end]
            # summary stats
            active = sum(1 for t in tools if t["status"] == "active")
            deprecated = total - active
            usage = {}
            try:
                from src.agent_orchestration.tools.metrics import get_tool_metrics
                usage = get_tool_metrics().snapshot()
            except Exception:
                pass
            # naive most/least used by successes+failures in usage
            def usage_count(t):
                k = f"{t['name']}:{t['version']}"
                st = usage.get(k, {})
                return int(st.get("successes", 0)) + int(st.get("failures", 0))
            most_used = sorted(tools, key=usage_count, reverse=True)[:5]
            least_used = sorted(tools, key=usage_count)[:5]
            return {
                "page": page,
                "limit": limit,
                "total": total,
                "counts": {"active": active, "deprecated": deprecated},
                "items": items,
                "most_used": most_used,
                "least_used": least_used,
            }

        # Tool execution endpoint (diagnostics only, gated by config)
        from fastapi import Header
        @app.post("/tools/execute")
        async def tools_execute(payload: dict, x_ao_diag_key: str | None = Header(default=None, alias="X-AO-DIAG-KEY")) -> dict:
            if not bool(self.config.get("agent_orchestration.diagnostics.allow_tool_execution", False)):
                return {"error": "tool execution disabled"}
            # Authentication: optional API key
            try:
                api_key = self.config.get("agent_orchestration.diagnostics.tool_exec_api_key")
                if api_key and (x_ao_diag_key != api_key):
                    try:
                        logger.warning("/tools/execute unauthorized attempt")
                    except Exception:
                        pass
                    from fastapi.responses import JSONResponse  # type: ignore
                    return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
            except Exception:
                # Fail-closed: if auth check errors, deny access
                from fastapi.responses import JSONResponse  # type: ignore
                return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
            return await _execute_tools_request(payload)

        async def _execute_tools_request(payload: dict) -> dict:
            # Basic per-process soft rate limit
            import time as _t
            now = _t.time()
            window = 60.0
            max_calls = int(self.config.get("agent_orchestration.diagnostics.max_tool_exec_per_min", 30))
            hist = getattr(self, "_exec_hist", [])
            hist = [t for t in hist if now - t < window]
            if len(hist) >= max_calls:
                return {"error": "rate_limited"}
            hist.append(now); self._exec_hist = hist
            # Validate payload
            try:
                name = str(payload.get("tool_name"))
                version = payload.get("version")
                args = payload.get("arguments") or {}
                if not name:
                    return {"error": "tool_name required"}
            except Exception:
                return {"error": "invalid payload"}
            # Resolve and invoke with timeout using request-local Redis client to avoid cross-loop issues
            import asyncio as _asyncio
            try:
                timeout_s = float(self.config.get("agent_orchestration.diagnostics.tool_exec_timeout_s", 10.0))
                started = _t.time()
                # Build per-request registry/coordinator and service
                reg = _make_request_local_registry() or getattr(self, "_tool_registry", None)
                if reg is None:
                    return {"error": "tool registry not initialized"}
                # Validate against allowed tools patterns, if configured
                allowed = self.config.get("agent_orchestration.diagnostics.allowed_tools") or []
                if allowed:
                    from fnmatch import fnmatch
                    full = f"{name}:{version or '*'}"
                    ok = any(fnmatch(full, patt) or fnmatch(f"{name}:*", patt) for patt in allowed)
                    if not ok:
                        return {"ok": False, "error": "tool not allowed"}
                from src.agent_orchestration.tools.coordinator import ToolCoordinator
                from src.agent_orchestration.tools.invocation_service import ToolInvocationService
                coord = ToolCoordinator(registry=reg, policy=self._tool_policy)
                def _resolver(spec):
                    return self._callable_registry.resolve_callable(spec)
                svc = ToolInvocationService(registry=reg, coordinator=coord, policy=self._tool_policy, callable_resolver=_resolver)
                res = await _asyncio.wait_for(svc.invoke_tool(name, version, args), timeout=timeout_s)
                dur_ms = int((_t.time() - started) * 1000)
                from src.agent_orchestration.tools.metrics import get_tool_metrics
                usage = get_tool_metrics().snapshot().get(f"{name}:{version or 'latest'}", {})
                return {"ok": True, "result": res, "duration_ms": dur_ms, "metrics": usage}
            except _asyncio.TimeoutError:
                return {"ok": False, "error": "timeout"}
            except Exception as e:
                return {"ok": False, "error": str(e)}

            for tid in tool_ids:
                nm, ver = tid.split(":", 1)
                st = await reg.get_status(nm, ver)
                spec = await reg.get_tool(nm, ver)
                items.append({
                    "name": nm,
                    "version": ver,
                    "status": st,
                    "last_used_at": getattr(spec, "last_used_at", 0.0) if spec else None,
                })
            cache_stats = await reg.cache_stats()
            usage = {}
            try:
                from src.agent_orchestration.tools.metrics import get_tool_metrics
                usage = get_tool_metrics().snapshot()
            except Exception:
                pass
            return {"tools": items, "cache": cache_stats, "usage": usage}

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
