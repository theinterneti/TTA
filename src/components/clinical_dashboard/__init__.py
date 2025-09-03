"""
Clinical Dashboard Integration Module

Production-ready clinical dashboard with API integration for therapeutic
monitoring, progress tracking, and clinical oversight with integration to all
9 therapeutic systems from the Advanced AI Agent Orchestration.

Components:
- ClinicalDashboardManager: Core dashboard management and data aggregation
- TherapeuticMonitoringService: Enhanced real-time therapeutic progress monitoring
- ClinicalOversightInterface: Healthcare professional dashboard interface
- ProgressAnalyticsEngine: Evidence-based metrics and visualization
- CrisisAlertSystem: Integration with EmotionalSafetySystem for clinical alerts
- TherapeuticGoalTracker: Clinical objective alignment and progress tracking

New API Integration Components:
- ClinicalDashboardAPIService: API integration with validated TTA endpoints
- ClinicalDashboardController: Main controller orchestrating all services
- dashboard_router: FastAPI endpoints for clinical dashboard functionality
"""

# Legacy components (existing)
# New API integration components
from .api_integration_service import (
    APIConfig,
    AuthToken,
    ClinicalDashboardAPIService,
)
from .clinical_dashboard_manager import ClinicalDashboardManager
from .clinical_oversight_interface import ClinicalOversightInterface
from .crisis_alert_system import CrisisAlertSystem
from .dashboard_controller import (
    ClinicalDashboardController,
    DashboardRequest,
    MetricCollectionRequest,
    OutcomeMeasurementRequest,
    get_dashboard_controller,
)
from .dashboard_endpoints import router as dashboard_router
from .progress_analytics_engine import ProgressAnalyticsEngine
from .therapeutic_goal_tracker import TherapeuticGoalTracker

# Enhanced monitoring service
from .therapeutic_monitoring_service import (
    AnalyticsReport,
    AnalyticsTimeframe,
    ClinicalOutcome,
    MetricDataPoint,
    MetricType,
    OutcomeMeasure,
    TherapeuticMonitoringService,
)

__all__ = [
    # Legacy components
    "ClinicalDashboardManager",
    "ClinicalOversightInterface",
    "ProgressAnalyticsEngine",
    "CrisisAlertSystem",
    "TherapeuticGoalTracker",
    # Enhanced monitoring service
    "TherapeuticMonitoringService",
    "MetricType",
    "OutcomeMeasure",
    "AnalyticsTimeframe",
    "MetricDataPoint",
    "ClinicalOutcome",
    "AnalyticsReport",
    # API integration components
    "ClinicalDashboardAPIService",
    "APIConfig",
    "AuthToken",
    "ClinicalDashboardController",
    "DashboardRequest",
    "MetricCollectionRequest",
    "OutcomeMeasurementRequest",
    "get_dashboard_controller",
    "dashboard_router",
]
