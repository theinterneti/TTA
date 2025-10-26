"""
Integrated Development Workflow

Combines AI Context Management, Error Recovery, and Development Observability
with TTA's component maturity workflow for automated spec-to-production pipeline.

Main Components:
- spec_to_production.py: Main workflow orchestrator
- quality_gates.py: Quality gate validators
- stage_handlers.py: Stage-specific logic
- workflow_config.yaml: Configuration

Usage:
    from workflow import run_workflow

    result = run_workflow(
        spec_file="specs/my_component.md",
        component_name="my_component",
        target_stage="staging"
    )
"""

from .quality_gates import (
    QualityGateResult,
    QualityGateValidator,
    run_quality_gates,
)

__all__ = [
    "QualityGateResult",
    "QualityGateValidator",
    "run_quality_gates",
]

__version__ = "1.0.0"
