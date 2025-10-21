"""
TTA Component Registry

This package provides centralized component discovery and maturity tracking.

Classes:
    ComponentMetadata: Metadata for a single component
    ComponentRegistry: Central registry for all TTA components

Example:
    ```python
    from scripts.registry import ComponentRegistry

    # Create registry (auto-discovers components)
    registry = ComponentRegistry()

    # Get all components
    components = registry.get_all_components()

    # Get specific component
    carbon = registry.get_component("carbon")

    # Get components by stage
    dev_components = registry.get_components_by_stage("Development")

    # Get promotion candidates
    candidates = registry.get_promotion_candidates()

    # Update all MATURITY.md files
    results = registry.update_all_maturity_files()
    ```
"""

from scripts.registry.component_registry import ComponentMetadata, ComponentRegistry

__all__ = ["ComponentMetadata", "ComponentRegistry"]
