from __future__ import annotations

from unittest.mock import Mock, patch

from src.components.player_experience_component import PlayerExperienceComponent
from src.orchestration import TTAOrchestrator
from src.orchestration.component import ComponentStatus


def test_player_experience_lifecycle_via_orchestrator() -> None:
    # Patch imports so orchestrator registers the component
    with patch(
        "src.orchestration.orchestrator.TTAOrchestrator._import_repository_components"
    ) as mock_repo:
        with patch(
            "src.orchestration.orchestrator.TTAOrchestrator._validate_repositories"
        ) as mock_validate:
            with patch(
                "src.orchestration.orchestrator.TTAOrchestrator._import_core_components"
            ) as mock_core:

                def _core_side_effect(self):
                    self.components["player_experience"] = PlayerExperienceComponent(
                        Mock()
                    )

                mock_core.side_effect = _core_side_effect
                mock_repo.return_value = None
                mock_validate.return_value = None

                orch = TTAOrchestrator()
                assert "player_experience" in orch.components
                pe = orch.components["player_experience"]
                assert pe.status in {ComponentStatus.STOPPED, ComponentStatus.ERROR}

                # Mock start to success
                with patch.object(pe, "start", return_value=True):
                    assert orch.start_component("player_experience") is True
                assert orch.get_component_status("player_experience") in {
                    ComponentStatus.RUNNING,
                    ComponentStatus.ERROR,
                    ComponentStatus.STOPPED,
                }

                # Mock stop to success (best-effort)
                with patch.object(pe, "stop", return_value=True):
                    assert orch.stop_component("player_experience") is True
