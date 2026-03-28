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

