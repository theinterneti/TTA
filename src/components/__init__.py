"""
TTA Components

This package contains component implementations for the TTA project.

Classes:
    Neo4jComponent: Component for managing Neo4j
    LLMComponent: Component for managing the LLM service
    AppComponent: Component for managing the TTA.prototype app

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components import Neo4jComponent, LLMComponent, AppComponent
    
    # Create a configuration object
    config = TTAConfig()
    
    # Create components
    neo4j = Neo4jComponent(config, repository="tta.dev")
    llm = LLMComponent(config, repository="tta.dev")
    app = AppComponent(config)
    
    # Start components
    neo4j.start()
    llm.start()
    app.start()
    ```
"""

from .neo4j_component import Neo4jComponent
from .llm_component import LLMComponent
from .app_component import AppComponent

__all__ = ['Neo4jComponent', 'LLMComponent', 'AppComponent']
