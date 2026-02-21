"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Adapters]]
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

# Add tta.prod to Python path for importing real agents
tta_prod_path = Path(__file__).parent.parent.parent / "tta.prod" / "src"
if str(tta_prod_path) not in sys.path:
    sys.path.insert(0, str(tta_prod_path))

try:
    from agents.base import BaseAgent
    from agents.dynamic_agents import WorldBuildingAgent
    from agents.ipa import IntentSchema, process_input
    from agents.narrative_generator import generate_narrative_response
except ImportError as e:
    logging.warning(f"Could not import real agents: {e}. Using fallback implementations.")
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
    """Configuration for retry logic."""

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


async def retry_with_backoff(func: callable, retry_config: RetryConfig, *args, **kwargs) -> Any:
    """
    Execute a function with exponential backoff retry logic.

    Args:
        func: Function to execute
        retry_config: Retry configuration
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        AgentCommunicationError: If all retries are exhausted
    """
    import random

    last_exception = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        except Exception as e:
            last_exception = e

            if attempt == retry_config.max_retries:
                # Final attempt failed
                break

            # Calculate delay with exponential backoff
            delay = min(
                retry_config.base_delay * (retry_config.exponential_base**attempt),
                retry_config.max_delay,
            )

            # Add jitter to prevent thundering herd
            if retry_config.jitter:
                delay *= 0.5 + random.random() * 0.5

            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")

            await asyncio.sleep(delay)

    # All retries exhausted
    raise AgentCommunicationError(
        f"All {retry_config.max_retries + 1} attempts failed. Last error: {last_exception}"
    )


class IPAAdapter:
    """Adapter for communicating with the real Input Processor Agent."""

    def __init__(self, fallback_to_mock: bool = True, retry_config: RetryConfig | None = None):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._available = process_input is not None and IntentSchema is not None

    async def process_input(self, text: str) -> dict[str, Any]:
        """
        Process player input using the real IPA implementation.

        Args:
            text: Player input text to process

        Returns:
            Dict containing processed intent and routing information

        Raises:
            AgentCommunicationError: If communication with IPA fails
        """
        if not self._available:
            if self.fallback_to_mock:
                logger.warning("Real IPA not available, using fallback mock implementation")
                return self._mock_process_input(text)
            raise AgentCommunicationError("Real IPA implementation not available")

        try:
            # Run the synchronous IPA function in a thread pool with retry logic
            async def _process_with_executor():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, process_input, text)

            intent_result = await retry_with_backoff(_process_with_executor, self.retry_config)

            # Convert IntentSchema to dict format expected by orchestration system
            if hasattr(intent_result, "dict"):
                intent_dict = intent_result.dict()
            elif hasattr(intent_result, "model_dump"):
                intent_dict = intent_result.model_dump()
            else:
                intent_dict = {"intent": str(intent_result), "confidence": 0.8}

            # Transform to orchestration system format
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

        except Exception as e:
            logger.error(f"Error communicating with real IPA: {e}")
            if self.fallback_to_mock:
                logger.warning("Falling back to mock implementation")
                return self._mock_process_input(text)
            raise AgentCommunicationError(f"IPA communication failed: {e}") from e

    def _mock_process_input(self, text: str) -> dict[str, Any]:
        """Fallback mock implementation for IPA processing."""
        return {
            "normalized_text": text,
            "routing": {"intent": "unknown", "confidence": 0.5},
            "raw_intent": {"intent": "unknown"},
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
    ):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self._available = WorldBuildingAgent is not None
        self._wba_instance = None

        if self._available and neo4j_manager:
            try:
                self._wba_instance = WorldBuildingAgent(neo4j_manager, self.tools)
            except Exception as e:
                logger.warning(f"Failed to initialize WBA instance: {e}")
                self._available = False

    async def process_world_request(
        self, world_id: str, updates: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process world building request using the real WBA implementation.

        Args:
            world_id: ID of the world to process
            updates: Optional updates to apply to the world

        Returns:
            Dict containing world state and processing results

        Raises:
            AgentCommunicationError: If communication with WBA fails
        """
        if not self._available or not self._wba_instance:
            if self.fallback_to_mock:
                logger.warning("Real WBA not available, using fallback mock implementation")
                return self._mock_process_world(world_id, updates)
            raise AgentCommunicationError("Real WBA implementation not available")

        try:
            # Prepare input for WBA
            wba_input = {
                "world_id": world_id,
                "action": "update" if updates else "fetch",
                "updates": updates or {},
            }

            # Run WBA processing in thread pool with retry logic
            async def _process_with_executor():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self._wba_instance.process, wba_input)

            result = await retry_with_backoff(_process_with_executor, self.retry_config)

            # Transform result to orchestration system format
            return {
                "world_id": world_id,
                "world_state": result.get("world_state", {}),
                "updated": updates is not None,
                "cached": False,
                "source": "real_wba",
                "raw_result": result,
            }

        except Exception as e:
            logger.error(f"Error communicating with real WBA: {e}")
            if self.fallback_to_mock:
                logger.warning("Falling back to mock implementation")
                return self._mock_process_world(world_id, updates)
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


class NGAAdapter:
    """Adapter for communicating with the real Narrative Generator Agent."""

    def __init__(self, fallback_to_mock: bool = True, retry_config: RetryConfig | None = None):
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()
        self._available = generate_narrative_response is not None

    async def generate_narrative(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Generate narrative content using the real NGA implementation.

        Args:
            prompt: Narrative generation prompt
            context: Optional context for narrative generation

        Returns:
            Dict containing generated narrative and metadata

        Raises:
            AgentCommunicationError: If communication with NGA fails
        """
        if not self._available:
            if self.fallback_to_mock:
                logger.warning("Real NGA not available, using fallback mock implementation")
                return self._mock_generate_narrative(prompt, context)
            raise AgentCommunicationError("Real NGA implementation not available")

        try:
            # Prepare input for NGA
            nga_input = {
                "prompt": prompt,
                "context": context or {},
                "player_input": prompt,  # NGA expects player_input field
            }

            # Run NGA processing in thread pool with retry logic
            async def _process_with_executor():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, generate_narrative_response, nga_input)

            result = await retry_with_backoff(_process_with_executor, self.retry_config)

            # Transform result to orchestration system format
            story_text = result.get(
                "response",
                result.get("story", f"Generated story for: {prompt[:64]}..."),
            )

            return {
                "story": story_text,
                "raw": story_text,
                "context_used": bool(context),
                "source": "real_nga",
                "raw_result": result,
            }

        except Exception as e:
            logger.error(f"Error communicating with real NGA: {e}")
            if self.fallback_to_mock:
                logger.warning("Falling back to mock implementation")
                return self._mock_generate_narrative(prompt, context)
            raise AgentCommunicationError(f"NGA communication failed: {e}") from e

    def _mock_generate_narrative(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Fallback mock implementation for NGA processing."""
        story = f"Generated story for: {prompt[:64]}..."

        return {
            "story": story,
            "raw": story,
            "context_used": bool(context),
            "source": "mock_fallback",
        }


class AgentAdapterFactory:
    """Factory for creating agent adapters with shared configuration."""

    def __init__(
        self,
        neo4j_manager=None,
        tools: dict[str, Any] | None = None,
        fallback_to_mock: bool = True,
        retry_config: RetryConfig | None = None,
    ):
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self.fallback_to_mock = fallback_to_mock
        self.retry_config = retry_config or RetryConfig()

    def create_ipa_adapter(self) -> IPAAdapter:
        """Create an IPA adapter instance."""
        return IPAAdapter(fallback_to_mock=self.fallback_to_mock, retry_config=self.retry_config)

    def create_wba_adapter(self) -> WBAAdapter:
        """Create a WBA adapter instance."""
        return WBAAdapter(
            neo4j_manager=self.neo4j_manager,
            tools=self.tools,
            fallback_to_mock=self.fallback_to_mock,
            retry_config=self.retry_config,
        )

    def create_nga_adapter(self) -> NGAAdapter:
        """Create an NGA adapter instance."""
        return NGAAdapter(fallback_to_mock=self.fallback_to_mock, retry_config=self.retry_config)
