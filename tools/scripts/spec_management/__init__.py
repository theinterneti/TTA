"""
TTA Specification Management Tools

This package provides comprehensive tools for managing TTA project specifications,
including validation, quality metrics, alignment checking, and automated workflows.

Components:
- spec_validator: Validates specification files against templates and standards
- spec_wizard: Interactive CLI tool for creating new specifications
- alignment_checker: Checks alignment between specifications and implementations
- quality_metrics: Calculates and tracks specification quality scores

Usage:
    # Validate specifications
    python -m scripts.spec_management.spec_validator .kiro/specs --recursive
    
    # Create new specification
    python -m scripts.spec_management.spec_wizard
    
    # Check alignment
    python -m scripts.spec_management.alignment_checker --report
    
    # Generate quality metrics
    python -m scripts.spec_management.quality_metrics --report
"""

__version__ = "1.0.0"
__author__ = "TTA Development Team"

# Import main classes for easier access
from .spec_validator import SpecificationValidator
from .spec_wizard import SpecificationWizard
from .alignment_checker import AlignmentChecker
from .quality_metrics import SpecificationQualityMetrics

__all__ = [
    "SpecificationValidator",
    "SpecificationWizard", 
    "AlignmentChecker",
    "SpecificationQualityMetrics"
]
