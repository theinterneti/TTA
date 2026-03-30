"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Unified_orchestrator]]
Unified Agent Orchestrator for IPA → WBA → NGA coordination.

This module provides a high-level orchestrator that coordinates the three main agents
(Input Processing, World Building, and Narrative Generation) with proper state management,
error handling, and persistence.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as aioredis

from .adapters import IPAAdapter, NGAAdapter, RetryConfig, WBAAdapter
from .therapeutic_safety import SafetyLevel, get_global_safety_service

logger = logging.getLogger(__name__)


class OrchestrationPhase(Enum):
    """Phases of the agent orchestration workflow."""

    INPUT_PROCESSING = "input_processing"
    WORLD_BUILDING = "world_building"
    NARRATIVE_GENERATION = "narrative_generation"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class OrchestrationState:
    """State of an orchestration workflow."""

    workflow_id: str
    session_id: str
    player_id: str
    phase: OrchestrationPhase
    user_input: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Phase results
    ipa_result: dict[str, Any] | None = None
    wba_result: dict[str, Any] | None = None
    nga_result: dict[str, Any] | None = None

    # Context and metadata
    world_context: dict[str, Any] = field(default_factory=dict)
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    safety_level: SafetyLevel = SafetyLevel.SAFE
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "workflow_id": self.workflow_id,
            "session_id": self.session_id,
            "player_id": self.player_id,
            "phase": self.phase.value,
            "user_input": self.user_input,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ipa_result": self.ipa_result,
            "wba_result": self.wba_result,
            "nga_result": self.nga_result,
            "world_context": self.world_context,
            "therapeutic_context": self.therapeutic_context,
            "safety_level": self.safety_level.value,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrchestrationState:
        """Create state from dictionary."""
        return cls(
            workflow_id=data["workflow_id"],
            session_id=data["session_id"],
            player_id=data["player_id"],
            phase=OrchestrationPhase(data["phase"]),
            user_input=data["user_input"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            ipa_result=data.get("ipa_result"),
            wba_result=data.get("wba_result"),
            nga_result=data.get("nga_result"),
            world_context=data.get("world_context", {}),
            therapeutic_context=data.get("therapeutic_context", {}),
            safety_level=SafetyLevel(data.get("safety_level", "safe")),
            error=data.get("error"),
        )


class UnifiedAgentOrchestrator:
    """
    Unified orchestrator for coordinating IPA, WBA, and NGA agents.

    This orchestrator manages the complete workflow:
    1. Input Processing (IPA) - Parse and understand user input
    2. World Building (WBA) - Update world state based on intent
    3. Narrative Generation (NGA) - Generate story response

    Features:
    - State persistence in Redis
    - Safety validation at each step
    - Error handling and recovery
    - Progress tracking
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        neo4j_manager: Any | None = None,
        enable_real_agents: bool = True,
        retry_config: RetryConfig | None = None,
    ):
        """
        Initialize the unified orchestrator.

        Args:
            redis_url: Redis connection URL for state persistence
            neo4j_manager: Neo4j manager for world state (optional)
            enable_real_agents: Whether to use real agent implementations
            retry_config: Retry configuration for agent communication
        """
        self.redis_url = redis_url
        self.neo4j_manager = neo4j_manager
        self.enable_real_agents = enable_real_agents
        self.retry_config = retry_config or RetryConfig()

        # Initialize adapters
        self.ipa_adapter = IPAAdapter(fallback_to_mock=True, retry_config=self.retry_config)
        self.wba_adapter = WBAAdapter(
            neo4j_manager=neo4j_manager,
            fallback_to_mock=True,
            retry_config=self.retry_config,
        )
        self.nga_adapter = NGAAdapter(fallback_to_mock=True, retry_config=self.retry_config)

        # Redis client for state persistence
        self.redis: aioredis.Redis | None = None
        self.safety_service = get_global_safety_service()
        self.initialized = False

    async def initialize(self):
        """Initialize the orchestrator and its dependencies."""
        try:
            # Connect to Redis
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()

            self.initialized = True
            logger.info("Unified Agent Orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    async def close(self):
        """Close connections and cleanup resources."""
        if self.redis:
            await self.redis.close()
        logger.info("Unified Agent Orchestrator closed")

    async def process_user_input(
        self,
        user_input: str,
        session_id: str,
        player_id: str,
        world_context: dict[str, Any] | None = None,
        therapeutic_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process user input through the complete agent workflow.

        Args:
            user_input: The user's input text
            session_id: Session identifier
            player_id: Player identifier
            world_context: Current world state context
            therapeutic_context: Therapeutic session context

        Returns:
            Dict containing the complete workflow result with narrative response
        """
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        # Create workflow state
        workflow_id = str(uuid.uuid4())
        state = OrchestrationState(
            workflow_id=workflow_id,
            session_id=session_id,
            player_id=player_id,
            phase=OrchestrationPhase.INPUT_PROCESSING,
            user_input=user_input,
            world_context=world_context or {},
            therapeutic_context=therapeutic_context or {},
        )

        try:
            # Save initial state
            await self._save_state(state)

            # Phase 1: Input Processing
            logger.info(f"[{workflow_id}] Phase 1: Input Processing")
            state = await self._process_input_phase(state)
            await self._save_state(state)

            # Safety check after input processing
            if state.safety_level in [SafetyLevel.BLOCKED, SafetyLevel.WARNING]:
                logger.warning(
                    f"[{workflow_id}] Safety concern detected: {state.safety_level.value}"
                )
                return await self._handle_safety_concern(state)

            # Phase 2: World Building
            logger.info(f"[{workflow_id}] Phase 2: World Building")
            state = await self._process_world_building_phase(state)
            await self._save_state(state)

            # Phase 3: Narrative Generation
            logger.info(f"[{workflow_id}] Phase 3: Narrative Generation")
            state = await self._process_narrative_phase(state)
            await self._save_state(state)

            # Mark as complete
            state.phase = OrchestrationPhase.COMPLETE
            state.updated_at = datetime.utcnow()
            await self._save_state(state)

            logger.info(f"[{workflow_id}] Workflow completed successfully")

            return {
                "workflow_id": workflow_id,
                "success": True,
                "narrative": state.nga_result.get("story", ""),
                "intent": state.ipa_result.get("routing", {}).get("intent"),
                "world_updates": state.wba_result,
                "safety_level": state.safety_level.value,
                "complete_state": state.to_dict(),
            }

        except Exception as e:
            logger.error(f"[{workflow_id}] Workflow error: {e}", exc_info=True)
            state.phase = OrchestrationPhase.ERROR
            state.error = str(e)
            await self._save_state(state)

            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": str(e),
                "narrative": "I'm having trouble processing that right now. Could you try rephrasing?",
                "safety_level": state.safety_level.value,
            }

    async def _process_input_phase(self, state: OrchestrationState) -> OrchestrationState:
        """Process input through IPA."""
        try:
            # Validate input safety
            safety_result = await self.safety_service.validate_text(state.user_input)
            state.safety_level = safety_result.level

            # Process through IPA
            ipa_result = await self.ipa_adapter.process_input(state.user_input)
            state.ipa_result = ipa_result

            state.phase = OrchestrationPhase.WORLD_BUILDING
            state.updated_at = datetime.utcnow()

            return state

        except Exception as e:
            logger.error(f"Input processing phase error: {e}")
            raise

    async def _process_world_building_phase(self, state: OrchestrationState) -> OrchestrationState:
        """Process world updates through WBA."""
        try:
            # Extract intent and entities from IPA result
            intent = state.ipa_result.get("routing", {}).get("intent", "unknown")
            entities = state.ipa_result.get("routing", {}).get("entities", {})

            # Build world update request
            world_id = state.world_context.get("world_id", state.session_id)
            updates = {
                "intent": intent,
                "entities": entities,
                "player_id": state.player_id,
                "session_id": state.session_id,
            }

            # Process through WBA
            wba_result = await self.wba_adapter.process_world_request(
                world_id=world_id, updates=updates
            )
            state.wba_result = wba_result

            # Update world context with changes
            if wba_result.get("world_state"):
                state.world_context.update(wba_result["world_state"])

            state.phase = OrchestrationPhase.NARRATIVE_GENERATION
            state.updated_at = datetime.utcnow()

            return state

        except Exception as e:
            logger.error(f"World building phase error: {e}")
            raise

    async def _process_narrative_phase(self, state: OrchestrationState) -> OrchestrationState:
        """Generate narrative response through NGA."""
        try:
            # Build narrative generation prompt
            prompt = self._build_narrative_prompt(state)

            # Prepare context for NGA
            nga_context = {
                "world_state": state.world_context,
                "intent": state.ipa_result.get("routing", {}).get("intent"),
                "entities": state.ipa_result.get("routing", {}).get("entities", {}),
                "world_updates": state.wba_result,
                "therapeutic_context": state.therapeutic_context,
                "safety_level": state.safety_level.value,
            }

            # Generate narrative
            nga_result = await self.nga_adapter.generate_narrative(
                prompt=prompt, context=nga_context
            )
            state.nga_result = nga_result

            state.updated_at = datetime.utcnow()

            return state

        except Exception as e:
            logger.error(f"Narrative generation phase error: {e}")
            raise

    def _build_narrative_prompt(self, state: OrchestrationState) -> str:
        """Build a narrative generation prompt from the current state."""
        intent = state.ipa_result.get("routing", {}).get("intent", "unknown")
        world_updates = state.wba_result.get("description", "")

        prompt = f"Player input: {state.user_input}\n"
        prompt += f"Detected intent: {intent}\n"

        if world_updates:
            prompt += f"World changes: {world_updates}\n"

        prompt += "\nGenerate a narrative response that:"
        prompt += "\n- Acknowledges the player's action"
        prompt += "\n- Describes the world changes"
        prompt += "\n- Maintains therapeutic tone"
        prompt += "\n- Encourages continued engagement"

        return prompt

    async def _handle_safety_concern(self, state: OrchestrationState) -> dict[str, Any]:
        """Handle safety concerns detected during processing."""
        logger.warning(
            f"Safety concern in workflow {state.workflow_id}: {state.safety_level.value}"
        )

        # Generate appropriate safety response
        if state.safety_level == SafetyLevel.BLOCKED:
            narrative = (
                "I notice you might be going through a difficult time. "
                "Your wellbeing is important. Would you like to talk about what's on your mind?"
            )
        else:
            narrative = (
                "I want to make sure you're feeling okay. "
                "Let's take a moment to check in. How are you feeling right now?"
            )

        return {
            "workflow_id": state.workflow_id,
            "success": True,
            "narrative": narrative,
            "safety_level": state.safety_level.value,
            "safety_intervention": True,
            "complete_state": state.to_dict(),
        }

    async def _save_state(self, state: OrchestrationState):
        """Save workflow state to Redis."""
        if not self.redis:
            logger.warning("Redis not available, skipping state persistence")
            return

        try:
            key = f"orchestration:workflow:{state.workflow_id}"
            await self.redis.setex(
                key,
                3600,
                json.dumps(state.to_dict()),  # 1 hour TTL
            )

            # Also save by session for retrieval
            session_key = f"orchestration:session:{state.session_id}:latest"
            await self.redis.setex(session_key, 3600, state.workflow_id)

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    async def get_workflow_state(self, workflow_id: str) -> OrchestrationState | None:
        """Retrieve workflow state from Redis."""
        if not self.redis:
            return None

        try:
            key = f"orchestration:workflow:{workflow_id}"
            data = await self.redis.get(key)

            if data:
                return OrchestrationState.from_dict(json.loads(data))

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve state: {e}")
            return None

    async def get_session_latest_workflow(self, session_id: str) -> OrchestrationState | None:
        """Get the latest workflow for a session."""
        if not self.redis:
            return None

        try:
            session_key = f"orchestration:session:{session_id}:latest"
            workflow_id = await self.redis.get(session_key)

            if workflow_id:
                return await self.get_workflow_state(workflow_id)

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve session workflow: {e}")
            return None
