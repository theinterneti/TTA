"""

# Logseq: [[TTA.dev/Agent_orchestration/Adapters]]
Agent communication adapters for bridging orchestration proxies with real agent implementations.

This module provides adapter classes that enable communication between the agent orchestration
system and the actual agent implementations in tta.prod/src/agents/.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from tta_dev_primitives import (
    FallbackPrimitive,
    RetryPrimitive,
    RetryStrategy,
    WorkflowContext,
    WorkflowPrimitive,
)

# Add tta.prod to Python path for importing real agents
tta_prod_path = Path(__file__).parent.parent.parent / "tta.prod" / "src"
if str(tta_prod_path) not in sys.path:
    sys.path.insert(0, str(tta_prod_path))

try:
    from agents.base import BaseAgent  # type: ignore[import]
    from agents.dynamic_agents import WorldBuildingAgent  # type: ignore[import]
    from agents.ipa import IntentSchema, process_input  # type: ignore[import]
    from agents.narrative_generator import (  # type: ignore[import-not-found]
        generate_narrative_response,
    )
except ImportError as e:
    logging.warning(
        f"Could not import real agents: {e}. Using fallback implementations."
    )
    process_input = None
    IntentSchema = None
    generate_narrative_response = None
    WorldBuildingAgent = None
    BaseAgent = None

logger = logging.getLogger(__name__)


class AgentCommunicationError(Exception):
    """Raised when agent communication fails."""

    pass


class RetryConfig:
    """Configuration for retry logic.

    .. deprecated::
        This class now serves as a bridge to TTA.dev ``RetryStrategy``/``RetryPrimitive``
        (see ``IPAAdapter``, ``WBAAdapter``, ``NGAAdapter`` for the migration pattern).
        New code should configure ``RetryStrategy`` directly.  ``RetryConfig`` will be
        removed once all callers are fully migrated.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def _transform_ipa_result(text: str, intent_result: Any) -> dict[str, Any]:
    """Convert raw IPA intent result to orchestration format."""
    if hasattr(intent_result, "model_dump"):
        intent_dict: dict[str, Any] = intent_result.model_dump()
    else:
        intent_dict = {"intent": str(intent_result), "confidence": 0.8}
    return {
        "normalized_text": text,
        "routing": {
            "intent": intent_dict.get("intent", "unknown"),
            "confidence": intent_dict.get("confidence", 0.8),
            "entities": intent_dict.get("entities", {}),
            "direction": intent_dict.get("direction"),
            "object": intent_dict.get("object"),
            "npc": intent_dict.get("npc"),
        },
        "raw_intent": intent_dict,
        "source": "real_ipa",
    }


class _IPACall(WorkflowPrimitive):
    """WorkflowPrimitive that executes the real IPA process_input function."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        text: str = input_data["text"]
        real_fn = input_data["real_fn"]
        loop = asyncio.get_running_loop()
        intent_result = await loop.run_in_executor(None, real_fn, text)
        return _transform_ipa_result(text, intent_result)


class _IPAFallback(WorkflowPrimitive):
    """WorkflowPrimitive that returns the mock IPA response."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        text: str = input_data["text"]
        return {
            "normalized_text": text,
            "routing": {"intent": "unknown", "confidence": 0.5},
            "raw_intent": {"intent": "unknown"},
            "source": "mock_fallback",
        }


class IPAAdapter:
    """Adapter for communicating with the real Input Processor Agent."""

    def __init__(
        self,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._available = process_input is not None and IntentSchema is not None
        self._builder = world_context_builder

    async def process_input(
        self,
        text: str,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process player input using the real IPA implementation.

        Args:
            text:             Player input text to process.
            session_id:       Optional session ID for WorkflowContext observability.
            location_id:      Optional current location (enables world context).
            player_id:        Optional player ID (passed to builder + spans).
            player_character: Optional character dict (tier-6 context).

        Returns:
            Dict containing processed intent and routing information.

        Raises:
            AgentCommunicationError: If communication with IPA fails and
                fallback_to_mock is False.
        """
        ctx = WorkflowContext(workflow_id=session_id or f"ipa-{id(self)}")
        input_data: dict[str, Any] = {"text": text, "real_fn": process_input}

        # Enrich with world context when builder is available
        if self._builder is not None and session_id and location_id:
            try:
                assembled = await self._builder.build(
                    session_id=session_id,
                    location_id=location_id,
                    player_id=player_id or "",
                    player_character=player_character,
                )
                input_data["world_context"] = assembled.text
                input_data["world_context_meta"] = {
                    "total_tokens": assembled.total_tokens,
                    "neo4j_available": assembled.neo4j_available,
                    "truncated_tiers": assembled.truncated_tiers,
                }
                logger.debug(
                    "IPA world context assembled: session=%s tokens=%d",
                    session_id,
                    assembled.total_tokens,
                )
            except Exception as exc:
                logger.warning("IPA: world context build failed: %s", exc)

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        if not self._available:
            if self.fallback_to_mock:
                logger.warning(
                    "Real IPA not available, using fallback mock implementation"
                )
                return self._mock_process_input(text)
            raise AgentCommunicationError("Real IPA implementation not available")

        call: WorkflowPrimitive = _IPACall()
        retry_call = RetryPrimitive(call, strategy=strategy)
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(retry_call, _IPAFallback())
        else:
            primitive = retry_call

        try:
            return await primitive.execute(input_data, ctx)  # type: ignore[return-value]
        except Exception as e:
            raise AgentCommunicationError(f"IPA communication failed: {e}") from e

    def _mock_process_input(self, text: str) -> dict[str, Any]:
        """Fallback mock implementation for IPA processing."""
        return {
            "normalized_text": text,
            "routing": {"intent": "unknown", "confidence": 0.5},
            "raw_intent": {"intent": "unknown"},
            "source": "mock_fallback",
        }


def _transform_wba_result(
    world_id: str, updates: dict[str, Any] | None, raw: dict[str, Any]
) -> dict[str, Any]:
    """Convert raw WBA result to orchestration format."""
    return {
        "world_id": world_id,
        "world_state": raw.get("world_state", {}),
        "updated": updates is not None,
        "cached": False,
        "source": "real_wba",
        "raw_result": raw,
    }


class _WBACall(WorkflowPrimitive):
    """WorkflowPrimitive that executes the real WBA process function."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        wba_instance = input_data["wba_instance"]
        wba_input: dict[str, Any] = input_data["wba_input"]
        world_id: str = input_data["world_id"]
        updates: dict[str, Any] | None = input_data["updates"]

        loop = asyncio.get_running_loop()
        raw: dict[str, Any] = await loop.run_in_executor(
            None,
            wba_instance.process,
            wba_input,  # type: ignore[misc]
        )
        return _transform_wba_result(world_id, updates, raw)


class _WBAFallback(WorkflowPrimitive):
    """WorkflowPrimitive that returns the mock WBA response."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        world_id: str = input_data["world_id"]
        updates: dict[str, Any] | None = input_data["updates"]
        world_state: dict[str, Any] = {"id": world_id, "regions": [], "entities": []}
        if updates:
            world_state.update(updates)
        return {
            "world_id": world_id,
            "world_state": world_state,
            "updated": updates is not None,
            "cached": False,
            "source": "mock_fallback",
        }


class WBAAdapter:
    """Adapter for communicating with the real World Builder Agent."""

    def __init__(
        self,
        neo4j_manager=None,
        tools: dict[str, Any] | None = None,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self._available = WorldBuildingAgent is not None
        self._wba_instance = None
        self._builder = world_context_builder

        if self._available and neo4j_manager:
            try:
                self._wba_instance = WorldBuildingAgent(neo4j_manager, self.tools)  # type: ignore[misc]
            except Exception as e:
                logger.warning(f"Failed to initialize WBA instance: {e}")
                self._available = False

    async def process_world_request(
        self,
        world_id: str,
        updates: dict[str, Any] | None = None,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process world building request using the real WBA implementation.

        Args:
            world_id:         ID of the world to process.
            updates:          Optional updates to apply to the world.
            session_id:       Optional session ID for WorkflowContext observability.
            location_id:      Optional current location (enables world context).
            player_id:        Optional player ID (passed to builder).
            player_character: Optional character dict (tier-6 context).

        Returns:
            Dict containing world state and processing results

        Raises:
            AgentCommunicationError: If communication with WBA fails and
                fallback_to_mock is False
        """
        ctx = WorkflowContext(workflow_id=session_id or f"wba-{id(self)}")
        input_data: dict[str, Any] = {
            "wba_instance": self._wba_instance,
            "wba_input": {
                "world_id": world_id,
                "action": "update" if updates else "fetch",
                "updates": updates or {},
            },
            "world_id": world_id,
            "updates": updates,
        }

        # Enrich with world context when builder is available
        if self._builder is not None and session_id and location_id:
            try:
                assembled = await self._builder.build(
                    session_id=session_id,
                    location_id=location_id,
                    player_id=player_id or "",
                    player_character=player_character,
                )
                input_data["world_context"] = assembled.text
                input_data["world_context_meta"] = {
                    "total_tokens": assembled.total_tokens,
                    "neo4j_available": assembled.neo4j_available,
                    "truncated_tiers": assembled.truncated_tiers,
                }
                logger.debug(
                    "WBA world context assembled: session=%s tokens=%d",
                    session_id,
                    assembled.total_tokens,
                )
            except Exception as exc:
                logger.warning("WBA: world context build failed: %s", exc)

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        if not self._available or not self._wba_instance:
            if self.fallback_to_mock:
                logger.warning(
                    "Real WBA not available, using fallback mock implementation"
                )
                return self._mock_process_world(world_id, updates)
            raise AgentCommunicationError("Real WBA implementation not available")

        call: WorkflowPrimitive = _WBACall()
        retry_call = RetryPrimitive(call, strategy=strategy)
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(retry_call, _WBAFallback())
        else:
            primitive = retry_call

        try:
            return await primitive.execute(input_data, ctx)  # type: ignore[return-value]
        except Exception as e:
            raise AgentCommunicationError(f"WBA communication failed: {e}") from e

    def _mock_process_world(
        self, world_id: str, updates: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Fallback mock implementation for WBA processing."""
        world_state = {"id": world_id, "regions": [], "entities": []}
        if updates:
            world_state.update(updates)

        return {
            "world_id": world_id,
            "world_state": world_state,
            "updated": updates is not None,
            "cached": False,
            "source": "mock_fallback",
        }


def _transform_nga_result(
    prompt: str, context: dict[str, Any] | None, raw: dict[str, Any]
) -> dict[str, Any]:
    """Convert raw NGA result to orchestration format."""
    story_text = raw.get(
        "response",
        raw.get("story", f"Generated story for: {prompt[:64]}..."),
    )
    return {
        "story": story_text,
        "raw": story_text,
        "context_used": bool(context),
        "source": "real_nga",
        "raw_result": raw,
    }


class _NGACall(WorkflowPrimitive):
    """WorkflowPrimitive that executes the real NGA generate_narrative_response function."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        nga_input: dict[str, Any] = input_data["nga_input"]
        prompt: str = input_data["prompt"]
        ctx_data: dict[str, Any] | None = input_data["context"]
        real_fn = input_data["real_fn"]
        loop = asyncio.get_running_loop()
        raw: dict[str, Any] = await loop.run_in_executor(None, real_fn, nga_input)
        return _transform_nga_result(prompt, ctx_data, raw)


class _NGAFallback(WorkflowPrimitive):
    """WorkflowPrimitive that returns the mock NGA response."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        prompt: str = input_data["prompt"]
        ctx_data: dict[str, Any] | None = input_data["context"]
        world_context_meta: dict[str, Any] = input_data.get("world_context_meta", {})
        story = f"Generated story for: {prompt[:64]}..."
        result: dict[str, Any] = {
            "story": story,
            "raw": story,
            "context_used": bool(ctx_data),
            "source": "mock_fallback",
        }
        if world_context_meta:
            result["world_context_meta"] = world_context_meta
        return result


class NGAAdapter:
    """Adapter for communicating with the real Narrative Generator Agent."""

    def __init__(
        self,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._available = generate_narrative_response is not None
        self._builder = world_context_builder

    async def generate_narrative(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate narrative content using the real NGA implementation.

        Args:
            prompt:           Narrative generation prompt.
            context:          Optional context for narrative generation.
            session_id:       Optional session ID for world context assembly.
            location_id:      Optional current location (enables world context).
            player_id:        Optional player ID (passed to builder).
            player_character: Optional character dict (tier-6 context).

        Returns:
            Dict containing generated narrative and metadata

        Raises:
            AgentCommunicationError: If communication with NGA fails
        """
        # Enrich prompt with world context when builder is available
        world_context_text: str = ""
        world_context_meta: dict[str, Any] = {}
        if self._builder is not None and session_id and location_id:
            try:
                assembled = await self._builder.build(
                    session_id=session_id,
                    location_id=location_id,
                    player_id=player_id or "",
                    player_character=player_character,
                )
                world_context_text = assembled.text
                world_context_meta = {
                    "total_tokens": assembled.total_tokens,
                    "neo4j_available": assembled.neo4j_available,
                    "truncated_tiers": assembled.truncated_tiers,
                }
                logger.debug(
                    "NGA world context assembled: session=%s tokens=%d",
                    session_id,
                    assembled.total_tokens,
                )
            except Exception as exc:
                logger.warning("NGA: world context build failed: %s", exc)

        ctx = WorkflowContext(workflow_id=session_id or f"nga-{id(self)}")
        nga_input: dict[str, Any] = {
            "prompt": prompt,
            "context": context or {},
            "player_input": prompt,  # NGA expects player_input field
        }
        if world_context_text:
            nga_input["world_context"] = world_context_text
            nga_input["world_context_meta"] = world_context_meta

        input_data: dict[str, Any] = {
            "nga_input": nga_input,
            "prompt": prompt,
            "context": context,
            "real_fn": generate_narrative_response,
            "world_context_meta": world_context_meta,
        }

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        if not self._available:
            if self.fallback_to_mock:
                logger.warning(
                    "Real NGA not available, using fallback mock implementation"
                )
                return self._mock_generate_narrative(
                    prompt, context, world_context_meta
                )
            raise AgentCommunicationError("Real NGA implementation not available")

        call: WorkflowPrimitive = _NGACall()
        retry_call = RetryPrimitive(call, strategy=strategy)
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(retry_call, _NGAFallback())
        else:
            primitive = retry_call

        try:
            return await primitive.execute(input_data, ctx)  # type: ignore[return-value]
        except Exception as e:
            raise AgentCommunicationError(f"NGA communication failed: {e}") from e

    def _mock_generate_narrative(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        world_context_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Fallback mock implementation for NGA processing."""
        story = f"Generated story for: {prompt[:64]}..."

        result: dict[str, Any] = {
            "story": story,
            "raw": story,
            "context_used": bool(context),
            "source": "mock_fallback",
        }
        if world_context_meta:
            result["world_context_meta"] = world_context_meta
        return result


class AgentAdapterFactory:
    """Factory for creating agent adapters with shared configuration."""

    def __init__(
        self,
        neo4j_manager=None,
        tools: dict[str, Any] | None = None,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
    ):
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self.world_context_builder = world_context_builder

    def create_ipa_adapter(self) -> IPAAdapter:
        """Create an IPA adapter instance."""
        return IPAAdapter(
            fallback_to_mock=self.fallback_to_mock,
            retry_config=self.retry_config,
            world_context_builder=self.world_context_builder,
        )

    def create_wba_adapter(self) -> WBAAdapter:
        """Create a WBA adapter instance."""
        return WBAAdapter(
            neo4j_manager=self.neo4j_manager,
            tools=self.tools,
            fallback_to_mock=self.fallback_to_mock,
            retry_config=self.retry_config,
            world_context_builder=self.world_context_builder,
        )

    def create_nga_adapter(self) -> NGAAdapter:
        """Create an NGA adapter instance."""
        return NGAAdapter(
            fallback_to_mock=self.fallback_to_mock,
            retry_config=self.retry_config,
            world_context_builder=self.world_context_builder,
        )
