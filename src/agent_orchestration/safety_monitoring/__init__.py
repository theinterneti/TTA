"""Safety monitoring and service orchestration component.

This component provides safety rules management, service orchestration,
and global service access for therapeutic safety validation.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Safety_monitoring/__init__]]

from .dashboard import SafetyMonitoringDashboard
from .provider import SafetyRulesProvider
from .service import (
    SafetyService,
    get_global_safety_service,
    set_global_safety_service_for_testing,
)

__all__ = [
    "SafetyMonitoringDashboard",
    "SafetyRulesProvider",
    "SafetyService",
    "get_global_safety_service",
    "set_global_safety_service_for_testing",
]
