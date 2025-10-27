"""
Component Maturity Automation System

This package provides automated tracking and updating of component maturity status.

Modules:
    metrics_collector: Collect quality metrics from pytest, ruff, pyright, bandit
    maturity_parser: Parse existing MATURITY.md files
    maturity_generator: Generate updated MATURITY.md content

Usage:
    from scripts.maturity.metrics_collector import collect_all_metrics
    from scripts.maturity.maturity_generator import generate_maturity_md

    metrics = collect_all_metrics("carbon", "src/components/carbon_component.py")
    content = generate_maturity_md(metrics, manual_sections)
"""

__version__ = "1.0.0"
__all__ = [
    "metrics_collector",
    "maturity_parser",
    "maturity_generator",
]
