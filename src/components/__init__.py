"""
TTA Components

This package contains component implementations for the TTA project.

Classes:
    Neo4jComponent: Component for managing Neo4j
    LLMComponent: Component for managing the LLM service
    AppComponent: Component for managing the TTA.prototype app
    DockerComponent: Component for managing Docker configurations
    CarbonComponent: Component for tracking carbon emissions

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components import Neo4jComponent, LLMComponent, AppComponent, DockerComponent, CarbonComponent

    # Create a configuration object
    config = TTAConfig()

    # Create components
    docker = DockerComponent(config)
    carbon = CarbonComponent(config)
    neo4j = Neo4jComponent(config, repository="tta.dev")
    llm = LLMComponent(config, repository="tta.dev")
    app = AppComponent(config)

    # Start components
    docker.start()
    carbon.start()
    neo4j.start()
    llm.start()
    app.start()
    ```
"""

from .neo4j_component import Neo4jComponent
from .llm_component import LLMComponent
from .app_component import AppComponent
from .docker_component import DockerComponent
from .carbon_component import CarbonComponent

__all__ = ['Neo4jComponent', 'LLMComponent', 'AppComponent', 'DockerComponent', 'CarbonComponent']
