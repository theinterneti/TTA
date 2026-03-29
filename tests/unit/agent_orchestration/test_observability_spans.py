"""Tests for IPA/WBA/NGA ObservablePrimitive wrapping (#310, #311, #312)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.agent_orchestration.adapters import IPAAdapter, NGAAdapter, WBAAdapter


# ---------------------------------------------------------------------------
# IPA observability (#310)
# ---------------------------------------------------------------------------


class TestIPAObservabilitySpan:
    """Verify ObservablePrimitive is applied to IPA execution path."""

    @pytest.mark.asyncio
    async def test_ipa_mock_path_executes_successfully(self) -> None:
        """ObservablePrimitive wrapper does not break IPA mock path."""
        adapter = IPAAdapter(fallback_to_mock=True)
        result = await adapter.process_input("explore the forest", session_id="s1")
        assert isinstance(result, dict)
        assert "routing" in result or "normalized_text" in result

    @pytest.mark.asyncio
    async def test_ipa_observable_on_real_path(self) -> None:
        """ObservablePrimitive.execute is called when the real agent is available."""
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = IPAAdapter(fallback_to_mock=True)
        adapter._available = True  # force real path

        captured: list[object] = []
        original_execute = ObservablePrimitive.execute

        async def spy_execute(self_inner: object, input_data: object, ctx: object) -> object:
            captured.append(self_inner)
            return await original_execute(self_inner, input_data, ctx)  # type: ignore[arg-type]

        mock_fn = lambda text: type("R", (), {"intent": "explore", "confidence": 0.9})()

        with patch.object(ObservablePrimitive, "execute", spy_execute):
            # Patch the real_fn used by _IPACall so it doesn't call None
            import src.agent_orchestration.adapters as _m
            with patch.object(_m, "process_input", mock_fn):
                await adapter.process_input("test", session_id="s2")

        assert len(captured) >= 1, "ObservablePrimitive.execute was not called"

    @pytest.mark.asyncio
    async def test_ipa_span_name_on_real_path(self) -> None:
        """IPA span is named 'ipa_processing'."""
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = IPAAdapter(fallback_to_mock=True)
        adapter._available = True

        names: list[str] = []
        original_init = ObservablePrimitive.__init__

        def spy_init(self_inner: ObservablePrimitive, primitive: object, name: str) -> None:
            names.append(name)
            original_init(self_inner, primitive, name)  # type: ignore[arg-type]

        mock_fn = lambda text: type("R", (), {"intent": "explore", "confidence": 0.9})()

        import src.agent_orchestration.adapters as _m
        with patch.object(ObservablePrimitive, "__init__", spy_init), \
             patch.object(_m, "process_input", mock_fn):
            await adapter.process_input("test", session_id="s3")

        assert "ipa_processing" in names


# ---------------------------------------------------------------------------
# WBA observability (#311)
# ---------------------------------------------------------------------------


class TestWBAObservabilitySpan:
    """Verify ObservablePrimitive is applied to WBA execution path."""

    @pytest.mark.asyncio
    async def test_wba_mock_path_executes_successfully(self) -> None:
        """ObservablePrimitive wrapper does not break WBA mock path."""
        adapter = WBAAdapter(fallback_to_mock=True)
        result = await adapter.process_world_request(
            world_id="w1", session_id="s5"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_wba_observable_on_real_path(self) -> None:
        """ObservablePrimitive.execute is called when the real WBA is available."""
        from unittest.mock import MagicMock
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = WBAAdapter(fallback_to_mock=True)
        adapter._available = True

        mock_wba = MagicMock()
        mock_wba.process.return_value = {"world_state": {}, "events": []}
        adapter._wba_instance = mock_wba

        captured: list[object] = []
        original_execute = ObservablePrimitive.execute

        async def spy_execute(self_inner: object, input_data: object, ctx: object) -> object:
            captured.append(self_inner)
            return await original_execute(self_inner, input_data, ctx)  # type: ignore[arg-type]

        with patch.object(ObservablePrimitive, "execute", spy_execute):
            await adapter.process_world_request(world_id="w2", session_id="s6")

        assert len(captured) >= 1

    @pytest.mark.asyncio
    async def test_wba_span_name_on_real_path(self) -> None:
        """WBA span is named 'wba_processing'."""
        from unittest.mock import MagicMock
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = WBAAdapter(fallback_to_mock=True)
        adapter._available = True

        mock_wba = MagicMock()
        mock_wba.process.return_value = {"world_state": {}, "events": []}
        adapter._wba_instance = mock_wba

        names: list[str] = []
        original_init = ObservablePrimitive.__init__

        def spy_init(self_inner: ObservablePrimitive, primitive: object, name: str) -> None:
            names.append(name)
            original_init(self_inner, primitive, name)  # type: ignore[arg-type]

        with patch.object(ObservablePrimitive, "__init__", spy_init):
            await adapter.process_world_request(world_id="w3", session_id="s7")

        assert "wba_processing" in names


# ---------------------------------------------------------------------------
# NGA observability (#312)
# ---------------------------------------------------------------------------


class TestNGAObservabilitySpan:
    """Verify ObservablePrimitive is applied to NGA execution path."""

    @pytest.mark.asyncio
    async def test_nga_mock_path_executes_successfully(self) -> None:
        """ObservablePrimitive wrapper does not break NGA mock path."""
        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative("tell me a story", session_id="s8")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_nga_observable_on_real_path(self) -> None:
        """ObservablePrimitive.execute is called when the real NGA is available."""
        from unittest.mock import MagicMock
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = NGAAdapter(fallback_to_mock=True)
        adapter._available = True

        mock_nga = MagicMock()
        mock_nga.generate.return_value = {"narrative": "Once upon a time..."}
        adapter._nga_instance = mock_nga

        captured: list[object] = []
        original_execute = ObservablePrimitive.execute

        async def spy_execute(self_inner: object, input_data: object, ctx: object) -> object:
            captured.append(self_inner)
            return await original_execute(self_inner, input_data, ctx)  # type: ignore[arg-type]

        with patch.object(ObservablePrimitive, "execute", spy_execute):
            await adapter.generate_narrative("test prompt", session_id="s9")

        assert len(captured) >= 1

    @pytest.mark.asyncio
    async def test_nga_span_name_on_real_path(self) -> None:
        """NGA span is named 'nga_processing'."""
        from unittest.mock import MagicMock
        from tta_dev_primitives.observability import ObservablePrimitive

        adapter = NGAAdapter(fallback_to_mock=True)
        adapter._available = True

        mock_nga = MagicMock()
        mock_nga.generate.return_value = {"narrative": "Once upon a time..."}
        adapter._nga_instance = mock_nga

        names: list[str] = []
        original_init = ObservablePrimitive.__init__

        def spy_init(self_inner: ObservablePrimitive, primitive: object, name: str) -> None:
            names.append(name)
            original_init(self_inner, primitive, name)  # type: ignore[arg-type]

        with patch.object(ObservablePrimitive, "__init__", spy_init):
            await adapter.generate_narrative("test prompt", session_id="s10")

        assert "nga_processing" in names

    @pytest.mark.asyncio
    async def test_nga_mock_result_shape(self) -> None:
        """NGA mock result has expected keys."""
        adapter = NGAAdapter(fallback_to_mock=True)
        result = await adapter.generate_narrative("adventure awaits", session_id="s11")
        assert isinstance(result, dict)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# SequentialPrimitive pipeline (#256)
# ---------------------------------------------------------------------------


class TestPipelineSequentialPrimitive:
    """Verify _build_agent_pipeline returns a correctly structured SequentialPrimitive."""

    # ------------------------------------------------------------------
    # Test 1: pipeline structure and name
    # ------------------------------------------------------------------

    def test_build_agent_pipeline_returns_sequential_with_correct_name(self) -> None:
        """Pipeline is a SequentialPrimitive with 3 steps and the expected name."""
        from tta_dev_primitives import SequentialPrimitive

        from src.agent_orchestration.unified_orchestrator import UnifiedAgentOrchestrator

        # Arrange
        orchestrator = UnifiedAgentOrchestrator()

        # Act
        pipeline = orchestrator._build_agent_pipeline()

        # Assert
        assert isinstance(pipeline, SequentialPrimitive)
        assert len(pipeline.primitives) == 3
        assert pipeline.name == "ipa_wba_nga_pipeline"

    # ------------------------------------------------------------------
    # Test 2: pipeline executes all three steps in order
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_pipeline_executes_all_three_steps(self) -> None:
        """Pipeline executes IPA, WBA, and NGA steps and all results appear in output."""
        from unittest.mock import AsyncMock

        from tta_dev_primitives import WorkflowContext

        from src.agent_orchestration.unified_orchestrator import UnifiedAgentOrchestrator

        # Arrange
        orchestrator = UnifiedAgentOrchestrator()
        ipa_return = {"routing": {"intent": "explore", "entities": {}}}
        wba_return = {"world_state": {"updated": True}}
        nga_return = {"story": "You walk into the forest."}

        with (
            patch.object(orchestrator.ipa_adapter, "process_input", AsyncMock(return_value=ipa_return)),
            patch.object(orchestrator.wba_adapter, "process_world_request", AsyncMock(return_value=wba_return)),
            patch.object(orchestrator.nga_adapter, "generate_narrative", AsyncMock(return_value=nga_return)),
        ):
            pipeline = orchestrator._build_agent_pipeline()
            ctx = WorkflowContext(workflow_id="wf-test-2")
            pipeline_input = {
                "user_input": "explore the forest",
                "session_id": "s-test-2",
                "player_id": "p1",
                "world_context": {},
                "therapeutic_context": {},
                "safety_level": "safe",
                "ipa_result": None,
                "wba_result": None,
                "nga_result": None,
            }

            # Act
            output = await pipeline.execute(pipeline_input, ctx)

        # Assert
        assert output["ipa_result"] == ipa_return
        assert output["wba_result"] == wba_return
        assert output["nga_result"] == nga_return

    # ------------------------------------------------------------------
    # Test 3: IPA result flows into WBA step (intent + entities)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ipa_result_flows_into_wba_step(self) -> None:
        """WBA adapter is called with intent and entities extracted from IPA result."""
        from unittest.mock import AsyncMock, call

        from tta_dev_primitives import WorkflowContext

        from src.agent_orchestration.unified_orchestrator import UnifiedAgentOrchestrator

        # Arrange
        orchestrator = UnifiedAgentOrchestrator()
        ipa_return = {"routing": {"intent": "talk", "entities": {"npc": "merchant"}}}
        wba_return = {"world_state": {}}
        nga_return = {"story": "The merchant greets you."}

        wba_mock = AsyncMock(return_value=wba_return)

        with (
            patch.object(orchestrator.ipa_adapter, "process_input", AsyncMock(return_value=ipa_return)),
            patch.object(orchestrator.wba_adapter, "process_world_request", wba_mock),
            patch.object(orchestrator.nga_adapter, "generate_narrative", AsyncMock(return_value=nga_return)),
        ):
            pipeline = orchestrator._build_agent_pipeline()
            ctx = WorkflowContext(workflow_id="wf-test-3")
            pipeline_input = {
                "user_input": "talk to the merchant",
                "session_id": "s-test-3",
                "player_id": "p1",
                "world_context": {"world_id": "world-1"},
                "therapeutic_context": {},
                "safety_level": "safe",
                "ipa_result": None,
                "wba_result": None,
                "nga_result": None,
            }

            # Act
            await pipeline.execute(pipeline_input, ctx)

        # Assert — WBA was called with the intent and entities from IPA
        wba_mock.assert_awaited_once()
        _, kwargs = wba_mock.call_args
        updates = kwargs.get("updates") or wba_mock.call_args[0][1] if len(wba_mock.call_args[0]) > 1 else kwargs.get("updates", {})
        # Retrieve from keyword args
        called_kwargs = wba_mock.call_args.kwargs
        assert called_kwargs["updates"]["intent"] == "talk"
        assert called_kwargs["updates"]["entities"] == {"npc": "merchant"}

    # ------------------------------------------------------------------
    # Test 4: NGA step receives updated world_context from WBA step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_nga_step_receives_world_context_from_wba(self) -> None:
        """NGA lambda receives a world_state dict that reflects the WBA world_state update."""
        from unittest.mock import AsyncMock

        from tta_dev_primitives import WorkflowContext

        from src.agent_orchestration.unified_orchestrator import UnifiedAgentOrchestrator

        # Arrange
        orchestrator = UnifiedAgentOrchestrator()
        ipa_return = {"routing": {"intent": "rest", "entities": {}}}
        wba_return = {"world_state": {"inn_visited": True, "time": "evening"}}
        nga_return = {"story": "You rest at the inn."}

        captured_nga_context: list[dict] = []

        original_generate = orchestrator.nga_adapter.generate_narrative

        async def spy_generate(prompt: str, context: dict | None = None, session_id: str = "") -> dict:
            if context:
                captured_nga_context.append(dict(context))
            return nga_return

        with (
            patch.object(orchestrator.ipa_adapter, "process_input", AsyncMock(return_value=ipa_return)),
            patch.object(orchestrator.wba_adapter, "process_world_request", AsyncMock(return_value=wba_return)),
            patch.object(orchestrator.nga_adapter, "generate_narrative", spy_generate),
        ):
            pipeline = orchestrator._build_agent_pipeline()
            ctx = WorkflowContext(workflow_id="wf-test-4")
            pipeline_input = {
                "user_input": "rest at the inn",
                "session_id": "s-test-4",
                "player_id": "p1",
                "world_context": {"world_id": "world-1"},
                "therapeutic_context": {},
                "safety_level": "safe",
                "ipa_result": None,
                "wba_result": None,
                "nga_result": None,
            }

            # Act
            await pipeline.execute(pipeline_input, ctx)

        # Assert — NGA context.world_state includes the WBA world_state update
        assert len(captured_nga_context) == 1
        nga_world_state = captured_nga_context[0]["world_state"]
        assert nga_world_state.get("inn_visited") is True
        assert nga_world_state.get("time") == "evening"

    # ------------------------------------------------------------------
    # Test 5: safety concern before pipeline short-circuits (no agent calls)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_safety_blocked_short_circuits_before_pipeline(self) -> None:
        """When safety service returns BLOCKED, no adapter is called and response flags the intervention."""
        from unittest.mock import AsyncMock, MagicMock

        from src.agent_orchestration.therapeutic_safety import SafetyLevel
        from src.agent_orchestration.unified_orchestrator import UnifiedAgentOrchestrator

        # Arrange
        orchestrator = UnifiedAgentOrchestrator()
        orchestrator.initialized = True
        orchestrator.redis = AsyncMock()

        # Build a fake ValidationResult with level=BLOCKED
        fake_safety_result = MagicMock()
        fake_safety_result.level = SafetyLevel.BLOCKED

        ipa_mock = AsyncMock()
        wba_mock = AsyncMock()
        nga_mock = AsyncMock()

        with (
            patch.object(
                orchestrator.safety_service,
                "validate_text",
                AsyncMock(return_value=fake_safety_result),
            ),
            patch.object(orchestrator.ipa_adapter, "process_input", ipa_mock),
            patch.object(orchestrator.wba_adapter, "process_world_request", wba_mock),
            patch.object(orchestrator.nga_adapter, "generate_narrative", nga_mock),
        ):
            # Act
            response = await orchestrator.process_user_input(
                user_input="harmful content",
                session_id="s-test-5",
                player_id="p1",
            )

        # Assert — none of the agent adapters were invoked
        ipa_mock.assert_not_awaited()
        wba_mock.assert_not_awaited()
        nga_mock.assert_not_awaited()

        # Assert — response contains safety_intervention flag
        assert response.get("safety_intervention") is True

