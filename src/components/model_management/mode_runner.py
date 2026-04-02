"""ModeRunner — thin wrapper around TTA.dev ModelRouterPrimitive.

Provides the same .call(mode, prompt, system, tier_override) interface
that TTA uses internally, delegating to the canonical TTA.dev primitive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ttadev.primitives.core.base import WorkflowContext
from ttadev.primitives.llm import ModelRouterPrimitive, ModelRouterRequest

MODES_PATH = Path(__file__).parent / "model_modes.yaml"


class ModeRunner:
    def __init__(self, modes_path: Path = MODES_PATH) -> None:
        self._router = ModelRouterPrimitive.from_yaml(modes_path)

    @property
    def _modes(self) -> dict[str, Any]:
        """Expose the underlying routing mode configs (used by tests and introspection)."""
        return self._router._modes

    async def call(
        self,
        mode: str,
        prompt: str,
        system: str | None = None,
        tier_override: int | None = None,
    ) -> str:
        """Call the best available model for the given mode.

        Args:
            mode: One of the mode keys in model_modes.yaml
            prompt: User/input content
            system: Optional system message override
            tier_override: Force a specific tier (1-based index)

        Returns:
            Model response text
        """
        ctx = WorkflowContext(workflow_id=f"mode-runner-{mode}")
        result = await self._router.execute(
            ModelRouterRequest(
                mode=mode,
                prompt=prompt,
                system=system,
                tier_override=tier_override,
            ),
            ctx,
        )
        return result.content
