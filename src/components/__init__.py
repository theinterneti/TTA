"""
TTA Components

This package contains component implementations for the TTA project.

Classes:
    Neo4jComponent: Component for managing Neo4j
    LLMComponent: Component for managing the LLM service
    AppComponent: Component for managing the TTA.prototype app
    DockerComponent: Component for managing Docker configurations
    CarbonComponent: Component for tracking carbon emissions
    PlayerExperienceComponent: Component for managing the Player Experience Interface

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components import Neo4jComponent, LLMComponent, AppComponent, DockerComponent, CarbonComponent, PlayerExperienceComponent

    # Create a configuration object
    config = TTAConfig()

    # Create components
    docker = DockerComponent(config)
    carbon = CarbonComponent(config)
    neo4j = Neo4jComponent(config, repository="tta.dev")
    llm = LLMComponent(config, repository="tta.dev")
    app = AppComponent(config)
    player_experience = PlayerExperienceComponent(config)

    # Start components
    docker.start()
    carbon.start()
    neo4j.start()
    llm.start()
    app.start()
    player_experience.start()
    ```
"""

from .agent_orchestration_component import AgentOrchestrationComponent
from .app_component import AppComponent
from .carbon_component import CarbonComponent
from .docker_component import DockerComponent
from .llm_component import LLMComponent
from .narrative_arc_orchestrator_component import NarrativeArcOrchestratorComponent
from .neo4j_component import Neo4jComponent
from .player_experience_component import PlayerExperienceComponent

__all__ = [
    "Neo4jComponent",
    "LLMComponent",
    "AppComponent",
    "DockerComponent",
    "CarbonComponent",
    "PlayerExperienceComponent",
    "NarrativeArcOrchestratorComponent",
    "AgentOrchestrationComponent",
]


# Ensure a default asyncio event loop exists for tests that call get_event_loop directly
try:
    import asyncio

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
except Exception:
    pass
