"""
Comprehensive End-to-End Testing Framework Module

This module provides comprehensive system integration testing, performance
benchmarking, security validation, and clinical workflow testing for the
complete TTA therapeutic platform across all Phase A and Phase B components.

Components:
- E2ETestOrchestrator: Core end-to-end testing orchestration and management
- SystemIntegrationTester: Complete system integration testing across all components
- PerformanceBenchmarkTester: Clinical-grade performance validation under load
- SecurityPenetrationTester: Comprehensive security validation and compliance verification
- ClinicalWorkflowTester: End-to-end therapeutic workflow testing across all systems
- IntegrationValidator: Integration validation between Phase A and Phase B components
"""

from .clinical_workflow_tester import ClinicalWorkflowTester
from .e2e_test_orchestrator import E2ETestOrchestrator
from .integration_validator import IntegrationValidator
from .performance_benchmark_tester import PerformanceBenchmarkTester
from .security_penetration_tester import SecurityPenetrationTester
from .system_integration_tester import SystemIntegrationTester

__all__ = [
    "E2ETestOrchestrator",
    "SystemIntegrationTester",
    "PerformanceBenchmarkTester",
    "SecurityPenetrationTester",
    "ClinicalWorkflowTester",
    "IntegrationValidator",
]
