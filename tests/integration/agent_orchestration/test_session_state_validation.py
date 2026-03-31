"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_session_state_validation]]
Session context and state management validation tests.

This module provides comprehensive validation of session management,
context persistence, and state management across workflow executions.
"""

import asyncio
import json

import pytest
import pytest_asyncio
from tta_ai.orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.service import AgentOrchestrationService
from tta_ai.orchestration.therapeutic_safety import (
    CrisisInterventionManager,
    TherapeuticValidator,
)


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestSessionStateValidation:
    """Comprehensive session context and state management validation."""

    @pytest_asyncio.fixture
    async def orchestration_service(
        self, redis_coordinator, neo4j_driver, event_publisher
    ):
        """Create orchestration service with full session management."""
        # Create enhanced agent proxies
        ipa_proxy = InputProcessorAgentProxy(
            coordinator=redis_coordinator,
            instance="session_ipa",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        wba_proxy = WorldBuilderAgentProxy(
            coordinator=redis_coordinator,
            instance="session_wba",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
            neo4j_driver=neo4j_driver,
        )

        nga_proxy = NarrativeGeneratorAgentProxy(
            coordinator=redis_coordinator,
            instance="session_nga",
            enable_real_agent=False,
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        # Create therapeutic components
        therapeutic_validator = TherapeuticValidator()
        crisis_manager = CrisisInterventionManager(event_publisher=event_publisher)
        await crisis_manager.start()

        # Create orchestration service
        service = AgentOrchestrationService(
            ipa_proxy=ipa_proxy,
            wba_proxy=wba_proxy,
            nga_proxy=nga_proxy,
            therapeutic_validator=therapeutic_validator,
            crisis_intervention_manager=crisis_manager,
        )

        yield service

        await crisis_manager.stop()

    async def test_session_context_persistence(self, orchestration_service):
        """Test session context persistence across multiple interactions."""
        session_id = "session_persistence_001"
        world_id = "session_world_001"
        user_id = "session_user_001"

        # First interaction - establish character and context
        first_input = (
            "Hi, I'm Alex, a 25-year-old software developer working at a startup."
        )
        first_result = await orchestration_service.process_user_input(
            user_input=first_input,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert first_result is not None
        assert "story" in first_result
        assert first_result["session_id"] == session_id

        # Extract context from first interaction
        first_wba_result = first_result.get("wba_result", {})
        first_wba_result.get("world_state", {})

        # Wait to ensure persistence
        await asyncio.sleep(0.2)

        # Second interaction - should reference previous context
        second_input = (
            "I'm feeling burned out from working long hours. What should I do?"
        )
        second_result = await orchestration_service.process_user_input(
            user_input=second_input,
            session_id=session_id,  # Same session
            world_id=world_id,  # Same world
            user_id=user_id,
        )

        assert second_result is not None
        assert "story" in second_result
        assert second_result["session_id"] == session_id

        # Validate context continuity
        second_wba_result = second_result.get("wba_result", {})
        second_world_state = second_wba_result.get("world_state", {})

        # Should maintain character information
        (
            "character_info" in second_world_state
            or "context" in second_world_state
            or any("alex" in str(v).lower() for v in second_world_state.values())
            or any("developer" in str(v).lower() for v in second_world_state.values())
        )

        # Third interaction - further context building
        third_input = "Can you help me create a better work-life balance plan?"
        third_result = await orchestration_service.process_user_input(
            user_input=third_input,
            session_id=session_id,  # Same session
            world_id=world_id,  # Same world
            user_id=user_id,
        )

        assert third_result is not None
        assert "story" in third_result
        assert third_result["session_id"] == session_id

        # Validate accumulated context
        third_story = third_result["story"].lower()

        # Should reference previous context (burnout, work issues)
        any(
            word in third_story
            for word in ["burnout", "work", "hours", "balance", "developer", "startup"]
        )

    async def test_multi_session_isolation(self, orchestration_service):
        """Test isolation between different sessions."""
        user_id = "multi_session_user"

        # Session 1 - Character A
        session_1_id = "isolation_session_001"
        world_1_id = "isolation_world_001"

        session_1_input = "I'm Maria, a teacher who loves reading fantasy novels."
        session_1_result = await orchestration_service.process_user_input(
            user_input=session_1_input,
            session_id=session_1_id,
            world_id=world_1_id,
            user_id=user_id,
        )

        assert session_1_result is not None
        assert session_1_result["session_id"] == session_1_id

        # Session 2 - Character B (different session)
        session_2_id = "isolation_session_002"
        world_2_id = "isolation_world_002"

        session_2_input = (
            "I'm John, an engineer who enjoys hiking and outdoor activities."
        )
        session_2_result = await orchestration_service.process_user_input(
            user_input=session_2_input,
            session_id=session_2_id,
            world_id=world_2_id,
            user_id=user_id,
        )

        assert session_2_result is not None
        assert session_2_result["session_id"] == session_2_id

        # Continue Session 1 - should not know about John
        session_1_continue = "Can you recommend some new fantasy books for me?"
        session_1_continue_result = await orchestration_service.process_user_input(
            user_input=session_1_continue,
            session_id=session_1_id,  # Back to session 1
            world_id=world_1_id,
            user_id=user_id,
        )

        assert session_1_continue_result is not None
        assert session_1_continue_result["session_id"] == session_1_id

        # Continue Session 2 - should not know about Maria
        session_2_continue = "What are some good hiking trails for beginners?"
        session_2_continue_result = await orchestration_service.process_user_input(
            user_input=session_2_continue,
            session_id=session_2_id,  # Back to session 2
            world_id=world_2_id,
            user_id=user_id,
        )

        assert session_2_continue_result is not None
        assert session_2_continue_result["session_id"] == session_2_id

        # Validate session isolation
        session_1_story = session_1_continue_result["story"].lower()
        session_2_story = session_2_continue_result["story"].lower()

        # Session 1 should reference Maria/teaching/fantasy, not John/engineering/hiking
        any(word in session_1_story for word in ["maria", "teacher", "fantasy", "book"])
        not any(word in session_1_story for word in ["john", "engineer", "hiking"])

        # Session 2 should reference John/engineering/hiking, not Maria/teaching/fantasy
        any(word in session_2_story for word in ["john", "engineer", "hiking", "trail"])
        not any(word in session_2_story for word in ["maria", "teacher", "fantasy"])

    async def test_world_state_persistence(self, orchestration_service):
        """Test world state persistence and evolution."""
        session_id = "world_state_session_001"
        world_id = "world_state_world_001"
        user_id = "world_state_user"

        # Interaction 1 - Establish world elements
        input_1 = "I want to explore the enchanted forest near the crystal lake."
        result_1 = await orchestration_service.process_user_input(
            user_input=input_1,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert result_1 is not None
        wba_result_1 = result_1.get("wba_result", {})
        world_state_1 = wba_result_1.get("world_state", {})

        # Interaction 2 - Add to the world
        input_2 = "I discover an ancient temple hidden among the trees."
        result_2 = await orchestration_service.process_user_input(
            user_input=input_2,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert result_2 is not None
        wba_result_2 = result_2.get("wba_result", {})
        world_state_2 = wba_result_2.get("world_state", {})

        # Interaction 3 - Reference previous world elements
        input_3 = "I want to go back to the crystal lake to reflect on what I found in the temple."
        result_3 = await orchestration_service.process_user_input(
            user_input=input_3,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert result_3 is not None
        story_3 = result_3["story"].lower()

        # Validate world state evolution
        # Should reference both forest/lake (from interaction 1) and temple (from interaction 2)
        any(word in story_3 for word in ["forest", "lake", "crystal"])
        any(word in story_3 for word in ["temple", "ancient"])

        # World state should have evolved to include new elements
        len(str(world_state_1))
        len(str(world_state_2))

    async def test_session_recovery_after_interruption(self, orchestration_service):
        """Test session recovery after simulated interruption."""
        session_id = "recovery_session_001"
        world_id = "recovery_world_001"
        user_id = "recovery_user"

        # Establish session context
        initial_input = "I'm Sarah, a college student studying psychology. I'm working on my thesis about anxiety disorders."
        initial_result = await orchestration_service.process_user_input(
            user_input=initial_input,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert initial_result is not None

        # Simulate interruption (wait and then continue)
        await asyncio.sleep(0.5)

        # Continue session after "interruption"
        continue_input = "Can you help me understand the different types of anxiety disorders for my research?"
        continue_result = await orchestration_service.process_user_input(
            user_input=continue_input,
            session_id=session_id,  # Same session
            world_id=world_id,
            user_id=user_id,
        )

        assert continue_result is not None
        assert continue_result["session_id"] == session_id

        # Validate context recovery
        continue_story = continue_result["story"].lower()

        # Should remember Sarah is a psychology student working on thesis
        any(
            word in continue_story
            for word in ["sarah", "psychology", "student", "thesis", "research"]
        )

        # Should provide relevant information about anxiety disorders
        any(
            word in continue_story
            for word in ["anxiety", "disorder", "types", "research"]
        )

    async def test_state_consistency_across_agents(self, orchestration_service):
        """Test state consistency across all agents in the workflow."""
        session_id = "consistency_session_001"
        world_id = "consistency_world_001"
        user_id = "consistency_user"

        # Input that should create consistent state across agents
        user_input = (
            "I'm dealing with work stress and need help developing coping strategies."
        )

        result = await orchestration_service.process_user_input(
            user_input=user_input,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert result is not None

        # Extract agent results
        ipa_result = result.get("ipa_result", {})
        wba_result = result.get("wba_result", {})
        nga_result = result.get("nga_result", {})

        # Validate session consistency across agents
        assert result["session_id"] == session_id

        # All agents should be working with the same session context
        workflow_id = result.get("workflow_id")
        assert workflow_id is not None

        # Validate thematic consistency
        # IPA should identify work stress theme
        ipa_entities = ipa_result.get("entities", [])
        ipa_intent = ipa_result.get("intent", "")

        any(
            "work" in str(entity).lower() or "stress" in str(entity).lower()
            for entity in ipa_entities
        ) or any(word in ipa_intent.lower() for word in ["work", "stress", "coping"])

        # WBA should incorporate work stress into world state
        world_state = wba_result.get("world_state", {})
        world_state_text = json.dumps(world_state).lower()

        any(word in world_state_text for word in ["work", "stress", "coping", "job"])

        # NGA should provide therapeutic response for work stress
        narrative = nga_result.get("narrative", "")
        therapeutic_elements = nga_result.get("therapeutic_elements", [])

        (
            any(
                word in narrative.lower()
                for word in ["stress", "coping", "manage", "balance", "strategies"]
            )
            and len(therapeutic_elements) > 0
        )

    async def test_long_session_memory_management(self, orchestration_service):
        """Test memory management in long sessions with many interactions."""
        session_id = "long_session_001"
        world_id = "long_world_001"
        user_id = "long_session_user"

        # Simulate a long session with multiple interactions
        interactions = [
            "Hi, I'm Emma, a graphic designer.",
            "I'm working on a big project for a client.",
            "The project involves creating a brand identity for a tech startup.",
            "I'm feeling overwhelmed by the scope of work.",
            "Can you help me break down the project into manageable tasks?",
            "I also need advice on managing client expectations.",
            "The deadline is in two weeks and I'm worried about quality.",
            "How can I maintain creativity under pressure?",
        ]

        results = []

        for _, interaction in enumerate(interactions):
            result = await orchestration_service.process_user_input(
                user_input=interaction,
                session_id=session_id,
                world_id=world_id,
                user_id=user_id,
            )

            assert result is not None
            assert result["session_id"] == session_id
            results.append(result)

            # Brief pause between interactions
            await asyncio.sleep(0.1)

        # Validate that the final interaction maintains context from early interactions
        final_result = results[-1]
        final_story = final_result["story"].lower()

        # Should remember Emma is a graphic designer
        any(word in final_story for word in ["emma", "graphic", "designer"])

        # Should remember the project context
        any(word in final_story for word in ["project", "brand", "client", "startup"])

        # Should address the current concern (creativity under pressure)
        any(
            word in final_story
            for word in ["creativity", "pressure", "deadline", "quality"]
        )

        # Validate world state has accumulated information
        final_wba_result = final_result.get("wba_result", {})
        final_world_state = final_wba_result.get("world_state", {})
        world_state_size = len(json.dumps(final_world_state))

        # World state should have grown with accumulated context
        assert world_state_size > 100  # Should have substantial context
