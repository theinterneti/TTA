"""

# Logseq: [[TTA.dev/Orchestration/Component_loader]]
Component Loader Abstraction for TTA Orchestrator.

This module provides protocols and implementations for component discovery and loading,
enabling dependency injection for improved testability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from .component import Component

logger = logging.getLogger(__name__)


class ComponentLoader(Protocol):
    """
    Protocol for component discovery and loading.

    This protocol defines the interface for discovering and instantiating
    components, allowing for different implementations (filesystem-based,
    mock-based, etc.) to be injected into the orchestrator.
    """

    def validate_paths(self) -> None:
        """
        Validate that all required paths exist and are properly structured.

        Raises:
            FileNotFoundError: If a required path does not exist.
            ValueError: If paths are improperly structured.
        """
        ...

    def discover_components(self) -> dict[str, Component]:
        """
        Discover and instantiate all available components.

        Returns:
            Dictionary mapping component names to Component instances.

        Raises:
            ImportError: If a component module cannot be imported.
            Exception: If component instantiation fails.
        """
        ...


class FilesystemComponentLoader:
    """
    Production component loader that discovers components from the filesystem.

    This implementation uses the actual filesystem structure to discover
    and import components from tta.dev and tta.prototype repositories.

    Attributes:
        config: Configuration object for component settings
        root_dir: Root directory of the project
        tta_dev_path: Path to the tta.dev repository
        tta_prototype_path: Path to the tta.prototype repository
    """

    def __init__(
        self,
        config,
        root_dir: Path,
        tta_dev_path: Path,
        tta_prototype_path: Path,
    ):
        """
        Initialize the filesystem component loader.

        Args:
            config: Configuration object
            root_dir: Root directory of the project
            tta_dev_path: Path to tta.dev repository
            tta_prototype_path: Path to tta.prototype repository
        """
        self.config = config
        self.root_dir = root_dir
        self.tta_dev_path = tta_dev_path
        self.tta_prototype_path = tta_prototype_path

    def validate_paths(self) -> None:
        """
        Validate that repository paths exist.

        Raises:
            FileNotFoundError: If a repository path does not exist.
        """
        if not self.tta_dev_path.exists():
            raise FileNotFoundError(
                f"tta.dev repository not found at {self.tta_dev_path}"
            )

        if not self.tta_prototype_path.exists():
            raise FileNotFoundError(
                f"tta.prototype repository not found at {self.tta_prototype_path}"
            )

        logger.info("Repository paths validated successfully")

    def discover_components(self) -> dict[str, Component]:
        """
        Discover and instantiate components from filesystem.

        This method imports core components that are enabled in configuration.

        Returns:
            Dictionary mapping component names to Component instances.
        """
        components: dict[str, Component] = {}

        # Import player experience component if enabled
        if self.config.get("player_experience.enabled", False):
            try:
                from src.components.player_experience_component import (  # noqa: PLC0415
                    PlayerExperienceComponent,
                )

                comp = PlayerExperienceComponent(self.config)
                components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.error(f"Failed to import PlayerExperienceComponent: {e}")

        # Import agent orchestration component if enabled
        if self.config.get("agent_orchestration.enabled", False):
            try:
                from src.components.agent_orchestration_component import (  # noqa: PLC0415
                    AgentOrchestrationComponent,
                )

                comp = AgentOrchestrationComponent(self.config)
                components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.error(f"Failed to import AgentOrchestrationComponent: {e}")

        # Import docker component if enabled
        if self.config.get("docker.enabled", False):
            try:
                from src.components.docker_component import (  # noqa: PLC0415
                    DockerComponent,
                )

                comp = DockerComponent(self.config)
                components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.debug(f"DockerComponent not available: {e}")

        # Import carbon component if enabled
        if self.config.get("carbon.enabled", False):
            try:
                from src.components.carbon_component import (  # noqa: PLC0415
                    CarbonComponent,
                )

                comp = CarbonComponent(self.config)
                components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.debug(f"CarbonComponent not available: {e}")

        # Import gameplay loop component if enabled
        if self.config.get("core_gameplay_loop.enabled", False):
            try:
                from src.components.gameplay_loop_component import (  # noqa: PLC0415
                    GameplayLoopComponent,
                )

                comp = GameplayLoopComponent(self.config)
                components[comp.name] = comp
                logger.info(f"Imported core component {comp.name}")
            except Exception as e:
                logger.debug(f"GameplayLoopComponent not available: {e}")

        logger.info(f"Discovered {len(components)} components from filesystem")
        return components


class MockComponentLoader:
    """
    Mock component loader for testing purposes.

    This implementation allows tests to inject pre-configured components
    without relying on filesystem operations or actual component imports.

    Attributes:
        components: Dictionary of pre-configured mock components
    """

    def __init__(self, components: dict[str, Component] | None = None):
        """
        Initialize the mock component loader.

        Args:
            components: Optional dictionary of pre-configured components.
                       Defaults to empty dictionary.
        """
        self.components = components or {}

    def validate_paths(self) -> None:
        """
        Mock path validation - always succeeds.

        This allows tests to bypass filesystem validation.
        """
        logger.debug("Mock path validation - always valid")

    def discover_components(self) -> dict[str, Component]:
        """
        Return pre-configured mock components.

        Returns:
            Dictionary of mock components provided at initialization.
        """
        logger.debug(f"Returning {len(self.components)} mock components")
        return self.components.copy()


__all__ = [
    "ComponentLoader",
    "FilesystemComponentLoader",
    "MockComponentLoader",
]
