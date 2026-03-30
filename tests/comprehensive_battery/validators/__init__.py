"""

# Logseq: [[TTA.dev/Tests/Comprehensive_battery/Validators/__init__]]
Validation modules for comprehensive testing.

Provides validators for data pipeline integrity and dashboard functionality
to ensure end-to-end system validation.
"""

from .dashboard_validator import DashboardValidator
from .data_pipeline_validator import DataPipelineValidator

__all__ = [
    "DataPipelineValidator",
    "DashboardValidator",
]
