"""
Clinical Dashboard Integration Module

This module provides real-time clinical dashboard functionality for therapeutic
monitoring, progress tracking, and clinical oversight with integration to all
9 therapeutic systems from the Advanced AI Agent Orchestration.

Components:
- ClinicalDashboardManager: Core dashboard management and data aggregation
- TherapeuticMonitoringService: Real-time therapeutic progress monitoring
- ClinicalOversightInterface: Healthcare professional dashboard interface
- ProgressAnalyticsEngine: Evidence-based metrics and visualization
- CrisisAlertSystem: Integration with EmotionalSafetySystem for clinical alerts
- TherapeuticGoalTracker: Clinical objective alignment and progress tracking
"""

from .clinical_dashboard_manager import ClinicalDashboardManager
from .therapeutic_monitoring_service import TherapeuticMonitoringService
from .clinical_oversight_interface import ClinicalOversightInterface
from .progress_analytics_engine import ProgressAnalyticsEngine
from .crisis_alert_system import CrisisAlertSystem
from .therapeutic_goal_tracker import TherapeuticGoalTracker

__all__ = [
    "ClinicalDashboardManager",
    "TherapeuticMonitoringService", 
    "ClinicalOversightInterface",
    "ProgressAnalyticsEngine",
    "CrisisAlertSystem",
    "TherapeuticGoalTracker",
]
