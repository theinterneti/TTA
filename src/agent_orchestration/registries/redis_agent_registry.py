from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

from redis.asyncio import Redis

from ..agents import Agent, AgentRegistry
from ..capability_matcher import CapabilityMatcher, MatchingStrategy
from ..models import (
    AgentCapability,
    AgentCapabilitySet,
    AgentId,
    CapabilityDiscoveryRequest,
    CapabilityDiscoveryResponse,
    CapabilityMatchCriteria,
    CapabilityMatchResult,
)

logger = logging.getLogger(__name__)


class RedisAgentRegistry(AgentRegistry):
    """
    Redis-backed AgentRegistry adapter with capability support.

    Keys:
      - {pfx}:agents:{type}:{instance} -> JSON payload (includes capabilities)
      - {pfx}:agents:index -> set of keys
      - {pfx}:capabilities:{type}:{instance} -> JSON capability set
      - {pfx}:capabilities:index -> set of capability keys

    Liveness:
      - Store last_heartbeat timestamp; liveness = now - last_heartbeat <= ttl
      - Background heartbeats update registered agents periodically
      - Capability data is refreshed with heartbeats
    """

    def __init__(
        self,
        redis: Redis,
        key_prefix: str = "ao",
        heartbeat_ttl_s: float = 30.0,
        heartbeat_interval_s: float | None = None,
        enable_events: bool = False,
        event_publisher: Any | None = None,
    ) -> None:
        super().__init__()
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        self._ttl = float(heartbeat_ttl_s)
        self._hb_task: asyncio.Task | None = None
        self._hb_interval_s: float = (
            float(heartbeat_interval_s)
            if heartbeat_interval_s is not None
            else max(1.0, heartbeat_ttl_s / 3.0)
        )

        # Event broadcasting
        self._enable_events = enable_events
        self._event_publisher = event_publisher
        self._event_channel_prefix = f"{self._pfx}:events"
        self._agent_status_cache: dict[
            str, dict[str, Any]
        ] = {}  # Track previous status for change detection

        # Capability matching
        self._capability_matcher = CapabilityMatcher()
        self._default_matching_strategy = MatchingStrategy.WEIGHTED_SCORE

    # ---- Key helpers ----
    def _key(self, agent_id: AgentId) -> str:
        return (
            f"{self._pfx}:agents:{agent_id.type.value}:{agent_id.instance or 'default'}"
        )

    def _index_key(self) -> str:
        return f"{self._pfx}:agents:index"

    def _capability_key(self, agent_id: AgentId) -> str:
        return f"{self._pfx}:capabilities:{agent_id.type.value}:{agent_id.instance or 'default'}"

    def _capability_index_key(self) -> str:
        return f"{self._pfx}:capabilities:index"

    def _event_channel(self, event_type: str) -> str:
        return f"{self._event_channel_prefix}:{event_type}"

    def _agent_status_key(self, agent_id: AgentId) -> str:
        return f"{agent_id.type.value}:{agent_id.instance or 'default'}"

    # ---- Overrides ----
    def register(self, agent: Agent) -> None:
        super().register(agent)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._restore_then_persist(agent))
        except RuntimeError:
            asyncio.run(self._restore_then_persist(agent))

    def deregister(self, agent_id: AgentId) -> None:
        super().deregister(agent_id)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._delete(agent_id))
        except RuntimeError:
            asyncio.run(self._delete(agent_id))

    async def _restore_then_persist(self, agent: Agent) -> None:
        with contextlib.suppress(Exception):
            await self.restore_state_if_available(agent)
        await self._persist(agent)

    async def _persist(self, agent: Agent) -> None:
        key = self._key(agent.agent_id)
        try:
            state: dict[str, Any] | None = None
            try:
                s = await agent.export_state()
                if isinstance(s, dict) and s:
                    state = s
            except Exception:
                state = None

            # Get agent capabilities if available
            capabilities: dict[str, Any] | None = None
            try:
                if hasattr(agent, "get_capabilities"):
                    cap_set = await agent.get_capabilities()
                    if isinstance(cap_set, AgentCapabilitySet):
                        capabilities = cap_set.dict()
                elif hasattr(agent, "capabilities") and agent.capabilities:
                    # Fallback for agents with direct capabilities attribute
                    if isinstance(agent.capabilities, AgentCapabilitySet):
                        capabilities = agent.capabilities.dict()
            except Exception:
                capabilities = None

            payload = {
                "name": agent.name,
                "agent_id": (
                    agent.agent_id.model_dump()
                    if hasattr(agent.agent_id, "model_dump")
                    else str(agent.agent_id)
                ),
                "status": agent.status_snapshot(),
                "last_heartbeat": time.time(),
            }
            if state is not None:
                payload["state"] = state
            if capabilities is not None:
                payload["capabilities"] = capabilities

            px = max(1, int(self._ttl * 1000))
            await self._redis.set(key, json.dumps(payload), px=px)
            await self._redis.sadd(self._index_key(), key)

            # Store capabilities separately for efficient searching
            if capabilities is not None:
                cap_key = self._capability_key(agent.agent_id)
                await self._redis.set(cap_key, json.dumps(capabilities), px=px)
                await self._redis.sadd(self._capability_index_key(), cap_key)

            # Detect and publish status changes
            await self._detect_and_publish_status_changes(agent)

        except Exception as e:
            logger.warning("Failed to persist agent registration: %s", e)

    async def _delete(self, agent_id: AgentId) -> None:
        key = self._key(agent_id)
        cap_key = self._capability_key(agent_id)
        with contextlib.suppress(Exception):
            # Remove agent data
            await self._redis.delete(key)
            await self._redis.srem(self._index_key(), key)

            # Remove capability data
            await self._redis.delete(cap_key)
            await self._redis.srem(self._capability_index_key(), cap_key)

            # Publish deregistration event
            await self._publish_agent_deregistered(agent_id)

    # ---- Heartbeats ----
    def start_heartbeats(self) -> None:
        if self._hb_task and not self._hb_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self._hb_task = loop.create_task(self._heartbeat_loop())

    def stop_heartbeats(self) -> None:
        if self._hb_task and not self._hb_task.done():
            self._hb_task.cancel()

    async def _heartbeat_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._hb_interval_s)
                await self._heartbeat_once()
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.warning("RedisAgentRegistry heartbeat error: %s", e)

    async def _heartbeat_once(self) -> None:
        for agent in self.all():
            await self._heartbeat_agent(agent)

    async def _heartbeat_agent(self, agent: Agent) -> None:
        key = self._key(agent.agent_id)
        try:
            # Refresh TTL and last_heartbeat; embed current status snapshot and optional state
            state: dict[str, Any] | None = None
            try:
                s = await agent.export_state()
                if isinstance(s, dict) and s:
                    state = s
            except Exception:
                state = None

            # Get fresh capability data during heartbeat
            capabilities: dict[str, Any] | None = None
            try:
                if hasattr(agent, "get_capabilities"):
                    cap_set = await agent.get_capabilities()
                    if isinstance(cap_set, AgentCapabilitySet):
                        capabilities = cap_set.dict()
                elif hasattr(agent, "capabilities") and agent.capabilities:
                    # Fallback for agents with direct capabilities attribute
                    if isinstance(agent.capabilities, AgentCapabilitySet):
                        capabilities = agent.capabilities.dict()
            except Exception:
                capabilities = None

            payload = {
                "name": agent.name,
                "agent_id": (
                    agent.agent_id.model_dump()
                    if hasattr(agent.agent_id, "model_dump")
                    else str(agent.agent_id)
                ),
                "status": agent.status_snapshot(),
                "last_heartbeat": time.time(),
            }
            if state is not None:
                payload["state"] = state
            if capabilities is not None:
                payload["capabilities"] = capabilities

            px = max(1, int(self._ttl * 1000))
            await self._redis.set(key, json.dumps(payload), px=px)

            # Update capability data separately for efficient searching
            if capabilities is not None:
                cap_key = self._capability_key(agent.agent_id)
                await self._redis.set(cap_key, json.dumps(capabilities), px=px)
                await self._redis.sadd(self._capability_index_key(), cap_key)

            # Detect and publish status changes (including heartbeat events)
            await self._detect_and_publish_status_changes(agent)

        except Exception as e:
            logger.warning(f"Failed to update heartbeat for agent {agent.agent_id}: {e}")

    async def restore_state_if_available(self, agent: Agent) -> bool:
        """If a serialized state exists in Redis for this agent, restore it.
        Returns True if state was found and applied.
        """
        key = self._key(agent.agent_id)
        try:
            val = await self._redis.get(key)
            if not val:
                return False
            data = json.loads(val)
            st = data.get("state")
            if isinstance(st, dict) and st:
                try:
                    await agent.import_state(st)
                    return True
                except Exception:
                    return False
        except Exception:
            return False
        return False

    # ---- Discovery across processes ----
    async def list_registered(self) -> list[dict[str, Any]]:
        try:
            keys = await self._redis.smembers(self._index_key())
            agents: list[dict[str, Any]] = []
            for bkey in keys:
                k = bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                val = await self._redis.get(k)
                if not val:
                    continue
                try:
                    data = json.loads(val)
                except Exception as e:
                    logger.debug(f"Failed to parse agent data for key {k}: {e}")
                    continue
                # Liveness calculation
                last = float(data.get("last_heartbeat", 0.0))
                data["alive"] = (time.time() - last) <= self._ttl
                agents.append(data)
            return agents
        except Exception:
            return []

    async def snapshot_async(self) -> dict[str, Any]:
        """Async snapshot combining local in-memory and redis-discovered agents."""
        local = super().snapshot()
        remote = await self.list_registered()
        return {"local": local, "redis_index": remote}

    # ---- Event Broadcasting ----
    async def _publish_agent_event(
        self, event_type: str, agent_id: AgentId, event_data: dict[str, Any]
    ) -> None:
        """Publish an agent event using the EventPublisher."""
        if not self._enable_events or not self._event_publisher:
            return

        try:
            agent_key = self._agent_status_key(agent_id)

            # Determine agent status from event data
            status = event_data.get("status", {}).get("status", "unknown")
            previous_status = None

            if event_type == "status_changed" and "changes" in event_data:
                changes = event_data["changes"]
                if "status" in changes:
                    previous_status = changes["status"].get("previous")

            # Publish using EventPublisher
            await self._event_publisher.publish_agent_status_event(
                agent_id=agent_key,
                agent_type=agent_id.type.value,
                status=status,
                instance=agent_id.instance,
                previous_status=previous_status,
                heartbeat_age=event_data.get("heartbeat_age", 0.0),
                metadata={
                    "event_type": event_type,
                    "name": event_data.get("name"),
                    "reason": event_data.get("reason"),
                    **event_data.get("status", {}),
                },
            )

            logger.debug(
                f"Published agent event via EventPublisher: {event_type} for {agent_key}"
            )

        except Exception as e:
            logger.warning(f"Failed to publish agent event via EventPublisher: {e}")

    async def _detect_and_publish_status_changes(self, agent: Agent) -> None:
        """Detect status changes and publish events."""
        if not self._enable_events:
            return

        agent_key = self._agent_status_key(agent.agent_id)
        current_status = agent.status_snapshot()

        # Get previous status from cache
        previous_status = self._agent_status_cache.get(agent_key, {})

        # Check for status changes
        status_changed = False
        changes = {}

        for key, current_value in current_status.items():
            previous_value = previous_status.get(key)
            if previous_value != current_value:
                changes[key] = {"previous": previous_value, "current": current_value}
                status_changed = True

        # Update cache
        self._agent_status_cache[agent_key] = current_status.copy()

        # Publish status change event if there are changes
        if status_changed:
            await self._publish_agent_event(
                "status_changed",
                agent.agent_id,
                {
                    "status": current_status,
                    "changes": changes,
                    "heartbeat_age": 0.0,  # Fresh heartbeat
                },
            )

    async def _publish_agent_registered(self, agent: Agent) -> None:
        """Publish agent registration event."""
        await self._publish_agent_event(
            "registered",
            agent.agent_id,
            {
                "name": agent.name,
                "status": agent.status_snapshot(),
                "heartbeat_age": 0.0,
            },
        )

    async def _publish_agent_deregistered(self, agent_id: AgentId) -> None:
        """Publish agent deregistration event."""
        await self._publish_agent_event(
            "deregistered", agent_id, {"reason": "explicit_deregistration"}
        )

        # Remove from status cache
        agent_key = self._agent_status_key(agent_id)
        self._agent_status_cache.pop(agent_key, None)

    async def _publish_heartbeat_event(
        self, agent: Agent, heartbeat_age: float = 0.0
    ) -> None:
        """Publish heartbeat event with current status."""
        await self._publish_agent_event(
            "heartbeat",
            agent.agent_id,
            {
                "name": agent.name,
                "status": agent.status_snapshot(),
                "heartbeat_age": heartbeat_age,
            },
        )

    # ---- Capability Management ----

    async def register_capabilities(
        self, agent_id: AgentId, capability_set: AgentCapabilitySet
    ) -> bool:
        """Register or update capabilities for an agent."""
        try:
            cap_key = self._capability_key(agent_id)
            capabilities_data = capability_set.dict()
            px = max(1, int(self._ttl * 1000))

            await self._redis.set(cap_key, json.dumps(capabilities_data), px=px)
            await self._redis.sadd(self._capability_index_key(), cap_key)

            logger.debug(
                f"Registered {len(capability_set.capabilities)} capabilities for {agent_id.type.value}:{agent_id.instance}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register capabilities for {agent_id}: {e}")
            return False

    async def get_agent_capabilities(
        self, agent_id: AgentId
    ) -> AgentCapabilitySet | None:
        """Get capabilities for a specific agent."""
        try:
            cap_key = self._capability_key(agent_id)
            data = await self._redis.get(cap_key)

            if not data:
                return None

            capabilities_dict = json.loads(data)
            return AgentCapabilitySet(**capabilities_dict)

        except Exception as e:
            logger.error(f"Failed to get capabilities for {agent_id}: {e}")
            return None

    async def list_all_capabilities(self) -> list[AgentCapabilitySet]:
        """List all registered agent capabilities."""
        try:
            cap_keys = await self._redis.smembers(self._capability_index_key())
            capability_sets = []

            for bkey in cap_keys:
                key = bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                data = await self._redis.get(key)

                if data:
                    try:
                        capabilities_dict = json.loads(data)
                        capability_set = AgentCapabilitySet(**capabilities_dict)
                        capability_sets.append(capability_set)
                    except Exception as e:
                        logger.warning(
                            f"Failed to parse capabilities from key {key}: {e}"
                        )

            return capability_sets

        except Exception as e:
            logger.error(f"Failed to list capabilities: {e}")
            return []

    async def discover_capabilities(
        self, request: CapabilityDiscoveryRequest
    ) -> CapabilityDiscoveryResponse:
        """Discover agents based on capability criteria using advanced matching algorithms."""
        start_time = time.time()

        try:
            all_capabilities = await self.list_all_capabilities()

            # Use configured default matching strategy
            strategy = self._default_matching_strategy

            # Use the capability matcher for sophisticated matching
            matches = self._capability_matcher.match_capabilities(
                capability_sets=all_capabilities,
                criteria=request.criteria,
                strategy=strategy,
                max_results=request.max_results,
            )

            # Apply additional sorting if requested
            if request.sort_by != "match_score":
                if request.sort_by == "agent_load":
                    matches.sort(
                        key=lambda x: x.agent_load_factor,
                        reverse=not request.sort_descending,
                    )
                elif request.sort_by == "estimated_duration":
                    matches.sort(
                        key=lambda x: x.capability.estimated_duration_ms or 0,
                        reverse=request.sort_descending,
                    )

            search_duration = int((time.time() - start_time) * 1000)

            return CapabilityDiscoveryResponse(
                matches=matches,
                total_agents_searched=len(all_capabilities),
                search_duration_ms=search_duration,
            )

        except Exception as e:
            logger.error(f"Capability discovery failed: {e}")
            return CapabilityDiscoveryResponse(
                matches=[],
                total_agents_searched=0,
                search_duration_ms=int((time.time() - start_time) * 1000),
            )

    # Legacy method kept for backward compatibility
    def _evaluate_capability_match(
        self,
        capability: AgentCapability,
        cap_set: AgentCapabilitySet,
        criteria: CapabilityMatchCriteria,
    ) -> CapabilityMatchResult | None:
        """
        Legacy capability matching method - now delegates to CapabilityMatcher.
        Kept for backward compatibility.
        """
        try:
            matches = self._capability_matcher.match_capabilities(
                capability_sets=[cap_set],
                criteria=criteria,
                strategy=MatchingStrategy.WEIGHTED_SCORE,
                max_results=1,
            )

            # Find the match for this specific capability
            for match in matches:
                if (
                    match.capability.name == capability.name
                    and match.capability.version == capability.version
                ):
                    return match

            return None

        except Exception as e:
            logger.error(f"Failed to evaluate capability match: {e}")
            return None

    def set_matching_strategy(self, strategy: MatchingStrategy) -> None:
        """Set the default capability matching strategy."""
        self._default_matching_strategy = strategy
        logger.info(f"Capability matching strategy set to: {strategy.value}")

    def get_matching_strategy(self) -> MatchingStrategy:
        """Get the current default capability matching strategy."""
        return self._default_matching_strategy

    async def get_matching_statistics(self) -> dict[str, Any]:
        """Get statistics about capability matching performance."""
        try:
            all_capabilities = await self.list_all_capabilities()

            total_agents = len(all_capabilities)
            total_capabilities = sum(
                len(cap_set.capabilities) for cap_set in all_capabilities
            )
            active_capabilities = sum(
                len(cap_set.get_active_capabilities()) for cap_set in all_capabilities
            )

            # Count capabilities by type
            type_counts = {}
            for cap_set in all_capabilities:
                for cap in cap_set.capabilities:
                    type_name = cap.type.value
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1

            # Calculate average load factor
            avg_load_factor = 0.0
            if total_agents > 0:
                avg_load_factor = (
                    sum(cap_set.load_factor for cap_set in all_capabilities)
                    / total_agents
                )

            return {
                "total_agents": total_agents,
                "total_capabilities": total_capabilities,
                "active_capabilities": active_capabilities,
                "capabilities_by_type": type_counts,
                "average_load_factor": avg_load_factor,
                "matching_strategy": self._default_matching_strategy.value,
                "matcher_weights": self._capability_matcher._strategy_weights,
            }

        except Exception as e:
            logger.error(f"Failed to get matching statistics: {e}")
            return {
                "error": str(e),
                "total_agents": 0,
                "total_capabilities": 0,
                "active_capabilities": 0,
            }

    # ---- Capability Data Freshness ----

    async def cleanup_stale_capabilities(self) -> int:
        """
        Clean up stale capability data that no longer has corresponding agent data.

        Returns:
            Number of stale capability entries removed
        """
        try:
            # Get all capability keys
            cap_keys = await self._redis.smembers(self._capability_index_key())
            agent_keys = await self._redis.smembers(self._index_key())

            # Convert agent keys to expected capability key format
            expected_cap_keys = set()
            for bkey in agent_keys:
                agent_key = (
                    bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                )
                # Convert from "ao:agents:type:instance" to "ao:capabilities:type:instance"
                if ":agents:" in agent_key:
                    cap_key = agent_key.replace(":agents:", ":capabilities:")
                    expected_cap_keys.add(cap_key)

            # Find stale capability keys
            stale_keys = []
            for bkey in cap_keys:
                cap_key = (
                    bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                )
                if cap_key not in expected_cap_keys:
                    stale_keys.append(cap_key)

            # Remove stale capability data
            removed_count = 0
            for stale_key in stale_keys:
                try:
                    await self._redis.delete(stale_key)
                    await self._redis.srem(self._capability_index_key(), stale_key)
                    removed_count += 1
                except Exception as e:
                    logger.warning(
                        f"Failed to remove stale capability key {stale_key}: {e}"
                    )

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} stale capability entries")

            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup stale capabilities: {e}")
            return 0

    async def refresh_capability_ttl(self, agent_id: AgentId) -> bool:
        """
        Refresh the TTL for capability data of a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if TTL was refreshed successfully
        """
        try:
            cap_key = self._capability_key(agent_id)
            max(1, int(self._ttl * 1000))

            # Check if capability data exists
            exists = await self._redis.exists(cap_key)
            if exists:
                await self._redis.expire(cap_key, int(self._ttl))
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to refresh capability TTL for {agent_id}: {e}")
            return False

    async def get_capability_freshness_info(self) -> dict[str, Any]:
        """
        Get information about capability data freshness.

        Returns:
            Dictionary with freshness statistics
        """
        try:
            cap_keys = await self._redis.smembers(self._capability_index_key())
            agent_keys = await self._redis.smembers(self._index_key())

            total_capabilities = len(cap_keys)
            total_agents = len(agent_keys)

            # Check for orphaned capabilities
            expected_cap_keys = set()
            for bkey in agent_keys:
                agent_key = (
                    bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                )
                if ":agents:" in agent_key:
                    cap_key = agent_key.replace(":agents:", ":capabilities:")
                    expected_cap_keys.add(cap_key)

            orphaned_count = 0
            for bkey in cap_keys:
                cap_key = (
                    bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                )
                if cap_key not in expected_cap_keys:
                    orphaned_count += 1

            return {
                "total_capability_entries": total_capabilities,
                "total_agent_entries": total_agents,
                "orphaned_capabilities": orphaned_count,
                "capability_coverage": (total_capabilities - orphaned_count)
                / max(1, total_agents),
                "ttl_seconds": self._ttl,
                "heartbeat_interval_seconds": self._hb_interval_s,
            }

        except Exception as e:
            logger.error(f"Failed to get capability freshness info: {e}")
            return {
                "error": str(e),
                "total_capability_entries": 0,
                "total_agent_entries": 0,
                "orphaned_capabilities": 0,
                "capability_coverage": 0.0,
            }

    # ---- Diagnostic Methods ----
    async def get_all_agents(self) -> dict[str, dict[str, Any]]:
        """
        Get all registered agents with their information.

        Returns:
            Dictionary mapping agent_id to agent_info
        """
        try:
            agents_list = await self.list_registered()
            result = {}

            for agent_data in agents_list:
                # Extract agent_id from the data
                agent_id_data = agent_data.get("agent_id")
                if isinstance(agent_id_data, dict):
                    # Construct agent_id string from type and instance
                    agent_type = agent_id_data.get("type", "unknown")
                    agent_instance = agent_id_data.get("instance", "default")
                    agent_id = f"{agent_type}:{agent_instance}"
                else:
                    agent_id = str(agent_id_data) if agent_id_data else "unknown"

                result[agent_id] = {
                    "agent_type": agent_id_data.get("type")
                    if isinstance(agent_id_data, dict)
                    else None,
                    "instance": agent_id_data.get("instance")
                    if isinstance(agent_id_data, dict)
                    else None,
                    "name": agent_data.get("name"),
                    "status": agent_data.get("status"),
                    "alive": agent_data.get("alive", False),
                    "last_heartbeat": agent_data.get("last_heartbeat"),
                    "capabilities": agent_data.get("capabilities"),
                    "state": agent_data.get("state"),
                }

            return result

        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return {}

    async def get_agent_info(self, agent_id: str) -> dict[str, Any] | None:
        """
        Get information for a specific agent.

        Args:
            agent_id: Agent identifier in format "type:instance"

        Returns:
            Agent information dictionary or None if not found
        """
        try:
            # Parse agent_id
            parts = agent_id.split(":", 1)
            if len(parts) != 2:
                logger.warning(f"Invalid agent_id format: {agent_id}")
                return None

            agent_type, instance = parts

            # Construct Redis key
            key = f"{self._pfx}:agents:{agent_type}:{instance}"

            # Get agent data from Redis
            val = await self._redis.get(key)
            if not val:
                return None

            data = json.loads(val)

            # Calculate liveness
            last = float(data.get("last_heartbeat", 0.0))
            alive = (time.time() - last) <= self._ttl

            return {
                "agent_type": agent_type,
                "instance": instance,
                "name": data.get("name"),
                "status": data.get("status"),
                "alive": alive,
                "last_heartbeat": last,
                "capabilities": data.get("capabilities"),
                "state": data.get("state"),
            }

        except Exception as e:
            logger.error(f"Failed to get agent info for {agent_id}: {e}")
            return None
