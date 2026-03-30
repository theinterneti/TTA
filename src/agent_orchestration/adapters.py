"""

# Logseq: [[TTA.dev/Agent_orchestration/Adapters]]
Agent communication adapters for bridging orchestration proxies with real agent implementations.

This module provides adapter classes that delegate to the native IPA/WBA/NGA agents
in ``src.components.ipa``, ``src.components.wba``, and ``src.components.nga``.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from ttadev.primitives import (
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )
    from ttadev.primitives.observability import ObservablePrimitive
except ImportError:
    from tta_dev_primitives import (  # type: ignore[no-redef]
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )
    from tta_dev_primitives.observability import (
        ObservablePrimitive,  # type: ignore[no-redef]
    )
from ttadev.primitives.recovery.circuit_breaker_primitive import (
    CircuitBreakerConfig,
    CircuitBreakerPrimitive,
)

from src.components.ipa.agent import IPAAgent as _NativeIPA
from src.components.ipa.models import ProcessedInput
from src.components.nga.agent import NGAAgent as _NativeNGA
from src.components.wba.agent import WBAAgent as _NativeWBA
from src.components.world_context.models import WorldContext

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


def _transform_ipa_result(text: str, result: ProcessedInput) -> dict[str, Any]:
    """Convert a ProcessedInput to the legacy orchestration dict format."""
    return {
        "normalized_text": result.normalized_text,
        "routing": {
            "intent": result.intent.value,
            "confidence": result.intent_confidence,
            "entities": {e.name: e.entity_type for e in result.entities},
            "npc": result.npc_names[0] if result.npc_names else None,
        },
        "raw_intent": result.model_dump(),
        "source": "native_ipa",
        "processed_input": result,
    }


class _IPACall(WorkflowPrimitive):  # type: ignore[misc]
    """WorkflowPrimitive that executes the native IPAAgent."""

    def __init__(self, agent: _NativeIPA) -> None:
        self._agent = agent

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        text: str = input_data["text"]
        session_id: str = input_data.get("session_id", "")
        player_id: str = input_data.get("player_id", "")
        location_id: str | None = input_data.get("location_id")
        result: ProcessedInput = await self._agent.process(
            raw_text=text,
            session_id=session_id,
            player_id=player_id,
            location_id=location_id,
        )
        return _transform_ipa_result(text, result)


class _IPAFallback(WorkflowPrimitive):  # type: ignore[misc]
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
    """Adapter for communicating with the Input Processing Agent."""

    def __init__(
        self,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
        cb_config: CircuitBreakerConfig | None = None,
        ipa_agent: _NativeIPA | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._builder = world_context_builder
        self._cb_config = cb_config or CircuitBreakerConfig()
        self._agent = ipa_agent or _NativeIPA()

    async def process_input(
        self,
        text: str,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process player input using the native IPA implementation.

        Args:
            text:             Player input text to process.
            session_id:       Optional session ID for WorkflowContext observability.
            location_id:      Optional current location (enables world context).
            player_id:        Optional player ID (passed to builder + spans).
            player_character: Optional character dict (tier-6 context).

        Returns:
            Dict containing processed intent and routing information.

        Raises:
            AgentCommunicationError: If the IPA fails and fallback_to_mock is False.
        """
        ctx = WorkflowContext(workflow_id=session_id or f"ipa-{id(self)}")
        input_data: dict[str, Any] = {
            "text": text,
            "session_id": session_id or "",
            "player_id": player_id or "",
            "location_id": location_id,
        }

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        call: WorkflowPrimitive = _IPACall(self._agent)
        retry_call = RetryPrimitive(call, strategy=strategy)  # type: ignore[arg-type]
        circuit_call = CircuitBreakerPrimitive(retry_call, config=self._cb_config)  # type: ignore[arg-type]
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(circuit_call, _IPAFallback())  # type: ignore[arg-type]
        else:
            primitive = circuit_call  # type: ignore[assignment]
        primitive = ObservablePrimitive(primitive, "ipa_processing")  # type: ignore[assignment, arg-type]

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
    world_id: str, updates: dict[str, Any] | None, world_context: WorldContext
) -> dict[str, Any]:
    """Convert a WorldContext to the legacy orchestration dict format."""
    return {
        "world_id": world_id,
        "world_state": {
            "id": world_id,
            "location": world_context.location.model_dump(),
            "npcs": [n.model_dump() for n in world_context.npcs],
            "active_events": [e.model_dump() for e in world_context.active_events],
        },
        "updated": updates is not None,
        "cached": False,
        "source": "native_wba",
        "world_context": world_context,
    }


class _WBACall(WorkflowPrimitive):  # type: ignore[misc]
    """WorkflowPrimitive that executes the native WBAAgent."""

    def __init__(self, agent: _NativeWBA) -> None:
        self._agent = agent

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        world_id: str = input_data["world_id"]
        updates: dict[str, Any] | None = input_data["updates"]
        processed_input: ProcessedInput = input_data["processed_input"]
        world_context: WorldContext = await self._agent.build(processed_input)
        return _transform_wba_result(world_id, updates, world_context)


class _WBAFallback(WorkflowPrimitive):  # type: ignore[misc]
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
    """Adapter for the World Building Agent."""

    def __init__(
        self,
        neo4j_manager: Any = None,
        tools: dict[str, Any] | None = None,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
        cb_config: CircuitBreakerConfig | None = None,
        wba_agent: _NativeWBA | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self._builder = world_context_builder
        self._cb_config = cb_config or CircuitBreakerConfig()
        self._agent = wba_agent or _NativeWBA(builder=world_context_builder)

    async def process_world_request(
        self,
        world_id: str,
        updates: dict[str, Any] | None = None,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process world building request using the native WBA implementation.

        Args:
            world_id:         ID of the world to process.
            updates:          Optional updates to apply to the world.
            session_id:       Optional session ID for WorkflowContext observability.
            location_id:      Optional current location (enables world context).
            player_id:        Optional player ID.
            player_character: Optional character dict (tier-6 context).

        Returns:
            Dict containing world state and processing results

        Raises:
            AgentCommunicationError: If the WBA fails and fallback_to_mock is False.
        """
        ctx = WorkflowContext(workflow_id=session_id or f"wba-{id(self)}")

        # Build a minimal ProcessedInput so WBAAgent.build() has the context it needs
        processed_input = ProcessedInput(
            raw_text="",
            normalized_text="",
            session_id=session_id or "",
            player_id=player_id or "",
            location_id=location_id,
        )

        input_data: dict[str, Any] = {
            "world_id": world_id,
            "updates": updates,
            "processed_input": processed_input,
        }

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        call: WorkflowPrimitive = _WBACall(self._agent)
        retry_call = RetryPrimitive(call, strategy=strategy)  # type: ignore[arg-type]
        circuit_call = CircuitBreakerPrimitive(retry_call, config=self._cb_config)  # type: ignore[arg-type]
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(circuit_call, _WBAFallback())  # type: ignore[arg-type]
        else:
            primitive = circuit_call  # type: ignore[assignment]
        primitive = ObservablePrimitive(primitive, "wba_processing")  # type: ignore[assignment, arg-type]

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
    prompt: str, context: dict[str, Any] | None, narrative: str
) -> dict[str, Any]:
    """Convert a narrative string to the legacy orchestration dict format."""
    return {
        "story": narrative,
        "raw": narrative,
        "context_used": bool(context),
        "source": "native_nga",
    }


class _NGACall(WorkflowPrimitive):  # type: ignore[misc]
    """WorkflowPrimitive that executes the native NGAAgent."""

    def __init__(self, agent: _NativeNGA) -> None:
        self._agent = agent

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        prompt: str = input_data["prompt"]
        ctx_data: dict[str, Any] | None = input_data["context"]
        processed_input: ProcessedInput = input_data["processed_input"]
        world_context: WorldContext = input_data["world_context"]
        narrative = await self._agent.generate(processed_input, world_context)
        return _transform_nga_result(prompt, ctx_data, narrative)


class _NGAFallback(WorkflowPrimitive):  # type: ignore[misc]
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
    """Adapter for the Narrative Generation Agent."""

    def __init__(
        self,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
        world_context_builder: Any | None = None,
        cb_config: CircuitBreakerConfig | None = None,
        nga_agent: _NativeNGA | None = None,
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._builder = world_context_builder
        self._cb_config = cb_config or CircuitBreakerConfig()
        self._agent = nga_agent or _NativeNGA()

    async def generate_narrative(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        session_id: str | None = None,
        location_id: str | None = None,
        player_id: str | None = None,
        player_character: dict[str, Any] | None = None,
        processed_input: ProcessedInput | None = None,
        world_context: WorldContext | None = None,
    ) -> dict[str, Any]:
        """Generate narrative content using the native NGA implementation.

        Args:
            prompt:           Narrative generation prompt / player input text.
            context:          Optional context dict for downstream use.
            session_id:       Optional session ID for WorkflowContext observability.
            location_id:      Optional current location (used to build world context).
            player_id:        Optional player ID.
            player_character: Optional character dict (tier-6 context).
            processed_input:  Pre-built ProcessedInput (skips IPA reconstruction).
            world_context:    Pre-built WorldContext (skips WBA call).

        Returns:
            Dict containing generated narrative and metadata.

        Raises:
            AgentCommunicationError: If the NGA fails and fallback_to_mock is False.
        """
        ctx = WorkflowContext(workflow_id=session_id or f"nga-{id(self)}")

        # Build ProcessedInput stub if not pre-supplied
        if processed_input is None:
            processed_input = ProcessedInput(
                raw_text=prompt,
                normalized_text=prompt.lower().strip(),
                session_id=session_id or "",
                player_id=player_id or "",
                location_id=location_id,
            )

        # Build WorldContext stub if not pre-supplied
        if world_context is None:
            from src.components.wba.agent import _minimal_world_context

            world_context = _minimal_world_context(location_id or "unknown")

        input_data: dict[str, Any] = {
            "prompt": prompt,
            "context": context,
            "processed_input": processed_input,
            "world_context": world_context,
        }

        strategy = RetryStrategy(
            max_retries=self.retry_config.max_retries,
            backoff_base=self.retry_config.base_delay,
            max_backoff=self.retry_config.max_delay,
            jitter=self.retry_config.jitter,
        )

        call: WorkflowPrimitive = _NGACall(self._agent)
        retry_call = RetryPrimitive(call, strategy=strategy)  # type: ignore[arg-type]
        circuit_call = CircuitBreakerPrimitive(retry_call, config=self._cb_config)  # type: ignore[arg-type]
        primitive: WorkflowPrimitive
        if self.fallback_to_mock:
            primitive = FallbackPrimitive(circuit_call, _NGAFallback())  # type: ignore[arg-type]
        else:
            primitive = circuit_call  # type: ignore[assignment]
        primitive = ObservablePrimitive(primitive, "nga_processing")  # type: ignore[assignment, arg-type]

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
