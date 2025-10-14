"""
Circuit breaker registry for managing multiple circuit breakers with centralized
state persistence and cleanup operations.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState

logger = logging.getLogger(__name__)


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers with centralized persistence.

    Provides circuit breaker lifecycle management, state synchronization,
    and cleanup operations for expired circuit breakers.

    Redis keys (prefix pfx=ao by default):
      - {pfx}:cb:registry -> set of active circuit breaker names
      - {pfx}:cb:state:{name} -> individual circuit breaker state
      - {pfx}:cb:metrics:{name} -> individual circuit breaker metrics
      - {pfx}:cb:cleanup:last -> timestamp of last cleanup operation
    """

    def __init__(self, redis, key_prefix: str = "ao") -> None:
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._cleanup_interval = 3600  # 1 hour
        self._cleanup_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    # ---- Redis key helpers ----
    def _registry_key(self) -> str:
        return f"{self._pfx}:cb:registry"

    def _cleanup_key(self) -> str:
        return f"{self._pfx}:cb:cleanup:last"

    def _state_pattern(self) -> str:
        return f"{self._pfx}:cb:state:*"

    def _metrics_pattern(self) -> str:
        return f"{self._pfx}:cb:metrics:*"

    # ---- Circuit breaker management ----
    async def get_or_create(
        self, name: str, config: CircuitBreakerConfig | None = None
    ) -> CircuitBreaker:
        """Get existing circuit breaker or create a new one."""
        async with self._lock:
            if name not in self._circuit_breakers:
                cb = CircuitBreaker(
                    redis=self._redis, name=name, config=config, key_prefix=self._pfx
                )
                await cb.initialize()
                self._circuit_breakers[name] = cb

                # Add to registry
                await self._redis.sadd(self._registry_key(), name)

                logger.debug(f"Created circuit breaker: {name}")

            return self._circuit_breakers[name]

    async def get(self, name: str) -> CircuitBreaker | None:
        """Get existing circuit breaker by name."""
        async with self._lock:
            return self._circuit_breakers.get(name)

    async def remove(self, name: str) -> bool:
        """Remove circuit breaker and clean up its state."""
        async with self._lock:
            if name in self._circuit_breakers:
                del self._circuit_breakers[name]

                # Remove from registry and clean up Redis keys
                await self._redis.srem(self._registry_key(), name)
                await self._redis.delete(f"{self._pfx}:cb:state:{name}")
                await self._redis.delete(f"{self._pfx}:cb:metrics:{name}")

                logger.info(f"Removed circuit breaker: {name}")
                return True
            return False

    async def list_names(self) -> list[str]:
        """List all registered circuit breaker names."""
        try:
            members = await self._redis.smembers(self._registry_key())
            return [
                m.decode() if isinstance(m, (bytes, bytearray)) else m for m in members
            ]
        except Exception as e:
            logger.warning(f"Failed to list circuit breaker names: {e}")
            return []

    async def get_all_metrics(self) -> dict[str, Any]:
        """Get metrics for all circuit breakers."""
        metrics = {}
        async with self._lock:
            for name, cb in self._circuit_breakers.items():
                try:
                    metrics[name] = await cb.get_metrics()
                except Exception as e:
                    logger.warning(
                        f"Failed to get metrics for circuit breaker {name}: {e}"
                    )
                    metrics[name] = {"error": str(e)}
        return metrics

    async def get_all_states(self) -> dict[str, CircuitBreakerState]:
        """Get states for all circuit breakers."""
        states = {}
        async with self._lock:
            for name, cb in self._circuit_breakers.items():
                try:
                    states[name] = await cb.get_state()
                except Exception as e:
                    logger.warning(
                        f"Failed to get state for circuit breaker {name}: {e}"
                    )
                    states[name] = CircuitBreakerState.CLOSED  # Default fallback
        return states

    # ---- Bulk operations ----
    async def reset_all(self) -> int:
        """Reset all circuit breakers to CLOSED state."""
        reset_count = 0
        async with self._lock:
            for name, cb in self._circuit_breakers.items():
                try:
                    await cb.reset()
                    reset_count += 1
                    logger.info(f"Reset circuit breaker: {name}")
                except Exception as e:
                    logger.warning(f"Failed to reset circuit breaker {name}: {e}")
        return reset_count

    async def get_open_circuit_breakers(self) -> list[str]:
        """Get names of all circuit breakers in OPEN state."""
        open_breakers = []
        states = await self.get_all_states()
        for name, state in states.items():
            if state == CircuitBreakerState.OPEN:
                open_breakers.append(name)
        return open_breakers

    # ---- Cleanup operations ----
    async def cleanup_expired_states(self) -> int:
        """Clean up expired circuit breaker states from Redis."""
        cleaned_count = 0
        try:
            # Get all registered names
            registered_names = set(await self.list_names())

            # Scan for state keys
            state_keys = []
            async for key in self._redis.scan_iter(match=self._state_pattern()):
                key_str = key.decode() if isinstance(key, (bytes, bytearray)) else key
                state_keys.append(key_str)

            # Check each state key
            for key in state_keys:
                # Extract name from key
                name = key.split(":")[-1]

                # If not in registry, check if expired
                if name not in registered_names:
                    try:
                        data = await self._redis.get(key)
                        if data:
                            state_data = json.loads(
                                data if isinstance(data, str) else data.decode()
                            )
                            updated_at = state_data.get("updated_at", 0)

                            # Clean up if older than 24 hours
                            if time.time() - updated_at > 86400:
                                await self._redis.delete(key)
                                await self._redis.delete(
                                    f"{self._pfx}:cb:metrics:{name}"
                                )
                                cleaned_count += 1
                                logger.debug(
                                    f"Cleaned up expired circuit breaker state: {name}"
                                )
                    except Exception as e:
                        logger.warning(f"Failed to process state key {key}: {e}")

            # Update cleanup timestamp
            await self._redis.set(self._cleanup_key(), int(time.time()))

        except Exception as e:
            logger.warning(f"Circuit breaker cleanup failed: {e}")

        return cleaned_count

    async def start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started circuit breaker cleanup task")

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task
            logger.info("Stopped circuit breaker cleanup task")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                cleaned = await self.cleanup_expired_states()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired circuit breaker states")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Circuit breaker cleanup loop error: {e}")

    # ---- Persistence helpers ----
    async def sync_registry_with_redis(self) -> None:
        """Synchronize in-memory registry with Redis state."""
        try:
            # Get all names from Redis registry
            redis_names = set(await self.list_names())

            # Get all names from memory
            memory_names = set(self._circuit_breakers.keys())

            # Remove from memory if not in Redis
            for name in memory_names - redis_names:
                if name in self._circuit_breakers:
                    del self._circuit_breakers[name]
                    logger.debug(f"Removed circuit breaker from memory: {name}")

            # Initialize circuit breakers that exist in Redis but not in memory
            for name in redis_names - memory_names:
                try:
                    cb = CircuitBreaker(
                        redis=self._redis, name=name, key_prefix=self._pfx
                    )
                    await cb.initialize()
                    self._circuit_breakers[name] = cb
                    logger.debug(f"Loaded circuit breaker from Redis: {name}")
                except Exception as e:
                    logger.warning(f"Failed to load circuit breaker {name}: {e}")

        except Exception as e:
            logger.warning(f"Failed to sync registry with Redis: {e}")

    async def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        try:
            states = await self.get_all_states()
            state_counts = {}
            for state in CircuitBreakerState:
                state_counts[state.value] = sum(
                    1 for s in states.values() if s == state
                )

            # Get last cleanup time
            last_cleanup = await self._redis.get(self._cleanup_key())
            last_cleanup_time = None
            if last_cleanup:
                with contextlib.suppress(ValueError, TypeError):
                    last_cleanup_time = int(last_cleanup)

            return {
                "total_circuit_breakers": len(self._circuit_breakers),
                "state_counts": state_counts,
                "last_cleanup_time": last_cleanup_time,
                "cleanup_task_running": self._cleanup_task is not None
                and not self._cleanup_task.done(),
            }
        except Exception as e:
            logger.warning(f"Failed to get registry stats: {e}")
            return {"error": str(e)}
