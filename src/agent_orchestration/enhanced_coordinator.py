"""
Enhanced message coordinator that integrates real agent communication with Redis infrastructure.

This module extends the existing RedisMessageCoordinator to support real agent communication
through the protocol bridge and adapter system.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis

from .adapters import AgentAdapterFactory, RetryConfig
from .coordinators.redis_message_coordinator import RedisMessageCoordinator
from .messaging import MessageResult
from .models import AgentId, AgentMessage, AgentType
from .protocol_bridge import MessageRouter, ProtocolTranslator, ProtocolType

logger = logging.getLogger(__name__)


class EnhancedRedisMessageCoordinator(RedisMessageCoordinator):
    """
    Enhanced Redis message coordinator with real agent communication support.

    Extends the base RedisMessageCoordinator to support routing messages to real
    agent implementations through the protocol bridge system.
    """

    def __init__(
        self,
        redis: Redis,
        key_prefix: str = "ao",
        queue_size: int = 1000,
        retry_attempts: int = 3,
        backoff_base: float = 1.0,
        backoff_factor: float = 2.0,
        backoff_max: float = 60.0,
        neo4j_manager=None,
        tools: dict[str, Any] | None = None,
        enable_real_agents: bool = True,
        fallback_to_mock: bool = True,
    ):
        # Initialize base coordinator
        super().__init__(
            redis=redis,
            key_prefix=key_prefix,
            queue_size=queue_size,
            retry_attempts=retry_attempts,
            backoff_base=backoff_base,
            backoff_factor=backoff_factor,
            backoff_max=backoff_max,
        )

        # Real agent communication setup
        self.enable_real_agents = enable_real_agents
        self.fallback_to_mock = fallback_to_mock

        if self.enable_real_agents:
            # Create adapter factory
            retry_config = RetryConfig(
                max_retries=retry_attempts,
                base_delay=backoff_base,
                exponential_base=backoff_factor,
                max_delay=backoff_max,
            )

            self.adapter_factory = AgentAdapterFactory(
                neo4j_manager=neo4j_manager,
                tools=tools,
                fallback_to_mock=fallback_to_mock,
                retry_config=retry_config,
            )

            # Create adapters
            self.ipa_adapter = self.adapter_factory.create_ipa_adapter()
            self.wba_adapter = self.adapter_factory.create_wba_adapter()
            self.nga_adapter = self.adapter_factory.create_nga_adapter()

            # Create message router
            self.message_router = MessageRouter(
                self.ipa_adapter, self.wba_adapter, self.nga_adapter
            )

            # Protocol translator
            self.protocol_translator = ProtocolTranslator()
        else:
            self.adapter_factory = None
            self.message_router = None
            self.protocol_translator = None

    async def send_message_to_real_agent(
        self, sender: AgentId, recipient: AgentId, message: AgentMessage
    ) -> MessageResult:
        """
        Send a message directly to a real agent implementation.

        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            message: Message to send

        Returns:
            MessageResult indicating delivery outcome
        """
        if not self.enable_real_agents or not self.message_router:
            return MessageResult(
                message_id=message.message_id,
                delivered=False,
                error="Real agent communication not enabled",
            )

        try:
            # Route message to appropriate real agent
            result = await self.message_router.route_message(recipient.type, message)

            # If successful, also store in Redis for audit/monitoring
            if result.delivered:
                await super().send_message(sender, recipient, message)

            return result

        except Exception as e:
            logger.error(f"Failed to send message to real agent {recipient}: {e}")

            # Fallback to standard Redis delivery if enabled
            if self.fallback_to_mock:
                logger.warning("Falling back to standard Redis message delivery")
                return await super().send_message(sender, recipient, message)
            else:
                return MessageResult(
                    message_id=message.message_id, delivered=False, error=str(e)
                )

    async def send_message(
        self, sender: AgentId, recipient: AgentId, message: AgentMessage
    ) -> MessageResult:
        """
        Send a message with automatic routing to real agents when available.

        This method automatically determines whether to route to real agents
        or use standard Redis message queuing based on configuration.
        """
        # Check if we should route to real agent
        if (
            self.enable_real_agents
            and self.message_router
            and recipient.type in [AgentType.IPA, AgentType.WBA, AgentType.NGA]
        ):

            try:
                return await self.send_message_to_real_agent(sender, recipient, message)
            except Exception as e:
                logger.warning(f"Real agent routing failed: {e}")

                if self.fallback_to_mock:
                    logger.info("Falling back to standard Redis delivery")
                    return await super().send_message(sender, recipient, message)
                else:
                    return MessageResult(
                        message_id=message.message_id, delivered=False, error=str(e)
                    )

        # Use standard Redis message delivery
        return await super().send_message(sender, recipient, message)

    async def process_agent_response(
        self,
        agent_type: AgentType,
        response: dict[str, Any],
        original_message: AgentMessage,
    ) -> dict[str, Any]:
        """
        Process a response from a real agent and translate it back to orchestration format.

        Args:
            agent_type: Type of agent that generated the response
            response: Raw response from the agent
            original_message: Original message that triggered the response

        Returns:
            Processed response in orchestration format
        """
        if not self.protocol_translator:
            return response

        try:
            # Translate response back to orchestration format
            translation = self.protocol_translator.translate_message(
                response,
                ProtocolType.REAL_AGENT,
                ProtocolType.ORCHESTRATION,
                agent_type,
            )

            if translation.success:
                return translation.translated_message
            else:
                logger.warning(f"Response translation failed: {translation.error}")
                return response

        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
            return response

    async def health_check_real_agents(self) -> dict[str, bool]:
        """
        Perform health checks on real agent adapters.

        Returns:
            Dict mapping agent types to health status
        """
        if not self.enable_real_agents:
            return {}

        health_status = {}

        # Check IPA adapter
        try:
            test_result = await self.ipa_adapter.process_input("health check")
            health_status["ipa"] = test_result.get("source") != "mock_fallback"
        except Exception as e:
            logger.warning(f"IPA health check failed: {e}")
            health_status["ipa"] = False

        # Check WBA adapter
        try:
            test_result = await self.wba_adapter.process_world_request("health_check")
            health_status["wba"] = test_result.get("source") != "mock_fallback"
        except Exception as e:
            logger.warning(f"WBA health check failed: {e}")
            health_status["wba"] = False

        # Check NGA adapter
        try:
            test_result = await self.nga_adapter.generate_narrative("health check")
            health_status["nga"] = test_result.get("source") != "mock_fallback"
        except Exception as e:
            logger.warning(f"NGA health check failed: {e}")
            health_status["nga"] = False

        return health_status

    async def get_real_agent_metrics(self) -> dict[str, Any]:
        """
        Get metrics from real agent adapters.

        Returns:
            Dict containing real agent communication metrics
        """
        if not self.enable_real_agents:
            return {}

        metrics = {
            "real_agents_enabled": True,
            "fallback_enabled": self.fallback_to_mock,
            "adapters_available": {
                "ipa": self.ipa_adapter._available if self.ipa_adapter else False,
                "wba": self.wba_adapter._available if self.wba_adapter else False,
                "nga": self.nga_adapter._available if self.nga_adapter else False,
            },
        }

        # Add health check results
        try:
            health_status = await self.health_check_real_agents()
            metrics["health_status"] = health_status
        except Exception as e:
            logger.warning(f"Failed to get health status: {e}")
            metrics["health_status"] = {}

        return metrics

    def configure_real_agents(
        self,
        enable_real_agents: bool | None = None,
        fallback_to_mock: bool | None = None,
        retry_config: RetryConfig | None = None,
    ) -> None:
        """
        Configure real agent communication settings at runtime.

        Args:
            enable_real_agents: Whether to enable real agent communication
            fallback_to_mock: Whether to fallback to mock implementations
            retry_config: Retry configuration for agent communication
        """
        if enable_real_agents is not None:
            self.enable_real_agents = enable_real_agents

        if fallback_to_mock is not None:
            self.fallback_to_mock = fallback_to_mock

        if retry_config is not None and self.adapter_factory:
            # Update retry configuration in adapters
            self.adapter_factory.retry_config = retry_config

            # Recreate adapters with new config
            self.ipa_adapter = self.adapter_factory.create_ipa_adapter()
            self.wba_adapter = self.adapter_factory.create_wba_adapter()
            self.nga_adapter = self.adapter_factory.create_nga_adapter()

            # Recreate message router
            self.message_router = MessageRouter(
                self.ipa_adapter, self.wba_adapter, self.nga_adapter
            )


class BatchedMessageProcessor:
    """Efficient batched message processing for agent coordination."""

    def __init__(
        self,
        batch_size: int = 10,
        batch_timeout_ms: int = 100,
        max_concurrent_batches: int = 5,
    ):
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.max_concurrent_batches = max_concurrent_batches

        self._pending_messages: list[dict[str, Any]] = []
        self._batch_lock = asyncio.Lock()
        self._processing_semaphore = asyncio.Semaphore(max_concurrent_batches)
        self._batch_timer: asyncio.Task | None = None

    async def add_message(
        self, message: dict[str, Any], processor_func: Callable
    ) -> Any:
        """Add message to batch for processing."""
        async with self._batch_lock:
            # Add message to pending batch
            message_entry = {
                "message": message,
                "processor": processor_func,
                "future": asyncio.Future(),
                "timestamp": time.time(),
            }

            self._pending_messages.append(message_entry)

            # Start batch timer if not already running
            if self._batch_timer is None or self._batch_timer.done():
                self._batch_timer = asyncio.create_task(self._batch_timeout_handler())

            # Process batch if it's full
            if len(self._pending_messages) >= self.batch_size:
                await self._process_current_batch()

            return await message_entry["future"]

    async def _batch_timeout_handler(self):
        """Handle batch timeout to process partial batches."""
        await asyncio.sleep(self.batch_timeout_ms / 1000.0)

        async with self._batch_lock:
            if self._pending_messages:
                await self._process_current_batch()

    async def _process_current_batch(self):
        """Process the current batch of messages."""
        if not self._pending_messages:
            return

        # Extract current batch
        batch = self._pending_messages.copy()
        self._pending_messages.clear()

        # Process batch asynchronously
        asyncio.create_task(self._execute_batch(batch))

    async def _execute_batch(self, batch: list[dict[str, Any]]):
        """Execute a batch of messages."""
        async with self._processing_semaphore:
            # Group messages by processor type for efficiency
            processor_groups = {}
            for entry in batch:
                processor_key = id(entry["processor"])
                if processor_key not in processor_groups:
                    processor_groups[processor_key] = {
                        "processor": entry["processor"],
                        "entries": [],
                    }
                processor_groups[processor_key]["entries"].append(entry)

            # Process each group
            for group in processor_groups.values():
                await self._process_group(group["processor"], group["entries"])

    async def _process_group(
        self, processor_func: Callable, entries: list[dict[str, Any]]
    ):
        """Process a group of messages with the same processor."""
        tasks = []

        for entry in entries:
            task = asyncio.create_task(
                self._process_single_message(processor_func, entry)
            )
            tasks.append(task)

        # Wait for all messages in the group to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_message(
        self, processor_func: Callable, entry: dict[str, Any]
    ):
        """Process a single message and set its future result."""
        try:
            result = await processor_func(entry["message"])
            entry["future"].set_result(result)
        except Exception as e:
            entry["future"].set_exception(e)


class ScalableWorkflowCoordinator:
    """Scalable coordinator for managing multiple simultaneous workflows."""

    def __init__(
        self,
        enhanced_coordinator: EnhancedRedisMessageCoordinator,
        max_concurrent_workflows: int = 100,
        workflow_timeout_s: float = 300.0,
        enable_batching: bool = True,
    ):
        self.enhanced_coordinator = enhanced_coordinator
        self.max_concurrent_workflows = max_concurrent_workflows
        self.workflow_timeout_s = workflow_timeout_s
        self.enable_batching = enable_batching

        # Workflow management
        self._active_workflows: dict[str, dict[str, Any]] = {}
        self._workflow_semaphore = asyncio.Semaphore(max_concurrent_workflows)
        self._workflow_lock = asyncio.Lock()

        # Batching support
        if enable_batching:
            self._batch_processor = BatchedMessageProcessor(
                batch_size=10, batch_timeout_ms=50, max_concurrent_batches=10
            )
        else:
            self._batch_processor = None

        # Monitoring integration
        from .monitoring import get_system_monitor

        self._system_monitor = get_system_monitor()

    async def execute_workflow(
        self,
        workflow_id: str,
        workflow_steps: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a complete workflow with scalable coordination."""
        async with self._workflow_semaphore:
            # Record workflow start
            self._system_monitor.start_workflow(workflow_id)

            try:
                async with self._workflow_lock:
                    self._active_workflows[workflow_id] = {
                        "start_time": time.time(),
                        "steps": workflow_steps,
                        "context": context or {},
                        "status": "running",
                    }

                # Execute workflow with timeout
                result = await asyncio.wait_for(
                    self._execute_workflow_steps(
                        workflow_id, workflow_steps, context or {}
                    ),
                    timeout=self.workflow_timeout_s,
                )

                # Record successful completion
                self._system_monitor.end_workflow(workflow_id, success=True)

                async with self._workflow_lock:
                    if workflow_id in self._active_workflows:
                        self._active_workflows[workflow_id]["status"] = "completed"
                        self._active_workflows[workflow_id]["result"] = result

                return result

            except asyncio.TimeoutError:
                logger.error(
                    f"Workflow {workflow_id} timed out after {self.workflow_timeout_s}s"
                )
                self._system_monitor.end_workflow(workflow_id, success=False)

                async with self._workflow_lock:
                    if workflow_id in self._active_workflows:
                        self._active_workflows[workflow_id]["status"] = "timeout"

                raise

            except Exception as e:
                logger.error(f"Workflow {workflow_id} failed: {e}")
                self._system_monitor.end_workflow(workflow_id, success=False)

                async with self._workflow_lock:
                    if workflow_id in self._active_workflows:
                        self._active_workflows[workflow_id]["status"] = "failed"
                        self._active_workflows[workflow_id]["error"] = str(e)

                raise

            finally:
                # Cleanup workflow after delay
                asyncio.create_task(self._cleanup_workflow(workflow_id, delay=60.0))

    async def _execute_workflow_steps(
        self, workflow_id: str, steps: list[dict[str, Any]], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute individual workflow steps."""
        results = {}
        accumulated_context = context.copy()

        for i, step in enumerate(steps):
            step_id = f"{workflow_id}_step_{i}"
            step_type = step.get("type")
            step_config = step.get("config", {})

            logger.debug(f"Executing step {step_id}: {step_type}")

            try:
                if step_type == "ipa":
                    result = await self._execute_ipa_step(
                        step_config, accumulated_context
                    )
                elif step_type == "wba":
                    result = await self._execute_wba_step(
                        step_config, accumulated_context
                    )
                elif step_type == "nga":
                    result = await self._execute_nga_step(
                        step_config, accumulated_context
                    )
                elif step_type == "parallel":
                    result = await self._execute_parallel_steps(
                        step_config, accumulated_context
                    )
                else:
                    raise ValueError(f"Unknown step type: {step_type}")

                results[step_id] = result

                # Update context with step results
                if step.get("update_context", True):
                    accumulated_context.update(result)

            except Exception as e:
                logger.error(f"Step {step_id} failed: {e}")
                results[step_id] = {"error": str(e), "success": False}

                # Check if workflow should continue on error
                if not step.get("continue_on_error", False):
                    raise

        return {
            "workflow_id": workflow_id,
            "steps_results": results,
            "final_context": accumulated_context,
            "success": True,
        }

    async def _execute_ipa_step(
        self, config: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute IPA step with batching support."""
        text = config.get("text") or context.get("player_input", "")

        if self._batch_processor:
            # Use batched processing
            async def ipa_processor(message):
                return await self.enhanced_coordinator.ipa_adapter.process_input(
                    message["text"]
                )

            result = await self._batch_processor.add_message(
                {"text": text}, ipa_processor
            )
        else:
            # Direct processing
            result = await self.enhanced_coordinator.ipa_adapter.process_input(text)

        return {"ipa_result": result, "step_type": "ipa"}

    async def _execute_wba_step(
        self, config: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute WBA step with batching support."""
        world_id = config.get("world_id") or context.get("session_id", "default")
        updates = config.get("updates") or context.get("world_updates")

        if self._batch_processor:
            # Use batched processing
            async def wba_processor(message):
                return (
                    await self.enhanced_coordinator.wba_adapter.process_world_request(
                        message["world_id"], message.get("updates")
                    )
                )

            result = await self._batch_processor.add_message(
                {"world_id": world_id, "updates": updates}, wba_processor
            )
        else:
            # Direct processing
            result = await self.enhanced_coordinator.wba_adapter.process_world_request(
                world_id, updates
            )

        return {"wba_result": result, "step_type": "wba"}

    async def _execute_nga_step(
        self, config: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute NGA step with batching support."""
        prompt = config.get("prompt") or context.get("narrative_prompt", "")
        narrative_context = config.get("context", {})
        narrative_context.update(context)

        if self._batch_processor:
            # Use batched processing
            async def nga_processor(message):
                return await self.enhanced_coordinator.nga_adapter.generate_narrative(
                    message["prompt"], message.get("context", {})
                )

            result = await self._batch_processor.add_message(
                {"prompt": prompt, "context": narrative_context}, nga_processor
            )
        else:
            # Direct processing
            result = await self.enhanced_coordinator.nga_adapter.generate_narrative(
                prompt, narrative_context
            )

        return {"nga_result": result, "step_type": "nga"}

    async def _execute_parallel_steps(
        self, config: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute multiple steps in parallel."""
        parallel_steps = config.get("steps", [])

        tasks = []
        for step in parallel_steps:
            if step.get("type") == "ipa":
                task = self._execute_ipa_step(step.get("config", {}), context)
            elif step.get("type") == "wba":
                task = self._execute_wba_step(step.get("config", {}), context)
            elif step.get("type") == "nga":
                task = self._execute_nga_step(step.get("config", {}), context)
            else:
                continue

            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "parallel_results": results,
            "step_type": "parallel",
            "success": all(not isinstance(r, Exception) for r in results),
        }

    async def _cleanup_workflow(self, workflow_id: str, delay: float = 60.0):
        """Clean up workflow data after delay."""
        await asyncio.sleep(delay)

        async with self._workflow_lock:
            self._active_workflows.pop(workflow_id, None)

    async def get_active_workflows(self) -> dict[str, dict[str, Any]]:
        """Get information about currently active workflows."""
        async with self._workflow_lock:
            return {
                workflow_id: {
                    "status": workflow_data["status"],
                    "start_time": workflow_data["start_time"],
                    "duration": time.time() - workflow_data["start_time"],
                    "steps_count": len(workflow_data["steps"]),
                }
                for workflow_id, workflow_data in self._active_workflows.items()
            }

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        async with self._workflow_lock:
            if workflow_id in self._active_workflows:
                self._active_workflows[workflow_id]["status"] = "cancelled"
                return True
            return False
